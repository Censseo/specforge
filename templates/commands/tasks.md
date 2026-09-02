---
description: Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.
skills:
  - task-decomposition
  - lens-requirements
semantic_anchors:
  - User Story Mapping    # Backbone → Skeleton → Ribs, Jeff Patton
  - Work Breakdown Structure  # Hierarchical decomposition, project management
  - Dependency Graph      # DAG for task ordering, critical path
  - Kanban                # Visualize flow, limit WIP, pull system
  - INVEST Criteria       # Tasks should be Independent, Valuable, Estimable
handoffs:
  - label: Analyze For Consistency
    agent: specforge.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: specforge.implement
    prompt: Start the implementation in phases
    send: true
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## User Input

```text
$ARGUMENTS
```

## Method

Apply the **`task-decomposition`** skill: organisation by user story, the strict checklist format, the
reuse markers, the phase structure, and both traceability tables.

## Operational Steps

1. **Setup**: run `{SCRIPT}` from the repo root; parse `FEATURE_DIR` and `AVAILABLE_DOCS`. All paths
   absolute. For single quotes in arguments use `'I'\''m Groot'`.

2. **Load design documents** from `FEATURE_DIR`:
   - Required: `plan.md` (stack, structure), `spec.md` (stories with priorities)
   - Optional: `data-model.md`, `contracts/`, `research.md` (reuse decisions), `quickstart.md`

   Generate from what exists; do not block on missing optional documents.

3. **Load the source idea** via the plan's "Idea Technical Alignment" section, the spec's `**Source**:`
   links, or `ideas/`. Extract its technical hints and constraints.

4. **Alignment check before generating**: verify the plan carries the idea's technical specifics
   (commands, tools, versions, ordering). Carry forward any divergence the plan already recorded. On a
   contradiction between idea and plan, stop, ask, and record the decision in the `tasks.md` header.

5. **Generate** using `templates/tasks-template.md` as the structure:
   - Phase 1 Setup, Phase 2 Foundational, Phase 3+ one per user story in priority order, final Polish
   - Map entities and endpoints to their stories; map reuse decisions from `research.md` to markers
   - Each story phase states its goal and its independent test criteria
   - Test tasks only where the spec or the user asked for them

6. **Append the traceability sections**: Idea Technical Traceability and Reuse Traceability. Any idea
   requirement without a task is added or explicitly waived with the user's agreement.

7. **Validate**: every task matches the checklist format; every story is independently testable; every
   requirement maps to at least one task; every reuse decision is reflected.

## Report

Total tasks and tasks per story, parallel opportunities, independent test criteria per story, suggested
MVP scope, format validation, idea alignment status, and the reuse summary. Flag it when NEW exceeds
half the components - the reuse search was probably too shallow.

Each task must be executable by someone holding the task text and the plan, and nothing else.
