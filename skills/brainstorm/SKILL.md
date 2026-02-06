---
name: brainstorm
description: Design and brainstorming. Use for "design this", "suggest approaches", "pros/cons analysis", "idea exploration" requests. Runs 3 strategists in parallel.
---

# /brainstorm - Multi-Agent Brainstorming

Brainstorming, design proposals, and idea exploration skill.

## Core Rule

**Always dispatch 3 strategist agents in parallel.**

- Opus Strategist (opus) -- logical strategy
- Gemini Strategist (opus; external: gemini-3-pro-preview) -- creative strategy
- Codex Strategist (opus; external: gpt-5.3-codex) -- risk validation

This mirrors the 3-auditor pattern in /audit, creating a symmetric multi-perspective architecture.

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

### 2. Dispatch 3 Agents (Parallel)

Invoke 3 Tasks simultaneously in a single message:

```typescript
// Opus Strategist (opus) -- logical strategy
Task({
  subagent_type: "opus-strategist",
  description: "Opus Strategist brainstorming {topic}",
  prompt: `

## Original Request

{original_request}

## Socratic Q&A

{qa_summary}

## Output Path

{{SESSION_DIR}}/brainstorm/
`,
  run_in_background: true,
});

// Gemini Strategist (opus; external: gemini-3-pro-preview) -- creative strategy
Task({
  subagent_type: "gemini-strategist",
  description: "Gemini Strategist brainstorming {topic}",
  prompt: `

## Original Request

{original_request}

## Socratic Q&A

{qa_summary}

## Output Path

{{SESSION_DIR}}/brainstorm/
`,
  run_in_background: true,
});

// Codex Strategist (opus; external: gpt-5.3-codex) -- risk validation
Task({
  subagent_type: "codex-strategist",
  description: "Codex Strategist brainstorming {topic}",
  prompt: `

## Original Request

{original_request}

## Socratic Q&A

{qa_summary}

## Output Path

{{SESSION_DIR}}/brainstorm/
`,
  run_in_background: true,
});
```

### 3. Dispatch Synthesizer (Sequential)

After all 3 agents complete, invoke the Synthesizer in brainstorm mode.

```typescript
// Collect agent file paths from each agent's return message.
// The orchestrator parses "Saved: {path}" from each agent's return and assembles the list below dynamically.

Task({
  subagent_type: "synthesizer",
  description: "Synthesizing brainstorm results",
  prompt: `
## Mode
brainstorm

## Brainstorming Topic
{topic}

## Source Files
- {{SESSION_DIR}}/brainstorm/opus.{nn}.md
- {{SESSION_DIR}}/brainstorm/gemini.{nn}.md
- {{SESSION_DIR}}/brainstorm/codex.{nn}.md

## Output Path
{{SESSION_DIR}}/brainstorm/
  `,
});
```

**Note:** The source file list uses actual paths returned by the agents. The filenames above are examples; the orchestrator dynamically assembles the list by parsing each agent's return message for the "Saved: {path}" pattern. If an agent fails to save a file and returns text directly instead, inline that content into the Synthesizer prompt as a fallback.

### 4. Final Output (Orchestrator Output)

```
**[Opus Strategist]** -- returned
**[Gemini Strategist]** -- returned
**[Codex Strategist]** -- returned
**[Synthesizer]** -- returned

**Report** -- `{{SESSION_DIR}}/brainstorm/synthesis.{nn}.md`
**Detail** -- `{{SESSION_DIR}}/brainstorm/`
```

**Notes**:

- Agents save files directly (orchestrator does not save)
- Filenames are determined by each agent per its convention
- Synthesizer consolidates all 3 results into a unified report
- Orchestrator does not relay detailed content
- Direct users to reference the files
