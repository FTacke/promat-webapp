# Runbook: Tests und CI-Release-Gate

## Zugehörige Spezifikation

- `docs/spec/platform-data-files.md` (Abschnitt „Release Gate and Deployment“ und `data/config/`)

## Zweck

Der kanonische lokale Testlauf, die Bedeutung der CI-Jobs und der Umgang mit operatoreigener Research-Konfiguration in Tests. Der lokale Lauf entspricht dem CI-Lauf; was lokal grün ist, ist die Basis für das automatische Produktions-Deployment von `main`.

## Voraussetzungen

- Python 3.12, Node.js (für die JS-Tests), Docker (nur für Image-Build und Backup-Rehearsal), `shellcheck` (optional lokal; CI führt es aus)
- keine Operator-Daten: `data/config/`, `data/sessions/`, `public/` und `secure/` dürfen leer sein

## Schritte: kanonischer lokaler Testlauf

1. Umgebung anlegen (einmalig):

   ```bash
   python3.12 -m venv .venv
   .venv/bin/pip install -r app/requirements.txt -r app/requirements-dev.txt
   ```

2. Laufzeitumgebung wie in CI setzen (Bash; unter PowerShell entsprechend mit `$env:`):

   ```bash
   export APP_ENV=testing FLASK_ENV=testing FLASK_SECRET_KEY=test-secret JWT_SECRET_KEY=test-secret
   export PROMAT_RUNTIME_ROOT=/tmp/promat PROMAT_PUBLIC_ROOT=/tmp/promat/public
   export AUTH_DATABASE_URL=sqlite:////tmp/promat/test.sqlite3 POSTGRES_PASSWORD=x
   export RATE_LIMIT_STORAGE_URI=redis://rate_limit:6379/0
   export AUTH_ACCESS_REQUEST_EMAIL=ci@example.test AUTH_ACCESS_REQUEST_FROM_EMAIL=no@example.test AUTH_ACCESS_REQUEST_SMTP_HOST=smtp.example.test
   mkdir -p /tmp/promat/data/config /tmp/promat/data/sessions /tmp/promat/public /tmp/promat/logs
   ```

3. Qualitäts-Checks im Repo-Root: `python -m ruff check .`, `python -m compileall -q app scripts`, `python scripts/ci_governance_checks.py`, `python scripts/validate_teaching_content.py`, `shellcheck --severity=warning scripts/*.sh`
4. Vollständige Python-Suite im Ordner `app/`: `python -m pytest tests -q`
5. JavaScript-Tests im Repo-Root: `node --test app/tests/js/*.test.mjs`
6. Optional Image und Backup-Rehearsal: `docker build -f app/Dockerfile -t promat-ci-image .` sowie `PYTHON=python scripts/ci_backup_restore_smoke.sh`. Der Image-Smoke läuft im gebauten Image: `docker run --rm -i -e PROMAT_RUNTIME_ROOT=/app -e PROMAT_PUBLIC_ROOT=/tmp/public promat-ci-image python - < scripts/ci_image_smoke.py` (Rechtsseiten, öffentliche Seiten, keine öffentlichen Entwürfe, Login-Redirect geschützter Seiten über die echte `create_app`-Komposition).
7. Optional PostgreSQL-Tests (Marker `postgres`, echte Migrationen gegen eine Wegwerf-Datenbank): einen Wegwerf-Server starten, zum Beispiel `docker run -d --name promat-test-pg -e POSTGRES_PASSWORD=pw -p 127.0.0.1:55432:5432 postgres:15`, dann `PROMAT_TEST_POSTGRES_URL=postgresql+psycopg2://postgres:pw@127.0.0.1:55432/postgres python -m pytest tests/test_postgres_integration.py -q` im Ordner `app/`. Ohne die Variable werden diese Tests übersprungen; in CI ist sie gesetzt (Service-Container im `python`-Job). Nicht gegen die lokale Dev-Datenbank (`promat_auth_db`) richten.

Die Suite ist die gesamte `pytest`-Konfiguration aus `app/pyproject.toml`. Es gibt keine Teilmenge als „kanonisch“; `-k`, `::` oder `--deselect` im CI-Schritt sind durch `app/tests/test_ci_workflows.py` verboten.

## Research-Konfiguration in Tests

