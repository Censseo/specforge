---
description: Macro command that validates the implementation end-to-end, runs a fix/validate loop up to 3 times if failures are found, then red-teams the release before the gate.
skills:
  - specforge-workflow
  - adversarial-review
  - finding-verification
  - quality-gates
lenses:
  - lens-requirements
  - lens-testing
  - lens-security
  - lens-reliability
  - lens-performance
  - lens-observability
  - lens-accessibility
  - lens-operations
semantic_anchors:
  - ATDD                    # Acceptance Test-Driven Development - executable specs
  - Regression Testing      # Verify unchanged functionality still works
  - Scientific Method       # Hypothesis, experiment, observation, conclusion
  - Exploratory Testing     # Charter-driven, observe beyond the script
  - FMEA                    # Enumerate failure modes, effects and detection
handoffs:
  - label: Manual Fix
    agent: specforge.fix
    prompt: Manually diagnose and fix the remaining issues
  - label: Re-validate
    agent: specforge.validate
    prompt: Re-run validation after manual fixes
  - label: Merge Feature
    agent: specforge.merge
    prompt: Merge this feature into main
scripts:
  sh: scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
  ps: scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks
---

## User Input

```text
$ARGUMENTS
```

Consider the user input before proceeding (if not empty).

## Outline

This macro command runs end-to-end validation with an automated fix/validate loop, then attacks what
only exists once the system runs.

1. Load test credentials and context
2. Run `/specforge.validate`
3. If partial/failed: `/specforge.fix` then re-validate (loop max 3x)
4. Early exit if no progress between retries
5. Adversarial release review through the operational lenses
6. QA gate record and final report

## Detailed Steps

### Step 1: Preparation

Run `{SCRIPT}` from repo root and parse JSON for FEATURE_DIR.

Load test credentials from `TEST_USER_CREDENTIALS.md` in project root. Extract usernames, passwords,
and service URLs for use during validation.

Read `FEATURE_DIR/gates/build-*.md` for the build gate verdict and any conditions carried into QA.
Read `tasks.md` to determine what is actually testable - testing a story whose tasks are unfinished
produces failures that mean nothing.

Initialize state:

- MAX_RETRIES = 3
- current_retry = 0
- validation_status = PENDING
- previous_failure_count = 999

### Step 2: Validation Loop

Repeat while `current_retry <= MAX_RETRIES` and `validation_status != PASSED`:

#### Step 2a: Validate

```text
Skill: specforge.validate
Args: Use TEST_USER_CREDENTIALS.md for test users. Run E2E tests via browser. Verify style cohesion. Start the agent-service if needed. Start all required infrastructure. Do not ask for confirmation - proceed with all scenarios.
```

Parse results: extract overall status (PASSED/FAILED/PARTIAL/INCOMPLETE), failure count, list of
failing scenarios.

`INCOMPLETE` means execution errors prevented testing. It is not a failure count of zero and it is
never a pass - treat it per the exit conditions below.

#### Step 2b: Check exit conditions

- If **PASSED**: break loop, go to Step 3
- If **INCOMPLETE** twice in a row: the environment is the problem, not the code. Break loop and
  report status INCOMPLETE with the infrastructure error - retrying will not help
- If `current_retry >= MAX_RETRIES`: log "Max retries reached", break loop
- If failure count >= previous_failure_count (no progress): log "No progress detected, stopping",
  break loop
- Otherwise: proceed to fix

#### Step 2c: Fix

```text
Skill: specforge.fix
Args: Fix the validation failures. Apply fixes directly without asking the user. Focus on the failing acceptance scenarios.
```

Each fix must root-cause before it patches, and must add the regression test that fails without the
fix. A fix that changes the symptom without addressing the cause moves the bug into the next round -
which is exactly what burns the three retries.

Log: `Retry {current_retry}: Applied fixes. Re-validating...`

#### Step 2d: Increment

```text
previous_failure_count = current_failure_count
current_retry += 1
```

Loop back to Step 2a.

### Step 3: Adversarial Release Review

The loop proves the scripted scenarios pass. This step attacks what the scenarios do not cover, and
what only becomes visible once the system actually runs.

Apply the `adversarial-review` skill against the feature as a whole - code, configuration, contracts
and operational surface. Weight the lenses that need a running system:

| Lens | The question it answers here |
|------|------------------------------|
| `lens-reliability` | What happens when a dependency is down, slow, or returns garbage |
| `lens-observability` | Would we notice this failing in production, how fast, and what would we look at next |
| `lens-operations` | Can this be deployed, configured and rolled back after traffic has flowed |
| `lens-testing` | Would the suite have caught the bugs the loop just fixed, before the loop |
| `lens-security` | Traced exploit paths on the running surface, not generic warnings |
| `lens-accessibility` | Keyboard and screen-reader completion of the primary flows |
| `lens-performance` | Behavior at real data volume, not fixture volume |
| `lens-requirements` | Does what shipped match what was specified |

Drop any lens with no surface in this feature and record the skip. Add any whose risk trigger fired.

Falsify every candidate with `finding-verification`. Then:

- **Confirmed and blocking** (Critical, or High and confirmed, or a constitution MUST violation, or a
  one-way door): file it as a bug in `validation/bugs/` and report - it blocks the gate.
- **Confirmed and advisory**: file it with an owner and a task.
- **Refuted**: drop it.

Findings from this step do **not** re-enter the retry loop. The loop is for scenario failures; these
go to the gate, where a human decides.

### Step 4: QA Gate Record

Apply the `quality-gates` skill, QA gate criteria Q1-Q8. Write `FEATURE_DIR/gates/qa-{date}.md` with
the verdict, the criteria table, the bug ledger and any conditions carried into the merge.

A gate cannot pass while a Critical bug is open, or while a High bug is open without a recorded,
accepted waiver.

### Step 5: Final Report

Save to `FEATURE_DIR/qa-report.md` and display:

```markdown
## QA Pipeline Complete

**Status**: {PASSED | FAILED | PARTIAL | INCOMPLETE}
**Gate**: {PASS | PASS WITH CONDITIONS | BLOCK}
**Validation Rounds**: {current_retry + 1}
**Final Pass Rate**: {rate}%

### Summary
- Scenarios tested: {total}
- Passed: {count}
- Failed: {count}
- Fixed during QA: {count}

### Adversarial Release Review
- Lenses run: {list} | Skipped: {lens - reason}
- Findings: {confirmed} confirmed ({blocking} blocking, {advisory} advisory), {refuted} refuted

### Remaining Failures (if any)
{list with severity and user story}

### Carried Conditions
| ID | Condition | Owner | Tracked as |

### Next Steps
{If gate PASS:} Feature ready for merge. Run `/specforge.merge`.
{If gate BLOCK:} {count} blocking items remain. Run `/specforge.fix` manually or `/specforge.qa` after manual fixes.
```

## Error Handling

- **No TEST_USER_CREDENTIALS.md**: Warn but continue
- **Validate fails to start (infra issue)**: Report and stop, status = INCOMPLETE, gate = BLOCK with
  reason `not-evaluable` - an environment that never ran proves nothing and is never a PASS
- **Fix fails**: Log error, increment retry, continue loop
- **No progress between retries**: Break early to avoid wasting time
- **Blocking review finding**: gate = BLOCK; report the failure scenario and the smallest fix
