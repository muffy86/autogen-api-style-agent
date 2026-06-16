# Skill: bug-triage
*Systematically diagnose a reported bug and ship a minimum fix with a regression test.*

## Purpose
Use this skill when a bug report needs to become a verified fix instead of a guess. The output is a clean reproduction, a root-cause classification, a failing test, the smallest safe patch, and proof that the behavior is corrected. Prefer this skill when the report is vague, flaky, or tied to a recent regression.

## When to invoke
- A new bug issue lands with steps to reproduce or user-visible symptoms.
- Support escalates a production defect and needs a minimum safe patch.
- A flaky test suggests a real regression that needs isolation.
- Smoke checks or post-deploy verification uncover incorrect behavior.

## Inputs
- Issue link or the exact reproduction steps.
- Affected environment, such as production, staging, or local dev.
- Recent deploy SHA or commit range suspected of introducing the bug.
- Expected behavior versus actual behavior.
- Any logs, screenshots, or failing request payloads already collected.

## Steps
1. Reproduce the issue locally.
   - Record the exact command, input, fixture, and observed output before changing code.
   - Keep a plain-text note with the failing behavior and environment assumptions.
   - Use:
     ```bash
     pytest -k <failing-area> -x -vv
     pnpm test -- --runInBand <pattern>
     curl -fsS <host>/<path>
     ```

2. Classify the root-cause bucket.
   - Decide whether the failure is code, config, deploy, dependency, data, or external service.
   - Avoid coding until one bucket clearly explains the symptom.

3. Scope the impact.
   - Identify which users, endpoints, jobs, or environments are affected.
   - Search history to estimate how long the bug has existed.
   - Use:
     ```bash
     git log -S '<suspect-token>' --oneline -- <path>
     git blame <path>
     ```

4. Write the failing test on branch `fix/<slug>` before the fix.
   - Prefer a unit test first, then integration, then end-to-end only if needed.
   - Commit the failing test before touching production code so the regression proof is preserved.
   - Use:
     ```bash
     git checkout -b fix/<slug>
     pytest tests/<target_test>.py -x
     git add tests/
     git commit -m "test: reproduce <bug-slug>"
     ```

5. Implement the minimum code change.
   - Change only the code required to make the failing test pass.
   - Do not mix refactors, renames, or cleanups into the same patch.

6. Run the full test suite locally.
   - Re-run the targeted test first, then the full suite for the project.
   - Capture the exact commands in the PR body so reviewers can replay them.
   - Use:
     ```bash
     pytest tests/<target_test>.py -x
     pytest
     ruff check .
     pnpm lint
     pnpm test
     ```

7. Document the root cause in the PR description.
   - Explain what broke, why it broke, why the chosen fix works, and the blast radius.
   - Include any mitigations needed before merge, such as backfills or config cleanup.

8. Open PR `fix: <short description>` and link the issue.
   - Use `Fixes #N` in the PR body so the issue auto-closes on merge.
   - Keep the title descriptive enough for release notes.
   - Use:
     ```bash
     git add .
     git commit -m "fix: <short description>"
     git push -u origin fix/<slug>
     gh pr create --base main --title "fix: <short description>"
     ```

## Success criteria
- [ ] The bug is reproducible or the missing reproduction detail is explicitly documented.
- [ ] A failing regression test was committed before the code fix.
- [ ] The minimum code change makes the new test pass.
- [ ] The full local test suite passes after the fix.
- [ ] The diff contains no unrelated refactors or formatting churn.
- [ ] The PR links the originating issue with `Fixes #N`.
- [ ] The PR body contains a root-cause paragraph and blast-radius summary.
- [ ] CI is green on the fix branch.

## Failure modes
- The bug does not reproduce locally. Ask for environment details, sample payloads, and logs before guessing.
- The test is flaky instead of deterministically failing. Quarantine the flake, open a follow-up, and keep the real bug fix separate.
- The root cause spans multiple systems. Split the work into a minimum fix PR and one or more follow-up hardening PRs.
- The fix requires data repair or a feature flag. Document the operational step in the PR and release notes before merge.

## Handoff
Leave a review-ready fix PR linked to the issue with the regression test in place. The next agent should inherit a branch with green CI and a clear root-cause write-up for release notes.
