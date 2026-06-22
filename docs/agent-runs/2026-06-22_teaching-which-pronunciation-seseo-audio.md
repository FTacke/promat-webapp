# 2026-06-22 Teaching `which-pronunciation` Seseo Audio

## Scope

Replaced only the two right-hand Seseo audio sources on the bilingual Spanish Teaching topic `which-pronunciation`. The Distinción sources and visible page copy remain unchanged.

## Existing System

- Productive topic audio is stored below `content/teaching/spanish/which-pronunciation/media/audio/`.
- The comparison assets use lower-case kebab-case semantic names in the `variation/` subfolder.
- Both `de.yaml` and `en.yaml` reference the topic-local relative audio paths; the app exposes them below `/teaching-media/spanish/which-pronunciation/audio/`.
- The first pilot assets were assembled with ffmpeg from wordlist item MP3s and approximately 80 ms of inserted silence, as documented in `docs/agent-runs/2026-05-12_teaching-audio-contrast-pilot.md`. No retained concatenation utility existed.

## Source Session And Items

The authoritative item mapping came from `data/sessions/spanish/ES-N-0004-2026-S01/alignment/wordlist.json` and was validated by the build script before processing:

- `items/wordlist/wl_065.mp3` -> `casa`
- `items/wordlist/wl_034.mp3` -> `caza`
- `items/wordlist/wl_063.mp3` -> `gracias`
- `items/wordlist/wl_008.mp3` -> `ciudad`
- `items/wordlist/wl_071.mp3` -> `paz`
- `items/wordlist/wl_066.mp3` -> `ración`

All six inputs are mono MP3 at 48 kHz and 160 kbit/s from the same normalized wordlist derivation pipeline.

## Generation

Added the idempotent `scripts/build_which_pronunciation_seseo_audio.py`. It verifies the exact session ID, task, item IDs, item text, and source files; decodes the complete item MP3s; inserts exactly 8,820 zero-valued samples (0.2 seconds at 44.1 kHz) between adjacent items; and exports mono MP3 at 44.1 kHz and 96 kbit/s to match the existing Teaching comparison profile.

Generated:

- `seseo-casa-caza-es-n-0004-2026-s01.mp3`: 29,197 bytes, 2.360 s, SHA-256 `1099612D9682581C3E6B2C4A0B120EE03A7470AA84E4AA7805821F64DFCDD04F`
- `seseo-word-series-es-n-0004-2026-s01.mp3`: 65,246 bytes, 5.376 s, SHA-256 `6B61A0B83442FAD3D05FBDBA349D249C513DF25282431D9B66032DE980ECCF46`

The measured durations equal the sum of the complete source-item durations plus one 0.2-second separator per transition. A second build produced identical hashes.

## Content And Regression Changes

- Updated `content/teaching/spanish/which-pronunciation/de.yaml` and `en.yaml` to use the two new right-hand Seseo assets.
- Kept `distincion-casa-caza.mp3` and `distincion-word-series.mp3` unchanged.
- Added a focused route regression in `app/tests/test_research_sessions.py` for left/right source order, removal of the old right-hand references, successful public delivery, MIME type, and non-empty response bodies.
- No active spec changed because the Teaching media boundary, content model, route, and vocabulary remain unchanged.

## Verification

Passed:

- `python -m ruff check .`
- `python -m compileall -q app scripts/build_which_pronunciation_seseo_audio.py`
- `python scripts/ci_governance_checks.py`
- `python scripts/validate_teaching_content.py`
- focused Teaching content audio tests: 2 passed
- focused page-source and Teaching media-route tests: 2 passed
- ffprobe profile and duration checks for both new MP3s
- deterministic rebuild/hash comparison
- repository search confirmed no productive `which-pronunciation` YAML still references the old Seseo filenames

The broader existing test files were also sampled. `test_teaching_content.py` currently has one unrelated pre-existing section-grouping expectation failure (`test_build_teaching_topic_page_parses_teaching_impulses`; 37 passed, 1 failed). The broad `test_teaching_pilot_topic_renders_canonical_two_column_storytelling` route test likewise reaches an unrelated stale `didactic_close` expectation before its later audio assertions. The new focused regressions pass independently of those baseline failures.
