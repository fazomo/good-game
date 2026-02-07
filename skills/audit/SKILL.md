---
name: audit
description: Precision audit. Use for "review", "check", "verify" requests. Dispatches 1-3 auditors based on AI backend config.
---

# /audit - Cross-Review

Precision audit skill for the audit target.

## Core Rule

**Always dispatch at least 1 reviewer (Opus). Conditionally dispatch Codex and Gemini auditors based on `.gg/config.json`.**

| Reviewer       | Model | Condition                  | Role                                        |
| -------------- | ----- | -------------------------- | ------------------------------------------- |
| opus-auditor   | opus  | **always**                 | Integrated integrity + convention audit     |
| codex-auditor  | opus  | if `backends.codex: true`  | Integrated audit (Codex cross-perspective)  |
| gemini-auditor | opus  | if `backends.gemini: true` | Integrated audit (Gemini cross-perspective) |

## Audit Target Types

| Type         | Description                            | Representative Cases                       |
| ------------ | -------------------------------------- | ------------------------------------------ |
| Blueprint    | Design document (Phase/Task structure) | Implementation spec written by Director    |
| Code         | Implementation code (source files)     | Code created/modified by Implementor       |
| Architecture | System/structure document              | Agent definitions, workflow designs        |
| General      | Other                                  | Audit targets not matching the above types |

## Usage

```
/audit <target path> [type: blueprint|code|architecture|general]
```

**Examples:**

```
/audit blueprint/                        # Blueprint audit (type auto-detected)
/audit {{SESSION_DIR}}/blueprint/        # Blueprint audit
/audit src/services/                     # Code audit (type auto-detected)
/audit agents/ type: architecture        # Architecture audit
```

If type is not specified, the orchestrator examines the target path content to determine the type and passes it to the skill.

## Workflow

```
1. Read target + confirm type
   |
2. Dispatch 1-3 auditors (parallel) -- based on backend config
   |
3. Wait for all dispatched reviewers to complete
   |
4. Orchestrator reports dispatched reviewer result file paths
   |
5. Feedback routing (context branching)
   - Pipeline internal (/blueprint follow-up): forward to executor (Director) -> revise
   - Pipeline internal (/execute follow-up): forward to executor (Implementor) -> revise
   - Standalone invocation (user direct /audit): report results to user and wait
```

## Implementation

### 1. Read Target

Verify the audit target files and determine the target type.

### 2. Read Configuration

**Backend config:**

```bash
CONFIG_PATH="{{PROJECT_ROOT}}/.gg/config.json"
```

The orchestrator reads this file and parses the JSON. If the file does not exist, default to Claude-only (`gemini: false`, `codex: false`) **and** display a notice:

```
Note: No .gg/config.json found. Running in Claude-only mode (Opus auditor only).
Run /gg:setup to configure AI backends.
```

**Language config:**

```bash
LANGUAGE=$(cat ~/.claude/LANGUAGE.md 2>/dev/null | head -1)
# Default to "English" if file is missing or empty
```

### 3. Dispatch Auditors (Parallel)

**Always dispatch Opus Auditor.** Conditionally dispatch Codex and Gemini auditors based on config. Every auditor prompt includes the resolved output language.

**GG Task Dispatch Policy (experience-first standard):**

- **Task standard format:** Use `Task({ ... })` for all Task examples in this skill.
- **Parallel dispatch requirement:** Parallel auditor Tasks must include `run_in_background: true`.
- **Single-response rule:** Dispatch the full parallel auditor Task group in one orchestrator response.
- **Sequential gate rule:** Present results or trigger feedback routing only after all dispatched parallel auditor Tasks complete.
- **Spec-gap note:** Official SDK schema may differ by surface, but GG enforces this standard for operational reliability.
- **GG standard:** `Task({ ... run_in_background: true })` is the GG operational standard for parallel auditor dispatch.

**Orchestrator pseudocode:**

```typescript
// ALWAYS: Opus Auditor
Task({
  subagent_type: "opus-auditor",
  description: "Opus auditing target",
  prompt: `
## Output Language
{language}

## Audit Target
{target_path}

## Audit Target Type
{target_type}

## Source Documents
{source_documents}

## Applied Best Practices
{best_practices_paths}

