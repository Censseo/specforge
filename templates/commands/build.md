---
description: Run the BUILD phase - decompose the plan into tasks, implement them test-first, red-team each increment through code lenses and clear the build gate.
skills:
  - specforge-workflow
  - task-decomposition
  - implementation-execution
  - adversarial-review
  - finding-verification
  - quality-gates
lenses:
  - lens-architecture
  - lens-maintainability
  - lens-security
  - lens-concurrency
  - lens-data
  - lens-testing
  - lens-performance
  - lens-api-contract
semantic_anchors:
  - TDD London School
  - SOLID Principles
  - Kanban
  - Mutation Testing
  - Falsification
handoffs:
  - label: Run QA Phase
    agent: specforge.qa
    prompt: Validate the implementation and clear the release gate
    send: true
  - label: Diagnose a Failure
    agent: specforge.fix
    prompt: Diagnose why the implementation is failing
  - label: Re-run Code Review
    agent: specforge.harness
    prompt: Re-run the build lenses on the current diff
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

# Build Phase

Phase 2 of 3. Turn the plan into code that does what the design says and nothing it must not.

Load the `specforge-workflow` skill for the phase model, and each step's skill as you reach it.

## Step 0 - Entry Check

Run `{SCRIPT}` and parse `FEATURE_DIR` and `AVAILABLE_DOCS`.

Verify before starting:

| Check | If it fails |
| ----- | ----------- |
| `plan.md` exists | Run `/specforge.design` first - stop here |
| Design gate record exists and is PASS or PASS WITH CONDITIONS | Report the gap; ask before proceeding |
| Open blocking conditions from the design gate | List them; ask before proceeding |
| `tasks.md` exists | Step 1 generates it |

Proceeding past a failed design gate is allowed only on the user's explicit say-so, and the build gate
record must say that it happened.

## Step 1 - Decompose

Apply the `task-decomposition` skill. If `tasks.md` already exists and matches the current plan, skip
to Step 2; if the plan changed after the tasks were written, regenerate the affected phases.

Output: `tasks.md`, organised by user story, with idea and reuse traceability tables.

## Step 2 - Implement, Phase by Phase

Apply the `implementation-execution` skill. For **each phase of `tasks.md`**:

1. Execute its tasks - sequential in order, `[P]` in parallel, same-file tasks never in parallel.
2. Write `task-results/T{n}-result.md` for each, including deviations and gotchas.
3. Run the project's own checks (build, lint, typecheck, affected tests) and quote the output.
4. Run the incremental adversarial pass below on the increment.
5. Aggregate TODOs; stop and ask if there are blockers.

Do not defer the review to the end. A defect found three tasks later costs a fix; found at the end it
costs a redesign.

## Step 3 - Adversarial Code Review (per increment)

Apply the `adversarial-review` skill against the increment's diff.

Run in this order - the first pass finds the most expensive defects:

1. **`lens-maintainability` Part 1** - fake implementations, stubs, placeholder returns, swallowed
   errors, hardcoded bypasses. These pass tests and demos; they are the highest-yield probe there is.
2. **`lens-security`** on any changed entry point, input handler, query, secret or permission.
3. **`lens-testing`** - would these tests fail if the behavior were removed?
4. The remaining default lenses whose risk triggers fired on this increment.

Falsify every candidate with `finding-verification` before reporting it. Fix confirmed blocking
findings inside the current phase rather than filing them for later.

## Step 4 - Build Gate

Apply the `quality-gates` skill, build gate criteria B1-B9. Evidence is command output and file
anchors, not assertion.

Write `FEATURE_DIR/gates/build-{date}.md`.

## Step 5 - Registry Update

Extract patterns, technology decisions, conventions and discovered anti-patterns from
`task-results/*.md` into `/memory/architecture-registry.md`, tagged with the feature and date.
"No new patterns - followed existing conventions" is a valid and useful entry.

## Report

```markdown
## Build Phase: {VERDICT}

### Tasks
| Phase | Total | Complete | Partial | Deferred |

### Checks
| Check | Command | Result |

### Adversarial Review
| Lens | Findings | Blocking | Fixed in place |
Skipped: {lens - reason}

### Open Findings
| ID | Severity | Location | Claim | Fix |

### Registry Updates
### Next
- PASS -> `/specforge.qa`
- BLOCK -> fix, then re-run the build gate
```

Report failing checks with their output. A task whose verification failed is `[~]`, never `[X]`.
