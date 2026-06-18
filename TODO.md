# ✅ TODO / Avanzamento — Barsanti Connect

Legenda: `[x]` fatto e **testato** · `[ ]` da fare

## Infrastruttura
- [x] Struttura progetto (app/ routers/ templates/ static/ tests/)
- [x] Dockerfile (Python 3.12-slim)
- [x] docker-compose con servizio **web** + **PostgreSQL**
- [x] Volume dedicato DB (`db_data`) — i dati sopravvivono al riavvio ✔ *verificato*
- [x] Volume dedicato media (`media_data`) — gli upload sopravvivono al riavvio
- [x] `.env.example` + generazione `.env` con segreti casuali
- [x] `.gitignore` / `.dockerignore` (segreti e media esclusi da git)

## Funzionalità obbligatorie
- [x] Pagina web visibile a **tutti** (anche ospiti) — *test: `test_homepage_visible_to_guest`*
- [x] Pubblicare post (testo libero, media **opzionale**) — *test: `test_create_post_with_hashtag`, `test_empty_post_rejected`*
- [x] Registrazione utente univoco (username + bio + password) — *test: `test_register_and_session`, `test_duplicate_username_rejected`*
- [x] Password protette con **argon2** + sessioni cookie HttpOnly
- [x] Modalità **ospite** con funzioni limitate — *test: `test_guest_cannot_post`, `test_guest_cannot_like`, `test_guest_cannot_create_event`, `test_guest_cannot_view_calendar`*
- [x] Post visibili a tutti — *test: feed in `test_create_post_with_hashtag`*
- [x] **Persistenza** su volume/DB dopo riavvio Docker — *verificato end-to-end (post + utente + hashtag sopravvivono a `down`/`up`)*
- [x] Ricerca per **utente / hashtag / evento** — *test: `test_search_users_hashtags_events`*
- [x] **Calendario** eventi scolastici, postabili solo da registrati — *test: `test_create_event`, `test_guest_cannot_create_event`*
- [x] **Confessioni anonime** non ricollegabili all'autore — *test: `test_confession_model_has_no_author_link`, `test_confession_is_anonymous_in_db`*

## Funzionalità opzionali
- [x] **Like** e **commenti** sotto i post (sezione commenti dedicata) — *test: `test_like_toggle`, `test_comment_flow`*
- [x] **Hashtag** automatici da `#testo` + pagina categoria — *test: `test_create_post_with_hashtag`*
- [x] **Pagine profilo pubbliche** (post + commenti) — *test: `/u/<username>` 200 + `test_search`*
- [x] **Tema chiaro/scuro** commutabile e persistente (localStorage)
- [x] Resa **mobile-first** + **PWA installabile** (manifest + service worker)

## Moderazione / Admin
- [x] Pannello admin (utenti + coda segnalazioni) — *test: `test_report_and_admin_queue`, `test_non_admin_cannot_open_admin`*
- [x] Elimina post/commenti/eventi/confessioni (autore o admin) — *test: `test_delete_post_permissions`, `test_only_admin_deletes_confession`*
- [x] **Ban** utenti + revoca sessione immediata — *test: `test_ban_revokes_session_and_blocks_posting`, `test_cannot_ban_admin`*
- [x] Funzione **segnala** per utenti registrati — *test: `test_report_and_admin_queue`*

## Test & qualità
- [x] Suite automatica **pytest**: **27 test, tutti verdi** (eseguiti in container Python 3.12)
- [x] Zero warning di deprecazione sul codice applicativo
- [x] Verifica persistenza con riavvio reale dei container
- [x] Smoke test HTTP di tutte le pagine + asset statici

## Documentazione & consegna
- [x] `TODO.md` (questo file)
- [x] `README.md` (guida d'uso e avvio)
- [x] `CLAUDE.md` (contesto progetto)
- [ ] Pubblicazione su **GitHub** (in attesa del login `gh auth login` da parte tua)

---

### Esito ultima esecuzione test
```
27 passed in 5.76s
```
