# Deployment Readiness + Repo Hygiene Audit for v0.7

## 1. Scope

Geprüft wurden read-only:

- Repo-Hygiene und Working Tree
- aktive vs. historische Dokumentation
- vorhandene Release-, CI- und Governance-Dateien
- Docker-, Compose-, Env- und Runtime-Verdrahtung im Repo
- vorhandene Data-Integration-Pfade und Scripts
- vorhandene serverbezogene Planungsdokumente im Repo
- ausgewählte read-only Checks: `git status`, `git tag`, Compile, Governance-Check, fokussierte Pytests, `docker compose ... config`

Ausdrücklich nicht durchgeführt:

- keine Code-Fixes
- keine Änderungen an Docker, nginx, Server, Runner, Services oder Firewall
- keine Migrationen, Seeds, Imports, Mails, Releases oder Tags
- keine Live-Server-Inspektion, weil in diesem Workspace kein Serverzugriff vorlag

## 2. Kurzfazit

- Repo-Hygiene-Status: nicht release-sauber; der Working Tree ist dirty und das Repo enthält zusätzlich einige historisch getrackte Root-/QA-Artefakte.
- v0.7-Readiness: fachlich weit fortgeschritten, aber formal noch nicht release-reif, weil Versionierungs- und Release-Artefakte fehlen und der aktuelle Governance-Gate nicht grün ist.
- Deployment-Readiness: grundlegende Container- und Env-Basis ist vorhanden und Compose validiert syntaktisch, aber produktive Server-, Runner-, Port-, Backup- und Runbook-Fragen sind noch nicht operationalisiert.
- Server-/nginx-Kontextstatus: nur repo-seitige Planungsinformationen vorhanden; keine verifizierte Live-Server-Dokumentation im Repo und kein direkter Serverzugriff in diesem Run.
- Data-Integration-Readiness: die lokale Intake-, Archiv- und Upload-Paket-Pipeline ist gut vorbereitet; für den ersten Server-Deploy fehlen aber der serverseitige Integrationsablauf, das minimale v0.7-Dataset und die Freigabereihenfolge.
- Wichtigste Blocker: dirty Working Tree, fehlender Release-Prozess, fehlendes Deployment-Runbook, ungeklärtes Runner-/SSH-Modell, ungeklärte Live-Ports/Domains/nginx-Struktur, fehlende Backup-/Rollback-/Monitoring-Dokumentation, fehlender dedizierter `/ready`-Endpunkt.
- Empfohlene Reihenfolge: Repo-Hygiene und Release-Kandidaten-Commit festziehen, Serverkontext verifizieren, Deployment-Runbook schreiben, Runner-/Deploy-Pipeline festlegen, minimale Datenintegration definieren, dann erster kontrollierter Deploy.

## 3. Repo Hygiene

### 3.1 Bewertungstabelle

| Bereich | Befund | Risiko | Empfehlung |
| --- | --- | --- | --- |
| Working Tree | `vor Release bereinigen`: `git status --short --branch` zeigt laufende Änderungen an CSS/JS/Auth-Templates sowie untracked Run-Logs und `scripts/qa/responsive_smoke.py`. | Ein v0.7-Tag würde lokalen Zwischenstand mit möglicher Scope-Unschärfe einfrieren. | Vor Release nur einen bewusst finalisierten, reviewten Satz Änderungen auf dem Kandidaten-Commit lassen. |
| Root-Debug-/QA-Dateien | `vor Release bereinigen`: `start.txt`, `_es_diag.txt`, `qa_check.py`, `simple_qa.py` sowie `app/capture_qa.py` sind in `HEAD` getrackt. | Widerspruch zur eigenen Root-Hygiene; erhöht Rauschen und Audit-Aufwand. | In einem separaten Repo-Hygiene-Run entscheiden: löschen, verschieben nach `scripts/qa/` oder klar als bewusstes Utility dokumentieren. |
| Lokale Root-Inspektionsdateien | `nicht committen`: `inspect_dw.py` und `inspect_styles.py` liegen lokal im Repo-Root, werden aber von `.gitignore` abgefangen. | Lokal okay, im Commit ein Governance-Verstoß. | Lokal belassen oder außerhalb des Roots verschieben; nicht in Release-Commits übernehmen. |
| `tmp/` und `app/tmp/` | `bewusst behalten`: beide Verzeichnisse werden via `.gitignore` ignoriert; `tmp/ui-qa/...` ist damit lokal-only. | Gering, solange keine Dateien daraus bewusst nachverfolgt werden. | QA-Artefakte weiterhin nur unter `tmp/ui-qa/...` erzeugen. |
| `scripts/qa/responsive_smoke.py` | `unklar`: liegt im kanonischen Utility-Ordner, ist aber aktuell untracked und enthält lokale Defaults für Dev-Login/QA. | Entweder nützliches wiederverwendbares QA-Tool oder halbfertiges lokales Hilfsscript. | Vor Release bewusst entscheiden: sauber committen oder lokal lassen. |
| `.gitignore` | `unklar`: gut für `tmp/`, `inspect_*.py`, Screenshots und `start.txt`; unzureichend gegen bereits getrackte Root-Dateien und nicht generisch für `qa_check.py`, `simple_qa.py`, `_es_diag.txt`. | Root-Hygiene-Verstöße werden nur teilweise präventiv verhindert. | Im späteren Cleanup Regeln und Tracking-Zustand gemeinsam bereinigen; Ignore allein löst getrackte Altlasten nicht. |
| `docs/agent-runs/` | `bewusst behalten`: Run-Logs sind zahlreich, aber korrekt im nicht-normativen Ordner gebündelt. | Niedrig, solange sie nicht als aktive Spec missverstanden werden. | Beibehalten; neue aktive Regeln weiterhin nur in `docs/spec/` oder `docs/runbooks/`. |
| `docs/spec/` | `OK`: aktive Source of Truth ist klar abgegrenzt und mit Root-/Scoped-AGENTS konsistent. | Gering. | Für v0.7 keine Shadow-Doku daneben aufbauen. |
| `docs/runbooks/` | `vor Release bereinigen`: es gibt nützliche Dev-/Intake-Runbooks, aber kein Deployment-/Server-/Release-Runbook. | Operative Lücke vor erstem systematischen Deploy. | Vor dem ersten Server-Deploy mindestens ein Production-Deployment-Runbook ergänzen. |
| `docs/plans/` | `unklar`: Planungsdokumente sind als Planung markiert, enthalten aber teils sehr konkrete Server- und Deploy-Annahmen. | Gefahr, dass Plan statt verifizierter Runbook-/Serverdoku verwendet wird. | Vor Deploy nur als Input behandeln; verifizierte Erkenntnisse in Runbook oder Serverdoku überführen. |
| `.github/` Governance | `OK`: `SECURITY.md`, PR-Template, Issue-Template und Dependabot sind vorhanden. | Gering. | Beibehalten. |
| `CODEOWNERS` | `bewusst behalten`: bewusst kommentar-only, noch nicht operativ. | Required reviews lassen sich damit noch nicht belastbar aktivieren. | Erst mit realen Teams/Handles scharf schalten. |
| CI-Konfiguration | `vor Release bereinigen`: es gibt genau einen PR-CI-Workflow, aber keinen Deploy- oder Release-Workflow. | Release- und Deploy-Prozess bleiben manuell und fehleranfällig. | Vor v0.7 Deploy-Gates und Release-Workflow definieren. |
| Historische Reports | `bewusst behalten`: alte Audits und Run-Logs sind im richtigen Ort. | Einzelne ältere Audits spiegeln nicht mehr den aktuellen Codezustand. | In der Freigabe klar auf aktive Specs und aktuelle Checks verweisen, nicht auf alte Audit-Fazitzeilen. |

