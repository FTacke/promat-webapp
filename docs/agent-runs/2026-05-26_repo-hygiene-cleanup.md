# Repo Hygiene Cleanup

## 1. Scope

Umgesetzt wurden nur die sicheren Hygiene- und Governance-Punkte aus dem vorherigen Audit:

- Root- und App-Scratch-Artefakte klassifizieren und bereinigen
- `.gitignore` für bekannte lokale QA-/Debug-Dateien schärfen
- `scripts/ci_governance_checks.py` an den aktuellen Shell-Zustand anpassen
- die lokale sichtbare i18n-Verzweigung in `app/src/app/research_views.py` minimal entfernen
- `scripts/qa/responsive_smoke.py` als bewusstes manuelles QA-Tool bereinigen

Ausdrücklich nicht Teil dieses Runs:

- keine Deployment-, Server-, nginx-, Runner- oder CI-Architekturänderungen
- keine Änderungen an `content/`, `content/teaching/`, Runtime-Daten oder Importbeständen
- keine Reparatur der separaten laufenden UI-/Shell-Arbeit im Working Tree
- keine Behebung fachfremder Testfehler außerhalb des Hygiene-Scope

## 2. Kurzfazit

- Der Repo-Hygiene-Gate ist wieder grün.
- Die getrackten Root-/App-Scratch-Dateien aus dem Audit sind entfernt oder jetzt sauber ignoriert.
- `scripts/qa/responsive_smoke.py` ist als kanonisches manuelles QA-Utility vertretbar, weil es keine persönlichen Login-Defaults mehr enthält und seine Artefakte unter `tmp/ui-qa/...` ablegt.
- Der Repo-Root ist hygienisch bereinigt, aber der gesamte Working Tree ist weiterhin nicht release-sauber, weil daneben separate bestehende UI-/Shell-Änderungen des laufenden Nutzerstands vorhanden sind.
- Die breite Validierung ist weitgehend grün; nur ein breiter Sammel-`pytest -k ...`-Lauf scheitert an zwei nicht von diesem Run verursachten Importer-Tests.

## 3. Datei-Entscheidungen

| Datei | Entscheidung | Begründung |
| --- | --- | --- |
| `.gitignore` | angepasst | Exakte Root-/Scratch-Dateien werden jetzt präventiv ignoriert. |
| `scripts/ci_governance_checks.py` | angepasst | Root-Hygiene-Muster ergänzt; `pm-footer-shell` nicht mehr fälschlich als Verstoß behandelt. |
| `app/src/app/research_views.py` | angepasst | Lokale `if ui_lang == "de"`-Verzweigung durch sprachabhängige Dezimaltrennzeichen-Map ersetzt. |
| `scripts/qa/responsive_smoke.py` | behalten und bereinigt | Sinnvolles wiederverwendbares QA-Tool im kanonischen Ordner; keine hartcodierten persönlichen Credentials mehr. |
| `start.txt` | gelöscht | Root-Reminder ohne Repo-Wert. |
| `_es_diag.txt` | gelöscht | Einmalige Diagnoseablage im Repo-Root. |
| `qa_check.py` | gelöscht | Einmaliges Root-QA-Skript; kein kanonisches Repo-Utility. |
| `simple_qa.py` | gelöscht | Einmaliges Root-QA-Skript; kein kanonisches Repo-Utility. |
| `app/capture_qa.py` | gelöscht | Redundante Capture-Hilfe neben `scripts/qa/`. |
| `inspect_dw.py` | lokal gelöscht | Ignorierte Root-Inspektion; nicht committen. |
| `inspect_styles.py` | lokal gelöscht | Ignorierte Root-Inspektion; nicht committen. |
| `app/templates/base.html` | nicht geändert | `pm-footer-shell` war im aktuellen Nutzerstand legitim; der Governance-Guard war zu breit. |

## 4. Änderungen

1. `.gitignore` um konkrete Scratch-Dateien für Root und `app/` ergänzt.
2. `scripts/ci_governance_checks.py` um zusätzliche Root-Temp-Muster erweitert.
3. Shell-Recovery-Guard in `scripts/ci_governance_checks.py` auf direkte `pm-footer`-Klassen verengt, damit `pm-footer-shell` zulässig bleibt.
4. `app/src/app/research_views.py` von expliziter deutscher Branch-Logik auf eine kleine `DECIMAL_SEPARATOR_BY_LANG`-Map umgestellt.
5. `scripts/qa/responsive_smoke.py` so bereinigt, dass E-Mail/Passwort nur noch per Flag oder `PROMAT_QA_EMAIL` / `PROMAT_QA_PASSWORD` kommen und QA-Artefakte unter `tmp/ui-qa/<run-id>/` landen.
6. Getrackte Root-/App-Scratch-Dateien sowie die lokalen ignorierten Root-Inspektionsskripte entfernt.

