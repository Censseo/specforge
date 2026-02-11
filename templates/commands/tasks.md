---
description: Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.
semantic_anchors:
  - User Story Mapping    # Backbone → Skeleton → Ribs, Jeff Patton
  - Work Breakdown Structure  # Hierarchical decomposition, project management
  - Dependency Graph      # DAG for task ordering, critical path
  - Kanban                # Visualize flow, limit WIP, pull system
  - INVEST Criteria       # Tasks should be Independent, Valuable, Estimable
handoffs:
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.implement
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

Consider the user input before proceeding (if not empty).

## Outline

> **Activated Frameworks**: User Story Mapping for organization, Work Breakdown Structure for decomposition, Dependency Graph for ordering, Kanban for flow visualization.

1. **Setup**: Run `{SCRIPT}` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**: plan.md (tech stack, libraries, structure), spec.md (user stories with priorities)
   - **Optional**: data-model.md (entities), contracts/ (API endpoints), research.md (decisions), quickstart.md (test scenarios)
   - Not all projects have all documents. Generate tasks based on what's available.

3. **Load source idea for alignment**:
   - Check plan.md for "Idea Technical Alignment" section, then spec.md for `**Source**:` or `**Parent Idea**:` links, then `ideas/` directory
   - Load the idea.md and extract **Technical Hints** and **Constraints** sections
   - Store as IDEA_TECHNICAL_REQUIREMENTS for validation in step 4

4. **Validate alignment with source idea** (before generating tasks):

   <alignment_checks>
   a. **Extract technical specifics from idea**: commands/CLI instructions (with order), specific tools/libraries/versions, step-by-step procedures, configuration patterns, integration sequences

   b. **Cross-check with plan.md**: verify plan's "Idea Technical Alignment" section exists; if plan has divergences, carry them to tasks (not ignore them); if plan lacks the section, perform alignment check now

   c. **Pre-generation checklist** — for each technical requirement in idea:
      - Is it reflected in plan.md?
      - Will the generated tasks implement it correctly?
      - Is the execution order preserved?
      - Are specific commands/tools preserved (not substituted)?

   d. **Stop on misalignment**: if idea specifies approach X but plan uses approach Y, report the divergence to user before generating tasks, ask for explicit confirmation, and document the decision in tasks.md header
   </alignment_checks>

5. **Execute task generation workflow**:
   - Load plan.md → extract tech stack, libraries, project structure
   - Load spec.md → extract user stories with priorities (P1, P2, P3, etc.)
   - If data-model.md exists: extract entities and map to user stories
   - If contracts/ exists: map endpoints to user stories
   - If research.md exists: extract decisions for setup tasks, existing codebase analysis, and reuse/extend/new markers per component
   - Map IDEA_TECHNICAL_REQUIREMENTS to specific tasks (see Task Generation Rules)
   - Map reuse decisions to specific tasks (see Reuse Task Rules)
   - Generate tasks organized by user story
   - Generate dependency graph showing user story completion order
   - Create parallel execution examples per user story
   - Validate: each user story has all needed tasks and is independently testable
   - Validate: each idea requirement maps to at least one task
   - Validate: reuse decisions from research.md are reflected in tasks

6. **Generate tasks.md**: Use `templates/tasks-template.md` as structure, fill with:
   - Correct feature name from plan.md
   - Phase 1: Setup tasks (project initialization)
   - Phase 2: Foundational tasks (blocking prerequisites for all user stories)
   - Phase 3+: One phase per user story (in priority order from spec.md)
   - Each phase includes: story goal, independent test criteria, tests (if requested), implementation tasks
   - Final Phase: Polish & cross-cutting concerns
   - All tasks follow the strict checklist format (see Task Generation Rules)
   - Clear file paths for each task
   - Dependencies section, parallel execution examples, implementation strategy
   - Idea Technical Traceability section and Reuse Traceability section (see below)

7. **Report**: Output path to generated tasks.md and summary:
   - Total task count and task count per user story
   - Parallel opportunities identified
   - Independent test criteria for each story
   - Suggested MVP scope (typically just User Story 1)
   - Format validation: confirm all tasks follow checklist format
   - Idea alignment status: confirm all technical requirements from idea are mapped
   - Reuse summary: count of REUSE/EXTEND/REFACTOR/NEW tasks; flag if NEW > 50%

Context for task generation: {ARGS}

The tasks.md should be immediately executable — each task must be specific enough that an LLM can complete it without additional context.

## Task Generation Rules

