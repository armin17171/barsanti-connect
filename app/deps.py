from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session as DBSession

from .database import get_db
from .models import Session as SessionModel, User
from .security import SESSION_COOKIE, unsign_token


def get_current_user(request: Request, db: DBSession = Depends(get_db)) -> User | None:
    """Ritorna l'utente loggato oppure None (ospite). Mai solleva eccezioni."""
    signed = request.cookies.get(SESSION_COOKIE)
    if not signed:
        return None
    token = unsign_token(signed)
    if not token:
        return None
    sess = db.get(SessionModel, token)
    if not sess:
        return None
    user = db.get(User, sess.user_id)
    if not user or user.is_banned:
        return None
    return user


def require_login(user: User | None = Depends(get_current_user)) -> User:
    """Richiede un utente registrato e attivo."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Devi accedere per usare questa funzione.",
        )
    return user


def require_admin(user: User = Depends(require_login)) -> User:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permessi insufficienti.",
        )
    return user
