#!/usr/bin/env python3
"""
Claude Code Setup - One-command installer for optimized Claude Code settings.

Detects your OS (Mac/Windows/Linux) and configures:
- CLAUDE.md with battle-tested instructions for better AI coding
- settings.json with zero-prompt permissions + deny-rule guardrails + hooks
- ccx command wrapper to launch Claude Code in the configured mode
- Hook scripts for session management and git safety
- Status line showing context usage and git branch

Usage:
    Mac/Linux:  python3 claude-setup.py
    Windows:    python claude-setup.py
"""

import json
import os
import platform
import shutil
import stat
import subprocess
import sys
from datetime import datetime


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

SYSTEM = platform.system()
IS_MAC = SYSTEM == "Darwin"
IS_WINDOWS = SYSTEM == "Windows"
IS_LINUX = SYSTEM == "Linux"

HOME = os.path.expanduser("~")
CLAUDE_DIR = os.path.join(HOME, ".claude")
HOOKS_DIR = os.path.join(CLAUDE_DIR, "hooks")


# ---------------------------------------------------------------------------
# CLAUDE.md content - platform-adapted
# ---------------------------------------------------------------------------

def get_platform_section():
    if IS_MAC:
        return (
            "## Platform\n"
            "- I use a Mac. Always use macOS keyboard shortcuts (Cmd, Option, etc.), "
            "macOS paths, and macOS-specific tools (pbcopy, open, etc.). Never reference "
            "Windows or Linux shortcuts - use the Mac equivalent (e.g., Cmd+Option+I for "
            "browser dev tools).\n"
        )
    elif IS_WINDOWS:
        return (
            "## Platform\n"
            "- I use Windows. Always use Windows keyboard shortcuts (Ctrl, Alt, etc.), "
            "Windows paths (backslashes), and Windows-specific tools. Never reference "
            "Mac shortcuts like Cmd - use the Windows equivalent (e.g., Ctrl+Shift+I or "
            "F12 for browser dev tools).\n"
        )
    else:
        return (
            "## Platform\n"
            "- I use Linux. Always use Linux keyboard shortcuts and paths. "
            "Use xdg-open for opening files/URLs.\n"
        )


