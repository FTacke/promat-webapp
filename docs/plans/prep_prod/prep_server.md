# prep_server.md — ProMat Production Server Preparation

Stand: 2026-05-23  
Ziel: Vorbereitung des ProMat-Repos für den späteren kontrollierten Prod-Deploy auf `vhrz2184`.

Diese Datei gehört ins ProMat-Repo. Sie dokumentiert die geplante Server-Zielarchitektur, die einzuhaltenden Serverregeln, die vorzubereitenden Runtime-Pfade, Docker-/Postgres-/nginx-/Monitoring-Konventionen und die offenen Schritte vor dem ersten produktiven Testbetrieb.

---

## 1. Grundsatz

Der Server ist ein Deployment-Ziel, nicht die Quelle der Anwendung. ProMat-Code gehört ins upstream Git-Repo und wird über einen GitHub Runner nach `/srv/webapps/promat/app` deployed. Direktes Bearbeiten von deployed app code auf dem Server ist nicht vorgesehen.

Große ProMat-Medien und ProMat-Daten dürfen nicht ins Git-Repo und nicht ins Docker Image. Sie gehören auf die separate Shared-Storage-Platte unter `/srv/webapps_storage`.

Für alle neuen ProMat-Datei- und Ordnernamen gilt ab jetzt verbindlich:

```text
promat
```

Nicht mehr verwenden:

```text
pronunciation-matters
```

Ausnahme: In bestehender historischer Serverdokumentation und bestehenden vorbereiteten Pfaden kann `pronunciation-matters` noch auftauchen. Vor dem ProMat-Deploy soll dieser vorbereitete Storage-Zweig serverseitig auf `promat` umbenannt werden.

---

## 2. Aktueller Serverzustand, der für ProMat relevant ist

### 2.1 Host

```text
Host: vhrz2184
OS: Ubuntu 22.04.5 LTS
Host root: /srv
Web root: /srv/webapps
Server docs: /srv/server_documentation
```

### 2.2 Shared Storage

Die separate `ext4`-Platte `/dev/sdb1` mit `LABEL=media` ist neutral gemountet:

```text
/dev/sdb1 or LABEL=media -> /srv/webapps_storage
```

CO.RA.PAN nutzt dieselbe Platte bereits so:

```text
/srv/webapps_storage/corapan/media
  -> bind-mounted to /srv/webapps/corapan/media
```

CO.RA.PAN bleibt dadurch unverändert bei:

```text
/srv/webapps/corapan/media -> /app/media
```

Der aktuelle ProMat-Vorbereitungsstand auf dem Server ist noch unter dem längeren Namen angelegt:

```text
/srv/webapps_storage/pronunciation-matters/data
/srv/webapps_storage/pronunciation-matters/media
```

Diese Pfade sind vorbereitet, aber noch nicht app-lokal gebunden. `/srv/webapps/pronunciation-matters` existiert nicht.

Für den späteren ProMat-Deploy soll dieser vorbereitete Storage-Zweig auf `promat` normalisiert werden:

```text
/srv/webapps_storage/promat/data
/srv/webapps_storage/promat/media
```

---

## 3. Zielstruktur für ProMat

### 3.1 Server-Root

```text
/srv/webapps/promat/
  app/
  config/
  data/
  media/
  logs/
  runner/
```

Bedeutung:

| Pfad | Zweck |
| --- | --- |
| `/srv/webapps/promat/app` | Git checkout / deployed working copy |
| `/srv/webapps/promat/config` | serverseitige Env-/Secret-Dateien, nicht ins Repo |
| `/srv/webapps/promat/data` | app-lokaler Bind-Mount auf Shared Storage |
| `/srv/webapps/promat/media` | app-lokaler Bind-Mount auf Shared Storage |
| `/srv/webapps/promat/logs` | ProMat Runtime-Logs |
| `/srv/webapps/promat/runner` | GitHub self-hosted runner für ProMat |

### 3.2 Physischer Storage

```text
/srv/webapps_storage/promat/
  data/
    incoming/
    releases/
    current -> releases/<version>      # erst nach erstem validierten Release anlegen

  media/
    incoming/
    releases/
    current -> releases/<version>      # erst nach erstem validierten Release anlegen
```

### 3.3 App-lokale Bind-Mounts

