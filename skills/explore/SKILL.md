---
name: explore
description: Multi-angle reconnaissance of a target path. Investigator agents analyze 3 axes (Structure/Domain/Expansion) with cross-validation, then results are file-based synthesized.
---

# /explore - Investigator Swarm Protocol

**"Recon to file. Synthesize. Report path."**

Analyzes the target from **3 axes**, always in **pairs of 2** for cross-validation.
Investigators save results to files, and the Synthesizer cross-validates and generates a consolidated report.

---

## Core Principle: 3 Axes x Paired Cross-Validation

### 3 Exploration Axes (Axis)

**All axes must be covered** regardless of level. Level determines "how specialized" the exploration is.

| Axis          | Core Question                          | Exploration Targets                                                              |
| :------------ | :------------------------------------- | :------------------------------------------------------------------------------- |
| **Structure** | What is where and how is it connected? | Directory structure, file layout, import/export relationships, inter-module deps |
| **Domain**    | What does this do in business terms?   | Domain terminology, business logic, data flow, core use cases                    |
| **Expansion** | What other areas are related?          | Modules that call this one, modules this depends on, blast radius                |

### Paired Cross-Validation

Approach the same target from **different directions** to discover discrepancies.

| Direction          | Approach           | Example                                                            |
| :----------------- | :----------------- | :----------------------------------------------------------------- |
| **Top-Down (TD)**  | From whole to part | Directory -> files -> functions / flow start -> end                |
| **Bottom-Up (BU)** | From part to whole | Import backtracing / individual function -> callers -> full system |

```
Example: Structure axis cross-validation

TD: "Found 3 entry points in src/auth/"
BU: "Only 2 are actually imported; login.ts is dead code"
-> Discrepancy found -> high-confidence intel
```

---

## Level System

| Level     | Squad Setup  | Assignment                                        | Characteristics                          |
| :-------- | :----------- | :------------------------------------------------ | :--------------------------------------- |
| **Quick** | 1 squad (2)  | 1 squad -> all 3 axes                             | Generalist: fast sweep of everything     |
| **Deep**  | 2 squads (4) | Squad A -> Structure+Domain, Squad B -> Expansion | Balanced: deep internal + external cover |

### When to use which level?

- **Quick**: "What's in here?" -- fast status check, simple file location
- **Deep**: "I need to properly understand this module" -- pre-refactoring research, bug root cause, blast radius analysis

---

## Usage

```
/explore <path> [--deep]
```

**Examples:**

```bash
/explore src/auth                    # Quick (default)
/explore src/auth --deep             # Deep
```

---

## Workflow

```
1. Dispatch Investigators (Parallel) -- 2-4 based on level
   Each Investigator saves results to file and returns path only
     |
2. Dispatch Synthesizer (Sequential) -- after all Investigators complete
   Reads all Investigator files, cross-validates, generates consolidated report
     |
3. Orchestrator reports paths only
```

---

## Implementation

### 1. Dispatch Protocol

Before dispatching Investigators, read the language configuration:

```bash
LANGUAGE=$(cat ~/.claude/LANGUAGE.md 2>/dev/null | head -1)
# Default to "English" if file is missing or empty
```

Based on the specified Level, invoke **all Investigators simultaneously (Parallel)**.
Every Investigator prompt **must include the output path and filename**.

**Parallel dispatch requirements (mandatory):**

- Dispatch all Investigator Tasks in a **single orchestrator response**
- Every Investigator Task **must** include `run_in_background: true`
- Do not invoke Synthesizer until **all dispatched Investigators** are complete

---

#### Quick: Generalist (1 squad = 2 agents)

One squad covers all 3 axes. Broad and shallow, fast reconnaissance.

```typescript
// Squad A: All 3 axes
Task({
  subagent_type: "investigator",
  description: "Squad-A TD: Full reconnaissance (Top-Down)",
  prompt: `
## Output Language
{language}

TARGET: {target}
ROLE: Squad-A Top-Down Scout
AXES: Structure + Domain + Expansion (all 3 axes)

MISSION:
Scout all 3 axes from top to bottom.

1. **Structure**: Directory structure -> key files -> identify entry points
2. **Domain**: Business purpose of this module -> core use cases -> data flow
3. **Expansion**: External modules that import this one -> blast radius

No prose. Facts only, bulleted format.

## Filename
investigator.01.md

## Output Path
{{SESSION_DIR}}/explore/
  `,
  run_in_background: true,
});

Task({
  subagent_type: "investigator",
  description: "Squad-A BU: Full reconnaissance (Bottom-Up)",
  prompt: `
## Output Language
{language}

TARGET: {target}
ROLE: Squad-A Bottom-Up Scout
AXES: Structure + Domain + Expansion (all 3 axes)

