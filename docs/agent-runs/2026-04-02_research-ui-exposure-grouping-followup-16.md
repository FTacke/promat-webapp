# Exposure-Gruppierung auf Profilseiten feinjustiert

Datum: 2026-04-02

## Ziel

Die bereits weitgehend richtige Exposure-Darstellung auf Profilseiten noch klarer gruppieren: kleine semantische Wrapper pro Eintrag, engere Bindung zwischen Summary und optionaler Notiz und deutlichere Trennung zwischen mehreren Aufenthalten, ohne Card-Look oder zusätzliche UI-Chroming-Schicht.

## Geänderte Bereiche

- `app/templates/pages/research_speaker_profile.html`: Exposure-Einträge mit dedizierten Wrapper-/Summary-/Notiz-Klassen gerendert
- `app/static/css/30_components.css`: Mikrotypografie und Abstände für Exposure-Einträge nachjustiert; enger innerhalb eines Eintrags, klarer getrennt zwischen Einträgen
- `app/templates/pages/sample_page.html`: Showcase-Markup an die aktive Exposure-Struktur angeglichen
- `app/tests/test_research_sessions.py`: Fallback für 0 Einträge und gerenderte Exposure-Gruppierung regressionsgesichert

## Normative Doku

- Keine Änderung unter `docs/spec/`: die bestehende Regel in `docs/spec/research-access.md` beschreibt die aktive Exposure-Darstellung bereits ausreichend.

## Verifikation

- Builder-Test für 1 Eintrag ohne Notiz bleibt abgedeckt
- Builder-Test für 1 Eintrag mit längerer Notiz bleibt abgedeckt
- Builder-Test für mehrere Einträge mit nur teilweiser Notiz bleibt abgedeckt
- zusätzlicher Builder-Test für 0 Einträge mit kompaktem Fallback ergänzt
- zusätzlicher Route-/Template-Test prüft Exposure-Wrapper, Summary- und Notiz-Klassen in der gerenderten Profilseite

## Offene Punkte

- Keine weiteren sichtbaren Restpunkte in der Exposure-Gruppierung erkannt; visuell bleibt der Block bewusst listenartig und ohne Kartenoptik.