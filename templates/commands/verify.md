---
description: Run sequential technical quality gates (build, test, lint, typecheck, security, coverage)
semantic_anchors:
  - Continuous Integration    # Automated build+test on every change, Martin Fowler
  - Fail Fast                 # Detect issues early, provide immediate feedback
  - Quality Gate              # Sonar-style pass/fail criteria before merge
  - Shift Left               # Move testing and verification earlier in the pipeline
handoffs:
  - label: Fix Errors
    agent: specforge.fix
    prompt: Fix the build/test/lint errors found during verification
  - label: Deep Review
    agent: specforge.review
    prompt: Deep-dive into the quality issues found during verification
  - label: Security Audit
    agent: specforge.security
    prompt: Run a comprehensive security audit
scripts:
  sh: scripts/bash/setup-hooks.sh --json --agent-dir __AGENT_DIR__
  ps: scripts/powershell/setup-hooks.ps1 -Json -AgentDir __AGENT_DIR__
---

# Technical Verification

> **Activated Frameworks**: Continuous Integration (Martin Fowler), Fail Fast, Quality Gate, Shift Left.

You are a Quality Gate Enforcer. Run technical checks sequentially, stopping at the first failure. Each gate must pass before the next one runs.

## User Input

```text
$ARGUMENTS
```

**Options**:
- `--all` (default): Run all gates
- `--skip-build`: Skip build gate
- `--skip-test`: Skip test gate
- `--skip-lint`: Skip lint gate
- `--skip-typecheck`: Skip typecheck gate
- `--skip-security`: Skip security gate
- `--skip-coverage`: Skip coverage gate
- `--fix`: Auto-fix lint and format issues where possible
- `--report`: Generate a report file
- `--threshold N`: Coverage threshold percentage (default: 80)

---

## Phase 1: Detection

Run `{SCRIPT}` and parse the JSON output to resolve project tools:

| Field | Gate |
|-------|------|
| `PROJECT_TYPE` | Build, Test commands |
| `PACKAGE_MANAGER` | Command prefix (npm/yarn/pnpm/bun/pip/cargo/go) |
| `TEST_RUNNER` | Test + Coverage commands |
| `LINTER` | Lint command |
| `FORMATTER` | Format command (used with --fix) |

---

## Phase 2: Tool Resolution

Map detected tools to concrete commands. Use the first matching entry.

### Build Commands

| Project Type | Command |
|---|---|
| node-typescript | `{pm} run build` (if build script exists) or `npx tsc --noEmit` |
| node | `{pm} run build` (if build script exists) |
| python | `python -m py_compile $(find . -name '*.py' -not -path './.venv/*')` or build command from pyproject.toml |
| rust | `cargo build 2>&1` |
| go | `go build ./... 2>&1` |
| java-maven | `mvn compile -q 2>&1` |
| java-gradle | `./gradlew compileJava 2>&1` |
| scala-sbt | `sbt compile 2>&1` |
| scala-mill | `mill __.compile 2>&1` |
| dotnet | `dotnet build 2>&1` |
| ruby | `bundle exec rake build 2>&1` (if Rakefile exists) |
| php | `composer run build 2>&1` (if build script exists) |

### Test Commands

| Test Runner | Command |
|---|---|
| jest | `npx jest --passWithNoTests 2>&1` |
| vitest | `npx vitest run 2>&1` |
| mocha | `npx mocha 2>&1` |
| pytest | `python -m pytest -q 2>&1` |
| cargo-test | `cargo test 2>&1` |
| go-test | `go test ./... 2>&1` |
| maven-test | `mvn test -q 2>&1` |
| gradle-test | `./gradlew test 2>&1` |
| sbt-test | `sbt test 2>&1` |
| mill-test | `mill __.test 2>&1` |
| rspec | `bundle exec rspec 2>&1` |
| phpunit | `vendor/bin/phpunit 2>&1` |
| dotnet-test | `dotnet test 2>&1` |

### Lint Commands

| Linter | Command | Fix Command |
|---|---|---|
| eslint | `npx eslint . 2>&1` | `npx eslint . --fix 2>&1` |
| ruff | `ruff check . 2>&1` | `ruff check . --fix 2>&1` |
| clippy | `cargo clippy -- -D warnings 2>&1` | — |
| go-vet | `go vet ./... 2>&1` | — |
| golangci-lint | `golangci-lint run 2>&1` | `golangci-lint run --fix 2>&1` |
| rubocop | `bundle exec rubocop 2>&1` | `bundle exec rubocop -a 2>&1` |
| scalafix | `sbt "scalafixAll --check" 2>&1` | `sbt scalafixAll 2>&1` |
| scalafmt | `scalafmt --check . 2>&1` | `scalafmt . 2>&1` |

