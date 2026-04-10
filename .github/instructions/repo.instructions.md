# PROMAT Repository Guidance

- `docs/spec/platform-data-files.md`, `docs/spec/research-access.md`, and `docs/spec/intake-workbook.md` are the binding sources of truth.
- Root `AGENTS.md` and scoped `AGENTS.md` files govern how changes are made, not the factual product rules themselves.
- Update existing spec files before creating any new active documentation.
- Shared app-shell and sidebar-navigation hierarchy count as active platform rules; update `docs/spec/platform-data-files.md` when they change, and do not rely on old run logs as the current UI source of truth.
- `sample` mirrors current accepted layout elements and is never the upstream design source; when a represented layout element changes on a real page, update `app/templates/pages/sample_page.html` in the same run.
- ADRs document why a durable choice was made; runbooks document repeatable procedures; run logs are never normative.
- `app/` is the only application source root.
- Keep `data/`, `public/`, and `secure/` strictly separated.
- Visible German UI text and maintained German prose headings/labels must use real umlauts and `ß`; keep technical identifiers, filenames, routes, URLs, keys, and machine values ASCII/English unless an active spec explicitly requires otherwise.
- Do not create shadow documentation buckets, parallel import contracts, or ad hoc source-of-truth notes.