Sobald `/srv/webapps/promat` existiert:

```text
/srv/webapps_storage/promat/data  -> /srv/webapps/promat/data
/srv/webapps_storage/promat/media -> /srv/webapps/promat/media
```

Empfohlene spätere `/etc/fstab`-Zeilen:

```fstab
/srv/webapps_storage/promat/data  /srv/webapps/promat/data   none  bind  0  0
/srv/webapps_storage/promat/media /srv/webapps/promat/media  none  bind  0  0
```

Keine app-lokalen Bind-Mounts anlegen, bevor `/srv/webapps/promat` bewusst als App-Root erstellt wurde.

---

## 4. Einmalige Umbenennung des vorbereiteten Storage-Zweigs

Der aktuelle Serverzustand enthält vorbereitete Pfade unter:

```text
/srv/webapps_storage/pronunciation-matters
```

Da ab jetzt `promat` verbindlich ist, soll vor dem eigentlichen ProMat-Deploy einmalig serverseitig umbenannt werden:

```bash
sudo mv /srv/webapps_storage/pronunciation-matters /srv/webapps_storage/promat
```

Vorher read-only prüfen:

```bash
findmnt /srv/webapps_storage
ls -lah /srv/webapps_storage
ls -lah /srv/webapps_storage/pronunciation-matters
test ! -e /srv/webapps_storage/promat
```

Danach prüfen:

```bash
ls -lah /srv/webapps_storage/promat
find /srv/webapps_storage/promat -maxdepth 3 -type d | sort
```

Erwartete Struktur nach Umbenennung:

```text
/srv/webapps_storage/promat/data/incoming
/srv/webapps_storage/promat/data/releases
/srv/webapps_storage/promat/media/incoming
/srv/webapps_storage/promat/media/releases
```

Anschließend Serverdokumentation aktualisieren:

```text
/srv/server_documentation/storage_mounts.md
/srv/server_documentation/runtime_paths.md
/srv/server_documentation/server_topology.md
/srv/server_documentation/app_inventory.md
/srv/server_documentation/change_log.md
```

Wichtig: Keine CO.RA.PAN-Pfade ändern. CO.RA.PAN muss weiter auf `/srv/webapps/corapan/media` laufen.

---

## 5. Docker-Zielarchitektur

### 5.1 Container-Namen

Verbindliche ProMat-Namen:

```text
promat-web-prod
promat-db-prod           # falls eigene Postgres-DB als Container
promat-worker-prod       # falls Import-/Integrationspipeline als Worker läuft
```

Nicht verwenden:

```text
pronunciation-matters-web-prod
pronmat-web-prod
```

### 5.2 Docker-Netzwerk

Bestehende Netze auf dem Server:

```text
corapan-network-prod
games-backend-prod
hedgedoc_hedgedoc_net
bridge
host
none
```

ProMat soll nicht an bestehende App-Netze angeschlossen werden, solange keine echte technische Abhängigkeit besteht. Dadurch werden CO.RA.PAN, Games und HedgeDoc nicht unnötig gekoppelt.

Empfohlen:

```text
promat-network-prod
```

Grundregel:

```text
ProMat bekommt ein eigenes Docker-Netzwerk.
Nicht corapan-network-prod wiederverwenden.
Nicht games-backend-prod wiederverwenden.
Nicht hedgedoc_hedgedoc_net wiederverwenden.
```

Falls ProMat später bewusst auf CO.RA.PAN-Dienste zugreifen soll, muss diese Kopplung separat geplant und dokumentiert werden. Kein implizites Cross-App-Networking.

### 5.3 Ports

Bereits dokumentierte Host-Ports:

| App | Host-Port |
| --- | --- |
| CO.RA.PAN | `127.0.0.1:6000 -> 5000` |
| Games | `127.0.0.1:7000 -> 5000` |
| HedgeDoc | `127.0.0.1:3100 -> 3000` |
| Marele | `0.0.0.0:5000 -> 5000` |

Empfohlener ProMat-Host-Port:

```text
127.0.0.1:8000 -> container:5000
```

Vor Nutzung prüfen:

```bash
ss -ltnp | grep -E ':8000\b' || true
docker ps --format 'table {{.Names}}\t{{.Ports}}'
```

