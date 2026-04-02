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
- Keine neuen freien Doku-Sammelbecken anlegen.

## Pflicht bei Änderungen

- Bei fachlichen Änderungen zuerst prüfen, welche Datei unter `docs/spec/` angepasst werden muss.
- Für jeden substanziellen Run einen Eintrag unter `docs/agent-runs/` anlegen.
- Bei dauerhaften Architekturentscheidungen zusätzlich ein ADR unter `docs/decisions/` anlegen oder aktualisieren.
- Bei wiederholbaren Abläufen zusätzlich das passende Runbook unter `docs/runbooks/` aktualisieren.