### 3.2 Working Tree

Aktueller Git-Status in diesem Run:

- modifiziert: mehrere UI-Dateien unter `app/static/`, `app/templates/`, `app/static/js/`
- gelöscht: mehrere alte MD3-/Legacy-Dateien
- untracked: `app/templates/_pm_skeletons/`, vier neue Run-Logs unter `docs/agent-runs/`, `scripts/qa/responsive_smoke.py`

Fazit:

- Der Working Tree ist nicht sauber genug für einen v0.7-Release.
- Die sichtbaren UI-Cleanup-Änderungen können fachlich zum nächsten Release gehören, aber nur als bewusst finalisierte, reviewte Einheit zusammen mit ihren zugehörigen Run-Logs.
- Lokale Root-/tmp-Artefakte und unfertige QA-Helfer dürfen nicht in denselben Release-Commit rutschen.

### 3.3 Governance-Check

Ausgeführter read-only Check: `python ../scripts/ci_governance_checks.py`

Ergebnis:

- Fail: temporäre QA-/Debug-Dateien im Repo-Root
- Fail: `app/src/app/research_views.py` enthält noch eine lokale `if ui_lang == "de"`-Verzweigung in `HEAD`
- Fail im aktuellen Working Tree, aber nicht in `HEAD`: `app/templates/base.html` enthält lokal `pm-footer`

Einordnung:

- Mindestens ein Governance-Problem liegt bereits in `HEAD`.
- Der Governance-Gate ist damit für einen Release-Kandidaten noch nicht belastbar grün.

### 3.4 Aktive vs. historische Doku

Aktiv und sauber abgegrenzt:

- `docs/spec/`
- `AGENTS.md` und scoped `AGENTS.md`
- `docs/runbooks/` für wiederholbare Abläufe

Historisch bzw. nur Planungsinput:

- `docs/agent-runs/`
- `docs/plans/`, insbesondere `docs/plans/prep_prod/prep_server.md` und `docs/plans/prep_prod/prep_intake.md`

Bewertung:

- Die Trennung ist im Repo grundsätzlich klar.
- Für den ersten Deploy reicht die vorhandene Planungsdoku allein noch nicht als operative Grundlage.

## 4. v0.7 Release Readiness

### 4.1 Befund

- Es gibt aktuell keine Git-Tags im Repo.
- Ein `CHANGELOG.md` existiert nicht.
- Es gibt keine dedizierten Release Notes oder ein Release-Verzeichnis.
- Die einzige sichtbare Versionsnummer im Repo ist `app/pyproject.toml` mit `1.0.0`; diese ist derzeit nicht als belastbare Produkt-Release-Strategie für `v0.7` dokumentiert.
- Release-Metadaten sind zur Laufzeit über `APP_VERSION`, `APP_RELEASE_TAG` und `APP_RELEASE_URL` vorgesehen, aber nicht prozessual dokumentiert.

### 4.2 v0.7-Vorschlag

#### Release-Ziel

Erster kontrollierter, dokumentierter Server-Deploy einer operativ gehärteten PROMAT-Basis mit:

- gesicherter App-, Auth- und Research-Readiness
- dokumentierten Betriebsvoraussetzungen
- definierter Minimal-Datenintegration
- reproduzierbarem Deploy-Ablauf

