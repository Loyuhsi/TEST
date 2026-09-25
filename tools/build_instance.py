"""Create/refresh the portable MO2 instance D:\\PM and its profile from the manifest.

建立可攜式 MO2 實例 D:\\PM 與設定檔：ModOrganizer.ini、modlist/plugins、佔位資料夾、備份。

Subcommands (all dry-run unless --apply; close MO2 first):
    python tools\\build_instance.py create --pm D:\\PM --ini-from "D:\\Nolvus\\Instances\\Nolvus Awakening\\MODS\\profiles\\Nolvus Awakening"
    python tools\\build_instance.py verify --pm D:\\PM          (after the first MO2 start: did MO2 drop lines?)
    python tools\\build_instance.py sync-order --pm D:\\PM      (after generating outputs: restore target plugin order)

Why placeholders: MO2 silently deletes modlist.txt lines whose folder does not exist,
so every target folder gets an (empty) folder before MO2 first opens the profile.
"""

from __future__ import annotations

import argparse
import datetime as dt
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, mo2, tes4, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, REPO_ROOT, Report, read_csv  # noqa: E402

DATA = REPO_ROOT / "data"
DEFAULT_PROFILE = "Pages-ZH"
PROFILE_INIS = ("Skyrim.ini", "SkyrimPrefs.ini", "SkyrimCustom.ini")
SEPARATOR_META = "[General]\nmodid=0\nversion=\nnewestVersion=\ncategory=0\ninstallationFile=\n"
KNOWN_TOOLS = {  # exe name (lower) -> MO2 title
    "sseedit.exe": "SSEEdit", "sseedit64.exe": "SSEEdit",
    "sseeditquickautoclean.exe": "SSEEdit QuickAutoClean",
    "dyndolodx64.exe": "DynDOLOD", "texgenx64.exe": "TexGen", "xlodgenx64.exe": "xLODGen",
    "pgpatcher.exe": "PGPatcher", "bodyslide x64.exe": "BodySlide",
    "pandora behaviour engine+.exe": "Pandora", "synthesis.exe": "Synthesis", "bethini.exe": "BethINI Pie",
}
GENERATED_TAIL = ["FNIS.esp", "Synthesis.esp", "PG_1.esp", "PG_2.esp", "DynDOLOD.esp", "Occlusion.esp"]


def backup(files: list[Path], profile_dir: Path, apply: bool) -> Path | None:
    existing = [f for f in files if f.exists()]
    if not existing:
        return None
    dest = profile_dir / "_backup" / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    if apply:
        dest.mkdir(parents=True, exist_ok=True)
        for f in existing:
            shutil.copy2(f, dest / f.name)
    return dest


def find_tools(pm: Path, max_depth: int = 5) -> list[tuple[str, Path]]:
    found: dict[str, Path] = {}
    for base in (pm / "tools", pm / "mods"):
        if not base.is_dir():
            continue
        stack = [(base, 0)]
        while stack:
            d, depth = stack.pop()
            try:
                entries = list(d.iterdir())
            except OSError:
                continue
            for p in entries:
                if p.is_dir() and depth < max_depth:
                    stack.append((p, depth + 1))
                elif p.is_file() and p.name.lower() in KNOWN_TOOLS:
                    found.setdefault(KNOWN_TOOLS[p.name.lower()], p)
    return sorted(found.items())


def mo2_ini_text(pm: Path, game_dir: Path, profile: str, tools: list[tuple[str, Path]]) -> str:
    exes = [("SKSE", game_dir / "skse64_loader.exe")] + tools
    lines = ["[General]", "gameName=Skyrim Special Edition", "game_edition=Steam",
             f"gamePath={mo2.qt_bytearray(str(game_dir))}", f"selected_profile={mo2.qt_bytearray(profile)}",
             "first_start=false", "", "[customExecutables]", f"size={len(exes)}"]
    for i, (title, exe) in enumerate(exes, start=1):
        fwd = str(exe).replace("\\", "/")
        lines += [f"{i}\\title={title}", f"{i}\\binary={fwd}", f"{i}\\arguments=",
                  f"{i}\\workingDirectory={str(exe.parent).replace(chr(92), '/')}", f"{i}\\ownicon=true",
                  f"{i}\\steamAppID=", f"{i}\\toolbar=false", f"{i}\\hide=false"]
    lines += ["", "[Settings]", "", "[Plugins]", ""]
    return "\r\n".join(lines)


def target_plan(manifest: Path | None) -> dict[str, str]:
    if manifest and manifest.exists():
        return {mo2.fold(r["folder"]): r["action"] for r in read_csv(manifest)}
    prov = DATA / "analysis" / "provenance.csv"
    return {mo2.fold(r["folder"]): r["action"] for r in read_csv(prov)} if prov.exists() else {}


