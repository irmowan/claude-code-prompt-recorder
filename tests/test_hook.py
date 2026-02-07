#!/usr/bin/env python3
"""
Tests for the prompt-recorder hook
Tests JSON output format, prompt recording, empty prompt handling, and special characters.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Path to the hook script
HOOK_SCRIPT = Path(__file__).parent.parent / "scripts" / "record-prompt.py"


def run_hook(prompt, cwd=None):
    """Run the hook script with given prompt and return parsed output"""
    input_data = {"user_prompt": prompt}
    if cwd:
        input_data["cwd"] = cwd

    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=json.dumps(input_data),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise Exception(f"Hook failed (exit {result.returncode}): {result.stderr}")

    return json.loads(result.stdout)


def test_json_output_format():
    """Test that output follows correct JSON schema"""
    with tempfile.TemporaryDirectory() as tmpdir:
        output = run_hook("test prompt", cwd=tmpdir)

        assert isinstance(output, dict)
        assert "hookSpecificOutput" in output
        assert isinstance(output["hookSpecificOutput"], dict)

        hook_output = output["hookSpecificOutput"]
        assert "hookEventName" in hook_output
        assert hook_output["hookEventName"] == "UserPromptSubmit"

        # Should NOT have additionalContext (pass-through)
        assert "additionalContext" not in hook_output

    print("PASS: JSON output format")


def test_prompt_recorded():
    """Test that prompt is written to prompt_log.txt"""
    with tempfile.TemporaryDirectory() as tmpdir:
        run_hook("fix the bug in auth.ts", cwd=tmpdir)

        log_file = os.path.join(tmpdir, ".claude", "prompt_log.txt")
        assert os.path.exists(log_file), ".claude/prompt_log.txt should be created"

        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "fix the bug in auth.ts" in content
        # Verify timestamp format [YYYY-MM-DD HH:MM:SS]
        assert content.startswith("[")
        assert "]" in content

    print("PASS: Prompt recorded to file")


def test_multiple_prompts_appended():
    """Test that multiple prompts are appended, not overwritten"""
    with tempfile.TemporaryDirectory() as tmpdir:
        run_hook("first prompt", cwd=tmpdir)
        run_hook("second prompt", cwd=tmpdir)
        run_hook("third prompt", cwd=tmpdir)

        log_file = os.path.join(tmpdir, ".claude", "prompt_log.txt")
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        assert len(lines) == 3, f"Expected 3 lines, got {len(lines)}"
        assert "first prompt" in lines[0]
        assert "second prompt" in lines[1]
        assert "third prompt" in lines[2]

    print("PASS: Multiple prompts appended")


def test_empty_prompt_skipped():
    """Test that empty prompts are not recorded"""
    with tempfile.TemporaryDirectory() as tmpdir:
        output = run_hook("", cwd=tmpdir)

        log_file = os.path.join(tmpdir, ".claude", "prompt_log.txt")
        assert not os.path.exists(log_file), ".claude/prompt_log.txt should not be created for empty prompt"

        # Should still output valid JSON
        assert "hookSpecificOutput" in output

    print("PASS: Empty prompt skipped")


def test_whitespace_only_prompt_skipped():
    """Test that whitespace-only prompts are not recorded"""
    with tempfile.TemporaryDirectory() as tmpdir:
        output = run_hook("   \n\t  ", cwd=tmpdir)

        log_file = os.path.join(tmpdir, ".claude", "prompt_log.txt")
        assert not os.path.exists(log_file), ".claude/prompt_log.txt should not be created for whitespace-only prompt"

        assert "hookSpecificOutput" in output

    print("PASS: Whitespace-only prompt skipped")


def test_special_characters():
    """Test handling of special characters in prompts"""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompt = 'fix the "bug" in user\'s code & database <script>alert(1)</script>'
        run_hook(prompt, cwd=tmpdir)

        log_file = os.path.join(tmpdir, ".claude", "prompt_log.txt")
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert '"bug"' in content
        assert "&" in content

    print("PASS: Special characters handled")


def test_unicode_prompt():
    """Test handling of unicode/CJK characters"""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompt = "帮我写一个排序函数"
        run_hook(prompt, cwd=tmpdir)

        log_file = os.path.join(tmpdir, ".claude", "prompt_log.txt")
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "帮我写一个排序函数" in content

    print("PASS: Unicode/CJK characters handled")


def test_multiline_prompt():
    """Test handling of multiline prompts"""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompt = "refactor the auth system\nto use async/await\nand add error handling"
        run_hook(prompt, cwd=tmpdir)

        log_file = os.path.join(tmpdir, ".claude", "prompt_log.txt")
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "refactor the auth system" in content

    print("PASS: Multiline prompt handled")


def test_fallback_prompt_field():
    """Test that the script falls back to 'prompt' field if 'user_prompt' is missing"""
    input_data = json.dumps({"prompt": "fallback test"})

    with tempfile.TemporaryDirectory() as tmpdir:
        input_with_cwd = json.dumps({"prompt": "fallback test", "cwd": tmpdir})

        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=input_with_cwd,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        log_file = os.path.join(tmpdir, ".claude", "prompt_log.txt")
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "fallback test" in content

    print("PASS: Fallback to 'prompt' field")


def run_all_tests():
    """Run all tests"""
    tests = [
        test_json_output_format,
        test_prompt_recorded,
        test_multiple_prompts_appended,
        test_empty_prompt_skipped,
        test_whitespace_only_prompt_skipped,
        test_special_characters,
        test_unicode_prompt,
        test_multiline_prompt,
        test_fallback_prompt_field,
    ]

    print(f"Running {len(tests)} hook tests...\n")

    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed.append((test.__name__, e))

    print(f"\n{'=' * 60}")
    if failed:
        print(f"FAILED: {len(failed)}/{len(tests)} tests failed")
        for name, error in failed:
            print(f"  - {name}: {error}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {len(tests)} tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    run_all_tests()
