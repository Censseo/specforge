<div align="center">
    <img src="./media/logo_large.webp" alt="SpecForge Logo" width="200" height="200"/>
    <h1>🔨 SpecForge</h1>
    <h3><em>Build high-quality software faster.</em></h3>
    <p><em>An enhanced fork of <a href="https://github.com/github/spec-kit">Spec Kit</a> with significant improvements</em></p>
</div>

<p align="center">
    <strong>An enhanced open source toolkit for Spec-Driven Development with advanced quality analysis, modular workflows, and intelligent code generation.</strong>
</p>

<p align="center">
    <a href="https://github.com/Censseo/specforge/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Censseo/specforge" alt="License"/></a>
</p>

---

## Table of Contents

- [🤔 What is Spec-Driven Development?](#-what-is-spec-driven-development)
- [⚡ Get Started](#-get-started)
- [📽️ Video Overview](#️-video-overview)
- [🤖 Supported AI Agents](#-supported-ai-agents)
- [🔧 Forge CLI Reference](#-specify-cli-reference)
- [📚 Core Philosophy](#-core-philosophy)
- [🌟 Development Phases](#-development-phases)
- [🎯 Experimental Goals](#-experimental-goals)
- [🔧 Prerequisites](#-prerequisites)
- [📖 Learn More](#-learn-more)
- [📋 Detailed Process](#-detailed-process)
- [🔍 Troubleshooting](#-troubleshooting)
- [👥 Maintainers](#-maintainers)
- [💬 Support](#-support)
- [🙏 Acknowledgements](#-acknowledgements)
- [📄 License](#-license)

## 🤔 What is Spec-Driven Development?

Spec-Driven Development **flips the script** on traditional software development. For decades, code has been king — specifications were just scaffolding we built and discarded once the "real work" of coding began. Spec-Driven Development changes this: **specifications become executable**, directly generating working implementations rather than just guiding them.

## ⚡ Get Started

### 1. Install Forge CLI

Choose your preferred installation method:

#### Option 1: Persistent Installation (Recommended)

Install once and use everywhere:

```bash
uv tool install forge-cli --from git+https://github.com/Censseo/specforge.git
```

Then use the tool directly:

```bash
# Create new project
forge init <PROJECT_NAME>

# Or initialize in existing project
forge init . --ai claude
# or
forge init --here --ai claude

# Check installed tools
forge check
```

To upgrade SpecForge, see the [Upgrade Guide](./docs/upgrade.md) for detailed instructions. Quick upgrade:

```bash
uv tool install forge-cli --force --from git+https://github.com/Censseo/specforge.git
```

#### Option 2: One-time Usage

Run directly without installing:

```bash
uvx --from git+https://github.com/Censseo/specforge.git forge init <PROJECT_NAME>
```

**Benefits of persistent installation:**

- Tool stays installed and available in PATH
- No need to create shell aliases
- Better tool management with `uv tool list`, `uv tool upgrade`, `uv tool uninstall`
- Cleaner shell configuration

### 2. Establish project principles

Launch your AI assistant in the project directory. The `/specforge.*` commands are available in the assistant.

Use the **`/specforge.constitution`** command to create your project's governing principles and development guidelines that will guide all subsequent development.

```bash
/specforge.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements
```

### 3. Create the spec

Use the **`/specforge.specify`** command to describe what you want to build. Focus on the **what** and **why**, not the tech stack.

```bash
/specforge.specify Build an application that can help me organize my photos in separate photo albums. Albums are grouped by date and can be re-organized by dragging and dropping on the main page. Albums are never in other nested albums. Within each album, photos are previewed in a tile-like interface.
```

### 4. Create a technical implementation plan

Use the **`/specforge.plan`** command to provide your tech stack and architecture choices.

```bash
/specforge.plan The application uses Vite with minimal number of libraries. Use vanilla HTML, CSS, and JavaScript as much as possible. Images are not uploaded anywhere and metadata is stored in a local SQLite database.
```

### 5. Break down into tasks

Use **`/specforge.tasks`** to create an actionable task list from your implementation plan.

```bash
/specforge.tasks
```

### 6. Execute implementation

Use **`/specforge.implement`** to execute all tasks and build your feature according to the plan.

```bash
/specforge.implement
```

For detailed step-by-step instructions, see our [comprehensive guide](./spec-driven.md).

## 📽️ Video Overview

Want to see SpecForge in action? Watch our [video overview](https://www.youtube.com/watch?v=a9eR1xsfvHg&pp=0gcJCckJAYcqIYzv)!

[![SpecForge video header](/media/specforge-video-header.jpg)](https://www.youtube.com/watch?v=a9eR1xsfvHg&pp=0gcJCckJAYcqIYzv)

## 🤖 Supported AI Agents

| Agent                                                                                | Support | Notes                                                                                                                                     |
| ------------------------------------------------------------------------------------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| [Qoder CLI](https://qoder.com/cli)                                                   | ✅      |                                                                                                                                           |
| [Amazon Q Developer CLI](https://aws.amazon.com/developer/learning/q-developer-cli/) | ⚠️      | Amazon Q Developer CLI [does not support](https://github.com/aws/amazon-q-developer-cli/issues/3064) custom arguments for slash commands. |
| [Amp](https://ampcode.com/)                                                          | ✅      |                                                                                                                                           |
| [Auggie CLI](https://docs.augmentcode.com/cli/overview)                              | ✅      |                                                                                                                                           |
| [Claude Code](https://www.anthropic.com/claude-code)                                 | ✅      |                                                                                                                                           |
| [CodeBuddy CLI](https://www.codebuddy.ai/cli)                                        | ✅      |                                                                                                                                           |
| [Codex CLI](https://github.com/openai/codex)                                         | ✅      |                                                                                                                                           |
| [Cursor](https://cursor.sh/)                                                         | ✅      |                                                                                                                                           |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli)                            | ✅      |                                                                                                                                           |
| [GitHub Copilot](https://code.visualstudio.com/)                                     | ✅      |                                                                                                                                           |
| [IBM Bob](https://www.ibm.com/products/bob)                                          | ✅      | IDE-based agent with slash command support                                                                                                |
| [Jules](https://jules.google.com/)                                                   | ✅      |                                                                                                                                           |
| [Kilo Code](https://github.com/Kilo-Org/kilocode)                                    | ✅      |                                                                                                                                           |
| [opencode](https://opencode.ai/)                                                     | ✅      |                                                                                                                                           |
| [Qwen Code](https://github.com/QwenLM/qwen-code)                                     | ✅      |                                                                                                                                           |
| [Roo Code](https://roocode.com/)                                                     | ✅      |                                                                                                                                           |
| [SHAI (OVHcloud)](https://github.com/ovh/shai)                                       | ✅      |                                                                                                                                           |
| [Windsurf](https://windsurf.com/)                                                    | ✅      |                                                                                                                                           |

## 🔧 Forge CLI Reference

The `forge` command supports the following options:

### Commands

| Command | Description                                                                                                                                             |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `init`  | Initialize a new Specify project from the latest template                                                                                               |
| `check` | Check for installed tools (`git`, `claude`, `gemini`, `code`/`code-insiders`, `cursor-agent`, `windsurf`, `qwen`, `opencode`, `codex`, `shai`, `qoder`) |

### `forge init` Arguments & Options

| Argument/Option        | Type     | Description                                                                                                                                                                                  |
| ---------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `<project-name>`       | Argument | Name for your new project directory (optional if using `--here`, or use `.` for current directory)                                                                                           |
| `--ai`                 | Option   | AI assistant to use: `claude`, `gemini`, `copilot`, `cursor-agent`, `qwen`, `opencode`, `codex`, `windsurf`, `kilocode`, `auggie`, `roo`, `codebuddy`, `amp`, `shai`, `q`, `bob`, or `qoder` |
| `--script`             | Option   | Script variant to use: `sh` (bash/zsh) or `ps` (PowerShell)                                                                                                                                  |
| `--ignore-agent-tools` | Flag     | Skip checks for AI agent tools like Claude Code                                                                                                                                              |
| `--no-git`             | Flag     | Skip git repository initialization                                                                                                                                                           |
| `--here`               | Flag     | Initialize project in the current directory instead of creating a new one                                                                                                                    |
| `--force`              | Flag     | Force merge/overwrite when initializing in current directory (skip confirmation)                                                                                                             |
| `--skip-tls`           | Flag     | Skip SSL/TLS verification (not recommended)                                                                                                                                                  |
| `--debug`              | Flag     | Enable detailed debug output for troubleshooting                                                                                                                                             |
| `--github-token`       | Option   | GitHub token for API requests (or set GH_TOKEN/GITHUB_TOKEN env variable)                                                                                                                    |

### Examples

```bash
# Basic project initialization
forge init my-project

# Initialize with specific AI assistant
forge init my-project --ai claude

# Initialize with Cursor support
forge init my-project --ai cursor-agent

# Initialize with Qoder support
forge init my-project --ai qoder

# Initialize with Windsurf support
forge init my-project --ai windsurf

# Initialize with Amp support
forge init my-project --ai amp

# Initialize with SHAI support
forge init my-project --ai shai

# Initialize with IBM Bob support
forge init my-project --ai bob

# Initialize with PowerShell scripts (Windows/cross-platform)
forge init my-project --ai copilot --script ps

# Initialize in current directory
forge init . --ai copilot
# or use the --here flag
forge init --here --ai copilot

# Force merge into current (non-empty) directory without confirmation
forge init . --force --ai copilot
# or
forge init --here --force --ai copilot

# Skip git initialization
forge init my-project --ai gemini --no-git

# Enable debug output for troubleshooting
forge init my-project --ai claude --debug

# Use GitHub token for API requests (helpful for corporate environments)
forge init my-project --ai claude --github-token ghp_your_token_here

# Check system requirements
forge check
```

### Available Slash Commands

After running `forge init`, your AI coding agent will have access to these slash commands for structured development:

#### Macro Pipeline Commands

Each of these runs a full pipeline non-interactively: it chains the individual commands below,
applies recommended defaults instead of stopping to ask, red-teams its output through domain lenses,
and writes a gate record before the next pipeline starts.

| Command                | Pipeline                                                                            |
| ---------------------- | ----------------------------------------------------------------------------------- |
| `/specforge.workflow`  | **Orchestrator** - design → build → qa, resuming from file state, stopping on BLOCK  |
| `/specforge.design`    | specify → clarify → plan → adversarial review → checklists → tasks → analyze → complexity analysis |
| `/specforge.build`     | per phase: breakdown (if complex) → implement → adversarial pass; then review → corrections → **final adversarial review** → **test plan** |
| `/specforge.qa`        | execute `test-plan.md` ⇄ fix loop (max 3 rounds, early exit on no progress) → adversarial release review |
| `/specforge.testplan`  | The adversarial test plan on its own, for regenerating or scoping it                 |
| `/specforge.harness`   | The adversarial review harness on any target, with any lens or focus selection       |

```bash
/specforge.workflow Add OAuth2 login with Google and GitHub
/specforge.design Add OAuth2 login with Google and GitHub
/specforge.build phase 3
/specforge.testplan                 # regenerate the plan, or /specforge.testplan smoke
/specforge.harness --focus architecture, design patterns, security, performance
```

**Models**: a slash command runs under one model for its whole execution. `/specforge.workflow` is
therefore a convenience - to use a different model per pipeline, run `design`, `build` and `qa`
separately and switch between them. Their handoffs chain them for you.

Each pipeline hands off to the next, so `/specforge.design` chains into `/specforge.build` and on into
`/specforge.qa`. Every stage has a gate check: a failure that would make the next stage meaningless
stops the pipeline and reports, rather than producing tasks from a broken plan.

Artifacts a pipeline produces beyond the usual ones:

| File | Written by | Purpose |
| ---- | ---------- | ------- |
| `complexity-analysis.md` | design | Per-phase DIRECT / BREAKDOWN verdict and lens exposure, consumed by build |
| `test-plan.md` | build | Adversarial scenarios across 10 coverage classes, executed by qa |
| `gates/{phase}-{date}.md` | each pipeline | Verdict, criteria table, findings, carried conditions |
| `qa-report.md` | qa | Final validation status, rounds, remaining failures |

Build ends with two passes that only make sense once everything is there. First a **final adversarial
review** of the whole branch diff - architecture, design patterns, security, performance, the things
that are expensive to change once shipped. It runs here rather than at merge because its findings
produce code changes, and those must land before QA validates; a review at merge time would surface
changes after QA had already signed off.

Then `test-plan.md`, written from what was actually built rather than from the spec: by that point the
pipeline knows where the implementation deviated and every gotcha it hit. Those deviations are the most
productive source of test scenarios there is, and they do not exist yet at design time.

The macro commands are orchestrators, not replacements: they call the same commands and skills as the
individual ones, so the two styles mix freely.

#### Core Workflow Commands

Essential commands for the Spec-Driven Development workflow:

| Command                 | Description                                                              |
| ----------------------- | ------------------------------------------------------------------------ |
| `/specforge.constitution` | Create or update project governing principles and development guidelines |
| `/specforge.idea`         | Transform raw ideas into structured vision documents with feature decomposition |
| `/specforge.specify`      | Define what you want to build (requirements and user stories)            |
| `/specforge.clarify`      | Clarify underspecified areas (recommended before `/specforge.plan`)        |
| `/specforge.plan`         | Create technical implementation plans with your chosen tech stack        |
| `/specforge.tasks`        | Generate actionable task lists for implementation                        |
| `/specforge.implement`    | Execute all tasks to build the feature according to the plan             |
| `/specforge.validate`     | Run integration tests by executing acceptance scenarios                  |
| `/specforge.fix`          | Diagnose and fix bugs by analyzing gaps between spec and implementation  |

#### Quick Change Command

For small modifications without the full workflow overhead:

| Command            | Description                                                                      |
| ------------------ | -------------------------------------------------------------------------------- |
| `/specforge.change`  | Apply focused changes (bug fixes, spec tweaks, user feedback, refinements)       |

Use `/specforge.change` when:
- Fixing a bug (code doesn't match spec)
- Tweaking a spec (clarify wording, add edge case)
- Responding to user feedback
- Making small refinements or polish

#### Quality & Analysis Commands

| Command                    | Description                                                                      |
| -------------------------- | -------------------------------------------------------------------------------- |
| `/specforge.analyze`         | Cross-artifact consistency & coverage analysis                                   |
| `/specforge.review`          | Code quality analysis, technical debt detection, actionable recommendations      |
| `/specforge.checklist`       | Generate quality checklists ("unit tests for English")                           |
| `/specforge.learn`           | Analyze codebase to update architecture registry + module CLAUDE.md files        |
| `/specforge.merge`           | Merge feature branch to main, consolidate docs to /docs                          |

#### Setup & Configuration Commands

| Command                       | Description                                                                 |
| ----------------------------- | --------------------------------------------------------------------------- |
| `/specforge.setup`              | **Orchestrator** - runs all setup-xxx sub-commands                          |
| `/specforge.setup-constitution` | Create/update project constitution                                          |
| `/specforge.setup-docs`         | Initialize /docs domain structure (from-code/from-docs/from-specs)          |
| `/specforge.setup-skills`       | Configure skills based on detected frameworks                               |
| `/specforge.setup-agents`       | Generate specialized subagents                                              |
| `/specforge.setup-mcp`          | Configure MCP server for testing/automation                                 |

#### Utility Commands

| Command                 | Description                                                                      |
| ----------------------- | -------------------------------------------------------------------------------- |
| `/specforge.breakdown`    | Create detailed task plans phase-by-phase                                        |
| `/specforge.taskstoissues`| Convert tasks.md to GitHub issues                                                |

### Workflow Overview

SpecForge supports three workflows: the three-phase workflow with quality gates, the classic
step-by-step full workflow, and the quick workflow for small changes.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                   MACRO PIPELINE (/specforge.workflow)                       │
│                                                                              │
│  ┌── DESIGN ──────────┐  ┌── BUILD ───────────┐  ┌── QA ─────────────────┐  │
│  │ specify            │  │ per phase:         │  │  ┌─ validate ◄──┐     │  │
│  │ clarify (auto)     │  │   breakdown?       │  │  │      │       │     │  │
│  │ plan               │  │   implement        │  │  │   failed?    │     │  │
│  │ ADVERSARIAL REVIEW │─►│   ADVERSARIAL PASS │─►│  │      │  fix ─┘     │  │
│  │ checklists (auto)  │  │ review             │  │  │   max 3 rounds     │  │
│  │ tasks              │  │ corrections        │  │  └──────┬─────────────┘  │
│  │ analyze (auto)     │  │                    │  │ ADVERSARIAL REVIEW      │  │
│  │ complexity analysis│  │                    │  │                         │  │
│  ├────────────────────┤  ├────────────────────┤  ├─────────────────────────┤  │
│  │ DESIGN GATE D1-D10 │  │ BUILD GATE B1-B9   │  │ QA GATE Q1-Q8           │  │
│  └────────────────────┘  └────────────────────┘  └─────────────────────────┘  │
│                                                                              │
│   Each gate returns PASS / PASS WITH CONDITIONS / BLOCK and writes a record  │
│   to specs/{feature}/gates/. A blocked gate stops the next pipeline.         │
│   (auto) = runs non-interactively, applying the recommended answer.          │
└─────────────────────────────────────────────────────────────────────────────┘
```

The classic step-by-step commands remain available and are what the phases call:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FULL WORKFLOW (New Features)                       │
│                                                                              │
│   idea ──► specify ──► clarify ──► plan ──► tasks ──► implement ──► validate│
│     │         │           │          │        │           │            │     │
│     ▼         ▼           ▼          ▼        ▼           ▼            ▼     │
│  idea.md   spec.md    (updates)   plan.md  tasks.md    code         report   │
│            + checklist            research.md                                │
│                                   data-model.md                              │
│                                   contracts/                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         QUICK WORKFLOW (Small Changes)                       │
│                                                                              │
│                              /specforge.change                                 │
│                                    │                                         │
│               ┌────────────────────┼────────────────────┐                    │
│               │                    │                    │                    │
│               ▼                    ▼                    ▼                    │
│           Bug Fix            Spec Tweak           User Feedback              │
│               │                    │                    │                    │
│               ▼                    ▼                    ▼                    │
│          Fix code           Edit spec.md          Apply change               │
│               │                    │                    │                    │
│               └────────────────────┴────────────────────┘                    │
│                                    │                                         │
│                                    ▼                                         │
│                            Update traceability                               │
│                            (tasks.md, spec.md)                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

See [Workflow Guide](./docs/workflows.md) for detailed workflow documentation.

### Skills

`forge init` and `forge update` install SpecForge's skill library into your agent's skills directory
(`.claude/skills/`, `.opencode/skills/`, and so on). Skills carry the methodology; commands are thin
orchestrators that invoke them. Agents also load skills on their own when the work matches, so the
guidance applies outside the slash commands too.

**Method skills** - one per workflow discipline:

`idea-shaping`, `spec-authoring`, `requirements-clarification`, `technical-planning`,
`task-decomposition`, `implementation-execution`, `integration-validation`, `bug-diagnosis`,
`artifact-analysis`, `quality-checklists`, `focused-change`, `feature-merge`, `codebase-learning`,
`constitution-authoring`, `semantic-anchors`, `specforge-workflow`, `adversarial-test-planning`.

**Adversarial review harness** - makes validations that can actually fail:

| Skill | Role |
| ----- | ---- |
| `adversarial-review` | The harness: framing, lens routing, finding schema, severity rubric, verdicts |
| `finding-verification` | Falsification pass - every finding must survive an attempt to prove it wrong |
| `quality-gates` | Entry and exit criteria for each phase, blocking rules, gate records |
| `adversarial-test-planning` | Scenario coverage designed to break the feature, not confirm it |

**Domain lenses** - each one a red-team perspective with probes, attack moves, a severity
calibration and its known false positives:

| Lens | Attacks |
| ---- | ------- |
| `lens-requirements` | Ambiguity, untestability, missing scenarios, hidden assumptions |
| `lens-architecture` | Boundary violations, hidden coupling, unjustified novelty, one-way doors |
| `lens-domain-model` | Illegal states, unenforced invariants, aggregate boundaries, language drift |
| `lens-api-contract` | Drift, breaking changes, weak error semantics, missing idempotency |
| `lens-data` | Migrations, integrity, unbounded queries, cache invalidation, retention |
| `lens-security` | STRIDE, authn/authz, injection, secrets, exposure - with traced exploit paths |
| `lens-privacy-compliance` | Personal data inventory, purpose, retention, deletion, third parties |
| `lens-performance` | Growth functions, I/O in loops, unbounded input, budgets |
| `lens-reliability` | Failure modes, timeouts, retries, partial failure, degraded modes |
| `lens-concurrency` | Races, lost updates, deadlocks, ordering and idempotency assumptions |
| `lens-observability` | Would we notice, how fast, and what would we look at next |
| `lens-testing` | Weak oracles, mocked-away truth, mutation thinking, skipped tests |
| `lens-accessibility` | WCAG 2.2 AA: keyboard, screen reader, contrast, focus, reflow, motion |
| `lens-ux-content` | The five states, dead ends, destructive actions, error copy |
| `lens-i18n` | Time zones, currency, unicode, pluralisation, locale assumptions |
| `lens-operations` | Deploy, rollback, config, flags, runbooks, cost |
| `lens-maintainability` | Fake implementations and stubs first, then smells and dead code |
| `lens-supply-chain` | Dependencies, pinning, install-time code, licences, CI permissions |
| `lens-llm-integration` | Prompt injection, tool authority, ungrounded output, cost bounds |

Lenses are selected automatically from the artifact type and the risk signals present in the change
(see the routing table in `adversarial-review/references/lens-registry.md`), or explicitly:

```bash
/specforge.harness --lens security,concurrency,data
/specforge.harness --focus architecture, design patterns, security, performance
```

`--focus` accepts free text naming domains, in any language, and maps it to lenses - so it stands in
for an agent's own built-in `/review` command without depending on one.

Skills you edit locally are preserved across `forge update`: the CLI tracks what it installed and
only refreshes files that are still unmodified.

### Environment Variables

| Variable          | Description                                                                                                                                                                                                                                                                                            |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `SPECFORGE_FEATURE` | Override feature detection for non-Git repositories. Set to the feature directory name (e.g., `001-photo-albums`) to work on a specific feature when not using Git branches.<br/>\*\*Must be set in the context of the agent you're working with prior to using `/specforge.plan` or follow-up commands. |

## 📚 Core Philosophy

Spec-Driven Development is a structured process that emphasizes:

- **Intent-driven development** where specifications define the "*what*" before the "*how*"
- **Rich specification creation** using guardrails and organizational principles
- **Multi-step refinement** rather than one-shot code generation from prompts
- **Heavy reliance** on advanced AI model capabilities for specification interpretation

## 🌟 Development Phases

| Phase                                    | Focus                    | Key Activities                                                                                                                                                     |
| ---------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **0-to-1 Development** ("Greenfield")    | Generate from scratch    | <ul><li>Start with high-level requirements</li><li>Generate specifications</li><li>Plan implementation steps</li><li>Build production-ready applications</li></ul> |
| **Creative Exploration**                 | Parallel implementations | <ul><li>Explore diverse solutions</li><li>Support multiple technology stacks & architectures</li><li>Experiment with UX patterns</li></ul>                         |
| **Iterative Enhancement** ("Brownfield") | Brownfield modernization | <ul><li>Add features iteratively</li><li>Modernize legacy systems</li><li>Adapt processes</li></ul>                                                                |

## 🎯 Experimental Goals

Our research and experimentation focus on:

### Technology independence

- Create applications using diverse technology stacks
- Validate the hypothesis that Spec-Driven Development is a process not tied to specific technologies, programming languages, or frameworks

### Enterprise constraints

- Demonstrate mission-critical application development
- Incorporate organizational constraints (cloud providers, tech stacks, engineering practices)
- Support enterprise design systems and compliance requirements

### User-centric development

- Build applications for different user cohorts and preferences
- Support various development approaches (from vibe-coding to AI-native development)

### Creative & iterative processes

- Validate the concept of parallel implementation exploration
- Provide robust iterative feature development workflows
- Extend processes to handle upgrades and modernization tasks

## 🔧 Prerequisites

- **Linux/macOS/Windows**
- [Supported](#-supported-ai-agents) AI coding agent.
- [uv](https://docs.astral.sh/uv/) for package management
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

If you encounter issues with an agent, please open an issue so we can refine the integration.

## 📖 Learn More

- **[Complete Spec-Driven Development Methodology](./spec-driven.md)** - Deep dive into the full process
- **[Detailed Walkthrough](#-detailed-process)** - Step-by-step implementation guide

---

## 📋 Detailed Process

<details>
<summary>Click to expand the detailed step-by-step walkthrough</summary>

You can use the Forge CLI to bootstrap your project, which will bring in the required artifacts in your environment. Run:

```bash
forge init <project_name>
```

Or initialize in the current directory:

```bash
forge init .
# or use the --here flag
forge init --here
# Skip confirmation when the directory already has files
forge init . --force
# or
forge init --here --force
```

![Forge CLI bootstrapping a new project in the terminal](./media/specify_cli.gif)

You will be prompted to select the AI agent you are using. You can also proactively specify it directly in the terminal:

```bash
forge init <project_name> --ai claude
forge init <project_name> --ai gemini
forge init <project_name> --ai copilot

# Or in current directory:
forge init . --ai claude
forge init . --ai codex

# or use --here flag
forge init --here --ai claude
forge init --here --ai codex

# Force merge into a non-empty current directory
forge init . --force --ai claude

# or
forge init --here --force --ai claude
```

The CLI will check if you have Claude Code, Gemini CLI, Cursor CLI, Qwen CLI, opencode, Codex CLI, Qoder CLI, or Amazon Q Developer CLI installed. If you do not, or you prefer to get the templates without checking for the right tools, use `--ignore-agent-tools` with your command:

```bash
forge init <project_name> --ai claude --ignore-agent-tools
```

### **STEP 1:** Establish project principles

Go to the project folder and run your AI agent. In our example, we're using `claude`.

![Bootstrapping Claude Code environment](./media/bootstrap-claude-code.gif)

You will know that things are configured correctly if you see the `/specforge.constitution`, `/specforge.specify`, `/specforge.plan`, `/specforge.tasks`, and `/specforge.implement` commands available.

The first step should be establishing your project's governing principles using the `/specforge.constitution` command. This helps ensure consistent decision-making throughout all subsequent development phases:

```text
/specforge.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements. Include governance for how these principles should guide technical decisions and implementation choices.
```

This step creates or updates the `.specforge/memory/constitution.md` file with your project's foundational guidelines that the AI agent will reference during specification, planning, and implementation phases.

### **STEP 2:** Create project specifications

With your project principles established, you can now create the functional specifications. Use the `/specforge.specify` command and then provide the concrete requirements for the project you want to develop.

> [!IMPORTANT]
> Be as explicit as possible about *what* you are trying to build and *why*. **Do not focus on the tech stack at this point**.

An example prompt:

```text
Develop Taskify, a team productivity platform. It should allow users to create projects, add team members,
assign tasks, comment and move tasks between boards in Kanban style. In this initial phase for this feature,
let's call it "Create Taskify," let's have multiple users but the users will be declared ahead of time, predefined.
I want five users in two different categories, one product manager and four engineers. Let's create three
different sample projects. Let's have the standard Kanban columns for the status of each task, such as "To Do,"
"In Progress," "In Review," and "Done." There will be no login for this application as this is just the very
first testing thing to ensure that our basic features are set up. For each task in the UI for a task card,
you should be able to change the current status of the task between the different columns in the Kanban work board.
You should be able to leave an unlimited number of comments for a particular card. You should be able to, from that task
card, assign one of the valid users. When you first launch Taskify, it's going to give you a list of the five users to pick
from. There will be no password required. When you click on a user, you go into the main view, which displays the list of
projects. When you click on a project, you open the Kanban board for that project. You're going to see the columns.
You'll be able to drag and drop cards back and forth between different columns. You will see any cards that are
assigned to you, the currently logged in user, in a different color from all the other ones, so you can quickly
see yours. You can edit any comments that you make, but you can't edit comments that other people made. You can
delete any comments that you made, but you can't delete comments anybody else made.
```

After this prompt is entered, you should see Claude Code kick off the planning and spec drafting process. Claude Code will also trigger some of the built-in scripts to set up the repository.

Once this step is completed, you should have a new branch created (e.g., `001-create-taskify`), as well as a new specification in the `specs/001-create-taskify` directory.

The produced specification should contain a set of user stories and functional requirements, as defined in the template.

At this stage, your project folder contents should resemble the following:

```text
└── .specforge
    ├── memory
    │  └── constitution.md
    ├── scripts
    │  ├── check-prerequisites.sh
    │  ├── common.sh
    │  ├── create-new-feature.sh
    │  ├── setup-plan.sh
    │  └── update-claude-md.sh
    ├── specs
    │  └── 001-create-taskify
    │      └── spec.md
    └── templates
        ├── plan-template.md
        ├── spec-template.md
        └── tasks-template.md
```

### **STEP 3:** Functional specification clarification (required before planning)

With the baseline specification created, you can go ahead and clarify any of the requirements that were not captured properly within the first shot attempt.

You should run the structured clarification workflow **before** creating a technical plan to reduce rework downstream.

Preferred order:

1. Use `/specforge.clarify` (structured) – sequential, coverage-based questioning that records answers in a Clarifications section.
2. Optionally follow up with ad-hoc free-form refinement if something still feels vague.

If you intentionally want to skip clarification (e.g., spike or exploratory prototype), explicitly state that so the agent doesn't block on missing clarifications.

Example free-form refinement prompt (after `/specforge.clarify` if still needed):

```text
For each sample project or project that you create there should be a variable number of tasks between 5 and 15
tasks for each one randomly distributed into different states of completion. Make sure that there's at least
one task in each stage of completion.
```

You should also ask Claude Code to validate the **Review & Acceptance Checklist**, checking off the things that are validated/pass the requirements, and leave the ones that are not unchecked. The following prompt can be used:

```text
Read the review and acceptance checklist, and check off each item in the checklist if the feature spec meets the criteria. Leave it empty if it does not.
```

It's important to use the interaction with Claude Code as an opportunity to clarify and ask questions around the specification - **do not treat its first attempt as final**.

### **STEP 4:** Generate a plan

You can now be specific about the tech stack and other technical requirements. You can use the `/specforge.plan` command that is built into the project template with a prompt like this:

```text
We are going to generate this using .NET Aspire, using Postgres as the database. The frontend should use
Blazor server with drag-and-drop task boards, real-time updates. There should be a REST API created with a projects API,
tasks API, and a notifications API.
```

The output of this step will include a number of implementation detail documents, with your directory tree resembling this:

```text
.
├── CLAUDE.md
├── memory
│  └── constitution.md
├── scripts
│  ├── check-prerequisites.sh
│  ├── common.sh
│  ├── create-new-feature.sh
│  ├── setup-plan.sh
│  └── update-claude-md.sh
├── specs
│  └── 001-create-taskify
│      ├── contracts
│      │  ├── api-spec.json
│      │  └── signalr-spec.md
│      ├── data-model.md
│      ├── plan.md
│      ├── quickstart.md
│      ├── research.md
│      └── spec.md
└── templates
    ├── CLAUDE-template.md
    ├── plan-template.md
    ├── spec-template.md
    └── tasks-template.md
```

Check the `research.md` document to ensure that the right tech stack is used, based on your instructions. You can ask Claude Code to refine it if any of the components stand out, or even have it check the locally-installed version of the platform/framework you want to use (e.g., .NET).

Additionally, you might want to ask Claude Code to research details about the chosen tech stack if it's something that is rapidly changing (e.g., .NET Aspire, JS frameworks), with a prompt like this:

```text
I want you to go through the implementation plan and implementation details, looking for areas that could
benefit from additional research as .NET Aspire is a rapidly changing library. For those areas that you identify that
require further research, I want you to update the research document with additional details about the specific
versions that we are going to be using in this Taskify application and spawn parallel research tasks to clarify
any details using research from the web.
```

During this process, you might find that Claude Code gets stuck researching the wrong thing - you can help nudge it in the right direction with a prompt like this:

```text
I think we need to break this down into a series of steps. First, identify a list of tasks
that you would need to do during implementation that you're not sure of or would benefit
from further research. Write down a list of those tasks. And then for each one of these tasks,
I want you to spin up a separate research task so that the net results is we are researching
all of those very specific tasks in parallel. What I saw you doing was it looks like you were
researching .NET Aspire in general and I don't think that's gonna do much for us in this case.
That's way too untargeted research. The research needs to help you solve a specific targeted question.
```

> [!NOTE]
> Claude Code might be over-eager and add components that you did not ask for. Ask it to clarify the rationale and the source of the change.

### **STEP 5:** Have Claude Code validate the plan

With the plan in place, you should have Claude Code run through it to make sure that there are no missing pieces. You can use a prompt like this:

```text
Now I want you to go and audit the implementation plan and the implementation detail files.
Read through it with an eye on determining whether or not there is a sequence of tasks that you need
to be doing that are obvious from reading this. Because I don't know if there's enough here. For example,
when I look at the core implementation, it would be useful to reference the appropriate places in the implementation
details where it can find the information as it walks through each step in the core implementation or in the refinement.
```

This helps refine the implementation plan and helps you avoid potential blind spots that Claude Code missed in its planning cycle. Once the initial refinement pass is complete, ask Claude Code to go through the checklist once more before you can get to the implementation.

You can also ask Claude Code (if you have the [GitHub CLI](https://docs.github.com/en/github-cli/github-cli) installed) to go ahead and create a pull request from your current branch to `main` with a detailed description, to make sure that the effort is properly tracked.

> [!NOTE]
> Before you have the agent implement it, it's also worth prompting Claude Code to cross-check the details to see if there are any over-engineered pieces (remember - it can be over-eager). If over-engineered components or decisions exist, you can ask Claude Code to resolve them. Ensure that Claude Code follows the [constitution](base/memory/constitution.md) as the foundational piece that it must adhere to when establishing the plan.

### **STEP 6:** Generate task breakdown with /specforge.tasks

With the implementation plan validated, you can now break down the plan into specific, actionable tasks that can be executed in the correct order. Use the `/specforge.tasks` command to automatically generate a detailed task breakdown from your implementation plan:

```text
/specforge.tasks
```

This step creates a `tasks.md` file in your feature specification directory that contains:

- **Task breakdown organized by user story** - Each user story becomes a separate implementation phase with its own set of tasks
- **Dependency management** - Tasks are ordered to respect dependencies between components (e.g., models before services, services before endpoints)
- **Parallel execution markers** - Tasks that can run in parallel are marked with `[P]` to optimize development workflow
- **File path specifications** - Each task includes the exact file paths where implementation should occur
- **Test-driven development structure** - If tests are requested, test tasks are included and ordered to be written before implementation
- **Checkpoint validation** - Each user story phase includes checkpoints to validate independent functionality

The generated tasks.md provides a clear roadmap for the `/specforge.implement` command, ensuring systematic implementation that maintains code quality and allows for incremental delivery of user stories.

### **STEP 7:** Implementation

Once ready, use the `/specforge.implement` command to execute your implementation plan:

```text
/specforge.implement
```

The `/specforge.implement` command will:

- Validate that all prerequisites are in place (constitution, spec, plan, and tasks)
- Parse the task breakdown from `tasks.md`
- Execute tasks in the correct order, respecting dependencies and parallel execution markers
- Follow the TDD approach defined in your task plan
- Provide progress updates and handle errors appropriately

> [!IMPORTANT]
> The AI agent will execute local CLI commands (such as `dotnet`, `npm`, etc.) - make sure you have the required tools installed on your machine.

Once the implementation is complete, test the application and resolve any runtime errors that may not be visible in CLI logs (e.g., browser console errors). You can copy and paste such errors back to your AI agent for resolution.

</details>

---

## 🔍 Troubleshooting

### Git Credential Manager on Linux

If you're having issues with Git authentication on Linux, you can install Git Credential Manager:

```bash
#!/usr/bin/env bash
set -e
echo "Downloading Git Credential Manager v2.6.1..."
wget https://github.com/git-ecosystem/git-credential-manager/releases/download/v2.6.1/gcm-linux_amd64.2.6.1.deb
echo "Installing Git Credential Manager..."
sudo dpkg -i gcm-linux_amd64.2.6.1.deb
echo "Configuring Git to use GCM..."
git config --global credential.helper manager
echo "Cleaning up..."
rm gcm-linux_amd64.2.6.1.deb
```

## 👥 Maintainers

- Hara Peko ([@censseo](https://github.com/censseo))

## 💬 Support

For support, please open a [GitHub issue](https://github.com/Censseo/specforge/issues/new). We welcome bug reports, feature requests, and questions about using Spec-Driven Development.

## 🙏 Acknowledgements

SpecForge is an enhanced fork of [GitHub's Spec Kit](https://github.com/github/spec-kit), originally created by [John Lam](https://github.com/jflam).

This project builds upon the foundational work of Spec Kit with significant improvements:

- Advanced quality analysis (dead code detection, spec deviation analysis)
- Enhanced documentation workflows with `/docs/` integration
- Modular setup architecture with `setup-xxx` commands
- Granular context generation and cross-artifact analysis
- Bootstrap and onboarding capabilities

We're grateful to the Spec Kit team for the excellent foundation that made SpecForge possible.

## 📄 License

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) file for the full terms.
