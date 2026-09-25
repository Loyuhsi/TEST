"""Check the profile's plugins: missing masters, master order, 254/4096 limits, BEES need.

檢查設定檔插件：缺少前置、前置順序、254 完整／4096 輕量上限、是否需要 BEES。

Usage (Windows):  python tools\\check_plugins.py --pm D:\\PM [--profile Pages-ZH]
Writes reports\\check_plugins.csv and .txt/.json. Read-only.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, pe, tes4, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402


def analyse(prof: vfs.Profile) -> tuple[list[dict], dict]:
    data_dir = prof.game_dir / "Data"
    providers = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, data_dir)
    primaries = vfs.primary_plugins(prof.game_dir)
    enabled = [p.name for p in prof.plugins if p.enabled]
    prim_low = {p.lower() for p in primaries}
    rows: list[dict] = []
    headers: dict[str, tes4.PluginHeader] = {}
    for name in primaries + [n for n in enabled if n.lower() not in prim_low]:
        path = providers.get(name.lower())
        row = {"plugin": name, "provider": "", "kind": "", "hedr": "", "masters": "", "status": "ok", "problem": ""}
        if path is None:
            if name in vfs.GENERATED_PLUGINS:
                row.update(status="pending", problem="輸出插件尚未重建（第五階段）")
            else:
                row.update(status="missing", problem="找不到插件檔（mod 未安裝或已停用）")
        else:
            row["provider"] = path.parent.name if path.parent != data_dir else "STOCK GAME\\Data"
            try:
                h = tes4.read_header(path)
                headers[name.lower()] = h
                row.update(kind=h.kind, hedr=f"{h.hedr_version:.2f}", masters=";".join(h.masters))
            except (tes4.PluginError, OSError) as e:
                row.update(status="unreadable", problem=str(e))
        rows.append(row)

    # effective load order: primaries, then masters (ESM/ESL-flagged), then the rest, keeping list order
    def is_master(r):
        h = headers.get(r["plugin"].lower())
        return h.is_master if h else r["plugin"].lower().endswith((".esm", ".esl"))
    prim_rows = [r for r in rows if r["plugin"].lower() in prim_low]
    rest = [r for r in rows if r["plugin"].lower() not in prim_low]
    order = prim_rows + [r for r in rest if is_master(r)] + [r for r in rest if not is_master(r)]
    pos = {r["plugin"].lower(): i for i, r in enumerate(order)}
    for i, r in enumerate(order):
        r["order"] = i
        h = headers.get(r["plugin"].lower())
        if not h:
            continue
        miss = [m for m in h.masters if m.lower() not in pos]
        late = [m for m in h.masters if m.lower() in pos and pos[m.lower()] > i]
        pending = [m for m in miss if m in vfs.GENERATED_PLUGINS]
        miss = [m for m in miss if m not in vfs.GENERATED_PLUGINS]
        if miss:
            r.update(status="missing_master", problem="缺少前置：" + ", ".join(miss))
        elif late:
            r.update(status="master_order", problem="前置載入順序在後：" + ", ".join(late))
        elif pending and r["status"] == "ok":
            r.update(status="pending_master", problem="前置為待重建輸出：" + ", ".join(pending))

    loaded = [r for r in order if r["status"] not in ("missing",)]
    kinds = Counter(headers[r["plugin"].lower()].is_light if r["plugin"].lower() in headers
                    else r["plugin"].lower().endswith(".esl") for r in loaded)
    full, light = kinds.get(False, 0), kinds.get(True, 0)
    bees_need = sum(1 for h in headers.values() if h.needs_bees)
    bees_present = any(d.name.lower() == "backportedeslsupport.dll"
                       for paths in vfs.skse_dll_providers(prof.mods_dir, prof.enabled_folders).values()
                       for d in paths[:1])
    exe_ver = pe.file_version(prof.game_dir / "SkyrimSE.exe")
    stats = {"full": full, "light": light, "bees_needed": bees_need, "bees_present": bees_present,
             "exe_version": exe_ver, "status_counts": dict(Counter(r["status"] for r in order))}
    return order, stats


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="檢查插件前置與數量上限（唯讀）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    prof = vfs.open_profile(args.pm, args.profile)
    order, st = analyse(prof)
    write_csv(args.out / "check_plugins.csv", order,
              ["order", "plugin", "provider", "kind", "hedr", "status", "problem", "masters"])
    rep = Report("check_plugins")
    rep.data = st
    sc = st["status_counts"]
    rep.add("full", "PASS" if st["full"] <= tes4.MAX_FULL else "FAIL", "完整插件數（含本體）",
            f"{st['full']} / {tes4.MAX_FULL}", st["full"])
    rep.add("light", "PASS" if st["light"] <= tes4.MAX_LIGHT else "FAIL", "輕量插件數（ESL）",
            f"{st['light']} / {tes4.MAX_LIGHT}", st["light"])
    for key, title, status in (("missing_master", "缺少前置的插件", "FAIL"), ("master_order", "前置順序錯誤", "FAIL"),
                               ("missing", "找不到的插件", "WARN"), ("unreadable", "無法讀取", "FAIL"),
                               ("pending", "待重建的輸出插件", "INFO"), ("pending_master", "依賴待重建輸出", "INFO")):
        n = sc.get(key, 0)
        rep.add(key, status if n else "PASS", title, f"{n} 個" + ("（見 reports\\check_plugins.csv）" if n else ""))
    ver = st["exe_version"] or "?"
    if st["bees_needed"] and ver.startswith("1.5.") and not st["bees_present"]:
        rep.add("bees", "FAIL", "BEES", f"{st['bees_needed']} 個插件是 1.71 版標頭，但未偵測到 Backported Extended ESL Support")
    else:
        rep.add("bees", "PASS", "BEES", f"1.71 標頭插件 {st['bees_needed']} 個；BEES {'已安裝' if st['bees_present'] else '未偵測'}；遊戲 {ver}")
    path = rep.save(args.out, stem="check_plugins")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
