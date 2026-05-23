# 2026-05-23 Performance diagnostics: teaching audio and shared startup

## Scope

- Investigate initial-load performance with emphasis on public Teaching topic pages, audio-player surfaces, and shared startup payload.
- Apply only small, measurement-backed fixes.

## Runtime used

- `scripts/dev-start.ps1` was not reliable for this run because the local migration wrapper aborted on a PostgreSQL migration-state mismatch (`column "state" does not exist`).
- Live diagnostics therefore used `tmp/run_app_8010.py` on `http://127.0.0.1:8010` against the local dev Postgres database.

## Representative routes checked

- Public landing baseline: `/en`
- Public Teaching topic with multiple players and embeds: `/en/teaching/spanish/which-pronunciation`
- Protected Research player spot-check after dev login: `/en/research/spanish/player/ES-L-0001-2026-S01/wordlist?source=speakers`

## Findings

### Shared initial payload

- `base.html` eagerly loads a large shared CSS chain plus shared startup JS on every page.
- Largest shared CSS files observed in the repo during this run:
  - `app/static/css/30_components.css`: about 234 KB
  - `app/static/css/00_tokens.css`: about 58 KB
  - `app/static/css/40_cards.css`: about 31.5 KB
  - `app/static/css/md3/components/top-app-bar.css`: about 28.3 KB
  - `app/static/css/20_layout.css`: about 27.5 KB
- Largest page JS files observed in the repo during this run:
  - `app/static/js/pages/research-comparison.js`: about 59.1 KB
  - `app/static/js/pages/research-player.js`: about 40.7 KB
  - `app/static/js/pages/research-phenomena-editor.js`: about 29.9 KB

### Teaching topic page hotspot

- The representative public topic page renders 16 `<audio>` tags for 8 visible clips:
  - 8 hidden custom-player audio elements
  - 8 native fallback audio elements
- The shipped audio footprint referenced by that one page is about 387 KB across 8 MP3 files.
- Before the fix, a fresh page load triggered immediate local MP3 `206` requests without user interaction.
- Server logs showed duplicate requests per visible clip on initial render, caused by the combination of:
  - template markup using `preload="metadata"` on both audio elements per player
  - client init forcing eager loading in `teaching-mini-player.js`

### Shared startup duplication

- `app/static/js/modules/core/entry.js` initialized Teaching mini players and citation copy immediately, then repeated those scans again on `DOMContentLoaded`, and again on `turbo:load`.
- The ready guards prevented duplicate listener binding on already-initialized nodes, but the extra scans still added avoidable work on first load.

### Research player spot-check

- The protected Research player was fetched successfully with the local dev admin credentials.
- The representative player HTML renders one primary `<audio>` tag for the checked single-session route, not the Teaching-style duplicated audio pair.
- The player still deserves follow-up performance work because the page embeds server JSON state and uses the heavier page module `app/static/js/pages/research-player.js`, but the measured eager-media regression in this run was concentrated on Teaching.

## Changes made

- `app/templates/partials/_teaching_blocks.html`
  - Switched both Teaching audio elements from `preload="metadata"` to `preload="none"`.
- `app/static/js/modules/core/teaching-mini-player.js`
  - Removed the init-time preload override.
  - Removed the init-time `audio.load()` call.
- `app/static/js/modules/core/entry.js`
  - Removed the redundant `DOMContentLoaded` calls for `initTeachingCitationCopy()` and `initTeachingMiniPlayers()`.

## Validation

- Live reload of `/en/teaching/spanish/which-pronunciation` after the fix still rendered correctly.
- Fresh server logs for the post-fix Teaching page load showed the normal shared CSS/JS requests but no automatic local MP3 requests during initial render.
- `get_errors` reported no new errors in:
  - `app/static/js/modules/core/entry.js`
  - `app/static/js/modules/core/teaching-mini-player.js`
- Existing template diagnostics in `app/templates/partials/_teaching_blocks.html` were unchanged and unrelated to this run.

## Remaining follow-up candidates

- Split or defer parts of the shared CSS chain in `base.html`, especially the heaviest global files.
- Audit external font/icon dependencies for real usage on public editorial pages.
- Measure authenticated Research player and comparison pages in a real browser session with login automation to quantify JSON payload size, timeupdate/highlight work, and audio metadata behavior.
- Revisit whether all shared startup modules in `entry.js` need to run on every public page.