---
name: lens-api-contract
description: |
  Adversarial API contract lens - attacks endpoints, schemas, events and public interfaces for drift,
  breaking changes, weak error semantics and missing idempotency. Activate when: reviewing an API
  contract, an endpoint, an event schema, or any interface other code depends on.
triggers: ["api review", "contract review", "endpoint review", "breaking change", "openapi", "response schema", "api versioning"]
lens:
  id: api-contract
  prefix: API
  domain: Interface contracts
  applies_to: [contracts, spec, code, docs]
  phases: [design, build, qa]
  blocking_severity: high
---

# API Contract Lens

**Failure this lens prevents**: a contract that says one thing while the implementation does another,
or a change that silently breaks every existing client.

## Load First

`contracts/` (OpenAPI, GraphQL schema, protobuf, event schemas), the route handlers that implement
them, the client code that consumes them, and the previous version of the contract if this is a change.

## Probes

| # | Probe | Failure signature | Evidence to capture |
| - | ----- | ----------------- | ------------------- |
| P1 | Does the implementation match the declared contract, field by field? | Extra field, missing field, different type or casing | Contract line vs handler line |
| P2 | Are all error responses documented with status codes? | Only 200 documented; 4xx/5xx undefined | Endpoint + missing cases |
| P3 | Is the status code semantically right? | 200 on failure, 500 on client error, 404 vs 403 confusion, 200 on async accept | Handler line |
| P4 | Is the error body shape consistent across endpoints? | Three different error formats in one API | Examples of each |
| P5 | Is this change backward compatible? | Removed or renamed field, narrowed type, new required input, changed default, changed enum | Old vs new |
| P6 | Are writes idempotent, or is retry unsafe? | POST with no idempotency key, retried by clients or gateways | Endpoint + effect of double call |
| P7 | Are list endpoints bounded? | No pagination, no max page size, unbounded include/expand | Endpoint |
| P8 | Is input validated at the edge, per the schema? | Handler trusts body shape; validation only partial | Field with no validation |
| P9 | Is authorization specified per endpoint, not assumed? | No authz statement; "authenticated" treated as "authorized" | Endpoint |
| P10 | Are nullability and optionality explicit? | Fields that may be absent are typed as always present | Field |
| P11 | Is versioning defined and is the deprecation path stated? | No version, or a version with no sunset policy | Contract header |
| P12 | Are timestamps, ids and enums in a stated format? | Mixed date formats, opaque vs numeric ids, undocumented enum values | Field |
| P13 | Do side effects match the verb? | GET mutates; DELETE is not idempotent; PUT partially updates | Handler |
| P14 | Are rate limits and payload limits documented? | No limit stated; unbounded upload | Endpoint |
| P15 | For events: is the schema versioned and are consumers tolerant? | Producer change with no consumer compatibility rule | Event + consumers |

## Attack Moves

- **Client simulation**: write the client call from the contract alone, then run it against the
  implementation. Every difference is a finding.
- **Compatibility diff**: mechanically diff old and new contracts. Classify each change as additive,
  breaking, or behavioural. Breaking changes without a version bump are High minimum.
- **Retry storm**: call every write endpoint twice with the same payload. Anything that produces two
  effects is a missing idempotency finding.
- **Error path walk**: for each endpoint, produce every documented and undocumented failure - bad
  input, missing auth, wrong owner, absent resource, downstream down. Record what actually comes back.
- **Field lifecycle**: for each field, ask who sets it, who reads it, and what happens when it is absent.

## Severity Calibration

| Severity | Contract-specific |
| -------- | ----------------- |
| Critical | Undeclared breaking change to a published contract; authorization missing on a mutating endpoint |
| High | Implementation drift on a primary endpoint; non-idempotent write that clients retry; unbounded list on a large collection; error cases undocumented on a primary flow |
| Medium | Inconsistent error shape; missing pagination on a small collection; ambiguous nullability |
| Low | Documentation wording, example freshness |

## Common False Positives

- An "undocumented" endpoint that is internal-only and unreachable from outside the deployment
  boundary - verify the routing before reporting.
- A breaking change that is coordinated and recorded (versioned, with a migration note). The record
  is the difference.
- Non-idempotent writes behind a gateway that already enforces idempotency keys. Check the gateway.

## Output

Findings with prefix `API`. Include a compatibility table when the contract changed:

```markdown
| Change | Type | Breaking? | Clients affected | Mitigation |
| ------ | ---- | --------- | ---------------- | ---------- |
```
