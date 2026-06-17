---
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

Note: context usage is shown in the status line. Quality degrades past ~40% — if it reaches 40%, the user types `handoff` immediately. Do not schedule reminder wakeups - they re-read the whole conversation at cold-cache prices.