Nur an `127.0.0.1` binden, nicht an `0.0.0.0`, wenn nginx als öffentlicher Reverse Proxy davor sitzt.

---

## 6. Postgres-Planung

### 6.1 Grundsatz

ProMat soll keine vorhandene App-DB mitbenutzen.

Nicht verwenden:

```text
corapan-db-prod
games-db-prod
hedgedoc_db
host PostgreSQL ohne bewusste Entscheidung
```

Empfohlen ist eine eigene containerisierte Postgres-Instanz:

```text
promat-db-prod
```

mit eigenem Docker named volume:

```text
promat_postgres_prod
```

und eigener interner DB-Konfiguration über serverseitige Env-Datei.

### 6.2 Warum eigene DB?

- CO.RA.PAN, Games und HedgeDoc haben eigene DB-Abhängigkeiten.
- Host-level PostgreSQL existiert zusätzlich, ist aber separat zu betrachten.
- DB-Migrationen, Schemaänderungen und Restarts sind genehmigungspflichtige Runtime-Aktionen.
- Eine eigene ProMat-DB minimiert das Risiko für bestehende produktive Apps.

### 6.3 Secret-Regel

Keine Passwörter, Tokens, DSNs oder vollständigen Connection Strings ins Repo oder in Serverdokumentation schreiben.

Serverseitig:

```text
/srv/webapps/promat/config/passwords.env
```

oder:

```text
/srv/webapps/promat/config/promat.env
```

Im Repo nur Variablennamen dokumentieren, keine Werte.

Beispiel erlaubte nicht-geheime Key-Namen:

```text
PROMAT_ENV
PROMAT_PUBLIC_BASE_URL
PROMAT_DATA_ROOT
PROMAT_MEDIA_ROOT
PROMAT_LOG_ROOT
DATABASE_URL
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
```

Die Werte liegen ausschließlich serverseitig.

---

## 7. Empfohlene Compose-Struktur

Beispielskizze für `infra/docker-compose.prod.yml` im ProMat-Repo:

```yaml
services:
  promat-web-prod:
    container_name: promat-web-prod
    build:
      context: ..
      dockerfile: infra/Dockerfile
    restart: unless-stopped
    env_file:
      - /srv/webapps/promat/config/passwords.env
    ports:
      - "127.0.0.1:8000:5000"
    volumes:
      - /srv/webapps/promat/data:/app/data:ro
      - /srv/webapps/promat/media:/app/media:ro
      - /srv/webapps/promat/logs:/app/logs
    depends_on:
      - promat-db-prod
    networks:
      - promat-network-prod
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://127.0.0.1:5000/health"]
      interval: 30s
      timeout: 5s
      retries: 5
      start_period: 20s

  promat-db-prod:
    image: postgres:16-alpine
    container_name: promat-db-prod
    restart: unless-stopped
    env_file:
      - /srv/webapps/promat/config/passwords.env
    volumes:
      - promat_postgres_prod:/var/lib/postgresql/data
    networks:
      - promat-network-prod
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \"$${POSTGRES_USER}\" -d \"$${POSTGRES_DB}\""]
      interval: 30s
      timeout: 5s
      retries: 5

networks:
  promat-network-prod:
    name: promat-network-prod
    driver: bridge

volumes:
  promat_postgres_prod:
    name: promat_postgres_prod
```

Falls die App zur Laufzeit in `/app/data` oder `/app/media` schreiben muss, nicht `:ro` verwenden oder Schreibbereiche trennen. Bevorzugt:

```text
/app/data und /app/media für versionierte Daten/Medien möglichst read-only
/app/runtime oder /app/storage für mutable Laufzeitdateien
```

---

## 8. ProMat-Daten- und Medienpipeline

### 8.1 Grundsatz

Nie direkt in `current` rsyncen. Nie Daten halb-live überschreiben.

Zielmuster:

```text
incoming/<timestamp> -> validate/integrate -> releases/<timestamp> -> current
```

### 8.2 Daten

```text
/srv/webapps_storage/promat/data/
  incoming/
    2026-05-23_120000/
  releases/
    2026-05-23_120000/
  current -> releases/2026-05-23_120000
```

App sieht:

```text
/srv/webapps/promat/data/current -> /app/data/current
```

