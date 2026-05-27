# prep_server.md — ProMat / Pronunciation Matters v0.7 Production Preparation

Stand: 2026-05-27
Basis: read-only reports `promat_v07_preflight_readonly_20260526_191204.md` und `promat_runner_deploy_pattern_readonly_20260526_191925.md`

Diese Datei ist eine Repo-seitige Planungs- und Freigabegrundlage. Sie dokumentiert den geplanten ersten produktiven ProMat-Deploy für Pronunciation Matters v0.7, aber sie führt selbst keine Runtime-Änderungen aus. Aktive Upload-Package-Regeln bleiben in [docs/spec/platform-data-files.md](docs/spec/platform-data-files.md) maßgeblich; diese Datei verdichtet daraus die serverseitige Deployment-Reihenfolge.

---

## 1. Naming Decision And Scope

- Für alle Serverordner, Runtime-Objekte, Container-, Network-, Volume- und Runner-Namen wird konsistent `promat` verwendet.
- Der öffentliche Produktname bleibt Pronunciation Matters.
- Die primäre öffentliche Produktionsdomain ist `pronunciation-matters.de`.
- `www.pronunciation-matters.de` soll auf `pronunciation-matters.de` umleiten, falls TLS für beide Hosts ausgestellt wird.
- `promat.hispanistica.com` ist kein Bestandteil des initialen Deploys. Es darf nur als möglicher späterer Alias-Redirect dokumentiert werden und erst nach separater DNS-/TLS-Prüfung eingeführt werden.
- Diese Doku beschreibt nur den ProMat-spezifischen Pfad. Bestehende CO.RA.PAN-, Games-, HedgeDoc- oder Marele-Ressourcen bleiben unberührt.

Nicht Ziel dieses Repo-Updates:

- keine Servereingriffe
- keine Runner-Installation
- keine Docker-Aktionen
- keine nginx-/certbot-Aktionen
- keine Secrets
- keine Datenübertragung

---

## 2. Public Domains

### 2.1 Initial Production Domains

| Zweck | Hostname | Status laut Preflight |
| --- | --- | --- |
| Primäre öffentliche Produktionsdomain | `pronunciation-matters.de` | DNS zeigt bereits auf den Host |
| Optionaler `www`-Host | `www.pronunciation-matters.de` | DNS zeigt bereits auf den Host |
| Später möglicher Alias | `promat.hispanistica.com` | aktuell kein DNS-Ergebnis |

### 2.2 Initiale öffentliche Routing-Regel

- Initial öffentlich ausrollen auf `pronunciation-matters.de`.
- Falls TLS sowohl für Apex als auch `www` ausgestellt wird, soll `www.pronunciation-matters.de` per Redirect auf `https://pronunciation-matters.de` zeigen.
- `promat.hispanistica.com` ist nur ein später möglicher Alias-Redirect. Dieser Host ist kein Teil des initialen Zertifikats- oder nginx-Scope, solange DNS dafür fehlt.

### 2.3 Preflight Domain Facts

- Es existiert aktuell kein nginx-vHost für `pronunciation-matters.de`, `www.pronunciation-matters.de` oder `promat.hispanistica.com`.
- Es existiert aktuell kein TLS-Zertifikat für diese Hosts.
- `pronunciation-matters.de` und `www.pronunciation-matters.de` lösen bereits auf den Zielhost auf.
- `promat.hispanistica.com` löst aktuell nicht auf.

---

## 3. Server Paths And Runtime Object Names

### 3.1 Verbindliche Serverpfade

```text
/srv/webapps/promat
/srv/webapps/promat/app
/srv/webapps/promat/config
/srv/webapps/promat/runner
/srv/webapps/promat/logs
/srv/webapps/promat/data
/srv/webapps_storage/promat
/srv/webapps_storage/promat/data
```

### 3.2 Verbindliche Runtime-Objektnamen

```text
promat-web-prod
promat-db-prod
promat-network-prod
promat_postgres_prod
promat-prod
actions.runner.<owner-repo>.promat-prod.service
```

Dabei gilt:

- `promat-prod` ist sowohl Compose-Projektname als auch Runner-Label.
- Der Runner-Service folgt dem Muster `actions.runner.<owner-repo>.promat-prod.service`.

### 3.3 Current Server State For This Repo Prep

