---
name: handoff
description: Save where we are so a new chat can continue. Use when the user types "handoff", or says the chat is too long or they are stopping for now.
---
<!-- starter-pack -->

# Handoff

Write a short note so a new chat can continue this work. The note is private: it must never go on GitHub, because the project may be a public website.

1. Look at what we did in this chat. If this folder uses git, also run `git status --short` and `git log --oneline -5`.
2. If `HANDOFF.md` already exists in this folder, read it first.
3. Write `HANDOFF.md` in the main folder of this project. Replace the old note. Use simple English and short lines:

```markdown
# Handoff - [today's date]

## What we are building
[1-2 sentences]

## What is done
- [each finished thing, with the file name]

## What is not working yet
- [each problem, what we tried, and the best idea to fix it]

## Next steps
1. [first thing to do]
2. [second thing]

## Important files
- [file] - [what it is for]
```

4. Keep it off GitHub. If this folder uses git:
   - Make sure `.gitignore` in the main folder has a line `HANDOFF.md` (create the file or add the line if missing).
   - If `git ls-files HANDOFF.md` prints anything, run `git rm --cached HANDOFF.md` so git stops sharing it (the file stays on the computer).

5. Then tell the user, in the language they write in:
"Saved. Now type /clear to start a fresh chat. Then type: read the handoff"
