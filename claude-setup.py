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
- **grill-me:** When the user has a plan and is about to implement something non-trivial, if grill-me is not in the available skills list, suggest they install it: create `~/.claude/skills/grill-me/skill.md` or re-run `claude-setup.py`.
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
- The end goal must always be the first section in STATUS.md. Every session should move toward it. If a task doesn't serve the end goal, flag it.
- Update project documentation .md files after completing each logical milestone or at natural breakpoints.

## Self-Improvement Loop
- After ANY correction from the user, append to `tasks/lessons.md` in the project root:
  `- [YYYY-MM-DD] RULE: <what to do or avoid> | WHY: <reason given>`
- At session start, if `tasks/lessons.md` exists, read it silently and apply all rules for the session
- Never delete entries - this file compounds over time

## Project Documentation

For any project under ~/Documents/dev/: if STATUS.md exists and ROADMAP.md does not, create ROADMAP.md, METRICS.md, and `context/` immediately at session start - before any other work. Do not wait to be asked.

### ROADMAP.md
Outcome-focused, not a feature list. Sections: End Goal (one sentence), Now, Next, Later, Completed, Risks.
- Now/Next/Later: outcomes, not tasks
- Risks table: Risk | Likelihood (1-5) | Impact (1-5) | Mitigation - keep to 3-5 risks max
Update after completing any milestone or shifting direction.

### METRICS.md
How we measure success. Table: Metric | Baseline | Target | Current | Last Updated.
Update at each milestone checkpoint.

### EXPERIMENTS.md
For AI/ML projects and product experiments. Prevents repeating failed experiments.
Each entry: Date, Hypothesis, Method, Result, Conclusion, Next Step.
Skip for pure infrastructure/refactoring work.

### context/ directory
AI-optimized snapshot for fast session restoration. Update after every logical milestone.
- `context/state.md` - current phase, immediate next action, recent changes, blockers
- `context/schema.md` - data structures, interfaces, API contracts, environment variables
- `context/decisions.md` - tactical/operational decisions (tooling, process, config) + one-line reasoning
- `context/insights.md` - discoveries, gotchas, non-obvious learnings

Note: `context/decisions.md` is for operational decisions. Technology/architecture choices (framework, database, irreversible patterns) belong in `docs/adr/` instead. Do not duplicate entries between the two.

### docs/adr/ (Architecture Decision Records)
One file per architectural decision: `docs/adr/NNN-title.md`
Fields: Status, Context, Decision, Consequences, Alternatives Considered.
Append-only - never edit past ADRs, write a new one to supersede.
Create when: choosing a framework, database, architecture pattern, or any hard-to-reverse decision.

### docs/research/
Save reference material, papers, and external docs here before reading so they are available next session. Name files: `YYYY-MM-DD-[topic].md`. Keep a one-line description at the top of each file.

## Transcriptions
- When the user provides any audio, video, Zoom call, voice memo, or other recording/transcript, always save it as a file inside the current project directory.
- Save to `docs/transcriptions/YYYY-MM-DD-[source-or-topic].md` (e.g., `docs/transcriptions/2026-04-15-zoom-call.md`).
- Create the `docs/transcriptions/` directory if it does not exist.
- Include metadata at the top: date, source type, participants (if known), topic/title.
- Do this automatically without being asked.

## Context Window Monitoring
- Do NOT auto-trigger handoff warnings. The user monitors context % in the status bar and will type "handoff" when ready.

### When I type "handoff" or "handoff <project>"
Invoke the handoff skill (Skill tool, skill="handoff"). If a project name is given (e.g. "handoff predmarkets", "handoff ai-caller" - any folder under ~/Documents/dev/), the skill writes to `~/Documents/dev/<project>/docs/SESSION_HANDOFF.md` using git state from that directory. If no project name, writes to the current project. Pasting the last ~50 lines of a filled-up session helps capture mid-debug state, but is not required - the skill can reconstruct from git diff + log alone.

### When I type "ooc" or "running out of context"
Context is nearly full. Invoke the handoff skill (Skill tool, skill="handoff") for the current project, then reply with exactly: "Session saved. Open a new Claude Code session in this directory and type `read handoff` to resume."

### On Every Session Start
Invoke the startup skill immediately (Skill tool, skill="startup") as your very first action, before responding to anything. The hook will have already loaded SESSION_HANDOFF.md and STATUS.md as context - do not re-read them.

