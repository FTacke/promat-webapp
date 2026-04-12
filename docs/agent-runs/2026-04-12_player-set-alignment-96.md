# Player Set Alignment 96

Datum: 2026-04-12

## Ziel

Die produktive Player-Set-Auswahl auf dieselbe sichtbare owner-gebundene Set-Liste wie `comparison` und `phenomena` ausrichten, den generischen Player-Container `Set-Kontext` aus dem normalen Erfolgszustand entfernen und die resultierende UI in `de` und `en` mit Screenshots abnehmen.

## Consulted Sources

- `docs/spec/research-player.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `docs/runbooks/ui-change-workflow.md`
- `docs/agent-runs/2026-04-12_research-player-ui-92.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- sichtbare Set-Auswahllogik in `app/src/app/research_sets.py`
- Player- und Comparison-Builder in `app/src/app/research_views.py`
- Phenomena-Overview-Builder in `app/src/app/research_phenomena_views.py`
- owner-gebundene Set-API-Listung in `app/src/app/routes/research_api.py`
- produktives Player-Template in `app/templates/pages/research_player.html`
- Regressionen in `app/tests/test_research_sets.py`
- Regressionen in `app/tests/test_research_player_set_context.py`
- Regressionen in `app/tests/test_research_comparison.py`
- Regressionen in `app/tests/test_research_phenomena.py`
- aktive Player-Spec in `docs/spec/research-player.md`
- Browser-QA-Artefakte unter `tmp/ui-qa/2026-04-12-player-set-alignment-96/`

## Wichtige Entscheidungen

- Die sichtbare owner-gebundene Workbench-Set-Liste wird serverseitig über einen gemeinsamen Selektor vereinheitlicht, statt den Player separat alle Drafts listen zu lassen.
- Sichtbar bleiben standardmäßig nur gespeicherte Custom-Sets; ein aktueller Draft erscheint im Player nur dann zusätzlich, wenn genau dieser Draft bereits aktiv über `set_id` geöffnet wurde.
- Die Default-API-Liste unter `/api/research/sets` folgt jetzt derselben sichtbaren Workbench-Regel; nur der explizite `include_drafts=true`-Pfad liefert weiterhin die vollständige Draft-Liste.
- Der generische Player-Block `Set-Kontext` entfällt im normalen Erfolgszustand vollständig; übrig bleiben nur gezielte Ausnahmehinweise für degradierte Spezialfälle.

## Verifikation

- Fokussierte Pytest-Regressionsläufe ausgeführt:
  - `tests/test_research_sets.py`
  - `tests/test_research_player_set_context.py`
  - `tests/test_research_comparison.py`
  - `tests/test_research_phenomena.py`
  - `tests/test_research_sessions.py`
- Ergebnis: `99 passed`.
- Neue Regressionen bestätigen explizit:
  - Player zeigt dieselbe sichtbare saved-only Workbench-Liste wie Comparison/Phenomena.
  - Unverwandte Drafts bleiben in Player, Comparison und Phenomena unsichtbar.
  - Ein bereits aktiver Draft bleibt im Player-Select als Kontextoption sichtbar.
  - Der normale Player-Erfolgszustand rendert keinen generischen `Set-Kontext`-Block mehr.
- Browser-QA auf isolierter Workspace-Instanz unter `http://127.0.0.1:8001` durchgeführt.
- Geprüfte reale Routen in `de` und `en`:
  - `/de/research/spanish/comparison`
  - `/en/research/spanish/comparison`
  - `/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings`
  - `/en/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings`
  - `/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings&compare_session=ES-L-0001-2027-S02&compare_mode=manual`
  - `/en/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings&compare_session=ES-L-0001-2027-S02&compare_mode=manual`
  - `/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=phenomena&set_id=<draft_set_id>`
  - `/en/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=phenomena&set_id=<draft_set_id>`
  - `/de/research/spanish/player/ES-L-0001-2026-S01/text?source=phenomena&set_id=<draft_set_id>`
  - `/en/research/spanish/player/ES-L-0001-2026-S01/text?source=phenomena&set_id=<draft_set_id>`
  - `/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=comparison&set_id=<text_only_set_id>`
  - `/en/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=comparison&set_id=<text_only_set_id>`
  - `/de/research/spanish/player/ES-L-0001-2026-S01/text?source=comparison&set_id=<text_only_set_id>`
  - `/en/research/spanish/player/ES-L-0001-2026-S01/text?source=comparison&set_id=<text_only_set_id>`
  - `/de/research/spanish/speakers/ES-L-0001?session=ES-L-0001-2026-S01`
  - `/en/research/spanish/speakers/ES-L-0001?session=ES-L-0001-2026-S01`
- Browserbefund:
  - Comparison listet nur kuratierte Presets plus gespeicherte Custom-Sets; der neue QA-Draft blieb dort unsichtbar.
  - Player zeigt bei aktivem Draft denselben gespeicherten Custom-Set-Bestand plus den aktiven Draft als Kontextoption.
  - Der normale Player-Erfolgszustand enthält keinen generischen `Set-Kontext`-Kasten mehr.
  - Der leere Set-Ausschnitt bleibt als expliziter taskbezogener Empty State erhalten.
  - Eine unbetroffene Referenzfläche derselben UI-Familie wurde über die Profilroute mitgeprüft.

## Screenshot-Artefakte

- `comparison_de_auth.png`
- `comparison_en_auth.png`
- `player_wordlist_de.png`
- `player_wordlist_en.png`
- `player_compare_de.png`
- `player_compare_en.png`
- `player_set_wordlist_de.png`
- `player_set_wordlist_en.png`
- `player_set_text_de.png`
- `player_set_text_en.png`
- `player_empty_wordlist_de.png`
- `player_empty_wordlist_en.png`
- `player_text_only_de.png`
- `player_text_only_en.png`
- `speaker_profile_de.png`
- `speaker_profile_en.png`
- `set_ids.json`

## Offene Punkte

- Im Selenium-Lauf trat nur eine bekannte Edge-Warnung zur Tracking-Prevention gegen das externe Bootstrap-Icons-CDN auf; es wurde kein produktspezifischer UI- oder JS-Fehler beobachtet.
- Keine verbleibende funktionale Inkonsistenz zwischen der sichtbaren owner-gebundenen Set-Liste in Player, Comparison und Phenomena festgestellt.