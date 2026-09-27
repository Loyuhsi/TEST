"""Audit every SKSE DLL that wins in the profile: will it load on Skyrim 1.5.97?

檢查設定檔中每個生效的 SKSE DLL 能否在 1.5.97 上載入（AE 專用版需替換）。

Usage (Windows):  python tools\\audit_skse.py --pm D:\\PM [--profile Pages-ZH]
                  python tools\\audit_skse.py --dll "path\\to\\Some.dll"     (one file only)
Also checks the STOCK GAME root: SkyrimSE.exe version, SKSE loader, Address Library
bin, and leftover ENB/ReShade files that Community Shaders refuses to run with.
Optional: --mv-1597-map data/analysis/mv2401_folder_map.csv (from tools/analysis/mv_wabbajack_map.py
run on the MV 2.40.1 .wabbajack) to suggest the 1.5.97-era Nexus file for each flagged mod.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, mo2, pe, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, read_csv, write_csv  # noqa: E402

FORBIDDEN_ROOT = ["d3d11.dll", "d3dcompiler_46e.dll", "d3dcompiler_47.dll", "dxgi.dll", "enbseries.ini",
                  "enblocal.ini", "enbseries"]
CLASS_TEXT = {"se": "SE 版（可用）", "multi": "多版本 NG（可用）", "ae_only": "AE 專用（1.5.97 無法載入）",
              "not_skse": "非 SKSE 外掛（相依函式庫）", "unknown": "無法判斷", "unreadable": "無法讀取"}
ADDRLIB_TEXT = {"ae": "只找 AE 版（versionlib-*.bin）", "se": "只找 SE 版（version-*.bin）",
                "both": "SE／AE 都支援", "": "沒有找到路徑字串"}


def classify(path: Path) -> tuple[str, str]:
    """(runtime class, Address Library hint) of one DLL."""
    try:
        info = pe.read_dll(path)
        return info.runtime_class, info.addrlib
    except (pe.PEError, OSError, IndexError, ValueError):
        return "unreadable", ""


def check_files(paths: list[Path], out: Path) -> int:
    rep = Report("audit_skse-dll")
    rows = []
    for p in paths:
        cls, addrlib = classify(p)
        rows.append({"dll": p.name, "path": str(p), "class": cls, "meaning": CLASS_TEXT.get(cls, cls),
                     "addrlib": addrlib})
        status = "FAIL" if cls in ("ae_only", "unreadable") else "PASS"
        rep.add(f"dll:{p}", status, p.name, f"{CLASS_TEXT.get(cls, cls)}；Address Library：{ADDRLIB_TEXT[addrlib]}")
    write_csv(out / "audit_skse-dll.csv", rows)
    rep.data = {"dlls": rows}
    path = rep.save(out, stem="audit_skse-dll")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="檢查 SKSE DLL 與 1.5.97 相容性（唯讀）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--mv-1597-map", type=Path, default=None)
    ap.add_argument("--dll", type=Path, action="append", default=[], help="只判斷這個 DLL 檔（可重複）")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    if args.dll:
        return check_files(args.dll, args.out)
    prof = vfs.open_profile(args.pm, args.profile)
    hints = {}
    if args.mv_1597_map and args.mv_1597_map.exists():
        hints = {mo2.fold(r["folder"]): r for r in read_csv(args.mv_1597_map)}
    providers = vfs.skse_dll_providers(prof.mods_dir, prof.enabled_folders)
    rows = []
    for name, paths in sorted(providers.items()):
        win = paths[0]
        cls, addrlib = classify(win)
        folder = win.parents[2].name
        h = hints.get(mo2.fold(folder), {})
        rows.append({"dll": win.name, "folder": folder, "class": cls, "meaning": CLASS_TEXT.get(cls, cls),
                     "addrlib": addrlib,
                     "overridden": ";".join(p.parents[2].name for p in paths[1:]),
                     "hint_1597_mod": h.get("nexus_mod_id", ""), "hint_1597_file": h.get("nexus_file_id", ""),
                     "hint_1597_version": h.get("nexus_version", "")})
    write_csv(args.out / "audit_skse.csv", rows)
    rep = Report("audit_skse")
    c = Counter(r["class"] for r in rows)
    bad = [r for r in rows if r["class"] in ("ae_only", "unreadable")]
    rep.add("dlls", "INFO", "生效的 SKSE DLL", ", ".join(f"{CLASS_TEXT.get(k, k)}={v}" for k, v in sorted(c.items())))
    rep.add("ae_only", "FAIL" if bad else "PASS", "需替換的 DLL",
            f"{len(bad)} 個：" + ", ".join(f"{r['dll']}（{r['folder']}）" for r in bad[:10]) if bad else "無")
    g = prof.game_dir
    ver = pe.file_version(g / "SkyrimSE.exe")
    rep.add("exe", "PASS" if ver == "1.5.97.0" else "FAIL", "STOCK GAME 遊戲版本", f"{ver}（需要 1.5.97.0）")
    rep.add("skse", "PASS" if (g / "skse64_1_5_97.dll").exists() and (g / "skse64_loader.exe").exists() else "FAIL",
            "SKSE 1.5.97", "skse64_loader.exe + skse64_1_5_97.dll")
    addr = any(any((p.parent / "version-1-5-97-0.bin").exists() for p in paths) for paths in providers.values()) or any(
        (prof.mods_dir / f / sub / "version-1-5-97-0.bin").exists()
        for f in prof.enabled_folders for sub in ("SKSE/Plugins", "skse/plugins"))
    rep.add("addrlib", "PASS" if addr else "FAIL", "Address Library（version-1-5-97-0.bin）", "已找到" if addr else "未找到")
    leftovers = [n for n in FORBIDDEN_ROOT if (g / n).exists()]
    rep.add("enb", "PASS" if not leftovers else "FAIL", "遊戲根目錄的 ENB/ReShade 殘留",
            ", ".join(leftovers) if leftovers else "無")
    cs = providers.get("communityshaders.dll")
    rep.add("cs", "PASS" if cs else "FAIL", "Community Shaders",
            f"已安裝（{cs[0].parents[2].name}）" if cs else "找不到 CommunityShaders.dll：照 docs/04 第 7 節安裝官方版")
    roots = [f for f in prof.enabled_folders
             if any((prof.mods_dir / f / n).is_dir() for n in ("Root", "root", "ROOT"))]
    rep.add("root", "INFO" if not roots else "WARN", "含 Root 資料夾的 mod（Root Builder 會部署到遊戲資料夾）",
            ", ".join(roots[:10]) if roots else "無")
    rep.data = {"exe_version": ver, "bad": bad, "root_mods": roots}
    path = rep.save(args.out, stem="audit_skse")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
