import time

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session as DBSession

from ..database import get_db
from ..deps import require_admin, require_login
from ..models import Confession, ConfessionComment, User
from ..web import redirect_to

router = APIRouter()

# Rate-limit SOLO in memoria: { user_id: ultimo_timestamp }.
# NON viene mai scritto su disco e NON è collegato al contenuto della confessione,
# quindi non permette di risalire all'autore guardando il database.
_last_confession: dict[int, float] = {}
_last_comment: dict[int, float] = {}
RATE_SECONDS = 20


def _check_rate(store: dict[int, float], user_id: int) -> None:
    now = time.monotonic()
    last = store.get(user_id, 0.0)
    if now - last < RATE_SECONDS:
        raise HTTPException(
            status_code=429,
            detail="Aspetta qualche secondo prima di pubblicare di nuovo.",
        )
    store[user_id] = now


@router.post("/confessions")
def create_confession(
    request: Request,
    body: str = Form(...),
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    body = body.strip()
    if not body:
        raise HTTPException(status_code=400, detail="La confessione non può essere vuota.")
    # Il login serve SOLO come gate anti-spam: l'id utente è usato per il rate-limit
    # in memoria, ma NON viene salvato insieme alla confessione.
    _check_rate(_last_confession, user.id)
    db.add(Confession(body=body))
    db.commit()
    return redirect_to("/confessions")


@router.post("/confessions/{confession_id}/comment")
def comment_confession(
    confession_id: int,
    request: Request,
    body: str = Form(...),
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    confession = db.get(Confession, confession_id)
    if not confession:
        raise HTTPException(status_code=404, detail="Confessione non trovata.")
    body = body.strip()
    if not body:
        raise HTTPException(status_code=400, detail="Il commento non può essere vuoto.")
    _check_rate(_last_comment, user.id)
    db.add(ConfessionComment(confession_id=confession_id, body=body))
    db.commit()
    return redirect_to("/confessions")


@router.post("/confessions/{confession_id}/delete")
def delete_confession(
    confession_id: int,
    request: Request,
    user: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    # Solo admin: non esiste un "autore" da verificare.
    confession = db.get(Confession, confession_id)
    if not confession:
        raise HTTPException(status_code=404, detail="Confessione non trovata.")
    db.delete(confession)
    db.commit()
    return redirect_to("/confessions")
