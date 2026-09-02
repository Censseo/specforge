# Lens Registry

Routing table for the adversarial review harness. Each lens is a separate skill (`lens-<id>`).

## Selection Rules

1. Run every lens marked **M** (mandatory) for the artifact type under review.
2. Add any lens whose risk trigger appears in the target.
3. Cap at 8 lenses per pass; split into waves ordered by blast radius if more trigger.
4. Record skipped lenses and the reason.

## Artifact Routing

Legend: **M** = mandatory, **C** = conditional (run if a risk trigger fires), blank = not applicable.

| Lens | idea | spec | plan / ADR | contracts | data-model | tasks | code | tests | config / IaC | docs |
| ---- | ---- | ---- | ---------- | --------- | ---------- | ----- | ---- | ----- | ------------ | ---- |
| `lens-requirements` | M | M | C | C | C | M | | C | | C |
| `lens-architecture` | C | C | M | C | C | C | M | | C | |
| `lens-domain-model` | C | M | M | C | M | C | C | | | C |
| `lens-api-contract` | | C | C | M | C | C | M | C | | C |
| `lens-data` | | C | M | C | M | C | M | C | M | |
| `lens-security` | C | M | M | M | M | C | M | C | M | |
| `lens-privacy-compliance` | C | M | C | C | M | C | C | | C | C |
| `lens-performance` | | C | M | C | C | C | M | C | C | |
| `lens-reliability` | | C | M | M | C | C | M | C | M | |
| `lens-concurrency` | | C | C | C | C | | M | C | | |
| `lens-observability` | | C | M | C | | C | M | | M | |
| `lens-testing` | | C | C | C | C | M | M | M | | |
| `lens-accessibility` | | C | C | | | C | M | C | | C |
| `lens-ux-content` | C | M | C | C | | C | C | | | C |
| `lens-i18n` | | C | C | C | C | | C | | C | C |
| `lens-operations` | | C | M | C | C | C | C | | M | C |
| `lens-maintainability` | | | C | C | | C | M | C | C | |
| `lens-supply-chain` | | | C | | | C | M | | M | |
| `lens-llm-integration` | C | C | C | C | | C | M | C | C | |

## Risk Triggers

A conditional lens becomes mandatory when its trigger is present anywhere in the target.

| Lens | Risk triggers |
| ---- | ------------- |
| `lens-requirements` | vague adjectives, TODO markers, missing acceptance criteria, requirement without a test |
| `lens-architecture` | new module or boundary, cross-layer import, new external dependency, pattern divergence from the registry |
| `lens-domain-model` | new entity, changed invariant, state machine, aggregate spanning transactions |
| `lens-api-contract` | new or changed endpoint, response shape change, status-code change, pagination, versioning |
| `lens-data` | migration, schema change, index change, bulk write, deletion, retention rule, cache |
| `lens-security` | authn/authz, secrets, user input, file upload, deserialization, network egress, crypto, admin surface |
| `lens-privacy-compliance` | personal data, tracking, logs containing user content, export, retention, third-party sharing, minors |
| `lens-performance` | loop over I/O, list endpoint, join, unbounded input, sync call on a hot path, new dependency in a request path |
| `lens-reliability` | external call, retry, queue, cron, partial failure, timeout, transaction spanning services |
| `lens-concurrency` | shared mutable state, async, worker, lock, idempotency key, read-modify-write, race-prone counter |
| `lens-observability` | new failure mode, background job, SLO claim, alerting change, log of a hot path |
| `lens-testing` | new behavior, bug fix, mocked boundary, flaky test, test deleted or skipped |
| `lens-accessibility` | UI component, form, modal, custom control, colour or contrast change, motion, keyboard flow |
| `lens-ux-content` | user-facing copy, error message, empty state, destructive action, onboarding, notification |
| `lens-i18n` | user-facing string, date, currency, number, sorting, name or address handling, RTL |
| `lens-operations` | deployment, feature flag, config, migration ordering, rollback, cost-bearing resource, runbook |
| `lens-maintainability` | long function, duplication, new abstraction, dead code, wide interface, added indirection |
| `lens-supply-chain` | new dependency, version bump, build script, CI change, published artifact, license-bearing code |
| `lens-llm-integration` | prompt, model call, tool definition, agent loop, untrusted text reaching a model, RAG retrieval |

## Phase Defaults

Used by the workflow commands when the user does not select lenses explicitly.

| Phase | Default lens set |
| ----- | ---------------- |
| **design** | requirements, architecture, domain-model, api-contract, data, security, privacy-compliance, reliability |
| **build** | architecture, maintainability, security, concurrency, data, testing, performance, api-contract |
| **qa** | requirements, testing, security, reliability, performance, observability, accessibility, operations |

Swap a default out when the target has no surface for it (no UI -> drop accessibility; no external
call -> drop reliability) and record the swap.
