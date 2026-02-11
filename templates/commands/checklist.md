---
description: Generate or review checklists for the current feature.
semantic_anchors:
  - Definition of Ready      # Criteria for starting work, Scrum artifact
  - Definition of Done       # Completion criteria, quality gates
  - INVEST Criteria          # Story quality validation
  - Acceptance Criteria      # Testable conditions for requirements
  - Quality Gates            # Stage-gate process checkpoints
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## Command Modes

| Mode         | Trigger                                              | Description                                      |
|--------------|------------------------------------------------------|--------------------------------------------------|
| **Generate** | Default, or explicit domain (e.g., `ux`, `security`) | Creates a new checklist file                     |
| **Review**   | `review`, `validate`, `check`                        | Validates existing checklists against spec/plan  |

**Examples:**

- `/specforge.checklist` → Generate mode (asks clarifying questions)
- `/specforge.checklist ux` → Generate UX checklist
- `/specforge.checklist review` → Review all existing checklists
- `/specforge.checklist review constitution` → Review only constitution.md checklist

---

## Core Concept: Unit Tests for Requirements

<purpose>
Checklists are unit tests for requirements writing. They validate the quality, clarity, and completeness of requirements in a given domain — not whether the implementation works.

If your spec is code written in English, the checklist is its unit test suite. You are testing whether the requirements are well-written, complete, unambiguous, and ready for implementation.
</purpose>

**Correct** (testing requirements quality):

- "Are visual hierarchy requirements defined for all card types?" [Completeness]
- "Is 'prominent display' quantified with specific sizing/positioning?" [Clarity]
- "Are accessibility requirements defined for keyboard navigation?" [Coverage]

**Wrong** (testing implementation):

- "Verify the button clicks correctly"
- "Test error handling works"
- "Confirm the API returns 200"

## User Input

```text
$ARGUMENTS
```

Consider the user input before proceeding (if not empty).

## Execution Steps

### 1. Setup

Run `{SCRIPT}` from repo root and parse JSON for FEATURE_DIR and AVAILABLE_DOCS list. All file paths must be absolute. For single quotes in args, use escape syntax: `'I'\''m Groot'` or double-quote: `"I'm Groot"`.

### 2. Clarify Intent

Derive up to three contextual clarifying questions. They should be generated from the user's phrasing combined with signals from spec/plan/tasks, ask only about information that materially changes checklist content, and be skipped if already unambiguous in `$ARGUMENTS`.

<algorithm>
1. Extract signals: feature domain keywords, risk indicators, stakeholder hints, explicit deliverables.
2. Cluster into candidate focus areas (max 4) ranked by relevance.
3. Identify probable audience and timing (author, reviewer, QA, release) if not explicit.
4. Detect missing dimensions: scope breadth, depth/rigor, risk emphasis, exclusion boundaries.
5. Formulate questions from these archetypes:
   - Scope refinement — "Should this include integration touchpoints with X and Y or stay limited to local module correctness?"
   - Risk prioritization — "Which risk areas should receive mandatory gating checks?"
   - Depth calibration — "Is this a lightweight pre-commit sanity list or a formal release gate?"
   - Audience framing — "Will this be used by the author only or peers during PR review?"
   - Boundary exclusion — "Should we explicitly exclude performance tuning items this round?"
   - Scenario class gap — "No recovery flows detected — are rollback / partial failure paths in scope?"
</algorithm>

**Question formatting**: If presenting options, use a compact table (Option | Candidate | Why It Matters), limit to A-E options, omit table if free-form is clearer.

**Defaults** (when interaction impossible): Depth: Standard; Audience: Reviewer (PR) if code-related, Author otherwise; Focus: Top 2 relevance clusters.

Output questions as Q1/Q2/Q3. After answers: if two or more scenario classes remain unclear, ask up to two follow-ups (Q4/Q5) with a one-line justification each. Do not exceed five total questions.

### 3. Understand User Request

Combine `$ARGUMENTS` + clarifying answers: derive checklist theme, consolidate explicit must-have items, map focus selections to category scaffolding, infer missing context from spec/plan/tasks without hallucinating.

