#!/usr/bin/env python3
"""
Claude Code Prompt Recorder Hook
Records each user prompt with a timestamp to .claude/prompt_log.txt in the project directory.
"""
import json
import os
import sys
from datetime import datetime


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    prompt = input_data.get("prompt", "")

    if not prompt.strip():
        sys.exit(0)

    claude_dir = os.path.join(os.getcwd(), ".claude")
    os.makedirs(claude_dir, exist_ok=True)
    log_file = os.path.join(claude_dir, "prompt_log.txt")
    log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {prompt.strip()}\n"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except OSError as e:
        print(f"Warning: Failed to write prompt log: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
