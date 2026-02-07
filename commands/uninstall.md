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

### Step 2.5: Delete LANGUAGE.md

Delete `~/.claude/LANGUAGE.md` if it exists:

```bash
rm -f ~/.claude/LANGUAGE.md
```

This file was created by `/gg:setup` and is specific to the good-game plugin.

### Step 2.7: Delete .gg/ Configuration

Delete the `.gg/` configuration directory if it exists:

```bash
rm -rf {{PROJECT_ROOT}}/.gg
```

Also remove the `.gg/` entry from `.gitignore` if it was added by setup:

```bash
if [ -f "{{PROJECT_ROOT}}/.gitignore" ]; then
  grep -v '^\.gg/$' "{{PROJECT_ROOT}}/.gitignore" > "{{PROJECT_ROOT}}/.gitignore.tmp" && mv "{{PROJECT_ROOT}}/.gitignore.tmp" "{{PROJECT_ROOT}}/.gitignore"
fi
```

### Step 3: Completion Message

```
**GG -- Uninstall Complete**

good-game plugin cleanup is complete.

**Restored/deleted items:**

- ~/.claude/CLAUDE.md: {Restored (from backup) / Deleted / Unchanged}
- ~/.claude/LANGUAGE.md: Deleted (if existed)
- {{PROJECT_ROOT}}/.gg/: Deleted (if existed)

**Next steps:**
1. Disable the plugin:
   /plugin disable good-game

2. (Optional) Fully remove the plugin:
   /plugin uninstall good-game

3. Restart your session.
```
