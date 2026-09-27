"""Write a same-name copy of a plugin without references to forms its master no longer has.

移除失效引用：外掛補丁若是為舊版的前置（例如 LOTD 5）製作，NPC 的 PKID（AI 套件）或
CNTO（物品）可能指向新版前置（LOTD V6）已刪除的記錄，遊戲會卡在載入。本工具在另一個
mod 資料夾寫出同名的修正版，只刪掉這些失效的子記錄；FormID、外觀與其他資料都不變，
也不佔插件名額。

Usage (Windows; close MO2 first; dry run unless --apply):
    python tools\\strip_refs.py --pm D:\\PM --plugin "Modpocalypse NPCs (v3) Legacy of the Dragonborn.esp" ^
        --master LegacyoftheDragonborn.esm --out "D:\\PM\\mods\\Pages - LOTD V6 修正"
--plugin and --master take a plugin name (resolved through the profile's enabled mods) or a file path.
    python tools\\strip_refs.py --pm D:\\PM --drop-missing --from-csv data\\analysis\\override_mismatch.csv ^
        --out "D:\\PM\\mods\\Pages - 版本不符修正"
--drop-missing removes whole override records whose target does not exist in the (non-official) master the
plugin names, e.g. patches made for a newer master: such records would otherwise turn into stray new
records, and on a 1.70-header master an object ID below 0x800 even lands on a Skyrim.esm hardcoded form.
    python tools\\strip_refs.py --pm D:\\PM --drop-unresolved-base --from-csv data\\analysis\\unresolved_refs.csv ^
        --out "D:\\PM\\mods\\Pages - 版本不符修正"
--drop-unresolved-base removes whole placed references (REFR, ACHR, ...) whose base object (NAME) does not exist in
the (non-official) master it names; the game cannot show them anyway. An override removed this way falls back to
the master's own record. Both modes can be combined.
The output folder must be a separate mod placed above the original in MO2. A plugin whose winning copy is already
in the output folder is checked again and updated in place (single-link files only), so modes can be stacked.
Writes reports\\strip_refs.*.
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, tes4, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, read_csv, write_csv  # noqa: E402

FIELDS = ["plugin", "record", "subrecord", "target"]
OFFICIAL = {"skyrim.esm", "update.esm", "dawnguard.esm", "hearthfires.esm", "dragonborn.esm", "_resourcepack.esl"}
PLACED = {"REFR", "ACHR", "PGRE", "PHZD", "PMIS", "PARW", "PBAR", "PBEA", "PCON", "PFLA"}


def is_official(name: str) -> bool:
    n = name.lower()
    return n in OFFICIAL or (n.startswith("cc") and n.endswith((".esm", ".esl")))


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


def base_of(rec: tes4.Record) -> int | None:
    """FormID in a placed reference's NAME (its base object), or None."""
    for typ, sub in tes4.iter_subrecords(rec.payload()):
        if typ == "NAME" and len(sub) >= 4:
            return struct.unpack_from("<I", sub, 0)[0]
    return None


