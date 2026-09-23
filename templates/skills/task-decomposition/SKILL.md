---
name: task-decomposition
description: |
  Turn a plan into a dependency-ordered task list organised by user story, where each task is
  independently executable and traceable. Uses story mapping, WBS, dependency graphs and Kanban.
  Activate when: generating tasks.md, breaking work into phases, or sequencing implementation.
triggers: ["generate tasks", "break down the work", "task list", "sequence the work", "tasks.md", "implementation phases", "breakdown"]
semantic_anchors: [User Story Mapping, Work Breakdown Structure, Dependency Graph, Kanban, INVEST Criteria]
phase: build
---

# Task Decomposition

> Every task must be executable by someone with the task text, the plan, and nothing else.

## Inputs

Required: `plan.md` (stack, structure), `spec.md` (stories with priorities).
Optional: `data-model.md`, `contracts/`, `research.md` (reuse decisions), `quickstart.md`.

Generate from what exists; do not block on missing optional documents.

## Organisation

Tasks are grouped **by user story**, so each story can be implemented and tested independently.

| Phase | Contents |
| ----- | -------- |
| Phase 1 | Setup - project initialisation, dependencies, configuration |
| Phase 2 | Foundational - blocking prerequisites shared by all stories |
| Phase 3+ | One phase per user story, in priority order (P1, P2, P3...) |
| Final | Polish and cross-cutting concerns |

Within a story: tests (if requested) -> models -> services -> endpoints -> integration.

Each story phase states its goal and its independent test criteria. If a story cannot be tested
alone, the decomposition is wrong.

## Task Format

Deviating from this format breaks downstream automation.

```text
- [ ] T012 [P] [US1] [NEW] Create User model in src/models/user.py
```

| Component | Rule |
| --------- | ---- |
| Checkbox | `- [ ]` always |
| Task ID | Sequential `T001`, in execution order |
| `[P]` | Only if parallelisable: different files, no incomplete dependencies |
| `[US#]` | Required for user-story phases; omitted for Setup, Foundational, Polish |
| Reuse marker | `[REUSE]` / `[EXTEND]` / `[REFACTOR]` / `[NEW]` from `research.md` |
| Description | One action, with the exact file path |

Wrong: `- [ ] Create User model` (no id, no story), `T001 [US1] Create model` (no checkbox).

## Reuse Markers

| Marker | Task content |
| ------ | ------------ |
| `[REUSE]` | Reference the existing component path; describe the wiring; create no new file |
| `[EXTEND]` | Reference the component; describe the added capability and the extension point |
| `[REFACTOR]` | Reference the component; describe the goal; list affected code; include a task to update existing callers |
| `[NEW]` | Reference the `research.md` justification for why nothing existing fits |

## Tests

Test tasks are generated only when the spec or the user asks for them (TDD, contract testing).
When they exist, they precede the implementation tasks they cover.

## Traceability Sections

Both go at the end of `tasks.md`. They are the proof that nothing was dropped.

```markdown
## Idea Technical Traceability

| Idea Requirement | Task(s) | Status |
| ---------------- | ------- | ------ |
| Use `pnpm` for install | T001 | Mapped |
| Migrate before seeding | T003 -> T004 | Order preserved |

## Reuse Traceability

| Type | Count | Tasks |
| ---- | ----- | ----- |
| REUSE | 4 | T005, ... |
| NEW | 2 | T020, T021 |
```

Any idea requirement without a task is either added or explicitly waived with the user's agreement.
If NEW exceeds half of the components, flag it: the reuse search was probably too shallow.

## Alignment Check Before Generating

1. Extract the idea's technical specifics: commands, tools and versions, ordering, configuration.
2. Verify `plan.md` carries them. If the plan diverges, carry the divergence forward - do not silently
   revert to the idea or silently follow the plan.
3. On a contradiction between the idea and the plan, stop and ask, then record the decision in the
   `tasks.md` header.

## Report

Total tasks, tasks per story, parallel opportunities, independent test criteria per story, suggested
MVP scope (usually story 1 alone), format validation, idea alignment status, reuse summary.

## Handoff

Next: `implementation-execution`. Run `artifact-analysis` first when the spec, plan and tasks were
written across several sessions.