def dropped_plugins() -> set[str]:
    p = DATA / "analysis" / "drop_list.csv"
    if not p.exists():
        return set()
    return {r["name"].lower() for r in read_csv(p) if r.get("kind") == "plugin"}


def cmd_create(args, rep: Report) -> None:
    pm: Path = args.pm
    apply = args.apply
    game = pm / "STOCK GAME"
    if not (pm / "ModOrganizer.exe").exists():
        rep.add("mo2", "FAIL", "D:\\PM 沒有 ModOrganizer.exe", "請先執行 harvest.py --from mv --mo2-and-tools --apply")
    if not (game / "SkyrimSE.exe").exists():
        rep.add("game", "FAIL", "D:\\PM\\STOCK GAME 沒有 SkyrimSE.exe", "請先執行 harvest.py --from nolvus --stock-game --apply")
    plan = target_plan(args.manifest)
    target = mo2.read_modlist(args.target)
    keep = [e for e in target if e.is_separator or plan.get(mo2.fold(e.name), "keep") != "drop"]
    dropped = len(target) - len(keep)
    mods = pm / "mods"
    placeholders = []
    for e in keep:
        d = mods / e.name
        if not d.exists():
            placeholders.append(e.name)
            if apply:
                d.mkdir(parents=True, exist_ok=True)
                if e.is_separator:
                    (d / "meta.ini").write_text(SEPARATOR_META, encoding="utf-8")
    pdir = pm / "profiles" / args.profile
    files = [pdir / n for n in ("modlist.txt", "plugins.txt", "loadorder.txt", "settings.ini", *PROFILE_INIS)]
    bdir = backup(files + [pm / "ModOrganizer.ini"], pdir, apply)
    drop_pl = dropped_plugins()
    all_plugins = mo2.read_plugins(args.target_plugins)
    plugins = [p for p in all_plugins if p.name.lower() not in drop_pl]
    if apply:
        pdir.mkdir(parents=True, exist_ok=True)
        mo2.write_modlist(pdir / "modlist.txt", keep)
        mo2.write_plugins(pdir / "plugins.txt", plugins)
        if (pdir / "loadorder.txt").exists():
            (pdir / "loadorder.txt").unlink()
        (pdir / "settings.ini").write_text("[General]\r\nLocalSaves=true\r\nLocalSettings=true\r\n"
                                           "AutomaticArchiveInvalidation=false\r\n", encoding="utf-8")
        exp = pdir / "_expected"
        exp.mkdir(exist_ok=True)
        mo2.write_modlist(exp / "modlist.txt", keep)
        mo2.write_plugins(exp / "plugins.txt", plugins)
        (pm / "portable.txt").touch()
    copied = []
    if args.ini_from:
        for name in PROFILE_INIS:
            src = next((p for p in Path(args.ini_from).glob("*") if p.name.lower() == name.lower()), None)
            if src:
                copied.append(name)
                if apply:
                    shutil.copy2(src, pdir / name)
    ini = pm / "ModOrganizer.ini"
    tools = find_tools(pm)
    if not ini.exists() or args.rewrite_ini:
        if apply:
            ini.write_text(mo2_ini_text(pm, game, args.profile, tools), encoding="utf-8")
        rep.add("ini", "PASS", "ModOrganizer.ini", f"寫入：遊戲路徑 {game}，工具 {', '.join(t for t, _ in tools) or '無'}")
    else:
        rep.add("ini", "INFO", "ModOrganizer.ini", "已存在，保留（要重寫請加 --rewrite-ini）")
    rep.add("profile", "PASS", f"設定檔 {args.profile}",
            f"modlist {len(keep)} 行（捨棄 {dropped}），plugins {len(plugins)} 個（排除 {len(all_plugins) - len(plugins)} 個自製插件）")
    rep.add("placeholders", "INFO", "佔位資料夾", f"{len(placeholders)} 個（之後用 MO2 安裝到同名資料夾並選 Replace）")
    rep.add("inis", "PASS" if copied else "WARN", "遊戲 ini", ", ".join(copied) if copied else
            "未指定 --ini-from：請從 Nolvus 設定檔複製 Skyrim.ini / SkyrimPrefs.ini")
    if bdir:
        rep.add("backup", "INFO", "備份", str(bdir))
    rep.data = {"placeholders": placeholders}


