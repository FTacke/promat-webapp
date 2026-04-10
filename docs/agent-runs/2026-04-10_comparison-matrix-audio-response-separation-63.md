# Comparison matrix audio response separation

- Date: 2026-04-10
- Area: comparison, player delivery
- Summary: Fixed matrix item playback by separating playback-safe inline audio responses from explicit download responses on the canonical player item route, while keeping direct download intact.

## Reproduced finding

- Comparison matrix play used the same canonical player item URL as the direct download action.
- The route returned `200` with `audio/mpeg`, but it also returned `Content-Disposition: attachment` for the item response.
- A direct download therefore worked, but the response contract was still built as a download response rather than as a playback-safe media response.
- A header probe against an isolated Flask test client showed the mismatch clearly before the fix:
  - item route: `audio/mpeg` plus `attachment; filename=...`
  - full-audio route: `audio/mpeg` plus inline disposition
- Real runtime artifacts were also spot-checked: the affected split MP3 file existed and was non-empty, so the root cause was not just a missing file.

## Root cause

- The canonical player item route mixed two intents into one default response:
  - matrix playback wanted an inline media response
  - direct item download wanted attachment semantics with the delivery filename contract
- Comparison JS used the same URL for both play and download, so there was no explicit separation of playback intent and download intent.
- The primary defect was response semantics, specifically the forced attachment disposition on the route used for matrix playback.
- Range behavior was checked as well; the fixed inline route now supports `206` partial responses for range requests, so range handling was not the blocking cause after the response contract was corrected.

## What changed

- The canonical item route under `/{ui_lang}/research/{language}/player/{session_id}/{task}/items/{item_id}.mp3` now serves inline `audio/mpeg` by default.
- Explicit download semantics stay on the same route family through `?download=1`, which keeps:
  - `Content-Disposition: attachment`
  - the prepared delivery filename contract `{person_id}_{task}_{item_id}_{download_label}.mp3`
- Comparison JS now uses:
  - the plain item URL for playback
  - the `?download=1` variant for the download button
- Comparison playback fetching was hardened so attachment-style responses are rejected instead of being treated as normal audio sources.

## Verification

- Static error check on:
  - `app/src/app/routes/public.py`
  - `app/static/js/pages/research-comparison.js`
  - `app/tests/test_research_comparison.py`
  - `app/tests/test_research_sessions.py`
  - `docs/spec/platform-data-files.md`
  - `docs/spec/research-access.md`
- `pytest app/tests/test_research_comparison.py`
- `pytest app/tests/test_research_sessions.py::test_player_item_download_route_uses_delivery_filename`
- `pytest app/tests/test_research_comparison.py::test_text_item_route_separates_playback_from_download`
- Direct isolated header probe after the fix showed:
  - playback item response: `Content-Type: audio/mpeg`, `Content-Disposition: inline; filename=...`
  - download variant: `Content-Disposition: attachment; filename=...`
  - range probe on playback route: `206` with `Content-Range: bytes 0-15/...`

## Added regressions

- Comparison test now verifies that the item route returns a playback-safe inline response by default and an attachment response for `?download=1`.
- Player delivery test now verifies:
  - inline playback semantics on the default item URL
  - attachment semantics plus delivery filename on the explicit download variant
  - `206` range behavior on the playback route
- Test helpers now write minimal MP3-like bytes instead of placeholder fake strings so the delivery tests exercise realistic playable artifacts.

## Limits

- No browser-side live playback click test was executed in a running local browser session during this run.
- The fix was verified through route/header inspection, regression tests, and isolated Flask test-client probes.
- A separate full `app/tests/test_research_sessions.py` run still exposes unrelated pre-existing fixture/config failures around missing `player_config.json`; those failures were outside this audio-response fix.
