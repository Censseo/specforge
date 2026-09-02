---
description: Run the DESIGN phase - specify, clarify and plan a feature, then red-team the design artifacts through domain lenses and clear the design gate.
skills:
  - specforge-workflow
  - spec-authoring
  - requirements-clarification
  - technical-planning
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
  - EARS Syntax
  - INVEST Criteria
  - Clean Architecture
  - ADR
  - Blast Radius
  - One-Way Door
handoffs:
  - label: Run Build Phase
    agent: specforge.build
    prompt: Decompose the plan into tasks and implement it
    send: true
  - label: Clarify Further
    agent: specforge.clarify
    prompt: Resolve the remaining ambiguities in the spec
  - label: Re-run Design Review
    agent: specforge.harness
    prompt: Re-run the design lenses on the updated artifacts
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --paths-only
  ps: scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly
---

## User Input

```text
$ARGUMENTS
```

# Design Phase

Phase 1 of 3. Produce design artifacts that are worth building and unambiguous enough to build
correctly, then attack them before anyone writes code.

Load the `specforge-workflow` skill for the phase model, and each step's skill as you reach it.

## Step 0 - Situate

Run `{SCRIPT}` and parse `REPO_ROOT`, `BRANCH`, `FEATURE_DIR`, `FEATURE_SPEC`, `IMPL_PLAN`.

Determine the entry point from what already exists:

| State | Entry |
| ----- | ----- |
| No spec, request is vague or spans several capabilities | `/specforge.idea` first, then return here |
| No spec, request is a clear single feature | Step 1 |
| Spec exists, no plan | Step 2 |
| Spec and plan exist | Step 3 |

Load `/memory/constitution.md` and `/memory/architecture-registry.md` before anything else. They
outrank everything you are about to write.

## Step 1 - Specify

Apply the `spec-authoring` skill. If no spec exists for this branch, run `/specforge.specify` with the
user's description to create the branch and the spec file, then continue here.

Output: `spec.md`, `checklists/requirements.md`.

## Step 2 - Clarify

Apply the `requirements-clarification` skill. Skip only when the spec has no Partial or Missing
category in the coverage scan - and say so explicitly rather than skipping silently.

Output: `spec.md` §Clarifications, with every answer integrated into the section it affects.

## Step 3 - Plan

Apply the `technical-planning` skill. Reuse before inventing; record every decision with its
alternatives and consequences; stop and ask on any divergence from the architecture registry.

Output: `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`.

## Step 4 - Adversarial Design Review

Apply the `adversarial-review` skill.

1. **Frame**: target (the design artifacts), intent, invariants, blast radius, reversibility.
2. **Select lenses**: the eight defaults above, minus any with no surface in this feature (record the
   skip and the reason), plus any lens whose risk trigger fires - see
   `adversarial-review/references/lens-registry.md`.
3. **Red pass**: run each lens's probes against the actual artifact text. Assume it is wrong.
4. **Falsify**: apply `finding-verification` to every candidate. Drop what is refuted.
5. **Triage**: dedupe by root cause, assign severity by rubric, mark blocking per `quality-gates`.

Findings that are cheap to fix now - a missing error case in a contract, an unquantified NFR, an
undefined cascade - fix them in the artifact immediately rather than filing them.

## Step 5 - Design Gate

Apply the `quality-gates` skill, design gate criteria D1-D10.

Write `FEATURE_DIR/gates/design-{date}.md` with the verdict, the criteria table, the findings and the
conditions. A gate with no record did not happen.

## Report

```markdown
## Design Phase: {VERDICT}

**Feature**: {name} | **Branch**: {branch}

### Artifacts
| Artifact | Path | Status |

### Adversarial Review
| Lens | Findings | Blocking |
Skipped: {lens - reason}

### Blocking Findings
| ID | Severity | Location | Claim | Fix |

### Conditions to Clear the Gate
1. ...

### Next
- PASS -> `/specforge.build`
- BLOCK -> fix the blocking findings, then re-run `/specforge.design`
```

Never report PASS with blocking findings open. If the artifacts could not be evaluated, the verdict is
BLOCK with reason `not-evaluable`.
