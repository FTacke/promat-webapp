# Production & Security Repair – Run 1: Repair- und Validation-Bericht

Datum: 2026-10-06. Nicht-normativer Bericht; aktive Regeln stehen in `docs/spec/`. Run-Journal: `docs/agent-runs/2026-10-06_production-security-repair-run1.md`.

**Endstatus des Runs: `READY_FOR_OPERATOR_PROMOTION`.** Alle Reparaturen sind im Repo umgesetzt und lokal, im gebauten Image und im Browser verifiziert. Der Merge nach `main` (und damit das Production-Deployment) wurde **nicht** durchgeführt: der Push wurde vom Berechtigungssystem der Umgebung abgelehnt und nicht auf anderem Weg wiederholt. Produktion läuft unverändert auf `5512451`.

## Stand

| Punkt | Wert |
|---|---|
| Branch | `repair/run1-production-security` (nur lokal, nicht gepusht) |
| Ausgangs-Commit | `87114a6` (Repo-HEAD des Audits `3c0bb8c` plus der eine Commit von `origin/local/preservation-activation`) |
| Commits | `d9bb22e` Audit-Berichte (Doku) · `bd89072` Reparatur · Doku-Commit mit diesem Bericht (= Branch-HEAD) |
| `origin/main` / Produktion | `5512451`; der Branch ist ein reiner Fast-Forward davon (17 Commits) |

## Phase 0: Reconciliation (Zustand vor den Änderungen)

- `origin/main` = `5512451` enthält das Reparatur-Set `54a5f2c`…`b454802` nicht; HEAD enthält es. `content/legal/` ist in HEAD vorhanden (Fix nicht neu implementiert).
- Am Code von HEAD verifiziert: der Profiling-Hook, die doppelte `next`-Validierung, fehlende Cache-Header, die globale GoatCounter-Einbindung, die Set-API-Lücken, die Env-Auflösung in `main.py`, der Deploy ohne Backup, das Access-Log-Format und das nur transitive `markdown-it-py` waren **offen**.
- Produktion read-only geprüft (siehe unten): der Status-Constraint `ck_access_requests_status` ist der alte (`submitted/reviewed/resolved`); alle 12 gespeicherten Zugangsanfragen stehen auf `submitted`.
- Baseline vor den Änderungen: `pytest` 892 passed, 1 failed (Windows/WSL-`bash -n`), 7 deselected; ruff, compileall, Governance (7/7), Teaching-Validierung, JS 11/11 grün.

## Befund-Tabelle

`CLOSED` heißt hier: im Repo behoben und verifiziert, **nicht** ausgeliefert. `CLOSED_AND_DEPLOYED` wird nach der Promotion erreicht und konnte in diesem Run nicht vergeben werden.

