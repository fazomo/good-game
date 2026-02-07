---
description: "Run initial plugin setup (install CLAUDE.md, select language, configure AI backends)"
---

# /gg:setup - Plugin Setup

Performs initial setup for the good-game plugin.

## Usage

```
/gg:setup
```

## What This Does

1. Installs the CLAUDE.md orchestrator protocol to `~/.claude/CLAUDE.md`
2. Selects response language preference
3. Selects external AI backend (Gemini, Codex) usage
4. Provides security notice about the auto-approve hook

## Workflow

### Step 1: Welcome & Explanation

Display the following message to the user:

```
**GG -- Plugin Setup**

Starting good-game plugin setup.

This setup will:

- Install the orchestrator protocol to ~/.claude/CLAUDE.md
- Back up any existing CLAUDE.md
- Let you choose your preferred response language
- Guide you through external AI configuration

After setup, restart your session to activate the protocol.
```

### Step 2: Language Selection

Use AskUserQuestion to select the response language.

```typescript
AskUserQuestion({
  questions: [
    {
      question: "Which language should the orchestrator respond in?",
      header: "Response Language",
      options: [
        "English",
        "Korean",
        "Japanese",
        "Chinese (Simplified)",
        "Chinese (Traditional)",
        "Other (specify in chat)",
      ],
      multiSelect: false,
    },
  ],
});
```

Store the selected language for use in Step 2.5 (LANGUAGE.md creation).

**"Other" handling:** If the user selects "Other (specify in chat)", use a follow-up AskUserQuestion with a free-form text prompt:

```typescript
AskUserQuestion({
  questions: [
    {
      question:
        "Please type the language you would like the orchestrator to respond in (e.g., Spanish, Portuguese, German):",
      header: "Custom Language",
      options: [],
      multiSelect: false,
    },
  ],
});
```

Use whatever the user types as the language value. If the user provides a blank or unrecognizable response, default to "English" and inform the user.

### Step 2.5: Create LANGUAGE.md

Write the selected language to `~/.claude/LANGUAGE.md` as a plain text file containing only the language name on a single line.

```bash
# Create the language config file
echo "{selected language}" > ~/.claude/LANGUAGE.md
```

Example: if the user selected "Korean", the file contains exactly `Korean` (no newline prefix, no markdown formatting, just the language name).

This file is the Single Source of Truth for language configuration. Both the orchestrator (via CLAUDE.md) and all subagents (via their agent .md prompts) read this file at runtime.

### Step 3: External AI Selection

Use AskUserQuestion to select external AI backends.

First run `which gemini` and `which codex` to check CLI availability.

```typescript
AskUserQuestion({
  questions: [
    {
      question:
        "Which AI backends would you like to use? (Default: Claude only)",
      header: "AI Backend",
      options: [
        "Claude only (no external AI, default)",
        "Claude + Gemini (Gemini Strategist uses Gemini for brainstorm)",
        "Claude + Codex (Codex Strategist uses Codex for brainstorm, codex-auditor uses Codex for audit)",
        "Claude + Gemini + Codex (full stack)",
      ],
      multiSelect: false,
    },
  ],
});
```

**NOTE:** The user's selection is informational only. Actual external AI usage is determined at runtime by agents checking `which gemini` / `which codex`. Even if the user selects "Claude only", installing the gemini CLI later will auto-enable it.

### Step 4: Auto-Approve Security Notice

Use AskUserQuestion to inform about the auto-approve hook.

```typescript
AskUserQuestion({
  questions: [
    {
      question:
        "Security notice about the auto-approve hook: This hook automatically approves Write/Edit/MultiEdit tool calls and mkdir Bash commands without user confirmation. This lets the orchestrator delegate file modifications to the Implementor agent without manual approval each time. For security-sensitive environments, disabling is recommended. Enable auto-approve?",
      header: "Security",
      options: [
        "Enable (default, convenience first)",
        "Disable (manual approval each time, security first)",
      ],
      multiSelect: false,
    },
  ],
});
```

**If "Disable" is selected:** Display the following guidance:

```
Auto-approve disable guidance:

The current Claude Code plugin system does not support selectively disabling
individual hooks within a plugin's hooks.json.

Available alternatives:

1. (Recommended) Control via Claude Code permissions:
   claude /permissions deny Write
   claude /permissions deny Edit
   -> Even if the auto-approve hook returns "allow", Claude Code performs a final permissions check.

2. Disable plugin and copy manually:
   /plugin disable good-game
   -> Then manually copy needed skills and agent files to local directories.
   -> Skills: copy to ~/.claude/skills/
   -> Agents: copy to ~/.claude/agents/

3. Use in manual approval mode:
   -> Even with auto-approve enabled, a confirmation popup appears for every tool call.
   -> Auto-approve only auto-approves Write/Edit/MultiEdit and mkdir.
   -> All other Bash commands still require manual approval.
```

### Step 5: Backup Existing CLAUDE.md

Check if `~/.claude/CLAUDE.md` exists:

```bash
ls -la ~/.claude/CLAUDE.md
```

If it exists, create a timestamped backup:

```bash
cp ~/.claude/CLAUDE.md ~/.claude/CLAUDE.md.backup.$(date +%Y%m%d-%H%M%S)
```

### Step 6: Install CLAUDE.md

**Path resolution:** `${CLAUDE_PLUGIN_ROOT}` is auto-substituted in hooks.json but not available in skill prompts. Instead, use Glob to dynamically find the plugin cache path.

1. Use Glob to search for `**/good-game/templates/CLAUDE.md` and find the actual path in the plugin cache
2. Read the file at that path
3. Replace `{PLUGIN_NAME}` with `gg` in the file content (global text replace)
4. Write the substituted content to `~/.claude/CLAUDE.md`

Note: The template no longer contains `{RESPONSE_LANGUAGE}`. Language configuration is handled via `~/.claude/LANGUAGE.md` (created in Step 2.5), which the orchestrator reads at runtime.

```
Glob("**/good-game/templates/CLAUDE.md") -> get actual path
Read: {actual path}/templates/CLAUDE.md
-> Replace {PLUGIN_NAME} -> gg
-> Write: ~/.claude/CLAUDE.md
```

### Step 7: Completion Message

```
**GG -- Setup Complete**

good-game plugin setup is complete.

**Installed items:**
- ~/.claude/CLAUDE.md (orchestrator protocol)
  (Previous file backed up: ~/.claude/CLAUDE.md.backup.{timestamp})
- ~/.claude/LANGUAGE.md (language configuration)

**Response Language:** {selected language}
**External AI:** {user's selection}
**auto-approve:** {enable/disable guidance}

**Available skills:**
- /gg:explore    -- Multi-angle codebase reconnaissance
- /gg:brainstorm -- 3-strategist parallel brainstorming (Opus + Gemini + Codex)
- /gg:blueprint  -- Precision implementation planning
- /gg:execute    -- Code implementation
- /gg:audit      -- 3-auditor parallel cross-review (Opus + Gemini + Codex)
- /gg:handoff-be -- BE modification request document
- /gg:handoff-fe -- FE handoff document
- /gg:cm         -- Logical unit commits

**Next step:** Restart your session. (Cmd+Shift+P > "Reload Window" or restart terminal)
The protocol activates automatically after restart.
```
