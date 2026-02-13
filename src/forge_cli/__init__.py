#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "typer",
#     "rich",
#     "platformdirs",
#     "readchar",
#     "httpx",
# ]
# ///
"""
Forge CLI - Setup tool for SpecForge projects

Usage:
    uvx forge-cli.py init <project-name>
    uvx forge-cli.py init .
    uvx forge-cli.py init --here

Or install globally:
    uv tool install --from forge-cli.py forge-cli
    forge init <project-name>
    forge init .
    forge init --here
"""

import os
import subprocess
import sys
import zipfile
import tempfile
import shutil
import shlex
import json
import re
from pathlib import Path
from typing import Optional, Tuple
import importlib.resources

import typer
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.tree import Tree
from typer.core import TyperGroup

# For cross-platform keyboard input
import readchar
import ssl
import truststore
from datetime import datetime, timezone

ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
client = httpx.Client(verify=ssl_context)

def _github_token(cli_token: str | None = None) -> str | None:
    """Return sanitized GitHub token (cli arg takes precedence) or None."""
    return ((cli_token or os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or "").strip()) or None

def _github_auth_headers(cli_token: str | None = None) -> dict:
    """Return Authorization header dict only when a non-empty token exists."""
    token = _github_token(cli_token)
    return {"Authorization": f"Bearer {token}"} if token else {}

def _parse_rate_limit_headers(headers: httpx.Headers) -> dict:
    """Extract and parse GitHub rate-limit headers."""
    info = {}
    
    # Standard GitHub rate-limit headers
    if "X-RateLimit-Limit" in headers:
        info["limit"] = headers.get("X-RateLimit-Limit")
    if "X-RateLimit-Remaining" in headers:
        info["remaining"] = headers.get("X-RateLimit-Remaining")
    if "X-RateLimit-Reset" in headers:
        reset_epoch = int(headers.get("X-RateLimit-Reset", "0"))
        if reset_epoch:
            reset_time = datetime.fromtimestamp(reset_epoch, tz=timezone.utc)
            info["reset_epoch"] = reset_epoch
            info["reset_time"] = reset_time
            info["reset_local"] = reset_time.astimezone()
    
    # Retry-After header (seconds or HTTP-date)
    if "Retry-After" in headers:
        retry_after = headers.get("Retry-After")
        try:
            info["retry_after_seconds"] = int(retry_after)
        except ValueError:
            # HTTP-date format - not implemented, just store as string
            info["retry_after"] = retry_after
    
    return info

def _format_rate_limit_error(status_code: int, headers: httpx.Headers, url: str) -> str:
    """Format a user-friendly error message with rate-limit information."""
    rate_info = _parse_rate_limit_headers(headers)
    
    lines = [f"GitHub API returned status {status_code} for {url}"]
    lines.append("")
    
    if rate_info:
        lines.append("[bold]Rate Limit Information:[/bold]")
        if "limit" in rate_info:
            lines.append(f"  • Rate Limit: {rate_info['limit']} requests/hour")
        if "remaining" in rate_info:
            lines.append(f"  • Remaining: {rate_info['remaining']}")
        if "reset_local" in rate_info:
            reset_str = rate_info["reset_local"].strftime("%Y-%m-%d %H:%M:%S %Z")
            lines.append(f"  • Resets at: {reset_str}")
        if "retry_after_seconds" in rate_info:
            lines.append(f"  • Retry after: {rate_info['retry_after_seconds']} seconds")
        lines.append("")
    
    # Add troubleshooting guidance
    lines.append("[bold]Troubleshooting Tips:[/bold]")
    lines.append("  • If you're on a shared CI or corporate environment, you may be rate-limited.")
    lines.append("  • Consider using a GitHub token via --github-token or the GH_TOKEN/GITHUB_TOKEN")
    lines.append("    environment variable to increase rate limits.")
    lines.append("  • Authenticated requests have a limit of 5,000/hour vs 60/hour for unauthenticated.")
    
    return "\n".join(lines)

# Agent configuration with name, folder, install URL, and CLI tool requirement
AGENT_CONFIG = {
    "copilot": {
        "name": "GitHub Copilot",
        "folder": ".github/",
        "install_url": None,  # IDE-based, no CLI check needed
        "requires_cli": False,
        "context_file": "copilot-instructions.md",
        "context_glob": "**/*copilot-instructions.md",
        "project_dir_env": "$PWD",
    },
    "claude": {
        "name": "Claude Code",
        "folder": ".claude/",
        "install_url": "https://docs.anthropic.com/en/docs/claude-code/setup",
        "requires_cli": True,
        "context_file": "CLAUDE.md",
        "context_glob": "**/*CLAUDE.md",
        "project_dir_env": "$CLAUDE_PROJECT_DIR",
    },
    "gemini": {
        "name": "Gemini CLI",
        "folder": ".gemini/",
        "install_url": "https://github.com/google-gemini/gemini-cli",
        "requires_cli": True,
        "context_file": "GEMINI.md",
        "context_glob": "**/*GEMINI.md",
        "project_dir_env": "$PWD",
    },
    "cursor-agent": {
        "name": "Cursor",
        "folder": ".cursor/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
        "context_file": "specify-rules.mdc",
        "context_glob": "**/*specify-rules.mdc",
        "project_dir_env": "$PWD",
    },
    "qwen": {
        "name": "Qwen Code",
        "folder": ".qwen/",
        "install_url": "https://github.com/QwenLM/qwen-code",
        "requires_cli": True,
        "context_file": "QWEN.md",
        "context_glob": "**/*QWEN.md",
        "project_dir_env": "$PWD",
    },
    "opencode": {
        "name": "opencode",
        "folder": ".opencode/",
        "install_url": "https://opencode.ai",
        "requires_cli": True,
        "context_file": "AGENTS.md",
        "context_glob": "**/*AGENTS.md",
        "project_dir_env": "$PWD",
    },
    "codex": {
        "name": "Codex CLI",
        "folder": ".codex/",
        "install_url": "https://github.com/openai/codex",
        "requires_cli": True,
        "context_file": "AGENTS.md",
        "context_glob": "**/*AGENTS.md",
        "project_dir_env": "$PWD",
    },
    "windsurf": {
        "name": "Windsurf",
        "folder": ".windsurf/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
        "context_file": "specify-rules.md",
        "context_glob": "**/*specify-rules.md",
        "project_dir_env": "$PWD",
    },
    "kilocode": {
        "name": "Kilo Code",
        "folder": ".kilocode/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
        "context_file": "specify-rules.md",
        "context_glob": "**/*specify-rules.md",
        "project_dir_env": "$PWD",
    },
    "auggie": {
        "name": "Auggie CLI",
        "folder": ".augment/",
        "install_url": "https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli",
        "requires_cli": True,
        "context_file": "specify-rules.md",
        "context_glob": "**/*specify-rules.md",
        "project_dir_env": "$PWD",
    },
    "codebuddy": {
        "name": "CodeBuddy",
        "folder": ".codebuddy/",
        "install_url": "https://www.codebuddy.ai/cli",
        "requires_cli": True,
        "context_file": "CODEBUDDY.md",
        "context_glob": "**/*CODEBUDDY.md",
        "project_dir_env": "$PWD",
    },
    "qoder": {
        "name": "Qoder CLI",
        "folder": ".qoder/",
        "install_url": "https://qoder.com/cli",
        "requires_cli": True,
        "context_file": "QODER.md",
        "context_glob": "**/*QODER.md",
        "project_dir_env": "$PWD",
    },
    "roo": {
        "name": "Roo Code",
        "folder": ".roo/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
        "context_file": "specify-rules.md",
        "context_glob": "**/*specify-rules.md",
        "project_dir_env": "$PWD",
    },
    "q": {
        "name": "Amazon Q Developer CLI",
        "folder": ".amazonq/",
        "install_url": "https://aws.amazon.com/developer/learning/q-developer-cli/",
        "requires_cli": True,
        "context_file": "AGENTS.md",
        "context_glob": "**/*AGENTS.md",
        "project_dir_env": "$PWD",
    },
    "amp": {
        "name": "Amp",
        "folder": ".agents/",
        "install_url": "https://ampcode.com/manual#install",
        "requires_cli": True,
        "context_file": "AGENTS.md",
        "context_glob": "**/*AGENTS.md",
        "project_dir_env": "$PWD",
    },
    "shai": {
        "name": "SHAI",
        "folder": ".shai/",
        "install_url": "https://github.com/ovh/shai",
        "requires_cli": True,
        "context_file": "SHAI.md",
        "context_glob": "**/*SHAI.md",
        "project_dir_env": "$PWD",
    },
    "bob": {
        "name": "IBM Bob",
        "folder": ".bob/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
        "context_file": "AGENTS.md",
        "context_glob": "**/*AGENTS.md",
        "project_dir_env": "$PWD",
    },
}

SCRIPT_TYPE_CHOICES = {"sh": "POSIX Shell (bash/zsh)", "ps": "PowerShell"}

# Maps agent key -> (command_dir_relative, file_extension, argument_format)
AGENT_COMMAND_DIRS = {
    "claude": (".claude/commands", "md", "$ARGUMENTS"),
    "gemini": (".gemini/commands", "toml", "{{args}}"),
    "copilot": (".github/agents", "agent.md", "$ARGUMENTS"),
    "cursor-agent": (".cursor/commands", "md", "$ARGUMENTS"),
    "qwen": (".qwen/commands", "toml", "{{args}}"),
    "opencode": (".opencode/command", "md", "$ARGUMENTS"),
    "windsurf": (".windsurf/workflows", "md", "$ARGUMENTS"),
    "codex": (".codex/prompts", "md", "$ARGUMENTS"),
    "kilocode": (".kilocode/workflows", "md", "$ARGUMENTS"),
    "auggie": (".augment/commands", "md", "$ARGUMENTS"),
    "roo": (".roo/commands", "md", "$ARGUMENTS"),
    "codebuddy": (".codebuddy/commands", "md", "$ARGUMENTS"),
    "amp": (".agents/commands", "md", "$ARGUMENTS"),
    "shai": (".shai/commands", "md", "$ARGUMENTS"),
    "q": (".amazonq/prompts", "md", "$ARGUMENTS"),
    "qoder": (".qoder/commands", "md", "$ARGUMENTS"),
    "bob": (".bob/commands", "md", "$ARGUMENTS"),
}

# Maps agent key -> context file path relative to project root
# Derived from update-agent-context.sh lines 62-77
AGENT_CONTEXT_PATHS = {
    "claude": "CLAUDE.md",
    "gemini": "GEMINI.md",
    "copilot": ".github/agents/copilot-instructions.md",
    "cursor-agent": ".cursor/rules/specify-rules.mdc",
    "qwen": "QWEN.md",
    "opencode": "AGENTS.md",
    "codex": "AGENTS.md",
    "windsurf": ".windsurf/rules/specify-rules.md",
    "kilocode": ".kilocode/rules/specify-rules.md",
    "auggie": ".augment/rules/specify-rules.md",
    "codebuddy": "CODEBUDDY.md",
    "qoder": "QODER.md",
    "roo": ".roo/rules/specify-rules.md",
    "q": "AGENTS.md",
    "amp": "AGENTS.md",
    "shai": "SHAI.md",
    "bob": "AGENTS.md",
}

