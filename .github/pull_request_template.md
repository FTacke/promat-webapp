## Ziel

Kurze Beschreibung des Changes und des gelösten Problems.

## Betroffene Bereiche

- App / Docs / Scripts / Runtime / Governance

## Verbindliche Quellen

- [ ] `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md` geprüft
- [ ] root `AGENTS.md` geprüft
- [ ] relevante scoped `AGENTS.md` geprüft

## Architektur- und Paritätswirkung

- Welche Architekturwirkung hat der Change?
- Gibt es Auswirkungen auf Dev/Prod-Parität?

## Dokumentation

- [ ] `docs/agent-runs/` aktualisiert
- [ ] `docs/start/` aktualisiert, falls Bootstrap/Setup/Governance/Repo-Struktur betroffen ist
- [ ] `docs/decisions/` aktualisiert, falls eine dauerhafte Entscheidung getroffen wurde
- [ ] `docs/runbooks/` aktualisiert, falls ein wiederholbarer Ablauf geändert wurde

## Governance-Check

- [ ] keine deutschen technischen Slugs oder alten Legacy-Pfade eingeführt
- [ ] `person_id`/`session_id` bleiben im kanonischen Format; keine Alt-IDs oder Session-IDs mit Level/L1/Varietät eingeführt
- [ ] kein Webapp-Zugriff auf `secure/`
- [ ] keine direkte öffentliche Auslieferung aus `data/`
- [ ] keine stillen Umbenennungen ohne Doku

## Verifikation

- Tests, Checks oder manuelle Validierung