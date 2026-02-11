---
description: Transform a raw idea into a structured vision document and decompose complex ideas into manageable features. Use this BEFORE /specforge.specify to enrich context and reduce ambiguity.
semantic_anchors:
  - Double Diamond        # Discover → Define → Develop → Deliver, divergent/convergent thinking
  - Jobs-to-Be-Done       # Outcome-focused: situation → motivation → outcome
  - User Story Mapping    # Backbone (activities) → Skeleton (tasks) → Ribs (stories)
  - Cynefin Framework     # Simple/Complicated/Complex/Chaotic - context-appropriate responses
  - YAGNI                 # You Aren't Gonna Need It - no speculative features
handoffs:
  - label: Specify Next Feature
    agent: speckit.specify
    prompt: Create a specification for the next unspecified feature
    send: true
  - label: Refine Idea Further
    agent: speckit.idea
    prompt: Continue refining the idea with additional context
  - label: Add More Features
    agent: speckit.idea
    prompt: Decompose additional features from the idea
---

## User Input

```text
$ARGUMENTS
```

Consider the user input before proceeding (if not empty).

## Purpose

> **Activated Frameworks**: Double Diamond for discovery (diverge then converge), Jobs-to-Be-Done for user outcomes, User Story Mapping for feature decomposition, Cynefin for complexity assessment.

The `/specforge.idea` command transforms a raw idea into a comprehensive vision document and decomposes complex ideas into smaller, manageable features. This is the **Discover** phase of Double Diamond.

**Workflow position**: `idea` → `specify` (per feature) → `clarify` → `plan` → `tasks` → `implement`

**Key principle**: Apply YAGNI - complex ideas should not be specified as a single monolithic feature. Break them into focused features that can be specified, planned, and implemented independently.

## Outline

The text the user typed after `/specforge.idea` is the raw idea. Your goal is to:

1. Enrich it through structured exploration
2. Assess complexity and identify natural boundaries
3. Decompose into features if complexity warrants it

### Phase 1: Idea Exploration (Interactive)

Conduct a focused discovery session with **5-7 questions maximum** across these dimensions:

#### 1.1 Problem & Context Discovery

Acknowledge the idea and identify what's missing. Ask questions ONE AT A TIME from:

- **Problem Space** (1-2 questions): What problem does this solve? Who has it? What triggers the need? How is it addressed today?
- **Users & Stakeholders** (1-2 questions): Primary users and roles? Secondary stakeholders? Technical proficiency?
- **Goals & Success** (1-2 questions): What does success look like? MVP vs. full vision? Timeline?
- **Constraints & Context** (1-2 questions): Technical constraints? Business constraints? What's out of scope?

#### 1.2 Question Format

For each question:

1. Provide context for why you're asking (1 sentence)
2. Ask the question clearly
3. Offer suggestions when helpful - either a **Suggested answer** with reasoning, or a table of options (A/B/C) the user can pick from
4. Accept short answers - don't require long explanations

#### 1.3 Adaptive Questioning

- **Skip questions** if the initial idea already provides the answer
- **Infer reasonable defaults** for non-critical aspects (document them as assumptions)
- **Stop early** if you have enough context (user says "done", "that's all", etc.)
- **Prioritize** questions that most reduce ambiguity for specification

### Phase 2: Complexity Analysis

After gathering context, assess whether the idea needs decomposition.

#### 2.1 Complexity Indicators

| Signal | Threshold |
| ------ | --------- |
| **Multiple user types** | > 2 primary users |
| **Independent capabilities** | > 3 distinct capabilities |
| **Phased delivery** | > 2 phases mentioned |
| **Domain boundaries** | > 1 domain |
| **Integration points** | > 2 integrations |
| **Data entities** | > 4 entities |

#### 2.2 Complexity Score

```text
Score = (user_types × 1) + (capabilities × 1.5) + (phases × 1) +
        (domains × 2) + (integrations × 1) + (entities × 0.5)
```

| Score | Complexity | Action |
| ----- | ---------- | ------ |
| 0-3 | Simple | Single `idea.md`, no decomposition |
| 4-6 | Moderate | `idea.md` + 2-3 feature files |
| 7-10 | Complex | `idea.md` + 4-6 feature files |
| 10+ | Very Complex | `idea.md` + features + suggest phased approach |

#### 2.3 Identify Feature Boundaries

If complexity score >= 4, identify natural feature boundaries using one of these lenses:

