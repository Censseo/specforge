---
name: lens-maintainability
description: |
  Adversarial maintainability lens - finds code that is hard to change safely, plus stubs, fakes and
  dead code masquerading as implementation. Activate when: reviewing a diff, a refactor, an
  abstraction, or checking whether an implementation is real.
triggers: ["maintainability review", "code smell", "refactor review", "dead code", "fake implementation", "stub", "technical debt", "is this real"]
lens:
  id: maintainability
  prefix: MNT
  domain: Maintainability and code health
  applies_to: [code, tasks, config]
  phases: [build, qa]
  blocking_severity: high
---

# Maintainability Lens

**Failure this lens prevents**: code that passes review, looks complete, and is either unchangeable or
not actually implemented.

## Load First

The diff, the files it touches in full (not just the changed hunks), and the callers of anything it
changes.

## Part 1 - Is It Actually Implemented?

The highest-value probes. A stub that returns a plausible value passes tests, review and demos.

| # | Probe | Failure signature | Severity floor |
| - | ----- | ----------------- | -------------- |
| K1 | Placeholder returns on a production path | `return []`, `return {}`, `return true`, `return "ok"` with no logic | Critical |
| K2 | Empty implementation | Body is `pass`, `return`, or a comment | Critical |
| K3 | Validation that cannot fail | Validator always returns true; check with no branch | Critical |
| K4 | `NotImplementedError` / `throw new Error("TODO")` reachable in production | Stub on a live path | Critical |
| K5 | Mock or fixture data in production code | Fake emails, lorem ipsum, hardcoded sample records | Critical |
| K6 | Swallowed errors | `catch {}`, `except: pass`, error logged then success returned | High |
| K7 | Hardcoded bypass | `if (true)`, `// skip for now`, feature check that never fires | High |
| K8 | TODO / FIXME / HACK / XXX on a critical path | Marker in code the primary flow executes | High |
| K9 | Simulated work | `sleep` standing in for a real operation; random success | High |
| K10 | Debug output left behind | `console.log`, `print`, debugger statements | Medium |

## Part 2 - Is It Changeable?

| # | Probe | Failure signature | Evidence |
| - | ----- | ----------------- | -------- |
| K11 | Function does one thing | > 50 lines, multiple levels of abstraction in one body, "and" in the name | Function |
| K12 | Nesting is shallow | More than 3 levels; deeply nested conditionals | Location |
| K13 | Parameters are few and meaningful | > 4 parameters; boolean flags controlling behavior | Signature |
| K14 | Duplication has a single source | Same logic in 3+ places, drifting | All sites |
| K15 | Names say what things are | `data`, `info`, `manager`, `helper`, `process`, `tmp` on non-trivial concepts | Name |
| K16 | Magic values are named | Unexplained literals in logic | Literal |
| K17 | The abstraction earns its cost | Indirection with one implementation and no second caller in sight | Abstraction |
| K18 | Comments explain why, not what | Comments restating the code, or contradicting it | Comment |
| K19 | Dead code is absent | Unreferenced exports, orphaned files, unreachable branches, large commented-out blocks, stale flags | Symbol + search proving zero references |
| K20 | Public surface is minimal | Everything exported; internals reachable from outside | Module |
| K21 | The change fits the surrounding code | New idiom, style or pattern inconsistent with the file's conventions | Diff vs file |
| K22 | Altitude is consistent | Low-level detail interleaved with high-level orchestration in one function | Function |

## Attack Moves

- **The stub hunt**: grep the diff for the Part 1 signatures before reading anything else. This
  catches more real defects than any style review.
- **Zero-reference search**: for each new or suspicious export, search the whole repository. Report the
  pattern and the count, not an impression.
- **The change request**: name the most likely next modification to this code and count the files it
  touches. High count means the seams are wrong.
- **Read it aloud**: a function whose description needs "and" twice is doing too much.
- **Delete the abstraction**: inline it mentally. If the code gets clearer, the abstraction is cost
  without benefit.

## Severity Calibration

| Severity | Maintainability-specific |
| -------- | ------------------------ |
| Critical | Fake implementation on a production path (Part 1, K1-K5) |
| High | Swallowed errors, hardcoded bypasses, TODOs on a critical path, orphaned files or dead exports at scale, duplication of business logic |
| Medium | Long functions, deep nesting, unclear names, speculative abstractions, inconsistent idiom |
| Low | Formatting, comment style, ordering - and only when a linter does not already cover it |

## Common False Positives

- A stub in test code, a fixture file, or an interface definition. Check the file's role first.
- An empty implementation that satisfies an interface deliberately (a null object, a no-op handler).
- "Duplication" between two bounded contexts that change for different reasons.
- A long function that is a flat, linear sequence with no branching - length alone is not complexity.
- Dead code that is a published API of a library. Check whether the consumers are outside the repo.

## Output

Findings with prefix `MNT`. Report Part 1 findings first and separately - they are correctness
defects, not style. Never mix them into the same table as naming suggestions.
