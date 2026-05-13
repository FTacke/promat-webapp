# 2026-05-12 Teaching Topic Content Embed Fix

## Scope

Fokussierter Content- und Embed-Fix fuer die Pilotseite `which-pronunciation` auf den Teaching-Topic-Routen.

## Changes

- updated `content/teaching/spanish/de/topics/which-pronunciation.yaml`
  - reordered the `Seseo und distinción` section to `text -> Spain map -> info box -> America map`
  - updated Datawrapper URLs to `https://datawrapper.dwcdn.net/poSnB/9/` and `https://datawrapper.dwcdn.net/Uza2n/5/`
  - removed redundant PROMAT captions from both Datawrapper embeds
- updated `content/teaching/spanish/en/topics/which-pronunciation.yaml`
  - mirrored the same section order and Datawrapper URLs
  - removed redundant PROMAT captions from both Datawrapper embeds
- updated `app/templates/partials/_teaching_blocks.html`
  - added `data-provider="datawrapper"` to the Datawrapper embed figure for targeted CSS
- updated `app/static/css/30_components.css`
  - removed forced light-only appearance hooks from the Datawrapper wrapper and iframe
  - kept Datawrapper wrappers neutral and added explicit no-filter/no-blend/no-opacity overrides for `data-provider="datawrapper"`
- updated `docs/spec/platform-data-files.md`
  - clarified that visible PROMAT captions for Datawrapper are optional and should not duplicate Datawrapper's own descriptive content
  - clarified that PROMAT must not force Datawrapper appearance via filter, blend, or `color-scheme`

## Verification

- focused regression updated in `app/tests/test_research_sessions.py`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py -q -k teaching_pilot_topic_renders_canonical_two_column_storytelling` passed
- browser QA confirmed on:
  - `/de/teaching/spanish/which-pronunciation`
  - `/en/teaching/spanish/which-pronunciation`
- verified on DE desktop:
  - `text -> Spain map -> info box -> Americas map` in the `Seseo und distinción` section
  - no visible PROMAT caption below either Datawrapper card
  - Datawrapper URLs `poSnB/9` and `Uza2n/5`
  - no horizontal overflow
- verified Datawrapper appearance neutrality on the live DE route:
  - exactly two `figure.pm-teaching-embed-card[data-provider="datawrapper"]`
  - computed `opacity: 1`, `filter: none`, and `mix-blend-mode: normal` on wrapper, surface, frame wrap, and iframe
  - no forced light-only `color-scheme`; computed value stays browser-default `light dark`
- verified on DE mobile:
  - `text -> Spain map -> info box -> Americas map`
  - no horizontal overflow
- screenshots saved under `tmp/ui-qa/2026-05-12-topic-content-embed-fix/`