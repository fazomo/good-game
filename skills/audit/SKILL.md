---
name: audit
description: Precision audit. Use for "review", "check", "verify" requests. Runs 3 auditors in parallel.
---

# /audit - Cross-Review

Precision audit skill for the audit target.

## Core Rule

**Always dispatch 3 reviewers in parallel.**

| Reviewer       | Model | Role                                                               |
| -------------- | ----- | ------------------------------------------------------------------ |
| opus-auditor   | opus  | Integrated integrity + convention audit                            |
| codex-auditor  | codex | Integrated integrity + convention audit (cross-perspective)        |
| gemini-auditor | opus  | Integrated integrity + convention audit (Gemini cross-perspective) |

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
2. Dispatch 3 auditors (parallel) -- Opus, Codex, Gemini
   |
3. Wait for all 3 reviewers to complete
   |
4. Orchestrator reports the 3 reviewer result file paths
   |
5. Feedback routing (context branching)
   - Pipeline internal (/blueprint follow-up): forward to executor (Director) -> revise
   - Pipeline internal (/execute follow-up): forward to executor (Implementor) -> revise
   - Standalone invocation (user direct /audit): report results to user and wait
```

## Implementation

### 1. Read Target

Verify the audit target files and determine the target type.

### 2. Dispatch 3 Auditors (Parallel)

Invoke 3 Tasks simultaneously in a single message:

```typescript
// Opus (integrated audit)
Task({
  subagent_type: "opus-auditor",
  description: "Opus auditing target",
  prompt: `
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

// Codex (integrated audit)
Task({
  subagent_type: "codex-auditor",
  description: "Codex auditing target",
  prompt: `
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

// Gemini (integrated audit)
Task({
  subagent_type: "gemini-auditor",
  description: "Gemini auditing target",
  prompt: `
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

### 3. Present Results (Orchestrator Output)

The orchestrator reports the 3 reviewer result file paths:

```
**[Opus]** -- `{{SESSION_DIR}}/audit/opus.{nn}.md`
**[Codex]** -- `{{SESSION_DIR}}/audit/codex.{nn}.md`
**[Gemini]** -- `{{SESSION_DIR}}/audit/gemini.{nn}.md`
```

**Note**: The orchestrator does not consolidate or summarize results. Only paths are reported.

### 4. Auto Feedback (Context Branching)

After audit completion, the orchestrator routes feedback **based on the calling context**:

#### Case A: Pipeline internal call (previous skill was /blueprint)

Executor = Director. Forward feedback to Director to revise the Blueprint document:

```typescript
Task({
  subagent_type: "director",
  description: "Director revising blueprint based on audit",
  prompt: `
## Audit Feedback - Audit Complete

3 reviewers have completed their audit.

### Audit Reports (must Read)
- {{SESSION_DIR}}/audit/opus.{nn}.md
- {{SESSION_DIR}}/audit/codex.{nn}.md
- {{SESSION_DIR}}/audit/gemini.{nn}.md

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

```typescript
Task({
  subagent_type: "implementor",
  description: "Implementor revising code based on audit",
  prompt: `
## Audit Feedback - Audit Complete

3 reviewers have completed their audit.

### Audit Reports (must Read)
- {{SESSION_DIR}}/audit/opus.{nn}.md
- {{SESSION_DIR}}/audit/codex.{nn}.md
- {{SESSION_DIR}}/audit/gemini.{nn}.md

### Original Target
{target_path}

Read the above audit reports to review the findings.
If Critical/Warning issues exist, revise the target accordingly.
  `,
});
```

#### Case C: Standalone invocation (user direct /audit)

No feedback routing. The orchestrator reports results to the user and waits:

```
**[Opus]** -- `{{SESSION_DIR}}/audit/opus.{nn}.md`
**[Codex]** -- `{{SESSION_DIR}}/audit/codex.{nn}.md`
**[Gemini]** -- `{{SESSION_DIR}}/audit/gemini.{nn}.md`

Please specify next action.
```

### 5. Workflow Summary

```
Audit -- 3 reviewers audit complete
Executor -- reads audit reports, revises target (pipeline internal calls only)
Executor -- revision complete, process ends
```

**Notes**:

- Feedback loop runs once only. If further audit is needed after revision, the user re-runs `/audit`.
- Executor is Director (Blueprint) or Implementor (Code) depending on context.
- For standalone invocations, no Executor feedback -- results are reported to the user only.
