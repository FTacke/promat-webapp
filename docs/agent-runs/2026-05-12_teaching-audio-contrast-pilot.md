# 2026-05-12 Teaching Audio Contrast Pilot

## Scope

Fokussierter Teaching-Topic-Run fuer die Section `Hörvergleich` auf der Pilotseite `which-pronunciation`.

## Source Audio

Verified source sessions under `data/sessions/spanish/`:

- `ES-N-0001-2026-S01`
  - metadata: native speaker, origin `Spain / Asturias`
  - source items used:
    - `items/wordlist/wl_065.mp3` -> `casa`
    - `items/wordlist/wl_034.mp3` -> `caza`
    - `items/wordlist/wl_063.mp3` -> `gracias`
    - `items/wordlist/wl_008.mp3` -> `ciudad`
    - `items/wordlist/wl_071.mp3` -> `paz`
    - `items/wordlist/wl_066.mp3` -> `ración`
- `ES-N-0002-2026-S01`
  - metadata: native speaker, origin `Spain / Galicia`
  - source items used:
    - `items/wordlist/wl_065.mp3` -> `casa`
    - `items/wordlist/wl_034.mp3` -> `caza`
    - `items/wordlist/wl_063.mp3` -> `gracias`
    - `items/wordlist/wl_008.mp3` -> `ciudad`
    - `items/wordlist/wl_071.mp3` -> `paz`
    - `items/wordlist/wl_066.mp3` -> `ración`

## Mapping Note

- pilot mapping used in this run:
  - `ES-N-0001` -> `distincion`
  - `ES-N-0002` -> `seseo`
- this mapping is not securely proven by filename or metadata alone
- metadata confirms speaker origin, but does not explicitly label `distinción` vs. `seseo`
- the public pilot files were generated with this provisional mapping and should receive a fachliche review before treating the labels as final

## Generated Public Audio

Created under `public/teaching/spanish/audio/variation/` with `ffmpeg` and an inserted pause of about `80ms` between items:

- `distincion-casa-caza.mp3`
- `seseo-casa-caza.mp3`
- `distincion-word-series.mp3`
- `seseo-word-series.mp3`

Verified outputs:

- `distincion-casa-caza.mp3` -> `26376` bytes, `2.12s`
- `seseo-casa-caza.mp3` -> `26063` bytes, `2.10s`
- `distincion-word-series.mp3` -> `61171` bytes, `5.04s`
- `seseo-word-series.mp3` -> `57409` bytes, `4.70s`

## Content Changes

- updated `content/teaching/spanish/de/topics/which-pronunciation.yaml`
  - rebuilt the `Hörvergleich` section as:
    - intro text
    - `audio_contrast` `casa vs. caza`
    - `audio_contrast` `gracias – ciudad – paz – ración`
  - switched both blocks to public Teaching audio URLs only
  - introduced a new follow-up section heading `Seseo in verschiedenen Ländern`
  - removed visible collapsible behavior from the remaining follow-up blocks on the pilot page
- updated `content/teaching/spanish/en/topics/which-pronunciation.yaml`
  - mirrored the same structure for `Listening comparison`

## UI Changes

- updated `app/templates/partials/_teaching_blocks.html`
  - `audio_contrast` now renders as a dedicated shared comparison container instead of raw generic audio cards
  - one shared transcript line per contrast block
  - two internal comparison examples with title, subtitle, note, and compact player area
- updated `app/static/css/30_components.css`
  - added the Teaching-specific audio contrast block family:
    - `pm-teaching-audio-contrast*`
    - `pm-teaching-mini-player*`
  - desktop two-column layout for the two contrast examples
  - mobile stacking for the same examples
- added `app/static/js/modules/core/teaching-mini-player.js`
  - lightweight public mini-player for Teaching only
  - no Research session, set, owner, compare, or protected media logic reused
- updated `app/static/js/modules/core/entry.js`
  - shared initialization hook for the Teaching mini-player
- updated `app/templates/pages/teaching_page.html` and `app/src/app/i18n.py`
  - added DE/EN labels for play, pause, and progress

## Spec And Tests

- updated `docs/spec/platform-data-files.md`
  - `audio_contrast` clarified as a non-collapsible public Teaching comparison block with one shared transcript line and two desktop columns when exactly two examples are present
- updated `app/tests/test_research_sessions.py`
  - focused route regression now asserts the new hearing-comparison structure and public audio URLs
- updated `app/tests/test_teaching_content.py`
  - added a focused builder test for public `audio_contrast` URLs and availability

## Verification

- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_teaching_content.py -q -k "audio_examples_and_contrast_transcript_inheritance or keeps_public_audio_contrast_urls_and_availability"` -> passed
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k teaching_pilot_topic_renders_canonical_two_column_storytelling` -> passed
- live HTML check on `http://127.0.0.1:8000/de/teaching/spanish/which-pronunciation` confirmed:
  - `pm-teaching-audio-contrast`
  - `pm-teaching-mini-player`
  - `casa vs. caza`
  - `gracias – ciudad – paz – ración`
- live audio routes returned `200 OK` for all four generated files with `audio/mpeg`
- browser QA confirmed:
  - DE desktop: first contrast block examples side by side
  - DE mobile: first contrast block examples stacked vertically
  - DE page contains no `details` elements
  - first mini-player becomes ready and playback advances beyond `0s`
  - EN desktop shows `Listening comparison` with the same two contrast blocks
- screenshots saved under `tmp/ui-qa/2026-05-12-teaching-audio-contrast-pilot/`