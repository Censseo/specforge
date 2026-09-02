---
description: Produce an adversarial test plan covering every scenario of the feature, saved as a file the QA pipeline consumes.
skills:
  - adversarial-test-planning
  - lens-testing
  - lens-requirements
semantic_anchors:
  - BDD Gherkin              # Given-When-Then scenarios
  - Specification by Example # Concrete examples as living documentation
  - Boundary Value Analysis  # 0, 1, max, max+1, empty
  - Exploratory Testing      # Charter-driven, observe beyond the script
  - FMEA                     # Enumerate failure modes, effects and detection
handoffs:
  - label: Run QA
    agent: specforge.qa
    prompt: Validate the feature against test-plan.md
    send: true
  - label: Review the Plan
    agent: specforge.harness
    prompt: Review test-plan.md with the testing and requirements lenses
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

Optional scope: a user story (`US2`), a class (`concurrency`), or `smoke` for a P1-only plan.

## Method

Apply the **`adversarial-test-planning`** skill: the ten coverage classes, the derivation moves, the
scenario format and the honesty rules.

Write a plan designed to **break** the feature, not to confirm it. A plan derived by paraphrasing the
acceptance criteria tests what was intended; the bugs are in the gap between that and what was built.

## Operational Steps

1. Run `{SCRIPT}` and parse `FEATURE_DIR`.

2. Load, in this order:

   | Source | Why |
   | ------ | --- |
   | `spec.md` | Stories, acceptance scenarios, requirements, edge cases |
   | `data-model.md`, `contracts/` | Constrained fields, states, error codes to attack |
   | `tasks.md` + `task-results/` | What was actually built; every deviation and gotcha recorded |
   | The diff against the base branch | What changed, and therefore what could have regressed |
   | `quickstart.md` | How to run it, seed data, credentials |
   | `spec.md` §Clarifications | Auto-applied assumptions - decisions made without the user |

   Read `task-results/` properly. A recorded gotcha is a defect the implementer already suspected, and
   it is the single most productive source of scenarios in the whole feature.

3. Derive scenarios across all ten classes. Every MUST, NEVER, ONLY and AT MOST in the spec becomes a
   scenario in its **negative** form. Every documented error code needs a scenario that produces it.

4. Build the requirement-to-scenario table. A requirement with no scenario is an untested requirement -
   add the scenario or record it under Not Covered with the risk accepted.

5. Mark anything unrunnable in this environment `BLOCKED` with the reason, and fill in the
   Not Covered section. Silence about what you did not test reports better coverage than you have.

6. Write `FEATURE_DIR/test-plan.md` in the skill's format.

7. Self-check with `lens-testing` before finishing:
   - Would each scenario fail if the behavior it targets were removed?
   - Does any expected outcome come from reading the implementation rather than the spec? Rewrite it.
   - Is any class empty? An empty class is a hole, not a clean bill.

## Report

```markdown
## Test Plan Ready

**File**: {FEATURE_DIR}/test-plan.md
**Scenarios**: {n} ({p1} P1, {p2} P2, {p3} P3) | **Blocked**: {n}

| Class | Scenarios |
| ----- | --------- |

### Requirements Without a Scenario
{list, or "none"}

### Not Covered
| Area | Why | Risk accepted |

### Next
Run `/specforge.qa` - it executes this plan.
```

## Error Handling

- **No spec.md**: STOP - there is nothing to derive coverage from
- **No tasks.md or task-results/**: WARN and continue from the spec and the diff; say in the plan that
  implementation deviations were unavailable
- **A scenario whose expected outcome is genuinely undecided**: mark it `NEEDS DECISION` rather than
  guessing, and list it in the report
