---
description: Create or update the feature specification from a natural language feature description or existing idea document.
semantic_anchors:
  - EARS Syntax           # Requirements patterns: Ubiquitous, Event-driven, State-driven
  - INVEST Criteria       # Story quality: Independent, Negotiable, Valuable, Estimable, Small, Testable
  - Specification by Example  # Concrete examples as specs, Gojko Adzic
  - Jobs-to-Be-Done       # Outcome-focused: situation → motivation → outcome
  - BDD Gherkin           # Given-When-Then acceptance scenarios
handoffs:
  - label: Build Technical Plan
    agent: speckit.plan
    prompt: Create a plan for the spec. I am building with...
  - label: Clarify Spec Requirements
    agent: speckit.clarify
    prompt: Clarify specification requirements
    send: true
  - label: Explore Idea First
    agent: speckit.idea
    prompt: Let me explore this idea before creating a formal specification
scripts:
  sh: scripts/bash/create-new-feature.sh --json "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 -Json "{ARGS}"
---

## User Input

```text
$ARGUMENTS
```

Consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/specforge.specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `{ARGS}` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

### Step 0: Detect Input Type and Load Context

<input_detection>

The input can be one of:

| Mode | Trigger | Example |
| ---- | ------- | ------- |
| Feature file | Path or number matching `features/##-*.md`, `##`, `feature ##` | `features/01-auth.md`, `01` |
| Idea | Path containing `idea.md` | `idea.md`, `specs/my-project/idea.md` |
| Description | Plain text (anything else) | `Add user authentication with OAuth2` |

#### Feature File Mode (decomposed idea)

1. Locate the feature file (by path or by finding `specs/*/features/##-*.md`)
2. Load the feature file as PRIMARY source — use its Summary, Use Cases, Scope, Dependencies
3. Load the PARENT idea.md for CONTEXT — use its Vision, Target Users, Goals, Features Overview, Constraints & Assumptions, Discovery Notes
4. Extract Technical Hints from both the idea's Constraints/Assumptions/Discovery Notes and the feature file's Technical Hints/Notes sections. These hints flow downstream to `/specforge.plan`.
5. Add source links in spec header:
   ```markdown
   **Source**: [Feature ##](./features/##-feature-name.md)
   **Parent Idea**: [idea.md](./idea.md)
   ```

#### Idea Mode (simple idea, no decomposition)

1. Load `idea.md` as primary source — use Vision, Problem Statement, Target Users, Goals, Scope, Use Cases
2. Extract Technical Hints from Constraints & Assumptions and Discovery Notes
3. Add source link: `**Source**: [idea.md](./idea.md)`

#### Description Mode (no idea document)

1. Use the plain text as the feature description
2. If an `idea.md` exists in the target directory, load it for additional context
3. If description is very vague (< 20 words), suggest `/specforge.idea` first

</input_detection>

<documentation_loading>

#### 0.3 Load Existing Documentation for Consistency

Before creating the specification, check for existing project documentation to ensure terminology and entity consistency:

1. If `/docs/README.md` exists, scan `/docs/*/spec.md` to list existing domains
2. Identify the relevant domain from the feature description (auth, payments, dashboard, etc.)
3. If domain exists, load `/docs/{domain}/spec.md` — extract existing features, entities, business rules, and API patterns
4. Use this context during specification: reuse entity names, follow domain patterns, ensure terminology consistency

If no `/docs` directory exists, proceed without domain context.

</documentation_loading>

#### 0.4 Feature File Status Update

After successfully creating a specification from a feature file:

1. Update the feature file status to `**Status**: Specified`
2. Update the feature's Specification Status table (`Specified: Yes`, link to spec file)
3. Update the parent idea.md Features Overview table status

Given that feature description (or idea document), do this:

### Steps 1-2: Branch Creation

1. **Generate a concise short name** (2-4 words) for the branch using action-noun format. Preserve technical terms.
   - "I want to add user authentication" → `user-auth`
   - "Create a dashboard for analytics" → `analytics-dashboard`

2. **Find the next available feature number** across all sources for the short-name:

   ```bash
   git fetch --all --prune
   ```

   Check remote branches (`git ls-remote --heads origin`), local branches (`git branch`), and `specs/` directories. Extract the highest number N from all sources and use N+1. If none found, start with 1.

3. **Run the script** `{SCRIPT}` with the calculated number and short-name:
   - Bash: `{SCRIPT} --json --number 5 --short-name "user-auth" "Add user authentication"`
   - PowerShell: `{SCRIPT} -Json -Number 5 -ShortName "user-auth" "Add user authentication"`

   Run this script exactly once per feature. Parse the JSON output for BRANCH_NAME and SPEC_FILE paths. For single quotes in args, use escape syntax: `'I'\''m Groot'` or double-quote.

### Step 3: Load Spec Template

Load `templates/spec-template.md` to understand required sections.

### Step 4: Generate Specification

Follow this execution flow:

