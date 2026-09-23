---
name: idea-shaping
description: |
  Turn a raw idea into a structured vision document and decompose complex ideas into independently
  specifiable features, using Double Diamond, Jobs-to-Be-Done, story mapping, Cynefin and YAGNI.
  Activate when: the request is vague, large, or spans several capabilities, before writing any spec.
triggers: ["explore this idea", "shape an idea", "vision document", "decompose feature", "break this into features", "is this too big", "scope this"]
semantic_anchors: [Double Diamond, Jobs-to-Be-Done, User Story Mapping, Cynefin Framework, YAGNI]
phase: design
---

# Idea Shaping

> The cheapest place to remove a feature is before it has a specification.

## When To Use

Use when the request is vague (under ~20 words of substance), spans multiple capabilities, or when the
user says "I want to build X" without saying what X does. Skip it for a clear single feature.

## Phase 1 - Discover (diverge)

Ask about the problem before the solution. Group questions, do not interrogate one at a time.

| Area | Questions |
| ---- | --------- |
| Problem | What is broken today? Who feels it? What does it cost them? |
| Users | Who is the primary user? Who else is affected? What do they use now? |
| Outcome | What is different after this exists? How would you know it worked? |
| Constraints | Deadline, budget, stack, compliance, team, existing systems |
| Non-goals | What are you deliberately not doing? |

Apply **Cynefin** to calibrate: a simple problem needs one round of questions; a complex one needs
probes and options, not a confident plan.

Apply **YAGNI** aggressively at this stage. Every capability mentioned "for later" goes into Future
Scope, not into the MVP.

## Phase 2 - Define (converge): complexity scoring

| Signal | Threshold |
| ------ | --------- |
| Multiple user types | > 2 primary users |
| Independent capabilities | > 3 distinct capabilities |
| Phased delivery | > 2 phases mentioned |
| Domain boundaries | > 1 domain |
| Integration points | > 2 integrations |
| Data entities | > 4 entities |

Score = number of thresholds crossed.

| Score | Complexity | Action |
| ----- | ---------- | ------ |
| 0-3 | Simple | Single `idea.md`, no decomposition |
| 4-6 | Moderate | `idea.md` + 2-3 feature files |
| 7-10 | Complex | `idea.md` + 4-6 feature files |
| 10+ | Very complex | `idea.md` + features + an explicit phased approach |

## Phase 3 - Feature boundaries

Cut features so that each is **independently valuable and independently testable**. Use User Story
Mapping: the backbone is the user's activity sequence; each feature is a vertical slice through it,
not a horizontal layer.

Bad cut: "database", "API", "frontend" - none can be delivered alone.
Good cut: "invite a teammate", "accept an invitation", "revoke access".

For each feature record: summary, use cases, in/out of scope, dependencies, priority, technical hints.

## Phase 4 - Document

`idea.md` sections: Vision, Problem Statement, Target Users, Goals and Success Metrics, MVP
Definition, Scope (in / future / explicitly out), Key Use Cases, Constraints and Assumptions,
Features Overview with a dependency graph and implementation order, Open Questions and Risks,
Discovery Notes.

Feature files (`features/##-name.md`) carry: summary, use cases, scope, dependencies, technical hints,
specification status.

## Discipline

- Record the questions you asked and the answers, verbatim where they carry technical instruction.
- Never invent a user need to justify a feature the user did not ask for.
- Every feature in the overview gets a priority and a dependency; unordered lists become unordered work.
- Preserve the user's technical instructions exactly, including command sequences and tool choices.

## Handoff

Next: `spec-authoring` per feature, in dependency order. Run `adversarial-review` with
`lens-requirements` on the idea before specifying if the score is 7 or higher.
