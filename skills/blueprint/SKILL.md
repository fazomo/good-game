---
name: blueprint
description: Implementation planning. Use for "make a plan", "how to implement", "break into steps" requests. Dispatches the Director agent.
---

# /blueprint - Implementation Planning

Turns brainstorm results into reality. Creates a **rigorous plan** so the Implementor can execute without thinking.

## Usage

```
/blueprint <design document or topic>
```

**Examples:**

```
/blueprint brainstorm/opus.01.md
/blueprint course cancellation feature
```

## Workflow

```
1. Collect context + brainstorm
   |
2. Gap analysis via AskUserQuestion
   |
3. Detect best practices
   |
4. Dispatch Director agent (pass output path)
   |
5. Report Phase list and overview path only
```

## Implementation

### 1. Collect & Record Source Documents

Gather `brainstorm/*.md` files from the session and **record the source document list**.

**Source document record format:**

When passing to the Director, explicitly state which documents form the basis of the blueprint:

```
## Source Documents

This blueprint is based on the following documents:

- {{SESSION_DIR}}/brainstorm/opus.{nn}.md
- {{SESSION_DIR}}/brainstorm/gemini.{nn}.md
- {{SESSION_DIR}}/brainstorm/codex.{nn}.md

Reflect all requirements from the above source documents without omission.
```

**Note**: The source document list is used during audit for **integrity verification**.

### 2. Gap Analysis & Confirmation

**Standalone mode (direct invocation without brainstorm):**
If no brainstorm session exists (`{{SESSION_DIR}}/brainstorm/*.md` files absent), skip Steps 1-2 and proceed directly to Step 3 (Best Practices detection). The user's direct input becomes the sole source, and the Director prompt's `## Design Reference` section contains the user's original request.

**Standard mode (post-brainstorm invocation):**
Brainstorm results contain open questions, undecided items, and conflicting opinions. Before passing to the Director, resolve these gaps with the user to increase plan precision.

**Process:**

1. Read and analyze brainstorm results (opus, gemini, codex, synthesis)
2. Identify:
   - **Open questions** -- explicitly raised unresolved questions from brainstorm
   - **Conflicting proposals** -- points where agents disagree
   - **Ambiguous requirements** -- areas open to interpretation at implementation level
   - **Missing decisions** -- implementation-critical decisions not covered in brainstorm
3. Confirm via AskUserQuestion

**Call pattern:**

The purpose differs from brainstorm's Socratic Interaction:

- brainstorm: "expand thinking" -- open questions, possibility exploration
- blueprint: "fill gaps" -- confirm, decide, scope

```typescript
AskUserQuestion({
  questions: [
    { question: "JWT vs Session for auth -- which do you want to go with?", header: "Tech Decision", options: [...], multiSelect: false },
    { question: "Which features should be in the MVP scope?", header: "Implementation Scope", options: [...], multiSelect: true },
    { question: "What level of error messages should users see?", header: "Edge Cases", options: [...], multiSelect: false },
    { question: "Any performance targets?", header: "Non-functional Requirements", options: [...], multiSelect: false },
  ]
})
```

**Example question categories (select/generate as appropriate):**

| Category             | Example                                                                  |
| -------------------- | ------------------------------------------------------------------------ |
| Implementation scope | "Features for MVP vs deferred to later?"                                 |
| Tech decisions       | "Approach A vs B from brainstorm -- which to adopt?"                     |
| Priorities           | "Phase ordering: dependency-based vs business-impact-based?"             |
| Edge cases           | "Handling concurrent requests, network failures, etc.?"                  |
| Non-functional reqs  | "Response time, concurrent users, security level to confirm?"            |
| Conflict resolution  | "Opus Strategist proposed X, Gemini Strategist proposed Y -- direction?" |

**Guidelines:**

- Max 5 questions per round (AskUserQuestion tool limit)
- Follow-up rounds allowed if first answers reveal new decision needs
- Questions should be grounded in actual gaps found in brainstorm results -- do not fabricate
- **Proceed to next step only after all gaps are filled**
- Confirmed decisions are passed to the Director as a `## Confirmed Decisions` section

### 3. Detect & Inject Best Practices

## Applicable Best Practices

Search for best-practices files at the following paths and, if found, Read them and apply their patterns:

1. Glob("{{PROJECT_ROOT}}/.claude/skills/_best-practices_/\*_/_.md") -- project-local best-practices
2. Glob("**/skills/_best-practices_/**/\*.md") -- installed plugin best-practices

If no files are found at these paths, skip this section.

### 4. Dispatch Director Agent

Before dispatching the Director, read the language configuration:

```bash
LANGUAGE=$(cat ~/.claude/LANGUAGE.md 2>/dev/null | head -1)
# Default to "English" if file is missing or empty
```

Pass the Director **output path** and **preprocessed results** explicitly:

**GG Task Dispatch Policy (experience-first standard):**

- **Task standard format:** Use `Task({ ... })` for Task examples in this skill.
- **Background rule:** Director dispatch uses `run_in_background: true`.
- **Completion gate:** Proceed to summary reporting and auto-audit only after the Director Task completes.
- **Single-task consistency:** Even single-agent dispatch follows the same `Task({ ... })` standard.
- **Spec-gap note:** Official SDK schema may differ by surface, but GG enforces this standard for operational reliability.
- **GG standard:** `Task({ ... run_in_background: true })` is the GG operational standard for background Task dispatch.

```typescript
Task({
  subagent_type: "director",
  description: "Director creating blueprint for {topic}",
  prompt: `
## Output Language
{language}

## Planning Topic
{topic}

## Design Reference
{brainstorm_content}

## Confirmed Decisions
{confirmed_decisions}

## Applicable Best Practices
{best_practices_list}

## Output Path
{{SESSION_DIR}}/blueprint/
  `,
  run_in_background: true,
});
```

**Director Prompt Components:**

| Field                 | Description                                       |
| --------------------- | ------------------------------------------------- |
| `topic`               | The planning topic requested by the user          |
| `brainstorm_content`  | Content from related brainstorm-\*.md files       |
| `confirmed_decisions` | Decisions confirmed with user during Gap Analysis |
| `best_practices_list` | Detected tech stack best practices skill paths    |
| `Output Path`         | Directory where the Director saves outputs        |

### 5. Present Summary (Orchestrator Output Format)

After confirming Director Task completion, orchestrator reports Phase list and save path only:

```
**[Director]** -- returned

**Path** -- `{{SESSION_DIR}}/blueprint/`

**Phase list:**
1. {Phase 1 title}
2. {Phase 2 title}
3. ...
```

**Note**: Orchestrator does not relay the full plan. Only Phase titles and path.

### 6. Auto-Audit Chain

After Director Task completion is confirmed, the orchestrator **automatically** triggers audit. Invoke the audit Skill tool directly.

Audit target: `{{SESSION_DIR}}/blueprint/*.md`

**After audit**: Per the audit skill, 3 audit reports (opus, codex, gemini) are automatically sent to the executor (Director) for revision.