def drop_missing(data: bytes, name: str, ids_of, overrides: bool = True,
                 bases: bool = False) -> tuple[bytes | None, list[dict], int]:
    """Remove override records whose target is not defined by its master (overrides=True) and
    placed references whose base object is not defined by its master (bases=True).

    ids_of(master name) returns the master's own object IDs, or None to skip that master.
    Returns (new bytes or None, one row per removed record, records+groups removed).
    """
    h = tes4.parse_header_bytes(data, name)
    masters = h.masters
    rows: list[dict] = []

    def missing(fid: int) -> bool:
        idx = fid >> 24
        if idx >= len(masters) or is_official(masters[idx]):
            return False
        ids = ids_of(masters[idx])
        return ids is not None and (fid & 0xFFFFFF) not in ids

    def why(item: tes4.Record) -> tuple[str, str] | None:
        """(subrecord, target) for the report when the record must go, else None."""
        if overrides and missing(item.form_id):
            return "", ""
        if bases and item.type in PLACED:
            base = base_of(item)
            if base is not None and missing(base):
                owner, oid = tes4.resolve(base, masters, name)
                return "NAME", f"{owner}:{oid:06X}"
        return None

    def prune(items: list) -> tuple[list, int]:
        out, gone, i = [], 0, 0
        while i < len(items):
            item = items[i]
            if isinstance(item, tes4.Group):
                kept, g = prune(item.items)
                gone += g
                if kept or not g:
                    item.items = kept
                    out.append(item)
                else:
                    gone += 1                       # a group we emptied
                i += 1
                continue
            reason = why(item)
            if reason is None:
                out.append(item)
                i += 1
                continue
            owner, oid = tes4.resolve(item.form_id, masters, name)
            gone += 1
            nxt = items[i + 1] if i + 1 < len(items) else None
            children = 0
            if item.type in ("CELL", "WRLD") and isinstance(nxt, tes4.Group) \
                    and nxt.label == struct.pack("<I", item.form_id):
                children = tes4.count_items(nxt.items)
                gone += 1 + children
                i += 1                              # its children group goes with it
            rows.append({"plugin": name, "record": f"{item.type} {owner}:{oid:06X}", "subrecord": reason[0],
                         "target": reason[1] or (f"含子記錄 {children} 筆" if children else "")})
            i += 1
        return out, gone

    head, items = tes4.parse_plugin(data, name)
    items, gone = prune(items)
    if not rows:
        return None, [], 0
    total = tes4.count_items(items)
    return tes4.serialize_plugin(tes4.set_record_count(head, total), items), rows, gone


def locate(value: str, providers: dict[str, Path] | None) -> Path | None:
    p = Path(value)
    if p.is_file():
        return p
    return providers.get(value.lower()) if providers is not None else None