#### Release-Scope

- bisher abgeschlossene Prod-Readiness- und Security-Härtungen
- Access-Request-Mail und Spam-Härtung
- CSP-/Header-/HTML-Senken-Härtung
- Governance- und UI-Cleanup, soweit finalisiert und reviewt
- Teaching- und Research-Basis in ihrem aktuell produktiven Scope
- Docker-/Compose-/Env-Basis für produktiven Betrieb

#### Nicht im Release

- lokale QA-Artefakte und Root-Debug-Dateien
- unfertige oder nur lokal verwendete Utility-Skripte
- serverseitige nginx-/Runner-/systemd-Konfigurationen ohne verifizierten Kontext
- unfreigegebene oder unbestimmte Runtime-Datenimporte
- ad hoc erstellte Release-Dokumente außerhalb der bestehenden Konventionen

#### Voraussetzungen

- sauberer Release-Kandidaten-Working-Tree
- grüner Governance-Gate
- grüner PR-CI-Lauf
- verifiziertes Server-/nginx-/Port-/Runner-Modell
- serverseitig gesetzte Secrets und produktive Volumes
- festgelegter Minimal-Datensatz für den ersten Deploy
- schriftliches Deployment-Runbook

#### Release-Checkliste

1. Release-Kandidaten-Commit mit sauberem Working Tree herstellen.
2. Governance-Check, Compile und fokussierte Release-Tests grün ausführen.
3. Produktions-Compose mit Platzhalterwerten validieren.
4. Deployment-Runbook, Runner-Modell und Serverpfade finalisieren.
5. Minimales v0.7-Dataset und Import-Reihenfolge festlegen.
6. Serverseitige Secrets, Redis, SMTP, DB und Volume-Pfade verifizieren.
7. Ersten kontrollierten Deploy durchführen.
8. Post-Deploy-Health- und Smoke-Checks erfolgreich abschließen.
9. Release Notes finalisieren.
10. Tag setzen und optional GitHub Release veröffentlichen.

#### Empfohlener Tagging-Zeitpunkt

Empfehlung für diesen ersten Deploy:

- noch nicht vorab taggen
- zuerst den finalen Release-Kandidaten-Commit und den ersten kontrollierten Deploy auf genau diesen Commit durchführen
- den Tag `v0.7` direkt nach erfolgreichem Health- und Smoke-Nachweis auf diesen Commit setzen

Begründung:

- Es gibt noch keinen deploy-by-tag-Workflow.
- Server- und Runner-Kontext sind noch nicht vollständig verifiziert.
- Der erste Deploy soll nicht mit einem zu früh gesetzten SemVer-Tag operativ fixiert werden.

Für spätere Releases sollte auf ein deploy-by-tag-Modell umgestellt werden.

#### Empfohlene Release-Notes-Struktur

1. Ziel und Freigabestatus von v0.7
2. Highlights nach Bereichen: Auth/Security, Research, Teaching, Governance, Ops
3. Operative Voraussetzungen und bekannte Grenzen
4. Datenstand und enthaltene Korpora/Teaching-Flächen
5. Deploy- und Migrationshinweise
6. Post-Deploy-Smoke und bekannte Restpunkte

## 5. Deployment Readiness im Repo

### 5.1 Deployment-Tabelle

