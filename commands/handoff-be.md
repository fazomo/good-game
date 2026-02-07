---
description: "Generate frontend-to-backend modification request document"
argument-hint: "[request description]"
---

# /handoff-be - Handoff (Frontend -> Backend)

Generates a document requesting backend modifications from the frontend perspective.

## Usage

```
/gg:handoff-be [request description]
```

**Examples:**

```
/gg:handoff-be cancellation reason field needed in API response
/gg:handoff-be
```

## When to Use

- When frontend development requires backend API modifications
- When requesting API response format changes

## Workflow

```
1. Collect session context
   |
2. Dispatch Writer agent
   |
3. Present document path
```

## Implementation

### 1. Collect Context

Gather current session discussion context and issue details. Collect relevant file paths from the session directory.

### 2. Dispatch Writer Agent

Before dispatching the Writer, read the language configuration:

```bash
LANGUAGE=$(cat ~/.claude/LANGUAGE.md 2>/dev/null | head -1)
# Default to "English" if file is missing or empty
```

Delegate document creation to the Writer agent:

```typescript
Task({
  subagent_type: "writer",
  description: "Writer generating BE request document",
  prompt: `
## Output Language
{language}

## Mode
handoff-be

## Request Content
{request_description}

## Session Context
{session_context_paths}

## Output Path
{{SESSION_DIR}}/handoff/
  `,
});
```

### 3. Present Document (Orchestrator Output)

```
**[Writer]** -- returned

**Path** -- `{{SESSION_DIR}}/handoff/be-request.{nn}.md`
```

**Note**: Orchestrator does not relay document content. Path only.

Request: $ARGUMENTS
