from tests.conftest import login, register


def test_health(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_homepage_visible_to_guest(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Barsanti" in r.text
    # L'ospite vede il banner ospite
    assert "ospite" in r.text.lower()


def test_register_and_session(client):
    r = register(client, "mario")
    assert r.status_code == 200  # redirect seguito fino alla home
    # Ora è loggato: la pagina impostazioni è accessibile
    assert client.get("/settings").status_code == 200


def test_duplicate_username_rejected(client):
    register(client, "luigi")
    c2 = client
    c2.post("/logout")
    r = register(c2, "luigi")
    assert r.status_code == 400
    assert "in uso" in r.text


def test_short_password_rejected(client):
    r = register(client, "peach", password="123")
    assert r.status_code == 400


def test_invalid_username_rejected(client):
    r = register(client, "a b!", password="secret123")
    assert r.status_code == 400


def test_login_wrong_password(client):
    register(client, "bowser")
    client.post("/logout")
    r = login(client, "bowser", "sbagliata")
    assert r.status_code == 401


def test_logout_revokes_access(client):
    register(client, "yoshi")
    assert client.get("/settings").status_code == 200
    client.post("/logout")
    # Senza sessione la pagina protetta non è accessibile
    assert client.get("/settings").status_code == 401


def test_register_password_mismatch(client):
    r = register(client, "discorde", password="secret123", confirm="diversa999")
    assert r.status_code == 400
    assert "coincid" in r.text.lower()
