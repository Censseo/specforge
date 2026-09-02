---
description: Execute the implementation planning workflow using the plan template to generate design artifacts.
skills:
  - technical-planning
  - architecture-decision-records
  - lens-architecture
  - lens-domain-model
  - lens-api-contract
semantic_anchors:
  - Clean Architecture    # Dependency rule, use cases, entities, Robert C. Martin
  - Hexagonal Architecture  # Ports and Adapters, domain isolation, Alistair Cockburn
  - ADR                   # Architecture Decision Records - Context, Decision, Consequences
  - C4 Model              # Context → Containers → Components → Code, Simon Brown
  - DRY                   # Don't Repeat Yourself - identify reuse opportunities first
  - arc42                 # Architecture documentation template, 12 sections
handoffs:
  - label: Create Tasks
    agent: specforge.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: specforge.checklist
    prompt: Create a checklist for the following domain...
scripts:
  sh: scripts/bash/setup-plan.sh --json
  ps: scripts/powershell/setup-plan.ps1 -Json
agent_scripts:
  sh: scripts/bash/update-agent-context.sh __AGENT__
  ps: scripts/powershell/update-agent-context.ps1 -AgentType __AGENT__
---

## User Input

```text
$ARGUMENTS
```

The input carries the tech stack and constraints the user wants ("I am building with...").

## Method

Apply the **`technical-planning`** skill: reuse before invention, the REUSE/EXTEND/REFACTOR/NEW
decision matrix, architecture alignment against the registry, decision records with alternatives and
consequences, and the reversibility assessment.

## Operational Steps

1. **Setup**: run `{SCRIPT}` from the repo root; parse `FEATURE_SPEC`, `IMPL_PLAN`, `SPECS_DIR`,
   `BRANCH`. For single quotes in arguments use `'I'\''m Groot'`.

2. **Load context**, in this order:

   | Source | What to take |
   | ------ | ------------ |
   | `FEATURE_SPEC` | What must be true when this is done |
   | `/memory/constitution.md` | Constraints that outrank the plan |
   | `/memory/architecture-registry.md` | Patterns, technology decisions, component conventions, anti-patterns |
   | Source `idea.md` (via `**Source**:` / `**Parent Idea**:` in the spec, or `ideas/`) | Technical hints, constraints, discovery notes |
   | `/docs/{domain}/spec.md` and its cross-domain references | Existing features, entities, business rules, API patterns |
   | The codebase | What can be reused |

   Where no registry or `/docs` exists, say so, recommend `/specforge.learn` after implementation, and
   proceed with explicit decision documentation.

3. **Explore and decide reuse** per the skill. Record findings in `research.md` under
   "Existing Codebase Analysis".

4. **Architecture alignment**: produce the alignment report in `plan.md`. On any divergence from the
   registry, stop and ask the user - approve, revise, or discuss alternatives - and record the answer.

5. **Phase 0 - research**: resolve every `NEEDS CLARIFICATION`, dependency and integration into a
   decision record in `research.md`.

6. **Phase 1 - design**: generate `data-model.md`, `contracts/` and `quickstart.md`, marking each
   entity EXISTING / EXTENDED / NEW and each endpoint EXISTING / MODIFIED / NEW. Then run
   `{AGENT_SCRIPT}` to update the agent context file, preserving manual sections.

7. **Constitution check**: evaluate before and after the design step. An unjustified violation is an
   error - resolve it or change the plan.

8. **Idea alignment**: cross-check the plan against the idea's technical hints; mark each ALIGNED,
   DIVERGENT (justified) or MISSING (add it). Stop and ask on a critical divergence.

9. **Red pass**: run `lens-architecture`, `lens-domain-model` and `lens-api-contract` over the
   artifacts you just wrote. Fix what they find in place.

## Report

Branch, plan path, generated artifacts, architecture alignment status (patterns followed, divergences
approved), idea alignment status, reuse summary (reused vs new), registry updates pending after
implementation, and open one-way doors.

Stop here. `/specforge.tasks` is the next step - or `/specforge.build` to run the whole build phase.
