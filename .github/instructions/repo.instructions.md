# PROMAT Repository Guidance

- `docs/spec/platform-data-files.md`, `docs/spec/research-access.md`, and `docs/spec/intake-workbook.md` are the binding sources of truth.
- Root `AGENTS.md` and scoped `AGENTS.md` files govern how changes are made, not the factual product rules themselves.
- Update existing spec files before creating any new active documentation.
- ADRs document why a durable choice was made; runbooks document repeatable procedures; run logs are never normative.
- `app/` is the only application source root.
- Keep `data/`, `public/`, and `secure/` strictly separated.
- Do not create shadow documentation buckets, parallel import contracts, or ad hoc source-of-truth notes.