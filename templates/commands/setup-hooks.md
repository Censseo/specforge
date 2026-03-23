---
description: Generate Claude Code hooks based on detected project tools and chosen profile
scripts:
  sh: scripts/bash/setup-hooks.sh --json --agent-dir __AGENT_DIR__
  ps: scripts/powershell/setup-hooks.ps1 -Json -AgentDir __AGENT_DIR__
---

# Hook Configuration Generator

You are a Hook Configuration Specialist. Generate project-specific Claude Code hooks based on detected tools and the chosen security/quality profile.

## User Input

```text
$ARGUMENTS
```

**Options**:
- `--profile minimal|standard|strict` (default: `standard`)
- `--dry-run` — Show generated hooks without writing to disk

---

## Phase 1: Detection

Run `{SCRIPT}` and parse the JSON output:

| Field | Usage |
|-------|-------|
| `PROJECT_TYPE` | Determine language-specific hooks |
| `FORMATTER` | PostToolUse auto-format command |
| `LINTER` | PreToolUse config protection patterns |
| `TEST_RUNNER` | Stop hook coverage command |
| `AGENT_DIR` | Output path for settings.local.json |

---

## Phase 2: Select Profile

Determine profile from user input (default: `standard`).

| Profile | PreToolUse | PostToolUse | SessionStart | Stop |
|---------|-----------|-------------|-------------|------|
| **minimal** | Secret detection only | — | — | — |
| **standard** | Secret detection, linter config protection | Auto-format, typecheck (if TS) | Load constitution | Coverage reminder |
| **strict** | All standard + console.log blocker | All standard | Load full context | Coverage + security reminder |

---

## Phase 3: Generate Hooks

Build the hooks JSON structure based on selected profile and detected tools.

### 3.1: PreToolUse Hooks

#### Secret Detection (all profiles)

```json
{
  "matcher": "tool == \"Edit\"",
  "hooks": [{
    "type": "command",
    "command": "#!/bin/bash\nFILE=\"$TOOL_INPUT_FILE_PATH\"\nif [ -n \"$TOOL_INPUT_NEW_STRING\" ]; then\n  echo \"$TOOL_INPUT_NEW_STRING\" | grep -qE '(AKIA[A-Z0-9]{16}|ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{20,}|sk_live_[a-zA-Z0-9]+|pk_live_[a-zA-Z0-9]+|-----BEGIN.*PRIVATE KEY-----|xox[bpas]-[a-zA-Z0-9-]+|SG\\.[a-zA-Z0-9_-]+)' && echo '🚫 BLOCKED: Potential secret detected in edit content. Use environment variables instead.' && exit 2\nfi\nexit 0"
  }]
}
```

#### Linter/Formatter Config Protection (standard, strict)

Generate the matcher pattern based on detected LINTER and FORMATTER. Protect config files from accidental modification:

| Detected Tool | Protected Files |
|---------------|----------------|
| eslint | `.eslintrc.*`, `eslint.config.*` |
| prettier | `.prettierrc*`, `prettier.config.*` |
| biome | `biome.json`, `biome.jsonc` |
| ruff | `ruff.toml`, `pyproject.toml` (ruff section) |
| clippy | `clippy.toml`, `.clippy.toml` |
| golangci-lint | `.golangci.yml`, `.golangci.yaml` |
| rubocop | `.rubocop.yml` |
| scalafmt | `.scalafmt.conf` |
| scalafix | `.scalafix.conf` |

```json
{
  "matcher": "tool == \"Edit\" && file_path matches \"\\\\.(eslintrc|prettierrc|biome)\"",
  "hooks": [{
    "type": "command",
    "command": "#!/bin/bash\necho '⚠️  WARNING: You are modifying a linter/formatter configuration file.'\necho 'Make sure this change is intentional.'\nexit 1"
  }]
}
```

Adapt the `file_path matches` pattern to include only the config files relevant to detected tools.

#### Console.log Blocker (strict only)

Only generate for Node.js/TypeScript projects:

```json
{
  "matcher": "tool == \"Edit\" && file_path matches \"\\\\.(ts|tsx|js|jsx)$\"",
  "hooks": [{
    "type": "command",
    "command": "#!/bin/bash\nif [ -n \"$TOOL_INPUT_NEW_STRING\" ]; then\n  echo \"$TOOL_INPUT_NEW_STRING\" | grep -qE 'console\\.(log|debug|info)\\(' && echo '⚠️  WARNING: Debug statement detected. Remove before committing.' && exit 1\nfi\nexit 0"
  }]
}
```

### 3.2: PostToolUse Hooks

#### Auto-Format (standard, strict)

Generate based on detected FORMATTER:

