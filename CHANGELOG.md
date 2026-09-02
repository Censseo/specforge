# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to the Forge CLI and templates are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-02

### Added - Skills, Phase Workflow and Adversarial Review

#### Skills are now the source of truth

The methodology that used to live inside each command has moved into skills, installed into every
agent's skills directory (`.claude/skills/`, `.opencode/skills/`, ...) by `forge init` and
`forge update`. Commands are now thin orchestrators that invoke them.

- **Method skills**: `specforge-workflow`, `idea-shaping`, `spec-authoring`,
  `requirements-clarification`, `technical-planning`, `task-decomposition`,
  `implementation-execution`, `integration-validation`, `bug-diagnosis`, `artifact-analysis`,
  `quality-checklists`, `focused-change`, `feature-merge`, `codebase-learning`,
  `constitution-authoring`, `semantic-anchors`
- Skills are also model-invoked: agents load them when the work matches, outside the slash commands
- Locally edited skill files are preserved across `forge update` via a content manifest
  (`skills/.specforge-skills.json`)

#### Macro pipeline commands

Non-interactive pipelines that chain the individual commands, apply recommended defaults instead of
stopping to ask, red-team their output, and gate before handing off.

| Command | Pipeline |
| ------- | -------- |
| `/specforge.workflow` | design → build → qa, resuming from file state, stopping on BLOCK |
| `/specforge.design` | specify → clarify (auto) → plan → adversarial review → checklists (auto) → tasks → analyze (auto) → complexity analysis |
| `/specforge.build` | per phase: breakdown (if complex) → implement → adversarial pass; then review → corrections |
| `/specforge.qa` | validate ⇄ fix loop (max 3 rounds, early exit on no progress) → adversarial release review |
| `/specforge.harness` | The adversarial review harness on any target with any lens selection |

- Each pipeline writes a gate record to `specs/{feature}/gates/` with a verdict of PASS,
  PASS WITH CONDITIONS or BLOCK, and stops rather than feeding a broken artifact to the next stage
- `/specforge.design` writes `complexity-analysis.md` classifying each task phase DIRECT or BREAKDOWN
  and recording its lens exposure; `/specforge.build` consumes it
- `/specforge.qa` writes `qa-report.md` with the validation rounds and remaining failures
- The workflow resumes from file state, so it survives session loss

#### Adversarial test plan

`/specforge.build` now ends by writing `FEATURE_DIR/test-plan.md`, and `/specforge.qa` executes it
instead of deriving scenarios from the spec at run time.

- New skill `adversarial-test-planning`: ten coverage classes (happy path, boundary, invalid input,
  permission, state, failure, concurrency, regression, data integrity, exploratory), derivation moves
  that invert every MUST / NEVER / ONLY in the spec, and a scenario format with preconditions, exact
  steps, an observable expected outcome and a "Fails if" clause
- New command `/specforge.testplan` to produce or regenerate it standalone (`smoke`, `US2`, a class)
- The plan is written at the **end** of build on purpose: `task-results/` deviations and gotchas are
  the most productive source of scenarios, and they do not exist at design time
- Scenarios that cannot run are marked `BLOCKED`; the plan carries an explicit Not Covered section
- `/specforge.validate` gains a test-plan mode: execute by TP id in priority order, report blocked
  scenarios as blocked, and let the plan's "Fails if" decide pass or fail
- QA retry rounds re-run the failing scenarios plus every P1, since a fix can break what passed

#### Final adversarial review at the end of build

- `/specforge.build` gains a final full-branch adversarial pass after the corrections and before the
  test plan, focused on architecture, design patterns, security and performance. It runs there rather
  than at merge because its findings produce code changes, which must land before QA validates
- Cheap fixes are applied in place; a blocking finding makes the build gate BLOCK and no test plan is
  written for code already known to be wrong
- `/specforge.merge` verifies both gate records cleared instead of repeating the review
- `/specforge.harness` gains `--focus`, mapping free text naming domains (in any language) to lenses,
  so it stands in for an agent's built-in `/review` command without depending on one

