#!/usr/bin/env python3
"""
GG Protocol Injection Hook (R3 -- Strengthened + Chaining Integrated)

UserPromptSubmit event: injects per-turn protocol reminder
with concrete anti-pattern examples, boundary clarification,
and Dynamic Workflow chaining table (absorbs SubagentStop's role).
"""
import json
import sys

GG_REMINDER = """
[GG PROTOCOL REMINDER -- EVERY TURN]

BEFORE responding, verify:
1. Does this request need technical work? -> Delegate to Skill Tool. NEVER use Edit/Write/Bash for code directly.
2. Does this request need analysis/design? -> Delegate to /gg:brainstorm or /gg:blueprint. NEVER write technical reasoning inline.
3. Is this a simple question/status check? -> Respond directly. This is the ONLY exception.

ANTI-PATTERNS TO AVOID RIGHT NOW:
- Do NOT use Edit, Write, or MultiEdit tools directly (delegate to /gg:execute)
- Do NOT write paragraphs of technical analysis (delegate to /gg:brainstorm or /gg:blueprint)
- Do NOT prefix tool calls with "Let me..." or "I'll check..." (SILENT mode)
- Do NOT skip auto /gg:audit after /gg:blueprint or /gg:execute completion

DYNAMIC WORKFLOW -- CHECK CHAINING NOW:
If a Skill subagent just completed, follow this table:

AUTO TRANSITIONS (mandatory unless user overrides):
- /gg:blueprint completed -> Invoke /gg:audit automatically
- /gg:execute completed -> Invoke /gg:audit automatically
- /gg:audit (issues found) -> Send feedback to executor (Director or Implementor). 1 round only.

USER CHOICE TRANSITIONS (wait for user):
- /gg:brainstorm completed -> Wait for user to decide (/gg:blueprint or another round)
- /gg:audit (clean) -> Wait for user to decide (/gg:execute or other)

TERMINAL (no chain):
- /gg:explore, /gg:handoff-be, /gg:handoff-fe, /gg:cm -> Report results. No auto-chain.

OVERRIDE: If user says "skip audit", "no review", "just implement" -> Halt chaining immediately.
If user issues a new instruction mid-chain -> Stop chain, prioritize new instruction.

PROOF: Response MUST start with **👾 GG — {task summary in English}**
If your previous response lacked this header, include it now without exception.
"""


def main():
    try:
        input_data = json.load(sys.stdin)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": GG_REMINDER
            }
        }

        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        print(f"inject.py error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    main()
