# 2026-10-09 Deploy first attempt failed after green CI; maps in editorial width

## Part A: maps use the editorial width

- `embed` was removed from `teaching_wide_block_types` in `app/templates/partials/_teaching_blocks.html`; both Datawrapper maps now sit in `--pm-layout-editorial-width` on the shared axis. No token, CSS or content change. Audio comparisons and the 2×2 example grid keep `--pm-layout-component-width`.
- Spec (`platform-data-files.md`) and `content/teaching_import/README.md` now state: maps and visualizations are editorial; wide variants must be functionally justified (side-by-side players, multi-column audio grid).
- Tests: `test_teaching_topic_layout.py` (embed not in the wide list), `test_research_sessions.py::test_teaching_topic_blocks_use_editorial_or_component_width_by_function` (exact order and variant, DE/EN).
- Browser (DE/EN, light/dark, 1440/820/390 px): maps 736 px (desktop/tablet) and 358 px (mobile), centered on the axis, legend, caption, source and the Canary inset readable, iframe heights 548/766 px (desktop), no overflow; audio comparison 928/788/358 px.

## Part B: deploy diagnosis (evidence from the public GitHub API, no logs available)

Timeline for `1058da9` (UTC, 2026-10-09):

| time | event |
|---|---|
| 13:56:06 | CI run 37940431349 (push) starts |
| 13:59:44 | job "Python" completes (last gate job) |
| 13:59:46 - 13:59:50 | job "release-gate" runs and succeeds; CI run `completed`/`success` |
| 13:59:52 | `Deploy production` run 37940889249 created (`workflow_run`, head_sha `1058da9`, same SHA as CI) |
| 13:59:56 - 13:59:57 | attempt 1: step 2 "Resolve the exact commit to deploy" fails after about 1 s; steps 3-6 skipped |
| 14:00:23 | attempt 2 (manual rerun) starts; step 2 passes, deploy and smoke succeed, 14:00:45 done |

Findings:

- The trigger, the job condition (`conclusion == success`), the SHA (`workflow_run.head_sha`) and the runner were correct; CI was neither running nor failed when the deploy started. So the hypothesis "deploy started before CI finished" is not supported.
- The only step that failed is the one that asks the REST endpoint `actions/workflows/ci.yml/runs?head_sha=...&status=success` and fails on any non-2xx answer or on `total_count < 1`. It ran 6 s after CI completed and failed within a second; the same call 28 s later succeeded. all earlier automatic deploys in the run list (about two dozen, plus a few skipped by design) passed on the first attempt, so this is intermittent: the runs list is an eventually consistent index (or a transient API error) that can lag behind the `completed` event.
- Not provable: whether the response was HTTP non-2xx or `total_count` 0 (job logs return HTTP 403 without authentication). The diagnosis "lookup of the runs index right after completion" is therefore strongly indicated by timing and step, but the exact response was not recorded. The workflow now records it for the remaining path.

Correction (`.github/workflows/deploy.yml`, no new mechanism, no sleep/retry):

- For `workflow_run` the payload is authoritative (event delivered only after completion, carries conclusion and tested SHA): the step no longer queries the runs index; it re-checks `CI_CONCLUSION == success` and uses `head_sha`.
- Job condition additionally requires `head_repository.full_name == github.repository`.
- The manual/rollback path keeps the API check ("commit must have a successful CI run") and now reports the HTTP status when the lookup itself fails, separated from "no successful CI run".
- Unchanged: `workflow_run` trigger on CI/main, serialized `production-deploy` concurrency, skip when main moved on, `release-gate` (`if: always()`, needs every job, requires `success` of each) so failed, cancelled or skipped CI jobs give a non-success workflow and no deployment.

Verification: YAML parses; `bash -n` of the step; local simulation of the step: `workflow_run` + `success` deploys the given SHA, `failure` refuses; manual path without a valid token reports `HTTP 401`. Static regression tests in `test_ci_workflows.py` (lookup only in the manual branch, no sleep/retry, repository check, conclusion re-check). Whether the new workflow behaves correctly end to end can only be observed on the next push (see the report).
