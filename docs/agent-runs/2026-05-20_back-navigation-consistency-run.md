# Webapp-weiter Zurueck-Navigation-Konsistenz-Run

Datum: 2026-05-20

## Ziel

Back-Navigation ueber Teaching, Research, Auth, Protected Account und Sample auf ein gemeinsames Pattern bringen: gleicher Shared-Pfad, gleiche Position oberhalb von Breadcrumb und Seitentitel, gleiche kompakte Komponente und zielorientierte Labels ohne `Zurueck` oder `Back to`.

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `.github/instructions/repo.instructions.md`
- `app/src/app/content_navigation.py`
- `app/src/app/routes/public.py`
- `app/src/app/routes/auth.py`
- `app/src/app/research_views.py`
- `app/src/app/teaching_content.py`

## Geaenderte Bereiche

- Shared content-header/back-link pipeline in `app/src/app/content_navigation.py` und `app/templates/partials/_content_header.html`
- Research-, Teaching- und Auth-Builder/Routes fuer zentrale `back_link`-Daten
- Shared CSS in `app/static/css/00_tokens.css`, `app/static/css/20_layout.css`, `app/static/css/30_components.css`
- Teaching-, Research-, Auth- und Sample-Templates
- i18n-Labels und fokussierte Regressionstests
- aktive Plattform-Spec und Repo-Instructions

## Wichtige Entscheidungen

- Page-level Back-Navigation wird ueber `content_header.back_link` zentralisiert, damit Position und Komponente nicht mehr pro Seite auseinanderlaufen.
- Der sichtbare Text der Back-Navigation benennt nur das Ziel; der Rueckpfeil kommt aus der gemeinsamen Nav-Pill-Komponente.
- Topic-/Profile-Seiten duerfen eine zweite Back-Navigation am Seitenende behalten, aber nur als Wiederverwendung derselben kompakten Komponente.

## Abweichungen

- Keine fachliche Abweichung von der aktiven Spezifikation.
- Fuer generische Browser-History-Aktionen auf Error-Seiten blieb die generische `Back`-Semantik bestehen; die zielgebundenen Home-Aktionen wurden jedoch auf target-only Labels reduziert.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "profile_page_uses_profile_wording_and_structured_exposure or player_page_maps_legacy_recordings_source_back_to_speakers_table or player_page_exposes_english_labels_for_migrated_wordlist_surface"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py app/tests/test_teaching_content.py -q -k "teaching_topic_renders_public_content_blocks or teaching_pilot_topic_renders_canonical_two_column_storytelling or teaching_english_topic_uses_natural_hub_backlink or research_workbench_routes_render_english_shared_aria_and_actions or player_route_renders_wordlist_runtime_and_profile_back_link or build_teaching_hub_page_groups_topics_and_sets_back_link"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_auth_phase1.py app/tests/test_research_sessions.py -q -k "password_forgot_page_uses_user_facing_copy_in_english or password_reset_page_uses_user_facing_invalid_link_copy or sample_page_exposes_semantic_interaction_preview_without_global_migration or sample_page_localizes_pm_pattern_lab_in_english"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_auth_phase1.py -q -k "account_password_page_uses_header_back_link_to_account or password_forgot_page_uses_user_facing_copy_in_english or password_reset_page_uses_user_facing_invalid_link_copy"`
- `get_errors` fuer geaenderte Auth-Header-Dateien ohne Befunde
- Browser-QA gegen lokalen Flask-Lauf auf `http://127.0.0.1:8010` mit Screenshots fuer representative Surfaces:
	- Research Design ` /en/research/spanish/design`: `← Corpus selection` oberhalb von Breadcrumb und H1, linksbuendig im Content-Container.
	- Auth Password Forgot `/auth/password/forgot?ui_lang=en`: `← Login` oberhalb von Breadcrumb und H1, gleiche Shared-Komponente wie auf oeffentlichen Seiten.
	- Teaching Topic `/de/teaching/spanish/final-r`: oberer und unterer Rueck-Link beide als dieselbe kompakte Nav-Pill, kein Full-Width-Back-Bar-Verhalten.
	- Desktop- und Mobile-Artefakte liegen unter `tmp/ui-qa/2026-05-20-back-navigation-consistency/`.

## Offene Punkte

- Keine funktionalen Restpunkte fuer den vereinheitlichten Page-Level-Back-Link-Run.
- Falls spaeter auch generische Error-Surface-History-Aktionen vereinheitlicht werden sollen, braucht das eine eigene Produktentscheidung statt eines stillen Mitziehens in diesem Run.

## Naechste sinnvolle Schritte

- Optional die Error-Surface-History-Aktion spaeter in eine explizite Produktentscheidung ueberfuehren, falls auch generische Browser-Back-Aktionen systemisch vereinheitlicht werden sollen.