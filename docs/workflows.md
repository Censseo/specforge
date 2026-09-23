# SpecForge Workflows

This guide describes the different workflows available in SpecForge and when to use each one.

## Workflow Selection Guide

| Scenario | Workflow | Commands |
|----------|----------|----------|
| New feature, gated end to end | Phase Workflow | workflow (design → build → qa) |
| New feature from scratch | Full Workflow | idea → specify → clarify → plan → tasks → implement → validate → merge |
| New feature (simple) | Standard Workflow | specify → plan → tasks → implement → merge |
| Bug fix | Quick Change | change |
| Spec clarification | Quick Change | change |
| User feedback | Quick Change | change |
| Code refinement | Quick Change | change |
| Major refactoring | Phase Workflow | workflow |
| Reviewing existing work | Harness | harness |

---

## Macro Pipelines (Design → Build → QA)

The macro commands chain the step-by-step commands into non-interactive pipelines. Each applies
recommended defaults instead of stopping to ask, red-teams its output through domain lenses, and
writes a gate record to `specs/{feature}/gates/` that returns PASS, PASS WITH CONDITIONS or BLOCK.

```bash
/specforge.workflow Add OAuth2 login with Google and GitHub
```

| Pipeline | Command | Chain | Gate |
|----------|---------|-------|------|
| Design | `/specforge.design` | specify → clarify (auto) → plan → **adversarial review** → checklists (auto) → tasks → analyze (auto) → complexity analysis | D1-D10 |
| Build | `/specforge.build` | per phase: breakdown (if complex) → implement → **adversarial pass**; then review → corrections → **final adversarial review** → **test plan** | B1-B9 |
| QA | `/specforge.qa` | execute `test-plan.md` ⇄ fix loop (max 3, early exit on no progress) → **adversarial release review** | Q1-Q8 |
| Merge | `/specforge.merge` | verify both gates → docs consolidation → merge | - |

### Models

A slash command runs under one model for its whole execution; it cannot switch between pipelines.
`/specforge.workflow` is therefore a convenience rather than the default. To use a different model per
pipeline - a stronger one for design, a cheaper one for the long mechanical build - run the three
separately and switch between them; their handoffs chain them for you. For per-step variation inside a
pipeline, set models on the specialised agents in `.specforge`-installed `agents/specforge/`, which
`/specforge.implement` honours per task.

### Non-interactive by design

The pipelines answer their own questions. `clarify` applies its own recommendation for each ambiguity
and records it as an assumption; `checklist` remediates failing items by fixing the spec or plan;
`analyze` applies its own remediations. Two things this deliberately does **not** do:

- It never resolves a genuine conflict between two requirements - it cannot know which one you meant.
  That is a CRITICAL finding that stops the pipeline.
- It never marks a checklist item passed without changing the artifact that made it fail.

Every auto-applied answer is written down. That is what makes the adversarial review able to attack
it, and what lets you see, at the end, how many decisions were made on your behalf.

### Gate checks between stages

A stage that would make the next one meaningless stops the pipeline rather than feeding it garbage:

| Stage | Stops the pipeline when |
|-------|-------------------------|
| specify | spec.md missing or empty |
| plan | architecture divergences need approval |
| adversarial review | a blocking finding remains (Critical, or High confirmed, or constitution MUST, or an unreviewed one-way door) |
| checklists | a CRITICAL item still FAILs after remediation |
| analyze | a CRITICAL finding remains after remediation |
| validate | the environment never started (INCOMPLETE twice - retrying will not help) |

### Complexity analysis

Design ends by classifying each phase of `tasks.md` as DIRECT or BREAKDOWN, and recording which lenses
that phase's content exposes. Build reads `complexity-analysis.md` to decide where to run
`/specforge.breakdown` first and which lenses to run on each increment.

A phase needs breakdown if it meets two or more of: more than 8 tasks, 3+ domains, many sequential
dependency chains, REFACTOR or complex EXTEND tasks, or exposure to security / migration /
concurrency / public contract changes.

