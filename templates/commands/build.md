---
description: Macro command that runs breakdown (if needed) and implementation for all phases, with an adversarial review per increment, followed by code review, corrections and an adversarial test plan for QA.
skills:
  - specforge-workflow
  - adversarial-review
  - finding-verification
  - adversarial-test-planning
  - quality-gates
lenses:
  - lens-maintainability
  - lens-security
  - lens-testing
  - lens-concurrency
  - lens-data
  - lens-api-contract
  - lens-architecture
  - lens-performance
semantic_anchors:
  - Kanban                  # Visualize flow, limit WIP, pull system
  - Critical Path Method    # Identify blocking sequences, optimize throughput
  - Boy Scout Rule          # Leave code better than you found it
  - Mutation Testing        # A test that cannot fail proves nothing
  - Falsification           # A finding must survive an attempt to disprove it
handoffs:
  - label: QA Validation
    agent: specforge.qa
    prompt: Run the QA validation pipeline against test-plan.md
    send: true
  - label: Re-build Phase
    agent: specforge.build
    prompt: Re-run build for a specific phase
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

Consider the user input before proceeding (if not empty). If user specifies a phase number
(e.g., "phase 3"), start from that phase. Otherwise process all phases.

## Outline

This macro command orchestrates the build pipeline: for each phase, optionally break down complex
phases, implement, then attack the increment through the code lenses. Finally, review the whole
feature and apply corrections.

1. Load tasks.md and complexity-analysis.md
2. For each phase: breakdown if needed, implement, adversarial pass on the increment
3. Code review after all phases
4. Add correction tasks to tasks.md
5. Implement corrections
6. Produce the adversarial test plan for QA
7. Record the build gate verdict

## Detailed Steps

### Step 1: Load Context

Run `{SCRIPT}` from repo root and parse JSON for FEATURE_DIR.

Read:

- `FEATURE_DIR/tasks.md` - full task list
- `FEATURE_DIR/complexity-analysis.md` - phase verdicts and lens exposure from `/specforge.design`
- `FEATURE_DIR/gates/design-*.md` - the design gate verdict and its carried conditions

If complexity-analysis.md does not exist, treat ALL phases as DIRECT, derive lens exposure from the
phase content, and log a warning.

If the design gate is BLOCK, report it and ask before proceeding. Building on a blocked design is the
user's call, not yours, and the build gate record must say it happened.

Build a phase execution plan from tasks.md phases. Skip phases where all tasks are already marked `[X]`.

Display the plan:

```text
Build Execution Plan: {feature-name}

Phase 1: Setup (3 tasks) - DIRECT - lenses: maintainability
Phase 2: Foundation (12 tasks) - BREAKDOWN first - lenses: maintainability, security, data
Phase 3: US1 (6 tasks, 2 done) - DIRECT (resume) - lenses: maintainability, testing
...

Starting from Phase {first-incomplete}...
```

### Step 2: Execute Phases

**CRITICAL: This is a continuous loop. You MUST process ALL phases in sequence without stopping or
returning control to the user between phases. After each phase completes, IMMEDIATELY proceed to the
next one.**

For each phase in order, skip if fully completed:

#### Step 2a: Breakdown (if verdict is BREAKDOWN)

```text
Skill: specforge.breakdown
Args: phase {phase_number}. You are in non-interactive mode: do not ask for confirmation between phases, process the named phase and return.
```

Verify task-plans/ directory has plan files for the phase. If breakdown failed, log warning and
proceed to implement anyway.

#### Step 2b: Implement

```text
Skill: specforge.implement
Args: phase {phase_number} --auto-continue
```

#### Step 2c: Adversarial Pass on the Increment

Run the review on **this phase's diff**, not on the whole feature. A defect found three tasks later
costs a fix; found at the end it costs a redesign.

Apply the `adversarial-review` skill against the increment, in this order:

1. **`lens-maintainability` Part 1 first** - placeholder returns, empty bodies, validations that
   cannot fail, `NotImplementedError` on live paths, mock data in production code, swallowed errors,
   hardcoded bypasses. These pass tests, demos and superficial review, and they are the single
   highest-yield probe in the pipeline.
2. **The lenses recorded for this phase** in complexity-analysis.md, plus any whose risk trigger fired
   in this diff (a migration, a new endpoint, shared mutable state, an LLM call).
3. **`lens-testing`** whenever the phase added behavior - would these tests fail if the behavior were
   removed?

Falsify every candidate with `finding-verification` before acting on it. Then:

- **Confirmed, in this phase's scope**: fix it now, inside the phase. Re-run the affected check.
- **Confirmed, out of scope**: append a task to the correction phase of tasks.md.
- **Refuted**: drop it. Do not report it, do not downgrade it.

