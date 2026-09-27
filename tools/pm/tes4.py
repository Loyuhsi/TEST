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
import zlib
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


# ---------------------------------------------------------------- records
ESL_MAX_NEW = 2048                  # new records a light plugin may hold (0x800-0xFFF)
ESL_MIN_ID, ESL_MIN_ID_BEES, ESL_MAX_ID = 0x800, 0x000, 0xFFF


def iter_records(data: bytes, name: str = ""):
    """Yield (type, flags, formID) for every record after the TES4 header.

    Groups are only headers (24 bytes) followed by their contents, so a linear walk that
    steps over GRUP headers visits every record, nested or not.
    """
    if len(data) < 24 or data[:4] != b"TES4":
        raise PluginError(f"{name}: not a TES4 plugin")
    pos = 24 + struct.unpack_from("<I", data, 4)[0]
    end = len(data)
    while pos < end:
        if pos + 24 > end:
            raise PluginError(f"{name}: truncated record header at {pos}")
        typ = bytes(data[pos:pos + 4])
        size, flags, form_id = struct.unpack_from("<III", data, pos + 4)
        if typ == b"GRUP":
            if size < 24:
                raise PluginError(f"{name}: bad group size at {pos}")
            pos += 24
            continue
        if pos + 24 + size > end:
            raise PluginError(f"{name}: truncated {typ.decode('ascii', 'replace')} record at {pos}")
        yield typ.decode("ascii", "replace"), flags, form_id
        pos += 24 + size


@dataclass
class RecordSummary:
    header: PluginHeader
    records: int = 0
    new: int = 0
    new_by_type: dict[str, int] = field(default_factory=dict)
    overrides_by_type: dict[str, int] = field(default_factory=dict)
    new_ids: list[int] = field(default_factory=list)

    @property
    def overrides(self) -> int:
        return self.records - self.new

    @property
    def new_cells(self) -> int:
        return self.new_by_type.get("CELL", 0)


def summarize_bytes(data: bytes, name: str = "") -> RecordSummary:
    h = parse_header_bytes(data, name)
    own = len(h.masters)
    s = RecordSummary(h)
    for typ, _flags, form_id in iter_records(data, name):
        s.records += 1
        if form_id >> 24 >= own:
            s.new += 1
            s.new_by_type[typ] = s.new_by_type.get(typ, 0) + 1
            s.new_ids.append(form_id & 0xFFFFFF)
        else:
            s.overrides_by_type[typ] = s.overrides_by_type.get(typ, 0) + 1
    return s


def summarize(path: Path) -> RecordSummary:
    path = Path(path)
    return summarize_bytes(path.read_bytes(), path.name)


def esl_ready(s: RecordSummary) -> tuple[bool, str]:
    """Can the light flag be set as is, without compacting form IDs?

    BEES lets 1.71-header plugins use object IDs from 0x000 on 1.5.97; older headers need 0x800+.
    """
    if s.header.is_light:
        return False, "已經是輕量插件"
    if s.new > ESL_MAX_NEW:
        return False, f"新增記錄 {s.new} 筆，超過 {ESL_MAX_NEW}"
    low = ESL_MIN_ID_BEES if s.header.needs_bees else ESL_MIN_ID
    bad = [i for i in s.new_ids if not low <= i <= ESL_MAX_ID]
    if bad:
        return False, f"{len(bad)} 筆新增記錄的編號超出 0x{low:03X}–0x{ESL_MAX_ID:03X}（需要壓縮 FormID）"
    return True, "可以直接加 ESL 旗標"


# ---------------------------------------------------------------- editable record tree
FLAG_COMPRESSED = 0x00040000


@dataclass
class Record:
    header: bytes                   # 24 bytes as read (size field refreshed on output)
    data: bytes                     # stored payload (compressed when the flag is set)

    @property
    def type(self) -> str:
        return self.header[:4].decode("ascii", "replace")

    @property
    def flags(self) -> int:
        return struct.unpack_from("<I", self.header, 8)[0]

    @property
    def form_id(self) -> int:
        return struct.unpack_from("<I", self.header, 12)[0]

    def payload(self) -> bytes:
        return record_payload(self.flags, self.data)

    def replace_payload(self, payload: bytes) -> "Record":
        """Same record with new (uncompressed) payload."""
        head = bytearray(self.header)
        struct.pack_into("<II", head, 4, len(payload), self.flags & ~FLAG_COMPRESSED)
        return Record(bytes(head), payload)

    def to_bytes(self) -> bytes:
        head = bytearray(self.header)
        struct.pack_into("<I", head, 4, len(self.data))
        return bytes(head) + self.data


