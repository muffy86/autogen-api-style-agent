# Skill: pr-hardening
*Prepare a PR for safe, boring merges.*

## Purpose
Use this skill when a branch is functionally complete but not yet safe to merge. The outcome is a tidy diff, a complete PR description, verified checks, and the right reviewers so approval can happen quickly. Reach for it before release sweeps, after long-running branches, or whenever a PR has drifted away from its original acceptance criteria.

## When to invoke
- A PR is functionally done and needs review-ready polish.
- A PR has been open long enough to drift behind the target branch.
- A release sweep needs open PRs cleaned up before merge.
- Reviewers asked for proof, structure, or narrower diffs before approval.

## Inputs
- PR number or URL.
- Acceptance criteria from the linked issue or ticket.
- Target branch, usually `main`.
- Current CI status and any review comments already left.
- Whether the PR changes UI, API behavior, schema, or infra.

## Steps
1. Review the diff end to end.
   - Look for debug prints, commented code, stray snapshots, IDE config, and unrelated formatting churn.
   - Check whitespace errors and accidental file permissions before asking for review.
   - Use:
     ```bash
     gh pr diff <pr-number>
     git diff --check
     ```

2. Verify every acceptance criterion.
   - Map each issue requirement to a code change, test, or screenshot.
   - Update the PR description so reviewers can see what is complete and what is deferred.

3. Confirm test coverage.
   - Add tests for new paths, update tests for changed behavior, and remove tests that only covered deleted code.
   - Keep proof close to the diff rather than relying on manual assurance.

4. Run lint and typecheck locally.
   - Re-run the same commands CI expects so surprises are caught before reviewers spend time.
   - Use:
     ```bash
     ruff check .
     pytest
     pnpm lint
     pnpm typecheck
     ```

5. Rebase onto the target branch and resolve conflicts cleanly.
   - Keep history linear if the team prefers rebases.
   - Force-push only with lease after verifying the branch is still correct.
   - Use:
     ```bash
     git fetch origin
     git rebase origin/main
     git push --force-with-lease
     ```

6. Rewrite the PR description.
   - Include Summary, Motivation, Changes, Testing, Screenshots or Logs, Rollout, and Rollback.
   - Keep the body scannable with short bullets and direct evidence.

7. Tag reviewers and labels.
   - Request review from `CODEOWNERS` and apply `type:*` and `area:*` labels.
   - Link the issue with `Closes #N` when merge should auto-close it.
   - Use:
     ```bash
     gh pr edit <pr-number> --add-label type:<type> --add-label area:<area>
     gh pr edit <pr-number> --add-reviewer @team-lead
     ```

8. Attach evidence for changed behavior.
   - Add screenshots for UI changes and short log excerpts for API or job behavior changes.
   - Prefer before and after evidence when the behavior is easy to compare.

## Success criteria
- [ ] The PR description contains Summary, Motivation, Changes, Testing, Screenshots or Logs, Rollout, and Rollback.
- [ ] The diff contains no debug code, WIP markers, or unrelated file churn.
- [ ] Acceptance criteria from the linked issue are explicitly addressed.
- [ ] New or changed behavior has corresponding tests or an explicit explanation for why tests are not possible.
- [ ] Local lint and typecheck pass before relying on CI.
- [ ] All required checks are green and the branch has no merge conflicts.
- [ ] A `CODEOWNERS` reviewer or fallback owner is requested.
- [ ] The issue is linked and labels are applied.

## Failure modes
- The diff is too large to review safely. Split the work into stacked PRs before hardening further.
- Tests are missing for core behavior. Add them before requesting review instead of asking reviewers to trust manual claims.
- `CODEOWNERS` is missing or incomplete. Fall back to the team lead and note the gap in the PR.
- Rebase introduces behavioral drift. Re-run the local checks and refresh screenshots or logs before pushing.

## Handoff
Leave the PR in a reviewer-ready state with green CI and a complete description. The next agent should be able to review, approve, or merge without rediscovering context.
