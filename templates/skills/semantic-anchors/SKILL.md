---
name: semantic-anchors
description: |
  Catalogue of the named frameworks (EARS, INVEST, Clean Architecture, 5 Whys, STRIDE...) that
  SpecForge skills and commands activate, plus the shared severity and status vocabulary. Activate
  when: choosing which mental models to apply, writing a new skill or command, or needing the
  canonical severity, validation or bug status definitions.
triggers: ["semantic anchors", "which framework", "ears", "invest", "anchor reference", "severity levels", "standard classifications"]
---

# Semantic Anchors

> Named frameworks activate rich context in far fewer tokens than describing the same discipline from
> scratch. "Apply EARS syntax; validate with INVEST" carries more than a paragraph of instruction.

Declare the anchors a skill or command uses in its frontmatter, then reference them in the body where
they apply.

## Requirements Engineering

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **EARS Syntax** | Easy Approach to Requirements Syntax. Patterns: Ubiquitous, Event-driven, State-driven, Optional, Complex. Eliminates ambiguity. | Writing functional requirements |
| **INVEST Criteria** | Independent, Negotiable, Valuable, Estimable, Small, Testable. Quality criteria for user stories. | Validating user story quality |
| **Specification by Example** | Concrete examples as specs. Living documentation. Collaborative discovery. Gojko Adzic. | Creating acceptance criteria |
| **Jobs-to-Be-Done** | Outcome-focused. "When [situation], I want to [motivation], so I can [outcome]". Clayton Christensen. | Understanding user needs |

## Testing & Validation

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **BDD Gherkin** | Given-When-Then syntax. Feature files. Scenarios. Dan North. Cucumber. | Writing acceptance scenarios |
| **ATDD** | Acceptance Test-Driven Development. Tests before code. Executable specs. | Validation workflow |
| **TDD London School** | Outside-in. Mock collaborators. Test behavior not state. Steve Freeman, Nat Pryce. | Unit testing approach |
| **TDD Chicago School** | Inside-out. State verification. Classic TDD. Kent Beck. | Alternative testing approach |
| **Property-Based Testing** | Generators. Invariants. Shrinking. QuickCheck, Hypothesis, fast-check. | Edge case discovery |

## Architecture & Design

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **Hexagonal Architecture** | Ports and Adapters. Domain isolation. Alistair Cockburn. | Code structure decisions |
| **Clean Architecture** | Dependency rule. Use cases. Entities. Robert C. Martin. | Layer organization |
| **C4 Model** | Context, Containers, Components, Code. Simon Brown. Hierarchical diagrams. | Architecture documentation |
| **ADR** | Architecture Decision Records. Context, Decision, Consequences. Michael Nygard. | Recording tech decisions |
| **arc42** | Template for architecture documentation. 12 sections. Stakeholder-focused. | Architecture docs structure |

## Design Principles

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **SOLID Principles** | Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion. | Code quality |
| **Convention over Configuration** | Sensible defaults. Minimal config. Ruby on Rails principle. | Default behavior decisions |
| **Principle of Least Astonishment** | Behavior matches expectations. Predictable interfaces. | UX and API design |
| **DRY** | Don't Repeat Yourself. Single source of truth. Pragmatic Programmer. | Code organization |
| **YAGNI** | You Aren't Gonna Need It. No speculative features. XP principle. | Scope decisions |

## Problem Solving & Debugging

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **5 Whys** | Root cause analysis. Iterative questioning. Toyota Production System. | Bug diagnosis |
| **Ishikawa Diagram** | Fishbone diagram. Cause categories: People, Process, Equipment, Materials, Environment, Management. | Complex problem analysis |
| **Rubber Duck Debugging** | Explain problem aloud. Articulate assumptions. Force clarity. | Stuck on bugs |
| **Scientific Method** | Hypothesis, Experiment, Observation, Conclusion. Systematic debugging. | Performance issues |

## Process & Workflow

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **Double Diamond** | Discover, Define, Develop, Deliver. Divergent and convergent thinking. Design Council. | Feature exploration |
| **Cynefin Framework** | Simple, Complicated, Complex, Chaotic, Disorder. Dave Snowden. Context-appropriate responses. | Decision making |
| **Wardley Mapping** | Value chain. Evolution stages. Strategic planning. Simon Wardley. | Tech strategy |
| **Kanban** | Visualize work. Limit WIP. Manage flow. Pull system. | Task management |

