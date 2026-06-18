import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from .config import settings
from .database import Base, SessionLocal, engine
from .deps import get_current_user
from .models import User
from .security import hash_password
from .templating import render
from .routers import admin, auth, confessions, events, pages, posts

_BASE_DIR = os.path.dirname(__file__)


def _wait_for_db(retries: int = 30, delay: float = 1.0) -> None:
    """Attende che il database sia pronto (utile al primo avvio del compose)."""
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                conn.execute(select(1))
            return
        except OperationalError:
            if attempt == retries:
                raise
            time.sleep(delay)


def _seed_admin() -> None:
    db = SessionLocal()
    try:
        existing = db.execute(
            select(User).where(User.username == settings.admin_username)
        ).scalar_one_or_none()
        if existing is None:
            db.add(User(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
                bio="Amministratore di Barsanti Connect",
                is_admin=True,
            ))
            db.commit()
        elif not existing.is_admin:
            existing.is_admin = True
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Per SQLite assicura che la cartella esista
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.split("///")[-1]
        parent = os.path.dirname(db_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
    _wait_for_db()
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.media_dir, exist_ok=True)
    _seed_admin()
    yield


app = FastAPI(title="Barsanti Connect", lifespan=lifespan)


# File statici (CSS/JS/logo) e media caricati dagli utenti
app.mount("/static", StaticFiles(directory=os.path.join(_BASE_DIR, "static")), name="static")
os.makedirs(settings.media_dir, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Mostra una pagina d'errore leggibile per le richieste HTML, JSON per le API."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept and "application/json" not in accept:
        db = SessionLocal()
        try:
            user = None
            try:
                user = get_current_user(request, db)
            except Exception:
                user = None
            return render("error.html", request, user=user, status_code=exc.status_code,
                          code=exc.status_code, message=exc.detail)
        finally:
            db.close()
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


# Router
app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(events.router)
app.include_router(confessions.router)
app.include_router(admin.router)
app.include_router(pages.router)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
