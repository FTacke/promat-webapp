# Governance Operationalization 01

Datum: 2026-03-31

## Ziel

Eine schlanke, aber verbindliche Agenten- und Repo-Governance über Root, relevante Teilbereiche, `.github/` und `docs/` einführen, die die bestehende PROMAT-Spezifikation operationalisiert.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- Root-Governance in `AGENTS.md`
- Scoped Governance in `app/AGENTS.md`, `docs/AGENTS.md`, `scripts/AGENTS.md`
- Repo-Agent-Instruktionen unter `.github/`
- aktive Doku-Struktur unter `docs/architecture/`, `docs/conventions/`, `docs/runbooks/`, `docs/decisions/`, `docs/agent-runs/`
- `README.md` zur besseren Auffindbarkeit der Governance

## Wichtige Entscheidungen

- Die Spezifikation bleibt die bindende Source of Truth; Governance-Dateien operationalisieren sie nur.
- `docs/agent-runs/` wird die Standardstelle für substanzielle Run-Dokumentation.
- `docs/start/` bleibt die zusätzliche Bootstrap- und Governance-Chronik, damit bestehende Repo-Regeln kompatibel bleiben.
- Für `.github/CODEOWNERS` wurde bewusst keine Datei angelegt, weil im Repo kein autoritativer Owner-Stand definiert ist.

## Abweichungen

- Keine aktive Architekturabweichung eingeführt.
- Historische Dokumente unter `docs/start/` enthalten weiterhin ältere Zustände und Begriffe; sie bleiben Historie und sind nicht als aktive Governance zu verwenden.

## Verifikation

- Bestehende Governance-Dateien und die Spezifikation wurden gegeneinander geprüft.
- Die neue Struktur vermeidet parallele aktive Doppeldokumentation.
- Repo-weit wurde geprüft, dass die neuen Regeln zum aktuellen bereinigten Routing- und Runtime-Stand passen.

## Offene Punkte

- Historische `docs/start/`-Einträge verwenden teils ältere Begriffe und Layout-Logik; sie sind korrekt als Historie, aber nicht harmonisiert.
- Eine spätere Owner-Zuordnung könnte `.github/CODEOWNERS` sinnvoll machen.
- Einige UI-Demo-Assets und Beispieltexte unter `app/templates/pages/sample_page.html` und den zugehörigen Bilddateinamen tragen weiterhin ältere deutsche Benennungen. Das ist keine Routing- oder Datenabweichung, aber ein verbleibender Konsistenzrest außerhalb der aktiven Governance-Schicht.

## Nächste sinnvolle Schritte

- Erste zukünftige Runs konsequent über `docs/agent-runs/_template.md` dokumentieren.
- Bei der nächsten dauerhaften Architekturentscheidung ein erstes ADR unter `docs/decisions/` anlegen.