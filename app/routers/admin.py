from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session as DBSession

from ..database import get_db
from ..deps import require_admin, require_login
from ..models import (
    Comment,
    Confession,
    Post,
    Report,
    Session as SessionModel,
    User,
)
from ..web import redirect_back, redirect_to

router = APIRouter()

VALID_TARGETS = {"post", "comment", "confession"}


@router.post("/report")
def create_report(
    request: Request,
    target_type: str = Form(...),
    target_id: int = Form(...),
    reason: str = Form(""),
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    if target_type not in VALID_TARGETS:
        raise HTTPException(status_code=400, detail="Tipo di segnalazione non valido.")

    model = {"post": Post, "comment": Comment, "confession": Confession}[target_type]
    if not db.get(model, target_id):
        raise HTTPException(status_code=404, detail="Contenuto non trovato.")

    db.add(Report(reporter_id=user.id, target_type=target_type,
                  target_id=target_id, reason=reason.strip()))
    db.commit()
    return redirect_back(request, default="/")


@router.post("/admin/users/{user_id}/ban")
def ban_user(
    user_id: int,
    request: Request,
    admin: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Utente non trovato.")
    if target.is_admin:
        raise HTTPException(status_code=400, detail="Non puoi bannare un amministratore.")
    target.is_banned = True
    # Revoca tutte le sessioni attive dell'utente bannato
    db.query(SessionModel).filter(SessionModel.user_id == user_id).delete()
    db.commit()
    return redirect_back(request, default="/admin")


@router.post("/admin/users/{user_id}/unban")
def unban_user(
    user_id: int,
    request: Request,
    admin: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="Utente non trovato.")
    target.is_banned = False
    db.commit()
    return redirect_back(request, default="/admin")


@router.post("/admin/reports/{report_id}/resolve")
def resolve_report(
    report_id: int,
    request: Request,
    admin: User = Depends(require_admin),
    db: DBSession = Depends(get_db),
):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Segnalazione non trovata.")
    report.resolved = True
    db.commit()
    return redirect_to("/admin")