### The adversarial test plan

Build then writes `FEATURE_DIR/test-plan.md`, and QA executes it. The timing is the point: at the
end of build the pipeline knows what was actually built, where it deviated from the plan, and every
gotcha the implementation hit. A plan derived from the spec alone tests what was intended; those
deviations are where the bugs are, and they do not exist yet at design time.

The plan covers ten classes, and an empty class is a hole rather than a clean bill:

| Class | Covers |
|-------|--------|
| C1 Happy path | The primary flow per user story |
| C2 Boundary | 0, 1, max, max+1, empty, unicode, negative, duplicate |
| C3 Invalid input | Malformed, wrong type, missing field, injection-shaped |
| C4 Permission | What each actor cannot do, including another user's records by id |
| C5 State | Illegal transitions, expired / deleted / already-processed entities |
| C6 Failure | Dependency down, slow, garbage; partial failure mid-operation |
| C7 Concurrency | Same action twice, simultaneously, out of order; stale edit |
| C8 Regression | What existed before and shares code with the change |
| C9 Data integrity | Is the stored state afterwards exactly what it should be |
| C10 Exploratory | Charters, not scripts |

Each scenario carries preconditions, exact steps, an expected **observable** outcome, and a "Fails if"
clause - which exists so a marginal result cannot be rationalised into a pass. Scenarios that cannot
run here are marked `BLOCKED` with a reason, and the plan has an explicit Not Covered section: a plan
that silently omits what it could not test reports better coverage than it has.

Regenerate or scope it on its own with `/specforge.testplan`, `/specforge.testplan smoke`, or
`/specforge.testplan US2`.

### The final review at the end of build

Build's last review pass runs over the whole feature branch diff, focused on architecture, design
patterns, security and performance - the things that are expensive to change once shipped.

It sits at the end of **build**, not at merge, for one reason: its findings produce code changes, and
those must land before QA validates. A review at merge time either duplicates a pass that already ran
on the same code, or surfaces changes after QA has already signed off on something else.

It catches two things nothing earlier could. The shape of the whole - duplication across phases, an
abstraction that grew three incompatible callers, a boundary that eroded task by task - which the
per-increment passes could not see because each saw one phase. And the fact that whatever ships becomes
the example the next feature copies: a shortcut that survives here is a convention by next month.

Cheap fixes are applied in place rather than filed. A follow-up task on merged code competes with new
work and usually loses. A blocking finding makes the build gate BLOCK, and no test plan is written for
code already known to be wrong.

`/specforge.merge` verifies this happened and cleared, rather than repeating it.

Run the same pass on demand with:

```bash
/specforge.harness --focus architecture, design patterns, security, performance
```

`--focus` takes free text naming domains, in any language, and maps it to lenses - so it replaces an
agent's built-in `/review` without depending on one.

### The QA loop

QA runs validate against `test-plan.md`, and if scenarios fail, fix, then re-validate - up to three
rounds. Retry rounds re-run the failing scenarios **plus every P1**, because a fix can break something
that passed. It exits early when the failure count stops dropping, because a round that fixes nothing
will not be rescued by the next one. Findings from the adversarial release review do **not** re-enter the loop: the loop is for
scenario failures, and those findings go to the gate where a human decides.

### What each phase reviews

| Phase | Default lenses |
|-------|----------------|
| Design | requirements, architecture, domain-model, api-contract, data, security, privacy-compliance, reliability |
| Build | architecture, maintainability, security, concurrency, data, testing, performance, api-contract |
| QA | requirements, testing, security, reliability, performance, observability, accessibility, operations |

Lenses with no surface in the feature are dropped, and the skip is recorded. Lenses whose risk
triggers fire (a migration, a new endpoint, an LLM call, a UI component...) are added automatically.

### Gates

