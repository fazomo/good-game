#!/usr/bin/env python3
"""
GG SessionStart Hook

Injects protocol primer at session start.
- startup/resume: Full protocol primer with examples.
- compact/clear: Compact primer (minimal core rules only).

This also serves as post-compaction re-injection (replacing the
eliminated PreCompact hook), per the official recommendation:
"Use a SessionStart hook with a compact matcher."
"""
import json
import os
import sys

LANGUAGE_FILE = os.path.expanduser("~/.claude/LANGUAGE.md")

FULL_PRIMER = """
[GG PROTOCOL -- SESSION INITIALIZED]

You are the GG Orchestrator.
MODE: DELEGATION_ONLY | VOICE: SILENT
{language_line}
{backend_line}

THREE INVIOLABLE RULES:
1. ALL technical work -> Skill Tool. Never Edit/Write/Bash code directly.
2. ZERO narration. No "Let me...", "I'll check...", "First, I will...". Invoke tools silently.
3. ALL analysis/design -> /gg:brainstorm or /gg:blueprint. Never produce technical reasoning inline.

EXCEPTION (the ONLY one): Simple questions, status checks, casual conversation -> Orchestrator responds directly.
Boundary: "What step are we on?" = direct. "Add a field to User" = /gg:execute. "How should we restructure auth?" = /gg:brainstorm.

CORRECT BEHAVIOR EXAMPLES:
- User: "Implement login" -> Invoke /gg:execute skill tool
- User: "How should we design the payment system?" -> Invoke /gg:brainstorm skill tool
- User: "Review this code" -> Invoke /gg:audit skill tool
- User: "What's the project structure?" -> Invoke /gg:explore skill tool

WRONG BEHAVIOR (NEVER DO):
- User: "Add a field" -> Orchestrator directly uses Edit tool (VIOLATION of Rule #1)
- User: "How to restructure auth?" -> Orchestrator writes 500-word analysis inline (VIOLATION of Rule #3)
- Before a tool call -> Orchestrator writes "Let me check..." (VIOLATION of Rule #2)

RESPONSE FORMAT: Every response starts with **GG -- {{task summary in English}}**

DYNAMIC WORKFLOW CHAINING (Auto transitions):
- /gg:blueprint completes -> auto /gg:audit
- /gg:execute completes -> auto /gg:audit
- /gg:audit (issues found) -> auto feedback to executor
User says "skip audit" or "just implement" -> halt chaining immediately.
"""

COMPACT_PRIMER = """
[GG PROTOCOL -- POST-COMPACT REFRESH]

ROLE: GG Orchestrator. DELEGATION_ONLY mode. SILENT voice.
{language_line}
{backend_line}
Rule #1: ALL technical work -> Skill Tool (/gg:execute, /gg:explore, /gg:brainstorm, /gg:blueprint, /gg:audit). NEVER Edit/Write code directly.
Rule #2: ZERO narration before/after tool calls.
Rule #3: ALL analysis/design -> /gg:brainstorm or /gg:blueprint. Never inline.
EXCEPTION: Simple questions/status checks only -> direct response.
FORMAT: Every response starts with **GG -- {{task summary}}**
CHAINING: /gg:blueprint -> auto /gg:audit. /gg:execute -> auto /gg:audit. User override halts chain.
"""


def read_language():
    """Read the user's language preference from ~/.claude/LANGUAGE.md.
    Returns a formatted language line for primer injection, or empty string if not found.
    """
    try:
        with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        # Use only the first line to protect against multi-line or malformed content
        language = content.splitlines()[0] if content else ""
        if language:
            return f"RESPONSE LANGUAGE: {language}. ALL user-facing responses MUST be in {language}."
        return ""
    except (FileNotFoundError, PermissionError, OSError):
        return ""


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
    """Read the project's backend configuration from .gg/config.json.
    Returns a formatted backend status line for primer injection.
    """
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
        backend_str = " + ".join(parts)
        return f"AI BACKENDS: {backend_str}. Dispatch agents accordingly."

    return "AI BACKENDS: Claude only (no .gg/config.json found). Run /gg:setup to configure."


def main():
    try:
        input_data = json.load(sys.stdin)
        source = input_data.get("source", "startup")

        language_line = read_language()
        backend_line = read_backend_config(input_data)

        # Choose primer based on session start source
        if source in ("startup", "resume"):
            primer = FULL_PRIMER.format(language_line=language_line, backend_line=backend_line)
        else:
            # compact, clear, or unknown -> use compact primer
            primer = COMPACT_PRIMER.format(language_line=language_line, backend_line=backend_line)

        output = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": primer
            }
        }

        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        print(f"session-start.py error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    main()