Diese Angaben stammen aus dem Aufgaben-Kontext vom 2026-05-27 und wurden in diesem repo-only Run nicht per SSH re-verifiziert:

- `/srv/webapps/promat` existiert.
- `/srv/webapps/promat/app`, `/srv/webapps/promat/config`, `/srv/webapps/promat/runner`, `/srv/webapps/promat/data` und `/srv/webapps/promat/logs` existieren.
- `/srv/webapps_storage/promat/data` ist aktiv nach `/srv/webapps/promat/data` gebunden.
- Es existiert kein app-lokaler Pfad `/srv/webapps/promat/media`.
- Es existiert kein Media-Bind-Mount.
- `/srv/webapps_storage/promat/media` darf höchstens als historisch vorbereiteter Storage-Pfad existieren, ist aber kein Bestandteil des initialen v0.7-Deployments.
- Noch nicht vorhanden bzw. noch nicht ausgeführt: ProMat-Runner, Checkout, Docker-Stack, nginx-vHost, TLS-Zertifikat, Monitoring-Ziel, Datenbank und App-Deploy.

### 3.4 Storage-Normalisierung

Die früher geplanten Server-Phasen C bis E gelten laut aktuellem Aufgaben-Kontext als bereits erledigt: der interne Server-Namespace ist `promat`, die App-Pfade existieren, und der Daten-Bind-Mount ist aktiv.

Für den App-Deploy bleibt verbindlich:

- keine automatische Storage-Umbenennung durch Repo-Skripte
- kein Media-Bind-Mount
- kein `/app/media`
- keine direkte Datenübertragung in `data/current`

---

## 4. Target Server Layout

### 4.1 App Root

```text
/srv/webapps/promat/
  app/
  config/
  runner/
  logs/
  data/
```

| Pfad | Zweck |
| --- | --- |
| `/srv/webapps/promat/app` | Git-Checkout und deployed working copy |
| `/srv/webapps/promat/config` | serverseitige Env-/Secret-Dateien |
| `/srv/webapps/promat/runner` | app-spezifischer GitHub self-hosted Runner |
| `/srv/webapps/promat/logs` | ProMat-Runtime-Logs |
| `/srv/webapps/promat/data` | app-lokaler Bind-Mount für ProMat-Daten |

### 4.2 Shared Storage Layout

```text
/srv/webapps_storage/promat/
  data/
    incoming/
    releases/
    current -> releases/<release_id>
```

`current` wird erst nach dem ersten validierten Promote-Schritt angelegt. Daten werden nicht direkt in ein bereits live verwendetes Release geschrieben.

### 4.3 App-lokale Bind Mounts

```text
/srv/webapps_storage/promat/data  -> /srv/webapps/promat/data
```

Empfohlene spätere `/etc/fstab`-Zeilen:

```fstab
/srv/webapps_storage/promat/data  /srv/webapps/promat/data   none  bind  0  0
```

Der Daten-Bind-Mount ist laut Aufgaben-Kontext für den ersten Deploy bereits aktiv. Vor einem echten Deploy wird er read-only geprüft, aber nicht durch Repo-Skripte angelegt oder verändert.

Für den initialen v0.7-Deploy gilt bewusst: kein separater `/srv/webapps/promat/media`-Bind-Mount und kein `/app/media`-Mount im Container. Topic-lokale Teaching-Medien bleiben Teil des versionierten `content/teaching/.../media`-Baums im Image; Research-Runtime-Artefakte liegen unter `/app/data`.

---

## 5. Existing Runner And Deploy Pattern To Follow

ProMat soll das auf dem Server bereits erfolgreiche Runner-/Deploy-Modell der anderen Apps übernehmen, aber ohne Ressourcen zu teilen.

### 5.1 Bestehendes Modell, das übernommen werden soll

- Bestehende Apps nutzen app-spezifische Runner-Verzeichnisse unter `/srv/webapps/<app>/runner`.
- Bestehende Runner-Services folgen dem Muster `actions.runner.<owner-repo>.<runner-name>.service`.
- Deployments laufen über repo-seitige Scripts statt über manuelle Code-Edits auf dem Server.

### 5.2 ProMat-spezifische Ableitung

