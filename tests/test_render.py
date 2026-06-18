from tests.conftest import register


def test_home_composer_has_media_menu(client):
    register(client, "render_home")
    page = client.get("/").text
    assert "js-media-btn" in page          # menu a tendina media
    assert "js-autogrow" in page           # textarea adattiva


def test_calendar_grid_renders(client):
    register(client, "render_cal")
    page = client.get("/calendar").text
    assert "cal-grid" in page              # griglia mensile
    # intestazioni dei giorni
    assert "Lun" in page and "Dom" in page


def test_settings_has_avatar_and_autogrow(client):
    register(client, "render_set")
    page = client.get("/settings").text
    assert 'name="avatar"' in page
    assert "js-autogrow" in page
    assert "js-pwd-toggle" in page


def test_theme_fab_present(client):
    assert "theme-fab" in client.get("/").text


def test_upcoming_event_popup_for_user(client):
    register(client, "render_ev")
    # crea un evento imminente (domani)
    from datetime import datetime, timedelta, timezone
    when = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
    client.post("/events", data={"title": "EventoImminente", "event_date": when})
    page = client.get("/").text
    assert "js-event-popup" in page
    assert "EventoImminente" in page
