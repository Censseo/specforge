---
name: requirements-clarification
description: |
  Detect and remove ambiguity in a specification through targeted, one-at-a-time questions, and encode
  every answer back into the spec. Uses a coverage taxonomy, Socratic questioning and impact ranking.
  Activate when: a spec exists and may be underspecified, before planning.
triggers: ["clarify the spec", "ambiguities", "what is unclear", "clarification questions", "underspecified", "resolve open questions"]
semantic_anchors: [Socratic Method, Requirements Elicitation, INVEST Criteria, Cynefin Framework, Active Listening]
phase: design
---

# Requirements Clarification

> Ask few questions, ask the right ones, and write every answer into the spec the moment it is given.

Run before planning. Skipping it is allowed for an exploratory spike, but rework risk rises and that
should be said out loud.

## Step 1 - Coverage Scan

Mark each category Clear / Partial / Missing. This map drives prioritisation; it is not output unless
no questions are asked.

| Group | Categories |
| ----- | ---------- |
| Functional scope | Core goals, success criteria, explicit out-of-scope, roles and personas |
| Domain and data | Entities, attributes, relationships, identity rules, lifecycle, volume assumptions |
| Interaction | Critical journeys, error/empty/loading states, accessibility, localisation |
| Quality attributes | Performance, scalability, reliability, observability, security and privacy, compliance |
| Integrations | External services and their failure modes, import/export formats, protocol and versioning |
| Edge cases | Negative scenarios, rate limiting, conflict resolution, concurrency |
| Constraints | Technical constraints, explicit trade-offs, rejected alternatives |
| Terminology | Canonical glossary, avoided synonyms |
| Completion | Acceptance criteria testability, definition of done |
| Placeholders | TODO markers, unquantified adjectives ("robust", "intuitive") |

## Step 2 - Build the Question Queue

Rank candidates by **Impact x Uncertainty**. A question earns its place only if the answer changes
architecture, data modelling, task decomposition, test design, UX behavior, operational readiness or
compliance.

Exclude: questions already answered, stylistic preferences, and plan-level execution detail unless it
blocks correctness. Prefer questions that prevent misaligned acceptance tests.

## Step 3 - Ask, One at a Time

Every question is answerable as either a 2-5 option choice or a short phrase (<= 5 words).

**Always lead with your own recommendation.** The user should be able to answer "yes".

```markdown
**Recommended:** Option B - [one or two sentences of reasoning]

| Option | Description |
| ------ | ----------- |
| A | ... |
| B | ... |
| C | ... |
| Short | A different short answer (<= 5 words) |

Reply with a letter, "yes" to accept the recommendation, or your own short answer.
```

For a short-answer question: `**Suggested:** <answer> - <brief reasoning>`.

Rules:

- Never reveal the queue in advance.
- A clarification retry on the same question is not a new question.
- Stop when critical ambiguities are resolved, the user says stop, or the queue is empty.
- Ask as many as the ambiguity requires - there is no fixed quota.

## Step 4 - Integrate Each Answer Immediately

After **each** accepted answer, before asking the next:

1. Ensure `## Clarifications` exists, with a `### Session YYYY-MM-DD` subheading.
2. Append `- Q: <question> -> A: <answer>`.
3. Apply the answer to the section it belongs to:

| Answer type | Destination |
| ----------- | ----------- |
| Functional | Functional Requirements |
| Actor or role | User Stories / Actors |
| Data shape | Data Model |
| Quality attribute | Non-Functional Requirements, converted to a measurable target |
| Edge case | Edge Cases / Error Handling |
| Terminology | Normalised across the whole spec, once, with `(formerly "X")` if needed |

Then **replace** the now-invalid statement rather than adding beside it - contradictions left behind
are worse than the original ambiguity - and save the file after each integration.

## Step 5 - Validate

After each write and once at the end:

- One clarification bullet per accepted answer, no duplicates.
- No lingering placeholder that the answer was meant to resolve.
- No contradicting earlier statement.
- Only `## Clarifications` and `### Session YYYY-MM-DD` added as new headings.
- Terminology consistent across every touched section.

## Step 6 - Report

Questions asked and answered, spec path, sections touched, and a coverage table marking each category
Resolved / Deferred / Clear / Outstanding. Flag any high-impact category the user chose to defer.

## Failure Modes

- Batching questions and then integrating none of them.
- Asking about tech stack when functional clarity is what is missing.
- Recording the answer without amending the ambiguous text.
- Continuing to ask after the user has said "proceed".
