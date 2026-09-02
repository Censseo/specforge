---
description: Macro command that runs the full design pipeline from specification through task generation with automated quality checks and an adversarial design review.
skills:
  - specforge-workflow
  - adversarial-review
  - finding-verification
  - quality-gates
lenses:
  - lens-requirements
  - lens-architecture
  - lens-domain-model
  - lens-api-contract
  - lens-data
  - lens-security
  - lens-privacy-compliance
  - lens-reliability
semantic_anchors:
  - Pipeline Orchestration  # Sequential stage execution with gates
  - Fail Fast               # Detect issues early, abort on critical failures
  - Convention over Configuration  # Apply defaults for non-interactive steps
  - Falsification           # A finding must survive an attempt to disprove it
  - Blast Radius            # Calibrate review rigor to what breaks if this is wrong
handoffs:
  - label: Build Implementation
    agent: specforge.build
    prompt: Run the build pipeline for this feature
    send: true
  - label: Re-run Design
    agent: specforge.design
    prompt: Re-run the design pipeline with adjustments
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --paths-only
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

## User Input

```text
$ARGUMENTS
```

Consider the user input before proceeding (if not empty).

## Outline

This macro command orchestrates the full design pipeline: specify, clarify, plan, adversarial review,
checklist, tasks, and analyze. It runs non-interactively where possible, applying recommended defaults
and remediations automatically.

1. Run `/specforge.specify` on user input
2. Run `/specforge.clarify` in non-interactive mode
3. Run `/specforge.plan`
4. Run the adversarial design review through the design lenses
5. Run `/specforge.checklist` (pre-implementation + review with auto-remediation)
6. Run `/specforge.tasks`
7. Run `/specforge.analyze` with auto-remediation
8. Perform complexity analysis of tasks.md phases
9. Record the design gate verdict and report completion

Run `{SCRIPT}` first to resolve `REPO_ROOT`, `BRANCH` and `FEATURE_DIR`. Load
`/memory/constitution.md` and `/memory/architecture-registry.md` before step 1 - they outrank every
artifact this pipeline produces.

## Detailed Steps

### Step 1: Specify

Invoke the specify sub-command to create the feature specification from user input.

```text
Skill: specforge.specify
Args: $ARGUMENTS
```

**Gate check**: Verify spec.md exists and is non-empty. Extract FEATURE_DIR path. If spec creation
failed, STOP and report.

### Step 2: Clarify (Non-Interactive)

Run clarification against docs/ and existing implementations.

```text
Skill: specforge.clarify
Args: Explore the docs/ and the existing implementations related to this feature to clarify integration points. Raise all unclear points. You are in non-interactive mode: for each question, apply the recommended remediation by default. Do not wait for user input. Apply all clarifications directly to the spec.
```

**Gate check**: Verify spec.md was updated. If clarify found no ambiguities, that is fine - proceed.

Every auto-applied answer is recorded under `## Clarifications` as an assumption, so the design review
in step 4 can attack it. An assumption nobody wrote down cannot be reviewed.

### Step 3: Plan

Generate the implementation plan.

```text
Skill: specforge.plan
Args: (no additional arguments)
```

**Gate check**: Verify plan.md and research.md exist in FEATURE_DIR. If plan reported architecture
divergences needing user approval, STOP and present them.

### Step 4: Adversarial Design Review

Attack the design artifacts before tasks are generated from them. A defect fixed here costs an edit;
the same defect found after implementation costs a redesign.

Apply the `adversarial-review` skill.

1. **Frame** in five lines: target (spec.md, plan.md, data-model.md, contracts/), intent, invariants,
   blast radius, reversibility. Blast radius and reversibility set the rigor for the rest of the pass.

2. **Select lenses**: the eight defaults in this command's frontmatter, minus any with no surface in
   this feature, plus any whose risk trigger fires (see
   `adversarial-review/references/lens-registry.md`). Record every skip with its reason - an
   unrecorded skip is a silent hole.

3. **Red pass**: run each lens's probes against the actual artifact text, not a summary of it.

4. **Falsify**: apply `finding-verification` to every candidate. Trace the failure path end to end,
   run the refutation checklist. Drop what is refuted rather than downgrading it.

5. **Triage**: dedupe by root cause, assign severity by the harness rubric, mark blocking per
   `quality-gates`.

**Non-interactive remediation**: fix confirmed non-blocking findings directly in the artifacts - a
missing error case in a contract, an unquantified NFR, an undefined cascade, an unenforced invariant.
Record each fix in the design gate record.

**Gate check**: If any **blocking** finding remains (Critical, or High and confirmed, or a
constitution MUST violation, or an unreviewed one-way door), STOP and report it with the failure
scenario and the proposed fix. Do not continue to task generation on a broken design.