**After each phase (then IMMEDIATELY continue to next phase):**

- Read tasks.md to verify completion status
- If tasks failed or have blockers in task-results/:
  - Log failures
  - Continue to next phase (do not stop the pipeline for individual task failures)
- Log: `Phase {N}: {name} - {completed}/{total} tasks complete, {findings} findings ({fixed} fixed)`
- **Do NOT stop here. Proceed to the next incomplete phase immediately.**

The one exception: a **Critical** confirmed finding on a production path - a secret committed, an
authorization bypass, a data-destroying migration. Fix it before moving on, or stop and report if the
fix is beyond this phase's scope.

### Step 3: Code Review

After all phases are implemented:

```text
Skill: specforge.review
Args: Update tasks.md with review action items. Generate a review report in reviews/. Apply task updates directly.
```

Read the review report. Extract health score and critical issues count.

This is the whole-feature pass: it sees cross-phase duplication, spec drift and dead code that the
per-increment passes could not, because they only ever saw one phase.

### Step 4: Correction Phase

If the review identified issues:

#### Step 4a: Verify corrections in tasks.md

The review should have added a correction phase to tasks.md. If it didn't, read the review report and
manually append correction tasks to tasks.md based on HIGH and CRITICAL findings, plus any out-of-scope
findings deferred from step 2c.

#### Step 4b: Implement corrections

```text
Skill: specforge.implement
Args: Execute the review correction tasks only (the last phase in tasks.md). Do not re-implement earlier phases.
```

#### Step 4c: Verify the corrections landed

Re-run the lenses that produced each correction against the fixed code. A correction task marked
complete whose finding still reproduces is not complete - reopen it.

### Step 5: Adversarial Test Plan

The build now knows things the spec never did: what was actually built, where it deviated, and every
gotcha the implementers hit. That knowledge is worth more as a test plan than as a memory.

```text
Skill: specforge.testplan
Args: (no additional arguments)
```

This writes `FEATURE_DIR/test-plan.md` - the full adversarial scenario set across the ten coverage
classes, with a requirement-to-scenario table and an explicit Not Covered section. `/specforge.qa`
executes it.

**Gate check**: verify test-plan.md exists and that every requirement appears either in the
requirement-to-scenario table or in Not Covered with a recorded reason. A requirement in neither is a
coverage hole the QA run will not find, because it will not look.

### Step 6: Build Gate Record

Apply the `quality-gates` skill, build gate criteria B1-B9. Evidence is command output and file
anchors, not assertion: run the project's own build, lint, typecheck and test commands and quote what
they printed.

Write `FEATURE_DIR/gates/build-{date}.md` with the verdict, the criteria table, the findings and the
conditions carried into QA.

### Step 7: Registry Update

Extract patterns, technology decisions, component conventions and discovered anti-patterns from
`task-results/*.md` into `/memory/architecture-registry.md`, tagged
`<!-- Added from {feature} ({date}) -->`. "No new patterns - followed existing conventions" is a valid
and useful entry.

### Step 8: Report

```markdown
## Build Pipeline Complete

**Feature**: {feature-name}
**Branch**: {branch-name}
**Gate**: {PASS | PASS WITH CONDITIONS | BLOCK}

### Phase Results

| Phase | Name | Tasks | Completed | Breakdown | Findings | Fixed | Status |
|-------|------|-------|-----------|-----------|----------|-------|--------|

### Project Checks

| Check | Command | Result |

### Review Results
- Health score: {score}/100
- Critical issues: {count} ({resolved} resolved)
- Corrections applied: {count}/{total}
- Lenses run: {list} | Skipped: {lens - reason}

### Test Plan
- `test-plan.md`: {n} scenarios ({p1} P1) | Requirements without a scenario: {n}

### Carried Conditions
| ID | Condition | Tracked as |

### Next Step
Run `/specforge.qa` to validate the implementation end-to-end against `test-plan.md`.
```

Report failing checks with their output. A task whose verification failed is `[~]`, never `[X]`.

## Error Handling

- **Missing tasks.md**: STOP - run `/specforge.design` first
- **Missing complexity-analysis.md**: WARN, treat all phases as DIRECT, derive lenses from content
- **Design gate BLOCK**: report and ask before proceeding; record the decision in the build gate
- **Phase implementation failure**: Log and continue to next phase
- **Critical confirmed finding on a production path**: fix before continuing, or stop and report
- **Review failure**: Log error, skip corrections, report to user
- **Test plan generation failure**: WARN and continue to the gate; QA will fall back to the spec's
  acceptance scenarios, with materially thinner coverage - say so in the report
