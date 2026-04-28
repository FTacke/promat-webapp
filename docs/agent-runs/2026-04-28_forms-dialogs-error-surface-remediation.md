# Forms, Dialoge und Error-Surface Remediation 3b

## Scope

- evaluate the remaining non-shell legacy islands from 3a and migrate only what can be proven safe without introducing a new shared PM family
- keep the recovered productive shell and all shell-owned files untouched
- prefer classification over half-migration for Phenomena dialogs/forms/textfields and the HTML error surface

## Consulted Sources

- `docs/spec/platform-data-files.md`
- `docs/spec/research-access.md`
- `docs/spec/research-capabilities.md`
- `docs/spec/intake-workbook.md`
- `AGENTS.md`
- `app/AGENTS.md`
- `docs/AGENTS.md`
- `scripts/AGENTS.md`
- `docs/runbooks/ui-change-workflow.md`
- `/memories/repo/promat-research-ui-notes.md`

## Ausgangsbefund

- `app/templates/pages/research_phenomena_overview.html` and `app/templates/pages/research_phenomena_editor.html` still use active `md3-dialog*` structure, and the overview rename flow still depends on `md3-form` plus `md3-outlined-textfield*`
- `app/templates/errors/*.html` still use `md3-error-*` structure and explicitly load `css/md3/components/errors.css`
- repo-wide inventory showed no established productive `pm-dialog`, `pm-form`, `pm-textfield`, `pm-textarea`, `pm-form-field`, or `pm-error` family; only `pm-form-action-row` exists in the PM interaction layer
- `app/src/app/research_views.py` now returns `pages/research_player.html` for the active player route, while an exact reference search for `research_player_stub.html` across `app/**` returned `NO_MATCHES`

## Geänderte Dateien

- deleted: `app/templates/pages/research_player_stub.html`
- `docs/agent-runs/2026-04-28_forms-dialogs-error-surface-remediation.md`

## Wichtige Entscheidungen

- do not migrate the productive Phenomena dialog/form/textfield slice in 3b
- do not migrate the productive HTML error surface in 3b
- delete the unreferenced `research_player_stub.html` instead of migrating its local language branches

## Entscheidungsbegründung

### Phenomena / Dialoge / Forms

- the active Phenomena JS hooks are data-attribute based, but the rendered structure still depends on the MD3 dialog and MD3 textfield family
- a real migration would require introducing or standardizing a PM dialog/form/textfield family that does not yet exist in the productive system
- 3b therefore keeps:
  - `md3-dialog*` in `research_phenomena_overview.html`
  - `md3-form` and `md3-outlined-textfield*` in the rename dialog
  - `md3-dialog*` in `research_phenomena_editor.html`
- decision: classify as an explicit later migration boundary instead of inventing a new shared family inside a narrow cleanup slice

### Error-Surface

- the HTML error pages already use PM action buttons, but their owning surface is still `md3-error-*` plus `css/md3/components/errors.css`
- there is no existing PM error-page surface family to migrate onto
- `app/static/css/md3/components/errors.css` still owns not only error layout but also page-level background behavior and legacy helper classes such as `md3-error-text`, `md3-empty-state`, `md3-error-card`, and `md3-offline-banner`
- decision: keep the error pages and `errors.css` deliberately classified as an isolated MD3 island until a dedicated PM error-surface family is defined

### Player Stub

- `research_player_stub.html` is not referenced anywhere under `app/**`
- active player rendering now points to `pages/research_player.html`
- decision: delete the dead stub rather than migrating its inline `ui_lang` branches or preserving an unused fallback surface

## Shell-Schutz

- no edits to `app/templates/base.html`, `app/templates/partials/_top_app_bar.html`, `app/templates/partials/_navigation_drawer.html`, `app/templates/partials/footer.html`, `app/static/css/layout.css`, `app/static/css/20_layout.css`, or `app/static/css/30_components.css`
- raw shell grep for `pm-shell-|pm-topbar|pm-footer` returned only accepted CSS token references in `layout.css` and `30_components.css`
- no new shell template-class migration hits were introduced

## Verifikation

- `Run auth phase tests` -> `37 passed`
- `Run research sessions tests` -> `182 passed`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_phenomena.py -q` -> `11 passed`
- `c:/dev/promat/.venv/Scripts/python.exe c:/dev/promat/scripts/ci_governance_checks.py` -> `PASS`
- exact post-delete reference search for `research_player_stub.html` across `app/**` -> `NO_MATCHES`
- `git -C c:/dev/promat status --short` after the cleanup showed only:
  - `D app/templates/pages/research_player_stub.html`

## Grep-/Regressionsergebnisse

- `/auth/refresh|initAuthRefresh|token-refresh` under `app/static`, `app/src`, `app/templates`, `app/tests` -> `NO_MATCHES`
- `pm-research-button|pm-research-inline-action` under `app/templates`, `app/static`, `app/src`, `app/tests` -> `NO_MATCHES`
- local `if ui_lang == 'de'` inventory in `app/templates/auth` and `app/src/app/research_views.py` -> `NO_MATCHES`
- remaining productive MD3 island inventory stays intentionally confined to:
  - `app/templates/pages/research_phenomena_overview.html`
  - `app/templates/pages/research_phenomena_editor.html`
  - `app/templates/errors/400.html`
  - `app/templates/errors/401.html`
  - `app/templates/errors/403.html`
  - `app/templates/errors/404.html`
  - `app/templates/errors/500.html`
  - `app/static/css/md3/components/errors.css`
- additional MD3 hits remain in `app/static/css/md3/**`, compatibility selectors, and `_md3_skeletons/`; these were inventory-only and untouched in 3b

## Browser-Abnahme

- no browser or screenshot pass was executed in 3b
- reason: no visible productive route template was changed; the only code change was deleting an unreferenced dead stub template
- if a later slice migrates active Phenomena dialogs/forms or the active error surface, a real browser pass and screenshots remain mandatory

## Abweichungen

- no active spec change was needed because no routing, access, shell, or runtime rule changed
- 3b intentionally stops short of a broader design-system migration and records the remaining active MD3 boundaries explicitly instead

## Offene Folgepunkte

- define a real productive PM dialog/form/textfield family before attempting a full Phenomena migration
- define a real productive PM error-page surface before replacing `md3-error-*` and `css/md3/components/errors.css`
- if broader MD3 cleanup resumes later, keep the productive shell frozen and migrate one family at a time with focused tests plus browser proof