@dataclass
class Group:
    header: bytes                   # 24 bytes; the size is recomputed on output
    items: list = field(default_factory=list)

    @property
    def label(self) -> bytes:
        return self.header[8:12]

    def to_bytes(self) -> bytes:
        body = b"".join(i.to_bytes() for i in self.items)
        head = bytearray(self.header)
        struct.pack_into("<I", head, 4, 24 + len(body))
        return bytes(head) + body


def record_payload(flags: int, data: bytes) -> bytes:
    if not flags & FLAG_COMPRESSED:
        return data
    if len(data) < 4:
        raise PluginError("compressed record without size")
    (size,) = struct.unpack_from("<I", data, 0)
    out = zlib.decompress(data[4:])
    if len(out) != size:
        raise PluginError(f"decompressed {len(out)} bytes, header says {size}")
    return out


def parse_items(data: bytes, pos: int, end: int, name: str = "") -> list:
    items = []
    while pos < end:
        if pos + 24 > end:
            raise PluginError(f"{name}: truncated header at {pos}")
        head = bytes(data[pos:pos + 24])
        (size,) = struct.unpack_from("<I", head, 4)
        if head[:4] == b"GRUP":
            if size < 24 or pos + size > end:
                raise PluginError(f"{name}: bad group size at {pos}")
            items.append(Group(head, parse_items(data, pos + 24, pos + size, name)))
            pos += size
        else:
            if pos + 24 + size > end:
                raise PluginError(f"{name}: truncated record at {pos}")
            items.append(Record(head, bytes(data[pos + 24:pos + 24 + size])))
            pos += 24 + size
    return items


def parse_plugin(data: bytes, name: str = "") -> tuple[Record, list]:
    """(TES4 header record, top-level items) of a whole plugin."""
    if len(data) < 24 or data[:4] != b"TES4":
        raise PluginError(f"{name}: not a TES4 plugin")
    (size,) = struct.unpack_from("<I", data, 4)
    tes4 = Record(bytes(data[:24]), bytes(data[24:24 + size]))
    return tes4, parse_items(data, 24 + size, len(data), name)


def serialize_plugin(tes4: Record, items: list) -> bytes:
    return tes4.to_bytes() + b"".join(i.to_bytes() for i in items)


def walk_records(items: list):
    for i in items:
        if isinstance(i, Group):
            yield from walk_records(i.items)
        else:
            yield i


def iter_subrecords(payload: bytes):
    """Yield (type, data) subrecords, folding XXXX size extensions."""
    pos, big = 0, None
    while pos + 6 <= len(payload):
        typ = payload[pos:pos + 4]
        (size,) = struct.unpack_from("<H", payload, pos + 4)
        pos += 6
        if big is not None:
            size, big = big, None
        data = payload[pos:pos + size]
        pos += size
        if typ == b"XXXX":
            (big,) = struct.unpack("<I", data[:4])
            continue
        yield typ.decode("ascii", "replace"), data


def build_subrecords(subs: list[tuple[str, bytes]]) -> bytes:
    out = bytearray()
    for typ, data in subs:
        t = typ.encode("ascii")
        if len(data) > 0xFFFF:
            out += b"XXXX" + struct.pack("<HI", 4, len(data)) + t + struct.pack("<H", 0) + data
        else:
            out += t + struct.pack("<H", len(data)) + data
    return bytes(out)


def resolve(form_id: int, masters: list[str], self_name: str) -> tuple[str, int]:
    """(plugin that defines the form, object id) for a form ID written in a plugin."""
    idx = form_id >> 24
    return (masters[idx] if idx < len(masters) else self_name), form_id & 0xFFFFFF


def set_record_count(tes4_record: Record, count: int) -> Record:
    """TES4 header record with the HEDR record count (records + groups) replaced."""
    subs = []
    for typ, data in iter_subrecords(tes4_record.payload()):
        if typ == "HEDR" and len(data) >= 12:
            data = data[:4] + struct.pack("<i", max(count, 0)) + data[8:]
        subs.append((typ, data))
    return tes4_record.replace_payload(build_subrecords(subs))


def count_items(items: list) -> int:
    """Records plus groups in a subtree (what HEDR counts)."""
    return sum(1 + count_items(i.items) if isinstance(i, Group) else 1 for i in items)