CLAUDE_MD_BODY = r"""
## Context Efficiency
- Do not echo back file contents you just read.
- Do not narrate tool calls ("Let me read the file..."). Just do it.
- Keep explanations proportional to complexity. No preambles or sycophantic language.
- Never re-read a file already read in this session.
- For files over 500 lines, use offset/limit to read only the relevant section.
- Use Grep to locate sections before reading entire files.
- When understanding a component's API contract, read its interface / abstract class / protocol / trait before its implementation - same information, ~75% fewer tokens.
- When dispatching subagents, end prompts with: "Final response under 2000 characters."
- Do not paste file contents into subagent prompts. Give them the path and let them read it.

## Clarifying Questions
- Always ask clarifying questions for complex or ambiguous tasks. Do not assume.
- Always put questions at the very bottom of your response. Structure: work first, then questions.
- For high-risk tasks (database migrations, destructive operations, architectural changes), state your planned approach in 3-5 bullet points and wait for approval.

## Tools
- **Context7:** Before implementing ANY library/framework/API, check the latest docs. Do not rely on training data.
- **Sequential Thinking:** For complex problems, debugging, architecture decisions, or multi-step planning, automatically activate sequential thinking MCP.
- Never ask for permission to search the web. Just do it.
- **Skills:** Before starting any niche or domain-specific task (marketing, SEO, data analysis, etc.), check if a relevant skill exists and recommend using it if so.
- **grill-me:** When the user has a plan and is about to implement something non-trivial, if grill-me is not in the available skills list, suggest they install it: create `~/.claude/skills/grill-me/SKILL.md` or re-run `claude-setup.py`.
- **Marketing skills plugin:** When working on any project involving marketing, growth, copywriting, SEO, content strategy, social media, pricing, sales, product positioning, referrals, or any other business/go-to-market work - enable the marketingskills plugin for that project by adding `"marketing-skills@marketingskills": true` to `enabledPlugins` in `.claude/settings.local.json`. Do this automatically at session start without being asked.

## Open Source First
- Before writing custom code for any non-trivial problem (parsing, auth, validation, queuing, caching, etc.), check if a well-maintained open-source library already solves it.
- Prefer established libraries over custom implementations unless there is a specific reason not to (licensing, bundle size, security, no good option exists).

## Software Engineering Principles

When writing new code, embody these. When about to violate one, flag it briefly
in your response - don't restructure unrequested code, but don't silently
introduce violations either.

**Always:**
- **High Cohesion**: each function/class/module does one thing. If you can
  describe it with "and", split it.
- **Low Coupling**: application modules interact through minimal, well-defined
  interfaces. Never reach into another application module's internals.
- **Encapsulation**: expose only what callers need; everything else is private
  or internal by default.

**When state is involved:**
- **Single Source of Truth**: each piece of mutable state has one place where
  it is written. Reads can be distributed; writes cannot. Never let two
  components independently modify the same state.

**For multi-module projects (not scripts or single-file utilities):**
- **Layered Architecture**: if the project has distinct layers (presentation /
  business logic / data access), respect them. Don't skip layers without
  flagging it explicitly.
- **Named pattern**: before writing a new class, service, or design involving
  multiple interacting components, name the pattern in plain English -
  event-based (Observer/pub-sub), swappable strategy (Strategy), multiple
  creation types (Factory Method), integration shim (Adapter), simplified
  interface (Facade). Name it before writing; if none fits, say so.

**Before presenting non-trivial changes:**
- Pause and ask yourself: "Is there a more elegant way?" If the fix feels hacky, implement the elegant solution instead.
- Skip for simple, obvious fixes - don't over-engineer.

## Testing
- Every piece of code must have tests. No exceptions.
- Run tests after writing them. If tests fail, fix the code not the tests (unless the test is wrong).
- After any bug fix or feature, run the full test suite before committing.
- For Python projects, run `pytest` with full output after changes.

## Security
- Never put API keys, secrets, or tokens in frontend code. All secrets stay server-side via environment variables.
- Audit third-party skills before trusting them.
- Never use a superuser/admin database account for application connections. Use a role scoped to only what the application needs.
- Apply principle of least privilege: database users, API keys, and service accounts get only the permissions they actually need.
- For row-level access control, use RLS (Row Level Security) in the database rather than application-layer filtering.

## Context Preservation
- When starting a new session, read existing .md files first to restore context.
- If STATUS.md does not exist in the project root, create it immediately before doing any other work. It must include: end goal, done, in progress, next steps, blockers/decisions.
- Update STATUS.md after every logical milestone - not just at session end. It should always reflect current state.
- Every project must have a documented grand goal (north star) - there is no such thing as a project without one. If it is missing or unclear, ask me what it is and document it before doing other work.
- The end goal must always be the first section in STATUS.md. Judge every task through that lens: is this actually moving us toward the goal? If it doesn't serve the end goal, flag it.
- Goals can evolve. When the grand goal changes, update the end goal section immediately - never keep working toward a stale north star.
- Update project documentation .md files after completing each logical milestone or at natural breakpoints.

## Self-Improvement Loop
- After ANY correction from the user, append to `tasks/lessons.md` in the project root:
  `- [YYYY-MM-DD] RULE: <what to do or avoid> | WHY: <reason given>`
- At session start, if `tasks/lessons.md` exists, read it silently and apply all rules for the session
- Never delete entries - this file compounds over time

## Project Documentation
- For any project under ~/Documents/dev/: if STATUS.md exists and ROADMAP.md does not, invoke the project-docs skill immediately at session start - before any other work. The skill defines ROADMAP.md, METRICS.md, EXPERIMENTS.md, context/, docs/adr/, and docs/research/.
- Update those docs after completing any milestone (templates and rules live in the project-docs skill).

## Transcriptions
- When the user provides any audio, video, call recording, or transcript, invoke the save-transcription skill automatically - it files it under `docs/transcriptions/`.

## Context Window Monitoring
- Do NOT auto-trigger handoff warnings. The user monitors context % in the status bar and will type "handoff" when ready.

### When I type "handoff" or "handoff <project>"
Invoke the handoff skill (Skill tool, skill="handoff"). If a project name is given (e.g. "handoff my-app" - any folder under ~/Documents/dev/), the skill writes to `~/Documents/dev/<project>/docs/SESSION_HANDOFF.md` using git state from that directory. If no project name, writes to the current project. Pasting the last ~50 lines of a filled-up session helps capture mid-debug state, but is not required - the skill can reconstruct from git diff + log alone.

### When I type "ooc" or "running out of context"
Context is nearly full. Invoke the handoff skill (Skill tool, skill="handoff") for the current project, then reply with exactly: "Session saved. Open a new Claude Code session in this directory and type `read handoff` to resume."

### On Every Session Start
Invoke the startup skill immediately (Skill tool, skill="startup") as your very first action, before responding to anything. The hook will have already loaded SESSION_HANDOFF.md and STATUS.md as context - do not re-read them.

## Git
- Run `git status` and `git diff --staged` before every commit.
- Before committing, scan ALL .md files in the project and update every one that is stale - no fixed list, check everything that exists.
- After completing a logical unit of work, mention once that it is a good time to commit. Do not repeat.
- When I say "update github": invoke the update-github skill (project CLAUDE.md may override it).
- When I say "deploy": run the update-github skill first, then run the deployment (project CLAUDE.md may define a project-specific deploy).
- Enable Dependabot on all new GitHub repos.

## Deployment
- Before considering any project's deployment complete, verify it can go from a fresh clone to working software with a single setup command (excluding secrets). Document this in a setup script or README.

## Commit Messages
Every commit must be thorough. Follow this format:
- type(scope): short summary
- Detailed description explaining WHY, not just what. At least 2-3 sentences.
- List ALL affected files/components under "Changes:"
- Types: feat, fix, refactor, docs, style, test, chore, perf, ci, build
- Never write "fix stuff", "updates", or single-line messages for multi-file changes.

## No PII
- Never include real names, emails, phone numbers, addresses, IPs, usernames, client names, API keys, or tokens in commits, comments, docs, or READMEs.

## Command Style
- Never use multi-line bash commands. Chain on one line with && or ; or pipes.
- For complex scripts, create a .sh or .py file and execute it.

## Communication
- Do NOT repeatedly suggest pushing, committing, or deploying. State what is ready once.
- Never use em dashes anywhere. Use ` - ` or rewrite the sentence.
- Never format content I will copy/paste (messages to people, prompts for other Claude instances, drafts) as markdown blockquotes - the `>` bars at line starts look terrible and break when pasted. Instead put the content as plain text between two `---` lines with a short label above, e.g. "Message below:". This applies always; blockquotes for paste-able content are never appropriate.

## Parallelism
- Always run long tasks in the background using `run_in_background`.
- Use subagents for 2+ independent tasks. Never do sequentially what can be done concurrently.
- Subagents do not inherit conversation context. Every delegation must name exact files/paths, the goal or error state, and the expected output.
- Minimize manual work for the user. If you can do it via CLI/API/SSH/scripting, do it.

## Long-Running Processes
- Probe first: before any long job (API scan, backtest, remote script, pipeline), run a minimal version (1 record / 2-3 rows / a one-liner) and confirm the output looks right. A 5-second probe prevents a 3-minute failure.
- Run the full job with output redirected to a log (`cmd > output.log 2>&1 &`), check the log within 60s to confirm it is healthy, then check every ~5 minutes until done. Never run a long job silently.

## Superpowers
- Always use superpowers skills wherever applicable. Never skip them because "it's simple."
- When executing plans: always use `superpowers:subagent-driven-development`. Never ask which approach.
- Before claiming done: use `superpowers:verification-before-completion`.

## Critical Rules
- Never make assumptions about account balances, API limits, send volumes, or resource constraints. Always ask or read from config/env.
- When presenting data/metrics, cross-verify against raw source data. Do not interpolate or estimate. Show exact raw data supporting each number.

## Project Boundaries
- Never modify or delete files inside another project's repo from the current session - a "helpful" cross-project edit can silently break that project. If work is needed there, write a paste-ready prompt for that project's own Claude instance and hand it to me. Reading other projects for context stays fine.

## Machine Resources (Mac + VM)
- CPU: processes you spawn must stay under ~25% of the Mac's processing power unless I explicitly allow more for a specific task. Throttle parallelism accordingly (worker counts, parallel jobs, make -j, concurrent subprocesses).
- Storage: before creating anything that grows over time (datasets, caches, logs, downloaded models, build artifacts), state the expected size and growth. Flag anything likely to exceed ~1GB before writing it.
- If a project directory, ~/.claude (projects/, transcripts, caches), or the VM looks bloated during normal work, surface it with a concrete plan: back up to the right remote (GitHub, dotenv repo, cloud storage) first, then clean up locally. Never delete unbacked data without asking.

## Phase Checkpoints
- Before starting each new phase of a multi-step task, run a full checkpoint: tests, clean git, 3-line status summary. Do not proceed until green.
"""


