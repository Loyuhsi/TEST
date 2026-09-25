"""Parse Skyrim SE plugin headers (TES4 record) without loading the whole file.

解析 Skyrim SE 插件（.esp/.esm/.esl）的 TES4 標頭：ESM/ESL 旗標、前置檔、版本。

Layout (SSE): 24-byte record header
    char[4] 'TES4' | uint32 dataSize | uint32 flags | uint32 formID |
    uint32 vcInfo | uint16 formVersion | uint16 unknown
followed by subrecords: char[4] type | uint16 size | data
(an 'XXXX' subrecord carries a uint32 size for the next subrecord).

Record flags: 0x001 = master (ESM), 0x080 = localized strings, 0x200 = light (ESL).
A .esm/.esl extension also implies master; .esl implies light.
HEDR version 1.70 = classic SSE; 1.71 = newer CK form range that needs
Backported Extended ESL Support (BEES) on runtimes before 1.6.1130.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path

FLAG_MASTER = 0x001
FLAG_LOCALIZED = 0x080
FLAG_LIGHT = 0x200

MAX_FULL = 254
MAX_LIGHT = 4096


class PluginError(ValueError):
    pass


@dataclass
class PluginHeader:
    name: str
    flags: int = 0
    form_version: int = 0
    hedr_version: float = 0.0
    num_records: int = 0
    next_object_id: int = 0
    author: str = ""
    description: str = ""
    masters: list[str] = field(default_factory=list)

    @property
    def ext(self) -> str:
        return Path(self.name).suffix.lower()

    @property
    def is_master(self) -> bool:
        return bool(self.flags & FLAG_MASTER) or self.ext in (".esm", ".esl")

    @property
    def is_light(self) -> bool:
        return bool(self.flags & FLAG_LIGHT) or self.ext == ".esl"

    @property
    def is_localized(self) -> bool:
        return bool(self.flags & FLAG_LOCALIZED)

    @property
    def needs_bees(self) -> bool:
        """True when the header uses the 1.71 form range (needs BEES on 1.5.97)."""
        return round(self.hedr_version, 2) >= 1.71

    @property
    def kind(self) -> str:
        if self.is_light:
            return "light"
        return "master" if self.is_master else "full"


def _zstring(b: bytes) -> str:
    b = b.split(b"\x00", 1)[0]
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("cp1252", errors="replace")


def parse_header_bytes(data: bytes, name: str = "") -> PluginHeader:
    if len(data) < 24 or data[:4] != b"TES4":
        raise PluginError(f"{name}: not a TES4 plugin")
    size, flags, _form_id, _vc, form_version, _unk = struct.unpack_from("<IIIIHH", data, 4)
    body = data[24:24 + size]
    if len(body) < size:
        raise PluginError(f"{name}: truncated header ({len(body)}/{size} bytes)")
    h = PluginHeader(name=name, flags=flags, form_version=form_version)
    pos = 0
    big_size = None
    while pos + 6 <= len(body):
        sub = body[pos:pos + 4]
        (ssize,) = struct.unpack_from("<H", body, pos + 4)
        pos += 6
        if big_size is not None:
            ssize, big_size = big_size, None
        payload = body[pos:pos + ssize]
        pos += ssize
        if sub == b"XXXX":
            (big_size,) = struct.unpack("<I", payload[:4])
        elif sub == b"HEDR" and len(payload) >= 12:
            h.hedr_version, h.num_records, h.next_object_id = struct.unpack("<fiI", payload[:12])
        elif sub == b"MAST":
            h.masters.append(_zstring(payload))
        elif sub == b"CNAM":
            h.author = _zstring(payload)
        elif sub == b"SNAM":
            h.description = _zstring(payload)
    return h


def read_header(path: Path) -> PluginHeader:
    path = Path(path)
    with open(path, "rb") as f:
        head = f.read(24)
        if len(head) < 24 or head[:4] != b"TES4":
            raise PluginError(f"{path.name}: not a TES4 plugin")
        (size,) = struct.unpack_from("<I", head, 4)
        body = f.read(size)
    return parse_header_bytes(head + body, path.name)


def build_header(name: str, *, masters: list[str] = (), flags: int = 0, hedr_version: float = 1.7,
                 num_records: int = 0, author: str = "", form_version: int = 44) -> bytes:
    """Build a minimal valid TES4 header (used by tests and placeholder plugins)."""
    def sub(t: bytes, payload: bytes) -> bytes:
        return t + struct.pack("<H", len(payload)) + payload

    body = sub(b"HEDR", struct.pack("<fiI", hedr_version, num_records, 0x800))
    if author:
        body += sub(b"CNAM", author.encode("utf-8") + b"\x00")
    for m in masters:
        body += sub(b"MAST", m.encode("utf-8") + b"\x00") + sub(b"DATA", b"\x00" * 8)
    return b"TES4" + struct.pack("<IIIIHH", len(body), flags, 0, 0, form_version, 0) + body
