"""Check / complete interface translation files (MCM menus) for sLanguage=CHINESE.

檢查並補齊介面翻譯檔（MCM 選單）：
  scan         ：列出每個翻譯檔是否有 _CHINESE 版、編碼是否為 UTF-16LE+BOM、缺哪些鍵
  make-chinese ：替缺少中文版的檔案，在「ZH Overrides」產生 _CHINESE.txt（先放英文，避免畫面出現 $KEY），
                 並把 BSA 內的 _ENGLISH.txt 另存為散檔（Scaleform Translation++ NG 只讀散檔做英文備援）

    python tools\\zh\\mcm_txt.py scan --pm D:\\PM
    python tools\\zh\\mcm_txt.py make-chinese --pm D:\\PM --out-mod "D:\\PM\\mods\\ZH Overrides" --apply
Translating the English placeholders is done later by coverage.py + llm_translate.py.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pm import bsa, fsutil, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402
from zh.common import (check_translation_encoding, has_cjk, needs_translation,  # noqa: E402
                       parse_translation_bytes, write_translation_txt)


@dataclass
class TFile:
    base: str                  # e.g. "skyui_se" (lower-case, language removed)
    language: str              # "ENGLISH", "CHINESE", ...
    folder: str                # providing mod
    where: str                 # "loose" or the BSA name
    raw: bytes = b""
    table: dict = field(default_factory=dict)

    @property
    def encoding(self) -> str:
        return check_translation_encoding(self.raw)


def split_name(name: str) -> tuple[str, str] | None:
    stem = name[:-4] if name.lower().endswith(".txt") else None
    if not stem or "_" not in stem:
        return None
    base, lang = stem.rsplit("_", 1)
    return base.lower(), lang.upper()


def collect(pm: Path, profile: str) -> dict[tuple[str, str], TFile]:
    """Winning translation file per (base, LANGUAGE), highest-priority mod first; loose beats BSA."""
    prof = vfs.open_profile(pm, profile)
    found: dict[tuple[str, str], TFile] = {}
    for folder in prof.enabled_folders:
        mod = prof.mods_dir / folder
        tr = None
        for cand in ("interface/translations", "Interface/Translations", "Interface/translations"):
            if (mod / cand).is_dir():
                tr = mod / cand
                break
        if tr:
            for p in tr.iterdir():
                sn = split_name(p.name)
                if sn and sn not in found:
                    raw = p.read_bytes()
                    found[sn] = TFile(sn[0], sn[1], folder, "loose", raw, parse_translation_bytes(raw))
        try:
            archives = [e for e in os.scandir(mod) if e.is_file() and e.name.lower().endswith(".bsa")]
        except OSError:
            archives = []
        for arc in archives:
            try:
                with bsa.BSA(Path(arc.path)) as b:
                    for e in b.find("interface\\translations\\*.txt"):
                        sn = split_name(e.path.rsplit("\\", 1)[-1])
                        if sn and sn not in found:
                            raw = b.read(e)
                            found[sn] = TFile(sn[0], sn[1], folder, arc.name, raw, parse_translation_bytes(raw))
            except (bsa.BSAError, OSError):
                continue
    return found


def analyse(found: dict) -> list[dict]:
    rows = []
    bases = sorted({b for b, lang in found if lang == "ENGLISH"})
    for base in bases:
        en = found[(base, "ENGLISH")]
        zh = found.get((base, "CHINESE"))
        missing = [k for k in en.table if not zh or k not in zh.table]
        untranslated = [k for k, v in (zh.table.items() if zh else []) if needs_translation(v)]
        rows.append({
            "base": base, "english_from": f"{en.folder} [{en.where}]", "english_keys": len(en.table),
            "chinese_from": f"{zh.folder} [{zh.where}]" if zh else "",
            "chinese_encoding": zh.encoding if zh else "",
            "missing_keys": len(missing), "english_values": len(untranslated),
            "status": "missing" if not zh else ("bad_encoding" if zh.where == "loose" and zh.encoding != "utf-16le-bom"
                                                else ("incomplete" if missing or untranslated else "ok")),
        })
    return rows


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="MCM/介面翻譯檔檢查與補齊")
    ap.add_argument("command", choices=["scan", "make-chinese"])
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--out-mod", type=Path, default=None)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    found = collect(args.pm, args.profile)
    rows = analyse(found)
    write_csv(args.out / "zh_mcm.csv", rows)
    rep = Report(f"zh_mcm-{args.command}")
    from collections import Counter
    c = Counter(r["status"] for r in rows)
    rep.add("files", "INFO", "有英文版的翻譯檔", f"{len(rows)} 個：" + ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    if args.command == "make-chinese":
        if not args.out_mod:
            rep.add("out", "FAIL", "需要 --out-mod", "")
        else:
            made = fixed = loose_en = 0
            for r in rows:
                en = found[(r["base"], "ENGLISH")]
                zh = found.get((r["base"], "CHINESE"))
                if r["status"] in ("missing", "incomplete", "bad_encoding"):
                    merged = dict(zh.table) if zh else {}
                    for k, v in en.table.items():
                        merged.setdefault(k, v)
                    if args.apply:
                        write_translation_txt(args.out_mod / "interface" / "translations" / f"{r['base']}_CHINESE.txt",
                                              merged)
                    made += 0 if zh else 1
                    fixed += 1 if zh else 0
                if en.where != "loose":
                    loose_en += 1
                    if args.apply:
                        write_translation_txt(args.out_mod / "interface" / "translations" / f"{r['base']}_ENGLISH.txt",
                                              en.table)
            rep.add("made", "PASS", "新建 _CHINESE.txt（先放英文）", f"{made} 個")
            rep.add("fixed", "PASS", "補齊缺鍵／修正編碼", f"{fixed} 個")
            rep.add("loose", "PASS", "BSA 內英文檔另存為散檔", f"{loose_en} 個")
            if not args.apply:
                rep.add("mode", "INFO", "模式", "試跑（加 --apply 才會寫入）")
    zh_ok = sum(1 for r in rows if r["status"] == "ok" and has_cjk(" ".join(found[(r["base"], "CHINESE")].table.values())))
    rep.add("ok", "INFO", "已完整中文化", f"{zh_ok} 個")
    path = rep.save(args.out, stem=f"zh_mcm-{args.command}")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
