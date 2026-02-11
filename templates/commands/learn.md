---
description: Analyze codebase and specs to update architecture registry, project state context, and local __AGENT_CONTEXT_FILE__ files (module and sub-module conventions)
semantic_anchors:
  - Pattern Mining           # Extract recurring solutions from code
  - ADR                      # Architecture Decision Records, Michael Nygard
  - Code Archaeology         # Understanding existing systems through analysis
  - Conway's Law             # System structure mirrors organization structure
  - Traceability             # Link specifications to implementation artifacts
---

## User Input

```text
$ARGUMENTS
```

Consider the user input before proceeding. User can specify: "all" (full analysis), feature names, specific directories, or "specs-only" / "modules-only" for partial updates.

## Purpose

> **Activated Frameworks**: Pattern Mining, ADR, Code Archaeology, Traceability.

This command analyzes the existing codebase and specifications to learn and document:

| Output | Location | What it captures |
| ------ | -------- | ---------------- |
| High-level patterns | `/memory/architecture-registry.md` | Architectural patterns, technology decisions, interface contracts, anti-patterns |
| Project state context | `specs/__AGENT_CONTEXT_FILE__` | Domain vocabulary, data model state, active contracts, feature dependencies, business invariants, cross-cutting concerns |
| Module conventions | `{module}/__AGENT_CONTEXT_FILE__` | Coding conventions, interface contracts, business invariants, state machines, guard rails, dependency graph, testing conventions |
| Sub-module conventions | `{module}/{subdir}/__AGENT_CONTEXT_FILE__` | Layer-specific patterns, function signatures with spec sources, injected dependencies, expected error types — only generated for directories exceeding complexity threshold |

## Outline

### Phase 1: Discovery

1. **Detect project structure**: Identify main source directories (`src/`, `lib/`, `app/`, `packages/`), detect subdirectories representing distinct modules, look for existing `__AGENT_CONTEXT_FILE__` files.

1. **Load existing registry** (if exists): Read `/memory/architecture-registry.md`, extract registered patterns, identify what needs updating.

1. **Scan for implemented features**: Look for `specs/*/task-results/` (completed implementations), extract patterns from plan.md and research.md files.

1. **Load consolidated docs** (primary source of truth):
   - Read all `/docs/*/spec.md` for domain vocabulary, business rules, entities, API contracts
   - Read `/docs/README.md` for domain index and boundaries
   - `/docs/` is the merged, reviewed specification — it takes precedence over `specs/` working files when both define the same entity, contract, or term

1. **Scan specs for in-progress state**:
   - Read all `specs/*/spec.md`, `specs/*/data-model.md`, `specs/*/contracts/`, `specs/*/plan.md`
   - Load existing `specs/__AGENT_CONTEXT_FILE__` to identify what needs updating
   - Merge with `/docs/` data: `/docs/` is authoritative for completed features; `specs/` adds in-progress features not yet merged

1. **Evaluate sub-module complexity**: For each module directory, inspect subdirectories — count source files (exclude tests, configs, generated), count exported symbols, check for known architectural layer names. Record results for Phase 5.

1. **Determine scope and active phases**:

   | Scope | Phase 2 (Specs Context) | Phase 3 (Arch Patterns) | Phase 4 (Module) | Phase 5 (Sub-Module) |
   | ----- | :---------------------: | :---------------------: | :--------------: | :------------------: |
   | `all` | Yes | Yes | Yes | Yes |
   | `specs-only` | Yes | — | — | — |
   | `modules-only` | — | Yes | Yes | Yes |
   | `deep` | Yes | Yes | Yes | Yes (force all layers) |
   | `{feature names}` | Yes (scoped) | — | Yes (scoped) | Yes (scoped) |
   | `{directories}` | — | — | Yes (scoped) | Yes (scoped) |
   | Default (no args) | Yes | Yes | Yes | — |

   Sub-module generation (Phase 5) only runs when explicitly included in scope because generating context files for small projects adds noise without benefit. Use `/specforge.learn all` or `/specforge.learn deep` to include sub-modules.

   **Scope rules** (where the table leaves room for ambiguity):
   - `deep`: Same as `all` but forces sub-module generation for all recognized architectural layers regardless of file count (only the 3-file minimum still applies)
   - `{feature names}`: Analyzes those features + their impacted modules + sub-modules
   - Default (no args): Analyzes features with task-results but not in registry

