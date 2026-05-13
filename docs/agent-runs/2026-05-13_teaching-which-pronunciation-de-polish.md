# Teaching Which-Pronunciation DE Polish

Datum: 2026-05-13

## Ziel

Die deutsche Themenseite `which-pronunciation` visuell und strukturell überarbeiten: serifenlose Lesetypografie für die Topic-Route, klarere Rücknavigation, Entfernung des redundanten unteren Hub-Blocks, ruhigerer Citation-Kasten und ein eigenständiger didaktischer Abschluss statt grüner Hinweisbox.

## Consulted Sources

- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `docs/runbooks/ui-change-workflow.md`
- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
- `app/src/app/teaching_content.py`
- `app/templates/pages/teaching_page.html`
- `app/templates/partials/_teaching_blocks.html`
- `app/templates/partials/_admonition.html`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/src/app/i18n.py`
- `app/tests/test_teaching_content.py`
- `app/tests/test_research_sessions.py`

## Geänderte Bereiche

- `content/teaching/spanish/de/topics/which-pronunciation.yaml`
- `app/src/app/teaching_content.py`
- `app/templates/pages/teaching_page.html`
- `app/templates/partials/_teaching_blocks.html`
- `app/src/app/i18n.py`
- `app/static/css/30_components.css`
- `app/static/css/40_cards.css`
- `app/tests/test_research_sessions.py`

## Wichtige Entscheidungen

- Der Topic-Backlink nutzt nun einen expliziten, nicht hub-titelspezifischen Text (`← Zurück zur Themenübersicht`) und wird auf Topic-Seiten oben und unten gerendert.
- Die Unterrichtsimpulse bleiben content-getrieben, aber nicht mehr als `tip_box`; stattdessen rendert die Seite einen normalen `section_heading` plus `rich_text` mit neuer Variant-Markierung `didactic_close`.
- Die Citation-Überarbeitung bleibt in der bestehenden shared-admonition-Familie, statt einen separaten Spezialkasten einzuführen.
- Die serifenlose Typografie wurde auf die Teaching-Topic-Route gezielt gescopt, damit keine unnötige globale Reading-Typografie umgestellt wird.

## Abweichungen

- Keine Spezifikationsänderung nötig; die Arbeit betrifft Layout-, Typografie- und Inhaltskomposition auf einer bestehenden Teaching-Seite.
- Die englische Topic-Datei wurde auf Wunsch bewusst nicht inhaltlich angepasst; die shared UI-Verbesserungen wirken trotzdem auf beide Sprachen.

## Verifikation

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q -k "groups_blocks_into_sections or keeps_only_existing_next_topics or derives_metadata_and_appends_top_level_citation"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_topic_renders_public_content_blocks or teaching_pilot_topic_renders_canonical_two_column_storytelling"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "sample_page_localizes_admonitions_in_english or sample_page_places_admonitions_before_pattern_lab_with_visible_titles"`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k "teaching_pilot_topic_renders_canonical_two_column_storytelling"`
- Browser-QA in der integrierten Browser-Session auf `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation`
- Live geprüft: oberer und unterer Rücklink, didaktischer Abschlussblock, serifenlose Textwirkung, Citation-Kasten mit vergrößerten Quote-/Copy-Icons

## Offene Punkte

- Die englische Inhaltsfassung von `which-pronunciation` ist noch nicht auf die neue deutsche Struktur nachgezogen.
- Die shared citation/admonition family nutzt an anderen Stellen weiterhin bestehende globale Tokens; dieses Run-Polish ändert nur die citation-spezifische Darstellung und die topic-spezifische Typografie.

## Nächste sinnvolle Schritte

- Die englische Topic-Datei inhaltlich an die neue deutsche Abschlussstruktur und Navigationslogik angleichen.
- Optional einen kleinen Screenshot-basierten QA-Helfer unter `tmp/ui-qa/` ergänzen, falls dieselbe Teaching-Route weiter iteriert wird.