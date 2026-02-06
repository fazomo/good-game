---
name: execute
description: Code implementation execution. Use for "implement", "write code", "run blueprint" requests. Dispatches Implementor agent.
---

# /execute - Implementor Execution Agent

Code implementation execution skill. Supports parallel execution.

## Usage

```
/execute <blueprint file or directory>
```

**Examples:**

```
/execute blueprint/01-phase-1.md      # Execute a specific Phase only
/execute blueprint/                   # Execute all Phases sequentially
```

## Workflow

```
1. Load blueprint
        |
2. Parse parallel sections
        |
3. Dispatch Implementor agents
        |
4. Monitor progress + branching/routing
        |
5. (On Phase completion) Run code-simplifier
        |
6. Verify build
        |
7. Report file list only
```

## Implementation

### 1. Load Blueprint

Read the implementation plan document.

- If a Phase file is specified: load that Phase only
- If a directory is specified: load all Phase files sequentially (`01-*.md`, `02-*.md`, ...)

### 2. Parse Parallel Sections

Identify parallelizable sections (specified in the Blueprint).

### 3. Dispatch Implementor Agents

Pass tasks and reference information to the Implementor:

```typescript
// Sequential execution
Task({
  subagent_type: "implementor",
  description: "Implementor implementing {task}",
  prompt: `
## Task
{task_name}

## Blueprint Reference
{phase_file_path}

## Protocol (Branching Conditions)
{protocol_section}

## Reference (Code/Verification)
{reference_section}
  `,
});

// Parallel execution - multiple Tasks in a single message
Task({ ..., run_in_background: true });
Task({ ..., run_in_background: true });
```

### 4. Monitor Progress + Branching/Routing

Check background agent status and handle branching conditions.

When an Implementor is blocked:

1. Record the problem situation
2. Report to orchestrator (never call Director directly)
3. Orchestrator either re-queries Director or decides directly
4. Receive response and continue

### 5. Code Simplification (After Phase Completion)

On Phase completion, dispatch the code-simplifier agent. If the code-simplifier plugin is not installed, this step may fail; on failure, skip this step and return only the Implementor results.

```typescript
Task({
  subagent_type: "code-simplifier:code-simplifier",
  description: "Simplify Phase {n} outputs",
  prompt: `
Clean up the files created/modified in {phase_name}.

File list:
{modified_files}

**Never change functionality.**
  `,
});
```

After code-simplifier completes:

1. Verify build with `pnpm build` or `npm run build`
2. On build failure, roll back changes
3. On build success, finalize commit

### 6. Report Completion

The Implementor does not create documents. The modified files themselves are the results.

The orchestrator reports only the list of modified files after the Implementor returns:

```
**[Implementor]** -- returned

**Files** --
- {file_path_1}
- {file_path_2}
```

**Note**: The orchestrator does not relay detailed implementation content. Only the modified file list is reported.

### 7. Auto-Audit Transition

After the Implementor reports completion, the orchestrator **automatically triggers `/audit`** per the CLAUDE.md Dynamic Workflow. The orchestrator invokes the audit skill directly.

The execute skill itself is not involved in this transition.