- ProMat bekommt einen eigenen Runner unter `/srv/webapps/promat/runner`.
- ProMat verwendet das Runner-Label `promat-prod`.
- ProMat deployt Code ausschließlich nach `/srv/webapps/promat/app`.
- ProMat-Env- und Secret-Dateien leben ausschließlich unter `/srv/webapps/promat/config`.
- Deployter Code unter `/srv/webapps/promat/app` wird nicht manuell editiert.
- Der Workflow soll `runs-on: [self-hosted, promat-prod]` verwenden.
- Der Workflow soll den Checkout vor dem Deploy explizit auf `GITHUB_SHA` zurücksetzen.
- Das Deployment delegiert an genau ein Repo-Script: `scripts/deploy_prod.sh`.
- Die produktive Env-Datei ist `/srv/webapps/promat/config/passwords.env`.
- Secrets werden nie gedruckt, committed, geloggt oder dokumentiert.

### 5.3 Explizit nicht wiederverwenden

- keine CO.RA.PAN-Runner-Verzeichnisse
- keine Games-Runner-Verzeichnisse
- keine fremden Runner-Labels
- keine fremden Runner-Services
- keine fremden Docker-Netze
- keine fremden Deploy-Scripts

### 5.4 Runner-Service-Zielmuster

```text
actions.runner.<owner-repo>.promat-prod.service
```

### 5.5 Empfohlenes Workflow-Muster

```yaml
jobs:
  deploy:
    runs-on: [self-hosted, promat-prod]
    steps:
      - uses: actions/checkout@v6
      - name: Reset checkout to triggering commit
        run: |
          git fetch --all --tags
          git reset --hard "$GITHUB_SHA"
      - name: Deploy production
        run: |
          bash scripts/deploy_prod.sh
```

Das Repo-Script bleibt die einzige Deploy-Entry-Point. Weder Workflow noch Runner sollen fremde App-Skripte, Runner-Verzeichnisse oder bestehende Service-Namen wiederverwenden.

---

## 6. Ports, Compose Scope, DB And Health

### 6.1 Port-Facts aus dem Preflight

| Port | Status laut Preflight |
| --- | --- |
| `8000` | erscheint frei |
| `5000` | belegt |
| `6000` | belegt |
| `7000` | belegt |
| `3100` | belegt |

### 6.2 ProMat-spezifischer Binding-Plan

```text
127.0.0.1:8000 -> container:5000
```

- Nur an `127.0.0.1` binden.
- Nicht an `0.0.0.0` binden.
- Keine Bindung auf bereits belegte Ports.

### 6.3 Compose-Scope

- ProMat erhält ein eigenes Compose-Deployment.
- ProMat erhält ein eigenes Docker-Netz `promat-network-prod`.
- ProMat erhält eine eigene DB `promat-db-prod`.
- ProMat erhält ein eigenes Postgres-Volume `promat_postgres_prod`.
- ProMat verwendet den Compose-Projektnamen `promat-prod`.
- ProMat darf keine bestehenden DB-Container, DB-Volumes oder App-Netze mitbenutzen.

Explizit nicht verwenden:

```text
corapan-db-prod
games-db-prod
hedgedoc_db
host PostgreSQL
corapan-network-prod
games-backend-prod
hedgedoc_hedgedoc_net
```

### 6.4 Empfohlenes Compose-Wrapper-Muster

Basis-Wrapper:

```bash
docker compose -p promat-prod --env-file /srv/webapps/promat/config/passwords.env -f infra/docker-compose.prod.yml <subcommand>
```

Empfohlener Deploy-Aufruf:

```bash
docker compose -p promat-prod --env-file /srv/webapps/promat/config/passwords.env -f infra/docker-compose.prod.yml up -d --build --force-recreate
```

### 6.5 Health And Readiness

Für den ersten Deploy werden lokal erwartet:

```text
docker ps --filter name=promat --format '{{.Names}}\t{{.Status}}'
http://127.0.0.1:8000/health
http://127.0.0.1:8000/ready
```

Semantik:

- `/health`: Prozess lebt und antwortet.
- `/ready`: App ist mit DB, Datenpfad, Logs-Pfad, produktivem Rate-Limit-Backend und erforderlichen Runtime-Artefakten betriebsbereit.
- Falls ein Docker `HEALTHCHECK` existiert, muss auch dieser Status gesund sein.
- Ein Deploy ist nicht erfolgreich, bis Health und Readiness grün sind oder eine temporäre Degradierung der Readiness mit bekanntem Grund explizit dokumentiert wurde.

---

## 7. Production Data Transfer And rsync Strategy