#### Model selection

- `/specforge.workflow` documents that a slash command runs under one model for its whole execution.
  For a different model per pipeline, run `design`, `build` and `qa` separately - their handoffs chain
  them - or set models on the specialised agents that `/specforge.implement` delegates to

#### Non-interactive and scoped invocation contracts

The sub-commands the pipelines call now document the arguments the pipelines send:

- `clarify`: non-interactive mode applies its own recommended answer per question and records it as a
  written assumption, so the adversarial review can attack it
- `checklist`: non-interactive generation, consolidated multi-domain files, and remediation that fixes
  the spec or plan rather than the checkbox
- `analyze`: remediation mode, with two things it refuses to auto-resolve - a genuine conflict between
  requirements, and a constitution conflict
- `breakdown`: `phase {N}` processes that phase without the progression prompt
- `implement`: `phase {N}` and `--auto-continue` scope execution and remove the prompts, not the rigor

#### Adversarial review harness

- `adversarial-review` - framing, lens routing, finding schema, severity rubric, anti-gaming rules
- `finding-verification` - every finding must survive a falsification attempt before it is reported;
  refuted findings are dropped, not demoted
- `quality-gates` - entry and exit criteria per phase (D1-D10, B1-B9, Q1-Q8), blocking rules, records

#### Domain lenses

Nineteen review lenses, each with probes, attack moves, a severity calibration and its known false
positives: `lens-requirements`, `lens-architecture`, `lens-domain-model`, `lens-api-contract`,
`lens-data`, `lens-security`, `lens-privacy-compliance`, `lens-performance`, `lens-reliability`,
`lens-concurrency`, `lens-observability`, `lens-testing`, `lens-accessibility`, `lens-ux-content`,
`lens-i18n`, `lens-operations`, `lens-maintainability`, `lens-supply-chain`, `lens-llm-integration`.

Lens selection is routed automatically by artifact type and risk signal
(`adversarial-review/references/lens-registry.md`), or chosen explicitly with `--lens`.

### Changed

- All core commands (`specify`, `clarify`, `plan`, `tasks`, `implement`, `validate`, `analyze`,
  `review`, `checklist`, `fix`, `idea`, `change`, `semantic-anchors`) rewritten as thin invokers that
  declare their `skills:` and keep only the operational steps: script wiring, paths and report contracts
- `merge`, `learn`, `breakdown` and `setup-constitution` now reference their skill; their operational
  bodies are unchanged
- `setup-skills` no longer regenerates skills that ship with SpecForge; it adds project-specific ones

### Pending

- Release packaging (`.github/workflows/scripts/create-release-packages.sh`) does not yet install
  skills or substitute the full `__AGENT_*__` placeholder set. The change is prepared in
  `docs/patches/release-packaging-skills.patch` and needs to be applied by someone with the
  `workflows` permission. Until then, release zips ship commands without the skills they invoke;
  installing with `forge init` is unaffected.

## [0.1.0] - 2026-02-08

### BREAKING CHANGE - Project Rebranding

**Spec Kit → SpecForge** 🔨

This project has evolved significantly beyond its original fork and is now **SpecForge** - an enhanced toolkit for Spec-Driven Development.

#### What's Changed

- **CLI renamed**: `specify` → `forge`
- **Package renamed**: `specify-cli` → `forge-cli`
- **Commands renamed**: `/speckit.*` → `/specforge.*`
- **Source directory**: `specify_cli` → `forge_cli`
- **Environment variables**: `SPECIFY_FEATURE` → `SPECFORGE_FEATURE`
- **Repository**: No longer a fork, independent project

#### New Capabilities

This rebranding reflects major improvements over the original Spec Kit:

- **Advanced quality analysis**: Dead code detection, fake implementation detection, spec deviation analysis in `/specforge.review`
- **Enhanced documentation**: `/docs/` as primary data source, OpenSpec-style domain organization
- **Modular workflows**: Refactored setup commands with `setup-xxx` namespace
- **Intelligent learning**: Granular context generation with `/specforge.learn`
- **Better analysis**: Cross-artifact consistency checking with `/specforge.analyze`
- **Bootstrap support**: New `/specforge.bootstrap` for project onboarding

