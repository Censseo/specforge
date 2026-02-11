---
description: Create detailed task implementation plans phase-by-phase with user confirmation between phases to avoid lazy execution
semantic_anchors:
  - Work Breakdown Structure  # Hierarchical decomposition, project management
  - Spike                     # Timeboxed research/exploration, XP practice
  - Dependency Injection      # Loose coupling for parallel development
  - Critical Path Method      # Identify blocking sequences
  - Progressive Elaboration   # Refine details as knowledge increases
---

## User Input

```text
$ARGUMENTS
```

Consider the user input before proceeding (if not empty).

## Outline

> **Activated Frameworks**: Work Breakdown Structure for decomposition, Critical Path Method for dependencies, Progressive Elaboration for detail refinement, Spike for research tasks.

### Phase 1: Context Loading and Progression Detection

1. **Setup**: Run `.specforge/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute.

2. **Load required context documents**:

   <required_docs>

   - tasks.md — complete task list and structure
   - plan.md — tech stack and architecture
   - research.md — reuse decisions (REUSE/EXTEND/REFACTOR/NEW per component), existing codebase analysis, technical decisions
   - `/memory/architecture-registry.md` — established patterns, technology decisions, component conventions, anti-patterns

   </required_docs>

   <optional_docs>

   - spec.md — feature requirements
   - data-model.md — entities and relationships
   - constitution.md — project principles
   - contracts/ directory — API specifications

   </optional_docs>

   Extract from research.md: the list of components and their reuse classification (REUSE, EXTEND, REFACTOR, NEW). This determines whether each task wires up existing code, extends it, refactors it, or creates something new.

   Extract from architecture-registry.md (ARCHITECTURE_CONTEXT): established patterns with file references, technology decisions, component conventions (file locations and naming), and anti-patterns to avoid.

3. **Check for specialized agents**:

   - Check if `__AGENT_DIR__/agents/specforge/researcher.md` and `__AGENT_DIR__/agents/specforge/planner.md` exist
   - Store availability for later use (determines subagent_type)

4. **Analyze tasks.md progression**:

   - Parse all phases and their tasks
   - Identify completed (`[X]`/`[x]`) and incomplete (`[ ]`) tasks
   - Determine current phase: first phase with incomplete tasks
   - Extract task count per phase (completed / total)

5. **Scan for existing implementation results**:

   - Check task-plans/ for existing plan files (T###-*.md)
   - Check task-results/ for result files (T###-result.md) from previous implement runs
   - Build available context list; extract gotchas, patterns that worked/failed, deviations from plans

6. **Display progression status**:

   ```text
   Feature Progress: {feature-name}

   Phase 1: Setup - Complete (3/3 tasks)
   Phase 2: Foundational - In Progress (5/47 tasks)  <- CURRENT PHASE
   Phase 3: User Story 1 - Pending (0/4 tasks)
   ...
   ```

7. **Ask user for confirmation**:

   - Show: "Ready to create detailed plans for **Phase {N}: {Phase Name}** ({count} incomplete tasks)"
   - Options: "yes"/"continue" (proceed), "next" (skip to next phase), "all" (process all remaining), "phase {N}" (jump to specific)
   - Stop and wait for user response.

### Phase 2: Research Phase (Only After User Confirmation)

Runs only after user confirms which phase to process. The purpose is to reduce uncertainty between the technical plan and actual implementation by validating reuse decisions against current codebase state.

1. **Launch researcher agent for codebase analysis**:

   Use Task tool with:
   - If `__AGENT_DIR__/agents/specforge/researcher.md` exists: subagent_type="researcher"
   - Otherwise: subagent_type="Explore" with thoroughness="medium"
   - Model: sonnet (reuse validation requires judgment)

   <researcher_prompt>
   You are the researcher agent for SpecKit breakdown.

   Task: Validate reuse decisions and analyze the codebase for {Phase Name} implementation.

   Context:
   - Feature: {feature-name}
   - Phase: {phase-name}
   - Tasks to plan: {list of task IDs and descriptions, with their [REUSE]/[EXTEND]/[REFACTOR]/[NEW] markers}
   - Tech stack: {from plan.md}
   - Previous reuse decisions: {from research.md Existing Codebase Analysis}

   <architecture_context>
   Patterns: {applicable patterns from architecture-registry.md with file references}
   Technology decisions: {applicable tech decisions}
   Conventions: {file location and naming conventions}
   Anti-patterns: {what to avoid}
   </architecture_context>

   ## Validate Reuse Decisions

   For each task, verify its reuse classification is still accurate. The plan made these decisions during /specforge.plan — your job is to confirm or flag changes:

   - **[REUSE]**: Verify component exists at specified location with expected interface. Flag as REUSE_NEEDS_UPDATE if changed.
   - **[EXTEND]**: Verify base component and identify exact extension points. Flag as EXTEND_BLOCKED if approach is no longer valid.
   - **[REFACTOR]**: Verify component is refactorable and identify all affected usages and tests. Flag as REFACTOR_HIGH_RISK if risky.
   - **[NEW]**: Double-check no existing code serves this purpose. Flag as NEW_SHOULD_BE_REUSE if reusable code found.

   ## Standard Research

   1. Find existing code patterns relevant to these tasks
   2. Locate reference implementations and similar features in the codebase
   3. Note gotchas or special considerations from constitution.md

   Search strategies: Glob for file patterns, Grep for similar implementations, read key architectural files, check .repomix/ for reference patterns.

   ## Deliverable

   Return a structured report with these sections:

   **Reuse Validation Report**

   | Task | Original Decision      | Validation                      | Status       |
   |------|------------------------|---------------------------------|--------------|
   | T001 | [REUSE] AuthService    | Component exists, API unchanged | VALID        |
   | T002 | [EXTEND] ReportService | New method signature needed     | NEEDS_UPDATE |

   **Implementation Gaps**
   - {what the plan assumed vs. what actually exists}

   **Existing Patterns Found**
   - Pattern: {name} at file:line

   **Gotchas and Dependencies**
   - {gotchas from constitution or previous implementations}
   - {imports needed per task}
   </researcher_prompt>

2. **Validate and report reuse decision changes**:

   - Parse researcher agent response
   - If any flags (NEEDS_UPDATE, BLOCKED, HIGH_RISK, SHOULD_REUSE): display to user, ask to update tasks.md markers
   - Store validated research findings for planning phase

### Phase 3: Group-Based Task Planning

Plans tasks by logical groups for efficiency (fewer agent calls, less token usage).

1. **Prepare tasks for planning**:

   a. **Collect incomplete tasks** without existing plans. Log skipped tasks.

   b. **Group tasks by topic** (priority order):
      1. By User Story: [US1], [US2], etc.
      2. By domain: "model/entity/schema" -> Data Models, "api/endpoint/route" -> API, "component/page/view/ui" -> Frontend, "service/repository" -> Backend, "test/spec" -> Testing, "config/setup" -> Configuration
      3. By target directory: tasks targeting same folder
      4. Ungrouped: remaining tasks

   c. **Display grouping**:

      ```text
      Task Groups for Phase {N}:

      Group 1: Data Models (5 tasks) — T004, T005, T006, T007, T008
      Group 2: API Endpoints (8 tasks) — T009-T016
      Group 3: Frontend Components (4 tasks) — T017-T020
      ```

   d. **Load shared context**: previous task results (lessons learned, gotchas) to pass to all groups.

2. **For each task group** (sequential groups, all tasks in group planned together):

   a. **Launch planner agent**:

      Use Task tool with:
      - If `__AGENT_DIR__/agents/specforge/planner.md` exists: subagent_type="planner"
      - Otherwise: subagent_type="general-purpose"
      - Model: sonnet by default. Escalate to opus when: group contains security/auth/payment tasks, 10+ tasks with complex dependencies, cross-domain integration, or user explicitly requested thorough analysis.

      <planner_prompt>
      You are the planner agent for SpecKit breakdown.

      Task: Create implementation plans for ALL tasks in this group.
      Group: {group_name} ({count} tasks)
      Phase: {phase_name}

      Tasks to plan:
      {for each task: T{number}: {description} [P={yes/no}] [Story={US# or N/A}]}

      <context>
      Research findings: {summary from researcher agent}
      Previous task results: {lessons learned from task-results/*.md}
      Tech stack: {from plan.md}
      Data model: {from data-model.md if relevant}
      Contracts: {from contracts/ if relevant}
      </context>

      <architecture_context>
      Established patterns: {patterns with file references}
      Technology decisions: {tools/libs to use}
      Component conventions: {file locations and naming}
      Anti-patterns: {what to avoid}
      </architecture_context>

      Plans that violate established patterns without justification will cause architectural drift — flag any necessary divergence.

      Generate a plan for each task. Separate plans with exactly:
      ---TASK_SEPARATOR---

      For each task, use this template structure (use these exact heading levels in output):

      ``# Task Plan: T{number}``

      ``## Task Description``
      {description}
      Phase: {phase} | User Story: {US# or N/A} | Parallel: {Yes/No} | Reuse Type: {REUSE/EXTEND/REFACTOR/NEW}

      ``## Architecture Alignment``
      - Patterns applied: {which registry patterns, how applied}
      - Tech decisions followed: {which, how}
      - Conventions: file at {correct path}, named per convention
      - Anti-patterns avoided: {list or N/A}
      - Status: Aligned / Divergent (with justification)

      ``## Reuse Decision``
      Original: {from tasks.md} | Validation: {VALID/NEEDS_UPDATE/SHOULD_REUSE}
      For REUSE: existing component path, wiring steps, no new files.
      For EXTEND: base component path, extension point, new capability.
      For REFACTOR: target path, goal, affected usages.
      For NEW: justification, similar pattern to follow.

      ``## Codebase Impact``
      - Files to create (NEW only): `{path}` — {purpose}
      - Files to modify: `{path}:{line}` — {change}
      - Dependencies: imports, services, data models

      ``## Implementation Steps``
      1. {step with file:line references}
      2. {step}
      Gotchas: {list}

      ``## Related Tasks``
      Depends on: T{numbers} | Blocks: T{numbers} | Parallel with: T{numbers}

      ``## Estimated Complexity``
      {Simple/Moderate/Complex} | {5min/15min/30min/1h/2h} | Risk: {Low/Medium/High}

      ---TASK_SEPARATOR---
      </planner_prompt>

   b. **Parse and write individual plan files**:
      - Split response by `---TASK_SEPARATOR---`
      - For each plan: extract task ID from `# Task Plan: T{number}`, sanitize description for filename (lowercase, hyphens, max 50 chars)
      - Create task-plans/ directory if needed
      - Write to `task-plans/T{number}-{sanitized-description}.md`

   c. **Update tasks.md** with plan references: append `[Plan](task-plans/T{number}-{filename}.md)` to each planned task.

   d. Log group completion: "{group_name}: {count} plans created"