## Documentation

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **Diataxis Framework** | Tutorials, How-to guides, Reference, Explanation. Four documentation types. Daniele Procida. | Documentation structure |
| **Docs-as-Code** | Version controlled. Reviewed. Automated. Same tools as code. | Doc workflow |

## Requirements Elicitation

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **Socratic Method** | Guided questioning to uncover assumptions. Reveal gaps through dialogue. | Clarification sessions |
| **Requirements Elicitation** | Structured discovery techniques. Stakeholder interviews. Observation. Workshops. | Gathering requirements |
| **Active Listening** | Capture intent, not just words. Paraphrase. Clarify understanding. | User interviews |

## Project Management

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **Work Breakdown Structure** | Hierarchical decomposition. Deliverable-oriented. WBS Dictionary. | Task decomposition |
| **User Story Mapping** | Backbone (activities) → Skeleton (tasks) → Ribs (stories). Jeff Patton. | Feature organization |
| **Dependency Graph** | DAG for task ordering. Critical path identification. Blocking analysis. | Task sequencing |
| **Critical Path Method** | Longest sequence of dependent tasks. Float calculation. Schedule optimization. | Project scheduling |
| **Progressive Elaboration** | Refine details as knowledge increases. Rolling wave planning. | Iterative planning |
| **Spike** | Timeboxed research/exploration. Reduce uncertainty. XP practice. | Research tasks |

## Quality Assurance

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **Definition of Ready** | Criteria for starting work. Scrum artifact. Prerequisites checklist. | Pre-work validation |
| **Definition of Done** | Completion criteria. Quality gates. Acceptance checklist. | Work completion |
| **Quality Gates** | Stage-gate process. Checkpoints. Go/no-go decisions. | Phase transitions |
| **Acceptance Criteria** | Testable conditions. Pass/fail requirements. Gherkin scenarios. | Story validation |
| **Exploratory Testing** | Session-based. Charter-driven. Observe beyond scripts. Discovery focus. | Finding edge cases |
| **Regression Testing** | Verify unchanged functionality. Detect unintended changes. | Post-change validation |

## Code Quality

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **Code Smell Catalog** | Martin Fowler's refactoring patterns. Long method. God class. Feature envy. | Code review |
| **OWASP Top 10** | Security vulnerability classification. Injection. Broken auth. XSS. | Security review |
| **Technical Debt Quadrant** | Martin Fowler: Reckless/Prudent × Deliberate/Inadvertent. | Debt classification |
| **Cyclomatic Complexity** | McCabe metric. Decision points. Branch counting. Testability indicator. | Complexity analysis |
| **Boy Scout Rule** | Leave code better than you found it. Incremental improvement. | Continuous improvement |

## Pattern Discovery

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **Pattern Mining** | Extract recurring solutions. Identify conventions. Document idioms. | Codebase analysis |
| **Code Archaeology** | Understanding existing systems. Historical analysis. Evolution tracking. | Legacy code |
| **Conway's Law** | System structure mirrors organization. Communication patterns. | Architecture analysis |

## Agent & System Design

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **Single Responsibility** | One reason to change. Focused purpose. SOLID SRP. | Agent design |
| **Separation of Concerns** | Independent aspects. Loose coupling. High cohesion. | System decomposition |
| **Domain-Driven Design** | Bounded contexts. Ubiquitous language. Aggregates. Eric Evans. | Domain modeling |
| **Microservices Pattern** | Independent deployment. Specialized components. API boundaries. | Service architecture |
| **Capability Mapping** | Skills to roles. Competency alignment. Resource allocation. | Agent assignment |

## Continuous Improvement

| Anchor | Core Concepts | When to Use |
|--------|---------------|-------------|
| **Kaizen** | Continuous small improvements. Toyota Production System. Incremental change. | Quick changes, refinements |
| **Hotfix** | Targeted fix with minimal scope. Emergency response. Isolated change. | Bug fixes, urgent issues |
| **Ship of Theseus** | Incremental change while maintaining identity. Gradual evolution. | Refactoring, migrations |
| **Continuous Delivery** | Small, frequent, safe changes. Always deployable. Fast feedback. | Frequent releases |

---

## Standard Classifications

