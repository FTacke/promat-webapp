# Research Player Reading Mode

Datum: 2026-04-15

## Ziel

Die produktive `text`-Ansicht im Unified Player so nachschaerfen, dass die Textansicht als ruhiger Lesemodus wirkt, der `Liste | Text`-Schalter lokal im Content-Header sitzt, die alte separate `Ansicht`-Box verschwindet und die relevante deutsche Zaehlung auf `Items` umgestellt wird.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/runbooks/ui-change-workflow.md`
- `docs/spec/research-player.md`
- `app/templates/pages/research_player.html`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-player.js`
- `app/src/app/research_views.py`
- `app/src/app/i18n.py`
- `app/tests/test_research_sessions.py`
- `app/tests/test_research_player_set_context.py`

## Geaenderte Bereiche

- produktives Player-Template fuer den integrierten View-Switch im Content-Header
- gemeinsame Player-Komponenten-CSS fuer den kompakteren Textschalter und den ruhigeren Running-Text-Modus
- relevante deutsche Player- und Comparison-Texte von `Eintraege` auf `Items`
- fokussierte Player-Regressionen fuer die neue Header-Struktur
- aktive Player-Spec fuer die lokale Platzierung des View-Switches und den Lesemodus-Charakter von `running_text`

## Wichtige Entscheidungen

- Der View-Switch bleibt eine source-getriebene lokale Inhaltsoption und sitzt deshalb rechts im Content-Panel-Header statt als zweite separate Box zwischen Materialleiste und Inhalt.
- Die Textansicht bleibt kein zweiter Arbeitsmodus: sie ist ein ruhiger Lesemodus mit deutlich leiseren Nummern, subtilerem Aktivzustand und erst bei Hover, Fokus oder aktivem Segment sichtbaren Download-Aktionen.
- Der kompakte `Liste | Text`-Schalter nutzt dieselbe textbasierte Sprache wie der globale `DE | EN`-Switch, statt eine weitere Button- oder Chipfamilie einzufuehren.
- Weil die Live-HTML auf Port `8000` trotz gruener Tests noch stale war, wurde der aktive Dev-Server explizit neu gestartet und danach erneut gegen die authentifizierten Realrouten geprueft.

## Verifikation

- `Run research sessions tests`-Task: `147 passed`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_player_set_context.py -q`: `28 passed`
- `http://127.0.0.1:8000/health`: `healthy`
- authentifizierte Live-Pruefung nach Server-Neustart fuer `http://127.0.0.1:8000/de/research/english/player/EN-L-0001-2026-S01/text?source=recordings`:
  - `pm-player-view-switch` vorhanden
  - `pm-player-view-bar` nicht mehr vorhanden
  - keine sichtbare `Ansicht`-Beschriftung
  - Header zeigt `56 Items`
  - `Liste` und `Text` sind im lokalen Schalter vorhanden
- authentifizierte Live-Pruefung nach Server-Neustart fuer `http://127.0.0.1:8000/en/research/english/player/EN-L-0001-2026-S01/text?source=recordings`:
  - `pm-player-view-switch` vorhanden
  - `pm-player-view-bar` nicht mehr vorhanden
  - keine sichtbare `Ansicht`-Beschriftung
  - Header zeigt `56 items`
- Regression auf unbetroffener Player-Flaeche `http://127.0.0.1:8000/de/research/english/player/EN-L-0001-2026-S01/wordlist?source=recordings`:
  - kein `pm-player-view-switch`
  - kein `pm-player-view-bar`

## Offene Punkte

- Eine echte visuelle Screenshot-Abnahme wurde in diesem Run nicht archiviert; die Live-Pruefung erfolgte ueber authentifizierte Realrouten und gerenderte HTML-Merkmale nach Dev-Server-Neustart.