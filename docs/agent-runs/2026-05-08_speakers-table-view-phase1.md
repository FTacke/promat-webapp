# 2026-05-08 speakers-table-view-phase1

- Added a cards/table view toggle to the protected `speakers` research page without changing routing, navigation, or the existing `recordings` page.
- Normalized `build_speakers_page(...)` onto one shared person-based result structure used by both the existing cards and the new table rows.
- Preserved selected-session profile links and canonical player task links from the same selected or matching session per person.
- Added bilingual labels and focused regressions for default cards view, `view=table`, invalid view fallback, query preservation, and English table labels.
- Refined the table to hide visible `session_id`, move the compact profile link under `person_id`, and keep the rightmost column as task-only `Aufzeichnungen`/`Recordings` links.
- Tightened the visual layout by switching the profile affordance to a muted text link and giving the speakers table content-driven column widths so the task-pill column keeps more usable space.
- Matched the cards view to the same quieter profile-link language by moving the profile action directly under the identity block and removing the separate profile action strip between metadata and recordings.
- Restored the visible divider and top spacing above the recordings footer on speaker cards and removed the extra bottom divider buffer from that footer so the card closes tighter.
- Updated the active research-access spec to record the new `speakers` view and table semantics.
- Focused validation: targeted `pytest` slice for the affected `speakers` tests passed after one local template-import repair and one query-state cleanup.