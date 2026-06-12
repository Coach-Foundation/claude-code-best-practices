# Get the Team Claude Code Setup (10 minutes)

**Stop babysitting Claude Code.** This setup makes Claude verify its own work, remember your sessions, and stop asking permission for everything - while guardrails block the genuinely dangerous stuff.

Everything here was audited against official Anthropic docs and stress-tested by 200+ research agents in June 2026. The broken advice got thrown out; only what survived verification ships.

## What changes for you

- **Zero permission prompts.** No more pressing "Yes" 200 times a day. Fifteen deny rules block the dangerous commands (rm -rf, force push, reading your credentials) - everything else just runs.
- **Claude checks its own work.** A Stop hook forces a verify-review-complete pass whenever code was written, before Claude tells you it's done. Fewer "done!" messages that aren't.
- **Your sessions survive.** Handoff files capture state before you run out of context. Open a new session, type `read handoff`, continue where you left off.
- **Structured workflows on demand.** Type "grade this" for rubric-based quality loops, "grill me" to stress-test a plan, "update github" for docs + commit + push + handoff in one command. Plus specialist agents (architect, code-verifier, mechanic) with the right model pre-picked for each job.

## Setup - the easy way (no terminal needed)

**Step 1:** Open Claude Code and paste this whole block as a message:

```
Set up my computer with our team's Claude Code configuration. Do this for me:

1. Download the team setup from https://github.com/Coach-Foundation/claude-code-best-practices.git
   into a temporary folder and run claude-setup.py with Python (python3 on Mac,
   python on Windows). It backs up my existing settings automatically and
   installs our team plugin (ap-optimal-claude) by itself. When it finishes,
   give me a one-line summary in plain language.

2. Test the safety net: try to run the command rm -rf /tmp/guardrail-test and
   confirm it gets BLOCKED. Tell me PASS or FAIL in simple words.

3. Then remind me to close and reopen Claude Code so everything loads fresh.

If anything goes wrong, explain it to me simply and tell me exactly what to
post in the team Slack thread.
```

**Step 2:** When Claude says **PASS**, close and reopen Claude Code, then react with a checkmark on the Slack message. Done - you never touch a terminal.

<details>
<summary>Prefer doing it yourself in the terminal? (technical path)</summary>

```bash
git clone https://github.com/Coach-Foundation/claude-code-best-practices.git
cd claude-code-best-practices
python3 claude-setup.py    # python claude-setup.py on Windows
```
The installer registers the team plugin marketplace and installs ap-optimal-claude automatically (via the claude CLI). If that step is skipped because `claude` is not on PATH, run inside a session:
```
/plugin marketplace add Coach-Foundation/claude-code-best-practices
/plugin install ap-optimal-claude@coach-foundation
```
Verify: restart, `/plugin` shows ap-optimal-claude installed, and asking Claude to run `rm -rf /tmp/guardrail-test` gets blocked. Your previous CLAUDE.md and settings.json are backed up with timestamps before anything is replaced.
</details>

## FAQ

**Will this overwrite my personal setup?**
The installer replaces CLAUDE.md and settings.json (timestamped backups are made first - you can restore anything). The plugin overwrites nothing.

**I already had Claude Code working fine.**
You'll keep everything you like and gain the verification hooks, guardrails, and session memory. If something feels wrong, your backups are in `~/.claude/` with timestamps and the plugin uninstalls in one command.

**Windows?**
Run `python claude-setup.py` instead. Everything works (plugin skills, agents, guardrails, settings) EXCEPT the four hook scripts, which are bash - they need WSL or Git Bash to fire. If you're on plain Windows you still get the full plugin + guardrails; the automatic session-context loading and stop-time self-review just won't run. Native Windows hook support is planned for plugin v1.1.

**Something broke / question?**
Post in the Slack thread. Known quirk: if `ccx` is not found after install, add `~/.local/bin` to your PATH (the installer prints the exact line).
