#!/usr/bin/env python3
"""
Claude Code Setup - One-command installer for optimized Claude Code settings.

Detects your OS (Mac/Windows/Linux) and configures:
- CLAUDE.md with battle-tested instructions for better AI coding
- settings.json with zero-prompt permissions + token optimization + hooks
- .claudeignore to prevent scanning large/irrelevant files
- cc command wrapper (blocks rm -rf and force push)
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
- When dispatching subagents, end prompts with: "Final response under 2000 characters."
- Do not paste file contents into subagent prompts. Give them the path and let them read it.

## Clarifying Questions
- Always ask clarifying questions for complex or ambiguous tasks. Do not assume.
- Always put questions at the very bottom of your response. Structure: work first, then questions.
- For high-risk tasks (database migrations, destructive operations, architectural changes), state your planned approach in 3-5 bullet points and wait for approval.

## Tools
- **Context7:** Before implementing ANY library/framework/API, check the latest docs. Do not rely on training data.
- Never ask for permission to search the web. Just do it.
- **Skills:** Before starting any niche or domain-specific task (marketing, SEO, data analysis, etc.), check if a relevant skill exists and recommend using it if so.

## Open Source First
- Before writing custom code for any non-trivial problem (parsing, auth, validation, queuing, caching, etc.), check if a well-maintained open-source library already solves it.
- Prefer established libraries over custom implementations unless there is a specific reason not to (licensing, bundle size, security, no good option exists).

## Testing
- Every piece of code must have tests. No exceptions.
- Run tests after writing them. If tests fail, fix the code not the tests (unless the test is wrong).
- After any bug fix or feature, run the full test suite before committing.

## Security
- Never put API keys, secrets, or tokens in frontend code. All secrets stay server-side via environment variables.
- Audit third-party skills before trusting them.

## Context Preservation
- Update project documentation .md files after completing each logical milestone or at natural breakpoints.
- Maintain a STATUS.md in the project root tracking: done, in progress, next, blockers/decisions.
- When starting a new session, read existing .md files first to restore context.

## Context Window Monitoring
- Do NOT auto-trigger handoff warnings. The user monitors context % in the status bar and will type "handoff" when ready.

### When I type "handoff"
Immediately create or update docs/SESSION_HANDOFF.md with: What We Were Doing, What Was Completed, Current State, Next Steps, Key Files Changed, Commands To Know, Decisions Made, Warnings/Gotchas.

### On Every Session Start
If docs/SESSION_HANDOFF.md exists, read it and confirm: "Handoff loaded. Continuing from: [one line summary]"

## Git
- Run `git status` and `git diff --staged` before every commit.
- After completing a logical unit of work, mention once that it is a good time to commit. Do not repeat.

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

## Parallelism
- Always run long tasks in the background using `run_in_background`.
- Use subagents for 2+ independent tasks. Never do sequentially what can be done concurrently.
- Minimize manual work for the user. If you can do it via CLI/API/SSH/scripting, do it.

## Self-Review Before Claiming Done
Before saying any task is "done", verify: (1) tests pass, (2) the feature actually works, (3) you did everything asked, (4) no half-modified files remain. If any check fails, fix it before claiming done.
"""


# ---------------------------------------------------------------------------
# settings.json
# ---------------------------------------------------------------------------

def get_settings():
    settings = {
        "permissions": {
            "defaultMode": "bypassPermissions"
        },
        "env": {
            "MAX_THINKING_TOKENS": "10000",
            "CLAUDE_CODE_SUBAGENT_MODEL": "haiku",
            "DISABLE_AUTO_COMPACT": "true"
        },
        "autoCompactWindow": 1000000,
        "hooks": {
            "Notification": [
                {
                    "hooks": [
                        get_notification_hook()
                    ]
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": os.path.join(HOOKS_DIR, "pre-commit-check.sh"),
                            "if": "Bash(git commit*)",
                            "statusMessage": "Checking git status..."
                        }
                    ]
                }
            ],
            "SessionStart": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": os.path.join(HOOKS_DIR, "session-start.sh"),
                            "statusMessage": "Loading session context..."
                        }
                    ]
                }
            ],
            "PreCompact": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": os.path.join(HOOKS_DIR, "pre-compact.sh"),
                            "statusMessage": "Preserving context before compaction..."
                        }
                    ]
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": os.path.join(HOOKS_DIR, "stop-self-review.sh"),
                            "statusMessage": "Verifying work completeness..."
                        }
                    ]
                }
            ]
        },
        "statusLine": {
            "type": "command",
            "command": "npx -y ccstatusline@latest",
            "padding": 0
        },
        "model": "sonnet"
    }
    return settings


