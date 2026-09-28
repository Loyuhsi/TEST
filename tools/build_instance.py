"""Create/refresh the portable MO2 instance D:\\PM and its profile from the manifest.

建立可攜式 MO2 實例 D:\\PM 與設定檔：ModOrganizer.ini、modlist/plugins、佔位資料夾、備份。

Subcommands (all dry-run unless --apply; close MO2 first):
    python tools\\build_instance.py create --pm D:\\PM --ini-from "D:\\Nolvus\\Instances\\Nolvus Awakening\\MODS\\profiles\\Nolvus Awakening"
    python tools\\build_instance.py verify --pm D:\\PM          (after the first MO2 start: did MO2 drop lines?)
    python tools\\build_instance.py set-language --pm D:\\PM [--language CHINESE] [--apply]
        (phase 6: set sLanguage in the profile's Skyrim.ini; create --ini-from keeps it afterwards)
    python tools\\build_instance.py sync-order --pm D:\\PM      (after generating outputs: restore target plugin order;
                                                             patches whose masters sit below them move down)

Why placeholders: MO2 silently deletes modlist.txt lines whose folder does not exist,
so every target folder gets an (empty) folder before MO2 first opens the profile.
"""

from __future__ import annotations

import argparse
import datetime as dt
import heapq
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
    "pandora behaviour engine+.exe": "Pandora", "pandora behaviour engine.exe": "Pandora",
    "synthesis.exe": "Synthesis", "bethini.exe": "BethINI Pie",
}
GENERATED_TAIL = ["FNIS.esp", "Synthesis.esp", "PG_1.esp", "PG_2.esp", "DynDOLOD.esp", "Occlusion.esp"]
OPENSSL_DLLS = ("libssl-3-x64.dll", "libcrypto-3-x64.dll")


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


def ini_value(text: str, section: str, key: str) -> str | None:
    cur = ""
    for line in text.splitlines():
        t = line.strip()
        if t.startswith("[") and t.endswith("]"):
            cur = t[1:-1].strip().lower()
        elif cur == section.lower() and "=" in t and t.split("=", 1)[0].strip().lower() == key.lower():
            return t.split("=", 1)[1].strip()
    return None


def set_ini_value(text: str, section: str, key: str, value: str) -> str:
    """Replace key in [section] (or add it right after the section header, or add the section)."""
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    cur, header = "", None
    for i, line in enumerate(lines):
        t = line.strip()
        if t.startswith("[") and t.endswith("]"):
            cur = t[1:-1].strip().lower()
            if cur == section.lower() and header is None:
                header = i
        elif cur == section.lower() and "=" in t and t.split("=", 1)[0].strip().lower() == key.lower():
            lines[i] = f"{line.split('=', 1)[0]}={value}"
            return nl.join(lines) + nl
    if header is None:
        lines = [f"[{section}]", f"{key}={value}", *lines]
    else:
        lines.insert(header + 1, f"{key}={value}")
    return nl.join(lines) + nl


def read_ini(path: Path) -> str:
    return path.read_bytes().decode("latin-1")          # byte-exact round trip for ANSI ini files


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
    skyrim_ini = pdir / "Skyrim.ini"
    language = ini_value(read_ini(skyrim_ini), "General", "sLanguage") if skyrim_ini.exists() else None
    if args.ini_from:
        for name in PROFILE_INIS:
            src = next((p for p in Path(args.ini_from).glob("*") if p.name.lower() == name.lower()), None)
            if src:
                copied.append(name)
                if apply:
                    shutil.copy2(src, pdir / name)
    if language and "Skyrim.ini" in copied:
        # the ini comes from Nolvus (English); keep the language this profile was switched to
        if apply and skyrim_ini.exists():
            text = read_ini(skyrim_ini)
            if ini_value(text, "General", "sLanguage") != language:
                skyrim_ini.write_bytes(set_ini_value(text, "General", "sLanguage", language).encode("latin-1"))
        rep.add("language", "INFO", "遊戲語言", f"沿用設定檔原本的 sLanguage={language}")
    # MO2 keeps libssl in dlls\; without a copy next to the exe, Windows may load an
    # incompatible libssl from PATH (miniconda, Git) and MO2 fails to start.
    ssl = [n for n in OPENSSL_DLLS if (pm / "dlls" / n).exists() and not (pm / n).exists()]
    if ssl:
        if apply:
            for n in ssl:
                shutil.copy2(pm / "dlls" / n, pm / n)
        rep.add("openssl", "PASS", "OpenSSL DLL", f"複製 {', '.join(ssl)} 到 D:\\PM 根目錄（避免載入 PATH 上的其他版本）")
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


