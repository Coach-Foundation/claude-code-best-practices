---
name: spec
description: Create a structured spec document before implementing any feature. Triggers plan mode and creates tasks/spec-[feature].md.
---

# Spec Workflow

Use when the user says "spec", "/spec", "write a spec for", or "spec out" anything.

## Step 1: Clarify (only if not already clear)

Ask:
- What is the feature or change?
- Who is the user and what problem does it solve?
- Any constraints (technical, time, scope)?

## Step 2: Create `tasks/spec-[feature-slug].md`

```markdown
# Spec: [Feature Name]
**Date:** YYYY-MM-DD
**Status:** Draft

## Problem
[One paragraph: what problem does this solve and for whom?]

## Goals
- [Goal 1]
- [Goal 2]

## Non-Goals (Out of Scope)
- [What we are explicitly NOT doing]

## Requirements
### Must Have
- [ ] [Requirement]
### Nice to Have
- [ ] [Requirement]

## Approach
[2-4 sentences on the technical approach]

## Acceptance Criteria
- [ ] [Testable criterion]
- [ ] [Testable criterion]

## Test Plan
- [ ] [Test case]
- [ ] [Test case]

## Open Questions
- [Question that needs an answer before implementation]
```

## Step 3: Enter plan mode

After writing the spec file, invoke `superpowers:writing-plans` to turn it into an implementation plan.
