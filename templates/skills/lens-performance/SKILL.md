---
name: lens-performance
description: |
  Adversarial performance lens - finds work that grows faster than it should, blocking calls on hot
  paths and resources with no ceiling. Activate when: reviewing a request path, a loop over I/O, a
  list endpoint, a job, or any change with a latency or throughput target.
triggers: ["performance review", "latency", "slow", "throughput", "scalability review", "hot path", "load", "optimize"]
lens:
  id: performance
  prefix: PRF
  domain: Performance and scalability
  applies_to: [plan, code, config, data-model]
  phases: [design, build, qa]
  blocking_severity: high
---

# Performance Lens

**Failure this lens prevents**: a system that works at demo scale and collapses at real scale.

## Load First

The request or job path end to end, the data volumes it touches, stated latency or throughput
targets, and any existing measurements. Without a target, the first finding is the missing target.

## Budget First

| Path | Target | Current | Dominant cost | Growth with N |
| ---- | ------ | ------- | ------------- | ------------- |

Fill this before probing. A performance review with no numbers produces opinions.

## Probes

| # | Probe | Failure signature | Evidence to capture |
| - | ----- | ----------------- | ------------------- |
| F1 | How does work grow with input size? | Nested iteration over collections that both scale; quadratic join | Code + both sizes |
| F2 | Is there I/O inside a loop? | Query, HTTP call, file read per item | Loop + call |
| F3 | Is any input unbounded? | No page size cap, no payload limit, no depth limit on nested queries | Endpoint |
| F4 | Is the same work repeated? | Identical computation or fetch per request with no memoisation | Call site |
| F5 | Are blocking calls on an async path? | Sync I/O in an event loop, CPU-heavy work in a request handler | Call site |
| F6 | Is data loaded that is never used? | `SELECT *`, full document fetch for one field, over-eager includes | Query |
| F7 | Is serialisation proportional to the response, not the dataset? | Whole collection serialised then sliced | Serializer |
| F8 | Are there ceilings on memory? | Full result set into memory, unbounded buffer, unbounded concurrency | Allocation site |
| F9 | Are external calls parallelised where independent, and bounded where not? | Sequential independent calls; unbounded fan-out | Call sequence |
| F10 | Is caching used where the read/write ratio justifies it, with a defined key and TTL? | No cache on a hot expensive read; or a cache with no invalidation | Read site |
| F11 | Do indexes support the actual query shapes? | Filter, sort or join without a usable index | Query + schema |
| F12 | Is startup or cold-path cost acceptable? | Heavy initialisation per request; connection created per call | Init site |
| F13 | Is the payload size reasonable? | Megabyte responses, no compression, images unbounded | Response |
| F14 | Does the change move work into a hot path? | New dependency, new call, new validation added per request | Diff |

## Attack Moves

- **Multiply by real N**: take the actual production size and 10x it. Recompute every count of
  operations. Report the ones that cross the budget.
- **Count the round trips**: for one user action, count queries and network calls. Compare with the
  minimum needed.
- **Profile, don't guess**: where possible, measure. A measured 3ms is worth more than a reasoned
  "this looks slow". If measurement is impossible, mark the finding `plausible`.
- **Tail thinking**: reason at p99, not the mean. What is the slowest realistic case - largest tenant,
  coldest cache, slowest dependency?
- **Concurrency squeeze**: what happens when 100 of these run at once? Connection pool, lock, memory.

## Severity Calibration

| Severity | Performance-specific |
| -------- | -------------------- |
| Critical | Unbounded growth that exhausts memory or connections, taking the service down |
| High | Primary flow misses its stated target at expected scale; N+1 on a main list; unbounded input reachable by a client |
| Medium | Secondary path degrades; missing cache on an expensive read; avoidable repeated work |
| Low | Micro-optimisation with no measurable effect at current scale |

## Common False Positives

- "Inefficient" code on a path that runs once at startup or over ten rows. Cost matters where volume is.
- N+1 that the ORM batches, or that hits a warm cache. Check the actual query log.
- Missing cache where the write rate makes it useless or wrong. State the read/write ratio.
- Optimising before a target exists - the finding then belongs to `lens-requirements`.

## Output

Findings with prefix `PRF`, each with the growth function (`O(n)` or operations per request), the
measured or estimated cost, and the target it violates.
