---
name: finding-verification
description: |
  Falsification pass over review findings - actively tries to prove each finding wrong before it is
  reported, so that what survives is real. Activate when: a review produced candidate findings, a bot
  or reviewer reported an issue, or before acting on any audit result.
triggers: ["verify findings", "falsify", "is this a real bug", "false positive", "confirm the finding", "validate review results"]
harness:
  id: finding-verification
  phases: [design, build, qa]
  produces: verdicts
---

# Finding Verification

> The value of a review is not the number of findings it produces. It is the ratio of findings that
> are real. Every unfalsified finding costs a reader their attention and the harness its credibility.

## When To Run

After any red pass, and on any finding arriving from outside (a review bot, a static analyzer, a
colleague, a previous session). Never act on an unverified finding, and never report one as confirmed.

## The Falsification Question

For each candidate finding, do not ask "is this a problem?". Ask:

> **What would have to be true for this finding to be wrong - and is it true?**

Then go look. Verification is an act of reading, searching, or executing, not of reasoning about the
summary.

## Protocol

### 1. Restate the failure as a claim that can fail

Rewrite the finding as: *given `<state or input>`, the system does `<wrong thing>` instead of
`<right thing>`.* If it cannot be written this way, it is not a finding - it is a preference. Drop it.

### 2. Trace the path end to end

Walk from the entry point to the failure site. At each hop, ask what stops the failure here.
Record the actual hops:

```text
POST /orders (router.ts:22)
  -> validateBody (middleware/validate.ts:14)  <- does the schema reject qty <= 0? NO, min not set
  -> createOrder (service/order.ts:61)         <- no guard
  -> reserveStock (repo/stock.ts:40)           <- `stock -= qty` with qty = -5 increases stock
```

A break anywhere in the chain refutes the finding.

### 3. Run the refutation checklist

| Check | If yes |
| ----- | ------ |
| Is it already guarded upstream (framework, middleware, type, DB constraint)? | REFUTED |
| Is the input unreachable from an untrusted or realistic source? | REFUTED |
| Is the state unreachable given other invariants? | REFUTED |
| Does an existing test cover exactly this case, with a real assertion? | REFUTED |
| Is this documented intended behavior? | REFUTED - or becomes a `lens-requirements` finding about the doc |
| Is the fix already present on the base branch or in the diff? | REFUTED |
| Does the failure only occur under a configuration the project does not support? | REFUTED |

### 4. Attempt the cheapest empirical proof available

In order of preference:

1. Run the code path (script, REPL, unit test, curl).
2. Write the failing test and watch it fail.
3. Grep for the guard and show the count is zero.
4. Read the full source of every hop.

Reasoning alone yields `plausible` at best - never `confirmed`.

### 5. Assign a verdict

| Verdict | Requirement |
| ------- | ----------- |
| **CONFIRMED** | Every hop verified by reading or execution; no refutation check fired |
| **PLAUSIBLE** | Path is coherent but at least one hop is unverified; the unverified hop is named in the finding |
| **REFUTED** | Any refutation check fired; record which one, then drop the finding |

### 6. Re-check severity after verification

Verification often changes the impact. A finding whose only reachable caller is an admin script drops
a level. One that turns out to affect stored data rises. Re-apply the rubric with what you now know.

## Verification Ledger

Keep this while working; include only the reported rows in the final output.

| ID | Claim | Refutation attempted | Result | Verdict |
| -- | ----- | -------------------- | ------ | ------- |
| SEC-002 | Timing-unsafe token compare | Searched for constant-time helper; none imported | No guard found | CONFIRMED |
| PRF-004 | N+1 in order list | Read serializer; `select_related('items')` present at repo/order.py:18 | Guard exists | REFUTED |

## Handling Findings From Others

Bot findings, analyzer output and reviewer comments get the same treatment - they are candidate
findings, not facts. Two additional rules:

- A high-confidence tool with a bad rule is still wrong. Verify the specific instance, not the rule.
- When you refute an external finding, say what refutes it, with the anchor. "Not a bug" without an
  anchor is not an answer.

## Failure Modes To Avoid

- **Confirming by restatement.** Repeating the claim in different words is not verification.
- **Verifying the fix instead of the defect.** The question is whether the defect exists now.
- **Accepting a mocked test as proof.** A test that mocks the failing boundary proves nothing about it.
- **Downgrading instead of dropping.** A refuted finding is deleted, not demoted to Low.
- **Stopping at the first hop.** The guard you found may be bypassed by another caller - check callers.
