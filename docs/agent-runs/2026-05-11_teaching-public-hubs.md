# Teaching Public Hubs

## Goal

Reshape the public Teaching area into a teacher-first flow:

- `/{ui_lang}/teaching` becomes a language selection surface
- each language hub exists publicly for `spanish`, `english`, `french`, and `german`
- Spanish keeps grouped topic cards
- empty languages render a quiet empty state instead of a 404
- visible in-body edition pills disappear from Teaching overview, hub, and topic pages

## Changed Files

- `app/src/app/teaching_content.py`
- `app/src/app/routes/public_content.py`
- `app/src/app/i18n.py`
- `app/src/app/routes/public.py`
- `app/templates/pages/teaching_page.html`
- `app/templates/pages/sample_page.html`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_teaching_content.py`
- `app/tests/test_research_sessions.py`
- `content/teaching/spanish/de/index.yaml`
- `content/teaching/spanish/en/index.yaml`
- `content/teaching/english/...`
- `content/teaching/french/...`
- `content/teaching/german/...`
- `docs/spec/platform-data-files.md`
- `docs/agent-runs/2026-05-11_teaching-public-hubs.md`

## What Changed

### Teacher-first overview

- The Teaching root now keeps the shared shell but presents a compact language selection with the exact prompt `Welche Sprache unterrichten Sie?` / `Which language do you teach?`.
- Overview cards no longer use teaser copy from language metadata.
- Status text is now derived from the resolved edition topic count:
  - `4 Themenseiten` on `/de/teaching` for Spanish
  - `1 topic page` on `/en/teaching` for Spanish
  - `Themenseiten im Aufbau` / `Topic pages in progress` for empty hubs

### Public hubs for all four teaching languages

- Added public Teaching manifests and `de` / `en` index files for `english`, `french`, and `german`.
- These hubs now return normal public Teaching pages with a calm empty state instead of missing-route behavior.
- Spanish hub indexes were reworked to expose explicit topic groups while keeping the flat `topics` list for metadata and route resolution.

### Grouped hubs and simplified backlinks

- Teaching hub rendering now supports grouped topic sections via `groups:` in the index YAML.
- Empty groups are ignored automatically.
- Hub pages now show `← Zur Sprachauswahl` / `← Back to language selection` above the content header.
- Topic pages now show `← {hub_title}` above the content header, for example `← Spanisch unterrichten`.
- Topic pages no longer duplicate the hub path through a second breadcrumb-style ancestor row.

### In-body edition switch removed

- `teaching_switch_items` remains available for internal route-aware edition logic and test coverage.
- The visible Teaching-body `Editionen` / `Editions` block is no longer rendered.
- The shared topbar `DE | EN` switch remains the only visible edition switch and still preserves route-aware Teaching targets.

### Sample mirror kept in sync

- The Sample page now renders Teaching selection cards through the same corpus-card macro used on the real Teaching root.
- The Sample teaching mirror now consumes grouped Teaching hub data instead of the removed flat `feature_cards` payload.

## Validation

### Focused tests

- `pytest app/tests/test_teaching_content.py -q` -> `9 passed`
- `pytest app/tests/test_research_sessions.py -q -k teaching` -> `13 passed, 183 deselected`
- `pytest app/tests/test_research_sessions.py -q -k sample_page_uses_shared_inner_shell_renderer` -> `1 passed`
- `get_errors` on changed Python, Jinja, and test files -> no errors

### Browser QA

Headless Edge screenshots were captured because the integrated browser tool path failed with `browserContext.newPage: Cannot read properties of undefined (reading '_page')`.

Artifacts were written to:

- `tmp/ui-qa/2026-05-11-teaching-hubs/teaching-root-de.png`
- `tmp/ui-qa/2026-05-11-teaching-hubs/teaching-hub-spanish-de.png`
- `tmp/ui-qa/2026-05-11-teaching-hubs/teaching-hub-english-de.png`
- `tmp/ui-qa/2026-05-11-teaching-hubs/teaching-topic-final-r-de.png`
- `tmp/ui-qa/2026-05-11-teaching-hubs/teaching-root-en.png`
- `tmp/ui-qa/2026-05-11-teaching-hubs/teaching-hub-spanish-en.png`
- `tmp/ui-qa/2026-05-11-teaching-hubs/sample-de.png`
- `tmp/ui-qa/2026-05-11-teaching-hubs/sample-de-tall.png`

Checked in the live browser screenshots:

- `/de/teaching`: exact teacher-language prompt, four cards, status-only body copy, no teaser paragraphs
- `/de/teaching/spanish`: grouped sections `Grundlagen` and `Laute und Artikulation`, no visible edition pills
- `/de/teaching/english`: quiet empty state with backlink, no 404
- `/de/teaching/spanish/final-r`: backlink to the hub and normal public content blocks
- `/en/teaching`: bilingual copy and topic-count status update (`1 topic page` for Spanish)
- `/en/teaching/spanish`: English grouped hub with the correct reduced topic set

Additional live HTML check on `/de/sample` confirmed the mirrored Teaching section contains:

- `Korpus-Karten · Unterricht`
- `4 Themenseiten`
- `Grundlagen`
- `Laute und Artikulation`
- `Themenseiten im Aufbau`

## Spec Alignment

`docs/spec/platform-data-files.md` now reflects the active Teaching contract:

- teacher-first root selection with topic-count status
- grouped or empty-state public hubs for all active teaching languages
- no second visible edition switch inside the Teaching page body

## Open Points

- No blocking open point remains in this slice.