CLAUDE_LOCAL_PATH = Path.home() / ".claude" / "local" / "claude"

def get_bundled_path() -> Optional[Path]:
    """Get the path to bundled templates/scripts if they exist.

    Returns the path to the bundled resources directory, or None if not bundled.
    """
    try:
        # Try to find bundled resources in the package
        pkg_path = Path(__file__).parent
        bundled_path = pkg_path / "bundled"
        if bundled_path.exists() and (bundled_path / "templates").exists():
            return bundled_path
        return None
    except Exception:
        return None

def _rewrite_paths_for_bundled(content: str) -> str:
    """Rewrite paths in template content for bundled templates."""
    # Same logic as create-release-packages.sh rewrite_paths
    # Match: (optional /)memory/ or scripts/ or templates/
    # But NOT when already prefixed with .specforge (e.g., ".specforge/scripts/")
    # Match at: start of line, after whitespace, after backtick, after quote
    for path in ['memory', 'scripts', 'templates']:
        # Match at start of string or line
        content = re.sub(rf'^(/?){path}/', rf'.specforge/{path}/', content, flags=re.MULTILINE)
        # Match after whitespace, backtick, or quotes
        content = re.sub(rf'(?<=[\s`"\'])(/?){path}/', rf'.specforge/{path}/', content)
    return content

def generate_agent_commands(
    ai_assistant: str,
    script_type: str,
    target_dir: Path,
    bundled_path: Path,
) -> bool:
    """Generate agent-specific command files from bundled templates.

    Handles processing command templates with agent-specific substitutions,
    creating output files in the appropriate format (md, toml, agent.md),
    copilot-specific prompt files, and agent-specific template files.

    Args:
        ai_assistant: The AI assistant key (claude, copilot, etc.)
        script_type: Script type (sh or ps)
        target_dir: Project root directory
        bundled_path: Path to bundled resources

    Returns:
        True if generation succeeded, False otherwise
    """
    templates_dir = bundled_path / "templates"
    agent_templates_dir = bundled_path / "agent_templates"
    commands_source = templates_dir / "commands"

    if not commands_source.exists():
        return False

    if ai_assistant not in AGENT_COMMAND_DIRS:
        return False

    cmd_dir, file_ext, arg_format = AGENT_COMMAND_DIRS[ai_assistant]
    output_dir = target_dir / cmd_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each command template
    script_variant = script_type
    for template_file in commands_source.glob("*.md"):
        name = template_file.stem
        content = template_file.read_text(encoding="utf-8")

        # Normalize line endings
        content = content.replace("\r\n", "\n").replace("\r", "\n")

        # Extract description from frontmatter
        description = ""
        desc_match = re.search(r'^description:\s*(.+)$', content, re.MULTILINE)
        if desc_match:
            description = desc_match.group(1).strip()

        # Extract script command for this variant
        script_command = ""
        script_pattern = rf'^\s*{script_variant}:\s*(.+)$'
        script_match = re.search(script_pattern, content, re.MULTILINE)
        if script_match:
            script_command = script_match.group(1).strip()

        # Replace {SCRIPT} placeholder
        content = content.replace("{SCRIPT}", script_command)

        # Remove scripts: and agent_scripts: sections from frontmatter
        lines = content.split("\n")
        filtered_lines = []
        skip_section = False
        for line in lines:
            if re.match(r'^scripts:\s*$', line) or re.match(r'^agent_scripts:\s*$', line):
                skip_section = True
                continue
            if skip_section and line.startswith("  "):
                continue
            if skip_section and (line.startswith("---") or (line and not line.startswith(" "))):
                skip_section = False
            if not skip_section:
                filtered_lines.append(line)
        content = "\n".join(filtered_lines)

        # Apply substitutions
        content = content.replace("{ARGS}", arg_format)

        # Agent-agnostic placeholders (MUST be replaced before __AGENT__
        # to avoid substring collision: __AGENT_DIR__ contains __AGENT__)
        agent_cfg = AGENT_CONFIG[ai_assistant]
        agent_dir = agent_cfg["folder"].rstrip("/")
        content = content.replace("__AGENT_DIR__", agent_dir)
        content = content.replace("__AGENT_NAME__", agent_cfg["name"])
        content = content.replace("__AGENT_CONTEXT_FILE__", agent_cfg.get("context_file", ""))
        content = content.replace("__AGENT_CONTEXT_GLOB__", agent_cfg.get("context_glob", ""))
        content = content.replace("__AGENT_PROJECT_DIR_ENV__", agent_cfg.get("project_dir_env", "$PWD"))

        # Agent key placeholder (e.g. "claude", "opencode")
        content = content.replace("__AGENT__", ai_assistant)
        content = _rewrite_paths_for_bundled(content)

        # Write output file
        if file_ext == "toml":
            # Escape backslashes for TOML
            content = content.replace("\\", "\\\\")
            output_content = f'description = "{description}"\n\nprompt = """\n{content}\n"""\n'
            output_file = output_dir / f"specforge.{name}.toml"
        elif file_ext == "agent.md":
            output_file = output_dir / f"specforge.{name}.agent.md"
            output_content = content
        else:
            output_file = output_dir / f"specforge.{name}.md"
            output_content = content

        output_file.write_text(output_content, encoding="utf-8")

    # Handle copilot-specific prompt files
    if ai_assistant == "copilot":
        prompts_dir = target_dir / ".github" / "prompts"
        prompts_dir.mkdir(parents=True, exist_ok=True)
        for agent_file in output_dir.glob("specforge.*.agent.md"):
            basename = agent_file.stem.replace(".agent", "")
            prompt_file = prompts_dir / f"{basename}.prompt.md"
            prompt_file.write_text(f"---\nagent: {basename}\n---\n", encoding="utf-8")

        # Create VS Code settings
        vscode_dir = target_dir / ".vscode"
        vscode_dir.mkdir(parents=True, exist_ok=True)
        vscode_settings = templates_dir / "vscode-settings.json"
        if vscode_settings.exists():
            handle_vscode_settings(vscode_settings, vscode_dir / "settings.json", Path("settings.json"))

    # Copy agent-specific files (like GEMINI.md, QWEN.md)
    if agent_templates_dir.exists():
        agent_specific_dir = agent_templates_dir / ai_assistant
        if agent_specific_dir.exists():
            for f in agent_specific_dir.iterdir():
                if f.is_file():
                    shutil.copy2(f, target_dir / f.name)

    return True


def build_template_from_bundled(
    ai_assistant: str,
    script_type: str,
    target_dir: Path,
    bundled_path: Path,
    verbose: bool = True,
    tracker: "StepTracker" = None
) -> bool:
    """Build template structure from bundled templates (similar to create-release-packages.sh).

    Args:
        ai_assistant: The AI assistant to build for (claude, copilot, etc.)
        script_type: Script type (sh or ps)
        target_dir: Directory to build the template into
        bundled_path: Path to bundled resources
        verbose: Whether to print verbose output
        tracker: Optional step tracker for progress

    Returns:
        True if build succeeded, False otherwise
    """
    templates_dir = bundled_path / "templates"
    scripts_dir = bundled_path / "scripts"
    memory_dir = bundled_path / "memory"
    agent_templates_dir = bundled_path / "agent_templates"

    if not templates_dir.exists():
        return False

    try:
        # Create .specforge directory structure
        specify_dir = target_dir / ".specforge"
        specify_dir.mkdir(parents=True, exist_ok=True)

        # Copy memory
        if memory_dir.exists():
            shutil.copytree(memory_dir, specify_dir / "memory", dirs_exist_ok=True)

        # Copy scripts based on variant
        if scripts_dir.exists():
            scripts_dest = specify_dir / "scripts"
            scripts_dest.mkdir(parents=True, exist_ok=True)

            if script_type == "sh":
                bash_dir = scripts_dir / "bash"
                if bash_dir.exists():
                    shutil.copytree(bash_dir, scripts_dest / "bash", dirs_exist_ok=True)
            elif script_type == "ps":
                ps_dir = scripts_dir / "powershell"
                if ps_dir.exists():
                    shutil.copytree(ps_dir, scripts_dest / "powershell", dirs_exist_ok=True)

            # Copy any root-level script files
            for f in scripts_dir.iterdir():
                if f.is_file():
                    shutil.copy2(f, scripts_dest / f.name)

        # Copy templates (except commands/ and vscode-settings.json)
        templates_dest = specify_dir / "templates"
        templates_dest.mkdir(parents=True, exist_ok=True)
        for item in templates_dir.iterdir():
            if item.name != "commands" and item.name != "vscode-settings.json":
                if item.is_file():
                    shutil.copy2(item, templates_dest / item.name)
                elif item.is_dir():
                    shutil.copytree(item, templates_dest / item.name, dirs_exist_ok=True)

        # Generate agent-specific commands
        if not generate_agent_commands(ai_assistant, script_type, target_dir, bundled_path):
            return False

        if tracker:
            tracker.complete("bundled", "templates built from package")
        elif verbose:
            console.print("[green]✓[/green] Built templates from bundled package")

        return True

    except Exception as e:
        if tracker:
            tracker.error("bundled", str(e))
        elif verbose:
            console.print(f"[yellow]Warning:[/yellow] Could not build from bundled templates: {e}")
        return False

BANNER = """
███████╗██████╗ ███████╗ ██████╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗
██╔════╝██╔══██╗██╔════╝██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
███████╗██████╔╝█████╗  ██║     █████╗  ██║   ██║██████╔╝██║  ███╗█████╗
╚════██║██╔═══╝ ██╔══╝  ██║     ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
███████║██║     ███████╗╚██████╗██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚══════╝╚═╝     ╚══════╝ ╚═════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
"""

