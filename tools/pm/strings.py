"""Read/write Bethesda localized string tables (.STRINGS / .DLSTRINGS / .ILSTRINGS).

讀寫 Bethesda 本地化字串檔。官方繁中字串為 UTF-8；英文通常為 cp1252。

Format: uint32 count | uint32 dataSize | count x (uint32 id, uint32 offset) | data
Offsets are relative to the start of the data block.
- .STRINGS: null-terminated strings
- .DLSTRINGS / .ILSTRINGS: uint32 length (including the null) + bytes + null
"""

from __future__ import annotations

import struct
from pathlib import Path


def kind_of(path: Path | str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".strings":
        return "strings"
    if ext in (".dlstrings", ".ilstrings"):
        return "lstrings"
    raise ValueError(f"not a string table: {path}")


def _decode(b: bytes, encoding: str | None) -> str:
    if encoding:
        return b.decode(encoding, errors="replace")
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", errors="replace")


def parse(data: bytes, kind: str, encoding: str | None = None) -> dict[int, str]:
    count, size = struct.unpack_from("<II", data, 0)
    dir_end = 8 + 8 * count
    base = dir_end
    out: dict[int, str] = {}
    for i in range(count):
        sid, off = struct.unpack_from("<II", data, 8 + 8 * i)
        p = base + off
        if kind == "strings":
            end = data.find(b"\x00", p)
            raw = data[p:end if end >= 0 else base + size]
        else:
            (length,) = struct.unpack_from("<I", data, p)
            raw = data[p + 4:p + 4 + length].rstrip(b"\x00")
        out[sid] = _decode(raw, encoding)
    return out


def read(path: Path, encoding: str | None = None) -> dict[int, str]:
    path = Path(path)
    return parse(path.read_bytes(), kind_of(path), encoding)


def build(table: dict[int, str], kind: str, encoding: str = "utf-8") -> bytes:
    directory = bytearray()
    blob = bytearray()
    for sid in sorted(table):
        directory += struct.pack("<II", sid, len(blob))
        enc = table[sid].encode(encoding, errors="replace") + b"\x00"
        if kind == "strings":
            blob += enc
        else:
            blob += struct.pack("<I", len(enc)) + enc
    return struct.pack("<II", len(table), len(blob)) + bytes(directory) + bytes(blob)


def write(path: Path, table: dict[int, str], encoding: str = "utf-8") -> None:
    path = Path(path)
    path.write_bytes(build(table, kind_of(path), encoding))
