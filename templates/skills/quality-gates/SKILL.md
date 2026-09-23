---
name: quality-gates
description: |
  Phase gates for the design -> build -> qa workflow: entry criteria, exit criteria, blocking rules and
  gate records. Activate when: deciding whether a phase is complete, whether to proceed to the next
  phase, or how to score a review verdict.
triggers: ["quality gate", "gate check", "definition of done", "can we proceed", "exit criteria", "phase gate", "ready to ship"]
harness:
  id: quality-gates
  phases: [design, build, qa]
  produces: gate-record
---

# Quality Gates

> A gate that never blocks is a decoration. A gate that always blocks is a wall. These gates block on
> evidence and pass on evidence, and they write down which one happened.

## Gate Verdicts

| Verdict | Meaning | Effect |
| ------- | ------- | ------ |
| **PASS** | All exit criteria met, no blocking findings open | Proceed to the next phase |
| **PASS WITH CONDITIONS** | Exit criteria met, open findings are advisory and recorded as owned follow-ups | Proceed; conditions tracked in `tasks.md` |
| **BLOCK** | An exit criterion failed or a blocking finding is open | Do not proceed; fix and re-run the gate |

`not-evaluable` (missing artifact, unreadable diff, no way to run the code) is a BLOCK, never a PASS.

## Blocking Rules

A finding is blocking when **any** of these hold:

- Severity is Critical.
- Severity is High **and** confidence is `confirmed`.
- It violates a MUST in `/memory/constitution.md` (always blocking, regardless of severity).
- It is a one-way door: data migration, public contract change, deletion, or external side effect
  that cannot be undone once shipped.
- It breaks a stated invariant from the framing step of the review.

Everything else is advisory. Advisory findings still get an owner and a task; they do not stop the phase.

Cost of the fix never changes whether a finding blocks. Expense is a condition to negotiate, not a
reason to reclassify.

## Design Gate

**Purpose**: the thing is worth building, buildable, and unambiguous enough to build correctly.

Entry criteria:

- A spec exists for the feature (`spec.md`), with user scenarios and functional requirements.
- The constitution has been loaded.

Exit criteria:

| # | Criterion | Evidence |
| - | --------- | -------- |
| D1 | Every functional requirement is testable and unambiguous | `lens-requirements` pass with no open High+ finding |
| D2 | Every requirement has at least one acceptance scenario | Traceability table in the spec |
| D3 | No unresolved `[NEEDS CLARIFICATION]` marker that affects scope, security, or data | Spec scan |
| D4 | Success criteria are measurable and technology-agnostic | Spec §Success Criteria |
| D5 | Architecture decisions are recorded with alternatives and consequences | `plan.md` §Architecture Alignment or an ADR |
| D6 | Divergences from the architecture registry are justified and approved | `plan.md` alignment report |
| D7 | Data model states entities, invariants, and lifecycle | `data-model.md` |
| D8 | Contracts state error cases and status codes, not only happy paths | `contracts/` |
| D9 | Security and privacy posture stated: trust boundaries, personal data, authz model | `lens-security` + `lens-privacy-compliance` pass |
| D10 | Reversibility assessed for every one-way door in the plan | Plan risk section |

Default lenses: requirements, architecture, domain-model, api-contract, data, security,
privacy-compliance, reliability.

## Build Gate

**Purpose**: the code does what the design says, and does not do what it must not.

Entry criteria:

- Design gate is PASS or PASS WITH CONDITIONS.
- `tasks.md` exists and every task maps to a requirement.

Exit criteria:

| # | Criterion | Evidence |
| - | --------- | -------- |
| B1 | Every planned task is complete or explicitly deferred with a reason | `tasks.md` status |
| B2 | Every requirement maps to code that implements it | Coverage table |
| B3 | No placeholder, stub, or fake implementation on a production path | `lens-maintainability` fake-implementation probes |
| B4 | Project checks pass: build, lint, typecheck, unit tests | Command output, quoted |
| B5 | New behavior has tests whose oracles actually assert the behavior | `lens-testing` pass |
| B6 | No confirmed Critical or High security finding | `lens-security` pass |
| B7 | Contracts implemented match contracts declared | `lens-api-contract` pass |
| B8 | Errors are handled, not swallowed; failures are observable | `lens-reliability` + `lens-observability` |
| B9 | No secret, credential, or personal datum added to the repo or the logs | Search evidence |

Default lenses: architecture, maintainability, security, concurrency, data, testing, performance,
api-contract.

## QA Gate

**Purpose**: it works in the running system, for real users, and can be operated.

Entry criteria:

- Build gate is PASS or PASS WITH CONDITIONS.
- The application can be started in a test environment.

Exit criteria:

| # | Criterion | Evidence |
| - | --------- | -------- |
| Q1 | Every P1 acceptance scenario executed and passed | Validation report |
| Q2 | Execution status honestly reported (`INCOMPLETE` when tests could not run) | Validation report |
| Q3 | Every open bug is triaged with severity and owner | `validation/bugs/` |
| Q4 | No open Critical bug; no open High bug without an accepted, recorded waiver | Bug ledger |
| Q5 | Cross-artifact consistency verified: spec, plan, tasks, code agree | `artifact-analysis` report |
| Q6 | Accessibility checks pass for changed UI surfaces | `lens-accessibility` pass |
| Q7 | Operability: deploy, rollback, config, and alerting paths named and viable | `lens-operations` pass |
| Q8 | Regression surface considered: what existing behavior could this break, and was it checked | Exploratory notes |

Default lenses: requirements, testing, security, reliability, performance, observability,
accessibility, operations.

## Gate Record

Write one per gate run, to `FEATURE_DIR/gates/{phase}-{date}.md`. The record is the audit trail; a
gate with no record did not happen.

```markdown
# {Phase} Gate - {feature}

**Date**: {date} | **Verdict**: {PASS | PASS WITH CONDITIONS | BLOCK}

## Criteria

| # | Criterion | Result | Evidence |
| - | --------- | ------ | -------- |

## Findings

| ID | Lens | Severity | Blocking | Status |
| -- | ---- | -------- | -------- | ------ |

## Conditions

1. {id} - {what must become true} - owner: {who} - tracked as: {task id}

## Lenses

Run: {list} | Skipped: {lens - reason}
```

## Re-running a Gate

- Re-run the full gate after any change that touches a blocking finding.
- Findings previously REFUTED stay refuted unless the code they were refuted against changed.
- A gate result is stale once the artifact changes; do not carry a PASS across a rewrite.
