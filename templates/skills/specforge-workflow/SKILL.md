---
name: specforge-workflow
description: |
  The SpecForge three-phase workflow - design, build, qa - with the skills, artifacts and gates that
  belong to each phase. Activate when: orchestrating a feature end to end, deciding which phase or
  skill applies next, or resuming work on a feature in progress.
triggers: ["workflow", "what next", "design build qa", "orchestrate feature", "resume feature", "which phase", "specforge workflow"]
workflow:
  phases: [design, build, qa]
---

# SpecForge Workflow

> Three phases, three gates. Each phase produces artifacts, each gate produces a verdict, and no phase
> starts on an unverified predecessor.

## The Phases

```text
DESIGN                        BUILD                        QA
idea -> spec -> clarify       tasks -> implement           validate -> analyze -> review
  -> plan                       -> incremental review        -> checklists
  -> adversarial design pass    -> adversarial code pass     -> adversarial release pass
  -> DESIGN GATE                -> BUILD GATE                -> QA GATE
```

## Phase 1 - Design

**Question**: is this worth building, and is it specified well enough to build correctly?

| Step | Skill | Artifact |
| ---- | ----- | -------- |
| Shape the idea (optional, for vague or large requests) | `idea-shaping` | `idea.md`, `features/##-*.md` |
| Write the specification | `spec-authoring` | `spec.md`, `checklists/requirements.md` |
| Remove ambiguity | `requirements-clarification` | `spec.md` §Clarifications |
| Plan the implementation | `technical-planning` | `plan.md`, `research.md`, `data-model.md`, `contracts/` |
| Adversarial pass | `adversarial-review` + design lenses | findings |
| Verify findings | `finding-verification` | verdicts |
| Gate | `quality-gates` | `gates/design-{date}.md` |

Default lenses: requirements, architecture, domain-model, api-contract, data, security,
privacy-compliance, reliability.

Exit: design gate PASS or PASS WITH CONDITIONS.

## Phase 2 - Build

**Question**: does the code do what the design says, and nothing it must not?

| Step | Skill | Artifact |
| ---- | ----- | -------- |
| Decompose into tasks | `task-decomposition` | `tasks.md` |
| Execute the tasks | `implementation-execution` | code, `task-results/` |
| Adversarial pass per increment | `adversarial-review` + build lenses | findings |
| Verify findings | `finding-verification` | verdicts |
| Gate | `quality-gates` | `gates/build-{date}.md` |

Default lenses: architecture, maintainability, security, concurrency, data, testing, performance,
api-contract.

Run the adversarial pass **per phase of `tasks.md`**, not once at the end. A defect found three tasks
later costs a fix; found at the end it costs a redesign.

Exit: build gate PASS or PASS WITH CONDITIONS.

## Phase 3 - QA

**Question**: does it work in the running system, for real users, and can it be operated?

| Step | Skill | Artifact |
| ---- | ----- | -------- |
| Execute acceptance scenarios | `integration-validation` | `validation/report-*.md`, `validation/bugs/` |
| Diagnose and fix failures | `bug-diagnosis` | fixes, `fix-analysis-*.md` |
| Cross-artifact consistency | `artifact-analysis` | analysis report |
| Requirements quality review | `quality-checklists` | `checklists/*.md` |
| Adversarial pass | `adversarial-review` + qa lenses | findings |
| Verify findings | `finding-verification` | verdicts |
| Gate | `quality-gates` | `gates/qa-{date}.md` |

Default lenses: requirements, testing, security, reliability, performance, observability,
accessibility, operations.

Exit: qa gate PASS or PASS WITH CONDITIONS. Then `feature-merge`, then `codebase-learning`.

## Choosing the Entry Point

| Situation | Start at |
| --------- | -------- |
| Vague or large request, multiple capabilities | `idea-shaping` |
| Clear single feature | `spec-authoring` |
| Spec exists, ambiguity suspected | `requirements-clarification` |
| Spec and plan exist, no tasks | `task-decomposition` |
| Small correction inside an existing feature | `focused-change` - no full workflow |
| Bug reported against shipped behavior | `bug-diagnosis` |
| Reviewing someone else's work | `adversarial-review` directly |

Do not run the full workflow for a one-line fix. The phases exist to control risk; where there is no
risk, they are overhead.

## Resumption

State lives in files, not in the conversation. To resume, read in this order:

1. `gates/` - the last verdict and its open conditions.
2. `tasks.md` - what is done, partial, or blocked.
3. `validation/bugs/` - what is open.
4. `task-results/` - what actually happened, including deviations.

Then re-enter at the earliest phase with an open blocking item.

## Rules That Hold Across Phases

- A gate verdict is stale once its artifacts change. Re-run it.
- Findings verified as REFUTED stay refuted until the code they were refuted against changes.
- Traceability is maintained continuously: requirement -> task -> code -> test -> scenario. Any break
  is a finding for `lens-requirements`, whatever phase notices it.
- `/memory/constitution.md` outranks every other document. A conflict with a MUST is Critical and
  blocking, always.
- Every phase writes down what it did not do, and why.