def get_notification_hook():
    if IS_MAC:
        return {
            "type": "command",
            "command": (
                "osascript -e 'display notification "
                "\"Claude Code needs your attention\" "
                "with title \"Claude Code\" "
                "sound name \"Hero\"'"
            )
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
# Hook scripts (portable - no hardcoded paths)
# ---------------------------------------------------------------------------

HOOK_PRE_COMMIT = """#!/bin/bash
# Show staged files and git status before committing
# Guard: only run inside a git repo
git rev-parse --git-dir > /dev/null 2>&1 || exit 0

echo "=== Staged files ==="
git diff --staged --name-only 2>/dev/null
echo ""
echo "=== Git status ==="
git status --short 2>/dev/null
"""

HOOK_SESSION_START = """#!/bin/bash
# Load session context on startup
# Outputs any existing handoff or status docs as additionalContext for Claude

CONTEXT=""

if [ -f docs/SESSION_HANDOFF.md ]; then
    CONTEXT="$CONTEXT\\n=== SESSION_HANDOFF.md ===\\n$(cat docs/SESSION_HANDOFF.md)"
fi

if [ -f STATUS.md ]; then
    CONTEXT="$CONTEXT\\n=== STATUS.md ===\\n$(cat STATUS.md)"
fi

if [ -n "$CONTEXT" ]; then
    PYTHON=$(command -v python3 || command -v python) 2>/dev/null
    [ -z "$PYTHON" ] && exit 0
    echo -e "$CONTEXT" | $PYTHON -c "
import json, sys
content = sys.stdin.read()
output = {'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': content}}
print(json.dumps(output))
"
fi
"""

HOOK_PRE_COMPACT = """#!/bin/bash
# Warn before context compaction and dump critical state
echo '{"systemMessage":"Context compaction occurring. Preserving critical state in STATUS.md."}'
"""

HOOK_STOP_SELF_REVIEW = """#!/bin/bash
# Stop hook: only require self-review if code was written or edited this session.
# For pure Q&A sessions this exits silently (zero token cost).

ARGS="${ARGUMENTS:-{}}"

STOP_HOOK_ACTIVE=$(echo "$ARGS" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(str(d.get('stop_hook_active', False)).lower())
except:
    print('false')
" 2>/dev/null)

if [ "$STOP_HOOK_ACTIVE" = "true" ]; then
    echo '{"decision": "approve"}'
    exit 0
fi

TRANSCRIPT_PATH=$(echo "$ARGS" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    print(d.get('transcript_path', ''))
except:
    print('')
" 2>/dev/null)

if [ -z "$TRANSCRIPT_PATH" ] || [ ! -f "$TRANSCRIPT_PATH" ]; then
    echo '{"decision": "approve"}'
    exit 0
fi

HAS_CODE_CHANGES=$(python3 -c "
import json, sys
try:
    with open(sys.argv[1]) as f:
        transcript = json.load(f)
    for msg in transcript.get('messages', []):
        if msg.get('role') == 'assistant':
            for block in msg.get('content', []):
                if isinstance(block, dict) and block.get('type') == 'tool_use':
                    if block.get('name') in ('Write', 'Edit', 'NotebookEdit'):
                        print('yes')
                        sys.exit(0)
    print('no')
except:
    print('no')
" "$TRANSCRIPT_PATH" 2>/dev/null)

if [ "$HAS_CODE_CHANGES" = "yes" ]; then
    python3 -c "
import json
reason = (
    'Code was written or modified this session. Before stopping, complete the 3-pass self-review: '
    '(1) Verification: run the full test suite and confirm all tests pass. '
    '(2) Adversarial Review: what assumptions did you not verify? How will this fail in production? '
    '(3) Completeness Check: re-read the original request - did you do everything asked? '
    'Fix any issues found before claiming done.'
)
print(json.dumps({'decision': 'block', 'reason': reason}))
"
else
    echo '{"decision": "approve"}'
fi
"""


# ---------------------------------------------------------------------------
# cc wrapper script
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# .claudeignore content - prevents scanning large/irrelevant files
# ---------------------------------------------------------------------------

CLAUDEIGNORE_CONTENT = """node_modules/
dist/
build/
.next/
*.lock
__pycache__/
.git/
*.db
*.sqlite
*.log
coverage/
*.min.js
*.min.css
vendor/
.playwright-mcp/
"""


CC_SCRIPT_UNIX = """#!/bin/bash
claude --dangerously-skip-permissions --disallowedTools "Bash(rm -rf *)" "Bash(git push --force *)" "Bash(git push -f *)" "$@"
"""

CC_SCRIPT_WINDOWS = """@echo off
claude --dangerously-skip-permissions --disallowedTools "Bash(rm -rf *)" "Bash(git push --force *)" "Bash(git push -f *)" %*
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


def install_cc_wrapper():
    """Install the cc wrapper command."""
    if IS_WINDOWS:
        cc_dir = os.path.join(HOME, "bin")
        cc_path = os.path.join(cc_dir, "cc.bat")
        os.makedirs(cc_dir, exist_ok=True)
        write_file(cc_path, CC_SCRIPT_WINDOWS)
        # Check if ~/bin is in PATH
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        if cc_dir not in path_dirs:
            print(f"\n  NOTE: Add {cc_dir} to your system PATH:")
            print(f"  1. Search 'Environment Variables' in Windows Settings")
            print(f"  2. Edit PATH, add: {cc_dir}")
            print(f"  3. Restart your terminal")
    else:
        cc_path = "/usr/local/bin/cc"
        try:
            os.makedirs("/usr/local/bin", exist_ok=True)
            write_file(cc_path, CC_SCRIPT_UNIX, executable=True)
        except PermissionError:
            print("  [!] Need sudo to install cc to /usr/local/bin")
            try:
                subprocess.run(
                    ["sudo", "mkdir", "-p", "/usr/local/bin"],
                    check=True
                )
                # Write via sudo
                proc = subprocess.run(
                    ["sudo", "tee", cc_path],
                    input=CC_SCRIPT_UNIX.encode(),
                    stdout=subprocess.DEVNULL,
                    check=True
                )
                subprocess.run(["sudo", "chmod", "+x", cc_path], check=True)
                print(f"  [OK] {cc_path}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback: install to ~/.local/bin
                fallback = os.path.join(HOME, ".local", "bin", "cc")
                os.makedirs(os.path.dirname(fallback), exist_ok=True)
                write_file(fallback, CC_SCRIPT_UNIX, executable=True)
                print(f"  [FALLBACK] Installed to {fallback}")
                print(f"  Add {os.path.dirname(fallback)} to your PATH if not already there")


def trigger_mac_notification():
    """Trigger a test notification so Script Editor appears in notification settings."""
    if IS_MAC:
        try:
            subprocess.run(
                ["osascript", "-e",
                 'display notification "Setup complete!" '
                 'with title "Claude Code" sound name "Hero"'],
                capture_output=True, timeout=5
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

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

    # Write settings.json
    print("\n3. Installing settings.json...")
    settings = get_settings()
    settings_path = os.path.join(CLAUDE_DIR, "settings.json")
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
    print(f"  [OK] {settings_path}")

    # Write hook scripts
    print("\n4. Installing hook scripts...")
    write_file(os.path.join(HOOKS_DIR, "pre-commit-check.sh"), HOOK_PRE_COMMIT, executable=True)
    write_file(os.path.join(HOOKS_DIR, "session-start.sh"), HOOK_SESSION_START, executable=True)
    write_file(os.path.join(HOOKS_DIR, "pre-compact.sh"), HOOK_PRE_COMPACT, executable=True)
    write_file(os.path.join(HOOKS_DIR, "stop-self-review.sh"), HOOK_STOP_SELF_REVIEW, executable=True)

    # Install .claudeignore (per-project template in home dir)
    print("\n5. Installing .claudeignore template...")
    claudeignore_path = os.path.join(HOME, ".claudeignore")
    if not os.path.exists(claudeignore_path):
        write_file(claudeignore_path, CLAUDEIGNORE_CONTENT)
    else:
        print(f"  [SKIP] {claudeignore_path} already exists")

    # Merge terminal bell setting
    print("\n6. Configuring notifications...")
    merge_claude_json()

    # Install cc wrapper
    print("\n7. Installing cc command...")
    install_cc_wrapper()

    # Trigger notification (Mac only)
    trigger_mac_notification()

    # Done
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)

    print(f"\nPlatform:       {plat_name}")
    print(f"CLAUDE.md:      {os.path.join(CLAUDE_DIR, 'CLAUDE.md')}")
    print(f"settings.json:  {os.path.join(CLAUDE_DIR, 'settings.json')}")
    print(f".claudeignore:  {claudeignore_path}")
    print(f"Hooks:          {HOOKS_DIR}")

    print("\n--- Token optimization (auto-configured) ---")
    print("  MAX_THINKING_TOKENS=10000    (70% thinking token reduction)")
    print("  Subagent model: haiku        (80% cheaper subagents)")
    print("  Effort level: medium         (50-70% fewer output tokens)")
    print("  Auto-compact: 75%            (earlier compaction, more buffer)")
    print("  .claudeignore installed       (prevents scanning junk files)")

    print("\n--- How to use ---")
    print("  cc              Start Claude Code (zero prompts, safe)")
    print("  cc --resume     Resume your last session")
    print("  claude          Start with default prompts (if you ever want them back)")

    print("\n--- Recommended plugins (run inside a cc session) ---")
    print('  Type: /install-plugin superpowers      (structured workflows)')
    print('  Type: /install-plugin context7          (latest library docs)')
    print('  Type: /install-plugin code-simplifier   (code quality reviews)')

    if IS_MAC:
        print("\n--- Mac notification setup ---")
        print("  1. Open System Settings -> Notifications")
        print("  2. Find 'Script Editor' in the list")
        print("  3. Set Alert Style to 'Persistent'")
        print("  4. Make sure 'Play sound for notifications' is ON")
        print("  You should have heard a test sound just now.")

    if IS_WINDOWS:
        print("\n--- Windows notification setup ---")
        print("  For richer notifications, install BurntToast:")
        print("  powershell: Install-Module -Name BurntToast")

    print("\n--- What cc blocks (safety) ---")
    print("  rm -rf           (recursive directory deletion)")
    print("  git push --force (overwriting remote git history)")
    print("  git push -f      (same as above)")
    print("  Everything else runs without prompts.\n")


if __name__ == "__main__":
    setup()
