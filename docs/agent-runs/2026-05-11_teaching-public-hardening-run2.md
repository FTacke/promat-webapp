# Teaching Public Hardening Run 2

## Goal

Harden the already implemented public Teaching rawbau from Run 1 without introducing a final redesign or large new features. Scope: edge cases, focused tests, responsive usability, governance alignment, production/runtime safety, and public Teaching asset delivery.

## Changed Files

- `app/src/app/teaching_content.py`
- `app/src/app/routes/public.py`
- `app/src/app/analytics.py`
- `app/static/css/30_components.css`
- `app/tests/test_teaching_content.py`
- `app/tests/test_research_sessions.py`
- `app/tests/test_analytics.py`
- `docs/spec/platform-data-files.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `.github/instructions/repo.instructions.md`

## Hardened Or Corrected

- Teaching image blocks now render when `src` exists even if `alt` is missing; the loader logs a warning and falls back to empty alt text instead of dropping the block.
- Added `clear_teaching_content_caches()` and focused Teaching content tests for missing alt text, empty credits, unknown blocks, next-topic filtering, target-edition fallback, and content-root discovery.
- Narrowed analytics retry behavior so only the known duplicate-key aggregate races retry; unrelated `IntegrityError`s are re-raised.
- Added a public Teaching asset route `/teaching/<path:asset_path>` that resolves safely from `PROMAT_PUBLIC_ROOT/teaching/...` and rejects parent traversal.
- Hardened Teaching content-root fallback discovery so local repo runs resolve `<repo>/content/teaching` and built images resolve `/app/content/teaching` even if the optional env override is absent.
- Added governance/spec wording that Teaching is fully public, separate from Research, editorial-file based, and that released Teaching media is public-root bounded.
- Applied Teaching-specific mobile topbar compression in shared CSS and re-ran mobile screenshots.

## Tests And Checks

### Pytest

- `pytest app/tests/test_teaching_content.py -q` -> `7 passed`
- `pytest app/tests/test_research_sessions.py -q -k teaching` -> `10 passed, 183 deselected`
- `pytest app/tests/test_research_sessions.py -q -k "teaching and asset"` -> `2 passed, 191 deselected`
- `pytest app/tests/test_analytics.py -q` -> `3 passed`

### Live HTTP And Browser Checks

- Earlier live route smoke remained green for:
  - `/de/teaching`
  - `/de/teaching/spanish`
  - `/de/teaching/spanish/final-r`
  - `/en/teaching/spanish`
  - `/en/teaching/spanish/final-r`
  - missing topic redirect to `/de/teaching/spanish`
  - protected research regression redirect on `/de/research/spanish/comparison`
  - unaffected public regression `/de/project/about`
- Repeated 390 px mobile screenshots confirmed the Teaching hub/topic content stacks remain readable.
- One narrow-screen topbar issue remains: on 390 px width the global `DE | EN` switch is still clipped at the right edge on drawer-free Teaching pages despite multiple CSS reductions.

### Production / Runtime Validation

- `docker compose -f app/infra/docker-compose.prod.yml config` confirms:
  - build context `C:\dev\promat`
  - dockerfile `app/Dockerfile`
  - `PROMAT_RUNTIME_ROOT=/app`
  - `PROMAT_PUBLIC_ROOT=/app/public`
  - `PROMAT_TEACHING_CONTENT_ROOT=/app/content/teaching`
- `docker build -f app/Dockerfile -t promat-teaching-check .` succeeded.
- `docker run --rm --entrypoint /bin/sh promat-teaching-check -c "ls -R /app/content/teaching"` confirmed the image contains the Teaching content tree.
- A rebuilt-image Python check with production runtime env vars confirmed both `DEFAULT_TEACHING_CONTENT_ROOT` and `TEACHING_CONTENT_ROOT` resolve to `/app/content/teaching` in the container layout.
- The Teaching loader now discovers the nearest ancestor `content/teaching` tree by default, which removes the old local-vs-container fallback mismatch.
- `public/teaching` currently contains no committed assets in this repo snapshot, so there was no real shipped Teaching media file to verify by live curl after the new route. Asset delivery was validated via focused route tests that create a temporary public Teaching file.

## Governance Updates

- Added concise Teaching public-boundary rules to root `AGENTS.md`.
- Added app-level Teaching runtime-boundary rules to `app/AGENTS.md`.
- Added Teaching public/editorial boundary guidance to `.github/instructions/repo.instructions.md`.
- Updated `docs/spec/platform-data-files.md` with the public Teaching asset route schema and explicit public-root delivery rule.

## Open Points

- The mobile Teaching topbar on very narrow widths still does not show the full global `DE | EN` switch cleanly in browser screenshots. This is now isolated to a Teaching-specific responsive shell issue, not a content or route issue.
- There are still no committed real assets under `public/teaching/...`; once assets are added, one live browser or curl pass should verify the new public asset route against a real file.

## Recommendations For Run 3

1. Fix the remaining 390 px Teaching topbar clipping with DOM-level browser inspection rather than further blind CSS compression.
2. Add one small live QA check for a real file under `public/teaching/...` once the first released Teaching asset is committed.
3. If additional Teaching editions or edition-only UI languages are added, extend focused tests around hub/topic switching and edition fallback before expanding the route contract.