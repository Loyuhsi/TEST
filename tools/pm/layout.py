"""Find where the game data starts inside a mod archive (MO2's "data root").

判斷壓縮檔裡遊戲資料的起點：FOMOD 交給 MO2；結構不明確、或插件和目標不符的交給人工。

Mirrors MO2's simple installer: data at the top level, or reached through single wrapper
folders (including "Data"). Stricter than MO2 wherever a wrong guess would silently install
the wrong thing: unknown folders or loose files next to the data (option folders, ENB or
game-root files) are refused, and so are plugins that the target load order does not expect.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

DATA_DIRS = frozenset({
    "meshes", "textures", "scripts", "source", "interface", "sound", "music", "strings", "video",
    "fonts", "menus", "shaders", "shadersfx", "materials", "trees", "facegen", "grass", "seq",
    "lodsettings", "distantlod", "dyndolod", "skse", "mcm", "dialogueviews", "calientetools",
    "netscriptframework", "dllplugins", "nemesis_engine", "pandora_engine", "lightplacer",
    "pbrnifpatcher", "pbrtexturesets", "dragonbornvoiceover", "seasons",
})
DATA_EXTS = frozenset({".esp", ".esm", ".esl", ".bsa", ".ba2", ".ini", ".modgroups"})
PLUGIN_EXTS = frozenset({".esp", ".esm", ".esl"})
DOC_EXTS = frozenset({".txt", ".md", ".pdf", ".url", ".htm", ".html", ".rtf", ".doc", ".docx",
                      ".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"})
DOC_DIRS = frozenset({"fomod", "docs", "doc", "documentation", "readme", "readmes", "screenshots",
                      "images", "img", "pictures", "preview", "previews", "license", "licenses",
                      "credits"})
SKIP_NAMES = frozenset({"meta.ini", "desktop.ini", "thumbs.db"})   # never installed
MAX_DEPTH = 4
_DRIVE = re.compile(r"^[A-Za-z]:")


@dataclass(frozen=True)
class Layout:
    kind: str                       # "simple" (install it), "fomod" (MO2 installer) or "manual"
    root: str = ""                  # data root inside the archive, '' = archive top level
    reason: str = ""
    plugins: tuple[str, ...] = ()   # plugin files found at the data root


def normalise(path: str) -> str:
    p = path.replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    return p


def _ext(name: str) -> str:
    dot = name.rfind(".")
    return name[dot:].lower() if dot > 0 else ""


def _is_doc_file(low: str) -> bool:
    return low in SKIP_NAMES or _ext(low) in DOC_EXTS


def _unsafe(path: str) -> bool:
    return path.startswith("/") or bool(_DRIVE.match(path)) or ".." in path.split("/")


def _level(paths: list[str], prefix: str) -> tuple[dict[str, str], dict[str, str]]:
    """Entries directly under prefix: ({lower: dir name}, {lower: file name})."""
    dirs: dict[str, str] = {}
    files: dict[str, str] = {}
    lead = prefix.lower() + "/" if prefix else ""
    for p in paths:
        if not p.lower().startswith(lead):
            continue
        head, sep, _ = p[len(lead):].partition("/")
        if sep:
            dirs.setdefault(head.lower(), head)
        elif head:
            files.setdefault(head.lower(), head)
    return dirs, files


def _has_data(dirs: dict[str, str], files: dict[str, str]) -> bool:
    return any(d in DATA_DIRS for d in dirs) or any(
        _ext(f) in DATA_EXTS and f not in SKIP_NAMES for f in files)


def _join(names: Iterable[str]) -> str:
    items = sorted(names, key=str.lower)
    return "、".join(items[:6]) + ("…" if len(items) > 6 else "")


def _check_root(prefix: str, dirs: dict[str, str], files: dict[str, str],
                expected: Iterable[str], target: set[str] | None, accept: bool) -> Layout:
    plugins = tuple(sorted((f for k, f in files.items() if _ext(k) in PLUGIN_EXTS), key=str.lower))
    have = {p.lower() for p in plugins}
    soft = []   # doubts a person may clear after looking at the archive (accept=True)
    unknown_files = [f for k, f in files.items() if _ext(k) not in DATA_EXTS and not _is_doc_file(k)]
    if unknown_files:   # game-root files (ENB) or a tool shipped as a mod (Pandora's .exe)
        soft.append(f"資料根目錄有不認得的檔案：{_join(unknown_files)}")
    unknown_dirs = [d for k, d in dirs.items() if k not in DATA_DIRS and k not in DOC_DIRS]
    if unknown_dirs:
        soft.append(f"資料根目錄有不認得的資料夾：{_join(unknown_dirs)}")
    missing = [p.strip() for p in expected if p.strip() and p.strip().lower() not in have]
    if missing:
        soft.append(f"預期的插件不在資料根目錄：{_join(missing)}")
    extra = [p for p in plugins if target is not None and p.lower() not in target]
    if extra:
        soft.append(f"插件不在目標 plugins.txt：{_join(extra)}")
    if soft and not accept:
        return Layout("manual", prefix, "；".join(soft), plugins)
    return Layout("simple", prefix, ("人工確認後放行：" + "；".join(soft)) if soft else "", plugins)


def classify(files: Iterable[str], expected_plugins: Iterable[str] = (),
             target_plugins: set[str] | None = None, accept: bool = False) -> Layout:
    """Decide how to install an archive from the paths of the files inside it.

    expected_plugins must all sit at the data root; target_plugins (lower-case names), when
    given, must contain every plugin found there; folders and files beside the data must be
    known. accept=True (a person checked the archive) lets those doubts pass, noted in the
    reason; FOMOD installers, unsafe paths and a missing or ambiguous data root still stop.
    """
    paths = [p for p in (normalise(f) for f in files) if p]
    if not paths:
        return Layout("manual", reason="壓縮檔是空的")
    bad = [p for p in paths if _unsafe(p)]
    if bad:
        return Layout("manual", reason=f"路徑不安全：{bad[0]}")
    if any(p.lower() == "fomod/moduleconfig.xml" or p.lower().endswith("/fomod/moduleconfig.xml")
           for p in paths):
        return Layout("fomod", reason="FOMOD 安裝程式：用 MO2 安裝")
    prefix = ""
    for _ in range(MAX_DEPTH + 1):
        dirs, files_here = _level(paths, prefix)
        if _has_data(dirs, files_here):
            return _check_root(prefix, dirs, files_here, expected_plugins, target_plugins, accept)
        inner = [d for k, d in dirs.items() if k not in DOC_DIRS]
        loose = [f for k, f in files_here.items() if not _is_doc_file(k)]
        if len(inner) == 1 and not loose:
            prefix = f"{prefix}/{inner[0]}" if prefix else inner[0]
            continue
        where = f"「{prefix}」裡" if prefix else "最上層"
        if not inner and not loose:
            return Layout("manual", prefix, f"{where}沒有遊戲資料")
        return Layout("manual", prefix, f"{where}找不到資料根目錄：{_join(inner + loose)}")
    return Layout("manual", prefix, "外層資料夾太多層")
