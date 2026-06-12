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
- The end goal must always be the first section in STATUS.md. Every session should move toward it. If a task doesn't serve the end goal, flag it.
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
            "command": "npx -y ccstatusline@2",
            "padding": 0
        }
        # No "model" pin: let each user keep their account default. The old
        # "sonnet" alias form is outdated; use full model IDs if pinning.
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

HOOK_PRE_COMMIT = r"""#!/bin/bash
# PreToolUse hook (git commit): show staged files + git status to the model.
# Plain stdout from a PreToolUse hook does NOT reach the model - it must be
# JSON with hookSpecificOutput.additionalContext.
git rev-parse --git-dir > /dev/null 2>&1 || exit 0
command -v python3 >/dev/null 2>&1 || exit 0
exec python3 -c '
import json, subprocess

def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""

staged = run(["git", "diff", "--staged", "--name-only"])
status = run(["git", "status", "--short"])
ctx = "=== Staged files ===\n" + staged + "\n\n=== Git status ===\n" + status
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": ctx}}))
'
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
STARTUP_MSG="$STARTUP_MSG Invoke the startup skill now (Skill tool, skill=\\"startup\\") to load project lessons and list relevant skills."
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
description: Run at the start of every new session. Loads project lessons and lists relevant skills.
---

# Session Startup

The hook has already handled git repo creation and STATUS.md. Your job here is two things:

## Step 1: Load Project Lessons

If `tasks/lessons.md` exists in the current project root, read it silently and apply all rules before proceeding.

## Step 2: Relevant Skills

From the available skills list, pick 3-5 most relevant to this project and list them:
`- skill-name: one line on what it does`

## Step 3: Summary

One line: `Session ready | lessons: [loaded N rules / none]`

Note: context usage is shown in the status line. If it climbs above ~60%, the user types `handoff` to save the session. Do not schedule reminder wakeups - they re-read the whole conversation at cold-cache prices.
"""

SKILL_UPDATE_GITHUB = """---
name: update-github
description: Update all project docs substantively, commit, push, and write a session handoff. Use when the user says "update github". For "deploy", run this first, then the deployment.
---

# Update GitHub

If the project CLAUDE.md defines "update github" differently, follow that instead.

Steps in order:

1. If `docs/SESSION_HANDOFF.md` exists, read it first - it captures prior session work that must be reflected in docs and the commit message.
2. Scan ALL .md files in the project (root, context/, docs/, docs/adr/, anywhere) - do not use a fixed list, find everything that exists. For each file: read its current content, cross-reference against actual session work (git diff + conversation), and make substantive updates (new entries, revised statuses, updated roadmap items, new insights, current metrics). Cosmetic edits or date-only changes are not enough.
3. Run `git status` and `git diff --stat HEAD` to confirm what changed.
4. Commit with a thorough message (type(scope): summary, then WHY, then all changes) covering work from both the current and prior session if a handoff existed.
5. `git push origin HEAD`.
6. Write `docs/SESSION_HANDOFF.md` capturing: what we were doing, what was completed, current state, open bugs, next steps in order, key files changed, decisions made, warnings.
"""

SKILL_PROJECT_DOCS = """---
name: project-docs
description: Project documentation system - creates and maintains ROADMAP.md, METRICS.md, EXPERIMENTS.md, context/, docs/adr/, docs/research/. Use at session start when STATUS.md exists but ROADMAP.md does not, or whenever creating or structuring project docs.
---

# Project Documentation System

If STATUS.md exists and ROADMAP.md does not, create ROADMAP.md, METRICS.md, and `context/` immediately - before any other work.

## ROADMAP.md
Outcome-focused, not a feature list. Sections: End Goal (one sentence), Now, Next, Later, Completed, Risks.
- Now/Next/Later: outcomes, not tasks
- Risks table: Risk | Likelihood (1-5) | Impact (1-5) | Mitigation - keep to 3-5 risks max
Update after completing any milestone or shifting direction.

## METRICS.md
How we measure success. Table: Metric | Baseline | Target | Current | Last Updated.
Update at each milestone checkpoint.

## EXPERIMENTS.md
For AI/ML projects and product experiments. Prevents repeating failed experiments.
Each entry: Date, Hypothesis, Method, Result, Conclusion, Next Step.
Skip for pure infrastructure/refactoring work.

## context/ directory
AI-optimized snapshot for fast session restoration. Update after every logical milestone.
- `context/state.md` - current phase, immediate next action, recent changes, blockers
- `context/schema.md` - data structures, interfaces, API contracts, environment variables
- `context/decisions.md` - tactical/operational decisions (tooling, process, config) + one-line reasoning
- `context/insights.md` - discoveries, gotchas, non-obvious learnings

Note: `context/decisions.md` is for operational decisions. Technology/architecture choices (framework, database, irreversible patterns) belong in `docs/adr/` instead. Do not duplicate entries between the two.

## docs/adr/ (Architecture Decision Records)
One file per architectural decision: `docs/adr/NNN-title.md`
Fields: Status, Context, Decision, Consequences, Alternatives Considered.
Append-only - never edit past ADRs, write a new one to supersede.
Create when: choosing a framework, database, architecture pattern, or any hard-to-reverse decision.

## docs/research/
Save reference material, papers, and external docs here before reading so they are available next session. Name files: `YYYY-MM-DD-[topic].md`. Keep a one-line description at the top of each file.
"""

