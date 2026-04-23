## Description

<!-- What does this PR do and why? Link to issue if applicable. -->

Closes #

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Refactor (no behavior change)
- [ ] Documentation
- [ ] Infrastructure / CI / tooling
- [ ] Dependency bump

## Affected Systems

- [ ] Python backend (`src/autogen_api_agent/`)
- [ ] SvelteKit frontend (`src/routes/`, `src/lib/`)
- [ ] MCP server
- [ ] Telegram bot (`src/nanoclaw_bot/`)
- [ ] Docker / deploy config
- [ ] CI / workflows
- [ ] Docs

## Testing Done

<!-- How did you verify this works? Commands run, endpoints hit, UIs clicked. -->

- [ ] `pytest` passes locally
- [ ] `pnpm run lint` passes
- [ ] `pnpm run typecheck` passes
- [ ] `pnpm run build` succeeds
- [ ] Manual smoke test via `scripts/smoke-test.sh`
- [ ] Added or updated automated tests

## Screenshots / Logs

<!-- Paste UI screenshots, curl output, or log excerpts that demonstrate the change. -->

## Definition of Done

- [ ] Code compiles, lints, and type-checks
- [ ] Tests added or updated (and passing)
- [ ] Docs / README updated if behavior changed
- [ ] `.env.example` updated if new env vars were introduced
- [ ] No secrets committed
- [ ] CI is green
- [ ] Breaking changes called out above
- [ ] Rollback plan noted below if this is risky

## Rollback Plan

<!-- How do we revert this if it breaks prod? (e.g., `git revert`, redeploy previous Vercel build, feature flag off) -->
