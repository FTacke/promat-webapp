# 2026-05-12 Teaching Topic Visual Polish and Embeds

## Scope

Gezielter Visual-Polish-Run fuer die oeffentliche Teaching-Topic-Seite `which-pronunciation` inklusive strukturierter Datawrapper-Embeds.

## Umsetzung

- `app/templates/pages/teaching_page.html`
  - Topic-Routen nutzen jetzt einen eigenen `pm-teaching-topic-header`-Container.
  - Topic-Blockgrid traegt die spezifische Klasse `pm-teaching-block-grid--topic`.
- `app/static/css/20_layout.css`
  - Topic-Header und Topic-Content haben jetzt getrennte Max-Widths.
  - Topic-Backlink und Topic-Grid bleiben breiter als der eigentliche Header.
  - Deutlicherer Abstand zwischen Topic-Header und erstem Content-Block.
- `app/static/css/30_components.css`
  - Topic-H1 und Lead zentriert und ruhiger skaliert.
  - Metadaten als ruhige Zeile direkt unter dem Lead behandelt.
  - Topic-Lesetypografie fuer Fliesstext, Materialtexte, Notes und Transkripte vergroessert.
  - Inline-Code ruhiger gehalten, ohne technische Badge-Anmutung.
  - Datawrapper-Embeds auf ihre eigene Block- und Frame-Geometrie eingestellt.
- `app/src/app/teaching_content.py`
  - `embed` als strukturierter Teaching-Block implementiert.
  - Aktiver Provider: `datawrapper`.
  - Fehlende `src`-Werte oder unbekannte Provider rendern keinen kaputten Block.
  - `height` wird normalisiert und faellt auf einen Default zurueck.
- `app/templates/partials/_teaching_blocks.html`
  - `embed`-Bloecke rendern Datawrapper-`iframe`s ueber strukturierte Felder.
  - Kein rohes iframe/script aus YAML.
- `app/static/js/modules/core/datawrapper.js`
  - zentrale Resize-Behandlung fuer Datawrapper-Embeds
- `app/static/js/modules/core/entry.js`
  - einmalige Initialisierung der Datawrapper-Resize-Logik im Core-Bundle
- `app/src/app/__init__.py`
  - CSP `frame-src` erlaubt jetzt neben YouTube auch `https://datawrapper.dwcdn.net`
- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
  - die beiden Karten wurden von statischen Bildern auf Datawrapper-`embed`-Bloecke umgestellt
- `content/teaching/spanish/en/topics/which-pronunciation.yaml`
  - dieselbe Umstellung fuer die englische Topic-Edition
- `app/tests/test_teaching_content.py`
  - neue Builder-Checks fuer `embed`, Default-Height und fail-closed bei invaliden Embeds
- `app/tests/test_research_sessions.py`
  - neue Render-Checks fuer Topic-Header-Container, Topic-Grid-Klasse und Datawrapper-`iframe`s
- `app/tests/test_auth_phase1.py`
  - CSP-Header-Test auf die erlaubte Datawrapper-Frame-Quelle erweitert
- `docs/spec/platform-data-files.md`
  - aktive Regeln fuer Topic-Headerbreite, Topic-Contentbreite, artikelnaehere Lesetypografie und sichere Datawrapper-Embeds geschaerft

## Validierung

### Pytest

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching or sample_page_uses_shared_inner_shell_renderer"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_auth_phase1.py -q -k security_headers_allow_project_youtube_embed`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_language_root_uses_shared_topbar_and_mobile_drawer"`

Beide Laeufe gruen.

Die beiden zusaetzlichen Nachlaeufe fuer CSP und den betroffenen Topic-Slice ebenfalls gruen.

### Browser-QA

Gepruefte QA-Routen fuer den Run:

- `/de/teaching`
- `/de/teaching/spanish`
- `/de/teaching/spanish/which-pronunciation`
- `/de/teaching/spanish/final-r`
- `/en/teaching`
- `/en/teaching/spanish`
- `/de/sample`
- Mobile: `/de/teaching/spanish/which-pronunciation`

Die Artefakte dieses Runs liegen unter `tmp/ui-qa/2026-05-12-teaching-topic-visual-polish/`.

Ergebnis:

- keine `SEVERE` Browser-Fehler nach Neustart der QA-Runtime
- verbleibende `WARNING`-Logs betreffen Tracking-Prevention fuer Bootstrap-Icons von jsDelivr
