"""PreToolUse guard for the local Claude session: always ask before deleting, spending or pushing.

本地 Claude 對話的防護：刪除檔案或資料夾、會花錢的翻譯、git push 之前，一律先跳出確認。
Reads the hook event JSON on stdin. When a shell command matches a rule it prints a
PreToolUse "ask" decision with a Chinese reason, so the user is prompted even if an allow
rule in .claude/settings.json covers the command. Anything else: no output, exit 0.
Deleting through the GUI (computer use) is not visible here; CLAUDE.md covers that.
"""

from __future__ import annotations

import json
import re
import sys

RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(?<![\w.-])rm\s", re.I), "刪除檔案或資料夾（rm）"),
    (re.compile(r"(?<![\w.-])(rmdir|rd)\s", re.I), "刪除資料夾（rmdir/rd）"),
    (re.compile(r"(?<![\w.-])(del|erase)\s", re.I), "刪除檔案（del/erase）"),
    (re.compile(r"\bRemove-Item\b", re.I), "刪除檔案或資料夾（Remove-Item）"),
    (re.compile(r"rmtree|os\.remove|os\.unlink|\.unlink\(|send2trash", re.I), "用 Python 刪除檔案"),
    (re.compile(r"robocopy\b.*\s/(mir|purge)\b", re.I), "robocopy /MIR 或 /PURGE 會刪除目的地檔案"),
    (re.compile(r"(?:^|[;&|]\s*)(?:format\s+[a-z]:|diskpart\b|Format-Volume\b)", re.I), "磁碟格式化或分割"),
    (re.compile(r"\bgit\s+(reset\s+--hard|clean\b)", re.I), "丟棄本機檔案的 git 操作"),
    (re.compile(r"\bgit\s+push\b", re.I), "推送到 GitHub（倉庫是公開的，確認沒有夾帶報告或金鑰）"),
    (re.compile(r"llm_translate\.py\s+run\b(?=.*--yes)", re.I | re.S), "會呼叫付費的 Claude API（花錢）"),
]


def commands(tool_input) -> list[str]:
    """All string values of the tool input (Bash and PowerShell both use 'command')."""
    if isinstance(tool_input, str):
        return [tool_input]
    if isinstance(tool_input, dict):
        out = []
        for v in tool_input.values():
            out += commands(v)
        return out
    if isinstance(tool_input, list):
        out = []
        for v in tool_input:
            out += commands(v)
        return out
    return []


def reasons_for(text: str) -> list[str]:
    return [why for pat, why in RULES if pat.search(text)]


def decision(reasons: list[str]) -> dict:
    return {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": "需要你確認：" + "；".join(dict.fromkeys(reasons)),
    }}


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if event.get("tool_name") not in ("Bash", "PowerShell"):
        return 0
    found: list[str] = []
    for cmd in commands(event.get("tool_input", {})):
        found += reasons_for(cmd)
    if found:
        sys.stdout.write(json.dumps(decision(found)))  # ASCII only: survives a cp950 console
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
