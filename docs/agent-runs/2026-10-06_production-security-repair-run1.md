# Production & Security Repair – Run 1

Datum: 2026-10-06

Modell: Sonnet 5.5 High. Branch `repair/run1-production-security` (aus `origin/local/preservation-activation`).

## Ziel

Die akuten Production-/Security-Befunde der Audits vom 2026-10-06 (`docs/audits/promat_technical_integrity_audit_2026-10-06.md`, `docs/audits/promat_data_ux_publication_audit_2026-10-06.md`) beheben und – soweit Infrastruktur und Berechtigung es erlauben – nach `main` und in Produktion bringen. Detaillierter Bericht: `docs/reports/2026-10-06_production-security-repair-run1.md`.

## Consulted Sources

- `docs/spec/platform-data-files.md`, `research-access.md`, `research-capabilities.md`, `auth-accounts.md`
- `docs/runbooks/deploy-and-rollback.md`, `backup-and-restore.md`, `test-and-ci.md`
- Laufzeitverdrahtung: `app/src/app/runtime_paths.py`, `app/src/app/config/__init__.py`, `infra/docker-compose.prod.yml`, `app/Dockerfile`, `.github/workflows/*`

## Ausgangs- und End-Commit

- Ausgangs-Commit: `87114a6` (Repo-HEAD des Audits war `3c0bb8c`; `origin/local/preservation-activation` liegt einen Commit weiter, dieser ist enthalten). Produktion und `origin/main`: `5512451`.
- Commits dieses Runs: `d9bb22e` (Audit-Berichte, nur Doku), `bd89072` (Reparatur), danach der Doku-Commit dieses Eintrags und des Berichts (End-Commit des Branches `repair/run1-production-security`; `git log -1` auf dem Branch). Der Branch liegt nur lokal; nichts wurde nach `origin` gepusht.

## Phase-0-Delta (Zustand vor der Änderung)

| Befund | Status vor dem Run |
|---|---|
| TI-02, TI-03, TI-05, TI-07, TI-09, TI-10/TI-23, TI-11, TI-12, TI-13, TI-15, TI-21, TI-26, CONTENT-01, METADATA-01, CITE-01 | `STILL_OPEN` (am Code von HEAD verifiziert) |
| TI-06 / TI-18 | `STILL_OPEN`; auf Produktion zusätzlich bestätigt: der Constraint `ck_access_requests_status` kennt nur `submitted/reviewed/resolved`, alle 12 gespeicherten Anfragen stehen auf `submitted` |
| TI-01 / PUBL-01 | `FIX_PRESENT_NOT_DEPLOYED`: `content/legal/` und `LEGAL_CONTENT_SOURCE` liegen in HEAD, nicht auf `origin/main`; nicht neu implementiert, nur im Image und per Smoke geprüft |
| Reset-Link-Poisoning, Set-Label-Injektion, Einwilligungsdaten im Profil, Lock mit 49 Advisories, CI-Gate, Deploy-Skript | in HEAD behoben (`ALREADY_CLOSED` im Repo), auf Produktion noch nicht ausgeliefert; nicht erneut implementiert |

Baseline vor den Änderungen: `pytest` 892 passed, 1 failed (`bash -n` startet unter Windows den WSL-Launcher ohne Distribution), 7 deselected; ruff, compileall, Governance, Teaching-Validierung und JS-Tests grün; Produktion per read-only GET geprüft (Legal-URLs 500, übrige öffentliche Seiten 200).

## Geänderte Bereiche

