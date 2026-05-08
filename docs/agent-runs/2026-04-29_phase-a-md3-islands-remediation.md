# 2026-04-29 · Phase A MD3 Islands Remediation

## Scope

- migrate the productive Phenomena rename/form dialog from the remaining MD3 form island onto the PM dialog/form family
- migrate the productive HTML error pages from `md3-error-*` onto the PM error-surface family
- inspect `_md3_skeletons/` and remove unreferenced legacy/QA scaffolds without touching productive auth/session behavior
- reduce MD3 assets only where they became provably unreferenced after those migrations

## Grundsatzentscheidung zu `promat-*`

`promat-*` bleibt das projektspezifische Content-/Reading-/Page-System der Webapp. Es ist in diesem Kontext kein Legacy-System. Phase A zielte ausschließlich auf echte MD3-/Legacy-Inseln und auf generische interaktive Komponenten, die nach `pm-*` überführt werden.

## Ausgangsbefund

- productive Phenomena still had one remaining MD3 island in the overview rename dialog:
  - `md3-dialog`
  - `md3-form`
  - `md3-outlined-textfield*`
- productive HTML error templates still used:
  - `md3-error-page`
  - `md3-error-container`
  - `app/static/css/md3/components/errors.css`
- `_md3_skeletons/` still existed as a mixed bucket of one productive auth base file plus multiple unreferenced demonstration skeletons
- broad `promat-*` page/content/readability classes remained active across project, sample, and research pages and were explicitly out of scope

## Rename/Form Dialog

- migrated `research_phenomena_overview.html` rename markup onto the PM family:
  - `pm-dialog pm-surface-density--spacious`
  - `pm-dialog__header`
  - `pm-dialog__body pm-dialog__body--form`
  - `pm-form`
  - `pm-form-field`
  - `pm-form-label`
  - `pm-form-control`
  - `pm-form-error`
  - `pm-dialog__actions pm-action-row pm-action-row--end`
- kept all existing `data-*` hooks unchanged:
  - `data-phenomena-rename-dialog`
  - `data-phenomena-rename-form`
  - `data-phenomena-rename-input`
  - `data-phenomena-rename-error`
  - `data-phenomena-rename-cancel`
- did not widen the JS architecture; the existing guarded native-dialog lifecycle in `research-phenomena-overview.js` remained sufficient
- focused regression confirmed:
  - no `md3-dialog`, `md3-form`, or `md3-outlined-textfield*` remain in the productive rename dialog slice
  - delete and confirm PM dialogs remain intact

## Error-Surface

- migrated productive `400`, `401`, `403`, `404`, and `500` HTML error templates onto the PM error-surface family
- productive error templates now use:
  - `pm-error-surface`
  - `pm-error-surface__code`
  - `pm-error-surface__title`
  - `pm-error-surface__body`
  - `pm-error-surface__actions`
  - `pm-action-row`
  - `pm-action-button`
- removed the template-level dependency on `css/md3/components/errors.css`
- added missing shared i18n keys for `errors.400.*` in German and English so all productive error pages stay on the shared translation layer
- kept API/HTML error separation unchanged; only the HTML templates and related tests changed
- visually, the productive error pages now use the calmer compact PM error surface rather than the earlier larger MD3 card-like error page

## MD3 Skeletons / QA-Gerüste

- `_md3_skeletons/auth_login_skeleton.html` remains in place because it is still extended productively by:
  - `app/templates/auth/login.html`
  - `app/templates/auth/access_request.html`
  - `app/templates/auth/password_forgot.html`
  - `app/templates/auth/password_reset.html`
- its current content is already a PM/promat auth/page wrapper; the remaining legacy aspect is mainly the folder and file naming, not active MD3 dialog markup
- removed the unreferenced skeleton/demo files:
  - `auth_dialog_skeleton.html`
  - `auth_profile_skeleton.html`
  - `dialog_skeleton.html`
  - `page_admin_skeleton.html`
  - `page_form_skeleton.html`
  - `page_large_form_skeleton.html`
  - `page_text_skeleton.html`
  - `sheet_skeleton.html`
- post-delete reference check found no remaining references to those removed skeleton files

## MD3-CSS-Bestände

- deleted `app/static/css/md3/components/errors.css` after the productive error templates stopped referencing it
- did not blindly remove broader MD3 CSS files because the remaining MD3 inventory is still tied to protected areas outside this slice:
  - auth compatibility CSS and JS still contain MD3 selectors
  - shared base loads broader MD3 token/layout/component assets
  - shell-related `md3-*` classes in `base.html` were explicitly out of scope
- result: Phase A reduced one fully dead productive MD3 CSS file and one group of dead skeleton templates, but intentionally did not force a speculative auth/shell MD3 cleanup

## Geänderte Dateien

- `app/templates/pages/research_phenomena_overview.html`
- `app/tests/test_research_phenomena.py`
- `app/templates/errors/400.html`
- `app/templates/errors/401.html`
- `app/templates/errors/403.html`
- `app/templates/errors/404.html`
- `app/templates/errors/500.html`
- `app/tests/test_auth_phase1.py`
- `app/src/app/i18n.py`
- `app/static/css/md3/components/errors.css` (deleted)
- `app/templates/_md3_skeletons/auth_dialog_skeleton.html` (deleted)
- `app/templates/_md3_skeletons/auth_profile_skeleton.html` (deleted)
- `app/templates/_md3_skeletons/dialog_skeleton.html` (deleted)
- `app/templates/_md3_skeletons/page_admin_skeleton.html` (deleted)
- `app/templates/_md3_skeletons/page_form_skeleton.html` (deleted)
- `app/templates/_md3_skeletons/page_large_form_skeleton.html` (deleted)
- `app/templates/_md3_skeletons/page_text_skeleton.html` (deleted)
- `app/templates/_md3_skeletons/sheet_skeleton.html` (deleted)
- `tmp/ui-qa/phase-a-md3-islands-2026-04-29/capture_phase_a_md3_islands.py`
- `docs/agent-runs/2026-04-29_phase-a-md3-islands-remediation.md`

