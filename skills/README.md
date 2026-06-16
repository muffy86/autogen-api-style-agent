# Factory Agent Skills Library
*Named, reusable engineering playbooks for factory agents.*

## What is a skill?
A skill is a named, reusable engineering playbook with a fixed shape. Agents invoke a skill by name and run the documented procedure with the live inputs for the task. The fixed shape keeps delegation predictable, reviewable, and easy to extend.

## Available skills
| Skill | Purpose | Typical trigger |
| --- | --- | --- |
| [repo-bootstrap](./repo-bootstrap.md) | Stand up baseline repository infrastructure, CI, ownership, and smoke checks. | New repository or template fork needs factory defaults. |
| [bug-triage](./bug-triage.md) | Reproduce a bug, isolate root cause, land a minimum fix, and add a regression test. | New bug issue, support escalation, or regression report. |
| [ci-repair](./ci-repair.md) | Restore a failing CI/CD pipeline by fixing the real cause without masking it. | PR checks red, `main` broken, or deploy workflow blocked. |
| [pr-hardening](./pr-hardening.md) | Make an in-flight PR reviewer-ready with clean diffs, proof, and context. | Feature work is complete and needs safe review. |
| [release-ship](./release-ship.md) | Promote a verified build to production with rollback instructions and release notes. | Scheduled release window, hotfix ship, or train cut. |
| [post-deploy-verify](./post-deploy-verify.md) | Prove a production deploy is healthy with evidence from flows, logs, and metrics. | Immediately after deploy, rollback, or prod config change. |

## How agents invoke a skill
Use this prompt pattern:

```text
Use the `bug-triage` skill from skills/bug-triage.md on issue #142.
```

Example delegation from an orchestrator agent:

```text
Sub-agent: use the `pr-hardening` skill from skills/pr-hardening.md on PR #88 against `main`. Return a reviewer-ready diff summary and any blockers.
```

Use the skill name exactly as written in the filename. Pass the live inputs in the same prompt so the receiving agent can execute without extra discovery.

## Skill file shape
- `# <Skill Title>` H1
- One-line italicized tagline
- `## Purpose`
- `## When to invoke`
- `## Inputs`
- `## Steps`
- `## Success criteria`
- `## Failure modes`
- `## Handoff`

## Adding a new skill
1. Pick a kebab-case name that reads like a factory action, usually verb-noun.
2. Copy the fixed shape and keep the top-level sections in the same order.
3. Write terse, imperative steps with concrete commands, file paths, and acceptance checks.
4. Add a row for the new skill in the table above and link the new markdown file.
5. Open a PR so other agents can review the contract before relying on it.

## Conventions
- Use kebab-case filenames under `skills/`.
- Write steps in imperative voice.
- Prefer concrete commands and paths over prose.
- Keep each skill file between 80 and 160 lines.
- Do not include secrets, credentials, or real service URLs in examples.
