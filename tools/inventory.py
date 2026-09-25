"""Inventory an installed MO2 instance (Nolvus or Mages & Vikings) into a CSV.

盤點已安裝的 MO2 實例（Nolvus 或 M&V）：每個 mod 的 Nexus ID、插件、SKSE DLL、大小。

Usage (Windows):
    python tools\\inventory.py --source mv     --instance D:\\MV
    python tools\\inventory.py --source nolvus --instance "D:\\Nolvus\\Instances\\Nolvus Awakening"
Writes reports\\inventory-<source>.csv and reports\\inventory-<source>.txt/.json. Read-only.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, mo2, pe  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402

PLUGIN_EXT = (".esp", ".esm", ".esl")
ENB_ROOT_FILES = ("d3d11.dll", "d3dcompiler_46e.dll", "dxgi.dll", "enbseries.ini", "enblocal.ini")
FIELDS = ["folder", "enabled", "priority", "is_separator", "mod_id", "file_id", "version",
          "installation_file", "bytes", "files", "plugins", "bsas", "skse_dlls", "dll_classes",
          "has_fontconfig", "translations_english", "translations_chinese", "nexus_url"]


def ci_child(parent: Path, *names: str) -> Path | None:
    """Case-insensitive child lookup (MO2 folders mix 'SKSE/Plugins' and 'skse/plugins')."""
    cur = parent
    for name in names:
        if not cur.is_dir():
            return None
        match = None
        try:
            for entry in os.scandir(cur):
                if entry.name.casefold() == name.casefold():
                    match = Path(entry.path)
                    break
        except OSError:
            return None
        if match is None:
            return None
        cur = match
    return cur


def scan_mod(folder: Path, sizes: bool) -> dict:
    row: dict = {"folder": folder.name}
    meta = folder / "meta.ini"
    if meta.exists():
        m = mo2.read_meta_ini(meta)
        row.update(mod_id=m.mod_id or "", file_id=m.file_id or "", version=m.version,
                   installation_file=m.installation_file, nexus_url=mo2.nexus_url(m.mod_id, m.file_id))
    plugins, bsas = [], []
    try:
        for e in os.scandir(folder):
            if e.is_file():
                low = e.name.lower()
                if low.endswith(PLUGIN_EXT):
                    plugins.append(e.name)
                elif low.endswith(".bsa"):
                    bsas.append(e.name)
    except OSError:
        pass
    row["plugins"] = ";".join(sorted(plugins, key=str.lower))
    row["bsas"] = ";".join(sorted(bsas, key=str.lower))
    dlls, classes = [], []
    sp = ci_child(folder, "SKSE", "Plugins")
    if sp:
        for d in sorted(sp.glob("*.dll"), key=lambda p: p.name.lower()):
            try:
                cls = pe.read_dll(d).runtime_class
            except (pe.PEError, OSError, IndexError, ValueError):
                cls = "unreadable"
            dlls.append(d.name)
            classes.append(f"{d.name}:{cls}")
    row["skse_dlls"] = ";".join(dlls)
    row["dll_classes"] = ";".join(classes)
    iface = ci_child(folder, "interface")
    row["has_fontconfig"] = "yes" if iface and ci_child(iface, "fontconfig.txt") else ""
    tr = ci_child(folder, "interface", "translations")
    if tr:
        names = [p.name for p in tr.iterdir() if p.is_file()]
        row["translations_english"] = ";".join(n for n in names if n.lower().endswith("_english.txt"))
        row["translations_chinese"] = ";".join(n for n in names if n.lower().endswith("_chinese.txt"))
    if sizes:
        b, n = fsutil.dir_size(folder)
        row["bytes"], row["files"] = b, n
    return row


def run(source: str, instance: Path, profile: str | None, sizes: bool, out_dir: Path) -> Report:
    paths = mo2.locate_instance(instance)
    rep = Report(f"inventory-{source}")
    mods_dir = paths["mods"]
    if not mods_dir.is_dir():
        rep.add("mods", "FAIL", "找不到 mods 資料夾", str(mods_dir))
        return rep
    profiles = mo2.list_profiles(paths["profiles"])
    if profile is None and profiles:
        profile = profiles[0] if len(profiles) == 1 else max(
            profiles, key=lambda p: (paths["profiles"] / p / "modlist.txt").stat().st_mtime)
    order: dict[str, tuple[int, bool]] = {}
    if profile:
        entries = mo2.read_modlist(paths["profiles"] / profile / "modlist.txt")
        for i, e in enumerate(entries, start=1):
            order[mo2.fold(e.name)] = (i, e.enabled)
    rows = []
    folders = sorted((p for p in mods_dir.iterdir() if p.is_dir()), key=lambda p: p.name.lower())
    for n, folder in enumerate(folders, start=1):
        if n % 250 == 0:
            print(f"  已掃描 {n}/{len(folders)} …", flush=True)
        row = scan_mod(folder, sizes)
        pri, en = order.get(mo2.fold(folder.name), ("", False))
        row.update(priority=pri, enabled="yes" if en else "", is_separator="yes" if folder.name.endswith(
            mo2.SEPARATOR_SUFFIX) else "")
        rows.append(row)
    csv_path = write_csv(out_dir / f"inventory-{source}.csv", rows, FIELDS)

    game = paths.get("game")
    rep.data = {"instance": str(instance), "mods_dir": str(mods_dir), "profiles": profiles,
                "profile_used": profile, "game_dir": str(game) if game else "", "csv": str(csv_path)}
    rep.add("mods", "PASS", "mod 資料夾數", f"{len(rows)}（設定檔 {profile or '無'} 啟用 "
            f"{sum(1 for r in rows if r.get('enabled'))} 個）", len(rows))
    with_ids = sum(1 for r in rows if r.get("mod_id"))
    rep.add("nexus_ids", "INFO", "含 Nexus ID 的 mod", f"{with_ids}/{len(rows)}")
    cls = Counter(c.rsplit(":", 1)[1] for r in rows for c in (r.get("dll_classes") or "").split(";") if c)
    rep.add("dlls", "INFO", "SKSE DLL 類型", ", ".join(f"{k}={v}" for k, v in sorted(cls.items())) or "無")
    if sizes:
        total = sum(int(r.get("bytes") or 0) for r in rows)
        rep.add("size", "INFO", "mods 總大小", fsutil.human(total), total)
    if game and Path(game).exists():
        g = Path(game)
        ver = pe.file_version(g / "SkyrimSE.exe")
        rep.add("exe", "INFO", "遊戲執行檔版本", f"{ver}（{g.name}）", ver)
        skse = sorted(p.name for p in g.glob("skse64_*.dll"))
        rep.add("skse", "INFO", "SKSE 版本檔", ", ".join(skse) or "無")
        enb = [n for n in ENB_ROOT_FILES if (g / n).exists()] + (["enbseries/"] if (g / "enbseries").is_dir() else [])
        rep.add("enb", "INFO", "遊戲根目錄的 ENB/ReShade 檔", ", ".join(enb) or "無")
        strings_bsa = g / "Data" / "Skyrim - Interface.bsa"
        rep.add("iface", "INFO", "Skyrim - Interface.bsa", "存在" if strings_bsa.exists() else "不存在")
        rep.data["exe_version"] = ver
    else:
        rep.add("game", "WARN", "找不到 Stock Game 資料夾", "請用 --instance 指向清單根目錄")
    return rep


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="盤點 MO2 實例（唯讀）")
    ap.add_argument("--source", required=True, help="標籤，例如 mv 或 nolvus")
    ap.add_argument("--instance", required=True, type=Path, help="清單根目錄（含 ModOrganizer.ini 或 MO2\\）")
    ap.add_argument("--profile", default=None, help="要讀取的設定檔名稱（預設自動選擇）")
    ap.add_argument("--no-sizes", action="store_true", help="不計算資料夾大小（較快）")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    rep = run(args.source, args.instance, args.profile, not args.no_sizes, args.out)
    path = rep.save(args.out, stem=f"inventory-{args.source}")
    print(rep.text())
    print(f"\n報告：{path}，清單：{args.out / f'inventory-{args.source}.csv'}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
