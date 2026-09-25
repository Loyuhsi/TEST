"""Shared helpers for the Chinese layer: DSD JSON, MCM translation txt, CJK checks, work items.

繁中化共用工具：DSD JSON、MCM 翻譯檔（UTF-16LE＋BOM）、中文判斷、待翻譯項目。

DSD (Dynamic String Distributor) files live at
    <mod>/SKSE/Plugins/DynamicStringDistributor/<Plugin.esp>/<name>.json
and hold a JSON list of {"form_id": "0x0176CD|Skyrim.esm", "type": "WEAP FULL",
"index": 2 (optional), "editor_id": (GMST only), "string": "..."}.
Interface translation files are interface/translations/<name>_<LANGUAGE>.txt, UTF-16LE with BOM,
one "$KEY<TAB>value" per line.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

TOOLS = Path(__file__).resolve().parents[1]
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

DSD_DIR = Path("SKSE") / "Plugins" / "DynamicStringDistributor"
CJK_RE = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
LATIN_RE = re.compile(r"[A-Za-z]")
# Tokens that must survive translation unchanged.
PLACEHOLDER_RE = re.compile(
    r"<[^<>\n]{1,80}>"                 # <Alias=Player>, <Global=X>, <font ...>, <br>
    r"|%(?:\d+\$)?[-+ #0]*\d*(?:\.\d+)?[sdifuxXc%]"   # printf
    r"|\{\d+\}"                          # {0}
    r"|\$[A-Za-z_][A-Za-z0-9_]*"       # $MCM_Key references
    r"|\[PageBreak\]|\[pagebreak\]"
)


def has_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text or ""))


def needs_translation(text: str) -> bool:
    """Heuristic: visible English words and no Chinese yet."""
    t = PLACEHOLDER_RE.sub("", text or "")
    return bool(LATIN_RE.search(t)) and not has_cjk(t)


def placeholders(text: str) -> list[str]:
    return sorted(PLACEHOLDER_RE.findall(text or ""))


# ------------------------------------------------------------------ keys
def norm_form(form_id: str, light: bool = False) -> tuple[int, str]:
    """'0x0176CD|Skyrim.esm', '050176CD|Skyrim.esm', 'FE000800|X.esl' -> (local id, plugin lower)."""
    fid, _, plugin = form_id.partition("|")
    fid = fid.strip()
    if fid.lower().startswith("0x"):
        fid = fid[2:]
    value = int(fid or "0", 16)
    if light or len(fid) == 8 and fid[:2].upper() == "FE":
        value &= 0xFFF
    else:
        value &= 0xFFFFFF
    return value, plugin.strip().lower()


def string_key(form_id: str, rtype: str, index: int | None, editor_id: str | None = None,
               light_plugins: set[str] | frozenset = frozenset()) -> tuple:
    if rtype.upper() == "GMST DATA":
        return ("GMST", (editor_id or "").lower())
    local, plugin = norm_form(form_id)
    if plugin in light_plugins:
        local &= 0xFFF
    return (local, plugin, rtype.upper(), index if index is not None else -1)


# ------------------------------------------------------------------ DSD
def read_dsd_file(path: Path) -> list[dict]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return []
    return [d for d in data if isinstance(d, dict) and "string" in d] if isinstance(data, list) else []


def iter_dsd(mod_dir: Path) -> Iterator[tuple[str, Path]]:
    """Yield (target plugin folder name, json path) for DSD files inside one mod."""
    base = Path(mod_dir) / DSD_DIR
    if not base.is_dir():
        for cand in ("skse/plugins/dynamicstringdistributor", "SKSE/plugins/DynamicStringDistributor"):
            if (Path(mod_dir) / cand).is_dir():
                base = Path(mod_dir) / cand
                break
        else:
            return
    for plugin_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        for js in sorted(plugin_dir.glob("*.json"), key=lambda p: p.name.lower()):
            yield plugin_dir.name, js


def write_dsd_file(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = []
    for e in entries:
        d = {"form_id": e["form_id"], "type": e["type"], "string": e["string"]}
        if e.get("index") is not None and e.get("index") != -1:
            d["index"] = int(e["index"])
        if e.get("editor_id") and e["type"].upper() == "GMST DATA":
            d["editor_id"] = e["editor_id"]
        clean.append(d)
    path.write_text(json.dumps(clean, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ interface translation txt
def read_translation_txt(path: Path) -> dict[str, str]:
    raw = Path(path).read_bytes()
    return parse_translation_bytes(raw)


def parse_translation_bytes(raw: bytes) -> dict[str, str]:
    if raw.startswith(b"\xff\xfe"):
        text = raw[2:].decode("utf-16-le", errors="replace")
    elif raw.startswith(b"\xfe\xff"):
        text = raw[2:].decode("utf-16-be", errors="replace")
    elif raw.startswith(b"\xef\xbb\xbf"):
        text = raw[3:].decode("utf-8", errors="replace")
    else:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("utf-16-le", errors="replace")
    out: dict[str, str] = {}
    for line in text.splitlines():
        if "\t" not in line or not line.startswith("$"):
            continue
        k, _, v = line.partition("\t")
        out[k.strip()] = v.rstrip("\r")
    return out


def translation_bytes(table: dict[str, str]) -> bytes:
    """UTF-16LE with BOM and CRLF (what SkyUI and STPP-NG expect)."""
    body = "\r\n".join(f"{k}\t{v}" for k, v in table.items()) + "\r\n"
    return b"\xff\xfe" + body.encode("utf-16-le")


def write_translation_txt(path: Path, table: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(translation_bytes(table))


def check_translation_encoding(raw: bytes) -> str:
    if raw.startswith(b"\xff\xfe"):
        return "utf-16le-bom"
    if raw.startswith(b"\xfe\xff"):
        return "utf-16be-bom"
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-bom"
    return "no-bom"


# ------------------------------------------------------------------ work items
@dataclass
class WorkItem:
    id: str
    kind: str            # dsd | mcm | strings
    source: str          # English text
    context: str = ""    # e.g. "WEAP FULL", MCM key, file name
    plugin: str = ""
    form_id: str = ""
    type: str = ""
    index: int | None = None
    editor_id: str | None = None
    file: str = ""       # mcm: translation base name; strings: table file name
    key: str = ""        # mcm key or string id
    extra: dict = field(default_factory=dict)

    @staticmethod
    def make_id(*parts) -> str:
        return hashlib.sha1("\x1f".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:16]


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    return n


def read_jsonl(path: Path) -> list[dict]:
    if not Path(path).exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def items_to_rows(items: Iterable[WorkItem]) -> Iterator[dict]:
    for it in items:
        yield asdict(it)


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]