Diese Section adressiert explizit die VPN-/SSH-Reibung für produktive Datenupdates.

### 7.1 Bevorzugtes Modell

- Nicht auf ad-hoc manuelle SSH-Sessions für routinemäßige Produktionsdatenupdates verlassen.
- Stattdessen explizite, validierte Prod-Upload-Packages aus der lokalen Research-Intake-Pipeline verwenden.
- Validierung und Promotion serverseitig über ein kontrolliertes Script oder einen Runner-getriggerten Workflow ausführen.
- Diese Planungsdatei übernimmt die aktive Allowlist aus [docs/spec/platform-data-files.md](docs/spec/platform-data-files.md); bei späteren Vertragsänderungen wird die Spec zuerst angepasst.

### 7.2 Zulässige Sync-Ziele

Falls `rsync` verwendet wird, dann nur zu genau einem dieser Ziele:

```text
/srv/webapps_storage/promat/data/incoming/<upload_id>
```

Unzulässig:

- direkt nach `current`
- direkt in ein bereits aktives `releases/<release_id>`
- direkt in einen Release-Pfad, den die App gerade verwendet

### 7.3 Promotion-Regeln

- Manifest, Checksums und Dateianzahl validieren, bevor ein Promote erfolgt.
- Validierte Uploads in einen neuen Release unter `releases/<release_id>` überführen.
- Produktiv mit atomarem `current`-Symlink-Switch promoten.
- Nur wenige bekannte gute vorige Releases behalten; Retention-Cleanup nur explizit und bewusst durchführen.
- Fehlgeschlagene Incoming- oder Staging-Verzeichnisse erst nach expliziter Freigabe bereinigen.

### 7.4 `rsync` Safety

- `rsync --delete` nie ohne gedruckte, geprüfte und explizit freigegebene Quelle/Ziel-Kombination.
- Keine blind destructive Synchronisation.
- Kein automatisches Entfernen produktiver Dateien durch Upload-Omission.

### 7.5 Prod Upload Package Allowlist

Erlaubt:

```text
sessions/.../metadata.json
sessions/.../alignment/*.json
sessions/.../derived/*.mp3
sessions/.../items/**/*.mp3
db/import_payload.json
config/research_player/**/*.json    # nur wenn explizit runtime-relevant
manifest.json
checksums.sha256
reports/*.md
reports/*.txt
reports/*.json
```

Verboten:

```text
*.wav
*.TextGrid
*.xlsx
secure/
raw/
source/
alignment_source/
working/
mfa_corpus/
mfa_output/
consent/questionnaire PDFs
temporary files
```

---

## 8. Webapp Access Request Form In Production

Die Produktionsverdrahtung für das Webapp-Access-/Request-Formular ist noch nicht verifizierbar, solange Checkout, produktive Env-Datei und Docker-Stack nicht bereitstehen.

### 8.1 Aktueller Stand laut Preflight

- Host-Mail-Werkzeuge sind vorhanden: `mail`, `mailx`, `sendmail` und Exim.
- Die ProMat-spezifische Formularintegration kann noch nicht geprüft werden, weil App-Checkout, produktive Env-Datei und produktiver Docker-Stack noch nicht existieren.

### 8.2 Erwartete nicht-geheime Env-Key-Namen

Nur Key-Namen dokumentieren, keine Werte:

```text
RATE_LIMIT_STORAGE_URI
AUTH_ACCESS_REQUEST_MAIL_ENABLED
AUTH_ACCESS_REQUEST_EMAIL
AUTH_ACCESS_REQUEST_SUBJECT
AUTH_ACCESS_REQUEST_FROM_EMAIL
AUTH_ACCESS_REQUEST_REPLY_TO_ENABLED
AUTH_MAIL_BACKEND
AUTH_MAIL_FROM_EMAIL
AUTH_MAIL_FROM_NAME
AUTH_MAIL_DEFAULT_REPLY_TO
AUTH_MAIL_SENDMAIL_PATH
AUTH_MAIL_TIMEOUT_SECONDS
AUTH_ACCESS_REQUEST_SMTP_HOST
AUTH_ACCESS_REQUEST_SMTP_PORT
AUTH_ACCESS_REQUEST_SMTP_USERNAME
AUTH_ACCESS_REQUEST_SMTP_PASSWORD
AUTH_ACCESS_REQUEST_SMTP_USE_TLS
AUTH_ACCESS_REQUEST_SMTP_USE_SSL
AUTH_ACCESS_REQUEST_SMTP_TIMEOUT_SECONDS
AUTH_ACCESS_REQUEST_FORM_MAX_AGE_SECONDS
AUTH_ACCESS_REQUEST_MIN_SUBMIT_SECONDS
```