#### Migration Guide

If upgrading from Spec Kit:

1. Uninstall old CLI: `uv tool uninstall specify-cli`
2. Install SpecForge: `uv tool install forge-cli --from git+https://github.com/Censseo/specforge.git`
3. Update slash commands in your workflows from `/speckit.*` to `/specforge.*`
4. Update any scripts/automation using `SPECIFY_FEATURE` to `SPECFORGE_FEATURE`

## [0.0.22] - 2025-11-07

- Support for VS Code/Copilot agents, and moving away from prompts to proper agents with hand-offs.
- Move to use `AGENTS.md` for Copilot workloads, since it's already supported out-of-the-box.
- Adds support for the version command. ([#486](https://github.com/github/spec-kit/issues/486))
- Fixes potential bug with the `create-new-feature.ps1` script that ignores existing feature branches when determining next feature number ([#975](https://github.com/github/spec-kit/issues/975))
- Add graceful fallback and logging for GitHub API rate-limiting during template fetch ([#970](https://github.com/github/spec-kit/issues/970))

## [0.0.21] - 2025-10-21

- Fixes [#975](https://github.com/github/spec-kit/issues/975) (thank you [@fgalarraga](https://github.com/fgalarraga)).
- Adds support for Amp CLI.
- Adds support for VS Code hand-offs and moves prompts to be full-fledged chat modes.
- Adds support for `version` command (addresses [#811](https://github.com/github/spec-kit/issues/811) and [#486](https://github.com/github/spec-kit/issues/486), thank you [@mcasalaina](https://github.com/mcasalaina) and [@dentity007](https://github.com/dentity007)).
- Adds support for rendering the rate limit errors from the CLI when encountered ([#970](https://github.com/github/spec-kit/issues/970), thank you [@psmman](https://github.com/psmman)).

## [0.0.20] - 2025-10-14

### Added

- **Intelligent Branch Naming**: `create-new-feature` scripts now support `--short-name` parameter for custom branch names
  - When `--short-name` provided: Uses the custom name directly (cleaned and formatted)
  - When omitted: Automatically generates meaningful names using stop word filtering and length-based filtering
  - Filters out common stop words (I, want, to, the, for, etc.)
  - Removes words shorter than 3 characters (unless they're uppercase acronyms)
  - Takes 3-4 most meaningful words from the description
  - **Enforces GitHub's 244-byte branch name limit** with automatic truncation and warnings
  - Examples:
    - "I want to create user authentication" → `001-create-user-authentication`
    - "Implement OAuth2 integration for API" → `001-implement-oauth2-integration-api`
    - "Fix payment processing bug" → `001-fix-payment-processing`
    - Very long descriptions are automatically truncated at word boundaries to stay within limits
  - Designed for AI agents to provide semantic short names while maintaining standalone usability

### Changed

- Enhanced help documentation for `create-new-feature.sh` and `create-new-feature.ps1` scripts with examples
- Branch names now validated against GitHub's 244-byte limit with automatic truncation if needed

## [0.0.19] - 2025-10-10

### Added

- Support for CodeBuddy (thank you to [@lispking](https://github.com/lispking) for the contribution).
- You can now see Git-sourced errors in the Forge CLI.

### Changed

- Fixed the path to the constitution in `plan.md` (thank you to [@lyzno1](https://github.com/lyzno1) for spotting).
- Fixed backslash escapes in generated TOML files for Gemini (thank you to [@hsin19](https://github.com/hsin19) for the contribution).
- Implementation command now ensures that the correct ignore files are added (thank you to [@sigent-amazon](https://github.com/sigent-amazon) for the contribution).

## [0.0.18] - 2025-10-06

### Added

- Support for using `.` as a shorthand for current directory in `specify init .` command, equivalent to `--here` flag but more intuitive for users.
- Use the `/speckit.` command prefix to easily discover Spec Kit-related commands.
- Refactor the prompts and templates to simplify their capabilities and how they are tracked. No more polluting things with tests when they are not needed.
- Ensure that tasks are created per user story (simplifies testing and validation).
- Add support for Visual Studio Code prompt shortcuts and automatic script execution.

### Changed

- All command files now prefixed with `speckit.` (e.g., `speckit.specify.md`, `speckit.plan.md`) for better discoverability and differentiation in IDE/CLI command palettes and file explorers

## [0.0.17] - 2025-09-22

### Added

- New `/clarify` command template to surface up to 5 targeted clarification questions for an existing spec and persist answers into a Clarifications section in the spec.
- New `/analyze` command template providing a non-destructive cross-artifact discrepancy and alignment report (spec, clarifications, plan, tasks, constitution) inserted after `/tasks` and before `/implement`.
  - Note: Constitution rules are explicitly treated as non-negotiable; any conflict is a CRITICAL finding requiring artifact remediation, not weakening of principles.

## [0.0.16] - 2025-09-22

### Added

- `--force` flag for `init` command to bypass confirmation when using `--here` in a non-empty directory and proceed with merging/overwriting files.

## [0.0.15] - 2025-09-21

### Added

- Support for Roo Code.

## [0.0.14] - 2025-09-21

### Changed

- Error messages are now shown consistently.

## [0.0.13] - 2025-09-21

### Added

- Support for Kilo Code. Thank you [@shahrukhkhan489](https://github.com/shahrukhkhan489) with [#394](https://github.com/github/spec-kit/pull/394).
- Support for Auggie CLI. Thank you [@hungthai1401](https://github.com/hungthai1401) with [#137](https://github.com/github/spec-kit/pull/137).
- Agent folder security notice displayed after project provisioning completion, warning users that some agents may store credentials or auth tokens in their agent folders and recommending adding relevant folders to `.gitignore` to prevent accidental credential leakage.

### Changed

- Warning displayed to ensure that folks are aware that they might need to add their agent folder to `.gitignore`.
- Cleaned up the `check` command output.

## [0.0.12] - 2025-09-21

### Changed

- Added additional context for OpenAI Codex users - they need to set an additional environment variable, as described in [#417](https://github.com/github/spec-kit/issues/417).

## [0.0.11] - 2025-09-20

### Added

- Codex CLI support (thank you [@honjo-hiroaki-gtt](https://github.com/honjo-hiroaki-gtt) for the contribution in [#14](https://github.com/github/spec-kit/pull/14))
- Codex-aware context update tooling (Bash and PowerShell) so feature plans refresh `AGENTS.md` alongside existing assistants without manual edits.

## [0.0.10] - 2025-09-20

### Fixed

- Addressed [#378](https://github.com/github/spec-kit/issues/378) where a GitHub token may be attached to the request when it was empty.

## [0.0.9] - 2025-09-19

### Changed

- Improved agent selector UI with cyan highlighting for agent keys and gray parentheses for full names

## [0.0.8] - 2025-09-19

### Added

- Windsurf IDE support as additional AI assistant option (thank you [@raedkit](https://github.com/raedkit) for the work in [#151](https://github.com/github/spec-kit/pull/151))
- GitHub token support for API requests to handle corporate environments and rate limiting (contributed by [@zryfish](https://github.com/@zryfish) in [#243](https://github.com/github/spec-kit/pull/243))

### Changed

- Updated README with Windsurf examples and GitHub token usage
- Enhanced release workflow to include Windsurf templates

## [0.0.7] - 2025-09-18

### Changed

- Updated command instructions in the CLI.
- Cleaned up the code to not render agent-specific information when it's generic.

## [0.0.6] - 2025-09-17

### Added

- opencode support as additional AI assistant option

## [0.0.5] - 2025-09-17

### Added

- Qwen Code support as additional AI assistant option

## [0.0.4] - 2025-09-14

### Added

- SOCKS proxy support for corporate environments via `httpx[socks]` dependency

### Fixed

N/A

### Changed

N/A
