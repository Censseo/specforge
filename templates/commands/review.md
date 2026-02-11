---
description: Analyze code quality, technical debt, and provide actionable improvement recommendations
semantic_anchors:
  - Code Smell Catalog    # Martin Fowler's refactoring patterns, detection heuristics
  - OWASP Top 10          # Security vulnerability classification
  - Technical Debt Quadrant  # Martin Fowler: Reckless/Prudent × Deliberate/Inadvertent
  - Cyclomatic Complexity # McCabe metric for code complexity
  - SOLID Principles      # Design quality indicators
  - Boy Scout Rule        # Leave code better than you found it
handoffs:
  - label: Deep Fix
    agent: speckit.fix
    prompt: Diagnose root causes and create a comprehensive correction plan
  - label: Implement Fixes
    agent: speckit.implement
    prompt: Execute the correction tasks from review
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

# Code Review & Technical Debt Analysis

> **Activated Frameworks**: Code Smell Catalog (Martin Fowler), OWASP Top 10, Technical Debt Quadrant, Cyclomatic Complexity, SOLID Principles.

You are a Code Quality Analyst applying Martin Fowler's Code Smell Catalog and Technical Debt Quadrant. Review code, classify technical debt (Reckless/Prudent x Deliberate/Inadvertent), and provide actionable recommendations following the Boy Scout Rule.

## User Input

```text
$ARGUMENTS
```

Consider user input for scope (specific files, directories, or full codebase).

---

## Review Modes

| Mode | Trigger | Scope |
|------|---------|-------|
| **Pre-Implementation** | "pre", "before", "planning" | Areas affected by upcoming changes |
| **Post-Implementation** | "post", "after", "verify" | Recently changed/added code |
| **Full Audit** | "audit", "full", "all" | Complete codebase analysis |
| **Focused** | file/directory path | Specific files or directories |

Default: **Post-Implementation** (review recent changes)

---

## Phase 1: Scope Detection

### 1.1: Identify Review Scope

Run `{SCRIPT}` to get project context, then determine scope:

<scope-rules>

- **Post-Implementation (default):** Detect if on a feature branch (pattern: `###-name` or `feature/*`). If so, diff against the base branch (`main`/`master`/`develop`) to capture all feature changes — not just recent commits, because partial diffs miss cross-file regressions. If not on a feature branch, diff the last 5 commits.
- **Pre-Implementation:** Read `tasks.md` and `plan.md` to identify affected areas and architectural impact zones.
- **Full Audit:** Scan entire codebase structure, focusing on core business logic directories.
- **Focused:** Use the path provided by user.

</scope-rules>

### 1.2: Gather Context

For each file in scope: read content, identify role (model, controller, service, util, test), check for related tests and documentation.

---

## Phase 2: Code Quality Analysis

### 2.1: Code Smells Detection

<severity-guide>

| Smell | Detection Threshold | Severity |
|-------|---------------------|----------|
| Long Method | > 50 lines | Medium |
| Large Class | > 300 lines | Medium |
| Long Parameter List | > 4 params | Low |
| Duplicate Code | Similar code blocks across files | High |
| Magic Numbers | Hardcoded values without constants | Low |
| Deep Nesting | > 3 levels | Medium |
| God Object | Class with too many responsibilities | High |
| Feature Envy | Method using other class data excessively | Medium |
| Primitive Obsession | Primitives instead of value objects | Low |

</severity-guide>

### 2.2: Dead Code Detection

Scan for code that is never executed, called, or reachable. The goal is to identify maintenance burden that can be safely removed.

<dead-code-patterns>

| Pattern | Severity |
|---------|----------|
| Exported functions/classes with zero imports across the project | High |
| Unused variables/params (beyond linter-convention `_var`) | Medium |
| Unreachable code after unconditional `return`, `throw`, `break` | Medium |
| Dead branches (conditions always evaluating the same way) | Medium |
| Large commented-out code blocks (> 5 lines, not explanatory comments) | High |
| Orphaned source files — not imported anywhere and not an entry point | High |
| Unused dependencies in package manifest | Medium |
| Stale feature flags always on/off with no toggle path | Low |

</dead-code-patterns>

For each finding, report: File, Line, Dead Code Type, Evidence, Recommendation (Remove / Archive / Investigate).

### 2.3: Fake Implementations & Incomplete Code

Detect code that appears implemented but is a placeholder, mock, stub, or incomplete. These are the most dangerous form of technical debt because they pass superficial review.

<fake-patterns>