def cmd_set_language(args, rep: Report) -> None:
    pdir = args.pm / "profiles" / args.profile
    path = pdir / "Skyrim.ini"
    if not path.exists():
        rep.add("ini", "FAIL", "找不到設定檔的 Skyrim.ini", str(path))
        return
    text = read_ini(path)
    current = ini_value(text, "General", "sLanguage")
    if current == args.language:
        rep.add("language", "PASS", "遊戲語言", f"已經是 sLanguage={args.language}")
    else:
        bdir = backup([path], pdir, args.apply)
        if args.apply:
            path.write_bytes(set_ini_value(text, "General", "sLanguage", args.language).encode("latin-1"))
        rep.add("language", "PASS" if args.apply else "INFO", "遊戲語言",
                f"sLanguage：{current or '（未設定）'} → {args.language}" + (f"；備份 {bdir}" if args.apply else "（試跑）"))
    archives = ini_value(text, "Archive", "sResourceArchiveList2") or ""
    if "voices_en0" in archives.lower():
        rep.add("voices", "PASS", "英文語音", "sResourceArchiveList2 仍有 Skyrim - Voices_en0.bsa（官方繁中沒有配音）")
    else:
        rep.add("voices", "WARN", "英文語音", "Skyrim.ini 的 sResourceArchiveList2 沒有 Skyrim - Voices_en0.bsa，"
                "遊戲可能沒有語音；停下回報")


def cmd_verify(args, rep: Report) -> None:
    pdir = args.pm / "profiles" / args.profile
    exp = pdir / "_expected"
    if not exp.exists():
        rep.add("exp", "FAIL", "找不到 _expected", "請先執行 create --apply")
        return
    want = [e.name for e in mo2.read_modlist(exp / "modlist.txt")]
    current = mo2.read_modlist(pdir / "modlist.txt")
    have = {mo2.fold(e.name) for e in current}
    lost = [n for n in want if mo2.fold(n) not in have]
    rep.add("modlist", "PASS" if not lost else "FAIL", "modlist.txt 與預期比對",
            "一致" if not lost else f"MO2 移除了 {len(lost)} 行，例如：{', '.join(lost[:5])}")
    wanted = {mo2.fold(n) for n in want}
    extra = [e.name for e in current if not e.is_separator and mo2.fold(e.name) not in wanted]
    if extra:
        rep.add("extra", "INFO", "清單外的資料夾", f"{len(extra)} 個：{', '.join(extra[:10])}")
    # a target plugin counts as missing when it is not enabled, whether or not MO2 kept its line
    wantp = [p.name for p in mo2.read_plugins(exp / "plugins.txt") if p.enabled]
    havep = {p.name.lower() for p in mo2.read_plugins(pdir / "plugins.txt") if p.enabled}
    lostp = [n for n in wantp if n.lower() not in havep]
    pending = [n for n in lostp if n in vfs.GENERATED_PLUGINS]
    other = [n for n in lostp if n not in vfs.GENERATED_PLUGINS]
    rep.add("plugins", "PASS" if not other else "WARN", "plugins.txt 與預期比對",
            f"缺少或未啟用 {len(other)} 個（mod 尚未安裝或已被修剪）；待重建輸出 {len(pending)} 個"
            + (f"；例如：{', '.join(other[:5])}" if other else ""))
    rep.data = {"lost_mods": lost, "lost_plugins": other, "pending_generated": pending, "extra_mods": extra}


