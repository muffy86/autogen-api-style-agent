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
- [ ] Preview deploy succeeded AND the preview URL was manually verified
      **(Fork PRs:** preview deploy is skipped — a maintainer must either push
      the commit to a trusted branch in this repo to generate a preview, or
      run `vercel deploy --token=$VERCEL_TOKEN` locally against the fork's
      checkout before merging. Do NOT merge a fork PR without a preview.)
- [ ] Preview smoke test passed (`scripts/smoke-test.sh` on the preview URL)
- [ ] Rollback target noted — the `Production Deploy` workflow captures this
      automatically via the Vercel API, but for manual deploys run
      `vercel ls --prod --token=$VERCEL_TOKEN` and record the current URL
- [ ] Breaking changes, migrations, or env var changes called out in the PR body

## Deploy (push to main)

- [ ] `Production Deploy` workflow triggered on the merge commit
- [ ] Deployment URL captured from the `Deploy to production` step
- [ ] Deploy timestamp logged (step output)
- [ ] 30s propagation wait observed before verification

## Post-deploy

- [ ] `scripts/post-deploy-verify.sh <prod-url>` exits 0
- [ ] `home` gate PASS (`/` returns 2xx, or 3xx that resolves to a valid page)
- [ ] `login` gate PASS (`/login` renders with 2xx — this is the one truly public route)
- [ ] `api-reach` gate PASS (`/api/suggestions` returns 3xx auth-redirect, 401, or 403 —
      confirms SvelteKit routing and `src/hooks.server.ts` auth middleware are live;
      an unauthenticated probe will NOT reach the route handler itself)
- [ ] Error rate stable vs. previous 15 minutes (Vercel/observability dashboard)
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
