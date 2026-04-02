# PROMAT Scripts Governance

Dieses Dokument ergänzt das Root-`AGENTS.md` für Arbeiten unter `scripts/`.

## Regeln

- Scripts implement the workflows defined by `docs/spec/` and, where relevant, `docs/runbooks/`.
- If import, seed, session, path, or export semantics change, update the relevant spec file in `docs/spec/` in the same run.
- Keep inputs, outputs, and side effects explicit.
- Public export to `public/` is always an explicit pipeline step.
- Do not create a second active documentation layer in `scripts/`.

## No-Go

- No script path may bypass `data/` / `public/` / `secure/` boundaries.
- No shadow import contract outside `docs/spec/intake-workbook.md`.