# ---------------------------------------------------------------------------
# settings.json
# ---------------------------------------------------------------------------

def get_settings():
    settings = {
        "permissions": {
            "defaultMode": "bypassPermissions",
            # Deny rules are enforced even in bypassPermissions mode
            # (verified live 2026-06-11). They replace the old cc-wrapper
            # blocklist, which used --disallowedTools and could be shadowed.
            "deny": [
                "Bash(rm -rf:*)",
                "Bash(rm -fr:*)",
                "Bash(sudo rm:*)",
                "Bash(git push --force:*)",
                "Bash(git push -f:*)",
                "Read(./.env)",
                "Read(./.env.*)",
                "Read(**/.env)",
                "Read(**/.env.*)",
                # Credential paths (Trail of Bits hardening pattern)
                "Read(~/.ssh/**)",
                "Read(~/.aws/**)",
                "Read(~/.kube/**)",
                "Read(~/.gnupg/**)",
                "Read(~/.npmrc)",
                "Read(~/.pypirc)"
            ]
        },
        # A compromised cloned repo could ship malicious MCP servers via its
        # .mcp.json - require explicit opt-in per project instead.
        "enableAllProjectMcpServers": False,
        "env": {
            "MAX_THINKING_TOKENS": "10000",
            "DISABLE_AUTO_COMPACT": "true"
        },
        "autoCompactWindow": 1000000,
        # Pre-declare the team marketplace with auto-update ON and the plugin
        # enabled, so a single installer run wires up continuous updates: skills,
        # agents, and hooks (which now live in the plugin) flow to the user on
        # every restart with zero further action. The CLI install step below is
        # a belt-and-suspenders fallback for older clients.
        "extraKnownMarketplaces": {
            "coach-foundation": {
                "source": {
                    "source": "github",
                    "repo": "Coach-Foundation/claude-code-best-practices"
                },
                "autoUpdate": True
            }
        },
        "enabledPlugins": {
            "ap-optimal-claude@coach-foundation": True
        },
        # Only the Notification hook stays here: its Windows variant is a direct
        # powershell command that fires without bash, so it cannot move into the
        # (bash-script) plugin without regressing native Windows. The other four
        # hooks now ship in the ap-optimal-claude plugin (hooks/hooks.json) so
        # they auto-update with the rest of the kit.
        "hooks": {
            "Notification": [
                {
                    "hooks": [
                        get_notification_hook()
                    ]
                }
            ]
        },
        "statusLine": {
            "type": "command",
            "command": "npx -y ccstatusline@2",
            "padding": 0
        }
        # No "model" pin: let each user keep their account default. The old
        # "sonnet" alias form is outdated; use full model IDs if pinning.
    }
    return settings


