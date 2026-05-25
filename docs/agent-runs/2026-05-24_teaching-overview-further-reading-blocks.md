# 2026-05-24 Teaching Overview And Further Reading Blocks

## Scope

Implemented two token-based Teaching topic block refinements on the productive German and English `which-pronunciation` topic page without changing Teaching routing or media logic.

## Changes

- added a dedicated `overview` topic block type in the Teaching content parser and rendered it through its own `overview` admonition variant
- converted the former intro `Auf einen Blick` / `At a glance` box on the productive DE and EN `which-pronunciation` topic files from `info_box` to `overview`
- extended `further_reading` to support structured items with `title`, `text`, `cta`, and `href`
- replaced the former `Ausblick: Weitere Aussprachemerkmale` / `Outlook: More pronunciation features` section on the productive DE and EN `which-pronunciation` topic files with a calm structured `further_reading` block placed before citation
- added central tokens plus shared CSS for the new `overview` visual variant and the structured `further_reading` block
- updated the active Teaching block catalog in `docs/spec/platform-data-files.md`
- updated focused unit and route tests for block parsing, order, labels, and rendered HTML

## Validation

- `python -m pytest app/tests/test_teaching_content.py -q`
- `python -m pytest app/tests/test_research_sessions.py -q -k which_pronunciation`
- `python -m pytest app/tests/test_research_sessions.py -q -k teaching`
- `python scripts/validate_teaching_content.py`

## Browser QA

- Desktop QA on `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation`
	- `overview` renders as a dedicated calm wordmark-accent block with compass icon and 3 bullets
	- `further_reading` renders before citation with 2 compact cards and the updated CTA wording
- Desktop QA on `http://127.0.0.1:8000/en/teaching/spanish/which-pronunciation`
	- English labels render as `At a glance` and `Further exploration`
	- old `Outlook` and textbook CTA phrasing are gone
- Regression QA on `http://127.0.0.1:8000/de/teaching/spanish/final-r`
	- no unexpected `overview` or `further_reading` block appeared on the unaffected topic page
- Mobile QA used headless Playwright because the integrated browser page kept a desktop-width `innerWidth` despite viewport resize attempts
	- 390 px viewport confirmed for DE and EN
	- `window.matchMedia('(max-width: 759px)')` matched on both pages
	- `further_reading` stacked to one column (`gridTemplateColumns: 254px`) without horizontal overflow
	- screenshots saved under `tmp/ui-qa/2026-05-24-teaching-overview-further-reading/`