def restore_states(current: dict[str, mo2.PluginEntry], expected: list[mo2.PluginEntry],
                   providers: dict[str, Path]) -> tuple[dict[str, mo2.PluginEntry], list[str], list[str], list[str]]:
    """Put back the target's enabled flags for expected plugins that an enabled mod provides.

    MO2 lists plugins it has not seen before as disabled, so every plugin installed after the
    profile was created starts out off. Returns (new current map, switched on, switched off,
    skipped because no enabled mod has the file).
    """
    out = dict(current)
    on: list[str] = []
    off: list[str] = []
    skipped: list[str] = []
    for e in expected:
        key = e.name.lower()
        if key not in providers:
            skipped.append(e.name)
            continue
        cur = out.get(key)
        if cur is not None and cur.enabled == e.enabled:
            continue
        if e.enabled:
            on.append(e.name)
        elif cur is not None:
            off.append(e.name)
        out[key] = mo2.PluginEntry(cur.name if cur is not None else e.name, e.enabled)
    return out, on, off, skipped


def order_after_masters(names: list[str], masters: dict[str, list[str]]) -> tuple[list[str], list[str], list[str]]:
    """Reorder so every plugin loads after the masters that are in the same list.

    A plugin keeps its place unless one of its masters sits below it; then it (and anything
    that needs it) moves down to just after its last master. Everything else keeps its
    relative order. masters maps lower-case names to master lists. Returns (new order,
    plugins that moved, plugins left in a master cycle).
    """
    idx = {n.lower(): i for i, n in enumerate(names)}
    waiting = {k: {m.lower() for m in masters.get(k, ()) if m.lower() in idx and m.lower() != k} for k in idx}
    children: dict[str, list[str]] = {}
    for k, ms in waiting.items():
        for m in ms:
            children.setdefault(m, []).append(k)
    ready = [idx[k] for k, ms in waiting.items() if not ms]
    heapq.heapify(ready)
    out: list[str] = []
    moved: list[str] = []
    top = -1
    while ready:
        i = heapq.heappop(ready)
        if i < top:
            moved.append(names[i])
        top = max(top, i)
        out.append(names[i])
        for c in children.get(names[i].lower(), ()):
            waiting[c].discard(names[i].lower())
            if not waiting[c]:
                heapq.heappush(ready, idx[c])
    done = {n.lower() for n in out}
    cycle = [n for n in names if n.lower() not in done]
    return out + cycle, moved, cycle