Secret-Werte, Zugangsdaten und vollständige Secret-Dateien werden nicht in Repo-Doku, Logs oder Reports dokumentiert.

### 8.3 Produktionsanforderungen für das Formular

- Für v0.7 ist `AUTH_MAIL_BACKEND=sendmail` mit lokalem sendmail-kompatiblem Transport der empfohlene Host-Pfad; SMTP bleibt als alternative Backend-Konfiguration erhalten.
- `AUTH_MAIL_FROM_EMAIL` muss eine serverseitig erlaubte Absenderadresse sein, `AUTH_MAIL_FROM_NAME` steuert den sichtbaren Anzeigenamen.
- Access-Request-Benachrichtigungen nutzen die Antragstelleradresse als `Reply-To`; Admin-Einladungen nutzen die E-Mail-Adresse des auslösenden Admins als `Reply-To`.
- Wenn direkter Versand deaktiviert ist oder fehlschlägt, bleibt die manuelle Kopie von Link, Betreff und Nachrichtentext als Fallback erhalten.
- App-seitige Implementierung und Serverkonfiguration müssen vor Go-Live verdrahtet und smoke-getestet sein.
- CSRF-Schutz muss aktiv sein.
- Rate Limiting muss aktiv sein.
- Spam-/Abuse-Schutz muss aktiv sein.
- Eingaben müssen validiert werden.
- Fehlerfälle müssen klar behandelt werden, ohne personenbezogene Daten in Logs offenzulegen.
- Nach Deployment muss eine harmlose Testsendeprobe erfolgen.
- Danach Logs nur metadata-basiert und ohne Offenlegung persönlicher Inhalte prüfen.
- Wenn Form Delivery fehlschlägt, muss das Verhalten klar rückrollbar sein; kein stilles `success`, wenn Mailversand oder Folgeaktion fehlschlagen.

### 8.4 SMTP/Mail Dependency Checks nach Freigabe

Read-only bzw. nicht-invasive Prüfungen nach Deployment:

- prüfen, dass die benötigten Env-Dateien unter `/srv/webapps/promat/config` vorhanden sind
- prüfen, dass die App die Form-Route erfolgreich rendert
- prüfen, dass eine harmlose Testanfrage verarbeitet wird
- prüfen, dass Mail-/App-Logs nur technisch notwendige Metadaten enthalten
- prüfen, dass bei SMTP-Fehlern ein klarer Failure-Pfad statt stiller Zustellungslücke greift
- falls das Formular für den Produktionsbetrieb kritisch ist, soll `/ready` die erforderlichen Formular-Abhängigkeiten reflektieren

---

## 9. nginx And TLS

- Laut Preflight existiert aktuell kein nginx-vHost für `pronunciation-matters.de`, `www.pronunciation-matters.de` oder `promat.hispanistica.com`.
- Laut Preflight existiert aktuell kein TLS-Zertifikat für `pronunciation-matters.de` oder `www.pronunciation-matters.de`.
- nginx soll `pronunciation-matters.de` auf `http://127.0.0.1:8000` reverse-proxien.
- Falls `www` im Zertifikat enthalten ist, soll `www.pronunciation-matters.de` auf `https://pronunciation-matters.de` umleiten.
- `promat.hispanistica.com` bleibt ein optionaler späterer Alias und ist mangels DNS nicht Teil des initialen v0.7-Deploys.
- nginx-Edits, certbot-Issuance und Reloads sind genehmigungspflichtige Runtime-Schritte.
- Vor jedem Reload muss `nginx -t` erfolgreich laufen.

---

## 10. Monitoring

Zukünftige Monitoring-Einträge sollen mindestens enthalten:

- Container:
  - `promat-web-prod`
  - `promat-db-prod`
- Lokale URLs:
  - `http://127.0.0.1:8000/`
  - `http://127.0.0.1:8000/health`
  - `http://127.0.0.1:8000/ready`
- Öffentliche URLs:
  - `https://pronunciation-matters.de/`
  - `https://pronunciation-matters.de/health`
  - `https://pronunciation-matters.de/ready`

