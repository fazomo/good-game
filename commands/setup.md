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

### Step 3: External AI Backend Selection

Detect available CLIs:

```bash
GEMINI_AVAILABLE=$(which gemini >/dev/null 2>&1 && echo "true" || echo "false")
CODEX_AVAILABLE=$(which codex >/dev/null 2>&1 && echo "true" || echo "false")
```

Build the option labels dynamically based on detection. If a CLI is not found, append ` [CLI not detected]` to its options.

**Orchestrator pseudocode** (not a literal runnable script):

```
AskUserQuestion:
  header: "AI Backend Configuration"
  question: |
    Which AI backends would you like to enable?

    Detected CLIs:
    - gemini: {installed / not found}
    - codex: {installed / not found}

    You can install missing CLIs later and re-run /gg:setup to update.
  options:
    - "Claude only (default)"
    - "Claude + Gemini"            # append " [CLI not detected]" if gemini not found
    - "Claude + Codex"             # append " [CLI not detected]" if codex not found
    - "Claude + Gemini + Codex"    # append " [some CLIs not detected]" if any not found
```

**If the user selects an option with `[CLI not detected]`:** Warn the user that the selected backend CLI is not currently installed and the corresponding agents will fail until the CLI is available. Proceed with saving the selection anyway (the user may intend to install it later).

**Save configuration:** Create the `.gg/` directory and write the config file.

```bash
mkdir -p {{PROJECT_ROOT}}/.gg
```

Map the selection to a config object:

| Selection               | `gemini` | `codex` |
| ----------------------- | -------- | ------- |
| Claude only             | `false`  | `false` |
| Claude + Gemini         | `true`   | `false` |
| Claude + Codex          | `false`  | `true`  |
| Claude + Gemini + Codex | `true`   | `true`  |

Write the config file to `{{PROJECT_ROOT}}/.gg/config.json`:

```json
{
  "version": 1,
  "backends": {
    "gemini": <true|false>,
    "codex": <true|false>
  }
}
```

**Add `.gg/` to `.gitignore`:** Only if `{{PROJECT_ROOT}}/.gitignore` already exists. If it exists and does not contain `.gg/`, append it. If `.gitignore` does not exist, do NOT create one -- instead, display a note to the user:

```
Note: No .gitignore found in project root. Consider adding `.gg/` to your
.gitignore to avoid committing plugin configuration to version control.
```

```bash
# Only append to existing .gitignore
if [ -f "{{PROJECT_ROOT}}/.gitignore" ]; then
  grep -qxF '.gg/' "{{PROJECT_ROOT}}/.gitignore" || echo '.gg/' >> "{{PROJECT_ROOT}}/.gitignore"
fi
```

**Note:** `{{PROJECT_ROOT}}` is not a literal shell variable. The orchestrator resolves this to the actual project root path at runtime (typically the current working directory).

### Step 4: Subagent Permission Notice

Display the following security notice and ask for acknowledgment:

**Orchestrator pseudocode:**

```
AskUserQuestion:
  header: "Subagent Permissions"
  question: |
    This plugin uses subagents (via Claude Code's Task tool) with
    bypassPermissions permission. This means subagents can:

    - Create directories (mkdir) for session documents and config
    - Create/write markdown files (.md) for reports, blueprints, audits
    - Read any file in your project for analysis
    - Execute specific CLI commands (gemini, codex) if those backends
      are enabled -- these run in sandboxed/read-only modes

    Subagents CANNOT:
    - Push to git, delete branches, or run destructive git commands
    - Access credentials or environment files (by convention)

    All generated documents are stored in:
    - .claude/docs/ (session documents)
    - .gg/ (plugin configuration)

    Do you acknowledge these permissions?
  options:
    - "Yes, I understand and accept"
    - "No, I want to review further before proceeding"
```

**If "No" is selected:** Display the following message and halt setup (do not proceed to Step 5):

```
Setup paused. You can review the agent definitions at:
  {plugin_path}/agents/

Each agent's frontmatter defines its permissionMode and available tools.
Re-run /gg:setup when ready to proceed.
```

**If "Yes" is selected:** Proceed to Step 5.

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

Build the skill list dynamically based on the backend selection:

- If `gemini: false` and `codex: false`: Show "Opus" only for brainstorm/audit
- If `gemini: true` and `codex: false`: Show "Opus + Gemini"
- If `gemini: false` and `codex: true`: Show "Opus + Codex"
- If both `true`: Show "Opus + Gemini + Codex"

```
**GG -- Setup Complete**

good-game plugin setup is complete.

**Installed items:**
- ~/.claude/CLAUDE.md (orchestrator protocol)
  (Previous file backed up: ~/.claude/CLAUDE.md.backup.{timestamp})
- ~/.claude/LANGUAGE.md (language configuration)
- {{PROJECT_ROOT}}/.gg/config.json (backend configuration)

**Configuration:**
- **Response Language:** {selected language}
- **AI Backends:** {backend description, e.g., "Claude + Gemini (Codex disabled)"}

**Available skills:**
- /gg:explore    -- Multi-angle codebase reconnaissance
- /gg:brainstorm -- {N}-strategist parallel brainstorming ({agent list})
- /gg:blueprint  -- Precision implementation planning
- /gg:execute    -- Code implementation
- /gg:audit      -- {N}-auditor parallel cross-review ({agent list})
- /gg:handoff-be -- BE modification request document
- /gg:handoff-fe -- FE handoff document
- /gg:cm         -- Logical unit commits

**Next step:** Restart your session. (Cmd+Shift+P > "Reload Window" or restart terminal)
The protocol activates automatically after restart.
```
