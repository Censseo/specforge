---
name: adversarial-test-planning
description: |
  Build a test plan that covers every scenario of a feature and is designed to break it - happy paths,
  boundaries, failures, permissions, concurrency and regressions - as an executable checklist another
  session can run. Activate when: writing a test plan, planning validation coverage, or before a QA run.
triggers: ["test plan", "adversarial test plan", "test scenarios", "coverage plan", "how do we test this", "qa plan", "validation plan"]
semantic_anchors: [BDD Gherkin, Specification by Example, Exploratory Testing, Boundary Value Analysis, FMEA, Mutation Testing]
phase: build
produces: test-plan.md
---

# Adversarial Test Planning

> A test plan written from the specification tests what you intended. A plan written adversarially
> tests what you actually built. The gap between the two is where the bugs live.

The output is a file another session executes without any of your context. Write it for that reader:
every scenario names its preconditions, its exact steps, its expected outcome and how to tell pass from
fail.

## Inputs

| Source | What to take |
| ------ | ------------ |
| `spec.md` | User stories, acceptance scenarios, functional requirements, edge cases |
| `plan.md`, `data-model.md`, `contracts/` | Boundaries, states, error codes, invariants worth attacking |
| `tasks.md`, `task-results/` | What was actually built, and every recorded deviation and gotcha |
| The diff | What changed - and therefore what could have regressed |
| `quickstart.md` | How to run the thing, seed data, credentials |

`task-results/` is the highest-value input and the one most often skipped. A recorded deviation or
gotcha is a defect the implementer already suspected; each one deserves a scenario.

## Coverage Model

Every scenario belongs to exactly one class. A plan missing a whole class is not a thorough plan with
a gap - it is a plan that will pass while the feature is broken.

| # | Class | Question it answers | Minimum |
| - | ----- | ------------------- | ------- |
| C1 | **Happy path** | Does the primary flow work end to end, as specified | One per user story |
| C2 | **Boundary** | 0, 1, max, max+1, empty, very long, unicode, negative, duplicate | One per constrained input |
| C3 | **Invalid input** | Malformed, wrong type, missing field, injection-shaped strings | One per entry point |
| C4 | **Permission** | What each actor cannot do - including another user's records by id | One per protected resource |
| C5 | **State** | Illegal transitions, acting on an expired, deleted or already-processed entity | One per state machine |
| C6 | **Failure** | Dependency down, slow, timing out, returning garbage; partial failure mid-operation | One per external dependency |
| C7 | **Concurrency** | The same action twice, simultaneously, out of order; double submit; stale edit | One per write path with shared state |
| C8 | **Regression** | What existed before and must still work, especially anything sharing code with the change | One per touched shared component |
| C9 | **Data integrity** | After the flow, is the stored state exactly what it should be | One per persisting flow |
| C10 | **Exploratory** | Charters, not scripts - "try to make the export produce an empty file" | Two or three per feature |

For a UI feature, add accessibility (keyboard-only completion, screen-reader names) and the five
states: empty, loading, partial, error, ideal.

## Deriving Scenarios Adversarially

Do not paraphrase the acceptance criteria. Attack them:

- **Invert each requirement.** "Only the owner can delete" becomes "log in as a non-owner and delete".
  Every MUST, NEVER, ONLY and AT MOST in the spec is a scenario in its negative form.
- **Walk each boundary from the model.** Every constrained field in `data-model.md` gives you its
  minimum, its maximum, one past each, and its empty case.
- **Take each error branch in the contract.** Every documented status code needs a scenario that
  produces it. An error the plan never triggers is an error nobody has seen work.
- **Mine the deviations.** Every gotcha in `task-results/` is a scenario. So is every assumption
  auto-applied during clarification - those were decisions made without the user.
- **Ask what would embarrass us.** Money wrong, data lost, another tenant's record shown, a stuck
  job nobody notices. Write the scenario that would catch each, even if you think it cannot happen.
- **Name the regression surface.** List what shares code with the change. Each of those is C8.

## Scenario Format

Each scenario is executable by someone with the file and the running app, and nothing else.

```markdown
### TP-014 - Refund exceeding the original amount is rejected [C3] [US2] [P1]

**Why this exists**: `refund.ts:40-88` added the refund path; the branch `amount > original`
is unreachable in the current test suite.

**Preconditions**: An order in state `paid`, total 50.00 EUR, seeded by `scripts/seed-order.sh`.
Logged in as `finance@test.local`.

**Steps**:
1. POST /api/orders/{id}/refund with `{"amount": 75.00}`
2. Read the response
3. GET /api/orders/{id}

**Expected**: 422 with error code `refund_exceeds_total`. Order state unchanged at `paid`,
no refund record created, no ledger entry written.

**Fails if**: any 2xx; a refund record exists; the order state changed; a 500 instead of 422.
```

Rules:

- Stable id `TP-###`, class tag, story tag, priority.
- **Why this exists** in one line. A scenario nobody can justify gets deleted at the first time crunch;
  one with a reason survives.
- Expected outcome states the **observable** result, including the stored state - not "it works".
- **Fails if** exists so that a reader cannot rationalise a bad result into a pass.
- No scenario depends on another having run first, unless it declares that dependency explicitly.

## Prioritisation

| Priority | Meaning |
| -------- | ------- |
| **P1** | Blocks release if it fails. Primary flows, permissions, money, data integrity |
| **P2** | Fix before merge. Secondary flows, documented error handling, regressions |
| **P3** | Track. Polish, rare edge cases, cosmetic |

A smoke run executes P1 only. If P1 takes more than about fifteen scenarios, the feature is doing too
much or the plan is padded - re-read it.

## Honesty Rules

- Mark scenarios that **cannot be executed** in this environment as `BLOCKED` with the reason. A plan
  that silently omits what it cannot test reports better coverage than it has.
- State the coverage you are **not** attempting, and why. "No load testing - no environment for it" is
  useful; silence is not.
- Do not write a scenario whose expected outcome you had to guess. Ask, or mark it `NEEDS DECISION`.
- Never write the plan to match the implementation you just read. If a scenario's expected outcome
  comes from the code rather than the spec, it tests that the code does what it does.

## Output File

Write to `FEATURE_DIR/test-plan.md`:

```markdown
# Adversarial Test Plan: {feature}

**Date**: {date} | **Source**: spec.md, plan.md, tasks.md, task-results/, diff {range}
**Scenarios**: {n} ({p1} P1, {p2} P2, {p3} P3) | **Blocked**: {n}

## How To Run

{Commands to start the system, seed data, and where credentials come from}

## Coverage Map

| Class | Scenarios | Notes |
| ----- | --------- | ----- |
| C1 Happy path | TP-001..004 | |
| C2 Boundary | TP-005..011 | |
| ... | | |

| Requirement | Scenarios |
| ----------- | --------- |
| FR-001 | TP-001, TP-014 |

## Not Covered

| Area | Why | Risk accepted |
| ---- | --- | ------------- |

## Scenarios

{one block per scenario, in the format above}
```

The requirement-to-scenario table is the part reviewers actually use: a requirement with no scenario
is an untested requirement, and that is a finding for `lens-testing` regardless of what the plan says
about itself.
