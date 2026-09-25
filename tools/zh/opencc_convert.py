"""Convert Simplified Chinese translation files to Taiwan Traditional (OpenCC s2twp) + noun pins.

把簡中翻譯檔轉成台灣繁體（OpenCC s2twp），再用對照表把名詞「釘」成官方繁中用語。

Handles, keeping each file's format and encoding:
  DSD JSON (only the "string" values), interface *_chinese.txt (only values, UTF-16LE+BOM kept),
  other JSON (string values that contain Chinese), and *_chinese.strings/.dlstrings/.ilstrings.
Default is a dry run with a report. Write converted copies with --out-dir (mirrors the tree),
or convert in place with --in-place (a .bak copy is kept next to each changed file).

    python -m pip install opencc
    python tools\\zh\\opencc_convert.py "D:\\PM\\mods\\ZH - 蘇禾 Nolvus DSD" --pins D:\\PM\\zh-work\\pins_chs_cht.tsv --in-place
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pm import fsutil, strings as st  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report  # noqa: E402
from zh.common import (check_translation_encoding, has_cjk, parse_translation_bytes,  # noqa: E402
                       translation_bytes)


def load_converter(config: str = "s2twp"):
    try:
        import opencc  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise SystemExit("需要 OpenCC：python -m pip install opencc") from e
    for name in (config, config + ".json"):
        try:
            return opencc.OpenCC(name)
        except Exception:  # noqa: BLE001 - different opencc packages raise different errors
            continue
    raise SystemExit(f"OpenCC 無法載入設定 {config}")


class Converter:
    def __init__(self, config: str, pins: list[tuple[str, str]]):
        self.cc = load_converter(config)
        self.pins = sorted(pins, key=lambda p: -len(p[0]))
        self.hits: Counter = Counter()
        self.changed = 0

    def __call__(self, text: str) -> str:
        if not text or not has_cjk(text):
            return text
        out = self.cc.convert(text)
        for src, dst in self.pins:
            if src in out:
                self.hits[f"{src}→{dst}"] += out.count(src)
                out = out.replace(src, dst)
        if out != text:
            self.changed += 1
        return out


def load_pins(path: Path | None, exclude: Path | None) -> list[tuple[str, str]]:
    if not path:
        return []
    skip = set()
    if exclude and exclude.exists():
        skip = {line.strip() for line in exclude.read_text(encoding="utf-8").splitlines() if line.strip()}
    pins = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f, delimiter="\t"):
            if len(row) >= 2 and row[0] != "source" and row[0] not in skip and row[0] != row[1]:
                pins.append((row[0], row[1]))
    return pins


def convert_json(obj, conv, dsd: bool):
    if isinstance(obj, list):
        return [convert_json(x, conv, dsd) for x in obj]
    if isinstance(obj, dict):
        if dsd:
            return {k: (conv(v) if k == "string" and isinstance(v, str) else v) for k, v in obj.items()}
        return {k: convert_json(v, conv, dsd) for k, v in obj.items()}
    if isinstance(obj, str):
        return conv(obj)
    return obj


def convert_file(path: Path, conv: Converter) -> bytes | None:
    """Return new bytes, or None when the file type is not handled / unchanged."""
    name = path.name.lower()
    before = conv.changed
    if name.endswith(".json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except ValueError:
            return None
        dsd = "dynamicstringdistributor" in str(path).lower().replace("\\", "/")
        new = convert_json(data, conv, dsd)
        out = (json.dumps(new, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    elif name.endswith(".txt") and "translations" in str(path).lower().replace("\\", "/"):
        raw = path.read_bytes()
        table = parse_translation_bytes(raw)
        new = {k: conv(v) for k, v in table.items()}
        out = translation_bytes(new)
        if check_translation_encoding(raw) != "utf-16le-bom" and table:
            conv.hits["(轉為 UTF-16LE+BOM)"] += 1
            return out
    elif name.endswith((".strings", ".dlstrings", ".ilstrings")):
        table = st.read(path, "utf-8")
        new = {k: conv(v) for k, v in table.items()}
        out = st.build(new, st.kind_of(path), "utf-8")
    else:
        return None
    return out if conv.changed != before else None


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="簡中→台灣繁體轉換（預設試跑）")
    ap.add_argument("inputs", nargs="+", type=Path)
    ap.add_argument("--config", default="s2twp")
    ap.add_argument("--pins", type=Path, default=None, help="chs-cht 對照表（strings_glossary.py 產生）")
    ap.add_argument("--exclude-pins", type=Path, default=None, help="不要套用的對照詞（一行一個）")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--out-dir", type=Path, default=None)
    g.add_argument("--in-place", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    conv = Converter(args.config, load_pins(args.pins, args.exclude_pins))
    files = []
    for inp in args.inputs:
        files += [inp] if inp.is_file() else sorted(p for p in inp.rglob("*") if p.is_file())
    changed = 0
    for f in files:
        new = convert_file(f, conv)
        if new is None:
            continue
        changed += 1
        if args.in_place:
            shutil.copy2(f, f.with_name(f.name + ".bak"))
            f.write_bytes(new)
        elif args.out_dir:
            root = next((i for i in args.inputs if i.is_dir() and i in f.parents), f.parent)
            dest = args.out_dir / f.relative_to(root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(new)
    rep = Report("zh_opencc")
    mode = "就地轉換（保留 .bak）" if args.in_place else (f"輸出到 {args.out_dir}" if args.out_dir else "試跑")
    rep.add("mode", "INFO", "模式", mode)
    rep.add("files", "PASS", "轉換的檔案", f"{changed}/{len(files)}；改變的字串 {conv.changed} 條")
    top = ", ".join(f"{k}×{v}" for k, v in conv.hits.most_common(15))
    rep.add("pins", "INFO", "名詞釘選命中", top or "無")
    rep.data = {"pin_hits": dict(conv.hits)}
    path = rep.save(args.out, stem="zh_opencc")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
