---
name: lens-architecture
description: |
  Adversarial architecture lens - attacks a plan, ADR or code structure for boundary violations,
  hidden coupling, unjustified novelty and irreversible decisions. Activate when: reviewing a
  technical plan, an ADR, a new module or a structural refactor.
triggers: ["architecture review", "review the plan", "is this design sound", "coupling", "boundaries", "ADR review", "design review"]
lens:
  id: architecture
  prefix: ARC
  domain: Software architecture
  applies_to: [plan, adr, code, config, contracts]
  phases: [design, build]
  blocking_severity: high
---

# Architecture Lens

**Failure this lens prevents**: a structure that is expensive to change later, chosen for reasons
nobody wrote down.

## Load First

`plan.md`, `/memory/architecture-registry.md`, `/memory/constitution.md`, existing module layout, and
the actual import graph of the touched area.

## Probes

| # | Probe | Failure signature | Evidence to capture |
| - | ----- | ----------------- | ------------------- |
| A1 | Does the dependency rule hold? | Domain imports infrastructure; inner layer knows outer layer | Import line, both module paths |
| A2 | Is each boundary crossed through an explicit port? | Direct SDK, ORM or HTTP client call inside domain logic | Call site |
| A3 | Could this have reused something that already exists? | New component duplicating a registry entry | Existing component path + overlap |
| A4 | Is every new pattern justified against the registry? | Divergence with no rationale recorded | Registry entry vs plan section |
| A5 | Is the decision reversible, and if not, is that stated? | One-way door (public API, data format, vendor lock) presented as routine | Decision + what makes it one-way |
| A6 | Were alternatives considered and rejected with reasons? | ADR with one option | ADR section |
| A7 | Does the component count match the problem size? | Service, queue or cache introduced for a problem that fits in a function | Component + workload it serves |
| A8 | Where does state live, and who owns it? | Two components writing the same data | Both writers |
| A9 | What happens when a dependency is unavailable? | Synchronous chain with no degradation path | Chain, hop by hop |
| A10 | Is the failure domain contained? | One component's failure takes down unrelated flows | Shared resource |
| A11 | Are cross-cutting concerns handled once? | Auth, logging, validation reimplemented per module | Duplicated implementations |
| A12 | Does the module map to a real domain concept? | `utils`, `helpers`, `common`, `manager` as a home for unrelated things | Module contents |
| A13 | Can this be tested without the whole system running? | No seam; every test needs the full stack | Component + missing seam |
| A14 | Does the plan say how the system evolves? | No migration or extension path for the obvious next requirement | Plan gap |
| A15 | Is the coupling direction the stable one? | Stable module depends on volatile one | Both modules + change rates |

## Attack Moves

- **Change simulation**: pick the three most likely next requirements. Trace which files each would
  touch. If a small requirement touches many modules, the boundaries are wrong.
- **Delete test**: for each new abstraction, ask what breaks if it is removed and the call inlined.
  If nothing breaks, it is speculative generality.
- **Vendor removal**: name the work to replace each external dependency. If a swap touches domain
  code, the port is missing.
- **Two-team test**: could two teams own the two sides of this boundary without a daily meeting?
- **Registry diff**: line up every decision against `architecture-registry.md`. Every divergence is
  either an approved evolution or drift; there is no third option.

## Severity Calibration

| Severity | Architecture-specific |
| -------- | --------------------- |
| Critical | An irreversible decision made without alternatives or approval; a boundary violation that makes correctness unverifiable |
| High | Dependency-rule violation, duplicated ownership of state, single point of failure on the primary flow, unjustified divergence from the registry |
| Medium | Speculative abstraction, weak seam that forces integration-only testing, cross-cutting logic duplicated |
| Low | Naming or placement that does not obscure the design |

## Common False Positives

- Duplication that is deliberate decoupling. Two similar shapes in two bounded contexts are not DRY
  violations; check whether they change for the same reason.
- A "missing abstraction" for a case that has occurred once. Two occurrences is a pattern, one is not.
- A layering violation inside a framework's own conventions (a Rails model, a Django view) - judge
  against the framework's grain, not an abstract ideal.
- A monolith is not a finding. Complexity that is not needed is.

## Output

Findings with prefix `ARC`. For any divergence from `/memory/architecture-registry.md`, state whether
it should be approved and registered, or reverted.
