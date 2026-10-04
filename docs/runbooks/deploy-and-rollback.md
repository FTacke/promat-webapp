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
   - **Konfigurationsprüfung mit dem neuen Image** (Platzhalter-Secrets, `PROMAT_PUBLIC_BASE_URL`, Rate-Limit-Store); bei Fehler bricht das Deployment ab, ohne einen laufenden Container anzufassen
   - Migrationen anwenden
   - nur den `web`-Container ersetzen (Datenbank und Redis werden nicht neu gestartet)
   - Health und Readiness prüfen

Wird CI rot, passiert nichts auf dem Server; der nächste grüne Commit deployt.

## Manuelles Deployment und Rollback

1. In GitHub: Actions → „Deploy production“ → „Run workflow“. Im Feld „Use workflow from“ den Branch oder Tag wählen, dessen Commit deployt werden soll.
2. Der Commit muss einen erfolgreichen CI-Lauf haben. Für einen älteren, bewährten Commit ist das normalerweise gegeben. Für einen noch nie getesteten Commit zuerst Actions → CI → „Run workflow“ auf diesem Ref ausführen.
3. Es gibt keine automatische Rücknahme. Ein Rollback ist ein erneutes Deployment des früheren Commits; Datenbank-Migrationen werden dabei nicht zurückgedreht (sie sind additiv). Ist die Datenbank durch eine Migration unbrauchbar, den DB-Restore aus `backup-and-restore.md` verwenden.
4. Danach `curl -fsS http://127.0.0.1:8000/health` und `/ready` auf dem Server sowie die Seiten aus der Prüfliste unten.

## Fehlerbilder

- „Production configuration is invalid“ im Deploy-Log: `/srv/webapps/promat/config/passwords.env` korrigieren (`JWT_SECRET_KEY`/`FLASK_SECRET_KEY` echte Zufallswerte, `PROMAT_PUBLIC_BASE_URL=https://<öffentliche Domain>`), Workflow erneut starten. Der laufende Container wurde nicht angetastet.
- „No successful CI run found“: CI auf dem Commit ausführen (siehe oben).
- Deployment läuft nicht an: prüfen, ob `deploy.yml` mit dem `workflow_run`-Trigger auf `main` liegt und der Runner online ist.

## Prüfliste für den Operator (einmalig nach Einführung, danach nach Bedarf)

Diese Punkte lassen sich nicht aus dem Repository klären und wurden nie gegen Produktion geprüft.

1. **Rechtsseiten:** `https://<domain>/impressum`, `/de/privacy` und `/en/privacy` liefern 200 (vorher lasen sie eine Datei, die das Image nicht enthält).
2. **JWT-Secret:** auf dem Server prüfen, ohne den Wert auszugeben: `grep -c '^JWT_SECRET_KEY=__' /srv/webapps/promat/config/passwords.env` muss `0` sein; Länge mindestens 32 Zeichen (`awk -F= '/^JWT_SECRET_KEY=/{print length($2)}' …`). Kürzere Schlüssel erzeugen mit PyJWT 2.15 pro Token eine `InsecureKeyLengthWarning` im Log.
3. **Öffentliche Basis-URL:** `PROMAT_PUBLIC_BASE_URL` ist `https://pronunciation-matters.de` (oder die kanonische Domain). Passwort-Reset anfordern und prüfen, dass der Link in der Mail diese Domain trägt, auch wenn die Anfrage mit anderem `Host` gestellt wird (nginx setzt `Host` und `X-Forwarded-Host` selbst: `nginx -T | grep -A20 pronunciation-matters`).
4. **Erstes CI-gesteuertes Deployment:** nach dem Merge auf `main` zeigt Actions zuerst `CI`, danach `Deploy production`; der Commit im Deploy-Log ist der getestete.
5. **Datenbank bleibt gesund:** vor und nach einem Deployment `docker inspect -f '{{.State.StartedAt}}' promat-db-prod` vergleichen: die Startzeit darf sich nicht ändern; `docker ps` zeigt `promat-db-prod` und `promat-rate-limit-prod` als healthy.
6. **Backup gegen die echte Datenbank:** `scripts/backup_prod_db.sh` ausführen, danach `scripts/verify_db_restore.sh --dump …` bis `RESTORE VERIFIED`; Cron-Eintrag und Zweitkopie einrichten (`backup-and-restore.md`).
7. **Branch-Schutz auf `main`:** in GitHub „Require status checks“ mit `release-gate` einschalten (Repository-Einstellung, nicht im Repo steuerbar).
8. **Research-Konfiguration:** flachen Baum und aktiven Release vergleichen, zum Beispiel `diff -r /srv/webapps_storage/promat/data/config/research_player /srv/webapps_storage/promat/data/current/config/research_player`. Der Publish-Schritt kopiert `config/` nicht in den flachen Baum (der Fall `théâtre` am 2026-06-19 war genau diese Abweichung); neue Kataloge, etwa für Deutsch, müssen bewusst dorthin gelangen.
9. **Intake-Organizer:** die lokale Altkopie unter `scripts/research_data_intake/import/organize_batch_working_tree.py` gegen die versionierte Fassung diffen (siehe `research-intake-working-pipeline.md`).
10. **Speaker-Profile:** ein Profil mit hinterlegten Einwilligungsdaten öffnen und prüfen, dass keine Einwilligungs- oder „Interne Notizen“-Zeilen erscheinen.

## Verifikation

- Deploy-Lauf grün, Container `promat-web-prod` healthy, Seiten aus der Prüfliste antworten.

## Risiken und Rückbau

- Ein Deployment ersetzt den Web-Container; kurze Unterbrechung bis zur Health-Prüfung ist normal.
- Rollback bedeutet Neu-Deployment eines alten Commits; Datenbank-Schemaänderungen bleiben bestehen.
