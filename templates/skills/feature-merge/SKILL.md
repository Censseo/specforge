---
name: feature-merge
description: |
  Close a feature: verify it is complete, consolidate its specification into the durable /docs domain
  documentation, merge the branch and clean up. Activate when: a feature is finished and ready to land,
  or when consolidating working specs into project documentation.
triggers: ["merge the feature", "consolidate docs", "land this feature", "close the feature", "merge to main", "update /docs"]
phase: qa
---

# Feature Merge and Documentation Consolidation

> `specs/` is working memory - one directory per feature, written once and abandoned. `/docs` is
> durable memory - one directory per domain, read by every future feature. Merging is the moment the
> first becomes the second.

## Phase 1 - Pre-merge Validation

Stop, do not warn, if any of these fail:

| Check | Failure |
| ----- | ------- |
| All tasks in `tasks.md` marked `[X]` | Incomplete tasks remain |
| Working tree clean | Uncommitted changes |
| Branch up to date with remote | Behind origin |
| QA gate PASS or PASS WITH CONDITIONS | Gate not cleared |

Warn (but may proceed) if `spec.md`, `plan.md` or `task-results/` are missing or thin.

## Phase 2 - Determine Target Domains

A feature can span several domains; a checkout feature may touch `payments`, `orders` and
`notifications`.

1. Read `**Domain**:` or `**Domains**:` from the spec header if present.
2. Otherwise infer from the feature name, stories and entities, and propose kebab-case domain names.
3. List the existing domains (`ls -d docs/*/`) for context.
4. **Confirm with the user.** Domains are user-defined; the skill suggests, the user decides.

## Phase 3 - Consolidate into `/docs/{domain}/spec.md`

For each target domain, extract only the parts of the feature spec that belong to it.

| Domain spec section | Content |
| ------------------- | ------- |
| Purpose | What this domain is responsible for |
| Features | One subsection per delivered feature: behavior, business rules, links to the source spec |
| Entities | Fields, relationships, invariants - merged with what is already there |
| Business rules | Normative statements, deduplicated |
| API contracts | Endpoints and events owned by this domain |
| Changelog | Feature, date, what changed |

Merge rules:

- **Never overwrite an existing domain spec.** Merge into it.
- On a conflict between the new feature and existing documentation, stop and ask - a silent overwrite
  loses a decision nobody will remember making.
- Deduplicate entities and rules rather than appending near-duplicates.
- Keep links back to `specs/{feature}/spec.md` for provenance.
- Update `/docs/README.md` with the domain index.

## Phase 4 - Git Operations

Merge the feature branch into the base branch following the repository's own convention (merge vs
rebase - check `CONTRIBUTING.md` before assuming). Include the documentation consolidation in the
merge, so `/docs` and the code land together.

Never rewrite history on a branch that is not yours.

## Phase 5 - Post-merge

- Mark the feature complete in `specs/{feature}/` (do not delete it - it is the audit trail).
- Run `codebase-learning` so the registry and context files absorb what this feature established.
- Report: branch merged, domains updated, files created or changed, follow-ups still open.

## Dry Run

When asked to preview, show: what would be merged, which `/docs` files would be created or appended
with an excerpt of each change, and explicitly what would **not** be done. Change nothing.

## Discipline

- A feature with open conditions from the QA gate merges only if those conditions are recorded as
  tracked follow-ups with owners.
- Documentation consolidation is not optional. Skipping it is how `/docs` becomes stale and every
  future feature re-derives the same domain knowledge.
