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
- [x] Pubblicazione su **GitHub** → https://github.com/armin17171/barsanti-connect (pubblico)

## Aggiornamenti successivi
- [x] **Immagine profilo** caricabile dagli utenti (upload/rimozione in Impostazioni, mostrata in feed/commenti/profilo/ricerca) — *test: `test_upload_and_show_avatar`, `test_reject_non_image_avatar`, `test_remove_avatar`*
- [x] Migrazione idempotente `avatar_path` (nessuna perdita dati su DB esistente) — *verificato sul Postgres live*
- [x] **Toggle tema solo in Home (switch della luce) e Impostazioni**, rimosso dal menu laterale — *verificato sul live*

## Aggiornamenti — secondo blocco
- [x] **Registrazione**: conferma password + pulsante 👁️ mostra/nascondi (anche login e impostazioni) — *test: `test_register_password_mismatch`*
- [x] **Upload fino a ~1 GB** (`MAX_UPLOAD_MB=1024`) + nuovi tipi **audio** — *test: `test_large_upload_allowed`, `test_audio_post_shows_player`*
- [x] **Composer**: menu a tendina su "Media" per scegliere foto/video/audio — *test: `test_home_composer_has_media_menu`*
- [x] **Video** in autoplay + loop + muto (con sblocco audio via controlli)
- [x] **Player audio** con onde grafiche, play/pausa e seek
- [x] **Modifica dei propri post** (testo + media), non di altri — *test: `test_edit_own_post`, `test_cannot_edit_others_post`*
- [x] **Confessioni**: cancellazione dall'autore via token segreto (hash nel DB, anonimato intatto) + admin — *test: `test_confession_author_delete_with_token`, `test_admin_delete_confession_without_token`*
- [x] **Calendario reale** a griglia mensile con navigazione — *test: `test_calendar_grid_renders`*
- [x] **Popup eventi imminenti** in home (prossimi 7 giorni), dismissibile — *test: `test_upcoming_event_popup_for_user`*
- [x] **Pulsante tema flottante** in basso a destra, solo icona (rimosso dal menu) — *test: `test_theme_fab_present`*
- [x] **Biografia adattiva** al testo, senza resize manuale — *test: `test_settings_has_avatar_and_autogrow`*
- [x] Migrazione idempotente `delete_token_hash` (dati preservati) — *verificato sul Postgres live*

---

### Esito ultima esecuzione test
```
42 passed in 9.43s
```
