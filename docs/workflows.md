# SpecForge Workflows

This guide describes the different workflows available in SpecForge and when to use each one.

## Workflow Selection Guide

| Scenario | Workflow | Commands |
|----------|----------|----------|
| New feature from scratch | Full Workflow | idea → specify → clarify → plan → tasks → implement → verify → validate → merge |
| New feature (simple) | Standard Workflow | specify → plan → tasks → implement → verify → merge |
| Bug fix | Quick Change | change |
| Spec clarification | Quick Change | change |
| User feedback | Quick Change | change |
| Code refinement | Quick Change | change |
| Major refactoring | Full Workflow | specify → plan → tasks → implement → verify → merge |
| Pre-merge quality check | Quality Gates | verify |
| Security assessment | Security Audit | security |

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
│    ┌────────┐    ┌──────────┐    ┌─────┐    ┌───────┐    ┌───────┐                      │
│───►│ verify │───►│ validate │───►│ fix │───►│ merge │───►│ learn │                      │
│    └────────┘    └──────────┘    └─────┘    └───────┘    └───────┘                      │
│         │              │              │           │            │                          │
│         ▼              ▼              ▼           ▼            ▼                          │
│    quality         validation/    (loop back)   /docs/     architecture-registry.md      │
│    gates           report.md                    + main     {module}/CLAUDE.md            │
│    report          bugs/                                                                 │
│                                                                                          │
│    ┌──────────┐                                                                          │
│    │ security │  (can be run at any time, recommended before merge)                      │
│    └──────────┘                                                                          │
│         │                                                                                │
│         ▼                                                                                │
│    security/report.md                                                                    │
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

### Phase 7: Verification (Quality Gates)

**Command**: `/specforge.verify`

**Purpose**: Run sequential technical quality gates before validation. Each gate must pass before the next one runs (fail-fast).

**Semantic Anchors Applied**:
- Continuous Integration (Martin Fowler)
- Fail Fast
- Quality Gate (Sonar-style pass/fail)
- Shift Left

**Quality Gates** (executed in order):
1. **Build** - Compile/build the project
2. **Test** - Run unit/integration tests
3. **Lint** - Code style and static analysis
4. **Typecheck** - Type verification (TypeScript, mypy, etc.)
5. **Security** - Dependency vulnerability scan
6. **Coverage** - Code coverage threshold (default: 80%)

**Options**:
- `--fix` - Auto-fix lint and format issues
- `--skip-build`, `--skip-test`, `--skip-lint`, etc. - Skip specific gates
- `--threshold N` - Coverage threshold percentage
- `--report` - Generate a report file

**Handoffs**:
- → `/specforge.fix` if errors are found
- → `/specforge.security` for deeper security audit
- → `/specforge.review` for deeper code review

---

### Phase 8: Validation

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

### Phase 9: Fix (If Needed)

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

┌──────────┐    ┌──────────┐
│  verify  │───►│ security │
└──────────┘    └──────────┘
     │               │
     ▼               ▼
 Quality gate    Security
 report          audit report
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

**`/specforge.verify`** - Technical quality gates
- Sequential gates: build → test → lint → typecheck → security → coverage
- Fail-fast: stops at first failing gate
- Auto-fix mode for lint/format issues
- Configurable coverage threshold
- Run before `/specforge.validate` or `/specforge.merge`

**`/specforge.security`** - Comprehensive security audit
- OWASP Top 10 vulnerability scan
- Hardcoded secrets detection
- Dependency vulnerability audit
- Authentication/authorization coverage analysis
- Severity levels: critical, high, medium
- Can be scoped to specific directories or changed files only

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
| **Setup** | `/specforge.setup` | - | Full setup (orchestrator) |
| | `/specforge.setup-constitution` | - | constitution |
| | `/specforge.setup-docs` | from-code/from-docs/from-specs | /docs/{domain}/ |
| | `/specforge.setup-skills` | - | Framework-specific skills |
| | `/specforge.setup-agents` | - | Specialized subagents |
| | `/specforge.setup-mcp` | - | MCP server config |
| | `/specforge.setup-hooks` | --profile minimal/standard/strict | Claude Code hooks |
| Explore | `/specforge.idea` | Raw idea | idea.md, features/ |
| Specify | `/specforge.specify` | Description | spec.md |
| Clarify | `/specforge.clarify` | - | Updated spec.md |
| Plan | `/specforge.plan` | Tech stack | plan.md, research.md, data-model.md, contracts/ |
| Tasks | `/specforge.tasks` | - | tasks.md |
| Implement | `/specforge.implement` | - | Code, task-results/ |
| **Verify** | `/specforge.verify` | --fix, --skip-*, --threshold | Quality gate report |
| **Validate** | `/specforge.validate` | - | validation/, bugs/ |
| Fix | `/specforge.fix` | Bug ID | Fixed code |
| **Merge** | `/specforge.merge` | - | /docs/{domain}/spec.md updated |
| **Learn** | `/specforge.learn` | - | architecture-registry, specs context, module + sub-module context |
| Change | `/specforge.change` | Description | Updated code/spec |
| Analyze | `/specforge.analyze` | - | Coverage report |
| Review | `/specforge.review` | Scope | Tech debt report |
| **Security** | `/specforge.security` | --scope, --severity, --fix | Security audit report |
| Breakdown | `/specforge.breakdown` | - | Detailed task plans |
| Issues | `/specforge.taskstoissues` | - | GitHub issues |

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