| Formatter | File Matcher | Command |
|-----------|-------------|---------|
| prettier | `\\.(ts\|tsx\|js\|jsx\|json\|css\|md)$` | `npx prettier --write "$TOOL_INPUT_FILE_PATH"` |
| biome | `\\.(ts\|tsx\|js\|jsx\|json)$` | `npx biome format --write "$TOOL_INPUT_FILE_PATH"` |
| black | `\\.py$` | `black --quiet "$TOOL_INPUT_FILE_PATH"` |
| ruff | `\\.py$` | `ruff format --quiet "$TOOL_INPUT_FILE_PATH"` |
| rustfmt | `\\.rs$` | `rustfmt "$TOOL_INPUT_FILE_PATH"` |
| gofmt | `\\.go$` | `gofmt -w "$TOOL_INPUT_FILE_PATH"` |
| scalafmt | `\\.scala$` | `scalafmt "$TOOL_INPUT_FILE_PATH"` |

```json
{
  "matcher": "tool == \"Edit\" && file_path matches \"<EXTENSION_PATTERN>\"",
  "hooks": [{
    "type": "command",
    "command": "#!/bin/bash\n<FORMATTER_COMMAND> 2>/dev/null || true"
  }]
}
```

Replace `<EXTENSION_PATTERN>` and `<FORMATTER_COMMAND>` with the values from the table above.

#### TypeScript Type Check (standard, strict — TypeScript projects only)

Only generate if `typescript` is in DETECTED_TOOLS:

```json
{
  "matcher": "tool == \"Edit\" && file_path matches \"\\\\.(ts|tsx)$\"",
  "hooks": [{
    "type": "command",
    "command": "#!/bin/bash\nnpx tsc --noEmit --pretty 2>&1 | head -20 || true"
  }]
}
```

### 3.3: SessionStart Hook (standard, strict)

```json
{
  "matcher": "",
  "hooks": [{
    "type": "command",
    "command": "#!/bin/bash\nSPEC_DIR=\".specforge\"\nif [ -f \"$SPEC_DIR/memory/constitution.md\" ]; then\n  echo '=== Project Constitution ==='\n  head -50 \"$SPEC_DIR/memory/constitution.md\"\nfi\nif [ -f \"$SPEC_DIR/memory/architecture-registry.md\" ]; then\n  echo ''\n  echo '=== Architecture Registry ==='\n  head -50 \"$SPEC_DIR/memory/architecture-registry.md\"\nfi"
  }]
}
```

### 3.4: Stop Hook (standard, strict)

```json
{
  "matcher": "",
  "hooks": [{
    "type": "command",
    "command": "#!/bin/bash\necho ''\necho '📋 Session ending — Reminders:'\necho '  • Run tests before committing'\necho '  • Check test coverage (target: 80%+)'\necho '  • Review git diff for unintended changes'"
  }]
}
```

For **strict** profile, add:
```bash
echo '  • Run /specforge.security before merge'
echo '  • Run /specforge.verify for quality gates'
```

---

## Phase 4: Assemble & Write

### 4.1: Build settings structure

Assemble all selected hooks into the Claude Code settings format:

```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "...", "hooks": [{ "type": "command", "command": "..." }] }
    ],
    "PostToolUse": [
      { "matcher": "...", "hooks": [{ "type": "command", "command": "..." }] }
    ],
    "SessionStart": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "..." }] }
    ],
    "Stop": [
      { "matcher": "", "hooks": [{ "type": "command", "command": "..." }] }
    ]
  }
}
```

### 4.2: Write or merge

- If `--dry-run`: display the JSON and stop
- If `__AGENT_DIR__/settings.local.json` exists: read it, merge the `hooks` key (preserve other settings), write back
- If it doesn't exist: create it with the hooks structure

### 4.3: Validate

After writing, verify the JSON is valid by parsing it.

---

## Completion

```markdown
## Hooks Setup Complete

**Profile**: {profile}
**Agent**: __AGENT_NAME__

### Hooks Generated

| Phase | Hook | Description |
|-------|------|-------------|
| PreToolUse | Secret Detection | Blocks edits containing API keys/tokens |
| PreToolUse | Config Protection | Warns on linter/formatter config changes |
| PostToolUse | Auto-Format | Runs {formatter} after edits |
| PostToolUse | TypeCheck | Runs tsc --noEmit on TS files |
| SessionStart | Context Loader | Loads constitution + architecture |
| Stop | Reminder | Coverage + test reminders |

**Written to**: `{agent_dir}/settings.local.json`

### Profile Reference
- Switch profile: `/specforge.setup-hooks --profile strict`
- Dry run: `/specforge.setup-hooks --dry-run`

### Next Steps
- Review generated hooks in settings.local.json
- Run `/specforge.setup-agents` to configure subagents
```
