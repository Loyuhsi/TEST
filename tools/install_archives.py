"""Install downloaded Nexus archives into their manifest folders (plain archives only).

批次安裝：把 D:\\PM\\downloads 裡已下載、沒有 FOMOD 的壓縮檔，解壓到 manifest 指定的資料夾並寫 MO2 的 meta.ini。

Usage (Windows; close MO2 first; dry run unless --apply):
    python tools\\install_archives.py --pm D:\\PM [--only FOLDER] [--limit 20] [--apply]
Each archive is matched to reports\\manifest.csv through the Nexus mod/file IDs in its .meta.
Left for MO2 and listed in reports\\install_archives.csv: FOMOD installers, archives whose data
root is unclear or whose plugins differ from the target, folders whose decisions.csv note asks
for FOMOD choices, merging or DIP, and folders that already have files. A replace_dll folder is
moved to <pm>\\_replaced\\ (kept, not deleted) before the new files go in.
Archives are unpacked in <pm>\\_install_staging\\ and the data root is renamed into place, so a
mod folder is either the untouched placeholder or the complete install (see pm/swap.py for the
crash journal). The tool's own temporary copies (readmes, wrapper folders) are removed.
"""

from __future__ import annotations

import argparse
import configparser
import datetime as dt
import os
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, layout, mo2, sevenzip, swap  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, REPO_ROOT, Report, read_csv, write_csv  # noqa: E402

NOTE_NEEDS_PERSON = ("FOMOD", "合併安裝", "Dynamic Interface Patcher")
STAGING_DIR = "_install_staging"
REPLACED_DIR = "_replaced"
JOURNAL = "swap-in-progress.txt"
RESERVED = frozenset({"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)),
                      *(f"lpt{i}" for i in range(1, 10))})
FIELDS = ["archive", "folder", "action", "status", "root", "plugins", "reason", "mod", "file"]
PENDING = ("install", "replace")
LABELS = {
    "install": ("PASS", "可自動安裝"),
    "replace": ("PASS", "可自動重裝（舊資料夾移到 _replaced，不刪除）"),
    "installed": ("PASS", "已安裝"),
    "replaced": ("PASS", "已重裝（舊資料夾在 _replaced）"),
    "fomod": ("INFO", "FOMOD，要用 MO2 安裝"),
    "manual": ("WARN", "需要人工判斷（見 install_archives.csv 的 reason 欄）"),
    "unmatched": ("INFO", "不在 manifest 的下載"),
    "skip": ("INFO", "資料夾已有檔案，略過"),
    "already": ("INFO", "先前已安裝"),
    "error": ("FAIL", "失敗（見 reason 欄）"),
}


@dataclass(frozen=True)
class Inputs:
    targets: dict[tuple[str, str], list[dict]]   # (mod id, file id) -> manifest rows
    notes: dict[str, str]                         # folder -> decisions.csv note
    expected: dict[str, list[str]]                # folder -> plugins it should provide
    target_plugins: set[str] | None               # lower-case names in data/target/plugins.txt
    accept: frozenset[str] = frozenset()          # folded folder names a person checked (--accept)


# ---------------------------------------------------------------- seams (replaced in tests)
def list_files(archive: Path) -> list[sevenzip.Entry]:
    return [e for e in sevenzip.list_entries(archive) if not e.is_dir]


def extract(archive: Path, dest: Path) -> None:
    sevenzip.extract(archive, dest)


def mo2_running() -> bool:
    """True when ModOrganizer.exe is running, or when that cannot be checked."""
    if os.name != "nt":
        return False
    try:
        r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq ModOrganizer.exe", "/NH"],
                           capture_output=True, stdin=subprocess.DEVNULL, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return True
    return b"modorganizer.exe" in r.stdout.lower()


# ---------------------------------------------------------------- inputs
def _rows(path: Path) -> list[dict]:
    return read_csv(path) if path.exists() else []


def load_inputs(args: argparse.Namespace) -> Inputs:
    targets: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for r in read_csv(args.manifest):
        fid = (r.get("nexus_file_id") or "").strip()
        if r.get("action") in ("download", "replace_dll") and fid:
            targets[((r.get("nexus_mod_id") or "").strip(), fid)].append(r)
    notes = {r["folder"]: r.get("note") or "" for r in _rows(args.decisions)}
    expected = {r["folder"]: [p for p in (r.get("plugins") or "").split(";") if p.strip()]
                for r in _rows(args.provenance)}
    target = None
    if args.target_plugins.exists():
        target = {p.name.lower() for p in mo2.read_plugins(args.target_plugins)}
    return Inputs(dict(targets), notes, expected, target, frozenset(mo2.fold(a) for a in args.accept))


