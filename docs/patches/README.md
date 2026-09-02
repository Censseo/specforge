# Pending Patches

Changes that could not be pushed from an automated session because they touch
`.github/workflows/`, which requires the `workflows` permission.

Apply them from a checkout with the necessary rights:

```bash
git apply docs/patches/<name>.patch
```

Delete the patch file once it has landed.

## release-packaging-skills.patch

Adds skills installation to `.github/workflows/scripts/create-release-packages.sh`, so that the
release zips carry the same skill library that `forge init` installs.

It adds three things to the script:

- `agent_meta()` - the folder, display name, context file, context glob and project-dir env for each
  agent. Mirrors `AGENT_CONFIG` in `src/forge_cli/__init__.py`; keep the two in sync.
- `substitute_agent_placeholders()` - replaces `__AGENT_DIR__`, `__AGENT_NAME__`,
  `__AGENT_CONTEXT_FILE__`, `__AGENT_CONTEXT_GLOB__`, `__AGENT_PROJECT_DIR_ENV__` and `__AGENT__`,
  longest token first. `generate_commands` now uses it, which also fixes those placeholders being
  left unsubstituted in released command files - only `__AGENT__` was replaced before.
- `generate_skills()` - renders `templates/skills/**` into `$base_dir/<agent folder>/skills`, applying
  the `{SCRIPT}` substitution from each skill's own `scripts:` frontmatter plus the placeholder and
  path rewriting, and copying non-Markdown files verbatim.

Until this lands, release packages ship the commands without the skills the commands invoke. Users
who install with `forge init` from the published package are unaffected: the Python path installs
skills itself.
