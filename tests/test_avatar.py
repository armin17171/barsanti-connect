from app.database import SessionLocal
from app.models import User
from tests.conftest import register

# 1x1 PNG fittizio: a save_image basta estensione + dimensione valide
FAKE_PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64


def _avatar_path(username):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.username == username).one().avatar_path
    finally:
        db.close()


def test_upload_and_show_avatar(client):
    register(client, "fotografo")
    # nessun avatar all'inizio
    assert _avatar_path("fotografo") is None

    r = client.post(
        "/settings",
        data={"bio": "con foto"},
        files={"avatar": ("io.png", FAKE_PNG, "image/png")},
    )
    assert r.status_code == 200
    path = _avatar_path("fotografo")
    assert path and path.endswith(".png")

    # appare nella pagina profilo come <img src="/media/...">
    page = client.get("/u/fotografo")
    assert f"/media/{path}" in page.text


def test_reject_non_image_avatar(client):
    register(client, "furbetto")
    r = client.post(
        "/settings",
        data={"bio": "x"},
        files={"avatar": ("video.mp4", b"0000", "video/mp4")},
    )
    assert r.status_code == 400
    assert _avatar_path("furbetto") is None


def test_remove_avatar(client):
    register(client, "pentito")
    client.post("/settings", data={"bio": "x"},
                files={"avatar": ("a.png", FAKE_PNG, "image/png")})
    assert _avatar_path("pentito") is not None
    # rimozione
    r = client.post("/settings", data={"bio": "x", "remove_avatar": "1"})
    assert r.status_code == 200
    assert _avatar_path("pentito") is None