| Deployment-Bereich | Repo-Status | Fehlende Info | Risiko | Nächster Schritt |
| --- | --- | --- | --- | --- |
| Dockerfile | Vorhanden und grundsätzlich prod-tauglich: Python 3.12 slim, Gunicorn auf Port 5000, `content/` wird ins Image kopiert. | Keine Build-/Image-Release-Strategie dokumentiert. | Mittel. | Docker-Build in Main-Deploy-Gate aufnehmen. |
| Compose-Produktionsbasis | Vorhanden und per `docker compose ... config` erfolgreich validiert. Services: `db`, `rate_limit`, `web`. | Kein Deploy-Runbook, kein fester Project-Name, kein dokumentierter Compose-Aufruf mit `--env-file`. | Mittel. | Produktions-Runbook mit exaktem Compose-Aufruf und Projektkonvention schreiben. |
| Netzwerk | Compose nutzt implizit `infra_default`, nicht das in `prep_server.md` geplante `promat-network-prod`. | Live-Netzwerkmodell des Servers unbekannt. | Mittel. | Entscheiden: explizites Netz oder bewusstes Default-Netz. |
| Ports | Compose bindet `127.0.0.1:6000:5000`. | Ob `6000` auf dem Zielserver frei ist, ist ungeklärt; die Planungsdoku nennt `6000` bereits für CO.RA.PAN und empfiehlt für PROMAT eher `8000`. | Hoch. | Live-Portbelegung und Reverse-Proxy-Upstream vor Runbook verifizieren. |
| Env/Secrets | Template vorhanden: `FLASK_SECRET_KEY`, `JWT_SECRET_KEY`, `POSTGRES_PASSWORD`, Redis, SMTP, Release-Metadaten. | Keine serverseitige Dokumentation, wo die echte Env-Datei liegt und wie sie gepflegt wird. | Hoch. | Serverseitige `passwords.env`-/Secret-Strategie dokumentieren. |
| Daten-Volume | Compose erwartet `/srv/webapps/promat/data:/app/data`. | Live-Existenz, Ownership und Backup-Strategie unbekannt. | Hoch. | Serverpfade und Berechtigungen verifizieren. |
| Public-Volume | Compose erwartet `/srv/webapps/promat/public:/app/public`. | Im Repo existiert aktuell kein `public/`-Verzeichnis; unklar, was v0.7 dort überhaupt benötigt. | Mittel. | Vor Deploy klären, ob `public` leer, vorbereitet oder produktiv benötigt wird. |
| Logs-Volume | Compose erwartet `/srv/webapps/promat/logs:/app/logs`. | Logrotation, Retention und Einsichtspfad nicht dokumentiert. | Mittel bis hoch. | Logging-/Rotation-Konventionen dokumentieren. |
| Healthcheck | Vorhanden: Compose nutzt `/health`; der Endpunkt prüft Flask plus Auth-DB. | Kein dedizierter `/ready`-Endpunkt. | Mittel. | `/ready` im späteren Ops-Run ergänzen oder im Runbook begründet auf `/health` beschränken. |
| Redis / Rate Limiter | Redis-Service ist im Compose enthalten, `RATE_LIMIT_STORAGE_URI` ist Pflicht und in Non-Dev nicht `memory://`. | Kein Server-Runbook für Redis-Backup, Persistence und Monitoring. | Mittel. | Redis-Betriebskonventionen dokumentieren. |
| SMTP / Access Request Mail | Vollständig verdrahtet über Env-Variablen in Compose und Template. | Provider, Absenderdomäne, SPF/DKIM/DMARC und Zustelltestprozess fehlen. | Mittel. | SMTP-Setup-Doku und Testverfahren definieren. |
| DB-Migrationen | SQL-Migrationskette und Migrationsscript sind vorhanden. | Kein Produktionsablauf für wann und wie Migrationen vor Deploy laufen, inkl. Backup und Fehlerfall. | Hoch. | Produktions-Migrationsschritt im Runbook definieren. |
| Initial Admin | Script `app/scripts/create_initial_admin.py` existiert, blockiert Produktion standardmäßig ohne `--allow-production`. | Keine produktive Anleitung für ersten Admin-Account. | Mittel. | Initial-Admin-Prozedur im Runbook festhalten. |
| Backup / Restore | Für die Intake-Pipeline existieren lokale Paket-/Archiv- und importerinterne Rollback-Mechanismen. | Keine Server-DB-/Volume-Backup- oder Restore-Doku für App-Deploys. | Hoch. | Backup-/Restore-Runbook vor erstem öffentlichen Deploy ergänzen. |
| Monitoring | Nur Planungsreferenzen auf `/srv/server_monitoring/...` vorhanden. | Keine verifizierte Monitoring-Einbindung. | Mittel bis hoch. | Live-Monitoring-Konventionen abfragen und dokumentieren. |
| Deploy-Scripts | Kein produktives Deploy-Script im Repo vorhanden. | Exakter Deploy-Ablauf fehlt. | Hoch. | `Production Deployment Runbook` und später `scripts/deploy_prod.*` definieren. |
| GitHub Workflows | Nur `ci.yml` vorhanden. | Kein Main-Deploy-Workflow, kein Manual-Release-Workflow. | Hoch. | Pipeline-Struktur ergänzen. |

### 5.2 Repo-Befunde im Detail

- `app/Dockerfile` ist gegenüber dem früheren Auditstand bereits modernisiert: Gunicorn ist der Entrypoint.
- `app/infra/docker-compose.prod.yml` ist syntaktisch valide.
- Compose verlangt produktive Serverpfade unter `/srv/webapps/promat/...`.
- Compose setzt `PROMAT_RUNTIME_ROOT=/app`, `PROMAT_PUBLIC_ROOT=/app/public`, `PROMAT_TEACHING_CONTENT_ROOT=/app/content/teaching`.
- `PROMAT_PUBLIC_ROOT` ist Pflichtkonfiguration, aber die aktuelle Teaching-Medienauslieferung erfolgt direkt aus `content/teaching/.../media` im Image; die Rolle des separaten `public`-Volumes für v0.7 ist deshalb noch zu klären.

## 6. Server-/nginx-/Apps-Kontext

### 6.1 Gefundene Informationen im Repo

| Thema | Befund | Bedeutung für PROMAT |
| --- | --- | --- |
| Server-Planungsdoku | `docs/plans/prep_prod/prep_server.md` enthält konkrete, aber ausdrücklich nur planende Angaben zu Host, `/srv`, Apps, Ports, nginx, Monitoring und Runner. | Nützlich als Input, aber nicht ausreichend als verifizierte Betriebsdoku. |
| Andere Apps laut Planung | Geplant dokumentiert sind CO.RA.PAN, Games, HedgeDoc und Marele. | Integration darf bestehende Ports, Netze und Pfade nicht kollidieren lassen. |
| Portannahmen laut Planung | Die Planungsdatei dokumentiert `6000` bereits für CO.RA.PAN und empfiehlt für PROMAT eher `8000`. | Konfliktpotenzial mit aktuellem Compose-Port `6000`. |
| Reverse-Proxy | Planungsdatei setzt nginx als vorgeschalteten Reverse Proxy voraus. | Upstream-Port und Domain müssen live verifiziert werden, bevor ein Runbook geschrieben wird. |
| Shared Storage | Planungsdoku nennt `/srv/webapps_storage` und eine Normalisierung von `pronunciation-matters` auf `promat`. | Relevante Serverpfade sind teilweise vorbereitet, aber nicht verifiziert. |
| Monitoring | Planungsdoku referenziert `/srv/server_monitoring/webapp_healthcheck.sh` und `healthcheck_targets.conf`. | Monitoring-Kontext könnte vorhanden sein, ist aber in diesem Run nicht live bestätigt. |
| Runner-Modell | Planungsdoku geht von einem self-hosted GitHub Runner unter `/srv/webapps/promat/runner` aus. | Nur Planungsstand; echte Runner-Existenz und Service-Name sind offen. |