Shared severity and status definitions used across specforge commands. Individual commands (validate, review, fix) may include a trimmed version; this is the canonical reference.

### Severity Levels

| Severity | Meaning | Action |
| -------- | ------- | ------ |
| CRITICAL | Blocks functionality or violates constitution | Must fix before proceeding |
| HIGH | Significant defect, security risk, or missing coverage | Fix before implementation/merge |
| MEDIUM | Quality issue, inconsistency, or partial coverage | Fix when practical |
| LOW | Style, minor redundancy, cosmetic | Fix if convenient |

### Validation Statuses

| Status | Condition |
| ------ | --------- |
| PASSED | All scenarios executed and passed |
| FAILED | All scenarios ran but some failed |
| INCOMPLETE | Execution errors prevented testing |
| PARTIAL | Some scenarios were skipped |

### Bug Statuses

| Status | Meaning |
| ------ | ------- |
| CONFIRMED | Bug reproduced and verified |
| CANNOT_REPRODUCE | Unable to trigger the described behavior |
| BY_DESIGN | Behavior is intentional per specification |
| ENVIRONMENT | Issue specific to a configuration, not a code defect |

---

## Anchor Combinations (Triangulation)

Combine anchors to create precise context:

| Combination | Activated Context |
|-------------|-------------------|
| `ATDD + BDD Gherkin + Specification by Example` | Full acceptance testing mindset with concrete examples |
| `Hexagonal Architecture + SOLID + Clean Architecture` | Layered, testable, maintainable code structure |
| `5 Whys + Ishikawa + Scientific Method` | Rigorous systematic debugging approach |
| `INVEST + EARS + Jobs-to-Be-Done` | Complete requirements engineering toolkit |
| `arc42 + C4 Model + ADR` | Comprehensive architecture documentation |
| `Socratic Method + Requirements Elicitation + Active Listening` | Effective clarification and discovery sessions |
| `Code Smell Catalog + OWASP Top 10 + Technical Debt Quadrant` | Comprehensive code review covering quality, security, and debt |
| `User Story Mapping + Work Breakdown Structure + Dependency Graph` | Complete task organization and sequencing |
| `Definition of Ready + Definition of Done + Quality Gates` | Full quality lifecycle management |
| `Pattern Mining + ADR + Code Archaeology` | Systematic pattern extraction and documentation |
| `Single Responsibility + Separation of Concerns + DDD` | Well-designed agent and component architecture |
| `Kaizen + Boy Scout Rule + Hotfix + YAGNI` | Quick, focused changes without over-engineering |

---

## Adversarial Review Anchors

Used by the review harness and its lenses.

| Anchor | Core concepts | When to use |
| ------ | ------------- | ----------- |
| **STRIDE** | Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege | Threat modelling a boundary |
| **OWASP ASVS** | Application Security Verification Standard. Levelled requirements. | Security review depth |
| **FMEA** | Failure Mode and Effects Analysis. Enumerate failures, effects, detection. | Reliability review |
| **Falsification** | Popper. A claim is meaningful only if it can be proven wrong. | Verifying findings |
| **Mutation Testing** | Change the code, see if a test fails. Measures oracle strength. | Test quality review |
| **Red Team / Blue Team** | Adversary and defender roles held separately. | Structuring a review pass |
| **Chaos Engineering** | Inject failure deliberately to discover weakness. | Resilience probing |
| **Blast Radius** | How far the damage reaches if this is wrong. | Calibrating review rigor |
| **One-Way Door** | Decisions that cannot be reversed cheaply. Bezos. | Deciding review depth |
| **WCAG 2.2 AA** | Web Content Accessibility Guidelines, level AA success criteria. | Accessibility review |
| **Four Golden Signals** | Latency, traffic, errors, saturation. Google SRE. | Observability review |
| **Expand-Contract** | Additive schema change, backfill, switch, remove. | Safe migrations |

## Anchor Combinations for Reviews

| Combination | Activated context |
| ----------- | ----------------- |
| `STRIDE + OWASP Top 10 + Trust Boundaries` | Complete security review posture |
| `FMEA + Chaos Engineering + Blast Radius` | Reliability review with prioritised failure modes |
| `Falsification + Mutation Testing + Oracle Quality` | Reviews whose findings and tests both hold up |
| `Expand-Contract + One-Way Door + Reversibility` | Safe data and contract evolution |
