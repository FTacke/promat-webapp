# Importer Smoke Required CI Fix

## 1. Scope

Geprüft und geändert wurde nur der Required-CI-Smoke für den Research-Production-Importer in `.github/workflows/ci.yml`.

Nicht geändert wurden Importer-Fachlogik, Runtime-Daten, Archivdaten, Datenimporte, Seeds, Migrationen, Deployment-Konfigurationen, `content/`, `content/teaching/` oder `public/teaching/`.

## 2. Ausgangslage

Lokal war die Importer-Suite grün:

```text
pytest app/tests/test_research_production_importer.py -q
24 passed
```

Der Required-CI-Workflow hatte den Importer-Smoke nach wiederholten `python-smokes`-Fehlschlägen aus dem Required Gate entfernt. Full/Nightly deckt den Importer weiterhin über `python -m pytest tests -q` im `app`-Working-Directory ab.

## 3. GitHub-Actions-Befund

Die öffentlichen GitHub-Run-Summary-Seiten waren ohne Sign-in einsehbar; die vollständigen Job-Logs waren nicht abrufbar. `gh` ist in dieser Umgebung nicht installiert, und der unauthentifizierte REST-Aufruf auf die Actions-API wurde mit `403` abgewiesen. Deshalb konnte die vollständige alte Pytest-Ausgabe aus GitHub Actions nicht direkt heruntergeladen werden.

Einsehbare Run-Summaries:

| Run-ID | Commit | Job | Step/Annotation | Ergebnis |
|---:|---|---|---|---|
| `26458948261` | `1cbee41` | `python-smokes` | Importer-Smoke im CI-Run, Log nur mit Sign-in | Failure, Exitcode `4` |
| `26459016783` | `edd7f42` | `python-smokes` | Importer-Smoke im CI-Run, Log nur mit Sign-in | Failure, Exitcode `4` |
| `26459148917` | `49dd0a3` | `python-smokes` | Importer-Smoke im CI-Run, Log nur mit Sign-in | Failure, Exitcode `2` |
| `26459370298` | `cbfa951` | `python-smokes` | Importer-Smoke im CI-Run, Log nur mit Sign-in | Failure, Exitcode `2` |
| `26459460029` | `8a97f6b` | `python-smokes` | Importer-Smoke entfernt | Success |
| `26460490934` | `b9cc303` | `python-smokes` | Node-ID-basierter Importer-Smoke wiederhergestellt | Failure, Exitcode `4` |

Git-History-Befund der alten Importer-Smoke-Varianten:

```text
164dab3 / bbabab6:
python -m pytest \
  tests/test_research_production_importer.py::test_load_intake_workbook_derives_session_id_and_ignores_out_of_scope_rows \
  tests/test_research_production_importer.py::test_run_text_pipeline_skips_missing_working_text_inputs_in_write_mode \
  tests/test_research_production_importer.py::test_run_text_pipeline_dry_run_does_not_require_written_manifest \
  -q

1cbee41 / edd7f42:
python -m pytest tests/test_research_production_importer.py::test_load_intake_workbook_derives_session_id_and_ignores_out_of_scope_rows tests/test_research_production_importer.py::test_run_text_pipeline_skips_missing_working_text_inputs_in_write_mode tests/test_research_production_importer.py::test_run_text_pipeline_dry_run_does_not_require_written_manifest -q

49dd0a3:
python -m pytest tests/test_research_production_importer.py -q

cbfa951:
python -m pytest app/tests/test_research_production_importer.py -q
```

## 4. Reproduktion der Exitcode-4-Klasse

Die lokale Reproduktion zeigt die typische Pytest-Usage-Fehlerklasse, die zu Exitcode `4` führt: ein Repo-Root-Pfad wird aus dem `app`-Working-Directory heraus ausgeführt.

```text
cd app
python -m pytest app/tests/test_research_production_importer.py -q

ERROR: file or directory not found: app/tests/test_research_production_importer.py
LASTEXITCODE=4
```

Der erste Wiederherstellungsversuch mit zwei expliziten Node-IDs lief lokal grün, scheiterte in GitHub Actions aber erneut im Step `Importer smoke tests` mit Exitcode `4`. Da die vollständigen Logs ohne Sign-in nicht abrufbar waren, wurde auf die robusteste akzeptierte Variante umgestellt: die komplette kleine Importer-Testdatei.

Der finale CI-Step vermeidet die zuvor beobachteten Fragilitätsquellen:

- `working-directory: app` ist explizit gesetzt.
- Testpfade sind relativ zu `app`.
- Es gibt keine Node-IDs.
- Es gibt keine `-k`-Expression.
- Die Datei ist klein genug für Required CI und lief lokal stabil mit `24 passed`.

## 5. CI-Änderung

Neu in `.github/workflows/ci.yml`:

```yaml
- name: Importer smoke tests
  working-directory: app
  run: |
    python -m pytest tests/test_research_production_importer.py -q
```

Warum die komplette Datei:

- Der Node-ID-basierte Required-Smoke blieb in Actions fragil, obwohl er lokal grün war.
- Die komplette Datei umfasst aktuell 24 kleine Unit-/Integrationstests ohne echte Datenimporte.
- Sie deckt die beiden zuletzt relevanten Importer-Verträge weiterhin ab:
  - `test_run_text_pipeline_dry_run_does_not_require_written_manifest`
  - `test_run_text_pipeline_skips_missing_working_text_inputs_in_write_mode`
- Die Laufzeit ist lokal weiterhin niedrig genug für Required CI.

Die breite Importer-Abdeckung bleibt im `Full Test`- und `Release Candidate Check`-Workflow über `python -m pytest tests -q` erhalten.

## 6. Lokale Validierung

```text
cd app
python -m pytest tests/test_research_production_importer.py -q
24 passed
```

```text
python -m pytest app/tests/test_research_production_importer.py -q
24 passed
```

```text
python -m ruff check .
All checks passed.
```

```text
python -m compileall app
passed
```

```text
python scripts/ci_governance_checks.py
All governance checks passed.
```

```text
pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q
66 passed
```

```text
pytest app/tests -q -k "security_headers or csp or access_request or runtime_config or governance"
16 passed, 458 deselected
```

```text
node --test app/tests/js/*.test.mjs
7 passed
```

```text
docker compose -f app/infra/docker-compose.prod.yml config
passed with placeholder CI environment values
```

Workflow-YAML parsing:

```text
ok .github/workflows/ci.yml
ok .github/workflows/full-test.yml
ok .github/workflows/release-candidate-check.yml
```

## 7. GitHub-Actions-Status

Status nach erstem Push:

- Commit `b9cc303` / Run `26460490934` / `CI #94` scheiterte erneut im Step `Importer smoke tests` mit Exitcode `4`.
- Vollständige Logs waren ohne Sign-in nicht abrufbar; die öffentliche Summary benennt aber den Step eindeutig.
- Der Workflow wurde danach auf den robusteren Full-File-Smoke umgestellt und wird erneut gepusht.

## 8. Bestätigungen

- Keine Datenimporte ausgeführt.
- Keine Runtime-/Archivdaten verändert.
- Keine Migrationen oder Seeds ausgeführt.
- Keine Tests geskippt.
- Keine Produktcode- oder Importer-Fachlogik geändert.
- Keine Deployment-/Serveränderungen.
- Keine Änderungen an `content/`, `content/teaching/` oder `public/teaching/`.
