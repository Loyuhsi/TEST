"""Build a CJK-capable Interface\\fontconfig.txt that keeps the UI mod's font names.

產生可顯示中文的 fontconfig.txt：保留 Edge UI／Sanguis 等介面 mod 使用的字型名稱，全部對應到中文字型。

Skyrim 1.5.97 reads only Interface\\fontconfig.txt, so the official fontconfig_cn.txt is merged with
the fontconfig.txt that currently wins in the profile (usually Edge UI / Mist's Font Replacer):
every "$Name" mapping points at the official Chinese font, fontlibs from both are kept.

    python tools\\zh\\fontconfig.py --pm D:\\PM --official "D:\\PM\\mods\\ZH - 官方繁中字串\\interface\\fontconfig_cn.txt" ^
        --out-mod "D:\\PM\\mods\\ZH Overrides" --apply
Put "ZH Overrides" at the very top of the left pane (highest priority) so its fontconfig.txt wins.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pm import fsutil, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report  # noqa: E402

MAP_RE = re.compile(r'^\s*map\s+"(?P<name>[^"]+)"\s*=\s*"(?P<font>[^"]+)"\s*(?P<style>\w+)?', re.I)
LIB_RE = re.compile(r'^\s*fontlib\s+"(?P<lib>[^"]+)"', re.I)
VALID_RE = re.compile(r'^\s*validNameChars\s+"(?P<chars>.*)"\s*$', re.I)
DEFAULT_KEYS = ("$EverywhereFont", "$EverywhereMediumFont", "$StartMenuFont")


def read_text(path: Path) -> str:
    raw = Path(path).read_bytes()
    for bom, enc in ((b"\xff\xfe", "utf-16-le"), (b"\xef\xbb\xbf", "utf-8")):
        if raw.startswith(bom):
            return raw[len(bom):].decode(enc, errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


def parse(text: str) -> dict:
    libs, maps, valid = [], {}, None
    for line in text.splitlines():
        if m := LIB_RE.match(line):
            libs.append(m.group("lib"))
        elif m := MAP_RE.match(line):
            maps[m.group("name")] = (m.group("font"), m.group("style") or "Normal")
        elif m := VALID_RE.match(line):
            valid = m.group("chars")
    return {"libs": libs, "maps": maps, "valid": valid}


def merge(official: dict, current: dict) -> tuple[str, list[str]]:
    default = next((official["maps"][k] for k in DEFAULT_KEYS if k in official["maps"]), None)
    if default is None and official["maps"]:
        default = next(iter(official["maps"].values()))
    libs = []
    for lib in official["libs"] + current["libs"]:
        if lib.lower() not in {x.lower() for x in libs}:
            libs.append(lib)
    names = list(official["maps"]) + [n for n in current["maps"] if n not in official["maps"]]
    remapped = []
    lines = [f'fontlib "{lib}"' for lib in libs] + [""]
    for name in names:
        if name in official["maps"]:
            font, style = official["maps"][name]
        else:
            font, style = default
            remapped.append(name)
        lines.append(f'map "{name}" = "{font}" {style}')
    if official["valid"] is not None:
        lines += ["", f'validNameChars "{official["valid"]}"']
    return "\r\n".join(lines) + "\r\n", remapped


def winning_fontconfig(pm: Path, profile: str) -> Path | None:
    prof = vfs.open_profile(pm, profile)
    for folder in prof.enabled_folders:
        for cand in ("interface/fontconfig.txt", "Interface/fontconfig.txt", "interface/FontConfig.txt"):
            p = prof.mods_dir / folder / cand
            if p.exists():
                return p
    return None


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="合併官方中文 fontconfig 與介面 mod 的字型名稱（預設試跑）")
    ap.add_argument("--official", required=True, type=Path, help="fontconfig_cn.txt")
    ap.add_argument("--current", type=Path, default=None, help="目前生效的 fontconfig.txt（預設自動從設定檔找）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--out-mod", required=True, type=Path)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    rep = Report("zh_fontconfig")
    current_path = args.current or winning_fontconfig(args.pm, args.profile)
    official = parse(read_text(args.official))
    current = parse(read_text(current_path)) if current_path and current_path.exists() else \
        {"libs": [], "maps": {}, "valid": None}
    text, remapped = merge(official, current)
    rep.add("current", "INFO", "目前生效的 fontconfig.txt", str(current_path.parent.parent.name) if current_path else "無")
    rep.add("maps", "PASS", "字型對應", f"官方 {len(official['maps'])} 個；介面 mod 額外名稱改指向中文字型 {len(remapped)} 個"
            + (f"：{', '.join(remapped[:10])}" if remapped else ""))
    if args.apply:
        dest = args.out_mod / "interface" / "fontconfig.txt"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        rep.add("write", "PASS", "已寫入", str(dest))
    path = rep.save(args.out, stem="zh_fontconfig")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
