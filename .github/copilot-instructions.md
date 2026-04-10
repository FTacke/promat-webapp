# PROMAT Copilot Instructions

PROMAT uses a single active spec layer under `docs/spec/` plus lightweight governance.

## Mandatory Context

Before changing architecture, routing, data paths, governance files, or repo structure, consult:

1. `docs/spec/platform-data-files.md`
2. `docs/spec/research-access.md`
3. `docs/spec/intake-workbook.md`
4. root `AGENTS.md`
5. the relevant scoped `AGENTS.md` in `app/`, `docs/`, or `scripts/`
6. active runtime wiring in `app/src/app/runtime_paths.py`, `app/src/app/config/__init__.py`, `docker-compose.dev-postgres.yml`, and `app/infra/docker-compose.prod.yml`

## Working Rules

- `docs/spec/` is the only active source of truth.
- Update the relevant spec file before or together with any implementation change that affects active rules.
- Treat shared app-shell and sidebar-navigation hierarchy as active platform rules; update `docs/spec/platform-data-files.md` when they change, and do not treat old run logs as the current UI contract.
- Treat `sample` as a mirror of current real layout elements, not as an experimental design source; when a represented layout element changes on a real page, update `app/templates/pages/sample_page.html` in the same run.
- ADRs explain why; runbooks explain how; run logs are never normative.
- Do not create shadow docs, free-form note buckets, or new active rules in run logs.
- `app/` is the only application source root.
- Keep `data/`, `public/`, and `secure/` strictly separated.
- Visible German UI text and maintained German prose headings/labels must use real umlauts and `ß`; keep technical identifiers, filenames, routes, URLs, keys, and machine values ASCII/English unless an active spec explicitly requires otherwise.

## Documentation Rule

- Every substantive run must add an entry under `docs/agent-runs/`.
- Update `docs/decisions/` only for durable architecture decisions.
- Update `docs/runbooks/` only for repeatable procedures.