# Agent Registry

Agent roster for the good-game plugin. Each agent is invoked exclusively through skills.

**Architecture highlight:** The symmetric multi-agent pattern -- Opus is always present, with optional Gemini and Codex agents adding cognitive diversity when enabled via `.gg/config.json`.

| Agent             | Model  | External Model       | Condition    | Used By                        | Role                           |
| ----------------- | ------ | -------------------- | ------------ | ------------------------------ | ------------------------------ |
| investigator      | sonnet | --                   | always       | /gg:explore                    | Codebase reconnaissance        |
| opus-strategist   | opus   | --                   | always       | /gg:brainstorm                 | Logical brainstorming          |
| gemini-strategist | opus   | gemini-3-pro-preview | if gemini on | /gg:brainstorm                 | Creative brainstorming         |
| codex-strategist  | opus   | gpt-5.3-codex        | if codex on  | /gg:brainstorm                 | Risk validation brainstorming  |
| director          | opus   | --                   | always       | /gg:blueprint                  | Implementation planning        |
| implementor       | opus   | --                   | always       | /gg:execute                    | Code implementation            |
| opus-auditor      | opus   | --                   | always       | /gg:audit                      | Audit (Opus perspective)       |
| codex-auditor     | opus   | gpt-5.3-codex        | if codex on  | /gg:audit                      | Audit (Codex perspective)      |
| gemini-auditor    | opus   | gemini-3-pro-preview | if gemini on | /gg:audit                      | Audit (Gemini perspective)     |
| synthesizer       | sonnet | --                   | conditional  | /gg:explore, /gg:brainstorm    | Parallel result synthesis      |
| writer            | sonnet | --                   | always       | /gg:handoff-be, /gg:handoff-fe | Handoff document generation    |
| code-simplifier   | opus   | --                   | always       | /gg:execute                    | Post-implementation refinement |

**Column descriptions:**

- **Model**: The Claude model used by the Task tool's subagent. This is the model Claude Code uses when running the agent.
- **External Model**: An external AI model the agent invokes internally via CLI. `--` means the agent runs on the Claude model alone. Gemini-strategist and gemini-auditor use the `gemini` CLI to call gemini-3-pro-preview. Codex-strategist and codex-auditor use the `codex` CLI to call gpt-5.3-codex.
- **Condition**: `always` = dispatched regardless of config. `if gemini on` / `if codex on` = dispatched only when the corresponding backend is enabled in `.gg/config.json`. `conditional` for `synthesizer` means: always in `/gg:explore`, but in `/gg:brainstorm` only when 2+ strategist source files are available.

## Permission Policy

All agent definition files in this directory use `permissionMode: acceptEdits`.

During real execution, the plugin's PreToolUse auto-approve hook additionally auto-approves `Write`, `Edit`, `MultiEdit`, and safe `mkdir` commands (no shell chaining), reducing repeated permission prompts in the normal GG workflow.

## Configuration

Backend availability is controlled by `{{PROJECT_ROOT}}/.gg/config.json`, created during `/gg:setup`. Skills read this config at dispatch time and only invoke conditional agents when their backend is enabled. If the config file is missing, skills default to Claude-only mode (Opus only).

## Agent Definition Files

Each agent's detailed prompt is defined in the `{agent-name}.md` file in this directory.
