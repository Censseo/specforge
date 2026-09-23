---
description: Create or update the feature specification from a natural language feature description or existing idea document.
skills:
  - spec-authoring
  - lens-requirements
semantic_anchors:
  - EARS Syntax           # Requirements patterns: Ubiquitous, Event-driven, State-driven
  - INVEST Criteria       # Story quality: Independent, Negotiable, Valuable, Estimable, Small, Testable
  - Specification by Example  # Concrete examples as specs, Gojko Adzic
  - Jobs-to-Be-Done       # Outcome-focused: situation → motivation → outcome
  - BDD Gherkin           # Given-When-Then acceptance scenarios
handoffs:
  - label: Build Technical Plan
    agent: specforge.plan
    prompt: Create a plan for the spec. I am building with...
  - label: Clarify Spec Requirements
    agent: specforge.clarify
    prompt: Clarify specification requirements
    send: true
  - label: Explore Idea First
    agent: specforge.idea
    prompt: Let me explore this idea before creating a formal specification
scripts:
  sh: scripts/bash/create-new-feature.sh --json "{ARGS}"
  ps: scripts/powershell/create-new-feature.ps1 -Json "{ARGS}"
---

## User Input

```text
$ARGUMENTS
```

The text the user typed after `/specforge.specify` **is** the feature description. Do not ask them to
repeat it unless the command was empty.

## Method

Apply the **`spec-authoring`** skill. It carries the EARS patterns, the INVEST test, the Gherkin
scenario shape, the success-criteria rules, the assumption policy and the self-validation checklist.
This command adds only the input detection, the branch mechanics and the file paths.

## Step 0 - Detect Input Type and Load Context

| Mode | Trigger | Primary source | Context |
| ---- | ------- | -------------- | ------- |
| Feature file | Path or number matching `features/##-*.md`, `##`, `feature ##` | The feature file: summary, use cases, scope, dependencies | Parent `idea.md`: vision, users, goals, constraints |
| Idea | Path containing `idea.md` | `idea.md`: vision, problem, users, goals, scope, use cases | - |
| Description | Plain text | The text itself | Any `idea.md` in the target directory |

Extract **Technical Hints** from the idea's Constraints, Assumptions and Discovery Notes, and from the
feature file's Technical Hints. These flow downstream to `/specforge.plan`.

Add source links to the spec header:

```markdown
**Source**: [Feature ##](./features/##-feature-name.md)
**Parent Idea**: [idea.md](./idea.md)
```

If the description is plain text under ~20 words, suggest `/specforge.idea` first.

**Documentation context**: if `/docs/README.md` exists, identify the relevant domain and load
`/docs/{domain}/spec.md`. Reuse its entity names, patterns and terminology - consistency with what
exists beats a better name invented here.

## Step 1 - Branch and File

1. Generate a 2-4 word action-noun short name ("add user authentication" -> `user-auth`).
2. Find the next feature number across all sources:

   ```bash
   git fetch --all --prune
   ```

   Check remote branches (`git ls-remote --heads origin`), local branches, and `specs/` directories.
   Use the highest N plus one; start at 1 if none exist.

3. Run `{SCRIPT}` **once**, with the number and short name:

   ```bash
   {SCRIPT} --json --number 5 --short-name "user-auth" "Add user authentication"
   ```

   Parse `BRANCH_NAME` and `SPEC_FILE`. For single quotes in arguments use `'I'\''m Groot'`.

The script creates and checks out the branch and initialises the spec file.

## Step 2 - Write the Specification

Load `templates/spec-template.md` for the section structure. Apply `spec-authoring` and write to
`SPEC_FILE`, preserving section order and headings.

If technical hints were extracted, append them in a quarantined section:

```markdown
---

## Technical Hints (For Planning)

> Preserved from the source idea. Not part of the functional specification.

### Source
### Technical Constraints
### Implementation Guidance
### Discovery Decisions
```

Preserve commands, tools and execution order verbatim. Substituting an "equivalent" tool for the one
the author named is a common and expensive failure.

## Step 3 - Validate

Write `FEATURE_DIR/checklists/requirements.md` from the `spec-authoring` self-validation checklist and
evaluate the spec against every item.

- All pass -> continue.
- Failures -> update the spec, re-validate, at most three iterations, then report what remains.
- `[NEEDS CLARIFICATION]` markers -> keep the three most critical (scope > security > UX > technical),
  make informed guesses for the rest, and present the survivors as options tables. Wait for answers,
  integrate, re-validate.

Then run `lens-requirements` over the finished spec as a quick red pass; fix what it finds directly.

## Step 4 - Feature File Status

When the spec came from a feature file, update: the feature's status to `Specified`, its Specification
Status table, and the parent idea's Features Overview row.

## Step 5 - Report

Branch name, spec path, checklist results, unresolved clarifications, and the next command
(`/specforge.clarify` or `/specforge.plan`, or `/specforge.design` to run the whole design phase).
