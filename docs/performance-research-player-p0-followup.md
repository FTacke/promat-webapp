# Research Player P0 Follow-up

## Scope

- Umsetzung der P0-Punkte aus [docs/performance-diagnostics-research-player.md](performance-diagnostics-research-player.md)
- Fokus auf Research Player `text`/`wordlist` und Research Comparison Initial-Boot
- Live-Nachmessung lokal gegen `http://127.0.0.1:8010`

## Umgesetzt

### 1. Player: doppelten Sync-Payload für `text` und `wordlist` entfernt

- Der Player bezieht seine Sync-Timings für `text` und `wordlist` jetzt aus dem bereits gerenderten DOM statt aus einem zweiten vollständigen JSON-Abbild.
- Token-Segmente tragen dafür `data-player-token-start-ms` und `data-player-token-end-ms` im DOM.
- Der eingebettete `pm-player-state` transportiert für diese Modi nur noch die Meta-Steuerdaten und keine vollständigen Item-/Token-Listen mehr.

### 2. Comparison: impliziten Default-Workspace ohne Initial-API-Kette gebaut

- Der authentifizierte Einstieg ohne `set_id` erzeugt beim ersten Laden keinen impliziten Draft mehr per API.
- Die Workbench startet stattdessen mit einem lokalen impliziten Default-Workspace und erzeugt erst bei einer echten Mutation einen persistenten Draft.
- Der zusätzliche Preset-Reload auf Client-Seite entfällt, weil `materialPresets` bereits serverseitig im Initialzustand enthalten sind.

### 3. Player: Hauptaudio auf `preload="none"` umgestellt

- Primäres und sekundäres Player-Audio laden keine Metadaten mehr beim Seitenaufbau.
- Für Item-Seeks lädt `research-player.js` Metadaten jetzt bei Bedarf vor dem Sprung an den Clip-Offset.

## Vorher / Nachher

### Research Player `text`

Direkt vergleichbarer Vorher-Wert aus der Diagnose:

- HTML: 223.8 KB
- JSON-State: 72.2 KB
- Audio-Requests vor Interaktion: 1
- DOM-Knoten: 1140

Live-Nachmessung nach Umsetzung auf `/en/research/spanish/player/ES-L-0001-2026-S01/text?source=speakers`:

- HTML: 180724 Bytes, ca. 176.5 KB
- JSON-State: 632 Bytes, ca. 0.6 KB
- Audio-Requests vor Interaktion: 0
- DOM-Knoten: 1140

Direkter Effekt:

- HTML um ca. 43.1 KB reduziert
- eingebetteter JSON-State um ca. 71.6 KB reduziert
- früher Audio-Request vor Interaktion entfernt

Zusätzlicher Live-Check nach erstem Item-Klick:

- danach 2 GET-Requests auf das Hauptaudio beobachtet
- Wiedergabe lief an; gemessener `currentTime` danach ca. `1.85s`
- gemessene Audio-Dauer ca. `226.27s`
- Fortschrittsregler war aktiv (`disabled = false`)

### Research Comparison ohne `set_id`

Vorher-Befund aus der Diagnose:

- authentifizierter Einstieg ohne `set_id` löste eine Initial-Kette aus:
  - sichtbare Sets laden
  - impliziten Draft anlegen
  - Standardmaterial per `PUT .../items` schreiben

Live-Nachmessung nach Umsetzung auf `/en/research/spanish/comparison` mit lokalem Dev-Admin:

- `0` Requests auf `/api/research/sets` beim ersten Seitenaufbau
- DOM-Knoten: `390`
- eingebetteter Comparison-State: `55535` Bytes, ca. `54.2 KB`

Der belastbare P0-Effekt im Comparison-Slice ist nicht eine kleinere Grundseite, sondern das Entfernen der frühen Set-API-Kette für den ersten authentifizierten Einstieg.

## Validierung

- `pytest app/tests/test_research_player_set_context.py -q`
- `pytest app/tests/test_research_comparison.py -q`
- `get_errors` auf:
  - `app/static/js/pages/research-player.js`
  - `app/static/js/pages/research-comparison.js`
  - `app/templates/pages/research_player.html`
  - `app/src/app/research_views.py`
  - `app/src/app/research_player_runtime.py`
- Live-Playwright-Smoke-Run gegen `http://127.0.0.1:8010` mit lokalem Dev-Admin-Login

## Offene Punkte

- Der Player transportiert weiterhin denselben sichtbaren Text im HTML; P0 reduziert die doppelte Timing-/Tokenstruktur, nicht die eigentliche Textmenge.
- Der Comparison-Initialzustand bleibt asset- und state-seitig relativ groß; P0 beseitigt hier vor allem unnötige frühe Mutations-Requests.
- Für weitere Schritte bleiben die P1/P2-Punkte aus der Diagnose gültig, besonders Shared-CSS-/Shared-JS-Segmentierung und spätere state-basierte Player-Navigation.