def read_download_meta(path: Path) -> dict[str, str]:
    cp = configparser.RawConfigParser(strict=False, interpolation=None)
    try:
        cp.read_string(path.read_text(encoding="utf-8", errors="replace").replace("\r", ""))
    except configparser.Error:
        return {}
    if not cp.has_section("General"):
        return {}
    return {k.lower(): v.strip().strip('"') for k, v in cp.items("General")}


# ---------------------------------------------------------------- plan
def _bad_folder(name: str) -> bool:
    return (not name.strip() or name != name.rstrip(" .") or any(c in name for c in '/\\:*?"<>|')
            or name.split(".")[0].strip().lower() in RESERVED)


def _note_flag(note: str) -> str:
    return next((k for k in NOTE_NEEDS_PERSON if k.lower() in note.lower()), "")


def _classify(row: dict, archive: Path, folder: str, busy: bool, inp: Inputs) -> dict:
    try:
        entries = list_files(archive)
    except sevenzip.SevenZipError as e:
        return row | {"status": "error", "reason": f"無法讀取壓縮檔：{e}"}
    lay = layout.classify([e.path for e in entries], inp.expected.get(folder, ()), inp.target_plugins,
                          accept=mo2.fold(folder) in inp.accept)
    row = row | {"root": lay.root, "plugins": ";".join(lay.plugins), "reason": lay.reason,
                 "size": sum(e.size for e in entries)}
    if lay.kind != "simple":
        return row | {"status": lay.kind}
    return row | {"status": "replace" if busy else "install"}


def plan_one(meta_path: Path, inp: Inputs, mods_dir: Path, only: set[str]) -> dict | None:
    archive = meta_path.with_suffix("")
    meta = read_download_meta(meta_path)
    mid, fid = meta.get("modid", ""), meta.get("fileid", "")
    row = dict.fromkeys(FIELDS, "") | {"archive": archive.name, "mod": mid, "file": fid,
                                       "version": meta.get("version", "")}
    hits = inp.targets.get((mid, fid), [])
    if only and not any(mo2.fold(h["folder"]) in only for h in hits):
        return None
    if not hits:
        return row | {"status": "unmatched", "reason": f"manifest 沒有 mod {mid} 檔案 {fid}"}
    row |= {"folder": "｜".join(h["folder"] for h in hits), "action": hits[0]["action"]}
    if len(hits) > 1:
        return row | {"status": "manual", "reason": "同一個檔案對應多個資料夾"}
    folder = hits[0]["folder"]
    flag = _note_flag(inp.notes.get(folder, ""))
    if flag:
        return row | {"status": "manual", "reason": f"decisions 註記要人工（{flag}）：{inp.notes[folder][:80]}"}
    if _bad_folder(folder):
        return row | {"status": "manual", "reason": "資料夾名稱不合法"}
    target = mods_dir / folder
    if not target.is_dir():
        return row | {"status": "manual", "reason": "佔位資料夾不存在（MO2 可能已刪掉 modlist 的那一行）"}
    busy = swap.has_content(target)
    if meta.get("installed", "").lower() == "true":
        if busy:
            return row | {"status": "already", "reason": "MO2 已標記這個下載為已安裝"}
        return row | {"status": "manual", "reason": "下載標記為已安裝，但資料夾是空的"}
    if busy and row["action"] != "replace_dll":
        return row | {"status": "skip", "reason": "資料夾已有檔案（可能已安裝）"}
    return _classify(row, archive, folder, busy, inp)


def plan(dl_dir: Path, mods_dir: Path, inp: Inputs, only: set[str]) -> list[dict]:
    rows = []
    for meta_path in sorted(dl_dir.glob("*.meta"), key=lambda p: p.name.lower()):
        if meta_path.with_suffix("").is_file():
            row = plan_one(meta_path, inp, mods_dir, only)
            if row is not None:
                rows.append(row)
    per_folder = Counter(mo2.fold(r["folder"]) for r in rows if r["status"] in PENDING)
    return [r | {"status": "manual", "reason": "同一個資料夾有多個壓縮檔"}
            if r["status"] in PENDING and per_folder[mo2.fold(r["folder"])] > 1 else r for r in rows]


# ---------------------------------------------------------------- apply
def _warn(msg: str) -> str:
    return f"；{msg}" if msg else ""


