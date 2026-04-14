# English Runtime Unlock 127

## Summary

Unlocked the English research workbench surfaces through the canonical capability layer so the already imported English runtime/session data now renders productively in the webapp instead of falling back to protected placeholders.

## Scope

- `app/src/app/research_capabilities.py`
- `app/src/app/research_views.py`
- `app/templates/pages/research_player.html`
- `app/tests/test_research_capabilities.py`
- `docs/spec/research-capabilities.md`

## Root cause

The main blocker was the canonical surface-mode logic in `app/src/app/research_capabilities.py`.

- `DEFAULT_RESEARCH_PAGE_SURFACE_MODES` marked all workbench pages except `design` as placeholders.
- `CORPUS_RESEARCH_PAGE_SURFACE_OVERRIDES` promoted only `spanish` to `productive`.
- `app/src/app/routes/public.py` already respected that central capability result and therefore continued routing `english/speakers`, `english/recordings`, `english/comparison`, and `english/phenomena` into the placeholder builder even though the English runtime session tree and metadata were already present.

After that central unlock, two dormant follow-on defects became visible because the previously hidden productive routes actually rendered:

1. `app/src/app/research_views.py` caught `ResearchSetStorageUnavailableError` in productive player/comparison fallback branches without importing it.
2. `app/templates/pages/research_player.html` used Jinja dot-access `block.items`, which bound to the dict method instead of the payload list when the connected-text English player actually rendered.

## Changes

- Replaced the Spanish-only surface override model in `app/src/app/research_capabilities.py` with data-driven readiness checks:
  - `speakers` and `recordings` become productive when canonical runtime sessions exist under `data/sessions/{language}/`
  - `comparison` becomes productive when at least one compare-capable task resolves to a ready runtime bundle through the shared player runtime
  - `phenomena` becomes productive when task catalogs and `phenomena_presets.json` load through the shared research-player config layer
- Added focused capability regression coverage in `app/tests/test_research_capabilities.py` for the English productive-readiness case.
- Updated `docs/spec/research-capabilities.md` so the active spec now describes readiness through canonical runtime/config prerequisites instead of fixed language lists.
- Imported `ResearchSetStorageUnavailableError` in `app/src/app/research_views.py` so productive player/comparison pages degrade cleanly when set storage is unavailable.
- Switched the running-text player template in `app/templates/pages/research_player.html` from `block.items` to `block['items']` to avoid the Jinja dict-method collision.

## Verification

### Focused tests

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_capabilities.py -q`
- Result: `13 passed`

### Real runtime route verification

Used the full app factory with initialized DB engine and a simulated authenticated request context against the current repository runtime data.

Verified all of the following with HTTP `200` responses and without the old placeholder text:

- `/de/research/english/speakers`
- `/de/research/english/recordings?task=wordlist`
- `/de/research/english/speakers/EN-L-0001`
- `/de/research/english/player/EN-L-0001-2026-S01/wordlist?source=recordings`
- `/de/research/english/player/EN-L-0001-2026-S01/text?source=recordings`
- `/de/research/english/comparison`
- `/de/research/english/phenomena`

Runtime checks also confirmed:

- `get_research_page_surface_mode("english", "speakers") == "productive"`
- `get_research_page_surface_mode("english", "recordings") == "productive"`
- `get_research_page_surface_mode("english", "comparison") == "productive"`
- `get_research_page_surface_mode("english", "phenomena") == "productive"`

## Outcome

The imported English corpus now uses the same productive runtime path as already freigeschaltete corpora where the shared runtime/config prerequisites are satisfied. The old placeholder gating was removed from the English path without adding a route-local hack.
