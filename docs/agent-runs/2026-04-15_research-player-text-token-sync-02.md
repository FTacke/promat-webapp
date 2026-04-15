# Research Player Text Token Sync

Datum: 2026-04-15

## Ziel

Den bestehenden produktiven Unified Player fuer `text` so erweitern, dass bei vorhandenen Token-Timings aus `alignment/text.json` neben der bestehenden Satz- bzw. Item-Aktivierung auch eine additive innere Token-Hervorhebung moeglich ist, ohne eine zweite Player-Architektur einzufuehren.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/research-player.md`
- `app/src/app/research_player_runtime.py`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/templates/pages/research_comparison.html`
- `app/static/js/pages/research-player.js`
- `app/static/js/pages/research-comparison.js`
- `app/tests/test_research_sessions.py`
- reale Alignment-Dateien unter `data/sessions/**/alignment/text.json`

## Geänderte Bereiche

- Player-Runtime-Normalisierung fuer `text`
- Player-Page-Builder und Client-State fuer Token-Timings
- produktives Unified-Player-Template fuer additive Token-Spans
- produktive Player-JS-Synchronisierung mit `requestAnimationFrame`
- minimale gemeinsame Komponenten-CSS fuer aktive Token-Hinterlegung
- fokussierte Research-Session-Tests
- aktive Player-Spec unter `docs/spec/`

## Wichtige Entscheidungen

- Die Erweiterung bleibt strikt im bestehenden Unified Player; es wurde keine zweite text-spezifische Player-Architektur eingefuehrt.
- Token-Hervorhebung ist rein additiv zur bestehenden Item-Hervorhebung und ersetzt diese nicht.
- Token-Logik wird nur aktiviert, wenn gueltige Token-Timings im produktiven `alignment/text.json` vorliegen; fehlende oder ungueltige Token degraden sauber auf Satz-only-Rendering.
- Die standalone `comparison`-Seite bleibt vorerst unveraendert. Ihr aktueller Matrix- und Clip-Renderpfad rendert Material global pro Matrixzelle und nicht als pro Session persistent dargestellte Textflaeche mit derselben Vollaudio-Sync-Logik wie der Player.

## Abweichungen

- Keine Abweichung von der aktiven Player-Architektur.
- Die Comparison-Seite wurde bewusst nicht in denselben Token-Sync-Pfad gezogen; das ist ein offener Folgepunkt und keine stillschweigende Teilmigration.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "player_route or authenticated_research_workbench_pages_render_after_access_gate"`
- `Run research sessions tests`-Task: `145 passed`
- Live-Validierung gegen frische App-Instanz auf `http://127.0.0.1:8010`
- bestaetigt fuer reale Routen:
  - `text`-Player mit Token-Spans auf English-Route
  - `text`-Player in `sentence_list` ebenfalls mit Token-Spans
  - `wordlist` bleibt ohne Token-Markup
  - Player-Compare-Route rendert ebenfalls Token-Spans innerhalb der bestehenden Item-Struktur
- bestaetigt, dass der bereits laufende alte Dev-Prozess auf Port `8000` noch stale HTML ohne neue Token-Spans auslieferte; die frische 8010-Instanz zeigte den aktuellen Stand korrekt.

## Offene Punkte

- Im aktuellen Runtime-Datenstand existiert keine reale `text`-Session ohne Token-Timings; der Fallback wird daher derzeit ueber Tests statt ueber eine Live-Route abgesichert.
- Fuer die standalone `comparison`-Seite waere eine gesonderte Entscheidung noetig, ob sie spaeter eine eigene per-Session Textflaeche mit kompatibler Sync-Architektur erhalten soll.

## Nächste sinnvolle Schritte

- Den laufenden lokalen Dev-Prozess auf Port `8000` neu starten, damit die aktuelle Player-Implementierung auch dort sichtbar ist.
- Falls Token-Sync spaeter in die standalone `comparison`-Seite soll, zuerst deren globale Matrix-Darstellung gegen eine pro Session gerenderte Textflaeche und gemeinsame Vollaudio-Sync-Primitiven ausrichten.