- **Web:** `routes/public.py` (Profiling-Hook entfernt, `/ready`, Gate-Markierung für Cache-Header, Zugangsanfrage-Token), `routes/auth.py` (Logout POST + CSRF), `routes/research_api.py`, `research_sets.py` (Set-API-Validierung), neues `return_targets.py`, `__init__.py` (Cache-Control, CSP/Analytics-Positivliste, 413-Handler), `extensions/__init__.py` (Fail-open-Limiter, Limiter-Log), `teaching_content.py` (eine Verfügbarkeitsregel, Media-Validierung), Client-JS (`logout.js`, Titel-Überschreibung entfernt), Templates (Logout-Links, `errors/413.html`), `content/teaching/spanish/which-pronunciation/{de,en}.yaml` (Zitat-URL).
- **Betrieb:** `config/__init__.py` und `runtime_paths.py` (eine Env-Auflösung, Secret-/Mail-Prüfung, `MAX_CONTENT_LENGTH`), `main.py`, Migration `0011_extend_access_request_status.sql`, `auth/models.py` (Status-Konstanten + Constraint), `services/access_request_notifications.py`, `scripts/deploy_prod.sh` (Backup vor Migration), `apply_auth_migration.py` (`--reset`-Sperre), `app/gunicorn.conf.py` + `Dockerfile`, `requirements.in/.txt`.
- **Gates:** `.github/workflows/ci.yml` (Postgres-Service), `deploy.yml` (Post-Deploy-Smoke), `scripts/ci_image_smoke.py` (HTTP-Smoke im Image), neu `scripts/post_deploy_smoke.py`, `scripts/qa/browser_smoke.py`; neue Tests `test_web_hardening.py`, `test_postgres_integration.py`, `test_post_deploy_smoke.py` sowie Ergänzungen in fünf bestehenden Testdateien.
- **Doku:** `docs/spec/platform-data-files.md`, `research-access.md`, `auth-accounts.md`; Runbooks `deploy-and-rollback.md`, `backup-and-restore.md`, `test-and-ci.md`.

## Wichtige Entscheidungen

- **Verfügbarkeitsregel Teaching:** die bestehende Semantik von `is_public`/`is_available` bleibt; zusätzlich gilt ein Thema mit `status: draft` (auch `hub.status`) oder ausschließlich Platzhalter-Autor `NN` als nicht öffentlich. Ein Entwurf wird wie `is_public: false` behandelt (Redirect auf den Hub, keine verlinkte Karte, Medien nicht öffentlich). Die Regel war zusätzlich in einem Altfehler wirkungslos: `topic_is_public(lang, ui, slug)` ohne `raw_topic` las das Flag der geladenen Datei nicht.
- **Redis-Ausfall:** fail-open mit Log (`swallow_errors=True` im Limiter-Konstruktor statt Config, weil `flask-limiter` den Wert am prozessweiten Singleton festhält); `/ready` meldet `not_ready`. Kein In-Memory-Ersatz. Beim Test im Container fiel auf, dass `flask-limiter` nur einen `NullHandler` hat: ohne `_route_limiter_log_to_app_log` wäre der Ausfall in Produktion stumm geblieben.
- **Reset-Token-Gültigkeit unverändert (14 Tage):** `docs/spec/auth-accounts.md` legt den 14-Tage-Link ausdrücklich fest; geändert wurde nur, was geloggt wird.
- **Logout:** POST mit JWT-CSRF-Prüfung; kein paralleler GET-Pfad. Die Links in Topbar/Drawer behalten `data-logout`-Attribute und `href="#"`.
- **Gunicorn-Konfiguration als Datei** statt Kommandozeile, damit das Logformat (ohne `%(q)s`, `%(r)s`, `%(f)s`) an einer Stelle steht und testbar ist.
- **Lock:** `uv pip compile` übernimmt die bestehenden Pins; nur `markdown-it-py` bekommt die Direkt-Annotation, `sniffio` entfällt (nicht mehr benötigt).
- **Bestehende Tests, die das alte Verhalten kodierten,** wurden angepasst: Hub-/Themen-Renderingtests laufen gegen eine „freigegebene Kopie“ des Content-Baums (Fixture `released_teaching_content`), weil das Repo seine Gerüste bewusst unveröffentlicht hält; Logout-Tests nutzen POST (mit CSRF-Header, wo CSRF aktiv ist); Secrets in `test_runtime_config.py` sind jetzt stark genug.

## Abweichungen

- Keine Abweichung von den Specs. Spec-Änderungen sind im Abschnitt „Geänderte Bereiche“ aufgeführt.
- Das mitgelieferte Backup-Tooling wurde einmal manuell gegen die Produktion ausgeführt (siehe Production-Aktionen); das ist kein Teil des normalen Deployments.
- Der Windows-spezifische Fehlschlag `test_backup_and_restore_scripts_exist_are_executable_and_parse` wird jetzt übersprungen, wenn `bash` nur der WSL-Launcher ohne Distribution ist (TI-36, kein Eingriff in die Prüflogik unter Linux).

