import calendar as pycal
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy import or_
from sqlalchemy.orm import Session as DBSession

from ..database import get_db
from ..deps import get_current_user, require_login
from ..media import delete_media, save_image
from ..models import (
    Comment,
    Confession,
    Event,
    Hashtag,
    Like,
    Post,
    Report,
    User,
)
from ..security import hash_password, verify_password
from ..templating import render
from ..web import redirect_to
from .auth import USERNAME_RE

router = APIRouter()


def _liked_ids(db: DBSession, user: User | None, post_ids: list[int]) -> set[int]:
    if not user or not post_ids:
        return set()
    rows = (
        db.query(Like.post_id)
        .filter(Like.user_id == user.id, Like.post_id.in_(post_ids))
        .all()
    )
    return {r[0] for r in rows}


@router.get("/")
def index(request: Request, user: User | None = Depends(get_current_user),
          db: DBSession = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(100).all()
    liked = _liked_ids(db, user, [p.id for p in posts])
    # Eventi imminenti (prossimi 7 giorni) per il popup in home — solo per i registrati
    upcoming = []
    if user:
        now = datetime.now(timezone.utc)
        soon = now + timedelta(days=7)
        upcoming = (
            db.query(Event)
            .filter(Event.event_date >= now, Event.event_date <= soon)
            .order_by(Event.event_date.asc())
            .limit(5)
            .all()
        )
    return render("index.html", request, user=user, posts=posts, liked_ids=liked, upcoming=upcoming)


@router.get("/post/{post_id}")
def post_detail(post_id: int, request: Request,
                user: User | None = Depends(get_current_user),
                db: DBSession = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        return render("not_found.html", request, user=user, status_code=404,
                      message="Post non trovato.")
    liked = _liked_ids(db, user, [post.id])
    return render("post_detail.html", request, user=user, post=post, liked_ids=liked)


@router.get("/post/{post_id}/edit")
def edit_post_page(post_id: int, request: Request,
                   user: User = Depends(require_login),
                   db: DBSession = Depends(get_db)):
    post = db.get(Post, post_id)
    if not post:
        return render("not_found.html", request, user=user, status_code=404,
                      message="Post non trovato.")
    if post.author_id != user.id:
        return render("not_found.html", request, user=user, status_code=403,
                      message="Puoi modificare solo i tuoi post.")
    return render("post_edit.html", request, user=user, post=post)


_MESI = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
         "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]


@router.get("/calendar")
def calendar(request: Request, month: str = "",
             user: User | None = Depends(get_current_user),
             db: DBSession = Depends(get_db)):
    # Gli ospiti NON possono accedere al calendario (requisito).
    if user is None:
        return redirect_to("/login")

    today = datetime.now(timezone.utc).date()
    try:
        year, mon = (int(x) for x in month.split("-"))
        date(year, mon, 1)
    except (ValueError, TypeError):
        year, mon = today.year, today.month

    events = db.query(Event).order_by(Event.event_date.asc()).all()
    by_day: dict[date, list] = {}
    for e in events:
        d = e.event_date.date()
        by_day.setdefault(d, []).append(e)

    weeks = []
    for week in pycal.Calendar(firstweekday=0).monthdatescalendar(year, mon):
        weeks.append([
            {"date": d, "in_month": d.month == mon, "today": d == today,
             "events": by_day.get(d, [])}
            for d in week
        ])

    prev_d = date(year, mon, 1) - timedelta(days=1)
    next_d = (date(year, mon, 28) + timedelta(days=10)).replace(day=1)
    month_events = [e for e in events if e.event_date.year == year and e.event_date.month == mon]

    return render("calendar.html", request, user=user, weeks=weeks,
                  month_label=f"{_MESI[mon]} {year}",
                  prev_month=f"{prev_d.year}-{prev_d.month:02d}",
                  next_month=f"{next_d.year}-{next_d.month:02d}",
                  month_events=month_events)


@router.get("/confessions")
def confessions(request: Request, user: User | None = Depends(get_current_user),
                db: DBSession = Depends(get_db)):
    items = db.query(Confession).order_by(Confession.created_at.desc()).limit(100).all()
    return render("confessions.html", request, user=user, confessions=items)


@router.get("/search")
def search(request: Request, q: str = "", user: User | None = Depends(get_current_user),
           db: DBSession = Depends(get_db)):
    q = q.strip()
    users = hashtags = events = []
    if q:
        like = f"%{q}%"
        users = db.query(User).filter(User.username.ilike(like)).limit(50).all()
        tag_q = q.lstrip("#").lower()
        hashtags = db.query(Hashtag).filter(Hashtag.tag.ilike(f"%{tag_q}%")).limit(50).all()
        events = (
            db.query(Event)
            .filter(or_(Event.title.ilike(like), Event.description.ilike(like)))
            .order_by(Event.event_date.asc())
            .limit(50)
            .all()
        )
    return render("search.html", request, user=user, q=q,
                  users=users, hashtags=hashtags, events=events)


@router.get("/hashtag/{tag}")
def hashtag_page(tag: str, request: Request,
                 user: User | None = Depends(get_current_user),
                 db: DBSession = Depends(get_db)):
    tag = tag.lstrip("#").lower()
    obj = db.query(Hashtag).filter(Hashtag.tag == tag).one_or_none()
    posts = []
    if obj:
        posts = sorted(obj.posts, key=lambda p: p.created_at, reverse=True)
    liked = _liked_ids(db, user, [p.id for p in posts])
    return render("hashtag.html", request, user=user, tag=tag, posts=posts, liked_ids=liked)


@router.get("/u/{username}")
def profile(username: str, request: Request,
            user: User | None = Depends(get_current_user),
            db: DBSession = Depends(get_db)):
    profile_user = db.query(User).filter(User.username == username).one_or_none()
    if not profile_user:
        return render("not_found.html", request, user=user, status_code=404,
                      message="Utente non trovato.")
    posts = (
        db.query(Post)
        .filter(Post.author_id == profile_user.id)
        .order_by(Post.created_at.desc())
        .all()
    )
    comments = (
        db.query(Comment)
        .filter(Comment.author_id == profile_user.id)
        .order_by(Comment.created_at.desc())
        .limit(50)
        .all()
    )
    liked = _liked_ids(db, user, [p.id for p in posts])
    return render("profile.html", request, user=user, profile_user=profile_user,
                  posts=posts, comments=comments, liked_ids=liked)


@router.get("/settings")
def settings_page(request: Request, user: User = Depends(require_login)):
    return render("settings.html", request, user=user)


@router.post("/settings")
def update_settings(
    request: Request,
    username: str = Form(...),
    bio: str = Form(""),
    current_password: str = Form(""),
    new_password: str = Form(""),
    confirm_new_password: str = Form(""),
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    new_username = username.strip()
    error = None

    # Validazione cambio username
    if new_username != user.username:
        if not USERNAME_RE.match(new_username):
            error = "Username non valido: 3-32 caratteri tra lettere, numeri, '_' e '.'."
        elif db.query(User).filter(User.username == new_username, User.id != user.id).first():
            error = "Username già in uso."

    # Validazione cambio password
    change_pw = bool(new_password)
    if not error and change_pw:
        if not verify_password(current_password, user.password_hash):
            error = "Password attuale errata."
        elif new_password != confirm_new_password:
            error = "Le due nuove password non coincidono."
        elif len(new_password) < 6:
            error = "La nuova password deve avere almeno 6 caratteri."

    if error:
        # Niente viene modificato; ripresenta i dati attuali
        return render("settings.html", request, user=user, error=error, status_code=400)

    user.username = new_username
    user.bio = bio.strip()
    message = "Profilo aggiornato."
    if change_pw:
        user.password_hash = hash_password(new_password)
        message = "Profilo e password aggiornati."
    db.commit()
    return render("settings.html", request, user=user, message=message)


@router.post("/me/avatar")
async def update_avatar(
    request: Request,
    avatar: UploadFile | None = File(None),
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    """Cambio immagine profilo dal cerchio nella pagina profilo."""
    if avatar is not None and avatar.filename:
        new_path = await save_image(avatar)
        if new_path:
            delete_media(user.avatar_path)
            user.avatar_path = new_path
            db.commit()
    return redirect_to(f"/u/{user.username}")


@router.get("/admin")
def admin_page(request: Request, user: User = Depends(require_login),
               db: DBSession = Depends(get_db)):
    if not user.is_admin:
        return render("not_found.html", request, user=user, status_code=403,
                      message="Area riservata agli amministratori.")
    users = db.query(User).order_by(User.created_at.desc()).all()
    reports = db.query(Report).order_by(Report.resolved.asc(), Report.created_at.desc()).all()
    return render("admin.html", request, user=user, users=users, reports=reports)