| Finding | Ausgangsstatus | Maßnahme | Test/Beleg | Endstatus |
|---|---|---|---|---|
| TI-02 Profiling-Hook (`?_profile=1`) | `STILL_OPEN` | Hook, Server-Timing-Header und die durchgereichte `profile`-Plumbing komplett entfernt | `test_player_route_never_registers_engine_listeners` (120 anonyme Requests, Listenerzahl unverändert), `test_profiling_hook_is_gone_from_production_code` | `CLOSED` |
| TI-01 / PUBL-01 Legal-Seiten, Produktionsstand | `FIX_PRESENT_NOT_DEPLOYED` | Fix (`content/legal/`) nicht neu implementiert, aber verifiziert; Image-Smoke und Post-Deploy-Smoke prüfen die fünf Legal-URLs künftig | Image-Smoke im gebauten Image grün (alle fünf URLs 200 über `create_app`); `test_post_deploy_smoke.py` (4); Produktion liefert bis zur Promotion weiter 500 | `BLOCKED_EXTERNAL` |
| CONTENT-01 öffentliche Entwürfe | `STILL_OPEN` | Eine Verfügbarkeitsregel in `teaching_content.topic_is_public`: `status: draft` / `hub.status: draft` oder nur Autor `NN` ⇒ nicht öffentlich (Redirect auf den Hub, keine verlinkte Karte, Medien nicht öffentlich); Altfehler behoben (Flag der geladenen Datei wurde nicht gelesen); Spec ergänzt | `test_web_hardening.py`: Regel über den realen Content-Baum (alle 14 Themen-Editionen), 12 Regelfälle; Browser DE+EN: Entwürfe leiten auf den Hub, Hub verlinkt sie nicht | `CLOSED` |
| METADATA-01 `document.title` | `STILL_OPEN` | Ursache waren **zwei** Module (`navigation/page-title.js`, `core/ui.js::initPageTitleAndScroll`): das erste gelöscht, das zweite auf reines Scroll-Verhalten reduziert (`initScrollIndicator`) | Test über den JS-Baum (kein `document.title =` außer Fragment-Navigation des Players), 7 Server-Titel-Tests; Browser: `document.title` == Server-`<title>` auf 14 Seiten (DE+EN), keine Konsolenmeldung | `CLOSED` |
| CITE-01 Zitat-URL | `STILL_OPEN` | `which-pronunciation` de/en: Zitat-URL = `https://pronunciation-matters.de/{ui_lang}/teaching/spanish/which-pronunciation` (non-`www`, kein Schlusspunkt in `copy_text`); Spec ergänzt | `test_topic_citation_urls_point_at_their_own_page_on_the_canonical_host` (Pfad == Seite, kanonischer Host, GET 200 ohne Redirect), `test_rendered_citation_box_exposes_the_page_url`; Post-Deploy-Smoke wiederholt das live | `CLOSED` |
| TI-03 Open Redirect | `STILL_OPEN` | Neues `return_targets.safe_return_target` ersetzt `_safe_next` und `_safe_next_value`; nur ein führender `/`, keine Backslashes/Steuerzeichen, bis zu drei Dekodierstufen geprüft, Login-/Logout-/Request-Ziele abgelehnt | 27 Ablehnungs- und 6 Annahmefälle (`////evil`, `%2F`-/`%252F`-Varianten, Backslash, Schemata, CRLF, Query), 4 HTTP-Fälle als angemeldeter Nutzer, Login-Roundtrip mit legitimem Ziel | `CLOSED` |
| TI-05 Cache-Control | `STILL_OPEN` | Zentral im `after_request`: geschützt (`/auth/`, `/admin`, `/api/`, `/login`, durch das Research-Gate markierte Antworten) ⇒ `private, no-store` + `Vary: Cookie`; Audio `private, no-cache`; öffentliche Seiten und `/static/` unberührt | 4 Header-Tests im Gesamtsystem; Browser DE+EN: geschützte Antwort `no-store`, nach UI-Logout zeigt Zurück nicht die Seite (landet auf `/login?next=…`) | `CLOSED` |
| TI-07 GoatCounter | `STILL_OPEN` | Positivliste öffentlicher Pfade; CSP erlaubt `gc.zgo.at`/`goatcounter.com` nur dort, sonst `'self'`; Spec ergänzt | 11 öffentliche und 9 geschützte/Konto-Pfade (jeweils eingeloggt und anonym), CSP-Test; Browser: keine Drittanfrage auf Research-Seiten | `CLOSED` |
| TI-09 Set-API | `STILL_OPEN` | `ResearchConfigError` ⇒ 400; `items`/`sessions` Pflicht (`PUT` ohne Feld/Body ⇒ 400, nur `[]` leert); `label` ≤ 200, `note` ≤ 4000; `MAX_CONTENT_LENGTH` 1 MiB; 413-Handler ohne Folgeexception (`request.values` abgesichert) mit lokalisierter Seite `errors/413.html` | 13 Set-API-Tests inkl. Nicht-Leeren, 413 JSON+HTML; Postgres-Roundtrip; Screenshots DE+EN der 413-Seite neben der 404-Seite derselben Familie | `CLOSED` |
| TI-21 Teaching-Media-Route | `STILL_OPEN` | Sprache muss Manifest haben (`[a-z]+`), Slug `[a-z0-9]+(-[a-z0-9]+)*`, `media_type` aus der Liste, Pfad unter `{topic}/media/{type}/`, nur Themen mit öffentlicher Edition | 12 Traversal-/Identifier-Fälle ⇒ 404, Resolver-Test, Entwurfs-Medien ⇒ 404, legitime Datei weiter 200 | `CLOSED` |
| TI-26 Logout | `STILL_OPEN` | `POST /auth/logout` (+ Alias) mit JWT-CSRF-Prüfung bei vorhandenem Cookie; kein GET; `logout.js` und Templates angepasst, kein GET-Fallback | 4 Tests (GET 405, ohne Header 403, mit Header 303, kaputtes Cookie wird gelöscht), bestehende Auth-Tests auf POST umgestellt; Browser: Logout über die UI | `CLOSED` |
| TI-06 Zugangsanfrage / Constraint | `STILL_OPEN` (Produktion bestätigt) | Migration `0011` (idempotent) erweitert den CHECK; Status-Konstanten in `auth/models.py` mit Modell-Constraint; Nachrichtenbau in den Fehlerbereich; Statusupdate-Fehler nach gesendeter Mail wird nicht als Zustellfehler gemeldet; Token einmalig (Nonce in der Session); Mail-Konfiguration beim Start geprüft | 8 neue SQLite-Tests, 4 Postgres-Tests; die Postgres-Tests werden ohne `0011` rot (geprüft: 4 Fehlschläge) | `CLOSED` |
| TI-18 Postgres-Lücke der Tests | `STILL_OPEN` | `test_postgres_integration.py` (Migrationskette zweimal, Schema-Parität Modelle↔DB, Status-Constraint, Statuspfade, Set-API); Service-Container und `PROMAT_TEST_POSTGRES_URL` im CI-Python-Job; Meta-Test sichert das Gate | 7 Postgres-Tests grün gegen Postgres 15; `test_python_job_provides_postgres_…` | `CLOSED` |
| TI-11 Config fail-closed | `STILL_OPEN` | Eine Auflösung `resolve_environment_name` (Argument, `PROMAT_ENV`, `FLASK_ENV`, `APP_ENV`, sonst `production`) für Config, Runtime-Pfade und `main.py`; Secrets: ≥ 32 Zeichen, nicht schwach/repetitiv, JWT ≠ Flask; keine Werte in Meldungen | über 20 neue Config-Tests (u. a. nur `PROMAT_ENV=production` ⇒ kein Debug, kein Default `development`) | `CLOSED` |
| TI-12 Backup vor Migration, `--reset` | `STILL_OPEN` | `deploy_prod.sh`: verifiziertes Backup vor der Migration, Abbruch bei Fehler (nur Erstinstallation ohne `users`-Tabelle überspringt); `apply_auth_migration.py --reset` nur in dev/test (Exit 2) | Reihenfolge-Test, Reset-Test; im Image: `--reset` unter `production` ⇒ Exit 2; Backup-Rehearsal lokal grün („RESTORE VERIFIED“); `shellcheck` sauber | `CLOSED` |
| TI-10 Redis-Ausfall | `STILL_OPEN` | Fail-open (`swallow_errors=True`, kein In-Memory-Ersatz), Redis-Timeouts 1 s, Limiter-Log wird an den App-Log geleitet (sonst stumm: nur `NullHandler`) | Test mit totem Redis (Seiten 200, Log-Eintrag in `promat-web.log`, `/ready` 503); im Container: Seiten 200 bei gestopptem Redis, Eintrag „Swallowing error“, `/ready` wieder 200 | `CLOSED` |
| TI-23 `/ready` | `STILL_OPEN` | Echte Redis-Prüfung (`storage.check()`), nur Codes statt Exception-/Hostdetails im JSON, Schreibprobe durch `os.access` ersetzt | 4 Tests (kein Leck von Host/Pfad/Fehlertext, keine Probe-Datei) | `CLOSED` |
| TI-13 Reset-Token im Log (Container) | `STILL_OPEN` | `app/gunicorn.conf.py`: Access-Log ohne Query und Referer; Reset-Seite sendet `Referrer-Policy: no-referrer`; Gültigkeit unverändert 14 Tage (Spec) | Format-Test; im Container: Request mit `?token=…` taucht im `docker logs` nicht auf | `CLOSED` |
| TI-13 Reset-Token im nginx-Log | `STILL_OPEN` | außerhalb des Repos: nginx nutzt das Standard-Log (`combined`, mit `$request` und `$http_referer`); Prüfpunkt im Runbook ergänzt | read-only `nginx -T` auf dem Server | `BLOCKED_EXTERNAL` |
| TI-15 `markdown-it-py` | `STILL_OPEN` | in `requirements.in`; Lock mit `uv pip compile` regeneriert, **keine Versionsänderung** (nur Reihenfolge/Annotation; `sniffio` entfällt) | Image baut, `import markdown_it` im Image 4.0.0, Suite grün | `CLOSED` |
| Reset-Link-Poisoning, Label-Injektion, Einwilligungsdaten im Profil (Teil von TI-01) | im Repo `ALREADY_CLOSED` | nicht neu implementiert; Verifikation über die vorhandenen Tests in der Suite | Suite grün | `ALREADY_CLOSED` |

