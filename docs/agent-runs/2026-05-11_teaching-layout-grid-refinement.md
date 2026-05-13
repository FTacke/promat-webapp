# Teaching Layout Grid Refinement

## Goal

Refine the public Teaching layout without changing routing, public access, edition switching, or the accepted teacher-first root selection:

- widen Teaching hubs and topic pages on desktop while keeping the root selection narrower
- keep hub topic cards visually uniform but allow up to three equal-width cards per row on desktop
- introduce a responsive topic block grid with optional `layout.span: 1 | 2 | 3`
- keep the block model backward compatible for existing YAML without layout metadata
- update English hub titles to the more natural `Teaching {language} pronunciation`

## Changed Files

- `app/src/app/teaching_content.py`
- `app/templates/pages/teaching_page.html`
- `app/templates/partials/_teaching_blocks.html`
- `app/templates/pages/sample_page.html`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_teaching_content.py`
- `app/tests/test_research_sessions.py`
- `content/teaching/spanish/de/index.yaml`
- `content/teaching/spanish/de/topics/final-r.yaml`
- `content/teaching/spanish/en/index.yaml`
- `content/teaching/spanish/en/topics/final-r.yaml`
- `content/teaching/english/en/index.yaml`
- `content/teaching/french/en/index.yaml`
- `content/teaching/german/en/index.yaml`
- `docs/spec/platform-data-files.md`
- `docs/agent-runs/2026-05-11_teaching-layout-grid-refinement.md`

## What Changed

### Broader hub and topic content width

- The Teaching root still renders as the existing narrow centered list.
- Hub and topic pages now use a broader desktop content width of about `70rem` so the main title and work surface no longer wrap prematurely.
- The shared content header and backlink row inherit that wider width only on hub and topic views.

### Hub cards stay uniform but can reach three columns

- Hub topic cards still use one shared card family with no featured, wide, compact, or mixed-height variants.
- The hub grid now uses a dedicated Teaching grid that is:
  - one column on mobile
  - two columns from tablet width
  - up to three columns on desktop
- The Spanish German UI hub was regrouped so one section now shows three real cards on desktop, making the three-column behavior visible in live QA.

### Topic pages now support `layout.span`

- `teaching_content.py` now normalizes `layout.span` per block with block-type defaults.
- Allowed values are `1`, `2`, and `3`; missing or invalid values fall back to the block-type default.
- Topic pages render blocks inside a responsive Teaching block grid:
  - mobile: one column
  - tablet: two columns, wider spans collapse to full width
  - desktop: three columns with `span 1`, `span 2`, and `span 3`
- No masonry, height equalization, or visual reordering was introduced.

### Content and copy updates

- The German `final-r` topic now carries explicit layout spans so the new grid is demonstrated on a real public page.
- The German `final-r` topic also now links to three next topics, which makes the topic-card grid visible on desktop.
- English hub titles were renamed to:
  - `Teaching Spanish pronunciation`
  - `Teaching English pronunciation`
  - `Teaching French pronunciation`
  - `Teaching German pronunciation`
- English topic backlinks inherit the updated hub title automatically.

### Sample kept aligned

- The Sample page now uses the same Teaching hub grid class for mirrored topic-card groups.
- The existing mirrored root list remains unchanged and stays narrow.

## Validation

### Focused tests

- `pytest app/tests/test_teaching_content.py -q` -> `10 passed`
- `pytest app/tests/test_research_sessions.py -q -k teaching` -> `14 passed, 183 deselected`
- `pytest app/tests/test_research_sessions.py -q -k sample_page_reflects_current_landing_and_corpus_cards` -> `1 passed, 196 deselected`
- `get_errors` on the touched Python, Jinja, CSS, and test files found no new relevant errors; the returned CSS `color-mix(...)` warnings and the standalone macro `<li>` warning are pre-existing unrelated diagnostics outside this slice.

### Browser QA

Local browser QA ran against `http://127.0.0.1:8010` with automated screenshot and HTML capture artifacts under:

- `tmp/ui-qa/2026-05-11-teaching-layout-grid/`

Artifacts include desktop and mobile screenshots plus HTML for:

- `/de/teaching`
- `/de/teaching/spanish`
- `/de/teaching/english`
- `/de/teaching/spanish/final-r`
- `/en/teaching`
- `/en/teaching/spanish`
- `/de/sample`

Checked visually in the generated screenshots:

- `/de/teaching` stays a narrow calm vertical list on desktop and mobile
- `/de/teaching/spanish` uses a visibly broader desktop content area, the title no longer wraps unnecessarily, and one hub group now renders three equal-width cards in one row
- `/de/teaching/english` keeps the quiet empty state on the broader desktop width
- `/de/teaching/spanish/final-r` uses the new block grid: a two-thirds text block beside a one-third audio block, followed by a two-thirds contrast block beside a one-third warning block; mobile collapses back to one column
- `/en/teaching/spanish` shows the updated natural English hub title without reintroducing any body-level edition UI

Checked in the HTML dumps:

- `/de/teaching`: `pm-teaching-page--overview`, `pm-teaching-language-list`, and no `pm-card--lang-es`
- `/de/teaching/spanish`: `pm-teaching-page--hub`, `pm-teaching-content-wide`, `pm-teaching-topic-grid`, and `Spanisch: Aussprache unterrichten`
- `/de/teaching/english`: updated empty-state text still present
- `/de/teaching/spanish/final-r`: `pm-teaching-page--topic`, `pm-teaching-block-grid`, `pm-teaching-block--span-1`, `pm-teaching-block--span-2`, `pm-teaching-block--span-3`, and at least three topic-card links
- `/en/teaching/spanish`: `Teaching Spanish pronunciation` and `Concrete pronunciation topics with examples and classroom prompts.`
- `/de/sample`: `pm-teaching-language-list` and `pm-teaching-topic-grid`

## Spec Alignment

`docs/spec/platform-data-files.md` now reflects the active Teaching layout contract for this slice:

- narrower root selection versus broader hub/topic content width
- uniform hub cards with up to three desktop columns
- responsive topic block grid with optional `layout.span` and no masonry or height logic

## Open Points

- No blocking open point remains in this refinement slice.