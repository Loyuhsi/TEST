"""The PreToolUse guard must ask before deleting, spending or pushing, and stay silent otherwise."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

GUARD = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "guard.py"


def run(tool: str, command: str) -> dict | None:
    event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": {"command": command}}
    out = subprocess.run([sys.executable, str(GUARD)], input=json.dumps(event), capture_output=True,
                         text=True, encoding="utf-8", check=True)
    return json.loads(out.stdout) if out.stdout.strip() else None


@pytest.mark.parametrize("tool,cmd", [
    ("Bash", 'rm -rf "D:/MV"'),
    ("Bash", "rm D:/PM/downloads/x.7z"),
    ("Bash", 'cmd /c rmdir /s /q "D:\\MV"'),
    ("Bash", 'cmd //c "rd /s /q D:\\WJ-Downloads"'),
    ("Bash", "cmd /c del /q D:\\PM\\overwrite\\*"),
    ("PowerShell", 'Remove-Item -Recurse -Force "D:\\Nolvus"'),
    ("Bash", "python -c \"import shutil; shutil.rmtree('D:/MV')\""),
    ("Bash", "robocopy D:/a D:/b /MIR"),
    ("Bash", "git push origin claude/sharp-faraday-b8ax3h"),
    ("Bash", "git reset --hard HEAD~1"),
    ("Bash", 'python tools/zh/llm_translate.py run --work "D:/PM/zh-work" --yes'),
    ("PowerShell", "python tools\\zh\\llm_translate.py run --mode batch --yes"),
])
def test_asks(tool, cmd):
    res = run(tool, cmd)
    assert res is not None, cmd
    h = res["hookSpecificOutput"]
    assert h["hookEventName"] == "PreToolUse" and h["permissionDecision"] == "ask"
    assert h["permissionDecisionReason"].startswith("需要你確認")


@pytest.mark.parametrize("tool,cmd", [
    ("Bash", 'python tools/preflight.py --install-drive D:'),
    ("Bash", 'python tools/harvest.py --from mv --instance "D:/MV" --pm "D:/PM" --mo2-and-tools --apply'),
    ("Bash", 'python tools/zh/llm_translate.py estimate --work "D:/PM/zh-work"'),
    ("Bash", 'python tools/zh/llm_translate.py run --work "D:/PM/zh-work"'),
    ("Bash", "git pull origin claude/sharp-faraday-b8ax3h"),
    ("Bash", "git log --format=%h -3"),
    ("Bash", "python -m json.tool .claude/settings.json"),
    ("PowerShell", "Get-ChildItem D:\\PM\\mods | Measure-Object"),
    ("Bash", "python tools/build_instance.py create --pm D:/PM --model x"),
])
def test_allows(tool, cmd):
    assert run(tool, cmd) is None, cmd


def test_ignores_other_tools_and_bad_input():
    event = {"tool_name": "Read", "tool_input": {"file_path": "rm -rf /"}}
    out = subprocess.run([sys.executable, str(GUARD)], input=json.dumps(event), capture_output=True, text=True)
    assert out.stdout == "" and out.returncode == 0
    out = subprocess.run([sys.executable, str(GUARD)], input="not json", capture_output=True, text=True)
    assert out.stdout == "" and out.returncode == 0
