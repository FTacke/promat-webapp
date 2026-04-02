# PROMAT Repo Governance

## Binding Sources

For active PROMAT rules, consult these files first:

1. `docs/spec/platform-data-files.md`
2. `docs/spec/research-access.md`
3. `docs/spec/intake-workbook.md`
4. relevant scoped `AGENTS.md`
5. runtime wiring in `app/src/app/runtime_paths.py`, `app/src/app/config/__init__.py`, `docker-compose.dev-postgres.yml`, and `app/infra/docker-compose.prod.yml`

`docs/spec/` is the only active source of truth for current factual rules.

## Core Repo Rules

- `app/` is the only application source root.
- `data/`, `public/`, and `secure/` keep their strict runtime boundaries.
- Technical keys, slugs, routes, field names, and controlled vocabularies stay English.
- User-visible German text stays separable from technical keys and uses real umlauts and `ß`.
- Do not reintroduce old German technical slugs, legacy runtime paths, or old public routes.
- Do not introduce Dev-only shadow architectures or fallback data stores.

## Documentation Rules

- Update an existing file under `docs/spec/` before creating any new active documentation.
- Do not place active rules in run logs, ADRs, folder READMEs, or ad hoc notes.
- ADRs in `docs/decisions/` explain why a decision was taken; they do not replace current specs.
- Runbooks in `docs/runbooks/` document repeatable procedures only.
- Run logs in `docs/agent-runs/` are non-normative work journals only.
- Delete or merge obsolete documentation instead of preserving shadow copies.

## Change Discipline

- If routing, data paths, IDs, vocabularies, research-access logic, or intake rules change, update the relevant file in `docs/spec/` in the same run.
- If the shared app-shell or navigation hierarchy changes, update the active rule in `docs/spec/platform-data-files.md` in the same run.
- If a durable architectural decision is accepted, add or update an ADR in `docs/decisions/`.
- If a repeatable workflow changes, add or update the relevant runbook in `docs/runbooks/`.
- Every substantive run adds one entry under `docs/agent-runs/`.

## No-Go

- No new shadow documentation buckets.
- No silent architecture decisions without spec updates.
- No webapp access to `secure/`.
- No direct public delivery from `data/`.