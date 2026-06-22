# Research sessions regression cleanup

## Scope

Systematically resolved the 14 baseline failures in `app/tests/test_research_sessions.py` without changing the completed Spanish Design/Reading expandable implementation.

## Failure classification

### Productive login-target defect: 9 failed cases

- Eight `test_research_language_root_renders_public_landing_with_real_page_links` parameter cases (`de`/`en` × `spanish`/`french`/`german`/`english`).
- One `test_research_language_root_shows_muted_locked_entries_for_signed_out_users` case.
- Failed assertion: the anonymous login CTA was expected to preserve the exact corpus-root `next` target.
- Cause: `build_research_language_root_page()` still emitted `login_next:research:{language_slug}:speakers`, contradicting the active corpus-root return-target rule.
- Fix: resolve the login CTA through `login_next:research:{language_slug}`. Existing locked sidebar/drawer items and copy already matched the active contract.

### Teaching test drift: 4 failed tests

- `test_teaching_topic_renders_public_content_blocks`
  - Stale assertion expected one admonition; current draft topic intentionally renders both the structured `info_box` context block and `tip_box`.
- `test_teaching_pilot_topic_renders_canonical_two_column_storytelling`
- `test_teaching_english_which_pronunciation_renders_single_markdown_citation`
  - Stale assertions expected the retired `rich_text--didactic_close` span-2 block and older CTA wording.
  - Current bilingual content intentionally uses `text` span 1 plus structured `teaching_impulses` span 1 with three ordered items, and the YAML CTAs are `Mehr erfahren` / `Learn more`.
- `test_teaching_topic_box_css_uses_eye_overview_and_structured_context_box`
  - Stale assertion expected the former fixed `820px` audio-section width.
  - Current topic-grid contract and CSS intentionally let span-2 audio blocks use the full available width through `max-width: none`.
- Tests were aligned to the current productive HTML, CSS, and YAML. The missing active-spec catalog entry and behavioral note for `teaching_impulses` were added to `docs/spec/platform-data-files.md`.

### Research workbench test drift: 1 failed test

- `test_research_workbench_builders_expose_english_shared_labels`
- Failed assertion expected the former long English speakers intro.
- The bilingual `speakers` and `comparison` intro translations were intentionally cleared in an earlier product change; the current calm workbench header uses the direct page title and relies on controls and state copy for orientation.
- The test now asserts the intentional empty intro, and the active UI rule is recorded in `docs/spec/platform-data-files.md`.

## Changed files

- `app/src/app/routes/public_content.py`
- `app/tests/test_research_sessions.py`
- `docs/spec/platform-data-files.md`
- this run log

Unrelated concurrent access-request changes already present in the worktree were not modified.

## Verification

- `.\.venv\Scripts\python.exe -m ruff check .` — passed.
- `.\.venv\Scripts\python.exe -m compileall -q app scripts` — passed.
- `.\.venv\Scripts\python.exe scripts/validate_teaching_content.py` — passed for four Teaching languages.
- `.\.venv\Scripts\python.exe -m pytest app/tests/test_research_sessions.py -q` — 221 passed.
- `node --test app/tests/js/reading_expandables.test.mjs` — 1 passed.
- All remaining `app/tests/js/*.test.mjs` files — 9 passed.
- `git diff --check` — passed.

The complete route suite includes the bilingual Spanish Design rendering, expandable material, footnotes, and unaffected Reading-route regressions; those remain green.
