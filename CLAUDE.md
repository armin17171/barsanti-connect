# CLAUDE.md — Contesto del progetto

Guida per chiunque (incluso Claude in sessioni future) lavori su questo repository.

## Cos'è
**Barsanti Connect**: social network interno a una scuola (stile Instagram), pensato
per girare in Docker su una macchina Ubuntu e accessibile via LAN in HTTP semplice.

## Stack
- **FastAPI** + **SQLAlchemy 2.0** (sincrono) — backend e pagine server-side
- **Jinja2** + **JavaScript vanilla** — frontend (niente SPA)
- **PostgreSQL** in produzione; **SQLite** per i test (l'app è DB-agnostica via `DATABASE_URL`)
- **argon2-cffi** per le password, cookie di sessione firmati con **itsdangerous**
- **PWA**: `manifest.webmanifest` + `sw.js`

## Avvio
```bash
cp .env.example .env   # poi modifica i segreti
docker compose up -d --build
# http://IP_MACCHINA:8000
```

## Struttura del codice
- `app/config.py` — `Settings` legge tutto da variabili d'ambiente (prefisso nessuno, case-insensitive)
- `app/database.py` — `engine`, `SessionLocal`, `get_db` (dipendenza per richiesta)
- `app/models.py` — modelli ORM
- `app/security.py` — `hash_password` / `verify_password` (argon2), firma del token di sessione
- `app/deps.py` — `get_current_user` (ospite = `None`), `require_login`, `require_admin`
- `app/routers/`
  - `auth.py` — register/login/logout (sessioni server-side in tabella `sessions`)
  - `posts.py` — post, like (toggle), commenti, eliminazione
  - `events.py` — eventi del calendario
  - `confessions.py` — confessioni e commenti **anonimi**
  - `admin.py` — segnalazioni, ban/unban, risoluzione segnalazioni
  - `pages.py` — tutte le pagine GET (feed, profilo, ricerca, hashtag, calendario, impostazioni, admin)
- `app/templating.py` — helper `render()` + filtri Jinja `linkify`, `humantime`, `datefmt`
- `app/media.py` — salvataggio/validazione upload (immagini/video)

## Pattern e convenzioni
- Le azioni che modificano dati usano **POST + redirect 303** (Post/Redirect/Get).
  I form funzionano **anche senza JavaScript**; il JS è solo progressive enhancement
  (like via fetch, toggle tema, menu).
- Gli errori `HTTPException` su richieste HTML mostrano `error.html`; sulle API JSON.
- L'admin iniziale viene creato/garantito all'avvio (`_seed_admin` in `main.py`).

## ⚠️ Invariante critica: anonimato delle confessioni
Il modello `Confession` **non deve mai** avere un campo che colleghi la riga all'autore
(niente `user_id`, niente hash riconducibile). Il rate-limit anti-spam è **solo in memoria**
(`routers/confessions.py`), mai persistito insieme al contenuto.
Esiste un test che lo verifica: `tests/test_events_confessions.py::test_confession_model_has_no_author_link`.
**Se modifichi le confessioni, questo test deve continuare a passare.**

## Persistenza
Due volumi Docker: `db_data` (Postgres) e `media_data` (upload). I dati sopravvivono
ai riavvii; `docker compose down -v` li azzera.

## Test
```bash
docker run --rm -v "$PWD":/app -w /app python:3.12-slim \
  bash -c "pip install -r requirements-dev.txt && pytest"
```
27 test che coprono auth, permessi ospite, post/like/commenti, hashtag, eventi,
anonimato confessioni, ricerca, segnalazioni, ban.

## Cose da NON fare
- Non aggiungere riferimenti all'autore nelle confessioni.
- Non scrivere segreti nel repo: usano `.env` (gitignored).
- Non rompere il funzionamento senza-JS dei form principali.
