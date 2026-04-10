# Comparison matrix native audio src playback

- Date: 2026-04-10
- Area: comparison, player delivery
- Summary: After the item-route delivery contract was corrected, comparison playback still failed in browser usage. This follow-up removed the extra Blob/Object-URL layer from matrix playback and switched comparison to browser-native direct audio URLs after a header probe.

## Reproduced finding

- The corrected item route now served the checked real clip with `audio/mpeg` and inline disposition.
- A spot-checked real runtime clip (`ES-L-0001-2026-S01` / `wl_001`) was non-empty and structurally valid.
- `ffprobe` validated the same clip successfully both:
  - directly from disk
  - through the canonical item playback route
- The running app on both port `8003` (fresh process) and port `8000` served the corrected playback/download header split.
- That meant the remaining failure was no longer explained by attachment headers or by the checked media file itself.

## Root cause refinement

- Comparison still played clips through `fetch(...).blob()` plus `URL.createObjectURL(...)` before assigning the result to one shared `Audio()` instance.
- With the route now already browser-safe, that extra Blob/Object-URL indirection was unnecessary and created a separate media-loading path from the canonical player route.
- The follow-up fix therefore aligned comparison playback with the browser's native media loading path while keeping the response header probe in place.

## What changed

- Comparison playback now performs a lightweight `HEAD` probe for the item URL and validates:
  - `audio/*` content type
  - no attachment disposition
  - non-zero content length
- After that probe, the shared `Audio()` instance receives the canonical item URL directly as `src` and uses native browser loading instead of a fetched blob URL.
- Explicit download remains on the `?download=1` variant and is unchanged by this follow-up.
- The Blob/Object-URL cache and revoke path were removed in favor of a simple validated-href cache.

## Verification

- Static error check on `app/static/js/pages/research-comparison.js`
- `pytest app/tests/test_research_comparison.py`
- Live route header check on port `8003` and `8000`
- `ffprobe` validation of the checked real clip on disk and over HTTP

## Limits

- No stable automated headless browser click-play proof was obtained in this environment.
- The current evidence is therefore: corrected headers, valid real clip bytes, and a simplified browser-native playback path that removes the remaining custom media indirection from comparison.