# Hook scripts that moved into the ap-optimal-claude plugin (v1.1.0). When
# merging into an existing settings.json we strip any leftover registrations of
# these (from an older direct install) so they do not double-fire with the
# plugin's copies. Matched by basename anywhere in the command string.
MIGRATED_HOOK_SCRIPTS = (
    "pre-commit-check.sh", "session-start.sh",
    "pre-compact.sh", "stop-self-review.sh",
)


def _strip_migrated_hooks(hooks):
    """Drop any hook entry whose command references a now-plugin-shipped script.
    Empties (events/groups left with no hooks) are removed so the structure stays clean."""
    cleaned = {}
    for event, groups in hooks.items():
        new_groups = []
        for group in groups:
            kept = [h for h in group.get("hooks", [])
                    if not any(s in (h.get("command") or "") for s in MIGRATED_HOOK_SCRIPTS)]
            if kept:
                ng = dict(group)
                ng["hooks"] = kept
                new_groups.append(ng)
        if new_groups:
            cleaned[event] = new_groups
    return cleaned


def merge_settings(existing, managed):
    """Merge the managed baseline into an existing settings.json non-destructively.

    Preserves user customizations - theme, tui, extra hooks (RTK, pytest,
    spec-guard), other enabled plugins, and any unknown top-level keys. The
    installer owns a small set of baseline keys (env, autoCompactWindow,
    statusLine, enableAllProjectMcpServers, marketplace) and wins for those;
    deny rules and enabled plugins are UNIONED so nothing the user added is lost.
    A fresh install (existing == {}) just yields the managed baseline.
    """
    result = dict(existing)  # carry over every unknown top-level key untouched

    # Baseline keys the installer owns outright
    for key in ("enableAllProjectMcpServers", "env", "autoCompactWindow", "statusLine"):
        if key in managed:
            result[key] = managed[key]

    # permissions: keep user keys (e.g. allow), enforce defaultMode, UNION the deny baseline
    perms = dict(result.get("permissions", {}))
    mperms = managed.get("permissions", {})
    if "defaultMode" in mperms:
        perms["defaultMode"] = mperms["defaultMode"]
    deny = list(perms.get("deny", []))
    for rule in mperms.get("deny", []):
        if rule not in deny:
            deny.append(rule)
    if deny:
        perms["deny"] = deny
    if perms:
        result["permissions"] = perms

    # extraKnownMarketplaces: add managed entries, keep any the user already has
    mkts = dict(result.get("extraKnownMarketplaces", {}))
    mkts.update(managed.get("extraKnownMarketplaces", {}))
    if mkts:
        result["extraKnownMarketplaces"] = mkts

    # enabledPlugins: UNION - never disable a plugin the user already enabled
    plugins = dict(result.get("enabledPlugins", {}))
    plugins.update(managed.get("enabledPlugins", {}))
    if plugins:
        result["enabledPlugins"] = plugins

    # hooks: strip the migrated-hook registrations (now in the plugin), keep every
    # other user hook (RTK, pytest, spec-guard), then set the managed Notification hook
    hooks = _strip_migrated_hooks(result.get("hooks", {}))
    for event, groups in managed.get("hooks", {}).items():
        hooks[event] = groups  # managed owns Notification
    if hooks:
        result["hooks"] = hooks

    return result