### Phase 2: Specs Context Extraction

1. **Extract project-wide state from docs and specs**:

   <data-source-priority>
   `/docs/{domain}/spec.md` (merged, reviewed) takes precedence over `specs/*/spec.md` (in-progress).
   When both sources define the same entity, contract, or term, `/docs/` wins.
   `specs/` adds what is not yet merged (in-progress features).
   </data-source-priority>

   For each sub-step below, apply this pattern: extract from `/docs/` first (primary, canonical), then supplement from `specs/` for in-progress features not yet in `/docs/`.

   Skip this phase if both `specs/` and `/docs/` are empty. Log: "No feature specs or docs found — skipping specs context generation."

   a. **Domain Vocabulary**: Extract entity names, business terms, acronyms. Build canonical term table: term, definition, source. Flag conflicting definitions. Identify aliases to prohibit (e.g., "Client" vs canonical "User").

   b. **Data Model State**: Extract entities with key fields and relationships. For each entity, record: name, key fields, owning feature/domain, status (ACTIVE = in `/docs/` + code, PLANNED = in `specs/` only, DEPRECATED = in `/docs/` but unreferenced in code). Identify shared entities referenced by multiple features and document change impact.

   c. **Active Interface Contracts**: Extract API and event contracts. For each: method, path/name, request/response types, owning feature. Group by REST APIs, Events, Shared Types. Identify conflicts or overlaps. Mark status: ACTIVE or PLANNED.

   d. **Feature Dependency Graph**: Build adjacency list from "Requires"/"Enables" sections and plan.md cross-references. Mark status: COMPLETE (in `/docs/`), IN_PROGRESS (in `specs/` with task-results), PLANNED (in `specs/` without task-results). Detect circular dependencies and flag as warnings.

   e. **Business Invariants**: Extract business rules and acceptance criteria (Given/When/Then). Categorize as Data invariants (DI-N), Workflow invariants (WI-N), Security invariants (SI-N). Cross-reference with `/memory/constitution.md` Specification Principles.

   f. **Cross-Cutting Concerns**: Scan codebase for auth patterns, error response formats, validation patterns, logging patterns. Document each with: pattern name, file reference, applicable scope.

### Phase 3: High-Level Pattern Extraction

1. **Extract architectural patterns**:

   a. **Layer patterns**: Service layer, repository, controller, DDD, event-driven, CQRS (as present).

   b. **Interface contracts**: API contracts between modules, event schemas, shared types.

   c. **Technology decisions**: From dependency manifests (package.json, requirements.txt, go.mod, etc.). Categorize by: framework, validation, state, data fetching, styling, testing. Document rationale from research.md if available.

   d. **Architectural anti-patterns**: Patterns refactored or abandoned, cross-cutting concerns handled incorrectly, tight coupling between modules.

### Phase 4: Module Convention Extraction

1. **For each detected module directory** (frontend/, backend/, api/, etc.):

   a. **Directory structure**: Analyze subdirectory organization.

   b. **Naming conventions**: File naming (PascalCase, camelCase, kebab-case), component/function naming, test file patterns.

   c. **Code patterns**: Identify recurring patterns for services, components, hooks, handlers — by scanning actual source files.

   d. **Error handling patterns**: Try-catch patterns, error boundaries, result types.

   e. **Testing conventions**: Test file location, framework, mocking patterns.

   f. **Interface contracts**: Scan exported functions/classes/endpoints (public API), cross-reference with `specs/*/contracts/`, scan imports from other modules. Document: interface name, type (REST/Function/Event), signature, consumers/providers, spec source.

   g. **Business invariants**: From specs referencing files in this module (via plan.md paths or task-results/). Document as: invariant ID (from Phase 2), enforcement mechanism in this module.

   h. **State machines / lifecycle rules**: Scan for enum types representing states, transition functions, status fields. Cross-reference with spec.md state transition descriptions. Document: entity, states, valid/invalid transitions, spec source.

   i. **Guard rails**: From architecture-registry anti-patterns, task-results lessons learned, constitution.md principles. Document: what is prohibited, why, source.

   j. **Module dependency graph**: Internal (project module imports), external (third-party packages), spec-sourced (which specs define requirements for this module).

