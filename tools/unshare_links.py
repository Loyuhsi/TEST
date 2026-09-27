"""Replace hardlinked tool settings with independent copies before a tool rewrites them.

把工具設定檔的硬連結換成獨立副本：BodySlide、DynDOLOD、xEdit 等工具會原地改寫自己的設定檔
（Config.xml、*.ini、記錄檔），硬連結會把這些修改帶回 Nolvus／M&V 的原檔。

Usage (Windows; close the tool first; dry run unless --apply):
    python tools\\unshare_links.py --path "D:\\PM\\mods\\BodySlide and Outfit Studio\\CalienteTools\\BodySlide"
    python tools\\unshare_links.py --path D:\\PM\\tools --apply
Only settings-type files are touched (.ini .xml .json .toml .cfg .txt up to 16 MB, .log of any size). Each one
gets a byte-identical copy in place of the link; the source instance keeps its file unchanged.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402

SETTINGS_EXTS = frozenset({".ini", ".xml", ".json", ".toml", ".cfg", ".txt", ".log"})
MAX_BYTES = 16 * 1024 * 1024


def shared_settings(root: Path) -> list[Path]:
    """Settings-type files under root that have more than one hardlink."""
    out = []
    for dirpath, _dirs, files in os.walk(fsutil.long_path(root)):
        for f in files:
            if os.path.splitext(f)[1].lower() not in SETTINGS_EXTS:
                continue
            p = os.path.join(dirpath, f)
            try:
                st = os.stat(p)
            except OSError:
                continue
            if st.st_nlink > 1 and (st.st_size <= MAX_BYTES or f.lower().endswith(".log")):
                out.append(Path(p))
    return sorted(out, key=lambda p: str(p).lower())


def display(p: Path, root: Path) -> str:
    s, r = str(p), fsutil.long_path(root)
    return os.path.relpath(s, r) if s.startswith(r) else s


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="把工具設定檔的硬連結換成獨立副本（預設試跑；請先關閉該工具）")
    ap.add_argument("--path", type=Path, action="append", required=True, help="要處理的資料夾（可重複）")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    rep = Report("unshare_links")
    rep.add("mode", "INFO", "模式", "實際執行" if args.apply else "試跑（加 --apply 才會寫入）")
    rows = []
    for root in args.path:
        if not root.is_dir():
            rep.add(f"missing:{root}", "FAIL", "找不到資料夾", str(root))
            continue
        found = shared_settings(root)
        done = errors = 0
        for p in found:
            row = {"folder": str(root), "file": display(p, root), "status": "shared"}
            if args.apply:
                try:
                    fsutil.unshare(p)
                    row["status"] = "unshared"
                    done += 1
                except OSError as e:
                    row["status"] = f"error: {e}"
                    errors += 1
            rows.append(row)
        detail = f"硬連結的設定檔 {len(found)} 個" + (f"，已換成獨立副本 {done} 個" if args.apply else "")
        if errors:
            rep.add(f"err:{root}", "FAIL", root.name, f"{detail}；失敗 {errors} 個（檔案可能正被工具使用）")
        else:
            rep.add(f"ok:{root}", "PASS" if args.apply or not found else "INFO", root.name, detail)
    write_csv(args.out / "unshare_links.csv", rows, ["folder", "file", "status"])
    rep.data = {"files": rows}
    path = rep.save(args.out, stem="unshare_links")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
