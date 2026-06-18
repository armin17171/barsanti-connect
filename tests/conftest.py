import os
import tempfile

import pytest

# Configura l'ambiente PRIMA di importare l'app (la config legge le env all'import)
_TMP_DB = os.path.join(tempfile.gettempdir(), "bc_test.sqlite3")
if os.path.exists(_TMP_DB):
    os.remove(_TMP_DB)
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP_DB}"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "adminpass"
os.environ["MEDIA_DIR"] = tempfile.mkdtemp(prefix="bc_media_")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c


def register(client, username, password="secret123", bio="", confirm=None):
    return client.post(
        "/register",
        data={
            "username": username,
            "password": password,
            "confirm_password": password if confirm is None else confirm,
            "bio": bio,
        },
    )


def login(client, username, password="secret123"):
    return client.post("/login", data={"username": username, "password": password})


def new_user_client(username, password="secret123"):
    """Un client separato già loggato come nuovo utente."""
    c = TestClient(app)
    c.__enter__()
    register(c, username, password)
    return c