## Bewusst nicht geänderte Bereiche

- `app/templates/base.html`
- `app/templates/partials/_top_app_bar.html`
- `app/templates/partials/_navigation_drawer.html`
- shell-relevante Footer-Struktur
- `app/static/css/layout.css`
- Shell-Regeln in `20_layout.css` und `30_components.css`
- `promat-*` Content-/Reading-/Page-System
- Auth-/Session-Code und `/auth/refresh`
- Runtime-/Datenmodell und Error-Handler-Architektur

## Tests

- Phenomena:
  - `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_phenomena.py -q` -> `11 passed`
- Auth/Error:
  - `Run auth phase tests` -> `39 passed`
- Research sessions / unaffected shared UI:
  - `Run research sessions tests` -> `185 passed`
- Governance:
  - `c:/dev/promat/.venv/Scripts/python.exe scripts/ci_governance_checks.py` -> `PASS`

## Grep-/Regressionsergebnisse

- forbidden auth refresh frontend paths:
  - `/auth/refresh|initAuthRefresh|token-refresh` -> `NO_MATCHES`
- forbidden legacy research interaction classes:
  - `pm-research-button|pm-research-inline-action` -> `NO_MATCHES`
- shell grep:
  - `pm-shell-|pm-topbar|pm-footer` returned only expected existing shared shell/token/CSS hits; no shell template migration was introduced
- productive error-template dependency:
  - `css/md3/components/errors.css` -> `NO_MATCHES`
- auth skeleton usage:
  - `_md3_skeletons/auth_login_skeleton.html` remains referenced exactly by the four productive auth templates above
- template-level MD3 markup after this run:
  - no productive rename/dialog/error MD3 markup remains
  - the remaining template hits are the out-of-scope shell classes in `base.html` (`md3-content-wrapper`, `md3-footer`)
- `promat-*` inventory:
  - `promat-page`, `promat-content`, and `promat-main-column` remain widely present across productive templates/CSS/tests as intended

## Browser-/Screenshot-Abnahme

- screenshot directory:
  - `tmp/ui-qa/phase-a-md3-islands-2026-04-29/`
- supporting QA report:
  - `tmp/ui-qa/phase-a-md3-islands-2026-04-29/qa_report.json`
- productive live route used:
  - `http://127.0.0.1:8000`
- captured artifacts:
  - `de-phenomena-overview.png`
  - `de-phenomena-rename-open.png`
  - `de-phenomena-rename-saved.png`
  - `de-phenomena-rename-reopen.png`
  - `de-phenomena-rename-open-mobile.png`
  - `de-error-404.png`
  - `en-error-404.png`
  - `de-project-guard.png`
  - `de-sample-guard.png`
  - `de-design-guard.png`
- verified outcomes:
  - rename dialog opens on the productive overview route with visible label/input relationship
  - rename save updates the set label and the dialog can be reopened with the persisted value
  - rename cancel closes the dialog cleanly
  - mobile rename dialog remains readable with stacked actions and intact field labeling
  - German and English 404 pages render on the calmer PM error surface with PM action buttons
  - guard pages `/de/project`, `/de/sample`, and `/de/research/spanish/design` remain visually stable
- limitation:
  - `401`/`403` were covered by focused HTML tests and shared template migration, but not separately screenshot-captured from the live dev server because they are not exposed there as easy standalone productive HTML routes without altering the app for QA
  - `500` was validated through template/test coverage only; no live forced 500 route was introduced for browser QA

## Verbleibende MD3-Treffer und Klassifizierung

- `app/templates/base.html`
  - `md3-content-wrapper`, `md3-footer`
  - classification: out-of-scope shell/runtime classes, explicitly untouched in this phase
- `app/templates/_md3_skeletons/auth_login_skeleton.html`
  - classification: productive auth compatibility filename/base wrapper still extended by four auth pages
- `app/static/css/md3/**`
  - classification: still loaded/shared compatibility CSS; not safely removable in this phase because auth compatibility selectors and shell/base loading still depend on the MD3 asset family
- `app/static/js/auth/password_reset.js` and `app/static/js/modules/auth/login.js`
  - classification: auth compatibility JS still querying MD3-named selectors/classes; out of scope for this run
- negative test assertions mentioning `md3-*`
  - classification: intentional regression coverage, not productive usage

## Offene Folgepunkte

- a later auth-focused cleanup can decide whether `auth_login_skeleton.html` should be renamed out of `_md3_skeletons/` and whether the remaining auth compatibility selectors can move off MD3 naming
- a later shell-safe pass can classify or retire the remaining out-of-scope `md3-content-wrapper` / `md3-footer` shell naming without reopening shell-recovery risk inside this phase
- if Phase B targets auth-compatible MD3 residue, start from the auth templates, auth JS selectors, and the still-loaded MD3 CSS inventory rather than from `promat-*`