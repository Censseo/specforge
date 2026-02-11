---
description: Execute the implementation planning workflow using the plan template to generate design artifacts.
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

Consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Run `{SCRIPT}` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**: Read FEATURE_SPEC and `/memory/constitution.md`. Load IMPL_PLAN template (already copied).

3. **Load source idea**: Extract the source idea from spec.md header or locate it:
   - Check spec.md for `**Source**:` or `**Parent Idea**:` links
   - If found, load the linked idea.md file; otherwise search `ideas/` by feature name
   - Extract **Technical Hints**, **Constraints & Assumptions**, and **Discovery Notes** sections
   - Store these as IDEA_TECHNICAL_CONSTRAINTS for validation in step 9

<doc_loading>
4. **Load existing documentation**: New features that contradict existing domain rules cause integration failures downstream.

   a. **Check `/docs` directory**: If `/docs/README.md` exists, list existing domains from `/docs/*/spec.md`.

   b. **Identify target domain** from spec.md's DOCUMENTATION_CONTEXT (set by specify) or infer from feature name.

   c. **Load domain spec** from `/docs/{domain}/spec.md`: extract existing features, entities, business rules, and API contracts to understand how the new feature fits.

   d. **Load cross-domain dependencies** if spec.md references other domains — load related specs for integration context.

   e. **Create DOCUMENTATION_CONTEXT** summarizing:
      - Features in domain (with business rules and integration points)
      - Reusable entities (with fields and extension needs)
      - Domain API patterns (with reuse potential for new feature)
      - Cross-domain dependencies (domain, dependency, contract)

   f. **If no `/docs` exists**: Log that this is likely the first feature and recommend running `/specforge.merge` after implementation.
</doc_loading>

<architecture_registry>
5. **Load architecture registry**: Skipping this step leads to pattern drift — teams waste time debugging inconsistencies across features.

   a. **Check for `/memory/architecture-registry.md`** and extract: established patterns, technology decisions, component conventions, anti-patterns, and cross-feature dependencies.

   b. **Create ARCHITECTURE_CONSTRAINTS list** covering: patterns to reuse, required technologies, component locations/naming, and approaches to avoid.

   c. **If no registry exists**: Log the absence, recommend running `/specforge.learn` after this feature, and proceed with explicit decision documentation.
</architecture_registry>

<codebase_exploration>
6. **Explore existing codebase**: Creating new code when reusable components exist wastes effort and fragments the codebase.

   a. **Identify reusable components**: Search for existing services, utilities, base classes, and data models that overlap with requirements.

   b. **Analyze existing architecture**: Understand project structure, established patterns, configuration mechanisms, and error handling conventions.

   c. **For each capability in the spec**: search for similar functionality, check service/lib/util directories, review related features, and inspect shared infrastructure.

   d. **Document findings** in research.md (Existing Codebase Analysis section) with tables for: reusable components found, existing patterns to follow, and potential conflicts.

   e. **Apply reuse decision matrix**: REUSE (fits as-is) → EXTEND (needs additions) → REFACTOR (needs redesign) → NEW (nothing suitable, document why).
</codebase_exploration>

<architecture_alignment>
7. **Validate architecture alignment**: Undocumented divergence causes architectural drift, which compounds across features until the system becomes unmaintainable.

   For each capability, check against ARCHITECTURE_CONSTRAINTS: does an established pattern exist? Is a technology decision specified? Does a component convention apply? Is there an anti-pattern risk?

   **Create Architecture Alignment Report** in plan.md with:
   - Patterns applied (from registry or new, aligned or divergent)
   - Technology alignment (registry vs. plan)
   - New patterns introduced (with justification and registry update flag)
   - Divergences requiring justification

   **If divergences detected**: Stop and ask the user — "Plan diverges from established patterns. Approve divergence? (yes/no/modify)". If "no", revise; if "yes", document approval; if "modify", discuss alternatives.

   **If no registry exists**: Mark all decisions as "New Pattern - to be registered" and proceed.
</architecture_alignment>

8. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (include Existing Codebase Analysis from step 6)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Phase 1: Update agent context by running the agent script
   - Re-evaluate Constitution Check post-design
   - Prefer extending existing components over creating new ones
   - Ensure Architecture Alignment section is included in plan.md

<idea_alignment>
9. **Validate alignment with source idea**: Plans that contradict the original idea's technical intent create rework when reviewers catch the mismatch.

   a. **Extract technical requirements from idea**: commands/scripts, tools/libraries/versions, execution order, technical patterns, and integration instructions.

   b. **Cross-check with plan.md**: For each constraint — mark as ALIGNED (plan addresses it), DIVERGENT (different approach, requires justification), or MISSING (not addressed, add to plan).

   c. **Create alignment report** in plan.md with source idea path, constraint status table, and any divergences with justification.

   d. **If critical divergences exist** (plan contradicts explicit technical instructions from idea): Stop and ask user to confirm before proceeding; document the decision in research.md.
</idea_alignment>

10. **Stop and report**: Command ends after Phase 2 planning. Report:
    - Branch and IMPL_PLAN path
    - Generated artifacts
    - Architecture alignment status (patterns followed, divergences approved)
    - Alignment status with source idea
    - Reuse summary: components reused vs. new code created
    - Registry updates needed: new patterns to register after implementation

## Phases

### Phase 0: Outline & Research

1. **Include Existing Codebase Analysis** (from step 6):
   - Copy findings from step 6 into research.md as the first section
   - Include Architecture Constraints from step 5
   - All subsequent decisions should reference this analysis and registry constraints

2. **Extract unknowns from Technical Context**:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

3. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   For each capability:
     Task: "Search codebase for existing implementation of {capability}"
   ```

4. **Consolidate findings** in `research.md`:

   ```markdown
   ## Existing Codebase Analysis
   [From step 6 - reusable components, patterns, conflicts]

   ## Technical Decisions

   ### Decision 1: [Topic]
   - **Decision**: [what was chosen]
   - **Existing code considered**: [what was evaluated]
   - **Reuse approach**: REUSE / EXTEND / REFACTOR / NEW
   - **Rationale**: [why, especially if NEW]
   - **Alternatives considered**: [what else evaluated]
   ```

**Output**: research.md with existing codebase analysis, all NEEDS CLARIFICATION resolved, and reuse decisions justified.

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete (with Existing Codebase Analysis)

1. **Extract entities from feature spec** → `data-model.md`:
   - First check if entities already exist in the codebase
   - If entity exists: reference it, note if extension needed
   - If entity is new: define name, fields, relationships, validation rules, state transitions
   - Mark each entity: EXISTING / EXTENDED / NEW

2. **Generate API contracts** from functional requirements:
   - First check if similar endpoints already exist
   - For each user action → endpoint, using patterns from codebase (step 6) and registry (step 5)
   - Output OpenAPI/GraphQL schema to `/contracts/`
   - Mark each endpoint: EXISTING / MODIFIED / NEW

3. **Agent context update**:
   - Run `{AGENT_SCRIPT}` to detect the AI agent in use
   - Update the appropriate agent-specific context file
   - Add only new technology from current plan
   - Preserve manual additions between markers

**Output**: data-model.md, /contracts/*, quickstart.md, agent-specific file. Each artifact should clearly indicate what is reused vs. new.
