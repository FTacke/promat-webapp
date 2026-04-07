# Wordlist Compare Default and Toolbar Cleanup

Datum: 2026-04-07

## Ziel

Den bestehenden produktiven `wordlist`-Compare-Modus funktional und layoutseitig auf den finalen Arbeitszustand bringen: Compare soll bei gültiger Vergleichssession standardmäßig als `A→B je Item` starten, die Toolbar in zwei klare Reihen verdichten, den separaten Fokus-Umschalter entfernen und auf Desktop sofort die gefüllte Vergleichsliste zeigen.

## Consulted Sources

- `AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/agent-runs/2026-04-06_research-player-wordlist-compare-layout-31.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/templates/partials/_research_speaker_card.html`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/js/pages/research-player.js`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_research_sessions.py`
- `docs/spec/research-player.md`

## Wichtige Entscheidungen

- Eine gewählte, gültige `compare_session` startet produktiv standardmäßig im sequenziellen Compare-Modus `A→B je Item`; `Einzeln` und `A/B manuell` bleiben bewusst alternative Arbeitszustände.
- Der separate `Primär`-/`Vergleich`-Fokus-Umschalter wurde entfernt; in `A/B manuell` definiert der zuletzt gewählte Eintrag die aktive Seite für die globale Transportsteuerung.
- Die Control-Bar ist auf zwei Reihen reduziert: Sessionwahl plus Modus oben, Transport plus Seek/Lautstärke/Geschwindigkeit darunter.
- Die Session-Selects zeigen nur noch kompakte `session_id`-Werte, damit die Modusgruppe auf Desktop stabil in derselben Reihe bleibt.
- Compare bleibt strikt desktop-only; schmale Viewports fallen ehrlich auf die Primäransicht zurück, ohne leere oder halbfertige Compare-Flächen zu zeigen.

## Abweichungen

- Keine Abweichung von Routing, Runtime-Grenzen oder Dokumentations-Governance.

## Verifikation

- Problems-Check für die geänderten Python-, Template-, CSS- und JS-Dateien ausgeführt.
- `pytest app/tests/test_research_sessions.py`
- Live-HTML gegen den lokalen Dev-Server geprüft: Default bei `compare_session` ist jetzt `data-player-mode="sequence"`, die Labels lauten `Einzeln`, `A/B manuell`, `A→B je Item`, und `data-player-activate-speaker` ist nicht mehr vorhanden.
- Lokale Headless-Screenshots gegen den frisch mit Workspace-Venv gestarteten Dev-Server ausgewertet:
  - `tmp/ui-qa/player-compare-pass6/desktop-sequence.png`
  - `tmp/ui-qa/player-compare-pass6/mobile-fallback.png`

## Offene Punkte

- Keine akuten offenen Punkte; weitere Feintypografie wäre optionales Polishing, nicht Teil des funktionalen Ziels.

## Nächste sinnvolle Schritte

- Den späteren `text`-Compare nur dann an diese Wortlisten-Logik angleichen, wenn dessen Satz- oder Segmentstruktur dieselbe kompakte Zweispalten-Sprache tatsächlich trägt.