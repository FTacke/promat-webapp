# PROMAT Repo Governance

## Binding Sources

For active PROMAT rules, consult these files first:

1. `docs/spec/platform-data-files.md`
2. `docs/spec/research-access.md`
3. `docs/spec/research-capabilities.md`
4. `docs/spec/intake-workbook.md`
5. relevant scoped `AGENTS.md`
6. runtime wiring in `app/src/app/runtime_paths.py`, `app/src/app/config/__init__.py`, `docker-compose.dev-postgres.yml`, and `app/infra/docker-compose.prod.yml`

`docs/spec/` is the only active source of truth for current factual rules.

## Core Repo Rules

- `app/` is the only application source root.
- `data/`, `public/`, and `secure/` keep their strict runtime boundaries.
- Research intake is separate from Teaching import or publication work; do not route research intake changes through `content/`, `content/teaching/`, or `public/teaching/`.
- Teaching is a fully public editorial surface separate from Research; do not route it through research auth, protected player delivery, owner-bound set state, or `data/` paths.
- Teaching content stays under `content/teaching/...`, and released Teaching media stays under `public/teaching/...` with public delivery only from the public-root boundary.
- Technical keys, slugs, routes, field names, and controlled vocabularies stay English.
- User-visible German text stays separable from technical keys and uses real umlauts and `ß`.
- Do not reintroduce old German technical slugs, legacy runtime paths, or old public routes.
- Do not introduce Dev-only shadow architectures or fallback data stores.
- `data/sessions/` is runtime-only for final research JSON/MP3 artifacts; do not copy WAV, TextGrid, XLSX, `secure/`, `raw/`, `source/`, or other intake/intermediate trees into it.
- The local research archive lives outside the repo under `PROMAT_LOCAL_ARCHIVE_ROOT`; do not create a second in-repo archive root.
- Prod upload packages are explicit allowlist exports from validated runtime artifacts and optional import payloads; do not ship WAV, TextGrid, XLSX, `secure/`, `raw/`, `source/`, or batch working files in them.
- Research intake must not invent metadata, task mappings, or audio provenance heuristically when filename-driven classification is missing or ambiguous.

## Documentation Rules

- Update an existing file under `docs/spec/` before creating any new active documentation.
- Do not place active rules in run logs, ADRs, folder READMEs, or ad hoc notes.
- ADRs in `docs/decisions/` explain why a decision was taken; they do not replace current specs.
- Runbooks in `docs/runbooks/` document repeatable procedures only.
- `docs/plans/` are planning inputs only; when a plan is superseded by active spec or implementation, add a clear status note or retire it instead of letting it compete with `docs/spec/`.
- Run logs in `docs/agent-runs/` are non-normative work journals only.
- Delete or merge obsolete documentation instead of preserving shadow copies.

## Repo Hygiene For Temporary QA Debug Files

- Do not create temporary screenshots, browser-capture artifacts, inspect scripts, measurement scripts, or ad hoc debug files in the repository root.
- Keep `start.txt` in the repository root as a tracked local dev helper entrypoint; do not delete it as temporary hygiene debris.
- Use `tmp/ui-qa/<YYYY-MM-DD>-<short-topic>/` for one-off browser screenshots, HTML dumps, debug captures, and run-specific inspection scripts.
- Use `scripts/qa/` for reusable QA or capture utilities that are intended to be kept.
- Use `docs/agent-runs/` for short Markdown run reports instead of keeping root notes or screenshot evidence in the root.
- Before finishing a run, check the repository root for accidental files such as `inspect_*.py`, `tmp_*.py`, `measure_*.py`, `verify_*.py`, `capture_*.py`, `*_screenshot.png`, `desktop_*.png`, and `mobile_*.png`, then move, delete, or document them before handoff.

## UI Change Discipline

- Before introducing new UI markup, CSS, or client-side interaction, inspect matching productive pages, shared partials, and shared CSS families in `app/templates/` and `app/static/css/`.
- Reuse or extend existing UI families before creating feature-local variants for buttons, form controls, badges or chips, cards or list rows, dialogs, empty states, sticky anchors, or overflow actions.
- Finished visible surfaces under the active public language set must be completed in `de` and `en` together; do not treat English as a later copy pass for already-finished UI.
- Visible UI copy for finished surfaces must resolve through the shared translation layer or server-injected localized payloads; do not leave hardcoded visible strings or local `de`/`en` branches in Python builders, templates, or page JS.
- Prefer calm, linear flows over parallel work islands; avoid mini-overlabels, duplicate status blocks, and mixed one-page workbenches unless the active spec explicitly requires them.
- For research UI, use `comparison` as the default reference for step containers, selection blocks, badge or meta rhythm, and vertical work sequences; use `player` as the default reference for dense material rows, compact work heads, sticky anchors, and muted versus active states.
- If shared CSS files or shared partials change, regression-check at least one unaffected page that uses the same component family.
- Any substantial UI change requires a browser pass and screenshots before completion; if the changed shared UI family appears on multiple real routes, update and re-check those routes in the same run.
- Browser acceptance for finished bilingual surfaces must cover the real app routes in both `de` and `en`, including dialogs, placeholders, empty states, overflow actions, and longer English labels where they affect layout.
- Do not close substantial UI runs on green tests alone; fix and re-check until the browser screenshots are linguistically and visually clean for the in-scope surfaces.
- If the user asks for an exact visual order, placement, or wording, that exact arrangement is the acceptance target for the run. A similar layout is not sufficient.
- When fixing UI ordering or labeling, add or update focused regressions so they assert the precise visible order and labels of the affected controls, not only their presence.
- If the live browser still shows the old arrangement after code and tests changed, treat stale runtime as the default suspect and verify the actual listener plus current HTML before concluding the implementation is correct.

## Change Discipline

- If routing, data paths, IDs, vocabularies, research-access logic, or intake rules change, update the relevant file in `docs/spec/` in the same run.
- If research task subsets, page capability metadata, render-mode vocabularies, or corpus-specific workbench readiness change, update `docs/spec/research-capabilities.md` in the same run.
- Research-access changes must keep the corpus-scoped rule generic: under `/{ui_lang}/research/{corpus}` only `design` may stay public, while all other research pages, detail routes, and player-media routes must gate access before rendering and must not rely on corpus-specific exceptions.
- If research intake runtime, archive, batch, or upload-package contracts change, update `docs/spec/platform-data-files.md` and the relevant runbook in the same run.
- If the shared app-shell or navigation hierarchy changes, update the active rule in `docs/spec/platform-data-files.md` in the same run.
- If a durable architectural decision is accepted, add or update an ADR in `docs/decisions/`.
- If a repeatable workflow changes, add or update the relevant runbook in `docs/runbooks/`.
- Every substantive run adds one entry under `docs/agent-runs/`.

## No-Go

- No new shadow documentation buckets.
- No silent architecture decisions without spec updates.
- No webapp access to `secure/`.
- No direct public delivery from `data/`.