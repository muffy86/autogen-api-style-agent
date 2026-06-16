# Skill: ci-repair
*Fix a failing CI/CD pipeline and leave it greener than you found it.*

## Purpose
Use this skill when a workflow is red and downstream delivery is blocked. The objective is to identify the first real failure, reproduce it, fix the cause, and restore green without hiding the signal. Prefer this over ad hoc patching when the pressure to “just make CI pass” risks masking the true defect.

## When to invoke
- A pull request has failing required checks.
- `main` is red and other work is blocked.
- A nightly build failed and needs triage before business hours.
- A deploy workflow is blocked by an earlier CI/CD failure.

## Inputs
- Failing workflow run URL or run ID.
- Branch name where the failure occurred.
- Recent commit SHA range or suspect merge window.
- Workflow file path under `.github/workflows/`.
- Whether the failure is blocking a release or only regular development.

## Steps
1. Read the full error log top to bottom.
   - Copy the first real error, not the final summary line or secondary stack traces.
   - Pull logs locally if the web UI truncates them.
   - Use:
     ```bash
     gh run view <run-id> --log-failed
     gh run view <run-id> --job <job-id> --log
     ```

2. Classify the failure.
   - Bucket it as lint, typecheck, unit test, integration test, build, container push, deploy, environment or secret, external service, or cache corruption.
   - State the bucket in the PR or incident note before applying a fix.

3. Check recent changes.
   - Identify the commit or merge that first introduced the failure.
   - Compare the failing branch against the last known green state.
   - Use:
     ```bash
     git log --oneline origin/main..HEAD
     git log --oneline <last-green-sha>..HEAD
     ```

4. Reproduce locally where possible.
   - Run the exact command from the failing workflow rather than an approximation.
   - Mirror the same runtime, flags, and environment as closely as possible.
   - Use:
     ```bash
     ruff check .
     pytest -x
     pnpm build
     docker build .
     ```

5. Fix the root cause.
   - Change code, config, workflow steps, or secrets only when they directly address the identified failure.
   - Do not add `continue-on-error`, broad skips, or `xfail` without an issue link and reviewer agreement.

6. Treat flakiness as a scoped reliability issue.
   - Add retry only at the smallest failing boundary and leave the underlying test visible.
   - File a follow-up issue tagged `flaky-test` if the immediate unblock uses a scoped mitigation.
   - Use:
     ```bash
     gh issue create --title "flaky-test: <scope>" --label flaky-test
     ```

7. Push the fix on branch `fix/ci-<slug>` and rerun CI.
   - Keep the branch single-purpose and tied to the failing workflow.
   - Watch required checks until every blocking job is green.
   - Use:
     ```bash
     git checkout -b fix/ci-<slug>
     git add .
     git commit -m "fix: repair ci for <scope>"
     git push -u origin fix/ci-<slug>
     gh pr create --base main --title "fix: repair ci for <scope>"
     gh pr checks --watch
     ```

8. Document the root cause and recurrence guard.
   - Explain what broke, why it broke, how the patch fixes it, and what prevents recurrence.
   - Link any follow-up issues for flaky tests, secret rotation, or infrastructure cleanup.

## Success criteria
- [ ] The first real failure is identified and documented.
- [ ] The failure reproduces locally or the reason it cannot be reproduced is documented.
- [ ] The fix addresses the root cause instead of muting the symptom.
- [ ] All required checks are green on the repair PR.
- [ ] No tests are newly skipped or marked `xfail` without an issue link.
- [ ] Cache keys remain unchanged unless cache corruption was the cause.
- [ ] The PR body records root cause, fix, and recurrence guard.
- [ ] The repair is merged or otherwise ready to unblock downstream work.

## Failure modes
- An external dependency is intermittently failing. Retry with backoff or narrow the assertion, but do not disable the job without evidence.
- A required secret is missing or expired. Rotate it, update repo secrets, and rerun the workflow instead of hardcoding fallback values.
- Only one matrix leg fails. Fix the narrow OS or version-specific issue rather than broadening the skip.
- Logs are truncated or noisy. Re-run the workflow with increased verbosity and isolate the first real error before editing code.

## Handoff
Leave a green CI repair PR or a merged fix that unblocks the pipeline. The next agent should inherit clear root-cause notes and linked follow-ups for any flakiness or secret rotation.
