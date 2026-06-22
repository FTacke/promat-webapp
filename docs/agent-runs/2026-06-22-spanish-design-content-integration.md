# Spanish design content integration

## Scope

- Replaced the complete `SPANISH_DESIGN_PAGE_CONTENT` payload with the prepared bilingual revision.
- Normalized the integrated Python dictionary indentation while preserving pre-existing formatting outside the replaced block.
- Added shared Reading-page rendering for localized `pm_expandable_text` material and page-level `footnotes_html`.
- Reused the shared action-button, reading typography, surface, spacing, border, and radius systems; added only Reading-specific scale and preview tokens.
- Added progressive expandable behavior with complete no-JavaScript fallback, localized toggle labels, `aria-expanded`, stable controlled IDs, responsive columns, and reduced-motion handling.
- Positioned footnotes immediately before the final `pm-literature` section and retained the existing literature family at a quieter reading scale.
- Refined the footnote apparatus to the full Reading measure with a compact number/text grid, UI-language-specific targets, localized accessible return links, and bidirectional reference navigation.
- Fixed the shared navigation scroll state so fragment-history events resolve and reveal their target instead of being overwritten by the generic scroll-to-top behavior.
- Applied the requested Spanish design heading, expandable-title, and wordlist-summary corrections without changing list items or research prose.
- Removed the temporary source document after integration to avoid a duplicate content source inside `app/`.
- Updated the focused route regression to cover wording that is unique to the revised content.

## Verification

- `python -m py_compile app/src/app/routes/public_page_content_data.py`
- `.\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -k "spanish_design_page" -q`
  - Superseded by the broader focused run below.
- `.\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -k "spanish_design_page or reading_expandable" -q`
  - Result: 6 passed.
- `.\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -k "spanish_design_page or reading_expandable or project_about_page_embeds_video_and_hides_intro" -q`
  - Result: 8 passed, including one unaffected shared Reading route.
- `node --test app/tests/js/reading_expandables.test.mjs`
  - Result: 1 passed.
- All JavaScript test files under `app/tests/js/` were run individually.
  - Result: 11 passed.
- Ruff checks, JavaScript syntax checks, Python compilation, and `git diff --check` passed for the changed implementation and regression files.
- Browser acceptance on `/de/research/spanish/design` and `/en/research/spanish/design` at `1440x1000` and `390x844`.
  - Both material blocks were clipped at 81 px initially, fully expanded to their complete measured height, used two desktop columns and one mobile column, and produced no horizontal overflow or browser-console errors.
  - The collapsed component was also checked in dark mode, and `/en/project/about` was checked as an unaffected shared Reading route.
  - The follow-up footnote pass measured identical footnote/literature widths (`724.5 px` desktop and `358 px` mobile) in both UI languages and exercised reference plus return-link navigation successfully.
  - The corrected navigation pass verified actual target placement, not only URL hashes: reference, return, and direct deep-link targets landed around `80 px` below the viewport top on desktop and mobile in both UI languages.
  - Screenshots and the machine-readable report live under `tmp/ui-qa/2026-06-22-spanish-design-reading-elements/`.
- The complete `app/tests/test_research_sessions.py` run reached 207 passed and 14 failures. Those failures concern pre-existing login-link, locked-navigation, Teaching-content/CSS, and workbench-intro expectations outside this change; the focused changed and unaffected routes pass.

## Notes

No route, access, capability, or runtime-boundary contract changed. The shared public Reading content-element contract was added to `docs/spec/platform-data-files.md`.
