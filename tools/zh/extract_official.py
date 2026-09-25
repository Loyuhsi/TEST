"""Extract the official Traditional Chinese strings and fonts from a game folder's BSAs.

從遊戲資料夾的 BSA 取出官方繁中字串（*_chinese.*）與中文字型，做成散檔 mod。
Run it on the Mages & Vikings "Stock Game" BEFORE deleting D:\\MV (its rebuilt
Skyrim - Interface.bsa contains the official Chinese strings for the base game + DLC).

    python tools\\zh\\extract_official.py --game-dir "D:\\MV\\Stock Game" ^
        --extra-bsa "D:\\MV\\mods\\Creation Club\\_ResourcePack.bsa" ^
        --out-mod "D:\\PM\\mods\\ZH - 官方繁中字串" --work D:\\PM\\zh-work --apply

English tables are copied to <work>\\official_english for the glossary (they are NOT put in the mod).
--fallback-english copies <name>_english.* to <name>_chinese.* for localized plugins that have
no Chinese table, so the game never shows blank names after sLanguage=CHINESE.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pm import bsa, fsutil, strings as st  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report  # noqa: E402

ZH_PATTERNS = ["strings\\*_chinese.*", "strings\\*traditional*", "interface\\fonts_cn.swf",
               "interface\\fontconfig_cn.txt", "interface\\translate_chinese.txt",
               "interface\\translations\\*_chinese.txt"]
EN_PATTERNS = ["strings\\*_english.*"]
TRAD_ONLY = set("們劍裝門龍與這個說對為會時過還學點體頭麼將記書買賣錢鐵銀戰殺醫藥")
SIMP_ONLY = set("们剑装门龙与这个说对为会时过还学点体头么将记书买卖钱铁银战杀医药")


def script_guess(text: str) -> str:
    t = sum(ch in TRAD_ONLY for ch in text)
    s = sum(ch in SIMP_ONLY for ch in text)
    if t == s == 0:
        return "unknown"
    return "traditional" if t >= s * 3 else ("simplified" if s >= t * 3 else "mixed")


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="取出官方繁中字串與字型（預設試跑）")
    ap.add_argument("--game-dir", required=True, type=Path)
    ap.add_argument("--extra-bsa", type=Path, action="append", default=[])
    ap.add_argument("--out-mod", required=True, type=Path)
    ap.add_argument("--work", type=Path, default=Path("D:/PM/zh-work"))
    ap.add_argument("--fallback-english", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    rep = Report("zh_extract_official")
    rep.add("mode", "INFO", "模式", "實際執行" if args.apply else "試跑（加 --apply 才會寫入）")
    data = args.game_dir / "Data"
    archives = sorted(data.glob("*.bsa")) + [p for p in args.extra_bsa if p.exists()]
    zh_found: dict[str, Path] = {}
    en_found: dict[str, Path] = {}
    for arc in archives:
        try:
            with bsa.BSA(arc) as b:
                for pat_list, found in ((ZH_PATTERNS, zh_found), (EN_PATTERNS, en_found)):
                    for pat in pat_list:
                        for e in b.find(pat):
                            if e.path in found:
                                continue
                            found[e.path] = arc
                            if args.apply:
                                dest_root = args.out_mod if found is zh_found else args.work / "official_english"
                                dest = dest_root.joinpath(*e.path.split("\\"))
                                dest.parent.mkdir(parents=True, exist_ok=True)
                                dest.write_bytes(b.read(e))
        except (bsa.BSAError, OSError) as e:
            rep.add(f"bsa:{arc.name}", "WARN", f"無法讀取 {arc.name}", str(e))
    tables = sorted(p for p in zh_found if p.startswith("strings\\"))
    rep.add("zh", "PASS" if tables else "FAIL", "中文字串表", f"{len(tables)} 個" +
            ("" if tables else "：這個遊戲資料夾的 BSA 沒有中文字串"))
    fonts = [p for p in zh_found if p.startswith("interface\\")]
    rep.add("fonts", "PASS" if any(p.endswith("fonts_cn.swf") for p in fonts) else "WARN", "中文字型與介面檔",
            ", ".join(Path(p).name for p in fonts) or "無")
    # which localized masters lack Chinese
    have = {Path(p).name.lower().rsplit("_chinese", 1)[0] for p in tables if "_chinese" in p}
    en_bases = sorted({Path(p).name.lower().rsplit("_english", 1)[0] for p in en_found})
    missing = [b for b in en_bases if b not in have]
    rep.add("missing", "WARN" if missing else "PASS", "有英文但沒有中文字串的插件",
            f"{len(missing)} 個：{', '.join(missing[:12])}" if missing else "無")
    if args.apply and args.fallback_english and missing:
        n = 0
        for p in en_found:
            base = Path(p).name.lower().rsplit("_english", 1)[0]
            if base in missing:
                src = (args.work / "official_english").joinpath(*p.split("\\"))
                dest = args.out_mod / "strings" / Path(p).name.lower().replace("_english", "_chinese")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(src.read_bytes())
                n += 1
        rep.add("fallback", "INFO", "以英文字串暫代", f"{n} 個檔案（之後可用 llm_translate 翻譯）")
    if args.apply and tables:
        sample = args.out_mod.joinpath(*tables[0].split("\\"))
        try:
            text = " ".join(list(st.read(sample).values())[:3000])
            rep.add("script", "INFO", "字形判斷", f"{Path(tables[0]).name}：{script_guess(text)}")
        except (OSError, ValueError, IndexError) as e:
            rep.add("script", "WARN", "字形判斷失敗", str(e))
    rep.data = {"zh_files": sorted(zh_found), "english_tables": sorted(en_found), "missing_chinese": missing}
    path = rep.save(args.out, stem="zh_extract_official")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