### Phase 5: Sub-Module Analysis

1. **For each module, evaluate sub-directories for granular context**:

   a. **Complexity threshold** — generate a sub-module `__AGENT_CONTEXT_FILE__` when ANY of:
      - Source file count >= 8 (excluding tests, configs, generated files)
      - Exported symbol count >= 15
      - Directory name matches a known architectural layer: `services/`, `models/`, `controllers/`, `handlers/`, `repositories/`, `api/`, `middleware/`, `routes/`, `resolvers/`, `adapters/`, `ports/`

   Skip directories that are test-only, config-only, generated (`dist/`, `node_modules/`, `__pycache__/`), have fewer than 3 source files, or are deeper than 3 levels from project root.

   b. **For qualifying sub-directories, extract**:

      - **Layer pattern**: Architectural role, file convention, one canonical code example from the codebase
      - **Function signatures with spec sources**: Public functions/methods cross-referenced with `specs/*/contracts/` and `specs/*/plan.md`
      - **Injected dependencies**: Constructor injection, parameter injection, module-level imports — what it provides, where it comes from
      - **Expected errors**: Error types raised/returned, handling patterns, cross-reference with spec error scenarios
      - **Layer-specific guard rails**: Rules specific to this layer (e.g., "Services should not access database directly — use repositories" because it breaks the repository pattern and makes testing harder)

### Phase 6: Generate/Update Files

1. **Update `/memory/architecture-registry.md`** — high-level content only:

   ```markdown
   # Architecture Registry
   > High-level patterns. Module-specific: `{module}/__AGENT_CONTEXT_FILE__`. Project state: `specs/__AGENT_CONTEXT_FILE__`.

   ## Architectural Patterns
   | Pattern | Description | Modules Using | Interface |
   | ------- | ----------- | ------------- | --------- |

   ## Technology Stack
   | Category | Technology | Rationale |
   | -------- | ---------- | --------- |

   ## Module Contracts
   ### {Module A} <-> {Module B}
   - **Interface**: ... **Contract**: ... **Location**: ...

   ## Architectural Anti-Patterns
   | Anti-Pattern | Issue | Correct Approach |
   | ------------ | ----- | ---------------- |
   ```

1. **Create/Update `specs/__AGENT_CONTEXT_FILE__`**: Use template from `templates/specs-context-template.md`. Fill from Phase 2 results. Preserve content between `<!-- MANUAL ADDITIONS START -->` and `<!-- MANUAL ADDITIONS END -->` markers. Skip if specs/ is empty (logged in Phase 2).

1. **Create/Update `{module}/__AGENT_CONTEXT_FILE__`** for each detected module:

   Use template from `templates/module-claude-template.md`. Fill sections from Phase 4 steps (a-j): Overview, Structure, Naming, Patterns, Components, Error Handling, Testing, Interface Contracts, Business Invariants, State Machines, Guard Rails, Module Dependency Graph, Gotchas. Preserve MANUAL ADDITIONS markers.

   ```markdown
   # {Module} Development Guidelines
   > Auto-generated by /specforge.learn. Manual additions preserved between markers.

   ## Directory Structure        <!-- a -->
   ## Naming Conventions         <!-- b -->
   ## Code Patterns              <!-- c -->
   ## Error Handling             <!-- d -->
   ## Testing                    <!-- e -->
   ## Interface Contracts        <!-- f -->
   ## Business Invariants        <!-- g -->
   ## State Machines & Lifecycle <!-- h -->
   ## Guard Rails                <!-- i -->
   ## Module Dependency Graph    <!-- j -->
   ## Gotchas

   <!-- MANUAL ADDITIONS START -->
   <!-- MANUAL ADDITIONS END -->
   ```

1. **Create/Update `{module}/{subdir}/__AGENT_CONTEXT_FILE__`** for qualifying sub-directories (passed Phase 5 threshold). No separate template — content varies by layer type:

   ```markdown
   # {SubDir} Layer Guidelines
   > Auto-generated by /specforge.learn on {DATE}
   > Layer: {layer_type} | Parent: {module_path}

   ## Layer Pattern
   ## Function Signatures & Spec Sources
   ## Injected Dependencies
   ## Expected Errors
   ## Guard Rails

   <!-- MANUAL ADDITIONS START -->
   <!-- MANUAL ADDITIONS END -->
   ```

   Populate each section from Phase 5b extraction. Use tables for signatures, dependencies, and errors. Preserve MANUAL ADDITIONS markers in existing files.

