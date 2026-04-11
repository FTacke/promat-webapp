# PROMAT Docs Governance

Dieses Dokument ergänzt das Root-`AGENTS.md` für Arbeiten unter `docs/`.

## Bereichsrollen

- `docs/spec/` enthält die einzige aktive Source of Truth.
- `docs/decisions/` enthält nur ADRs und erklärt das Warum.
- `docs/runbooks/` enthält nur wiederholbare Abläufe.
- `docs/agent-runs/` enthält nur nicht-normative Arbeitsjournale.

## Regeln

- Neue aktive Regeln werden immer in eine bestehende oder neue passende Datei unter `docs/spec/` integriert.
- ADRs, Runbooks und Run-Logs dürfen keine konkurrierende Soll-Spezifikation aufbauen.
- Wenn eine ältere Doku-Datei nach `docs/spec/` überführt wurde, wird sie gelöscht oder vollständig entnormativisiert.
- Wiederkehrende Implementierungs-, UI- oder Prüf-Erkenntnisse aus mehreren Runs müssen in `docs/spec/` oder `docs/runbooks/` verdichtet werden; sie dürfen nicht nur als implizites Wissen in `docs/agent-runs/` stehen bleiben.
- `docs/plans/` bleiben Planungstexte; wenn ein Plan durch aktive Spec oder produktive Umsetzung überholt ist, erhält er einen klaren Statushinweis zurück auf `docs/spec/` oder wird entfernt.
- Keine neuen freien Doku-Sammelbecken anlegen.

## Pflicht bei Änderungen

- Bei fachlichen Änderungen zuerst prüfen, welche Datei unter `docs/spec/` angepasst werden muss.
- Bei Änderungen an App-Shell, Navigationshierarchie oder Bereichsnavigation die aktive Regel unter `docs/spec/platform-data-files.md` aktualisieren statt Zwischenstände in Run-Logs als Soll-Zustand stehen zu lassen.
- Für jeden substanziellen Run einen Eintrag unter `docs/agent-runs/` anlegen.
- Bei dauerhaften Architekturentscheidungen zusätzlich ein ADR unter `docs/decisions/` anlegen oder aktualisieren.
- Bei wiederholbaren Abläufen zusätzlich das passende Runbook unter `docs/runbooks/` aktualisieren.