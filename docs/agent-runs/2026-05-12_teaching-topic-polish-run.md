# 2026-05-12 Teaching Topic Polish Run

## Scope

Gezielter Polish-Run fuer die oeffentliche Teaching-Pilotseite `which-pronunciation` plus den zugehoerigen Topic-Renderer und die gemeinsame Teaching-CSS.

## Umsetzung

- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
  - `topic_meta` als erster Body-Block eingefuegt
  - `audio_examples` als collapsible/default-closed gesetzt
  - Audio-Leads und Beispielhinweise redaktionell beruhigt
- `content/teaching/spanish/en/topics/which-pronunciation.yaml`
  - dieselbe strukturelle Angleichung fuer die englische Edition
- `app/src/app/teaching_content.py`
  - `audio_examples` und der Legacy-Alias `audio_example` tragen jetzt `collapsible` und `default_open` durch
- `app/templates/partials/_teaching_blocks.html`
  - `topic_meta` als expliziter Body-Block gerendert
  - `audio_examples` optional als ruhiger Details-Block gerendert
  - Audio-Karten ohne sichtbare Feldlabels fuer Transkript, Hinweis, Quelle und Speaker-ID
  - Quellenangabe bleibt auf Blockebene, Speaker-ID bleibt nur als kleine Sekundaerinfo auf Karten
- `app/static/css/20_layout.css`
  - Hub-Header zentriert, Backlink bleibt separat darueber
- `app/static/css/30_components.css`
  - topic-spezifische Lesetypografie ruhiger abgestimmt
  - Audio-Karten und Audio-Details auf das reduzierte Rendering angepasst
  - Inline-Code etwas leiser gesetzt
- `docs/spec/platform-data-files.md`
  - aktive Teaching-Regeln fuer `topic_meta`, Topic-H1, zentrierte Hub-Header, ruhige `audio_examples` und topic-spezifische Lesetypografie geschaerft
- `app/tests/test_teaching_content.py`
  - `audio_examples`-Collapsible-Flags abgesichert
- `app/tests/test_research_sessions.py`
  - Pilotseite auf genau einen `h1`, expliziten `topic_meta`-Block, default-closed `audio_examples` und das Fehlen sichtbarer Audio-Feldlabels abgesichert

## Validierung

### Pytest

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching or sample_page_uses_shared_inner_shell_renderer"`

Beide Laeufe gruen.

### Browser-QA

Selenium/Edge-Capture gegen eine isolierte Runtime auf `http://127.0.0.1:8010`.

Artefakte unter `tmp/ui-qa/2026-05-12-teaching-topic-polish/` fuer:

- `/de/teaching`
- `/en/teaching`
- `/de/teaching/spanish`
- `/de/teaching/spanish/which-pronunciation`
- `/de/teaching/spanish/final-r`
- `/en/teaching/spanish`
- `/de/sample`
- Mobile: `/de/teaching`
- Mobile: `/de/teaching/spanish/which-pronunciation`

Beobachtung:

- Hub-Header jetzt visuell zentriert und mit den Gruppen ausgerichtet
- Pilotseite ruhiger, `topic_meta` als erster Body-Block, `audio_examples` standardmaessig geschlossen
- `final-r` und `sample` ohne sichtbare Regressionssignale
- Browser-Konsole meldete nur bestehende Tracking-Prevention-Warnungen zu Bootstrap Icons