### Phase 7: Review and Apply

1. **Present changes to user**:

   ```markdown
   ## Learn Summary

   ### Architecture Registry Updates
   - [N] patterns added/updated, [N] tech decisions, [N] module contracts

   ### Specs Context
   | Section | Items | Status |
   | ------- | ----- | ------ |
   | Domain Vocabulary | [N] | Created/Updated |
   | ... | | |

   ### Module Files
   | Module | Status | Conventions | Contracts | Invariants | Guard Rails |
   | ------ | ------ | ----------- | --------- | ---------- | ----------- |

   ### Sub-Module Files
   | Sub-Module | Threshold Met | Items |
   | ---------- | ------------- | ----- |

   ### Warnings
   - [Conflicting vocabulary / circular dependencies / overlapping contracts]

   ### Recommendations
   - [Missing documentation / suggested manual additions]

   Apply changes? (yes/no/selective)
   ```

1. **Apply changes** with user confirmation. Update all target files. Preserve manual additions between markers. Log changes made.

## Output Files

- `/memory/architecture-registry.md` — high-level architectural patterns
- `specs/__AGENT_CONTEXT_FILE__` — project state context for spec agents
- `{module}/__AGENT_CONTEXT_FILE__` — module conventions, contracts, invariants
- `{module}/{subdir}/__AGENT_CONTEXT_FILE__` — layer-specific context (qualifying dirs only)

## Key Principles

- **High-level vs Local**: Registry = cross-cutting patterns, module files = module-specific, specs context = project state
- **Docs over specs**: `/docs/` is the merged, reviewed source of truth; `specs/` supplements with in-progress features. `/docs/` wins on conflicts because downstream commands (`/specforge.specify`, `/specforge.plan`) rely on consistent canonical terms
- **Extract, don't invent**: Only document what is actually present in code, docs, or specs
- **Aggregate, don't duplicate**: Specs context aggregates from `/docs/` and `specs/` without copying verbatim
- **Preserve manual additions**: Content between MANUAL markers is never overwritten
- **Sub-module is conditional**: Only generated when complexity warrants it (>= 8 files, >= 15 exports, or known layer name) to avoid noisy context in small projects
- **Spec-sourced**: Contracts, invariants, and state machines reference their source spec ID so `/specforge.fix` can trace regressions back to requirements

## Usage Examples

```bash
# Quick update after implementation (modules + specs context, NO sub-modules)
/specforge.learn

# Full analysis INCLUDING sub-module context files
/specforge.learn all

# Full analysis + force sub-modules for ALL recognized layers (even small ones)
/specforge.learn deep

# Learn from specific features (includes their impacted modules + sub-modules)
/specforge.learn feat-001-auth feat-002-dashboard

# Analyze specific directories + their sub-modules
/specforge.learn src/frontend src/backend

# Update only the specs context file (skip modules entirely)
/specforge.learn specs-only

# Update only module + sub-module files (skip specs context)
/specforge.learn modules-only
```

## Integration with Workflow

| Command | What it loads from /learn output | Why |
| ------- | ------------------------------- | --- |
| `/specforge.specify` | `specs/__AGENT_CONTEXT_FILE__` | Vocabulary consistency — prevents inventing conflicting terms |
| `/specforge.plan` | `architecture-registry.md` + `specs/__AGENT_CONTEXT_FILE__` + `/docs/` directly | Architecture alignment + contract/invariant awareness |
| `/specforge.implement` | `{module}/__AGENT_CONTEXT_FILE__` + `{subdir}/__AGENT_CONTEXT_FILE__` | Conventions + contracts reduce functional drift during coding |
| `/specforge.clarify` | `specs/__AGENT_CONTEXT_FILE__` | Asks questions using correct domain vocabulary |
| `/specforge.merge` | Produces `/docs/` that /learn reads | Closes the feedback loop: merge -> learn -> specify |
