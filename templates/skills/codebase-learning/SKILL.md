---
name: codebase-learning
description: |
  Analyse the codebase and its specs to update the architecture registry, the project context file and
  per-module convention files, so future work inherits what has been established. Activate when: after
  implementing or merging a feature, or when agent context files are stale.
triggers: ["learn the codebase", "update the registry", "refresh context files", "extract patterns", "update architecture registry", "document conventions"]
phase: qa
---

# Codebase Learning

> Every feature teaches the project something. Without this step, the lesson is lost and the next
> feature re-derives it - differently.

## Outputs

| Output | Location | Captures |
| ------ | -------- | -------- |
| High-level patterns | `/memory/architecture-registry.md` | Architectural patterns, technology decisions, interface contracts, anti-patterns |
| Project state | `specs/__AGENT_CONTEXT_FILE__` | Domain vocabulary, data model state, active contracts, feature dependencies, business invariants, cross-cutting concerns |
| Module conventions | `{module}/__AGENT_CONTEXT_FILE__` | Coding conventions, interface contracts, invariants, state machines, guard rails, dependency graph, testing conventions |
| Sub-module conventions | `{module}/{subdir}/__AGENT_CONTEXT_FILE__` | Layer-specific patterns and signatures - only for directories above the complexity threshold |

## Source Priority

`/docs/{domain}/spec.md` is authoritative: it is merged and reviewed. `specs/*/` supplements it with
in-progress work not yet consolidated. Where both define the same entity, contract or term, `/docs`
wins.

## Phase 1 - Discovery

Detect source directories and module boundaries; load the existing registry; find features with
`task-results/` (actually implemented); read `/docs/*/spec.md` and `/docs/README.md`; read in-progress
`specs/*/`; evaluate sub-module complexity (source file count excluding tests and generated code,
exported symbol count, recognised layer names).

## Phase 2 - Project State Extraction

| Extract | Method |
| ------- | ------ |
| Domain vocabulary | Canonical term table: term, definition, source. Flag conflicting definitions; list prohibited aliases |
| Data model state | Entity, key fields, owner, status: ACTIVE (`/docs` + code), PLANNED (`specs` only), DEPRECATED (`/docs` but unreferenced) |
| Interface contracts | Method, path or event name, request and response types, owner, status; flag overlaps |
| Feature dependency graph | Adjacency list from Requires/Enables; status COMPLETE / IN_PROGRESS / PLANNED; flag cycles |
| Business invariants | Data (DI-n), workflow (WI-n), security (SI-n); cross-reference the constitution |
| Cross-cutting concerns | Auth, error format, validation, logging patterns with file references |

## Phase 3 - Pattern Extraction

Layer patterns present (service, repository, controller, DDD, event-driven, CQRS); interface contracts
between modules; technology decisions from the dependency manifests with rationale from `research.md`;
and anti-patterns - approaches that were tried and abandoned, with the reason.

Anti-patterns are the highest-value entries in a registry. They are the only record of why the obvious
approach was rejected.

## Phase 4 - Module Conventions

Per module: naming and file organisation, interface contracts it exposes, invariants it enforces,
state machines it owns, guard rails (what must never be done here), its dependency edges, and its
testing conventions.

## Phase 5 - Sub-modules

Only for directories that exceed the complexity threshold, and only when the scope explicitly asks.
Generating context files for small directories adds noise that dilutes the useful ones.

## Phase 6 - Write

- **Preserve manual content.** Everything between the manual markers stays exactly as it is.
- Add new entries dated and attributed: `<!-- Added from {feature} ({date}) -->`.
- Update rather than duplicate an existing entry.
- Never delete a registry entry without saying why; a pattern that was abandoned becomes an
  anti-pattern entry, not an absence.

## Phase 7 - Report

Files created or updated, patterns added, conflicts detected (especially vocabulary conflicts and
duplicate contracts), and entities now marked DEPRECATED.

"No new patterns - the feature followed existing conventions" is a good result. Record it.

## Who Consumes This

| Skill | Reads | Why |
| ----- | ----- | --- |
| `spec-authoring` | Project context file | Vocabulary consistency |
| `technical-planning` | Registry + context + `/docs` | Architecture alignment and contract awareness |
| `implementation-execution` | Module and sub-module context | Conventions reduce drift during coding |
| `requirements-clarification` | Project context file | Ask questions in the right vocabulary |
