# PROMAT Copilot Instructions

PROMAT uses a single active spec layer under `docs/spec/` plus lightweight governance.

## Mandatory Context

Before changing architecture, routing, data paths, governance files, or repo structure, consult:

1. `docs/spec/platform-data-files.md`
2. `docs/spec/research-access.md`
3. `docs/spec/research-capabilities.md`
4. `docs/spec/intake-workbook.md`
5. root `AGENTS.md`
6. the relevant scoped `AGENTS.md` in `app/`, `docs/`, or `scripts/`
7. active runtime wiring in `app/src/app/runtime_paths.py`, `app/src/app/config/__init__.py`, `docker-compose.dev-postgres.yml`, and `app/infra/docker-compose.prod.yml`

## Working Rules

- `docs/spec/` is the only active source of truth.
- Update the relevant spec file before or together with any implementation change that affects active rules.
- Do not migrate the recovered productive shell from the accepted `promat-*` shell state to `pm-shell-*`, `pm-topbar*`, or `pm-footer*` without explicit scope plus browser- and screenshot-proven parity on real routes.
- Treat shared app-shell and sidebar-navigation hierarchy as active platform rules; update `docs/spec/platform-data-files.md` when they change, and do not treat old run logs as the current UI contract.
- Treat `sample` as a mirror of current real layout elements, not as an experimental design source; when a represented layout element changes on a real page, update `app/templates/pages/sample_page.html` in the same run.
- Before introducing new UI patterns, inspect the relevant productive pages, shared partials, and shared CSS families first.
- Reuse or extend existing UI families before creating page-local variants for buttons, form controls, badges or chips, cards or list rows, dialogs, empty states, or overflow actions.
- For research UI, treat `comparison` as the primary reference for step containers, selection blocks, badge or meta rhythm, and linear vertical work sequences; treat `player` as the reference for dense material rows, compact work heads, sticky anchors, and muted versus active row states.
- Prefer calm, linear flows over parallel work islands; avoid mini-overlabels, duplicate status blocks, or a second competing surface when the same job is already solved on an existing page.
- For page-level back navigation, reuse the shared compact back-link family: keep it above breadcrumbs and the page-entry heading, align it to the active content axis even when inner header copy stays narrower, use target-only localized labels instead of visible `Zurück`/`Back to` helper phrasing, and do not re-wrap it in `pm-container`, `pm-reading`, or other box-creating helper containers.
- Substantial UI changes require browser validation plus screenshots, and shared or global CSS changes require regression checks on unaffected pages that use the same component family.
- If the user gives an exact UI arrangement, label wording, or screenshot-backed correction, treat that as a hard acceptance target. Do not close the run on a nearby approximation.
- For UI fixes about order, placement, or wording, update focused tests and browser-QA assertions to check the exact requested order and visible labels, not only that the controls still exist.
- If tests and the live browser disagree, assume stale runtime or stale QA assumptions until proven otherwise; verify the active listener and current live HTML before claiming the fix is done.
- For research-access changes, treat `/{ui_lang}/research/{corpus}/design` as the only public corpus-scoped research page unless the active spec says otherwise; all other research pages, detail routes, and player-media routes must gate access before rendering, without corpus-specific exceptions or body-level login CTAs.
- For research architecture changes, keep `app/src/app/research_capabilities.py` aligned with `docs/spec/research-capabilities.md` and remove duplicated capability literals instead of adding new parallel lookups.
- ADRs explain why; runbooks explain how; run logs are never normative.
- Do not create shadow docs, free-form note buckets, or new active rules in run logs.
- `app/` is the only application source root.
- Keep `data/`, `public/`, and `secure/` strictly separated.
- Visible German UI text and maintained German prose headings/labels must use real umlauts and `ß`; keep technical identifiers, filenames, routes, URLs, keys, and machine values ASCII/English unless an active spec explicitly requires otherwise.

## Documentation Rule

- Every substantive run must add an entry under `docs/agent-runs/`.
- Update `docs/decisions/` only for durable architecture decisions.
- Update `docs/runbooks/` only for repeatable procedures.