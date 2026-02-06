# Agent Registry

Agent roster for the good-game plugin. Each agent is invoked exclusively through skills.

**Architecture highlight:** The 3-strategist / 3-auditor symmetric pattern -- three AI models (Opus, Gemini, Codex) power both brainstorm and audit phases, ensuring cognitive diversity at every critical decision point.

| Agent             | Model  | External Model       | Used By                                | Role                           |
| ----------------- | ------ | -------------------- | -------------------------------------- | ------------------------------ |
| investigator      | sonnet | --                   | /gg:explore                            | Codebase reconnaissance        |
| opus-strategist   | opus   | --                   | /gg:brainstorm                         | Logical brainstorming          |
| gemini-strategist | opus   | gemini-3-pro-preview | /gg:brainstorm                         | Creative brainstorming         |
| codex-strategist  | opus   | gpt-5.3-codex        | /gg:brainstorm                         | Risk validation brainstorming  |
| director          | opus   | --                   | /gg:blueprint                          | Implementation planning        |
| implementor       | opus   | --                   | /gg:execute                            | Code implementation            |
| opus-auditor      | opus   | --                   | /gg:audit                              | Audit (Opus perspective)       |
| codex-auditor     | opus   | gpt-5.3-codex        | /gg:audit                              | Audit (Codex perspective)      |
| gemini-auditor    | opus   | gemini-3-pro-preview | /gg:audit                              | Audit (Gemini perspective)     |
| synthesizer       | sonnet | --                   | /gg:audit, /gg:explore, /gg:brainstorm | Parallel result synthesis      |
| writer            | sonnet | --                   | /gg:handoff-be, /gg:handoff-fe         | Handoff document generation    |
| code-simplifier   | opus   | --                   | /gg:execute                            | Post-implementation refinement |

**Column descriptions:**

- **Model**: The Claude model used by the Task tool's subagent. This is the model Claude Code uses when running the agent.
- **External Model**: An external AI model the agent invokes internally via CLI. `--` means the agent runs on the Claude model alone. Gemini-strategist and gemini-auditor use the `gemini` CLI to call gemini-3-pro-preview. Codex-strategist and codex-auditor use the `codex` CLI to call gpt-5.3-codex.

## Agent Definition Files

Each agent's detailed prompt is defined in the `{agent-name}.md` file in this directory.