def get_notification_hook():
    if IS_MAC:
        return {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Hero.aiff & open -g /Applications/Utilities/Terminal.app"
        }
    elif IS_WINDOWS:
        return {
            "type": "command",
            "command": (
                'powershell.exe -c "'
                "[System.Media.SystemSounds]::Exclamation.Play(); "
                "$null = New-BurntToastNotification "
                "-Text 'Claude Code','Needs your attention' "
                "-ErrorAction SilentlyContinue"
                '"'
            )
        }
    else:
        return {
            "type": "command",
            "command": (
                "notify-send 'Claude Code' 'Needs your attention' 2>/dev/null; "
                "printf '\\a'"
            )
        }


# ---------------------------------------------------------------------------
# Hook scripts have moved to the ap-optimal-claude plugin
# ---------------------------------------------------------------------------
# The four bash hooks (pre-commit-check, session-start, pre-compact,
# stop-self-review) now live in plugins/ap-optimal-claude/hooks/ and are
# registered via that plugin's hooks/hooks.json, so they auto-update with the
# rest of the kit. Only the OS-specific Notification hook (get_notification_hook
# above) is still installed directly into settings.json by this script, because
# its Windows variant must run without bash.


# ---------------------------------------------------------------------------
# ccx wrapper script
# ---------------------------------------------------------------------------
# NOTE: the command is deliberately NOT named "cc" - that shadows the system
# C compiler (/usr/bin/cc) and breaks native builds. Safety comes from
# permissions.deny rules in settings.json (enforced even in bypass mode),
# not from a bypassable --disallowedTools blocklist.

CCX_SCRIPT_UNIX = """#!/bin/bash
claude "$@"
"""

CCX_SCRIPT_WINDOWS = """@echo off
claude %*
"""


