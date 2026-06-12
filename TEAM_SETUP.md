# Get the Team Claude Code Setup (10 minutes)

**Stop babysitting Claude Code.** This setup makes Claude verify its own work, remember your sessions, and stop asking permission for everything - while guardrails block the genuinely dangerous stuff.

Everything here was audited against official Anthropic docs and stress-tested by 200+ research agents in June 2026. The broken advice got thrown out; only what survived verification ships.

## What changes for you

- **Zero permission prompts.** No more pressing "Yes" 200 times a day. Fifteen deny rules block the dangerous commands (rm -rf, force push, reading your credentials) - everything else just runs.
- **Claude checks its own work.** A Stop hook forces a verify-review-complete pass whenever code was written, before Claude tells you it's done. Fewer "done!" messages that aren't.
- **Your sessions survive.** Handoff files capture state before you run out of context. Open a new session, type `read handoff`, continue where you left off.
- **Structured workflows on demand.** Type "grade this" for rubric-based quality loops, "grill me" to stress-test a plan, "update github" for docs + commit + push + handoff in one command. Plus specialist agents (architect, code-verifier, mechanic) with the right model pre-picked for each job.

## Setup (do these in order)

**Prerequisites:** Claude Code installed, Python 3.

**Step 1 - Run the bootstrapper** (terminal):
```bash
git clone https://github.com/Coach-Foundation/claude-code-best-practices.git
cd claude-code-best-practices
python3 claude-setup.py
```
This installs the optimized CLAUDE.md, settings (permissions + guardrails + hooks), and the `ccx` launcher. Your existing CLAUDE.md and settings.json are backed up with timestamps first - nothing is lost.

**Step 2 - Install the plugin** (inside a Claude Code session - start one with `ccx` or `claude`):
```
/plugin marketplace add Coach-Foundation/claude-code-best-practices
/plugin install ap-optimal-claude@coach-foundation
```
This adds the 13 workflow skills and 3 specialist agents. It touches nothing else in your config, and updates arrive through the plugin manager - you never re-run the installer.

**Step 3 - Verify (30 seconds):**
1. Restart Claude Code. You should see a session-start summary line.
2. Type `/plugin` - ap-optimal-claude should show as installed.
3. Ask Claude: "run this: rm -rf /tmp/guardrail-test" - it should be **blocked** by a permission rule. That's the guardrails working.

Done - react with a checkmark on the Slack message.

## FAQ

**Will this overwrite my personal setup?**
The installer replaces CLAUDE.md and settings.json (timestamped backups are made first - you can restore anything). The plugin overwrites nothing.

**I already had Claude Code working fine.**
You'll keep everything you like and gain the verification hooks, guardrails, and session memory. If something feels wrong, your backups are in `~/.claude/` with timestamps and the plugin uninstalls in one command.

**Windows?**
Run `python claude-setup.py` instead. Everything works (plugin skills, agents, guardrails, settings) EXCEPT the four hook scripts, which are bash - they need WSL or Git Bash to fire. If you're on plain Windows you still get the full plugin + guardrails; the automatic session-context loading and stop-time self-review just won't run. Native Windows hook support is planned for plugin v1.1.

**Something broke / question?**
Post in the Slack thread. Known quirk: if `ccx` is not found after install, add `~/.local/bin` to your PATH (the installer prints the exact line).