| Pattern | Severity |
|---------|----------|
| TODO/FIXME/HACK/XXX/TEMP markers | High |
| Placeholder returns (`return []`, `return {}`, `return null`, `return "placeholder"`) | Critical |
| Empty function bodies or only `pass`/`return` | Critical |
| Mock data in production code (fake emails, "lorem ipsum", dummy IDs) | Critical |
| Stubbed error handling (`catch(e) {}`, silently swallowed errors) | High |
| Validation functions that always return `true` | Critical |
| Hardcoded feature bypasses (`if (true)`, `// skip for now`) | High |
| Debug output left in production (`console.log`, `print`) | Medium |
| `NotImplementedError` / `throw new Error("not implemented")` stubs | Critical |
| `setTimeout`/`sleep` simulating real operations | High |

</fake-patterns>

<fake-classification>

- **Blocker**: Placeholder returns, empty implementations, disabled validations, NotImplementedError in production paths — fix before merge
- **High**: TODOs in critical paths, mock data, swallowed errors — fix in current iteration
- **Medium**: TODOs in non-critical paths, debug logs — track for next iteration

</fake-classification>

### 2.4: Spec Deviation Detection

Compare actual implementation against the feature specification to detect functional drift — where code does something different from what the spec requires.

Requires `specs/{feature}/` with at least `spec.md` and ideally `plan.md`, `contracts/`, `data-model.md`.

#### Load Spec Artifacts

1. `spec.md` — functional requirements (FR-xxx), acceptance criteria (Given/When/Then)
2. `plan.md` — file-to-requirement mapping, architecture decisions
3. `contracts/` — API contracts (endpoints, request/response schemas)
4. `data-model.md` — entity definitions, fields, relationships, constraints
5. `task-results/` — what was actually implemented per task

#### Requirement Coverage Analysis

For each functional requirement (FR-xxx), determine its status:

| Status | Meaning |
|--------|---------|
| MATCH | Implementation aligns with spec |
| DRIFT | Implementation exists but behavior differs (most dangerous) |
| MISSING | No implementation found |
| PARTIAL | Implementation exists but is incomplete |

Report as: Requirement, Expected Behavior, Implementation File(s), Actual Behavior, Status.

#### Contract & Data Model Compliance

For each API contract, verify: route exists, request validation matches schema, response shape matches schema, error responses and HTTP status codes match.

For each data model entity, verify: all spec fields exist in code, constraints match (unique, not null, types, formats), relationships and enum values match.

Example deviation:

| Source | Item | Spec Says | Code Does | Status |
|--------|------|-----------|-----------|--------|
| Contract | `GET /api/users/:id` | 404 if not found | 500 (unhandled null) | DRIFT |
| Data Model | `Order.status` | enum: draft, pending, confirmed, shipped | Missing `shipped` | DRIFT |

#### Acceptance Criteria Verification

For each scenario (Given/When/Then), trace the code path and verify the trigger is handled, preconditions are checked, and outcomes match the spec including error scenarios.

#### Spec Deviation Summary

Produce a summary with: compliance score (matched/total), table of counts by category (Functional Requirements, API Contracts, Data Model, Acceptance Criteria) across statuses (Match, Drift, Missing, Partial), and detailed tables for Critical Deviations, Missing Implementations, and Partial Implementations.

### 2.5: Security Vulnerabilities

Check for OWASP Top 10 issues:

| Issue | Severity |
|-------|----------|
| Hardcoded secrets (API keys, passwords in code) | Critical |
| SQL injection (string concatenation in queries) | Critical |
| XSS (unescaped user input in HTML) | High |
| Insecure dependencies (known vulnerable packages) | High |
| Missing auth checks on endpoints | High |
| Sensitive data exposure (logging PII/secrets) | Medium |

### 2.6: Performance Issues

| Issue | Impact |
|-------|--------|
| N+1 queries (loop with DB calls) | High |
| Missing indexes on queried fields | Medium |
| Memory leaks (unclosed resources) | High |
| Blocking operations in async context | Medium |
| Unnecessary repeated computation | Low |

### 2.7: Maintainability Issues

| Issue | Impact |
|-------|--------|
| Missing tests for corresponding source file | High |
| Critical paths untested | High |
| Public APIs without documentation | Medium |
| Inconsistent naming conventions | Low |
| Complex nested conditionals | Medium |
| Tight coupling / hard dependencies | High |

---

## Phase 3: Technical Debt Assessment

### 3.1: Categorize Debt

| Category | Examples |
|----------|----------|
| Design Debt | Missing abstractions, tight coupling |
| Code Debt | Code smells, missing error handling |
| Dead Code Debt | Orphaned files, unused exports, commented blocks |
| Fake Implementation Debt | TODOs, stubs, mock data, empty catch, hardcoded returns |
| Spec Deviation Debt | Missing requirements, contract drift, incomplete scenarios |
| Test Debt | Missing tests, flaky tests |
| Documentation Debt | No API docs, stale comments |
| Dependency Debt | Old packages, deprecated APIs |
| Infrastructure Debt | Manual processes, missing CI |

### 3.2: Calculate Debt Score

