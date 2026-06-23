# Spanische Design-Seite: Citation, Fußnoten und Literaturverweise

## Ziel

Die Research-Citation visuell an die bestehende Teaching-Citation angleichen, vorhandene DOI-/Online-Angaben in der Literatur verlinken und alle Fußnoten der spanischen Design-Seite robust auf eine numerische Folge 1–4 umstellen.

## Konsultierte Grundlagen

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`, `app/AGENTS.md`, `docs/AGENTS.md`
- bestehende Teaching-Citation-, Admonition- und Footnote-Partials

## Änderungen und Entscheidungen

- Die Research-Citation nutzt den vorhandenen Teaching-Theme-Kontext und damit exakt dessen Quote-Icon; es wurde kein neues Icon und keine neue Card eingeführt.
- Bereits vorhandene DOI- und Online-URLs werden in beiden Sprachfassungen als Links gerendert; die Literaturauswahl bleibt unverändert.
- Projektkontext und Wortlisten-Fußnoten sind in beiden Sprachen fortlaufend von 1 bis 4 nummeriert.
- Die Footnote-Partial verwendet die vollständigen lokalisierten IDs direkt und hängt die Sprache nicht länger doppelt an.
- Ein Content-Test prüft Eindeutigkeit, fortlaufende numerische Labels, vollständige Vor- und Rückreferenzen sowie gleiche Fußnotenzahlen in Deutsch und Englisch.
- Keine aktive Spec musste geändert werden, da Routing, Access, Capabilities und Inhaltsauswahl unverändert bleiben.

## Verifikation

- Fokussierte Research- und Teaching-Regressionstests sowie Ruff.
- Browserprüfung der realen deutschen und englischen Research-Routen auf Desktop und Mobile einschließlich Icon-Gleichheit, Literatur-Links, Fußnoten-Zielen, Rücksprüngen, Überlauf und Konsolenfehlern.

## Abweichungen und offene Punkte

Keine.
