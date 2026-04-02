# Research Recordings Speakers Correction Unification 03

Datum: 2026-04-01

## Ziel

Bestehende Research-Seiten und den `Sample`-Pruefstand in einem gezielten Korrektur- und Vereinheitlichungsrun an die aktuell gewuenschte Layout- und Hierarchielogik anpassen.

## Consulted Sources

- `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_recordings.html`
- `app/templates/pages/research_speakers.html`
- `app/templates/pages/research_speaker_profile.html`
- `app/templates/pages/sample_page.html`

## Geänderte Bereiche

- Research-Templates fuer `recordings`, `speakers` und Profil
- Research-bezogene Komponenten- und Card-Styles
- `Sample` als Referenzflaeche fuer Research-Workbench-Komponenten
- Research-Referenzdokumentation unter `docs/research_pages/`

## Wichtige Entscheidungen

- Keine neue Architektur, sondern nur gezielte Hierarchie- und Komponentenvereinheitlichung innerhalb der bestehenden dateibasierten Research-Anbindung
- Die `recordings`-Task-Zone nutzt integrierte Counts in den Panels statt einer separaten Summary-Box
- Speaker-Cards trennen den Profilteil und den Aufgabenfuss staerker; Aufgabenlinks bleiben direkt, aber bewusst leiser als Filterchips oder Hauptaktionen
- Das Profil bleibt ein Detailziel, wird aber als vertikale Hauptkarte mit nachgelagertem Aufgabencontainer gelesen
- `Sample` zeigt jetzt Dummy-Referenzen fuer die geschaerften Research-Komponenten, damit kuenftige UI-Arbeit dieselben Muster wiederverwenden kann

## Abweichungen

- Keine Abweichung von der aktiven Spezifikation oder von der bestehenden Dev/Prod-Paritaet

## Verifikation

- Editor-/Syntaxpruefung fuer die geaenderten Templates, Python- und CSS-Dateien
- manuelle Routenvalidierung der betroffenen Research-Seiten und der `Sample`-Seite steht nach dem Patch an

## Offene Punkte

- Die Task-Counts in `recordings` bleiben bis zu einer spaeteren task-genauen Datenanbindung an die aktuell sichtbare gefilterte Ergebnismenge gebunden
- Der Player ist weiterhin nur strukturell vorbereitet und nicht fachlich umgesetzt

## Nächste sinnvolle Schritte

- Route-Rendering der betroffenen Seiten im Flask-Testclient pruefen
- bei spaeterer echter Task-Datenbindung die Panel-Counts task-spezifisch machen