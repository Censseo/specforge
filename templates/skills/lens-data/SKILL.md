---
name: lens-data
description: |
  Adversarial data lens - attacks schemas, migrations, queries, caches and retention for integrity
  loss, irreversible operations and unbounded growth. Activate when: reviewing a migration, a schema
  change, a query, a bulk operation, a cache, or a deletion path.
triggers: ["migration review", "schema review", "data integrity", "query review", "n+1", "index", "data loss", "retention"]
lens:
  id: data
  prefix: DAT
  domain: Data and persistence
  applies_to: [plan, data-model, code, migrations, config]
  phases: [design, build, qa]
  blocking_severity: critical
---

# Data Lens

**Failure this lens prevents**: losing, corrupting, or silently duplicating data - the failures that
cannot be fixed by a redeploy.

## Load First

Migration files, schema definitions, repository and query code, cache usage, backup and retention
configuration, and the row counts of affected tables if available.

## Probes

| # | Probe | Failure signature | Evidence to capture |
| - | ----- | ----------------- | ------------------- |
| D1 | Does the migration run against populated tables? | `NOT NULL` with no default, type narrowing, unique index on non-unique data | Migration line + why existing rows fail |
| D2 | Is the migration reversible, and is the down path tested? | No down migration, or a down that drops data | Migration |
| D3 | Does the migration lock a large table? | Blocking `ALTER`, index build without `CONCURRENTLY`, full-table rewrite | Statement + table size |
| D4 | Is deploy order safe in both directions? | Code expects the new column before the migration lands; old code breaks on the new schema | Ordering description |
| D5 | Are integrity rules in the database, not only in code? | No FK, no unique constraint, no check - enforced by application only | Constraint that is missing |
| D6 | Can a write partially succeed? | Multi-step write with no transaction; commit before the dependent write | Code path |
| D7 | Is deletion soft or hard, and is that intentional? | Hard delete of data referenced elsewhere; soft delete not filtered in queries | Delete site + readers |
| D8 | Are queries bounded? | No LIMIT, no pagination, `SELECT *` over a wide table, unbounded IN list | Query |
| D9 | Is there a query inside a loop? | 1 + N pattern in a serializer, resolver or handler | Loop + query line |
| D10 | Do queried columns have an index, and is it usable? | Filter or join on an unindexed column; index unusable due to a function or leading wildcard | Query + schema |
| D11 | Is the cache invalidated on every write path? | Write path that bypasses the cache update; no TTL | Write site |
| D12 | Is stale-read tolerated where it is used? | Read-after-write on a replica used for a decision | Read site |
| D13 | Does the data have a retention rule? | Personal or high-volume data with unbounded growth and no deletion job | Table |
| D14 | Are backups and restore actually verified for this data? | New store with no backup path | Store |
| D15 | Is precision preserved? | Money in floats; timestamps without time zone; truncated ids | Field |
| D16 | Are bulk operations chunked and resumable? | Single transaction over millions of rows; no progress marker | Job |

## Attack Moves

- **Restore-and-run**: run the migration against a copy of production-shaped data, not an empty schema.
- **Interrupt test**: kill the process halfway through the bulk operation. What state is left, and can
  it be resumed or re-run safely?
- **Double execution**: run the migration or job twice. Anything that is not idempotent is a finding.
- **Constraint removal**: for each rule enforced only in application code, find a second write path
  (admin script, background job, another service) that bypasses it.
- **Growth projection**: multiply current row count by the stated growth rate over a year. Which query
  or index stops working?

## Severity Calibration

| Severity | Data-specific |
| -------- | ------------- |
| Critical | Possible data loss or corruption; irreversible migration with no backup; hard delete of referenced data; money precision loss |
| High | Migration fails or locks in production; missing integrity constraint on a core relation; unbounded query on a large table; cache never invalidated |
| Medium | N+1 on a secondary path; missing index causing a slow but survivable query; no retention rule on non-personal data |
| Low | Naming, ordering, or a redundant index |

## Common False Positives

- A missing index on a table that is small and stays small. Check expected cardinality first.
- An N+1 that the ORM already resolves by eager loading configured elsewhere - check the query log,
  not the source alone.
- Application-level integrity where the database cannot express the rule. The finding is then about
  the number of write paths, not the missing constraint.

## Output

Findings with prefix `DAT`. For every migration finding, state the safe sequence explicitly:
expand -> backfill -> switch -> contract.
