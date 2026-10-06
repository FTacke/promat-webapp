# Runbook: Deployment, Rollback und Produktionsprüfung

## Zugehörige Spezifikation

- `docs/spec/platform-data-files.md` (Abschnitt „Release Gate and Deployment“)

## Zweck

Wie ein Commit von `main` nach Produktion gelangt, wie ein fehlgeschlagenes Deployment behandelt und zurückgenommen wird und was der Operator nach der Einführung des CI-gesteuerten Deployments einmalig auf dem Server prüfen muss.

## Ablauf nach einem Push auf `main`

1. `CI` (`.github/workflows/ci.yml`) läuft für den Commit; `release-gate` ist nur grün, wenn Python-Suite, JS-Tests, Image-Build und Backup-Rehearsal grün sind.
2. Erst nach erfolgreichem Abschluss startet `Deploy production` (`workflow_run`). Das Deployment nimmt `workflow_run.head_sha`, also genau den getesteten Commit, und bricht ab, wenn für diesen Commit kein erfolgreicher CI-Lauf existiert.
3. Ist `main` inzwischen weitergewandert, wird dieser Lauf übersprungen (Warnung im Log); der Lauf des neueren Commits übernimmt. Deployments laufen nie parallel.
4. Auf dem Server (Runner `promat-prod`): `git fetch`, Checkout des Commits, danach `scripts/deploy_prod.sh`:
   - Datenbank und Rate-Limit-Dienst starten bzw. unverändert lassen und auf Health warten
   - Web-Image bauen
   - **Konfigurationsprüfung mit dem neuen Image** (Platzhalter-/schwache Secrets, `JWT_SECRET_KEY` ≠ `FLASK_SECRET_KEY`, `PROMAT_PUBLIC_BASE_URL`, Rate-Limit-Store, Absender/Empfänger/SMTP-Host der Zugangsanfrage-Mail); bei Fehler bricht das Deployment ab, ohne einen laufenden Container anzufassen
   - **Datenbank-Backup vor den Migrationen** (`scripts/backup_prod_db.sh`, mit `pg_restore --list` geprüft); schlägt es fehl, bricht das Deployment ab, bevor sich das Schema ändert. Nur eine Datenbank ohne `users`-Tabelle (Erstinstallation) überspringt das Backup
   - Migrationen anwenden
   - nur den `web`-Container ersetzen (Datenbank und Redis werden nicht neu gestartet)
   - Health und Readiness prüfen
5. Danach (im Workflow) `scripts/post_deploy_smoke.py --base-url https://pronunciation-matters.de`: nur lesende GETs. Geprüft werden die Rechtsseiten (200), öffentliche Seiten (200 mit serverseitigem `<title>`), dass Entwurfs-Themen nicht öffentlich sind, dass geschützte Research-Seiten zum Login umleiten, die Zitat-URL der Themenseite und `/ready`. Ein roter Smoke macht den Lauf rot; es gibt keinen automatischen Rollback.

Wird CI rot, passiert nichts auf dem Server; der nächste grüne Commit deployt.

## Manuelles Deployment und Rollback

1. In GitHub: Actions → „Deploy production“ → „Run workflow“. Im Feld „Use workflow from“ den Branch oder Tag wählen, dessen Commit deployt werden soll.
2. Der Commit muss einen erfolgreichen CI-Lauf haben. Für einen älteren, bewährten Commit ist das normalerweise gegeben. Für einen noch nie getesteten Commit zuerst Actions → CI → „Run workflow“ auf diesem Ref ausführen.
3. Es gibt keine automatische Rücknahme. Ein Rollback ist ein erneutes Deployment des früheren Commits; Datenbank-Migrationen werden dabei nicht zurückgedreht (sie sind additiv). Ist die Datenbank durch eine Migration unbrauchbar, den DB-Restore aus `backup-and-restore.md` verwenden.
4. Danach `curl -fsS http://127.0.0.1:8000/health` und `/ready` auf dem Server sowie die Seiten aus der Prüfliste unten.

## Fehlerbilder

