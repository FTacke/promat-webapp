# Designsystem Shell Regression Recovery

## Scope

- recovery slice for the visually regressive shared-shell canonicalization from Step 3
- productive shared shell only: `base.html`, topbar, navigation drawer, footer, shell wrapper CSS, and shell-specific regression assertions
- keep Step 1 auth/session stabilization, Step 2 and 2b i18n consolidation, later non-shell layout/card/literature improvements, and still-unreferenced legacy auth deletions

## Ausgangsbefund

- the productive shell had been moved from the accepted `md3-content-wrapper` / `promat-*` shell markup to `pm-shell-*`, `pm-topbar*`, `pm-panel*`, and `pm-footer*`
- shared CSS added alias selectors for the new shell class family in `layout.css`, `20_layout.css`, and `30_components.css`
- pytest still passed, but the visible shell drifted in topbar rhythm, sidebar containment, active nav treatment, borders, spacing, and footer/layout parity
- the user clarified the recovery target explicitly: visual parity beats class-name canonicalization; do not roll back unrelated improvements or already accepted earlier remediation slices

## Entscheidung: Parität vor Kanonisierung

- restore the productive shell markup to the previously accepted wrapper and `promat-*` shell classes
- remove only the shell alias additions that existed to support the `pm-*` shell conversion
- keep unrelated same-session changes outside the shell slice, including literature list styling, team-card spacing, shared card hover behavior, material-choice consolidation, auth i18n, and the admin settings icon support
- keep deleted legacy auth templates/scripts deleted as long as no productive references remain

## Zurückgesetzte Shell-Dateien

- `app/templates/base.html`
- `app/templates/partials/_top_app_bar.html`
- `app/templates/partials/_navigation_drawer.html`
- `app/templates/partials/footer.html`
- `app/tests/test_auth_phase1.py`
- shell-only assertions in `app/tests/test_research_sessions.py`

## Zurückgesetzte oder bereinigte CSS-Änderungen

- `app/static/css/layout.css`: removed the temporary `.pm-shell-layout`, `.pm-shell-main`, and `.pm-panel--standard .pm-panel__inner` shell alias selectors
- `app/static/css/20_layout.css`: removed the temporary `.pm-shell-layout` wrapper aliases while keeping the later literature and team-grid changes
- `app/static/css/30_components.css`: removed the temporary shell alias selectors for `pm-topbar*`, `pm-panel*`, `pm-user-menu*`, and `pm-footer*` while keeping unrelated later changes such as the settings icon support, auth secondary border, and non-shell component adjustments

## Beibehaltene Änderungen aus 1/4, 2/4 und 2b/4

- Step 1 auth/session and app-factory stabilization remains intact
- Step 2 shared/footer/error/research i18n consolidation remains intact
- Step 2b account/auth i18n cleanup remains intact
- non-shell follow-up improvements in `00_tokens.css`, `20_layout.css`, `40_cards.css`, `promat_page.html`, and `public_page_content_data.py` were not rolled back

## Gelöschte Legacy-Dateien: erneut geprüft

- rechecked for references to:
  - `account_profile.html`
  - `account_delete.html`
  - `account_profile.js`
  - `account_delete.js`
  - `account_password.js`
- result: no remaining matches under `app/**`
- decision: keep those legacy files deleted

## Tests

- focused guard first: `Run focused research root test` -> `1 passed`
- post-CSS focused rerun: `Run focused research root test` -> `1 passed`
- full auth regression: `Run auth phase tests` -> `37 passed`
- full research regression: `Run research sessions tests` -> `182 passed`

## Grep-/Regressionsergebnisse

- no matches for `/auth/refresh|initAuthRefresh|token-refresh` under `app/**`
- no matches for `refreshToken` under `app/static/**`, `app/templates/**`, or `app/src/app/routes/**`
- no matches for `pm-research-button|pm-research-inline-action` under `app/**`
- no matches for direct `if ui_lang == 'de'` / `if ui_lang == "de"` branches in `app/templates/auth/**` or `app/src/app/research_views.py`

## Browser-/Screenshot-Abnahme

- verified local runtime reachable on `http://127.0.0.1:8000`
- captured and reviewed headless Edge screenshots under `tmp/ui-qa/shell-recovery-2026-04-28/`
- reviewed routes:
  - `/de/project`
  - `/de/project/team`
  - `/de/sample`
  - `/de/research/spanish/design`
  - productive login route `/login?next=/de/project`
- result:
  - topbar utility order remains language switch -> theme switch -> account/login
  - project, sample, and research pages show the expected left sidebar shell with the accepted section/language header rhythm
  - muted locked research sidebar entries keep the label-first plus trailing-lock ordering
  - active nav state, content containment, divider rhythm, and footer shell read consistently with the accepted productive shell
  - `/de/login` is not the productive auth route and returns 404; browser acceptance therefore used the actual localized login surface on `/login?next=/de/project`

## Offene Folgepunkte für 3a/4

- if shell canonicalization resumes in Step 3a, do it additively: keep productive visuals stable first, introduce parity-safe dual classes if needed, and remove old shell classes only after screenshot-proven parity on real routes
- keep shell migration separate from unrelated design-system cleanup so visual regressions are attributable to a small, browser-verifiable slice