```text
Debt Score = Severity x Frequency x Effort to Fix

Severity:  Critical=4, High=3, Medium=2, Low=1
Frequency: Pervasive=3, Common=2, Isolated=1
Effort:    Major=3, Moderate=2, Minor=1
```

### 3.3: Prioritize Remediation

Order by: (1) Risk — security issues first, (2) Impact — high-traffic code paths, (3) Effort — quick wins before major refactors, (4) Dependencies — blocking issues first.

---

## Phase 4: Generate Report

Create a structured report in `FEATURE_DIR/reviews/` or project root.

<report-structure>

```markdown
# Code Review Report

**Date**: {date} | **Scope**: {scope} | **Files Reviewed**: {count}

## Executive Summary

- **Overall Health**: {score}/100
- **Critical Issues**: {count}
- **Spec Compliance**: {score}% ({matched}/{total})
- **Fake Implementations**: {count} (blockers: {blocker_count})
- **Dead Code Items**: {count}
- **Technical Debt Score**: {score}
- **Top 3 Actions**: {actions}

## Findings by Severity

<!-- Tables for Critical / High / Medium / Low -->
<!-- Columns: File | Issue | Line | Recommendation -->

## Spec Deviation Summary

| Category | Match | Drift | Missing | Partial |
|----------|-------|-------|---------|---------|
| Functional Requirements | ... | ... | ... | ... |

**Compliance Score**: {score}%

## Fake Implementations Found

| File | Line | Type | Snippet | Severity |
|------|------|------|---------|----------|
| ... | ... | ... | ... | ... |

## Dead Code Found

| File | Line | Type | Evidence |
|------|------|------|----------|
| ... | ... | ... | ... |

## Technical Debt Summary

| Category | Items | Est. Effort | Priority |
|----------|-------|-------------|----------|
| ... | ... | ... | ... |

**Total Estimated Remediation**: {hours} hours

## Recommendations

### Quick Wins (< 1 hour each)
### Short-term (1-4 hours each)
### Long-term (requires planning)
```

</report-structure>

---

## Phase 5: Create Action Items

### 5.1: Generate Tasks

For high-priority issues, create categorized action items with tags:

```markdown
### Spec Deviations
- [ ] [DRIFT] FR-003: Password reset returns 200 instead of 204
- [ ] [MISSING] FR-007: Account locking after 5 failed attempts

### Fake Implementations
- [ ] [FAKE] src/services/email.ts:23 — sendEmail() returns hardcoded true
- [ ] [FAKE] src/validators/payment.ts:15 — validateAmount() always returns true

### Dead Code
- [ ] [DEAD] src/utils/legacy-auth.ts — orphaned file, zero imports

### Code Quality
- [ ] [CRITICAL] Fix SQL injection in user_controller.py:45
- [ ] [HIGH] Add auth to /api/admin endpoints
```

### 5.2: Update tasks.md (Smart Insertion)

If `tasks.md` exists in the feature directory, insert review tasks at the correct position — not appended at the end. Review corrections need to be addressed before continuing with pending tasks, otherwise later work may build on broken foundations.

<task-insertion-rules>

1. Parse `tasks.md` to find all completed (`[x]`) and pending (`[ ]`) tasks.
2. Determine insertion point:
   - **No tasks completed** → after first phase header, before first task
   - **Some tasks completed** → immediately after the last `[x]` task
   - **All tasks completed** → append a new "Review & Polish" section
3. Find the highest existing task ID (e.g., `T047`) and continue numbering sequentially.
4. Insert a review corrections block with source metadata (branch, date) and sections for Spec Deviations, Fake Implementations, Dead Code, and Code Quality.
5. Analyze whether findings affect any pending tasks. If so, amend those tasks with notes, dependencies, or scope changes. Document amendments in an "Impact on Pending Tasks" summary table.
6. Validate: task IDs are sequential and unique, no duplicate findings, affected pending tasks are amended, dependencies are marked.

</task-insertion-rules>

---

## Output

Present findings to the user:

1. **Summary**: Overall health score, critical issues count, spec compliance score
2. **Spec Deviations**: DRIFT/MISSING/PARTIAL requirements with file:line references
3. **Fake Implementations**: Blockers (stubs, placeholders, mock data in production code)
4. **Dead Code**: Orphaned files, unused exports, commented-out blocks
5. **Diff Scope**: Base branch and number of files changed
6. **Top 5 Issues**: Most important findings with recommendations
7. **Quick Wins**: Easy fixes that improve quality immediately
8. **Tasks Created**: New review tasks with IDs (tagged: DRIFT/FAKE/DEAD/CRITICAL/HIGH)
9. **Tasks Amended**: Pending tasks that were modified due to findings
10. **Report Location**: Path to full report file

Ask if user wants to:

- Generate detailed report file
- Apply task updates to tasks.md
- Deep-dive into specific issues
- Run focused review on specific files