- „Production configuration is invalid“ im Deploy-Log: `/srv/webapps/promat/config/passwords.env` korrigieren (`JWT_SECRET_KEY` und `FLASK_SECRET_KEY` **verschiedene** echte Zufallswerte von mindestens 32 Zeichen, `PROMAT_PUBLIC_BASE_URL=https://<öffentliche Domain>`, `AUTH_ACCESS_REQUEST_EMAIL` / `AUTH_ACCESS_REQUEST_FROM_EMAIL` echte Adressen, bei `smtp` ein echter `AUTH_ACCESS_REQUEST_SMTP_HOST`), Workflow erneut starten. Der laufende Container wurde nicht angetastet. Die Meldung nennt den Namen der Variable, nie ihren Wert.
- „Database backup failed“: Platz und Schreibrecht im Backup-Ordner (`PROMAT_BACKUP_DIR`, Standard `/srv/webapps_storage/promat/backups/postgres`) und Zustand von `promat-db-prod` prüfen (`backup-and-restore.md`); es wurde keine Migration angewendet und kein Container ersetzt.
- Post-Deploy-Smoke rot: die genannte URL prüfen. Bei 5xx auf Rechtsseiten oder öffentlichen Seiten Container-Log lesen und im Zweifel auf den vorherigen Commit zurückrollen (siehe oben).
- „No successful CI run found“: CI auf dem Commit ausführen (siehe oben).
- Deployment läuft nicht an: prüfen, ob `deploy.yml` mit dem `workflow_run`-Trigger auf `main` liegt und der Runner online ist.

## Prüfliste für den Operator (einmalig bei Einführung, danach nach Bedarf)

Diese Punkte lassen sich nicht aus dem Repository klären und wurden nie gegen Produktion geprüft. **Die Punkte 2 und 3 vor dem Merge prüfen:** Der Produktionsstart verlangt ab dieser Änderung einen echten `JWT_SECRET_KEY` und `PROMAT_PUBLIC_BASE_URL=https://…`. Sind sie falsch, bricht das erste Deployment in der Konfigurationsprüfung ab; der laufende Container bleibt dabei unverändert, es wird aber auch nichts ausgeliefert.

1. **Rechtsseiten:** `https://<domain>/impressum`, `/de/privacy` und `/en/privacy` liefern 200 (vorher lasen sie eine Datei, die das Image nicht enthält).
2. **Secrets:** auf dem Server prüfen, ohne den Wert auszugeben: `grep -c '^\(JWT\|FLASK\)_SECRET_KEY=__' /srv/webapps/promat/config/passwords.env` muss `0` sein; Länge mindestens 32 Zeichen (`awk -F= '/^(JWT|FLASK)_SECRET_KEY=/{print $1, length($2)}' …`); die beiden Werte müssen **verschieden** sein (`awk -F= '/^(JWT|FLASK)_SECRET_KEY=/{print $2}' … | sort -u | wc -l` muss `2` sein). Seit dieser Version bricht der Start andernfalls ab (die Konfigurationsprüfung des Deployments fängt das ab, ohne den laufenden Container anzufassen).
   Zusätzlich: `AUTH_ACCESS_REQUEST_EMAIL` und `AUTH_ACCESS_REQUEST_FROM_EMAIL` sind echte Adressen (kein `__SET_…__`), und bei Backend `smtp` ist `AUTH_ACCESS_REQUEST_SMTP_HOST` ein echter Host (`grep -c '__SET_' /srv/webapps/promat/config/passwords.env` für die genutzten Variablen prüfen; `AUTH_MAIL_BACKEND` wird von `infra/docker-compose.prod.yml` derzeit nicht an den Container durchgereicht, Standard ist `smtp`).
