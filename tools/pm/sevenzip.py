"""Thin wrapper around the 7-Zip command line: list archive contents and extract.

7-Zip 命令列包裝：列出壓縮檔內容、解壓到指定資料夾。
Console output is forced to UTF-8 (-sccUTF-8) so non-ASCII file names survive the code page,
and stdin is closed so a password-protected archive fails instead of waiting for input.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .fsutil import long_path

DEFAULT_PATHS = (Path(r"C:\Program Files\7-Zip\7z.exe"), Path(r"C:\Program Files (x86)\7-Zip\7z.exe"))
SEPARATOR = "----------"
TIMEOUT = 3600


class SevenZipError(Exception):
    """7-Zip is missing or could not read / extract an archive."""


@dataclass(frozen=True)
class Entry:
    path: str      # forward slashes, relative to the archive root
    is_dir: bool
    size: int = 0


def find_7z() -> Path:
    found = shutil.which("7z")
    if found:
        return Path(found)
    for cand in DEFAULT_PATHS:
        if cand.exists():
            return cand
    raise SevenZipError("找不到 7-Zip（7z.exe），請先安裝 7-Zip")


def _is_dir(fields: dict[str, str]) -> bool:
    if fields.get("Folder") == "+":
        return True
    # Windows attributes ("D", "RD") or a unix mode string ("drwxr-xr-x")
    return any((t.isupper() and "D" in t) or (len(t) == 10 and t.startswith("d"))
               for t in fields.get("Attributes", "").split())


def _entry(fields: dict[str, str]) -> Entry | None:
    path = fields.get("Path", "").replace("\\", "/").rstrip("/")
    if not path:
        return None
    try:
        size = int(fields.get("Size") or 0)
    except ValueError:
        size = 0
    return Entry(path, _is_dir(fields), size)


def parse_slt(text: str) -> list[Entry]:
    """Parse `7z l -slt` output: records follow the '----------' line, one 'Key = value' each."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    try:
        start = lines.index(SEPARATOR) + 1
    except ValueError:
        return []
    entries: list[Entry] = []
    fields: dict[str, str] = {}
    for line in lines[start:]:
        key, sep, value = line.partition(" = ")
        if not sep:
            continue
        if key == "Path" and fields:
            entries.append(_entry(fields))
            fields = {}
        fields[key] = value
    if fields:
        entries.append(_entry(fields))
    return [e for e in entries if e is not None]


def _run(args: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run([str(find_7z()), *args], capture_output=True,
                              stdin=subprocess.DEVNULL, timeout=TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise SevenZipError(f"7-Zip 無法執行：{e}") from None


def _failure(r: subprocess.CompletedProcess) -> str:
    err = (r.stderr or b"").decode("utf-8", errors="replace").strip()
    last = err.splitlines()[-1] if err else "（沒有訊息）"
    return f"7-Zip 結束代碼 {r.returncode}：{last}"


def list_entries(archive: Path) -> list[Entry]:
    r = _run(["l", "-slt", "-sccUTF-8", str(archive)])
    if r.returncode != 0:
        raise SevenZipError(_failure(r))
    return parse_slt(r.stdout.decode("utf-8", errors="replace"))


def extract(archive: Path, dest: Path) -> None:
    Path(dest).mkdir(parents=True, exist_ok=True)
    # \\?\ prefix: deep mod trees can pass 260 characters under the staging folder
    r = _run(["x", "-y", "-bd", "-sccUTF-8", f"-o{long_path(dest)}", str(archive)])
    if r.returncode != 0:
        raise SevenZipError(_failure(r))


def extract_args(archive: Path, dest: Path, listfile: Path) -> list[str]:
    """Arguments for extracting only the members named in listfile (UTF-8, one per line)."""
    return ["x", "-y", "-bd", "-sccUTF-8", "-scsUTF-8", f"-o{long_path(dest)}", str(archive), f"@{listfile}"]


def extract_files(archive: Path, dest: Path, members: list[str]) -> None:
    """Extract only the given members (paths as list_entries reports them), keeping their folders.

    The names go through a list file so hundreds of members never hit the command-line limit.
    """
    Path(dest).mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(suffix=".txt", prefix="7z-list-")
    listfile = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write("".join(m.replace("/", os.sep) + "\n" for m in members))
        r = _run(extract_args(archive, dest, listfile))
    finally:
        listfile.unlink(missing_ok=True)
    if r.returncode != 0:
        raise SevenZipError(_failure(r))
