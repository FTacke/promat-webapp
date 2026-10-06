# Production Promotion & Verification – Run 1.5

Datum: 2026-10-06. Kein Repair-Run; keine Code-Änderung. Grundlage: `2026-10-06_production-security-repair-run1.md` und `docs/reports/2026-10-06_production-security-repair-run1.md`.

## Git / Deployment

| Punkt | Wert |
|---|---|
| Ausgangs-Stand | Branch `repair/run1-production-security` = `606e3f9`, Working Tree sauber, `origin/main` = `5512451`, kein fremder Commit auf `main`; reiner Fast-Forward (18 Commits) |
| Delta zu Run 1 | keines |
| Gates vor dem Push | die in Run 1 auf diesem Code-Stand ausgeführten (pytest 1070 passed/1 Windows-Skip, JS 11/11, ruff, compileall, Governance, Teaching-Validierung, shellcheck, Postgres-15-Integration, Docker-Build + Image-Smoke, Browser-Smoke DE+EN); seit `bd89072` nur Doku-Dateien hinzugekommen |
| Server-Vorprüfung | Secrets 44 Zeichen/verschieden/keine Platzhalter, Basis-URL HTTPS, Mail-Variablen gesetzt, 19 GB frei, DB/Redis/Web healthy (siehe Run 1; unverändert) |
| Push | `git push origin repair/run1-production-security:main` (`5512451..606e3f9`), kein Force |
| CI / `release-gate` | grün (alle Jobs inkl. Postgres-Service) |
| Deploy | `Deploy production` per `workflow_run` auf `606e3f9`: erfolgreich (Konfigurationsprüfung → Backup → Migration → Austausch `web` → Health/Ready → Post-Deploy-Smoke) |
| Production-Commit | `606e3f90e651…` (Checkout `/srv/webapps/promat/app`, `git rev-parse HEAD`) = `main` zum Zeitpunkt des Deploys |
| Backups | Deploy-Backup `promat_db_20261006T083632Z.dump` (Prüfsumme OK) vor der Migration; zusätzlich Run-1-Backup `…T075800Z` |

Danach wurde dieser Doku-Commit gepusht (löst einen weiteren, inhaltlich identischen Deploy aus). Endgültige SHAs: siehe Abschnitt „Abschluss“.

## Production Verification

`VERIFIED_PRODUCTION` = am Live-System (`https://pronunciation-matters.de`) beobachtet.

| Run-1-Punkt | Status | Beleg |
|---|---|---|
| TI-01 Legal-Seiten | `VERIFIED_PRODUCTION` | `/impressum`, `/{de,en}/impressum`, `/{de,en}/privacy` je 200 |
| CONTENT-01 Entwürfe | `VERIFIED_PRODUCTION` | `/de/teaching/french/liaison` ⇒ 302 auf den Hub; Post-Deploy-Smoke prüft alle Entwurfs-Editionen (nicht 200) |
| METADATA-01 Titel | `VERIFIED_PRODUCTION` | `page-title.js` ⇒ 404; `ui.js` ohne Titel-Zuweisung; Server-`<title>` je Route (DE „Welche Aussprache unterrichten?“, EN „Which pronunciation should you teach?“). Die Titel nach JS-Ausführung wurden in Produktion nicht per Browser gemessen (nur im identischen Container in Run 1) |
| CITE-01 Zitat-URL | `VERIFIED_PRODUCTION` | `data-copy-text` nennt `https://pronunciation-matters.de/de/teaching/spanish/which-pronunciation`; Smoke prüft DE+EN inkl. 200 ohne Redirect |
| TI-02 Profiling-Hook | `VERIFIED_PRODUCTION` | `?_profile=1` + Header ⇒ keine `X-Promat-Player-Profile`-Antwort; im Prod-Container 0 Treffer für den Hook im Quelltext |
| TI-03 Open Redirect | `VERIFIED_PRODUCTION` (anonym) | `/login?next=////evil.example/x` rendert kein `next` im Formular; der Wert erscheint nur URL-kodiert in Sprachwechsel-/Login-Links derselben Seite. Redirect als angemeldeter Nutzer: nur Test (lokal/CI grün) |
| TI-05 Cache-Control | `VERIFIED_PRODUCTION` für `/login` (`private, no-store`); geschützte Research-Antworten `BLOCKED_EXTERNAL` | benötigt ein Produktionskonto; Test und Browser-Smoke in Run 1 grün |
| TI-07 GoatCounter | `VERIFIED_PRODUCTION` (öffentlich) | auf `/de/research/spanish/design` geladen, CSP dort mit `gc.zgo.at`; geschützte Seiten leiten anonym um. Geschützte Seiten eingeloggt: `BLOCKED_EXTERNAL` (Konto nötig) |
| Geschützte Research-Seiten | `VERIFIED_PRODUCTION` | `/de/research/spanish/speakers` ⇒ 302 `/login?next=…` |
| Speaker-Profil ohne Consent-Felder | `BLOCKED_EXTERNAL` | nur mit Konto sichtbar; Test in der Suite |
| TI-26 Logout POST | `VERIFIED_PRODUCTION` | `GET /auth/logout` ⇒ 405 |
| TI-06 Constraint | `VERIFIED_PRODUCTION` | `ck_access_requests_status` enthält `notified`/`notification_failed` (Migration 0011 angewendet) |
| TI-09 Set-API, TI-21 Media | `BLOCKED_EXTERNAL` / Tests | Set-API braucht ein Konto; Media-Traversal bewusst nicht gegen Produktion geprobt; Tests grün |
| TI-10/TI-23 `/ready` | `VERIFIED_PRODUCTION` | `/ready` 200, JSON nur mit `ok`/Codes, Redis-Prüfung `ok`; `/health` healthy |
| TI-11/TI-12/TI-15 | `VERIFIED_PRODUCTION` | Start mit der neuen Config-Prüfung erfolgreich; Deploy hat vor der Migration ein Backup erzeugt; Image mit `markdown-it-py` läuft |
| TI-13 Container-Log | `VERIFIED_PRODUCTION` (Format) | Container läuft mit `gunicorn.conf.py`; Log-Format ohne Query/Referer (in Run 1 am Container belegt) |
| Runtime-Logs | `VERIFIED_PRODUCTION` | seit dem Deploy keine `ERROR`/Traceback im Container- und App-Log (die 405 älteren Einträge stammen vom Vorgängercontainer) |