## Git
- Run `git status` and `git diff --staged` before every commit.
- Before committing, scan ALL .md files in the project (root, context/, docs/, docs/adr/, anywhere) and update every one that is stale - do not use a fixed list, check everything that exists.
- After completing a logical unit of work, mention once that it is a good time to commit. Do not repeat.
- When I say "update github": check the project CLAUDE.md first - some projects define this differently. Otherwise follow these steps in order: (0) if `docs/SESSION_HANDOFF.md` exists, read it - it captures prior session work that must be included; (1) scan ALL .md files in the project and update every one that is stale; (2) run `git status` and `git diff --stat HEAD`; (3) commit with a thorough message covering work from both the current and prior session if a handoff existed; (4) `git push origin HEAD`; (5) invoke the handoff skill to write `docs/SESSION_HANDOFF.md`.
- When I say "deploy": do everything "update github" does first (read handoff, update all docs, commit, push, write handoff), then run the deployment. Use the `deploy` skill for the deployment step unless the project CLAUDE.md defines a project-specific deploy process.
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

## Parallelism
- Always run long tasks in the background using `run_in_background`.
- Use subagents for 2+ independent tasks. Never do sequentially what can be done concurrently.
- Minimize manual work for the user. If you can do it via CLI/API/SSH/scripting, do it.

## Long-Running Processes
- Any process expected to take >30 seconds: redirect output with `cmd > output.log 2>&1 &` then immediately tail with `tail -f output.log` or Monitor the log file.
- Never run a long job silently and wait - failures must surface within the first few output lines, not at the end of a wasted run.
- After starting: check the log within 60s to confirm it is running correctly. If it has errored or stalled, fix it, restart, and check again after 60s.
- Only once confirmed healthy do you switch to 5-minute (270s) wakeup checks until the job completes.

## Self-Review Before Claiming Done
Before saying any task is "done", verify: (1) tests pass, (2) the feature actually works, (3) you did everything asked, (4) no half-modified files remain. If any check fails, fix it before claiming done.

## Superpowers
- Always use superpowers skills wherever applicable. Never skip them because "it's simple."
- When executing plans: always use `superpowers:subagent-driven-development`. Never ask which approach.
- Before claiming done: use `superpowers:verification-before-completion`.

## Critical Rules
- Never make assumptions about account balances, API limits, send volumes, or resource constraints. Always ask or read from config/env.
- When presenting data/metrics, cross-verify against raw source data. Do not interpolate or estimate. Show exact raw data supporting each number.

## Phase Checkpoints
- Before starting each new phase of a multi-step task, run a full checkpoint: tests, clean git, 3-line status summary. Do not proceed until green.
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
# Session startup: initialize project state in bash, then inject context Claude can read

HOME_DEV="$HOME/Documents/dev"
CWD=$(pwd)
CONTEXT=""
REPO_CREATED=""

