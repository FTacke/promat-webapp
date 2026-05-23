# 2026-05-23 Research player performance diagnostics

## Scope

- Focused follow-up on Research Player, Research Comparison, and shared page-start costs.
- No further Teaching-specific optimization except shared startup files.

## Runtime

- `scripts/dev-start.ps1` was still unsuitable as a reliable diagnostics entrypoint because of the local migration-state mismatch.
- Live measurements used `tmp/run_app_8010.py` on `http://127.0.0.1:8010`.

## Measured routes

- `/en`
- `/en/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=speakers`
- `/en/research/spanish/player/ES-L-0001-2026-S01/text?source=speakers`
- `/en/research/spanish/comparison?task=wordlist`

## Key findings

- The `text` player route is primarily payload- and DOM-heavy, not JS-CPU-heavy:
  - about 223.8 KB HTML
  - about 72.2 KB embedded JSON state
  - 50 item nodes plus 393 token nodes in the DOM
  - the same 50 items and 393 tokens also present in the JSON state
- Local replay measurements showed JSON parse and item-map build costs were small, so duplication and document size matter more than startup compute.
- The player still issues one early audio request before user interaction because the main audio uses `preload="metadata"`.
- `research-player.js` is page-specific and its heavier sync/highlight loops only begin during playback, not during initial page boot.
- `research-comparison.js` is also page-specific, but authenticated comparison boot still performs extra set-related API work on initial load when no explicit `set_id` is present.
- Shared startup still carries a broad CSS base plus global core/bootstrap/navigation scripts.

## Safe fix applied

- `app/static/js/modules/core/entry.js` now lazy-loads optional DOM-specific modules only when matching elements are present:
  - `datawrapper.js`
  - `teaching-mini-player.js`
  - `teaching-citation-copy.js`

## Validation

- `get_errors` reported no new issues in `app/static/js/modules/core/entry.js`.
- With browser cache disabled:
  - landing, player, and comparison no longer loaded those three optional modules
  - a real Teaching page still loaded them correctly
- Browser measurements and server logs were recorded for request structure, JSON size, HTML size, and early audio behavior.

## Follow-up priorities

- P0: reduce duplicate token/item transport on the `text` player
- P0: reduce comparison default-workspace boot API churn
- P0: decide whether player audio preload can be relaxed without UX regression
- P1: continue segmenting shared startup and large shared CSS families
- P1: address oversized landing assets for general page-load improvement