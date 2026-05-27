# Footer Version and GoatCounter Deploy Wiring

## Scope

Implemented repository-side production/deploy improvements for automatic footer release metadata and GoatCounter analytics on `pronunciation-matters.de`.

## Changes

- Footer release label now renders from app configuration instead of a hardcoded template or branding value.
- `VITE_APP_VERSION` is accepted as the public deploy version source and falls back to `dev` when missing.
- The production deploy workflow resolves the latest GitHub Release tag before deploy and exports it as `VITE_APP_VERSION`, `APP_RELEASE_TAG`, and `APP_RELEASE_URL`.
- GoatCounter is rendered centrally from `base.html` only when production config exposes the exact endpoint `https://pronunciation-matters.goatcounter.com/count`.
- CSP now allows the exact GoatCounter script host and count endpoint.
- Privacy text documents GoatCounter as cookieless aggregate web analytics.
- Env examples, production env template, deployment notes, and active spec were updated.

## Verification

- Latest GitHub Release checked through the GitHub API: `v0.7`.
- `python scripts/ci_governance_checks.py` -> passed.
- `python -m ruff check .` -> passed.
- `python -m compileall app` -> passed.
- `python -m pytest app/tests -q` -> 504 passed, 80 expected Flask-Limiter test warnings.
- `node --test app/tests/js/*.test.mjs` -> 9 passed.
- `docker compose --env-file app/passwords.env.template -f infra/docker-compose.prod.yml config` -> passed.
- `docker build -f app/Dockerfile -t promat-webapp-local-check .` -> passed.
- `git diff --check` -> passed.
- After the first push, GitHub `python-smokes` exposed that CI's global `APP_ENV=testing` was leaking into the runtime-config reload helper; the helper now sets `APP_ENV` alongside `FLASK_ENV`, and the exact CI smoke commands pass locally.

## Typecheck Note

- Installed the pinned local dev typechecker (`mypy==1.18.2`) into the workspace venv.
- `mypy .` is not a currently green repo gate: it stops first on duplicate historical `tmp/ui-qa/**/qa_script.py` module names.
- A scoped `mypy app/src/app app/tests --exclude "tmp"` still reports the existing baseline of missing stubs, path/import setup issues, and pre-existing type errors outside this run.
