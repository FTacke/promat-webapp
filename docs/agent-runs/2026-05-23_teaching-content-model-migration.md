# Teaching Content Model Migration

## Scope

- cut Teaching loader logic over to the new hub/topic tree without productive legacy fallbacks
- moved released Spanish Teaching media from the old public asset tree into topic-local media folders
- updated public Teaching delivery to use the dedicated `/teaching-media/...` route
- migrated Teaching tests and active platform spec to the new model

## Implemented Model

- hub editions now live at `content/teaching/{teaching_lang}/hubs/{ui_lang}.yaml`
- topic editions now live at `content/teaching/{teaching_lang}/{topic_slug}/{ui_lang}.yaml`
- topic-local media now lives at `content/teaching/{teaching_lang}/{topic_slug}/media/{media_type}/...`
- hub files keep grouping and order only; title, summary, and author byline for topic cards come from the referenced topic file
- public Teaching topic media now resolves only through `/teaching-media/{teaching_lang}/{topic_slug}/{media_type}/{filename}`

## Content Migration

- migrated `spanish` from `de/index.yaml`, `en/index.yaml`, and `de|en/topics/*.yaml` to topic folders plus `hubs/de.yaml` and `hubs/en.yaml`
- created explicit unpublished topic editions for `soft-spanish-hard-german` and `r` so pending cards remain visible without duplicating hub copy
- kept `which-pronunciation` and `final-r` as public topics in both `de` and `en`
- moved Spanish audio, image, and download assets into `which-pronunciation/media/...` and `final-r/media/...`
- migrated empty `english`, `french`, and `german` hub editions to the new `hubs/{ui_lang}.yaml` layout

## Code Changes

- removed legacy hub/topic fallback reads from `app/src/app/teaching_content.py`
- made hub cards and topic-grid cards topic-driven instead of index-driven
- blocked direct public topic routes for unpublished topic editions while still rendering them as muted hub cards
- added topic-local media resolution and a dedicated public route in `app/src/app/routes/public.py`
- added author bylines to shared Teaching topic cards in the shared template/CSS family
- added `scripts/validate_teaching_content.py` for manifest, hub, equivalent-link, and topic-media validation

## Validation

- `python -m pytest app/tests/test_teaching_content.py -q`
- `python -m pytest app/tests/test_research_sessions.py -q -k teaching`

## Follow-up Notes

- the old `public/teaching/spanish` media tree was removed after moving the assets into topic-local media folders
- the validator is now the fast repo-level check for structural Teaching content regressions