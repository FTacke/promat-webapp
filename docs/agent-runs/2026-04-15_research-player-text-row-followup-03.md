# Research Player Text Row Follow-up

Datum: 2026-04-15

## Ziel

Die produktive `text`-Sentence-List im Unified Player so nachschaerfen, dass Token-Hervorhebung sichtbar bleibt, technische oder hilfsweise Katalog-Metadaten nicht doppelt in der sichtbaren Zeile auftauchen und die Zeitangabe rechts im Feld wie bei `wordlist` sitzt.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `docs/spec/research-player.md`
- `app/templates/pages/research_player.html`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-player.js`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- Text-Zeilen-Meta im produktiven Player-Template
- Token-Aktivstil in den gemeinsamen Komponenten-CSS
- Token-Fallback in der produktiven Player-Sync-Logik
- fokussierte HTML-Regressions-Assertions fuer den Text-Player
- aktive Player-Spec fuer sichtbare Satzlisten-Metadaten
- Live-Validierung auf dem frisch neu gestarteten Dev-Server unter Port `8000`

## Wichtige Entscheidungen

- Technische Item-IDs und Hilfsmarker wie das Gruppenkuerzel `D` bleiben rein runtime- oder katalogintern und werden in der sichtbaren `text`-Sentence-List nicht doppelt neben der linken Anzeige-Nummerierung gezeigt.
- Die Zeitangabe bleibt Metadatum der Zeile, sitzt aber innerhalb des Feldes rechtsbuendig statt in der linken Metazeile.
- Wenn das aktuelle Audio innerhalb eines aktiven Items in eine kleine Token-Luecke faellt, bleibt der naechstliegende Token aktiv markiert, damit die innere Hervorhebung nicht scheinbar verschwindet.
- Die aktive Token-Hervorhebung bleibt rein als ruhige Hintergrundmarkierung umgesetzt: keine Border, kein zusaetzliches Padding, keine Gewichtungs- oder Groessenverschiebung, nur eine subtile Hintergrundfarbe mit kleiner Rundung.

## Abweichungen

- Der laufende Dev-Prozess auf Port `8000` lieferte weiterhin stale HTML ohne Token-Spans aus; die produktive Pruefung musste daher gegen eine frische App-Instanz auf Port `8010` erfolgen.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "renders_text_token_spans_when_alignment_tokens_exist or keeps_sentence_only_text_markup_when_no_tokens_exist"`
- `Run research sessions tests`-Task: `145 passed`
- Live-Validierung gegen frische App-Instanz auf `http://127.0.0.1:8010`
- bestaetigt fuer den frisch neu gestarteten Port-`8000`-Server auf `ES-L-0001-2026-S01/text?source=recordings&render_mode=sentence_list`:
  - Token-Spans werden gerendert
  - weder `d_02` noch das Gruppenkuerzel `D` erscheinen mehr als sichtbares Metadatum in der Zeile
  - Zeit sitzt in eigenem rechten Slot innerhalb der Zeile
- bestaetigt fuer reale Produktivrouten auf Port `8000`:
  - `wordlist` bleibt ohne Token-Markup und ohne neue Zeit-Slot-Struktur
  - `text`-Sentence-List in `de` und `en` rendert Token-Spans und rechten Zeit-Slot
  - Player-Compare-Route fuer `text` rendert denselben rechten Zeit-Slot und Token-Spans pro Zeile

## Offene Punkte

- Fuer die dynamische Token-Hervorhebung im laufenden Port-`8000`-Prozess ist ein Neustart des Dev-Servers noetig, weil dieser Prozess noch alten HTML-Stand ausliefert.

## Nächste sinnvolle Schritte

- Den lokalen Dev-Server auf Port `8000` neu starten, damit die aktualisierte Sentence-List auch dort sichtbar ist.