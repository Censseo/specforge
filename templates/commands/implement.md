---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
skills:
  - implementation-execution
  - adversarial-review
  - lens-maintainability
  - lens-security
  - lens-testing
semantic_anchors:
  - TDD London School    # Outside-in, mock collaborators, test behavior not state
  - Clean Architecture   # Dependency rule, use cases, entities, Robert C. Martin
  - SOLID Principles     # SRP, OCP, LSP, ISP, DIP for maintainable code
  - Kanban               # Visualize work, limit WIP, manage flow, pull system
  - Fail Fast            # Detect issues early, immediate feedback
  - DRY                  # Don't Repeat Yourself, single source of truth
handoffs:
  - label: Diagnose Issues
    agent: specforge.fix
    prompt: Diagnose why implementation is failing and create a correction plan
  - label: Validate
    agent: specforge.validate
    prompt: Run integration tests to verify implementation
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

## Method

Apply the **`implementation-execution`** skill: phase gates, test-first order, per-task result records,
honest completion reporting and the registry update.

## Operational Steps

1. Run `{SCRIPT}` from the repo root; parse `FEATURE_DIR` and `AVAILABLE_DOCS`. All paths absolute.
   For single quotes in arguments use `'I'\''m Groot'`.

2. **Checklists**: if `FEATURE_DIR/checklists/` exists, count `- [ ]` vs `- [X]` per file and show:

   ```text
   | Checklist | Total | Completed | Incomplete | Status |
   ```

   If anything is incomplete, show the table and ask whether to proceed. Do not decide alone.

3. **Minimal context**: read `tasks.md` and `plan.md`; scan (do not read) `task-plans/` and
   `task-results/`. Load `data-model.md`, `contracts/` and `research.md` only when a task needs them.

4. **Project hygiene**: verify or create the ignore files for the detected stack:

   | Condition | File |
   | --------- | ---- |
   | `git rev-parse --git-dir` succeeds | `.gitignore` |
   | `Dockerfile*` or Docker in the plan | `.dockerignore` |
   | `.eslintrc*` / `eslint.config.*` | `.eslintignore` / config `ignores` |
   | `.prettierrc*` | `.prettierignore` |
   | `*.tf` files | `.terraformignore` |
   | Helm charts | `.helmignore` |

   Append missing patterns to existing files; never overwrite them.

5. **Agent registry**: run `ls __AGENT_DIR__/agents/specforge/*.md`. Read each frontmatter (name,
   description, model) and build a `{file pattern} -> {agent}` registry: `backend/**` -> backend-coder,
   `*.tsx` -> frontend-coder, `*.test.*` -> tester, no match -> direct implementation. Log what was
   found. An empty registry means every task runs in direct mode.

6. **Execute** per the skill, phase by phase. In delegate mode, invoke the matching agent with:

   ```yaml
   Task:
     subagent_type: "{agent-name}"
     model: "{agent-model}"
     description: "Implement T{n}: {short description}"
     prompt: |
       Implement task T{n} from {FEATURE_DIR}/tasks.md
       Task: {full task description}
       1. Load {FEATURE_DIR}/task-plans/T{n}-*.md if it exists
       2. Load previous results (T{n-1} and dependency results)
       3. Implement following the plan's steps
       4. Report: status, files changed, deviations, gotchas, TODOs, lessons
   ```

   Then write `task-results/T{n}-result.md` and update `tasks.md`.

7. **After each phase**: aggregate TODOs into blockers / enhancements / debt; stop and ask if there
   are blockers. Then run the incremental red pass - `lens-maintainability` Part 1 first (stubs, fake
   implementations, swallowed errors), then `lens-security` and `lens-testing` on what changed.

8. **Completion**: verify every required task, check the implementation against the spec, run the full
   check suite and quote the output, then update `/memory/architecture-registry.md` with the patterns,
   decisions, conventions and anti-patterns the feature established.

## Report

Task status per phase, check-suite output including failures, findings fixed in place, registry
updates, and what was deliberately left undone. A task whose verification failed is `[~]`, never `[X]`.

If `tasks.md` is missing or incomplete, suggest `/specforge.tasks` first.
