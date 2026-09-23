---
name: implementation-execution
description: |
  Execute a task list into working code with test-first discipline, phase gates, result records and
  registry updates. Uses TDD London School, Clean Architecture, SOLID, Kanban and Fail Fast.
  Activate when: implementing tasks.md, executing a plan, or building a feature increment.
triggers: ["implement", "execute the tasks", "build the feature", "start coding", "run the task list", "implement tasks.md"]
semantic_anchors: [TDD London School, Clean Architecture, SOLID Principles, Kanban, Fail Fast, DRY]
phase: build
---

# Implementation Execution

> Finish each phase before starting the next, prove each task worked, and write down what actually
> happened - including where it differed from the plan.

## Before Starting

1. **Checklists**: scan `checklists/` and count items. Show the status table. If anything is
   incomplete, ask before proceeding - do not decide unilaterally that the gaps are fine.
2. **Minimal context**: read `tasks.md` and `plan.md`. Scan (do not read) `task-plans/` and
   `task-results/`. Load `data-model.md`, `contracts/` and `research.md` only when a task needs them.
3. **Project hygiene**: verify or create the ignore files for the detected stack (`.gitignore`,
   `.dockerignore`, `.eslintignore`, `.prettierignore`, `.terraformignore`, `.helmignore`). Append
   missing patterns to existing files; never overwrite them.
4. **Agent registry**: list `__AGENT_DIR__/agents/specforge/*.md`. Map file patterns to specialised
   agents (`backend/**` -> backend-coder, `*.test.*` -> tester, fallback -> direct implementation).

## Execution Rules

- Complete each phase before the next. Kanban: limit work in progress; a half-finished phase is worse
  than a not-started one.
- Sequential tasks in order; `[P]` tasks together; tasks touching the same file always sequentially.
- Tests before implementation when test tasks exist (outside-in: start from the behavior, mock
  collaborators, assert behavior not internal state).
- Setup -> Foundational -> Stories -> Polish. Within a story: models -> services -> endpoints ->
  integration.
- Apply SOLID and the dependency rule as you write, not as a cleanup pass.
- Fail fast: surface the problem at the point of detection rather than compensating downstream.

## Per Task

1. Load the task plan (`task-plans/T{n}-*.md`) if it exists; follow its steps, patterns and gotchas.
2. Load the results of the tasks it depends on - deviations and gotchas from earlier tasks are the
   highest-value context available.
3. Implement, directly or by delegating to the matching specialised agent.
4. Verify: run the relevant test, lint and typecheck. Quote the output.
5. Write `task-results/T{n}-result.md`:

```markdown
Status: Complete | Partial | Failed
Files Changed:
  - {file}: {what changed}
Deviations from Plan: {what differed and why, or "None"}
Gotchas Discovered: {issues and resolutions, or "None"}
TODOs Left:
  - Blockers: {critical}
  - Enhancements: {nice-to-have}
  - Technical debt: {shortcuts taken}
Lessons Learned: {what worked, what did not}
```

Then update `tasks.md`: `[X]` complete, `[~]` partial.

## Errors

| Situation | Action |
| --------- | ------ |
| Task plan missing | Warn, implement from the task description |
| Task plan malformed | Best-effort extraction, log what was unclear |
| Prerequisite missing | Report the missing prerequisite, skip the task with a clear message |
| Non-parallel task fails | Halt; report with debugging context |
| Parallel `[P]` task fails | Continue the others, report the failure |

Never mark a task complete when its verification failed. A green tick on a red test is a lie the next
phase will act on.

## After Each Phase

Aggregate the TODOs from `task-results/` into blockers, enhancements and technical debt. If there are
blockers, stop and ask: resolve, continue, or stop.

Run the build-phase adversarial pass on the increment now - `lens-maintainability` (fake
implementations first), `lens-security`, `lens-testing` - not at the end of everything.

## Completion

- Verify every required task is complete or explicitly deferred.
- Check the implementation against the specification, requirement by requirement.
- Run the full check suite: build, lint, typecheck, tests. Report the output, including failures.
- Summarise status honestly. "Done except X" is a valid and useful result; "done" when X is broken is not.

## Registry Update

Review `task-results/` for patterns worth keeping and add them to
`/memory/architecture-registry.md`, tagged `<!-- Added from {feature} ({date}) -->`:

- Established patterns: pattern, files, when to use, example
- Technology decisions: category, decision, rationale
- Component conventions: type, location, naming
- Anti-patterns discovered: what, why avoided, better approach

"No new patterns - the feature followed existing conventions" is a good outcome; record it too.

## Handoff

Next: `integration-validation`. Run the build gate from `quality-gates` before it.
