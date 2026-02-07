# Claude Code Prompt Recorder

A Claude Code plugin that records every user prompt with a timestamp to `prompt_log.txt` in the project directory. Useful for reviewing your interaction history, tracking prompt patterns, and building a personal prompt knowledge base.

## What It Does

Intercepts every prompt submitted to Claude Code via the `UserPromptSubmit` hook, and appends it with a timestamp to `prompt_log.txt` in the current working directory. The prompt is passed through unchanged — recording is completely transparent with zero impact on your workflow.

**Log format:**
```
[2026-02-07 14:30:15] 帮我写一个排序函数
[2026-02-07 14:32:08] Fix the TypeError in src/utils.ts line 42
[2026-02-07 14:35:22] Refactor the auth module to use async/await
```

## Installation

### Option 1: Via Marketplace (Recommended)

1. Add the marketplace:
```bash
claude plugin marketplace add irmowan/claude-code-prompt-recorder
```

2. Install the plugin:
```bash
claude plugin install prompt-recorder@irmowan-marketplace
```

3. Restart Claude Code

Verify installation with `/plugin` command. You should see the `prompt-recorder` plugin listed.

### Option 2: Direct Install

```bash
claude plugin install /path/to/claude-code-prompt-recorder
```

Then restart Claude Code.

## Usage

No configuration needed. Once installed, every prompt you submit is automatically recorded.

```bash
# Just use Claude Code as usual
claude "fix the bug in auth.ts"
# → [2026-02-07 10:00:01] fix the bug in auth.ts  is appended to prompt_log.txt

claude "add unit tests for the User model"
# → [2026-02-07 10:05:33] add unit tests for the User model  is appended to prompt_log.txt
```

The `prompt_log.txt` file is created in the current working directory (the project root where Claude Code is running).

## Log File Location

- **Path:** `<project_root>/prompt_log.txt`
- **Format:** `[YYYY-MM-DD HH:MM:SS] <prompt text>`
- **Encoding:** UTF-8
- **Mode:** Append-only (existing logs are never overwritten)

## Architecture

```
claude-code-prompt-recorder/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── hooks/
│   └── hooks.json           # UserPromptSubmit hook registration
├── scripts/
│   └── record-prompt.py     # Core recording script
└── tests/
    └── test_hook.py         # Test suite
```

**Hook script (`scripts/record-prompt.py`):**
- Reads JSON input from stdin (Claude Code hook protocol)
- Extracts `user_prompt` and `cwd` fields
- Appends timestamped entry to `prompt_log.txt`
- Outputs pass-through JSON (does not modify the prompt)
- Skips empty prompts silently

## FAQ

**Does this modify my prompts?**
No. The hook only records and passes through — your prompts reach Claude unchanged.

**Where is the log file?**
In the working directory where Claude Code is running, typically your project root.

**Will this slow down Claude Code?**
No. The script runs in under 10ms (file append only).

**Can I exclude certain prompts?**
Not in the current version. All non-empty prompts are recorded.

**Is `prompt_log.txt` gitignored?**
The plugin's own `.gitignore` excludes it. You may want to add `prompt_log.txt` to your project's `.gitignore` as well.

## License

MIT
