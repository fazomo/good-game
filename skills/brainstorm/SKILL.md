---
name: brainstorm
description: Design and brainstorming. Use for "design this", "suggest approaches", "pros/cons analysis", "idea exploration" requests. Dispatches 1-3 strategists based on AI backend config.
---

# /brainstorm - Multi-Agent Brainstorming

Brainstorming, design proposals, and idea exploration skill.

## Core Rule

**Always dispatch at least 1 strategist agent (Opus). Conditionally dispatch Gemini and Codex strategists based on `.gg/config.json`.**

- Opus Strategist (opus) -- logical strategy -- **always dispatched**
- Gemini Strategist (opus; external: gemini-3-pro-preview) -- creative strategy -- **if `backends.gemini: true`**
- Codex Strategist (opus; external: gpt-5.3-codex) -- risk validation -- **if `backends.codex: true`**

This creates a 1-to-3 strategist pattern depending on the user's configured AI backends.

## Usage

```

/brainstorm <topic or requirement>

```

## Workflow

```

1. Receive user's initial request
   |
2. Socratic interaction via AskUserQuestion
   - Questions that expand the user's thinking
   - Background, goals, constraints, priorities, target users, etc.
   - More questions are better, but don't force them
   - Ask from diverse perspectives
     |
3. Dispatch Opus Strategist + Gemini Strategist + Codex Strategist in parallel
   - Pass both the original request and Q&A content
     |
4. Orchestrator reports only paths and one-line common/diff summary

```

## Implementation

### 1. Socratic Interaction

Use the AskUserQuestion tool to expand the user's thinking with probing questions.

**Call pattern:**

- **Up to 5 questions** at once
- Provide 3-5 options per question (users can also type "Other" for free-form input)
- Use `multiSelect: true` where multiple selections make sense
- **Follow-up questions allowed**: After the first round of answers, ask more questions if new angles emerge
- Stop when the user has provided sufficient context

```typescript
AskUserQuestion({
  questions: [
    { question: "Who are the primary users?", header: "Users", options: [...], multiSelect: false },
    { question: "What are the key success metrics?", header: "Metrics", options: [...], multiSelect: true },
    { question: "Are there any constraints?", header: "Constraints", options: [...], multiSelect: true },
    { question: "What's the priority?", header: "Priority", options: [...], multiSelect: false },
  ]
})
```

**Example questions (select/generate as appropriate):**

- "Who are the primary users of this feature?"
- "What's the most important success metric?"
- "Are there budget or time constraints?"
- "Have you tried any approaches before?"
- "How do competitors solve this problem?"
- "What happens if this feature doesn't exist?"
- "Which requirements are highest priority?"
- "Are there technical constraints?"
- "Who are the stakeholders?"

**Guidelines:**

- Max 5 questions per round, follow-up rounds allowed
- Questions should feel natural, not forced
- **Depth of initial conversation is key**: Brainstorm quality correlates with conversation depth
- If user answers reveal new angles, probe deeper with follow-up questions
- Proceed to the next step when the user has answered sufficiently

### 2. Read Configuration

Before dispatching agents, read both the backend configuration and language configuration.

**Backend config:**

```bash
CONFIG_PATH="{{PROJECT_ROOT}}/.gg/config.json"
```

The orchestrator reads this file and parses the JSON. Determine which backends are enabled:

- `gemini`: boolean (default: `false`)
- `codex`: boolean (default: `false`)

If the config file does not exist, treat both as `false` (Claude-only mode) **and** display a notice to the user:

```
Note: No .gg/config.json found. Running in Claude-only mode.
Run /gg:setup to configure AI backends.
```

**Language config:**

```bash
LANGUAGE=$(cat ~/.claude/LANGUAGE.md 2>/dev/null | head -1)
# Default to "English" if file is missing or empty
```

The orchestrator reads `~/.claude/LANGUAGE.md` and uses the first line as the language value. If the file is missing or empty, default to `"English"`.

### 3. Dispatch Agents (Parallel)

**Always dispatch Opus Strategist.** Conditionally dispatch Gemini and Codex strategists based on the config read in step 2. Every agent prompt includes the resolved output language.

**Orchestrator pseudocode:**

```
// ALWAYS: Opus Strategist (opus) -- logical strategy
Task(opus-strategist):
  description: "Opus Strategist brainstorming {topic}"
  prompt: |
    ## Output Language
    {language}

    ## Original Request
    {original_request}

    ## Socratic Q&A
    {qa_summary}

    ## Output Path
    {{SESSION_DIR}}/brainstorm/
  run_in_background: true

// CONDITIONAL: Gemini Strategist (if gemini backend enabled)
if config.backends.gemini:
  Task(gemini-strategist):
    description: "Gemini Strategist brainstorming {topic}"
    prompt: |
      ## Output Language
      {language}

      ## Original Request
      {original_request}

      ## Socratic Q&A
      {qa_summary}

      ## Output Path
      {{SESSION_DIR}}/brainstorm/
    run_in_background: true

// CONDITIONAL: Codex Strategist (if codex backend enabled)
if config.backends.codex:
  Task(codex-strategist):
    description: "Codex Strategist brainstorming {topic}"
    prompt: |
      ## Output Language
      {language}

      ## Original Request
      {original_request}

      ## Socratic Q&A
      {qa_summary}

      ## Output Path
      {{SESSION_DIR}}/brainstorm/
    run_in_background: true
```

### 4. Dispatch Synthesizer (Sequential)

After all dispatched agents complete, invoke the Synthesizer in brainstorm mode.

The source file list is dynamic based on which agents were dispatched:

**Orchestrator pseudocode:**

```
// Build source file list dynamically
sourceFiles = [{{SESSION_DIR}}/brainstorm/opus.{nn}.md]
if config.backends.gemini:
  sourceFiles.append({{SESSION_DIR}}/brainstorm/gemini.{nn}.md)
if config.backends.codex:
  sourceFiles.append({{SESSION_DIR}}/brainstorm/codex.{nn}.md)

Task(synthesizer):
  description: "Synthesizing brainstorm results"
  prompt: |
    ## Output Language
    {language}

    ## Mode
    brainstorm

    ## Brainstorming Topic
    {topic}

    ## Source Files
    {sourceFiles, one per line prefixed with "- "}

    ## Output Path
    {{SESSION_DIR}}/brainstorm/
```

**If only Opus was dispatched (Claude-only mode):** The synthesizer still runs but with a single source. Its output will be a streamlined report based on one perspective rather than a multi-perspective synthesis.

**Note:** The source file list uses actual paths returned by the agents. The filenames above are examples; the orchestrator dynamically assembles the list by parsing each agent's return message for the "Saved: {path}" pattern. If an agent fails to save a file and returns text directly instead, inline that content into the Synthesizer prompt as a fallback.

### 5. Final Output (Orchestrator Output)

Report only the agents that were dispatched:

```
**[Opus Strategist]** -- returned
**[Gemini Strategist]** -- returned          // only if gemini enabled
**[Codex Strategist]** -- returned           // only if codex enabled
**[Synthesizer]** -- returned

**Report** -- `{{SESSION_DIR}}/brainstorm/synthesis.{nn}.md`
**Detail** -- `{{SESSION_DIR}}/brainstorm/`
```

**Notes:**

- Agents save files directly (orchestrator does not save)
- Filenames are determined by each agent per its convention
- Synthesizer consolidates all dispatched results into a unified report
- Orchestrator does not relay detailed content
- Direct users to reference the files