3. **Öffentliche Basis-URL:** `PROMAT_PUBLIC_BASE_URL` ist `https://pronunciation-matters.de` (oder die kanonische Domain). Passwort-Reset anfordern und prüfen, dass der Link in der Mail diese Domain trägt, auch wenn die Anfrage mit anderem `Host` gestellt wird (nginx setzt `Host` und `X-Forwarded-Host` selbst: `nginx -T | grep -A20 pronunciation-matters`).
4. **Erstes CI-gesteuertes Deployment:** nach dem Merge auf `main` zeigt Actions zuerst `CI`, danach `Deploy production`; der Commit im Deploy-Log ist der getestete.
5. **Datenbank bleibt gesund:** vor und nach einem Deployment `docker inspect -f '{{.State.StartedAt}}' promat-db-prod` vergleichen: die Startzeit darf sich nicht ändern; `docker ps` zeigt `promat-db-prod` und `promat-rate-limit-prod` als healthy.
6. **Backup gegen die echte Datenbank:** `scripts/backup_prod_db.sh` ausführen, danach `scripts/verify_db_restore.sh --dump …` bis `RESTORE VERIFIED`; Cron-Eintrag und Zweitkopie einrichten (`backup-and-restore.md`).
7. **Branch-Schutz auf `main`:** in GitHub „Require status checks“ mit `release-gate` einschalten (Repository-Einstellung, nicht im Repo steuerbar).
8. **Research-Konfiguration:** flachen Baum und aktiven Release vergleichen, zum Beispiel `diff -r /srv/webapps_storage/promat/data/config/research_player /srv/webapps_storage/promat/data/current/config/research_player`. Der Publish-Schritt kopiert `config/` nicht in den flachen Baum (der Fall `théâtre` am 2026-06-19 war genau diese Abweichung); neue Kataloge, etwa für Deutsch, müssen bewusst dorthin gelangen.
9. **Intake-Organizer:** die lokale Altkopie unter `scripts/research_data_intake/import/organize_batch_working_tree.py` gegen die versionierte Fassung diffen (siehe `research-intake-working-pipeline.md`).
10. **Speaker-Profile:** ein Profil mit hinterlegten Einwilligungsdaten öffnen und prüfen, dass keine Einwilligungs- oder „Interne Notizen“-Zeilen erscheinen.
11. **Proxy-Logs und Header (nginx):** `nginx -T` prüfen. Das Zugriffslog-Format darf die Query nicht enthalten (`$uri` statt `$request`, kein `$http_referer`), weil Passwort-Reset-Links das Token als `?token=` tragen; der App-Container loggt ohne Query und ohne Referer. `Host` und `X-Forwarded-*` müssen von nginx selbst gesetzt werden.
12. **Backup-Ordner:** `PROMAT_BACKUP_DIR` (Standard `/srv/webapps_storage/promat/backups/postgres`) muss für den Runner-Benutzer beschreibbar und groß genug sein, denn jedes Deployment legt vor den Migrationen ein Backup an (Aufräumen: `--keep`, Standard 14).
13. **Redis-Ausfall:** der Rate-Limiter läuft bei Redis-Ausfall fail-open (Seiten bleiben erreichbar, jeder Fehler steht im Container-Log als „Swallowing error“); `/ready` meldet dann 503 und der Healthcheck bleibt unverändert auf `/health`. Redis-Ausfälle daher über `/ready` oder das Container-Log überwachen. Ein Monitor-Thread in der App (Intervall `RATELIMIT_HEALTH_POLL_SECONDS`, Standard 5 s) schaltet den Limiter während des Ausfalls ab, damit Anfragen nicht je rund 2,5 s auf die Verbindung warten; im Log erscheinen „Rate-limit storage is unavailable“ und beim Wiederanlauf „… available again“.
14. **Komprimierung und Cache der Static-Dateien (nginx, einmalig):** Die App liefert versionierte Static-Dateien (`/static/...?v=...`) mit `Cache-Control: public, max-age=31536000, immutable`; nginx gibt den Header unverändert weiter. Komprimiert wird nur, was nginx dafür freigibt. Standard ist `gzip_types text/html` (CSS, JS, JSON und SVG gehen unkomprimiert hinaus; `30_components.css` hat unkomprimiert rund 250 KB). Im `server`- oder `http`-Block des Pronunciation-Vhosts eintragen und prüfen:

    ```nginx
    gzip on;
    gzip_vary on;
    gzip_comp_level 5;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/css application/javascript text/javascript application/json image/svg+xml;
    ```

    `woff2`, JPEG und MP3 sind bereits komprimiert und bleiben draußen. Danach `sudo nginx -t && sudo systemctl reload nginx`. Prüfen: `curl -sI -H 'Accept-Encoding: gzip' https://<domain>/static/css/30_components.css` zeigt `Content-Encoding: gzip`, und `curl -sI 'https://<domain>/static/css/00_tokens.css?v=1'` zeigt `Cache-Control: public, max-age=31536000, immutable`. Kein `proxy_hide_header Cache-Control` und kein `expires`, das den App-Header überschreibt.

## Verifikation

- Deploy-Lauf grün (einschließlich „Post-deploy smoke“), Container `promat-web-prod` healthy, Seiten aus der Prüfliste antworten.
- Manuell jederzeit wiederholbar (nur lesende GETs, ohne Login): `python3 scripts/post_deploy_smoke.py --base-url https://pronunciation-matters.de`. Der Browser-Teil (Seitentitel nach JavaScript, Zurück-Taste nach Logout, kein Analytics-Skript auf Research-Seiten) steht in `scripts/qa/browser_smoke.py`.

## Risiken und Rückbau

- Ein Deployment ersetzt den Web-Container; kurze Unterbrechung bis zur Health-Prüfung ist normal.
- Rollback bedeutet Neu-Deployment eines alten Commits; Datenbank-Schemaänderungen bleiben bestehen.
