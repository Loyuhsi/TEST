"""Tidy the DSD JSON files of the ZH mods so Dynamic String Distributor 1.4.x applies the right entry.

整理 ZH mod 裡的 DSD JSON：
  - 單一欄位（FULL、DESC、DNAM、SHRT…）不能帶 "index"。DSD 1.4.x 不會把低優先、帶 index 的條目去重，
    它可能反過來蓋掉正確的那一筆。只有 QUST CNAM／NNAM、INFO NAM1、MESG ITXT、PERK EPF2／EPFD 需要 index。
  - form_id 少了 "|插件名"（例如 NIM Translator 匯出的檔）時，補上所在資料夾的插件名；否則 DSD 會略過。
Only enabled mods whose name starts with --prefix (default "ZH") are touched, only single-link files
(never a hardlinked original), and the first original is kept as <file>.bak. Dry run unless --apply.

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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pm import fsutil, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402
from zh.common import iter_dsd, uses_index  # noqa: E402

FIELDS = ["mod", "file", "entries", "index_removed", "form_id_fixed", "status"]


def tidy(entries: list, plugin_dir: str) -> tuple[int, int]:
    """Fix entries in place; returns (indexes removed, form_ids completed)."""
    removed = fixed = 0
    for e in entries:
        if not isinstance(e, dict):
            continue
        if "index" in e and not uses_index(str(e.get("type", ""))):
            del e["index"]
            removed += 1
        fid = e.get("form_id")
        if isinstance(fid, str) and fid.strip() and "|" not in fid:
            e["form_id"] = f"{fid.strip()}|{plugin_dir}"
            fixed += 1
    return removed, fixed


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="整理 ZH mod 的 DSD JSON（預設試跑）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--prefix", default="ZH", help="只處理名稱以這個開頭的已啟用 mod（預設 ZH）")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    prof = vfs.open_profile(args.pm, args.profile)
    rep = Report("zh_dsd_normalize")
    rep.add("mode", "INFO", "模式", "實際執行" if args.apply else "試跑（加 --apply 才會寫入）")
    rows: list[dict] = []
    for folder in prof.enabled_folders:
        if not folder.upper().startswith(args.prefix.upper()):
            continue
        for plugin_dir, js in iter_dsd(prof.mods_dir / folder):
            row = {"mod": folder, "file": f"{plugin_dir}/{js.name}", "entries": 0, "index_removed": 0,
                   "form_id_fixed": 0, "status": ""}
            rows.append(row)
            try:
                data = json.loads(js.read_text(encoding="utf-8-sig"))
            except (OSError, ValueError) as e:
                row["status"] = f"無法解析（DSD 會略過整個檔）：{e}"
                continue
            if not isinstance(data, list):
                row["status"] = "不是 DSD 的條目清單"
                continue
            row["entries"] = len(data)
            removed, fixed = tidy(data, plugin_dir)
            row["index_removed"], row["form_id_fixed"] = removed, fixed
            if not (removed or fixed):
                row["status"] = "不用改"
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
                row["status"] = "已修正"
            else:
                row["status"] = "會修正"
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
