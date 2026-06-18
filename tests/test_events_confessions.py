from app.models import Confession
from tests.conftest import register


# ---------- Calendario / eventi ----------

def test_guest_cannot_view_calendar(client):
    r = client.get("/calendar")  # segue il redirect verso /login
    assert r.status_code == 200
    assert "Accedi" in r.text  # è finito sulla pagina di login


def test_guest_cannot_create_event(client):
    r = client.post("/events", data={"title": "Festa", "event_date": "2026-07-01T10:00"})
    assert r.status_code == 401


def test_create_event(client):
    register(client, "prof")
    r = client.post("/events", data={
        "title": "Assemblea di istituto",
        "description": "In aula magna",
        "event_date": "2026-07-01T10:00",
    })
    assert r.status_code == 200
    cal = client.get("/calendar")
    assert "Assemblea di istituto" in cal.text


# ---------- Confessioni anonime ----------

def test_confession_model_has_no_author_link():
    """GARANZIA ANONIMATO: la tabella confessioni non ha colonne che puntano all'utente."""
    cols = {c.name for c in Confession.__table__.columns}
    assert "author_id" not in cols
    assert "user_id" not in cols
    # delete_token_hash è l'hash di un token casuale dato all'autore: NON deriva
    # dall'identità dell'utente, quindi l'anonimato resta totale.
    assert cols == {"id", "body", "created_at", "delete_token_hash"}


def test_guest_cannot_post_confession(client):
    r = client.post("/confessions", data={"body": "segreto"})
    assert r.status_code == 401


def test_confession_is_anonymous_in_db(client):
    register(client, "confessore")
    r = client.post("/confessions", data={"body": "confessione top secret"})
    assert r.status_code == 200
    # Visibile come "Anonimo"
    page = client.get("/confessions")
    assert "confessione top secret" in page.text
    assert "Anonimo" in page.text
    # Nel DB non esiste alcun legame con l'utente
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        conf = db.query(Confession).filter(Confession.body == "confessione top secret").one()
        # l'oggetto non possiede alcun attributo che identifichi l'autore
        assert not hasattr(conf, "author_id")
        assert not hasattr(conf, "user_id")
    finally:
        db.close()


def test_only_admin_deletes_confession(client):
    register(client, "anon1")
    client.post("/confessions", data={"body": "da moderare"})
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        cid = db.query(Confession).filter(Confession.body == "da moderare").one().id
    finally:
        db.close()
    # utente normale non può
    r = client.post(f"/confessions/{cid}/delete")
    assert r.status_code == 403