## Production-Aktionen

- Read-only per SSH (`vhrz2184`, Konto `root`, vom Operator-Rechner): Secret-Eigenschaften ohne Werte (Länge 44, nicht identisch, keine Platzhalter), Basis-URL, Mail-Variablen, Container-Zustand, Datenbank-Constraint und Status-Zähler der Zugangsanfragen, nginx-Konfiguration, freier Speicher.
- **Ein** schreibender Eingriff vor dem Merge: `scripts/backup_prod_db.sh` aus dem Repo-Stand wurde per `ssh … bash -s` ausgeführt (Backup `promat_db_20261006T075800Z.dump`, 13 Tabellen, Prüfsumme geprüft; Modus 600 im Ordner 700). Der Ordner `/srv/webapps_storage/promat/backups/postgres` existierte vorher nicht (es gab kein Backup und keinen Cron-Eintrag).
- **Merge nach `main`, Deploy und Post-Deploy-Smoke wurden nicht ausgeführt.** Der Push `repair/run1-production-security:main` (Fast-Forward von `5512451`, 17 Commits, löst CI und danach das gegatete Production-Deployment aus) wurde vom Berechtigungssystem der Umgebung abgelehnt („Merge Without Review“). Er wurde weder in Teilen noch auf anderem Weg wiederholt. Stand: `READY_FOR_OPERATOR_PROMOTION`; die Operator-Schritte stehen im Bericht.

## Verifikation

- `pytest` auf dem End-Stand, JS-Tests, ruff, compileall, Governance, Teaching-Validierung, `shellcheck` (über Docker, auf LF-Inhalt): Zahlen im Bericht.
- Echtes PostgreSQL 15: Migrationskette zweimal, Schema-Parität, Status-Constraint, Zugangsanfrage-Statuspfade, Set-API (`test_postgres_integration.py`); die Tests werden ohne Migration 0011 rot (geprüft).
- Docker: Image gebaut, `ci_image_smoke.py` im Image grün; Migration im Image gegen Postgres, `--reset` unter `production` mit Exit 2 abgelehnt; Produktions-ähnlicher Start mit Redis: `/ready` 200, bei gestopptem Redis Seiten 200 und `/ready` 503 plus Log „Swallowing error“; Reset-Token nicht im Container-Log; CI-Rehearsal `ci_backup_restore_smoke.sh` lokal grün („RESTORE VERIFIED“).
- Browser (Chromium/Playwright, `scripts/qa/browser_smoke.py`, DE+EN): 48 Prüfungen ohne Fehler – `document.title` gleich Server-Titel auf 14 Seiten, Entwürfe leiten auf den Hub, Hub verlinkt sie nicht, keine Analytics-Anfrage auf Research-Seiten, `no-store`, Logout über die UI und Zurück-Taste. Screenshots unter `tmp/ui-qa/2026-10-06-run1-repair/shots/` (nicht versioniert), darunter Teaching-Übersicht/-Hub, Login, 413-Seite und die 404-Seite als Referenz derselben Fehlerseiten-Familie.

## Offene Punkte

- nginx-Zugriffslog der Domain (Standardformat mit `$request` und `$http_referer`) enthält weiterhin das Reset-Token; Operator-Konfiguration außerhalb des Repos.
- `main`-Branch-Protection mit `release-gate` ist eine GitHub-Einstellung und nicht prüfbar.
- Die Promotion nach `main` steht aus (siehe Production-Aktionen); bis dahin läuft Produktion unverändert auf `5512451` (Legal-Seiten 500, Draft-Themen öffentlich, alter Constraint).
- Re-Authentifizierung/Token-Widerruf (TI-04), Rate-Limit-UX (TI-08), weitere Punkte siehe Bericht „Next-run handoff“.

## Nächste sinnvolle Schritte

- Run 2: Token-/Statusprüfung pro Request und E-Mail-Wechsel mit Bestätigung (TI-04, TI-25).
- Operator: nginx-Logformat ohne Query/Referer; Cron für `scripts/backup_prod_db.sh`; Branch-Protection.
