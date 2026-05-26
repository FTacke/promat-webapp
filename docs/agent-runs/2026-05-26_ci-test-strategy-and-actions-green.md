# CI Test Strategy + GitHub Actions Green

## 1. Scope

In diesem Run wurden geändert:

- `.github/workflows/ci.yml` auf stabile essenzielle Smoke-Gates für `push`/`pull_request` auf `main`
- neuer Workflow `.github/workflows/full-test.yml` für breite Full-Suite als `workflow_dispatch`, Nightly (`schedule`) und selektive Push-Pfade
- neuer Workflow `.github/workflows/release-candidate-check.yml` für manuellen RC-Check inkl. optionalem `responsive_smoke.py` ohne Deployment
- minimaler Fix der bekannten fragilen CI-Testverträge in `app/tests/test_research_sessions.py` blieb erhalten:
  - line-ending-robuster Teaching-Media-Vergleich
  - Prewarm-Test mit explizit aufgebauter Runtime-Session im Testsetup

Ausdrücklich nicht geändert:

- keine Produktlogik
- keine Deployment- oder Serverkonfiguration
- keine echten Datenimporte
- keine Migrationen gegen echte Daten
- keine echten Mails
- keine Release-Tags

## 2. Alte CI-Struktur

Vorher lief im einzigen CI-Workflow (`.github/workflows/ci.yml`) ein breiter Block:

- Ruff, Compile, Governance
- danach in einem einzigen Step mehrere große Pytest-Läufe inklusive kompletter `tests/test_research_sessions.py`

Warum fragil/zu breit:

- Detail- und Integrationsnahes wurde als harter Push-Gate geführt
- plattformabhängige Unterschiede (CRLF/LF, Runtime-Root-Fixture-Abhängigkeit) konnten den Hauptgate blockieren
- keine saubere Trennung zwischen essenziellen Kernverträgen und tieferen Full-Suiten

## 3. Neue CI-Struktur

### PR/Main CI (`.github/workflows/ci.yml`)

Trigger:

- `push` auf `main`
- `pull_request` auf `main`
- `workflow_dispatch`

Jobs:

- `quality-and-config`:
  - `python -m ruff check .`
  - `python -m compileall app`
  - `python scripts/ci_governance_checks.py`
  - `docker compose -f app/infra/docker-compose.prod.yml config` (mit Platzhalter-Secrets)
- `python-smokes`:
  - Runtime-/Config-Smoke
  - Auth-/Access-/Rate-limit-/Security-Header-Smokes
  - Research-Access-/Player-Prewarm-/Teaching-Media-Smokes
  - Importer-Dry-run-/No-side-effects-Smokes
- `js-smokes`:
  - `node --test app/tests/js/*.test.mjs`

### Full/Nightly (`.github/workflows/full-test.yml`)

Trigger:

- `workflow_dispatch`
- `schedule` (nightly)
- selektiver `push` auf `main` bei Änderungen an Full-relevanten Pfaden (`scripts/research_data_intake/**`, zentrale Testdateien, `content/**`, `data/**`, CI-Workflow-Dateien)

Inhalt:

- Ruff, Compile, Governance
- volle `pytest tests -q`
- JS-Tests
- Compose-Config-Check

### Release Candidate Check (`.github/workflows/release-candidate-check.yml`)

Trigger:

- `workflow_dispatch` mit Inputs

Inhalt:

- Ruff, Compile, Governance
- volle `pytest tests -q`
- JS-Tests
- Compose-Config-Check
- Docker Build
- optional `responsive_smoke.py` nur bei gesetztem Input und vorhandenen QA-Secrets
- kein Deployment

## 4. Bekannte Fehler

### Teaching-Media-Line-Ending

- Ursache: Plattformabhängiger CRLF/LF-Bytevergleich
- Fix: Test vergleicht line-ending-normalisiert (`\r\n` -> `\n`)
- Validierung:
  - Einzeltest lokal grün
  - Einzeltest unter CI-ähnlicher Runtime-Env grün

### Research-Player-Prewarm

- Ursache: implizite Abhängigkeit von vorhandener Runtime-Session im Test; CI nutzt leeren `PROMAT_RUNTIME_ROOT=/tmp/promat`
- Fix: Test erzeugt eine stabile minimale Session plus Artefakte explizit im `runtime_env`
- Validierung:
  - Einzeltest lokal grün
  - Einzeltest unter CI-ähnlicher Runtime-Env grün
  - volle `test_research_sessions.py` im CI-ähnlichen Kontext grün

## 5. Lokale Validierung

Ausgeführt:

- `python -m ruff check .` -> grün
- `python -m compileall app` -> grün
- `python scripts/ci_governance_checks.py` -> grün
- `pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q` -> grün
- `pytest app/tests -q -k "security_headers or csp or access_request or runtime_config or governance"` -> grün
- `pytest app/tests -q -k "research_smoke or player_smoke or teaching_smoke or importer_smoke"` -> 0 selected (keine Marker vorhanden, dokumentiert)
- ersatzweise die konkret in `ci.yml` ausgewählten Smoke-Tests direkt ausgeführt -> grün
- `pytest app/tests/test_research_sessions.py::test_teaching_topic_media_route_serves_released_media -q` -> grün
- `pytest app/tests/test_research_sessions.py::test_research_player_prewarm_request_warms_route_without_rendering_body -q` -> grün
- `node --test app/tests/js/*.test.mjs` -> grün
- `docker compose -f app/infra/docker-compose.prod.yml config` mit Platzhalter-Secrets -> grün

## 6. GitHub Actions Iterationen

| Commit | Workflow | Ergebnis | Fehler | Fix |
|---|---|---|---|---|
| `164dab3` | `CI` (`26458617026`) | in Auswertung | - | neue CI-Strategie gepusht |
| `164dab3` | `Full Test` (`26458616946`) | in Auswertung | - | neuer Full/Nightly-Workflow gepusht |
| `164dab3` | `.github/workflows/release-candidate-check.yml` (`26458614416`) | failure | Workflow ungültig: `secrets` in `if`-Expression nicht erlaubt | `if` nur über Inputs; Secret-Prüfung in Script-Guard verschoben |
| `bbabab6` | `CI` (`26458706962`) | in Auswertung | - | YAML-Fix für RC-Workflow gepusht |

## 7. Finaler Actions-Status

- PR/Main CI grün: in Auswertung
- Full/Nightly optional: in Auswertung
- Release Candidate Check optional: Workflow-Datei validiert (manueller Run noch nicht gestartet)
- Externe Blocker: keine bestätigt

## 8. Nicht umgesetzt

- kein Deployment
- keine Serveränderungen
- keine Datenimporte
- keine Migrationen
- keine echten Mails
- keine Release-Tags
- keine Force-Pushes
- keine unrelated Refactors

## 9. Nächste Schritte

1. CI-Run `26458706962` final prüfen und Status im Bericht abschließen.
2. Optional einen manuellen `Full Test`-Run und/oder `Release Candidate Check`-Run per `workflow_dispatch` triggern.
3. Danach kann als separater Track der Server Live Read-only Audit und das Production Deployment Runbook folgen.
