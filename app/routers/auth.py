import re

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session as DBSession

from ..database import get_db
from ..deps import get_current_user
from ..models import Session as SessionModel, User
from ..security import (
    SESSION_COOKIE,
    hash_password,
    new_session_token,
    sign_token,
    verify_password,
)
from ..templating import render
from ..web import redirect_to

router = APIRouter()

USERNAME_RE = re.compile(r"^[A-Za-z0-9_.]{3,32}$")


def _start_session(db: DBSession, response: Response, user: User) -> None:
    token = new_session_token()
    db.add(SessionModel(token=token, user_id=user.id))
    db.commit()
    response.set_cookie(
        SESSION_COOKIE,
        sign_token(token),
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,  # 30 giorni
    )


@router.get("/register")
def register_page(request: Request, user: User | None = Depends(get_current_user)):
    if user:
        return redirect_to("/")
    return render("register.html", request, user=None)


@router.post("/register")
def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    bio: str = Form(""),
    db: DBSession = Depends(get_db),
):
    username = username.strip()
    error = None
    if not USERNAME_RE.match(username):
        error = "Username non valido: 3-32 caratteri tra lettere, numeri, '_' e '.'."
    elif len(password) < 6:
        error = "La password deve avere almeno 6 caratteri."
    elif db.query(User).filter(User.username == username).first():
        error = "Username già in uso."

    if error:
        return render("register.html", request, user=None, error=error,
                      values={"username": username, "bio": bio}, status_code=400)

    user = User(username=username, password_hash=hash_password(password), bio=bio.strip())
    db.add(user)
    db.commit()
    db.refresh(user)

    response = RedirectResponse(url="/", status_code=303)
    _start_session(db, response, user)
    return response


@router.get("/login")
def login_page(request: Request, user: User | None = Depends(get_current_user)):
    if user:
        return redirect_to("/")
    return render("login.html", request, user=None)


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: DBSession = Depends(get_db),
):
    username = username.strip()
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return render("login.html", request, user=None,
                      error="Username o password errati.", status_code=401)
    if user.is_banned:
        return render("login.html", request, user=None,
                      error="Questo account è stato bannato.", status_code=403)

    response = RedirectResponse(url="/", status_code=303)
    _start_session(db, response, user)
    return response


@router.post("/logout")
def logout(request: Request, db: DBSession = Depends(get_db)):
    signed = request.cookies.get(SESSION_COOKIE)
    if signed:
        from ..security import unsign_token

        token = unsign_token(signed)
        if token:
            sess = db.get(SessionModel, token)
            if sess:
                db.delete(sess)
                db.commit()
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(SESSION_COOKIE)
    return response
