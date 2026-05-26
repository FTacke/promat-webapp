# PROMAT Scripts Governance

Dieses Dokument ergänzt das Root-`AGENTS.md` für Arbeiten unter `scripts/`.

## Regeln

- Scripts implement the workflows defined by `docs/spec/` and, where relevant, `docs/runbooks/`.
- Research-data intake and derivation scripts belong under `scripts/research_data_intake/`.
- General dev, bootstrap, and non-intake maintenance scripts stay at the top level under `scripts/`.
- If import, seed, session, path, or export semantics change, update the relevant spec file in `docs/spec/` in the same run.
- Keep inputs, outputs, and side effects explicit.
- Public export to `public/` is always an explicit pipeline step.
- Research intake scripts must keep `data/sessions/` runtime-only and must not write WAV, TextGrid, XLSX, `secure/`, `raw/`, or `source/` into runtime session trees.
- Research intake archives belong under `PROMAT_LOCAL_ARCHIVE_ROOT` outside the repo, not under `data/`, `public/`, `secure/`, or ad hoc folders in the workspace.
- Upload-package creation is an explicit allowlist export step from validated runtime artifacts, not a raw batch copy.
- Research intake work must not modify `content/`, `content/teaching/`, or `public/teaching/` unless the task explicitly includes Teaching.
- Do not create a second active documentation layer in `scripts/`.

## No-Go

- No script path may bypass `data/` / `public/` / `secure/` boundaries.
- No shadow import contract outside `docs/spec/intake-workbook.md`.
- No heuristic invention of research task identity, audio provenance, or person mapping when filename-driven classification is missing.