TAGLINE = "SpecForge - Spec-Driven Development Toolkit"
class StepTracker:
    """Track and render hierarchical steps without emojis, similar to Claude Code tree output.
    Supports live auto-refresh via an attached refresh callback.
    """
    def __init__(self, title: str):
        self.title = title
        self.steps = []  # list of dicts: {key, label, status, detail}
        self.status_order = {"pending": 0, "running": 1, "done": 2, "error": 3, "skipped": 4}
        self._refresh_cb = None  # callable to trigger UI refresh

    def attach_refresh(self, cb):
        self._refresh_cb = cb

    def add(self, key: str, label: str):
        if key not in [s["key"] for s in self.steps]:
            self.steps.append({"key": key, "label": label, "status": "pending", "detail": ""})
            self._maybe_refresh()

    def start(self, key: str, detail: str = ""):
        self._update(key, status="running", detail=detail)

    def complete(self, key: str, detail: str = ""):
        self._update(key, status="done", detail=detail)

    def error(self, key: str, detail: str = ""):
        self._update(key, status="error", detail=detail)

    def skip(self, key: str, detail: str = ""):
        self._update(key, status="skipped", detail=detail)

    def _update(self, key: str, status: str, detail: str):
        for s in self.steps:
            if s["key"] == key:
                s["status"] = status
                if detail:
                    s["detail"] = detail
                self._maybe_refresh()
                return

        self.steps.append({"key": key, "label": key, "status": status, "detail": detail})
        self._maybe_refresh()

    def _maybe_refresh(self):
        if self._refresh_cb:
            try:
                self._refresh_cb()
            except Exception:
                pass

    def render(self):
        tree = Tree(f"[cyan]{self.title}[/cyan]", guide_style="grey50")
        for step in self.steps:
            label = step["label"]
            detail_text = step["detail"].strip() if step["detail"] else ""

            status = step["status"]
            if status == "done":
                symbol = "[green]●[/green]"
            elif status == "pending":
                symbol = "[green dim]○[/green dim]"
            elif status == "running":
                symbol = "[cyan]○[/cyan]"
            elif status == "error":
                symbol = "[red]●[/red]"
            elif status == "skipped":
                symbol = "[yellow]○[/yellow]"
            else:
                symbol = " "

            if status == "pending":
                # Entire line light gray (pending)
                if detail_text:
                    line = f"{symbol} [bright_black]{label} ({detail_text})[/bright_black]"
                else:
                    line = f"{symbol} [bright_black]{label}[/bright_black]"
            else:
                # Label white, detail (if any) light gray in parentheses
                if detail_text:
                    line = f"{symbol} [white]{label}[/white] [bright_black]({detail_text})[/bright_black]"
                else:
                    line = f"{symbol} [white]{label}[/white]"

            tree.add(line)
        return tree

def get_key():
    """Get a single keypress in a cross-platform way using readchar."""
    key = readchar.readkey()

    if key == readchar.key.UP or key == readchar.key.CTRL_P:
        return 'up'
    if key == readchar.key.DOWN or key == readchar.key.CTRL_N:
        return 'down'

    if key == readchar.key.ENTER:
        return 'enter'

    if key == readchar.key.ESC:
        return 'escape'

    if key == readchar.key.CTRL_C:
        raise KeyboardInterrupt

    return key

def select_with_arrows(options: dict, prompt_text: str = "Select an option", default_key: str = None) -> str:
    """
    Interactive selection using arrow keys with Rich Live display.
    
    Args:
        options: Dict with keys as option keys and values as descriptions
        prompt_text: Text to show above the options
        default_key: Default option key to start with
        
    Returns:
        Selected option key
    """
    option_keys = list(options.keys())
    if default_key and default_key in option_keys:
        selected_index = option_keys.index(default_key)
    else:
        selected_index = 0

    selected_key = None

    def create_selection_panel():
        """Create the selection panel with current selection highlighted."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="white", justify="left")

        for i, key in enumerate(option_keys):
            if i == selected_index:
                table.add_row("▶", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")
            else:
                table.add_row(" ", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")

        table.add_row("", "")
        table.add_row("", "[dim]Use ↑/↓ to navigate, Enter to select, Esc to cancel[/dim]")

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_key, selected_index
        with Live(create_selection_panel(), console=console, transient=True, auto_refresh=False) as live:
            while True:
                try:
                    key = get_key()
                    if key == 'up':
                        selected_index = (selected_index - 1) % len(option_keys)
                    elif key == 'down':
                        selected_index = (selected_index + 1) % len(option_keys)
                    elif key == 'enter':
                        selected_key = option_keys[selected_index]
                        break
                    elif key == 'escape':
                        console.print("\n[yellow]Selection cancelled[/yellow]")
                        raise typer.Exit(1)

                    live.update(create_selection_panel(), refresh=True)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Selection cancelled[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()

    if selected_key is None:
        console.print("\n[red]Selection failed.[/red]")
        raise typer.Exit(1)

    return selected_key

console = Console()

class BannerGroup(TyperGroup):
    """Custom group that shows banner before help."""

    def format_help(self, ctx, formatter):
        # Show banner before help
        show_banner()
        super().format_help(ctx, formatter)


app = typer.Typer(
    name="forge",
    help="Setup tool for SpecForge spec-driven development projects",
    add_completion=False,
    invoke_without_command=True,
    cls=BannerGroup,
)

def show_banner():
    """Display the ASCII art banner."""
    banner_lines = BANNER.strip().split('\n')
    colors = ["bright_blue", "blue", "cyan", "bright_cyan", "white", "bright_white"]

    styled_banner = Text()
    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        styled_banner.append(line + "\n", style=color)

    console.print(Align.center(styled_banner))
    console.print(Align.center(Text(TAGLINE, style="italic bright_yellow")))
    console.print()

@app.callback()
def callback(ctx: typer.Context):
    """Show banner when no subcommand is provided."""
    if ctx.invoked_subcommand is None and "--help" not in sys.argv and "-h" not in sys.argv:
        show_banner()
        console.print(Align.center("[dim]Run 'specify --help' for usage information[/dim]"))
        console.print()

def run_command(cmd: list[str], check_return: bool = True, capture: bool = False, shell: bool = False) -> Optional[str]:
    """Run a shell command and optionally capture output."""
    try:
        if capture:
            result = subprocess.run(cmd, check=check_return, capture_output=True, text=True, shell=shell)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=check_return, shell=shell)
            return None
    except subprocess.CalledProcessError as e:
        if check_return:
            console.print(f"[red]Error running command:[/red] {' '.join(cmd)}")
            console.print(f"[red]Exit code:[/red] {e.returncode}")
            if hasattr(e, 'stderr') and e.stderr:
                console.print(f"[red]Error output:[/red] {e.stderr}")
            raise
        return None

def check_tool(tool: str, tracker: StepTracker = None) -> bool:
    """Check if a tool is installed. Optionally update tracker.
    
    Args:
        tool: Name of the tool to check
        tracker: Optional StepTracker to update with results
        
    Returns:
        True if tool is found, False otherwise
    """
    # Special handling for Claude CLI after `claude migrate-installer`
    # See: https://github.com/github/specforge/issues/123
    # The migrate-installer command REMOVES the original executable from PATH
    # and creates an alias at ~/.claude/local/claude instead
    # This path should be prioritized over other claude executables in PATH
    if tool == "claude":
        if CLAUDE_LOCAL_PATH.exists() and CLAUDE_LOCAL_PATH.is_file():
            if tracker:
                tracker.complete(tool, "available")
            return True
    
    found = shutil.which(tool) is not None
    
    if tracker:
        if found:
            tracker.complete(tool, "available")
        else:
            tracker.error(tool, "not found")
    
    return found

def is_git_repo(path: Path = None) -> bool:
    """Check if the specified path is inside a git repository."""
    if path is None:
        path = Path.cwd()
    
    if not path.is_dir():
        return False

    try:
        # Use git command to check if inside a work tree
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            check=True,
            capture_output=True,
            cwd=path,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def init_git_repo(project_path: Path, quiet: bool = False) -> Tuple[bool, Optional[str]]:
    """Initialize a git repository in the specified path.
    
    Args:
        project_path: Path to initialize git repository in
        quiet: if True suppress console output (tracker handles status)
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    try:
        original_cwd = Path.cwd()
        os.chdir(project_path)
        if not quiet:
            console.print("[cyan]Initializing git repository...[/cyan]")
        subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
        subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", "Initial commit from Specify template"], check=True, capture_output=True, text=True)
        if not quiet:
            console.print("[green]✓[/green] Git repository initialized")
        return True, None

    except subprocess.CalledProcessError as e:
        error_msg = f"Command: {' '.join(e.cmd)}\nExit code: {e.returncode}"
        if e.stderr:
            error_msg += f"\nError: {e.stderr.strip()}"
        elif e.stdout:
            error_msg += f"\nOutput: {e.stdout.strip()}"
        
        if not quiet:
            console.print(f"[red]Error initializing git repository:[/red] {e}")
        return False, error_msg
    finally:
        os.chdir(original_cwd)

def handle_vscode_settings(sub_item, dest_file, rel_path, verbose=False, tracker=None) -> None:
    """Handle merging or copying of .vscode/settings.json files."""
    def log(message, color="green"):
        if verbose and not tracker:
            console.print(f"[{color}]{message}[/] {rel_path}")

    try:
        with open(sub_item, 'r', encoding='utf-8') as f:
            new_settings = json.load(f)

        if dest_file.exists():
            merged = merge_json_files(dest_file, new_settings, verbose=verbose and not tracker)
            with open(dest_file, 'w', encoding='utf-8') as f:
                json.dump(merged, f, indent=4)
                f.write('\n')
            log("Merged:", "green")
        else:
            shutil.copy2(sub_item, dest_file)
            log("Copied (no existing settings.json):", "blue")

    except Exception as e:
        log(f"Warning: Could not merge, copying instead: {e}", "yellow")
        shutil.copy2(sub_item, dest_file)

def merge_json_files(existing_path: Path, new_content: dict, verbose: bool = False) -> dict:
    """Merge new JSON content into existing JSON file.

    Performs a deep merge where:
    - New keys are added
    - Existing keys are preserved unless overwritten by new content
    - Nested dictionaries are merged recursively
    - Lists and other values are replaced (not merged)

    Args:
        existing_path: Path to existing JSON file
        new_content: New JSON content to merge in
        verbose: Whether to print merge details

    Returns:
        Merged JSON content as dict
    """
    try:
        with open(existing_path, 'r', encoding='utf-8') as f:
            existing_content = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is invalid, just use new content
        return new_content

    def deep_merge(base: dict, update: dict) -> dict:
        """Recursively merge update dict into base dict."""
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = deep_merge(result[key], value)
            else:
                # Add new key or replace existing value
                result[key] = value
        return result

    merged = deep_merge(existing_content, new_content)

    if verbose:
        console.print(f"[cyan]Merged JSON file:[/cyan] {existing_path.name}")

    return merged

