# 2026-06-19 French Theatre Live Production Fix

## Scope

- Corrected the live French wordlist catalog display value for stable item ID `wl_014`.
- Kept all session alignments, item IDs, MP3 assets, research sets, DB rows, and active releases intact.
- Used the canonical catalog already present in the active release as the replacement source for the stale flat app config.

## Backup

- Snapshot root: `/srv/webapps_storage/promat/backups/french_theatre_fix_20260619T170538Z`
- Captured the active-release French config/session tree and the flat app French config/session tree as separate tarballs.
- Dumped all seven `research_*` PostgreSQL tables and recorded before/after table counts.
- Saved the exact pre/post catalog files, Dry-run reports, structured searches, loader/audio validation, HTTP results, and container status.
- Both `checksums.sha256` and `evidence_checksums.sha256` passed verification.

## Read-only Audit

- Active DB: zero affected tables, rows, cells, or occurrences across all `research_*` tables.
- Active runtime/session alignment JSON: zero noncanonical occurrences.
- Active `current` release catalog: canonical and structurally identical to the flat catalog except for `$.items[13].text`.
- Flat app config: one noncanonical occurrence in `config/research_player/french/task_catalogs/wordlist.json` at `$.items[13].text`.
- Public/Secure data, filenames, asset keys, URLs, and unaccented English forms: zero active matches.
- An old failed upload under `data/quarantine/` contains eight nonactive historical occurrences. It is not read by the app and remains unchanged as forensic quarantine input.

## Apply

- Copied the canonical active-release `wordlist.json` to a temporary sibling in the flat app config directory.
- Validated JSON and byte identity with the canonical source, then atomically moved it over the stale flat file.
- No DB migration, package publish, intake re-import, alignment regeneration, audio rewrite, or release switch was necessary.
- Restarted only `promat-web-prod` to invalidate in-process research config/session caches.

## Validation

- Repeated production migration Dry-run: 194 JSON files and seven DB tables scanned; zero affected files, rows, or occurrences; no path changes.
- Flat and active-release catalog SHA-256 now match: `ebd46556ffae3a7f5a33fab75b7a388676e707348e987202ef61512c7ea89f45`.
- App loader: one canonical catalog `wl_014`; 21 ready French wordlist sessions; 21 canonical session labels; zero duplicates or missing items.
- Item delivery: 21/21 `wl_014` downloads resolved; 21/21 MP3 assets exist and are non-empty; all download labels are canonical.
- Active search: zero noncanonical and zero unaccented matches; canonical counts are 2 in each config tree and 68 in each session tree.
- `/health`, `/ready`, French de/en corpus roots, and French de/en design routes returned HTTP 200.
- Protected speaker, player, and item-audio routes returned the expected unauthenticated HTTP 302 login redirect.
- PostgreSQL research table counts were unchanged after apply.

## Intake Protection

- `scripts/research_data_intake/item_text_normalization.py` owns the French-only canonical correction.
- `alignment_export/wordlist_alignment.py` applies it before label validation and reports `canonical_item_correction`.
- `intake_storage.py` rejects stale French JSON in production packages.
- Regression coverage remains in the French migration, production importer, and working-tree intake tests.