Monitoring bleibt notify-only und darf weder Container noch Services, Mounts, Runner oder Daten automatisch reparieren.

---

## 11. Deployment Phases For First Production Deploy

Die bisherige Checkliste wird für v0.7 in explizite Phasen zerlegt.

### Phase A. Read-only diagnostics

Ziel:

- Host-, Storage-, Port-, nginx-, DNS- und Runner-Ausgangslage read-only bestätigen.

Erwartete Fakten aus dem Preflight:

- bestehende Apps gesund
- `8000` frei, `5000`, `6000`, `7000`, `3100` belegt
- ProMat-App-Root und Daten-Bind-Mount laut Aufgaben-Kontext vorhanden; kein ProMat-Runner, kein ProMat-nginx-vHost, kein TLS-Zertifikat, kein Docker-Stack

### Phase B. Documentation update and approval

Ziel:

- Repo-Doku und Servervorgehen freigabefähig machen.

Umfang:

- diese Planungsdatei
- aktive Upload-Package-Spec
- Deploy-Report nach Abschluss der Runtime-Arbeiten

### Phase C. One-time storage rename

Status:

- laut Aufgaben-Kontext vom 2026-05-27 bereits abgeschlossen.

Keine Repo- oder Deploy-Skripte führen diesen Schritt aus. Vor dem ersten Deploy genügt ein read-only Recheck, dass `/srv/webapps_storage/promat/data` existiert und aktiv nach `/srv/webapps/promat/data` gebunden ist.

### Phase D. Create `/srv/webapps/promat/{app,config,runner,data,logs}`

Status:

- laut Aufgaben-Kontext vom 2026-05-27 bereits abgeschlossen.

Die Verzeichnisse werden von Repo-Skripten nicht angelegt, gelöscht oder permission-seitig verändert.

### Phase E. Bind mounts / fstab

Status:

- laut Aufgaben-Kontext vom 2026-05-27 bereits abgeschlossen.

Der Deploy prüft `/srv/webapps/promat/data` und `/srv/webapps/promat/logs`, verändert aber keine Mounts und keine `/etc/fstab`.

### Phase F. Runner / app checkout / config secrets

Ziel:

- ProMat-eigenen Runner unter `/srv/webapps/promat/runner` bereitstellen
- App-Checkout unter `/srv/webapps/promat/app` anlegen
- produktive Secrets nur unter `/srv/webapps/promat/config` bereitstellen

Regeln:

- keine fremden Runner wiederverwenden
- bestehende Runner-Verzeichnisse und Runner-Services nicht verändern
- keine bestehenden App-Secrets kopieren
- keine Secrets ins Repo schreiben
- kein manuelles Editieren des deployed Code-Trees
- produktive Env-Datei unter `/srv/webapps/promat/config/passwords.env` bereitstellen
- Workflow auf `GITHUB_SHA` zurücksetzen und danach nur `scripts/deploy_prod.sh` ausführen

### Phase G. ProMat-only compose deployment

Ziel:

- nur ProMat-Container und nur ProMat-Netz/Volumes deployen.

Erwartete Runtime-Objekte:

```text
promat-web-prod
promat-db-prod
promat-network-prod
promat_postgres_prod
```

Empfohlenes Deploy-Muster:

```bash
docker compose -p promat-prod --env-file /srv/webapps/promat/config/passwords.env -f infra/docker-compose.prod.yml up -d --build --force-recreate
```

### Phase H. Local health/readiness on `127.0.0.1:8000`

Ziel:

- App lokal vor öffentlichem Routing verifizieren.

Erwartete Checks:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/health
http://127.0.0.1:8000/ready
```

Zusätzlich prüfen:

- Docker-Health-Status, falls ein `HEALTHCHECK` definiert ist
- `curl -fsS http://127.0.0.1:8000/health`
- `curl -fsS http://127.0.0.1:8000/ready`
- Deploy nicht als erfolgreich markieren, solange diese Gates nicht grün sind oder eine bekannte temporäre Degradierung nicht dokumentiert wurde

### Phase I. certbot / TLS

Ziel:

- TLS für `pronunciation-matters.de` und optional `www.pronunciation-matters.de` nur nach Freigabe einrichten.

Nicht Teil des initialen TLS-Scope:

- `promat.hispanistica.com`, solange kein DNS vorhanden ist