### 6.2 Fehlende Informationen vor einem echten Deployment-Runbook

| Benötigte Info | Warum nötig | Wer/woher |
| --- | --- | --- |
| Live-Host- und App-Inventar unter `/srv` | Damit PROMAT keine Pfade, Users, Gruppen oder Volumes anderer Apps verletzt. | Server-Owner oder read-only Serverzugriff |
| Aktive nginx-Struktur (`sites-enabled`, includes, naming) | Damit das Runbook keinen Proxy-Aufbau erfindet. | Server-Owner oder read-only `nginx -T` |
| Tatsächlich belegte Ports und Upstreams | Compose-Port und nginx-Upstream müssen konfliktfrei sein. | Server-Owner oder read-only `ss -tulpn`, `docker ps` |
| Tatsächliche Domains/Subdomains | Für TLS, HSTS, CSP-Hosts, Release Notes und Smoke-URLs. | Betreiber/Domain-Verantwortliche |
| TLS-/Certbot-Konventionen | Für Erstdeploy, Redirects und Zertifikatsablauf. | Server-Owner / Serverdoku |
| Runner-Modell: self-hosted vs. SSH | Entscheidet GitHub-Secrets, Workflow-Design und Deploy-Befehle. | Repo-/Server-Verantwortliche |
| Existenz und Zustand eines GitHub Runners | Ohne das kann kein Main-Deploy-Workflow belastbar geplant werden. | Server-Owner / GitHub Repo Admin |
| Pfad-, User- und Permission-Konventionen unter `/srv/webapps/promat` | Für Volumes, Logs, Runner und Deploy-User. | Server-Owner |
| Backup- und Restore-Konventionen | Vor Migrationen und Datenintegration zwingend. | Server-Owner / Ops-Verantwortliche |
| Logrotation und Monitoring-Prozess | Für öffentlichen Betrieb und Incident-Triage. | Server-Owner / Ops-Verantwortliche |

Bewertung:

- Ein späteres Deployment-Runbook kann auf Basis der vorhandenen Repo-Pläne vorbereitet werden.
- Es darf aber noch nicht final geschrieben werden, als ob Ports, Domains, nginx und Runner bereits verifiziert wären.

## 7. GitHub Actions / Runner Plan

### 7.1 Ist-Zustand

- Vorhanden: ein Workflow `.github/workflows/ci.yml`
- Nicht vorhanden: Main-Deploy-Workflow
- Nicht vorhanden: Manual-Release-Workflow
- Nicht vorhanden: dokumentiertes Runner- oder SSH-Deploy-Modell

### 7.2 Aktueller CI-Befund

Vorhandenes PR-CI deckt bereits ab:

- Python-Setup
- Dependency-Installation
- `compileall`
- Governance-Checks
- Fokus-Pytests für Auth, Runtime, Research und Security-nahe Bereiche

In diesem Audit ausgeführte read-only Checks:

- `compileall` erfolgreich
- fokussierte Pytests erfolgreich: `tests/test_runtime_config.py`, `tests/test_auth_phase1.py`, `tests/test_research_sessions.py`, `tests/test_research_phenomena.py`, `tests/test_teaching_content.py`
- Security-/Governance-Fokus-Tests erfolgreich
- Governance-Script insgesamt nicht grün

### 7.3 Empfohlene Pipeline-Struktur

#### Workflow 1: PR CI

Soll prüfen:

- `ruff`
- `compileall`
- Governance-Checks
- Auth/Runtime/Access-Request/Research-Sessions/Research-Phenomena-Tests
- Teaching-Content-Tests oder Validator
- `docker compose -f app/infra/docker-compose.prod.yml config` mit Platzhalterwerten

Soll nicht:

- deployen
- echte Secrets laden
- echte Mails senden
- Serverdaten anfassen
- vollständige Browser-E2E auf jedem Push erzwingen

#### Workflow 2: Main Deploy Gate

Soll prüfen:

- alles aus PR CI
- Docker-Build
- Compose-Validierung mit Platzhaltern
- optional Image-Build/Artefakt-Erzeugung
- Deploy nur nach geschützter Trigger-Regel
- Post-Deploy-Healthcheck
- fokussierter Smoke
- definierter Rollback-Hook

Empfehlung:

- nur mit Environment-Protection und Approval
- Deploy des exakten Commit-SHA, nicht des impliziten `main`-Zustands

#### Workflow 3: Manual Release v0.7

Soll leisten:

- manuelle Auslösung
- Auswahl eines Commit-SHA oder später eines Tags
- Prüfung auf sauberen Release-Status
- optional Deploy auf Zielumgebung
- Post-Deploy-Smoke
- optional GitHub Release erzeugen

### 7.4 Secrets-Strategie

GitHub-Secrets nur für:

- SSH-Deploy, falls SSH-Modell gewählt wird
- ggf. Container-Registry-Zugang
- ggf. Release-Automation

Nur serverseitig halten:

- `POSTGRES_PASSWORD`
- `FLASK_SECRET_KEY`
- `JWT_SECRET_KEY`
- SMTP-Credentials
- produktive Redis-/Provider-/Runtime-Werte

Empfehlung:

- bei self-hosted Runner möglichst keine produktiven App-Secrets in GitHub speichern
- stattdessen serverlokale Env-Datei plus Runner mit minimalen Berechtigungen

