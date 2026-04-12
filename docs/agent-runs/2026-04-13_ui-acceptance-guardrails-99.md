# UI Acceptance Guardrails 99

Datum: 2026-04-13

## Ziel

Die Workspace-Instruktionen und das UI-Runbook so nachschärfen, dass exakte UI-Vorgaben, screenshotgestützte Korrekturen und Browser-vs-Code-Diskrepanzen künftig als harte Abnahmekriterien behandelt werden und nicht erneut durch zu grobe Tests oder stale Runtime-Zustände verdeckt bleiben.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/runbooks/ui-change-workflow.md`

## Geänderte Bereiche

- Workspace-Instruktionen in `.github/copilot-instructions.md` und `.github/instructions/repo.instructions.md`
- Repo- und App-Governance in `AGENTS.md` und `app/AGENTS.md`
- Wiederholbarer UI-Abnahmeablauf in `docs/runbooks/ui-change-workflow.md`

## Wichtige Entscheidungen

- Exakte UI-Anordnungen, konkrete Labeltexte und screenshotgestützte Nutzerkorrekturen gelten jetzt ausdrücklich als harte Acceptance Targets, nicht als bloße Hinweise.
- Für UI-Änderungen an Reihenfolge, Platzierung oder Beschriftung müssen fokussierte Regressionen und Browser-QA künftig die exakte sichtbare Ordnung prüfen, nicht nur die Existenz der Controls.
- Wenn Browser und Code/Teststand auseinanderlaufen, wird stale Runtime explizit als Standardverdacht behandelt und vor Abschluss aktiv geprüft.

## Abweichungen

- Keine Abweichung von aktiven Specs oder Runtime-Grenzen.
- Kein Produktcode wurde geändert; der Lauf schärft nur Governance und Arbeitsanweisungen.

## Verifikation

- Editor-Fehlerprüfung für die geänderten Instruktions- und Runbook-Dateien: keine Fehler.
- Manuelle Gegenprüfung der eingefügten Regeln in `.github`-Instruktionen, Root-/App-`AGENTS.md` und `docs/runbooks/ui-change-workflow.md`.

## Offene Punkte

- Instruktionen reduzieren diese Fehlerklasse deutlich, erzwingen sie aber nicht deterministisch. Falls künftig noch stärkere Absicherung gewünscht ist, wäre ein ergänzender Hook- oder QA-Skriptpfad der nächste Schritt.

## Nächste sinnvolle Schritte

- Bei der nächsten UI-Korrektur dieselben verschärften Regeln anwenden und prüfen, ob zusätzliche Hook-basierte Schutzmechanismen sinnvoll sind.