def write_fixed(rep: Report, key: str, name: str, detail: str, new: bytes, dest: Path, apply: bool) -> None:
    if not apply:
        rep.add(key, "WARN", name, detail + f"；會寫到 {dest.parent.name}")
        return
    if dest.exists() and os.stat(fsutil.long_path(dest)).st_nlink > 1:
        rep.add(key, "FAIL", name, detail + f"；{dest} 是硬連結，不能覆寫")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".strip-tmp")
    tmp.write_bytes(new)
    os.replace(tmp, dest)
    rep.add(key, "PASS", name, detail + f"；已寫到 {dest.parent.name}")


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="移除插件中指向前置已不存在記錄的引用（預設試跑；請先關閉 MO2）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--plugin", action="append", default=[], help="插件名稱或檔案路徑（可重複）")
    ap.add_argument("--from-csv", type=Path, help="從 CSV 的 plugin 欄讀插件清單")
    ap.add_argument("--master", help="--types 模式：新版前置的名稱或檔案路徑，例如 LegacyoftheDragonborn.esm")
    ap.add_argument("--drop-missing", action="store_true",
                    help="刪掉覆寫目標在（非官方）前置裡不存在的整筆記錄")
    ap.add_argument("--drop-unresolved-base", action="store_true",
                    help="刪掉基底物件（NAME）在（非官方）前置裡不存在的放置記錄（REFR、ACHR…）")
    ap.add_argument("--out", type=Path, required=True, help="寫出修正版的 mod 資料夾（要放在原 mod 之上）")
    ap.add_argument("--types", default="NPC_", help="要處理的記錄類型，逗號分隔（預設 NPC_）")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    dropping = args.drop_missing or args.drop_unresolved_base
    rep = Report("strip_refs")
    rep.add("mode", "INFO", "模式", ("刪除覆寫不存在記錄的整筆記錄；" if args.drop_missing else "")
            + ("刪除基底物件不存在的放置記錄；" if args.drop_unresolved_base else "")
            + ("實際執行" if args.apply else "試跑（加 --apply 才會寫入）"))
    plugins = list(args.plugin)
    if args.from_csv:
        plugins += [r["plugin"].strip() for r in read_csv(args.from_csv) if (r.get("plugin") or "").strip()]
    plugins = list(dict.fromkeys(plugins))                  # a scan table lists a plugin once per record
    if not plugins:
        ap.error("請指定 --plugin 或 --from-csv")
    if not dropping and not args.master:
        ap.error("請指定 --master，或改用 --drop-missing／--drop-unresolved-base")
    values = plugins + ([args.master] if args.master else [])
    providers = None
    if dropping or not all(Path(v).is_file() for v in values):
        prof = vfs.open_profile(args.pm, args.profile)
        providers = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, prof.game_dir / "Data")
    out_dir = args.out
    all_rows: list[dict] = []
    if dropping:
        cache: dict[str, set[int] | None] = {}

        def ids_of(master: str) -> set[int] | None:
            key = master.lower()
            if key not in cache:
                path = locate(master, providers)
                cache[key] = existing_ids(path) if path is not None else None
            return cache[key]
    else:
        master_path = locate(args.master, providers)
        if master_path is None:
            rep.add("master", "FAIL", "找不到前置", args.master)
            return finish(rep, [], args.report_dir)
        master_name = master_path.name
        existing = existing_ids(master_path)
        rep.add("master", "INFO", "前置", f"{master_name}：自己新增的記錄 {len(existing)} 筆")
        types = {t.strip() for t in args.types.split(",") if t.strip()}
    for value in plugins:
        src = locate(value, providers)
        name = src.name if src else value
        key = f"src:{name}"
        if src is None:
            rep.add(key, "FAIL", name, "找不到插件（mod 未啟用或名稱錯誤）")
            continue
        in_out = src.parent.resolve() == out_dir.resolve()
        try:
            data = src.read_bytes()
            if dropping:
                new, rows, gone = drop_missing(data, src.name, ids_of, overrides=args.drop_missing,
                                               bases=args.drop_unresolved_base)
            else:
                new, rows = strip(data, src.name, master_name, existing, types)
        except (tes4.PluginError, OSError, ValueError) as e:
            rep.add(key, "FAIL", name, f"無法處理：{e}")
            continue
        if new is None:
            if dropping:
                what = "；".join(t for t, on in (("前置裡都找得到覆寫目標", args.drop_missing),
                                                 ("放置記錄的基底物件都找得到", args.drop_unresolved_base)) if on)
            else:
                what = f"沒有指向 {master_name} 已不存在記錄的引用"
            if in_out:
                rep.add(key, "PASS", name, f"已修正：生效的是 {out_dir.name} 裡的版本，{what}")
            else:
                rep.add(key, "PASS", name, f"{what}（來源：{src.parent.name}）")
            continue
        all_rows += rows
        where = f"來源：{src.parent.name}" + ("（原地更新修正版）" if in_out else "")
        if dropping:
            n_base = sum(1 for r in rows if r["subrecord"] == "NAME")
            parts = ([f"{len(rows) - n_base} 筆覆寫不存在記錄的記錄"] if args.drop_missing else []) \
                + ([f"{n_base} 筆基底物件不存在的放置記錄"] if args.drop_unresolved_base else [])
            detail = f"刪除 {'、'.join(parts)}（連同子記錄與空群組共 {gone} 項）；{where}"
        else:
            recs = len({r["record"] for r in rows})
            kinds = {k: sum(1 for r in rows if r["subrecord"] == k) for k in ("PKID", "CNTO", "COED")}
            detail = (f"{recs} 筆記錄有失效引用：PKID {kinds['PKID']}、CNTO {kinds['CNTO']}（COED {kinds['COED']}）；"
                      f"{where}")
        write_fixed(rep, key, name, detail, new, out_dir / src.name, args.apply)
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
