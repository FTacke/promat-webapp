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
- `docs/plans/` are planning inputs only; when a plan is superseded by active spec or implementation, add a clear status note or retire it instead of letting it compete with `docs/spec/`.
- Run logs in `docs/agent-runs/` are non-normative work journals only.
- Delete or merge obsolete documentation instead of preserving shadow copies.

## UI Change Discipline

- Before introducing new UI markup, CSS, or client-side interaction, inspect matching productive pages, shared partials, and shared CSS families in `app/templates/` and `app/static/css/`.
- Reuse or extend existing UI families before creating feature-local variants for buttons, form controls, badges or chips, cards or list rows, dialogs, empty states, sticky anchors, or overflow actions.
- Prefer calm, linear flows over parallel work islands; avoid mini-overlabels, duplicate status blocks, and mixed one-page workbenches unless the active spec explicitly requires them.
- For research UI, use `comparison` as the default reference for step containers, selection blocks, badge or meta rhythm, and vertical work sequences; use `player` as the default reference for dense material rows, compact work heads, sticky anchors, and muted versus active states.
- If shared CSS files or shared partials change, regression-check at least one unaffected page that uses the same component family.
- Any substantial UI change requires a browser pass and screenshots before completion; if a mirrored element exists in `sample`, update it in the same run.

## Change Discipline

- If routing, data paths, IDs, vocabularies, research-access logic, or intake rules change, update the relevant file in `docs/spec/` in the same run.
- If the shared app-shell or navigation hierarchy changes, update the active rule in `docs/spec/platform-data-files.md` in the same run.
- If an active layout element changes on a real page and `sample` contains that element, update `app/templates/pages/sample_page.html` in the same run.
- If a durable architectural decision is accepted, add or update an ADR in `docs/decisions/`.
- If a repeatable workflow changes, add or update the relevant runbook in `docs/runbooks/`.
- Every substantive run adds one entry under `docs/agent-runs/`.

## No-Go

- No new shadow documentation buckets.
- No silent architecture decisions without spec updates.
- No webapp access to `secure/`.
- No direct public delivery from `data/`.