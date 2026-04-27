# 2026-04-27 · Interaction-System Phase 2 Legacy Audit · Run 145

## Purpose

This audit records where the old interaction families still exist after the current productive phase-2 migration slice. It is non-normative and complements the active semantic rule in `docs/spec/platform-data-files.md`.

## Replaced In This Run

| File | Previous family | Semantic replacement | Status | Notes |
| --- | --- | --- | --- | --- |
| `app/templates/auth/login.html` | `pm-research-button`, `pm-research-inline-action` | primary action button for submit, navigation pills for secondary links | replaced | Login keeps the leading login icon. |
| `app/templates/auth/access_request.html` | `pm-research-button`, `pm-research-inline-action` | primary action button for submit, navigation pill for login handoff | replaced | Existing form JS hooks preserved. |
| `app/templates/auth/password_forgot.html` | `pm-research-button`, `pm-research-inline-action` | primary action button for submit, navigation pills for back/access links | replaced | No new local control family introduced. |
| `app/templates/auth/password_reset.html` | `pm-research-button`, `pm-research-inline-action` | primary action buttons for reset/request-new-link, navigation pills for back/access links | replaced | Reset state stays bilingual through translations. |
| `app/templates/pages/account.html` | `pm-research-button`, `pm-research-inline-action` | primary action button for save, navigation pill for password route | replaced | Account metadata remains unchanged. |
| `app/templates/auth/account_password.html` | `pm-research-button`, `pm-research-inline-action` | primary action button for submit, navigation pill for back | replaced | Must-reset flow keeps the same form structure. |
| `app/templates/auth/admin_users.html` | `pm-research-button`, `pm-research-inline-action` | action buttons by hierarchy, chip toggle left unchanged | replaced | Toolbar, invite dialog, edit dialog, and reset-password action migrated. |
| `app/templates/pages/research_player.html` | `pm-research-button`, `pm-research-inline-action` | navigation pills for back/profile/reference navigation, action buttons for compare/remove/fallback actions | replaced in touched slice | Player task chooser stays a selection component via `pm-material-choice`. |
| `app/templates/pages/research_speaker_profile.html` | `pm-research-inline-action` | navigation pill | replaced | Back-to-speakers link now matches speaker/player navigation semantics. |
| `app/templates/pages/sample_page.html` | mixed old button and inline-action families in mirrored sections | mirrored CTA links, nav pills, and action buttons | replaced in mirrored slices | Sample now matches the changed productive elements from this run. |
| `app/templates/pages/research_comparison.html` | `pm-research-inline-action` | secondary workbench clear-filter action | secondary action button | replaced | Filter chips and session selectors stayed separate workbench selection components. |
| `app/templates/pages/research_phenomena_overview.html` | `pm-research-button`, `pm-research-inline-action` | create, view, edit, and modify controls | primary/secondary action buttons plus small nav pills | replaced | Overflow rename/delete controls stay in the existing overflow menu family. |
| `app/templates/pages/research_phenomena_editor.html` | `pm-research-button`, `pm-research-inline-action` | discard, save, select-all, clear-all | action buttons | replaced | Dense editor actions now use the semantic action family under existing JS hooks. |
| `app/templates/pages/research_player_stub.html` | `pm-research-button`, `pm-research-inline-action` | stub navigation links | navigation pills | replaced | Stub now mirrors the productive navigation semantics instead of the retired generic action family. |

## Remaining Legacy Usage

- No productive template, productive runtime-JS, or active shared CSS selector usage of `pm-research-button` or `pm-research-inline-action` remains after the later dead-CSS cleanup pass.
- Repo grep after the cleanup leaves only historical documentation references to the retired class names.

## Mapping Summary

- `pm-research-button` for submit, save, refresh, create, compare, modify, reset, and close actions maps to `pm-action-button` unless the control is a specialized workbench transport control.
- `pm-research-inline-action` for compact navigation routes maps to `pm-nav-pill`.
- Editorial card footers map to `pm-cta-link` or `pm-cta-link` visual rendering inside already-clickable cards.
- Chips, tabs, filter toggles, and task-selection states remain separate selection components and should not be migrated into the button hierarchy.

## Open Questions

- The dead-CSS cleanup for the retired interaction families is complete for the current codebase state.
- If future work expands the player transport family, it should keep using player-specific control classes rather than collapsing media controls into the generic semantic action-button hierarchy.