### 7.5 Offene Fragen

- self-hosted Runner oder SSH-Deploy?
- Rollback per Git checkout plus `docker compose up -d --build` oder per Image-/Release-Verzeichnis?
- Deployment vom Commit-SHA oder künftig vom Tag?
- separate Staging-Umgebung oder direkt kontrollierter Prod-Deploy?

## 8. Data Integration Plan

### 8.1 Data-Integration-Tabelle

| Datenbereich | Quelle | Ziel | Tool/Script | Risiko | Nächster Schritt |
| --- | --- | --- | --- | --- | --- |
| Auth/Core-Schema | Repo-Migrationen unter `app/migrations/` | produktive Postgres-DB | `app/scripts/apply_auth_migration.py` | Hoch, wenn Ablauf unklar bleibt | Produktions-Migrationsschritt definieren |
| Initial Admin | serverseitige Eingaben / Env | produktive Postgres-DB | `app/scripts/create_initial_admin.py` | Mittel | Erst-Admin-Prozedur und Verantwortlichkeit festlegen |
| Research-Person/Session-Metadaten | lokales Workbook + Batch | DB + `data/sessions/{language}/{session_id}` | `scripts/research_data_intake/import_batch_to_production.py` | Hoch bei falscher Reihenfolge | Minimalen v0.7-Freigabedatensatz definieren |
| Runtime-Sessions | validierte lokale Runtime-Artefakte | Server-Datenvolume | `build_prod_upload_package.py` plus später Server-Integrationsschritt | Hoch | Server-Upload-/Integrationsablauf dokumentieren |
| Upload-Paket | validierte Runtime-Artefakte + optional `db/import_payload.json` | serverseitiges Incoming/Release-Verzeichnis | `scripts/research_data_intake/build_prod_upload_package.py` | Mittel | Paketformat und serverseitigen Merge definieren |
| Research-Player-Konfig | versionierte JSON-Dateien unter `data/config/research_player/` | Repo/Container und optional Upload-Paket | Repo plus optional `--include-research-player-config` | Niedrig bis mittel | Für v0.7 festlegen, welche Sprachkonfigurationen live gehen |
| Teaching-Content | versioniert unter `content/teaching/` | im Image unter `/app/content/teaching` | Docker-Build | Niedrig | Im Release-Scope festlegen, welche Teaching-Flächen live sein sollen |
| Teaching-Medien | aktuell topic-lokal unter `content/teaching/.../media` | derzeit direkt aus dem Image/Content-Pfad erreichbar | kein separater Export im aktuellen Repo-Befund | Mittel | Vor Deploy dokumentieren, ob dies bewusst so bleibt |
| Public Assets | kein `public/`-Verzeichnis im Workspace | serverseitiges `/srv/webapps/promat/public` laut Compose | aktuell unklar | Mittel | Zweck und Minimalinhalt des Public-Volumes klären |
| Local Archive | außerhalb des Repos unter `PROMAT_LOCAL_ARCHIVE_ROOT` | lokal, nicht Server | `import_batch_to_production.py` | Niedrig | Vor Prod-Import Archivpfad und Verantwortlichkeit bestätigen |
| Dry-run / Idempotenz | lokal möglich | vor Serverintegration | `--dry-run`, Validatoren, importerinterne Rollback-Mechanik | Positiv, aber nur lokal dokumentiert | Serverseitigen Dry-run-/Preview-Schritt konzipieren |

### 8.2 Minimaler v0.7-Datensatz

Technisch minimal erforderlich:

1. produktive DB mit aktuellem Schema
2. mindestens ein Admin-Account
3. versionierte `data/config/research_player/...`-Konfiguration für die freigegebenen Korpora
4. Teaching-Content aus dem Repo, sofern Teaching Teil von v0.7 ist

Optional, aber für eine inhaltlich aussagekräftige v0.7-Freigabe wahrscheinlich nötig:

1. mindestens ein bewusst ausgewähltes Research-Session-Paket pro freigegebenem Korpus
2. definierte Import-Payloads für Metadaten
3. Post-Import-Smoke auf echten Research-Routen

Wichtige Beobachtung:

- Die App kann technisch ohne breite Runtime-Sessions starten.
- Für einen inhaltlich sinnvollen v0.7-Release muss aber entschieden werden, ob die erste Freigabe nur die Plattform oder auch konkrete Forschungsdaten umfasst.

### 8.3 Reihenfolge für späteren Integrationslauf

1. Server-Backups verifizieren.
2. DB-Migrationen ausführen.
3. Initialen Admin sicherstellen.
4. Research-Player-Konfig prüfen.
5. Minimales Upload-Paket serverseitig einspielen.
6. Health-/Smoke-Routen prüfen.
7. Erst danach weiteren Datenumfang freigeben.

## 9. Sicherheits-/Betriebscheck

