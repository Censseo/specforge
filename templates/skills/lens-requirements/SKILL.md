---
name: lens-requirements
description: |
  Adversarial requirements lens - attacks a spec, idea or task list for ambiguity, untestability,
  missing scenarios and unstated assumptions. Activate when: reviewing a spec, an idea, acceptance
  criteria or a task breakdown, or before the design gate.
triggers: ["review spec", "requirements review", "is this spec clear", "ambiguous requirement", "testable requirement", "acceptance criteria review"]
lens:
  id: requirements
  prefix: REQ
  domain: Requirements engineering
  applies_to: [idea, spec, tasks, contracts, docs]
  phases: [design, qa]
  blocking_severity: high
---

# Requirements Lens

**Failure this lens prevents**: building the wrong thing correctly, or building something whose
correctness nobody can decide.

## Load First

`spec.md`, the source `idea.md` if referenced, `/memory/constitution.md`, and any existing
`checklists/`. Read the actual requirement text - not a summary of it.

## Probes

| # | Probe | Failure signature | Evidence to capture |
| - | ----- | ----------------- | ------------------- |
| R1 | Can each requirement fail? Write the test that would fail if it were violated | No observable behavior; nothing to assert | Requirement id + why no oracle exists |
| R2 | Are quantities quantified? | "fast", "scalable", "robust", "intuitive", "secure", "soon", "large" with no number | Quoted adjective + section |
| R3 | Is the actor named for every behavior? | Passive voice hiding who acts ("the data is validated") | Requirement id |
| R4 | Does every user scenario have Given / When / Then with a concrete outcome? | Scenarios that stop at the action | Scenario id |
| R5 | Are the negative paths specified? | Only happy paths; no error, empty, denied, expired, conflicting cases | List of missing paths |
| R6 | Are the boundaries stated? | No min/max, no limits, no pagination rule, no size cap | Requirement id |
| R7 | Is out-of-scope stated explicitly? | No exclusions section, so scope is unbounded | Spec section |
| R8 | Do two requirements conflict? | Same subject, incompatible rules | Both ids, quoted |
| R9 | Is the same concept named consistently? | Synonym drift (user / account / member) across sections | Term map |
| R10 | Does every requirement trace to a goal, and every goal to a requirement? | Orphan requirement (gold plating) or uncovered goal | Traceability gap |
| R11 | Are success criteria measurable and technology-agnostic? | Criteria naming frameworks, or with no metric | Criterion text |
| R12 | Are assumptions written down as assumptions? | Hidden assumption discovered only by asking | Assumption + where it hides |
| R13 | Does the spec leak implementation? | Framework, table, endpoint or class names in a functional requirement | Quoted leak |
| R14 | Do unresolved markers remain? | `[NEEDS CLARIFICATION]`, TODO, TKTK, `???`, `<placeholder>` | Marker + impact on scope |
| R15 | Are non-functional requirements present at all? | No performance, availability, security, privacy, accessibility, or retention statement | Missing category list |
| R16 | Would two competent engineers build the same thing from this? | Two defensible readings exist | Both readings, stated |

## Attack Moves

- **Malicious compliance**: implement the requirement exactly as written, in the cheapest way that
  satisfies the letter. If the result is useless or absurd, the requirement is underspecified.
- **Requirement inversion**: negate the requirement. If the negation would also pass the stated
  acceptance criteria, the criteria assert nothing.
- **Scenario gap sweep**: for each entity, walk create / read / update / delete / list / restore /
  concurrent-edit / permission-denied. Name the ones the spec never mentions.
- **The new hire test**: read only the spec and list every question you would have to ask before
  writing a line of code. Each question is a candidate finding.
- **Number hunt**: list every quantity the system must respect (timeouts, limits, sizes, retention,
  concurrency). Mark the ones with no value in the spec.

## Severity Calibration

| Severity | Requirements-specific |
| -------- | --------------------- |
| Critical | Conflicting requirements on a primary flow, or a MUST from the constitution unaddressed |
| High | A primary-flow requirement is untestable, or a primary scenario has no acceptance criteria |
| Medium | A secondary path is unspecified, a quantity is missing, or terminology drifts |
| Low | Wording, ordering, or redundancy with no ambiguity |

## Common False Positives

- A quantity deliberately deferred to the plan, with the deferral written down. Not a finding.
- Terminology that differs because the domains genuinely differ (a `user` and an `account` may be
  distinct entities). Check the glossary before claiming drift.
- Missing NFR sections in a spec whose template puts them in `plan.md`. Check where they live first.
- An "implementation leak" that is actually a hard external constraint (a mandated protocol, a
  regulator-specified format). Constraints belong in the spec.

## Output

Findings with prefix `REQ`. For each ambiguity, propose the disambiguating question in the form
`quality-checklists` and `requirements-clarification` can consume directly:

```markdown
| ID | Requirement | Defect | Question to resolve it | Severity |
| -- | ----------- | ------ | ---------------------- | -------- |
```