def _set_aside_skipped(src: Path, dest: Path) -> None:
    for child in list(src.iterdir()):
        low = child.name.lower()
        if (child.is_file() and low in layout.SKIP_NAMES) or (child.is_dir() and low == "fomod"):
            dest.mkdir(parents=True, exist_ok=True)
            os.replace(child, dest / child.name)


def _aside_path(replace: bool, target: Path, staging: Path, pm: Path) -> Path:
    """Where the current folder goes: the staging area for a placeholder, _replaced otherwise."""
    if not replace:
        return staging / "placeholder"
    root = pm / REPLACED_DIR
    root.mkdir(parents=True, exist_ok=True)
    dest = root / target.name
    return dest if not dest.exists() else root / f"{target.name} ({dt.datetime.now():%Y%m%d-%H%M%S})"


def _write_metas(row: dict, target: Path, meta_path: Path) -> None:
    (target / "meta.ini").write_text(
        mo2.install_meta_text(row["mod"], row["file"], row.get("version", ""), row["archive"]),
        encoding="utf-8", newline="")
    text = meta_path.read_text(encoding="utf-8", errors="replace")
    meta_path.write_text(mo2.mark_download_installed(text), encoding="utf-8", newline="")


def install_one(row: dict, dl_dir: Path, mods_dir: Path, pm: Path) -> dict:
    target, replace = mods_dir / row["folder"], row["status"] == "replace"
    staging = pm / STAGING_DIR / dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    unpacked = staging / "x"
    try:
        extract(dl_dir / row["archive"], unpacked)
        src = unpacked / row["root"] if row["root"] else unpacked
        if not src.is_dir():
            raise OSError(f"解壓後找不到資料根目錄「{row['root']}」")
        _set_aside_skipped(src, staging / "skipped")
        if not replace and swap.has_content(target):
            raise OSError("資料夾在安裝前已有檔案")
        aside = _aside_path(replace, target, staging, pm)
        swap.put_in_place(src, target, aside, pm / STAGING_DIR / JOURNAL)
    except (sevenzip.SevenZipError, OSError) as e:
        # keep staging while the target is missing: it may hold the placeholder to restore
        left = "" if not target.exists() else swap.remove_tree(staging)
        return row | {"status": "error", "reason": f"{type(e).__name__}: {e}" + _warn(left)}
    try:
        _write_metas(row, target, dl_dir / (row["archive"] + ".meta"))
    except OSError as e:
        return row | {"status": "error",
                      "reason": f"檔案已放好，但寫 meta 失敗：{e}" + _warn(swap.remove_tree(staging))}
    note = f"舊內容移到 {aside.relative_to(pm)}" if replace else ""
    reason = "；".join(x for x in (row["reason"], note, swap.remove_tree(staging)) if x)
    return row | {"status": "replaced" if replace else "installed", "reason": reason}


def clear_stale_staging(pm: Path) -> str:
    """Remove unpack folders an interrupted run left (after recovery has run)."""
    root = pm / STAGING_DIR
    stale = [d for d in root.iterdir() if d.is_dir()] if root.is_dir() else []
    warnings = [w for w in (swap.remove_tree(d) for d in stale) if w]
    return f"{len(stale)} 個" + _warn("；".join(warnings)) if stale else ""


def apply(rows: list[dict], dl_dir: Path, mods_dir: Path, pm: Path,
          limit: int | None) -> tuple[list[dict], str]:
    """Install the pending rows; stop if a folder could not be put back."""
    out, done, stopped = [], 0, ""
    journal = pm / STAGING_DIR / JOURNAL
    for row in rows:
        if row["status"] in PENDING and not stopped and (limit is None or done < limit):
            row = install_one(row, dl_dir, mods_dir, pm)
            done += 1
            if journal.exists():
                stopped = f"{row['folder']} 沒能放回 mods，批次已停止；請重新執行本工具（會先還原）"
        out.append(row)
    staging_root = pm / STAGING_DIR
    if staging_root.is_dir() and not any(staging_root.iterdir()):
        staging_root.rmdir()
    return out, stopped


# ---------------------------------------------------------------- report
def check_space(rep: Report, rows: list[dict], pm: Path, limit: int | None, apply_mode: bool) -> bool:
    pending = [r for r in rows if r["status"] in PENDING]
    needed = sum(int(r.get("size") or 0) for r in pending[:limit])
    free = fsutil.free_bytes(pm)
    detail = f"預計解壓 {fsutil.human(needed)}，{pm.anchor or pm} 剩 {fsutil.human(free)}"
    if free < needed * 1.1 + (1 << 30):
        rep.add("space", "FAIL" if apply_mode else "WARN", "磁碟空間不夠", detail)
        return False
    rep.add("space", "INFO", "磁碟空間", detail)
    return True


