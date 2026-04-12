# Research Player Cleanup 93

Datum: 2026-04-12

## Ziel

Die noch offenen sichtbaren und funktionalen Restpunkte des produktiven Unified Players gezielt nachziehen: neutraler Player-Kopf statt task-zentriertem Seitenkopf, verlässlicher Compare-Einstieg, sichtbare und funktionale Set-Auswahl im Materialbalken, konsistente Player-Label-Nutzung sowie Bereinigung der Standard-Dev-Runtime auf `127.0.0.1:8000`.

## Consulted Sources

- `docs/spec/research-player.md`
- `docs/spec/platform-data-files.md`
- `docs/runbooks/ui-change-workflow.md`
- `docs/agent-runs/2026-04-11_unified-player-normalization-run-91.md`
- `docs/agent-runs/2026-04-12_research-player-ui-92.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`
- Repo-Memory: `promat-dev-setup-notes`, `promat-shell-notes`, `promat-research-ui-notes`

## Geänderte Bereiche

- Player-Page-Head und Compare-/Task-Labeling in `app/src/app/research_views.py`
- Zentrale Player-Labels in `app/src/app/i18n.py`
- Dokumenttitel-Formatierung in `app/src/app/branding.py`
- Player-Template-Materialbar in `app/templates/pages/research_player.html`
- Compare-/Card-Scope-Fix in `app/static/js/pages/research-player.js`
- Zielgerichtete Player-Regressionen in `app/tests/test_research_sessions.py`
- Wiederverwendbarer QA-Capture über Env-Overrides in `tmp/ui-qa/2026-04-12-research-player-ui-92/capture_player_ui.py`
- Finale QA-Artefakte unter `tmp/ui-qa/2026-04-12-research-player-cleanup-93/`

## Wichtige Entscheidungen

- Der produktive Player-Kopf bleibt neutral `Player`; der aktive Task bleibt in Summary, Materialbar und Itembereich sichtbar, nicht im Seiten-H1.
- Die Footer-Aktion für den Einstieg in den bounded direct compare bleibt ein explizites `Vergleich hinzufügen` beziehungsweise `Add comparison`, statt als generischer Seitenlink oder stiller Moduswechsel zu wirken.
- Player-eigene sichtbare Labels sollen aus dem Player-Katalog kommen; `Aufgabe` im Player wird deshalb nicht länger aus dem Comparison-Katalog gezogen.
- Die Runtime-Abweichung auf `8000` war kein Quellstandsproblem mehr, sondern eine Mehrfach-Prozesslage mit mehreren parallelen `src.app.main`- und QA-Server-Prozessen. Maßgeblich behoben wurde das erst nach vollständigem Entfernen aller konkurrierenden Python-Listener und einem sauberen Neustart über `scripts/dev-start.ps1`.

## Abweichungen

- Keine Abweichung von der aktiven Player-Spec.
- Der vorhandene QA-Capture-Skriptpfad unter `tmp/ui-qa/2026-04-12-research-player-ui-92/` wurde minimal verallgemeinert, damit der Abschlusslauf ohne einen weiteren Einmalskript-Fork in ein neues Ausgabeverzeichnis schreiben konnte.
- Die einzigen Browser-Log-Warnungen im Abschlusslauf betrafen Edge-Tracking-Prevention für die externe Bootstrap-Icons-CSS auf der Login-Seite; keine Player-spezifischen JS-Fehler im Lauf.

## Verifikation

- Editor-Fehlerprüfung für alle geänderten Python-, JS-, Template- und Testdateien: keine Fehler.
- Pytest:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_sessions.py tests/test_research_player_set_context.py`
  - Ergebnis: `61 passed`
- Laufzeitdiagnose auf `8000`:
  - initialer Listener war ein globaler `python.exe -B -m src.app.main` aus `AppData`
  - HTML auf `8000` renderte noch `Wortliste` als H1 und ohne neue Materialbar-Elemente
  - mehrere parallele `src.app.main`- und `run_local_server.py`-Prozesse wurden identifiziert und beendet
  - danach sauberer Neustart über `scripts/dev-start.ps1`
  - finaler Live-Check auf `8000` bestätigt `Player · Pronunciation Matters`, `H1 Player`, Task-Label und Set-Select im HTML
- Browser-QA via Selenium/Edge gegen reale `8000`-Routen in `de` und `en` erneut ausgeführt:
  - `comparison_de_auth.png`, `comparison_en_auth.png`
  - `player_wordlist_de.png`, `player_wordlist_en.png`
  - `player_compare_de.png`, `player_compare_en.png`
  - `player_set_wordlist_de.png`, `player_set_wordlist_en.png`
  - `player_set_text_de.png`, `player_set_text_en.png`
  - `player_empty_wordlist_de.png`, `player_empty_wordlist_en.png`
  - `player_text_only_de.png`, `player_text_only_en.png`
  - `speaker_profile_de.png`, `speaker_profile_en.png`
- Zusätzliche Interaktionsprüfung per Selenium-Snippet gegen `8000`:
  - Klick auf `Vergleich hinzufügen` setzt `data-player-compare-open=true` und blendet die Sekundärkarte ein
  - Set-Wechsel über `Set wählen` navigiert auf die gewählte `set_id` und rendert den erwarteten expliziten Leerzustand
- Textdump-Suche in `tmp/ui-qa/2026-04-12-research-player-cleanup-93/` bestätigt keine sichtbaren Translation-Keys oder rohen `set_id`-Marker in den finalen QA-Artefakten.

## Offene Punkte

- Der globale Python-Basisprozessname kann in der Windows-Prozessliste trotz `venv`-Start irreführend wirken; entscheidend für künftige Diagnosen bleibt die Kombination aus exklusivem Listener-Zustand und Live-HTML-Prüfung auf `8000`.
- Die QA-Drafts `QA Player Cleanup 93 Draft Mix` und `QA Player Cleanup 93 Text Only` wurden für den Abschlusslauf neu angelegt und im Artefaktordner dokumentiert; spätere Läufe sollten wieder eigene QA-Labels verwenden.

## Nächste sinnvolle Schritte

- Den wiederverwendbaren QA-Capture bei der nächsten substanziellen Player-Änderung erneut direkt gegen `8000` laufen lassen, statt wieder auf einen Nebenserver auszuweichen.
- Falls weitere Shell- oder Player-Diagnosen auf Windows nötig werden, immer zuerst konkurrierende `src.app.main`-Listener und alte QA-Server räumen, bevor HTML-Differenzen als Quellcodeproblem interpretiert werden.