Anonym nicht beobachtbar, mit einem QA-Konto jederzeit nachholbar: `PROMAT_QA_USER=… PROMAT_QA_PASSWORD=… python scripts/qa/browser_smoke.py --base-url https://pronunciation-matters.de --out tmp/ui-qa/<datum>-prod`. Es wurde kein Produktionskonto angelegt.

## Operator-Punkte

| Punkt | Status | Durchgeführt |
|---|---|---|
| A. nginx-Access-Log | `COMPLETE` | Neues `/etc/nginx/conf.d/promat-log-format.conf` (`log_format promat_noquery`: `$request_method $uri`, kein `$request`, kein `$http_referer`), `access_log …/pronunciation-matters.access.log promat_noquery;` in allen vier Server-Blöcken von `sites-available/pronunciation-matters.de.conf` (Sicherung `/root/pronunciation-matters.de.conf.bak.20261006`). `nginx -t` ok, `reload`. Test mit harmlosem Wert `?token=HARMLESSTESTVALUE123` samt Referer: 0 Treffer im neuen Log, Zeile zeigt nur den Pfad. Andere Sites auf dem Server unverändert; Logrotate (`/var/log/nginx/*.log`, wöchentlich, 4 Rotationen) greift. Der Test-Request vor dem Reload steht im alten Gemeinschaftslog (harmloser Wert) |
| B. Backup-Automation | `COMPLETE` | `/etc/cron.d/promat-db-backup`: täglich 02:15 als root, `scripts/backup_prod_db.sh --keep 14` aus dem Deploy-Checkout, Log `/srv/webapps/promat/logs/backup.log`. Derselbe Befehl einmal ausgeführt: Exit 0, Dump 87 962 Byte/13 Tabellen, Prüfsumme OK, Modus 600/700, Rotation durch `--keep` (14). `cron` aktiv. Ein Restore-Test (`verify_db_restore.sh`) wurde auf dem Server nicht ausgeführt (CI-Rehearsal deckt ihn ab); empfohlen monatlich |
| C. Branch Protection | `BLOCKED_EXTERNAL` | `main`: `protected: false`, keine Required Checks. Ändern geht nur mit Admin-Token/UI; keines vorhanden, und das Git-Credential wurde nicht für API-Änderungen verwendet. **UI-Schritte:** GitHub → Settings → Branches → Add rule `main` → „Require status checks to pass before merging“ → Check `release-gate` wählen (erscheint nach dem ersten CI-Lauf) → optional „Do not allow bypassing“ nur, wenn ein Notfallweg bleibt. Hinweis: das Deployment ist ohnehin durch `workflow_run` an grünes CI gebunden; die Protection schützt `main` selbst |

## Handoff für Run 2

- **Auth/Token:** TI-04 (Token-/Statusprüfung pro Request, Logout/Deaktivierung wirkt sofort, E-Mail-Wechsel mit Bestätigung), TI-25 (Admin-Invarianten). Logout widerruft das Token weiterhin nicht.
- **Privacy/Research-Data:** nichts Neues aus Run 1.5; DATA-01 (ID3-Titel), TI-27 (Notizfelder, interne IDs) bleiben wie im Audit.
- **Unerwartete neue Findings:** keine. Beobachtungen aus Run 1 bleiben: Redis-Ausfall kostet je Request ca. 2,5 s (fail-open, TI-08), rohe 429-Seite, gunicorn-Reset bei Bodies > 1 MiB (nginx erlaubt 50 MB), Landing-`<title>` doppelt, `AUTH_MAIL_BACKEND` wird von Compose nicht durchgereicht.
- **Offen im Betrieb:** Branch Protection (UI), Restore-Übung auf dem Server, ein QA-Konto für den authentifizierten Browser-Smoke gegen Produktion.

## Abschluss

Siehe Terminal-Ausgabe; SHAs von `main` und Production nach dem Doku-Push stehen am Ende dieser Datei.