| Thema | Status | Blocker? | Nächster Schritt |
| --- | --- | ---: | --- |
| HTTPS / TLS | Unbekannt im Live-Betrieb; nur Planungsannahmen vorhanden. | Ja | Live-Domain und Zertifikatsverwaltung verifizieren. |
| HSTS | Unbekannt ohne Live-nginx-Kontext. | Ja | Reverse-Proxy-Konfiguration lesen. |
| Security Headers / CSP | App-seitig durch frühere Hardening-Runs grundsätzlich adressiert; im Audit nicht live gegen Zielserver geprüft. | Nein, aber zu verifizieren | Im Post-Deploy-Smoke Header prüfen. |
| Secrets | Repo-seitig nur Templates; echte produktive Werte fehlen naturgemäß. | Ja | Serverseitige Secret-Datei anlegen und absichern. |
| SMTP | Verdrahtung im Repo vorhanden, produktive Providerdaten und Zustellprozess fehlen. | Ja | SMTP-Provider und Testverfahren festlegen. |
| Redis / Rate Limiter | Repo-seitig vorhanden. | Ja | Redis-Service und Persistence im Zielbetrieb verifizieren. |
| Logs ohne Secrets/PII | Access-Request-Metadaten-Regeln sind spezifiziert; Live-Logpfade und Retention fehlen. | Mittel | Logrotation und Einsichtspfad dokumentieren. |
| Access-Request-Mail | Implementiert, aber operativ noch ohne Provider- und Zustellkontext. | Ja | SMTP- und Empfänger-Konfiguration festlegen. |
| Backups | Keine verifizierte Server-Backup-Doku im Repo. | Ja | Backup-/Restore-Prozess vor erstem öffentlichen Deploy klären. |
| DB-Restore-Test | Nicht dokumentiert. | Ja | Restore-Probe definieren. |
| Monitoring | Nur planungsseitig angedeutet. | Ja | Live-Monitoring-Einbindung dokumentieren. |
| Healthcheck | `/health` vorhanden, `/ready` fehlt. | Nein für ersten Basistest, aber operativer Mangel | Readiness-Strategie vor Release festlegen. |
| Disk Space | Ohne Serverzugriff unbekannt. | Ja | Server-Check vor Deploy. |
| Logrotation | Unbekannt. | Ja | Ops-Doku ergänzen. |
| Error Handling | Im Audit nicht als aktueller Blocker aufgefallen. | Nein | Im Deploy-Smoke Fehlerpfade beobachten. |
| Admin-Accounts | Bootstrap-Script vorhanden, aber kein Produktionsablauf. | Mittel | Initial-Admin-Runbook erstellen. |
| Security Contact | `SECURITY.md` verweist korrekt auf privaten Kanal; öffentliches Vulnerability Intake ist bewusst noch nicht aktiviert. | Nein | Vor öffentlicher Freigabe privaten Meldekanal organisatorisch bestätigen. |
| CODEOWNERS / Required Reviews | `CODEOWNERS` ist kommentar-only. | Nein, solange Required Reviews nicht aktiviert werden | Erst bei echten Teams/Handles scharf schalten. |
| Dependabot / Dependency-Prozess | `dependabot.yml` vorhanden. | Nein | Beibehalten. |
| Server Updates | Im Repo nicht dokumentiert. | Mittel | Ops-Konventionen erheben. |

## 10. Folgeprompts

### 1. Production Deployment Runbook

```text
Erstelle ein verbindliches Production Deployment Runbook für PROMAT auf Basis der bereits vorhandenen Repo-Realität, aber nur dort, wo Fakten verifiziert sind.

Nutze als aktive Quellen:
- docs/spec/platform-data-files.md
- docs/spec/research-access.md
- docs/spec/research-capabilities.md
- docs/spec/intake-workbook.md
- app/infra/docker-compose.prod.yml
- app/Dockerfile
- app/src/app/runtime_paths.py
- app/src/app/config/__init__.py
- app/scripts/apply_auth_migration.py
- app/scripts/create_initial_admin.py

Arbeite ausdrücklich mit folgenden Audit-Befunden:
- Compose validiert, aber Port-/Runner-/nginx-Kontext ist noch nicht live verifiziert.
- `/health` existiert, `/ready` noch nicht.
- produktive Pfade unter /srv/webapps/promat sind nur teilweise dokumentiert.
- Secrets müssen serverseitig bleiben.

Liefere:
- Voraussetzungen
- exakten Ablauf vor Deploy / während Deploy / nach Deploy
- Migrations- und Initial-Admin-Schritt
- Health-/Smoke-Schritte
- Rollback-Minimum
- offene Stellen, die erst nach Live-Server-Read-only-Inspektion finalisiert werden dürfen

Keine Implementierung. Keine Dateiänderungen außerhalb des Runbooks.
```

### 2. GitHub Actions CI Deploy Pipeline

```text
Entwirf eine GitHub-Actions-Struktur fuer PROMAT mit drei Workflows:
1. PR CI
2. Main Deploy Gate
3. Manual Release v0.7

Ausgangslage:
- aktuell existiert nur .github/workflows/ci.yml
- produktive Secrets sollen moeglichst serverseitig bleiben
- Runner-Modell ist noch offen: self-hosted vs SSH
- Docker Compose Production File ist app/infra/docker-compose.prod.yml

Beruecksichtige:
- compileall
- Governance-Checks
- fokussierte Pytests
- optional Docker-Build
- Compose config validation mit Platzhaltern
- Post-Deploy-Health/Smoke
- Rollback-Hook

Liefere:
- konkrete Workflow-Aufteilung
- Trigger-Regeln
- benoetigte GitHub-Secrets je Runner-Modell
- was nur serverseitig liegen darf
- Empfehlung fuer den ersten v0.7-Release

Keine Workflow-Dateien aendern.
```

### 3. Server Bootstrap / nginx Integration