def download_template_from_github(ai_assistant: str, download_dir: Path, *, script_type: str = "sh", verbose: bool = True, show_progress: bool = True, client: httpx.Client = None, debug: bool = False, github_token: str = None) -> Tuple[Path, dict]:
    repo_owner = "Censseo"
    repo_name = "specforge"
    if client is None:
        client = httpx.Client(verify=ssl_context)

    if verbose:
        console.print("[cyan]Fetching latest release information...[/cyan]")
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    try:
        response = client.get(
            api_url,
            timeout=30,
            follow_redirects=True,
            headers=_github_auth_headers(github_token),
        )
        status = response.status_code
        if status != 200:
            # Format detailed error message with rate-limit info
            error_msg = _format_rate_limit_error(status, response.headers, api_url)
            if debug:
                error_msg += f"\n\n[dim]Response body (truncated 500):[/dim]\n{response.text[:500]}"
            raise RuntimeError(error_msg)
        try:
            release_data = response.json()
        except ValueError as je:
            raise RuntimeError(f"Failed to parse release JSON: {je}\nRaw (truncated 400): {response.text[:400]}")
    except Exception as e:
        console.print(f"[red]Error fetching release information[/red]")
        console.print(Panel(str(e), title="Fetch Error", border_style="red"))
        raise typer.Exit(1)

    assets = release_data.get("assets", [])
    pattern = f"specforge-template-{ai_assistant}-{script_type}"
    matching_assets = [
        asset for asset in assets
        if pattern in asset["name"] and asset["name"].endswith(".zip")
    ]

    asset = matching_assets[0] if matching_assets else None

    if asset is None:
        console.print(f"[red]No matching release asset found[/red] for [bold]{ai_assistant}[/bold] (expected pattern: [bold]{pattern}[/bold])")
        asset_names = [a.get('name', '?') for a in assets]
        console.print(Panel("\n".join(asset_names) or "(no assets)", title="Available Assets", border_style="yellow"))
        raise typer.Exit(1)

    download_url = asset["browser_download_url"]
    filename = asset["name"]
    file_size = asset["size"]

    if verbose:
        console.print(f"[cyan]Found template:[/cyan] {filename}")
        console.print(f"[cyan]Size:[/cyan] {file_size:,} bytes")
        console.print(f"[cyan]Release:[/cyan] {release_data['tag_name']}")

    zip_path = download_dir / filename
    if verbose:
        console.print(f"[cyan]Downloading template...[/cyan]")

    try:
        with client.stream(
            "GET",
            download_url,
            timeout=60,
            follow_redirects=True,
            headers=_github_auth_headers(github_token),
        ) as response:
            if response.status_code != 200:
                # Handle rate-limiting on download as well
                error_msg = _format_rate_limit_error(response.status_code, response.headers, download_url)
                if debug:
                    error_msg += f"\n\n[dim]Response body (truncated 400):[/dim]\n{response.text[:400]}"
                raise RuntimeError(error_msg)
            total_size = int(response.headers.get('content-length', 0))
            with open(zip_path, 'wb') as f:
                if total_size == 0:
                    for chunk in response.iter_bytes(chunk_size=8192):
                        f.write(chunk)
                else:
                    if show_progress:
                        with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                            console=console,
                        ) as progress:
                            task = progress.add_task("Downloading...", total=total_size)
                            downloaded = 0
                            for chunk in response.iter_bytes(chunk_size=8192):
                                f.write(chunk)
                                downloaded += len(chunk)
                                progress.update(task, completed=downloaded)
                    else:
                        for chunk in response.iter_bytes(chunk_size=8192):
                            f.write(chunk)
    except Exception as e:
        console.print(f"[red]Error downloading template[/red]")
        detail = str(e)
        if zip_path.exists():
            zip_path.unlink()
        console.print(Panel(detail, title="Download Error", border_style="red"))
        raise typer.Exit(1)
    if verbose:
        console.print(f"Downloaded: {filename}")
    metadata = {
        "filename": filename,
        "size": file_size,
        "release": release_data["tag_name"],
        "asset_url": download_url
    }
    return zip_path, metadata

