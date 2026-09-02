---
description: Run the QA phase - execute acceptance scenarios against the running system, analyse artifact consistency, red-team the release through operational lenses and clear the release gate.
skills:
  - specforge-workflow
  - integration-validation
  - bug-diagnosis
  - artifact-analysis
  - quality-checklists
  - adversarial-review
  - finding-verification
  - quality-gates
lenses:
  - lens-requirements
  - lens-testing
  - lens-security
  - lens-reliability
  - lens-performance
  - lens-observability
  - lens-accessibility
  - lens-operations
semantic_anchors:
  - ATDD
  - BDD Gherkin
  - Exploratory Testing
  - Regression Testing
  - FMEA
  - Four Golden Signals
handoffs:
  - label: Fix Failures
    agent: specforge.fix
    prompt: Diagnose and fix the validation failures
    send: true
  - label: Merge the Feature
    agent: specforge.merge
    prompt: Consolidate the docs and merge the feature branch
  - label: Re-run Release Review
    agent: specforge.harness
    prompt: Re-run the qa lenses on the feature
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

Scope hints: `full` (default), `smoke`, `US1`, `api`, `ui`.

# QA Phase

Phase 3 of 3. Does it work in the running system, for real users, and can it be operated?

Load the `specforge-workflow` skill for the phase model, and each step's skill as you reach it.

## Step 0 - Entry Check

Run `{SCRIPT}` and parse `FEATURE_DIR` and `AVAILABLE_DOCS`. Verify the build gate record exists and
is PASS or PASS WITH CONDITIONS; list any open conditions before starting.

Read `tasks.md` to determine what is actually testable. Testing a story whose tasks are unfinished
produces failures that mean nothing.

## Step 1 - Execute Acceptance Scenarios

Apply the `integration-validation` skill. Start the environment, run the Given/When/Then scenarios by
priority, capture evidence for every scenario, and run an exploratory pass alongside the scripted one.

Report status honestly: `INCOMPLETE` when execution errors prevented testing, `PARTIAL` when scenarios
were skipped. Never `PASSED` for either.

Output: `validation/report-{date}.md`, `validation/bugs/BUG-*.md`, `validation/screenshots/`.

## Step 2 - Diagnose and Fix

Apply the `bug-diagnosis` skill to every unresolved bug, in severity order. Root-cause each one before
fixing it, add the regression test that fails without the fix, and update the bug record.

Then re-run the scenarios that caught them. A fix is not done until the failing scenario passes.

## Step 3 - Cross-Artifact Analysis

Apply the `artifact-analysis` skill: duplication, ambiguity, underspecification, constitution
conflicts, coverage gaps, terminology drift across `spec.md`, `plan.md` and `tasks.md`.

Read-only. Propose remediation; apply nothing without approval.

## Step 4 - Requirements Quality Review

Apply the `quality-checklists` skill in review mode over `checklists/`. Every PASS needs an evidence
location. Generate a domain checklist where a risk area has none.

## Step 5 - Adversarial Release Review

Apply the `adversarial-review` skill against the feature as a whole - code, configuration, contracts
and operational surface.

Default lenses above; drop any with no surface here and record the skip; add any whose risk trigger
fired. Falsify every candidate with `finding-verification`.

Give particular weight to what only exists now that the system runs: what happens when a dependency is
down (`lens-reliability`), how anyone would notice (`lens-observability`), how this deploys and rolls
back (`lens-operations`).

## Step 6 - QA Gate

Apply the `quality-gates` skill, QA gate criteria Q1-Q8. Write `FEATURE_DIR/gates/qa-{date}.md`.

## Report

```markdown
## QA Phase: {VERDICT}

**Validation status**: {PASSED | FAILED | PARTIAL | INCOMPLETE}

### Scenarios
| Story | Scenarios | Passed | Failed | Skipped |

### Bugs
| ID | Severity | Status | Story |

### Cross-Artifact Analysis
| Category | Findings | Critical |

### Adversarial Review
| Lens | Findings | Blocking |
Skipped: {lens - reason}

### Open Blocking Items
### Next
- PASS -> `/specforge.merge`
- BLOCK -> `/specforge.fix`, then re-run `/specforge.qa`
```