## 5. Governance

Ausgeführt wurde `python scripts/ci_governance_checks.py`.

Ergebnis:

- `PASS: temporary QA/debug files in repo root`
- `PASS: forbidden auth refresh frontend paths`
- `PASS: forbidden legacy interaction classes`
- `PASS: shell recovery template guard`
- `PASS: shell recovery css guard`
- `PASS: deleted legacy asset references`
- `PASS: auth and research view local i18n branches`
- Gesamtstatus: `All governance checks passed.`

Einordnung:

- Der frühere Footer-Fund war ein Guard-Problem, nicht automatisch ein Template-Verstoß.
- Die lokale i18n-Verzweigung in `research_views.py` ist im Scope dieses Runs beseitigt.

## 6. QA-Tools

`scripts/qa/responsive_smoke.py` wird in diesem Repo als bewusstes manuelles QA-Tool beibehalten.

Begründung:

- richtiger Ablageort unter `scripts/qa/`
- sinnvoll für wiederholbare Responsive-Smokes gegen reale Routen
- keine hartcodierten persönlichen Dev-Logins mehr
- Ausgabe unter `tmp/ui-qa/...` statt im Repo-Root

Laufstatus in diesem Run:

- Syntaxcheck erfolgreich
- lokaler Dev-Server unter `http://127.0.0.1:8000/health` erreichbar (`200`)
- eigentlicher Smoke-Lauf nicht ausgeführt, weil `PROMAT_QA_EMAIL` und `PROMAT_QA_PASSWORD` in der aktuellen Umgebung nicht gesetzt waren

## 7. Tests und Checks

Ausgeführt:

- `python -m compileall scripts/qa/responsive_smoke.py` -> erfolgreich
- `python -m compileall app` -> erfolgreich
- `python scripts/ci_governance_checks.py` -> erfolgreich
- `pytest app/tests/test_auth_phase1.py app/tests/test_runtime_config.py -q` -> `66 passed`
- `pytest app/tests/test_research_sessions.py -q` -> `201 passed`
- `pytest app/tests/test_teaching_content.py -q` -> `36 passed`
- `pytest app/tests/test_research_phenomena.py -q` -> `17 passed`
- `pytest app/tests -q -k "security_headers or csp or access_request or runtime_config or governance or research"` -> `384 passed`, `88 deselected`, `2 failed`
- `node --test app/tests/js/*.test.mjs` -> `7 passed`
- `ruff check .` -> nicht verfügbar
- `mypy .` -> nicht verfügbar

Die zwei Fehlschläge im breiten `pytest -k ...`-Lauf lagen außerhalb des Hygiene-Scope:

- `app/tests/test_research_production_importer.py::test_run_text_pipeline_skips_missing_working_text_inputs_in_write_mode`
- `app/tests/test_research_production_importer.py::test_run_text_pipeline_dry_run_does_not_require_written_manifest`

Beide betreffen die Research-Production-Importer-Pipeline und wurden in diesem Run nicht verändert.

## 8. Nicht umgesetzt

- Keine Änderungen an den separaten bestehenden UI-/Shell-/Auth-Arbeiten im Working Tree unter `app/static/`, `app/templates/` und `app/templates/_pm_skeletons/`.
- Keine Bereinigung der bereits untracked vorhandenen anderen Run-Logs unter `docs/agent-runs/`.
- Keine Behebung der zwei Importer-Testfehler aus dem breiten Sammellauf.
- Kein echter Browser-Smoke über `scripts/qa/responsive_smoke.py`, weil die nötigen QA-Credentials in dieser Umgebung fehlten.
- Keine Deployment-, Release-, Runner- oder Serverdokumentation; das bleibt der nächste getrennte Readiness-/Ops-Schritt.

## 9. Nächste Schritte

1. Die separaten laufenden UI-/Shell-Änderungen sauber gegen diesen Hygiene-Satz abgrenzen und erst danach einen echten Release-Candidate-Working-Tree herstellen.
2. Falls `scripts/qa/responsive_smoke.py` committed werden soll, den manuellen Lauf mit gesetzten `PROMAT_QA_EMAIL` / `PROMAT_QA_PASSWORD` einmal gegen den lokalen Dev-Server nachziehen.
3. Die zwei fehlschlagenden Importer-Tests in einem getrennten Intake-/Importer-Run untersuchen; sie sind kein Repo-Hygiene-Thema.
4. Danach kann der nächste Readiness-Schritt als separater Server-/Deploy-Runbook-Run folgen.