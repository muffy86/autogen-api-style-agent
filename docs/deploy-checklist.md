# Deploy Checklist

This checklist governs every production deploy. The pipeline enforces most of
it automatically — humans confirm the rest.

## Required secrets

Configure in GitHub repo settings → Secrets and variables → Actions:

| Secret | Source | Purpose |
| --- | --- | --- |
| `VERCEL_TOKEN` | Vercel → Account → Tokens | Auth for CLI deploys/promotes |
| `VERCEL_ORG_ID` | `.vercel/project.json` after `vercel link` | Scopes deploys to the right team |
| `VERCEL_PROJECT_ID` | `.vercel/project.json` after `vercel link` | Scopes deploys to this project |

`GITHUB_TOKEN` is provided automatically.

Fork PRs skip preview deploys — secrets aren't exposed to forks.

## Pre-deploy (before merging to main)

- [ ] All CI checks green on the PR (`lint`, `test`, `docker`)
- [ ] Preview deploy succeeded and the preview URL was manually verified
- [ ] Preview smoke test passed (`scripts/smoke-test.sh`)
- [ ] Rollback target noted — record the current production deployment URL from `vercel ls --prod`
- [ ] Breaking changes, migrations, or env var changes called out in the PR body

## Deploy (push to main)

- [ ] `Production Deploy` workflow triggered on the merge commit
- [ ] Deployment URL captured from the `Deploy to production` step
- [ ] Deploy timestamp logged (step output)
- [ ] 30s propagation wait observed before verification

## Post-deploy

- [ ] `scripts/post-deploy-verify.sh` exits 0
- [ ] Home (`/`), login (`/login`), and API reachability (`/api/suggestions`) gates all PASS
- [ ] Error rate stable vs. previous 15 minutes (check Vercel/observability dashboard)
- [ ] No spike in 5xx responses in the first 10 minutes

## On failure

- [ ] `scripts/rollback.sh <prev-url>` ran and succeeded (auto-triggered by workflow)
- [ ] Commit comment posted confirming rollback
- [ ] Incident issue filed with `incident` + `deploy-failure` labels
- [ ] Recovery task opened to diagnose and fix-forward
- [ ] Do NOT re-deploy the failing commit until the root cause is understood

## Manual rollback

If you need to roll back without the workflow:

```bash
export VERCEL_TOKEN=...
export GITHUB_REPOSITORY=muffy86/autogen-api-style-agent
export COMMIT_SHA=<sha-of-bad-commit>
./scripts/rollback.sh <previous-deployment-url>
```

Find `<previous-deployment-url>` with `vercel ls --prod --token="$VERCEL_TOKEN"`.
