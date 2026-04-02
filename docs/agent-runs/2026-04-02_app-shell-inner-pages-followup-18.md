# Gemeinsame Innen-Shell über Standardseiten vereinheitlicht

Hinweis: Die dort eingeführte Shell-Vereinheitlichung bleibt aktiv, aber die damalige kopflose Research-Sidebar-Regel wurde im späteren Follow-up revidiert. Der Sidebar-Header ist inzwischen auf allen Innen-Seiten wieder systemweit Standard.

Datum: 2026-04-02

## Ziel

Die neue Shell-Hierarchie von einer Research-spezifischen Umsetzung auf die gemeinsame Innen-Shell der Standardseiten übertragen: gleiche Topbar-Geometrie, gleicher vertikaler Shell-Start, gleiche Sidebar-Trennlinie und explizite Regeln für Sidebar-Kopfkontexte. Die Landing-Seite bleibt ausgenommen.

## Ursache der Inkonsistenz

- Die neue Shell-Variant war bisher in `app/static/css/layout.css` an `data-page="research"` gebunden.
- `sample` lief noch über einen separaten Renderpfad statt über den gemeinsamen `_render_promat_page`-Pfad.
- Dadurch waren Shell-Breite, Sidebar-Offset, Divider und Render-Absicherung faktisch research-zentriert statt plattformweit.

## Geänderte Bereiche

- `app/static/css/00_tokens.css`: generische Inner-Shell-Tokens ergänzt und bisherige research-spezifische Breiten/Offsets daran angekoppelt
- `app/static/css/layout.css`: Shell-Variant von `data-page="research"` auf die gemeinsame Klasse `app-shell--inner` verlagert
- `app/src/app/routes/public.py`: `_render_promat_page` markiert Standard-Innenseiten zentral als `app-shell--inner`; `sample` nutzt jetzt denselben Renderpfad
- `app/tests/test_research_sessions.py`: zusätzliche Render-Regressionen für Projekt, Forschung, Unterricht und Sample ergänzt

## Damals eingeführte Zwischenregeln

- Alle Standard-Innenseiten aus dem gemeinsamen Renderpfad nutzen `app-shell--inner`.
- Landing bleibt bei ihrem eigenen Layout und erhält diese Shell nicht.
- `context_mode="section"` rendert einen Bereichskopf mit Icon.
- `context_mode="language"` rendert den Sprachkontext mit Rücklink.
- `context_mode="none"` renderte in diesem Zwischenstand keinen Sidebar-Kopf; das wurde später wieder verworfen.
- Die Forschungs-Übersicht war in diesem Zwischenstand bewusst kopflos in der Sidebar; dieser Sonderfall wurde im Folge-Run wieder entfernt.

## Verifikation

- `/de/project`
- `/de/research`
- `/de/research/spanish`
- `/de/teaching/spanish`
- `/de/sample`
- vollständiger Testlauf: `pytest tests/test_research_sessions.py`

## Normative Doku

- Keine Änderung unter `docs/spec/`: der Umbau betrifft die gemeinsame Shell-Architektur und visuelle Hierarchie, nicht aktive fachliche Regeln.

## Bewusste Ausnahmen

- Landing-/Index-Seite behält ihr eigenes Grundlayout.
- Auth-/panel-hidden-Flächen sind nicht Teil dieser Standard-Innen-Shell.