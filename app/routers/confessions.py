import hashlib
import secrets
import time

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session as DBSession

from ..database import get_db
from ..deps import require_login
from ..models import Confession, ConfessionComment, User
from ..web import redirect_to

router = APIRouter()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

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
    # Token segreto per consentire all'autore di cancellare la propria confessione.
    # Nel DB salviamo solo l'hash; il token "in chiaro" torna al browser che lo
    # conserva localmente. Nessun legame con l'identità dell'utente.
    token = secrets.token_urlsafe(24)
    conf = Confession(body=body, delete_token_hash=_hash_token(token))
    db.add(conf)
    db.commit()
    db.refresh(conf)
    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse({"id": conf.id, "token": token})
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
    token: str = Form(""),
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    confession = db.get(Confession, confession_id)
    if not confession:
        raise HTTPException(status_code=404, detail="Confessione non trovata.")
    # Può cancellare: l'admin (senza sapere chi l'ha scritta) oppure chi possiede
    # il token segreto originale (= l'autore). Il confronto è sugli hash.
    is_author = bool(
        token and confession.delete_token_hash
        and secrets.compare_digest(_hash_token(token), confession.delete_token_hash)
    )
    if not user.is_admin and not is_author:
        raise HTTPException(status_code=403, detail="Non puoi cancellare questa confessione.")
    db.delete(confession)
    db.commit()
    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse({"ok": True})
    return redirect_to("/confessions")
