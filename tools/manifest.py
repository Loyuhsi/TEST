"""Phase 4: decide the action for every target folder from the real installs.

第四階段：依實際安裝結果，替目標清單每個資料夾決定動作（保留／下載／重建／捨棄／需檢查）。

Usage (Windows):
    python tools\\manifest.py --pm D:\\PM
Inputs: data/target/modlist.txt, data/analysis/provenance.csv, data/analysis/nexus_candidates.csv,
data/analysis/mv_folder_map.csv, reports/inventory-*.csv, data/decisions.csv (manual overrides)
and what is already inside D:\\PM\\mods.
data/decisions.csv columns: folder,action,note[,nexus_mod_id,nexus_file_id,nexus_version]; IDs given
there win over every other ID source.
Outputs: reports/manifest.csv, reports/downloads.html, reports/manifest.txt/.json
"""

from __future__ import annotations

import argparse
import html
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, mo2, pe  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, REPO_ROOT, Report, read_csv, write_csv  # noqa: E402

DATA = REPO_ROOT / "data"
FIELDS = ["line", "folder", "section", "category", "present", "action", "nexus_mod_id", "nexus_file_id",
          "nexus_version", "id_source", "url", "ae_only_dlls", "note"]


def load_optional(path: Path) -> list[dict]:
    return read_csv(path) if path.exists() else []


def by_folder(rows: list[dict], key: str = "folder") -> dict[str, dict]:
    return {mo2.fold(r[key]): r for r in rows if r.get(key)}


def ae_only_dlls(folder: Path) -> list[str]:
    out = []
    for cand in ("SKSE/Plugins", "skse/plugins"):
        sp = folder / cand
        if sp.is_dir():
            for d in sp.glob("*.dll"):
                try:
                    if pe.read_dll(d).runtime_class == "ae_only":
                        out.append(d.name)
                except (pe.PEError, OSError, IndexError, ValueError):
                    pass
            break
    return out


def decide(r: dict, present: bool, ids: dict, decision: dict | None, dlls: list[str]) -> tuple[str, str]:
    cat = r.get("category", "")
    if decision:
        return decision["action"], decision.get("note", "manual decision")
    if cat == "generated":
        return "regenerate", r.get("note", "")
    if cat in ("custom", "non_nexus"):
        return "drop", r.get("note", "")
    if present:
        if dlls:
            return "replace_dll", "AE-only SKSE DLL: install the 1.5.97 / NG build of this mod"
        return "keep", ""
    if ids.get("mod_id"):
        return "download", r.get("note", "")
    return "review", "no Nexus ID yet - identify manually and add to data/decisions.csv"


