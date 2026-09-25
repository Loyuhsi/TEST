"""Remove plugins that depend (directly or indirectly) on dropped or unavailable plugins.

修剪相依插件：凡是前置檔被捨棄或取得不到的插件，一併停用（可遞迴），並建議停用對應資料夾。

Usage (Windows; close MO2 first; dry run unless --apply):
    python tools\\prune_dependents.py --pm D:\\PM [--profile Pages-ZH] [--disable-folders] [--apply]
A plugin is "unavailable" when no enabled mod provides it, except the tool outputs that are
regenerated in Phase 5 (Synthesis.esp, DynDOLOD.esm, ...). Writes reports\\prune-plan.csv.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, mo2, tes4, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402
from build_instance import backup  # noqa: E402


def plan(prof: vfs.Profile) -> tuple[list[dict], list[str]]:
    data_dir = prof.game_dir / "Data"
    providers = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, data_dir)
    primaries = {p.lower() for p in vfs.primary_plugins(prof.game_dir)}
    enabled = [p.name for p in prof.plugins if p.enabled]
    removed: dict[str, str] = {}
    headers: dict[str, tes4.PluginHeader] = {}
    for n in enabled:
        path = providers.get(n.lower())
        if path is None:
            if n not in vfs.GENERATED_PLUGINS:
                removed[n.lower()] = "無提供者（mod 被捨棄或未安裝）"
            continue
        try:
            headers[n.lower()] = tes4.read_header(path)
        except (tes4.PluginError, OSError) as e:
            removed[n.lower()] = f"無法讀取：{e}"
    available = {n.lower() for n in enabled} | primaries | {g.lower() for g in vfs.GENERATED_PLUGINS}
    changed = True
    while changed:
        changed = False
        for n in enabled:
            k = n.lower()
            if k in removed or k not in headers:
                continue
            for m in headers[k].masters:
                mk = m.lower()
                if mk in removed or mk not in available:
                    removed[k] = f"前置 {m} " + ("已被移除" if mk in removed else "未啟用／不存在")
                    changed = True
                    break
    rows = []
    folder_plugins: dict[str, list[str]] = {}
    for n in enabled:
        path = providers.get(n.lower())
        folder = path.parent.name if path is not None and path.parent != data_dir else ""
        if folder:
            folder_plugins.setdefault(folder, []).append(n.lower())
        rows.append({"plugin": n, "folder": folder, "action": "remove" if n.lower() in removed else "keep",
                     "reason": removed.get(n.lower(), "")})
    # folders whose every root plugin is removed are usually patches for something dropped
    suggest = []
    for folder in prof.enabled_folders:
        roots = [p.lower() for p in vfs.root_plugins(prof.mods_dir / folder)]
        if roots and all(p in removed or p not in {x.lower() for x in enabled} for p in roots) \
                and any(p in removed for p in roots):
            suggest.append(folder)
    return rows, suggest


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="修剪相依插件（預設試跑；請先關閉 MO2）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--disable-folders", action="store_true", help="一併停用所有插件都被移除的資料夾")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    prof = vfs.open_profile(args.pm, args.profile)
    rows, suggest = plan(prof)
    write_csv(args.out / "prune-plan.csv", rows, ["plugin", "folder", "action", "reason"])
    rm = [r for r in rows if r["action"] == "remove"]
    rep = Report("prune_dependents")
    rep.add("mode", "INFO", "模式", "實際執行" if args.apply else "試跑（加 --apply 才會寫入）")
    rep.add("remove", "WARN" if rm else "PASS", "要停用的插件", f"{len(rm)} 個" +
            (f"，例如：{', '.join(r['plugin'] for r in rm[:8])}" if rm else ""))
    rep.add("folders", "INFO", "建議停用的資料夾", f"{len(suggest)} 個" +
            (f"：{', '.join(suggest[:8])}" if suggest else ""))
    if args.apply and (rm or (suggest and args.disable_folders)):
        pdir = prof.profile_dir
        b = backup([pdir / "plugins.txt", pdir / "modlist.txt", pdir / "loadorder.txt"], pdir, True)
        gone = {r["plugin"].lower() for r in rm}
        mo2.write_plugins(pdir / "plugins.txt", [p for p in prof.plugins if p.name.lower() not in gone])
        if (pdir / "loadorder.txt").exists():
            (pdir / "loadorder.txt").unlink()
        if args.disable_folders and suggest:
            sset = {mo2.fold(s) for s in suggest}
            mo2.write_modlist(pdir / "modlist.txt",
                              [mo2.ModEntry(e.name, "-" if mo2.fold(e.name) in sset else e.state, e.line_no)
                               for e in prof.modlist])
        rep.add("backup", "INFO", "備份", str(b))
    rep.data = {"removed": rm, "suggested_folders": suggest}
    path = rep.save(args.out, stem="prune_dependents")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