def download_and_extract_template(project_path: Path, ai_assistant: str, script_type: str, is_current_dir: bool = False, *, verbose: bool = True, tracker: StepTracker | None = None, client: httpx.Client = None, debug: bool = False, github_token: str = None, force_download: bool = False) -> Path:
    """Download the latest release and extract it to create a new project.
    Returns project_path. Uses tracker if provided (with keys: fetch, download, extract, cleanup)

    If bundled templates are available (installed with the package), they are used first.
    Falls back to GitHub download if bundled templates are not available or force_download is True.
    """
    current_dir = Path.cwd()

    # Try bundled templates first (unless force_download is set)
    bundled_path = get_bundled_path()
    if bundled_path and not force_download:
        if tracker:
            tracker.add("bundled", "Build from bundled templates")
            tracker.start("bundled", "checking bundled templates")

        # Create project directory if needed
        if not is_current_dir:
            project_path.mkdir(parents=True, exist_ok=True)

        # Try to build from bundled templates
        if build_template_from_bundled(
            ai_assistant,
            script_type,
            project_path,
            bundled_path,
            verbose=verbose and tracker is None,
            tracker=tracker
        ):
            if tracker:
                # Skip GitHub-related steps since we used bundled templates
                tracker.skip("fetch", "using bundled templates")
                tracker.skip("download", "using bundled templates")
                tracker.skip("extract", "using bundled templates")
                tracker.skip("zip-list", "using bundled templates")
                tracker.skip("extracted-summary", "using bundled templates")
                tracker.skip("cleanup", "no download needed")
            elif verbose:
                console.print("[green]✓[/green] Templates built from bundled package")
            return project_path

        # Bundled build failed, fall back to GitHub
        if tracker:
            tracker.error("bundled", "failed, falling back to GitHub")
        elif verbose:
            console.print("[yellow]Bundled templates failed, falling back to GitHub download...[/yellow]")

        # Clean up if we created the directory
        if not is_current_dir and project_path.exists():
            shutil.rmtree(project_path)

    # Fall back to GitHub download
    if tracker:
        tracker.start("fetch", "contacting GitHub API")
    try:
        zip_path, meta = download_template_from_github(
            ai_assistant,
            current_dir,
            script_type=script_type,
            verbose=verbose and tracker is None,
            show_progress=(tracker is None),
            client=client,
            debug=debug,
            github_token=github_token
        )
        if tracker:
            tracker.complete("fetch", f"release {meta['release']} ({meta['size']:,} bytes)")
            tracker.add("download", "Download template")
            tracker.complete("download", meta['filename'])
    except Exception as e:
        if tracker:
            tracker.error("fetch", str(e))
        else:
            if verbose:
                console.print(f"[red]Error downloading template:[/red] {e}")
        raise

    if tracker:
        tracker.add("extract", "Extract template")
        tracker.start("extract")
    elif verbose:
        console.print("Extracting template...")

    try:
        if not is_current_dir:
            project_path.mkdir(parents=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_contents = zip_ref.namelist()
            if tracker:
                tracker.start("zip-list")
                tracker.complete("zip-list", f"{len(zip_contents)} entries")
            elif verbose:
                console.print(f"[cyan]ZIP contains {len(zip_contents)} items[/cyan]")

            if is_current_dir:
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    zip_ref.extractall(temp_path)

                    extracted_items = list(temp_path.iterdir())
                    if tracker:
                        tracker.start("extracted-summary")
                        tracker.complete("extracted-summary", f"temp {len(extracted_items)} items")
                    elif verbose:
                        console.print(f"[cyan]Extracted {len(extracted_items)} items to temp location[/cyan]")

                    source_dir = temp_path
                    if len(extracted_items) == 1 and extracted_items[0].is_dir():
                        source_dir = extracted_items[0]
                        if tracker:
                            tracker.add("flatten", "Flatten nested directory")
                            tracker.complete("flatten")
                        elif verbose:
                            console.print(f"[cyan]Found nested directory structure[/cyan]")

                    for item in source_dir.iterdir():
                        dest_path = project_path / item.name
                        if item.is_dir():
                            if dest_path.exists():
                                if verbose and not tracker:
                                    console.print(f"[yellow]Merging directory:[/yellow] {item.name}")
                                for sub_item in item.rglob('*'):
                                    if sub_item.is_file():
                                        rel_path = sub_item.relative_to(item)
                                        dest_file = dest_path / rel_path
                                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                                        # Special handling for .vscode/settings.json - merge instead of overwrite
                                        if dest_file.name == "settings.json" and dest_file.parent.name == ".vscode":
                                            handle_vscode_settings(sub_item, dest_file, rel_path, verbose, tracker)
                                        else:
                                            shutil.copy2(sub_item, dest_file)
                            else:
                                shutil.copytree(item, dest_path)
                        else:
                            if dest_path.exists() and verbose and not tracker:
                                console.print(f"[yellow]Overwriting file:[/yellow] {item.name}")
                            shutil.copy2(item, dest_path)
                    if verbose and not tracker:
                        console.print(f"[cyan]Template files merged into current directory[/cyan]")
            else:
                zip_ref.extractall(project_path)

                extracted_items = list(project_path.iterdir())
                if tracker:
                    tracker.start("extracted-summary")
                    tracker.complete("extracted-summary", f"{len(extracted_items)} top-level items")
                elif verbose:
                    console.print(f"[cyan]Extracted {len(extracted_items)} items to {project_path}:[/cyan]")
                    for item in extracted_items:
                        console.print(f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")

                if len(extracted_items) == 1 and extracted_items[0].is_dir():
                    nested_dir = extracted_items[0]
                    temp_move_dir = project_path.parent / f"{project_path.name}_temp"

                    shutil.move(str(nested_dir), str(temp_move_dir))

                    project_path.rmdir()

                    shutil.move(str(temp_move_dir), str(project_path))
                    if tracker:
                        tracker.add("flatten", "Flatten nested directory")
                        tracker.complete("flatten")
                    elif verbose:
                        console.print(f"[cyan]Flattened nested directory structure[/cyan]")

    except Exception as e:
        if tracker:
            tracker.error("extract", str(e))
        else:
            if verbose:
                console.print(f"[red]Error extracting template:[/red] {e}")
                if debug:
                    console.print(Panel(str(e), title="Extraction Error", border_style="red"))

        if not is_current_dir and project_path.exists():
            shutil.rmtree(project_path)
        raise typer.Exit(1)
    else:
        if tracker:
            tracker.complete("extract")
    finally:
        if tracker:
            tracker.add("cleanup", "Remove temporary archive")

        if zip_path.exists():
            zip_path.unlink()
            if tracker:
                tracker.complete("cleanup")
            elif verbose:
                console.print(f"Cleaned up: {zip_path.name}")

    return project_path


def ensure_executable_scripts(project_path: Path, tracker: StepTracker | None = None) -> None:
    """Ensure POSIX .sh scripts under .specforge/scripts (recursively) have execute bits (no-op on Windows)."""
    if os.name == "nt":
        return  # Windows: skip silently
    scripts_root = project_path / ".specforge" / "scripts"
    if not scripts_root.is_dir():
        return
    failures: list[str] = []
    updated = 0
    for script in scripts_root.rglob("*.sh"):
        try:
            if script.is_symlink() or not script.is_file():
                continue
            try:
                with script.open("rb") as f:
                    if f.read(2) != b"#!":
                        continue
            except Exception:
                continue
            st = script.stat(); mode = st.st_mode
            if mode & 0o111:
                continue
            new_mode = mode
            if mode & 0o400: new_mode |= 0o100
            if mode & 0o040: new_mode |= 0o010
            if mode & 0o004: new_mode |= 0o001
            if not (new_mode & 0o100):
                new_mode |= 0o100
            os.chmod(script, new_mode)
            updated += 1
        except Exception as e:
            failures.append(f"{script.relative_to(scripts_root)}: {e}")
    if tracker:
        detail = f"{updated} updated" + (f", {len(failures)} failed" if failures else "")
        tracker.add("chmod", "Set script permissions recursively")
        (tracker.error if failures else tracker.complete)("chmod", detail)
    else:
        if updated:
            console.print(f"[cyan]Updated execute permissions on {updated} script(s) recursively[/cyan]")
        if failures:
            console.print("[yellow]Some scripts could not be updated:[/yellow]")
            for f in failures:
                console.print(f"  - {f}")

def detect_installed_agents(project_path: Path) -> list[str]:
    """Detect which agents have been installed in this project.

    Scans for specforge command files in each agent's known command directory.

    Returns:
        List of agent keys (e.g., ['claude', 'gemini', 'cursor-agent'])
    """
    detected = []
    for agent_key, (cmd_dir, _, _) in AGENT_COMMAND_DIRS.items():
        cmd_path = project_path / cmd_dir
        if cmd_path.exists() and list(cmd_path.glob("specforge.*")):
            detected.append(agent_key)
    return detected


def detect_script_type(project_path: Path) -> str:
    """Detect the script type used in this project.

    Checks .specforge/scripts/ for bash/ or powershell/ directories.

    Returns:
        'sh' or 'ps', defaulting to platform default if indeterminate.
    """
    scripts_dir = project_path / ".specforge" / "scripts"
    if (scripts_dir / "bash").exists():
        return "sh"
    if (scripts_dir / "powershell").exists():
        return "ps"
    return "ps" if os.name == "nt" else "sh"


def _extract_markdown_body(content: str) -> str:
    """Extract the markdown body, stripping any YAML frontmatter.

    Handles plain markdown and MDC format with --- fenced frontmatter.
    """
    if content.startswith("---"):
        end_idx = content.find("---", 3)
        if end_idx != -1:
            return content[end_idx + 3:].lstrip("\n")
    return content


def _format_context_for_agent(agent_key: str, body: str) -> str:
    """Wrap markdown body in agent-specific format if needed.

    For Cursor (.mdc), adds YAML frontmatter. For all others, returns body as-is.
    """
    if agent_key == "cursor-agent":
        return f"---\ndescription: SpecForge project context\nglobs: \n---\n\n{body}"
    return body


def sync_context_files(installed_agents: list[str], project_path: Path, tracker: "StepTracker" = None) -> None:
    """Sync context files across all installed agents using last-modified-wins.

    Finds the most recently modified context file among all installed agents
    and copies its content to all other agents' context files.
    Deduplicates shared physical files (e.g., AGENTS.md used by multiple agents).
    """
    # Collect existing context files with mtime, deduplicated by resolved path
    context_files: dict[str, tuple[Path, float]] = {}  # agent_key -> (path, mtime)
    seen_paths: dict[str, str] = {}  # resolved_path_str -> first agent_key that uses it

    for agent_key in installed_agents:
        rel_path = AGENT_CONTEXT_PATHS.get(agent_key)
        if not rel_path:
            continue
        full_path = project_path / rel_path
        if not full_path.exists():
            continue

        resolved = str(full_path.resolve())
        if resolved in seen_paths:
            # Same physical file used by another agent - skip duplicate
            continue
        seen_paths[resolved] = agent_key
        context_files[agent_key] = (full_path, full_path.stat().st_mtime)

    if not context_files:
        if tracker:
            tracker.complete("context-sync", "no context files found, nothing to sync")
        return

    # Find the most recently modified context file
    newest_agent = max(context_files, key=lambda k: context_files[k][1])
    newest_path, _ = context_files[newest_agent]
    newest_content = newest_path.read_text(encoding="utf-8")

    # Extract the markdown body (strip any format-specific wrapper)
    body_content = _extract_markdown_body(newest_content)

    synced_count = 0
    created_count = 0
    synced_targets: set[str] = set()  # deduplicate by resolved path
    # Write to all other context files, creating missing ones
    for agent_key in installed_agents:
        rel_path = AGENT_CONTEXT_PATHS.get(agent_key)
        if not rel_path:
            continue
        target_path = project_path / rel_path
        resolved_target = str(target_path.resolve())

        # Skip the source file
        if resolved_target == str(newest_path.resolve()):
            continue

        # Deduplicate shared physical files (e.g., AGENTS.md used by multiple agents)
        if resolved_target in synced_targets:
            continue
        synced_targets.add(resolved_target)

        is_new = not target_path.exists()
        formatted = _format_context_for_agent(agent_key, body_content)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(formatted, encoding="utf-8")
        if is_new:
            created_count += 1
        synced_count += 1

    if tracker:
        msg = f"synced from {newest_agent} to {synced_count} file(s)"
        if created_count:
            msg += f" ({created_count} created)"
        tracker.complete("context-sync", msg)


def sync_agent_working_files(installed_agents: list[str], project_path: Path, tracker: "StepTracker" = None) -> None:
    """Sync skills/ and agents/specforge/ directories across agent dirs.

    For each file individually, the most recently modified version wins
    and is copied to all other agent directories.
    Files that exist only in one agent dir are copied to all others.
    """
    sync_subdirs = ["skills", os.path.join("agents", "specforge")]
    total_synced = 0

    for subdir in sync_subdirs:
        # Collect all files across all agent dirs for this subdir
        # file_rel_path -> list of (agent_key, full_path, mtime)
        all_files: dict[str, list[tuple[str, Path, float]]] = {}

        for agent_key in installed_agents:
            agent_folder = AGENT_CONFIG[agent_key]["folder"].rstrip("/")
            working_dir = project_path / agent_folder / subdir

            if not working_dir.exists():
                continue

            for file_path in working_dir.rglob("*"):
                if not file_path.is_file():
                    continue
                rel = file_path.relative_to(working_dir)
                rel_str = str(rel)
                if rel_str not in all_files:
                    all_files[rel_str] = []
                all_files[rel_str].append((agent_key, file_path, file_path.stat().st_mtime))

        # For each file, find the newest version and copy to all agent dirs that don't have it or have older
        for rel_str, sources in all_files.items():
            # Find the newest version
            newest = max(sources, key=lambda x: x[2])
            newest_agent, newest_path, newest_mtime = newest
            newest_content = newest_path.read_bytes()

            # Copy to all other agent dirs
            for agent_key in installed_agents:
                if agent_key == newest_agent:
                    continue
                agent_folder = AGENT_CONFIG[agent_key]["folder"].rstrip("/")
                target_path = project_path / agent_folder / subdir / rel_str

                # Skip if target already has the same or newer content
                if target_path.exists() and target_path.stat().st_mtime >= newest_mtime:
                    continue

                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_bytes(newest_content)
                # Preserve mtime from source
                shutil.copystat(newest_path, target_path)
                total_synced += 1

    if tracker:
        tracker.complete("working-sync", f"{total_synced} file(s) synced")


def update_shared_resources(
    project_path: Path,
    script_type: str,
    bundled_path: Optional[Path],
    *,
    force_download: bool = False,
    tracker: "StepTracker" = None,
    github_token: str = None,
    skip_tls: bool = False,
    debug: bool = False,
) -> bool:
    """Update .specforge/scripts/ and .specforge/templates/ from latest templates.

    CRITICAL: .specforge/memory/ is NEVER touched.

    Returns:
        True if update succeeded, False otherwise.
    """
    specify_dir = project_path / ".specforge"

    if bundled_path and not force_download:
        templates_dir = bundled_path / "templates"
        scripts_dir = bundled_path / "scripts"

        # Update scripts
        if scripts_dir.exists():
            scripts_dest = specify_dir / "scripts"
            # Remove old scripts and replace with new
            if scripts_dest.exists():
                shutil.rmtree(scripts_dest)
            scripts_dest.mkdir(parents=True, exist_ok=True)

            if script_type == "sh":
                bash_dir = scripts_dir / "bash"
                if bash_dir.exists():
                    shutil.copytree(bash_dir, scripts_dest / "bash", dirs_exist_ok=True)
            elif script_type == "ps":
                ps_dir = scripts_dir / "powershell"
                if ps_dir.exists():
                    shutil.copytree(ps_dir, scripts_dest / "powershell", dirs_exist_ok=True)

            # Copy any root-level script files
            for f in scripts_dir.iterdir():
                if f.is_file():
                    shutil.copy2(f, scripts_dest / f.name)

        # Update templates (except commands/ and vscode-settings.json)
        if templates_dir.exists():
            templates_dest = specify_dir / "templates"
            templates_dest.mkdir(parents=True, exist_ok=True)
            for item in templates_dir.iterdir():
                if item.name in ("commands", "vscode-settings.json"):
                    continue
                dest = templates_dest / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                elif item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)

        return True

    # Fall back to GitHub download for shared resources
    current_dir = Path.cwd()
    verify = not skip_tls
    local_ssl_context = ssl_context if verify else False
    local_client = httpx.Client(verify=local_ssl_context)

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Download any agent variant (shared resources are the same)
            zip_path, meta = download_template_from_github(
                "claude", temp_path,
                script_type=script_type,
                verbose=False,
                show_progress=False,
                client=local_client,
                debug=debug,
                github_token=github_token
            )

            # Extract to temp
            extract_path = temp_path / "extracted"
            extract_path.mkdir()
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # Find the .specforge dir in extracted content
            extracted_items = list(extract_path.iterdir())
            source_dir = extract_path
            if len(extracted_items) == 1 and extracted_items[0].is_dir():
                source_dir = extracted_items[0]

            specforge_source = source_dir / ".specforge"
            if not specforge_source.exists():
                return False

            # Update scripts
            scripts_source = specforge_source / "scripts"
            if scripts_source.exists():
                scripts_dest = specify_dir / "scripts"
                if scripts_dest.exists():
                    shutil.rmtree(scripts_dest)
                shutil.copytree(scripts_source, scripts_dest, dirs_exist_ok=True)

            # Update templates (NOT memory)
            templates_source = specforge_source / "templates"
            if templates_source.exists():
                templates_dest = specify_dir / "templates"
                templates_dest.mkdir(parents=True, exist_ok=True)
                for item in templates_source.iterdir():
                    dest = templates_dest / item.name
                    if item.is_file():
                        shutil.copy2(item, dest)
                    elif item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)

        return True

    except Exception as e:
        if tracker:
            tracker.error("shared", str(e))
        return False


