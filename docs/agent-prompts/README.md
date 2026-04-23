# Factory Agent Role Prompts

These are the four persistent roles every agent in this factory adopts. Every Capy task starts by referencing one of these files so the agent knows its lane.

## The four roles

| Role | File | Purpose | Output |
| --- | --- | --- | --- |
| Architect | `architect.md` | Decomposes a request into atomic tasks | Ordered task list (no code) |
| Builder | `builder.md` | Implements one task with minimum diff | Changed files + check results |
| Verifier | `verifier.md` | Quality gate on builder diffs | PASS / FAIL / NEEDS_INFO with evidence |
| Shipper | `shipper.md` | Final production gate | SHIP NOW / HOLD / ROLLBACK REQUIRED |

## Pipeline flow

```text
Request → Architect → Builder (per task) → Verifier → Shipper → Production
                    ↘────────────── loop until PASS ──────────────↗
```

Builder and Verifier repeat per atomic task until Verifier returns PASS. Once the full set of work is ready to ship, route the complete result through Shipper once for the final release decision.

## How to reference these in a Capy task

Start every task prompt with the role line, such as `[ROLE: BUILDER]`, and point the agent at the matching file: `See docs/agent-prompts/builder.md`. Pair the role tag with a task-type tag when useful, for example `[TASK TYPE: BOOTSTRAP]`, `[TASK TYPE: FEATURE]`, or `[TASK TYPE: RECOVERY]`.

## When to use which role

- New or ambiguous request → Architect first
- Atomic task with clear acceptance criteria → Builder
- Reviewing a diff or PR → Verifier
- Deciding whether to merge or deploy → Shipper

## Invariants

- Architects never write code
- Builders never skip checks
- Verifiers never approve without proof
- Shippers never ship on yellow/red
