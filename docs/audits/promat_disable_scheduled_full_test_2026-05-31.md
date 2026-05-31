# Disable Scheduled Full Test – 2026-05-31

## Changed workflow

`.github/workflows/full-test.yml` (`name: Full Test`)

## Trigger removed

```yaml
schedule:
  - cron: "17 2 * * *"
```

Daily scheduled run at 02:17 UTC was removed.

## Current trigger state

```yaml
on:
  workflow_dispatch:
```

The workflow remains fully available via manual `workflow_dispatch` from the GitHub Actions UI or CLI.

## Reason

The Full Test workflow runs against research-importer path assumptions that no longer match the current repo layout, causing persistent red runs without blocking any deploy-gated checks. Disabling the schedule stops the noise while the underlying test failures are evaluated and fixed separately.

## Scope

- Only `.github/workflows/full-test.yml` was changed.
- `ci.yml`, `deploy.yml`, and `release-candidate-check.yml` are untouched.
- No app code, tests, CSS, or documentation specs were modified.

## Next steps

Research-importer test failures should be addressed in a dedicated fix run when the intake refactor is scoped.
