# Wordlist Player Click and Global Play Separation

Datum: 2026-04-07

## Ziel

Den bestehenden produktiven `wordlist`-Player gezielt in Verhalten und Layout schärfen: Item-Klick als echte Einzelprüfung, globales Play als globaler Transport, `Beide abspielen` als standardmäßig aktiver Compare-Item-Toggle im Kopf der Vergleichsliste und ein Wiedergabebereich ohne compare-spezifische Hilfstexte oder Zusatzsteuerung.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/agent-runs/2026-04-07_research-player-wordlist-compare-cleanup-35.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-player.md`

## Wichtige Entscheidungen

- Compare bleibt auf derselben kanonischen Player-Route und verwendet jetzt optional `compare_mode=manual`; ohne expliziten Modus startet ein gültiger Compare-Zustand mit standardmäßig aktivem `Beide abspielen`.
- Item-Klick und globales Play sind im Client-Code getrennte Pfade: Item-Klick ruft nur begrenzte Clip-Prüfung auf, globales Play spielt den aktuellen Vollaudio-Kontext ab der aktuellen Position weiter.
- Der Compare-Toggle wurde aus dem globalen Wiedergabebereich entfernt und in den Kopf der Vergleichsliste verschoben, weil er ausschließlich Compare-Item-Verhalten steuert.
- Die globale Wiedergabezone enthält nur noch Play/Pause, Zeit, Seek, Lautstärke und Geschwindigkeit; die bisherigen Modus-Erklärtexte wurden dort entfernt.
- Die zweite Player-Reihe bleibt ruhig und kompakt: Lautstärke und Geschwindigkeitssteuerung haben jetzt ähnlich zurückhaltende visuelle Breite statt eines dominanten Einzel-Sliders.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py` → `32 passed`
- Problems-Check für `research_views.py`, `research_player.html`, `research-player.js`, `20_layout.css`, `30_components.css`, `test_research_sessions.py`, `platform-data-files.md` und `research-player.md` → keine Fehler
- Live-HTML gegen den lokalen Dev-Server geprüft:
  - Single: `data-player-compare-open="false"`, keine Toggle-Markup-Reste, versteckte Sekundärkarte weiterhin vorhanden
  - Compare: `data-player-mode="sequence"`, `data-player-sequence-toggle checked`, Toggle liegt im Compare-Panel statt im globalen Wiedergabebereich
- Instrumentierte Headless-Edge-Prüfung der Browserlogik bestätigt:
  - Single-Item-Klick startet den Primärclip bei ca. `0.497s`, stoppt wieder am Clipende bei ca. `1.177s`, globales Play setzt danach genau dort fort statt wieder bei `0.497s`
  - Compare mit aktivem `Beide abspielen`: Klick auf ein Item startet Primärclip, danach automatisch den zugeordneten Vergleichsclip desselben Items
  - Compare mit deaktiviertem Toggle: Klick rechts startet nur die rechte Seite; globales Play setzt anschließend diesen sekundären Vollkontext an dessen aktueller Position fort
- Frische Live-Screenshots aus dem verifizierten Serverlauf:
  - `tmp/ui-qa/player-click-play-layout-36/single-live.png`
  - `tmp/ui-qa/player-click-play-layout-36/compare-live.png`

## Abweichungen

- Der erste Live-Neustart lieferte trotz korrekter Workspace-Dateien noch alten Compare-Output. Für die verlässliche Live-Prüfung musste der Dev-Server mit explizitem `PYTHONPATH` auf `c:/dev/promat/app` neu gestartet werden, damit `src.app.main` sicher aus dem aktuellen App-Root geladen wurde.

## Offene Punkte

- Keine offene funktionale Baustelle im produktiven `wordlist`-Player aus diesem Run.

## Nächste sinnvolle Schritte

- Optional nur noch visuelle Feingewichtung einzelner Abstände oder Slider-Breiten nach weiterem Screenshot-Review; funktional ist die Trennung von Item-Prüfung und globalem Transport jetzt verifiziert.