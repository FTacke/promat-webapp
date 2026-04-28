# Designsystem PM Canonical Remediation

## Scope

- Step 3 remediation slice for shared shell canonicalization.
- Productive shared app shell only: `base.html`, topbar, navigation drawer, footer, shared shell CSS, and focused shell regressions.
- Dead legacy auth templates and page scripts that were no longer referenced anywhere in productive routing or template wiring.

## Ausgangsbefund

- `app/templates/base.html` still rendered the productive shell with `md3-content-wrapper`, `promat-main-column`, and `md3-footer` while also loading the numbered canonical CSS stack.
- The productive shared partials `_top_app_bar.html`, `_navigation_drawer.html`, and `footer.html` still emitted `promat-*` shell classes as first-class markup.
- The numbered shared CSS already carried a mixed compatibility layer, but the productive shell markup itself was not yet canonical `pm-*`.
- Legacy account templates `auth/account_profile.html` and `auth/account_delete.html` plus `app/static/js/auth/account_profile.js`, `account_delete.js`, and `account_password.js` were no longer referenced by productive routing or productive templates.

## Entscheidungen

- Canonicalize the productive shared shell markup to `pm-*` now, but keep compatibility aliases in shared CSS so the remaining unmigrated `promat-*` surfaces do not break.
- Do not remove the MD3 stylesheet stack from `base.html` in this pass. The cheap discriminating check showed that remaining productive or QA-classified surfaces still depend on MD3 dialog, textfield, button, and typographic primitives that are only partially mirrored in the numbered CSS files.
- Delete dead legacy auth templates and their page scripts instead of retaining them as localized but unreachable ballast.
- Keep remaining `promat-*` page/content families and remaining MD3 workbench primitives explicitly classified for follow-up rather than widening this pass into a broad page-by-page rewrite.

## Inventur: pm-*, md3-*, promat-*

- `pm-*` is already the active productive card, interaction, and research component family across landing, account, corpus cards, speaker cards, and most workbench surfaces.
- `promat-*` was still the active productive shell family before this pass for topbar, drawer, footer, shell wrappers, and many page/content helpers.
- `md3-*` remains present in three main buckets:
  - compatibility selectors inside numbered CSS (`10_typography.css`, `30_components.css`, `40_cards.css`)
  - productive-but-unmigrated workbench/admin/error primitives such as dialogs, textfields, and legacy text sections
  - `_md3_skeletons/` QA or legacy scaffold templates

## Geänderte Dateien

- `app/templates/base.html`
- `app/templates/partials/_top_app_bar.html`
- `app/templates/partials/_navigation_drawer.html`
- `app/templates/partials/footer.html`
- `app/static/css/layout.css`
- `app/static/css/20_layout.css`
- `app/static/css/30_components.css`
- `app/tests/test_auth_phase1.py`
- `app/tests/test_research_sessions.py`
- deleted: `app/templates/auth/account_profile.html`
- deleted: `app/templates/auth/account_delete.html`
- deleted: `app/static/js/auth/account_profile.js`
- deleted: `app/static/js/auth/account_delete.js`
- deleted: `app/static/js/auth/account_password.js`

## CSS-Load-Order

- The numbered canonical CSS stack remains the intended primary system layer.
- In this pass, `base.html` load order was intentionally not reduced yet.
- Reason: the productive codebase still contains MD3 dialog, textfield, button, and typography primitives on admin, error, and research-phenomena surfaces, and the numbered CSS files only partially cover those compatibility needs.
- Result: shell markup is now canonicalized first, while MD3 stylesheet removal is deferred until those remaining primitives are explicitly absorbed or migrated.

## Migrierte Templates

- `base.html` now emits `pm-shell-layout`, `pm-shell-main`, and `pm-shell-footer` as the productive shell wrappers.
- `_top_app_bar.html` now emits `pm-topbar*`, `pm-site-title*`, and `pm-user-menu*` classes.
- `_navigation_drawer.html` now emits `pm-panel*` classes for productive drawer markup.
- `footer.html` now emits `pm-footer*` classes.

