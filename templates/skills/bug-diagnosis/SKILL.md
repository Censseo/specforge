---
name: bug-diagnosis
description: |
  Find the root cause of a defect and fix it, using 5 Whys, Ishikawa categorisation and the scientific
  method - then verify the fix and update the bug record. Activate when: something is broken, a
  validation failed, a bug report exists, or behavior does not match the spec.
triggers: ["diagnose", "why is this failing", "root cause", "fix the bug", "debug", "5 whys", "it doesn't work"]
semantic_anchors: [5 Whys, Ishikawa Diagram, Scientific Method, Rubber Duck Debugging, Fail Fast]
phase: qa
---

# Bug Diagnosis and Fix

> You are the fixer. Escalate only for credentials, access or a genuine product decision - not because
> the defect is in an unfamiliar layer.

## Problem Categories

| Category | Symptom | Root cause pattern | Action |
| -------- | ------- | ------------------ | ------ |
| Spec gap | Works, but not what was needed | Spec incomplete or ambiguous | Choose a sensible default, record the assumption, implement |
| Implementation bug | Code does not match spec | Logic error | Fix the code |
| Misunderstanding | Wrong thing built entirely | Requirements misread | Re-frame with Jobs-to-Be-Done, update spec, re-implement |
| Integration | Parts work alone, fail together | Missing glue, wrong coupling | Add the integration |
| Performance | Works but too slow or heavy | NFR not met | Optimise, with a measurement |

## Phase 1 - Gather

Load unresolved bugs from `validation/bugs/` (the structured, preferred source), then user-reported
symptoms, then `validation/report-*.md`. Read each bug file in full.

If the input is vague, ask exactly four things: what did you expect, what happened, when did it start,
what is the error text. Then stop asking and start investigating.

Record a symptoms table: symptom, affected area, severity, user's own words verbatim.

## Phase 2 - Diagnose

### Spec vs implementation

For each affected story, compare requirement by requirement: implemented / where / working, buggy or
missing. The gap list is the work list.

### Plan vs reality

Compare `tasks.md` against `task-results/`. Tasks marked complete but broken are the highest-signal
lead available - the deviation is usually recorded there already.

### Root cause - 5 Whys

Ask "why" until the answer stops being a restatement. Stop at the cause you can actually change.

```markdown
| Symptom | 5 Whys conclusion | Ishikawa category | Confidence |
| ------- | ----------------- | ----------------- | ---------- |
| Login 500 | Exception uncaught -> no error contract for this path | Equipment (code) | High |
```

Ishikawa categories: Equipment (code), Process (spec), People (misunderstanding), Materials
(integration), Environment (config, infrastructure).

### Scientific method

State the hypothesis, name the experiment that would falsify it, run it, record the observation.
Never fix on a hypothesis you did not test - a fix that changes the symptom without addressing the
cause moves the bug rather than removing it.

## Phase 3 - Impact

Files to change, dependency order, risk per change with a mitigation, and effort split between code
fixes, spec clarifications and re-validation.

## Phase 4 - Plan

Two groups: **immediate fixes** (implementation defects) and **spec clarifications** (gaps needing a
decision). Then choose a path:

| Path | When |
| ---- | ---- |
| A - code fixes only | Cause is understood and lives in code |
| B - clarify first | A gap must be resolved before the fix is meaningful |
| C - major misunderstanding | The wrong thing was built; revisit the idea, decide salvage vs restart |

## Phase 5 - Fix

For each fix, in dependency order: locate the cause, apply the change, verify it (test it, add a
regression test that fails without the fix), and record what changed.

For spec gaps, prefer a documented assumption over a blocking question. Ask only when the choice is
genuinely ambiguous with no defensible default - and keep fixing the other issues meanwhile.

## Phase 6 - Record

- Update bug frontmatter: `status: resolved`, `resolved_date`, `fix_applied`; add a `## Resolution`
  section with the change and its verification.
- Mark fix tasks complete in `tasks.md`; downgrade broken "complete" tasks to `[~]` with the fix id.
- Save `task-results/FIX-XXX-result.md` and `fix-analysis-{date}.md`.

## Output

Report what was **done**, not what is proposed: bugs resolved, files modified, assumptions made
(flagged for review), verification status per fix. If a fix could not be completed, name the specific
blocker.

## Quick Fix Mode

Given `path:line` and a symptom: read the context, identify the defect, fix it, verify it, report the
before and after. No ceremony.

## Handoff

Re-run `integration-validation` to confirm. A fix is not done until the scenario that caught it passes.
