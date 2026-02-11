---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
semantic_anchors:
  - TDD London School    # Outside-in, mock collaborators, test behavior not state
  - Clean Architecture   # Dependency rule, use cases, entities, Robert C. Martin
  - SOLID Principles     # SRP, OCP, LSP, ISP, DIP for maintainable code
  - Kanban               # Visualize work, limit WIP, manage flow, pull system
  - Fail Fast            # Detect issues early, immediate feedback
  - DRY                  # Don't Repeat Yourself, single source of truth
handoffs:
  - label: Diagnose Issues
    agent: speckit.fix
    prompt: Diagnose why implementation is failing and create a correction plan
  - label: Validate
    agent: speckit.validate
    prompt: Run integration tests to verify implementation
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

Consider the user input before proceeding (if not empty).

## Outline

1. Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Check checklists status** (if FEATURE_DIR/checklists/ exists):
   - Scan all checklist files, count items matching `- [ ]`, `- [X]`, `- [x]`
   - Display a status table:

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | PASS   |
     | test.md   | 8     | 5         | 3          | FAIL   |
     ```

   - If any checklist is incomplete: display the table, then ask "Some checklists are incomplete. Proceed with implementation anyway? (yes/no)" and wait for response.
   - If all complete: display the table and proceed.

3. **Minimal context loading** (agents will load their own detailed context):
   - Read tasks.md for the complete task list and execution plan
   - Read plan.md for tech stack, architecture, and file structure
   - Scan (don't read) task-plans/ and task-results/ directories
   - Do not load data-model.md, contracts/, research.md, or quickstart.md upfront -- agents load these as needed

4. **Project setup verification**:

   Create/verify ignore files for the detected technology stack from plan.md.

   <detection-rules>
   - `git rev-parse --git-dir 2>/dev/null` succeeds -> create/verify .gitignore
   - Dockerfile* exists or Docker in plan.md -> create/verify .dockerignore
   - .eslintrc* exists -> create/verify .eslintignore
   - eslint.config.* exists -> ensure config's `ignores` entries cover required patterns
   - .prettierrc* exists -> create/verify .prettierignore
   - package.json exists -> create/verify .npmignore (if publishing)
   - *.tf files exist -> create/verify .terraformignore
   - Helm charts present -> create/verify .helmignore
   </detection-rules>

   If an ignore file already exists, verify it contains essential patterns and append missing ones only. If missing, create with the full standard pattern set for that technology.

5. Parse tasks.md and extract task phases (Setup, Tests, Core, Integration, Polish), dependencies (sequential vs parallel [P]), task details (ID, description, file paths), and execution order.

6. **Load available specialized agents**:
   - Run `ls __AGENT_DIR__/agents/speckit/*.md 2>/dev/null`

   <if-agents-found>
   For each agent file: read frontmatter (name, description, model), derive file-pattern mappings, build an agent registry `{pattern} -> {name} (model: {model})`. Example mappings:
   - `backend/**`, `api/**` -> backend-coder
   - `frontend/**`, `*.tsx` -> frontend-coder
   - `*.test.*`, `tests/**` -> tester
   - No match -> implementer (fallback)

   Log: "Found N specialized agents: {names with models}"
   Store this registry -- it determines delegate vs direct mode in Step 7.
   </if-agents-found>

   <if-no-agents>
   Log: "No specialized agents detected, using direct implementation for all tasks."
   Set agent registry to empty. All tasks use direct mode.
   </if-no-agents>

   When task plans exist (task-plans/T{number}-*.md): follow implementation steps exactly, use reference patterns from "Existing Patterns to Follow", check gotchas before starting, verify dependencies, and use exact file paths from "Codebase Impact Analysis".

7. **Execute implementation** following the task plan:

   Apply Kanban (limit WIP, phase gates), TDD London School (outside-in, test-first).

   - Complete each phase before moving to the next
   - Respect dependencies: sequential tasks in order, parallel [P] tasks together
   - Test tasks before implementation tasks (TDD outside-in)
   - Same-file tasks run sequentially to avoid conflicts

   <task-execution>
   For each task:

   **a. Determine execution mode** from the agent registry (Step 6):
   - Match task file paths against registry patterns
   - Match found -> delegate mode (Task tool)
   - No match or empty registry -> direct mode (implement directly)

   **b. Delegate mode** -- use the Task tool to invoke the specialized agent:

   ```yaml
   Task:
     subagent_type: "{agent-name}"
     model: "{agent-model}"
     description: "Implement T{number}: {short-description}"
     prompt: |
       Implement task T{number} from {FEATURE_DIR}/tasks.md
       Task: {full-task-description}
       Instructions:
       1. Load task plan from {FEATURE_DIR}/task-plans/T{number}-*.md if exists
       2. Load previous results (T{number-1}-result.md and dependency results)
       3. Extract: what was implemented, deviations, gotchas, TODOs, lessons
       4. Implement following the plan's steps (or standard patterns if no plan)
       5. Report: status, files changed, deviations, gotchas, TODOs, lessons
   ```

   After the agent returns, create task-results/T{number}-result.md (format below), update tasks.md marking [X] or [~], and log progress.

   **c. Direct mode** -- same workflow without the Task tool:
   Load task plan and previous results, implement directly with Edit/Write, create the result file, update tasks.md, and log progress.
   </task-execution>

   <result-file-format>
   task-results/T{number}-result.md:

   ```markdown
   Status: Complete | Partial | Failed
   Files Changed:
     - {file}: {description of changes}
   Deviations from Plan: {what changed vs plan and why, or "None"}
   Gotchas Discovered: {issues and resolutions, or "None"}
   TODOs Left:
     - Blockers: {critical issues preventing progress}
     - Enhancements: {nice-to-have improvements}
     - Technical debt: {shortcuts taken}
   Lessons Learned: {patterns that worked/didn't work}
   ```

   </result-file-format>

   <error-handling>
   - Plan file missing: log warning, implement using task description only
   - Plan malformed: best-effort extraction, log issues
   - Dependent files missing: report missing prerequisite, skip task with clear message
   </error-handling>

   **After each phase**: aggregate TODOs from task-results, categorize (blockers / enhancements / tech debt). If blockers exist, stop and ask the user whether to resolve, continue, or stop. Otherwise proceed.

8. **Implementation execution rules** -- apply TDD London School, Clean Architecture, SOLID, Kanban:
   - Setup first: project structure, dependencies, configuration
   - Tests before code: write tests for contracts, entities, scenarios before implementation
   - Core development: models, services, endpoints following SOLID
   - Integration: database, middleware, logging respecting dependency rule
   - Polish: unit tests (DRY), performance optimization

9. **Progress tracking**:
   - Report progress after each task; mark [X] complete or [~] partial
   - Halt on non-parallel task failure; for parallel [P] tasks, continue with successes and report failures
   - Provide clear error messages with debugging context

10. **Completion validation**:
    - Verify all required tasks are completed
    - Check implemented features match the original specification
    - Validate tests pass and coverage meets requirements
    - Report final status summary

11. **Update Architecture Registry** (for cross-feature consistency):

    Apply ADR for decisions, arc42 for structure, DRY for pattern reuse.

    After successful implementation:

    a. Review task-results/*.md for reusable patterns, anti-patterns, and technology decisions made during implementation.

    b. Extract and register to `/memory/architecture-registry.md`:
       - Established patterns: `| Pattern | Files | When to Use | Example |`
       - Technology decisions: `| Category | Decision | Rationale |`
       - Component conventions: `| Type | Location | Naming |`
       - Anti-patterns discovered: `| Anti-Pattern | Why Avoided | Better Approach |`

       Format: `<!-- Added from {feature-name} ({date}) -->`

    c. If no new patterns: log "No new patterns established - feature followed existing conventions" (this is a good outcome).

    d. Include registry update in feature commit: "chore: update architecture registry with {feature-name} patterns"

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/specforge.tasks` first to regenerate the task list.
