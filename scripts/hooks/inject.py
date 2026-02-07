#!/usr/bin/env python3
"""
GG Protocol Injection Hook (R3 -- Strengthened + Chaining Integrated)

UserPromptSubmit event: injects per-turn protocol reminder
with concrete anti-pattern examples, boundary clarification,
and Dynamic Workflow chaining table (absorbs SubagentStop's role).
"""
import json
import os
import sys

def _iter_config_candidates(input_data):
    """Yield possible .gg/config.json paths in priority order."""
    roots = []

    payload_cwd = input_data.get("cwd")
    if isinstance(payload_cwd, str) and payload_cwd.strip():
        roots.append(payload_cwd.strip())

    env_project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "").strip()
    if env_project_dir:
        roots.append(env_project_dir)

    roots.append(os.getcwd())

    seen = set()
    for root in roots:
        abs_root = os.path.abspath(root)
        if abs_root in seen:
            continue
        seen.add(abs_root)

        current = abs_root
        while True:
            yield os.path.join(current, ".gg", "config.json")
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent


def read_backend_config(input_data):
    """Read .gg/config.json for backend status injection."""
    checked = set()
    for config_path in _iter_config_candidates(input_data):
        if config_path in checked:
            continue
        checked.add(config_path)

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (FileNotFoundError, PermissionError, OSError, json.JSONDecodeError):
            continue

        backends = config.get("backends", {})
        gemini = backends.get("gemini", False)
        codex = backends.get("codex", False)
        parts = ["Claude"]
        if gemini:
            parts.append("Gemini")
        if codex:
            parts.append("Codex")
        return " + ".join(parts)

    return "Claude only"


GG_REMINDER_TEMPLATE = """
[GG PROTOCOL REMINDER -- EVERY TURN]

AI BACKENDS: {backend_status}. Dispatch agents accordingly.

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

PROOF: Response MUST start with **GG -- {{task summary in English}}**
If your previous response lacked this header, include it now without exception.
"""


def main():
    try:
        input_data = json.load(sys.stdin)

        backend_status = read_backend_config(input_data)
        reminder = GG_REMINDER_TEMPLATE.format(backend_status=backend_status)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": reminder
            }
        }

        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        print(f"inject.py error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    main()
