---
description: Reference the catalogue of semantic anchors - named frameworks that SpecForge skills and commands activate - plus the shared severity and status vocabulary.
skills:
  - semantic-anchors
---

# Semantic Anchors

## Method

The full catalogue lives in the **`semantic-anchors`** skill: the anchor tables by discipline
(requirements engineering, testing, architecture, design principles, debugging, process, documentation,
elicitation, project management, quality assurance, code quality, pattern discovery, system design,
continuous improvement, adversarial review), the standard severity and status classifications, and the
anchor combinations that triangulate a mindset.

Load it when you need to:

- choose which mental models a piece of work should activate,
- declare the `semantic_anchors:` of a new command or skill,
- look up the canonical severity, validation status or bug status definitions.

## Why Anchors

Named frameworks activate rich context in far fewer tokens than describing the same discipline from
scratch.

Instead of:

> "Write requirements that are testable, unambiguous, and focused on user value with clear acceptance
> criteria that can be verified"

Write:

> "Apply EARS Syntax for requirements. Validate with INVEST criteria. Define acceptance via
> Specification by Example."

Fewer words, and a more precise mental model.

## Declaring Anchors

```markdown
---
description: Create feature specification
skills:
  - spec-authoring
semantic_anchors:
  - EARS Syntax
  - INVEST Criteria
  - Specification by Example
  - Jobs-to-Be-Done
---
```

Then reference them in the body where they apply, rather than restating what they mean.