Geschlossen (`CLOSED`): 18 · `BLOCKED_EXTERNAL`: 2 (TI-01 Auslieferung, TI-13 nginx) · `ALREADY_CLOSED`: 1.

## Production status

- **Commit auf `main`: keiner.** `origin/main` und Produktion stehen auf `5512451`.
- **Deployment: nicht ausgeführt.** Der Push `git push origin repair/run1-production-security:main` wurde abgelehnt (Berechtigungssystem, „Merge Without Review“) und bewusst nicht erneut versucht.
- **Legal-Smoke / Security-Smoke gegen Produktion nach Deploy: nicht möglich**, da nichts ausgeliefert wurde. Ergebnis der read-only Prüfung am 2026-10-06 vor den Änderungen: `/impressum`, `/{de,en}/impressum`, `/{de,en}/privacy` liefern 500; `/de`, `/de/teaching`, `/de/research/spanish/design` 200; geschützte Research-Routen leiten auf `/login?next=…`; `/ready` ist öffentlich (alte Fassung).
- **Vorprüfungen auf dem Server (read-only per SSH, keine Werte ausgegeben):**
  - `JWT_SECRET_KEY` und `FLASK_SECRET_KEY`: je 44 Zeichen, ≥ 30 verschiedene Zeichen, kein Platzhalter, **verschieden** ⇒ erfüllen die neue Startprüfung.
  - `PROMAT_PUBLIC_BASE_URL=https://pronunciation-matters.de`; `AUTH_ACCESS_REQUEST_EMAIL`, `AUTH_ACCESS_REQUEST_FROM_EMAIL` und `AUTH_ACCESS_REQUEST_SMTP_HOST` gesetzt, keine Platzhalter; `AUTH_MAIL_BACKEND` ist nicht gesetzt (Standard `smtp`, passt zur Prüfung); `RATE_LIMIT_STORAGE_URI` Redis; `PROMAT_ENV=production`.
  - Container `promat-web-prod`, `promat-db-prod`, `promat-rate-limit-prod` laufen seit 25 h healthy; Runner `vhrz2184-promat-prod` aktiv (Benutzer `root`); 19 GB frei; `python3` 3.10 vorhanden (für den Post-Deploy-Smoke).
  - Datenbank: alter Constraint (siehe oben), 12 Anfragen, alle `submitted`.
  - **Es gab weder Backup-Ordner noch Backup-Cron** (`/srv/webapps_storage/promat/backups/postgres` fehlte).
