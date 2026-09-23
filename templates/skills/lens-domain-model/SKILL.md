---
name: lens-domain-model
description: |
  Adversarial domain model lens - attacks entities, invariants, aggregates and state machines for
  unenforceable rules, illegal states and language drift. Activate when: reviewing a data model,
  entities, business rules, or a state machine.
triggers: ["domain model review", "entity review", "invariant", "aggregate", "state machine", "business rules review", "ubiquitous language"]
lens:
  id: domain-model
  prefix: DOM
  domain: Domain modelling
  applies_to: [spec, plan, data-model, code]
  phases: [design, build]
  blocking_severity: high
---

# Domain Model Lens

**Failure this lens prevents**: a model that permits states the business forbids, discovered later as
corrupt data.

## Load First

`data-model.md`, the entity definitions in code, `spec.md` business rules, and the project glossary
or `specs/` context file if one exists.

## Probes

| # | Probe | Failure signature | Evidence to capture |
| - | ----- | ----------------- | ------------------- |
| M1 | For each entity, what invariant must always hold? | No invariant stated; anything is a valid instance | Entity + missing rule |
| M2 | Can an illegal state be constructed? | Optional fields that are mandatory in some states; booleans encoding a state machine | Constructor path to the illegal state |
| M3 | Who enforces each invariant, and where? | Enforced in the UI only, or in one of three write paths | Enforcement site + unguarded path |
| M4 | Is the aggregate boundary the transaction boundary? | One operation must atomically update two aggregates | Operation + both aggregates |
| M5 | Is identity defined? | No natural or surrogate key rule; equality undefined | Entity |
| M6 | Is the lifecycle complete? | States with no exit; transitions with no trigger; no terminal state | State diagram gap |
| M7 | Are illegal transitions rejected? | Any state reachable from any state | Transition table |
| M8 | Do names in the model match the names the business uses? | Code says `Item`, business says `LineItem`, spec says `Product` | Term map |
| M9 | Are value objects used for constrained values? | Money, email, quantity as bare primitives | Field + constraint that is now unenforced |
| M10 | What happens to children when a parent is deleted? | Cascade unspecified; orphans possible | Relationship |
| M11 | Is history required, and is it modelled? | Current-state-only model where the business asks "what changed and when" | Requirement + model gap |
| M12 | Are units, currencies, precision and time zones explicit? | Bare numbers for money or durations; naive datetimes | Field |
| M13 | Does the model support the queries the spec requires? | Required listing or report is impossible or requires a scan | Requirement + model |
| M14 | Are enumerations closed and complete? | Free-text status; enum missing a state used in the spec | Field + missing value |

## Attack Moves

- **Illegal state construction**: try to instantiate a nonsensical entity (negative quantity, order
  with no lines, shipped-before-paid). If the type or schema allows it, only discipline prevents it.
- **Invariant hunt in prose**: every "must", "always", "never", "at most", "only if" in the spec is an
  invariant. List them, then find where each is enforced. Unenforced ones are findings.
- **Concurrent edit**: two actors modify the same aggregate simultaneously. Which invariant breaks?
- **Language audit**: collect every name for the same concept across spec, model, code, and UI. More
  than one name is drift.
- **Deletion walk**: delete each root entity and follow the graph. Name every orphan and dangling
  reference.

## Severity Calibration

| Severity | Domain-specific |
| -------- | --------------- |
| Critical | An invariant protecting money, safety or data integrity is unenforceable in the model |
| High | Illegal states are representable on a primary entity; aggregate boundary splits a required atomic operation; cascade behavior undefined for a parent-child pair |
| Medium | Primitive obsession on a constrained value; missing history where reporting needs it; incomplete lifecycle on a secondary entity |
| Low | Naming inconsistency with no ambiguity of meaning |

## Common False Positives

- Anemic models are not automatically a defect. Judge by whether invariants are enforced somewhere
  reachable by every write path, not by where the methods live.
- A missing value object in a language without cheap types (or in a thin adapter layer) may be a
  deliberate trade-off. Check for enforcement at the boundary before reporting.
- Different names across bounded contexts are correct by design. Drift only counts inside one context.

## Output

Findings with prefix `DOM`. Include an invariant table: rule, where stated, where enforced, write
paths that bypass it.
