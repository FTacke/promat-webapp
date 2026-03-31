# PROMAT Copilot Instructions

PROMAT uses a binding repo specification plus operational governance. Read the relevant rules before making structural changes.

## Mandatory Context

Before changing architecture, routing, data paths, governance files, or repo structure, consult:

1. `docs/PROMAT_ Plattform-, Daten- und Filestruktur.md`
2. root `AGENTS.md`
3. the relevant scoped `AGENTS.md` in `app/`, `docs/`, or `scripts/`
4. active runtime wiring in `app/src/app/runtime_paths.py`, `app/src/app/config/__init__.py`, `docker-compose.dev-postgres.yml`, and `app/infra/docker-compose.prod.yml`

## Working Rules

- Keep the bootstrap small, explicit, and maintainable.
- `app/` is the only application source root.
- `data/` is protected research data, `public/` is explicitly released media, `secure/` is never for webapp access.
- Technical keys, slugs, route segments, data fields, and controlled vocabularies are English only.
- UI chrome is currently German and must stay separable from technical keys.
- Do not reintroduce old German technical slugs, old public routes, or legacy runtime paths.
- Use `AUTH_DATABASE_URL`, `PROMAT_RUNTIME_ROOT`, and `PROMAT_PUBLIC_ROOT` as canonical runtime variables.
- Do not mix raw data, derived data, and public assets.
- Think Dev and Prod as the same architecture with minimal documented environment-only differences.
- Do not make silent architecture decisions; update governance and documentation in the same run.

## Documentation Rule

- Every substantive run must add an entry under `docs/agent-runs/`.
- Bootstrap, setup, governance, or repo-structure runs must also update `docs/start/`.