- **Einziger schreibender Eingriff:** ein verifiziertes Backup vor der geplanten Migration, ausgeführt mit dem Repo-Skript per `ssh … bash -s` (`promat_db_20261006T075800Z.dump`, 87 910 Byte, 13 Tabellen, `sha256sum -c` OK; Dateimodus 600, Ordner 700). Es ist der Restore-Punkt des jetzigen Produktionsstands.
- **Bekannte verbleibende Produktionsabweichungen** (bis zur Promotion): Legal-Seiten 500; Draft-Themen öffentlich (`liaison`, `gleitlaute`, `nasalvokale`, `r-am-silbenende`); Zitat-URL der Themenseite zeigt auf die Domain-Wurzel (`www`); Titel nach JavaScript konstant; GoatCounter auf Research-Seiten; Profiling-Hook, Open Redirect, fehlende Cache-Header und die weiteren Befunde dieser Tabelle aktiv; Zugangsanfragen bleiben auf `submitted`. nginx loggt Query und Referer (auch nach der Promotion).

### Operator-Schritte bis `CLOSED_AND_DEPLOYED`

1. Entscheidung und Review des Branches `repair/run1-production-security` (17 Commits über `5512451`; Fast-Forward, kein Merge-Commit nötig).
2. `git push origin repair/run1-production-security:main` (oder PR) – löst `CI` aus; `release-gate` muss grün werden (Python mit Postgres-Service, JS, Docker mit HTTP-Smoke im Image, Backup/Restore).
3. Danach startet `Deploy production` per `workflow_run` auf dem Commit `head_sha`: Konfigurationsprüfung → **Backup** → Migrationen (inkl. `0011`) → Austausch von `web` → Health/Ready → **Post-Deploy-Smoke**. Die Server-Vorprüfungen oben sind bereits erfüllt.
4. Danach manuell: `python3 scripts/post_deploy_smoke.py --base-url https://pronunciation-matters.de` und optional `scripts/qa/browser_smoke.py` (mit `PROMAT_QA_USER`/`PROMAT_QA_PASSWORD`); Legal-URLs 200, Entwürfe nicht öffentlich, Zitat-URL, Login-Redirect.
5. Operator-seitig (unabhängig vom Merge): nginx-Logformat ohne Query und ohne Referer (`$uri` statt `$request`, kein `$http_referer`), Cron für `scripts/backup_prod_db.sh`, Branch-Protection mit `release-gate`.
6. Nach erfolgreichem Deploy diesen Bericht ergänzen (Endstatus `CLOSED_AND_DEPLOYED`, Commit auf `main`, Smoke-Ergebnis).