### 4. Load Project References

Read from `/memory/` directory:

- **Constitution** (`/memory/constitution.md`): Extract "Specification Principles" — generate checklist items for each principle.
- **Architecture Registry** (`/memory/architecture-registry.md`): Extract "Established Patterns", "Technology Decisions", and "Anti-Patterns" — generate alignment items (only if plan.md exists).

If files don't exist or contain only template placeholders: skip automatic generation, notify user.

### 5. Load Feature Context

Read from FEATURE_DIR: `spec.md` (required), `plan.md` and `tasks.md` (if they exist). Load only portions relevant to active focus areas. Prefer summarizing long sections into concise requirement bullets; use progressive disclosure if gaps are detected.

### 6. Generate Checklist

Create `FEATURE_DIR/checklists/` directory if needed. Generate a checklist file with a short descriptive name based on domain (e.g., `ux.md`, `api.md`, `security.md`). Each run creates a new file; if the file already exists, append to it. Number items sequentially from CHK001.

<constitution-items>
Auto-generate from `/memory/constitution.md` for each defined principle:

```markdown
## Constitution Compliance

### Accessibility [Constitution §Accessibility]
- [ ] CHK001 - Are accessibility requirements defined per constitution? [Constitution]
- [ ] CHK002 - Are WCAG compliance levels specified? [Constitution §Accessibility]

### Performance [Constitution §Performance]
- [ ] CHK003 - Are performance thresholds quantified per constitution? [Constitution]
- [ ] CHK004 - Do response time requirements meet constitution minimums? [Constitution §Performance]
```

</constitution-items>

<registry-items>
Auto-generate from `/memory/architecture-registry.md` (only if plan.md exists):

```markdown
## Architecture Alignment

- [ ] CHK009 - Does the plan use established patterns from registry? [Registry §Patterns]
- [ ] CHK010 - Are technology decisions aligned with registry? [Registry §Technology]
- [ ] CHK011 - Are any anti-patterns from registry present in the plan? [Registry §Anti-Patterns]
```

</registry-items>

Skip sections where constitution/registry placeholders are not filled.

<writing-checklist-items>
Every checklist item evaluates the requirements themselves across these dimensions:

- **Completeness** — Are all necessary requirements present?
- **Clarity** — Are requirements unambiguous and specific?
- **Consistency** — Do requirements align with each other?
- **Measurability** — Can requirements be objectively verified?
- **Coverage** — Are all scenarios and edge cases addressed?

**Item structure**: Question format asking about requirement quality, focused on what is written (or missing) in the spec/plan. Include quality dimension in brackets and reference spec section `[Spec §X.Y]` or use gap markers `[Gap]`, `[Ambiguity]`, `[Conflict]`, `[Assumption]`.

Correct patterns:

- "Are [requirement type] defined/specified/documented for [scenario]?"
- "Is [vague term] quantified/clarified with specific criteria?"
- "Are requirements consistent between [section A] and [section B]?"

Wrong patterns (these describe implementation testing, not requirements testing):

- "Verify landing page displays 3 episode cards"
- "Test hover states work correctly on desktop"
- "Check that related episodes section shows 3-5 items"

The distinction: wrong items test whether the system behaves correctly; correct items test whether the requirements are written correctly.

**Traceability**: At least 80% of items should include a traceability reference (`[Spec §X.Y]`, `[Gap]`, `[Ambiguity]`, `[Conflict]`, `[Assumption]`).

**Consolidation**: Soft cap of 40 items. Merge near-duplicates. If more than 5 low-impact edge cases, combine into one item.
</writing-checklist-items>

### 7. Structure Reference

Follow the canonical template in `templates/checklist-template.md` for title, meta section, category headings, and ID formatting. If template is unavailable, use: H1 title, purpose/created meta lines, `##` category sections containing `- [ ] CHK### <requirement item>` lines with globally incrementing IDs starting at CHK001.

### 8. Report

Output full path to created checklist, item count, and remind user that each run creates a new file. Summarize: focus areas selected, depth level, actor/timing, and any explicit user-specified must-have items incorporated.

## Example Checklist Types

**UX Requirements Quality:** `ux.md`