1. **By User Journey**: Group by workflow stages (e.g., "Onboarding", "Core Usage", "Administration")
2. **By Domain**: Separate business domains (e.g., "Authentication", "Payments", "Notifications")
3. **By Priority**: MVP vs. future phases
4. **By Independence**: Features that can be built/deployed independently

Each feature needs: an action-oriented name (2-4 words), a one-sentence description, and identified dependencies.

### Phase 3: Document Generation

#### 3.1 Create Idea Directory

```bash
NEXT_NUM=$(ls -d ideas/[0-9][0-9][0-9]-* 2>/dev/null | sed 's/.*\/\([0-9]*\)-.*/\1/' | sort -n | tail -1 | awk '{print $1+1}')
NEXT_NUM=${NEXT_NUM:-1}
IDEA_NUM=$(printf "%03d" $NEXT_NUM)
mkdir -p "ideas/${IDEA_NUM}-<short-name>/features"
```

**Directory structure**:

```text
ideas/###-<short-name>/
├── idea.md                    # High-level vision (always created)
└── features/                  # Feature files (if complexity ≥ 4)
    ├── 01-<feature-name>.md
    └── 02-<feature-name>.md

.speckit/                              # Created later by /specforge.specify
├── ###-<short-name>/                  # Spec for simple idea (complexity < 4)
└── ###-01-<feature-name>/             # Spec per feature (complexity ≥ 4)
```

#### 3.2 Write Idea Document

Create `ideas/###-<short-name>/idea.md` using this structure:

````markdown
# Idea: [CONCISE TITLE]

**Created**: [DATE]
**Status**: Exploration
**Short Name**: [short-name]

## Vision

[One paragraph elevator pitch: What is this? Who is it for? Why does it matter?]

## Problem Statement

### The Problem
[Clear description of the problem being solved]

### Current Situation
[How users currently deal with this - workarounds, pain points, gaps]

### Why Now?
[What triggers the need for this solution]

## Target Users

### Primary Users
- **[Persona 1]**: [Role, needs, technical level, key motivations]
- **[Persona 2]**: [Role, needs, technical level, key motivations]

### Secondary Stakeholders
- [Other affected parties and their interests]

## Goals & Success Metrics

### Primary Goals
1. [Goal with measurable outcome]
2. [Goal with measurable outcome]

