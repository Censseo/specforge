---
name: lens-concurrency
description: |
  Adversarial concurrency lens - finds races, lost updates, deadlocks and order assumptions in code
  that can run more than once at a time. Activate when: reviewing shared state, async code, workers,
  locks, counters, schedulers or anything running in multiple replicas.
triggers: ["concurrency review", "race condition", "deadlock", "lost update", "thread safety", "idempotency", "parallel", "locking"]
lens:
  id: concurrency
  prefix: CON
  domain: Concurrency and ordering
  applies_to: [code, plan, data-model]
  phases: [build, qa]
  blocking_severity: high
---

# Concurrency Lens

**Failure this lens prevents**: bugs that appear only under load, cannot be reproduced, and corrupt
data while looking like a fluke.

## Load First

The deployment shape (replicas, workers, threads), shared state (database rows, cache keys, files,
in-memory maps), and every read-modify-write sequence in the diff.

## Probes

| # | Probe | Failure signature | Evidence to capture |
| - | ----- | ----------------- | ------------------- |
| C1 | Is there a read-modify-write without atomicity? | Read value, compute, write back - no transaction, no atomic op, no version check | Sequence |
| C2 | Is check-then-act separated? | `if not exists: create` - two callers both pass the check | Both lines |
| C3 | Is shared mutable state protected? | Module-level dict, cached object, singleton mutated per request | State + writers |
| C4 | Is uniqueness enforced by the database, not by a prior lookup? | Duplicate rows under concurrency despite an application check | Insert path |
| C5 | Is the lock scope right, and can it deadlock? | Two locks acquired in different orders; lock held across I/O | Lock sites |
| C6 | Are operations idempotent where they can be delivered twice? | Second delivery creates a second effect | Handler |
| C7 | Is ordering assumed where it is not guaranteed? | Message A assumed before B; parallel jobs assumed sequential | Assumption site |
| C8 | Is there a lost-update path on user edits? | Last write wins with no version, etag or conflict detection | Update handler |
| C9 | Are async tasks awaited or deliberately fire-and-forget? | Unawaited promise or task, exceptions vanish, work lost on shutdown | Call site |
| C10 | Is cancellation and shutdown handled? | In-flight work dropped on deploy; no drain | Shutdown path |
| C11 | Are resources released on every path? | Connection or file leaked on the error branch | Acquisition site |
| C12 | Is the scheduled job safe when two replicas run it? | Cron in every replica with no leader election or lock | Job config |
| C13 | Do caches suffer stampede? | Expensive recompute by every caller when a hot key expires | Cache read |
| C14 | Is time used as a coordination mechanism? | `sleep` to wait for another actor; clock comparison across machines | Code |

## Attack Moves

- **Two-actor interleave**: write the two execution timelines side by side, statement by statement.
  Find the interleaving that breaks the invariant. If you cannot construct one, the finding is refuted.
- **Replica multiplication**: assume the documented replica count. Every "only one of these runs"
  assumption is a candidate finding.
- **Duplicate delivery**: run every consumer twice with the same message.
- **Slow-motion crash**: pause between each step of a sequence and ask what another actor could do
  in that window.
- **Search for atomics**: grep for `+= 1`, `count = count`, `find_or_create`, `exists ... create`.

## Severity Calibration

| Severity | Concurrency-specific |
| -------- | -------------------- |
| Critical | Race corrupting money, permissions or persisted state; deadlock reachable on the primary flow |
| High | Lost updates on user data; duplicate records or effects from non-idempotent handlers; scheduled job double-running with side effects |
| Medium | Cache stampede; unawaited background work with recoverable loss; resource leak on an error branch |
| Low | Theoretical race in code that is single-threaded by construction |

## Common False Positives

- Races in code that provably runs single-threaded (single replica, single-threaded runtime, per-key
  serialised queue). Verify the runtime model before reporting.
- "Missing lock" where the database enforces the invariant with a unique constraint or atomic update.
- Non-idempotent handlers behind exactly-once delivery guaranteed by the broker - check the broker.

## Output

Findings with prefix `CON`. Each must show the interleaving explicitly as two timelines. Prefer fixes
that remove the race (atomic operation, unique constraint, idempotency key) over fixes that add a lock.
