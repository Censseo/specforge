---
name: lens-testing
description: |
  Adversarial testing lens - attacks the test suite itself: weak oracles, mocked-away truth, missing
  edge cases and tests that cannot fail. Activate when: reviewing tests, a bug fix without a test,
  coverage claims, or before the build and qa gates.
triggers: ["test review", "are these tests good", "coverage", "flaky test", "test quality", "missing tests", "mutation testing"]
lens:
  id: testing
  prefix: TST
  domain: Test strategy and quality
  applies_to: [tasks, code, tests, contracts]
  phases: [build, qa]
  blocking_severity: high
---

# Testing Lens

**Failure this lens prevents**: a green suite that proves nothing.

Coverage percentage is not evidence. The question is not how much code the tests execute, but which
defects they would catch.

## Load First

The tests for the changed behavior, the code they cover, the CI configuration, and any skipped or
quarantined tests.

## Probes

| # | Probe | Failure signature | Evidence to capture |
| - | ----- | ----------------- | ------------------- |
| T1 | Would the test fail if the behavior were removed? | Test asserts only that no exception was raised, or asserts a mock was called | Test + assertion |
| T2 | Does the test mock the thing it claims to verify? | The boundary under test is stubbed; the test verifies the stub | Mock + subject |
| T3 | Does the bug fix have a regression test that fails without the fix? | Fix committed with no test, or a test that passes on the old code | Fix + test |
| T4 | Are the edge cases covered? | Only the happy path: no empty, boundary, duplicate, unicode, negative, max | Missing cases |
| T5 | Are error paths tested? | No test for the failure, timeout, denied or not-found branch | Branch |
| T6 | Are the assertions specific? | `assert result` / `assertTrue(x)` where a value should be compared | Assertion |
| T7 | Do tests depend on each other or on order? | Shared mutable fixture; passing only in suite order | Fixture |
| T8 | Are tests deterministic? | Real time, real network, real randomness, sleeps, timing assumptions | Source of nondeterminism |
| T9 | Are any tests skipped, quarantined or deleted in this change? | `skip`, `xfail`, `.only`, commented-out test, removed file | Location + reason |
| T10 | Is the test at the right level? | Unit test asserting integration behavior, or an e2e test for pure logic | Test |
| T11 | Are contracts tested against the real schema? | Handcrafted fixture that has drifted from `contracts/` | Fixture vs contract |
| T12 | Is test data realistic? | Only tiny, clean inputs; nothing resembling production shape or size | Fixture |
| T13 | Does every acceptance scenario have an executable counterpart? | Scenario in the spec with no test | Scenario id |
| T14 | Do tests run in CI on every change? | Suite excluded, marked manual, or failing without blocking | CI config |
| T15 | Would a plausible wrong implementation still pass? | Test cannot distinguish correct from nearly-correct | Alternative implementation |

## Attack Moves

- **Mental mutation**: change a `<` to `<=`, invert a condition, return a constant, delete a
  validation. For each mutation, name the test that fails. Silence is a finding.
- **Delete the implementation**: replace the function body with a stub returning a plausible value.
  How many tests still pass?
- **Oracle audit**: for each test, name the specific defect it would catch. Tests with no answer are
  ceremony.
- **Skip archaeology**: for each skipped test, find out when and why. A skip with no expiry is
  permanent by default.
- **Scenario diff**: line up spec acceptance scenarios against test names. Report the unmatched ones.

## Severity Calibration

| Severity | Testing-specific |
| -------- | ---------------- |
| Critical | Tests disabled or deleted to make a build pass; the suite cannot fail on the primary flow |
| High | New behavior on a primary flow with no test; bug fix with no regression test; test mocks the boundary it verifies; flaky test tolerated on a critical path |
| Medium | Edge cases untested; weak assertions; test at the wrong level; unrealistic fixtures |
| Low | Naming, structure, duplication in test code |

## Common False Positives

- Missing unit tests for code that is thoroughly covered by an integration test that would catch the
  same defects. Judge by defect coverage, not by test count.
- Mocks at a boundary that is genuinely out of scope (a third-party API in a unit test) - that is
  correct, provided a contract test exists somewhere.
- Absence of tests for generated or trivially declarative code.

## Output

Findings with prefix `TST`, plus the mutation table:

```markdown
| Mutation | Test that catches it | Verdict |
| -------- | -------------------- | ------- |
```