1. Parse user description from Input — if empty: ERROR "No feature description provided"
2. Extract key concepts using Jobs-to-Be-Done lens: actors (who), actions (what), outcomes (why), constraints (boundaries)
3. For unclear aspects, apply Convention over Configuration — make informed guesses using industry conventions. Only mark with `[NEEDS CLARIFICATION: specific question]` when scope is significantly impacted, multiple valid interpretations exist, or no reasonable convention applies. Limit: max 3 markers. Prioritize: scope > security > UX > technical.
4. Fill User Scenarios using BDD Gherkin (Given-When-Then)
5. Generate Functional Requirements using EARS Syntax patterns — each requirement must pass INVEST "Testable" criterion
6. Define Success Criteria (SMART-style) — measurable, technology-agnostic outcomes verifiable via Specification by Example
7. Identify Key Entities (if data involved)
8. Include Technical Hints section if extracted from idea — preserve commands, tools, libraries, approaches, and execution order. Mark as "For implementation planning - not part of functional spec"
9. Return: SUCCESS (spec ready for planning)

### Step 5: Write the Specification

Write the specification to SPEC_FILE using the template structure, replacing placeholders with concrete details while preserving section order and headings.

If Technical Hints were extracted from the idea, append this section:

```markdown
---

## Technical Hints (For Planning)

> This section preserves technical guidance from the source idea.
> It is not part of the functional specification but should be considered during `/specforge.plan`.

### Source
- **Idea**: [path to idea.md]
- **Feature**: [path to feature file, if applicable]

### Technical Constraints
[From idea's Constraints & Assumptions section]

### Implementation Guidance
[Commands, tools, libraries, step-by-step procedures from idea]

### Discovery Decisions
[Key technical decisions from idea's Discovery Notes]
```

### Step 6: Specification Quality Validation

After writing the initial spec, validate it against quality criteria:

**a. Create Spec Quality Checklist** at `FEATURE_DIR/checklists/requirements.md`:

```markdown
# Specification Quality Checklist: [FEATURE NAME]

**Feature**: [Link to spec.md] | **Created**: [DATE]

## Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value, written for non-technical stakeholders

## Requirement Completeness
- [ ] Requirements are testable, unambiguous, with measurable success criteria
- [ ] All acceptance scenarios and edge cases identified
- [ ] Scope clearly bounded, dependencies and assumptions identified

## Feature Readiness
- [ ] All functional requirements have clear acceptance criteria
- [ ] User scenarios cover primary flows
- [ ] No implementation details leak into specification
```

**b. Run Validation**: Review the spec against each checklist item, documenting specific issues found.

**c. Handle Validation Results**:

- **All items pass**: Mark checklist complete, proceed to step 7
- **Items fail (excluding [NEEDS CLARIFICATION])**: List failures, update spec, re-validate (max 3 iterations). If still failing, document remaining issues and warn user.
- **[NEEDS CLARIFICATION] markers remain**: Keep only the 3 most critical (by scope/security/UX impact), make informed guesses for the rest. Present each as:

  ```markdown
  ## Question [N]: [Topic]
  **Context**: [Quote relevant spec section]
  **What we need to know**: [Specific question]

  | Option | Answer | Implications |
  |--------|--------|--------------|
  | A      | [First answer]  | [Impact] |
  | B      | [Second answer] | [Impact] |
  | C      | [Third answer]  | [Impact] |
  | Custom | Your own answer | [How to provide] |
  ```

  Present all questions together (max 3, numbered Q1-Q3). Wait for user responses, update spec, re-validate.

**d. Update Checklist** after each validation iteration with current pass/fail status.

### Step 7: Report Completion

Report completion with branch name, spec file path, checklist results, and readiness for the next phase (`/specforge.clarify` or `/specforge.plan`).

The script creates and checks out the new branch and initializes the spec file before writing.

## General Guidelines

> **Activated Frameworks**: Apply EARS Syntax for unambiguous requirements. Validate stories with INVEST criteria. Use Specification by Example for acceptance criteria. Frame needs as Jobs-to-Be-Done.

- Focus on **WHAT** users need and **WHY** (Jobs-to-Be-Done: "When [situation], I want [action], so I can [outcome]")
- Avoid HOW to implement (no tech stack, APIs, code structure)
- Written for business stakeholders, not developers
- Requirements should pass INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable
- Do not create checklists embedded in the spec — that is a separate command
- Mandatory sections: complete for every feature. Optional sections: include only when relevant, remove entirely if N/A.

### For AI Generation

> **Apply**: Convention over Configuration, Principle of Least Astonishment, YAGNI

When creating a spec from a user prompt:

1. **Make informed guesses** using industry standards and common patterns
2. **Document assumptions** in the Assumptions section
3. **Limit clarifications** to max 3 `[NEEDS CLARIFICATION]` markers — only for scope-altering, multi-interpretation, or no-convention-applies situations
4. **Prioritize**: scope > security/privacy > UX > technical details
5. **INVEST validation**: Every requirement must be Testable

Reasonable defaults (do not ask about these): data retention, performance targets, error handling, authentication method, integration patterns — use industry-standard practices.

### Success Criteria Guidelines

> **Apply**: SMART criteria adapted for features

Success criteria must be measurable, technology-agnostic, user-focused, and verifiable via Specification by Example.

**Good**: "Users complete checkout in under 3 minutes" | "System supports 10,000 concurrent users"
**Bad**: "API response under 200ms" (use user-facing metric instead) | "React components render efficiently" (framework-specific)