# ---------------------------------------------------------------------------
# Installation logic
# ---------------------------------------------------------------------------

def backup_file(path):
    """Back up a file with a timestamp if it exists."""
    if os.path.exists(path):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{path}.backup_{ts}"
        shutil.copy2(path, backup_path)
        print(f"  [BACKUP] {os.path.basename(path)} -> {os.path.basename(backup_path)}")
        return True
    return False


def write_file(path, content, executable=False):
    """Write content to a file, creating parent directories."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    newline = "\r\n" if path.endswith(".bat") else "\n"
    with open(path, "w", newline=newline) as f:
        f.write(content)
    if executable and not IS_WINDOWS:
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    print(f"  [OK] {path}")


def merge_claude_json():
    """Merge terminal_bell setting into .claude.json without overwriting login data."""
    claude_json_path = os.path.join(HOME, ".claude.json")
    backup_file(claude_json_path)
    try:
        with open(claude_json_path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data["preferredNotifChannel"] = "terminal_bell"
    with open(claude_json_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  [OK] {claude_json_path} (terminal bell enabled)")


def remove_legacy_cc():
    """Remove the old 'cc' wrapper that shadowed the system C compiler."""
    for legacy in [os.path.join(HOME, ".local", "bin", "cc"),
                   os.path.join(HOME, "bin", "cc.bat")]:
        if os.path.exists(legacy):
            try:
                with open(legacy) as f:
                    if "claude" in f.read():
                        os.remove(legacy)
                        print(f"  [REMOVED] legacy wrapper {legacy}")
            except OSError:
                pass
    legacy_usr = "/usr/local/bin/cc"
    if not IS_WINDOWS and os.path.exists(legacy_usr):
        try:
            with open(legacy_usr) as f:
                if "claude" in f.read():
                    print(f"  [!] Old wrapper at {legacy_usr} shadows the C compiler.")
                    print(f"      Remove it with: sudo rm {legacy_usr}")
        except OSError:
            pass


def install_ccx_wrapper():
    """Install the ccx wrapper command (user-local, no sudo, no name collision)."""
    if IS_WINDOWS:
        ccx_dir = os.path.join(HOME, "bin")
        ccx_path = os.path.join(ccx_dir, "ccx.bat")
        os.makedirs(ccx_dir, exist_ok=True)
        write_file(ccx_path, CCX_SCRIPT_WINDOWS)
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        if ccx_dir not in path_dirs:
            print(f"\n  NOTE: Add {ccx_dir} to your system PATH:")
            print(f"  1. Search 'Environment Variables' in Windows Settings")
            print(f"  2. Edit PATH, add: {ccx_dir}")
            print(f"  3. Restart your terminal")
    else:
        ccx_path = os.path.join(HOME, ".local", "bin", "ccx")
        os.makedirs(os.path.dirname(ccx_path), exist_ok=True)
        write_file(ccx_path, CCX_SCRIPT_UNIX, executable=True)
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        if os.path.dirname(ccx_path) not in path_dirs:
            print(f"  NOTE: Add {os.path.dirname(ccx_path)} to your PATH, e.g.:")
            print(f"  echo 'export PATH=\"$HOME/.local/bin:$PATH\"' >> ~/.zshrc")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def install_team_plugin():
    """Belt-and-suspenders plugin install via the claude CLI.

    settings.json already pre-declares the marketplace (auto-update ON) and
    enables the plugin via extraKnownMarketplaces + enabledPlugins, so on most
    clients the plugin installs and stays current with no CLI step. This runs
    the explicit CLI commands anyway to cover older clients that do not act on
    those settings keys.
    """
    claude_bin = shutil.which("claude")
    if not claude_bin:
        print("  [SKIP] claude CLI not on PATH - settings.json already enables the")
        print("         plugin, so it should install on restart. If it does not, run:")
        print("         /plugin marketplace add Coach-Foundation/claude-code-best-practices")
        print("         /plugin install ap-optimal-claude@coach-foundation")
        return
    steps = [
        (["plugin", "marketplace", "add", "Coach-Foundation/claude-code-best-practices"],
         "marketplace coach-foundation"),
        (["plugin", "install", "ap-optimal-claude@coach-foundation"],
         "plugin ap-optimal-claude"),
    ]
    for args, label in steps:
        try:
            r = subprocess.run([claude_bin] + args, capture_output=True, text=True, timeout=180)
            out = (r.stdout or r.stderr or "").strip()
            tail = out.splitlines()[-1] if out else "done"
            print(f"  [{'OK' if r.returncode == 0 else '!'}] {label}: {tail}")
            if r.returncode != 0:
                print("      If this keeps failing, run inside Claude Code: /plugin install ap-optimal-claude@coach-foundation")
        except Exception as exc:
            print(f"  [!] {label} failed ({exc})")
            print("      Run inside Claude Code: /plugin install ap-optimal-claude@coach-foundation")


def setup():
    plat_name = "Mac" if IS_MAC else "Windows" if IS_WINDOWS else "Linux"
    print(f"\nClaude Code Setup - {plat_name}")
    print("=" * 50)

    # Create directories
    os.makedirs(CLAUDE_DIR, exist_ok=True)
    os.makedirs(HOOKS_DIR, exist_ok=True)

    # Back up existing files
    print("\n1. Backing up existing files...")
    backed_up = False
    for fname in ["CLAUDE.md", "settings.json"]:
        if backup_file(os.path.join(CLAUDE_DIR, fname)):
            backed_up = True
    if not backed_up:
        print("  No existing files to back up.")

    # Write CLAUDE.md
    print("\n2. Installing CLAUDE.md...")
    claude_md = "# Claude Code Instructions\n\n" + get_platform_section() + CLAUDE_MD_BODY
    write_file(os.path.join(CLAUDE_DIR, "CLAUDE.md"), claude_md)

    # Write settings.json - MERGE into any existing file (a timestamped backup was
    # made above). Overwriting wholesale would wipe user customizations: other
    # enabled plugins, theme/tui, and extra hooks (RTK, pytest, spec-guard).
    print("\n3. Installing settings.json (merging into existing)...")
    managed = get_settings()
    settings_path = os.path.join(CLAUDE_DIR, "settings.json")
    try:
        with open(settings_path) as f:
            existing = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing = {}
    settings = merge_settings(existing, managed)
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
    print(f"  [OK] {settings_path}")

    # Hooks now ship in the ap-optimal-claude plugin (hooks/hooks.json) so they
    # auto-update with the rest of the kit. Remove the copies that older installs
    # wrote into ~/.claude/hooks: leaving them would double-fire every hook once
    # the plugin updates (plugin + settings.json would both register them). The
    # Notification hook stays inline in settings.json and needs no script file.
    print("\n4. Migrating hooks to the plugin (removing old local copies)...")
    migrated_hooks = [
        "pre-commit-check.sh", "session-start.sh",
        "pre-compact.sh", "stop-self-review.sh",
        # afk-resume.sh: retired reminder loop from earlier versions (token sink -
        # each wakeup re-read the whole conversation at cold-cache prices).
        "afk-resume.sh",
    ]
    removed_any = False
    for hname in migrated_hooks:
        hpath = os.path.join(HOOKS_DIR, hname)
        if os.path.exists(hpath):
            os.remove(hpath)
            print(f"  [REMOVED] {hname}")
            removed_any = True
    if not removed_any:
        print("  Clean install - nothing to migrate.")

    # Write skills
    print("\n4b. Installing skills...")
    SKILLS_DIR = os.path.join(CLAUDE_DIR, "skills")
    startup_dir = os.path.join(SKILLS_DIR, "startup")
    os.makedirs(startup_dir, exist_ok=True)
    write_file(os.path.join(startup_dir, "SKILL.md"), SKILL_STARTUP)
    for skill_name, skill_content in [
        ("update-github", SKILL_UPDATE_GITHUB),
        ("project-docs", SKILL_PROJECT_DOCS),
        ("save-transcription", SKILL_SAVE_TRANSCRIPTION),
    ]:
        skill_dir = os.path.join(SKILLS_DIR, skill_name)
        os.makedirs(skill_dir, exist_ok=True)
        write_file(os.path.join(skill_dir, "SKILL.md"), skill_content)
    legacy_reminder = os.path.join(SKILLS_DIR, "context-reminder")
    if os.path.isdir(legacy_reminder):
        shutil.rmtree(legacy_reminder)
        print("  [REMOVED] context-reminder skill (reminder loop retired)")

    # Optional: grill-me skill
    grill_me_dir = os.path.join(SKILLS_DIR, "grill-me")
    grill_me_path = os.path.join(grill_me_dir, "SKILL.md")
    if os.path.exists(grill_me_path) or os.path.exists(os.path.join(grill_me_dir, "skill.md")):
        print("  [SKIP] grill-me skill already installed")
    else:
        try:
            answer = input("\n  Install grill-me skill? Stress-tests plans before implementation (recommended) [Y/n]: ").strip().lower()
        except EOFError:
            # Non-interactive run (e.g. Claude executing the installer): default to yes
            answer = ""
        if answer in ("", "y", "yes"):
            os.makedirs(grill_me_dir, exist_ok=True)
            write_file(grill_me_path, SKILL_GRILL_ME)
            print("  [OK] grill-me skill installed")
        else:
            print("  [SKIP] grill-me skill skipped")

    # Remove the dead .claudeignore (not a Claude Code feature; replaced by
    # permissions.deny Read rules in settings.json)
    claudeignore_path = os.path.join(HOME, ".claudeignore")
    if os.path.exists(claudeignore_path):
        os.remove(claudeignore_path)
        print(f"\n  [REMOVED] {claudeignore_path} (.claudeignore is not a Claude Code feature)")

    # Merge terminal bell setting
    print("\n5. Configuring notifications...")
    merge_claude_json()

    # Install ccx wrapper (and clean up the old cc one)
    print("\n6. Installing ccx command...")
    remove_legacy_cc()
    install_ccx_wrapper()

    # Install the team plugin (marketplace + ap-optimal-claude) - no typed commands needed
    print("\n7. Installing the ap-optimal-claude team plugin...")
    install_team_plugin()

    # Done
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)

    print(f"\nPlatform:       {plat_name}")
    print(f"CLAUDE.md:      {os.path.join(CLAUDE_DIR, 'CLAUDE.md')}")
    print(f"settings.json:  {os.path.join(CLAUDE_DIR, 'settings.json')}")
    print(f"Hooks:          via the ap-optimal-claude plugin (auto-updating)")

    print("\n--- Continuous updates (auto-configured) ---")
    print("  The team marketplace is registered with auto-update ON, so future")
    print("  skill / agent / hook changes arrive on restart - no re-running this")
    print("  installer for those. Re-run it only for CLAUDE.md / settings / deny-rule changes.")

    print("\n--- Token optimization (auto-configured) ---")
    print("  MAX_THINKING_TOKENS=10000     (caps the extended-thinking budget)")
    print("  DISABLE_AUTO_COMPACT=true     (prefer session handoff files over autocompact)")
    print("  Stop hook (via plugin)         (self-review pass when code was edited)")

    print("\n--- How to use ---")
    print("  ccx             Start Claude Code (zero prompts, deny-rule guardrails)")
    print("  ccx --resume    Resume your last session")
    print("  claude          Same thing (settings.json sets the permission mode)")

    print("\n--- Recommended plugins (run inside a cc session) ---")
    print('  Type: /install-plugin superpowers      (structured workflows)')
    print('  Type: /install-plugin context7          (latest library docs)')
    print('  Type: /install-plugin code-simplifier   (code quality reviews)')

    if IS_MAC:
        print("\n--- Mac notifications ---")
        print("  When Claude needs attention you get a chime + the Terminal dock badge.")
        print("  No floating banners are used.")

    if IS_WINDOWS:
        print("\n--- Windows notification setup ---")
        print("  For richer notifications, install BurntToast:")
        print("  powershell: Install-Module -Name BurntToast")

    print("\n--- Safety guardrails (permissions.deny in settings.json) ---")
    print("  rm -rf / rm -fr / sudo rm   (recursive deletion)")
    print("  git push --force / -f       (overwriting remote history)")
    print("  Read .env / .env.*          (secrets stay out of context)")
    print("  These bind even in bypassPermissions mode (verified live).")
    print("  Everything else runs without prompts.\n")


if __name__ == "__main__":
    setup()