```text
Erstelle einen read-only Server-Bootstrap- und nginx-Integrationsplan fuer PROMAT.

Wichtig:
- nichts erfinden, was im Live-Server noch nicht bestaetigt ist
- vorhandene Planungsdoku unter docs/plans/prep_prod/prep_server.md nur als Input verwenden
- alle offenen Punkte fuer Live-Read-only-Checks explizit markieren

Zu klaeren:
- Zielpfade unter /srv/webapps/promat
- Volume-Layout
- Portbelegung
- nginx-Upstream und Site-Struktur
- TLS-/Certbot-Konvention
- Deploy-User / Rechte / Gruppen
- self-hosted runner vs SSH
- Monitoring- und Logrotation-Einbindung

Liefere:
- verifizierbare Checkliste fuer einen spaeteren Live-Read-only-Serveraudit
- Vorschlag fuer PROMAT-Integration ohne Konflikte mit anderen Apps
- Liste aller Entscheidungen, die vor dem ersten echten Deploy noch getroffen werden muessen

Keine Serveränderungen.
```

### 4. Data Integration Plan

```text
Erarbeite einen konkreten Data-Integration-Plan fuer den ersten kontrollierten PROMAT-Deploy.

Nutze:
- docs/spec/platform-data-files.md
- docs/spec/intake-workbook.md
- docs/runbooks/research-intake-working-pipeline.md
- scripts/research_data_intake/README.md
- scripts/research_data_intake/import_batch_to_production.py
- scripts/research_data_intake/build_prod_upload_package.py
- app/scripts/apply_auth_migration.py

Behandle:
- minimales v0.7-Dataset
- Research-Player-Konfig
- DB-Metadatenimport
- Runtime-Sessions
- Teaching-Content und Topic-Medien
- Dry-run, Idempotenz, Validierung
- Reihenfolge vor/nach DB-Migration
- Post-Import-Smoke
- Backups vor Import

Keine Daten importieren. Keine Files ändern.
```

### 5. v0.7 Release Notes and Tagging

```text
Erstelle einen Vorschlag fuer den v0.7-Release-Prozess von PROMAT.

Ausgangslage:
- keine Tags vorhanden
- kein CHANGELOG.md vorhanden
- pyproject-Version ist 1.0.0, aber der naechste Produktrelease soll v0.7 heissen
- erster systematischer Server-Deploy steht noch aus

Liefere:
- empfohlene Versionierungsstrategie
- wie v0.7 dokumentiert werden soll
- empfohlene Release-Notes-Struktur
- welche abgeschlossenen Bloecke in v0.7 gehoeren
- welche bekannten Einschraenkungen und operativen Voraussetzungen in die Notes muessen
- ob der Tag fuer diesen ersten Deploy vor oder nach erfolgreichem Deploy gesetzt werden soll und warum

Keine Tags erzeugen. Keine Release-Dateien aendern.
```

### 6. Optional: Repo Hygiene Cleanup

```text
Fuehre einen gezielten Repo-Hygiene-Cleanup-Plan fuer PROMAT aus, aber zunaechst noch ohne Dateien zu aendern.

Pruefe und klassifiziere:
- getrackte Root-Debug-/QA-Dateien wie start.txt, qa_check.py, simple_qa.py, _es_diag.txt
- app/capture_qa.py
- untracked QA-Helfer in scripts/qa/
- .gitignore-Luecken fuer Root-Artefakte
- was nach scripts/qa/ gehoert, was nach tmp/ui-qa/, was geloescht werden sollte

Liefere:
- konkrete Move/Delete/Keep-Empfehlungen
- vorgeschlagene Commit-Reihenfolge
- Risiken fuer bestehende QA-Workflows

Noch keine Dateien aendern.
```

## 11. Tests/Checks

### 11.1 Ausgeführte read-only Kommandos / Checks

- `git status --short --branch`
- `git tag --sort=-creatordate | Select-Object -First 20`
- Lesen von `.gitignore`, README, `.github/*`, `docs/spec/*`, `docs/runbooks/*`, `docs/plans/prep_prod/*`
- `python -m compileall src/app`
- `python ../scripts/ci_governance_checks.py`
- `python -m pytest tests/test_runtime_config.py tests/test_auth_phase1.py tests/test_research_sessions.py tests/test_research_phenomena.py tests/test_teaching_content.py -q`
- `python -m pytest tests -q -k "security_headers or csp or access_request or runtime_config or governance"`
- `docker compose -f app/infra/docker-compose.prod.yml config` mit sicheren Platzhaltern
- mehrere gezielte `git ls-files`, `git show HEAD:...`, Verzeichnislisten und Textsuchen

### 11.2 Ergebnisse

- fokussierte Pytests: grün
- Sicherheits-/Governance-Fokus-Pytest-Subset: grün
- Compile-Check: grün
- Compose-Konfigurationscheck: grün
- Governance-Script: nicht grün
- Git-Status: dirty

### 11.3 Nicht ausgeführte Kommandos mit Grund

- keine Live-Server-Kommandos wie `hostname`, `nginx -T`, `docker ps`, `ss -tulpn`, `systemctl ...`, weil kein Serverzugriff im Workspace vorlag
- kein `docker build`, weil der Audit-Kontext read-only auf Readiness und nicht auf vollständige lokale Build-/Deploy-Simulation begrenzt war
- keine Migrationen, Seeds, Datenimporte, SMTP-Tests, Deploys oder nginx-Reloads wegen ausdrücklichem No-Go

## 12. No-Go

Bestätigung für diesen Run:

- keine Dateien geändert außer diesem Auditbericht
- keine Serveränderungen
- keine Secrets ausgegeben
- kein Deployment
- keine Migrationen
- kein Datenimport
- keine echten Mails
- kein Tag oder Release erstellt