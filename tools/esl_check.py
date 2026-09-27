"""Summarise plugin records and check or set the ESL (light) flag.

插件記錄摘要與 ESL（輕量）旗標：看插件覆寫了哪些記錄類型、能不能直接加 ESL 旗標；
替重建出來的輸出（Synthesis.esp、FNIS.esp）加旗標；掃描可以騰出完整插件名額的候選。

Usage (Windows):
    python tools\\esl_check.py --plugin "D:\\...\\Synthesis.esp"             (summary, read-only)
    python tools\\esl_check.py --scan --pm D:\\PM [--profile Pages-ZH]      (every enabled full plugin, read-only)
    python tools\\esl_check.py --plugin "D:\\PM\\mods\\SYNTHESSIS\\Synthesis.esp" --flag --apply
    python tools\\esl_check.py --plugin "...\\Synthesis.esp" --subrecords LAND   (which fields a record type carries)
--flag only touches a file with a single hardlink (a generated output, never a harvested
original) whose new records already fit the light range. Writes reports\\esl_check.txt/.json/.csv.
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, tes4, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402

FIELDS = ["plugin", "provider", "kind", "hedr", "masters", "records", "new", "overrides", "new_cells",
          "esl_ready", "reason", "override_types", "new_types"]


def top(counts: dict[str, int], n: int = 12) -> str:
    return ", ".join(f"{k} {v}" for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n])


def row_for(path: Path, provider: str = "") -> dict:
    s = tes4.summarize(path)
    ok, why = tes4.esl_ready(s)
    return {"plugin": path.name, "provider": provider or str(path.parent), "kind": s.header.kind,
            "hedr": f"{s.header.hedr_version:.2f}", "masters": len(s.header.masters), "records": s.records,
            "new": s.new, "overrides": s.overrides, "new_cells": s.new_cells, "esl_ready": "yes" if ok else "",
            "reason": why, "override_types": top(s.overrides_by_type), "new_types": top(s.new_by_type)}


def subrecord_counts(path: Path, rtype: str) -> tuple[int, dict[str, int]]:
    """(records of rtype, how many of them carry each subrecord type)."""
    _head, items = tes4.parse_plugin(path.read_bytes(), path.name)
    n, counts = 0, {}
    for rec in tes4.walk_records(items):
        if rec.type != rtype:
            continue
        n += 1
        for sub in {t for t, _ in tes4.iter_subrecords(rec.payload())}:
            counts[sub] = counts.get(sub, 0) + 1
    return n, counts


def set_light_flag(path: Path) -> str:
    """Set the light flag in place; returns '' on success or why it was refused."""
    if os.stat(fsutil.long_path(path)).st_nlink > 1:
        return "檔案是硬連結（來源實例的原檔），不能原地修改"
    ok, why = tes4.esl_ready(tes4.summarize(path))
    if not ok:
        return why
    with open(fsutil.long_path(path), "r+b") as f:
        f.seek(8)
        (flags,) = struct.unpack("<I", f.read(4))
        f.seek(8)
        f.write(struct.pack("<I", flags | tes4.FLAG_LIGHT))
    return ""


def scan(pm: Path, profile: str) -> list[dict]:
    prof = vfs.open_profile(pm, profile)
    data_dir = prof.game_dir / "Data"
    providers = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, data_dir)
    rows = []
    for p in prof.plugins:
        path = providers.get(p.name.lower())
        if not p.enabled or path is None or path.parent == data_dir:
            continue
        try:
            if tes4.read_header(path).is_light:
                continue
            rows.append(row_for(path, path.parent.name))
        except (tes4.PluginError, OSError) as e:
            rows.append({"plugin": p.name, "provider": path.parent.name, "reason": f"無法讀取：{e}"})
    return rows


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="插件記錄摘要與 ESL 旗標（預設唯讀；--flag 要加 --apply 才寫入）")
    ap.add_argument("--plugin", type=Path, action="append", default=[], help="要分析的插件檔（可重複）")
    ap.add_argument("--scan", action="store_true", help="掃描設定檔中所有已啟用的完整插件")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--flag", action="store_true", help="替 --plugin 指定的檔案加上 ESL 旗標")
    ap.add_argument("--subrecords", metavar="TYPE", help="統計 --plugin 中這種記錄帶有哪些子記錄，例如 LAND")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    rep = Report("esl_check")
    rows: list[dict] = []
    if not args.plugin and not args.scan:
        ap.error("請指定 --plugin 或 --scan")
    for path in args.plugin:
        try:
            r = row_for(path)
        except (tes4.PluginError, OSError) as e:
            rep.add(f"read:{path.name}", "FAIL", path.name, f"無法讀取：{e}")
            continue
        rows.append(r)
        detail = (f"{r['kind']}，HEDR {r['hedr']}，前置 {r['masters']} 個；記錄 {r['records']} 筆"
                  f"（新增 {r['new']}、覆寫 {r['overrides']}）；覆寫類型：{r['override_types'] or '無'}"
                  + (f"；新增類型：{r['new_types']}" if r["new"] else "")
                  + (f"；新增 CELL {r['new_cells']} 個" if r["new_cells"] else "")
                  + f"；ESL：{r['reason']}")
        rep.add(f"sum:{path.name}", "INFO", path.name, detail)
        if args.subrecords:
            try:
                n, counts = subrecord_counts(path, args.subrecords)
            except (tes4.PluginError, OSError, ValueError) as e:
                rep.add(f"subs:{path.name}", "FAIL", f"{args.subrecords} 子記錄", f"無法讀取：{e}")
            else:
                rep.add(f"subs:{path.name}", "INFO", f"{args.subrecords} 子記錄",
                        f"{args.subrecords} 記錄 {n} 筆；各子記錄出現在幾筆記錄：{top(counts, 20) or '無'}")
        if args.flag:
            if not args.apply:
                rep.add(f"flag:{path.name}", "INFO", "加 ESL 旗標（試跑）",
                        "可以" if r["esl_ready"] else f"不行：{r['reason']}")
                continue
            why = set_light_flag(path)
            rep.add(f"flag:{path.name}", "FAIL" if why else "PASS", "加 ESL 旗標",
                    why or f"{path.name} 已是輕量插件")
    if args.scan:
        found = scan(args.pm, args.profile)
        rows += found
        ready = [r for r in found if r.get("esl_ready")]
        safe = [r for r in ready if not r.get("new_cells")]
        rep.add("scan", "INFO", "已啟用的完整插件（不含本體與 CC）", f"{len(found)} 個")
        rep.add("ready", "INFO", "可以直接加 ESL 旗標", f"{len(ready)} 個，其中沒有新增 CELL 的 {len(safe)} 個"
                + (f"，例如：{', '.join(r['plugin'] for r in safe[:10])}" if safe else ""))
        rep.add("note", "INFO", "說明", "這只是騰出名額的候選清單，不要自行加旗標；需要時由雲端決定")
    write_csv(args.out / "esl_check.csv", rows, FIELDS)
    rep.data = {"plugins": rows}
    path = rep.save(args.out, stem="esl_check")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
