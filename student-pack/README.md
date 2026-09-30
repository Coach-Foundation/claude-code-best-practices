# Student starter pack

A small, safe pack for first-time Claude Code users (built for the students of a university Claude Code hackathon). It is a beginner edition of this repo's settings, with everything that could break a setup or burn a Claude Pro plan's limits left out.

## What the student pastes into Claude Code (one line)

Only AFTER the hackathon page's "Set up Claude Code with your own account" step (the switch-to-own-account script) (the installer refuses while the hackathon rules block is still in `~/.claude/CLAUDE.md`):

```
Install my Claude starter pack. Run this command in bash and tell me the result in simple words: curl -fsSL https://raw.githubusercontent.com/Coach-Foundation/claude-code-best-practices/student-v1/student-pack/install.sh | bash
```

To remove it:

```
Remove my Claude starter pack. Run this command in bash and tell me the result in simple words: curl -fsSL https://raw.githubusercontent.com/Coach-Foundation/claude-code-best-practices/student-v1/student-pack/remove.sh | bash
```

## What it installs

| Piece | Why a beginner wants it |
|---|---|
| `handoff` skill | Type `handoff` before a chat gets too long, and Claude saves where you are in `HANDOFF.md` so a fresh chat can continue. The note stays off GitHub (added to `.gitignore`), because student projects are often public websites. |
| `grill-me` skill | Type `grill me` and Claude asks you questions about your idea, one at a time, before building, so you build the right thing. |
| 6 short lines at the end of `~/.claude/CLAUDE.md` | Claude replies in your language, uses simple words, asks before deleting files, and reminds you about handoff. |

## What it never does

- Never touches `settings.json`: no model change, no permission change, no hooks, no plugins, nothing that updates itself.
- Never overwrites a skill the student made (it only replaces files that carry its `<!-- starter-pack -->` tag).
- Downloads everything before changing anything, so a network error leaves the laptop as it was.
- Adds its CLAUDE.md lines between its own markers (`<!-- >>> starter pack >>> -->`), outside the hackathon rules markers, so the switch step and the remove step never touch each other's text.

## Habits card (for the Starter Pack page, not installed)

- `/clear` - start a fresh chat when you start a new task. Type `handoff` first if you want to continue later.
- `/usage` - see how much of your Claude plan you have left.
- When something breaks, copy the whole error message and paste it into Claude.

## Why it is a script and not a Claude prompt

The same file runs on Mac (bash) and Windows (Git Bash, the shell Claude Code already uses there), needs only `curl`, and gives the same result on every laptop. `PACK_BASE` overrides the download location for tests.

## Tests

`python3 scripts/test_student_pack.py` runs `install.sh` and `remove.sh` with `HOME` set to a temp folder and files served from this folder. Covers: fresh install, refusal while hackathon rules are present, keeping existing CLAUDE.md text, second run, keeping a student's own skill, download failure, removal. Not covered automatically: Windows Git Bash, and real Claude Code running the pasted line. Those need the manual test below.

## Release checklist

1. Deploy (`./scripts/deploy.sh`) so `student-pack/` is on the public repo's `main`.
2. Manual test on a Mac and a Windows laptop, each on Claude Pro after the switch step. Paste this test line (same as the student line, but reading from `main` because the tag does not exist yet), restart Claude Code, type `grill me`, then `handoff`:
   `Install my Claude starter pack. Run this command in bash and tell me the result in simple words: curl -fsSL https://raw.githubusercontent.com/Coach-Foundation/claude-code-best-practices/main/student-pack/install.sh | PACK_BASE=https://raw.githubusercontent.com/Coach-Foundation/claude-code-best-practices/main/student-pack bash`
3. Tag the public repo `student-v1` and push the tag. Only then give the line to students.
4. A change after release means a new tag (`student-v2`) and a new line. Never move `student-v1`.
