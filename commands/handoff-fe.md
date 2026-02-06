---
description: "Generate backend-to-frontend handoff document"
argument-hint: "[description]"
---

# /handoff-fe - Handoff (Backend -> Frontend)

Generates a handoff document for the frontend team after backend development is complete.

## Usage

```
/gg:handoff-fe [description]
```

**Examples:**

```
/gg:handoff-fe course cancellation API complete
/gg:handoff-fe
```

## When to Use

- When backend API development is complete and ready for frontend handoff
- When notifying the frontend team of API changes

## Workflow

```
1. Collect session context (blueprint, execute)
   |
2. Dispatch Writer agent
   |
3. Present document path
```

## Implementation

### 1. Collect Context

Reference session blueprint and execute results. Collect relevant file paths from the session directory.

### 2. Dispatch Writer Agent

Delegate document creation to the Writer agent:

```typescript
Task({
  subagent_type: "writer",
  description: "Writer generating FE handoff document",
  prompt: `
## Mode
handoff-fe

## Handoff Content
{handoff_description}

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

**Path** -- `{{SESSION_DIR}}/handoff/fe-handoff.{nn}.md`
```

**Note**: Orchestrator does not relay document content. Path only.

Handoff content: $ARGUMENTS