### TypeCheck Commands

| Tool | Condition | Command |
|---|---|---|
| tsc | TypeScript detected | `npx tsc --noEmit --pretty 2>&1` |
| mypy | mypy in detected tools | `python -m mypy . 2>&1` |
| — | Go, Rust, Java, Scala | Included in Build gate (skip) |

### Security Commands

| Project Type | Command |
|---|---|
| node (npm) | `npm audit --audit-level=high 2>&1` |
| node (pnpm) | `pnpm audit --audit-level=high 2>&1` |
| node (yarn) | `yarn audit --level high 2>&1` |
| python | `pip-audit 2>&1` (or `safety check 2>&1`) |
| rust | `cargo audit 2>&1` |
| go | `govulncheck ./... 2>&1` |
| java-maven | `mvn org.owasp:dependency-check-maven:check 2>&1` |
| ruby | `bundle-audit check 2>&1` |
| dotnet | `dotnet list package --vulnerable 2>&1` |

### Coverage Commands

| Test Runner | Command | Threshold Check |
|---|---|---|
| jest | `npx jest --coverage --coverageReporters=text-summary 2>&1` | Parse "Statements" line |
| vitest | `npx vitest run --coverage 2>&1` | Parse coverage summary |
| pytest | `python -m pytest --cov --cov-report=term-summary --cov-fail-under={threshold} 2>&1` | Built-in threshold |
| cargo-test | `cargo tarpaulin --out Stdout 2>&1` | Parse coverage % |
| go-test | `go test -cover ./... 2>&1` | Parse "coverage:" lines |

---

## Phase 3: Sequential Execution

Execute each gate in order. **Stop at the first failure**.

### Gate Execution Pattern

For each enabled gate:

1. Print header: `## Gate {N}/6: {NAME}`
2. Print command being run
3. Execute the resolved command via bash
4. Capture exit code and output
5. **If exit code = 0**: Print `✅ PASS` with duration, continue to next gate
6. **If exit code ≠ 0**: Print `❌ FAIL`, show relevant output (last 30 lines), **STOP execution**

### Gate Order

| # | Gate | Skip Condition |
|---|------|---------------|
| 1 | **Build** | `--skip-build` or no build command detected |
| 2 | **Test** | `--skip-test` or no test runner detected |
| 3 | **Lint** | `--skip-lint` or no linter detected |
| 4 | **TypeCheck** | `--skip-typecheck` or type checking included in build |
| 5 | **Security** | `--skip-security` or no security tool available |
| 6 | **Coverage** | `--skip-coverage` or no coverage tool available |

### Auto-Fix Mode (--fix)

If `--fix` is specified:
- Before the Lint gate, run the formatter (if detected): `{formatter} .`
- Use the fix variant of the lint command
- Re-run the lint check after fixing to confirm

---

## Phase 4: Results

### Console Output

Always display the results table:

```markdown
## Verification Results

| # | Gate | Status | Duration |
|---|------|--------|----------|
| 1 | Build | ✅ PASS | 3.2s |
| 2 | Test | ✅ PASS | 12.1s |
| 3 | Lint | ❌ FAIL | 1.5s |
| 4 | TypeCheck | ⏭ SKIPPED | — |
| 5 | Security | ⏭ SKIPPED | — |
| 6 | Coverage | ⏭ SKIPPED | — |

**Result: ❌ FAIL at Gate 3 (Lint)**
```

### Failure Details

When a gate fails, include:
- The command that was run
- The exit code
- The relevant output (last 30 lines, trimmed)
- A brief analysis of the failure cause
- Suggested fix action

### File Report (--report)

If `--report` is specified, write to `verification-report-{date}.md`:

```markdown
# Verification Report

**Date**: {date} | **Project**: {project_type} | **Result**: {PASS|FAIL}

## Gates

| Gate | Status | Duration | Command |
|------|--------|----------|---------|
| ... | ... | ... | ... |

## Failure Details
{if any}

## Environment
- Project Type: {project_type}
- Package Manager: {package_manager}
- Test Runner: {test_runner}
- Linter: {linter}
```

---

## Output

Present the results table and:

- If **all gates PASS**: `✅ All quality gates passed. Ready for merge/deploy.`
- If **FAIL at Build/Test**: Recommend `/specforge.fix` to diagnose root cause
- If **FAIL at Lint**: Suggest re-running with `--fix` for auto-correction
- If **FAIL at Security**: List vulnerable packages and recommend updating
- If **FAIL at Coverage**: Show current % vs threshold, identify uncovered files
