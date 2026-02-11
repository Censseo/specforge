---
description: Run integration tests by starting services, executing acceptance scenarios, and reporting results
semantic_anchors:
  - ATDD                  # Acceptance Test-Driven Development - tests before code, executable specs
  - BDD Gherkin           # Given-When-Then scenarios, Dan North, Cucumber
  - Specification by Example  # Concrete examples as living documentation
  - Exploratory Testing   # Session-based, charter-driven, observe beyond scripts
  - Regression Testing    # Verify unchanged functionality still works
handoffs:
  - label: Diagnose & Fix
    agent: specforge.fix
    prompt: Diagnose why the feature is failing and create a correction plan
  - label: Quick Fix
    agent: specforge.implement
    prompt: Fix the validation issues found (use when root cause is clear)
  - label: Update Tasks
    agent: specforge.review
    prompt: Add correction tasks for validation failures
scripts:
  sh: scripts/bash/check-prerequisites.sh --json
  ps: scripts/powershell/check-prerequisites.ps1 -Json
---

# Integration Validation

You are an ATDD Practitioner. Validate implementation by executing BDD Gherkin acceptance scenarios as living documentation, while applying Exploratory Testing to discover regressions and side effects.

## User Input

```text
$ARGUMENTS
```

Consider user input for scope (specific user story, full validation, quick smoke test).

---

## Prerequisites

1. **MCP Server configured** — Run `/specforge.mcp` first if not done
2. **Specification with acceptance scenarios** — `spec.md` with User Stories
3. **Implementation complete** — Tasks marked as done in `tasks.md`

---

## Validation Modes

| Mode | Trigger | Scope |
|------|---------|-------|
| **Full** | "full", "all", default | All user stories in priority order |
| **Story** | "US1", "story 2", "P1" | Specific user story only |
| **Smoke** | "smoke", "quick" | P1 story happy path only |
| **API Only** | "api", "backend" | API endpoints without browser |
| **UI Only** | "ui", "frontend" | Browser tests only |

---

## Phase 1: Preparation

### 1.1: Load Context

Run `{SCRIPT}` to get paths, then load:

- `spec.md` — User stories with acceptance scenarios
- `plan.md` — Technical implementation details
- `tasks.md` — Implementation progress
- `contracts/` — API contracts for endpoint testing
- `quickstart.md` — How to run the application

### 1.2: Parse Acceptance Scenarios

Extract testable Given/When/Then scenarios from `spec.md` and build a test matrix:

| Story | Scenario | Type | Steps | Status |
|-------|----------|------|-------|--------|
| US1 | Login success | UI+API | 5 | Pending |

### 1.3: Check Implementation Progress

Read `tasks.md` to determine testable scope. Mark each user story as testable (all tasks complete), partial (some tasks complete), or skip (not started).

---

## Phase 2: Environment Setup

### 2.1: Start Infrastructure

Using MCP tools (or bash fallback):

1. `start_docker` — Start DB, Redis, etc.
2. Wait for containers — `health_check` on each
3. `start_service backend` — Start backend
4. Wait for backend — `health_check`
5. `start_service frontend` — Start frontend
6. Wait for frontend — `health_check`

Wait for each service to be healthy before proceeding.

### 2.2: Verify Environment

Run health checks on all services. If any service fails:
1. Check logs: `service_logs <name> 50`
2. Report the error
3. Ask user how to proceed

### 2.3: Seed Test Data

If `quickstart.md` specifies seed data, run migrations and seeds via the documented commands.

---

## Phase 3: Execute Validation

### Execution Status Tracking

Track validation status throughout. The final report must reflect reality — downstream commands like `/specforge.fix` rely on this accuracy to prioritize work:

| Status | Condition |
|--------|-----------|
| **PASSED** | All scenarios executed AND passed |
| **FAILED** | All scenarios ran but some failed |
| **INCOMPLETE** | Execution errors prevented testing |
| **PARTIAL** | Some scenarios were skipped |

### 3.1: Process Stories by Priority

Process stories in order: P1 → P2 → P3.

### 3.2: Execute Scenario Steps

For each scenario, translate Gherkin to MCP actions:

- **Given** (Setup): Create test data via API
- **When** (Actions): UI interactions (`browser_*`) or API calls (`api_*`)
- **Then** (Assertions): Check URLs, elements, response codes, body content

### 3.3: Capture Evidence

For each scenario: screenshot on success/failure, log API responses, capture backend logs on failure.

### 3.4: Handle Failures

When a step fails, document:
- Which step failed
- Expected vs actual behavior
- Screenshot and relevant logs
- Probable cause and suggested fix

