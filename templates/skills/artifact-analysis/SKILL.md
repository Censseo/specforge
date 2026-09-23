---
name: artifact-analysis
description: |
  Read-only cross-artifact consistency and coverage analysis across spec, plan and tasks - duplication,
  ambiguity, underspecification, constitution conflicts, coverage gaps and terminology drift.
  Activate when: checking that artifacts agree, before implementing, or during the QA gate.
triggers: ["analyze artifacts", "consistency check", "coverage analysis", "do spec and tasks agree", "traceability", "gap analysis"]
semantic_anchors: [Traceability Matrix, Gap Analysis, Static Analysis, EARS Syntax, Semantic Consistency]
phase: qa
---

# Cross-Artifact Analysis

> Read-only. Produce the report, propose remediation, change nothing without explicit approval.

Run after `tasks.md` exists. `/memory/constitution.md` outranks every artifact: a conflict with a MUST
is CRITICAL, always.

## Step 1 - Load, Progressively

| Artifact | Extract |
| -------- | ------- |
| `spec.md` | Overview, functional and non-functional requirements, user stories, edge cases |
| `plan.md` | Architecture and stack choices, data model references, phases, constraints |
| `tasks.md` | Task ids, descriptions, phase grouping, `[P]` markers, referenced paths |
| `/memory/constitution.md` | Principle names and MUST/SHOULD statements |

Do not dump raw artifacts into the output.

## Step 2 - Build Semantic Models

- **Requirements inventory**: each requirement with a stable slug key ("User can upload file" ->
  `user-can-upload-file`).
- **Story and action inventory**: discrete user actions with their acceptance criteria.
- **Task coverage map**: each task to the requirements it serves, by explicit reference or key phrase.
- **Constitution rule set**: the normative statements, as rules.

## Step 3 - Detection Passes

| Pass | Looks for |
| ---- | --------- |
| A. Duplication | Near-duplicate requirements; mark the weaker phrasing for consolidation |
| B. Ambiguity | Vague adjectives without criteria; unresolved placeholders (TODO, TKTK, `???`) |
| C. Underspecification | Requirements with a verb but no measurable object; stories without acceptance criteria; tasks referencing undefined components |
| D. Constitution alignment | Anything conflicting with a MUST; missing mandated sections or gates |
| E. Coverage gaps | Requirements with zero tasks; tasks with no requirement; NFRs absent from tasks |
| F. Inconsistency | Terminology drift; entities in the plan but not the spec; ordering contradictions; conflicting technology choices |

Cap at 50 findings; aggregate the remainder in an overflow summary. Stable ids prefixed by category
initial, so a re-run on unchanged inputs produces the same report.

## Step 4 - Severity

| Severity | Criterion |
| -------- | --------- |
| CRITICAL | Violates a constitution MUST; a core artifact is missing; a baseline requirement has zero coverage |
| HIGH | Duplicate or conflicting requirements; ambiguous security or performance attribute; untestable acceptance criterion |
| MEDIUM | Terminology drift; NFR without task coverage; underspecified edge case |
| LOW | Wording, redundancy that does not affect execution |

## Step 5 - Report

```markdown
## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
| -- | -------- | -------- | ----------- | ------- | -------------- |

### Coverage Summary

| Requirement key | Has task? | Task ids | Notes |
| --------------- | --------- | -------- | ----- |

### Constitution Alignment Issues
### Unmapped Tasks

### Metrics
- Total requirements / Total tasks / Coverage % / Ambiguity count / Duplication count / Critical count
```

## Step 6 - Next Actions

- Critical issues present: resolve before implementing.
- Only low and medium: may proceed, with the improvements listed.
- Give concrete commands, not advice ("add coverage for `performance-metrics` in tasks.md").

Then ask whether to produce remediation edits. Do not apply them unprompted.

## Discipline

- Report what is absent as absent. Do not infer content that is not written.
- Cite specific instances, never generic patterns.
- No issues found is a legitimate result - publish the coverage statistics that support it.
