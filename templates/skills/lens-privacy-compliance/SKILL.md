---
name: lens-privacy-compliance
description: |
  Adversarial privacy and compliance lens - finds personal data that is collected without basis,
  retained without limit, exported without control or logged without need. Activate when: the change
  touches personal data, tracking, logging of user content, exports, retention or third-party sharing.
triggers: ["privacy review", "gdpr", "pii", "personal data", "retention", "compliance review", "data protection", "consent"]
lens:
  id: privacy-compliance
  prefix: PRV
  domain: Privacy and compliance
  applies_to: [spec, data-model, code, config, docs]
  phases: [design, qa]
  blocking_severity: high
---

# Privacy and Compliance Lens

**Failure this lens prevents**: holding data the organisation cannot justify, cannot delete, or cannot
explain.

This lens produces engineering findings, not legal advice. Where a question is genuinely legal
(lawful basis, cross-border transfer), the finding is "this decision is unrecorded and needs an owner".

## Load First

`data-model.md`, logging configuration, analytics and telemetry calls, third-party SDK usage, export
and reporting features, and any existing data inventory or privacy notice.

## Data Inventory First

| Field | Category | Source | Purpose | Lawful basis recorded? | Retention | Shared with |
| ----- | -------- | ------ | ------- | ---------------------- | --------- | ----------- |

Categories: identifier, contact, content, behavioural, location, financial, health, biometric,
special category, children's data. Any row with a blank cell is a candidate finding.

## Probes

| # | Probe | Failure signature | Evidence to capture |
| - | ----- | ----------------- | ------------------- |
| V1 | Is every collected field actually used? | Field collected "in case we need it" | Field + no reader |
| V2 | Is the purpose stated for each category? | Data used for a purpose the user was not told about | Field + use site |
| V3 | Does personal data reach logs? | Request bodies, emails, tokens, addresses in log lines | Log call |
| V4 | Does personal data reach third parties? | Analytics, error tracking or LLM calls carrying user content | Call site + payload |
| V5 | Is there a retention rule and a job that enforces it? | Unbounded retention; a policy with no deletion path | Table + missing job |
| V6 | Can a user's data actually be deleted or exported on request? | No path to find all records for a subject; data in blobs and backups unaccounted | Missing path |
| V7 | Is special-category or children's data handled with extra care? | Health, biometric, or under-age data treated like ordinary fields | Field |
| V8 | Is data minimised at each hop? | Full record passed where an id would do; over-broad SELECT feeding an external call | Call site |
| V9 | Is consent or preference respected in code? | Tracking that fires before consent; opt-out not checked at the call site | Call site |
| V10 | Is access to personal data restricted and auditable? | Any employee role can read all records; no audit trail on access | Authz + audit gap |
| V11 | Is data encrypted in transit and at rest where required? | Plaintext storage of sensitive fields; internal hop without TLS | Store or hop |
| V12 | Is cross-border transfer known? | Region unstated for a store or a vendor holding personal data | Config |
| V13 | Are anonymised or pseudonymised datasets actually so? | Re-identifiable "anonymous" data (rare combinations, retained keys) | Dataset |
| V14 | Are breach-relevant events detectable? | No way to tell which records were exposed if a token leaks | Missing signal |

## Attack Moves

- **Follow one user**: pick a single subject and trace every place their data lands - tables, caches,
  logs, queues, backups, third parties, exports. The list is usually longer than the model says.
- **Deletion drill**: given a deletion request, write the exact steps. Any step you cannot write is a
  finding.
- **Log grep**: search logging and error-reporting calls for the fields in the inventory.
- **Vendor sweep**: list every third party in the request path and what each receives.
- **Purpose test**: for each field, state the feature that breaks if it is removed. No answer means
  no purpose.

## Severity Calibration

| Severity | Privacy-specific |
| -------- | ---------------- |
| Critical | Special-category or children's data collected or exposed without control; personal data sent to an unapproved third party; credentials or full records in logs |
| High | No deletion or export path for personal data; unbounded retention of identifiable data; consent not enforced at the call site; unrestricted internal access |
| Medium | Over-collection with a plausible purpose; pseudonymisation that is reversible; missing region record |
| Low | Documentation gaps in the inventory where the practice itself is sound |

## Common False Positives

- Data that looks personal but is synthetic or public reference data. Verify the source.
- Logging of identifiers that are opaque and unlinkable outside the system. State the linkability.
- A missing deletion path for data under a legal retention obligation - that is a documented rule,
  not a gap, once recorded.

## Output

Findings with prefix `PRV`, plus the completed data inventory table. Route genuinely legal questions
to a named owner rather than answering them.
