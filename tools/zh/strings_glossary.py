"""Build glossaries by aligning string tables of the same game data in two languages.

以字串 ID 對齊兩種語言的字串表，產生名詞對照表：
  en-zh  ：官方英文 ↔ 官方繁中（給 LLM 翻譯用的術語表）
  chs-cht：社群簡中 ↔ 官方繁中（OpenCC 轉換後，把社群用語「釘」成官方繁中名詞）

    python tools\\zh\\strings_glossary.py en-zh --a D:\\PM\\zh-work\\official_english\\strings ^
        --b "D:\\PM\\mods\\ZH - 官方繁中字串\\strings" --out D:\\PM\\zh-work\\glossary_en_zh.tsv
    python tools\\zh\\strings_glossary.py chs-cht --a <社群簡中 strings 資料夾> --b <官方繁中 strings 資料夾> ^
        --out D:\\PM\\zh-work\\pins_chs_cht.tsv
Glossaries are derived from game text: keep them local, do not publish them.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pm import fsutil, strings as st  # noqa: E402
from zh.common import has_cjk  # noqa: E402

LANG_RE = re.compile(r"_(english|chinese|[a-z]+)\.(strings|dlstrings|ilstrings)$", re.I)


def tables(folder: Path, include_dl: bool) -> dict[str, Path]:
    """Map 'skyrim.strings' (language removed) -> path."""
    out = {}
    exts = (".strings", ".dlstrings") if include_dl else (".strings",)
    for p in Path(folder).rglob("*"):
        if p.suffix.lower() in exts and LANG_RE.search(p.name):
            out[LANG_RE.sub(r".\2", p.name.lower())] = p
    return out


def aligned_pairs(a_dir: Path, b_dir: Path, include_dl: bool):
    ta, tb = tables(a_dir, include_dl), tables(b_dir, include_dl)
    for base in sorted(set(ta) & set(tb)):
        a, b = st.read(ta[base]), st.read(tb[base])
        for sid in a.keys() & b.keys():
            yield base, a[sid], b[sid]


def is_name(en: str, max_len: int) -> bool:
    return (1 < len(en) <= max_len and "\n" not in en and not en.rstrip().endswith((".", "!", "?"))
            and bool(re.search(r"[A-Za-z]", en)))


def build_en_zh(a_dir: Path, b_dir: Path, include_dl: bool, max_len: int) -> list[tuple]:
    votes: dict[str, Counter] = defaultdict(Counter)
    src: dict[str, str] = {}
    for base, en, zh in aligned_pairs(a_dir, b_dir, include_dl):
        en, zh = en.strip(), zh.strip()
        if is_name(en, max_len) and has_cjk(zh):
            votes[en][zh] += 1
            src.setdefault(en, base)
    rows = []
    for en, c in votes.items():
        zh, n = c.most_common(1)[0]
        rows.append((en, zh, n, len(c), src[en]))
    rows.sort(key=lambda r: (-r[2], r[0].lower()))
    return rows


def build_chs_cht(a_dir: Path, b_dir: Path, max_cjk: int) -> list[tuple]:
    from zh.opencc_convert import load_converter
    cc = load_converter("s2twp")
    votes: dict[str, Counter] = defaultdict(Counter)
    for _base, chs, cht in aligned_pairs(a_dir, b_dir, include_dl=False):
        chs, cht = chs.strip(), cht.strip()
        if not (has_cjk(chs) and has_cjk(cht)) or len(chs) > max_cjk or "\n" in chs:
            continue
        conv = cc.convert(chs)
        if conv != cht:
            votes[conv][cht] += 1
    rows = []
    for conv, c in votes.items():
        cht, n = c.most_common(1)[0]
        if len(conv) >= 2:
            rows.append((conv, cht, n, len(c), ""))
    rows.sort(key=lambda r: (-len(r[0]), r[0]))
    return rows


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="對齊字串表產生術語表")
    ap.add_argument("mode", choices=["en-zh", "chs-cht"])
    ap.add_argument("--a", required=True, type=Path, help="en-zh：英文表資料夾；chs-cht：社群簡中表資料夾")
    ap.add_argument("--b", required=True, type=Path, help="官方繁中表資料夾")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--include-dl", action="store_true", help="也納入 DLSTRINGS（較長的說明文字）")
    ap.add_argument("--max-len", type=int, default=48)
    args = ap.parse_args(argv)
    rows = build_en_zh(args.a, args.b, args.include_dl, args.max_len) if args.mode == "en-zh" \
        else build_chs_cht(args.a, args.b, max_cjk=16)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(["source", "target", "count", "variants", "table"])
        w.writerows(rows)
    ambiguous = sum(1 for r in rows if r[3] > 1)
    print(f"{args.mode}: {len(rows)} 筆（其中 {ambiguous} 筆有多種譯法，取最常見）→ {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
