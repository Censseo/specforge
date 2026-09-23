---
name: adversarial-review
description: |
  Adversarial review harness - runs a red-team pass over any artifact (spec, plan, contracts, code, config,
  migrations, docs) through domain lenses, then falsifies its own findings before reporting.
  Activate when: reviewing, auditing, red-teaming, "poke holes", validating a gate, or before merging/shipping.
triggers: ["adversarial review", "red team", "audit", "poke holes", "challenge this", "quality gate", "review harness", "find flaws"]
harness:
  id: adversarial-review
  phases: [design, build, qa]
  produces: findings, gate-verdict
  requires_skills: [finding-verification, quality-gates]
---

# Adversarial Review Harness

> A review is only useful when it can fail the thing under review. This harness makes failure
> reachable: it hunts for defects through explicit lenses, then tries to destroy its own findings
> before anyone acts on them.

## Core Contract

1. Every finding names a **concrete failure**: inputs or state -> wrong outcome. No failure path, no finding.
2. Every finding carries **evidence anchored to a location** (`file:line`, `spec.md §FR-003`, command output).
3. Every finding survives a **falsification attempt** before it is reported (see `finding-verification`).
4. Severity is assigned by **rubric**, not by feeling.
5. The harness returns a **verdict**, not a mood: PASS, PASS WITH CONDITIONS, or BLOCK.

## Protocol

### Step 1 - Frame the target

Establish, in five lines maximum, before reading anything else:

| Field | Meaning |
| ----- | ------- |
| Target | What is under review (paths, artifacts, diff range) |
| Intent | What this change is supposed to achieve |
| Invariants | What must remain true after the change |
| Blast radius | What breaks if this is wrong (users, data, money, safety) |
| Reversibility | One-way door or easily undone |

Blast radius and reversibility set the rigor: a one-way door with user data at stake justifies the
full lens sweep; a reversible internal refactor does not.

### Step 2 - Select lenses

Load `references/lens-registry.md` and pick lenses by artifact type and risk signal.
Rules:

- Always run the lenses marked **mandatory** for the artifact type.
- Add every lens whose **risk trigger** is present in the target.
- Cap at 8 lenses per pass. More lenses produce dilution, not coverage. If more than 8 trigger,
  run the pass in two waves ordered by blast radius.
- Record which lenses were skipped and why. An unrecorded skip is a silent hole.

### Step 3 - Red pass (one lens at a time)

For each selected lens, load its `lens-*` skill and run its probes. Working rules:

- **Assume the artifact is wrong.** The task is to find where, not to confirm it is fine.
- Work from the failure backwards: name a plausible bad outcome, then look for the path that reaches it.
- Read the actual artifact. A finding derived from the summary and not the source is a guess.
- Record candidate findings in the schema below. Do not self-censor here - filtering happens in Step 4.

### Step 4 - Falsification pass

Hand every candidate finding to `finding-verification`. For each, actively try to prove it wrong:
find the guard that already handles it, the caller that cannot pass that input, the test that covers it.

Verdicts:

| Verdict | Meaning | Reported? |
| ------- | ------- | --------- |
| CONFIRMED | The failure path was traced end to end and nothing prevents it | Yes |
| PLAUSIBLE | The path is real but one link is unverified; the unverified link is stated | Yes, flagged |
| REFUTED | Something already prevents the failure | No - dropped |

Drop refuted findings silently. Do not report them as "considered and dismissed" unless the user
asked for the reasoning trace.

### Step 5 - Triage and dedupe

- Merge findings that share a root cause, even across lenses. Report the root cause once, list the
  symptoms under it.
- Assign severity with the rubric below.
- Mark each finding blocking or advisory using the gate rules in `quality-gates`.
- Rank by (severity, confidence, fix cost) - most severe and most certain first.

### Step 6 - Verdict and report

Emit the report format below and a gate verdict. Never end an adversarial review without a verdict.

## Finding Schema