@app.command()
def init(
    project_name: str = typer.Argument(None, help="Name for your new project directory (optional if using --here, or use '.' for current directory)"),
    ai_assistant: str = typer.Option(None, "--ai", help="AI assistant to use: claude, gemini, copilot, cursor-agent, qwen, opencode, codex, windsurf, kilocode, auggie, codebuddy, amp, shai, q, bob, or qoder "),
    script_type: str = typer.Option(None, "--script", help="Script type to use: sh or ps"),
    ignore_agent_tools: bool = typer.Option(False, "--ignore-agent-tools", help="Skip checks for AI agent tools like Claude Code"),
    no_git: bool = typer.Option(False, "--no-git", help="Skip git repository initialization"),
    here: bool = typer.Option(False, "--here", help="Initialize project in the current directory instead of creating a new one"),
    force: bool = typer.Option(False, "--force", help="Force merge/overwrite when using --here (skip confirmation)"),
    force_download: bool = typer.Option(False, "--force-download", help="Force downloading templates from GitHub even if bundled templates are available"),
    skip_tls: bool = typer.Option(False, "--skip-tls", help="Skip SSL/TLS verification (not recommended)"),
    debug: bool = typer.Option(False, "--debug", help="Show verbose diagnostic output for network and extraction failures"),
    github_token: str = typer.Option(None, "--github-token", help="GitHub token to use for API requests (or set GH_TOKEN or GITHUB_TOKEN environment variable)"),
):
    """
    Initialize a new Specify project from the latest template.

    This command will:
    1. Check that required tools are installed (git is optional)
    2. Let you choose your AI assistant
    3. Use bundled templates if available, or download from GitHub
    4. Extract the template to a new project directory or current directory
    5. Initialize a fresh git repository (if not --no-git and no existing repo)
    6. Optionally set up AI assistant commands

    Examples:
        specify init my-project
        specify init my-project --ai claude
        specify init my-project --ai copilot --no-git
        specify init --ignore-agent-tools my-project
        specify init . --ai claude         # Initialize in current directory
        specify init .                     # Initialize in current directory (interactive AI selection)
        specify init --here --ai claude    # Alternative syntax for current directory
        specify init --here --ai codex
        specify init --here --ai codebuddy
        specify init --here
        specify init --here --force  # Skip confirmation when current directory not empty
        specify init --here --force-download  # Force GitHub download instead of bundled templates
    """

    show_banner()

    if project_name == ".":
        here = True
        project_name = None  # Clear project_name to use existing validation logic

    if here and project_name:
        console.print("[red]Error:[/red] Cannot specify both project name and --here flag")
        raise typer.Exit(1)

    if not here and not project_name:
        console.print("[red]Error:[/red] Must specify either a project name, use '.' for current directory, or use --here flag")
        raise typer.Exit(1)

    if here:
        project_name = Path.cwd().name
        project_path = Path.cwd()

        existing_items = list(project_path.iterdir())
        if existing_items:
            console.print(f"[yellow]Warning:[/yellow] Current directory is not empty ({len(existing_items)} items)")
            console.print("[yellow]Template files will be merged with existing content and may overwrite existing files[/yellow]")
            if force:
                console.print("[cyan]--force supplied: skipping confirmation and proceeding with merge[/cyan]")
            else:
                response = typer.confirm("Do you want to continue?")
                if not response:
                    console.print("[yellow]Operation cancelled[/yellow]")
                    raise typer.Exit(0)
    else:
        project_path = Path(project_name).resolve()
        if project_path.exists():
            error_panel = Panel(
                f"Directory '[cyan]{project_name}[/cyan]' already exists\n"
                "Please choose a different project name or remove the existing directory.",
                title="[red]Directory Conflict[/red]",
                border_style="red",
                padding=(1, 2)
            )
            console.print()
            console.print(error_panel)
            raise typer.Exit(1)

    current_dir = Path.cwd()

    setup_lines = [
        "[cyan]Specify Project Setup[/cyan]",
        "",
        f"{'Project':<15} [green]{project_path.name}[/green]",
        f"{'Working Path':<15} [dim]{current_dir}[/dim]",
    ]

    if not here:
        setup_lines.append(f"{'Target Path':<15} [dim]{project_path}[/dim]")

    console.print(Panel("\n".join(setup_lines), border_style="cyan", padding=(1, 2)))

    should_init_git = False
    if not no_git:
        should_init_git = check_tool("git")
        if not should_init_git:
            console.print("[yellow]Git not found - will skip repository initialization[/yellow]")

    if ai_assistant:
        if ai_assistant not in AGENT_CONFIG:
            console.print(f"[red]Error:[/red] Invalid AI assistant '{ai_assistant}'. Choose from: {', '.join(AGENT_CONFIG.keys())}")
            raise typer.Exit(1)
        selected_ai = ai_assistant
    else:
        # Create options dict for selection (agent_key: display_name)
        ai_choices = {key: config["name"] for key, config in AGENT_CONFIG.items()}
        selected_ai = select_with_arrows(
            ai_choices, 
            "Choose your AI assistant:", 
            "copilot"
        )

    if not ignore_agent_tools:
        agent_config = AGENT_CONFIG.get(selected_ai)
        if agent_config and agent_config["requires_cli"]:
            install_url = agent_config["install_url"]
            if not check_tool(selected_ai):
                error_panel = Panel(
                    f"[cyan]{selected_ai}[/cyan] not found\n"
                    f"Install from: [cyan]{install_url}[/cyan]\n"
                    f"{agent_config['name']} is required to continue with this project type.\n\n"
                    "Tip: Use [cyan]--ignore-agent-tools[/cyan] to skip this check",
                    title="[red]Agent Detection Error[/red]",
                    border_style="red",
                    padding=(1, 2)
                )
                console.print()
                console.print(error_panel)
                raise typer.Exit(1)

    if script_type:
        if script_type not in SCRIPT_TYPE_CHOICES:
            console.print(f"[red]Error:[/red] Invalid script type '{script_type}'. Choose from: {', '.join(SCRIPT_TYPE_CHOICES.keys())}")
            raise typer.Exit(1)
        selected_script = script_type
    else:
        default_script = "ps" if os.name == "nt" else "sh"

        if sys.stdin.isatty():
            selected_script = select_with_arrows(SCRIPT_TYPE_CHOICES, "Choose script type (or press Enter)", default_script)
        else:
            selected_script = default_script

    console.print(f"[cyan]Selected AI assistant:[/cyan] {selected_ai}")
    console.print(f"[cyan]Selected script type:[/cyan] {selected_script}")

    tracker = StepTracker("Initialize Specify Project")

    sys._specify_tracker_active = True

    tracker.add("precheck", "Check required tools")
    tracker.complete("precheck", "ok")
    tracker.add("ai-select", "Select AI assistant")
    tracker.complete("ai-select", f"{selected_ai}")
    tracker.add("script-select", "Select script type")
    tracker.complete("script-select", selected_script)
    for key, label in [
        ("bundled", "Build from bundled templates"),
        ("fetch", "Fetch latest release"),
        ("download", "Download template"),
        ("extract", "Extract template"),
        ("zip-list", "Archive contents"),
        ("extracted-summary", "Extraction summary"),
        ("chmod", "Ensure scripts executable"),
        ("cleanup", "Cleanup"),
        ("git", "Initialize git repository"),
        ("final", "Finalize")
    ]:
        tracker.add(key, label)

    # Track git error message outside Live context so it persists
    git_error_message = None

    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))
        try:
            verify = not skip_tls
            local_ssl_context = ssl_context if verify else False
            local_client = httpx.Client(verify=local_ssl_context)

            download_and_extract_template(project_path, selected_ai, selected_script, here, verbose=False, tracker=tracker, client=local_client, debug=debug, github_token=github_token, force_download=force_download)

            ensure_executable_scripts(project_path, tracker=tracker)

            if not no_git:
                tracker.start("git")
                if is_git_repo(project_path):
                    tracker.complete("git", "existing repo detected")
                elif should_init_git:
                    success, error_msg = init_git_repo(project_path, quiet=True)
                    if success:
                        tracker.complete("git", "initialized")
                    else:
                        tracker.error("git", "init failed")
                        git_error_message = error_msg
                else:
                    tracker.skip("git", "git not available")
            else:
                tracker.skip("git", "--no-git flag")

            tracker.complete("final", "project ready")
        except Exception as e:
            tracker.error("final", str(e))
            console.print(Panel(f"Initialization failed: {e}", title="Failure", border_style="red"))
            if debug:
                _env_pairs = [
                    ("Python", sys.version.split()[0]),
                    ("Platform", sys.platform),
                    ("CWD", str(Path.cwd())),
                ]
                _label_width = max(len(k) for k, _ in _env_pairs)
                env_lines = [f"{k.ljust(_label_width)} → [bright_black]{v}[/bright_black]" for k, v in _env_pairs]
                console.print(Panel("\n".join(env_lines), title="Debug Environment", border_style="magenta"))
            if not here and project_path.exists():
                shutil.rmtree(project_path)
            raise typer.Exit(1)
        finally:
            pass

    console.print(tracker.render())
    console.print("\n[bold green]Project ready.[/bold green]")
    
    # Show git error details if initialization failed
    if git_error_message:
        console.print()
        git_error_panel = Panel(
            f"[yellow]Warning:[/yellow] Git repository initialization failed\n\n"
            f"{git_error_message}\n\n"
            f"[dim]You can initialize git manually later with:[/dim]\n"
            f"[cyan]cd {project_path if not here else '.'}[/cyan]\n"
            f"[cyan]git init[/cyan]\n"
            f"[cyan]git add .[/cyan]\n"
            f"[cyan]git commit -m \"Initial commit\"[/cyan]",
            title="[red]Git Initialization Failed[/red]",
            border_style="red",
            padding=(1, 2)
        )
        console.print(git_error_panel)

    # Agent folder security notice
    agent_config = AGENT_CONFIG.get(selected_ai)
    if agent_config:
        agent_folder = agent_config["folder"]
        security_notice = Panel(
            f"Some agents may store credentials, auth tokens, or other identifying and private artifacts in the agent folder within your project.\n"
            f"Consider adding [cyan]{agent_folder}[/cyan] (or parts of it) to [cyan].gitignore[/cyan] to prevent accidental credential leakage.",
            title="[yellow]Agent Folder Security[/yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        console.print()
        console.print(security_notice)

    steps_lines = []
    if not here:
        steps_lines.append(f"1. Go to the project folder: [cyan]cd {project_name}[/cyan]")
        step_num = 2
    else:
        steps_lines.append("1. You're already in the project directory!")
        step_num = 2

    # Add Codex-specific setup step if needed
    if selected_ai == "codex":
        codex_path = project_path / ".codex"
        quoted_path = shlex.quote(str(codex_path))
        if os.name == "nt":  # Windows
            cmd = f"setx CODEX_HOME {quoted_path}"
        else:  # Unix-like systems
            cmd = f"export CODEX_HOME={quoted_path}"
        
        steps_lines.append(f"{step_num}. Set [cyan]CODEX_HOME[/cyan] environment variable before running Codex: [cyan]{cmd}[/cyan]")
        step_num += 1

    steps_lines.append(f"{step_num}. Start using slash commands with your AI agent:")

    steps_lines.append("   2.1 [cyan]/specforge.constitution[/] - Establish project principles")
    steps_lines.append("   2.2 [cyan]/specforge.specify[/] - Create baseline specification")
    steps_lines.append("   2.3 [cyan]/specforge.plan[/] - Create implementation plan")
    steps_lines.append("   2.4 [cyan]/specforge.tasks[/] - Generate actionable tasks")
    steps_lines.append("   2.5 [cyan]/specforge.implement[/] - Execute implementation")

    steps_panel = Panel("\n".join(steps_lines), title="Next Steps", border_style="cyan", padding=(1,2))
    console.print()
    console.print(steps_panel)

    enhancement_lines = [
        "Optional commands that you can use for your specs [bright_black](improve quality & confidence)[/bright_black]",
        "",
        f"○ [cyan]/specforge.clarify[/] [bright_black](optional)[/bright_black] - Ask structured questions to de-risk ambiguous areas before planning (run before [cyan]/specforge.plan[/] if used)",
        f"○ [cyan]/specforge.analyze[/] [bright_black](optional)[/bright_black] - Cross-artifact consistency & alignment report (after [cyan]/specforge.tasks[/], before [cyan]/specforge.implement[/])",
        f"○ [cyan]/specforge.checklist[/] [bright_black](optional)[/bright_black] - Generate quality checklists to validate requirements completeness, clarity, and consistency (after [cyan]/specforge.plan[/])"
    ]
    enhancements_panel = Panel("\n".join(enhancement_lines), title="Enhancement Commands", border_style="cyan", padding=(1,2))
    console.print()
    console.print(enhancements_panel)

@app.command()
def check():
    """Check that all required tools are installed."""
    show_banner()
    console.print("[bold]Checking for installed tools...[/bold]\n")

    tracker = StepTracker("Check Available Tools")

    tracker.add("git", "Git version control")
    git_ok = check_tool("git", tracker=tracker)

    agent_results = {}
    for agent_key, agent_config in AGENT_CONFIG.items():
        agent_name = agent_config["name"]
        requires_cli = agent_config["requires_cli"]

        tracker.add(agent_key, agent_name)

        if requires_cli:
            agent_results[agent_key] = check_tool(agent_key, tracker=tracker)
        else:
            # IDE-based agent - skip CLI check and mark as optional
            tracker.skip(agent_key, "IDE-based, no CLI check")
            agent_results[agent_key] = False  # Don't count IDE agents as "found"

    # Check VS Code variants (not in agent config)
    tracker.add("code", "Visual Studio Code")
    code_ok = check_tool("code", tracker=tracker)

    tracker.add("code-insiders", "Visual Studio Code Insiders")
    code_insiders_ok = check_tool("code-insiders", tracker=tracker)

    console.print(tracker.render())

    console.print("\n[bold green]Forge CLI is ready to use![/bold green]")

    if not git_ok:
        console.print("[dim]Tip: Install git for repository management[/dim]")

    if not any(agent_results.values()):
        console.print("[dim]Tip: Install an AI assistant for the best experience[/dim]")

@app.command()
def migrate(
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be changed without making changes"),
):
    """
    Migrate a project from speckit/specify to specforge.

    This command handles the full migration:
    1. Rename .specify/ directory to .specforge/
    2. Rename command files from speckit.* to specforge.* in all agent dirs
    3. Replace /speckit. references with /specforge. inside command files
    4. Rename agents/speckit/ subdirectories to agents/specforge/
    5. Update .vscode/settings.json references
    6. Preserve all memory files and project-specific content

    Examples:
        forge migrate              # Run migration
        forge migrate --dry-run    # Preview changes without applying
    """
    show_banner()

    project_path = Path.cwd()

    # Detect what needs migration
    old_specify_dir = project_path / ".specify"
    new_specforge_dir = project_path / ".specforge"

    has_old_dir = old_specify_dir.exists()
    has_new_dir = new_specforge_dir.exists()

    # Scan for old command files (speckit.*) in agent dirs
    old_command_files: list[tuple[Path, Path]] = []  # (old_path, new_path)
    old_content_files: list[Path] = []  # files containing /speckit. references
    old_agent_dirs: list[tuple[Path, Path]] = []  # agents/speckit/ -> agents/specforge/

    for agent_key, (cmd_dir, _, _) in AGENT_COMMAND_DIRS.items():
        cmd_path = project_path / cmd_dir
        if not cmd_path.exists():
            continue

        # Find speckit.* command files to rename
        for f in cmd_path.glob("speckit.*"):
            if f.is_file():
                new_name = f.name.replace("speckit.", "specforge.", 1)
                old_command_files.append((f, f.parent / new_name))

        # Find specforge.* files with old /speckit. content references
        for f in cmd_path.glob("specforge.*"):
            if f.is_file():
                try:
                    content = f.read_text(encoding="utf-8")
                    if "/speckit." in content or "speckit." in content:
                        old_content_files.append(f)
                except Exception:
                    pass

        # Also check speckit.* files for content (they'll be renamed then updated)
        for f in cmd_path.glob("speckit.*"):
            if f.is_file():
                try:
                    content = f.read_text(encoding="utf-8")
                    if "/speckit." in content or "speckit." in content:
                        # Will be handled after rename
                        pass
                except Exception:
                    pass

        # Check for agents/speckit/ subdirectory
        agent_folder = AGENT_CONFIG[agent_key]["folder"].rstrip("/")
        old_agents_subdir = project_path / agent_folder / "agents" / "speckit"
        new_agents_subdir = project_path / agent_folder / "agents" / "specforge"
        if old_agents_subdir.exists() and old_agents_subdir.is_dir():
            old_agent_dirs.append((old_agents_subdir, new_agents_subdir))

    # Check .vscode/settings.json for old references
    vscode_settings_path = project_path / ".vscode" / "settings.json"
    has_old_vscode = False
    if vscode_settings_path.exists():
        try:
            content = vscode_settings_path.read_text(encoding="utf-8")
            if "speckit." in content or ".specify/" in content:
                has_old_vscode = True
        except Exception:
            pass

    # Check if anything needs migration
    needs_migration = has_old_dir or old_command_files or old_content_files or old_agent_dirs or has_old_vscode

    if not needs_migration:
        console.print("[green]No migration needed.[/green] This project already uses the specforge naming.")
        if has_new_dir:
            console.print("[dim]Tip: Run 'forge update' to update templates and sync agents.[/dim]")
        raise typer.Exit(0)

    # Display what will be done
    tracker = StepTracker("Migrate to SpecForge")

    if has_old_dir:
        tracker.add("dir-rename", "Rename .specify/ to .specforge/")
    if old_command_files:
        tracker.add("cmd-rename", f"Rename {len(old_command_files)} command file(s)")
    if old_command_files or old_content_files:
        tracker.add("content-replace", "Replace speckit references in file content")
    if old_agent_dirs:
        tracker.add("agents-rename", f"Rename {len(old_agent_dirs)} agents/speckit/ dir(s)")
    if has_old_vscode:
        tracker.add("vscode", "Update .vscode/settings.json")
    tracker.add("final", "Finalize")

    if dry_run:
        console.print("[yellow]Dry run mode - no changes will be made.[/yellow]\n")
        dry_lines = ["[bold]Changes that would be applied:[/bold]", ""]

        if has_old_dir:
            if has_new_dir:
                dry_lines.append("  1. Merge .specify/ into existing .specforge/ (preserve memory)")
            else:
                dry_lines.append("  1. Rename .specify/ -> .specforge/")

        step = 2
        if old_command_files:
            dry_lines.append(f"  {step}. Rename command files:")
            for old_f, new_f in old_command_files[:5]:
                dry_lines.append(f"     {old_f.relative_to(project_path)} -> {new_f.name}")
            if len(old_command_files) > 5:
                dry_lines.append(f"     ... and {len(old_command_files) - 5} more")
            step += 1

        all_content_targets = len(old_command_files) + len(old_content_files)
        if all_content_targets:
            dry_lines.append(f"  {step}. Replace /speckit. -> /specforge. in {all_content_targets} file(s)")
            step += 1

        if old_agent_dirs:
            dry_lines.append(f"  {step}. Rename agents/speckit/ directories:")
            for old_d, new_d in old_agent_dirs:
                dry_lines.append(f"     {old_d.relative_to(project_path)} -> {new_d.relative_to(project_path)}")
            step += 1

        if has_old_vscode:
            dry_lines.append(f"  {step}. Update .vscode/settings.json references")
            step += 1

        dry_lines.append("")
        dry_lines.append("  [bright_black]Tip: Set SPECFORGE_FEATURE instead of SPECIFY_FEATURE in your env[/bright_black]")

        console.print(Panel("\n".join(dry_lines), border_style="yellow", padding=(1, 2)))
        raise typer.Exit(0)

    # Execute migration
    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))

        try:
            # Step 1: Rename .specify/ -> .specforge/
            if has_old_dir:
                tracker.start("dir-rename")
                if has_new_dir:
                    # Both exist: merge old into new, preserving new's memory
                    for item in old_specify_dir.rglob("*"):
                        if not item.is_file():
                            continue
                        rel = item.relative_to(old_specify_dir)
                        dest = new_specforge_dir / rel

                        # Never overwrite memory files from the new dir
                        if str(rel).startswith("memory") and dest.exists():
                            continue

                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest)

                    shutil.rmtree(old_specify_dir)
                    tracker.complete("dir-rename", "merged into existing .specforge/")
                else:
                    old_specify_dir.rename(new_specforge_dir)
                    tracker.complete("dir-rename", "renamed")

            # Step 2: Rename speckit.* -> specforge.* command files
            if old_command_files:
                tracker.start("cmd-rename")
                renamed_count = 0
                for old_f, new_f in old_command_files:
                    if old_f.exists():
                        # If target already exists, remove old one
                        if new_f.exists():
                            old_f.unlink()
                        else:
                            old_f.rename(new_f)
                        renamed_count += 1
                tracker.complete("cmd-rename", f"{renamed_count} file(s) renamed")

            # Step 3: Replace speckit references in file content
            if old_command_files or old_content_files:
                tracker.start("content-replace")
                # Build set of files to update (renamed files + existing files with old content)
                files_to_update: set[Path] = set()

                # After rename, the new files need content update
                for _, new_f in old_command_files:
                    if new_f.exists():
                        files_to_update.add(new_f)

                # Existing specforge.* files with old content
                for f in old_content_files:
                    if f.exists():
                        files_to_update.add(f)

                # Also scan all specforge.* files in all agent dirs for any remaining refs
                for agent_key, (cmd_dir, _, _) in AGENT_COMMAND_DIRS.items():
                    cmd_path = project_path / cmd_dir
                    if cmd_path.exists():
                        for f in cmd_path.glob("specforge.*"):
                            if f.is_file():
                                files_to_update.add(f)

                updated_count = 0
                for f in files_to_update:
                    try:
                        content = f.read_text(encoding="utf-8")
                        new_content = content.replace("/speckit.", "/specforge.")
                        new_content = new_content.replace("speckit.", "specforge.")
                        new_content = new_content.replace(".specify/", ".specforge/")
                        new_content = new_content.replace("SPECIFY_FEATURE", "SPECFORGE_FEATURE")
                        if new_content != content:
                            f.write_text(new_content, encoding="utf-8")
                            updated_count += 1
                    except Exception:
                        pass

                tracker.complete("content-replace", f"{updated_count} file(s) updated")

            # Step 4: Rename agents/speckit/ -> agents/specforge/
            if old_agent_dirs:
                tracker.start("agents-rename")
                for old_d, new_d in old_agent_dirs:
                    if old_d.exists():
                        if new_d.exists():
                            # Merge old into new
                            shutil.copytree(old_d, new_d, dirs_exist_ok=True)
                            shutil.rmtree(old_d)
                        else:
                            old_d.rename(new_d)
                tracker.complete("agents-rename", f"{len(old_agent_dirs)} dir(s) renamed")

            # Step 5: Update .vscode/settings.json
            if has_old_vscode:
                tracker.start("vscode")
                try:
                    content = vscode_settings_path.read_text(encoding="utf-8")
                    new_content = content.replace("speckit.", "specforge.")
                    new_content = new_content.replace(".specify/", ".specforge/")
                    if new_content != content:
                        vscode_settings_path.write_text(new_content, encoding="utf-8")
                    tracker.complete("vscode", "references updated")
                except Exception as e:
                    tracker.error("vscode", str(e))

            tracker.complete("final", "migration complete")

        except Exception as e:
            tracker.error("final", str(e))
            console.print(Panel(f"Migration failed: {e}", title="Failure", border_style="red"))
            raise typer.Exit(1)

    console.print(tracker.render())
    console.print("\n[bold green]Migration complete.[/bold green]")

    # Post-migration tips
    tips_lines = [
        "[bold]Post-migration tips:[/bold]",
        "",
        "  - If you use the SPECIFY_FEATURE environment variable, rename it to SPECFORGE_FEATURE",
        "  - Run [cyan]forge update[/cyan] to regenerate commands from latest templates",
        "  - Review your agent context files (CLAUDE.md, AGENTS.md, etc.) for any remaining old references",
    ]
    console.print(Panel("\n".join(tips_lines), border_style="cyan", padding=(1, 2)))


