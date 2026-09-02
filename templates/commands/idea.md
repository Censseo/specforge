---
description: Transform a raw idea into a structured vision document and decompose complex ideas into manageable features. Use this BEFORE /specforge.specify to enrich context and reduce ambiguity.
skills:
  - idea-shaping
  - lens-requirements
semantic_anchors:
  - Double Diamond        # Discover → Define → Develop → Deliver, divergent/convergent thinking
  - Jobs-to-Be-Done       # Outcome-focused: situation → motivation → outcome
  - User Story Mapping    # Backbone (activities) → Skeleton (tasks) → Ribs (stories)
  - Cynefin Framework     # Simple/Complicated/Complex/Chaotic - context-appropriate responses
  - YAGNI                 # You Aren't Gonna Need It - no speculative features
handoffs:
  - label: Specify Next Feature
    agent: specforge.specify
    prompt: Create a specification for the next unspecified feature
    send: true
  - label: Refine Idea Further
    agent: specforge.idea
    prompt: Continue refining the idea with additional context
  - label: Add More Features
    agent: specforge.idea
    prompt: Decompose additional features from the idea
---

## User Input

```text
$ARGUMENTS
```

## Method

Apply the **`idea-shaping`** skill: the discovery question set, the Cynefin calibration, the complexity
score, the feature-boundary rules and the document structure.

Use this before `/specforge.specify` when the request is vague, spans several capabilities, or names a
solution without naming a problem. Skip it for a clear single feature.

## Operational Steps

1. **Explore** (interactive). Ask the discovery questions in groups, not one at a time. Record the
   answers verbatim where they carry technical instruction - a paraphrase loses the constraint.

2. **Score the complexity** using the skill's signal table, then choose the output shape:

   | Score | Complexity | Output |
   | ----- | ---------- | ------ |
   | 0-3 | Simple | `idea.md` only |
   | 4-6 | Moderate | `idea.md` + 2-3 feature files |
   | 7-10 | Complex | `idea.md` + 4-6 feature files |
   | 10+ | Very complex | `idea.md` + features + an explicit phased approach |

3. **Cut the features** as vertical slices - each independently valuable and independently testable.
   Never cut by layer (database / API / frontend): none of those can ship alone.

4. **Create the directory**: `specs/{idea-slug}/` containing `idea.md` and, when decomposed,
   `features/##-feature-name.md`.

5. **Write `idea.md`** with: Vision, Problem Statement (the problem, the current situation, why now),
   Target Users (primary and secondary), Goals and Success Metrics, MVP Definition, Scope (in MVP /
   in future / explicitly out), Key Use Cases, Constraints and Assumptions, Features Overview with the
   dependency graph and implementation order, Open Questions and Risks, Discovery Notes.

   The Features Overview table drives everything downstream:

   ```markdown
   | # | Feature | Description | Priority | Dependencies | Status |
   | - | ------- | ----------- | -------- | ------------ | ------ |
   | 01 | user-auth | One sentence | P1/MVP | None | Not specified |
   ```

6. **Write each feature file** with: summary, use cases, in and out of scope, dependencies, technical
   hints, and a specification status block.

7. **Red pass** (score 7+): run `lens-requirements` over the idea before anyone specifies it. Vague
   goals and unstated assumptions are far cheaper to fix here.

## Report

Idea path, complexity score and the reasoning, features created with their priorities and dependencies,
the recommended implementation order, and open questions.

Next: `/specforge.specify` for the first feature in dependency order - or `/specforge.design` to run the
whole design phase for it.
