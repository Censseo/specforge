# Attack and Probe Library

Cross-lens moves that generate findings. Use these when a lens's own probes come up empty - an empty
lens usually means the probes were read passively rather than executed against the artifact.

## Generic Falsification Moves

| Move | Question | Typical yield |
| ---- | -------- | ------------- |
| **Boundary walk** | What happens at 0, 1, max, max+1, empty, null, unicode, negative, duplicate? | Off-by-one, unhandled empty, overflow |
| **Adversarial input** | What does a hostile caller send here? | Injection, DoS, auth bypass |
| **Concurrency replay** | What if this runs twice, simultaneously, or out of order? | Races, double-charge, lost update |
| **Partial failure** | What if step 3 of 5 fails? What state remains? | Orphaned records, stuck jobs |
| **Scale shift** | What at 100x rows, 100x users, 100x payload? | N+1, memory blowup, timeout |
| **Time travel** | Clock skew, DST, leap day, expiry exactly now, retry after TTL | Expiry bugs, scheduling gaps |
| **Trust inversion** | Which input is trusted that shouldn't be? | Authorization holes, SSRF |
| **Absence check** | What is *not* here that should be? Search, prove absence | Missing validation, missing test |
| **Contract diff** | Does the implementation match its declared contract exactly? | Drift, undocumented behavior |
| **Rollback test** | Can this be undone? What breaks if we revert after 1 hour of traffic? | One-way doors, data loss |
| **Second reader** | Would a new engineer read this the way the author meant? | Ambiguity, misleading naming |
| **Requirement inversion** | Negate each requirement - does the system still pass its own tests? | Weak oracles, vacuous tests |

## Proving Absence

"Nothing validates this" is a claim that must be earned. Acceptable evidence:

- A search that was actually run, with the pattern and the result count.
- The full call path traced from entry point to sink with no guard found.
- The test file read end to end with the case absent.

Unacceptable: "I did not see any validation."

## Oracle Quality Check

Before trusting a passing test as evidence that a behavior is correct, check the oracle:

1. Would the test fail if the behavior were removed? (If not, it asserts nothing.)
2. Does it assert the outcome, or only that no exception was raised?
3. Does it mock the very thing it claims to verify?
4. Would it catch the failure scenario in the finding under review?

A test that fails all four is not coverage - its absence is itself a finding for `lens-testing`.

## De-escalation Checks

Run these before reporting, to avoid burning credibility:

- Is this already handled one layer up (framework, middleware, database constraint, type system)?
- Is the input actually reachable from an untrusted source, or only from internal callers?
- Is the state described actually reachable given the system's other invariants?
- Does a test already cover exactly this case?
- Is this the intended behavior, documented somewhere the review has not read yet?

Any "yes" refutes the finding. Drop it.