## Output Path
{{SESSION_DIR}}/audit/
  `,
  run_in_background: true,
});

// CONDITIONAL: Codex Auditor
if config.backends.codex:
  Task({
    subagent_type: "codex-auditor",
    description: "Codex auditing target",
    prompt: `
## Output Language
{language}

## Audit Target
{target_path}

## Audit Target Type
{target_type}

## Source Documents
{source_documents}

## Applied Best Practices
{best_practices_paths}

## Output Path
{{SESSION_DIR}}/audit/
    `,
    run_in_background: true,
  });

// CONDITIONAL: Gemini Auditor
if config.backends.gemini:
  Task({
    subagent_type: "gemini-auditor",
    description: "Gemini auditing target",
    prompt: `
## Output Language
{language}

## Audit Target
{target_path}

## Audit Target Type
{target_type}

## Source Documents
{source_documents}

## Applied Best Practices
{best_practices_paths}

## Output Path
{{SESSION_DIR}}/audit/
    `,
    run_in_background: true,
  });
```

### 4. Present Results (Orchestrator Output)

Report only the auditors that were dispatched:

```
**[Opus]** -- `{{SESSION_DIR}}/audit/opus.{nn}.md`
**[Codex]** -- `{{SESSION_DIR}}/audit/codex.{nn}.md`     // only if codex enabled
**[Gemini]** -- `{{SESSION_DIR}}/audit/gemini.{nn}.md`   // only if gemini enabled
```

**Note:** The orchestrator does not consolidate or summarize results. Only paths are reported.

### 5. Auto Feedback (Context Branching)

After audit completion, the orchestrator routes feedback **based on the calling context**:

#### Case A: Pipeline internal call (previous skill was /blueprint)

Executor = Director. Forward feedback to Director to revise the Blueprint document:

**Orchestrator pseudocode:**

```typescript
Task({
  subagent_type: "director",
  description: "Director revising blueprint based on audit",
  prompt: `
## Output Language
{language}

## Audit Feedback - Audit Complete

{N} reviewer(s) have completed their audit.

### Audit Reports (must Read)
- {{SESSION_DIR}}/audit/opus.{nn}.md
- {{SESSION_DIR}}/audit/codex.{nn}.md    // only if codex was dispatched
- {{SESSION_DIR}}/audit/gemini.{nn}.md   // only if gemini was dispatched

### Original Target
{target_path}

### Common Critical Issues Summary
{common_critical_summary}

Read the above audit reports to review the findings.
If Critical/Warning issues exist, revise the target accordingly.
Overwrite revised content at the same path.
  `,
});
```

#### Case B: Pipeline internal call (previous skill was /execute)

Executor = Implementor. Forward feedback to Implementor to revise the code:

**Orchestrator pseudocode:**

```typescript
Task({
  subagent_type: "implementor",
  description: "Implementor revising code based on audit",
  prompt: `
## Audit Feedback - Audit Complete

{N} reviewer(s) have completed their audit.

### Audit Reports (must Read)
- {{SESSION_DIR}}/audit/opus.{nn}.md
- {{SESSION_DIR}}/audit/codex.{nn}.md    // only if codex was dispatched
- {{SESSION_DIR}}/audit/gemini.{nn}.md   // only if gemini was dispatched

### Original Target
{target_path}

Read the above audit reports to review the findings.
If Critical/Warning issues exist, revise the target accordingly.
  `,
});
```

**Note:** Case B dispatches the Implementor, which is a code-only agent. No `## Output Language` is injected here -- the Implementor produces code, not documents.

#### Case C: Standalone invocation (user direct /audit)

No feedback routing. The orchestrator reports results to the user and waits:

```
**[Opus]** -- `{{SESSION_DIR}}/audit/opus.{nn}.md`
**[Codex]** -- `{{SESSION_DIR}}/audit/codex.{nn}.md`     // only if codex enabled
**[Gemini]** -- `{{SESSION_DIR}}/audit/gemini.{nn}.md`   // only if gemini enabled

Please specify next action.
```

### 6. Workflow Summary

```
Audit -- 1-3 reviewers audit complete (based on backend config)
Executor -- reads audit reports, revises target (pipeline internal calls only)
Executor -- revision complete, process ends
```

**Notes:**

- Feedback loop runs once only. If further audit is needed after revision, the user re-runs `/audit`.
- Executor is Director (Blueprint) or Implementor (Code) depending on context.
- For standalone invocations, no Executor feedback -- results are reported to the user only.
