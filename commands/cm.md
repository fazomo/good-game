---
description: "Commit current changes as logical units"
---

Commit the current work as separate commits grouped by logical units.

## Steps

1. **Check current changes**
   - Run `git status` to see staged/unstaged changes
   - Run `git diff` to understand each file's changes

2. **Group changes into logical units**
   - Group related changes together
   - Each group should form a complete feature/fix unit
   - Example groups: feature addition, bug fix, refactoring, documentation update

3. **Commit each unit sequentially**
   - Start with the most critical changes
   - For each logical unit:
     - `git add [related files]`
     - Write a conventional commit message
     - `git commit -m "type(scope): description"`
   - Commit types: feat, fix, refactor, docs, style, test, chore

4. **Verify commits**
   - Run `git log --oneline -10` to review commit history
   - Run `git status` to check for remaining changes

## Guidelines

- Each commit must be independently meaningful
- Unrelated changes must be in separate commits