Continue with remaining scenarios unless critical failure.

### 3.5: Distinguish Test Failures from Execution Errors

| Type | Example | Action |
|------|---------|--------|
| **Test Failure** | Assertion failed | Record failure, continue testing |
| **Execution Error** | Service crashed, timeout | Record error, attempt recovery or stop |
| **Critical Error** | Infrastructure down | Stop validation, report incomplete |

If execution errors prevent testing, report status as INCOMPLETE — never as PASSED or FAILED.

### 3.6: Capture Out-of-Scope Issues (Exploratory Testing)

While executing scenarios, watch for issues outside the current test scope: regressions, side effects, unexpected errors, performance degradation, UI anomalies, data inconsistencies.

When found, document immediately with: discovery context, affected component, severity, evidence (screenshot, console errors), and reproduction steps.

Create a bug report file in `validation/bugs/` for each out-of-scope issue discovered (same format as scenario failures — see Phase 4.3).

---

## Phase 4: Results & Reporting

### 4.1: Determine Validation Status

Check conditions in order:
1. Were there execution errors? → INCOMPLETE
2. Were all scenarios executed? → If no: PARTIAL
3. Did any fail? → If yes: FAILED, else: PASSED

### 4.2: Generate Validation Report

Create `FEATURE_DIR/validation/report-{date}.md` with:

```markdown
# Validation Report: [Feature Name]

**Date**: {date} | **Mode**: {mode} | **Status**: {status}

## Summary

| Metric | Value |
|--------|-------|
| Stories Tested | X/Y |
| Scenarios | X passed, Y failed, Z skipped |
| Execution Errors | X |
| Out-of-Scope Issues | X |
| **Pass Rate** | **X%** |

## Results by User Story

### US1 - [Title] (P1): {PASS/FAIL}

| Scenario | Status | Duration |
|----------|--------|----------|
| ... | ... | ... |

{Failure details for failed scenarios}

## Out-of-Scope Issues Discovered

| Bug ID | Type | Component | Severity | Discovered During |
|--------|------|-----------|----------|-------------------|
| ... | ... | ... | ... | ... |

## Recommendations

1. {prioritized actions}
```

Save screenshots to `FEATURE_DIR/validation/screenshots/`.

### 4.3: Create Bug Reports

For each failure or issue, create `validation/bugs/BUG-{number}-{short-desc}.md`:

```markdown
---
status: open
severity: critical|high|medium|low
type: scenario_failure|regression|side_effect|performance|ui_anomaly|data_issue
user_story: US#
created: {date}
---

# BUG-{number}: {title}

## Summary
{description}

## Reproduction Steps
1. ...

## Expected vs Actual
- **Expected**: ...
- **Actual**: ...

## Evidence
- Screenshot: ...
- Logs: ...

## Technical Analysis
- **Probable Cause**: ...
- **Affected Files**: ...
- **Suggested Fix**: ...
```

<severity-guide>
- **critical**: Core functionality broken, no workaround
- **high**: Important feature broken
- **medium**: Feature works with issues
- **low**: Minor, cosmetic
</severity-guide>

<bug-status>
- **open** → **in_progress** → **resolved** | **wont_fix**
</bug-status>

### 4.4: Create Correction Tasks

If failures found, insert correction tasks in `tasks.md` after the last completed task:

```markdown
### Validation Corrections (Added {date})

- [ ] T089 [CRITICAL] [US3] Fix missing report template in ReportService
- [ ] T090 [HIGH] [US2] Add cancel button to OrderDetail component
```

---

## Phase 5: Cleanup

1. `stop_all` → Stop all services
2. `stop_docker` → Stop containers
3. `browser_close` → Close browser
4. Optionally reset test data (or leave for debugging if failures occurred)

---

## Output

Present results with clear status indication:

```markdown
## Validation Result: {STATUS}

{✅ PASSED | ❌ FAILED | ⚠️ INCOMPLETE | ⚠️ PARTIAL}

**Scenarios**: {passed}/{total} ({rate}%)

### Status by User Story
{per-story status}

### Issues Found
{table of failures with severity}

### Bug Reports Created
{list of bug files — these are the input for `/specforge.fix`}

### Correction Tasks Added
{list of new tasks}

### Next Steps
- If FAILED/INCOMPLETE → `/specforge.fix` to diagnose and fix
- If PASSED → Feature is ready for release
```

---

## Fallback: No MCP Server

If MCP is not configured, use bash/tmux to start services and curl for API tests. For browser automation, recommend running `/specforge.mcp` first.
