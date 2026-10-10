"""Decide which files of a community translation pack match the mods actually installed.

比對社群漢化包（例如蘇禾的「Other」包）與 D:\\PM 實際安裝的 mod 版本，決定哪些檔案可以採用。

Verdicts per pack file (same relative path as the English file it replaces):
  .pex   accept when the compile time matches the installed script (xTranslator keeps the header)
  *_chinese.txt / *_english.txt   accept when the keys match the installed English file
  DSD .json   accept when its plugin folder is active; entries for missing plugins are harmless
  *_DESC.ini (Description Framework, in the Data root)   accept when its keys include every key of the
              installed file of the same name; review when there is no installed file (a new description set)
  .swf / other   review (cannot be verified automatically)
  no installed counterpart   skip (the mod is not in this list)
--include FILE (repeatable) copies a reviewed or skipped file anyway, after you checked it by hand.

    python tools\\zh\\diff_pack.py --pack "D:\\zh-packs\\MV 2.5.1 Other" --pm D:\\PM ^
        --accept-to "D:\\PM\\mods\\ZH - 蘇禾 M&V Other（已比對）" --apply
"""

from __future__ import annotations

import argparse
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pm import fsutil, pex, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402
from zh.common import DSD_DIR, parse_translation_bytes  # noqa: E402


def vfs_index(prof: vfs.Profile, top_dirs: set[str], root_files: set[str] = frozenset()) -> dict[str, Path]:
    """lower-case relative path -> winning file (loose files only), limited to the pack's top folders and
    to the file names the pack has in its root."""
    idx: dict[str, Path] = {}
    for folder in prof.enabled_folders:
        base = prof.mods_dir / folder
        try:
            entries = list(base.iterdir())
        except OSError:
            continue
        for p in entries:
            if p.is_file() and p.name.lower() in root_files:
                idx.setdefault(p.name.lower(), p)
        subs = [p for p in entries if p.is_dir() and p.name.lower() in top_dirs]
        for sub in subs:
            for p in sub.rglob("*"):
                if p.is_file():
                    idx.setdefault(p.relative_to(base).as_posix().lower(), p)
    return idx


def find_english_txt(rel: str, idx: dict[str, Path]) -> Path | None:
    stem = rel.rsplit("_", 1)[0]
    return idx.get(stem + "_english.txt")


def ini_keys(path: Path) -> set[str]:
    keys = set()
    for line in path.read_bytes().decode("utf-8", errors="replace").splitlines():
        t = line.strip().lstrip("\ufeff")
        if t and not t.startswith((";", "#", "[")) and "=" in t:
            keys.add(t.split("=", 1)[0].strip().lower())
    return keys


def judge(rel: str, pack_file: Path, idx: dict[str, Path], active_plugins: set[str]) -> tuple[str, str]:
    low = rel.lower()
    if low.endswith("_desc.ini") and "/" not in low:
        inst = idx.get(low)
        if not inst:
            return "review", "new Description Framework file: check its EditorIDs, then --include it"
        missing = ini_keys(inst) - ini_keys(pack_file)
        if not missing:
            return "accept", "keys include every installed key"
        return "review", f"{len(missing)} installed keys missing from the pack file"
    if low.endswith(".pex"):
        inst = idx.get(low)
        if not inst:
            return "skip", "no installed script with this name"
        try:
            a, b = pex.read(pack_file), pex.read(inst)
        except (pex.PexError, OSError) as e:
            return "review", f"unreadable pex: {e}"
        if a.compile_time == b.compile_time and a.source.lower() == b.source.lower():
            return "accept", "same compile time"
        return "reject", f"different script version ({a.compile_time} != {b.compile_time})"
    if low.endswith(".txt") and "/translations/" in "/" + low:
        en = find_english_txt(low, idx)
        if not en:
            return "skip", "no installed English translation file"
        pk = set(parse_translation_bytes(pack_file.read_bytes()))
        ek = set(parse_translation_bytes(en.read_bytes()))
        if not ek:
            return "review", "installed English file is empty"
        overlap = len(pk & ek) / len(ek)
        if overlap >= 0.95 and len(pk - ek) <= max(2, len(ek) // 20):
            return "accept", f"keys match ({overlap:.0%})"
        return "reject" if overlap < 0.6 else "review", f"keys overlap {overlap:.0%}, extra {len(pk - ek)}"
    if low.endswith(".json") and low.startswith(DSD_DIR.as_posix().lower()):
        plugin = low.split("/")[3] if len(low.split("/")) > 4 else ""
        return ("accept", "plugin active") if plugin in active_plugins else ("skip", f"plugin {plugin} not active")
    if low in idx:
        return "review", "replaces an installed file; check the mod version by hand"
    return "skip", "no installed counterpart"


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="比對社群漢化包與已安裝版本（預設試跑）")
    ap.add_argument("--pack", required=True, type=Path, help="已解壓的漢化包資料夾（結構同 Data）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--accept-to", type=Path, default=None, help="把 accept 的檔案複製到這個 mod 資料夾")
    ap.add_argument("--include-review", action="store_true", help="review 的檔案也一併複製")
    ap.add_argument("--include", action="append", default=[], metavar="FILE",
                    help="人工確認過、要採用的檔案（包內相對路徑或檔名，可重複）")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    prof = vfs.open_profile(args.pm, args.profile)
    active = {p.name.lower() for p in prof.plugins if p.enabled} | {p.lower() for p in vfs.primary_plugins(prof.game_dir)}
    pack_root = args.pack
    # packs are often zipped with an extra top folder or a "Data" folder
    for cand in (pack_root / "Data", pack_root / "data"):
        if cand.is_dir():
            pack_root = cand
    top_dirs = {p.name.lower() for p in pack_root.iterdir() if p.is_dir()}
    root_files = {p.name.lower() for p in pack_root.iterdir() if p.is_file()}
    idx = vfs_index(prof, top_dirs, root_files)
    wanted = {w.replace("\\", "/").lower() for w in args.include}
    rows = []
    for f in sorted(p for p in pack_root.rglob("*") if p.is_file()):
        rel = f.relative_to(pack_root).as_posix()
        verdict, why = judge(rel, f, idx, active)
        if verdict in ("review", "skip") and (rel.lower() in wanted or f.name.lower() in wanted):
            verdict, why = "include", f"--include（原判斷 {verdict}：{why}）"
        rows.append({"file": rel, "verdict": verdict, "reason": why})
        if args.apply and args.accept_to and (verdict in ("accept", "include")
                                              or (verdict == "review" and args.include_review)):
            dest = args.accept_to / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
    write_csv(args.out / "zh_diff_pack.csv", rows)
    c = Counter(r["verdict"] for r in rows)
    rep = Report("zh_diff_pack")
    rep.add("summary", "INFO", "比對結果", ", ".join(f"{k}={v}" for k, v in sorted(c.items())))
    rep.add("reject", "WARN" if c.get("reject") else "PASS", "版本不符而拒絕的檔案", f"{c.get('reject', 0)} 個")
    unknown = [w for w in wanted if not any(r["file"].lower() == w or r["file"].lower().rsplit("/", 1)[-1] == w
                                            for r in rows)]
    if unknown:
        rep.add("include", "WARN", "--include 找不到的檔案", ", ".join(sorted(unknown)))
    rep.add("mode", "INFO", "模式", "已複製到 " + str(args.accept_to) if args.apply and args.accept_to else "試跑")
    path = rep.save(args.out, stem="zh_diff_pack")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
