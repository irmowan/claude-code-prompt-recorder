#!/usr/bin/env python3
"""
Claude Code Prompt Recorder Hook
Records each user prompt with a timestamp to prompt_log.txt in the project directory.
"""
import json
import os
import sys
from datetime import datetime


def main():
    # Load input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    prompt = input_data.get("user_prompt", "") or input_data.get("prompt", "")
    session_id = input_data.get("session_id", "unknown")
    cwd = input_data.get("cwd", os.getcwd())

    # Skip empty prompts
    if not prompt.strip():
        output_continue()
        sys.exit(0)

    # Record the prompt
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    claude_dir = os.path.join(cwd, ".claude")
    os.makedirs(claude_dir, exist_ok=True)
    log_file = os.path.join(claude_dir, "prompt_log.txt")

    log_entry = f"[{timestamp}] {prompt}\n"

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except OSError as e:
        print(f"Warning: Failed to write prompt log: {e}", file=sys.stderr)

    # Pass through without modifying the prompt
    output_continue()


def output_continue():
    """Output empty JSON to let the prompt pass through unchanged."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit"
        }
    }
    print(json.dumps(output))
