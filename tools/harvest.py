"""Hardlink the mod folders the target list needs from an installed base list into D:\\PM.

從已安裝的基底清單（M&V 或 Nolvus）以硬連結擷取目標需要的 mod 資料夾到 D:\\PM。

Examples (Windows; add --apply to actually write, default is a dry run):
    python tools\\harvest.py --from mv --instance D:\\MV --pm D:\\PM --mo2-and-tools
    python tools\\harvest.py --from nolvus --instance "D:\\Nolvus\\Instances\\Nolvus Awakening" --pm D:\\PM --stock-game

Folders are selected from a plan CSV (default data/analysis/provenance.csv, or a
reports/manifest.csv produced later) by the column action == harvest_<from>.
Destination folder names are always the TARGET names (MO2 matches them exactly).
Hardlinks survive deleting the source install; files named meta.ini are copied.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, mo2  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, REPO_ROOT, Report, read_csv, write_csv  # noqa: E402

DEFAULT_PLAN = REPO_ROOT / "data" / "analysis" / "provenance.csv"
MO2_SKIP = {"mods", "downloads", "profiles", "overwrite", "stock game", "game root", "webcache",
            "crashdumps", "logs", "modorganizer.ini", "portable.txt", "nxmhandler.ini"}
ENB_RESHADE = ["d3d11.dll", "d3dcompiler_46e.dll", "d3dcompiler_47.dll", "dxgi.dll", "ReShade.ini",
               "ReShadePreset.ini", "reshade-shaders", "enbseries", "enbcache", "enblocal.ini", "enbseries.ini"]


def index_dirs(parent: Path) -> dict[str, str]:
    return {mo2.fold(p.name): p.name for p in parent.iterdir() if p.is_dir()} if parent.is_dir() else {}


def resolve_source(target: str, index: dict[str, str]) -> tuple[str | None, str]:
    if mo2.fold(target) in index:
        return index[mo2.fold(target)], "exact"
    base = mo2.strip_dup_suffix(target)
    if base and mo2.fold(base) in index:
        return index[mo2.fold(base)], "dup_suffix"
    return None, "missing"


def nonempty(p: Path) -> bool:
    return p.is_dir() and any(p.iterdir())


def remove_enb(game_dir: Path, apply: bool) -> list[str]:
    removed = []
    for name in ENB_RESHADE:
        p = game_dir / name
        if p.exists():
            removed.append(name)
            if apply:
                shutil.rmtree(p) if p.is_dir() else p.unlink()
    for p in game_dir.glob("enb*"):
        if p.name not in removed and p.suffix.lower() in (".fx", ".bmp", ".ini", ".fxh", ""):
            removed.append(p.name)
            if apply:
                shutil.rmtree(p) if p.is_dir() else p.unlink()
    return removed


def run(args) -> Report:
    src_label = args.source_label
    paths = mo2.locate_instance(args.instance)
    rep = Report(f"harvest-{src_label}")
    pm_root: Path = args.pm
    pm_mods = pm_root / "mods"
    apply = args.apply
    mode = "實際執行" if apply else "試跑（未寫入任何檔案，加 --apply 才會執行）"
    rep.add("mode", "INFO", "模式", mode)

    if not paths["mods"].is_dir():
        rep.add("src", "FAIL", "找不到來源 mods 資料夾", str(paths["mods"]))
        return rep
    if apply:
        pm_mods.mkdir(parents=True, exist_ok=True)
    if not fsutil.same_volume(paths["mods"], pm_root) and not args.allow_copy:
        rep.add("volume", "FAIL", "來源與 D:\\PM 不在同一個磁碟分割區", "硬連結只能在同一個 NTFS 分割區內使用")
        return rep

    plan = read_csv(args.plan)
    wanted = [r for r in plan if r.get("action") == f"harvest_{src_label}"]
    if args.also_actions:
        extra = set(args.also_actions.split(","))
        wanted += [r for r in plan if r.get("action") in extra]
    index = index_dirs(paths["mods"])
    rows = []
    total = fsutil.CloneStats()
    missing = 0
    for r in wanted:
        target = r["folder"]
        src_name, how = resolve_source(target, index)
        row = {"target": target, "source_folder": src_name or "", "match": how, "status": ""}
        if not src_name:
            row["status"] = "missing_in_source"
            missing += 1
        elif nonempty(pm_mods / target) and not args.overwrite:
            row["status"] = "already_present"
        else:
            st = fsutil.clone_tree(paths["mods"] / src_name, pm_mods / target, apply=apply,
                                   allow_copy_fallback=args.allow_copy, overwrite=args.overwrite)
            total.add(st)
            row.update(status="linked" if not st.errors else "errors", linked=st.linked, copied=st.copied,
                       bytes=st.bytes, errors=" | ".join(st.errors[:3]))
        rows.append(row)

    extras = []
    if args.mo2_and_tools:
        base = paths["ini_dir"]
        for entry in sorted(base.iterdir(), key=lambda p: p.name.lower()):
            if entry.name.casefold() in MO2_SKIP or entry.suffix.lower() == ".wabbajack":
                continue
            dest = pm_root / entry.name
            if entry.is_dir():
                st = fsutil.clone_tree(entry, dest, apply=apply, allow_copy_fallback=args.allow_copy)
            else:
                st = fsutil.CloneStats()
                if not dest.exists():
                    if apply:
                        os.link(entry, dest)
                    st.linked = 1
            total.add(st)
            extras.append(entry.name)
        rep.add("mo2", "PASS" if (base / "ModOrganizer.exe").exists() else "WARN", "MO2 程式與工具",
                f"{len(extras)} 項（含 tools\\）" if extras else "來源沒有 ModOrganizer.exe")
    if args.stock_game:
        game = paths.get("game")
        if not game or not Path(game).is_dir():
            rep.add("stock", "FAIL", "找不到 STOCK GAME", str(game))
        else:
            dest = pm_root / "STOCK GAME"
            st = fsutil.clone_tree(Path(game), dest, apply=apply, allow_copy_fallback=args.allow_copy,
                                   copy_names={"skyrim.ini", "skyrimprefs.ini", "skyrimcustom.ini"})
            total.add(st)
            removed = remove_enb(dest, apply) if apply else [n for n in ENB_RESHADE if (Path(game) / n).exists()]
            rep.add("stock", "PASS", "STOCK GAME 已連結", f"{st.linked} 個檔案；移除 ENB/ReShade：{', '.join(removed) or '無'}")

    out_csv = write_csv(args.out / f"harvest-{src_label}.csv", rows,
                        ["target", "source_folder", "match", "status", "linked", "copied", "bytes", "errors"])
    done = sum(1 for r in rows if r["status"] in ("linked", "already_present"))
    rep.add("folders", "PASS" if missing == 0 else "WARN", f"計畫中要從 {src_label} 擷取的資料夾",
            f"{len(wanted)} 個：完成/已存在 {done}，來源缺少 {missing}（見 {out_csv.name}）")
    rep.add("bytes", "INFO", "共享資料量（硬連結不佔額外空間）", fsutil.human(total.bytes))
    if total.errors:
        rep.add("errors", "FAIL", "錯誤", f"{len(total.errors)} 個，例如：{total.errors[0]}")
    if src_label == "mv":
        rep.add("next", "INFO", "下一步",
                "刪除 D:\\MV 前，先執行 tools\\zh\\extract_official.py 取出官方繁中字串與字型")
    rep.data = {"plan": str(args.plan), "pm": str(pm_root), "source_mods": str(paths["mods"]),
                "extras": extras, "missing": [r["target"] for r in rows if r["status"] == "missing_in_source"]}
    return rep


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="以硬連結擷取 mod 資料夾到 D:\\PM（預設試跑）")
    ap.add_argument("--from", dest="source_label", required=True, choices=["mv", "nolvus"])
    ap.add_argument("--instance", required=True, type=Path, help="來源清單根目錄")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"), help="新實例根目錄，預設 D:\\PM")
    ap.add_argument("--plan", type=Path, default=DEFAULT_PLAN, help="計畫 CSV（provenance.csv 或 manifest.csv）")
    ap.add_argument("--also-actions", default="", help="額外一併擷取的 action（逗號分隔）")
    ap.add_argument("--mo2-and-tools", action="store_true", help="一併連結 MO2 程式與 tools\\（建議從 M&V）")
    ap.add_argument("--stock-game", action="store_true", help="一併連結 STOCK GAME 並移除 ENB（建議從 Nolvus）")
    ap.add_argument("--overwrite", action="store_true", help="覆蓋 D:\\PM 中已存在的資料夾")
    ap.add_argument("--allow-copy", action="store_true", help="無法建立硬連結時改為複製（會佔空間）")
    ap.add_argument("--apply", action="store_true", help="實際寫入（未加時只試跑）")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    rep = run(args)
    path = rep.save(args.out, stem=f"harvest-{args.source_label}")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