3. **Phase completion**:

   - Show summary with count of plans created and list of plan files
   - Check for more phases with incomplete tasks
   - If yes: "Phase {N} complete. Continue with Phase {N+1}: {Name}? (yes/no/summary)"
   - If no: "All phases complete! Generating final summary..."
   - Stop and wait for user response. If "yes", loop back to Phase 2 step 1 for next phase. Otherwise proceed to Phase 4.

### Phase 4: Final Summary

1. **Generate comprehensive summary**:

   ```text
   SpecKit Breakdown Summary — {feature-name}

   ## Phases Processed
   Phase {N}: {name}
   - Tasks planned: {x}/{total}
   - Complexity: Simple ({n}), Moderate ({n}), Complex ({n})
   - Files to create/modify: {n}/{n}

   ## Overall Statistics
   - Total plans created: {n}
   - Estimated time: {range}
   - Critical path: {key task IDs}
   - Phases remaining: {n}

   ## Next Steps
   1. Review plans in task-plans/
   2. Run /specforge.implement to execute
   3. Plans guide implementation with exact steps and references

   ## Key Patterns and Gotchas
   - {patterns discovered}
   - {gotchas to watch}
   ```

## Operating Principles

**Architecture consistency drives quality.** Plans follow established patterns from architecture-registry.md because architectural drift across features creates compounding maintenance cost. If a task cannot follow a pattern, flag it with justification rather than silently diverging.

**Validate before planning.** Components marked for reuse may have changed since the plan was written. The researcher phase catches mismatches between plan assumptions and codebase reality, preventing wasted implementation effort.

**Reuse classification determines approach.** REUSE tasks wire up existing code (no new files). EXTEND tasks add to existing components at identified extension points. REFACTOR tasks modify existing code with awareness of all affected usages. Only NEW tasks create files, and only after confirming no reusable alternative exists.

**Phase-by-phase, group-by-group.** Planning all phases at once produces stale plans. Working in groups (by user story, domain, or directory) gives coherent plans with shared context while keeping agent calls efficient.

**Discover, don't assume.** The researcher agent finds actual patterns in the codebase rather than assuming any particular framework. Plans are based on what exists, not what might exist.

## Error Handling

- **No tasks.md**: Error and suggest running `/specforge.tasks` first
- **No incomplete tasks**: Inform user all tasks are already planned
- **Agent failure**: Log error, skip group, continue with next group
- **Parse failure**: If `---TASK_SEPARATOR---` parsing fails, attempt extraction by `# Task Plan:` headers
- **File write error**: Report error, suggest manual creation
- **User cancellation**: Save progress, generate summary of work done so far

## Context

$ARGUMENTS
