# Wordlist Player Compare Cleanup

Datum: 2026-04-07

## Ziel

Den bestehenden produktiven `wordlist`-Player-Compare-Zustand strukturell bereinigen: kein halb geöffneter Compare-Startzustand mehr, ruhiger zweizeiliger Wiedergabebereich, klare Karten-Grid-Kopplung und reduzierte Compare-Logik mit manuellem Grundzustand plus optionalem A→B-Toggle.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/agent-runs/2026-04-07_research-player-wordlist-compare-repair-33.md`
- `docs/agent-runs/2026-04-07_research-player-wordlist-card-ia-34.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/templates/partials/_research_speaker_card.html`

## Geänderte Bereiche

- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`
- `docs/spec/research-player.md`
- `docs/spec/platform-data-files.md`

## Wichtige Entscheidungen

- Der Single-Startzustand rendert weiter eine versteckte sekundäre Placeholder-Karte im DOM, damit `Vergleich hinzufügen` den Compare-Zustand ohne Vollreload öffnen kann; sichtbar bleibt im Startzustand aber ausschließlich die Primärkarte mit Wortliste.
- Ein gültiger Compare-Zustand hat keinen separaten Modusblock mehr: manueller Vergleich ist der Grundzustand, und `Beide nacheinander` ist die einzige zuschaltbare Playback-Option.
- Das Kartenband schaltet jetzt sauber zwischen voller Einzelbreite und einem echten Zweier-Grid um; die Compare-Liste folgt derselben Zweispaltenlogik, indem die Nummerierung in die linke Vergleichszelle integriert wird.
- Die Wiedergabezone ist in Transportzeile und Einstellungszeile getrennt; Geschwindigkeit ist als kompakter Stufenregler umgesetzt, Lautstärke bleibt eigener Slider.
- Im Player-Surface wird `hidden` explizit mit `display: none !important` abgesichert, weil die Kartenklassen sonst den Browser-Default überschreiben und versteckte Compare-Placeholder sichtbar werden konnten.

## Abweichungen

- Keine Abweichung von der aktiven Spezifikation nach diesem Run; die Spezifikation wurde im selben Run auf den verifizierten Zustand nachgezogen.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py` → `31 passed`
- Problems-Check für `research_views.py`, `research_player.html`, `research-player.js`, `20_layout.css`, `30_components.css`, `40_cards.css` und `test_research_sessions.py` → keine Fehler
- Gerenderter Flask-Test-Client mit realen Dev-Daten bestätigt:
  - Single-Zustand: versteckte Sekundärkarte, sichtbare Aktion `Vergleich hinzufügen`, kein Sequenz-Toggle, kein Modusblock
  - Compare-Zustand mit gültiger Vergleichssession: `data-player-mode="manual"`, Sequenz-Toggle sichtbar, alter Modusblock nicht mehr vorhanden, Compare-Kartenband weiter als `is-compare-ready`
- Live-Server nach explizitem Neustart gegen den aktuellen Workspace-Code geprüft:
  - Der vorher sichtbare leere Compare-Container im Startzustand kam aus einer Kombination von stale Dev-Server und durch Autoren-CSS überschriebenem `hidden`
  - Single-Live-Screenshot bestätigt nur Primärkarte plus Playback-Zone plus Wortliste: `tmp/ui-qa/player-compare-cleanup-35/single-live.png`
  - Compare-Live-Screenshot bestätigt zwei gleich breite Karten, manuellen Grundzustand und sichtbaren Toggle `Beide nacheinander`: `tmp/ui-qa/player-compare-cleanup-35/compare-live.png`

## Offene Punkte

- Keine offene funktionale Baustelle im produktiven `wordlist`-Compare-Fluss aus diesem Run.

## Nächste sinnvolle Schritte

- Optional nur noch visuelle Feinjustierung nach Screenshot- oder Live-Review, falls konkrete Raster- oder Abstandsprobleme auf einer Zielbreite auffallen.
