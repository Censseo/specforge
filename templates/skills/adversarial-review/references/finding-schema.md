# Finding Schema and Worked Examples

## Required Fields

| Field | Rule |
| ----- | ---- |
| `id` | `<LENS-PREFIX>-<n>`. Prefixes: REQ, ARC, DOM, API, DAT, SEC, PRV, PRF, REL, CON, OBS, TST, A11Y, UX, I18N, OPS, MNT, SUP, LLM |
| `lens` | The lens that produced it |
| `target` | `path:line`, `file §section`, or `endpoint` - never "the codebase" |
| `claim` | One sentence stating the defect. Not a question, not a suggestion |
| `failure_scenario` | Concrete inputs or state, then the wrong outcome. Must be reproducible in principle |
| `evidence` | Quotable anchors: code lines, spec text, command output, absence proven by a search that was run |
| `severity` | From the harness rubric |
| `confidence` | `confirmed` or `plausible`; `plausible` must name the unverified link |
| `blocking` | Boolean, decided by the gate rules |
| `fix` | The smallest change that removes the defect |
| `verification` | How a reviewer proves the fix worked |

## Good vs Bad Claims

| Bad | Why | Good |
| --- | --- | ---- |
| "Error handling could be improved" | No defect, no failure | "`parseConfig` swallows `JSONDecodeError` and returns `{}`, so a corrupt config boots the service with defaults silently" |
| "This endpoint might be slow" | Speculation | "`GET /orders` loads `order.items` per row inside the serializer loop: 1 + N queries, N = page size 100" |
| "Consider adding tests" | Preference | "No test covers the refund path added in `refund.ts:40-88`; the branch `amount > original` is unreachable in the suite" |
| "The spec is vague" | Not located | "FR-007 requires 'fast search' with no target; acceptance cannot be evaluated and the perf task T031 has no threshold" |

## Worked Example - Confirmed

```yaml
id: DAT-001
lens: data
target: migrations/0042_add_status.sql:3
claim: >
  The migration adds a NOT NULL column without a default to a populated table, so it fails on
  any environment with existing rows.
failure_scenario: >
  Deploy to staging where `orders` has 1.2M rows -> ALTER TABLE raises
  "column status contains null values" -> deploy aborts mid-release with schema half-applied.
evidence:
  - migrations/0042_add_status.sql:3 `ADD COLUMN status text NOT NULL`
  - no backfill statement in the file; no default clause
  - orders table is populated in all envs (seed in fixtures/orders.sql)
severity: high
confidence: confirmed
blocking: true
fix: >
  Add column nullable, backfill in a separate statement, then set NOT NULL in a follow-up migration.
verification: >
  Run the migration against a restored staging dump; assert it completes and status has no nulls.
```

## Worked Example - Plausible

```yaml
id: CON-003
lens: concurrency
target: src/jobs/counter.ts:31
claim: >
  The view counter uses read-modify-write without a lock, so concurrent workers lose increments.
failure_scenario: >
  Two workers read count=41 within the same tick, both write 42; one view is lost. Under the
  documented 4-worker deployment this is expected at any meaningful traffic.
evidence:
  - src/jobs/counter.ts:31-34 read then write, no transaction
  - deploy/worker.yaml replicas: 4
  - UNVERIFIED: whether the queue guarantees single-consumer per key
severity: medium
confidence: plausible
blocking: false
fix: Replace with an atomic increment (`UPDATE ... SET count = count + 1`).
verification: Concurrency test with 4 writers x 1000 increments asserting the final value is 4000.
```

The unverified link is stated explicitly. If the queue does guarantee single-consumer per key, the
finding is REFUTED and must be dropped rather than downgraded.