MISSION:
Scout all 3 axes from bottom to top.

1. **Structure**: Backtrace imports -> inter-module connections -> identify external dependencies
2. **Domain**: Individual function/class roles -> collect domain terminology -> infer business rules
3. **Expansion**: What this module depends on -> dependency chain -> potential coupling

No prose. Facts only, bulleted format.

## Filename
investigator.02.md

## Output Path
{{SESSION_DIR}}/explore/
  `,
  run_in_background: true,
});
```

---

#### Deep: Balanced (2 squads = 4 agents)

- **Squad A**: Structure + Domain (internal focus)
- **Squad B**: Expansion (external connections focus)

```typescript
// Squad A: Structure + Domain
Task({
  subagent_type: "investigator",
  description: "Squad-A TD: Structure + Domain (Top-Down)",
  prompt: `
## Output Language
{language}

TARGET: {target}
ROLE: Squad-A Top-Down (Internal Focus)
AXES: Structure + Domain

MISSION:
1. **Structure**: Directory -> files -> entry points -> identify core modules
2. **Domain**: Business flow start -> key use cases -> data transformation process

No prose. Facts only, bulleted format.

## Filename
investigator.01.md

## Output Path
{{SESSION_DIR}}/explore/
  `,
  run_in_background: true,
});

Task({
  subagent_type: "investigator",
  description: "Squad-A BU: Structure + Domain (Bottom-Up)",
  prompt: `
## Output Language
{language}

TARGET: {target}
ROLE: Squad-A Bottom-Up (Internal Focus)
AXES: Structure + Domain

MISSION:
1. **Structure**: Backtrace imports -> inter-module dependencies -> circular reference check
2. **Domain**: Individual function roles -> domain terminology -> business rules/constraints

No prose. Facts only, bulleted format.

## Filename
investigator.02.md

## Output Path
{{SESSION_DIR}}/explore/
  `,
  run_in_background: true,
});

// Squad B: Expansion
Task({
  subagent_type: "investigator",
  description: "Squad-B TD: Expansion (Top-Down)",
  prompt: `
## Output Language
{language}

TARGET: {target}
ROLE: Squad-B Top-Down (External Focus)
AXIS: Expansion

MISSION:
Trace the **consumers** of this module.
- Who imports this module?
- Which features call it?
- What is the blast radius on change?

No prose. Facts only, bulleted format.

## Filename
investigator.03.md

## Output Path
{{SESSION_DIR}}/explore/
  `,
  run_in_background: true,
});

Task({
  subagent_type: "investigator",
  description: "Squad-B BU: Expansion (Bottom-Up)",
  prompt: `
## Output Language
{language}

TARGET: {target}
ROLE: Squad-B Bottom-Up (External Focus)
AXIS: Expansion

MISSION:
Trace the **dependencies** of this module.
- What does this module import?
- What external library dependencies exist?
- What is the depth and potential risk of the dependency chain?

No prose. Facts only, bulleted format.

## Filename
investigator.04.md

## Output Path
{{SESSION_DIR}}/explore/
  `,
  run_in_background: true,
});
```

---

### 2. Dispatch Synthesizer (Sequential)

After all Investigators complete, invoke the Synthesizer.
This follows the same pattern as the audit skill's Synthesizer dispatch.

```typescript
// Collect Investigator file paths (returned by each Investigator).
// The orchestrator parses "Saved: {path}" from each Investigator's return message and assembles the list below dynamically.

Task({
  subagent_type: "synthesizer",
  description: "Synthesizing exploration results",
  prompt: `
## Output Language
{language}

## Mode
explore

## Exploration Target
{target}

## Source Files
- {{SESSION_DIR}}/explore/investigator.01.md
- {{SESSION_DIR}}/explore/investigator.02.md
(... list all files generated by Investigators. Quick: 2 files, Deep: 4 files)

## Output Path
{{SESSION_DIR}}/explore/
  `,
});
```

**Note:** The source file list uses actual paths returned by the Investigators. The filenames above are examples; the orchestrator dynamically assembles the list by parsing each Investigator's return message for the "Saved: {path}" pattern. If an Investigator fails to save a file and returns text directly instead, inline that content into the Synthesizer prompt as a fallback.

---

### 3. Final Output (Orchestrator Output)

```
**[Investigator]** -- returned
**[Synthesizer]** -- returned

**Report** -- `{{SESSION_DIR}}/explore/synthesis.{nn}.md`
**Detail** -- `{{SESSION_DIR}}/explore/investigator.*.md`
```

**Notes**:

- Investigators save files directly (orchestrator does not save)
- Synthesizer cross-validates and generates the consolidated report
- Orchestrator does not relay detailed content
- Direct users to reference the files
