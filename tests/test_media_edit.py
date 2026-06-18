import re

from app.database import SessionLocal
from app.models import Confession
from tests.conftest import register

FAKE = b"0" * 32


def _latest_pid(client):
    return re.search(r"/post/(\d+)", client.get("/").text).group(1)


# ---------- Audio ----------

def test_audio_post_shows_player(client):
    register(client, "musicista")
    r = client.post("/posts", data={"body": "ascolta questa"},
                    files={"media": ("brano.mp3", FAKE, "audio/mpeg")})
    assert r.status_code == 200
    # la creazione reindirizza alla pagina del post: deve contenere il player audio
    assert "js-audio" in r.text


# ---------- Modifica post ----------

def test_edit_own_post(client):
    register(client, "scrittore")
    client.post("/posts", data={"body": "testo originale #uno"})
    pid = _latest_pid(client)
    r = client.post(f"/posts/{pid}/edit", data={"body": "testo modificato #due"})
    assert r.status_code == 200
    assert "testo modificato" in client.get(f"/post/{pid}").text
    # il nuovo hashtag è collegato, il vecchio no
    assert "testo modificato" in client.get("/hashtag/due").text
    assert "testo modificato" not in client.get("/hashtag/uno").text


def test_cannot_edit_others_post(client):
    register(client, "proprietario")
    client.post("/posts", data={"body": "mio post"})
    pid = _latest_pid(client)
    client.post("/logout")
    register(client, "ladro")
    assert client.post(f"/posts/{pid}/edit", data={"body": "rubato"}).status_code == 403
    assert client.get(f"/post/{pid}/edit").status_code == 403


# ---------- Confessioni: delete autore (token) e admin ----------

def test_confession_author_delete_with_token(client):
    register(client, "tokenuser")
    r = client.post("/confessions", data={"body": "cancellami io"},
                    headers={"Accept": "application/json"})
    assert r.status_code == 200
    data = r.json()
    cid, token = data["id"], data["token"]
    # senza token non si può
    assert client.post(f"/confessions/{cid}/delete").status_code == 403
    # con il token sì
    assert client.post(f"/confessions/{cid}/delete", data={"token": token}).status_code == 200
    db = SessionLocal()
    try:
        assert db.get(Confession, cid) is None
    finally:
        db.close()


def test_admin_delete_confession_without_token(client):
    register(client, "anon_scrittore")
    client.post("/confessions", data={"body": "rimozione admin"})
    db = SessionLocal()
    try:
        cid = db.query(Confession).filter(Confession.body == "rimozione admin").one().id
    finally:
        db.close()
    client.post("/logout")
    client.post("/login", data={"username": "admin", "password": "adminpass"})
    # l'admin cancella senza token (e senza sapere chi l'ha scritta)
    assert client.post(f"/confessions/{cid}/delete").status_code == 200


def test_large_upload_allowed(client):
    """Verifica che file ben oltre 1 MB siano accettati (limite reale ~1 GB)."""
    register(client, "bigfile")
    big = b"\x89PNG\r\n\x1a\n" + b"0" * (3 * 1024 * 1024)  # ~3 MB
    r = client.post("/posts", data={"body": "file grande"},
                    files={"media": ("big.png", big, "image/png")})
    assert r.status_code == 200