```yaml
id: SEC-002                      # <LENS-PREFIX>-<n>, stable within a report
lens: security
target: src/api/session.ts:88
claim: >                         # one sentence, the defect itself
  Session tokens are compared with == so a timing side channel leaks the token prefix.
failure_scenario: >              # inputs or state -> wrong outcome, concrete
  An attacker submits 10k tokens differing at byte 1..n and measures response time to
  recover the token byte by byte.
evidence:                        # anchored, quotable
  - src/api/session.ts:88 `if (token == stored)`
  - no constant-time helper imported in this module
severity: high                   # critical | high | medium | low
confidence: confirmed            # confirmed | plausible
blocking: true
fix: >                           # smallest change that removes the defect
  Replace with crypto.timingSafeEqual over Buffers of equal length.
verification: >                  # how anyone proves the fix worked
  Unit test asserting timingSafeEqual is called; benchmark shows no length correlation.
```

## Severity Rubric

Severity = worst credible **impact**, adjusted by **likelihood** and **reversibility**.

| Severity | Definition |
| -------- | ---------- |
| **Critical** | Data loss or corruption, security or privacy breach, money moved wrongly, safety impact, or total unavailability of the primary flow. Also: any violation of a constitution MUST. |
| **High** | A primary user story fails, a documented contract is broken, a requirement has no implementation, or recovery requires manual intervention. |
| **Medium** | A secondary flow degrades, an edge case is unhandled, an NFR target is missed without an outage, or maintenance cost grows materially. |
| **Low** | Cosmetic, stylistic, or a latent risk with no current failure path. |

Adjusters:

- Likelihood **remote** (requires an attacker with existing admin, or a state the system cannot reach): drop one level.
- Reversibility **one-way** (data migration, public API, deletion, external side effect): raise one level.
- Blast radius **all users** or **all tenants**: raise one level.
- Never adjust below Low or above Critical.

## What Is Not a Finding

Reject these before they reach the report - they are the noise that makes reviews ignorable:

- Anything a linter or formatter already enforces.
- A restatement of a requirement without a defect ("the spec says X" is not a finding).
- Speculation without a failure path ("this could maybe be slow").
- A preference dressed as a defect ("I would have used a factory here").
- A finding whose evidence is the artifact summary rather than the artifact.
- A duplicate of a finding already reported under another lens.
- A "consider" or "you might want to" with no consequence attached.

## Report Format

```markdown
## Adversarial Review: {target}

**Lenses run**: {list} | **Skipped**: {lens - reason} | **Verdict**: {PASS | PASS WITH CONDITIONS | BLOCK}

### Blocking Findings

| ID | Lens | Severity | Location | Claim | Fix |
| -- | ---- | -------- | -------- | ----- | --- |

### Advisory Findings

| ID | Lens | Severity | Location | Claim | Fix |
| -- | ---- | -------- | -------- | ----- | --- |

### Coverage

| Lens | Probes run | Findings | Notes |
| ---- | ---------- | -------- | ----- |

### Conditions to Clear the Gate

1. {finding id} - {what must be true to unblock}
```

## Anti-Gaming Rules

The harness is worthless if it learns to pass itself. These rules hold:

- A pass with zero findings is legitimate **only** if the coverage table shows the probes actually ran
  against real content. State what was checked and found sound.
- Never lower a severity to reach PASS. Change the verdict, not the rubric.
- Never convert a blocking finding to advisory because the fix is expensive. Cost belongs in the
  conditions, not in the severity.
- If the artifact cannot be evaluated (missing file, unreadable diff, no way to run the code),
  the verdict is BLOCK with reason `not-evaluable`, never PASS.

## References

- Lens catalogue and routing: `references/lens-registry.md`
- Finding schema and worked examples: `references/finding-schema.md`
- Attack and probe library: `references/attack-library.md`
- Falsification protocol: `finding-verification` skill
- Gate thresholds: `quality-gates` skill
