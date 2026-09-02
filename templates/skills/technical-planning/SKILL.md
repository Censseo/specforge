---
name: technical-planning
description: |
  Turn a specification into a technical plan with research, data model, contracts and recorded
  decisions - reusing what exists before creating anything new. Uses Clean and Hexagonal Architecture,
  ADR, C4 and arc42. Activate when: planning an implementation, choosing a design, or writing an ADR.
triggers: ["create a plan", "technical plan", "how should we build this", "architecture decision", "design the implementation", "research the approach"]
semantic_anchors: [Clean Architecture, Hexagonal Architecture, ADR, C4 Model, DRY, arc42]
phase: design
---

# Technical Planning

> The plan's job is to make the implementation boring. Every decision it leaves open becomes an
> improvisation later.

## Inputs

| Input | Why it matters |
| ----- | -------------- |
| `spec.md` | What must be true when this is done |
| `/memory/constitution.md` | Constraints that outrank the plan |
| `/memory/architecture-registry.md` | Established patterns, technology decisions, anti-patterns |
| Source `idea.md` | Technical hints and constraints that must survive to implementation |
| `/docs/{domain}/spec.md` | Existing features, entities, business rules, API patterns |
| The existing codebase | What can be reused |

## Step 1 - Reuse Before Invention

Creating what already exists fragments the codebase and doubles maintenance. For each capability in
the spec:

1. Search for existing services, utilities, base classes and models that overlap.
2. Read them - do not judge from the name.
3. Apply the decision matrix, in order:

| Decision | Condition |
| -------- | --------- |
| REUSE | Fits as-is; wire it up |
| EXTEND | Needs additions that do not change existing behavior |
| REFACTOR | Needs redesign to serve both uses; includes updating existing callers |
| NEW | Nothing suitable exists - and the plan says why |

Record the findings in `research.md` under "Existing Codebase Analysis": reusable components found,
patterns to follow, and conflicts detected.

If NEW exceeds half the components, the search was probably too shallow. Say so and look again.

## Step 2 - Architecture Alignment

For each capability, check against the registry: is there an established pattern, a mandated
technology, a component convention, an anti-pattern risk?

Produce the alignment report in `plan.md`:

- Patterns applied (from the registry, or new)
- Technology alignment (registry vs plan)
- New patterns introduced, with justification and a flag to register them after implementation
- Divergences requiring approval

**A divergence stops the plan.** Ask the user: approve, revise, or discuss alternatives. Record the
answer. Undocumented divergence is how architectures rot.

Where no registry exists, mark decisions "New Pattern - to be registered" and note that
`codebase-learning` should run after implementation.

## Step 3 - Research (Phase 0)

For each unknown in the technical context, each dependency and each integration, produce a decision
record in `research.md`:

```markdown
### Decision: [topic]

- **Decision**: what was chosen
- **Existing code considered**: what was evaluated
- **Reuse approach**: REUSE / EXTEND / REFACTOR / NEW
- **Rationale**: why - especially if NEW
- **Alternatives considered**: what else, and why not
- **Consequences**: what this makes easy, what it makes hard, what it makes irreversible
```

An ADR with one option is not a decision record; it is a rationalisation.

## Step 4 - Design and Contracts (Phase 1)

| Artifact | Content | Marking |
| -------- | ------- | ------- |
| `data-model.md` | Entities, fields, relationships, validation rules, state transitions, invariants | EXISTING / EXTENDED / NEW per entity |
| `contracts/` | Endpoint or event per user action, with error cases and status codes | EXISTING / MODIFIED / NEW per endpoint |
| `quickstart.md` | How to run and exercise the feature | - |
| Agent context | New technology added; manual sections preserved | - |

Design against the dependency rule: domain logic depends on nothing outward. Every boundary crossing
goes through an explicit port.

## Step 5 - Constitution Check

Evaluate the plan against every constitution principle, before and after the design step. An
unjustified violation is an error, not a note - resolve it or change the plan.

## Step 6 - Idea Alignment

Cross-check the plan against the source idea's technical hints. Mark each ALIGNED, DIVERGENT
(justified) or MISSING (add it). A plan that quietly substitutes a different tool for the one the
author specified will be caught in review at ten times the cost.

## Step 7 - Reversibility

For every decision, state whether it is a one-way door: public contracts, data formats, vendor
choices, deletions, external side effects. One-way doors get an explicit paragraph on what it would
take to undo them.

## Output Summary

Branch, plan path, generated artifacts, architecture alignment status, idea alignment status, reuse
summary (reused vs new), registry updates pending, and open risks.

## Handoff

Run `adversarial-review` with `lens-architecture`, `lens-domain-model`, `lens-api-contract`,
`lens-data`, `lens-security` before the design gate. Then `task-decomposition`.
