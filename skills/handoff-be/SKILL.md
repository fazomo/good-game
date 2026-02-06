---
name: handoff-be
description: Generates a frontend-to-backend modification request document.
---

# /handoff-be - Handoff (Frontend -> Backend)

Generates a document requesting backend modifications from the frontend perspective.

## Usage

```
/handoff-be [request description]
```

**Examples:**

```
/handoff-be cancellation reason field needed in API response
/handoff-be
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

Delegate document creation to the Writer agent:

```typescript
Task({
  subagent_type: "writer",
  description: "Writer generating BE request document",
  prompt: `
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
