# 2026-05-27 Fix Health Rate Limit CI Deploy

## Context
- Production deploy was failing because web health checks hit `/health` and received HTTP 429, which marked `promat-web-prod` unhealthy.
- Goal: ensure `/health` and `/ready` never get blocked by normal request rate limiting while preserving rate limits on normal mutating endpoints.

## Root Cause
- Flask-Limiter global defaults were active and no robust central exemption guaranteed for probe endpoints.
- Under repeated checks, probes could be counted and throttled.

## Changes
- Added central limiter bypass logic for `/health` and `/ready` in `app/src/app/extensions/__init__.py`.
- Added explicit route-level limiter exemptions (defense in depth) for probe endpoints in `app/src/app/routes/public.py`.
- Added regression coverage in `app/tests/test_auth_phase1.py`:
  - health endpoint does not return 429 under repeated requests
  - readiness endpoint does not return 429 under repeated requests
  - mutating route rate limits remain active
- Added spec note in `docs/spec/platform-data-files.md` that `/health` and `/ready` are unauthenticated probes and must not be blocked by normal rate limits.

## Local Validation
- `pytest app/tests/test_auth_phase1.py -q` -> passed
- `pytest app/tests/test_research_intake_storage.py app/tests/test_research_production_importer.py app/tests/test_research_presets.py -q` -> passed
- `ruff check .` -> passed

## Git
- Fix commit: `746a053afa2ef35b9d68805b568868f0208dc619`
- Commit message: `Bypass rate limiting for health and readiness probes`

## GitHub Actions
- CI run: 26528435466 (`.github/workflows/ci.yml`) -> success
- Deploy run: 26528435397 (`.github/workflows/deploy.yml`) -> success

## Outcome
- Deploy health gate recovered for this change set.
- Probe endpoints remain available for liveness/readiness checks without weakening core route rate limiting.
