# 2026-04-28 · CI and GitHub Governance Remediation

## Scope

- harden CI and GitHub governance after the completed auth, i18n, shell-recovery, and 3a non-shell cleanup slices
- add reproducible test execution in CI
- codify a small set of high-value governance regression guards
- add missing GitHub policy and maintenance files
- tighten existing PR and issue templates without broad instructions-layer rewrites
- keep app functionality, auth/session architecture, shell state, and design-system surfaces unchanged

## Ausgangsbefund

- `.github/workflows/ci.yml` ran Ruff plus `compileall`, but not the focused pytest suites that had been used for local remediation validation
- `.github/SECURITY.md`, `.github/CODEOWNERS`, and `.github/dependabot.yml` were missing
- `.github/pull_request_template.md` existed, but it did not explicitly surface the recent high-risk regression axes around sensitive data, auth/session impact, i18n impact, shell impact, or required run-log updates
- `.github/ISSUE_TEMPLATE/bug_report.md` and `.github/ISSUE_TEMPLATE/architecture_change.md` existed, but they did not yet ask for route, language, auth state, shell involvement, or a public-security warning
- `.github/copilot-instructions.md` already pointed at the right active sources, but it did not explicitly warn against another blind shell-class migration after the recovered `promat-*` shell state

## Geänderte Dateien

