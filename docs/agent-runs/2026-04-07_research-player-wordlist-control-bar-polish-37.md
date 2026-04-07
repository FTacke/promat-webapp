# Wordlist Player Control-Bar Polish

Datum: 2026-04-07

## Ziel

Den bestehenden produktiven `wordlist`-Player visuell nachschärfen, ohne die aktuelle Funktionslogik umzubauen: den globalen Wiedergabe-Container als kompakte Zwei-Block-Struktur lesbarer machen, die deaktivierte Compare-Umschaltung klarer zeichnen, `pm-card`-Hover-Zustände entfernen und die vertikale Rhythmik der Wortlistenzeilen stabilisieren.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/research-player.md`
- `app/templates/pages/research_player.html`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/static/js/pages/research-player.js`
- `app/tests/test_research_sessions.py`
- `app/scripts/dev-start.ps1`

## Geänderte Bereiche

- `app/templates/pages/research_player.html`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`

## Wichtige Entscheidungen

- Der globale Wiedergabebereich bleibt funktional unverändert, wird auf Desktop aber als echte Zwei-Block-Struktur gelesen: links Transport, rechts Einstellungen.
- Die Zeitanzeige sitzt im Transportblock oberhalb der Seekbar, damit die Leiste nicht mehr durch einen seitlichen Zeit-Cluster fragmentiert wird.
- Lautstärke und Geschwindigkeit bleiben zwei gleichwertige Einstellungsfelder mit derselben visuellen Breite; der kompakte Geschwindigkeits-Pill bleibt erhalten.
- Der Compare-Toggle behält seine aktuelle Position im Listenkopf, bekommt aber einen klareren Off-State statt eines zu stark ausgegrauten Schalters.
- `pm-card`-Hover-States werden entfernt, damit die Speaker- und Player-Karten im Arbeitsmodus ruhiger bleiben.

## Abweichungen

- Keine Abweichung von aktiven Routing-, Runtime- oder Datenraumregeln.
- Keine zusätzliche Spezifikationsänderung war nötig; der Run bleibt im bereits dokumentierten `wordlist`-Player-Vertrag.

## Verifikation

- VS-Code-Problems-Check für `research_player.html`, `20_layout.css`, `30_components.css`, `40_cards.css` und `test_research_sessions.py` ohne verbleibende Fehler.
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sessions.py -q` aus `app/` → `32 passed`
- Live-HTML gegen den laufenden Dev-Server auf `127.0.0.1:8000` geprüft:
  - Single enthält `pm-player-control-bar__block--transport`, `pm-player-control-bar__block--settings`, `pm-player-transport-main`, `pm-player-list__row--single`
  - Compare enthält zusätzlich `data-player-compare-open="true"`, `data-player-sequence-toggle`, `pm-player-list__row--compare`
- Headless-Edge-Screenshots aus dem laufenden Dev-Server erstellt und visuell geprüft:
  - `tmp/ui-qa/player-control-bar-layout-37/single-live.png`
  - `tmp/ui-qa/player-control-bar-layout-37/compare-live.png`

## Offene Punkte

- Keine funktionale Restbaustelle aus diesem Polishing-Run.
- Weitere Änderungen wären nur noch Feintypografie oder optionales Spacing-Tuning.

## Nächste sinnvolle Schritte

- Falls gewünscht, den mobilen Fallback des Wiedergabebereichs noch einmal separat auf kleinere Breiten screenshot-basiert feinjustieren.