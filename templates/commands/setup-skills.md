---
description: Configure project-specific skills based on detected frameworks, on top of the SpecForge skills installed with the toolkit.
skills:
  - semantic-anchors
scripts:
  sh: scripts/bash/setup-hooks.sh --json --agent-dir __AGENT_DIR__
  ps: scripts/powershell/setup-hooks.ps1 -Json -AgentDir __AGENT_DIR__
---

## User Input

```text
$ARGUMENTS
```

## Purpose

Detect the project's technology stack and create framework-specific skills.

SpecForge already installs its own skill set into `__AGENT_DIR__/skills/` - the workflow method skills
(`spec-authoring`, `technical-planning`, `implementation-execution`, ...), the adversarial review
harness (`adversarial-review`, `finding-verification`, `quality-gates`) and the domain lenses
(`lens-security`, `lens-data`, `lens-accessibility`, ...). This command adds what those cannot know:
the conventions of *this* project's frameworks.

Do not regenerate or overwrite a skill whose name already exists in `__AGENT_DIR__/skills/`. Extend it,
or pick a project-specific name.

---

## Phase 1: Detection

Run `{SCRIPT}` and parse:

```json
{
  "DETECTED_FRAMEWORKS": [
    {"name": "react", "docs_url": "...", "github_url": "..."},
    {"name": "next", "docs_url": "...", "github_url": "..."}
  ],
  "SKILLS_DIR": "/path/to/__AGENT_DIR__/skills"
}
```

---

## Phase 2: Generate Skills

For each detected framework, create a skill file in `{SKILLS_DIR}/`:

### Skill Template

```markdown
---
name: {framework}-patterns
description: {Framework} best practices and patterns for this project
---

# {Framework} Patterns

## Conventions
[Extracted from codebase or framework defaults]

## Best Practices
[Framework-specific guidance]

## Common Patterns
[Code examples from project or defaults]
```

### Skill Categories

| Category | Skill Example | Source |
|----------|---------------|--------|
| Frontend | react-patterns, vue-conventions | Detected frameworks |
| Backend | express-patterns, fastapi-usage | Detected frameworks |
| Database | prisma-patterns, typeorm-usage | Detected ORM |
| Testing | jest-conventions, pytest-patterns | Detected test tools |

---

## Completion

```markdown
## Skills Setup Complete

### Skills Created
| Skill | Framework | Path |
|-------|-----------|------|
| {skill} | {framework} | {path} |

### Next Steps
- Review generated skills
- Add project-specific conventions
- Run /specforge.setup-agents to use skills in agents
```
