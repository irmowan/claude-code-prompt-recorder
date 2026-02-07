#!/usr/bin/env python3
"""
Claude Code Prompt Recorder Hook
Records each user prompt with a timestamp to prompt_log.txt in the project directory.
"""
import json
import os
import sys
from datetime import datetime


print("hook triggered")
# Load input from stdin
try:
    input_data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
    sys.exit(1)

prompt = input_data.get("prompt", "")
log_file = os.path.join(os.getcwd(), "prompt_log.txt")
log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {prompt.strip()}\n"

try:
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)
except OSError as e:
    print(f"Warning: Failed to write prompt log: {e}", file=sys.stderr)

sys.exit(0)
