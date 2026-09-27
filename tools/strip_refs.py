"""Write a same-name copy of a plugin without references to forms its master no longer has.

移除失效引用：外掛補丁若是為舊版的前置（例如 LOTD 5）製作，NPC 的 PKID（AI 套件）或
CNTO（物品）可能指向新版前置（LOTD V6）已刪除的記錄，遊戲會卡在載入。本工具在另一個
mod 資料夾寫出同名的修正版，只刪掉這些失效的子記錄；FormID、外觀與其他資料都不變，
也不佔插件名額。

Usage (Windows; close MO2 first; dry run unless --apply):
    python tools\\strip_refs.py --pm D:\\PM --plugin "Modpocalypse NPCs (v3) Legacy of the Dragonborn.esp" ^
        --master LegacyoftheDragonborn.esm --out "D:\\PM\\mods\\Pages - LOTD V6 修正"
--plugin and --master take a plugin name (resolved through the profile's enabled mods) or a file path.
The output folder must be a separate mod placed above the original in MO2. Writes reports\\strip_refs.*.
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, tes4, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402

FIELDS = ["plugin", "record", "subrecord", "target"]


def existing_ids(path: Path) -> set[int]:
    """Object IDs of the records a plugin defines itself (not its overrides)."""
    data = path.read_bytes()
    own = len(tes4.parse_header_bytes(data, path.name).masters)
    return {fid & 0xFFFFFF for _t, _f, fid in tes4.iter_records(data, path.name) if fid >> 24 >= own}


def strip(data: bytes, name: str, master: str, existing: set[int],
          types: set[str]) -> tuple[bytes | None, list[dict]]:
    """(new plugin bytes or None when nothing changed, removed references)."""
    h = tes4.parse_header_bytes(data, name)
    lowered = [m.lower() for m in h.masters]
    if master.lower() not in lowered:
        return None, []
    idx = lowered.index(master.lower())

    def dangling(sub: bytes) -> bool:
        if len(sub) < 4:
            return False
        (fid,) = struct.unpack_from("<I", sub, 0)
        return fid >> 24 == idx and (fid & 0xFFFFFF) not in existing

    rows: list[dict] = []
    head, items = tes4.parse_plugin(data, name)

    def fix(rec: tes4.Record) -> tes4.Record:
        subs = list(tes4.iter_subrecords(rec.payload()))
        out: list[tuple[str, bytes]] = []
        removed: list[tuple[str, bytes]] = []
        drop_coed = False
        for typ, sub in subs:
            if typ in ("PKID", "CNTO") and dangling(sub):
                removed.append((typ, sub))
                drop_coed = typ == "CNTO"
                continue
            if typ == "COED" and drop_coed:
                removed.append((typ, sub))
                drop_coed = False
                continue
            drop_coed = False
            out.append((typ, sub))
        if not removed:
            return rec
        items_left = sum(1 for t, _ in out if t == "CNTO")
        out = [(t, struct.pack("<I", items_left) if t == "COCT" else s)
               for t, s in out if not (t == "COCT" and items_left == 0)]
        owner, oid = tes4.resolve(rec.form_id, h.masters, name)
        for typ, sub in removed:
            target = f"{master}:{struct.unpack_from('<I', sub, 0)[0] & 0xFFFFFF:06X}" if typ != "COED" else ""
            rows.append({"plugin": name, "record": f"{rec.type} {owner}:{oid:06X}", "subrecord": typ,
                         "target": target})
        return rec.replace_payload(tes4.build_subrecords(out))

    def walk(group_items: list) -> None:
        for i, item in enumerate(group_items):
            if isinstance(item, tes4.Group):
                walk(item.items)
            elif item.type in types:
                group_items[i] = fix(item)

    walk(items)
    if not rows:
        return None, []
    return tes4.serialize_plugin(head, items), rows


def locate(value: str, providers: dict[str, Path] | None) -> Path | None:
    p = Path(value)
    if p.is_file():
        return p
    return providers.get(value.lower()) if providers is not None else None


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="移除插件中指向前置已不存在記錄的引用（預設試跑；請先關閉 MO2）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--plugin", action="append", required=True, help="插件名稱或檔案路徑（可重複）")
    ap.add_argument("--master", required=True, help="新版前置的名稱或檔案路徑，例如 LegacyoftheDragonborn.esm")
    ap.add_argument("--out", type=Path, required=True, help="寫出修正版的 mod 資料夾（要放在原 mod 之上）")
    ap.add_argument("--types", default="NPC_", help="要處理的記錄類型，逗號分隔（預設 NPC_）")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    rep = Report("strip_refs")
    rep.add("mode", "INFO", "模式", "實際執行" if args.apply else "試跑（加 --apply 才會寫入）")
    providers = None
    if not all(Path(v).is_file() for v in [*args.plugin, args.master]):
        prof = vfs.open_profile(args.pm, args.profile)
        providers = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, prof.game_dir / "Data")
    master_path = locate(args.master, providers)
    if master_path is None:
        rep.add("master", "FAIL", "找不到前置", args.master)
        return finish(rep, [], args.report_dir)
    master_name = master_path.name
    existing = existing_ids(master_path)
    rep.add("master", "INFO", "前置", f"{master_name}：自己新增的記錄 {len(existing)} 筆")
    types = {t.strip() for t in args.types.split(",") if t.strip()}
    out_dir = args.out
    all_rows: list[dict] = []
    for value in args.plugin:
        src = locate(value, providers)
        name = src.name if src else value
        if src is None:
            rep.add(f"src:{name}", "FAIL", name, "找不到插件（mod 未啟用或名稱錯誤）")
            continue
        if src.parent.resolve() == out_dir.resolve():
            rep.add(f"src:{name}", "PASS", name, f"已修正：生效的是 {out_dir.name} 裡的版本")
            continue
        try:
            new, rows = strip(src.read_bytes(), src.name, master_name, existing, types)
        except (tes4.PluginError, OSError, ValueError) as e:
            rep.add(f"src:{name}", "FAIL", name, f"無法處理：{e}")
            continue
        if new is None:
            rep.add(f"src:{name}", "PASS", name, f"沒有指向 {master_name} 已不存在記錄的引用（來源：{src.parent.name}）")
            continue
        all_rows += rows
        recs = len({r["record"] for r in rows})
        kinds = {k: sum(1 for r in rows if r["subrecord"] == k) for k in ("PKID", "CNTO", "COED")}
        detail = (f"{recs} 筆記錄有失效引用：PKID {kinds['PKID']}、CNTO {kinds['CNTO']}（COED {kinds['COED']}）；"
                  f"來源：{src.parent.name}")
        dest = out_dir / src.name
        if not args.apply:
            rep.add(f"src:{name}", "WARN", name, detail + f"；會寫到 {out_dir.name}")
            continue
        if dest.exists() and os.stat(fsutil.long_path(dest)).st_nlink > 1:
            rep.add(f"src:{name}", "FAIL", name, detail + f"；{dest} 是硬連結，不能覆寫")
            continue
        out_dir.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name(dest.name + ".strip-tmp")
        tmp.write_bytes(new)
        os.replace(tmp, dest)
        rep.add(f"src:{name}", "PASS", name, detail + f"；已寫到 {out_dir.name}")
    return finish(rep, all_rows, args.report_dir)


def finish(rep: Report, rows: list[dict], out: Path) -> int:
    write_csv(out / "strip_refs.csv", rows, FIELDS)
    rep.data = {"removed": rows}
    path = rep.save(out, stem="strip_refs")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