SKILL_SAVE_TRANSCRIPTION = """---
name: save-transcription
description: Save any provided audio, video, Zoom call, voice memo, or other recording/transcript as a file in the current project. Use automatically whenever the user provides a transcript or recording content.
---

# Save Transcription

- Save to `docs/transcriptions/YYYY-MM-DD-[source-or-topic].md` (e.g., `docs/transcriptions/2026-04-15-zoom-call.md`).
- Create the `docs/transcriptions/` directory if it does not exist.
- Include metadata at the top: date, source type, participants (if known), topic/title.
- Do this automatically without being asked.
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
# Stop hook: require a self-review pass only when code was written or edited
# since the last real user prompt. Pure Q&A turns stop silently (zero cost).
# Hook input arrives as JSON on stdin; the transcript at transcript_path is JSONL.
command -v python3 >/dev/null 2>&1 || exit 0
exec python3 -c '
import json, sys

try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)

if d.get("stop_hook_active"):
    sys.exit(0)

path = d.get("transcript_path") or ""
EDIT_TOOLS = ("Write", "Edit", "NotebookEdit")
edited = False
try:
    with open(path) as f:
        for line in f:
            try:
                entry = json.loads(line)
            except Exception:
                continue
            message = entry.get("message") or {}
            content = message.get("content")
            if entry.get("type") == "user":
                # A genuine user prompt (string content, or blocks with no
                # tool_result) resets the flag; tool results do not.
                if isinstance(content, str):
                    edited = False
                elif isinstance(content, list) and not any(
                    isinstance(b, dict) and b.get("type") == "tool_result" for b in content
                ):
                    edited = False
                continue
            if not isinstance(content, list):
                continue
            if any(
                isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") in EDIT_TOOLS
                for b in content
            ):
                edited = True
except Exception:
    sys.exit(0)

if edited:
    reason = (
        "Code was written or modified this turn. Before stopping, complete the 3-pass self-review: "
        "(1) Verification: run the relevant tests/checks and confirm they pass. "
        "(2) Adversarial review: which assumptions did you not verify? How could this fail? "
        "(3) Completeness: re-read the original request - was everything done? "
        "Fix any issues found, then stop."
    )
    print(json.dumps({"decision": "block", "reason": reason}))
'
"""


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

    # Remove retired afk/context-reminder machinery from previous versions.
    # The 15-min reminder loop was a token sink: each wakeup re-read the whole
    # conversation at cold-cache prices. The status line shows context % instead.
    legacy_afk = os.path.join(HOOKS_DIR, "afk-resume.sh")
    if os.path.exists(legacy_afk):
        os.remove(legacy_afk)
        print("  [REMOVED] afk-resume.sh (reminder loop retired)")

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
        answer = input("\n  Install grill-me skill? Stress-tests plans before implementation (recommended) [Y/n]: ").strip().lower()
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

    # Trigger notification (Mac only)
    trigger_mac_notification()

    # Done
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)

    print(f"\nPlatform:       {plat_name}")
    print(f"CLAUDE.md:      {os.path.join(CLAUDE_DIR, 'CLAUDE.md')}")
    print(f"settings.json:  {os.path.join(CLAUDE_DIR, 'settings.json')}")
    print(f"Hooks:          {HOOKS_DIR}")

    print("\n--- Token optimization (auto-configured) ---")
    print("  MAX_THINKING_TOKENS=10000     (caps the extended-thinking budget)")
    print("  DISABLE_AUTO_COMPACT=true     (prefer session handoff files over autocompact)")
    print("  Stop hook                      (self-review pass when code was edited)")

    print("\n--- How to use ---")
    print("  ccx             Start Claude Code (zero prompts, deny-rule guardrails)")
    print("  ccx --resume    Resume your last session")
    print("  claude          Same thing (settings.json sets the permission mode)")

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

    print("\n--- Safety guardrails (permissions.deny in settings.json) ---")
    print("  rm -rf / rm -fr / sudo rm   (recursive deletion)")
    print("  git push --force / -f       (overwriting remote history)")
    print("  Read .env / .env.*          (secrets stay out of context)")
    print("  These bind even in bypassPermissions mode (verified live).")
    print("  Everything else runs without prompts.\n")


if __name__ == "__main__":
    setup()
