from app.database import SessionLocal
from app.models import User
from tests.conftest import register

# PNG fittizio: a save_image basta estensione + dimensione valide
FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64


def _avatar_path(username):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.username == username).one().avatar_path
    finally:
        db.close()


def test_upload_avatar_from_profile(client):
    register(client, "fotografo")
    assert _avatar_path("fotografo") is None

    r = client.post("/me/avatar", files={"avatar": ("io.png", FAKE_PNG, "image/png")})
    assert r.status_code == 200
    path = _avatar_path("fotografo")
    assert path and path.endswith(".png")
    # appare nella pagina profilo come <img src="/media/...">
    assert f"/media/{path}" in client.get("/u/fotografo").text


def test_reject_non_image_avatar(client):
    register(client, "furbetto")
    r = client.post("/me/avatar", files={"avatar": ("video.mp4", b"0000", "video/mp4")})
    assert r.status_code == 400
    assert _avatar_path("furbetto") is None


def test_replace_avatar(client):
    register(client, "cambista")
    client.post("/me/avatar", files={"avatar": ("a.png", FAKE_PNG, "image/png")})
    first = _avatar_path("cambista")
    client.post("/me/avatar", files={"avatar": ("b.png", FAKE_PNG, "image/png")})
    second = _avatar_path("cambista")
    assert first and second and first != second


def test_guest_cannot_change_avatar(client):
    r = client.post("/me/avatar", files={"avatar": ("x.png", FAKE_PNG, "image/png")})
    assert r.status_code == 401
