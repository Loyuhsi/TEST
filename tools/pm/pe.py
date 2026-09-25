"""Minimal PE (Windows DLL) export-table reader for SKSE plugin runtime checks.

讀取 DLL 匯出表，判斷 SKSE 外掛能否在 1.5.97（SE）上載入。

SKSE 2.0.x (Skyrim 1.5.97) calls SKSEPlugin_Query; SKSE 2.1+ (AE 1.6.x/1.7.x)
reads the exported SKSEPlugin_Version data block. CommonLibSSE-NG
"multi-runtime" plugins export both. So:
    Query only          -> SE build (loads on 1.5.97)
    Version only        -> AE-only build (will NOT load on 1.5.97)
    Query + Version     -> multi-runtime / NG (loads on both)
    neither + no Load   -> not an SKSE plugin (helper DLL)
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path


class PEError(ValueError):
    pass


@dataclass
class DllInfo:
    path: str
    machine: int = 0
    exports: set[str] = field(default_factory=set)

    @property
    def is_skse_plugin(self) -> bool:
        return "SKSEPlugin_Load" in self.exports

    @property
    def runtime_class(self) -> str:
        q = "SKSEPlugin_Query" in self.exports
        v = "SKSEPlugin_Version" in self.exports
        if not self.is_skse_plugin and not (q or v):
            return "not_skse"
        if q and v:
            return "multi"
        if q:
            return "se"
        if v:
            return "ae_only"
        return "unknown"

    @property
    def loads_on_1597(self) -> bool | None:
        return {"se": True, "multi": True, "ae_only": False}.get(self.runtime_class)


def _rva_to_offset(rva: int, sections: list[tuple[int, int, int, int]]) -> int:
    for va, vsize, raw_ptr, raw_size in sections:
        if va <= rva < va + max(vsize, raw_size):
            return raw_ptr + (rva - va)
    raise PEError(f"RVA 0x{rva:x} not in any section")


def _cstring(data: bytes, off: int) -> str:
    end = data.find(b"\x00", off)
    return data[off:end if end >= 0 else len(data)].decode("ascii", errors="replace")


def read_dll(path: Path) -> DllInfo:
    data = Path(path).read_bytes()
    return parse_dll(data, str(path))


def parse_dll(data: bytes, name: str = "") -> DllInfo:
    if data[:2] != b"MZ":
        raise PEError(f"{name}: not an MZ executable")
    (e_lfanew,) = struct.unpack_from("<I", data, 0x3C)
    if data[e_lfanew:e_lfanew + 4] != b"PE\x00\x00":
        raise PEError(f"{name}: missing PE signature")
    coff = e_lfanew + 4
    machine, nsections, _ts, _sym, _nsym, opt_size, _chars = struct.unpack_from("<HHIIIHH", data, coff)
    opt = coff + 20
    (magic,) = struct.unpack_from("<H", data, opt)
    if magic == 0x20B:       # PE32+
        dd_off = opt + 112
    elif magic == 0x10B:     # PE32
        dd_off = opt + 96
    else:
        raise PEError(f"{name}: unknown optional header magic 0x{magic:x}")
    export_rva, export_size = struct.unpack_from("<II", data, dd_off)
    sec_off = opt + opt_size
    sections = []
    for i in range(nsections):
        s = sec_off + i * 40
        vsize, va, raw_size, raw_ptr = struct.unpack_from("<IIII", data, s + 8)
        sections.append((va, vsize, raw_ptr, raw_size))
    info = DllInfo(path=name, machine=machine)
    if not export_rva:
        return info
    eo = _rva_to_offset(export_rva, sections)
    (_flags, _ts, _maj, _min, _name_rva, _base, _nfuncs, nnames,
     _funcs_rva, names_rva, _ords_rva) = struct.unpack_from("<IIHHIIIIIII", data, eo)
    if nnames:
        no = _rva_to_offset(names_rva, sections)
        for i in range(nnames):
            (nrva,) = struct.unpack_from("<I", data, no + 4 * i)
            info.exports.add(_cstring(data, _rva_to_offset(nrva, sections)))
    return info


VS_FIXEDFILEINFO_SIG = b"\xbd\x04\xef\xfe"


def fixed_file_version(data: bytes) -> str | None:
    """Return 'a.b.c.d' from the VS_FIXEDFILEINFO block (e.g. SkyrimSE.exe -> '1.5.97.0')."""
    i = data.find(VS_FIXEDFILEINFO_SIG)
    while i >= 0:
        if i + 16 <= len(data):
            _sig, struc, ms, ls = struct.unpack_from("<IIII", data, i)
            if struc in (0x00010000, 0):
                return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
        i = data.find(VS_FIXEDFILEINFO_SIG, i + 1)
    return None


def file_version(path: Path) -> str | None:
    try:
        return fixed_file_version(Path(path).read_bytes())
    except OSError:
        return None


def build_dll(exports: list[str]) -> bytes:
    """Build a tiny PE32+ DLL with the given export names (for tests)."""
    file_align = 0x200
    sect_rva = 0x1000
    # export directory layout inside the single section
    names_blob = b""
    name_offsets = []
    dll_name = b"test.dll\x00"
    for n in exports:
        name_offsets.append(len(names_blob))
        names_blob += n.encode() + b"\x00"
    edir_size = 40
    n = len(exports)
    funcs_off = edir_size
    names_off = funcs_off + 4 * n
    ords_off = names_off + 4 * n
    dllname_off = ords_off + 2 * n
    strings_off = dllname_off + len(dll_name)
    body = bytearray(strings_off + len(names_blob))
    struct.pack_into("<IIHHIIIIIII", body, 0, 0, 0, 0, 0, sect_rva + dllname_off, 1, n, n,
                     sect_rva + funcs_off, sect_rva + names_off, sect_rva + ords_off)
    for i in range(n):
        struct.pack_into("<I", body, funcs_off + 4 * i, sect_rva)          # dummy function RVA
        struct.pack_into("<I", body, names_off + 4 * i, sect_rva + strings_off + name_offsets[i])
        struct.pack_into("<H", body, ords_off + 2 * i, i)
    body[dllname_off:dllname_off + len(dll_name)] = dll_name
    body[strings_off:] = names_blob
    raw = bytes(body) + b"\x00" * (-len(body) % file_align)

    e_lfanew = 0x40
    opt_size = 240
    headers_size = file_align
    dos = bytearray(0x40)
    dos[0:2] = b"MZ"
    struct.pack_into("<I", dos, 0x3C, e_lfanew)
    coff = struct.pack("<HHIIIHH", 0x8664, 1, 0, 0, 0, opt_size, 0x2022)
    opt = bytearray(opt_size)
    struct.pack_into("<H", opt, 0, 0x20B)
    struct.pack_into("<I", opt, 108, 16)                       # NumberOfRvaAndSizes
    struct.pack_into("<II", opt, 112, sect_rva, len(body))      # export directory
    sect = bytearray(40)
    sect[0:6] = b".edata"
    struct.pack_into("<IIII", sect, 8, len(body), sect_rva, len(raw), headers_size)
    header = bytes(dos) + b"PE\x00\x00" + coff + bytes(opt) + bytes(sect)
    header += b"\x00" * (headers_size - len(header))
    return header + raw
