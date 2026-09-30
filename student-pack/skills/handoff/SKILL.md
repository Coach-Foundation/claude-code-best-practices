---
name: handoff
description: Save where we are so a new chat can continue. Use when the user types "handoff", or says the chat is too long or they are stopping for now.
---
<!-- starter-pack -->

# Handoff

Write a short note so a new chat can continue this work. The note is private: it must never go on GitHub, because the project may be a public website.

1. Find the project folder: the folder of the files we worked on in this chat (if we worked on no files, use the current folder). Run `git -C "<that folder>" rev-parse --show-toplevel`. If it prints a path, that path is the project folder. If it fails, the project folder is the folder of the files (or the current folder).
2. Look at what we did in this chat. If the project folder uses git, also run `git status --short` and `git log --oneline -5` there.
3. If `HANDOFF.md` already exists in the project folder, read it first.
4. Write `HANDOFF.md` in the project folder. Replace the old note. Use simple English and short lines:

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

5. Keep it off GitHub, always, even if the folder does not use git yet:
   - Make sure `.gitignore` in the project folder has a line `HANDOFF.md` (create the file or add the line if missing).
   - If the project folder uses git and `git ls-files HANDOFF.md` prints anything, run `git rm --cached HANDOFF.md` so git stops sharing it (the file stays on the computer).

6. Then tell the user, in the language they write in:
"Saved. Now type /clear to start a fresh chat. Then type: read the handoff"
