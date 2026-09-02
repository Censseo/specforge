---
description: Run the full three-phase workflow - design, build, qa - with adversarial review and a gate at each phase boundary. Resumes from wherever the feature currently is.
skills:
  - specforge-workflow
  - adversarial-review
  - finding-verification
  - quality-gates
semantic_anchors:
  - Quality Gates
  - Definition of Done
  - Blast Radius
  - Falsification
handoffs:
  - label: Design Only
    agent: specforge.design
    prompt: Run only the design phase
  - label: Build Only
    agent: specforge.build
    prompt: Run only the build phase
  - label: QA Only
    agent: specforge.qa
    prompt: Run only the qa phase
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --paths-only
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

## User Input

```text
$ARGUMENTS
```

The input is the feature description, a feature path, or empty to resume the current branch.

# Full Workflow

Orchestrates `/specforge.design` -> `/specforge.build` -> `/specforge.qa`, stopping at any gate that
blocks. Load the `specforge-workflow` skill first.

## Step 0 - Locate the Feature and Resume Point

Run `{SCRIPT}` and parse the paths. Then read state from files, not from the conversation:

| Read | Tells you |
| ---- | --------- |
| `FEATURE_DIR/gates/` | The last verdict and its open conditions |
| `tasks.md` | What is done, partial, blocked |
| `validation/bugs/` | What is open |
| `task-results/` | What actually happened, including deviations |

Re-enter at the **earliest phase with an open blocking item**. A later phase built on a blocked earlier
one is wasted work.

| State found | Enter at |
| ----------- | -------- |
| No spec | Design, from the start |
| Spec, no plan, or design gate BLOCK | Design |
| Plan, design gate cleared, no tasks or build gate BLOCK | Build |
| Build gate cleared, qa gate open or BLOCK | QA |
| All gates PASS | Report and offer `/specforge.merge` |

State the resume point and why before doing anything.

## Step 1 - Calibrate Rigor

Before the first phase, frame the work once and let it set the depth of every review:

| Field | Effect |
| ----- | ------ |
| Blast radius | Who or what breaks if this is wrong - users, data, money, safety |
| Reversibility | One-way doors force the full lens sweep and an explicit undo plan |
| Risk triggers present | Each one makes its conditional lens mandatory |

A reversible internal change does not need the full sweep. Say which lenses you are dropping and why -
an unrecorded skip is a silent hole.

## Step 2 - Run the Phases

Run each phase command in order. After each:

1. Read the gate verdict.
2. **PASS** -> continue to the next phase.
3. **PASS WITH CONDITIONS** -> continue, and carry the conditions forward as tracked tasks with owners.
4. **BLOCK** -> stop. Report what blocks, what would clear it, and the smallest next action. Do not
   start the next phase.

Between phases, confirm with the user before continuing when the next phase writes code, touches
production data, or costs significant time. Within a phase, keep going.

## Step 3 - Close

When all three gates are cleared: summarise, then offer `/specforge.merge` and `/specforge.learn`.

## Report

```markdown
## Workflow: {feature}

| Phase | Verdict | Gate record | Blocking |
| ----- | ------- | ----------- | -------- |
| Design | PASS | gates/design-2025-01-14.md | 0 |
| Build | PASS WITH CONDITIONS | gates/build-2025-01-16.md | 0 (2 advisory) |
| QA | BLOCK | gates/qa-2025-01-17.md | 1 |

### What Blocks
| ID | Severity | Location | Claim | What would clear it |

### Carried Conditions
| ID | Condition | Owner | Tracked as |

### Next Action
{one concrete step}
```

## Rules

- Never report a phase PASS with a blocking finding open.
- A gate verdict is stale once its artifacts change - re-run it rather than carrying it forward.
- `/memory/constitution.md` outranks everything. A conflict with a MUST is Critical and blocking in
  every phase.
- Do not run this workflow for a one-line fix. Use `/specforge.change`.
