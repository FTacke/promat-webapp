# PROMAT Dokumentationssystem reduziert

Datum: 2026-04-02

## Ziel

Die gesamte aktive Dokumentationslandschaft auf wenige, klare und dauerhaft wartbare Orte reduzieren: eine Spec-Ebene unter `docs/spec/`, ADRs unter `docs/decisions/`, Runbooks unter `docs/runbooks/` und nicht-normative Arbeitsjournale unter `docs/agent-runs/`.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `docs/AGENTS.md`
- `app/AGENTS.md`
- `scripts/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`

## Geänderte Bereiche

- neue aktive Spezifikation unter `docs/spec/`
- Root-README und Repo-Governance
- ADR-, Runbook- und Run-Log-Metadokumente
- Löschung redundanter Doku-Orte unter `docs/start/`, `docs/layout/`, `docs/zenscial_base/`, `docs/research_pages/`, `docs/architecture/`, `docs/conventions/` und `docs/data-intake/`
- Löschung lokaler README-Schatten unter `scripts/`, `data/`, `public/`, `secure/` und `app/static/js/modules/navigation/`

## Wichtige Entscheidungen

- Aktive Fach- und Technikregeln stehen nur noch in `docs/spec/`.
- `README.md` im Root bleibt ein Einstieg und verweist auf die Spec-Dateien, statt selbst eine zweite Fachspezifikation zu tragen.
- `docs/decisions/` erklärt nur noch das Warum, `docs/runbooks/` nur noch wiederholbare Abläufe, `docs/agent-runs/` nur noch nicht-normative Arbeitsprotokolle.
- Alte dated Einzelnotizen, Parallel-Spezifikationen und Schatten-READMEs wurden bewusst entfernt statt konserviert.

## Abweichungen

- Keine.

## Verifikation

- aktive Regeln aus alter Spezifikation, Research-Referenz und Intake-Doku in drei neue Spec-Dateien überführt
- PR-/Issue-Templates sowie AGENTS/.github auf die neue Spec-Ebene umgestellt
- fokussierter Testlauf `app/tests/test_research_sessions.py` bleibt grün
- gezielte Suchläufe gegen alte aktive Doku-Orte und alte Source-of-Truth-Verweise in Governance durchgeführt

## Offene Punkte

- Historische Agent-Run-Dateien enthalten weiterhin Verweise auf inzwischen gelöschte frühere Doku-Orte; sie bleiben als Journal bestehen, sind aber nicht normativ.

## Nächste sinnvolle Schritte

- neue fachliche Regeln künftig nur noch durch Aktualisierung einer bestehenden Datei unter `docs/spec/` einführen
- neue Runbooks nur dann anlegen, wenn ein Ablauf tatsächlich wiederholt durch andere Personen oder Agents gefahren werden muss
