"""Phase 4: put target plugins that are missing on disk into their target folders.

補齊缺少的目標插件：目標 plugins.txt 有、但 D:\\PM 找不到檔案的插件，從 M&V／Nolvus 的安裝或
已下載的壓縮檔放進對應的資料夾（多半是補丁合集的 FOMOD 選項比我們擷取的那份多）。

Usage (Windows; close MO2 first; dry run unless --apply):
    python tools\\fill_plugins.py --pm D:\\PM --mv D:\\MV --nolvus "D:\\Nolvus\\Instances\\Nolvus Awakening"
    python tools\\fill_plugins.py ... --apply
    python tools\\fill_plugins.py ... --plan-downloads
    python tools\\nexus_fetch.py --pm D:\\PM --manifest reports\\fill_plugins_downloads.csv --apply
Sources, tried in order for each missing plugin:
  1. installed M&V / Nolvus mod folders: the plugin and its same-stem .bsa files are hardlinked;
     a data/plugin_sources.csv row with mode "whole" merges the entire source folder instead;
  2. archives in <pm>\\downloads: 7-Zip extracts only the needed files.
Destination: a data/plugin_sources.csv row, else the target folder named like the source folder
(also MO2 "Name2" duplicates); for archives, the folder whose Nexus IDs match the archive's .meta
(data/extra_archives.csv first, then reports\\manifest.csv).
Plugins with no source get candidate folders; --plan-downloads writes those folders' own Nexus
archives to reports\\fill_plugins_downloads.csv (manifest format) for nexus_fetch.
Never overwrites or deletes files and never creates mod folders.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import install_archives  # noqa: E402
from pm import fsutil, mo2, sevenzip, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, REPO_ROOT, Report, read_csv, write_csv  # noqa: E402

DATA = REPO_ROOT / "data"
ARCHIVE_EXT = (".7z", ".zip", ".rar")
STAGING_DIR = "_fill_staging"
FIELDS = ["plugin", "status", "source", "source_folder", "archive", "member", "dest", "candidates", "note"]
DL_FIELDS = ["folder", "action", "nexus_mod_id", "nexus_file_id", "nexus_version", "url", "note"]
STOP = {"patch", "patches", "collection", "hub", "the", "of", "and", "for", "a", "an", "se", "ae", "aio",
        "addon", "addons", "official", "unofficial", "fix", "fixes", "version", "s", "esp", "esm", "esl"}
STATUS_TEXT = {
    "install": "從 M&V／Nolvus 安裝補上（硬連結）",
    "whole": "整個來源資料夾合併（whole）",
    "archive": "從壓縮檔取出",
    "ambiguous": "不明確（見 csv 的 note）",
    "unresolved": "找不到來源",
}


# ---------------------------------------------------------------- seams (replaced in tests)
def list_files(archive: Path) -> list[sevenzip.Entry]:
    return [e for e in sevenzip.list_entries(archive) if not e.is_dir]


def extract_files(archive: Path, dest: Path, members: list[str]) -> None:
    sevenzip.extract_files(archive, dest, members)


def mo2_running() -> bool:
    return install_archives.mo2_running()


# ---------------------------------------------------------------- helpers
def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower().replace("'", ""))
    return {w for w in words if w not in STOP}


def plugin_prefix(plugin: str) -> str:
    stem = Path(plugin).stem
    if " - " in stem:
        return stem.split(" - ", 1)[0]
    return re.split(r"[_\-]", stem, maxsplit=1)[0]


def is_plugin(name: str) -> bool:
    return name.lower().endswith(vfs.PLUGIN_EXT)


def same_stem_archives(names: list[str], plugin: str) -> list[str]:
    """Companion BSAs of a plugin: 'X.bsa' and 'X - Textures.bsa' style names."""
    stem = Path(plugin).stem.lower()
    return [n for n in names if n.lower().endswith(".bsa")
            and (Path(n).stem.lower() == stem or Path(n).stem.lower().startswith(stem + " - "))]


@dataclass
class Mapping:
    sources: dict[tuple[str, str], tuple[str, str]] = field(default_factory=dict)  # (label, fold) -> (target, mode)
    prefixes: list[tuple[str, list[str]]] = field(default_factory=list)            # (folded prefix, targets)

    def prefix_targets(self, plugin: str) -> list[str]:
        name = mo2.fold(plugin)
        best = max((p for p in self.prefixes if name.startswith(p[0])), key=lambda p: len(p[0]), default=None)
        return best[1] if best else []


def load_mapping(path: Path) -> Mapping:
    m = Mapping()
    for r in read_csv(path) if path.exists() else []:
        kind = (r.get("kind") or "").strip()
        targets = [t.strip() for t in (r.get("target") or "").split("|") if t.strip()]
        if kind == "source" and targets:
            key = ((r.get("source") or "*").strip().lower(), mo2.fold(r.get("match") or ""))
            m.sources[key] = (targets[0], (r.get("mode") or "plugins").strip().lower())
        elif kind == "prefix" and targets:
            m.prefixes.append((mo2.fold(r.get("match") or ""), targets))
    return m


# ---------------------------------------------------------------- inputs
@dataclass
class World:
    mods_dir: Path
    folders: list[str]                                   # enabled target folders, priority order
    by_fold: dict[str, str]
    missing: list[str]
    installs: dict[str, list[tuple[str, Path]]]          # plugin lower -> [(label, source folder path)]
    archives: dict[str, list[tuple[Path, str, int]]]     # plugin lower -> [(archive, member, size)]
    members: dict[Path, list[str]]                       # archive -> all member paths
    archive_ids: dict[Path, tuple[str, str]]             # archive -> (mod, file)
    id_folders: dict[tuple[str, str], list[str]]         # (mod, file) -> folders (extra first)
    mod_folders: dict[str, list[str]]                    # mod -> folders
    folder_ids: dict[str, tuple[str, str, str]]          # fold(folder) -> (mod, file, version)
    dropped: set[str]                                    # fold(folder) with action drop
    mapping: Mapping
    siblings: dict[str, Counter] = field(default_factory=dict)  # fold(prefix) -> folders holding such plugins


def missing_plugins(prof: vfs.Profile) -> tuple[list[str], dict[str, Counter]]:
    """Missing target plugins, plus which folders already hold plugins of each name prefix."""
    exp = prof.profile_dir / "_expected" / "plugins.txt"
    if not exp.exists():
        raise FileNotFoundError(f"找不到 {exp}（請先執行 build_instance.py create --apply）")
    present = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, prof.game_dir / "Data")
    generated = {g.lower() for g in vfs.GENERATED_PLUGINS}
    siblings: dict[str, Counter] = defaultdict(Counter)
    for path in present.values():
        if path.parent.parent == prof.mods_dir:
            siblings[mo2.fold(plugin_prefix(path.name))][path.parent.name] += 1
    missing = [p.name for p in mo2.read_plugins(exp)
               if p.enabled and p.name.lower() not in present and p.name.lower() not in generated]
    return missing, dict(siblings)


def index_installs(sources: list[tuple[str, Path]]) -> dict[str, list[tuple[str, Path]]]:
    idx: dict[str, list[tuple[str, Path]]] = defaultdict(list)
    for label, inst in sources:
        mods = mo2.locate_instance(inst)["mods"]
        if not mods.is_dir():
            continue
        for e in sorted(os.scandir(mods), key=lambda e: e.name.lower()):
            if e.is_dir():
                for name in vfs.root_plugins(Path(e.path)):
                    idx[name.lower()].append((label, Path(e.path)))
    return idx


def index_archives(dl_dir: Path, cache_path: Path) -> tuple[dict, dict, dict]:
    cache: dict = {}
    if cache_path.exists():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cache = {}
    plugins: dict[str, list[tuple[Path, str, int]]] = defaultdict(list)
    members: dict[Path, list[str]] = {}
    ids: dict[Path, tuple[str, str]] = {}
    fresh: dict = {}
    for a in sorted(dl_dir.glob("*")) if dl_dir.is_dir() else []:
        if not a.is_file() or a.suffix.lower() not in ARCHIVE_EXT:
            continue
        meta = install_archives.read_download_meta(Path(str(a) + ".meta")) if Path(str(a) + ".meta").exists() else {}
        ids[a] = ((meta.get("modid") or "").strip(), (meta.get("fileid") or "").strip())
        st = a.stat()
        key = f"{a.name}|{st.st_size}|{st.st_mtime_ns}"
        entries = cache.get(key)
        if entries is None:
            try:
                entries = [[e.path, e.size] for e in list_files(a)
                           if is_plugin(e.path) or e.path.lower().endswith(".bsa")]
            except sevenzip.SevenZipError:
                entries = []
        fresh[key] = entries
        members[a] = [p for p, _ in entries]
        for path, size in entries:
            name = path.rsplit("/", 1)[-1]
            if is_plugin(name):
                plugins[name.lower()].append((a, path, size))
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(fresh, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
    return plugins, members, ids


def load_world(args: argparse.Namespace) -> World:
    prof = vfs.open_profile(args.pm, args.profile)
    folders = prof.enabled_folders
    missing, siblings = missing_plugins(prof)
    srcs = [(label, Path(p)) for label, p in (("nolvus", args.nolvus), ("mv", args.mv)) if p]
    installs = index_installs(srcs)
    arch, members, archive_ids = index_archives(args.downloads or args.pm / "downloads",
                                                args.out / "fill_plugins_cache.json")
    id_folders: dict[tuple[str, str], list[str]] = defaultdict(list)
    mod_folders: dict[str, list[str]] = defaultdict(list)
    folder_ids: dict[str, tuple[str, str, str]] = {}
    dropped: set[str] = set()
    rows = (read_csv(args.extra) if args.extra.exists() else []) + \
        (read_csv(args.manifest) if args.manifest.exists() else [])
    for r in rows:
        folder = (r.get("folder") or "").strip()
        mod, fid = (r.get("nexus_mod_id") or "").strip(), (r.get("nexus_file_id") or "").strip()
        if r.get("action") == "drop":
            dropped.add(mo2.fold(folder))
            continue
        if not folder or not mod:
            continue
        if folder not in id_folders[(mod, fid)]:
            id_folders[(mod, fid)].append(folder)
        if folder not in mod_folders[mod]:
            mod_folders[mod].append(folder)
        folder_ids.setdefault(mo2.fold(folder), (mod, fid, (r.get("nexus_version") or "").strip()))
    return World(prof.mods_dir, folders, {mo2.fold(f): f for f in folders}, missing, installs, arch, members,
                 archive_ids, dict(id_folders), dict(mod_folders), folder_ids, dropped, load_mapping(args.sources),
                 siblings)


# ---------------------------------------------------------------- planning
def install_dest(w: World, label: str, src: Path) -> tuple[str | None, str, str]:
    """(target folder, mode, how) for a source-install folder, or (None, '', reason)."""
    for key in ((label, mo2.fold(src.name)), ("*", mo2.fold(src.name))):
        if key in w.mapping.sources:
            target, mode = w.mapping.sources[key]
            if mo2.fold(target) not in w.by_fold:
                return None, "", f"plugin_sources.csv 的目的資料夾不在 modlist：{target}"
            return w.by_fold[mo2.fold(target)], mode, "mapping"
    if mo2.fold(src.name) in w.by_fold:
        return w.by_fold[mo2.fold(src.name)], "plugins", "same_name"
    dups = [f for f in w.folders if (b := mo2.strip_dup_suffix(f)) and mo2.fold(b) == mo2.fold(src.name)]
    if len(dups) == 1:
        return dups[0], "plugins", "dup_suffix"
    if dups:
        return None, "", "多個同名後綴資料夾：" + "; ".join(dups)
    return None, "", f"目標沒有對應 {label}「{src.name}」的資料夾"


def score_folders(w: World, plugin: str) -> list[str]:
    pt = tokens(plugin_prefix(plugin))
    if not pt:
        return []
    wants_patch = "patch" in plugin.lower()
    scored = []
    for f in w.folders:
        if mo2.fold(f) in w.dropped:
            continue
        ft = tokens(f)
        s = len(pt & ft) / len(pt)
        if s >= 0.5:
            bonus = 0.1 if wants_patch and re.search(r"patch|hub|collection", f, re.I) else 0.0
            scored.append((s + bonus, f))
    scored.sort(key=lambda x: -x[0])
    return [f for _, f in scored[:3]]


def sibling_folders(w: World, plugin: str) -> list[str]:
    counts = w.siblings.get(mo2.fold(plugin_prefix(plugin)), Counter())
    return [f for f, _ in counts.most_common(3) if mo2.fold(f) in w.by_fold and mo2.fold(f) not in w.dropped]


def candidates(w: World, plugin: str) -> list[str]:
    mapped = [w.by_fold[mo2.fold(t)] for t in w.mapping.prefix_targets(plugin) if mo2.fold(t) in w.by_fold]
    return mapped or sibling_folders(w, plugin) or score_folders(w, plugin)


def archive_dest(w: World, plugin: str, archive: Path) -> tuple[str | None, str]:
    mod, fid = w.archive_ids.get(archive, ("", ""))
    exact = [f for f in w.id_folders.get((mod, fid), []) if mo2.fold(f) in w.by_fold]
    same_mod = [f for f in w.mod_folders.get(mod, []) if mo2.fold(f) in w.by_fold and f not in exact]
    pool = exact + same_mod
    if not pool:
        return None, f"壓縮檔的 Nexus 編號 {mod}/{fid} 對不到 modlist 的資料夾"
    wanted = [w.by_fold[mo2.fold(t)] for t in w.mapping.prefix_targets(plugin) if mo2.fold(t) in w.by_fold]
    hit = [f for f in wanted + sibling_folders(w, plugin) if f in pool]
    if hit:
        return hit[0], ""
    scored = [f for f in score_folders(w, plugin) if f in pool]
    if scored:
        return scored[0], ""
    if len(exact) == 1:
        return exact[0], ""
    return None, "壓縮檔對應多個資料夾：" + "; ".join(pool)


def plan(w: World) -> list[dict]:
    rows = []
    for plugin in w.missing:
        row = {"plugin": plugin, "status": "unresolved", "source": "", "source_folder": "", "archive": "",
               "member": "", "dest": "", "candidates": "", "note": ""}
        notes = []
        for label, src in w.installs.get(plugin.lower(), []):
            dest, mode, how = install_dest(w, label, src)
            if dest:
                row.update(status="whole" if mode == "whole" else "install", source=label,
                           source_folder=str(src), dest=dest, note=how)
                break
            notes.append(how)
        if row["status"] == "unresolved":
            hits = w.archives.get(plugin.lower(), [])
            by_archive: dict[Path, list[tuple[str, int]]] = defaultdict(list)
            for a, member, size in hits:
                by_archive[a].append((member, size))
            for a, found in by_archive.items():
                if len({s for _, s in found}) > 1:
                    notes.append(f"{a.name} 裡有 {len(found)} 個大小不同的同名檔："
                                 + "; ".join(m for m, _ in found[:4]))
                    row.update(status="ambiguous", archive=a.name)
                    continue
                dest, why = archive_dest(w, plugin, a)
                if dest:
                    row.update(status="archive", archive=a.name, member=found[0][0], dest=dest, note="")
                    notes = []
                    break
                notes.append(why)
                row.update(status="ambiguous", archive=a.name)
        if row["status"] in ("unresolved", "ambiguous"):
            row["candidates"] = "; ".join(candidates(w, plugin))
        row["note"] = row["note"] or " | ".join(notes)
        rows.append(row)
    return rows


def plan_downloads(w: World, rows: list[dict]) -> list[dict]:
    have = set(w.archive_ids.values())
    out: dict[tuple[str, str], dict] = {}
    for r in rows:
        if r["status"] != "unresolved":
            continue
        for f in [c.strip() for c in r["candidates"].split(";") if c.strip()]:
            mod, fid, ver = w.folder_ids.get(mo2.fold(f), ("", "", ""))
            if not mod or not fid or (mod, fid) in have:
                continue
            d = out.setdefault((mod, fid), {"folder": f, "action": "download", "nexus_mod_id": mod,
                                            "nexus_file_id": fid, "nexus_version": ver,
                                            "url": mo2.nexus_url(int(mod), int(fid)) if mod.isdigit() and fid.isdigit() else "",
                                            "note": "", "_n": 0})
            d["_n"] += 1
    rows_out = []
    for d in out.values():
        d["note"] = f"fill_plugins：候選來源，{d.pop('_n')} 個缺少的插件"
        rows_out.append(d)
    return rows_out


# ---------------------------------------------------------------- apply
def _link(src: Path, dst: Path) -> str:
    if dst.exists():
        return "skipped"
    os.link(fsutil.long_path(src), fsutil.long_path(dst))
    return "linked"


def apply(w: World, rows: list[dict], pm: Path) -> dict[str, int]:
    counts = defaultdict(int)
    merged: set[tuple[str, str]] = set()
    by_archive: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        dest = w.mods_dir / r["dest"] if r["dest"] else None
        try:
            if r["status"] == "install":
                src = Path(r["source_folder"])
                names = [e.name for e in os.scandir(src) if e.is_file()]
                actual = next((n for n in names if n.lower() == r["plugin"].lower()), r["plugin"])
                for n in [actual, *same_stem_archives(names, actual)]:
                    counts[_link(src / n, dest / n)] += 1
                r["status"] = "done"
            elif r["status"] == "whole":
                key = (r["source_folder"], r["dest"])
                if key not in merged:
                    st = fsutil.clone_tree(Path(r["source_folder"]), dest, apply=True)
                    counts["linked"] += st.linked
                    counts["skipped"] += st.skipped
                    counts["error"] += len(st.errors)
                    merged.add(key)
                r["status"] = "done"
            elif r["status"] == "archive":
                by_archive[r["archive"]].append(r)
        except OSError as e:
            r["status"], r["note"] = "error", str(e)
            counts["error"] += 1
    archives = {a.name: a for a in w.members}
    for name, items in by_archive.items():
        a = archives[name]
        wanted: dict[str, list[dict]] = defaultdict(list)
        for r in items:
            folder = r["member"].rsplit("/", 1)[0] if "/" in r["member"] else ""
            sibs = [m for m in w.members[a] if (m.rsplit("/", 1)[0] if "/" in m else "") == folder]
            for m in [r["member"], *same_stem_archives(sibs, r["plugin"])]:
                wanted[m].append(r)
        staging = pm / STAGING_DIR / uuid.uuid4().hex[:8]
        try:
            extract_files(a, staging, list(wanted))
            for m, rs in wanted.items():
                src = staging / m
                for r in rs:
                    dst = w.mods_dir / r["dest"] / m.rsplit("/", 1)[-1]
                    if dst.exists():
                        counts["skipped"] += 1
                    elif src.exists():
                        shutil.copy2(src, dst)
                        counts["extracted"] += 1
                    else:
                        r["status"], r["note"] = "error", f"解壓後找不到 {m}"
                        counts["error"] += 1
            for r in items:
                if r["status"] == "archive":
                    r["status"] = "done"
        except (OSError, sevenzip.SevenZipError) as e:
            for r in items:
                r["status"], r["note"] = "error", str(e)
            counts["error"] += len(items)
        finally:
            shutil.rmtree(staging, ignore_errors=True)
    root = pm / STAGING_DIR
    if root.is_dir() and not any(root.iterdir()):
        root.rmdir()
    return dict(counts)


# ---------------------------------------------------------------- main
def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="補齊缺少檔案的目標插件（先關 MO2；預設試跑）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--mv", type=Path, help="M&V 安裝資料夾，例如 D:\\MV")
    ap.add_argument("--nolvus", type=Path, help="Nolvus 實例資料夾")
    ap.add_argument("--downloads", type=Path, help="壓縮檔資料夾（預設 <pm>\\downloads）")
    ap.add_argument("--manifest", type=Path, default=DEFAULT_REPORT_DIR / "manifest.csv")
    ap.add_argument("--extra", type=Path, default=DATA / "extra_archives.csv")
    ap.add_argument("--sources", type=Path, default=DATA / "plugin_sources.csv")
    ap.add_argument("--plan-downloads", action="store_true", help="寫出候選合集的下載清單")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    fsutil.enable_utf8_console()
    args = parse_args(argv)
    rep = Report("fill_plugins")
    rep.add("mode", "INFO", "模式", "實際執行" if args.apply else "試跑（加 --apply 才會寫入）")
    if args.apply and mo2_running():
        rep.add("mo2", "FAIL", "MO2 還開著", "請先關閉 MO2 再執行")
        return finish(rep, [], args.out)
    try:
        w = load_world(args)
    except FileNotFoundError as e:
        rep.add("input", "FAIL", "缺少輸入", str(e))
        return finish(rep, [], args.out)
    rows = plan(w)
    rep.add("missing", "INFO", "目標插件缺少檔案", f"{len(rows)} 個（已排除第 5 階段的輸出插件）")
    counts = defaultdict(int)
    for r in rows:
        counts[r["status"]] += 1
    for st in ("install", "whole", "archive"):
        if counts[st]:
            rep.add(st, "PASS", STATUS_TEXT[st], f"{counts[st]} 個")
    for st in ("ambiguous", "unresolved"):
        if counts[st]:
            rep.add(st, "WARN", STATUS_TEXT[st], f"{counts[st]} 個")
    if args.plan_downloads:
        dl = plan_downloads(w, rows)
        write_csv(args.out / "fill_plugins_downloads.csv", dl, DL_FIELDS)
        rep.add("downloads", "INFO", "候選合集的下載清單",
                f"{len(dl)} 個壓縮檔 → reports\\fill_plugins_downloads.csv（交給 nexus_fetch.py --manifest）")
    if args.apply:
        done = apply(w, rows, args.pm)
        rep.add("applied", "FAIL" if done.get("error") else "PASS", "寫入結果",
                f"連結 {done.get('linked', 0)}、解壓放入 {done.get('extracted', 0)}、"
                f"已存在略過 {done.get('skipped', 0)}、錯誤 {done.get('error', 0)}")
        rep.add("next", "INFO", "下一步", "關 MO2 跑 build_instance.py sync-order --restore-states --apply，再 verify")
    return finish(rep, rows, args.out)


def finish(rep: Report, rows: list[dict], out: Path) -> int:
    write_csv(out / "fill_plugins.csv", rows, FIELDS)
    rep.data = {"rows": len(rows)}
    path = rep.save(out, stem="fill_plugins")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
