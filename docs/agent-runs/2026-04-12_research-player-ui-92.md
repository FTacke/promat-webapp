# Research Player UI 92

Datum: 2026-04-12

## Ziel

Die besprochenen UI-Anpassungen am produktiven Research Player gemäß aktiver Spec umsetzen, die Set-, Task- und View-Logik sichtbar sauber trennen, explizite Empty States im Player erhalten und die fertige Oberfläche bilingual im Browser mit Screenshots abnehmen.

## Consulted Sources

- `docs/spec/research-player.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `docs/runbooks/ui-change-workflow.md`
- `docs/agent-runs/2026-04-11_bilingual-ui-acceptance-run-90.md`
- `docs/agent-runs/2026-04-11_unified-player-normalization-run-91.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- Produktive Player-Logik in `app/src/app/research_views.py`
- Produktive Player-Template-Struktur in `app/templates/pages/research_player.html`
- Player-Interaktion in `app/static/js/pages/research-player.js`
- Shared Player-Layouts und Komponenten in `app/static/css/20_layout.css` und `app/static/css/30_components.css`
- Set-Kontext- und Session-Regressionen in `app/tests/test_research_player_set_context.py` und `app/tests/test_research_sessions.py`
- Aktive Player-Regeln in `docs/spec/research-player.md`
- Browser-QA-Artefakte und wiederholbare Hilfsskripte unter `tmp/ui-qa/2026-04-12-research-player-ui-92/`

## Wichtige Entscheidungen

- Die Player-Metadatenkarten bleiben die primäre Session-Identität; Taskwechsel und Set-Auswahl sitzen darunter in einer kompakten Materialleiste statt in konkurrierenden Header- oder Toolbar-Strukturen.
- Set-, Task- und View-Zustand bleiben strikt getrennt: `set_id` filtert nur den sichtbaren Task-Ausschnitt, der Taskwechsel bleibt ein eigener Schalter, und ein View-Switch erscheint nur bei echten textfähigen Quellen.
- Leere taskgebundene Set-Ausschnitte rendern weiterhin die volle Player-Hülle mit Metadaten, Materialleiste und explizitem Leerzustand statt auf einen Voll-Session-Fallback oder einen irreführenden Unavailable-Shell zurückzufallen.
- Profilzugriffe gehören in die Footer-Aktionszeile jeder Metadatenkarte; die obere Kartenkante behält nur die knappe Rollenkennzeichnung.
- Für die Abschluss-QA wurde ein isolierter lokaler Server auf `127.0.0.1:8001` als maßgebliche Browser-Referenz genutzt, nachdem die laufende Instanz auf `127.0.0.1:8000` trotz aktuellem Workspace-Stand bei Übersetzungs- und Empty-State-Verhalten abwich.

## Abweichungen

- Keine Abweichung von der aktiven Spec für Player-Architektur oder UI-Regeln.
- Es gab eine Dev-Runtime-Abweichung: die bereits laufende App auf `127.0.0.1:8000` renderte im Browser noch einen veralteten Task-Label-Key und den älteren Empty-State-Fallback. Die finale Abnahme wurde deshalb auf einer isoliert aus dem aktuellen Workspace gestarteten Instanz auf `127.0.0.1:8001` durchgeführt.
- Temporäre QA-Hilfsskripte und Screenshot-Artefakte liegen ausschließlich unter `tmp/ui-qa/2026-04-12-research-player-ui-92/` und sind nicht normativ.

## Verifikation

- Fokussierte Pytest-Regressionen für Player-Set-Kontext und Player-Surfaces wurden im Run grün ausgeführt.
- Zusätzliche Regression ergänzt: der aktive owner-gebundene Draft muss im Player-Set-Select als aktuelles Set erscheinen, nicht nur die Default-Option `Alle Items`.
- Wiederholbare Selenium/Edge-Browserabnahme mit `capture_player_ui.py` gegen reale Routen in `de` und `en` durchgeführt.
- QA-Sets für diesen Lauf erzeugt und dokumentiert in `tmp/ui-qa/2026-04-12-research-player-ui-92/set_ids.json`.
- Zuerst Browserlauf gegen `127.0.0.1:8000` ausgeführt, sichtbare Runtime-Abweichung identifiziert und anschließend die finale Abnahme auf `127.0.0.1:8001` wiederholt.
- Final valide Screenshot- und Textdump-Artefakte liegen unter `tmp/ui-qa/2026-04-12-research-player-ui-92/`, unter anderem:
  - `comparison_de_auth.png` und `comparison_en_auth.png`
  - `player_wordlist_de.png` und `player_wordlist_en.png`
  - `player_compare_de.png` und `player_compare_en.png`
  - `player_set_wordlist_de.png` und `player_set_wordlist_en.png`
  - `player_set_text_de.png` und `player_set_text_en.png`
  - `player_empty_wordlist_de.png` und `player_empty_wordlist_en.png`
  - `player_text_only_de.png` und `player_text_only_en.png`
  - `speaker_profile_de.png` und `speaker_profile_en.png`
- Finaler Browserzustand auf `8001` bestätigt:
  - Task-Label rendert lokalisiert als `Aufgabe` beziehungsweise `Task`
  - owner-gebundene Sets inklusive Draft erscheinen im Set-Select
  - leere Set-Ausschnitte behalten Summary Cards, Materialleiste und expliziten Leerzustand innerhalb des Players
  - eine unbetroffene Referenzfläche derselben UI-Familie wurde über die Sprecherprofil-Screenshots mitgeprüft

## Offene Punkte

- Die Ursache für die Abweichung der laufenden Instanz auf `127.0.0.1:8000` wurde für diesen Run eingegrenzt, aber nicht dauerhaft bereinigt; maßgeblich abgeschlossen wurde nur die verlässliche Workspace-Instanz auf `8001`.
- Die QA-Hilfsskripte unter `tmp/ui-qa/2026-04-12-research-player-ui-92/` sind für Wiederverwendung nützlich, bleiben aber bewusst außerhalb der aktiven Dokumentation und Produktpfade.

## Nächste sinnvolle Schritte

- Die Ursache der Render-Abweichung auf `127.0.0.1:8000` separat bereinigen, damit der Standard-Dev-Start wieder denselben Stand wie `create_app()` und der isolierte QA-Server rendert.
- Bei der nächsten substantiellen Player-Änderung denselben Selenium-Lauf unter `tmp/ui-qa/` fortschreiben statt neue manuelle Einzelprüfungen zu improvisieren.