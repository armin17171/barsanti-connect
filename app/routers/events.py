from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from sqlalchemy.orm import Session as DBSession

from ..database import get_db
from ..deps import require_login
from ..models import Event, User
from ..web import redirect_to

router = APIRouter()


@router.post("/events")
def create_event(
    request: Request,
    title: str = Form(...),
    event_date: str = Form(...),
    description: str = Form(""),
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    title = title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="Il titolo è obbligatorio.")
    # event_date arriva da <input type="datetime-local"> -> "YYYY-MM-DDTHH:MM"
    try:
        dt = datetime.fromisoformat(event_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Data evento non valida.")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    event = Event(author_id=user.id, title=title, description=description.strip(), event_date=dt)
    db.add(event)
    db.commit()
    return redirect_to("/calendar")


@router.post("/events/{event_id}/delete")
def delete_event(
    event_id: int,
    request: Request,
    user: User = Depends(require_login),
    db: DBSession = Depends(get_db),
):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento non trovato.")
    if event.author_id != user.id and not user.is_admin:
        raise HTTPException(status_code=403, detail="Non puoi eliminare questo evento.")
    db.delete(event)
    db.commit()
    return redirect_to("/calendar")
