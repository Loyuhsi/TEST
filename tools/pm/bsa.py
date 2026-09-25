"""Read Skyrim BSA archives (v104 LE / v105 SE) and extract selected files.

讀取 BSA 封裝檔並擷取指定檔案（例如官方繁中字串與字型）。
v105 compressed files use LZ4 frames: `pip install lz4` is needed only then.

Header (36 bytes): 'BSA\\0' | version | offset(36) | archiveFlags | folderCount |
fileCount | totalFolderNameLength | totalFileNameLength | fileFlags
Folder record: v105 = hash u64, count u32, pad u32, offset u64 (24 bytes);
               v104 = hash u64, count u32, offset u32 (16 bytes).
File record: hash u64, size u32 (bit 30 toggles compression), offset u32.
"""

from __future__ import annotations

import fnmatch
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

ARCH_DIR_NAMES = 0x1
ARCH_FILE_NAMES = 0x2
ARCH_COMPRESSED = 0x4
ARCH_EMBED_NAMES = 0x100
SIZE_COMPRESS_TOGGLE = 0x40000000


class BSAError(ValueError):
    pass


@dataclass
class BSAEntry:
    path: str       # lower-case, backslash separated (as stored)
    size: int       # raw stored size (without toggle bit)
    offset: int
    compressed: bool


class BSA:
    def __init__(self, path: Path):
        self.path = Path(path)
        self._f = open(self.path, "rb")
        head = self._f.read(36)
        if head[:4] != b"BSA\x00":
            raise BSAError(f"{self.path.name}: not a BSA")
        (self.version, _off, self.flags, nfolders, nfiles,
         _folder_names_len, file_names_len, _file_flags) = struct.unpack_from("<IIIIIIII", head, 4)
        if self.version not in (103, 104, 105):
            raise BSAError(f"{self.path.name}: unsupported BSA version {self.version}")
        rec = 24 if self.version == 105 else 16
        folders = []
        for _ in range(nfolders):
            data = self._f.read(rec)
            (_h, count) = struct.unpack_from("<QI", data, 0)
            folders.append(count)
        records: list[tuple[str, int, int]] = []
        for count in folders:
            fname = ""
            if self.flags & ARCH_DIR_NAMES:
                (ln,) = struct.unpack("<B", self._f.read(1))
                fname = self._f.read(ln).rstrip(b"\x00").decode("cp1252", errors="replace")
            for _ in range(count):
                _h, size, off = struct.unpack("<QII", self._f.read(16))
                records.append((fname, size, off))
        names: list[str] = []
        if self.flags & ARCH_FILE_NAMES:
            blob = self._f.read(file_names_len)
            names = [n.decode("cp1252", errors="replace") for n in blob.split(b"\x00")[:nfiles]]
        self.entries: list[BSAEntry] = []
        for i, (folder, size, off) in enumerate(records):
            name = names[i] if i < len(names) else f"{i:08d}.bin"
            full = f"{folder}\\{name}" if folder else name
            toggled = bool(size & SIZE_COMPRESS_TOGGLE)
            compressed = bool(self.flags & ARCH_COMPRESSED) != toggled
            self.entries.append(BSAEntry(full.lower(), size & 0x3FFFFFFF, off, compressed))

    def close(self) -> None:
        self._f.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def find(self, pattern: str) -> list[BSAEntry]:
        pat = pattern.lower().replace("/", "\\")
        return [e for e in self.entries if fnmatch.fnmatch(e.path, pat)]

    def read(self, entry: BSAEntry) -> bytes:
        self._f.seek(entry.offset)
        size = entry.size
        if self.flags & ARCH_EMBED_NAMES:
            (ln,) = struct.unpack("<B", self._f.read(1))
            self._f.read(ln)
            size -= 1 + ln
        if not entry.compressed:
            return self._f.read(size)
        (orig,) = struct.unpack("<I", self._f.read(4))
        payload = self._f.read(size - 4)
        if self.version == 105:
            try:
                import lz4.frame  # type: ignore
            except ImportError as e:  # pragma: no cover - depends on environment
                raise BSAError("此 BSA 使用 LZ4 壓縮，請先執行：python -m pip install lz4") from e
            out = lz4.frame.decompress(payload)
        else:
            out = zlib.decompress(payload)
        if len(out) != orig:
            raise BSAError(f"{entry.path}: size mismatch {len(out)} != {orig}")
        return out

    def extract(self, patterns: list[str], out_dir: Path) -> list[Path]:
        out_dir = Path(out_dir)
        written = []
        seen = set()
        for pat in patterns:
            for e in self.find(pat):
                if e.path in seen:
                    continue
                seen.add(e.path)
                dest = out_dir.joinpath(*e.path.split("\\"))
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(self.read(e))
                written.append(dest)
        return written


def build_bsa(files: dict[str, bytes], *, version: int = 105, compress: bool = False) -> bytes:
    """Build a small BSA (for tests). Hashes are zero; the game would reject it."""
    folders: dict[str, list[tuple[str, bytes]]] = {}
    for path, data in files.items():
        folder, _, name = path.lower().replace("/", "\\").rpartition("\\")
        folders.setdefault(folder, []).append((name, data))
    flags = ARCH_DIR_NAMES | ARCH_FILE_NAMES | (ARCH_COMPRESSED if compress else 0)
    folder_names_len = sum(len(f) + 1 for f in folders)
    file_names = [n for fl in folders.values() for n, _ in fl]
    file_names_len = sum(len(n) + 1 for n in file_names)
    rec = 24 if version == 105 else 16
    header_len = 36 + rec * len(folders)
    file_block_len = sum(1 + len(f) + 1 + 16 * len(fl) for f, fl in folders.items())
    data_start = header_len + file_block_len + file_names_len
    out = bytearray(struct.pack("<4sIIIIIIII", b"BSA\x00", version, 36, flags, len(folders),
                                len(file_names), folder_names_len, file_names_len, 0))
    for f, fl in folders.items():
        if version == 105:
            out += struct.pack("<QIIQ", 0, len(fl), 0, 0)
        else:
            out += struct.pack("<QII", 0, len(fl), 0)
    blobs = bytearray()
    for f, fl in folders.items():
        enc = f.encode("cp1252")
        out += struct.pack("<B", len(enc) + 1) + enc + b"\x00"
        for _name, data in fl:
            if compress:
                if version == 105:
                    import lz4.frame  # type: ignore
                    payload = struct.pack("<I", len(data)) + lz4.frame.compress(data)
                else:
                    payload = struct.pack("<I", len(data)) + zlib.compress(data)
            else:
                payload = data
            out += struct.pack("<QII", 0, len(payload), data_start + len(blobs))
            blobs += payload
    out += b"".join(n.encode("cp1252") + b"\x00" for n in file_names)
    assert len(out) == data_start, (len(out), data_start)
    return bytes(out + blobs)
