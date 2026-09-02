---
description: Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation.
skills:
  - artifact-analysis
  - lens-requirements
semantic_anchors:
  - Traceability Matrix   # Requirements ↔ Implementation mapping, V-Model
  - Gap Analysis          # Current state vs desired state, coverage assessment
  - Static Analysis       # Code/doc analysis without execution
  - EARS Syntax           # Requirements quality validation
  - Semantic Consistency  # Terminology and concept alignment across artifacts
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

## Method

Apply the **`artifact-analysis`** skill: the semantic models, the six detection passes, the severity
heuristic and the report format.

Read-only. Produce the report, offer a remediation plan, and change nothing without explicit approval.
`/memory/constitution.md` outranks every artifact: a conflict with a MUST is CRITICAL.

## Operational Steps

1. Run `{SCRIPT}` once from the repo root; parse `FEATURE_DIR` and `AVAILABLE_DOCS`. Derive
   `SPEC = FEATURE_DIR/spec.md`, `PLAN = FEATURE_DIR/plan.md`, `TASKS = FEATURE_DIR/tasks.md`.
   Abort with the missing prerequisite command if any is absent. For single quotes use `'I'\''m Groot'`.

2. Load progressively - only the sections the skill lists, never the whole artifacts into the output.

3. Build the requirements inventory, story inventory, task coverage map and constitution rule set.

4. Run detection passes A-F. Cap at 50 findings; summarise the overflow. Use stable ids so a re-run on
   unchanged inputs produces the same report.

5. Emit the report: findings table, coverage summary, constitution alignment issues, unmapped tasks,
   and the metrics block (requirements, tasks, coverage %, ambiguity count, duplication count,
   critical count).

6. Give concrete next actions with commands, not advice. Then ask whether to produce remediation edits.

## Discipline

- Report what is absent as absent; do not infer content that is not written.
- Cite specific instances, never generic patterns.
- No issues found is a legitimate result - publish the coverage statistics that support it.

For a full-feature red-team pass rather than a consistency check, use `/specforge.harness` or
`/specforge.qa`.
