---
description: Apply small, focused changes to an existing feature - bug fixes, spec tweaks, user feedback, or refinements - without the overhead of the full workflow.
skills:
  - focused-change
  - bug-diagnosis
semantic_anchors:
  - Kaizen                # Continuous small improvements, Toyota Production System
  - Boy Scout Rule        # Leave it better than you found it
  - Hotfix                # Targeted fix with minimal scope
  - Ship of Theseus       # Incremental change while maintaining identity
  - Continuous Delivery   # Small, frequent, safe changes
  - YAGNI                 # Don't over-engineer the change
handoffs:
  - label: Full Specify
    agent: specforge.specify
    prompt: This change is too large for /change. Run full specification workflow.
  - label: Validate Change
    agent: specforge.validate
    prompt: Validate that the change works as expected
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

## Method

Apply the **`focused-change`** skill: the scope test, the four change paths, and the traceability rules.

Use this instead of the full workflow when the change is small and local. The workflow exists to
control risk; where there is no risk, it is overhead - but traceability never is.

## Step 1 - Triage and Scope Check

Run `{SCRIPT}` and load only what the change touches: the relevant spec section, the affected files,
and the related task line.

Detect the type:

| Type | Triggers | Path |
| ---- | -------- | ---- |
| Bug fix | "broken", "error", "fails", an error message | Fix the code |
| Spec tweak | "clarify", "update spec", "add requirement", "edge case" | Edit the spec, then cascade |
| User feedback | "user said", "testing showed", "feedback" | Categorise, then apply |
| Refinement | "improve", "optimise", "polish", "cleaner" | Refactor, behavior unchanged |
| Too large | Multiple features, new entities, architecture | Escalate |

Apply the skill's scope test. Escalating to `/specforge.specify` or `/specforge.design` is a correct
outcome - a "quick change" that becomes a redesign mid-flight is not.

## Step 2 - Apply the Change

Follow the path from the skill. In every path:

- Fix at the cause, not at the symptom.
- Verify by running the affected test; add a regression test for a bug fix.
- For a refinement, run the existing tests before and after - if a test needed changing, it was not a
  refinement.

## Step 3 - Traceability

Update whatever the change made untrue:

| Change | Update |
| ------ | ------ |
| Behavior differs from the spec | `spec.md`, and a `## Clarifications` entry with the date |
| A task marked `[X]` was actually broken | Downgrade to `[~]` with a note |
| A new edge case is now handled | The relevant requirement |
| Pure refactoring | Nothing - optional note in the commit |

## Step 4 - Red Pass Where It Matters

When the change touches security, data, a public contract or a permission, run the matching lens
(`lens-security`, `lens-data`, `lens-api-contract`) before finishing. Small changes in those areas are
exactly where the expensive defects live.

## Report

```markdown
## Change Complete

**Type**: {type} | **Scope**: {files touched}

### What Changed
### Verification
| Check | Result |

### Traceability Updated
### Next
```
