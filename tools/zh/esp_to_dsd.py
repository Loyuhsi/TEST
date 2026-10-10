"""Turn the text of a translated plugin into DSD JSON for the plugin version we actually run.

把翻譯版插件（例如 Nexus 上版本或清理狀態和我們不同的繁中 ESP）的文字轉成 DSD JSON，不換插件。
只取全部符合的字串：
  - 我們插件自己的記錄（覆寫前置的記錄交給 coverage／AI，避免蓋到別的插件的版本）。
  - 同一筆記錄、同一欄位；EditorID 相同（兩邊都沒有時，只能靠 FormID）。
  - 選項、回應、日誌這類「依位置編號」的欄位，同一筆記錄兩邊的條數相同。
  - 我們的是英文、翻譯版是中文、<Alias> 之類的標記一致。
  - 後面載入、以我們的插件為前置的插件沒有改掉這段文字。
  - 有 --original（翻譯版所根據的英文原版插件）時，我們的英文還要和它一字不差。

    python tools\\zh\\esp_to_dsd.py --pm D:\\PM --translated "D:\\zh-packs\\SIRENROOT\\evgSIRENROOT.esm" ^
        --out-mod "D:\\PM\\mods\\ZH - Nexus 繁中 - SIRENROOT"
    ... --apply
--plugin defaults to the translated file's name (our winning copy of that plugin is the reference); when the
translated file is named differently, its own records are renamed to --plugin before matching.
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

FIELDS = ["form_id", "type", "index", "editor_id", "reason", "checked", "ours", "translated"]
REASONS = {
    "converted": "轉成 DSD",
    "not_chinese": "翻譯版這一條不是中文",
    "no_counterpart": "我們的插件沒有這一條",
    "master_record": "覆寫前置的記錄（交給 coverage／AI）",
    "editor_id_differs": "EditorID 不同或只有一邊有（記錄被改作他用）",
    "count_differs": "同一筆記錄的條數不同（選項、回應的位置會錯開）",
    "no_editor_id": "沒有 EditorID 可核對，而且 ESL 旗標不同（FormID 可能重編過）",
    "already_chinese": "我們的已經是中文",
    "no_translation_needed": "我們的不需要翻譯（數字、符號）",
    "source_changed": "我們的英文和英文原版不同（改版改過這段）",
    "overridden": "後面的插件改了這段文字",
    "markup_differs": "<Alias> 等標記不一致（原文可能改過）",
}
CHECKED = {"original": "和英文原版一字不差", "editor_id": "EditorID 相同", "form_id": "只靠 FormID（沒有 EditorID，例如對話）"}
# fields whose index is a position inside the record: an added or removed entry shifts every later one
POSITIONAL = frozenset({"INFO NAM1", "MESG ITXT", "PERK EPF2", "PERK EPFD"})


def rename_plugin(rows: list[dict], old: str, new: str) -> None:
    """Records the translated file defines itself carry its own file name; give them ours."""
    if old.lower() == new.lower():
        return
    for r in rows:
        fid, sep, owner = r["form_id"].partition("|")
        if sep and owner.strip().lower() == old.lower():
            r["form_id"] = f"{fid}|{new}"


def convert(ours: list[dict], translated: list[dict], plugin: str, light_ours: bool = False,
            light_translated: bool = False, original: list[dict] | None = None,
            later: dict[tuple, str] | None = None) -> tuple[list[dict], list[dict]]:
    """(DSD entries, one row per translated string with the reason). Translated (and original) form_ids must
    already name `plugin` for its own records; `later` maps keys to the text of the last later plugin."""
    own = plugin.lower()
    lo = {own} if light_ours else set()
    lt = {own} if light_translated else set()

    def key(e: dict, light: set[str]) -> tuple:
        return string_key(e["form_id"], e["type"], e["index"], e.get("editor_id"), light)

    def counts(rows: list[dict], light: set[str]) -> Counter:
        return Counter(string_key(e["form_id"], e["type"], None, None, light)[:3]
                       for e in rows if e["type"].upper() in POSITIONAL)

    by_key = {key(e, lo): e for e in ours}
    orig = {key(e, lt): e["string"] for e in original} if original is not None else None
    n_ours, n_tr = counts(ours, lo), counts(translated, lt)
    strict = light_ours != light_translated
    later = later or {}
    entries, rows = [], []
    for t in translated:
        k = key(t, lt)
        o = by_key.get(k)
        ed_o = ((o or {}).get("editor_id") or "").lower()
        ed_t = (t.get("editor_id") or "").lower()
        checked = ""
        if not has_cjk(t["string"]):
            reason = "not_chinese"
        elif o is None:
            reason = "no_counterpart"
        elif k[0] == "GMST" or k[1] != own:
            reason = "master_record"
        elif ed_o != ed_t:
            reason = "editor_id_differs"
        elif t["type"].upper() in POSITIONAL and n_ours[k[:3]] != n_tr[k[:3]]:
            reason = "count_differs"
        elif orig is None and not ed_o and strict:
            reason = "no_editor_id"
        elif has_cjk(o["string"]):
            reason = "already_chinese"
        elif not needs_translation(o["string"]):
            reason = "no_translation_needed"
        elif orig is not None and orig.get(k) != o["string"]:
            reason = "source_changed"
        elif k in later and later[k] != o["string"]:
            reason = "overridden"
        elif placeholders(o["string"]) != placeholders(t["string"]):
            reason = "markup_differs"
        else:
            reason = "converted"
            checked = "original" if orig is not None else "editor_id" if ed_o else "form_id"
            entries.append({"form_id": o["form_id"], "type": o["type"], "index": o["index"],
                            "editor_id": o.get("editor_id"), "string": t["string"]})
        rows.append({"form_id": t["form_id"], "type": t["type"], "index": t["index"],
                     "editor_id": t.get("editor_id") or "", "reason": reason, "checked": checked,
                     "ours": (o or {}).get("string", "")[:80], "translated": t["string"][:80]})
    return entries, rows


def later_overrides(prof: vfs.Profile, providers: dict[str, Path], plugin: str, light: bool,
                    cache: Path) -> tuple[dict[tuple, str], list[str], list[str]]:
    """Text of our plugin's own records as the last later plugin that lists it as a master leaves it;
    also (names checked, names that could not be read)."""
    primaries = vfs.primary_plugins(prof.game_dir)
    active = primaries + [p.name for p in prof.plugins if p.enabled and p.name not in primaries]
    pos = next((i for i, n in enumerate(active) if n.lower() == plugin.lower()), None)
    if pos is None:
        return {}, [], []
    own, lo = plugin.lower(), ({plugin.lower()} if light else set())
    later: dict[tuple, str] = {}
    names, unreadable = [], []
    for name in active[pos + 1:]:
        path = providers.get(name.lower())
        if not path:
            continue
        try:
            h = tes4.read_header(path)
        except (tes4.PluginError, OSError):
            continue
        if own not in {m.lower() for m in h.masters}:
            continue
        if h.is_localized:
            unreadable.append(f"{name}（本地化）")
            continue
        try:
            rows = extract_plugin_strings(path, cache, localized=False)
        except Exception as e:  # noqa: BLE001 - one bad plugin must not stop the run
            unreadable.append(f"{name}（{e}）")
            continue
        names.append(name)
        for e in rows:
            k = string_key(e["form_id"], e["type"], e["index"], e.get("editor_id"), lo)
            if k[0] != "GMST" and k[1] == own:
                later[k] = e["string"]
    return later, names, unreadable


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="翻譯版插件 → DSD JSON（不換插件；預設試跑）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--translated", type=Path, required=True, help="翻譯版插件（解壓出來的檔，不要安裝）")
    ap.add_argument("--original", type=Path, default=None,
                    help="翻譯版所根據的英文原版插件（選用；有的話只轉我們的英文和它一字不差的字串）")
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
    extra = [p for p in (args.original,) if p is not None]
    if not args.translated.is_file():
        rep.add("translated", "FAIL", "找不到翻譯版插件", str(args.translated))
    elif any(not p.is_file() for p in extra):
        rep.add("original", "FAIL", "找不到英文原版插件", str(args.original))
    elif ours_path is None:
        rep.add("ours", "FAIL", "找不到我們的插件", f"{plugin}（mod 未啟用或名稱錯誤）")
    else:
        try:
            h_ours, h_tr = tes4.read_header(ours_path), tes4.read_header(args.translated)
            h_orig = tes4.read_header(args.original) if args.original else None
        except (tes4.PluginError, OSError) as e:
            rep.add("read", "FAIL", "無法讀取插件", str(e))
            h_ours = h_tr = h_orig = None
        if h_ours is not None and any(h.is_localized for h in (h_ours, h_tr, h_orig) if h):
            rep.add("localized", "FAIL", "本地化插件",
                    "字串在 .strings 字串表裡，不在插件中；這個工具只處理字串寫在插件裡的版本")
        elif h_ours is not None:
            cache = args.work / "plugin_cache"
            other_cache = cache / "esp_to_dsd"      # never share cache entries with our installed plugins
            ours = extract_plugin_strings(ours_path, cache, localized=False)
            translated = extract_plugin_strings(args.translated, other_cache, localized=False)
            rename_plugin(translated, args.translated.name, plugin)
            original = None
            if args.original:
                original = extract_plugin_strings(args.original, other_cache, localized=False)
                rename_plugin(original, args.original.name, plugin)
            if h_ours.is_light != h_tr.is_light:
                rep.add("light", "WARN", "ESL 旗標不同",
                        f"我們的{'是' if h_ours.is_light else '不是'} ESL、翻譯版{'是' if h_tr.is_light else '不是'}："
                        "FormID 可能重編過，沒有 EditorID 的記錄不轉（有英文原版時用 --original 核對）")
            later, dependents, unreadable = later_overrides(prof, providers, plugin, h_ours.is_light, cache)
            entries, rows = convert(ours, translated, plugin, h_ours.is_light, h_tr.is_light, original, later)
            c = Counter(r["reason"] for r in rows)
            rep.add("source", "INFO", "比對", f"我們的 {ours_path.parent.name}\\{plugin}：{len(ours)} 條字串；"
                    f"翻譯版：{len(translated)} 條" + (f"；英文原版：{len(original)} 條" if original is not None else ""))
            rep.add("later", "INFO", "後面以它為前置的插件",
                    f"{len(dependents)} 個" + (f"：{', '.join(dependents[:6])}" if dependents else ""))
            if unreadable:
                rep.add("later_bad", "WARN", "後面以它為前置、但沒辦法核對的插件",
                        f"{len(unreadable)} 個：{'；'.join(unreadable[:4])}（這些插件改過的文字可能被舊譯文蓋掉，回報 Claude）")
            rep.add("result", "INFO", "結果", "；".join(f"{REASONS[k]} {c[k]}" for k in REASONS if c.get(k)))
            how = Counter(r["checked"] for r in rows if r["checked"])
            if how:
                rep.add("checked", "INFO", "轉換的核對方式", "；".join(f"{CHECKED[k]} {how[k]}" for k in CHECKED if how[k]))
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
