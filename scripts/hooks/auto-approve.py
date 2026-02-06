#!/usr/bin/env python3
"""
PreToolUse Auto-Approve Hook

Auto-approves safe operations:
- Write, Edit, MultiEdit tools
- Bash commands starting with "mkdir" (no chaining)

Note: Write is also in permissions.allow; kept here as safety net.
"""
import json
import re
import sys

SAFE_TOOLS = {"Write", "Edit", "MultiEdit"}

# Reject commands with shell chaining operators
CHAIN_PATTERN = re.compile(r'[;&|]')


def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})

        should_approve = False

        if tool_name in SAFE_TOOLS:
            should_approve = True
        elif tool_name == "Bash":
            command = str(tool_input.get("command", "")).strip()
            if command.startswith("mkdir") and not CHAIN_PATTERN.search(command):
                should_approve = True

        if should_approve:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "allow",
                    "permissionDecisionReason": f"Auto-approved: {tool_name}"
                }
            }
            print(json.dumps(output))

        sys.exit(0)

    except Exception as e:
        print(f"auto-approve.py error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    main()
