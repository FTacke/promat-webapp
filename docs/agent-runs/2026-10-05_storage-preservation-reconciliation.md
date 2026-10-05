# Reconciliation: local-storage audit and preservation tooling

Datum: 2026-10-05

Branch: `claude/storage-preservation-consolidated` = `claude/archive-provenance-preservation` (`6d26bd3`, itself on the architecture plan and the Production Safety Foundation) + merge of `origin/main` (`5512451`, the local-storage audit) + this reconciliation. Not merged into `main`; nothing deployed; no production, `K:` or research-data access.

## Remote verification

- `5512451` is reachable from `origin/main` (pushed there directly, parent `28c63d1`, which is also the merge base of the Claude branches). All five expected files are present: the audit report, `local-storage-hygiene.md`, `storage_inventory.py`, the agent-run report and the spec section.
- The earlier "not on any branch" finding was correct at that time and is now obsolete.

## Findings and changes

| Finding | Resolution |
|---|---|
| Audit and hygiene runbook said migration = verified copy + switch `PROMAT_LOCAL_ARCHIVE_ROOT` to the preservation root; that would make intake write directly to the institutional share | Implementation already separates them (only preservation tools read `PROMAT_PRESERVATION_ROOT`; guarded by a test). Runbooks, spec and a note in the audit report corrected: the local archive stays the working archive |
| Two vocabularies (audit lifecycle vs preservation states) | One model: states per unit, roles per location, mapping documented (`ACTIVE`/`INTAKE_COMPLETE` → `ACTIVE_LOCAL`) |
| Inventory knew only a reachability probe | Read-only integration: env/arg root, root id, quick per-unit states, consumption of the `promat.cleanup_eligibility.v1` JSON (snapshot warning), archive-root entries not covered; no logic duplicated |
| Content outside archive units (`praat_pipeline`, first-generation workbooks, batch workbooks, catalogs) is not copied by the unit tool | Reported (`archive_root_entries_not_covered_by_unit_copy`, `not_covered`), documented as separate operator work; no migration of historical material |
| Conflict | `docs/spec/platform-data-files.md`: both additions kept (my subsections under "Local Archive Filesystem", the audit's "Local Storage Roles And Preservation Root" section) |

## Carried forward, unchanged

Organizer equivalence is not established and neither organizer was touched (prerequisite for German intake). The code fallback for an unset `PROMAT_LOCAL_ARCHIVE_ROOT` was not changed. Measured byte counts live only in the audit report.

## Validation

See the final response of the run; summary: new inventory and preservation tests, canonical suite, ruff, governance checks.
