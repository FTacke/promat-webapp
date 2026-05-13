# Repo Root Hygiene Cleanup

## Problem

Temporary QA/debug artifacts had been written to the repository root, including screenshots, one-off inspection scripts, measurement scripts, and ad hoc notes.

## Actions

- moved reusable root capture helpers to `scripts/qa/`
  - `capture_qa.py`
  - `capture_qa.ps1`
- moved one-off root screenshots, inspect scripts, measurement scripts, verification scripts, and ad hoc notes to `tmp/ui-qa/2026-05-12-root-cleanup/`
- added root-specific ignore patterns to `.gitignore`
- added repo hygiene guidance to `AGENTS.md`
- mirrored the same root-artifact guidance in `.github/instructions/repo.instructions.md`
- added a PR checklist item to `.github/pull_request_template.md`
- added a lightweight root-artifact guard to `scripts/ci_governance_checks.py`

## Kept

- reusable capture utilities now live under `scripts/qa/`
- one-off QA/debug artifacts were preserved under `tmp/ui-qa/2026-05-12-root-cleanup/` instead of staying in the root

## Verification

- `git status --short` captured before cleanup
- repository root checked after cleanup for `inspect_*.py`, `tmp_*.py`, `measure_*.py`, `verify_*.py`, `capture_*.py`, `*_screenshot.png`, and `start.txt`
- no application logic, Teaching UI logic, content structure, or productive routes were changed