def cmd_verify(args, rep: Report) -> None:
    pdir = args.pm / "profiles" / args.profile
    exp = pdir / "_expected"
    if not exp.exists():
        rep.add("exp", "FAIL", "找不到 _expected", "請先執行 create --apply")
        return
    want = [e.name for e in mo2.read_modlist(exp / "modlist.txt")]
    have = {mo2.fold(e.name) for e in mo2.read_modlist(pdir / "modlist.txt")}
    lost = [n for n in want if mo2.fold(n) not in have]
    rep.add("modlist", "PASS" if not lost else "FAIL", "modlist.txt 與預期比對",
            "一致" if not lost else f"MO2 移除了 {len(lost)} 行，例如：{', '.join(lost[:5])}")
    wantp = [p.name for p in mo2.read_plugins(exp / "plugins.txt")]
    havep = {p.name.lower() for p in mo2.read_plugins(pdir / "plugins.txt")}
    lostp = [n for n in wantp if n.lower() not in havep]
    pending = [n for n in lostp if n in vfs.GENERATED_PLUGINS]
    other = [n for n in lostp if n not in vfs.GENERATED_PLUGINS]
    rep.add("plugins", "PASS" if not other else "WARN", "plugins.txt 與預期比對",
            f"缺少 {len(other)} 個（mod 尚未安裝或已被修剪）；待重建輸出 {len(pending)} 個"
            + (f"；例如：{', '.join(other[:5])}" if other else ""))
    rep.data = {"lost_mods": lost, "lost_plugins": other, "pending_generated": pending}


def cmd_sync_order(args, rep: Report) -> None:
    prof = vfs.open_profile(args.pm, args.profile)
    ref = [p.name for p in mo2.read_plugins(prof.profile_dir / "_expected" / "plugins.txt")] \
        if (prof.profile_dir / "_expected" / "plugins.txt").exists() else \
        [p.name for p in mo2.read_plugins(args.target_plugins)]
    rank = {n.lower(): i for i, n in enumerate(ref)}
    current = {p.name.lower(): p for p in prof.plugins}
    providers = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, None)
    for g in vfs.GENERATED_PLUGINS:
        if g.lower() in providers and g.lower() not in current:
            current[g.lower()] = mo2.PluginEntry(g, True)
    known = sorted((p for k, p in current.items() if k in rank), key=lambda p: rank[p.name.lower()])
    unknown = [p for k, p in current.items() if k not in rank]
    tail_idx = next((i for i, p in enumerate(known) if p.name in GENERATED_TAIL), len(known))
    ordered = known[:tail_idx] + unknown + known[tail_idx:]
    # masters (ESM/ESL-flagged) must come first, as MO2/the game enforce
    def is_master(p):
        path = providers.get(p.name.lower())
        try:
            return tes4.read_header(path).is_master if path else p.name.lower().endswith((".esm", ".esl"))
        except (tes4.PluginError, OSError):
            return p.name.lower().endswith((".esm", ".esl"))
    ordered = [p for p in ordered if is_master(p)] + [p for p in ordered if not is_master(p)]
    files = [prof.profile_dir / "plugins.txt", prof.profile_dir / "loadorder.txt"]
    bdir = backup(files, prof.profile_dir, args.apply)
    if args.apply:
        mo2.write_plugins(prof.profile_dir / "plugins.txt", ordered)
        if (prof.profile_dir / "loadorder.txt").exists():
            (prof.profile_dir / "loadorder.txt").unlink()
    rep.add("order", "PASS", "插件順序", f"{len(ordered)} 個：依目標順序 {len(known)}，新增的 {len(unknown)} 個放在輸出插件之前")
    if unknown:
        rep.add("unknown", "INFO", "不在目標清單中的插件", ", ".join(p.name for p in unknown[:15]))
    if bdir:
        rep.add("backup", "INFO", "備份", str(bdir))


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="建立／檢查 D:\\PM 實例（預設試跑，加 --apply 才寫入；請先關閉 MO2）")
    ap.add_argument("command", choices=["create", "verify", "sync-order"])
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default=DEFAULT_PROFILE)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_REPORT_DIR / "manifest.csv")
    ap.add_argument("--target", type=Path, default=DATA / "target" / "modlist.txt")
    ap.add_argument("--target-plugins", type=Path, default=DATA / "target" / "plugins.txt")
    ap.add_argument("--ini-from", type=Path, default=None, help="複製 Skyrim.ini 等的來源設定檔資料夾（Nolvus）")
    ap.add_argument("--rewrite-ini", action="store_true", help="重寫已存在的 ModOrganizer.ini（會先備份）")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    rep = Report(f"build_instance-{args.command}")
    rep.add("mode", "INFO", "模式", "實際執行" if args.apply else "試跑（加 --apply 才會寫入）")
    {"create": cmd_create, "verify": cmd_verify, "sync-order": cmd_sync_order}[args.command](args, rep)
    path = rep.save(args.out, stem=f"build_instance-{args.command}")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
