# Interview Player UI Polish 133

Datum: 2026-04-21

## Ziel

Den bereits produktiven Interview-Renderer innerhalb der bestehenden einheitlichen Research-Player-Architektur visuell nachschärfen: ruhigere Turn-Hierarchie, korrekt inline eingebettete Materialreferenzen und ein kompaktes, webapp-konformes Referenz-Popover ohne neue Player-Zone, neue Routefamilie oder neue Capability-Semantik.

## Consulted Sources

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/repo.instructions.md`
- `app/AGENTS.md`
- `docs/spec/research-player.md`
- `docs/runbooks/ui-change-workflow.md`
- `app/templates/pages/research_player.html`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-player.js`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- `app/templates/pages/research_player.html`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/js/pages/research-player.js`
- `app/tests/test_research_sessions.py`

## Wichtige Entscheidungen

- Die obere gemeinsame Player-Zone blieb unverändert; der Lauf beschränkt sich vollständig auf den Interview-Contentbereich innerhalb der bestehenden Player-Seite.
- `interview` bleibt im bestehenden Capability- und Route-Contract unverändert: kein Compare, kein Set-Filter, keine Sonderroute, kein zweiter Player-Header.
- Die linke Turn-Spalte wurde auf Rollenbadge plus Zeit reduziert; sichtbare `Segment X`-Metazeilen wurden aus dem normalen Rendering entfernt.
- Die Rollenhierarchie wurde visuell umgedreht: `Sprecher:in` beziehungsweise `Speaker` ist auffälliger, `Explorator:in` beziehungsweise `Interviewer` bleibt bewusst ruhiger.
- Die aktive Interview-Hervorhebung konzentriert sich jetzt auf die Textfläche statt den gesamten Turnblock.
- Materialreferenzen werden als echte Inline-Einfügung im Satzfluss gerendert; die frühere Blockzerlegung war ein Root-Cause-Problem durch verschachtelte Interaktion (`button` in `button`) und wurde durch einen nicht-buttonbasierten, zugänglichen Seek-Surface im Interview-Renderer behoben.
- Das Referenz-Overlay wurde von einem MD3-artigen Dialog zu einem kompakten Popover beziehungsweise auf Mobile zu einem kleinen Bottom-Sheet-Ableger umgebaut.
- Der Mini-Player im Popover verwendet jetzt reduzierte, playernahe eigene Controls statt den nativen Browser-Audiocontrols.

## Verifikation

### Tests

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_capabilities.py -q`
- zusätzliche fokussierte Markup-Regressionen in `app/tests/test_research_sessions.py` prüfen unter anderem:
  - keine sichtbare `pm-player-transcript__segment`-Metazeile
  - kein `data-player-reference-close`
  - Inline-Referenzlabel-Markup vorhanden
  - `Im Kontext öffnen` im neuen Tab

### Browser und Screenshots

Headless-Edge-Screenshots gegen den real laufenden Dev-Server unter `http://127.0.0.1:8000` wurden unter `tmp/ui-qa/2026-04-21-interview-player-polish-133/` erzeugt:

- `de-interview-desktop.png`
- `de-interview-popover-desktop.png`
- `en-interview-popover-desktop.png`
- `de-interview-popover-mobile.png`
- `de-wordlist-regression-desktop.png`

Geprüft wurden dabei:

- DE-Interview-Desktop: ruhige Turn-Spalte, keine sichtbare Segmentmetazeile, inline gesetzte Referenz im Satzfluss
- DE-Interview-Desktop mit Popover: kompaktes Referenz-Popover mit Badge, Nummer, Label, Mini-Player und `Im Kontext öffnen`
- EN-Interview-Desktop mit Popover: korrekte englische Rollenlabels und CTA, gleiche Layout-Hierarchie
- DE-Interview-Mobile: kompaktes Bottom-Sheet-artiges Popover statt schwerem Dialog
- DE-Wordlist-Desktop: Gegenprüfung einer unbetroffenen Player-Komponentenfamilie nach Shared-CSS-Änderungen

## Offene Punkte

- Die mobile Kopfzeile zeigt im Screenshot weiterhin die bekannte enge Belegung zwischen Brand und Sprachumschalter; diese liegt außerhalb des Interview-Renderer-Scopes und wurde in diesem Lauf nicht verändert.
- Für das Popover wurde bewusst kein zusätzliches sichtbares Close-X ergänzt, weil Outside-Click, Escape und erneuter Klick auf die Referenz bereits den ruhigeren bestehenden Interaktionsstil erfüllen.
