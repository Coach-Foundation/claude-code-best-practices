---
name: update-github
description: Update all project docs substantively, commit, push, and write a session handoff. Use when the user says "update github". For "deploy", run this first, then the deployment.
---

# Update GitHub

If the project CLAUDE.md defines "update github" differently, follow that instead.

Steps in order:

1. If `docs/SESSION_HANDOFF.md` exists, read it first - it captures prior session work that must be reflected in docs and the commit message.
2. Scan ALL .md files in the project (root, context/, docs/, docs/adr/, anywhere) - do not use a fixed list, find everything that exists. For each file: read its current content, cross-reference against actual session work (git diff + conversation), and make substantive updates (new entries, revised statuses, updated roadmap items, new insights, current metrics). Cosmetic edits or date-only changes are not enough.
3. Run `git status` and `git diff --stat HEAD` to confirm what changed.
4. Commit with a thorough message (use the commit-rules skill) covering work from both the current and prior session if a handoff existed.
5. `git push origin HEAD`.
6. Invoke the handoff skill to write `docs/SESSION_HANDOFF.md`.
