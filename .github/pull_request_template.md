## Ziel

Kurze Beschreibung des Changes und des gelösten Problems.

## Betroffene Bereiche

- App / Docs / Scripts / Runtime / Governance

## Verbindliche Quellen

- [ ] relevante Datei(en) unter `docs/spec/` geprüft
- [ ] root `AGENTS.md` geprüft
- [ ] relevante scoped `AGENTS.md` geprüft

## Architektur- und Paritätswirkung

- Welche Architekturwirkung hat der Change?
- Gibt es Auswirkungen auf Dev/Prod-Parität?

## Dokumentation

- [ ] `docs/spec/` aktualisiert, falls aktive Regeln betroffen sind
- [ ] `docs/agent-runs/` aktualisiert
- [ ] `docs/decisions/` aktualisiert, falls eine dauerhafte Entscheidung getroffen wurde
- [ ] `docs/runbooks/` aktualisiert, falls ein wiederholbarer Ablauf geändert wurde

## Governance-Check

- [ ] keine deutschen technischen Slugs oder alten Legacy-Pfade eingeführt
- [ ] `person_id`/`session_id` bleiben im kanonischen Format; keine Alt-IDs oder Session-IDs mit Level/L1/Varietät eingeführt
- [ ] kein Webapp-Zugriff auf `secure/`
- [ ] keine direkte öffentliche Auslieferung aus `data/`
- [ ] keine stillen Umbenennungen ohne Doku

## UI- und Konsistenzcheck

- [ ] produktive Referenzseiten geprüft, falls UI betroffen ist
- [ ] bestehende UI-Familien wiederverwendet oder erweitert statt neu erfunden
- [ ] `sample` aktualisiert, falls ein repräsentiertes aktives UI-Element geändert wurde
- [ ] Browser-Durchlauf und Screenshots ergänzt, falls die Änderung visuell substanziell ist
- [ ] bei Änderungen an globalem oder shared CSS die betroffenen Familien auf mindestens einer weiteren Seite gegengeprüft

## Verifikation

- Tests, Checks oder manuelle Validierung