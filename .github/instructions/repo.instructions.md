# PROMAT Repository Guidance

- `docs/spec/platform-data-files.md`, `docs/spec/research-access.md`, and `docs/spec/intake-workbook.md` are the binding sources of truth.
- Root `AGENTS.md` and scoped `AGENTS.md` files govern how changes are made, not the factual product rules themselves.
- Update existing spec files before creating any new active documentation.
- Shared app-shell and sidebar-navigation hierarchy count as active platform rules; update `docs/spec/platform-data-files.md` when they change, and do not rely on old run logs as the current UI source of truth.
- `sample` mirrors current accepted layout elements and is never the upstream design source; when a represented layout element changes on a real page, update `app/templates/pages/sample_page.html` in the same run.
- For substantial UI changes, follow `docs/runbooks/ui-change-workflow.md` in addition to the binding specs and AGENTS files.
- Before building new UI markup, CSS, or client interaction, inspect the relevant productive pages, shared partials, and existing CSS families.
- Reuse or extend existing UI families before creating page-local variants for buttons, inputs, selects, textareas, badges, chips, cards, list rows, dialogs, empty states, sticky anchors, or overflow actions.
- For research workbench UI, use `comparison` as the reference for step containers, selection blocks, badge or meta rhythm, and clear vertical flows; use `player` as the reference for dense list rows, compact work heads, sticky anchors, and muted versus active row states.
- Prefer calm, linear flows over parallel work islands; avoid extra mini-headings or a second competing surface when the same job is already solved on an existing page.
- Shared CSS changes are high-risk and require regression checks on unaffected pages that use the same family; visually substantial UI changes also require browser validation and screenshots.
- ADRs document why a durable choice was made; runbooks document repeatable procedures; run logs are never normative.
- `app/` is the only application source root.
- Keep `data/`, `public/`, and `secure/` strictly separated.
- Visible German UI text and maintained German prose headings/labels must use real umlauts and `ß`; keep technical identifiers, filenames, routes, URLs, keys, and machine values ASCII/English unless an active spec explicitly requires otherwise.
- Do not create shadow documentation buckets, parallel import contracts, or ad hoc source-of-truth notes.