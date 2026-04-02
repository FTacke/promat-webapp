# PROMAT Personbasierter Research-Zugang

Datum: 2026-04-02

## Ziel

Den Bootstrap-Stand der Research-Fläche strukturell auf personbasierten Zugang umstellen und die Repo-Regeln für kanonische Research-IDs festziehen.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- aktive Runtime- und Seed-Dateien unter `app/src/app/` und `scripts/session_setup/`

## Geänderte Bereiche

- personbasierte Research-Runtime und Templates
- spanischer Dev-Seed mit Mehrfach-Sessions pro Lernenden-Person
- aktive Governance unter `.github/`, `AGENTS.md`, `docs/conventions/`
- aktive Referenzdoku zu Research, Import und Intake

## Wichtige Entscheidungen

- `person_id` trägt jetzt Korpuscode und Sprecherstatus; `session_id` referenziert genau `person_id`, Jahr und Session-Nummer.
- `speakers` bleibt personbasiert, `recordings` bleibt session-/taskbasiert.
- Native-Speaker-Vergleichsprofile bleiben ein strikter Ein-Session-Sonderfall.

## Abweichungen

- Keine.

## Verifikation

- spanischer Dev-Seed neu geschrieben
- fokussierte Tests für Aggregation und Selektion grün
- aktive Doku und Governance auf alte ID-Beispiele geprüft und aktualisiert

## Offene Punkte

- Kein vollständiger Browser-E2E-Test gegen laufenden Dev-Server.

## Nächste sinnvolle Schritte

- echte Importpipeline später direkt auf denselben Person-/Session-Vertrag ausrichten
- Player- und Exportausbau an die neue Session-Fokussierung anbinden