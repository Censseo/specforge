---
name: spec-authoring
description: |
  Write a feature specification that is testable, unambiguous and free of implementation detail, using
  EARS, INVEST, BDD Gherkin, Jobs-to-Be-Done and Specification by Example. Activate when: writing or
  revising a spec, user stories, functional requirements, acceptance scenarios or success criteria.
triggers: ["write a spec", "specification", "user stories", "functional requirements", "acceptance criteria", "ears", "spec this feature"]
semantic_anchors: [EARS Syntax, INVEST Criteria, Specification by Example, Jobs-to-Be-Done, BDD Gherkin]
phase: design
---

# Specification Authoring

> A specification is code written in English. It compiles into an implementation, and its bugs are
> ambiguities.

## What Belongs in a Spec

**WHAT** users need and **WHY**. Never HOW. No framework, table, endpoint or class names in a
functional requirement - unless an external constraint mandates them, in which case they belong in a
Constraints section, labelled as such.

Audience: someone who understands the business and not the codebase.

## Sources and Context

Before writing, load whichever apply:

| Source | Use |
| ------ | --- |
| `idea.md` / `features/##-*.md` | Vision, goals, use cases, technical hints |
| `/docs/{domain}/spec.md` | Existing entities, business rules, API patterns - reuse the terminology |
| `/memory/constitution.md` | Non-negotiable principles that become requirements |
| `specs/` agent context file | Domain vocabulary already in use |

Reusing an existing entity name matters more than inventing a better one.

## Writing Requirements - EARS

Every functional requirement follows one of five patterns:

| Pattern | Shape |
| ------- | ----- |
| Ubiquitous | The system shall `<response>` |
| Event-driven | When `<trigger>`, the system shall `<response>` |
| State-driven | While `<state>`, the system shall `<response>` |
| Optional | Where `<feature is included>`, the system shall `<response>` |
| Unwanted | If `<undesired condition>`, then the system shall `<response>` |

Every requirement must pass the INVEST "Testable" criterion: you can write the test that fails when
it is violated. If you cannot, the requirement is not finished.

## Writing Scenarios - Gherkin

```gherkin
Given <the precondition, concretely>
When <the actor does one thing>
Then <the observable outcome, with a value>
```

Each user story needs: the primary path, at least one error path, and the boundary cases that matter.
A story with only a happy path is half-specified.

## Framing Needs - Jobs-to-Be-Done

> When `<situation>`, I want to `<motivation>`, so I can `<outcome>`.

Write user stories this way before converting them to requirements. It keeps the outcome visible and
prevents solutions from being smuggled into the problem statement.

## Success Criteria

Measurable, technology-agnostic, user-observable.

| Good | Bad | Why |
| ---- | --- | --- |
| "Users complete checkout in under 3 minutes" | "API responds in under 200ms" | The user metric survives a rewrite |
| "System supports 10,000 concurrent users" | "React components render efficiently" | Framework-specific and unmeasurable |
| "95% of imports succeed without manual correction" | "Import is robust" | Robust is not a number |

## Handling the Unknown

Apply Convention over Configuration. Make an informed guess using industry standards and **write the
assumption down** in an Assumptions section. Do not ask about: data retention defaults, standard
error handling, common auth methods, ordinary integration patterns.

Use `[NEEDS CLARIFICATION: specific question]` only when:

- the answer changes scope materially, or
- multiple valid interpretations exist with different costs, or
- no reasonable convention applies.

Maximum three markers. Priority when choosing which three: scope > security and privacy > UX >
technical detail.

## Self-Validation Before Handing Off

Write `checklists/requirements.md` and evaluate the spec against it:

```markdown
## Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value, readable by a non-technical stakeholder

## Requirement Completeness
- [ ] Requirements are testable, unambiguous, with measurable success criteria
- [ ] Acceptance scenarios and edge cases identified
- [ ] Scope bounded; dependencies and assumptions stated

## Feature Readiness
- [ ] Every functional requirement has acceptance criteria
- [ ] User scenarios cover the primary flows and their failures
```

Iterate at most three times. Remaining failures get written down, not hidden.

## Presenting Open Questions

```markdown
## Question [N]: [Topic]

**Context**: [quote the relevant spec text]
**What we need to know**: [one specific question]

| Option | Answer | Implications |
| ------ | ------ | ------------ |
| A | ... | ... |
| B | ... | ... |
| Custom | Your own answer | ... |
```

Present all questions at once (max 3), then integrate the answers into the spec.

## Technical Hints

Technical guidance inherited from an idea is preserved, but quarantined:

```markdown
## Technical Hints (For Planning)

> Not part of the functional specification. Considered during planning.
```

Preserve commands, tools, libraries and execution order verbatim - substituting an "equivalent" tool
for one the author named is a common and expensive failure.

## Handoff

Next: `requirements-clarification` if ambiguity remains, otherwise `technical-planning`. Before either,
run `adversarial-review` with `lens-requirements`.
