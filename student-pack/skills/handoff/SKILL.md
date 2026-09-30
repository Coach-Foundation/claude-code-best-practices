---
name: handoff
description: Save where we are so a new chat can continue. Use when the user types "handoff", or says the chat is too long or they are stopping for now.
---
<!-- starter-pack -->

# Handoff

Write a short note so a new chat can continue this work.

1. Look at what we did in this chat. If this folder uses git, also run `git status --short` and `git log --oneline -5`.
2. If `docs/SESSION_HANDOFF.md` already exists, read it first.
3. Write `docs/SESSION_HANDOFF.md` in this folder (make the `docs` folder if needed). Replace the old note. Use simple English and short lines:

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

4. Then tell the user, in the language they write in:
"Saved. Now type /clear to start a fresh chat. Then type: read the handoff"
