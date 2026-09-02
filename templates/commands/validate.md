---
description: Run integration tests by starting services, executing acceptance scenarios, and reporting results
skills:
  - integration-validation
  - lens-testing
  - lens-accessibility
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

## User Input

```text
$ARGUMENTS
```

Scope: `full` (default), `smoke`, `US1` / `P1`, `api`, `ui`.

## Method

Apply the **`integration-validation`** skill: the Gherkin-to-action translation, evidence capture, the
exploratory pass, the status determination rules and the bug report format.

The report must reflect reality. Everything downstream is built on it.

## Prerequisites

| Requirement | If missing |
| ----------- | ---------- |
| MCP server configured | Run `/specforge.setup-mcp`, or fall back to bash and curl |
| `spec.md` with acceptance scenarios | Nothing to validate - stop |
| Implementation complete in `tasks.md` | Validate only the stories whose tasks are done |

## Operational Steps

1. Run `{SCRIPT}` for paths, then load `spec.md` (scenarios), `plan.md`, `tasks.md`, `contracts/` and
   `quickstart.md`.

2. Build the test matrix and mark each story **testable**, **partial** or **skip** based on `tasks.md`.

3. Start the environment: `start_docker`, health-check the containers, `start_service backend`,
   health-check, `start_service frontend`, health-check. Seed data per `quickstart.md`. If a service
   fails, read its logs (`service_logs <name> 50`), report, and ask how to proceed.

4. Execute scenarios by priority (P1 -> P2 -> P3), translating Given / When / Then into setup, actions
   (`browser_*` or `api_*`) and assertions. Capture a screenshot and the response for every scenario;
   capture service logs on every failure.

5. Run the exploratory pass alongside: regressions, side effects, performance changes, UI anomalies,
   data inconsistencies. File each as a bug immediately.

6. Determine status: execution errors -> INCOMPLETE; scenarios skipped -> PARTIAL; any failure ->
   FAILED; otherwise PASSED.

7. Write `validation/report-{date}.md`, one `validation/bugs/BUG-{n}-{slug}.md` per issue (frontmatter:
   status, severity, type, user_story, created), and screenshots to `validation/screenshots/`.

8. Insert correction tasks into `tasks.md` after the last completed task, tagged with severity and story.

9. Cleanup: `stop_all`, `stop_docker`, `browser_close`. Leave test data in place when failures
   occurred - it is the evidence.

## Report

Status, scenario counts per story, failures with severity, bug files created (these are the input for
`/specforge.fix`), correction tasks added, and the next step.

Never report PASSED when scenarios were skipped, and never FAILED when the system never ran.

## Fallback

Without MCP: start services with bash or tmux and test APIs with curl. For browser automation,
recommend `/specforge.setup-mcp` first.
