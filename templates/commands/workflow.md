---
description: Macro command that runs the full design, build and qa pipelines end to end, resuming from wherever the feature currently is.
skills:
  - specforge-workflow
  - quality-gates
semantic_anchors:
  - Pipeline Orchestration  # Sequential stage execution with gates
  - Quality Gates           # Stage-gate checkpoints, go/no-go decisions
  - Fail Fast               # Abort on critical failures rather than compounding them
  - Blast Radius            # Calibrate rigor to what breaks if this is wrong
handoffs:
  - label: Design Only
    agent: specforge.design
    prompt: Run only the design pipeline
  - label: Build Only
    agent: specforge.build
    prompt: Run only the build pipeline
  - label: QA Only
    agent: specforge.qa
    prompt: Run only the qa pipeline
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --paths-only
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

## User Input

```text
$ARGUMENTS
```

The input is the feature description, a feature path, or empty to resume the current branch.

## Outline

Chains the three macro pipelines and stops at the first gate that blocks.

1. Locate the feature and determine the resume point
2. Run `/specforge.design` (unless already cleared)
3. Run `/specforge.build` (unless already cleared)
4. Run `/specforge.qa`
5. Report and hand off to `/specforge.merge`

Each pipeline runs non-interactively and produces its own gate record. This command adds the
resumption logic and the stop-on-block rule between them.

## Detailed Steps

### Step 1: Locate the Feature and Resume Point

Run `{SCRIPT}` and parse the paths. Then read state from files, not from the conversation:

| Read | Tells you |
| ---- | --------- |
| `FEATURE_DIR/gates/` | The last verdict per phase and its open conditions |
| `FEATURE_DIR/complexity-analysis.md` | Whether design completed and which phases need breakdown |
| `tasks.md` | What is done, partial, blocked |
| `validation/bugs/` | What is open |
| `task-results/` | What actually happened, including deviations |

Re-enter at the **earliest phase with an open blocking item**. A later phase built on a blocked
earlier one is wasted work.

| State found | Enter at |
| ----------- | -------- |
| No spec | Design |
| Spec but no plan, or design gate BLOCK | Design |
| Plan and design gate cleared, no tasks or no complexity-analysis.md | Design (from step 6) |
| Tasks exist, build gate absent or BLOCK | Build |
| Build gate cleared, qa gate absent or BLOCK | QA |
| All three gates cleared | Report and offer `/specforge.merge` |

State the resume point and why before doing anything.

### Step 2: Run the Pipelines

```text
Skill: specforge.design
Args: $ARGUMENTS
```

```text
Skill: specforge.build
Args: (no additional arguments)
```

```text
Skill: specforge.qa
Args: (no additional arguments)
```

After each pipeline, read its gate record:

| Verdict | Action |
| ------- | ------ |
| **PASS** | Continue to the next pipeline immediately |
| **PASS WITH CONDITIONS** | Continue, and carry the conditions forward as tasks with owners |
| **BLOCK** | Stop. Report what blocks, what would clear it, and the smallest next action |

Do not start the next pipeline on a BLOCK. Within a pipeline, keep going - the macro commands handle
their own internal failures.

Confirm with the user before starting `/specforge.build` when the design pipeline auto-applied a large
number of clarification answers: a design where a dozen decisions were made on their behalf deserves a
look before it becomes code.

### Step 3: Report

```markdown
## Workflow: {feature}

| Pipeline | Verdict | Gate record | Blocking |
|----------|---------|-------------|----------|
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

- Never report a pipeline PASS with a blocking finding open.
- A gate verdict is stale once its artifacts change - re-run the pipeline rather than carrying a PASS
  across a rewrite.
- `/memory/constitution.md` outranks everything. A conflict with a MUST is Critical and blocking in
  every phase.
- Do not run this for a one-line fix. Use `/specforge.change`.

## Error Handling

- **Cannot determine the feature**: STOP and ask which feature or branch
- **Gate record missing for a phase whose artifacts exist**: treat the phase as not cleared and re-run it
- **A pipeline stops mid-way**: report its own error output verbatim; do not retry it blindly
