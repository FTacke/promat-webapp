# 2026-05-12 Teaching Audio Examples CO.RA.PAN

## Scope

Fokussierter Teaching-Run fuer den Folgeabschnitt `Seseo in verschiedenen Ländern` auf der Pilotseite `which-pronunciation`.

## Adopted `hoermal` Principles

- one shared listening-material container instead of separate outer cards per example
- internal example grid for equal-rank listening items
- one compact transcript box per example with token ID visually subordinate inside the same example surface
- one compact player per example, aligned toward the lower area of the example block
- one shared source line for the whole block, not per example
- desktop two-column inner layout and mobile single-column stacking

## Copied CO.RA.PAN Audio

Copied from the textbook project:

- `C:\dev\linguistik.hispanistica\docs\assets\audiofiles\corapan\MEXb80def27c.mp3`
- `C:\dev\linguistik.hispanistica\docs\assets\audiofiles\corapan\CHL8b78ac16b.mp3`
- `C:\dev\linguistik.hispanistica\docs\assets\audiofiles\corapan\ARGCBAeca46a987.mp3`

Copied to PROMAT public teaching assets:

- `public/teaching/spanish/audio/corapan/MEXb80def27c.mp3`
- `public/teaching/spanish/audio/corapan/CHL8b78ac16b.mp3`
- `public/teaching/spanish/audio/corapan/ARGCBAeca46a987.mp3`

Verified sizes:

- `MEXb80def27c.mp3` -> `102328` bytes
- `CHL8b78ac16b.mp3` -> `35445` bytes
- `ARGCBAeca46a987.mp3` -> `29277` bytes

## Content Changes

- updated `content/teaching/spanish/de/topics/which-pronunciation.yaml`
  - inserted a short explanatory text block after the section heading
  - rebuilt `audio_examples` as one shared CO.RA.PAN material block
  - switched examples to public teaching URLs under `/teaching/spanish/audio/corapan/...`
  - moved source metadata to one block-level source object with label and URL
  - stored token IDs once per example via `token_id`
- updated `content/teaching/spanish/en/topics/which-pronunciation.yaml`
  - mirrored the same structure and public audio paths in English

## Builder / Template / CSS / JS Changes

- updated `app/src/app/teaching_content.py`
  - added inline markdown rendering for `transcript` and `note`
  - added support for block-level audio source objects `{label, url}`
  - added `token_id` support on examples
  - tightened example validity so block-level source no longer makes empty example entries render
- updated `app/templates/partials/_teaching_blocks.html`
  - added a dedicated shared `pm-teaching-audio-examples` container
  - added internal `pm-teaching-audio-example` items with transcript box, token line, shared source footer, and reused `pm-teaching-mini-player`
  - kept source rendering once at block level
- updated `app/templates/pages/teaching_page.html`
  - added the translated label hook for the shared source prefix
- updated `app/static/css/30_components.css`
  - added the Teaching-specific shared audio-examples block styling and internal grid
  - aligned example cards and player placement for calmer row rhythm
  - kept the existing teaching mini-player as the reused player surface
- updated `app/src/app/i18n.py`
  - added DE/EN copy for the shared source prefix

## Tests And Checks

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q -k "audio_examples_and_contrast_transcript_inheritance or keeps_public_audio_contrast_urls_and_availability or keeps_public_audio_examples_source_token_ids_and_audio"` -> passed
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k teaching_pilot_topic_renders_canonical_two_column_storytelling` -> passed
- live HTTP checks on the running app returned `200 OK` with `audio/mpeg` for:
  - `/teaching/spanish/audio/corapan/MEXb80def27c.mp3`
  - `/teaching/spanish/audio/corapan/CHL8b78ac16b.mp3`
  - `/teaching/spanish/audio/corapan/ARGCBAeca46a987.mp3`
- browser QA confirmed:
  - one shared `pm-teaching-audio-examples` block
  - three internal `pm-teaching-audio-example` items
  - one shared `CO.RA.PAN` source line
  - DE desktop first row examples aligned side by side
  - DE mobile examples stacked vertically
  - mini-player in the examples block becomes ready and playback advances beyond `0s`
  - EN desktop shows the same shared examples block structure
- screenshots saved under `tmp/ui-qa/2026-05-12-teaching-audio-examples-corapan/`

## Open Points

- the follow-up blocks after this section were intentionally not redesigned in this run
- the copied public audio files exist and are used live, but git tracking still depends on the repo-wide `public/*` ignore policy