## Migrierte oder entfernte CSS-Familien

- `layout.css` and `20_layout.css` now alias the shell wrapper layout to `pm-shell-*` without breaking the older wrapper names still referenced elsewhere.
- `30_components.css` now treats `pm-topbar*`, `pm-panel*`, `pm-user-menu*`, and `pm-footer*` as first-class aliases for the older shell selectors.
- No MD3 compatibility family was removed from the numbered CSS in this pass.

## Legacy-Assets gelöscht oder klassifiziert

- Deleted as dead legacy:
  - `app/templates/auth/account_profile.html`
  - `app/templates/auth/account_delete.html`
  - `app/static/js/auth/account_profile.js`
  - `app/static/js/auth/account_delete.js`
  - `app/static/js/auth/account_password.js`
- Verified deletion condition: after removal, grep found no remaining references to those file paths or script names under `app/{src,templates,static/js,tests}`.

## Public-/Sample-/Stub-Klassifizierung

- `app/templates/pages/sample_page.html`: still intentionally mirrors current productive page/content families and still contains `promat-page*` helpers. Not migrated in this shell pass.
- `app/templates/pages/research_player_stub.html`: still contains visible `if ui_lang == 'de'` branches and `promat-page*` wrappers. Classified as follow-up, not touched here.
- `app/src/app/routes/public.py` and `app/src/app/routes/public_content.py`: still contain many direct `if ui_lang == "de"` branches for public/sample content payloads. Classified as content/i18n follow-up, not a shell pass target.
- `app/src/app/research_capabilities.py`: remaining language branching is capability-data related and was not treated as Step 3 shell cleanup.

## Tests

- Focused validation first: `Run focused research root test` -> `1 passed`.
- Full research suite after shell canonicalization: `Run research sessions tests` -> `182 passed`.
- Full auth suite after shell canonicalization and dead-legacy deletion: `Run auth phase tests` -> `37 passed`.

## Grep-/Regressionsergebnisse

- `pm-research-button|pm-research-inline-action`: no matches under `app/{templates,static,src,tests}`.
- Deleted legacy auth files: no remaining references after deletion.
- Productive shell test expectations now assert `pm-topbar*` and `pm-panel*` markup instead of `promat-topbar*` / `promat-panel*`.
- `md3-card|promat-card|pm-card` grep confirms `pm-card` is the active productive card family, while `promat-card` and `md3-card` still survive as compatibility or legacy buckets.
- Shared numbered CSS still contains deliberate compatibility selectors and some hardcoded color tokens / `!important` usage; those were inventoried, not broadened in this pass.

## Verbleibende bewusst klassifizierte Legacy-Treffer

- `base.html` still loads the MD3 stylesheet stack because the remaining workbench/admin/error primitives are not yet fully absorbed by the numbered CSS.
- `app/templates/pages/admin_dashboard.html` still uses MD3 text-section and button primitives.
- `app/templates/pages/research_phenomena_overview.html` and `app/templates/pages/research_phenomena_editor.html` still use MD3 dialog, button, form, and textfield primitives.
- Error templates still load `css/md3/components/errors.css` and keep MD3 error-page primitives.
- `_md3_skeletons/` remains as explicit legacy/QA scaffold territory.
- Productive page/content helpers still have many `promat-page*`, `promat-content-*`, and `promat-card*` aliases across page templates and numbered CSS.

## Offene Folgepunkte ...

- Migrate or absorb the remaining MD3 dialog, textfield, button, and typography primitives into the numbered CSS so the MD3 base stack can be removed from `base.html` safely.
- Canonicalize the remaining `promat-page*` and `promat-content-*` page/content families on productive pages and mirrored `sample` surfaces.
- Replace remaining public/sample/stub `if ui_lang == "de"` branches with translation-layer or localized payload wiring where those surfaces are part of the active finished UI.
- Run a real browser screenshot pass for the changed shell routes; the integrated browser could be opened in this run, but page contents and screenshots were not inspectable from chat tools in this session.