Rollback bleibt das Neu-Deployment des früheren Commits (`5512451`); das Backup oben deckt die Migration `0011` (additiv, idempotent) ab.

## Tests

| Prüfung | Ergebnis |
|---|---|
| `pytest` (End-Stand, mit Postgres 15 über `PROMAT_TEST_POSTGRES_URL`) | **1070 passed, 1 skipped, 7 deselected** (`data`-Marker) in 117 s; der Skip ist `test_backup_and_restore_scripts_exist_are_executable_and_parse` (unter Windows startet `bash` den WSL-Launcher ohne Distribution; auf Linux läuft der Test) |
| davon neu | 139 Tests in drei neuen Dateien (`test_web_hardening.py` 128, `test_postgres_integration.py` 7, `test_post_deploy_smoke.py` 4); weitere Ergänzungen in `test_runtime_config.py`, `test_auth_phase1.py` (Zugangsanfrage), `test_deploy_and_backup_scripts.py` und `test_ci_workflows.py`; insgesamt +178 Tests gegenüber der Baseline (893 → 1071 ausgewählt) |
| Ohne Postgres-URL (lokal Standard) | die 7 Postgres-Tests werden übersprungen; in CI läuft der Service-Container |
| JS | `node --test app/tests/js/*.test.mjs`: 11/11 |
| `ruff check .`, `compileall`, Governance (7/7), Teaching-Validierung (4 Sprachen) | grün |
| `shellcheck --severity=warning` (Docker, LF-Inhalt) auf `deploy_prod.sh`, `backup_prod_db.sh`, `restore_db_dump.sh`, `verify_db_restore.sh`, `ci_backup_restore_smoke.sh` | sauber |
| Docker | Image aus dem Arbeitsstand gebaut; `ci_image_smoke.py` im Image: Legal-/öffentliche Seiten 200, Entwürfe nicht öffentlich, geschützte Seiten ⇒ Login |
| PostgreSQL | Migration im Image zweimal gegen echtes Postgres 15; Constraint danach mit fünf Werten; `--reset` unter `production` ⇒ Exit 2 |
| Produktions-ähnlicher Containerstart (Gunicorn, Postgres, Redis) | `/ready` 200; Legal-URLs 200; Entwurfs-Thema 302 auf den Hub; Reset-Token nicht im Log; Redis-Ausfall: Seiten 200 (+ ca. 2,5 s Wartezeit pro Request, Namensauflösung des gestoppten Containers), `/ready` 503, Logeintrag, danach wieder 200 |
| Backup/Restore-Rehearsal (`ci_backup_restore_smoke.sh`, lokal, echte Migrationen) | „RESTORE VERIFIED“, 13 Tabellen |
| Browser (Chromium, `scripts/qa/browser_smoke.py`, DE+EN, gegen den Container) | 48 Prüfungen, 0 Fehler; Screenshots in `tmp/ui-qa/2026-10-06-run1-repair/shots/` (nicht versioniert) |

