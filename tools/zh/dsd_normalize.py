"""Tidy the DSD JSON files of the ZH mods so Dynamic String Distributor 1.4.x applies the right entry.

整理 ZH mod 裡的 DSD JSON：
  - 單一欄位（FULL、DESC、DNAM、SHRT…）不能帶 "index"。DSD 1.4.x 不會把低優先、帶 index 的條目去重，
    它可能反過來蓋掉正確的那一筆。只有 QUST CNAM／NNAM、INFO NAM1、MESG ITXT、PERK EPF2／EPFD 需要 index。
  - form_id 少了 "|插件名"（例如 NIM Translator 匯出的檔）時補上；否則 DSD 會略過。
    是所在資料夾插件自己的記錄、還是它前置（例如 Skyrim.esm）的記錄，要讀那個插件確認：
    FormID 最高的位元組小於前置數量時可能是前置的記錄。兩種都找不到或都找得到時不改，列在報告。
  - llm_translate 寫的 *~ai.json 刻意帶著它要蓋過的英文條目的 index，不改。
Only enabled mods whose name starts with --prefix (default "ZH") are touched, only single-link files
(never a hardlinked original), and the first original is kept as <file>.bak. Dry run unless --apply.
Completing bare form_ids reads the plugin with sse-plugin-interface (cache in <work>/plugin_cache).

    python tools\\zh\\dsd_normalize.py --pm D:\\PM
    python tools\\zh\\dsd_normalize.py --pm D:\\PM --apply
Writes reports\\zh_dsd_normalize.txt/.json/.csv.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pm import fsutil, tes4, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402
from zh.common import iter_dsd, string_key, uses_index  # noqa: E402

FIELDS = ["mod", "file", "entries", "index_removed", "form_id_fixed", "form_id_unresolved", "status"]
AI_SUFFIX = "~ai.json"          # llm_translate output that deliberately repeats an English entry's index


def tidy(entries: list, resolve: Callable[[str, str], str | None]) -> tuple[int, int, list[str]]:
    """Fix entries in place; returns (indexes removed, form_ids completed, form_ids left as they were).
    resolve(bare form_id, type) gives the completed form_id or None when it cannot tell."""
    removed = fixed = 0
    unresolved = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        if "index" in e and not uses_index(str(e.get("type", ""))):
            del e["index"]
            removed += 1
        fid = e.get("form_id")
        if isinstance(fid, str) and fid.strip() and "|" not in fid:
            full = resolve(fid.strip(), str(e.get("type", "")))
            if full:
                e["form_id"] = full
                fixed += 1
            else:
                unresolved.append(fid.strip())
    return removed, fixed, unresolved


class Resolver:
    """Completes bare form_ids for one DSD folder by looking at the plugin's own strings."""

    def __init__(self, plugin_dir: str, providers: dict[str, Path], cache: Path):
        self.plugin_dir, self.providers, self.cache = plugin_dir, providers, cache
        self._keys: set[tuple] | None = None
        self.header = None
        self.problem = ""

    def keys(self) -> set[tuple]:
        if self._keys is None:
            self._keys = set()
            path = self.providers.get(self.plugin_dir.lower())
            if path is None:
                self.problem = "找不到這個插件（Overwrite 或未啟用）"
                return self._keys
            try:
                self.header = tes4.read_header(path)
            except (tes4.PluginError, OSError) as e:
                self.problem = f"無法讀取插件：{e}"
                return self._keys
            from zh.coverage import extract_plugin_strings
            light = {self.plugin_dir.lower()} if self.header.is_light else set()
            try:
                rows = extract_plugin_strings(path, self.cache, localized=self.header.is_localized)
            except Exception as e:  # noqa: BLE001 - one bad plugin must not stop the run
                self.problem = f"無法解析插件：{e}"
                return self._keys
            for r in rows:
                self._keys.add(string_key(r["form_id"], r["type"], None, None, light)[:3])
        return self._keys

    def __call__(self, fid: str, rtype: str) -> str | None:
        keys = self.keys()
        if not keys:
            return None
        try:
            raw = int(fid[2:] if fid.lower().startswith("0x") else fid, 16)
        except ValueError:
            return None
        own = self.plugin_dir.lower()
        light = {own} if self.header.is_light else set()
        owners = [self.plugin_dir]
        if (raw >> 24) < len(self.header.masters):
            owners.append(self.header.masters[raw >> 24])
        hits = []
        for owner in owners:
            local = raw & (0xFFF if owner.lower() in light else 0xFFFFFF)
            if string_key(f"0x{local:06X}|{owner}", rtype, None, None, light)[:3] in keys:
                hits.append(f"0x{local:06X}|{owner}")
        return hits[0] if len(hits) == 1 else None


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="整理 ZH mod 的 DSD JSON（預設試跑）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--prefix", default="ZH", help="只處理名稱以這個開頭的已啟用 mod（預設 ZH）")
    ap.add_argument("--work", type=Path, default=Path("D:/PM/zh-work"), help="插件解析快取放在 <work>/plugin_cache")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    prof = vfs.open_profile(args.pm, args.profile)
    providers = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, prof.game_dir / "Data")
    resolvers: dict[str, Resolver] = {}
    rep = Report("zh_dsd_normalize")
    rep.add("mode", "INFO", "模式", "實際執行" if args.apply else "試跑（加 --apply 才會寫入）")
    rows: list[dict] = []
    for folder in prof.enabled_folders:
        if not folder.upper().startswith(args.prefix.upper()):
            continue
        for plugin_dir, js in iter_dsd(prof.mods_dir / folder):
            row = {"mod": folder, "file": f"{plugin_dir}/{js.name}", "entries": 0, "index_removed": 0,
                   "form_id_fixed": 0, "form_id_unresolved": 0, "status": ""}
            rows.append(row)
            if js.name.endswith(AI_SUFFIX):
                row["status"] = "AI 檔（刻意保留 index）"
                continue
            try:
                data = json.loads(js.read_text(encoding="utf-8-sig"))
            except (OSError, ValueError) as e:
                row["status"] = f"無法解析（DSD 會略過整個檔）：{e}"
                continue
            if not isinstance(data, list):
                row["status"] = "不是 DSD 的條目清單"
                continue
            row["entries"] = len(data)
            resolver = resolvers.setdefault(plugin_dir.lower(),
                                            Resolver(plugin_dir, providers, args.work / "plugin_cache"))
            removed, fixed, unresolved = tidy(data, resolver)
            row["index_removed"], row["form_id_fixed"] = removed, fixed
            row["form_id_unresolved"] = len(unresolved)
            if unresolved:
                row["status"] = (f"{len(unresolved)} 個 form_id 判斷不出插件（{resolver.problem or '自己和前置都找不到或都有'}），"
                                 f"例如 {unresolved[0]}；")
            if not (removed or fixed):
                row["status"] += "不用改" if not unresolved else "其他不用改"
                continue
            if os.stat(fsutil.long_path(js)).st_nlink > 1:
                row["status"] = "硬連結，不能修改"
                continue
            if args.apply:
                bak = js.with_name(js.name + ".bak")
                if not bak.exists():
                    shutil.copy2(js, bak)
                tmp = js.with_name(js.name + ".tmp")
                tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
                os.replace(tmp, js)
                row["status"] += "已修正"
            else:
                row["status"] += "會修正"
    write_csv(args.out / "zh_dsd_normalize.csv", rows, FIELDS)
    changed = [r for r in rows if r["index_removed"] or r["form_id_fixed"]]
    rep.add("files", "INFO", "DSD 檔", f"{len(rows)} 個（{len({r['mod'] for r in rows})} 個 mod）")
    rep.add("fix", "PASS" if args.apply or not changed else "WARN", "要整理的檔",
            f"{len(changed)} 個：拿掉單一欄位的 index {sum(r['index_removed'] for r in rows)} 條、"
            f"補上 form_id 的插件名 {sum(r['form_id_fixed'] for r in rows)} 條")
    by_mod: dict[str, int] = {}
    for r in changed:
        by_mod[r["mod"]] = by_mod.get(r["mod"], 0) + r["index_removed"] + r["form_id_fixed"]
    if by_mod:
        rep.add("mods", "INFO", "各 mod", "；".join(f"{m} {n}" for m, n in sorted(by_mod.items())))
    unresolved = [r for r in rows if r["form_id_unresolved"]]
    if unresolved:
        rep.add("unresolved", "WARN", "判斷不出插件的 form_id（沒改，DSD 會略過這些條目）",
                f"{sum(r['form_id_unresolved'] for r in unresolved)} 條："
                + "；".join(f"{r['mod']}/{r['file']} {r['form_id_unresolved']}" for r in unresolved[:6]))
    bad = [r for r in rows if r["status"].startswith(("無法解析", "不是", "硬連結"))]
    if bad:
        rep.add("bad", "FAIL" if any(r["status"].startswith("硬連結") for r in bad) else "WARN", "沒有處理的檔",
                "；".join(f"{r['mod']}/{r['file']}：{r['status']}" for r in bad[:8]))
    rep.data = {"rows": rows}
    path = rep.save(args.out, stem="zh_dsd_normalize")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
