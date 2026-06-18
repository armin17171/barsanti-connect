<p align="center">
  <img src="app/static/img/logo.png" width="96" alt="Barsanti Connect logo">
</p>

<h1 align="center">Barsanti Connect</h1>

<p align="center">
  Il social network dell'Istituto Barsanti — una piccola "Instagram" interna alla scuola.<br>
  Post, hashtag, like, commenti, calendario eventi e confessioni <strong>anonime</strong>.
</p>

---

## ✨ Cosa puoi fare

- 🏠 **Feed pubblico** visibile a chiunque sulla rete (anche senza account)
- ✍️ **Pubblicare post** con testo libero e, se vuoi, **foto, video o audio** (menu a tendina sul tasto Media, file fino a ~1 GB)
- ✏️ **Modificare i propri post** (testo e media); i video partono da soli in loop e muti, l'audio ha un player con onde
- 🔖 **Hashtag automatici**: scrivi `#esempio` e nasce la categoria con tutti i post relativi
- ❤️ **Like** e 💬 **commenti** sotto ogni post
- 📅 **Calendario eventi** a griglia mensile (solo per utenti registrati) + **promemoria** in home per gli eventi imminenti
- 🎭 **Confessioni anonime**: pubblichi senza che nessuno — nemmeno l'amministratore — possa risalire a te (puoi però cancellare le tue)
- 🔍 **Ricerca** per utente, hashtag o evento
- 👤 **Profili pubblici** navigabili con post e commenti di ciascun utente
- 🌗 **Tema chiaro/scuro** commutabile in qualsiasi momento
- 📱 **Installabile sul telefono** come app (PWA)
- 🛡️ **Pannello amministratore**: modera contenuti, gestisce segnalazioni, banna utenti

### Ospite vs utente registrato
| Funzione | Ospite | Registrato |
|---|:---:|:---:|
| Vedere feed, post, profili, hashtag | ✅ | ✅ |
| Pubblicare post / commentare / mettere like | ❌ | ✅ |
| Calendario eventi | ❌ | ✅ |
| Confessioni anonime | solo lettura | scrittura |
| Segnalare contenuti | ❌ | ✅ |

---

## 🚀 Avvio rapido (Docker)

Requisiti: **Docker** e **Docker Compose** su una macchina Linux (Ubuntu).

```bash
# 1. Entra nella cartella del progetto
cd app_social

# 2. Crea il file di configurazione e modifica i valori (password, chiave segreta)
cp .env.example .env
nano .env        # imposta password DB, SECRET_KEY e password admin

# 3. Avvia tutto
docker compose up -d --build
```

Fatto. L'app è raggiungibile da **qualsiasi dispositivo della rete** all'indirizzo:

```
http://IP_DELLA_MACCHINA:8000
```

> Trovi l'IP della macchina con `hostname -I`. Esempio: `http://10.0.0.241:8000`

### Generare una SECRET_KEY sicura
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Primo accesso amministratore
Al primo avvio viene creato automaticamente l'account admin con le credenziali
definite in `.env` (`ADMIN_USERNAME` / `ADMIN_PASSWORD`). **Cambia la password**
dalla pagina *Impostazioni* dopo il primo accesso.

---

## 🛠️ Comandi utili

```bash
docker compose up -d --build     # avvia (ricostruendo l'immagine)
docker compose down              # ferma (i dati restano nei volumi)
docker compose down -v           # ferma ed ELIMINA tutti i dati (reset totale)
docker compose logs -f web       # log dell'applicazione in tempo reale
docker compose restart web       # riavvia solo l'app
docker compose ps                # stato dei container
```

### I dati si perdono al riavvio?
**No.** Post, utenti e media sono salvati in due volumi Docker dedicati
(`db_data` per il database PostgreSQL, `media_data` per i file caricati).
Sopravvivono a `docker compose down` e al riavvio della macchina.
Vengono cancellati **solo** se esegui `docker compose down -v`.

---

## 🔒 Note sulla privacy delle confessioni

Le confessioni sono **realmente anonime**: nella tabella del database **non esiste
alcun campo** che colleghi una confessione all'utente che l'ha scritta (nessun
`user_id`, nessun hash riconducibile). Il login è richiesto solo come barriera
anti-spam, ma l'identità non viene mai salvata.

Conseguenza pratica: l'amministratore **può cancellare** una confessione che viola
le regole, ma **non può sapere chi l'ha scritta** né bannarne l'autore.

Chi pubblica una confessione **può cancellare la propria**: al momento della
pubblicazione il browser riceve un token segreto (salvato solo localmente sul
dispositivo); nel database ne resta solo l'hash, non collegato all'utente. Quindi
il pulsante "elimina" sulle proprie confessioni compare solo sul dispositivo da cui
sono state scritte, senza mai registrare un legame con l'identità.

---

## 🧪 Test

La suite automatica gira in un container isolato (nessuna dipendenza da installare
sulla macchina):

```bash
docker run --rm -v "$PWD":/app -w /app python:3.12-slim \
  bash -c "pip install -r requirements-dev.txt && pytest"
```

Copre: registrazione/login, permessi ospite, post/like/commenti, hashtag,
eventi, **anonimato delle confessioni**, ricerca, segnalazioni e ban.

---

## 🧱 Architettura

- **Backend:** FastAPI (Python) + SQLAlchemy
- **Database:** PostgreSQL (volume dedicato)
- **Frontend:** template Jinja2 + JavaScript vanilla (niente framework pesanti)
- **Sicurezza:** password con **argon2**, sessioni server-side con cookie HttpOnly firmato
- **PWA:** manifest + service worker per l'installazione su mobile

```
app_social/
├── app/
│   ├── main.py            # avvio app, lifespan, error handler
│   ├── config.py          # configurazione da variabili d'ambiente
│   ├── database.py        # engine/sessione SQLAlchemy
│   ├── models.py          # tabelle del database
│   ├── security.py        # argon2 + firma cookie
│   ├── deps.py            # dipendenze (utente corrente, login, admin)
│   ├── routers/           # auth, posts, events, confessions, admin, pages
│   ├── templates/         # pagine HTML (Jinja2)
│   └── static/            # CSS, JS, logo, manifest, service worker
├── tests/                 # suite pytest
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

---

## 📄 Licenza
Progetto scolastico dell'Istituto Barsanti. Uso interno/educativo.
