---
name: lens-security
description: |
  Adversarial security lens - threat-models the change and hunts for authentication, authorization,
  injection, secret and exposure defects with a traced exploit path. Activate when: reviewing code
  handling input, auth, secrets, files, network calls or admin surfaces, or before any gate.
triggers: ["security review", "threat model", "vulnerability", "injection", "auth bypass", "secrets", "owasp", "is this secure"]
lens:
  id: security
  prefix: SEC
  domain: Application security
  applies_to: [spec, plan, contracts, data-model, code, config]
  phases: [design, build, qa]
  blocking_severity: critical
---

# Security Lens

**Failure this lens prevents**: an attacker doing something the system was never meant to permit.

This lens is for defensive review of code the team owns or is authorized to assess. Findings must
include a traced path from an untrusted input to a sink - never a generic warning.

## Load First

Entry points (routes, handlers, jobs, webhooks, CLI), authentication and authorization middleware,
anything touching secrets, and the trust boundaries in `plan.md`.

## Trust Model First

Before probing, write the boundaries down. Half of all security findings come from this table alone.

| Boundary | Untrusted side | What crosses it | What validates it |
| -------- | -------------- | --------------- | ----------------- |

Any row with an empty last column is a candidate finding.

## Probes

| # | Probe | Failure signature | Evidence to capture |
| - | ----- | ----------------- | ------------------- |
| S1 | Is every endpoint authenticated unless deliberately public? | Route added outside the auth middleware; public by omission | Route + middleware config |
| S2 | Is authorization checked per object, not just per role? | Any authenticated user can read another user's record by changing an id | Handler + missing ownership check |
| S3 | Are privileged operations gated at the server, not the UI? | Admin action protected only by hiding the button | Handler |
| S4 | Is user input concatenated into an interpreter? | String-built SQL, shell, LDAP, XPath, template or regex | Sink line |
| S5 | Is output encoded for its context? | User content into HTML, attributes, JS, or URLs without escaping | Render site |
| S6 | Are secrets absent from code, logs, errors and the repo? | Literal key, token in a log line, secret echoed in an error response | Line + what leaks |
| S7 | Is user-controlled data used to build a request target? | Server-side request forgery via a URL, hostname or redirect parameter | Fetch site |
| S8 | Is user-controlled data used to build a path? | Path traversal in upload, download or include | Path construction |
| S9 | Is deserialization limited to trusted data? | Pickle, YAML unsafe load, Java serialization on untrusted input | Sink |
| S10 | Is file upload constrained by type, size and storage location? | Any file, any size, stored in a served directory | Upload handler |
| S11 | Are tokens and sessions handled safely? | Predictable token, no expiry, no rotation on privilege change, non-constant-time compare | Token code |
| S12 | Is crypto used correctly? | Home-made crypto, ECB, static IV, MD5/SHA1 for passwords, fast hash for password storage | Crypto call |
| S13 | Are error responses free of internals? | Stack traces, SQL text, file paths, versions returned to clients | Error handler |
| S14 | Is rate limiting present on abusable endpoints? | Login, reset, search, export or expensive endpoints unlimited | Endpoint |
| S15 | Do secrets and permissions follow least privilege? | Wildcard IAM, DB superuser, token with more scope than needed | Config |
| S16 | Are dependencies with known vulnerabilities excluded? | Pinned version with a published advisory affecting a used code path | Package + advisory |
| S17 | Is CORS, CSP and cookie configuration restrictive? | `Access-Control-Allow-Origin: *` with credentials; `SameSite` unset; no CSP | Config |
| S18 | Are mass-assignment and over-posting prevented? | Request body bound directly to a model including role or id fields | Binding site |

## Attack Moves

- **STRIDE sweep** per boundary: Spoofing, Tampering, Repudiation, Information disclosure, Denial of
  service, Elevation of privilege. One pass per crossing, not per file.
- **Taint trace**: pick each untrusted source and follow it to every sink. Name the sanitizer at each
  hop, or the absence of one.
- **IDOR walk**: for every endpoint taking an identifier, ask what stops user A passing user B's id.
- **Privilege climb**: starting as the lowest-privilege actor, list every operation reachable. Compare
  with the intended permission matrix.
- **Log inspection**: grep the logging calls for request bodies, headers, tokens and personal data.

## Severity Calibration

| Severity | Security-specific |
| -------- | ----------------- |
| Critical | Unauthenticated remote impact, authorization bypass to other users' data, injection reaching a sink, secret committed or logged, RCE |
| High | Authenticated privilege escalation, sensitive data exposure to a lesser-privileged actor, weak crypto protecting real secrets, missing rate limit on credential endpoints |
| Medium | Defense-in-depth gap with another control in place, verbose errors, permissive CORS without credentials |
| Low | Hardening suggestion with no reachable exploit path |

## Common False Positives

- A "missing" check performed by framework middleware applied globally. Verify the middleware chain.
- Injection into an interpreter that only receives constants - confirm the value is actually
  attacker-influenced.
- A hardcoded value that is a test fixture or a public identifier. Check the file's role before
  calling it a leaked secret; report the location, not the value.
- Dependency advisories affecting a code path the project never calls. State the reachable path or
  drop the severity.

## Output

Findings with prefix `SEC`. Each must contain the traced path `source -> hop -> sink` and the smallest
fix. Never include a working exploit payload beyond what is needed to demonstrate reachability.
