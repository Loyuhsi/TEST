"""Read the header of a compiled Papyrus script (.pex, Skyrim = big-endian).

讀取 Papyrus 腳本（.pex）標頭：編譯時間、原始檔名、字串表數量，用來判斷翻譯版是否對應同一版本。
xTranslator edits the string table in place and keeps the header, so an identical compile time
means the translated script was made from the same script version.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

MAGIC = 0xFA57C0DE


class PexError(ValueError):
    pass


@dataclass
class PexHeader:
    major: int
    minor: int
    game_id: int
    compile_time: int
    source: str
    user: str
    machine: str
    string_count: int


def parse(data: bytes) -> PexHeader:
    if len(data) < 18 or struct.unpack_from(">I", data, 0)[0] != MAGIC:
        raise PexError("not a Skyrim .pex file")
    major, minor, game_id, ctime = struct.unpack_from(">BBHQ", data, 4)
    pos = 16

    def wstr():
        nonlocal pos
        (n,) = struct.unpack_from(">H", data, pos)
        s = data[pos + 2:pos + 2 + n].decode("utf-8", errors="replace")
        pos += 2 + n
        return s

    source, user, machine = wstr(), wstr(), wstr()
    (count,) = struct.unpack_from(">H", data, pos)
    return PexHeader(major, minor, game_id, ctime, source, user, machine, count)


def read(path: Path) -> PexHeader:
    with open(path, "rb") as f:
        return parse(f.read(4096))


def build(source: str = "Test.psc", ctime: int = 1234567890, strings: tuple[str, ...] = ("a",)) -> bytes:
    """Minimal header + string table (for tests)."""
    def w(s: str) -> bytes:
        b = s.encode("utf-8")
        return struct.pack(">H", len(b)) + b
    out = struct.pack(">IBBHQ", MAGIC, 3, 2, 1, ctime) + w(source) + w("user") + w("pc")
    out += struct.pack(">H", len(strings)) + b"".join(w(s) for s in strings)
    return out
