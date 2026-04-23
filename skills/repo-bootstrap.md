# Skill: repo-bootstrap
*Set up a net-new repo with all factory infrastructure.*

## Purpose
Use this skill when a repository needs the baseline factory scaffolding before feature work starts. The goal is to leave the repo with CI, release hooks, contribution templates, ownership, environment scaffolding, and a smoke check that proves the app boots. Use it for greenfield repos, template forks, or older repos that never received the standard foundation.

## When to invoke
- A new repository has been created and needs factory defaults.
- A forked template is missing CI, ownership, or release scaffolding.
- An existing repo has code but lacks baseline workflows and smoke checks.
- The team wants to standardize repo structure before opening feature work.

## Inputs
- Repository URL or local path.
- Target default branch name, usually `main`.
- Primary language or stack.
- List of required secrets and which environment uses each one.
- Whether the team uses a long-lived `develop` branch.

## Steps
1. Clone the repo and create branch `chore/factory-bootstrap`.
   - Start from a clean checkout on the default branch.
   - Use:
     ```bash
     git clone <repo-url>
     cd <repo>
     git checkout main
     git pull --ff-only
     git checkout -b chore/factory-bootstrap
     ```

2. Establish branch structure.
   - Confirm the default branch is `main` and create `develop` only if the team uses it.
   - Set branch protection with the GitHub CLI. This requires repo admin rights.
   - Use:
     ```bash
     gh repo view --json defaultBranchRef
     gh api repos/<owner>/<repo>/branches/main/protection                --method PUT                --input - <<'EOF'
     {
       "required_status_checks": {"strict": true, "contexts": ["ci"]},
       "enforce_admins": true,
       "required_pull_request_reviews": {"required_approving_review_count": 1},
       "restrictions": null
     }
     EOF
     ```

3. Add the CI workflow at `.github/workflows/ci.yml`.
   - Include lint, test matrix, and build jobs for the detected stack.
   - Start from a canonical workflow skeleton and wire the real project commands.
   - Use:
     ```yaml
     name: ci
     on:
       pull_request:
       push:
         branches: [main]
     jobs:
       lint:
       test:
       build:
     ```

4. Add `.github/workflows/release.yml` for tag-triggered releases.
   - Keep it scaffolded even if production deploy is not wired yet.
   - Gate release execution behind environment approval if the platform supports it.
   - Use:
     ```yaml
     name: release
     on:
       push:
         tags:
           - 'v*.*.*'
     ```

5. Add `.github/PULL_REQUEST_TEMPLATE.md`.
   - Include these sections in order: Summary, Changes, Testing, Checklist.
   - Keep the checklist short enough that contributors will actually fill it out.

6. Add `.github/ISSUE_TEMPLATE/bug_report.md` and `.github/ISSUE_TEMPLATE/feature_request.md`.
   - Collect reproduction steps, expected behavior, and environment details in the bug template.
   - Collect user value, acceptance criteria, and rollout notes in the feature template.

7. Add `.env.example` with every environment variable the app reads.
   - Comment each variable with purpose and whether it is required.
   - Use obvious placeholders, never real values.

8. Add `CODEOWNERS` at the repo root or `.github/CODEOWNERS`.
   - Define a default owner and explicit owners for critical paths such as `.github/`, `src/`, and `infra/`.
   - Use placeholders such as `@team-lead` rather than real handles in templates.

9. Add `scripts/smoke.sh` or `scripts/smoke.ps1`.
   - Keep the smoke check minimal: app starts, health endpoint responds, process exits cleanly.
   - Mark the script executable and run it locally.
   - Use:
     ```bash
     chmod +x scripts/smoke.sh
     ./scripts/smoke.sh
     ```

10. Add the lint configuration for the stack.
    - Use `ruff.toml`, `.eslintrc.json`, `biome.json`, or the stack-equivalent config and wire it into CI.
    - Confirm the local lint command matches the CI command exactly.
    - Use:
      ```bash
      ruff check .
      pytest -q
      pnpm lint
      pnpm build
      ```

11. Add `README.md` scaffolding if it is missing.
    - Include Title, Quick Start, Configuration, Contributing, and License.
    - Keep startup instructions copy-pasteable from a fresh clone.

12. Open PR `chore: factory bootstrap` against `main` and confirm CI passes.
    - Stage, commit, and push the bootstrap branch.
    - Create the PR and watch required checks until they finish.
    - Use:
      ```bash
      git add .
      git commit -m "chore: factory bootstrap"
      git push -u origin chore/factory-bootstrap
      gh pr create --base main --title "chore: factory bootstrap"
      gh pr checks --watch
      ```

## Success criteria
- [ ] `.github/workflows/ci.yml` exists and runs lint, test, and build jobs.
- [ ] `.github/workflows/release.yml` exists as a tag-triggered scaffold.
- [ ] PR and issue templates are present under `.github/`.
- [ ] `.env.example` is committed with placeholders only and no real secrets.
- [ ] `CODEOWNERS` or `.github/CODEOWNERS` assigns default ownership for critical paths.
- [ ] `scripts/smoke.sh` or `scripts/smoke.ps1` exists, is executable if applicable, and passes locally.
- [ ] Lint configuration is wired into CI and passes.
- [ ] `README.md` contains the baseline sections if it was previously missing.
- [ ] Branch protection is enforced on `main`, or the lack of admin rights is explicitly documented.
- [ ] The bootstrap PR is open against `main` with green CI.

## Failure modes
- Missing GitHub admin rights prevent branch protection changes. Document the exact command attempted and escalate to a repo admin.
- The language toolchain is unclear. Stop and ask for the stack before inventing workflows or config files.
- CI fails on lint or test after scaffolding. Fix the configuration before merge instead of downgrading checks.
- The smoke script depends on secrets that do not exist yet. Replace them with placeholder-safe local defaults or split the smoke check to a no-secret path.

## Handoff
Leave a bootstrap PR open against `main` with the reviewer tagged per `CODEOWNERS`. The next agent should inherit a repo with baseline factory infrastructure and a green CI signal.
