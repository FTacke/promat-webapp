# Unified Player Normalization

Datum: 2026-04-11

## Ziel

Den Research-Player gemäß `docs/plans/player_new.md` intern auf eine gemeinsame, source-gesteuerte Architektur für Wortliste, Satzliste, echte Textquellen und Set-Ausschnitte umstellen, ohne die bestehende Route-Familie zu brechen.

## Consulted Sources

- `docs/plans/player_new.md`
- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/intake-workbook.md`
- `docs/spec/research-player.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/runtime_paths.py`
- `app/src/app/config/__init__.py`
- `docker-compose.dev-postgres.yml`
- `app/infra/docker-compose.prod.yml`

## Geänderte Bereiche

- Normalisierte Source-/Item-Metadaten in `app/src/app/research_presets.py`
- Vereinheitlichte Player-Builder-Logik in `app/src/app/research_views.py`
- Optionaler `render_mode`-Durchstich in `app/src/app/routes/public.py`
- Running-Text-Renderer und View-Switch in `app/templates/pages/research_player.html`
- Ergänzende Player-Styles in `app/static/css/30_components.css`
- Explizite Source-Metadaten in `data/config/research_player/spanish/task_catalogs/wordlist.json` und `data/config/research_player/spanish/task_catalogs/text.json`
- Tests in `app/tests/test_research_presets.py`, `app/tests/test_research_sessions.py`, `app/tests/test_research_player_set_context.py`
- Aktive Spec-Aktualisierung in `docs/spec/research-player.md`
- Statushinweis in `docs/plans/player_new.md`

## Wichtige Entscheidungen

- Der Player normalisiert jetzt jede produktive Anfrage zuerst zu einer expliziten Source-Beschreibung plus einer gemeinsamen Item-Sequenz; Wortliste und `text` teilen damit denselben internen Stack.
- Echte Textquellen werden nicht heuristisch erkannt, sondern nur über explizite `player_source`-Metadaten im Task-Catalog freigeschaltet.
- Set-Kontext erzeugt zur Laufzeit eine eigene Source-Klasse `set`; dadurch bleibt `text` innerhalb eines Set-Ausschnitts bewusst list-only und rekonstruiert keinen Fließtext.
- `render_mode=running_text` ist nur bei echten Textquellen mit passender Source-Metadatenlage aktiv. Bei Set-Ausschnitten und im direkten Vergleich fällt der Player sauber auf `sentence_list` zurück.
- Das alte `player_config.json` bleibt kompatibel erhalten, ist aber nicht mehr die normative Wahrheitsquelle für echte Textfähigkeit.

## Verifikation

- Pytest:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest tests/test_research_presets.py tests/test_research_sessions.py tests/test_research_player_set_context.py`
  - Ergebnis: `70 passed`
- Live-Browser-QA auf laufender Dev-Instanz via Selenium/Edge gegen reale Routen:
  - `http://127.0.0.1:8000/de/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings`
  - `http://127.0.0.1:8000/en/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=recordings`
  - `http://127.0.0.1:8000/de/research/spanish/player/ES-L-0001-2026-S01/text?source=recordings`
  - `http://127.0.0.1:8000/en/research/spanish/player/ES-L-0001-2026-S01/text?source=recordings`
  - `http://127.0.0.1:8000/de/research/spanish/comparison`
- Screenshots abgelegt unter `tmp/ui-qa/2026-04-11-unified-player-run-91/`

## Offene Punkte

- Im ausgelieferten spanischen Korpus gibt es aktuell noch keine produktive, explizit als `connected_text` deklarierte Textquelle. Die neue Running-Text-Ansicht ist deshalb über neue Pytest-Fixtures validiert, nicht über eine live ausgelieferte Korpus-Route.
- Für `interview` bleibt die gemeinsame Normalisierung bewusst außerhalb des Produktpfads; die Route bleibt erhalten, rendert aber weiter den ehrlichen Unavailable-Zustand.