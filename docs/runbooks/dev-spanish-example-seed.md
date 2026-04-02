# Runbook: Refresh Spanish Dev Example Sessions

## Zweck

Rebuild the canonical Spanish dev example sessions under `data/sessions/spanish/` from the tracked manifest and example fixtures.

## Voraussetzungen

- The repository root is the working directory.
- The Python virtual environment is available.
- `PROMAT_RUNTIME_ROOT` and `PROMAT_PUBLIC_ROOT` resolve to the workspace root and `public/`.

## Schritte

1. Optional dry run:

   ```powershell
   c:/dev/promat/.venv/Scripts/python.exe scripts/session_setup/seed_dev_spanish_example_sessions.py --dry-run
   ```

2. Rebuild the tracked dev sessions:

   ```powershell
   c:/dev/promat/.venv/Scripts/python.exe scripts/session_setup/seed_dev_spanish_example_sessions.py
   ```

3. If runtime-facing research logic changed, run the focused tests:

   ```powershell
   c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_sessions.py
   ```

## Verifikation

- Session folders under `data/sessions/spanish/` match canonical `person_id` and `session_id` formats.
- Learner sessions expose `wordlist`, `text`, and `interview`.
- Native-speaker sessions expose `wordlist` and `text` only.
- `metadata.json` uses lowercase `target_language` and lowercase snake_case `standard_variety`.

## Risiken und Rückbau

- The script rewrites tracked dev example session content.
- If the result is wrong, inspect the manifest in `scripts/session_setup/dev_spanish_example_sessions.json`, fix it, and rerun the seed.
