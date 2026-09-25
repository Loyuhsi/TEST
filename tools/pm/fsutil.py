"""Filesystem helpers: hardlink cloning, disk space, long Windows paths.

檔案系統工具：硬連結複製、磁碟空間、Windows 長路徑。

Hardlinks only work inside one NTFS volume. A hardlinked file keeps its data
after the original path is deleted, which is what lets us delete the source
Nolvus / Mages & Vikings installs once D:\\PM is assembled. Editing a
hardlinked file in place changes every link, so files we intend to edit
(meta.ini, ini files) are copied instead.
"""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

COPY_INSTEAD_OF_LINK = {"meta.ini"}
IS_WINDOWS = os.name == "nt"


def long_path(p: Path | str) -> str:
    """Return a path string safe for >260 char paths on Windows."""
    s = str(Path(p).absolute())
    if IS_WINDOWS and not s.startswith("\\\\?\\"):
        if s.startswith("\\\\"):
            return "\\\\?\\UNC\\" + s[2:]
        return "\\\\?\\" + s
    return s


def same_volume(a: Path, b: Path) -> bool:
    a, b = Path(a), Path(b)
    while not a.exists():
        a = a.parent
    while not b.exists():
        b = b.parent
    return os.stat(a).st_dev == os.stat(b).st_dev


def free_bytes(path: Path) -> int:
    p = Path(path)
    while not p.exists():
        p = p.parent
    return shutil.disk_usage(p).free


def dir_size(path: Path) -> tuple[int, int]:
    """Return (total_bytes, file_count) for a directory tree."""
    total = count = 0
    for root, _dirs, files in os.walk(long_path(path)):
        for f in files:
            try:
                total += os.stat(os.path.join(root, f)).st_size
                count += 1
            except OSError:
                pass
    return total, count


@dataclass
class CloneStats:
    linked: int = 0
    copied: int = 0
    skipped: int = 0
    bytes: int = 0
    errors: list[str] = field(default_factory=list)

    def add(self, other: "CloneStats") -> None:
        self.linked += other.linked
        self.copied += other.copied
        self.skipped += other.skipped
        self.bytes += other.bytes
        self.errors.extend(other.errors)


def clone_tree(src: Path, dst: Path, *, apply: bool, allow_copy_fallback: bool = False,
               copy_names: set[str] = COPY_INSTEAD_OF_LINK, overwrite: bool = False) -> CloneStats:
    """Mirror src into dst using hardlinks (copies for names in copy_names).

    With apply=False nothing is written; the returned stats describe what would happen.
    """
    stats = CloneStats()
    src, dst = Path(src), Path(dst)
    src_l = long_path(src)
    for root, _dirs, files in os.walk(src_l):
        rel = os.path.relpath(root, src_l)
        out_dir = os.path.join(long_path(dst), rel) if rel != "." else long_path(dst)
        if apply:
            os.makedirs(out_dir, exist_ok=True)
        for f in files:
            s = os.path.join(root, f)
            d = os.path.join(out_dir, f)
            try:
                size = os.stat(s).st_size
            except OSError as e:
                stats.errors.append(f"stat {s}: {e}")
                continue
            if os.path.exists(d) and not overwrite:
                stats.skipped += 1
                continue
            stats.bytes += size
            if f.casefold() in {n.casefold() for n in copy_names}:
                if apply:
                    shutil.copy2(s, d)
                stats.copied += 1
                continue
            if not apply:
                stats.linked += 1
                continue
            try:
                if os.path.exists(d):
                    os.remove(d)
                os.link(s, d)
                stats.linked += 1
            except OSError as e:
                if allow_copy_fallback:
                    shutil.copy2(s, d)
                    stats.copied += 1
                else:
                    stats.errors.append(f"link {s} -> {d}: {e}")
    return stats


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:,.1f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024
    return f"{n:.1f} TB"


def enable_utf8_console() -> None:
    """Make Chinese text print correctly in the Windows console."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