- "Are visual hierarchy requirements defined with measurable criteria? [Clarity, Spec §FR-1]"
- "Is the number and positioning of UI elements explicitly specified? [Completeness, Spec §FR-1]"
- "Are interaction state requirements (hover, focus, active) consistently defined? [Consistency]"
- "Are accessibility requirements specified for all interactive elements? [Coverage, Gap]"
- "Is fallback behavior defined when images fail to load? [Edge Case, Gap]"
- "Can 'prominent display' be objectively measured? [Measurability, Spec §FR-4]"

**API Requirements Quality:** `api.md`

- "Are error response formats specified for all failure scenarios? [Completeness]"
- "Are rate limiting requirements quantified with specific thresholds? [Clarity]"
- "Are authentication requirements consistent across all endpoints? [Consistency]"
- "Are retry/timeout requirements defined for external dependencies? [Coverage, Gap]"
- "Is versioning strategy documented in requirements? [Gap]"

---

## Review Mode Execution

When `$ARGUMENTS` contains "review", "validate", or "check", execute this flow instead of generation.

### 1. Setup

Run `{SCRIPT}` from repo root and parse JSON for FEATURE_DIR.

### 2. Load Checklists

Scan `FEATURE_DIR/checklists/` for all `.md` files. If a specific checklist is named (e.g., `review constitution`), load only that file. If no checklists exist, abort with: "No checklists found. Run `/specforge.checklist` first to generate."

### 3. Load Feature Context

Read from FEATURE_DIR: `spec.md` (required), `plan.md` (if exists). Also load `/memory/constitution.md` and `/memory/architecture-registry.md` if the checklist contains `[Constitution]` or `[Registry]` markers.

### 4. Validate Each Item

For each unchecked item (`- [ ]`), analyze against loaded documents:

| Status  | Meaning                                                          |
|---------|------------------------------------------------------------------|
| PASS    | Clear evidence found in spec/plan that satisfies the requirement |
| FAIL    | No evidence found, or evidence contradicts the requirement       |
| PARTIAL | Some evidence exists but incomplete or ambiguous                 |

For each item, record: status, evidence location (e.g., "spec.md:L45-52"), and a one-sentence justification.

### 5. Generate Validation Report

Output a Markdown report (do not write to file):

```markdown
## Checklist Validation Report

**Feature**: [FEATURE_NAME]
**Date**: [DATE]
**Checklists Reviewed**: [LIST]

### Summary

| Checklist | Total | Pass | Fail | Partial | Already Checked |
|-----------|-------|------|------|---------|-----------------|
| constitution.md | 8 | 5 | 2 | 1 | 0 |
| ux.md | 12 | 8 | 3 | 1 | 0 |

**Overall**: 13/20 items pass (65%)

### Detailed Results

#### constitution.md

| ID | Item | Status | Evidence |
|----|------|--------|----------|
| CHK001 | Are accessibility requirements defined? | PASS | spec.md:L45 defines WCAG 2.1 AA |
| CHK002 | Are performance thresholds quantified? | FAIL | No performance metrics found |

### Failed Items (Action Required)

1. **CHK002** - Are performance thresholds quantified?
   - **Gap**: spec.md has no performance section
   - **Suggestion**: Add NFR section with response time targets

### Partial Items (Review Recommended)

1. **CHK003** - Is sensitive data handling specified?
   - **Found**: Authentication flow mentions password hashing
   - **Missing**: No data classification or retention policy
```

### 6. Offer Auto-Check

Ask: "Would you like me to mark the {N} passing items as checked in the checklist files?"

If confirmed: update each checklist file changing `- [ ]` to `- [x]` for PASS items only, add validation timestamp `<!-- Validated: {DATE} -->`, report files updated.

If declined: no changes made.

### 7. Suggest Next Steps

- **All PASS**: "All checklist items validated. Ready for `/specforge.implement`."
- **Some FAIL**: "Address {N} failed items before implementation. Consider `/specforge.clarify` to resolve gaps."
- **Many FAIL**: "Significant gaps detected. Consider revisiting `/specforge.specify` to improve spec completeness."
