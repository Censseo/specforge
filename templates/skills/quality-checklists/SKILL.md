---
name: quality-checklists
description: |
  Generate and review checklists that test the quality of requirements - unit tests for requirements
  writing, not for the implementation. Activate when: creating a domain checklist (ux, api, security),
  validating checklists against the spec, or establishing a definition of ready or done.
triggers: ["create a checklist", "checklist review", "definition of done", "definition of ready", "quality checklist", "validate checklists"]
semantic_anchors: [Definition of Ready, Definition of Done, INVEST Criteria, Acceptance Criteria, Quality Gates]
phase: qa
---

# Quality Checklists

> If the spec is code written in English, the checklist is its unit test suite. It tests the
> requirements, never the implementation.

## The Distinction That Matters

| Correct - tests the requirements | Wrong - tests the system |
| -------------------------------- | ------------------------ |
| "Are visual hierarchy requirements defined for all card types? [Completeness]" | "Verify the landing page shows 3 cards" |
| "Is 'prominent display' quantified with sizing and positioning? [Clarity]" | "Test hover states work on desktop" |
| "Are keyboard navigation requirements defined? [Coverage, Gap]" | "Check the API returns 200" |

If an item could be executed against a running system, it belongs in a test, not here.

## Generate Mode

### 1. Clarify intent

Derive up to three questions, only where the answer changes the checklist's content. Skip them when
the request is already unambiguous.

Question archetypes: scope refinement, risk prioritisation, depth calibration (pre-commit sanity vs
release gate), audience framing (author, peer reviewer, QA, release), boundary exclusion, and
scenario-class gaps ("no recovery flows are mentioned - are rollback paths in scope?").

Defaults when interaction is impossible: depth Standard; audience Reviewer for code-related, Author
otherwise; focus on the top two relevance clusters. Never exceed five questions in total.

### 2. Load references

- `/memory/constitution.md`: generate a Constitution Compliance section, one or more items per
  principle, referencing `[Constitution §X]`.
- `/memory/architecture-registry.md` (only when `plan.md` exists): generate an Architecture Alignment
  section for established patterns, technology decisions and anti-patterns.
- `spec.md` (required), `plan.md` and `tasks.md` where relevant.

Skip sections whose source file is missing or is still a template placeholder, and say so.

### 3. Write the items

Each item is a question about the requirements, tagged with a quality dimension and a traceability
reference.

Dimensions: **Completeness**, **Clarity**, **Consistency**, **Measurability**, **Coverage**.

References: `[Spec §X.Y]`, `[Gap]`, `[Ambiguity]`, `[Conflict]`, `[Assumption]`,
`[Constitution §X]`, `[Registry §X]`.

Patterns that work:

- "Are [requirement type] defined for [scenario]?"
- "Is [vague term] quantified with specific criteria?"
- "Are requirements consistent between [section A] and [section B]?"

Rules: at least 80% of items carry a traceability reference; soft cap of 40 items; merge
near-duplicates; collapse more than five low-impact edge cases into one item. Number from `CHK001`,
globally incrementing. Write to `FEATURE_DIR/checklists/{domain}.md`.

## Review Mode

Triggered by "review", "validate" or "check".

For each unchecked item, judge against the loaded documents:

| Status | Meaning |
| ------ | ------- |
| PASS | Clear evidence in spec or plan satisfies it |
| FAIL | No evidence, or evidence contradicts it |
| PARTIAL | Some evidence, incomplete or ambiguous |

Record the evidence location (`spec.md:L45-52`) and one sentence of justification per item. Evidence
is mandatory - a PASS without a location is not a PASS.

Report: a summary table per checklist, detailed results, failed items with the gap and a concrete
suggestion, and partial items with what is present and what is missing.

Then offer to mark passing items as checked. Only PASS items, only with confirmation, with a
`<!-- Validated: {date} -->` marker.

## Next Steps

| Result | Recommendation |
| ------ | -------------- |
| All PASS | Ready for the next phase |
| Some FAIL | Address them; `requirements-clarification` for gaps |
| Many FAIL | Return to `spec-authoring` - the spec is not ready |
