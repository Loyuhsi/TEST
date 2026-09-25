#!/usr/bin/env python3
"""Map every MO2 mod folder of a Wabbajack modlist to its source archives.

從 Wabbajack 模組清單（Mages & Vikings）逐一對應每個 MO2 mod 資料夾與其來源封存檔及 Nexus ID。

The script reads the ``modlist`` entry (Wabbajack's JSON DTO) of a
``.wabbajack`` file and writes two outputs:

* ``<prefix>_folder_map.csv``   one row per MO2 mod folder (``mods\\<Folder>\\...``)
* ``<prefix>_modlist_meta.json`` modlist-level metadata and counts

Input modes (first match wins):

1. ``--modlist-json PATH``   an already extracted ``modlist`` JSON file.
2. ``--wabbajack PATH``      a local ``.wabbajack`` file (it is a ZIP archive;
                             only the ``modlist`` entry is inflated).
3. default                   remote mode: the official gallery index
                             (wabbajack-tools/mod-lists ``repositories.json``)
                             names the Mages & Vikings repository JSON; the
                             entry with ``links.machineURL == MagesAndVikings``
                             gives the ``links.download`` CDN URL, and ONLY the
                             ZIP central directory plus the ``modlist`` entry
                             are read with HTTP Range requests (~25 MB instead
                             of 5.4 GB).

Remote layout (verified 2026-09-25): a Wabbajack "authored files" CDN URL
serves ``<url>/definition.json.gz`` (JSON: Size, Hash, Parts[{Index, Offset,
Size, Hash}]) and ``<url>/parts/<Index>``; each part is a contiguous 2 MiB
byte range of the ``.wabbajack`` ZIP and honours HTTP ``Range``. A seekable
file object that maps ZIP offsets onto part ranges lets the stdlib ``zipfile``
module parse the (ZIP64) central directory and inflate the ``modlist`` entry;
``zipfile`` verifies the entry's CRC-32, so a corrupted transfer is detected.
If ``definition.json.gz`` is missing, plain Range requests against the URL
itself are used.

Folder attribution rules:

* A directive belongs to folder F when its ``To`` path is ``mods\\F\\...``.
  Folder names are grouped case-insensitively (Windows semantics).
* ``CreateBSA`` directives build a BSA from staged files whose ``To`` is
  ``TEMP_BSA_FILES\\<TempID>\\...``. Those staged files are attributed to the
  folder of the BSA they are packed into, but only for archive attribution
  (``primary_archive_*``, ``archive_count``, ``all_archives``); they are not
  counted in ``file_count``/``total_bytes`` because they are not installed as
  loose files (the BSA itself counts as one file; Wabbajack records its size
  as 0).
* The archive of a directive is the first element of ``ArchiveHashPath``.
* ``primary`` = the archive that provides the most files to the folder
  (ties: more bytes, then archive name, then hash). Folders fed only by
  ``InlineFile``/``RemappedInlineFile`` directives get ``InlineOnly``.
* ``patched_count`` counts ``PatchedFromArchive`` (and ``TransformedTexture``,
  if present) directives; ``inline_count`` counts ``InlineFile`` and
  ``RemappedInlineFile`` directives.

Output is deterministic: rows are sorted by folder name (case-insensitive),
every list is sorted, and JSON keys are emitted in a fixed order. Only the
``fetched_date`` field depends on the day the script runs (override it with
``--fetched-date``).

Examples::

    # Mages & Vikings (current gallery version) via ranged CDN reads
    python tools/analysis/mv_wabbajack_map.py --out-dir data/analysis

    # a local .wabbajack (e.g. MV 2.40.1, Nexus file 703199), separate prefix
    python tools/analysis/mv_wabbajack_map.py \\
        --wabbajack "D:/Downloads/Mages & Vikings.wabbajack" --out-prefix mv2401

Only the Python 3.11+ standard library is used.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import datetime as _dt
import gzip
import hashlib
import io
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------

# Official gallery index: {"<RepositoryName>": "<repository modlists.json URL>"}.
REPOSITORIES_URL = (
    "https://raw.githubusercontent.com/wabbajack-tools/mod-lists/master/repositories.json"
)
MV_REPOSITORY_NAME = "MagesAndVikings"
# Used when the gallery index cannot be read or lacks the repository.
MV_REPOSITORY_URL = (
    "https://raw.githubusercontent.com/nicolasbertolino/MagesAndVikings/main/modlists.json"
)
MV_MACHINE_URL = "MagesAndVikings"

USER_AGENT = "mv_wabbajack_map/1.0 (+stdlib urllib)"
HTTP_TIMEOUT = 120  # seconds per request
HTTP_RETRIES = 5
READ_AHEAD = 64 * 1024  # small reads are widened to this many bytes and cached

MODLIST_ENTRY_NAMES = ("modlist", "modlist.json")

CSV_COLUMNS = [
    "folder",
    "primary_archive_name",
    "primary_source",
    "nexus_mod_id",
    "nexus_file_id",
    "nexus_version",
    "nexus_mod_name",
    "archive_count",
    "all_archives",
    "file_count",
    "patched_count",
    "inline_count",
    "total_bytes",
    "skse_dlls",
    "plugins",
]

# Downloader class name (``$type`` before ',' and '+') -> source label.
SOURCE_BY_DOWNLOADER = {
    "NexusDownloader": "Nexus",
    "Nexus": "Nexus",
    "HttpDownloader": "HTTP",
    "Http": "HTTP",
    "GameFileSourceDownloader": "GameFile",
    "GameFileSource": "GameFile",
    "WabbajackCDNDownloader": "WabbajackCDN",
    "WabbajackCDN": "WabbajackCDN",
    "MegaDownloader": "Mega",
    "Mega": "Mega",
    "GoogleDriveDownloader": "GoogleDrive",
    "GoogleDrive": "GoogleDrive",
}
SOURCE_LABELS = ("Nexus", "HTTP", "GameFile", "WabbajackCDN", "Mega", "GoogleDrive", "Other")

INLINE_TYPES = {"InlineFile", "RemappedInlineFile"}
PATCHED_TYPES = {"PatchedFromArchive", "TransformedTexture"}
PLUGIN_EXTS = (".esp", ".esm", ".esl")
TEMP_BSA_ROOT = "temp_bsa_files"


def log(msg: str) -> None:
    """Progress output goes to stderr so stdout stays clean."""
    try:
        print(msg, file=sys.stderr, flush=True)
    except UnicodeEncodeError:  # e.g. a legacy Windows console code page
        enc = sys.stderr.encoding or "ascii"
        print(msg.encode(enc, "backslashreplace").decode(enc), file=sys.stderr, flush=True)


# --------------------------------------------------------------------------
# HTTP helpers
# --------------------------------------------------------------------------


def quote_url(url: str) -> str:
    """Percent-encode spaces, '&' etc. in the path of a URL (idempotent)."""
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe="/")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


class HttpClient:
    """Minimal urllib wrapper with retries and a transfer counter."""

    def __init__(self) -> None:
        self.bytes_transferred = 0
        self.requests = 0

    def get(self, url: str, byte_range: tuple[int, int] | None = None) -> tuple[int, dict, bytes]:
        """GET ``url``; ``byte_range`` is an inclusive (first, last) pair."""
        headers = {"User-Agent": USER_AGENT, "Accept-Encoding": "identity"}
        if byte_range is not None:
            headers["Range"] = f"bytes={byte_range[0]}-{byte_range[1]}"
        last_exc: Exception | None = None
        for attempt in range(HTTP_RETRIES):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                    body = resp.read()
                    self.requests += 1
                    self.bytes_transferred += len(body)
                    return resp.status, dict(resp.headers.items()), body
            except urllib.error.HTTPError as exc:
                # 4xx (except 408/429) will not improve on retry.
                if 400 <= exc.code < 500 and exc.code not in (408, 429):
                    raise
                last_exc = exc
            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
                last_exc = exc
            delay = 2 ** attempt
            log(f"  retry {attempt + 1}/{HTTP_RETRIES} for {url} in {delay}s ({last_exc})")
            time.sleep(delay)
        raise RuntimeError(f"GET failed after {HTTP_RETRIES} attempts: {url}: {last_exc}")

    def get_json(self, url: str) -> Any:
        _, _, body = self.get(url)
        return json.loads(body.decode("utf-8-sig"))

    def get_range(self, url: str, first: int, last: int, total: int | None = None) -> bytes:
        """Fetch bytes [first, last] (inclusive) and validate the length."""
        status, headers, body = self.get(url, (first, last))
        want = last - first + 1
        if status == 206:
            if len(body) != want:
                raise RuntimeError(f"short range read from {url}: got {len(body)}, want {want}")
            return body
        if status == 200:
            # Server ignored Range; acceptable only for small bodies (CDN parts).
            if total is not None and len(body) == total:
                return body[first : last + 1]
            raise RuntimeError(f"server ignored Range header for {url} (status 200, {len(body)} bytes)")
        raise RuntimeError(f"unexpected HTTP status {status} for {url}")


# --------------------------------------------------------------------------
# Seekable remote file backed by HTTP Range requests
# --------------------------------------------------------------------------


@dataclass
class Part:
    index: int
    offset: int
    size: int


class RemoteWabbajack(io.RawIOBase):
    """Read-only, seekable view of a remote ``.wabbajack`` file.

    Uses the CDN's chunked layout (definition.json.gz + parts/<n>) when
    available, otherwise plain Range requests on the URL itself.
    """

    def __init__(self, url: str, http: HttpClient) -> None:
        super().__init__()
        self.url = quote_url(url).rstrip("/")
        self.http = http
        self.pos = 0
        self.definition: dict | None = None
        self.parts: list[Part] = []
        self._part_offsets: list[int] = []
        self._cache_start = -1
        self._cache = b""
        self._load_layout()

    # -- layout discovery -------------------------------------------------
    def _load_layout(self) -> None:
        def_url = f"{self.url}/definition.json.gz"
        try:
            _, _, raw = self.http.get(def_url)
            data = gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw
            self.definition = json.loads(data.decode("utf-8-sig"))
            if not isinstance(self.definition, dict) or not self.definition.get("Parts"):
                raise ValueError("definition has no Parts")
        except urllib.error.HTTPError as exc:
            log(f"  no CDN definition (HTTP {exc.code}); falling back to direct Range requests")
            self.definition = None
        except (ValueError, OSError, EOFError) as exc:  # HTML page, bad gzip/JSON, ...
            log(f"  unusable CDN definition ({exc.__class__.__name__}); falling back to direct Range requests")
            self.definition = None
        if self.definition is not None:
            parts = sorted(
                (Part(int(p["Index"]), int(p["Offset"]), int(p["Size"])) for p in self.definition["Parts"]),
                key=lambda p: p.offset,
            )
            # Sanity: parts must tile the file without gaps or overlaps.
            expected = 0
            for p in parts:
                if p.offset != expected:
                    raise RuntimeError(f"CDN parts are not contiguous at offset {expected} (part {p.index})")
                expected += p.size
            self.size = int(self.definition["Size"])
            if expected != self.size:
                raise RuntimeError(f"CDN parts cover {expected} bytes but Size is {self.size}")
            self.parts = parts
            self._part_offsets = [p.offset for p in parts]
        else:
            status, headers, _ = self.http.get(self.url, (0, 0))
            content_range = {k.lower(): v for k, v in headers.items()}.get("content-range", "")
            m = re.search(r"/(\d+)$", content_range)
            if status != 206 or not m:
                raise RuntimeError(f"{self.url} supports neither the CDN part layout nor HTTP Range")
            self.size = int(m.group(1))

    # -- raw ranged access ------------------------------------------------
    def _fetch(self, offset: int, length: int) -> bytes:
        """Fetch ``length`` bytes starting at ``offset`` (may span parts)."""
        if not self.parts:
            return self.http.get_range(self.url, offset, offset + length - 1)
        out = bytearray()
        while length > 0:
            i = bisect.bisect_right(self._part_offsets, offset) - 1
            part = self.parts[i]
            lo = offset - part.offset
            hi = min(part.size, lo + length) - 1
            chunk = self.http.get_range(f"{self.url}/parts/{part.index}", lo, hi, total=part.size)
            out += chunk
            offset += len(chunk)
            length -= len(chunk)
        return bytes(out)

    # -- io.RawIOBase interface ------------------------------------------
    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, offset: int, whence: int = io.SEEK_SET) -> int:
        if whence == io.SEEK_SET:
            new = offset
        elif whence == io.SEEK_CUR:
            new = self.pos + offset
        elif whence == io.SEEK_END:
            new = self.size + offset
        else:
            raise ValueError(f"invalid whence {whence}")
        if new < 0:
            raise ValueError("negative seek position")
        self.pos = new
        return self.pos

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0:
            return b""
        start, end = self.pos, self.pos + n
        cache_end = self._cache_start + len(self._cache)
        if self._cache_start <= start and end <= cache_end:
            data = self._cache[start - self._cache_start : end - self._cache_start]
        elif n < READ_AHEAD:
            # Widen small reads (ZIP headers) and keep them cached.
            fetch_len = min(READ_AHEAD, self.size - start)
            self._cache = self._fetch(start, fetch_len)
            self._cache_start = start
            data = self._cache[:n]
        else:
            data = self._fetch(start, n)
        self.pos += len(data)
        return data

    def readinto(self, b: Any) -> int:
        data = self.read(len(b))
        b[: len(data)] = data
        return len(data)


# --------------------------------------------------------------------------
# Loading the modlist JSON
# --------------------------------------------------------------------------


@dataclass
class LoadedModlist:
    raw: bytes
    source: dict = field(default_factory=dict)
    gallery: dict | None = None


def _read_modlist_entry(zf: zipfile.ZipFile) -> tuple[bytes, dict]:
    names = {n: n for n in zf.namelist() if "/" not in n}
    entry_name = next((n for n in MODLIST_ENTRY_NAMES if n in names), None)
    if entry_name is None:
        sample = sorted(n for n in names if not re.fullmatch(r"[0-9a-f-]{36}", n))[:20]
        raise RuntimeError(f"no 'modlist' entry in the .wabbajack ZIP; non-GUID entries: {sample}")
    info = zf.getinfo(entry_name)
    log(
        f"  entry '{entry_name}': {info.compress_size:,} bytes compressed, "
        f"{info.file_size:,} bytes inflated (method {info.compress_type})"
    )
    raw = zf.read(entry_name)  # zipfile verifies CRC-32 here
    meta = {
        "entry_name": entry_name,
        "compress_type": info.compress_type,
        "compressed_size": info.compress_size,
        "uncompressed_size": info.file_size,
        "crc32": f"{info.CRC:08x}",
        "local_header_offset": info.header_offset,
        "zip_entry_count": len(zf.infolist()),
    }
    return raw, meta


def load_from_local_wabbajack(path: Path) -> LoadedModlist:
    log(f"reading local .wabbajack: {path}")
    with zipfile.ZipFile(path) as zf:
        raw, entry = _read_modlist_entry(zf)
    return LoadedModlist(
        raw=raw,
        source={
            "mode": "local_wabbajack",
            "wabbajack_file_name": path.name,
            "wabbajack_file_size": path.stat().st_size,
            "modlist_entry": entry,
        },
    )


def resolve_repository_url(http: HttpClient, repository_name: str) -> str:
    """Look the repository up in the official gallery index (with fallback)."""
    log(f"fetching gallery index: {REPOSITORIES_URL}")
    try:
        repos = http.get_json(REPOSITORIES_URL)
        for name, url in repos.items():
            if name.casefold() == repository_name.casefold():
                return str(url)
        log(f"  repository {repository_name!r} not in gallery index; using built-in URL")
    except Exception as exc:  # network or format problem -> documented fallback
        log(f"  gallery index unavailable ({exc}); using built-in URL")
    return MV_REPOSITORY_URL


def resolve_gallery_entry(http: HttpClient, repo_url: str, machine_url: str) -> dict:
    """Return the gallery entry whose links.machineURL matches ``machine_url``."""
    log(f"fetching repository metadata: {repo_url}")
    entries = http.get_json(repo_url)
    if isinstance(entries, dict):
        entries = [entries]
    for entry in entries:
        links = entry.get("links") or {}
        if str(links.get("machineURL", "")).casefold() == machine_url.casefold():
            return entry
    known = [(e.get("links") or {}).get("machineURL") for e in entries]
    raise RuntimeError(f"machineURL {machine_url!r} not found in {repo_url}; available: {known}")


def load_from_cdn(http: HttpClient, download_url: str, gallery: dict | None) -> LoadedModlist:
    log(f"opening remote .wabbajack: {download_url}")
    remote = RemoteWabbajack(download_url, http)
    log(
        f"  size {remote.size:,} bytes; layout: "
        + (f"CDN definition with {len(remote.parts)} parts" if remote.parts else "direct Range")
    )
    if gallery:
        meta_size = (gallery.get("download_metadata") or {}).get("Size")
        if meta_size is not None and int(meta_size) != remote.size:
            log(f"  WARNING: gallery download_metadata.Size={meta_size} differs from remote size {remote.size}")
    with zipfile.ZipFile(remote) as zf:
        raw, entry = _read_modlist_entry(zf)
    definition = remote.definition or {}
    uploaded_at = definition.get("UploadedAt")
    source = {
        "mode": "cdn_ranged",
        "download_url": download_url,
        "request_base_url": remote.url,
        "cdn_definition_url": f"{remote.url}/definition.json.gz" if remote.parts else None,
        "cdn_part_count": len(remote.parts),
        "cdn_part_size": remote.parts[0].size if remote.parts else None,
        "wabbajack_file_name": definition.get("OriginalFileName"),
        "wabbajack_file_size": remote.size,
        "wabbajack_hash_xxh64_b64": definition.get("Hash"),
        "cdn_uploaded_at": (
            _dt.datetime.fromtimestamp(int(uploaded_at), _dt.timezone.utc).isoformat().replace("+00:00", "Z")
            if uploaded_at
            else None
        ),
        "http_requests": http.requests,
        "http_bytes_transferred": http.bytes_transferred,
        "modlist_entry": entry,
    }
    return LoadedModlist(raw=raw, source=source, gallery=gallery)


def load_modlist(args: argparse.Namespace) -> LoadedModlist:
    if args.modlist_json:
        path = Path(args.modlist_json)
        log(f"reading extracted modlist JSON: {path}")
        raw = path.read_bytes()
        return LoadedModlist(raw=raw, source={"mode": "modlist_json", "modlist_json_file_name": path.name})
    if args.wabbajack:
        return load_from_local_wabbajack(Path(args.wabbajack))
    http = HttpClient()
    gallery = None
    download_url = args.download_url
    repo_url = None
    if not download_url:
        repo_url = args.repo_url or resolve_repository_url(http, args.repository_name)
        gallery = resolve_gallery_entry(http, repo_url, args.machine_url)
        download_url = gallery["links"]["download"]
        log(f"  gallery entry: {gallery.get('title')} {gallery.get('version')}")
    loaded = load_from_cdn(http, download_url, gallery)
    loaded.source["gallery_index_url"] = None if args.download_url or args.repo_url else REPOSITORIES_URL
    loaded.source["gallery_repository_url"] = repo_url
    loaded.source["gallery_machine_url"] = None if args.download_url else args.machine_url
    return loaded


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------


def split_path(path: str) -> list[str]:
    return [p for p in path.replace("/", "\\").split("\\") if p]


def type_name(obj: dict) -> str:
    """Short type name: 'NexusDownloader+State, Wabbajack.Lib' -> 'NexusDownloader'."""
    t = str(obj.get("$type", ""))
    return t.split(",")[0].split("+")[0].strip()


def archive_hash_of(directive: dict) -> str | None:
    """First element of ArchiveHashPath (list form, or WJ 2.x dict form)."""
    ahp = directive.get("ArchiveHashPath")
    if not ahp:
        return None
    if isinstance(ahp, list):
        return str(ahp[0])
    if isinstance(ahp, dict):
        base = ahp.get("BaseHash") or ahp.get("Hash")
        return str(base) if base is not None else None
    return None


def parse_meta_ini(meta: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in (meta or "").splitlines():
        if "=" in line and not line.lstrip().startswith(("[", ";", "#")):
            k, v = line.split("=", 1)
            out[k.strip().casefold()] = v.strip()
    return out


@dataclass
class ArchiveInfo:
    hash: str
    name: str
    size: int
    downloader: str
    source: str
    nexus_game: str = ""
    nexus_mod_id: str = ""
    nexus_file_id: str = ""
    nexus_version: str = ""
    nexus_mod_name: str = ""
    nexus_author: str = ""
    url: str = ""
    game_version: str = ""

    def list_token(self) -> str:
        return f"{clean_cell(self.name)}|{self.source}|{self.nexus_mod_id}|{self.nexus_file_id}"


def build_archive_index(archives: list[dict]) -> dict[str, ArchiveInfo]:
    index: dict[str, ArchiveInfo] = {}
    for a in archives:
        state = a.get("State") or {}
        downloader = type_name(state)
        source = SOURCE_BY_DOWNLOADER.get(downloader, "Other")
        meta = parse_meta_ini(a.get("Meta"))
        info = ArchiveInfo(
            hash=str(a.get("Hash")),
            name=str(a.get("Name") or ""),
            size=int(a.get("Size") or 0),
            downloader=downloader or "(none)",
            source=source,
        )
        if source == "Nexus":
            info.nexus_game = str(state.get("GameName") or meta.get("gamename") or "")
            info.nexus_mod_id = str(state.get("ModID") or meta.get("modid") or "")
            info.nexus_file_id = str(state.get("FileID") or meta.get("fileid") or "")
            info.nexus_version = str(state.get("Version") or "")
            info.nexus_mod_name = str(state.get("Name") or "")
            info.nexus_author = str(state.get("Author") or "")
        info.url = str(state.get("Url") or meta.get("directurl") or "")
        info.game_version = str(state.get("GameVersion") or "")
        index[info.hash] = info
    return index


def clean_cell(value: str) -> str:
    """Keep CSV cells single-line and free of the list separators."""
    return re.sub(r"[\r\n\t]+", " ", value).replace(";", ",").replace("|", "/").strip()


@dataclass
class FolderStats:
    names: Counter = field(default_factory=Counter)  # observed spellings
    file_count: int = 0
    patched_count: int = 0
    inline_count: int = 0
    total_bytes: int = 0
    archive_files: Counter = field(default_factory=Counter)  # hash -> files
    archive_bytes: Counter = field(default_factory=Counter)  # hash -> bytes
    skse_dlls: set = field(default_factory=set)
    plugins: set = field(default_factory=set)
    bsa_staged_files: int = 0

    @property
    def name(self) -> str:
        # Most frequent spelling; ties broken by ordinal order.
        return sorted(self.names.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def analyse(modlist: dict) -> tuple[list[dict], dict]:
    archives = build_archive_index(modlist.get("Archives") or [])
    directives = modlist.get("Directives") or []

    # TempID of every CreateBSA -> folder key (or None when outside mods\).
    bsa_targets: dict[str, tuple[str | None, str]] = {}
    for d in directives:
        if type_name(d) == "CreateBSA" and d.get("TempID"):
            parts = split_path(str(d.get("To", "")))
            folder = parts[1] if len(parts) >= 3 and parts[0].casefold() == "mods" else None
            bsa_targets[str(d["TempID"]).casefold()] = (folder, str(d.get("To", "")))

    folders: dict[str, FolderStats] = defaultdict(FolderStats)
    directive_types: Counter = Counter()
    destinations: Counter = Counter()
    ahp_depth: Counter = Counter()
    archive_use: Counter = Counter()
    unknown_archive_refs: Counter = Counter()
    bsa_staged: Counter = Counter()
    destinations_sub: Counter = Counter()
    unattributed_bsa_files = 0
    total_installed_bytes = 0
    all_directive_bytes = 0
    temp_bsa_bytes = 0

    for d in directives:
        dtype = type_name(d)
        directive_types[dtype] += 1
        parts = split_path(str(d.get("To", "")))
        size = int(d.get("Size") or 0)
        ahash = archive_hash_of(d)
        ahp = d.get("ArchiveHashPath")
        if isinstance(ahp, list):
            ahp_depth[str(len(ahp))] += 1
        elif isinstance(ahp, dict):
            ahp_depth[str(1 + len(ahp.get("Paths") or []))] += 1
        else:
            ahp_depth["0"] += 1
        all_directive_bytes += size
        if ahash is not None:
            archive_use[ahash] += 1
            if ahash not in archives:
                unknown_archive_refs[ahash] += 1

        top = parts[0] if len(parts) > 1 else "(root files)"
        destinations[top] += 1
        if len(parts) > 2 and top.casefold() not in ("mods", TEMP_BSA_ROOT):
            destinations_sub[f"{parts[0]}\\{parts[1]}"] += 1

        # Staged BSA content -> attribute archive usage to the BSA's folder.
        if top.casefold() == TEMP_BSA_ROOT and len(parts) >= 2:
            folder, bsa_to = bsa_targets.get(parts[1].casefold(), (None, ""))
            bsa_staged[bsa_to or f"(unknown TempID {parts[1]})"] += 1
            temp_bsa_bytes += size
            if folder is None:
                if not bsa_to:
                    unattributed_bsa_files += 1
                continue
            st = folders[folder.casefold()]
            st.names[folder] += 0  # register spelling without weighting it
            st.bsa_staged_files += 1
            if ahash is not None:
                st.archive_files[ahash] += 1
                st.archive_bytes[ahash] += size
            continue

        total_installed_bytes += size
        if not (len(parts) >= 3 and parts[0].casefold() == "mods"):
            continue
        folder = parts[1]
        rel = parts[2:]
        st = folders[folder.casefold()]
        st.names[folder] += 1
        st.file_count += 1
        st.total_bytes += size
        if dtype in PATCHED_TYPES:
            st.patched_count += 1
        if dtype in INLINE_TYPES:
            st.inline_count += 1
        if ahash is not None:
            st.archive_files[ahash] += 1
            st.archive_bytes[ahash] += size
        fname = rel[-1]
        low = fname.casefold()
        if len(rel) == 1 and low.endswith(PLUGIN_EXTS):
            st.plugins.add(fname)
        if len(rel) == 3 and [r.casefold() for r in rel[:2]] == ["skse", "plugins"] and low.endswith(".dll"):
            st.skse_dlls.add(fname)

    rows: list[dict] = []
    for key in sorted(folders, key=lambda k: (k, folders[k].name)):
        st = folders[key]

        def rank(h: str) -> tuple:
            a = archives.get(h)
            return (-st.archive_files[h], -st.archive_bytes[h], (a.name if a else "").casefold(), h)

        ranked = sorted(st.archive_files, key=rank)
        primary = archives.get(ranked[0]) if ranked else None
        tokens = [archives[h].list_token() if h in archives else f"(unknown {h})|Other||" for h in ranked]
        row = {
            "folder": st.name,
            "primary_archive_name": primary.name if primary else "",
            "primary_source": primary.source if primary else ("InlineOnly" if st.file_count else "Other"),
            "nexus_mod_id": primary.nexus_mod_id if primary and primary.source == "Nexus" else "",
            "nexus_file_id": primary.nexus_file_id if primary and primary.source == "Nexus" else "",
            "nexus_version": primary.nexus_version if primary and primary.source == "Nexus" else "",
            "nexus_mod_name": primary.nexus_mod_name if primary and primary.source == "Nexus" else "",
            "archive_count": len(ranked),
            "all_archives": ";".join(tokens),
            "file_count": st.file_count,
            "patched_count": st.patched_count,
            "inline_count": st.inline_count,
            "total_bytes": st.total_bytes,
            "skse_dlls": ";".join(sorted(st.skse_dlls, key=lambda s: (s.casefold(), s))),
            "plugins": ";".join(sorted(st.plugins, key=lambda s: (s.casefold(), s))),
        }
        row["_bsa_staged_files"] = st.bsa_staged_files
        row["_archive_hashes"] = ranked
        rows.append(row)

    rows.sort(key=lambda r: (r["folder"].casefold(), r["folder"]))

    # ---- modlist-level statistics -------------------------------------
    archives_by_source = Counter(a.source for a in archives.values())
    archives_by_downloader = Counter(a.downloader for a in archives.values())
    http_hosts = Counter(
        urllib.parse.urlsplit(a.url).hostname or "(none)" for a in archives.values() if a.source == "HTTP"
    )
    nexus_games = Counter(a.nexus_game for a in archives.values() if a.source == "Nexus")
    game_versions = Counter(a.game_version for a in archives.values() if a.source == "GameFile")
    default_game = str(modlist.get("GameType") or "")
    non_default_nexus = sorted(
        (
            {"name": a.name, "game": a.nexus_game, "mod_id": a.nexus_mod_id, "file_id": a.nexus_file_id}
            for a in archives.values()
            if a.source == "Nexus" and a.nexus_game.casefold() != default_game.casefold()
        ),
        key=lambda x: (x["name"].casefold(), x["file_id"]),
    )
    folder_rows = rows
    def is_separator(r: dict) -> bool:
        return r["folder"].casefold().endswith("_separator")

    separators = [r for r in folder_rows if is_separator(r)]
    multi = [r for r in folder_rows if r["archive_count"] > 1]
    non_nexus_primary = sorted(
        (
            {"folder": r["folder"], "primary_source": r["primary_source"], "primary_archive_name": r["primary_archive_name"]}
            for r in folder_rows
            if r["primary_source"] not in ("Nexus", "InlineOnly")
        ),
        key=lambda x: (x["folder"].casefold(), x["folder"]),
    )
    folders_per_archive: Counter = Counter()
    for r in folder_rows:
        folders_per_archive.update(r["_archive_hashes"])

    stats = {
        "archives": archives,
        "counts": {
            "archives_total": len(archives),
            "archives_by_source": {k: archives_by_source.get(k, 0) for k in SOURCE_LABELS},
            "archives_by_downloader_type": dict(sorted(archives_by_downloader.items())),
            "archives_referenced_by_directives": sum(1 for h in archives if archive_use[h]),
            "archives_unreferenced": sum(1 for h in archives if not archive_use[h]),
            "unknown_archive_references": sum(unknown_archive_refs.values()),
            "archives_used_by_multiple_folders": sum(1 for v in folders_per_archive.values() if v > 1),
            "http_hosts": dict(sorted(http_hosts.items())),
            "nexus_game_names": dict(sorted(nexus_games.items())),
            "directives_total": len(directives),
            "directives_by_type": dict(sorted(directive_types.items())),
            "archive_hash_path_depth": dict(sorted(ahp_depth.items(), key=lambda kv: int(kv[0]))),
            "mod_folders": len(folder_rows),
            "mod_folders_separators": len(separators),
            "mod_folders_non_separator": len(folder_rows) - len(separators),
            "mod_folders_by_primary_source": dict(
                sorted(Counter(r["primary_source"] for r in folder_rows).items())
            ),
            "mod_folders_inline_only_non_separator": sum(
                1 for r in folder_rows if r["primary_source"] == "InlineOnly" and not is_separator(r)
            ),
            "mod_folders_with_multiple_archives": len(multi),
            "mod_folders_with_patched_files": sum(1 for r in folder_rows if r["patched_count"]),
            "mod_folders_with_skse_dlls": sum(1 for r in folder_rows if r["skse_dlls"]),
            "mod_folders_with_plugins": sum(1 for r in folder_rows if r["plugins"]),
            "mod_folders_with_bsa_built_by_wabbajack": sum(1 for r in folder_rows if r["_bsa_staged_files"]),
            "plugins_in_mod_folders": sum(len(r["plugins"].split(";")) for r in folder_rows if r["plugins"]),
            "skse_dlls_in_mod_folders": sum(len(r["skse_dlls"].split(";")) for r in folder_rows if r["skse_dlls"]),
        },
        "sizes": {
            "archives_total_bytes": sum(a.size for a in archives.values()),
            "all_directives_total_bytes": all_directive_bytes,
            "installed_files_total_bytes": total_installed_bytes,
            "temp_bsa_files_total_bytes": temp_bsa_bytes,
            "mods_total_bytes": sum(r["total_bytes"] for r in folder_rows),
            "note": (
                "Sums of Archive.Size / Directive.Size. all_directives_total_bytes should equal the gallery's "
                "SizeOfInstalledFiles; installed_files_total_bytes excludes TEMP_BSA_FILES staging files; "
                "CreateBSA directives report Size 0."
            ),
        },
        "game_files": {
            "game_type": default_game,
            "other_games": modlist.get("OtherGames") or [],
            "game_file_source_archives": archives_by_source.get("GameFile", 0),
            "game_versions": dict(sorted(game_versions.items())),
            "nexus_archives_for_other_games": non_default_nexus,
        },
        "destinations": {
            "by_top_level": dict(sorted(destinations.items(), key=lambda kv: (kv[0].casefold(), kv[0]))),
            "by_second_level_outside_mods": dict(
                sorted(destinations_sub.items(), key=lambda kv: (kv[0].casefold(), kv[0]))
            ),
            "temp_bsa_files_by_target_bsa": dict(sorted(bsa_staged.items(), key=lambda kv: (kv[0].casefold(), kv[0]))),
            "temp_bsa_files_unattributed": unattributed_bsa_files,
            "note": (
                "Counts of directives by the first component of 'To'. TEMP_BSA_FILES are staging "
                "files packed into the listed BSAs by CreateBSA; they are not installed loose."
            ),
        },
        "folders_with_non_nexus_primary": non_nexus_primary,
    }
    return rows, stats


# --------------------------------------------------------------------------
# Optional comparison with an MO2 modlist.txt
# --------------------------------------------------------------------------


def compare_mo2_modlist(path: Path, rows: list[dict]) -> dict:
    """Overlap between CSV folders and '+'/'-' entries of an MO2 modlist.txt."""
    listed: dict[str, str] = {}
    unmanaged = 0
    enabled = 0
    for line in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = line.rstrip("\r\n")
        if not line or line.startswith("#"):
            continue
        state, name = line[0], line[1:]
        if state == "*":
            unmanaged += 1
            continue
        if state not in "+-":
            continue
        listed.setdefault(name.casefold(), name)
        enabled += state == "+"
    ours = {r["folder"].casefold(): r["folder"] for r in rows}
    both = listed.keys() & ours.keys()
    only_txt = sorted((listed[k] for k in listed.keys() - ours.keys()), key=str.casefold)
    only_wj = sorted((ours[k] for k in ours.keys() - listed.keys()), key=str.casefold)

    def split(names: list[str]) -> dict:
        seps = [n for n in names if n.casefold().endswith("_separator")]
        return {"count": len(names), "separators": len(seps), "names": names}

    return {
        "file_name": path.name,
        "entries_plus_minus": len(listed),
        "entries_enabled": enabled,
        "entries_unmanaged_star": unmanaged,
        "separators_in_txt": sum(1 for k in listed if k.endswith("_separator")),
        "overlap": len(both),
        "only_in_modlist_txt": split(only_txt),
        "only_in_wabbajack": split(only_wj),
    }


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(CSV_COLUMNS)
        for r in rows:
            writer.writerow([r[c] for c in CSV_COLUMNS])


def build_meta(loaded: LoadedModlist, modlist: dict, stats: dict, fetched_date: str, comparison: dict | None) -> dict:
    gallery = loaded.gallery
    gallery_meta = None
    if gallery:
        gallery_meta = {
            "title": gallery.get("title"),
            "version": gallery.get("version"),
            "author": gallery.get("author"),
            "maintainers": gallery.get("maintainers"),
            "game": gallery.get("game"),
            "official": gallery.get("official"),
            "tags": gallery.get("tags"),
            "nsfw": gallery.get("nsfw"),
            "date_updated": gallery.get("dateUpdated"),
            "machine_url": (gallery.get("links") or {}).get("machineURL"),
            "readme": (gallery.get("links") or {}).get("readme"),
            "nexus_collection": (gallery.get("links") or {}).get("nexusCollection"),
            "download_metadata": gallery.get("download_metadata"),
        }
    source = dict(loaded.source)
    source["modlist_json_bytes"] = len(loaded.raw)
    source["modlist_json_sha256"] = hashlib.sha256(loaded.raw).hexdigest()
    meta = {
        "schema": "mv_wabbajack_map/1",
        "fetched_date": fetched_date,
        "generator": "tools/analysis/mv_wabbajack_map.py",
        "modlist": {
            "name": modlist.get("Name"),
            "version": modlist.get("Version"),
            "author": modlist.get("Author"),
            "description": modlist.get("Description"),
            "game_type": modlist.get("GameType"),
            "wabbajack_version": modlist.get("WabbajackVersion"),
            "is_nsfw": modlist.get("IsNSFW"),
            "website": modlist.get("Website"),
            "readme": modlist.get("Readme"),
            "community": modlist.get("Community"),
        },
        "source": source,
        "gallery": gallery_meta,
        "game_files": stats["game_files"],
        "counts": stats["counts"],
        "sizes": stats["sizes"],
        "destinations": stats["destinations"],
        "folders_with_non_nexus_primary": stats["folders_with_non_nexus_primary"],
        "mo2_modlist_comparison": comparison,
        "csv_rules": {
            "primary": "archive providing the most files to the folder (ties: bytes, name, hash)",
            "all_archives": "name|source|nexus_mod_id|nexus_file_id, ordered like primary ranking",
            "file_count": "directives whose To is mods\\<folder>\\... (loose files; a built BSA counts once)",
            "bsa_staging": "TEMP_BSA_FILES\\<TempID> files count toward archive attribution of the BSA's folder only",
            "patched_count": "PatchedFromArchive (+TransformedTexture)",
            "inline_count": "InlineFile + RemappedInlineFile",
            "skse_dlls": "<folder>\\SKSE\\Plugins\\*.dll",
            "plugins": "*.esp/*.esm/*.esl at the folder root",
        },
    }
    return meta


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    src = p.add_mutually_exclusive_group()
    src.add_argument("--wabbajack", metavar="PATH", help="local .wabbajack file to read the 'modlist' entry from")
    src.add_argument("--modlist-json", metavar="PATH", help="already extracted 'modlist' JSON file")
    src.add_argument("--download-url", metavar="URL", help="remote .wabbajack URL (skips the gallery lookup)")
    p.add_argument("--repository-name", default=MV_REPOSITORY_NAME, help="gallery repository name (default: MagesAndVikings)")
    p.add_argument("--repo-url", default=None, help="repository modlists.json URL (skips the gallery index lookup)")
    p.add_argument("--machine-url", default=MV_MACHINE_URL, help="links.machineURL of the gallery entry")
    p.add_argument("--out-dir", default="data/analysis", help="output directory (default: data/analysis)")
    p.add_argument("--out-prefix", default="mv", help="output file prefix (default: mv)")
    p.add_argument("--save-modlist-json", metavar="PATH", help="also write the extracted 'modlist' JSON here (cache)")
    p.add_argument("--compare-mo2-modlist", metavar="PATH", help="MO2 modlist.txt to compare the folder set against")
    p.add_argument("--fetched-date", default=None, help="date recorded in the meta JSON (default: today, UTC)")
    return p.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    fetched_date = args.fetched_date or _dt.datetime.now(_dt.timezone.utc).date().isoformat()

    loaded = load_modlist(args)
    if args.save_modlist_json:
        Path(args.save_modlist_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.save_modlist_json).write_bytes(loaded.raw)
        log(f"saved modlist JSON: {args.save_modlist_json}")

    log("parsing modlist JSON ...")
    modlist = json.loads(loaded.raw.decode("utf-8-sig"))
    if not isinstance(modlist, dict) or "Directives" not in modlist or "Archives" not in modlist:
        raise RuntimeError("the 'modlist' JSON has no Archives/Directives; unsupported Wabbajack format")
    log(
        f"  {modlist.get('Name')} {modlist.get('Version')}: "
        f"{len(modlist['Archives']):,} archives, {len(modlist['Directives']):,} directives"
    )

    rows, stats = analyse(modlist)
    comparison = compare_mo2_modlist(Path(args.compare_mo2_modlist), rows) if args.compare_mo2_modlist else None
    meta = build_meta(loaded, modlist, stats, fetched_date, comparison)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"{args.out_prefix}_folder_map.csv"
    meta_path = out_dir / f"{args.out_prefix}_modlist_meta.json"
    write_csv(csv_path, rows)
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    c = stats["counts"]
    log(f"wrote {csv_path} ({len(rows)} folders) and {meta_path}")
    log(f"  primary sources: {c['mod_folders_by_primary_source']}")
    log(f"  archives by source: {c['archives_by_source']}")
    if comparison:
        log(
            f"  vs {comparison['file_name']}: overlap {comparison['overlap']}, "
            f"only in txt {comparison['only_in_modlist_txt']['count']}, "
            f"only in wabbajack {comparison['only_in_wabbajack']['count']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
