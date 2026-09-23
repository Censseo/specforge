---
description: Analyze code quality, technical debt, and provide actionable improvement recommendations
skills:
  - adversarial-review
  - finding-verification
  - code-review
  - tech-debt
  - lens-maintainability
  - lens-security
  - lens-performance
  - lens-data
  - lens-testing
semantic_anchors:
  - Code Smell Catalog    # Martin Fowler's refactoring patterns, detection heuristics
  - OWASP Top 10          # Security vulnerability classification
  - Technical Debt Quadrant  # Martin Fowler: Reckless/Prudent × Deliberate/Inadvertent
  - Cyclomatic Complexity # McCabe metric for code complexity
  - SOLID Principles      # Design quality indicators
  - Boy Scout Rule        # Leave code better than you found it
handoffs:
  - label: Deep Fix
    agent: specforge.fix
    prompt: Diagnose root causes and create a comprehensive correction plan
  - label: Implement Fixes
    agent: specforge.implement
    prompt: Execute the correction tasks from review
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

## User Input

```text
$ARGUMENTS
```

Scope: `post` (default), `pre`, `audit`, or a file or directory path.

## Method

Apply the **`adversarial-review`** harness with the code lenses, then **`finding-verification`** before
reporting anything. This command adds the scope detection, the spec-deviation pass and the task
insertion rules.

| Mode | Trigger | Scope |
| ---- | ------- | ----- |
| Post-implementation | default, "post", "after" | Diff against the base branch on a feature branch; otherwise the last 5 commits |
| Pre-implementation | "pre", "before", "planning" | Areas `tasks.md` and `plan.md` say will be affected |
| Full audit | "audit", "full", "all" | The whole codebase, business logic first |
| Focused | a path | That path |

On a feature branch, diff the whole branch against its base - partial diffs miss cross-file regressions.

## Step 1 - Scope and Context

Run `{SCRIPT}` for project context, determine the scope from the table, then read each file in scope:
its role (model, controller, service, util, test) and whether it has tests and documentation.

## Step 2 - Lens Pass

Run, in this order:

1. **`lens-maintainability` Part 1** - fake implementations, stubs, placeholder returns, empty bodies,
   validations that cannot fail, mock data in production code, swallowed errors, hardcoded bypasses.
   These are correctness defects, not style, and they pass superficial review.
2. **`lens-security`** - traced exploit paths only, never generic warnings.
3. **`lens-data`**, **`lens-performance`**, **`lens-testing`** where their risk triggers fired.
4. **`lens-maintainability` Part 2** - smells, duplication, dead code, naming, altitude.

Use the `code-review` and `tech-debt` skills for the detection thresholds and the debt quadrant.

## Step 3 - Spec Deviation Pass

Where `specs/{feature}/` exists, compare the implementation against `spec.md`, `contracts/` and
`data-model.md`.

Per functional requirement: **MATCH** / **DRIFT** (exists but behaves differently - the most dangerous)
/ **MISSING** / **PARTIAL**. Per contract: route exists, request validation matches, response shape
matches, error responses and status codes match. Per entity: fields, constraints, relationships, enum
values.

```markdown
| Source | Item | Spec says | Code does | Status |
| ------ | ---- | --------- | --------- | ------ |
| Contract | `GET /api/users/:id` | 404 if not found | 500 (unhandled null) | DRIFT |
```

## Step 4 - Falsify

Apply `finding-verification` to every candidate. Drop what is refuted. Name the unverified link on
anything reported as plausible.

## Step 5 - Debt Assessment

Categorise: design, code, dead code, fake implementation, spec deviation, test, documentation,
dependency, infrastructure debt.

```text
Debt Score = Severity x Frequency x Effort
Severity: Critical=4 High=3 Medium=2 Low=1
Frequency: Pervasive=3 Common=2 Isolated=1
Effort: Major=3 Moderate=2 Minor=1
```

Prioritise by risk, then impact, then effort, then blocking dependencies.

## Step 6 - Report

Write to `FEATURE_DIR/reviews/` or the project root: executive summary (health score, critical count,
spec compliance %, fake implementations, dead code items, debt score, top three actions), findings by
severity, spec deviation summary, fake implementations, dead code, debt summary, and recommendations
split into quick wins / short-term / long-term.

## Step 7 - Action Items

Generate tagged items - `[DRIFT]`, `[MISSING]`, `[FAKE]`, `[DEAD]`, `[CRITICAL]`, `[HIGH]` - and insert
them into `tasks.md` at the **correct position**, not appended:

1. No tasks complete -> after the first phase header.
2. Some complete -> immediately after the last `[X]`.
3. All complete -> a new "Review & Polish" section.

Continue the existing task numbering. Then amend any pending task the findings affect, and summarise
those amendments in an "Impact on Pending Tasks" table.

## Output

Summary, spec deviations, fake implementations, dead code, diff scope, top five issues, quick wins,
tasks created and amended, report path. Then ask whether to fix, deep-dive, or re-run focused.
