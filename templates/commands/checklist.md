---
description: Generate or review checklists for the current feature.
skills:
  - quality-checklists
  - lens-requirements
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

## User Input

```text
$ARGUMENTS
```

| Mode | Trigger | Result |
| ---- | ------- | ------ |
| Generate | default, or a domain (`ux`, `api`, `security`) | A new checklist file |
| Review | `review`, `validate`, `check` | Validation of existing checklists against spec and plan |

Examples: `/specforge.checklist`, `/specforge.checklist ux`, `/specforge.checklist review`,
`/specforge.checklist review constitution`.

## Method

Apply the **`quality-checklists`** skill. Checklists are unit tests for requirements: they test what is
written, never whether the system behaves. If an item could be executed against a running system, it
belongs in a test, not here.

## Operational Steps - Generate

1. Run `{SCRIPT}` from the repo root; parse `FEATURE_DIR` and `AVAILABLE_DOCS`. Absolute paths.
   For single quotes use `'I'\''m Groot'`.

2. Derive up to three clarifying questions per the skill's algorithm - only where the answer changes
   the checklist's content. Never exceed five in total.

3. Load `/memory/constitution.md` (generates the Constitution Compliance section) and
   `/memory/architecture-registry.md` (generates Architecture Alignment, only when `plan.md` exists).
   Skip sections whose source is missing or still a placeholder, and say so.

4. Load `spec.md` (required), plus `plan.md` and `tasks.md` where relevant to the focus areas.

5. Write `FEATURE_DIR/checklists/{domain}.md` following `templates/checklist-template.md`. Number from
   `CHK001`, globally incrementing. Each run creates a new file; append if the name already exists.

6. Apply the skill's item rules: quality dimension in brackets, traceability reference on at least 80%
   of items, soft cap of 40 items, near-duplicates merged.

## Operational Steps - Review

1. Run `{SCRIPT}`; parse `FEATURE_DIR`.

2. Scan `FEATURE_DIR/checklists/` for `.md` files, or load only the one named. If none exist, stop:
   "No checklists found. Run `/specforge.checklist` first."

3. Load `spec.md` (required) and `plan.md`. Load `/memory/constitution.md` and
   `/memory/architecture-registry.md` when the checklist carries `[Constitution]` or `[Registry]` markers.

4. Judge each unchecked item PASS / FAIL / PARTIAL with an evidence location (`spec.md:L45-52`) and one
   sentence of justification. A PASS without a location is not a PASS.

5. Emit the validation report: summary table per checklist, detailed results, failed items with the gap
   and a concrete suggestion, partial items with what is present and what is missing.

6. Offer to mark passing items as checked. Only PASS items, only with confirmation, with a
   `<!-- Validated: {date} -->` marker.

## Non-Interactive Mode

When the input says non-interactive (as `/specforge.design` does):

- Skip the clarifying questions; use your own recommended answer for each and note it in the
  checklist header.
- `pre-implementation, for all domains, ... single consolidated file` means one file covering every
  applicable domain (constitution compliance, architecture alignment, requirements, security, data,
  UX, operations as relevant), not one file per domain.
- In review mode, `propose and apply remediation` means: for each FAIL or PARTIAL item, fix the
  **spec or plan** so the item passes, then re-evaluate it. Remediation edits the artifact - never the
  checklist item, and never the checkbox on an item that still fails.
- Report which items were remediated and which remain FAIL. CRITICAL items still failing stop the
  caller's pipeline.

## Next Steps

| Result | Recommendation |
| ------ | -------------- |
| All PASS | Proceed to `/specforge.implement` or `/specforge.build` |
| Some FAIL | Address them; `/specforge.clarify` for the gaps |
| Many FAIL | Return to `/specforge.specify` - the spec is not ready |
