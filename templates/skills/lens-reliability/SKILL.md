---
name: lens-reliability
description: |
  Adversarial reliability lens - finds failure modes with no handling, retries that make things worse
  and operations that cannot survive a partial failure. Activate when: reviewing external calls,
  queues, jobs, transactions across services, timeouts or error handling.
triggers: ["reliability review", "failure modes", "retry", "timeout", "resilience", "what if this fails", "partial failure", "availability"]
lens:
  id: reliability
  prefix: REL
  domain: Reliability and resilience
  applies_to: [plan, contracts, code, config]
  phases: [design, build, qa]
  blocking_severity: high
---

# Reliability Lens

**Failure this lens prevents**: a system that works when everything works.

## Load First

Every outbound call, every background job and queue consumer, transaction boundaries, timeout and
retry configuration, and the stated availability expectation.

## Failure Inventory First

| Dependency | Failure mode | Detection | Handling | User-visible effect |
| ---------- | ------------ | --------- | -------- | ------------------- |

Failure modes to enumerate for each dependency: unavailable, slow, returns an error, returns wrong
data, returns partially, times out, rate-limits, is duplicated, arrives out of order.

## Probes

| # | Probe | Failure signature | Evidence to capture |
| - | ----- | ----------------- | ------------------- |
| L1 | Does every outbound call have a timeout? | Default-infinite client, no deadline propagated | Call site |
| L2 | Is retry bounded, backed off and jittered? | Immediate retry loop, unlimited attempts, synchronized retry storms | Retry code |
| L3 | Is retry safe for this operation? | Retrying a non-idempotent write; duplicate charges or records | Operation |
| L4 | What is the behavior when the dependency is down? | Unhandled exception surfaced to the user; whole page fails for one widget | Handler |
| L5 | Is there a degraded mode, and is it stated? | All-or-nothing behavior where partial service is possible | Feature |
| L6 | Can a multi-step operation fail halfway? | No compensation, no saga, no cleanup - orphaned state | Sequence + orphan |
| L7 | Are errors handled or swallowed? | `catch {}`, `except: pass`, error logged and execution continues as if it succeeded | Handler |
| L8 | Are failures distinguishable from empty results? | Failure returns `[]` or `null`, indistinguishable from "nothing found" | Return site |
| L9 | Do background jobs handle their own failure? | No dead-letter, no max attempts, failure invisible | Job |
| L10 | Is message processing idempotent and order-tolerant? | At-least-once delivery assumed to be exactly-once; ordering assumed | Consumer |
| L11 | Is there a circuit breaker or bulkhead on a shared dependency? | One slow dependency exhausts the pool for everything | Pool config |
| L12 | Is the health check meaningful? | Returns 200 when dependencies are down; checks nothing | Health endpoint |
| L13 | What happens on restart mid-operation? | In-memory state lost; no resume point | Operation |
| L14 | Are transactions scoped correctly across the boundary? | Transaction held open across a network call; distributed transaction assumed | Code |
| L15 | Is there a stated recovery path for each failure? | No runbook, no manual remedy for a known failure mode | Failure mode |

## Attack Moves

- **Kill it**: for each dependency, assume it is down for 5 minutes. Walk the user experience. Then
  assume it is slow rather than down - usually worse.
- **Duplicate delivery**: deliver every message twice, out of order. What breaks?
- **Halfway crash**: stop the process after each step of a multi-step operation. Enumerate the states
  left behind and whether the system can recover from each.
- **Retry math**: attempts x callers x downstream fan-out. Does retry amplify a brownout into an outage?
- **Silent failure hunt**: grep for empty catch blocks, ignored return values, and errors logged at
  debug level.

## Severity Calibration

| Severity | Reliability-specific |
| -------- | -------------------- |
| Critical | A single dependency failure takes down the primary flow with no recovery; retries cause duplicate irreversible effects (charges, sends, deletions) |
| High | No timeout on a request-path call; swallowed errors on a primary flow; partial failure leaves inconsistent state; unbounded retry |
| Medium | Missing degraded mode; failure indistinguishable from empty on a secondary path; no dead-letter on a non-critical job |
| Low | Health check granularity; log level of a handled failure |

## Common False Positives

- Missing timeouts where the client library sets a sensible default - verify the default rather than
  assuming infinity.
- "No retry" on an operation where failing fast is correct. Retry is not a virtue.
- Missing circuit breakers on a dependency that is in-process or cannot be slow.
- Compensation logic that exists at a higher level (an outer transaction, an idempotent replay).

## Output

Findings with prefix `REL`, plus the completed failure inventory. For each Critical or High, state
the smallest control that removes the failure mode: timeout, idempotency key, dead-letter, breaker,
or compensation.