- Die echten Task-Kataloge und Player-Configs unter `data/config/research_player/` sind operatoreigene Laufzeitkonfiguration und nicht im Repo.
- Tests, die nur irgendwelche Katalogeinträge brauchen, verwenden die minimalen, synthetischen Fixtures unter `app/tests/fixtures/runtime/` über die Fixture `fixture_runtime_root` (`app/tests/conftest.py`). Sie sind kein Forschungsinhalt.
- Tests, die den Inhalt der echten Kataloge prüfen (zum Beispiel Item-Anzahl oder `wl_014 = théâtre`), tragen den Marker `data` und laufen nicht im Standardlauf. Der Operator führt sie gegen die echte Konfiguration aus: `PROMAT_RUNTIME_ROOT=<repo-root> python -m pytest -m data`.
- Eine Runtime-Konfiguration (lokal, Paket, Server) lässt sich mit den App-Loadern prüfen: `python scripts/research_data_intake/validate_research_config.py --runtime-root <root> [--language german] [--require-complete]`.

## CI-Jobs (`.github/workflows/ci.yml`)

| Job | Prüft |
|---|---|
| `python` | ruff, compileall, Governance, Teaching-Validierung, shellcheck, gesamte pytest-Suite (mit PostgreSQL-Service-Container für die `postgres`-Tests) |
| `javascript` | `node --test` |
| `docker` | Compose-Config, Image-Build, Laufzeit-Assets und HTTP-Smoke im gebauten Image (`scripts/ci_image_smoke.py`: Rechtsseiten, öffentliche Seiten, Entwürfe nicht öffentlich, Login-Redirect) |
| `browser-smoke` | Chromium (Playwright) gegen die echte App-Factory mit synthetischer Fixture-Runtime (`scripts/qa/fixture_runtime.py`) und gestubbtem Audio: Seiten ohne Page-/Console-Fehler, Login-Rücksprung, „Alle Items“ im Player, stabile Set-Auswahl im Vergleich (auch bei gespeichertem Set: kein `private-copy`, keine Schreibzugriffe), Stop-Steuerung und kein paralleles Audio, Light/Dark, kein horizontaler Überlauf bei 390 px |
| `backup-restore` | echte Migrationen, Backup, verifizierter Restore in Wegwerf-Postgres |
| `release-gate` | Sammelstatus; hängt von allen anderen Jobs ab |

Ein neuer Job muss in `release-gate.needs` aufgenommen werden (wird getestet).

### Browser-Smoke lokal

```text
pip install playwright==1.59.0 && python -m playwright install chromium
python scripts/qa/ci_browser_smoke.py --out tmp/ui-qa/<YYYY-MM-DD>-ci-smoke
```

Das Skript baut die Fixture-Runtime in ein Temp-Verzeichnis, startet die App in-process auf einem freien Port, legt ein einzelnes QA-Konto an und räumt danach auf (`--keep-runtime` behält das Verzeichnis). Keine echten Daten, kein Netzwerk. Exit 1 bei jeder fehlgeschlagenen Prüfung; Screenshots liegen unter `--out` (in CI als Artefakt `browser-smoke-screenshots`). Nachgewiesen rot werden die Mutationen: Stop-Logik oder Stop-Icon der Vergleichsmatrix entfernt, „Alle Items“ nie als aktuelle Set-Option markiert, Syntaxfehler in `research-player.js` (`static_scripts.test.mjs` fängt Letzteres zusätzlich im JS-Test), `set_id` immer in der URL (`research_ui_state_helpers.test.mjs`); die Routenmatrix (`test_route_security_matrix.py`) wird rot, wenn `@jwt_required()` von einer Set-Route entfernt wird.

Windows/Git-Bash: `PYTHONIOENCODING=utf-8` setzen, wenn eigene Debug-Skripte Konsolenmeldungen ausgeben, und `MSYS_NO_PATHCONV=1` bei Pfad-Argumenten, die mit `/` beginnen.

## Verifikation

- Alle Schritte oben grün; `pytest` meldet höchstens `deselected` für `data`-Tests.
- In CI ist `release-gate` grün, bevor das Deployment startet.

## Risiken und Rückbau

- Ein roter Job stoppt das Deployment des betroffenen Commits (siehe `deploy-and-rollback.md`).
- Fixtures nie mit echten Katalogen überschreiben: die Tests erwarten die minimalen Fixture-Items.