@app.command()
def update(
    add: Optional[list[str]] = typer.Option(None, "--add", help="Add new agent(s) to the project (e.g., --add gemini --add cursor-agent)"),
    script_type: str = typer.Option(None, "--script", help="Script type override: sh or ps (auto-detected if not set)"),
    force_download: bool = typer.Option(False, "--force-download", help="Force downloading templates from GitHub even if bundled templates are available"),
    skip_tls: bool = typer.Option(False, "--skip-tls", help="Skip SSL/TLS verification (not recommended)"),
    debug: bool = typer.Option(False, "--debug", help="Show verbose diagnostic output"),
    github_token: str = typer.Option(None, "--github-token", help="GitHub token for API requests (or set GH_TOKEN or GITHUB_TOKEN environment variable)"),
    skip_sync: bool = typer.Option(False, "--skip-sync", help="Skip context file and working file synchronization"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be updated without making changes"),
):
    """
    Update all installed agents, sync context files, and refresh shared resources.

    This command will:
    1. Detect all agents installed in the current project
    2. Optionally add new agent(s) with --add
    3. Update shared resources (.specforge/scripts/, .specforge/templates/)
    4. Re-generate command files for all detected agents
    5. Sync context files across agents (last-modified wins)
    6. Sync skills and sub-agents across agent directories (per-file last-modified wins)

    Memory files (.specforge/memory/) are NEVER touched.

    Examples:
        forge update                          # Update all installed agents
        forge update --add gemini             # Add Gemini and update everything
        forge update --add gemini --add roo   # Add multiple agents
        forge update --skip-sync              # Update commands only, skip file sync
        forge update --dry-run                # Preview what would happen
        forge update --force-download         # Force GitHub template download
    """
    show_banner()

    project_path = Path.cwd()

    # Phase 1: Validate project
    specforge_dir = project_path / ".specforge"
    if not specforge_dir.exists():
        console.print("[red]Error:[/red] No .specforge directory found. Run 'forge init --here' first.")
        raise typer.Exit(1)

    # Phase 2: Detect installed agents
    installed = detect_installed_agents(project_path)

    if not installed and not add:
        console.print("[red]Error:[/red] No installed agents detected and no --add flag provided.")
        console.print("[dim]Tip: Run 'forge init --here --ai <agent>' to set up an agent first.[/dim]")
        raise typer.Exit(1)

    # Phase 3: Validate --add agents
    agents_to_add = []
    if add:
        for agent_key in add:
            if agent_key not in AGENT_CONFIG:
                console.print(f"[red]Error:[/red] Unknown agent '{agent_key}'. Valid: {', '.join(AGENT_CONFIG.keys())}")
                raise typer.Exit(1)
            if agent_key in installed:
                console.print(f"[yellow]Note:[/yellow] '{agent_key}' is already installed, will update.")
            else:
                agents_to_add.append(agent_key)

    all_agents = list(dict.fromkeys(installed + agents_to_add))  # preserve order, deduplicate

    # Phase 4: Detect script type
    detected_script = script_type or detect_script_type(project_path)

    if script_type and script_type not in SCRIPT_TYPE_CHOICES:
        console.print(f"[red]Error:[/red] Invalid script type '{script_type}'. Choose from: {', '.join(SCRIPT_TYPE_CHOICES.keys())}")
        raise typer.Exit(1)

    # Phase 5: Display summary
    summary_lines = [
        "[cyan]SpecForge Update[/cyan]",
        "",
        f"{'Project':<20} [green]{project_path.name}[/green]",
        f"{'Installed agents':<20} [green]{', '.join(installed) if installed else '(none)'}[/green]",
    ]
    if agents_to_add:
        summary_lines.append(f"{'Adding agents':<20} [cyan]{', '.join(agents_to_add)}[/cyan]")
    summary_lines.append(f"{'Script type':<20} [green]{detected_script}[/green]")
    summary_lines.append(f"{'Sync':<20} [green]{'skip' if skip_sync else 'enabled'}[/green]")
    console.print(Panel("\n".join(summary_lines), border_style="cyan", padding=(1, 2)))

    if dry_run:
        console.print("[yellow]Dry run mode - no changes will be made.[/yellow]\n")
        dry_lines = [
            "[bold]Actions that would be performed:[/bold]",
            "",
            f"  1. Update shared resources (.specforge/scripts/, .specforge/templates/)",
            f"     [bright_black]Memory (.specforge/memory/) will NOT be touched[/bright_black]",
            f"  2. Regenerate commands for {len(all_agents)} agent(s): {', '.join(all_agents)}",
        ]
        if not skip_sync:
            # Check which context files exist
            context_info = []
            for ak in all_agents:
                rp = AGENT_CONTEXT_PATHS.get(ak)
                if rp:
                    fp = project_path / rp
                    exists = fp.exists()
                    context_info.append(f"    - {ak}: {rp} {'(exists)' if exists else '(will create)'}")
            dry_lines.append(f"  3. Sync context files (last-modified wins):")
            dry_lines.extend(context_info)
            dry_lines.append(f"  4. Sync skills and sub-agents across agent directories")
        else:
            dry_lines.append(f"  3. [bright_black]Sync skipped (--skip-sync)[/bright_black]")
        dry_lines.append(f"  {4 if not skip_sync else 3}. Ensure scripts are executable")
        console.print(Panel("\n".join(dry_lines), border_style="yellow", padding=(1, 2)))
        raise typer.Exit(0)

    # Phase 6: Execute update with tracker
    tracker = StepTracker("Update SpecForge Project")

    tracker.add("detect", "Detect installed agents")
    tracker.complete("detect", f"{len(installed)} found" + (f", adding {len(agents_to_add)}" if agents_to_add else ""))

    for key, label in [
        ("shared", "Update shared resources"),
        ("commands", "Regenerate agent commands"),
        ("context-sync", "Sync context files"),
        ("working-sync", "Sync skills and sub-agents"),
        ("chmod", "Ensure scripts executable"),
        ("final", "Finalize"),
    ]:
        tracker.add(key, label)

    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:
        tracker.attach_refresh(lambda: live.update(tracker.render()))

        try:
            # Get template source
            bundled_path = get_bundled_path()

            # --- Update shared resources (scripts + templates, NOT memory) ---
            tracker.start("shared")
            success = update_shared_resources(
                project_path, detected_script, bundled_path,
                force_download=force_download,
                tracker=tracker,
                github_token=github_token,
                skip_tls=skip_tls,
                debug=debug,
            )
            if success:
                tracker.complete("shared", "scripts and templates updated, memory preserved")
            else:
                tracker.error("shared", "failed to update shared resources")

            # --- Regenerate commands for all agents ---
            tracker.start("commands")
            source_path = bundled_path
            if not source_path:
                tracker.error("commands", "no bundled templates available")
            else:
                cmd_errors = []
                for agent_key in all_agents:
                    if not generate_agent_commands(agent_key, detected_script, project_path, source_path):
                        cmd_errors.append(agent_key)

                if cmd_errors:
                    tracker.error("commands", f"failed for: {', '.join(cmd_errors)}")
                else:
                    tracker.complete("commands", f"{len(all_agents)} agent(s) updated")

            # --- Sync context files ---
            if not skip_sync:
                tracker.start("context-sync")
                sync_context_files(all_agents, project_path, tracker)

                tracker.start("working-sync")
                sync_agent_working_files(all_agents, project_path, tracker)
            else:
                tracker.skip("context-sync", "--skip-sync")
                tracker.skip("working-sync", "--skip-sync")

            # --- Ensure executable scripts ---
            ensure_executable_scripts(project_path, tracker=tracker)

            tracker.complete("final", "update complete")

        except Exception as e:
            tracker.error("final", str(e))
            console.print(Panel(f"Update failed: {e}", title="Failure", border_style="red"))
            if debug:
                import traceback
                console.print(Panel(traceback.format_exc(), title="Debug Traceback", border_style="magenta"))
            raise typer.Exit(1)

    console.print(tracker.render())
    console.print("\n[bold green]Update complete.[/bold green]")

    # Show memory preservation notice
    memory_dir = specforge_dir / "memory"
    if memory_dir.exists():
        console.print(f"[dim]Memory preserved: .specforge/memory/ ({len(list(memory_dir.rglob('*')))} files untouched)[/dim]")


@app.command()
def version():
    """Display version and system information."""
    import platform
    import importlib.metadata
    
    show_banner()
    
    # Get CLI version from package metadata
    cli_version = "unknown"
    try:
        cli_version = importlib.metadata.version("forge-cli")
    except Exception:
        # Fallback: try reading from pyproject.toml if running from source
        try:
            import tomllib
            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    cli_version = data.get("project", {}).get("version", "unknown")
        except Exception:
            pass
    
    # Fetch latest template release version
    repo_owner = "Censseo"
    repo_name = "specforge"
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    
    template_version = "unknown"
    release_date = "unknown"
    
    try:
        response = client.get(
            api_url,
            timeout=10,
            follow_redirects=True,
            headers=_github_auth_headers(),
        )
        if response.status_code == 200:
            release_data = response.json()
            template_version = release_data.get("tag_name", "unknown")
            # Remove 'v' prefix if present
            if template_version.startswith("v"):
                template_version = template_version[1:]
            release_date = release_data.get("published_at", "unknown")
            if release_date != "unknown":
                # Format the date nicely
                try:
                    dt = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
                    release_date = dt.strftime("%Y-%m-%d")
                except Exception:
                    pass
    except Exception:
        pass

    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column("Key", style="cyan", justify="right")
    info_table.add_column("Value", style="white")

    info_table.add_row("CLI Version", cli_version)
    info_table.add_row("Template Version", template_version)
    info_table.add_row("Released", release_date)
    info_table.add_row("", "")
    info_table.add_row("Python", platform.python_version())
    info_table.add_row("Platform", platform.system())
    info_table.add_row("Architecture", platform.machine())
    info_table.add_row("OS Version", platform.version())

    panel = Panel(
        info_table,
        title="[bold cyan]Forge CLI Information[/bold cyan]",
        border_style="cyan",
        padding=(1, 2)
    )

    console.print(panel)
    console.print()

def main():
    app()

if __name__ == "__main__":
    main()