def summarize(rep: Report, rows: list[dict], apply_mode: bool, inp: Inputs, filtered: bool) -> None:
    counts = Counter(r["status"] for r in rows)
    for status, (level, title) in LABELS.items():
        n = counts.get(status, 0)
        if not n:
            continue
        if apply_mode and status in PENDING:
            level, title = "INFO", "這次沒安裝（超過 --limit 或批次停止）"
        rep.add(status, level, title, f"{n} 個")
    if not filtered:
        seen = {(r["mod"], r["file"]) for r in rows}
        missing = sum(len(v) for k, v in inp.targets.items() if k not in seen)
        rep.add("missing", "INFO", "manifest 目標還沒有下載檔", f"{missing} 個")


def finish(rep: Report, rows: list[dict], out: Path) -> int:
    write_csv(out / "install_archives.csv", rows, FIELDS)
    path = rep.save(out, stem="install_archives")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="批次安裝沒有 FOMOD 的已下載壓縮檔（先關 MO2；預設試跑）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--manifest", type=Path, default=DEFAULT_REPORT_DIR / "manifest.csv")
    ap.add_argument("--decisions", type=Path, default=REPO_ROOT / "data" / "decisions.csv")
    ap.add_argument("--provenance", type=Path, default=REPO_ROOT / "data" / "analysis" / "provenance.csv")
    ap.add_argument("--target-plugins", type=Path, default=REPO_ROOT / "data" / "target" / "plugins.txt")
    ap.add_argument("--only", action="append", default=[], metavar="FOLDER", help="只處理這個資料夾（可重複）")
    ap.add_argument("--accept", action="append", default=[], metavar="FOLDER",
                    help="人工看過壓縮檔後放行：不認得的資料夾、預期插件不符、插件不在目標（可重複；不放行 FOMOD 與 decisions 註記）")
    ap.add_argument("--limit", type=int, default=None, help="這次最多安裝幾個")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    return ap.parse_args(argv)


def recover(rep: Report, pm: Path, mods_dir: Path) -> bool:
    """Put back a folder a killed run left missing; False when that could not be done."""
    try:
        level, msg = swap.recover(pm / STAGING_DIR / JOURNAL, mods_dir, pm / STAGING_DIR, pm / REPLACED_DIR)
    except (OSError, ValueError) as e:
        rep.add("recover", "FAIL", "上次安裝中斷，無法自動還原", str(e))
        return False
    if msg:
        rep.add("recover", level, "上次安裝中斷", msg)
    return level != "FAIL"


def run_apply(rep: Report, rows: list[dict], dl_dir: Path, mods_dir: Path,
              args: argparse.Namespace) -> list[dict]:
    if mo2_running():
        rep.add("mo2", "FAIL", "MO2 正在執行", "先關閉 Mod Organizer 再用 --apply")
        return rows
    if not check_space(rep, rows, args.pm, args.limit, apply_mode=True):
        return rows
    stale = clear_stale_staging(args.pm)
    if stale:
        rep.add("staging", "INFO", "清掉上次留下的暫存解壓資料夾", stale)
    rows, stopped = apply(rows, dl_dir, mods_dir, args.pm, args.limit)
    if stopped:
        rep.add("stopped", "FAIL", "批次停止", stopped)
    return rows


def main(argv: list[str] | None = None) -> int:
    fsutil.enable_utf8_console()
    args = parse_args(argv)
    rep = Report("install_archives")
    paths = mo2.find_instance_paths(args.pm)
    mods_dir, dl_dir = paths["mods"], paths["downloads"]
    if not mods_dir.is_dir() or not dl_dir.is_dir():
        rep.add("paths", "FAIL", "找不到 MO2 的 mods 或 downloads 資料夾", f"{mods_dir}；{dl_dir}")
        return finish(rep, [], args.out)
    recovered = recover(rep, args.pm, mods_dir)
    inp = load_inputs(args)
    rows = plan(dl_dir, mods_dir, inp, {mo2.fold(o) for o in args.only})
    rep.add("mode", "INFO", "執行" if args.apply else "試跑（除了還原中斷的安裝，不改動檔案）",
            f"判斷了 {len(rows)} 個下載")
    if not args.apply:
        check_space(rep, rows, args.pm, args.limit, apply_mode=False)
    elif recovered:
        rows = run_apply(rep, rows, dl_dir, mods_dir, args)
    summarize(rep, rows, args.apply, inp, bool(args.only))
    return finish(rep, rows, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