oder, wenn Compose direkt `/srv/webapps/promat/data/current:/app/data:ro` mountet:

```text
/app/data
```

### 8.3 Medien

```text
/srv/webapps_storage/promat/media/
  incoming/
    2026-05-23_120000/
  releases/
    2026-05-23_120000/
  current -> releases/2026-05-23_120000
```

### 8.4 Integrationsscript

Empfohlener Repo-Pfad:

```text
scripts/integrate_data.sh
```

oder getrennt:

```text
scripts/integrate_data.sh
scripts/integrate_media.sh
```

Serverseitige Verwendung:

```bash
cd /srv/webapps/promat/app
bash scripts/integrate_data.sh /srv/webapps/promat/data/incoming/<timestamp>
bash scripts/integrate_media.sh /srv/webapps/promat/media/incoming/<timestamp>
```

Das Script darf:

- validieren
- normalisieren
- Indizes/Manifeste erzeugen
- einen Release-Ordner erzeugen
- `current` atomar umschalten

Das Script darf nicht:

- vorhandene produktive Releases blind löschen
- `rsync --delete` ohne explizite Freigabe verwenden
- CO.RA.PAN-Pfade anfassen
- Serverdokumentation ungefragt ändern

---

## 9. nginx-Planung

nginx ist Runtime-Konfiguration. Lesen ist okay, Edit/Reload nur nach expliziter Freigabe.

Aktuelle dokumentierte Domains:

| Domain | Upstream |
| --- | --- |
| `corapan.hispanistica.com` | `http://127.0.0.1:6000` |
| `games.hispanistica.com` | `http://127.0.0.1:7000` |
| `notes.hispanistica.com` | `http://127.0.0.1:3100` |
| `marele.hispanistica.com` | `http://127.0.0.1:5000` |

Geplanter ProMat-Upstream:

```text
http://127.0.0.1:8000
```

Mögliche Domain, final noch zu entscheiden:

```text
promat.hispanistica.com
```

Vor nginx-Änderung prüfen:

```bash
sudo nginx -T
grep -RIn '8000\|promat' /etc/nginx || true
curl -I http://127.0.0.1:8000/health
```

Nach genehmigter nginx-Konfiguration:

```bash
sudo nginx -t
sudo systemctl reload nginx
curl -I https://promat.hispanistica.com/
```

`systemctl reload nginx` nur nach Freigabe.

---

## 10. Health, Readiness und Monitoring

ProMat soll von Anfang an bereitstellen:

```text
/health
/ready
```

### 10.1 Semantik

```text
/health
  Liveness: Prozess läuft, App antwortet.

/ready
  Readiness: App kann ihre Runtime-Abhängigkeiten nutzen:
  - DB erreichbar
  - Datenpfad lesbar
  - Medienpfad lesbar
  - notwendige Manifeste/Indizes vorhanden
```

### 10.2 Erwartete Statuscodes

```text
/health -> 200 bei laufender App
/ready  -> 200 bei vollständiger Bereitschaft
/ready  -> 503 oder JSON status=degraded/unhealthy bei fehlenden Dependencies
```

### 10.3 Monitoring-Integration

Bestehendes Monitoring:

```text
/srv/server_monitoring/webapp_healthcheck.sh
/srv/server_monitoring/healthcheck_targets.conf
```

Manueller Check ohne Mail:

```bash
/srv/server_monitoring/webapp_healthcheck.sh check
```

ProMat soll später in `healthcheck_targets.conf` ergänzt werden mit:

- Container:
  - `promat-web-prod`
  - `promat-db-prod`
  - ggf. `promat-worker-prod`
- Lokale URLs:
  - `http://127.0.0.1:8000/`
  - `http://127.0.0.1:8000/health`
  - `http://127.0.0.1:8000/ready`
- Öffentliche URL:
  - `https://promat.hispanistica.com/` oder finale Domain

Monitoring bleibt notify-only. Es darf keine Container reparieren, keine Services neu starten, keine Mounts ändern und keine Daten anfassen.

---

## 11. GitHub Runner und Deploy-Modell

### 11.1 Zielstruktur

```text
/srv/webapps/promat/runner
/srv/webapps/promat/app
/srv/webapps/promat/config
/srv/webapps/promat/logs
```

