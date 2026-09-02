---
name: integration-validation
description: |
  Execute acceptance scenarios against the running system, capture evidence, and report status
  honestly - including when tests could not run. Uses ATDD, BDD Gherkin, exploratory and regression
  testing. Activate when: validating a feature, running acceptance tests, or verifying a fix in situ.
triggers: ["validate the feature", "run acceptance tests", "integration validation", "does it actually work", "end to end test", "verify implementation"]
semantic_anchors: [ATDD, BDD Gherkin, Specification by Example, Exploratory Testing, Regression Testing]
phase: qa
---

# Integration Validation

> The report must reflect reality. Everything downstream - triage, fixes, the release decision -
> is built on it.

## Modes

| Mode | Trigger | Scope |
| ---- | ------- | ----- |
| Full | default | All user stories, priority order |
| Story | "US1", "P1" | One story |
| Smoke | "smoke", "quick" | P1 happy path only |
| API only | "api", "backend" | Endpoints, no browser |
| UI only | "ui", "frontend" | Browser only |

## Phase 1 - Prepare

Load `spec.md` (scenarios), `plan.md`, `tasks.md` (what is actually finished), `contracts/`,
`quickstart.md` (how to run it).

Build the test matrix and mark each story **testable** (all tasks done), **partial** or **skip**.
Testing a story whose tasks are unfinished produces failures that mean nothing.

## Phase 2 - Environment

Start infrastructure, then services, health-checking each before the next. If a service fails: read
its logs, report the error, ask how to proceed. Seed data per `quickstart.md`.

An environment that will not start is an `INCOMPLETE` result, never a `FAILED` one - the difference
matters to whoever reads the report.

## Phase 3 - Execute

Translate each Gherkin scenario:

| Clause | Action |
| ------ | ------ |
| Given | Establish the precondition, usually via API |
| When | Perform the action - UI interaction or API call |
| Then | Assert the observable outcome: status, body, URL, rendered element, stored state |

Capture evidence for every scenario: screenshot, response body, and service logs on failure.

Distinguish rigorously:

| Type | Example | Action |
| ---- | ------- | ------ |
| Test failure | Assertion failed | Record, continue |
| Execution error | Service crashed, timeout | Record, attempt recovery, may stop |
| Critical error | Infrastructure down | Stop, report INCOMPLETE |

## Exploratory Pass

While executing scripted scenarios, watch for what the script does not cover: regressions, side
effects, unexpected errors, performance changes, UI anomalies, data inconsistencies. Record each
immediately with context, severity, evidence and reproduction steps - these are usually the most
valuable findings of the whole phase.

## Phase 4 - Status and Reports

Determine status in this order:

1. Execution errors prevented testing -> **INCOMPLETE**
2. Not all scenarios ran -> **PARTIAL**
3. Any scenario failed -> **FAILED**
4. Otherwise -> **PASSED**

Write `validation/report-{date}.md`: summary metrics, results per story, failure details,
out-of-scope issues, prioritised recommendations. Screenshots in `validation/screenshots/`.

Write one bug file per failure or discovered issue, `validation/bugs/BUG-{n}-{slug}.md`:

```markdown
---
status: open
severity: critical|high|medium|low
type: scenario_failure|regression|side_effect|performance|ui_anomaly|data_issue
user_story: US#
created: {date}
---

# BUG-{n}: {title}

## Summary
## Reproduction Steps
## Expected vs Actual
## Evidence
## Technical Analysis
- Probable cause / Affected files / Suggested fix
```

Severity: **critical** core broken, no workaround; **high** important feature broken; **medium** works
with issues; **low** cosmetic.

Insert correction tasks into `tasks.md` after the last completed task, tagged with severity and story.

## Phase 5 - Cleanup

Stop services and containers, close the browser. Leave test data in place when failures occurred -
it is the evidence.

## Honesty Rules

- Never report PASSED when scenarios were skipped. That is PARTIAL.
- Never report FAILED when the system never ran. That is INCOMPLETE.
- Never mark a scenario passed because the code "looks right". Execution or nothing.

## Handoff

Failures -> `bug-diagnosis`. All passing -> the QA gate, then `feature-merge`.