### Success Indicators
- [How you'll know this succeeded - quantitative if possible]

### MVP Definition
[What's the minimum viable version that delivers value?]

## Scope

### In Scope (MVP)
- [Feature/capability 1]
- [Feature/capability 2]

### In Scope (Future)
- [Features for later phases]

### Explicitly Out of Scope
- [What this will NOT do - important boundaries]

## Key Use Cases (Sketches)

### Use Case 1: [Title]
**Actor**: [Who]
**Goal**: [What they want to achieve]
**Flow**:
1. [Step 1]
2. [Step 2]
3. [Expected outcome]

### Use Case 2: [Title]
[Same structure]

## Constraints & Assumptions

### Known Constraints
- **Technical**: [Platform, integration, existing system constraints]
- **Business**: [Budget, timeline, team, compliance constraints]
- **User**: [Accessibility, language, device constraints]

### Assumptions
- [Assumption 1 - things we're assuming to be true]
- [Assumption 2 - defaults we've chosen]

## Features Overview

<!--
  Populated when complexity analysis identifies multiple features.
  Leave empty for simple ideas (complexity score < 4).
-->

**Complexity Score**: [X]/10 - [Simple|Moderate|Complex|Very Complex]

### Feature Breakdown

| # | Feature | Description | Priority | Dependencies | Status |
|---|---------|-------------|----------|--------------|--------|
| 01 | [feature-name] | [One sentence] | P1/MVP | None | 🔲 Not specified |
| 02 | [feature-name] | [One sentence] | P1/MVP | 01 | 🔲 Not specified |

**Status Legend**: 🔲 Not specified → 📝 Specified → ✅ Implemented

### Feature Dependencies Graph

```text
[01-core-feature]
    └── [02-dependent-feature]
[03-independent-feature]
```

### Implementation Order

1. **Phase 1 (MVP)**: 01, 02, ...
2. **Phase 2**: 03, 04, ...

## Open Questions & Risks

### Questions to Resolve
- [Question that needs answering before or during specification]

### Identified Risks
- [Risk 1]: [Potential mitigation]

## Discovery Notes

### Session [DATE]
- Q: [Question asked] → A: [Answer given]

## Technical Hints

<!--
  Capture technical requirements to preserve through specification,
  planning, and implementation.
-->

### Required Commands/Scripts

| Order | Command/Script | Purpose |
|-------|----------------|---------|
| 1 | [command] | [what it does] |

### Required Tools & Versions

- **[Tool/Library]**: [version] - [why required]

### Integration Sequences

[Describe integration patterns or protocols if applicable]

### Implementation Notes

- [Technical note that must be preserved]
````

#### 3.3 Generate Feature Files (if complexity >= 4)

For each identified feature, create `ideas/###-<short-name>/features/##-feature-short-name.md`:

```markdown
# Feature: [FEATURE TITLE]

**Parent Idea**: [Link to idea.md]
**Feature ID**: ##
**Priority**: P1/P2/P3
**Status**: Not Specified

## Summary

[2-3 sentences describing this specific feature and its value]

## User Value

**Who benefits**: [Specific user persona from idea.md]
**What they gain**: [Concrete benefit]
**Success metric**: [How to measure this feature's success]

## Scope

### This Feature Includes
- [Capability 1]
- [Capability 2]

### This Feature Does NOT Include
- [Explicitly excluded - may be in another feature]

## Key Use Cases

### Use Case 1: [Title]
**Actor**: [Who]
**Goal**: [What they want]
**Flow**:
1. [Step]
2. [Step]
3. [Expected outcome]

## Dependencies

### Requires
- [Feature ##]: [What this feature needs from it]

### Enables
- [Feature ##]: [What this feature provides to it]

## Technical Hints

### Required Commands/Scripts

| Order | Command/Script | Purpose |
|-------|----------------|---------|
| 1 | [command] | [what it does] |

### Required Tools & Versions

- **[Tool/Library]**: [version] - [why required]

### Implementation Notes

- [Technical constraint]

## Open Questions

- [Questions specific to this feature]

## Notes

[Any additional context for specification]
```

#### 3.4 Validation Checklist

Before completing, verify:

- [ ] Vision is clear; problem is well-defined (not solution-first thinking)
- [ ] Target users identified with needs; at least 2-3 use cases sketched
- [ ] MVP scope defined and bounded; out-of-scope items explicit
- [ ] Success metrics measurable; constraints documented; complexity score calculated
- [ ] If complexity >= 4: features have focused scopes, documented dependencies, no overlaps, logical order

### Phase 4: Completion

Save all documents (`idea.md` always, `features/*.md` if complexity >= 4), then report:

**For simple ideas (complexity < 4)**: Show file path, vision summary, primary users, MVP scope, complexity score, open question count, and next step (`/specforge.specify ideas/###-<short-name>`).

**For complex ideas (complexity >= 4)**: Show idea file path, features directory, vision summary, complexity rating, feature table (name, priority, status), recommended implementation order, and next step (`/specforge.specify` with the first feature path).

**Handoff options**:

- `/specforge.specify` with feature number or path to specify
- `/specforge.idea` to add more features or details
- Edit documents directly for manual refinement

## Guidelines

- Be conversational - this is exploration, not interrogation. Make suggestions, offer your best guesses, and let the user accept or override them.
- Infer sensible defaults. Focus on the "what" and "why", not the "how" (that comes in planning).
- Keep the idea doc to 1-3 pages. Aim for 5-7 questions max; stop when you have enough.
- Decompose complexity into focused, independent features with mapped dependencies, but don't force decomposition on simple ideas.
- Avoid implementation details (tech stack, architecture, code). Always define the MVP; without it, scope tends to creep.

If limited to few questions, prioritize: (1) problem validation, (2) primary user, (3) success definition, (4) scope boundaries, (5) constraints.

### Handling Ideas by Detail Level

**Vague ideas** (e.g., "an app for photos"): Start with the problem, identify the user, find the one thing it does well, then build from there.

**Detailed ideas**: Summarize what you understood, ask only for missing pieces, confirm assumptions, move quickly to document generation.

**Complex ideas** (score >= 4): Explain the decomposition, present proposed features in a table for confirmation, confirm dependencies, suggest phasing for very complex ideas, then generate idea.md first followed by each feature file.

### Examples

**Simple idea** (no decomposition):
> "Add a dark mode toggle to the settings page"

Complexity: ~2 (single capability, one user type, no integrations) → Create idea.md only

**Complex idea** (4+ features):
> "Create an e-commerce platform with product catalog, shopping cart, checkout, user accounts, order management, and analytics"

Complexity: ~9 (6 capabilities, 2 user types, multiple integrations)
→ Features: `01-user-accounts`, `02-product-catalog`, `03-shopping-cart`, `04-checkout`, `05-order-management`, `06-analytics`
→ Recommend phased approach: MVP (01-04), Phase 2 (05-06)