Verbleibende Fehlschläge: keine. Zur Einordnung des Skips siehe oben. Nicht ausgeführt: ein CI-Lauf auf GitHub (Push abgelehnt); die dortigen Jobs entsprechen den lokal ausgeführten Prüfungen.

## Next-run handoff

Nur Punkte, die nach diesem Run relevant bleiben:

- **Promotion nach `main`** (Operator-Schritte oben); danach Bericht und Run-Journal auf `CLOSED_AND_DEPLOYED` ziehen.
- **Run 2 (außerhalb des Scopes, abhängig vom jetzigen Stand):** TI-04 (Token-/Statusprüfung pro Request, E-Mail-Wechsel mit Bestätigung) und TI-25 (Admin-Invarianten). Die jetzige Logout-Änderung widerruft das Token nicht; Spec `auth-accounts.md` sagt das ausdrücklich.
- **Rest aus diesem Scope:** nginx-Log (Operator). Die 14-Tage-Gültigkeit der Reset-/Einladungslinks bleibt laut Spec; das Token ist nur noch im nginx-Log sichtbar, bis dieses umgestellt ist.
- **Neu entdeckt:**
  - Auf der Produktion existierte kein Backup und kein Backup-Cron (Ordner fehlte); das Deployment erzeugt jetzt eines, ein Cron fehlt weiterhin.
  - `flask-limiter` loggt sonst nirgends hin (NullHandler); der Fix steckt in `extensions/__init__.py`.
  - Bei Redis-Ausfall kostet jeder Request die fehlschlagende Verbindung (hier ca. 2,5 s); fail-open ist damit funktional, aber langsam (TI-08/TI-10 Folge: Rate-Limit-Strategie).
  - Eine Form-Anfrage über 1 MiB wird von Gunicorn mit 413 beantwortet, der Browser sieht dabei teils `ERR_CONNECTION_RESET`; nginx erlaubt global `client_max_body_size 50m`. Gegebenenfalls nginx auf denselben Grenzwert setzen.
  - Roh-429-Seite („429 Too Many Requests“) beim Auslösen des `5 per hour`-Limits der Zugangsanfrage (bekannt als TI-08).
  - Der Landing-`<title>` lautet „Pronunciation Matters · Pronunciation Matters“ (Daten-/UX-Audit); der englische Zitat-Titel („Which pronunciation should be taught?“) weicht vom Seitentitel („…should you teach?“) ab (CITE-02, Publication-Architektur, Run 4).
  - `infra/docker-compose.prod.yml` reicht `AUTH_MAIL_BACKEND`/`AUTH_MAIL_FROM_EMAIL` nicht an den Container durch; das Template nennt `sendmail`, wirksam ist der Standard `smtp`.
