# Pre-merge Checklist

Before merging any PR into `main`, confirm every box:

- [ ] Verifier has reviewed and returned **PASS** (link to the verifier report in the PR)
- [ ] All CI checks green (lint, typecheck, test, build)
- [ ] Coverage did not drop (see `scripts/check-coverage.sh` output in CI)
- [ ] No new regressions (see `scripts/regression-check.sh` output in CI)
- [ ] PR description complete (summary, motivation, test plan, screenshots if UI)
- [ ] No WIP, TODO, FIXME, or `console.log` / debug `print(` in changed files
- [ ] Rollback path documented (revert SHA or feature flag toggle)
- [ ] Deployment target confirmed (which env: staging / prod / preview)

## Usage

Paste this checklist into every PR description. Merging is blocked until all boxes are ticked and the Verifier agent has posted its PASS evidence.

See @docs/agent-prompts/verifier.md for the verifier's operating rules.