### Phase J. nginx vhost and redirects

Ziel:

- nginx-vHost für `pronunciation-matters.de` auf `127.0.0.1:8000` einrichten.
- optional `www.pronunciation-matters.de` nach Apex umleiten.

Pflicht vor Reload:

```bash
nginx -t
```

### Phase K. Public checks and form smoke test

Ziel:

- öffentliche Erreichbarkeit prüfen
- Formular smoke-testen
- Fehlerpfade prüfen

Minimum:

- `pronunciation-matters.de` öffentlich erreichbar
- Redirect-Verhalten von `www`, falls eingerichtet
- harmlose Formular-Testsendung
- datensparsame Logprüfung

### Phase L. Monitoring inclusion

Ziel:

- ProMat in das bestehende Monitoring aufnehmen.

Einzubeziehen:

- `promat-web-prod`
- `promat-db-prod`
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/ready`
- `https://pronunciation-matters.de/`
- `https://pronunciation-matters.de/health`
- `https://pronunciation-matters.de/ready`

### Phase M. Server documentation update and deploy report

Ziel:

- serverseitige autoritative Dokumentation nachziehen und den ersten Deploy dokumentieren.

Mindestens prüfen:

```text
/srv/server_documentation/change_log.md
/srv/server_documentation/app_inventory.md
/srv/server_documentation/docker_containers.md
/srv/server_documentation/docker_networks.md
/srv/server_documentation/runtime_paths.md
/srv/server_documentation/storage_mounts.md
/srv/server_documentation/nginx_routing.md
/srv/server_documentation/monitoring.md
/srv/server_documentation/reports/promat_initial_prod_deploy_<timestamp>.md
```

Zusätzliche Cleanup-Folgearbeit nach dem Initial-Deploy:

- serverseitige Dokumentation von historischen `pronunciation-matters`-Storage-Vorbereitungsnamen auf den finalen `promat`-Namensraum bereinigen
- prüfen, welche Bestandsdokumente den späteren Alias `promat.hispanistica.com` fälschlich als Pflichtbestandteil lesen lassen, und diese auf optional/historical zurückführen
- Runner-/Deploy-Dokumentation auf genau einen ProMat-Runner, genau ein Deploy-Script und genau eine produktive Env-Datei verdichten

---

## 12. Hard No-Go Rules

```text
- CO.RA.PAN-Pfade nicht anfassen.
- Keine bestehenden App-Netze für ProMat wiederverwenden.
- Keine bestehenden DB-Container oder DB-Volumes wiederverwenden.
- ProMat nicht an belegte Host-Ports binden.
- Bestehende Runner-Verzeichnisse oder Runner-Services nicht verändern.
- Keine bestehenden App-Secrets kopieren.
- Kein nginx reload ohne explizite Freigabe.
- Keine certbot-Zertifikatsausstellung ohne explizite Freigabe.
- Kein Docker start/stop/build/up/down ohne explizite Freigabe.
- Kein chmod/chown/setfacl/mv/rm/rsync --delete ohne explizite Freigabe.
- Keine Secrets in Repo, Logs, Reports oder Serverdoku.
```

Zusätzlich:

- keine ProMat-Deploys über CO.RA.PAN- oder Games-Runner
- kein manuelles Editieren von `/srv/webapps/promat/app`
- keine direkte Datenübertragung in `current`
- kein direktes Schreiben in einen gerade live verwendeten Release-Pfad

---

## 13. Minimal Approved Runtime Actions Still Required After This Repo Update

Nach diesem Repo-Update bleiben für den echten Produktionspfad nur freigabepflichtige Runtime-Schritte offen:

1. read-only Server-Recheck der im Aufgaben-Kontext gemeldeten Ausgangslage
2. ProMat-eigenen Runner registrieren und App-Checkout plus produktive Env-Datei bereitstellen
3. ProMat-only Compose-Deploy auf `127.0.0.1:8000`
4. lokale `/health`- und `/ready`-Prüfung
5. certbot/TLS nur für `pronunciation-matters.de` und optional `www.pronunciation-matters.de`
6. nginx-vHost plus Redirect für `www`, falls beide Zertifikate vorhanden sind
7. öffentliche Checks, Formular-Smoke-Test und datensparsame Logprüfung
8. Monitoring-Einbindung
9. serverseitige Dokumentation und Initial-Deploy-Report aktualisieren
