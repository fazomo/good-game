---
description: "Remove plugin traces and restore CLAUDE.md"
---

# /gg:uninstall - Plugin Uninstall

Cleans up traces of the good-game plugin installation.

## Usage

```
/gg:uninstall
```

## What This Does

1. Restores ~/.claude/CLAUDE.md from backup or deletes it
2. Provides guidance for disabling the plugin

## Workflow

### Step 1: Confirmation

Use AskUserQuestion to confirm with the user.

```typescript
AskUserQuestion({
  questions: [
    {
      question:
        "Remove the good-game plugin? This will restore or delete ~/.claude/CLAUDE.md.",
      header: "Uninstall Confirmation",
      options: ["Yes, remove it", "No, cancel"],
      multiSelect: false,
    },
  ],
});
```

If "No" is selected, terminate immediately.

### Step 2: Restore CLAUDE.md

1. Check if `~/.claude/CLAUDE.md.backup.*` files exist:

```bash
ls -t ~/.claude/CLAUDE.md.backup.* 2>/dev/null | head -1
```

2. If a backup exists:
   - Restore the most recent backup to `~/.claude/CLAUDE.md`
   - Delete all backup files after restore

```bash
# Find most recent backup
LATEST_BACKUP=$(ls -t ~/.claude/CLAUDE.md.backup.* 2>/dev/null | head -1)

# Restore
cp "$LATEST_BACKUP" ~/.claude/CLAUDE.md

# Clean up backups
rm ~/.claude/CLAUDE.md.backup.*
```

3. If no backup exists:
   - Check if the current CLAUDE.md was installed by good-game (content contains "GG Orchestrator")
   - If so, delete it
   - Otherwise, leave it untouched

### Step 3: Completion Message

```
**GG -- Uninstall Complete**

good-game plugin cleanup is complete.

**Restored/deleted items:**
- ~/.claude/CLAUDE.md: {Restored (from backup) / Deleted / Unchanged}

**Next steps:**
1. Disable the plugin:
   /plugin disable good-game

2. (Optional) Fully remove the plugin:
   /plugin uninstall good-game

3. Restart your session.
```