### Step 5: Checklists - Generate and Auto-Remediate

#### Step 5a: Generate pre-implementation checklists

```text
Skill: specforge.checklist
Args: pre-implementation, for all domains, for deviation check and constitution and architecture compliance, single consolidated file. You are in non-interactive mode, if you need user answer, use your recommended answer.
```

#### Step 5b: Review and remediate

```text
Skill: specforge.checklist
Args: review. Propose and apply remediation for failing and partial items. You are in non-interactive mode, if you need user answer, use your recommended answer.
```

**Gate check**: If any CRITICAL checklist items remain FAIL after remediation, STOP and report.
LOW/MEDIUM warnings are logged and we proceed.

### Step 6: Tasks

Generate the dependency-ordered task list.

```text
Skill: specforge.tasks
Args: (no additional arguments)
```

**Gate check**: Verify tasks.md exists in FEATURE_DIR with proper format (T### IDs, checkboxes,
phases). Verify every step-4 finding that produced a code change has a task covering it.

### Step 7: Analyze and Auto-Remediate

Run cross-artifact consistency analysis and apply fixes.

```text
Skill: specforge.analyze
Args: propose and apply remediations for all findings. Do not ask the user - apply reasonable fixes directly.
```

**Gate check**: If CRITICAL findings remain after remediation, STOP and report. Otherwise proceed.

### Step 8: Complexity Analysis

Read the final tasks.md and analyze each phase to determine which need `/specforge.breakdown` before
`/specforge.implement`.

**Evaluation criteria per phase:**

| Criteria | DIRECT (implement directly) | BREAKDOWN (needs breakdown first) |
|----------|---------------------------|----------------------------------|
| Task count | <= 8 tasks | > 8 tasks |
| Cross-domain scope | 1-2 domains | 3+ domains (backend+frontend+DB) |
| Dependency density | Mostly parallel [P] tasks | Many sequential dependency chains |
| Reuse complexity | REUSE/NEW only | REFACTOR or complex EXTEND tasks |
| Review exposure | No blocking lens triggers | Touches security, data migration, concurrency or a public contract |

A phase **needs breakdown** if it meets 2 or more BREAKDOWN criteria.

The review-exposure row also decides which lenses the build pipeline runs on that phase. Record them.

**Save output** to `FEATURE_DIR/complexity-analysis.md`:

```markdown
# Complexity Analysis

**Feature**: {feature-name}
**Date**: {date}
**Source**: tasks.md

## Phase Analysis

| Phase | Name | Tasks | Domains | Dependencies | Reuse | Lenses | Verdict |
|-------|------|-------|---------|--------------|-------|--------|---------|
| 1 | ... | N | N | N sequential | types | security,data | DIRECT or BREAKDOWN |

## Summary

- **Direct implement**: Phase X, Phase Y
- **Needs breakdown**: Phase Z, Phase W
- **Total phases**: N
```

### Step 9: Design Gate Record

Apply the `quality-gates` skill, design gate criteria D1-D10. Write
`FEATURE_DIR/gates/design-{date}.md` with the verdict, the criteria table, the findings from step 4
and the conditions carried forward.

A gate with no record did not happen. Carried conditions become tasks with owners in `tasks.md`.

### Step 10: Report

Output a summary:

```markdown
## Design Pipeline Complete

**Feature**: {feature-name}
**Branch**: {branch-name}
**Gate**: {PASS | PASS WITH CONDITIONS | BLOCK}

### Artifacts Generated
- spec.md, plan.md, research.md, tasks.md, checklists/, complexity-analysis.md, gates/design-{date}.md

### Quality Status
- Checklist: {passed}/{total} pass
- Analyze: {critical} critical, {high} high remaining
- Adversarial review: {findings} findings ({fixed} fixed in place, {blocking} blocking)
- Lenses run: {list} | Skipped: {lens - reason}

### Complexity Verdicts
- Direct implement: {phases}
- Needs breakdown: {phases}

### Carried Conditions
| ID | Condition | Tracked as |

### Next Step
Run `/specforge.build` to start implementation.
```

## Error Handling

- **Spec creation failure**: STOP - nothing downstream is meaningful
- **Plan architecture divergence**: STOP and present the divergence for approval
- **Blocking review finding**: STOP - report the failure scenario and the smallest fix
- **CRITICAL checklist item still FAIL after remediation**: STOP and report
- **CRITICAL analyze finding after remediation**: STOP and report
- **Artifacts that cannot be evaluated** (missing file, unreadable): gate verdict is BLOCK with
  reason `not-evaluable`, never PASS
