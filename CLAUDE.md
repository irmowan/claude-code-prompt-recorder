# Claude Code Prompt Recorder

A UserPromptSubmit hook plugin that records every user prompt with a timestamp to `prompt_log.txt` in the project directory.

**Core functionality:**
- Intercepts prompts via UserPromptSubmit hook
- Records timestamp + prompt text to `prompt_log.txt`
- Pass-through only — does not modify prompts
- Skips empty prompts

## Architecture

**Hook Layer (hooks/hooks.json):**
- Registers `UserPromptSubmit` event with `matcher: "*"`
- Invokes `scripts/record-prompt.py` via command hook
- Timeout: 10 seconds

**Script (scripts/record-prompt.py):**
- Reads JSON from stdin (`user_prompt`, `cwd`, `session_id`)
- Appends `[YYYY-MM-DD HH:MM:SS] <prompt>` to `<cwd>/prompt_log.txt`
- Outputs pass-through JSON with empty `hookSpecificOutput`

**Directory structure:**
- `scripts/` - Hook script
- `hooks/` - Hook configuration
- `tests/` - Test suite
- `.claude-plugin/` - Plugin metadata

## Build Commands

**Testing:**
- Run all tests: `python -m pytest tests/`
- Run hook tests: `python -m pytest tests/test_hook.py`

## Conventions

**Hook output format:**
- JSON structure: `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit"}}`
- No `additionalContext` — prompt is not modified
- Exit code 0 for all success paths

**Log format:**
- One line per prompt: `[YYYY-MM-DD HH:MM:SS] <prompt text>`
- UTF-8 encoding, append mode
- File: `prompt_log.txt` in working directory