def run(args) -> Report:
    rep = Report("manifest")
    target = mo2.read_modlist(args.target)
    prov = by_folder(read_csv(args.provenance))
    nexus = by_folder(load_optional(DATA / "analysis" / "nexus_candidates.csv"))
    mvmap = by_folder(load_optional(DATA / "analysis" / "mv_folder_map.csv"))
    inv: dict[str, dict] = {}
    for name in ("nolvus", "mv"):
        for row in load_optional(args.reports / f"inventory-{name}.csv"):
            if row.get("mod_id"):
                inv.setdefault(mo2.fold(row["folder"]), row)
    decisions = by_folder(load_optional(args.decisions))
    mods_dir = args.pm / "mods"

    rows = []
    for e in target:
        if e.is_separator or not e.enabled:
            continue
        key = mo2.fold(e.name)
        base = mo2.strip_dup_suffix(e.name)
        bkey = mo2.fold(base) if base else None
        p = prov.get(key, {"category": "unknown", "section": "", "note": ""})
        folder = mods_dir / e.name
        present = folder.is_dir() and any(folder.iterdir())
        ids: dict = {}
        for src, table in (("inventory", inv), ("mv_map", mvmap)):
            hit = table.get(key) or (table.get(bkey) if bkey else None)
            if hit and (hit.get("mod_id") or hit.get("nexus_mod_id")):
                ids = {"mod_id": hit.get("mod_id") or hit.get("nexus_mod_id"),
                       "file_id": hit.get("file_id") or hit.get("nexus_file_id"),
                       "version": hit.get("version") or hit.get("nexus_version"), "source": src}
                break
        dec = decisions.get(key)
        if dec and (dec.get("nexus_mod_id") or "").strip():
            ids = {"mod_id": dec["nexus_mod_id"].strip(), "file_id": (dec.get("nexus_file_id") or "").strip(),
                   "version": (dec.get("nexus_version") or "").strip(), "source": "decision"}
        if not ids:
            nx = nexus.get(key)
            if nx and nx.get("nexus_mod_id") and nx.get("confidence") in ("high", "medium") \
                    and nx.get("category") in ("nexus_found", "nexus_ambiguous", "adult_gated"):
                ids = {"mod_id": nx["nexus_mod_id"], "file_id": nx.get("suggested_file_id", ""),
                       "version": nx.get("suggested_file_version", ""),
                       "source": f"nexus_search:{nx.get('confidence')}"}
        dlls = ae_only_dlls(folder) if present else []
        action, note = decide(p, present, ids, dec, dlls)
        mid = ids.get("mod_id", "")
        fid = ids.get("file_id", "")
        rows.append({
            "line": e.line_no, "folder": e.name, "section": p.get("section", ""), "category": p.get("category", ""),
            "present": "yes" if present else "", "action": action, "nexus_mod_id": mid, "nexus_file_id": fid,
            "nexus_version": ids.get("version", ""), "id_source": ids.get("source", ""),
            "url": mo2.nexus_url(int(mid), int(fid or 0)) if str(mid).isdigit() else "",
            "ae_only_dlls": ";".join(dlls), "note": note,
        })

    out = args.reports
    write_csv(out / "manifest.csv", rows, FIELDS)
    write_downloads_html(out / "downloads.html", rows)
    counts = Counter(r["action"] for r in rows)
    rep.data = {"by_action": dict(counts), "pm": str(args.pm)}
    rep.add("total", "INFO", "目標資料夾", f"{len(rows)} 個")
    for action, title in (("keep", "已就位"), ("download", "需從 Nexus 下載"), ("regenerate", "第五階段重建"),
                          ("replace_dll", "需換成 1.5.97 版 DLL"), ("review", "尚無來源，需人工確認"),
                          ("drop", "捨棄")):
        n = counts.get(action, 0)
        status = "WARN" if action in ("review", "replace_dll") and n else "INFO"
        rep.add(action, status, title, f"{n} 個")
    rep.add("files", "INFO", "輸出", "reports\\manifest.csv、reports\\downloads.html")
    return rep


def write_downloads_html(path: Path, rows: list[dict]) -> None:
    todo = [r for r in rows if r["action"] in ("download", "replace_dll", "review")]
    parts = ["<!doctype html><meta charset='utf-8'><title>Pages 下載清單</title>",
             "<style>body{font-family:system-ui,'Microsoft JhengHei';margin:16px}table{border-collapse:collapse}"
             "td,th{border:1px solid #ccc;padding:4px 8px}tr.done{opacity:.35}code{user-select:all}</style>",
             "<h1>待下載／待處理的 mod</h1><p>在 Nexus 檔案頁按 <b>Mod Manager Download</b>，"
             "MO2 安裝時把名稱改成「資料夾名稱」欄（可直接選取複製），遇到同名資料夾選 <b>Replace</b>。"
             "勾選框只存在這台電腦的瀏覽器。</p><table><tr><th>✓</th><th>行</th><th>動作</th>"
             "<th>資料夾名稱</th><th>Nexus</th><th>備註</th></tr>"]
    for r in todo:
        link = f"<a href='{html.escape(r['url'])}' target='_blank'>{r['nexus_mod_id']}/{r['nexus_file_id'] or '?'}</a>" \
            if r["url"] else "—"
        parts.append(f"<tr><td><input type=checkbox data-k='{r['line']}'></td><td>{r['line']}</td>"
                     f"<td>{r['action']}</td><td><code>{html.escape(r['folder'])}</code></td><td>{link}</td>"
                     f"<td>{html.escape(r['note'])}</td></tr>")
    parts.append("</table><script>document.querySelectorAll('input[data-k]').forEach(b=>{const k='pm-'+b.dataset.k;"
                 "try{b.checked=localStorage.getItem(k)==='1'}catch(e){}b.closest('tr').classList.toggle('done',b.checked);"
                 "b.onchange=()=>{try{localStorage.setItem(k,b.checked?'1':'0')}catch(e){}"
                 "b.closest('tr').classList.toggle('done',b.checked)}})</script>")
    path.write_text("\n".join(parts), encoding="utf-8")


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="產生組合清單（唯讀，只寫 reports/）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--target", type=Path, default=DATA / "target" / "modlist.txt")
    ap.add_argument("--provenance", type=Path, default=DATA / "analysis" / "provenance.csv")
    ap.add_argument("--decisions", type=Path, default=DATA / "decisions.csv")
    ap.add_argument("--reports", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    args.reports.mkdir(parents=True, exist_ok=True)
    rep = run(args)
    path = rep.save(args.reports, stem="manifest")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