def cmd_sync_order(args, rep: Report) -> None:
    prof = vfs.open_profile(args.pm, args.profile)
    expected = prof.profile_dir / "_expected" / "plugins.txt"
    if args.restore_states and not expected.exists():
        # the raw target list still holds plugins of dropped mods; only _expected is filtered
        rep.add("states", "FAIL", "啟用狀態", f"找不到 {expected}，沒有處理；請先執行 create --apply")
        return
    ref_entries = mo2.read_plugins(expected if expected.exists() else args.target_plugins)
    rank = {p.name.lower(): i for i, p in enumerate(ref_entries)}
    current = {p.name.lower(): p for p in prof.plugins}
    providers = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, prof.game_dir / "Data")
    # regenerated outputs belong enabled; MO2 lists a plugin it has not seen before as disabled
    outputs_on = []
    for g in sorted(vfs.GENERATED_PLUGINS):
        key = g.lower()
        if key in providers and not (key in current and current[key].enabled):
            current[key] = mo2.PluginEntry(current[key].name if key in current else g, True)
            outputs_on.append(g)
    if args.restore_states:
        current, on, off, skipped = restore_states(current, ref_entries, providers)
        rep.add("states", "WARN" if off else "PASS", "啟用狀態",
                f"依目標啟用 {len(on)} 個、停用 {len(off)} 個；檔案不在已啟用的 mod 或遊戲資料夾裡，"
                f"略過 {len(skipped)} 個（之後要再跑 prune_dependents）")
        if off:
            rep.add("states_off", "INFO", "依目標改為停用", ", ".join(off[:15]))
    known = sorted((p for k, p in current.items() if k in rank), key=lambda p: rank[p.name.lower()])
    unknown = [p for k, p in current.items() if k not in rank]
    tail_idx = next((i for i, p in enumerate(known) if p.name in GENERATED_TAIL), len(known))
    ordered = known[:tail_idx] + unknown + known[tail_idx:]
    headers: dict[str, tes4.PluginHeader | None] = {}

    def header(p):
        key = p.name.lower()
        if key not in headers:
            path = providers.get(key)
            try:
                headers[key] = tes4.read_header(path) if path else None
            except (tes4.PluginError, OSError):
                headers[key] = None
        return headers[key]

    # masters (ESM-flagged, .esm/.esl) must come first, as MO2/the game enforce
    def is_master(p):
        h = header(p)
        return h.is_master if h else p.name.lower().endswith((".esm", ".esl"))
    groups = [[p for p in ordered if is_master(p)], [p for p in ordered if not is_master(p)]]
    # newer patch versions can need masters the target lists below them: move those patches down
    masters = {p.name.lower(): (header(p).masters if header(p) else []) for p in ordered}
    by_name = {p.name.lower(): p for p in ordered}
    moved: list[str] = []
    cycles: list[str] = []
    for i, group in enumerate(groups):
        names, mv, cyc = order_after_masters([p.name for p in group], masters)
        groups[i] = [by_name[n.lower()] for n in names]
        moved += mv
        cycles += cyc
    plain = {p.name.lower() for p in groups[1]}
    stuck = [p.name for p in groups[0] if any(m.lower() in plain for m in masters[p.name.lower()])]
    ordered = groups[0] + groups[1]
    files = [prof.profile_dir / "plugins.txt", prof.profile_dir / "loadorder.txt"]
    bdir = backup(files, prof.profile_dir, args.apply)
    if args.apply:
        mo2.write_plugins(prof.profile_dir / "plugins.txt", ordered)
        if (prof.profile_dir / "loadorder.txt").exists():
            (prof.profile_dir / "loadorder.txt").unlink()
    rep.add("order", "PASS", "插件順序", f"{len(ordered)} 個：依目標順序 {len(known)}，新增的 {len(unknown)} 個放在輸出插件之前")
    rep.add("masters", "PASS", "前置順序",
            f"移動 {len(moved)} 個插件到它的前置之後" + (f"，例如：{', '.join(moved[:10])}" if moved else ""))
    if stuck:
        rep.add("masters_esm", "WARN", "ESM 插件以一般插件為前置",
                f"{len(stuck)} 個（遊戲一定先載入 ESM，排序修不了）：{', '.join(stuck[:10])}")
    if cycles:
        rep.add("masters_cycle", "WARN", "前置互相依賴（循環）", f"{len(cycles)} 個，維持原順序：{', '.join(cycles[:10])}")
    rep.data = {"moved": moved, "esm_needs_plain": stuck, "cycles": cycles}
    if outputs_on:
        rep.add("outputs", "INFO", "啟用重建出來的輸出插件", ", ".join(outputs_on))
    if unknown:
        rep.add("unknown", "INFO", "不在目標清單中的插件", ", ".join(p.name for p in unknown[:15]))
    if bdir:
        rep.add("backup", "INFO", "備份", str(bdir))


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="建立／檢查 D:\\PM 實例（預設試跑，加 --apply 才寫入；請先關閉 MO2）")
    ap.add_argument("command", choices=["create", "verify", "sync-order", "set-language"])
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default=DEFAULT_PROFILE)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_REPORT_DIR / "manifest.csv")
    ap.add_argument("--target", type=Path, default=DATA / "target" / "modlist.txt")
    ap.add_argument("--target-plugins", type=Path, default=DATA / "target" / "plugins.txt")
    ap.add_argument("--ini-from", type=Path, default=None, help="複製 Skyrim.ini 等的來源設定檔資料夾（Nolvus）")
    ap.add_argument("--rewrite-ini", action="store_true", help="重寫已存在的 ModOrganizer.ini（會先備份）")
    ap.add_argument("--restore-states", action="store_true",
                    help="sync-order：依 _expected 還原插件的啟用狀態（MO2 會把新裝的插件列為停用）；"
                         "只處理檔案已在的插件，之後要再跑 prune_dependents")
    ap.add_argument("--language", default="CHINESE", help="set-language：Skyrim.ini 的 sLanguage（預設 CHINESE）")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    rep = Report(f"build_instance-{args.command}")
    rep.add("mode", "INFO", "模式", "實際執行" if args.apply else "試跑（加 --apply 才會寫入）")
    {"create": cmd_create, "verify": cmd_verify, "sync-order": cmd_sync_order,
     "set-language": cmd_set_language}[args.command](args, rep)
    path = rep.save(args.out, stem=f"build_instance-{args.command}")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