A finding blocks when it is Critical, or High and confirmed, or violates a constitution MUST, or is a
one-way door, or breaks a stated invariant. Everything else is advisory but still gets an owner and a
task. The cost of the fix never changes whether a finding blocks.

Gate verdicts are stale once their artifacts change - the workflow re-runs them rather than carrying a
PASS across a rewrite.

### Resuming

The workflow reads its state from files (`gates/`, `tasks.md`, `validation/bugs/`, `task-results/`),
so it survives a lost session. Re-running `/specforge.workflow` re-enters at the earliest phase with an
open blocking item.

---

## Adversarial Review (Any Target)

```bash
/specforge.harness                          # the current diff vs the base branch
/specforge.harness src/api/                 # a path
/specforge.harness spec.md                  # an artifact
/specforge.harness --lens security,data     # explicit lens selection
/specforge.harness --phase design           # a phase's default lens set
/specforge.harness --depth deep             # every triggered lens, no cap
```

Every finding must name a concrete failure (inputs or state → wrong outcome), carry evidence anchored
to a location, and survive a falsification attempt. Findings that are refuted are dropped, not
downgraded - which is what makes a zero-finding result meaningful.

---

## Full Workflow (New Features)

The complete Spec-Driven Development workflow for building new features from scratch.

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                          │
│    ┌──────┐    ┌─────────┐    ┌─────────┐    ┌──────┐    ┌───────┐    ┌──────┐          │
│    │ idea │───►│ specify │───►│ clarify │───►│ plan │───►│ tasks │───►│ impl │          │
│    └──────┘    └─────────┘    └─────────┘    └──────┘    └───────┘    └──────┘          │
│        │            │              │             │            │           │              │
│        ▼            ▼              ▼             ▼            ▼           ▼              │
│    idea.md      spec.md        spec.md       plan.md     tasks.md      code             │
│    features/    checklists/    (updated)     research.md               tests            │
│                 (/docs read)                 data-model.md                               │
│                                              contracts/                                  │
│                                              (/docs read)                                │
│                                                                                          │
│    ┌──────────┐    ┌─────┐    ┌───────┐    ┌───────┐                                    │
│───►│ validate │───►│ fix │───►│ merge │───►│ learn │                                    │
│    └──────────┘    └─────┘    └───────┘    └───────┘                                    │
│         │              │           │            │                                        │
│         ▼              ▼           ▼            ▼                                        │
│    validation/    (loop back)   /docs/     architecture-registry.md                      │
│    report.md                    + main     {module}/CLAUDE.md                            │
│    bugs/                                                                                 │
│                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### Phase 1: Exploration (Optional)

**Command**: `/specforge.idea`

**Purpose**: Transform a raw, vague idea into a structured vision document. Decompose complex ideas into manageable features.

**When to use**:
- Starting with a vague concept
- Complex feature requiring decomposition
- Need to explore before specifying

**Outputs**:
- `idea.md` - Vision document with user goals, constraints, technical hints
- `features/*.md` - Decomposed feature files (if complex)

**Skip if**: You already have clear requirements

---

### Phase 2: Specification

**Command**: `/specforge.specify`

**Purpose**: Create a formal specification document with user stories, functional requirements, and acceptance scenarios.

**Semantic Anchors Applied**:
- EARS Syntax for requirements
- INVEST Criteria for story quality
- Specification by Example for acceptance criteria
- Jobs-to-Be-Done for user outcomes

**Outputs**:
- `spec.md` - Complete feature specification
- `checklists/requirements.md` - Quality checklist

**Key Activities**:
1. Define user stories with priorities (P1, P2, P3)
2. Write functional requirements (EARS patterns)
3. Create acceptance scenarios (BDD Gherkin)
4. Define success criteria (measurable outcomes)

---

### Phase 3: Clarification

**Command**: `/specforge.clarify`

**Purpose**: Reduce ambiguity through structured questioning. Maximum 5 targeted questions.