# Git repo check - only in ~/Documents/dev/*
if [[ "$CWD" == "$HOME_DEV"/* ]] && ! git rev-parse --git-dir > /dev/null 2>&1; then
    FOLDER=$(basename "$CWD")
    if [ ! -f .gitignore ]; then
        printf 'node_modules/\\n.env\\n.env.*\\n__pycache__/\\n*.pyc\\n.DS_Store\\n.venv/\\nvenv/\\ndist/\\nbuild/\\n*.log\\n' > .gitignore
    fi
    git init -q && git add . && git commit -q -m "chore: initial commit" 2>/dev/null
    if gh repo create "$FOLDER" --private --source=. --push --quiet 2>/dev/null; then
        REPO_CREATED="GitHub repo '$FOLDER' created and pushed."
    else
        REPO_CREATED="git init done but gh repo create failed (name collision or gh not authed)."
    fi
fi

# STATUS.md check - only in ~/Documents/dev/*
if [[ "$CWD" == "$HOME_DEV"/* ]] && [ ! -f STATUS.md ]; then
    cat > STATUS.md << 'STATUSMD'
# Project Status

## End Goal
[describe the end goal here]

## Done
- nothing yet

## In Progress
- nothing yet

## Next Steps
- nothing yet

## Blockers / Decisions
- none
STATUSMD
fi

# Load context files
if [ -f docs/SESSION_HANDOFF.md ]; then
    CONTEXT="$CONTEXT\\n=== SESSION_HANDOFF.md ===\\n$(cat docs/SESSION_HANDOFF.md)"
fi

if [ -f STATUS.md ]; then
    CONTEXT="$CONTEXT\\n=== STATUS.md ===\\n$(cat STATUS.md)"
fi

# Load context directory files for AI session restoration
if [ -f context/state.md ]; then
    CONTEXT="$CONTEXT\\n=== context/state.md ===\\n$(cat context/state.md)"
fi
if [ -f context/schema.md ]; then
    CONTEXT="$CONTEXT\\n=== context/schema.md ===\\n$(cat context/schema.md)"
fi

# Startup instruction goes in additionalContext - this is what Claude actually reads
STARTUP_MSG="\\n[SESSION START]"
[ -n "$REPO_CREATED" ] && STARTUP_MSG="$STARTUP_MSG $REPO_CREATED"
STARTUP_MSG="$STARTUP_MSG Invoke the startup skill now (Skill tool, skill=\\"startup\\") to list relevant skills and start the context reminder loop."
CONTEXT="$CONTEXT$STARTUP_MSG"

PYTHON=$(command -v python3 || command -v python) 2>/dev/null
[ -z "$PYTHON" ] && exit 0

echo -e "$CONTEXT" | $PYTHON -c "
import json, sys
content = sys.stdin.read()
print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart', 'additionalContext': content}}))
"
"""

SKILL_STARTUP = """---
name: startup
description: Run at the start of every new session. Lists relevant skills and starts the 15-min context reminder loop.
---

# Session Startup

The hook has already handled git repo creation and STATUS.md. Your job here is three things:

## Step 0: Load Project Lessons

If `tasks/lessons.md` exists in the current project root, read it silently and apply all rules before proceeding.

## Step 1: Relevant Skills

From the available skills list, pick 3-5 most relevant to this project and list them:
`- skill-name: one line on what it does`

## Step 2: Context Reminder Loop

Call ScheduleWakeup with:
- delaySeconds: 900
- reason: "15-min context check reminder"
- prompt: "CONTEXT REMINDER: Tell the user this message verbatim: '**Context check:** If you are above 60%, type handoff to save your session before it is lost.' After sending that message, call ScheduleWakeup again with delaySeconds=900, reason='15-min context check reminder', and this same prompt text to continue the loop."

## Step 3: Summary

One line: `Session ready | lessons: [loaded N rules / none] | reminder: started`
"""

SKILL_CONTEXT_REMINDER = """---
name: context-reminder
description: Recurring 15-min context check reminder. Notifies user to check context percentage, then reschedules itself to keep the loop running.
---

# Context Reminder

Tell the user this message (make it visible, not buried):

> **Context check:** If you're above 60%, type `handoff` to save your session before it's lost.

Then immediately call ScheduleWakeup with:
- delaySeconds: 900
- reason: "15-min context check reminder"
- prompt: "CONTEXT REMINDER: Tell the user this message verbatim: '**Context check:** If you are above 60%, type handoff to save your session before it is lost.' After sending that message, call ScheduleWakeup again with delaySeconds=900, reason='15-min context check reminder', and this same prompt text to continue the loop."

This keeps the loop running every 15 minutes.
"""

SKILL_GRILL_ME = """---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

Interview me relentlessly about every aspect of this plan until
we reach a shared understanding. Walk down each branch of the design
tree resolving dependencies between decisions one by one.

If a question can be answered by exploring the codebase, explore
the codebase instead.

For each question, provide your recommended answer.
"""

HOOK_PRE_COMPACT = """#!/bin/bash
# Auto-save handoff before context compaction
echo '{"systemMessage":"Context compaction is about to occur. Before compacting, immediately run the handoff skill and save docs/SESSION_HANDOFF.md for this project. Do this now - write the full handoff file first, then compaction can proceed."}'
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

    # Write skills
    print("\n4b. Installing skills...")
    SKILLS_DIR = os.path.join(CLAUDE_DIR, "skills")
    startup_dir = os.path.join(SKILLS_DIR, "startup")
    context_reminder_dir = os.path.join(SKILLS_DIR, "context-reminder")
    os.makedirs(startup_dir, exist_ok=True)
    os.makedirs(context_reminder_dir, exist_ok=True)
    write_file(os.path.join(startup_dir, "SKILL.md"), SKILL_STARTUP)
    write_file(os.path.join(context_reminder_dir, "SKILL.md"), SKILL_CONTEXT_REMINDER)

    # Optional: grill-me skill
    grill_me_dir = os.path.join(SKILLS_DIR, "grill-me")
    grill_me_path = os.path.join(grill_me_dir, "skill.md")
    if os.path.exists(grill_me_path):
        print("  [SKIP] grill-me skill already installed")
    else:
        answer = input("\n  Install grill-me skill? Stress-tests plans before implementation (recommended) [Y/n]: ").strip().lower()
        if answer in ("", "y", "yes"):
            os.makedirs(grill_me_dir, exist_ok=True)
            write_file(grill_me_path, SKILL_GRILL_ME)
            print("  [OK] grill-me skill installed")
        else:
            print("  [SKIP] grill-me skill skipped")

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
