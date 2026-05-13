# Teaching Public Hubs Refinement

## Goal

Refine the already accepted public Teaching flow without changing its routing, public access model, edition logic, or grouped topic architecture:

- turn `/{ui_lang}/teaching` into a calmer one-column language selection list
- remove language-color signaling from the Teaching root selection surface
- switch hub and topic backlinks to the shared outlined secondary button pattern
- tighten hub titles and lead copy around pronunciation teaching
- allow short muted group intro sentences from content
- keep Sample aligned with the active Teaching UI

## Changed Files

- `app/src/app/routes/public_content.py`
- `app/src/app/teaching_content.py`
- `app/src/app/i18n.py`
- `app/templates/partials/_corpus_card.html`
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
- `docs/agent-runs/2026-05-11_teaching-public-hubs-refinement.md`

## What Changed

### Teaching root refined into neutral selection rows

- The Teaching root still uses the teacher-first language selection, but it now renders as one centered vertical list instead of compact colored cards.
- Selection rows now use a dedicated neutral `teaching-selection-row` presentation through the shared corpus-card macro.
- Root entries keep only the language name, status line, and quiet `Öffnen` / `Open` action.
- The explicit Teaching order is now `spanish`, `english`, `french`, `german`.

### Backlinks moved onto shared secondary buttons

- Hub pages now render `← Zur Sprachauswahl` / `← Back to language selection` through `render_action_button(...)` with the shared secondary small button styling.
- Topic pages now render `← {hub_title}` through the same shared button family.

### Hub copy tightened and group intros enabled

- Public Teaching hubs now use pronunciation-focused titles such as `Spanisch: Aussprache unterrichten` and `Spanish: Teaching pronunciation`.
- Group payloads can carry `description` or `intro` from YAML and render them as short muted orientation lines above the topic cards.
- Empty-state wording was tightened to `Für diese Sprache sind noch keine öffentlichen Themenseiten hinterlegt.` / `No public topic pages have been added for this language yet.`

### Sample mirror kept in sync

- The Sample page now mirrors the refined Teaching root list styling through the same shared corpus-card path.
- The mirrored grouped Teaching section also renders the new muted group descriptions.

## Validation

### Focused tests

- `pytest app/tests/test_teaching_content.py -q` -> `9 passed`
- `pytest app/tests/test_research_sessions.py -q -k teaching` -> `13 passed, 183 deselected`
- `pytest app/tests/test_research_sessions.py -q -k sample_page_reflects_current_landing_and_corpus_cards` -> `1 passed`
- `get_errors` on touched Python, Jinja, and test files -> no errors

### Browser QA

The integrated browser path still failed with `browserContext.newPage: Cannot read properties of undefined (reading '_page')`, so browser QA used the existing headless Edge fallback against `http://127.0.0.1:8010`.

Artifacts were written to:

- `tmp/ui-qa/2026-05-11-teaching-refinement/de_teaching.png`
- `tmp/ui-qa/2026-05-11-teaching-refinement/de_teaching.html`
- `tmp/ui-qa/2026-05-11-teaching-refinement/de_teaching_spanish.png`
- `tmp/ui-qa/2026-05-11-teaching-refinement/de_teaching_spanish.html`
- `tmp/ui-qa/2026-05-11-teaching-refinement/de_teaching_english.png`
- `tmp/ui-qa/2026-05-11-teaching-refinement/de_teaching_english.html`
- `tmp/ui-qa/2026-05-11-teaching-refinement/de_teaching_spanish_final-r.png`
- `tmp/ui-qa/2026-05-11-teaching-refinement/de_teaching_spanish_final-r.html`
- `tmp/ui-qa/2026-05-11-teaching-refinement/en_teaching.png`
- `tmp/ui-qa/2026-05-11-teaching-refinement/en_teaching.html`
- `tmp/ui-qa/2026-05-11-teaching-refinement/en_teaching_spanish.png`
- `tmp/ui-qa/2026-05-11-teaching-refinement/en_teaching_spanish.html`
- `tmp/ui-qa/2026-05-11-teaching-refinement/de_sample.png`
- `tmp/ui-qa/2026-05-11-teaching-refinement/de_sample.html`

Checked in live HTML dumps and screenshots:

- `/de/teaching`: one centered vertical selection list, four neutral rows, order `Spanisch -> Englisch -> Französisch -> Deutsch`, no language-color modifier class on the root rows
- `/de/teaching/spanish`: pronunciation-focused hub title, outlined secondary backlink button, both muted group intro sentences visible
- `/de/teaching/english`: quiet empty-state card with the updated German text
- `/de/teaching/spanish/final-r`: topic page uses the new outlined backlink button to the hub
- `/en/teaching/spanish`: English title `Spanish: Teaching pronunciation` plus the new English group intro sentence
- `/de/sample`: HTML dump confirms the refined Teaching mirror includes `pm-teaching-language-list` and four `pm-teaching-language-row` anchors

## Spec Alignment

`docs/spec/platform-data-files.md` now reflects the refined active Teaching contract:

- neutral one-column selection list on the Teaching root
- shared outlined secondary backlinks on Teaching hub and topic pages
- optional muted group intro sentence sourced from content

## Open Points

- No blocking open point remains in this refinement slice.