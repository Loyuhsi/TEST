"""Turn the text of a translated plugin into DSD JSON for the plugin version we actually run.

把翻譯版插件（例如 Nexus 上版本或清理狀態和我們不同的繁中 ESP）的文字轉成 DSD JSON，不換插件：
只取「同一筆記錄、同一欄位（必要時同一 index）、兩邊 EditorID 相同、我們的是英文、翻譯版是中文、
而且 <Alias> 之類的標記一致」的字串。其他（我們沒有的記錄、記錄被改作他用、翻譯版還是英文）一律跳過。

    python tools\\zh\\esp_to_dsd.py --pm D:\\PM --translated "D:\\zh-packs\\SIRENROOT\\evgSIRENROOT.esm" ^
        --out-mod "D:\\PM\\mods\\ZH - Nexus 繁中 - SIRENROOT"
    ... --apply
--plugin defaults to the translated file's name (our winning copy of that plugin is the reference).
--file-name sets the JSON name; DSD lets a higher file name win inside one plugin folder, so a name that
starts with "!" makes this translation lose to any other DSD file for the same plugin.
Writes reports\\zh_esp_to_dsd.txt/.json/.csv. Needs sse-plugin-interface (requirements-zh.txt).
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pm import fsutil, tes4, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402
from zh.common import (DSD_DIR, has_cjk, needs_translation, placeholders, string_key,  # noqa: E402
                       write_dsd_file)
from zh.coverage import extract_plugin_strings  # noqa: E402

FIELDS = ["form_id", "type", "index", "editor_id", "reason", "ours", "translated"]
REASONS = {
    "converted": "轉成 DSD",
    "not_chinese": "翻譯版這一條不是中文",
    "no_counterpart": "我們的插件沒有這一條",
    "editor_id_differs": "EditorID 不同（記錄被改作他用）",
    "already_chinese": "我們的已經是中文",
    "no_translation_needed": "我們的不需要翻譯（數字、符號）",
    "markup_differs": "<Alias> 等標記不一致（原文可能改過）",
}


def convert(ours: list[dict], translated: list[dict], light: set[str]) -> tuple[list[dict], list[dict]]:
    """(DSD entries, one row per translated string with the reason)."""
    by_key = {string_key(e["form_id"], e["type"], e["index"], e.get("editor_id"), light): e for e in ours}
    entries, rows = [], []
    for t in translated:
        k = string_key(t["form_id"], t["type"], t["index"], t.get("editor_id"), light)
        o = by_key.get(k)
        if not has_cjk(t["string"]):
            reason = "not_chinese"
        elif o is None:
            reason = "no_counterpart"
        elif o.get("editor_id") and t.get("editor_id") and o["editor_id"].lower() != t["editor_id"].lower():
            reason = "editor_id_differs"
        elif has_cjk(o["string"]):
            reason = "already_chinese"
        elif not needs_translation(o["string"]):
            reason = "no_translation_needed"
        elif placeholders(o["string"]) != placeholders(t["string"]):
            reason = "markup_differs"
        else:
            reason = "converted"
            entries.append({"form_id": o["form_id"], "type": o["type"], "index": o["index"],
                            "editor_id": o.get("editor_id"), "string": t["string"]})
        rows.append({"form_id": t["form_id"], "type": t["type"], "index": t["index"],
                     "editor_id": t.get("editor_id") or "", "reason": reason,
                     "ours": (o or {}).get("string", "")[:80], "translated": t["string"][:80]})
    return entries, rows


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="翻譯版插件 → DSD JSON（不換插件；預設試跑）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--translated", type=Path, required=True, help="翻譯版插件（解壓出來的檔，不要安裝）")
    ap.add_argument("--plugin", default=None, help="對應的插件名稱（預設和翻譯版同名）")
    ap.add_argument("--out-mod", type=Path, required=True, help="寫出 DSD 的 mod 資料夾")
    ap.add_argument("--file-name", default="nexus_cht.json")
    ap.add_argument("--work", type=Path, default=Path("D:/PM/zh-work"), help="插件解析快取放在 <work>/plugin_cache")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    rep = Report("zh_esp_to_dsd")
    rep.add("mode", "INFO", "模式", "實際執行" if args.apply else "試跑（加 --apply 才會寫入）")
    plugin = args.plugin or args.translated.name
    prof = vfs.open_profile(args.pm, args.profile)
    providers = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, prof.game_dir / "Data")
    ours_path = providers.get(plugin.lower())
    rows: list[dict] = []
    if not args.translated.is_file():
        rep.add("translated", "FAIL", "找不到翻譯版插件", str(args.translated))
    elif ours_path is None:
        rep.add("ours", "FAIL", "找不到我們的插件", f"{plugin}（mod 未啟用或名稱錯誤）")
    else:
        try:
            h_ours, h_tr = tes4.read_header(ours_path), tes4.read_header(args.translated)
        except (tes4.PluginError, OSError) as e:
            rep.add("read", "FAIL", "無法讀取插件", str(e))
            h_ours = h_tr = None
        if h_ours is not None and (h_ours.is_localized or h_tr.is_localized):
            rep.add("localized", "FAIL", "本地化插件",
                    "字串在 .strings 字串表裡，不在插件中；這個工具只處理字串寫在插件裡的版本")
        elif h_ours is not None:
            cache = args.work / "plugin_cache"
            ours = extract_plugin_strings(ours_path, cache, localized=False)
            translated = extract_plugin_strings(args.translated, cache, localized=False)
            light = {plugin.lower()} if h_ours.is_light else set()
            entries, rows = convert(ours, translated, light)
            c = Counter(r["reason"] for r in rows)
            rep.add("source", "INFO", "比對", f"我們的 {ours_path.parent.name}\\{plugin}：{len(ours)} 條字串；"
                    f"翻譯版：{len(translated)} 條")
            rep.add("result", "INFO", "結果", "；".join(f"{REASONS[k]} {c[k]}" for k in REASONS if c.get(k)))
            ours_todo = sum(1 for e in ours if needs_translation(e["string"]) and not has_cjk(e["string"]))
            rep.add("cover", "INFO", "我們插件的英文字串由這份翻譯涵蓋",
                    f"{len(entries)}/{ours_todo}" + (f"（{len(entries) / ours_todo:.0%}）" if ours_todo else ""))
            dest = args.out_mod / DSD_DIR / plugin / args.file_name
            if not entries:
                rep.add("write", "WARN", "沒有可轉換的字串", "版本差太多或翻譯版不是中文")
            elif args.apply:
                write_dsd_file(dest, entries)
                rep.add("write", "PASS", "已寫入", f"{len(entries)} 條 → {dest}")
            else:
                rep.add("write", "INFO", "會寫入", f"{len(entries)} 條 → {dest}")
    write_csv(args.out / "zh_esp_to_dsd.csv", [r for r in rows if r["reason"] != "converted"], FIELDS)
    rep.data = {"plugin": plugin, "rows": len(rows)}
    path = rep.save(args.out, stem="zh_esp_to_dsd")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
