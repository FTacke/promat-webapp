# 2026-05-12 Teaching Topic Correction Run

## Scope

Schneller Korrekturlauf für die Pilot-Topic-Seite `which-pronunciation` mit Fokus auf drei sichtbare Restprobleme: ruhigere Infobox-Hierarchie in zweispaltigen Abschnitten, kein doppelter PROMAT-Titel über Datawrapper-Embeds und neutrale Datawrapper-Darstellung ohne ungewollte Theme-Effekte.

## Umsetzung

- `app/templates/partials/_teaching_blocks.html`
  - sichtbare PROMAT-Embed-Titel für Datawrapper entfernt
  - `title` bleibt für den `iframe`-Titel und damit für Accessibility erhalten
- `app/static/css/30_components.css`
  - topic-lokale `info_box`-Darstellung in `span: 1` kompakter und ruhiger gemacht
  - Abstand zwischen Infobox-Titel und Body reduziert
  - Datawrapper-Embed-Oberflächen explizit auf neutrale helle Darstellung ohne Filter/Blend/Opacity-Effekte festgelegt
- `app/tests/test_research_sessions.py`
  - HTML-Regressionscheck ergänzt: keine sichtbare `pm-teaching-embed-card__title`, aber weiter vorhandene `iframe`-Titelattribute
- `docs/spec/platform-data-files.md`
  - aktive Regel ergänzt: Datawrapper-`title` ist auf Topic-Seiten Accessibility-/iframe-Titel, kein sichtbarer Kartenkopf
  - aktive Regel ergänzt: Topic-`info_box` in zweispaltigen Gruppen bleibt Begleitblock und keine konkurrierende Hero-Fläche

## Validierung

### Pytest

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q -k "embed or teaching"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "which_pronunciation or teaching_pilot or datawrapper or teaching"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_auth_phase1.py -q -k security_headers_allow_project_youtube_embed`

Alle fokussierten Läufe grün.

### Browser-QA

Geprüft im selben Run:

- `/de/teaching/spanish/which-pronunciation`
- `/en/teaching/spanish/which-pronunciation`

Artefakte:

- `tmp/ui-qa/2026-05-12-teaching-topic-correction-quick/`

Ergebnis:

- keine `SEVERE` Browser-Fehler
- keine sichtbaren doppelten PROMAT-Titel über Datawrapper-Embeds
- Datawrapper-Embeds erscheinen mit dunkler Schrift auf heller Fläche
- die rechte `info_box` wirkt kompakter und hierarchisch klarer als Begleitblock neben dem Haupttext
