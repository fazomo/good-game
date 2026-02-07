# good-game

> One AI is an opinion. Three AIs are a strategy. GG.

Multi-agent orchestration protocol for Claude Code. Three AI architectures. One unified workflow. Zero blind spots.

Every AI model has blind spots. Opus reasons deeply but can over-engineer. Gemini thinks laterally but can hallucinate. Codex writes precise syntax but misses the big picture. good-game combines all three -- not as a committee, but as a structured pipeline where each model's strength covers another's weakness.

## The 3 + 3 Pattern

The architectural signature of good-game: **up to 3 strategists brainstorm, up to 3 auditors review.** Same three AI engines, symmetric across both phases when all backends are enabled.

| Phase          | Opus (Logic)      | Gemini (Creative)   | Codex (Validation) |
| :------------- | :---------------- | :------------------ | :----------------- |
| **Brainstorm** | `opus-strategist` | `gemini-strategist` | `codex-strategist` |
| **Audit**      | `opus-auditor`    | `gemini-auditor`    | `codex-auditor`    |

_Plus: `director`, `implementor`, `investigator`, `synthesizer`, `writer`, `code-simplifier` manage the flow between phases._

```
           [ YOUR INTENT ]
                 |
         +-------+-------+        << Brainstorm (3 strategists)
         |       |       |
       Opus   Gemini   Codex
         |       |       |
         +-------+-------+
                 |
            [ DIRECTOR ]           << Plan
                 |
          [ IMPLEMENTOR ]          << Build
                 |
         +-------+-------+        << Audit (3 auditors)
         |       |       |
       Opus   Gemini   Codex
         |       |       |
         +-------+-------+
                 |
              [ GG ]
```

### Why three different models?

To avoid groupthink. When three instances of the same model review code, they share the same blind spots. By using different underlying architectures for strategist and auditor roles, good-game ensures that a weakness in one model is caught by another. The names (opus-, gemini-, codex-) reflect this architectural diversity -- not vendor loyalty.

## Installation

### 1. Add Marketplace

```bash
claude /plugin marketplace add {owner}/good-game
```

### 2. Install Plugin

```bash
claude /plugin install good-game
```

### 3. Run Setup

After installation, run the setup skill in Claude Code:

```
/gg:setup
```

This will:

- Install the orchestrator protocol to `~/.claude/CLAUDE.md`
- Let you choose your preferred response language
- Back up any existing CLAUDE.md
- Guide you through external AI configuration

### 4. Restart Session

Restart your Claude Code session to activate the protocol.

## Skills

| Skill        | Command          | Description                                                 |
| ------------ | ---------------- | ----------------------------------------------------------- |
| Explore      | `/gg:explore`    | Multi-angle codebase reconnaissance (Investigator swarm)    |
| Brainstorm   | `/gg:brainstorm` | 1-3 strategist parallel brainstorming (config-based)         |
| Blueprint    | `/gg:blueprint`  | Precision implementation planning (Director)                |
| Execute      | `/gg:execute`    | Blueprint-based code implementation (Implementor)           |
| Audit        | `/gg:audit`      | 1-3 auditor parallel cross-review (config-based)            |
| Handoff (BE) | `/gg:handoff-be` | Frontend-to-backend modification request document           |
| Handoff (FE) | `/gg:handoff-fe` | Backend-to-frontend handoff document                        |
| Commit       | `/gg:cm`         | Logical unit commits for current changes                    |
| Setup        | `/gg:setup`      | Initial plugin configuration                                |
| Uninstall    | `/gg:uninstall`  | Remove plugin traces and restore CLAUDE.md                  |

## Agents

| Agent             | Model  | External AI          | Role                           |
| ----------------- | ------ | -------------------- | ------------------------------ |
| investigator      | sonnet | --                   | Codebase reconnaissance        |
| opus-strategist   | opus   | --                   | Logical brainstorming          |
| gemini-strategist | opus   | gemini-3-pro-preview | Creative brainstorming         |
| codex-strategist  | opus   | gpt-5.3-codex        | Risk validation brainstorming  |
| director          | opus   | --                   | Implementation planning        |
| implementor       | opus   | --                   | Code implementation            |
| opus-auditor      | opus   | --                   | Audit (Opus perspective)       |
| codex-auditor     | opus   | gpt-5.3-codex        | Audit (Codex perspective)      |
| gemini-auditor    | opus   | gemini-3-pro-preview | Audit (Gemini perspective)     |
| synthesizer       | sonnet | --                   | Result synthesis (explore always, brainstorm when 2+ sources) |
| writer            | sonnet | --                   | Handoff document generation    |
| code-simplifier   | opus   | --                   | Post-implementation refinement |

## Dynamic Workflow

The orchestrator automatically chains skills:

```
/gg:brainstorm -> (user choice) -> /gg:blueprint -> (auto) -> /gg:audit
                                                                  |
                                            issues? -> feedback to Director -> done
                                            clean?  -> (user choice) -> /gg:execute -> (auto) -> /gg:audit
                                                                                                     |
                                                                             issues? -> feedback to Implementor -> done
```

User can override auto-chaining at any time with "skip audit" or "just implement".

## External AI (Optional)

good-game supports optional cross-validation using external AI providers:

- **Gemini** (`gemini` CLI): Used by Gemini Strategist (brainstorm) and Gemini Auditor (audit)
- **Codex** (`codex` CLI): Used by Codex Strategist (brainstorm) and Codex Auditor (audit)

External AI is **not required**. Without it, all agents fall back to Claude-only analysis. The system detects available CLIs at runtime using `which gemini` / `which codex`.

### Installing External CLIs

Refer to each CLI's official documentation for installation:

- **Gemini CLI:** [https://github.com/google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli)
- **Codex CLI:** [https://github.com/openai/codex](https://github.com/openai/codex)

## Security Notices

### auto-approve Hook

This plugin includes an auto-approve hook that automatically approves Write, Edit, MultiEdit tool calls and `mkdir` Bash commands without user confirmation. This is designed for the delegation workflow where the orchestrator delegates to the Implementor agent.

**If you work in a security-sensitive environment**, consider disabling auto-approve during setup or disabling the plugin's hooks entirely.

### Subagent Permission Mode

All bundled subagents use `permissionMode: acceptEdits`. Combined with the PreToolUse auto-approve hook above, this keeps normal document/code workflows low-friction while preserving guardrails for non-whitelisted commands.

### External AI Data Transmission

When using Gemini or Codex integration, portions of your code context are sent to Google (Gemini) or OpenAI (Codex) servers. If your organization has policies against external data transmission, use "Claude only" mode.

### CLAUDE.md Override

The setup skill installs a CLAUDE.md file to `~/.claude/CLAUDE.md`. This file acts as the highest-priority instruction for Claude Code. If you use another plugin that also requires CLAUDE.md, there will be a conflict. Your existing CLAUDE.md is backed up before installation.

## Uninstall

```
/gg:uninstall
```

This will restore your original CLAUDE.md from backup and provide instructions for disabling the plugin.

## License

[MIT](LICENSE)
