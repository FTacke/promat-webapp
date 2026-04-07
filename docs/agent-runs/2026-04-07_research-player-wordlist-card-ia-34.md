# Wordlist Player Card-First Information Architecture

Datum: 2026-04-07

## Ziel

Den bestehenden produktiven `wordlist`-Player strukturell umbauen, ohne eine zweite Player-Familie einzuführen: Sessionwahl in die Metadatenkarten verlagern, Compare als bewusst aktivierten Zustand modellieren und die Wiedergabezone auf echte Playback- und Compare-Steuerung reduzieren.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-player.md`
- `docs/agent-runs/2026-04-06_research-player-wordlist-mvp-28.md`
- `docs/agent-runs/2026-04-06_research-player-wordlist-compare-layout-31.md`
- `docs/agent-runs/2026-04-07_research-player-wordlist-compare-default-32.md`
- `docs/agent-runs/2026-04-07_research-player-wordlist-compare-repair-33.md`
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

## Umbau

- Die Sessionwahl wurde aus der oberen Wiedergabezone entfernt und in die Kartenidentität verlagert: Die sichtbare `session_id` im Kartenkopf ist jetzt der Session-Switcher mit Dropdown-Menü.
- Der Single-Zustand startet mit nur einer sichtbaren Primärkarte. Wenn weitere produktive `wordlist`-Sessions verfügbar sind, erscheint dort die sekundäre Aktion `Vergleich hinzufügen`.
- Compare ist kein dauerhaft offenes Formular mehr. Erst nach expliziter Aktivierung wird die zweite Vergleichskarte sichtbar.
- Ohne gewählte Vergleichssession zeigt die zweite Karte einen ehrlichen Auswahlzustand `Vergleichssession wählen` statt einer permanenten Toolbar-Selectbox.
- Mit gültiger `compare_session` stehen Primär- und Vergleichskarte als gleichbereite Karten direkt über den beiden Wortlisten-Spalten.
- Die Wiedergabezone liegt jetzt unter den Karten und enthält nur noch Modus, Play oder Pause, Zeit, Seekbar, Lautstärke und direkte Geschwindigkeitswahl.

## Erhaltene Funktionalität

- Gemeinsamer produktiver `wordlist`-Player auf derselben kanonischen Route
- Sessionwechsel
- Compare
- `Einzeln`
- `A/B manuell`
- `A→B je Item`
- Split-Download
- clientseitiger Moduswechsel ohne Vollreload
- ehrliche Fallback-Zustände bei fehlenden Artefakten
- Desktop-only Compare mit sauberem Single-Fallback auf schmalen Breiten

## Wichtige Entscheidungen

- Der Umbau ändert nur die Informationsarchitektur der Oberfläche, nicht die Grundarchitektur des gemeinsamen Players.
- Compare-Aktivierung und Compare-Deaktivierung werden im bereits geladenen Surface leichtgewichtig im Client-State behandelt; Sessionwechsel selbst bleibt ein normaler Seitenwechsel, weil neue Session-Daten geladen werden müssen.
- Die Karten bleiben technisch Teil derselben Familie wie die Speaker-Cards, erhalten aber playergerechte Breiten und einen card-internen Session-Switcher.
- Die Compare-Liste bleibt die gemeinsame, ausgerichtete Zwei-Spalten-Liste; die Karten definieren jetzt sichtbarer die linke und rechte Sprecherstruktur darüber.

## Verifikation

- `Set-Location c:/dev/promat; c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py` → `31 passed`
- Gerenderter Flask-Test-Client mit realen Dev-Daten bestätigt:
  - Single ohne `compare_session`: `Vergleich hinzufügen`, `data-player-compare-open="false"`, beide Session-Menüs im Kartenbereich
  - Compare mit gültiger `compare_session`: `Vergleich entfernen`, `data-player-compare-open="true"`, Mode-Gruppe und Compare-Panel vorhanden
- Live-HTML gegen den lokal gestarteten Flask-Dev-Server bestätigt dieselben Marker.
- Aktueller Desktop-Screenshot des umgebauten Compare-Zustands:
  - `tmp/ui-qa/player-card-ia-pass8/desktop-compare.png`

## Abweichungen

- Der lokale Dev-Server musste für die Live-Prüfung explizit neu gestartet werden; davor antwortete Port `8000` nicht zuverlässig mit dem aktuellen Workspace-Zustand.
- Kein Ausbau von `text` oder `interview` in diesem Run.

## Offene Punkte

- Keine neue funktionale Baustelle im `wordlist`-Player. Mögliche weitere Schritte wären nur visuelle Feingewichtung einzelner Card- und Toolbar-Abstände.