- `.github/workflows/ci.yml`
- `.github/copilot-instructions.md`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/architecture_change.md`
- `.github/SECURITY.md`
- `.github/CODEOWNERS`
- `.github/dependabot.yml`
- `scripts/ci_governance_checks.py`
- `docs/agent-runs/2026-04-28_ci-github-governance-remediation.md`

## CI-Änderungen

- kept the existing `contents: read` permission model
- kept Ruff and Python compile checks
- added a job timeout of 20 minutes
- moved the harmless CI environment setup to job-level env so all CI steps run under the same reproducible testing context
- switched CI to an explicit non-secret SQLite test database path for the workflow environment instead of a default local PostgreSQL development URL
- extended runtime layout preparation with `data/sessions`
- added a dedicated `Governance regression checks` step that runs `python ../scripts/ci_governance_checks.py`
- added a dedicated `Pytest regression suite` step that runs:
  - `python -m pytest tests/test_auth_phase1.py -q`
  - `python -m pytest tests/test_research_sessions.py -q`
  - `python -m pytest tests/test_research_phenomena.py -q`

## Governance-Checks

- added `scripts/ci_governance_checks.py` as a focused Python guard script
- the script checks only the high-value regression axes that had already been verified manually during remediation:
  - forbidden auth-refresh frontend paths under `app/static`, `app/src`, `app/templates`, `app/tests`
  - forbidden legacy interaction classes under productive app paths
  - shell-recovery template guard for `pm-shell-`, `pm-topbar`, `pm-footer` in `app/templates`
  - shell-recovery CSS guard for actual `.pm-shell-`, `.pm-topbar`, `.pm-footer` selectors in `layout.css`, `20_layout.css`, `30_components.css`
  - deleted legacy asset references under `app/**`
  - auth/research-view local `if ui_lang == 'de'` branches in `app/templates/auth` and `app/src/app/research_views.py`
- the shell CSS guard is intentionally narrower than a raw grep for `pm-topbar` or `pm-footer`, because the accepted shell state already contains legitimate token variables such as `--pm-topbar-*` and `--pm-footer-*`; the guard blocks new class-selector migration, not existing token vocabulary

## SECURITY.md

- added `.github/SECURITY.md`
- documented that PROMAT may involve protected research data and personenbezogene Metadaten
- explicitly instructs reporters not to disclose vulnerabilities in public issues or PRs
- explicitly forbids posting real audio, runtime artifacts, PII, credentials, or secrets in GitHub artifacts
- uses the required honest placeholder line:
  - `Security contact: TODO before public deployment`
- marks only `main` as supported and older branches as unsupported

## CODEOWNERS

- added `.github/CODEOWNERS`
- created it as a valid comment-only scaffold because no confirmed GitHub handles or team slugs were available in the repo context
- documented the intended ownership split for auth/security, architecture, i18n, research, UI, governance, and documentation areas
- avoided invalid placeholder handles so the file remains syntactically safe instead of silently broken

## Dependabot

- added `.github/dependabot.yml`
- inventory confirmed real ecosystems in scope:
  - GitHub Actions under `.github/workflows`
  - Python dependencies under `app/requirements*.txt` and `app/pyproject.toml`
  - Docker under `app/Dockerfile`
- configured weekly updates for:
  - `github-actions` at `/`
  - `pip` at `/app`
  - `docker` at `/app`
- did not add npm or other ecosystems because no `package.json` exists in the repo

## PR-/Issue-Templates

- `.github/pull_request_template.md` was tightened with explicit review gates for:
  - local tests executed
  - no secrets committed
  - no protected research data, audio, runtime artifacts, or PII committed
  - `docs/agent-runs/` updated
  - auth/session impact checked
  - i18n impact checked
  - designsystem/shell impact checked
  - shell not migrated unless explicitly in scope
- `.github/ISSUE_TEMPLATE/bug_report.md` now asks for:
  - route or surface
  - language
  - auth state
  - whether the shell is affected
  - expected vs actual behavior
  - browser/environment context
  - screenshots without sensitive data
  - an explicit public security warning that points users to `SECURITY.md`
- `.github/ISSUE_TEMPLATE/architecture_change.md` now asks for:
  - auth/session, i18n, and shell/designsystem implications
  - a data/security note not to post sensitive artifacts publicly
  - expected verification and acceptance evidence
- `.github/ISSUE_TEMPLATE/config.yml` was left unchanged because no safe repository-specific security contact link URL was available
- note: the repository currently uses the lowercase GitHub-recognized file `.github/pull_request_template.md`, not `PULL_REQUEST_TEMPLATE.md`

## Instructions-/Copilot-Layer

- left `.github/instructions/repo.instructions.md` unchanged because it already points to the canonical sources and did not need another governance rewrite
- made one small targeted addition to `.github/copilot-instructions.md`:
  - do not migrate the recovered productive shell from the accepted `promat-*` shell state to `pm-shell-*`, `pm-topbar*`, or `pm-footer*` without explicit scope and screenshot-proven parity
- no new instructions, prompts, skills, or hooks were added

## Tests

- `Run auth phase tests` -> `37 passed`
- `Run research sessions tests` -> `182 passed`
- `c:/dev/promat/.venv/Scripts/python.exe -m pytest app/tests/test_research_phenomena.py -q` -> `11 passed`
- `c:/dev/promat/.venv/Scripts/python.exe c:/dev/promat/scripts/ci_governance_checks.py` -> all guards passed

## Grep-/Regressionsergebnisse

- `.github` inventory after remediation:
  - `CODEOWNERS`
  - `copilot-instructions.md`
  - `dependabot.yml`
  - `instructions/`
  - `ISSUE_TEMPLATE/`
  - `pull_request_template.md`
  - `SECURITY.md`
  - `workflows/`
- `ISSUE_TEMPLATE/` inventory:
  - `architecture_change.md`
  - `bug_report.md`
  - `config.yml`
- explicit grep result for `/auth/refresh|initAuthRefresh|token-refresh` under `app/static app/src app/templates app/tests` -> `NO_MATCHES`
- explicit grep result for `pm-research-button|pm-research-inline-action` under `app/templates app/static app/src app/tests` -> `NO_MATCHES`
- explicit grep result for `account_profile.html|account_delete.html|account_profile.js|account_delete.js|account_password.js|admin_dashboard.html` under `app/**` -> `NO_MATCHES`
- explicit raw grep for `pm-shell-|pm-topbar|pm-footer` across `app/templates` plus the three shell CSS files returned only accepted CSS token references in `layout.css` and `30_components.css`; no template migration hits appeared
- the narrower governance script guard for actual shell selector migration passed cleanly

## Bewusst nicht geänderte Bereiche

- no auth/session architecture changes
- no `/auth/refresh` reintroduction
- no shell migration and no edits to `base.html`, `_top_app_bar.html`, `_navigation_drawer.html`, footer partials, or shell layout rules
- no designsystem migration beyond governance guards
- no public i18n broad cleanup
- no Phenomena dialog or error-surface rebuild
- no new docs/spec changes because active product rules did not change in this run; only CI/governance enforcement was added around already accepted rules

## Offene Folgepunkte für 3b/4 oder spätere Governance

- replace the comment-only `.github/CODEOWNERS` scaffold with real GitHub handles or teams before enabling required CODEOWNERS review enforcement
- replace the `SECURITY.md` placeholder contact before any public deployment
- if CI later needs stronger runtime parity, decide whether one additional smoke test around the real dev-start path is worth the extra complexity
- if future regressions show up outside the current focused guards, extend `scripts/ci_governance_checks.py` incrementally instead of turning it into a broad brittle grep bucket
- after 4/4, an isolated `3b/4` remains a product decision, not a governance blocker: Forms/Dialoge/Error-Surface still contain deliberately classified MD3 legacy structure, but the new CI/governance layer now protects the already accepted shell, auth, and interaction regressions around them