---
name: focused-change
description: |
  Apply a small, bounded change - a bug fix, a spec tweak, a piece of user feedback, a refinement -
  without the full workflow, while keeping traceability intact. Activate when: the change is small and
  local, and running design-build-qa would cost more than the change itself.
triggers: ["quick change", "small fix", "tweak the spec", "user feedback", "polish this", "minor change", "just change"]
phase: build
---

# Focused Change

> The workflow exists to control risk. Where there is no risk, it is overhead - but traceability is
> never overhead.

## Scope Test - Run It First

| Signal | Verdict |
| ------ | ------- |
| Touches one behavior in a few files | Proceed |
| Adds a new entity, endpoint or module | Escalate to the full workflow |
| Changes architecture or a public contract | Escalate |
| Affects more than one user story | Escalate |
| Cannot be verified in a few minutes | Escalate |

Escalating is not failure. A "quick change" that turns into a redesign mid-flight is.

## Triage

| Type | Triggers | Path |
| ---- | -------- | ---- |
| Bug fix | "broken", "error", "fails", an error message | Fix the code |
| Spec tweak | "clarify", "add requirement", "edge case" | Edit the spec, then check cascade |
| User feedback | "user said", "testing showed", "confusing" | Categorise, then apply |
| Refinement | "improve", "optimise", "polish", "cleaner" | Refactor with no behavior change |

## Bug Fix Path

1. Quick 5-Whys - two or three levels, not a ceremony.
2. Apply the fix at the cause, not at the symptom.
3. Verify: run the affected test; add a regression test that fails without the fix.
4. Update traceability: mark the task `[~]` if it was wrongly marked complete; note the fix in the
   spec if behavior changed.

## Spec Tweak Path

1. Locate the exact section.
2. Apply the edit; replace contradicted text rather than adding beside it.
3. Cascade check:

| Change | Code impact | Action |
| ------ | ----------- | ------ |
| Clarification only | None | Done |
| New edge case | May need handling | Check the code |
| Behavior change | Likely needs an update | Update the code, or add a task |

Then record it in `## Clarifications` with the date.

## User Feedback Path

Capture the feedback verbatim first - the paraphrase loses the signal.

| Feedback type | Response |
| ------------- | -------- |
| UX friction | Adjust the flow |
| Confusion | Clarify labels and messages |
| Missing case | Add handling |
| Wrong behavior | Fix to match the expectation |
| Feature request | Escalate |

If behavior changed, update the spec. An undocumented behavior change is a future bug report.

## Refinement Path

Behavior must not change. Verify by running the existing tests before and after - if a test needed
changing, it was not a refinement.

| Type | Example |
| ---- | ------- |
| Performance | Cache a result, remove a query from a loop |
| Readability | Rename, extract, flatten |
| UX polish | Better loading state, clearer error text |
| Code quality | Remove duplication, tighten types |

## Always

- Say which files changed and why.
- Say what you verified and how.
- Update `tasks.md` or `spec.md` when the change makes either untrue.
- Run `adversarial-review` with one or two relevant lenses when the change touches security, data or
  a public contract - small changes in those areas are exactly where the expensive defects live.