**Semantic Anchors Applied**:
- Socratic Method for guided questioning
- Requirements Elicitation techniques
- INVEST Criteria validation

**Outputs**:
- Updated `spec.md` with clarifications section
- Resolved ambiguities encoded directly in spec

**Question Categories**:
- Functional scope & behavior
- Domain & data model
- Interaction & UX flow
- Non-functional requirements
- Integration & dependencies
- Edge cases & failure handling

---

### Phase 4: Technical Planning

**Command**: `/specforge.plan`

**Purpose**: Create technical implementation plan with architecture decisions, data models, and API contracts.

**Semantic Anchors Applied**:
- Clean Architecture / Hexagonal Architecture
- ADR (Architecture Decision Records)
- C4 Model for documentation
- DRY (Don't Repeat Yourself)

**Outputs**:
- `plan.md` - Technical implementation plan
- `research.md` - Research findings and decisions
- `data-model.md` - Entity definitions and relationships
- `contracts/` - API specifications
- `quickstart.md` - Test scenarios

**Key Activities**:
1. Load architecture registry (established patterns)
2. Explore existing codebase for reuse
3. Define tech stack and libraries
4. Design data model
5. Create API contracts
6. Document architecture decisions

---

### Phase 5: Task Generation

**Command**: `/specforge.tasks`

**Purpose**: Generate actionable, dependency-ordered task list organized by user story.

**Semantic Anchors Applied**:
- User Story Mapping (Jeff Patton)
- Work Breakdown Structure
- Dependency Graph
- Kanban flow

**Outputs**:
- `tasks.md` - Complete task breakdown

**Task Organization**:
```
Phase 1: Setup
Phase 2: Foundational
Phase 3+: User Story phases (by priority)
Final: Polish & cross-cutting
```

**Task Format**:
```markdown
- [ ] T001 [P] [US1] [REUSE] Description with file path
```
- `[P]` - Parallelizable
- `[US1]` - User story reference
- `[REUSE|EXTEND|REFACTOR|NEW]` - Reuse marker

---

### Phase 6: Implementation

**Command**: `/specforge.implement`

**Purpose**: Execute all tasks to build the feature according to the plan.

**Semantic Anchors Applied**:
- TDD London School (outside-in)
- Clean Architecture
- SOLID Principles
- Kanban (limit WIP)

**Execution Flow**:
1. Check checklists status
2. Load minimal context
3. Verify project setup (ignore files)
4. Load specialized agents
5. Execute tasks phase by phase
6. Create task results (`task-results/T###-result.md`)
7. Update architecture registry

**Modes**:
- **Delegate mode**: Uses specialized agents (backend-coder, frontend-coder, etc.)
- **Direct mode**: Implements directly when no agent matches

---

### Phase 7: Validation

**Command**: `/specforge.validate`

**Purpose**: Run integration tests by executing BDD acceptance scenarios.

**Semantic Anchors Applied**:
- ATDD (Acceptance Test-Driven Development)
- BDD Gherkin
- Exploratory Testing
- Regression Testing

**Outputs**:
- `validation/report-*.md` - Validation report
- `validation/screenshots/` - Evidence
- `validation/bugs/BUG-*.md` - Bug reports

**Key Activities**:
1. Start required services
2. Execute acceptance scenarios
3. Capture out-of-scope issues (regressions, side effects)
4. Generate bug files for failures
5. Cleanup services

---

### Phase 8: Fix (If Needed)

**Command**: `/specforge.fix`

**Purpose**: Diagnose and fix bugs found during validation.

**Semantic Anchors Applied**:
- 5 Whys (root cause analysis)
- Ishikawa Diagram
- Scientific Method

**Problem Categories**:
| Category | Action |
|----------|--------|
| Spec Gap | Update spec, then implement |
| Implementation Bug | Fix code directly |
| Misunderstanding | Re-analyze, update spec |
| Integration Issue | Add missing glue code |
| Performance Issue | Optimize code |

---

## Quick Change Workflow

For small, focused modifications without the full workflow overhead.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                              /specforge.change                                    │
│                                    │                                            │
│                            ┌───────┴───────┐                                    │
│                            │    Triage     │                                    │
│                            │  (30 sec max) │                                    │
│                            └───────┬───────┘                                    │
│                                    │                                            │
│            ┌───────────┬───────────┼───────────┬───────────┐                    │
│            │           │           │           │           │                    │
│            ▼           ▼           ▼           ▼           ▼                    │
│        Bug Fix    Spec Tweak   Feedback   Refinement   Too Large               │
│            │           │           │           │           │                    │
│            ▼           ▼           ▼           ▼           ▼                    │
│       5-Whys +    Edit spec   Capture +   Boy Scout   Escalate to              │
│       Fix code    Cascade     Apply       Improve     full workflow            │
│            │           │           │           │                                │
│            └───────────┴───────────┴───────────┘                                │
│                            │                                                    │
│                            ▼                                                    │
│                    Update traceability                                          │
│                    (tasks.md, spec.md)                                          │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### When to Use `/specforge.change`

**Use for:**
- Bug fixes (code doesn't match spec)
- Spec tweaks (clarify wording, add edge case)
- User feedback (adjust behavior based on testing)
- Refinements (improve UX, performance tuning)
- Small enhancements (add field, modify validation)

**Escalate to full workflow if:**
- Change affects multiple user stories
- Requires new data model or API endpoints
- Needs architectural decisions
- Scope exceeds 3 files

### Semantic Anchors Applied

- **Kaizen** - Continuous small improvements
- **Boy Scout Rule** - Leave it better than you found it
- **Hotfix** - Targeted fix with minimal scope
- **YAGNI** - Don't over-engineer the change

### Change Types

| Type | Triggers | Process |
|------|----------|---------|
| **Bug Fix** | "broken", "error", "fails" | Quick 5-Whys → Fix → Verify |
| **Spec Tweak** | "clarify", "add requirement" | Edit spec.md → Cascade if needed |
| **User Feedback** | "user said", "testing showed" | Capture → Apply → Update spec |
| **Refinement** | "improve", "optimize", "polish" | Boy Scout improvement |

### Example Usage

```bash
# Bug fix
/specforge.change The login button doesn't work on mobile

# Spec tweak
/specforge.change Add requirement: email must be validated with RFC 5322 format

# User feedback
/specforge.change Users are confused by the Submit button - they don't know what happens next

# Refinement
/specforge.change Improve error messages in the payment flow to be more user-friendly
```

---

## Supporting Workflows

### Quality Analysis

```
┌─────────┐    ┌─────────┐    ┌─────────┐
│ analyze │───►│ review  │───►│  learn  │
└─────────┘    └─────────┘    └─────────┘
     │              │              │
     ▼              ▼              ▼
 Coverage      Tech debt     Architecture
 report        report        + specs context
                              + module context
                              + sub-module context
```

**`/specforge.analyze`** - Cross-artifact consistency
- Run after `/specforge.tasks`, before `/specforge.implement`
- Detects gaps, duplications, ambiguities
- Validates constitution alignment

**`/specforge.review`** - Code quality analysis
- Code smell detection (Martin Fowler catalog)
- Security vulnerabilities (OWASP Top 10)
- Technical debt classification
- Generates improvement tasks

**`/specforge.learn`** - Pattern discovery and documentation
- Analyze existing codebase and all feature specifications
- Update architecture registry (HIGH LEVEL patterns only)
- Generate/update `specs/__AGENT_CONTEXT_FILE__` (project state: vocabulary, entities, contracts, invariants)
- Update module `__AGENT_CONTEXT_FILE__` files (local conventions + interface contracts + invariants + guard rails)
- Generate sub-module `__AGENT_CONTEXT_FILE__` files for high-complexity directories
- Auto-loaded by AI agents during implementation and specification

### Merge Workflow

```
┌───────────┐    ┌─────────┐    ┌─────────┐
│ implement │───►│  merge  │───►│  learn  │
└───────────┘    └─────────┘    └─────────┘
                      │              │
                      ▼              ▼
                   /docs/      CLAUDE.md
                 + main       files updated
```

**`/specforge.merge`** - Feature completion and documentation
- Verify all tasks completed
- Merge feature branch to main
- Consolidate specs to `/docs/{domain}/spec.md` (OpenSpec-style, by domain)
- Optionally run `/specforge.learn` to update patterns
- `/docs/{domain}/` becomes source of truth for future specify/plan

### Checklist Workflow

```
/specforge.checklist [domain]
        │
        ├── Generate mode (default)
        │   └── Creates domain-specific checklist
        │
        └── Review mode
            └── Validates existing checklists
```

**Purpose**: "Unit tests for English" - validate requirements quality, not implementation.

---

## Command Quick Reference

| Phase | Command | Input | Output |
|-------|---------|-------|--------|
| **Pipelines** | `/specforge.workflow` | Description or empty | All three pipelines, gate records |
| | `/specforge.design` | Description or empty | spec.md, plan.md, tasks.md, checklists/, complexity-analysis.md, gates/design-*.md |
| | `/specforge.build` | Optional `phase N` | Code, task-results/, reviews/, gates/build-*.md |
| | `/specforge.qa` | - | validation/, qa-report.md, gates/qa-*.md |
| | `/specforge.testplan` | Optional scope | test-plan.md |
| | `/specforge.harness` | Target + lenses or --focus | Findings and a verdict |
| **Setup** | `/specforge.setup` | - | Full setup (orchestrator) |
| | `/specforge.setup-bootstrap` | from-code/from-docs/from-specs | constitution + /docs/{domain}/ |
| | `/specforge.setup-agents` | - | agents + skills + MCP |
| Explore | `/specforge.idea` | Raw idea | idea.md, features/ |
| Specify | `/specforge.specify` | Description | spec.md |
| Clarify | `/specforge.clarify` | - | Updated spec.md |
| Plan | `/specforge.plan` | Tech stack | plan.md, research.md, data-model.md, contracts/ |
| Tasks | `/specforge.tasks` | - | tasks.md |
| Implement | `/specforge.implement` | - | Code, task-results/ |
| **Merge** | `/specforge.merge` | - | /docs/{domain}/spec.md updated |
| **Learn** | `/specforge.learn` | - | architecture-registry, specs context, module + sub-module context |
| Validate | `/specforge.validate` | - | validation/, bugs/ |
| Fix | `/specforge.fix` | Bug ID | Fixed code |
| Change | `/specforge.change` | Description | Updated code/spec |
| Analyze | `/specforge.analyze` | - | Coverage report |
| Review | `/specforge.review` | Scope | Tech debt report |

---

## Best Practices

### For New Features

1. **Start with constitution** - Define project principles first
2. **Be explicit in specs** - Focus on WHAT and WHY, not HOW
3. **Clarify before planning** - Resolve ambiguities early
4. **Validate incrementally** - Test each user story independently

### For Changes

1. **Use `/specforge.change` for small modifications** - Don't over-engineer
2. **Respect scope limits** - Escalate if > 3 files affected
3. **Maintain traceability** - Update tasks.md and spec.md
4. **Verify after fixing** - Run quick sanity check

### For Quality

1. **Run analyze before implement** - Catch gaps early
2. **Review code periodically** - Don't accumulate tech debt
3. **Extract patterns** - Keep architecture registry current
4. **Use checklists** - Validate requirements, not just code
5. **Review each increment, not the whole feature** - A defect found three tasks later costs a fix;
   found at the end it costs a redesign
6. **Falsify before reporting** - A review whose findings do not hold up teaches everyone to ignore it
7. **Record what you skipped** - An unrecorded skipped lens is a silent hole in the coverage