### 11.2 Runner-Service

Geplanter systemd-Service-Name:

```text
actions.runner.FTacke-promat.promat-prod.service
```

Der exakte Name hängt vom GitHub-Repo und Runner-Label ab. Bestehendes Muster:

```text
actions.runner.<owner-repo>.<runner-name>.service
```

### 11.3 Workflow

Empfohlener Workflow im ProMat-Repo:

```yaml
name: Deploy production

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: [self-hosted, promat-prod]
    steps:
      - name: Deploy on server
        run: |
          cd /srv/webapps/promat/app
          bash scripts/deploy_prod.sh
```

### 11.4 Deploy-Script

Empfohlener Repo-Pfad:

```text
scripts/deploy_prod.sh
```

Mindestverhalten:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd /srv/webapps/promat/app

git fetch origin main
git reset --hard origin/main

docker compose \
  --env-file /srv/webapps/promat/config/passwords.env \
  -f infra/docker-compose.prod.yml \
  up -d --build --remove-orphans

docker ps --filter name=promat
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:8000/ready || true
```

Keine Secrets ausgeben. Keine `.env` auscatten.

---

## 12. Vorbereitungs-Checkliste vor erstem ProMat-Deploy

### 12.1 Read-only prüfen

```bash
hostname
date -Is
findmnt /srv/webapps_storage
ls -lah /srv/webapps_storage
ls -lah /srv/webapps_storage/promat 2>/dev/null || true
ls -lah /srv/webapps_storage/pronunciation-matters 2>/dev/null || true
docker network ls
docker ps
ss -ltnp
grep -RIn 'promat\|8000' /etc/nginx || true
```

### 12.2 Storage normalisieren

Falls noch vorhanden:

```text
/srv/webapps_storage/pronunciation-matters
```

und noch nicht vorhanden:

```text
/srv/webapps_storage/promat
```

dann nach Freigabe:

```bash
sudo mv /srv/webapps_storage/pronunciation-matters /srv/webapps_storage/promat
```

### 12.3 App-Root erstellen

Nach Freigabe:

```bash
sudo mkdir -p /srv/webapps/promat/{app,config,logs,runner}
sudo mkdir -p /srv/webapps/promat/data
sudo mkdir -p /srv/webapps/promat/media
```

### 12.4 Bind-Mounts setzen

Nach Freigabe `/etc/fstab` ergänzen:

```fstab
/srv/webapps_storage/promat/data  /srv/webapps/promat/data   none  bind  0  0
/srv/webapps_storage/promat/media /srv/webapps/promat/media  none  bind  0  0
```

Dann:

```bash
sudo findmnt --verify --verbose --tab-file /etc/fstab
sudo mount /srv/webapps/promat/data
sudo mount /srv/webapps/promat/media
findmnt /srv/webapps/promat/data
findmnt /srv/webapps/promat/media
```

### 12.5 Docker-Netz und Container

Wenn Compose das Network selbst anlegt, keine manuelle Anlage nötig.

Wenn manuell nötig, nur nach Freigabe:

```bash
docker network create promat-network-prod
```

Dann Deploy über Runner/Workflow oder kontrolliert über:

```bash
cd /srv/webapps/promat/app
bash scripts/deploy_prod.sh
```

### 12.6 Healthchecks

```bash
docker ps --filter name=promat
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/ready
```

Wenn nginx schon konfiguriert ist:

```bash
curl -I https://promat.hispanistica.com/
```

### 12.7 Monitoring ergänzen

Nach App-Deploy und stabiler Domain:

```text
/srv/server_monitoring/healthcheck_targets.conf
```

um ProMat ergänzen.

Danach:

```bash
/srv/server_monitoring/webapp_healthcheck.sh check
```

Nur `check`, nicht `alert`, nicht `monthly`.

---

## 13. Was auf keinen Fall passieren darf

```text
- Keine CO.RA.PAN-Pfade für ProMat wiederverwenden.
- ProMat nicht unter /srv/webapps/corapan/... ablegen.
- ProMat nicht an corapan-network-prod hängen, außer eine echte Cross-App-Abhängigkeit ist bewusst geplant.
- ProMat nicht an games-backend-prod hängen.
- Keine bestehenden DB-Container mitbenutzen.
- Keine bestehenden Docker volumes löschen.
- Kein nginx reload ohne Freigabe.
- Kein docker compose down für fremde Apps.
- Keine deployed app code edits unter /srv/webapps/*/app.
- Keine Secrets in Repo, Logs, Reports oder Serverdoku.
- Kein rsync direkt nach current.
- Kein rsync --delete ohne explizite Freigabe und geprüfte Quelle/Ziel.
```

---

## 14. Namenskonventionen

Verbindlich:

| Bereich | Name |
| --- | --- |
| App short name | `promat` |
| Server root | `/srv/webapps/promat` |
| Shared storage root | `/srv/webapps_storage/promat` |
| Web container | `promat-web-prod` |
| DB container | `promat-db-prod` |
| Worker container | `promat-worker-prod` |
| Docker network | `promat-network-prod` |
| DB volume | `promat_postgres_prod` |
| Runner label | `promat-prod` |
| Runner service suffix | `promat-prod` |
| Env file | `/srv/webapps/promat/config/passwords.env` |
| Host port | `127.0.0.1:8000` |
| Internal app port | `5000` |
| Internal data path | `/app/data` |
| Internal media path | `/app/media` |
| Internal logs path | `/app/logs` |

Nicht verwenden:

```text
pronunciation-matters
pronmat
pm
```

---

## 15. Offene Entscheidungen vor dem finalen Prod-Test

- Finale Domain:
  - Vorschlag: `promat.hispanistica.com`
- App-Port intern:
  - Vorschlag: `5000`
- Host-Port:
  - Vorschlag: `127.0.0.1:8000`
- Eigene DB:
  - Empfehlung: ja, `promat-db-prod`
- Worker:
  - nötig, wenn Daten-/Medienintegration regelmäßig serverseitig laufen soll
- Schreibmodell:
  - Sind `/app/data` und `/app/media` read-only?
  - Gibt es zusätzlich `/app/runtime` für Schreibdaten?
- Erste Datenlieferung:
  - Format
  - Validierungsregeln
  - Release-Manifest
  - Rollback-Strategie
- Monitoring:
  - Welche URLs außer `/`, `/health`, `/ready` kritisch sind
- Backup:
  - DB-Dumps
  - Daten-/Medien-Releases
  - Umgang mit alten Releases

---

## 16. Minimaler Zielzustand für ersten internen Prod-Test

Für den ersten nur selbst genutzten Prod-Test reicht:

```text
/srv/webapps/promat/app
/srv/webapps/promat/config/passwords.env
/srv/webapps/promat/logs
/srv/webapps_storage/promat/data
/srv/webapps_storage/promat/media
/srv/webapps/promat/data -> bind mount
/srv/webapps/promat/media -> bind mount
promat-web-prod
promat-db-prod
promat-network-prod
127.0.0.1:8000
/health
/ready
```

Optional erst später:

```text
public nginx route
public DNS
server monitoring inclusion
worker container
automated data integration
```

Wenn die App aber öffentlich über nginx erreichbar sein soll, müssen nginx und Monitoring direkt mit eingeplant werden.

---

## 17. Abschlussregel

Jeder produktive Schritt auf dem Server muss nach dem Servermodell dokumentiert werden:

```text
/srv/server_documentation/change_log.md
/srv/server_documentation/app_inventory.md
/srv/server_documentation/docker_containers.md
/srv/server_documentation/docker_networks.md
/srv/server_documentation/runtime_paths.md
/srv/server_documentation/storage_mounts.md
/srv/server_documentation/nginx_routing.md
/srv/server_documentation/monitoring.md
```

Nicht jede Datei wird bei jedem Schritt geändert. Aber nach jedem ProMat-Deploy-Schritt muss geprüft werden, welche autoritativen Dateien betroffen sind.

Zusätzlich sollte für den ersten ProMat-Prod-Deploy ein Report erzeugt werden:

```text
/srv/server_documentation/reports/promat_initial_prod_deploy_<timestamp>.md
```

Dieser Report sollte enthalten:

- ausgeführte Schritte
- gesetzte Mounts
- Containerstatus
- Docker-Netzwerk
- DB-Volume
- nginx-Upstream
- Healthcheck-Ergebnisse
- Monitoring-Ergebnis
- offene Folgearbeiten
