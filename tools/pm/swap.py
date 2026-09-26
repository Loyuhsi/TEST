"""Swap a freshly unpacked folder in for an MO2 mod folder, with crash recovery.

把解壓好的資料夾換進 MO2 的 mod 資料夾；中途被中斷時，下次執行會先把原資料夾放回去。

MO2 silently drops modlist.txt lines whose folder is missing, so a mod folder must never
stay absent. The old folder is renamed aside and the new one renamed in; a small journal
names both paths until the target exists again. Retries (antivirus scans briefly lock
fresh files) always run with the original folder back in place.
"""

from __future__ import annotations

import os
import shutil
import stat
import sys
import time
from pathlib import Path

from .fsutil import long_path

ATTEMPTS = 5
JUNK_NAMES = frozenset({"desktop.ini", "thumbs.db"})   # Explorer drops these into browsed folders


class SwapError(OSError):
    """The journal is unusable, or the original folder could not be put back."""


def has_content(folder: Path) -> bool:
    """True when the folder holds anything besides Explorer's desktop.ini / Thumbs.db."""
    return any(c.name.lower() not in JUNK_NAMES for c in Path(folder).iterdir())


def _retry(action, attempts: int = ATTEMPTS) -> None:
    for i in range(attempts):
        try:
            action()
            return
        except PermissionError:
            if i == attempts - 1:
                raise
            time.sleep(1 + i)


def _swap_once(src: Path, target: Path, aside: Path) -> None:
    os.rename(target, aside)
    try:
        os.rename(src, target)
    except OSError:
        try:
            _retry(lambda: os.rename(aside, target))
        except OSError as e:
            raise SwapError(f"無法把原資料夾放回 {target}：{e}") from e
        raise


def put_in_place(src: Path, target: Path, aside: Path, journal: Path) -> None:
    """Rename target to aside and src to target; on failure the original target is back."""
    journal.parent.mkdir(parents=True, exist_ok=True)
    journal.write_text(f"{target}\n{aside}\n", encoding="utf-8")
    try:
        _retry(lambda: _swap_once(src, target, aside))
    finally:
        if target.exists():
            journal.unlink(missing_ok=True)


def _norm(path: Path) -> str:
    return os.path.normcase(os.path.abspath(path))


def _inside(path: Path, root: Path) -> bool:
    return _norm(path).startswith(_norm(root).rstrip("\\/") + os.sep)


def recover(journal: Path, mods_dir: Path, staging_root: Path, replaced_root: Path) -> tuple[str, str]:
    """Undo (or confirm) a swap that a killed run left behind.

    Returns (level, message), ("", "") when there was nothing to do. A journal that cannot be
    trusted raises SwapError and nothing is touched. When the parked folder itself is gone, an
    empty folder keeps MO2's modlist line: expected for a parked placeholder (it held nothing
    but Explorer files), a FAIL for content moved to _replaced.
    """
    if not journal.exists():
        return "", ""
    lines = journal.read_text(encoding="utf-8").splitlines() + ["", ""]
    target_s, aside_s = lines[0].strip(), lines[1].strip()
    if not target_s or not aside_s or "\x00" in target_s + aside_s:
        raise SwapError(f"中斷紀錄 {journal} 不完整或損壞，沒有處理")
    target, aside = Path(target_s), Path(aside_s)
    if _norm(target.parent) != _norm(mods_dir):
        raise SwapError(f"中斷紀錄 {journal} 指向 mods 以外的位置，沒有處理")
    parked, replaced = _inside(aside, staging_root), _inside(aside, replaced_root)
    if not (parked or replaced):
        raise SwapError(f"中斷紀錄 {journal} 的暫放位置不在預期的資料夾，沒有處理")
    if target.exists():
        journal.unlink()
        return "INFO", f"{target.name} 已在原位（上次在收尾時中斷）"
    if aside.exists():
        _retry(lambda: os.rename(aside, target))
        journal.unlink()
        return "WARN", f"已把 {target.name} 放回 mods"
    target.mkdir()
    journal.unlink()
    if parked:
        return "WARN", f"暫放的空佔位資料夾不見了，已重建空的 {target.name}"
    return "FAIL", (f"{target.name} 的舊內容不在 _replaced（{aside.name}），"
                    "已先建立空資料夾讓 MO2 保留這一行；請人工確認")


def _writable_retry(func, path, _exc) -> None:
    os.chmod(path, stat.S_IWRITE)
    func(path)


_RMTREE_KW = ({"onexc": _writable_retry} if sys.version_info >= (3, 12)
              else {"onerror": _writable_retry})


def remove_tree(path: Path) -> str:
    """Remove a temporary folder this tool made; return a warning instead of raising."""
    try:
        if Path(path).exists():
            shutil.rmtree(long_path(path), **_RMTREE_KW)
    except OSError as e:
        return f"暫存資料夾沒清掉：{path}（{e}）"
    return ""