Tasks are organized by user story so each story can be implemented and tested independently.

Tests are optional: only generate test tasks if explicitly requested in the feature specification or by the user (e.g. TDD approach).

### Checklist Format

Every task follows this format — deviations break downstream automation:

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

<format_components>

1. **Checkbox**: `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential (T001, T002, T003...) in execution order
3. **[P] marker**: Only if task is parallelizable (different files, no dependencies on incomplete tasks)
4. **[Story] label**: [US1], [US2], etc. — required for user story phase tasks only (not Setup, Foundational, or Polish phases)
5. **Description**: Clear action with exact file path

</format_components>

**Correct**:

- `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- `- [ ] T012 [P] [US1] Create User model in src/models/user.py`

**Wrong** (these break parsing):

- `- [ ] Create User model` — missing ID and Story label
- `T001 [US1] Create model` — missing checkbox

### Task Organization

1. **From User Stories (spec.md)** — primary organization:
   - Each user story (P1, P2, P3...) gets its own phase
   - Map all related components (models, services, endpoints/UI, tests if requested) to their story
   - Mark story dependencies (most stories should be independent)

2. **From Contracts**: map each endpoint to its user story; if tests requested, add contract test task [P] before implementation

3. **From Data Model**: map each entity to its user story(ies); if entity serves multiple stories, put in earliest story or Setup phase

4. **From Setup/Infrastructure**: shared infrastructure → Setup (Phase 1); blocking tasks → Foundational (Phase 2); story-specific setup → within that story's phase

### Phase Structure

- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (blocking prerequisites — must complete before user stories)
- **Phase 3+**: User Stories in priority order (P1, P2, P3...)
  - Within each story: Tests (if requested) → Models → Services → Endpoints → Integration
  - Each phase should be a complete, independently testable increment
- **Final Phase**: Polish & Cross-Cutting Concerns

### Reuse Task Rules

Tasks reflect reuse decisions from research.md — this avoids rebuilding what already exists.

**Task Type Markers**:

- `[REUSE]` — use existing component as-is (wire it up)
- `[EXTEND]` — add capabilities to existing component
- `[REFACTOR]` — modify existing component for broader use
- `[NEW]` — create new component (must be justified in research.md)

**Examples**:

- `- [ ] T005 [P] [US1] [REUSE] Wire existing AuthService for user validation`
- `- [ ] T015 [P] [US4] [NEW] Create PaymentGateway integration in src/services/payment.py`

**Per-marker guidance**:

- **[REUSE]**: Reference existing component path; describe integration; no new file creation
- **[EXTEND]**: Reference component to extend; describe new capability and extension approach
- **[REFACTOR]**: Reference component to refactor; describe goal; list affected code; include task to update existing usages
- **[NEW]**: Reference research.md justification; explain why existing code couldn't be used; follow existing codebase patterns

### Idea Technical Traceability

Include at the end of tasks.md. This section proves every idea requirement has a corresponding task — missing mappings mean lost requirements.

```markdown
## Idea Technical Traceability

**Source Idea**: [path to idea.md]

| Idea Requirement | Task(s) | Status |
|------------------|---------|--------|
| [Command/tool/approach from idea] | T001, T005 | Mapped |
| [Execution order requirement] | T003 → T004 → T005 | Order preserved |

### Divergences from Idea (if any)

| Idea Specified | Task Implements | Justification |
|----------------|-----------------|---------------|
| [original approach] | [different approach] | [reason from plan.md] |
```

If any technical requirement from the idea is not mapped to a task, either add the missing task(s) or document why it was intentionally omitted (with user confirmation).

### Reuse Traceability

Include after Idea Technical Traceability. This section tracks code reuse health — a high NEW ratio signals that existing code may not have been properly explored.

```markdown
## Reuse Traceability

**Source**: research.md (Existing Codebase Analysis)

| Type | Count | Tasks |
|------|-------|-------|
| REUSE | X | T001, T005, ... |
| EXTEND | X | T008, T012, ... |
| REFACTOR | X | T015, ... |
| NEW | X | T020, T021, ... |

| Component | Decision | Task | Justification |
|-----------|----------|------|---------------|
| AuthService | REUSE | T005 | Existing auth fits requirements |
| PaymentGateway | NEW | T020 | No existing payment integration |
```

Every [NEW] task needs explicit justification from research.md. More [REUSE]/[EXTEND] than [NEW] indicates good code reuse. If NEW > 50%, reconsider whether existing code was properly explored.
