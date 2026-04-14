# Run Log: Raw Archive Backfill

## Summary

- hardened the central production importer so batch raw masters are archived into productive session trees
- added an explicit raw-only backfill mode for already imported sessions
- updated spec, runbook, and intake README so the archive rule is binding and operationally repeatable

## Key Decisions

- productive `raw/` is mandatory whenever an unmodified original WAV master exists in batch `raw/`
- productive `source/` remains the processed working layer and is never copied into `raw/` as a substitute
- batch raw mapping stays filename-driven by `person_id` and task via the shared batch inventory helpers; ambiguous raw mappings are hard conflicts
- the central importer now handles raw archival in normal write mode and supports `--sync-raw-only` for clean backfill of already imported sessions

## Validation Plan

- run a raw-aware dry-run against the real ES batch
- run a one-person raw-only backfill and verify `source/` stays unchanged while `raw/` is added
- run the full ES raw-only backfill for the already imported Spanish sessions
- verify productive session trees and metadata contain archived raw masters afterward

## Validation Results

- focused unit tests passed:
	`c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_raw_sync_importer.py -q`
- full ES raw-only dry-run before backfill showed `raw_sync=31`, `raw_missing=2`, `raw_conflict=0`
- one-person raw-only backfill for `ES-L-0001` completed successfully and left the SHA256 of `source/wordlist.wav` unchanged
- after the full ES raw-only backfill, a second dry-run showed `raw_sync=0`, `raw_keep=31`, `raw_missing=2`, `raw_conflict=0`
- productive raw archive result:
	- learner sessions `ES-L-0001` through `ES-L-0009` now contain `raw/wordlist.wav`, `raw/text.wav`, and `raw/interview.wav`
	- native sessions `ES-N-0001` and `ES-N-0002` now contain `raw/wordlist.wav` and `raw/text.wav`
	- no native `interview` raw masters existed in the batch, so those remain transparently absent
- research metadata table counts stayed stable after the raw-only backfill: `people=11`, `sessions=11`, `exposures=3`