# Player Layout Follow-up 98

Datum: 2026-04-13

## Ziel

Den produktiven Player noch einmal exakt auf die nachgeschärften Layoutvorgaben bringen: Footer-Reihenfolge der Primär- und Vergleichskarten korrigieren, den Compare-Einstieg als `Vergleich` statt `Vergleich hinzufügen` benennen und die Materialleiste als kompakte Ein-Zeilen-Leiste ohne obere Doppelbeschriftung umsetzen.

## Consulted Sources

- `docs/spec/research-player.md`
- `docs/spec/platform-data-files.md`
- `docs/runbooks/ui-change-workflow.md`
- `docs/agent-runs/2026-04-12_player-fix-validation-97.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`
- `app/tests/test_research_player_set_context.py`

## Geänderte Bereiche

- Footer-Aktionsreihenfolge und Compare-Label in `app/src/app/research_views.py` und `app/src/app/i18n.py`
- Kompakte Ein-Zeilen-Materialleiste in `app/templates/pages/research_player.html`
- Geometrie für Inline-Set-Gruppe und Footer-Ausrichtung in `app/static/css/30_components.css` und `app/static/css/40_cards.css`
- Nachgezogene Regressionen in `app/tests/test_research_sessions.py` und `app/tests/test_research_player_set_context.py`
- Aktualisierte Live-QA unter `tmp/ui-qa/2026-04-12-player-fix-97/`

## Wichtige Entscheidungen

- Die Primärkarte ohne aktiven Vergleich rendert nun `Profil →` links und `Vergleich` rechts; die Vergleichskarte rendert `Profil →` links und `Vergleich entfernen` rechts.
- Die rechte Kopfzone bleibt badge-only; ein separates `Vergleich ändern` wurde weiterhin bewusst nicht eingeführt.
- Die Player-Materialleiste bleibt ohne oberen Bereichstitel und ohne zweite Beschriftungsebene: links nur die Task-Chips, rechts eine echte Inline-Gruppe aus `Set wählen`, Info-Hinweis und Select.
- Für die finale Browser-Abnahme war erneut entscheidend, den alten Global-Python-Listener auf `8000` zu entfernen und den Server kanonisch über `./scripts/dev-start.ps1` neu zu starten.

## Abweichungen

- Keine Abweichung von der aktiven Spec; es handelt sich um eine präzisierende Layout-Nachführung innerhalb des bestehenden Player-Solls.
- Die QA-Artefakte bleiben im vorhandenen Ordner `tmp/ui-qa/2026-04-12-player-fix-97/`, weil dieser Lauf direkt auf dem vorherigen Live-QA-Pfad aufsetzt.

## Verifikation

- Editor-Fehlerprüfung der geänderten produktiven Dateien: keine Fehler.
- Fokussierter Pytest-Lauf:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sessions.py tests/test_research_player_set_context.py -q`
  - Ergebnis: `64 passed`
- Stale Python-Listener auf `127.0.0.1:8000` identifiziert und beendet.
- Dev-Server kanonisch über `./scripts/dev-start.ps1` neu gestartet.
- Headless-Edge-Live-QA gegen `127.0.0.1:8000` erfolgreich erneut ausgeführt.
- Bestätigte Ergebnisse laut `metrics.json` und Screenshots:
  - Primärkarte ohne Vergleich: Footer-Reihenfolge `profile`, `compare-add`
  - Vergleichskarte: Footer-Reihenfolge `profile`, `compare-remove`
  - Materialleiste ohne alten Task-Titel und ohne alte Select-Label-Zeile
  - Inline-Label `Set wählen` sitzt neben dem Select in derselben kompakten Steuerzeile
- Relevante Artefakte:
  - `tmp/ui-qa/2026-04-12-player-fix-97/player_de.png`
  - `tmp/ui-qa/2026-04-12-player-fix-97/player_compare_de.png`
  - `tmp/ui-qa/2026-04-12-player-fix-97/metrics.json`

## Offene Punkte

- Keine offene funktionale Abweichung im angefragten Footer- oder Materialleistenbereich festgestellt.
- Die Headless-Edge-GPU-Warnung blieb infrastrukturell und ohne Einfluss auf die UI-Abnahme.

## Nächste sinnvolle Schritte

- Falls weitere Player-Feinjustierung gewünscht ist, als Nächstes nur noch typografische Mikroabstände und Breitenverhalten der Leiste zwischen Desktop und schmalem Tablet gezielt nachziehen.