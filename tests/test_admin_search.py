from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import Post, User
from tests.conftest import register


def _admin(client):
    client.post("/login", data={"username": "admin", "password": "adminpass"})
    return client


def test_search_users_hashtags_events(client):
    register(client, "cercami")
    client.post("/posts", data={"body": "evviva #ricerca"})
    client.post("/events", data={"title": "EventoCercabile", "event_date": "2026-08-01T09:00"})

    r = client.get("/search", params={"q": "cercami"})
    assert "cercami" in r.text
    r2 = client.get("/search", params={"q": "ricerca"})
    assert "ricerca" in r2.text
    r3 = client.get("/search", params={"q": "EventoCercabile"})
    assert "EventoCercabile" in r3.text


def test_non_admin_cannot_open_admin(client):
    register(client, "nonadmin")
    r = client.get("/admin")
    assert r.status_code == 403


def test_report_and_admin_queue(client):
    # un utente crea un post
    register(client, "postatore")
    client.post("/posts", data={"body": "contenuto segnalabile"})
    db = SessionLocal()
    try:
        pid = db.query(Post).filter(Post.body == "contenuto segnalabile").one().id
    finally:
        db.close()
    # un altro utente lo segnala
    client.post("/logout")
    register(client, "segnalatore")
    r = client.post("/report", data={"target_type": "post", "target_id": pid,
                                      "reason": "spam", "next": "/"})
    assert r.status_code == 200
    # l'admin vede la segnalazione
    client.post("/logout")
    _admin(client)
    admin_page = client.get("/admin")
    assert "spam" in admin_page.text


def test_ban_revokes_session_and_blocks_posting():
    # client separato per l'utente bersaglio
    target = TestClient(app)
    target.__enter__()
    register(target, "daBannare")
    db = SessionLocal()
    try:
        uid = db.query(User).filter(User.username == "daBannare").one().id
    finally:
        db.close()

    # l'admin banna
    admin = TestClient(app)
    admin.__enter__()
    _admin(admin)
    r = admin.post(f"/admin/users/{uid}/ban", data={"next": "/admin"})
    assert r.status_code == 200

    # la sessione dell'utente bannato è revocata: non può più pubblicare
    r2 = target.post("/posts", data={"body": "ci provo ancora"})
    assert r2.status_code == 401

    target.__exit__(None, None, None)
    admin.__exit__(None, None, None)


def test_cannot_ban_admin(client):
    _admin(client)
    db = SessionLocal()
    try:
        admin_id = db.query(User).filter(User.username == "admin").one().id
    finally:
        db.close()
    r = client.post(f"/admin/users/{admin_id}/ban")
    assert r.status_code == 400
