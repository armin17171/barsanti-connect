from tests.conftest import register


def _create_post(client, body):
    return client.post("/posts", data={"body": body})


def test_guest_cannot_post(client):
    r = client.post("/posts", data={"body": "ciao"})
    assert r.status_code == 401


def test_create_post_with_hashtag(client):
    register(client, "ada")
    r = _create_post(client, "Primo post #scuola #barsanti")
    assert r.status_code == 200
    # Appare nel feed
    feed = client.get("/")
    assert "Primo post" in feed.text
    # La pagina hashtag lo elenca
    tagpage = client.get("/hashtag/scuola")
    assert "Primo post" in tagpage.text
    assert tagpage.status_code == 200


def test_empty_post_rejected(client):
    register(client, "grace")
    r = client.post("/posts", data={"body": "   "})
    assert r.status_code == 400


def test_like_toggle(client):
    register(client, "alan")
    _create_post(client, "metti like")
    # recupera id post dal feed
    import re
    feed = client.get("/").text
    post_id = re.search(r"/post/(\d+)", feed).group(1)

    r1 = client.post(f"/posts/{post_id}/like", headers={"Accept": "application/json"})
    assert r1.json() == {"liked": True, "count": 1}
    r2 = client.post(f"/posts/{post_id}/like", headers={"Accept": "application/json"})
    assert r2.json() == {"liked": False, "count": 0}


def test_guest_cannot_like(client):
    register(client, "owner1")
    _create_post(client, "post pubblico")
    import re
    post_id = re.search(r"/post/(\d+)", client.get("/").text).group(1)
    client.post("/logout")
    r = client.post(f"/posts/{post_id}/like", headers={"Accept": "application/json"})
    assert r.status_code == 401


def test_comment_flow(client):
    register(client, "turing")
    _create_post(client, "commentami")
    import re
    post_id = re.search(r"/post/(\d+)", client.get("/").text).group(1)
    r = client.post(f"/posts/{post_id}/comment", data={"body": "bel post!"})
    assert r.status_code == 200
    detail = client.get(f"/post/{post_id}")
    assert "bel post!" in detail.text


def test_delete_post_permissions(client):
    # autore crea, un altro utente non può eliminare
    register(client, "autore")
    _create_post(client, "mio post")
    import re
    post_id = re.search(r"/post/(\d+)", client.get("/").text).group(1)
    client.post("/logout")
    register(client, "estraneo")
    r = client.post(f"/posts/{post_id}/delete", data={"next": "/"})
    assert r.status_code == 403
    # ora l'autore lo elimina
    client.post("/logout")
    client.post("/login", data={"username": "autore", "password": "secret123"})
    r2 = client.post(f"/posts/{post_id}/delete", data={"next": "/"})
    assert r2.status_code == 200
    assert client.get(f"/post/{post_id}").status_code == 404
