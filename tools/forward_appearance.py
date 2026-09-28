"""Write a same-name copy of an NPC patch whose appearance fields come from the appearance mod we installed.

外觀轉送：NPC 補丁（例如 AI Overhaul 對 NITHI 的補丁）若是照外觀 mod 的另一個版本或變體做的，
它引用外觀 mod 新增記錄（皮膚、頭部零件、臉部貼圖）的編號會錯位，NPC 會黑臉、身體錯亂甚至當機。
本工具在另一個 mod 資料夾寫出同名修正版：每筆 NPC 保留補丁自己的 AI 等資料，外觀子記錄改用
--from 插件（我們裝的外觀 mod）那一筆的值；FormID 會換算成補丁的前置編號。不佔插件名額。

Usage (Windows; close MO2 first; dry run unless --apply):
    python tools\\forward_appearance.py --pm D:\\PM ^
        --plugin "NITHI NPCs - The Reach - Complete - AI Overhaul.esp" ^
        --from "NITHI NPCS - The Reach - Women.esp" --from "NITHI NPCs - The Reach - Men.esp" ^
        --out "D:\\PM\\mods\\Pages - 版本不符修正"
--plugin and --from take a plugin name (resolved through the profile's enabled mods) or a file path.
Other reference fields that still point at a --from plugin's own records and disagree with it are
reported, not changed. A copy already in --out is updated in place (single-link files only).
Writes reports\\forward_appearance.*.
"""

from __future__ import annotations

import argparse
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, tes4, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402
from strip_refs import locate, write_fixed  # noqa: E402

FIELDS = ["plugin", "npc", "source", "changed", "note"]
# NPC_ subrecords in the order xEdit writes them (TES5); used to place a field the patch lacks
ORDER = ["EDID", "VMAD", "OBND", "ACBS", "SNAM", "INAM", "VTCK", "TPLT", "RNAM", "SPCT", "SPLO", "DEST", "DSTD",
         "DMDL", "DMDT", "DMDS", "DSTF", "WNAM", "ANAM", "ATKR", "ATKD", "ATKE", "SPOR", "OCOR", "GWOR", "ECOR",
         "PRKZ", "PRKR", "COCT", "CNTO", "COED", "AIDT", "PKID", "KSIZ", "KWDA", "CNAM", "FULL", "SHRT", "DATA",
         "DNAM", "PNAM", "HCLF", "ZNAM", "GNAM", "NAM5", "NAM6", "NAM7", "NAM8", "CSDT", "CSDI", "CSDC", "CSCR",
         "DOFT", "SOFT", "DPLT", "CRIF", "FTST", "QNAM", "NAM9", "NAMA", "TINI", "TINC", "TINV", "TIAS"]
RANK = {t: i for i, t in enumerate(ORDER)}
TINT = ("TINI", "TINC", "TINV", "TIAS")
# appearance groups: each is replaced as a whole; the tint layers move together
GROUPS = [("RNAM",), ("WNAM",), ("ANAM",), ("PNAM",), ("HCLF",), ("NAM6",), ("NAM7",), ("FTST",), ("QNAM",),
          ("NAM9",), ("NAMA",), TINT]
GROUP_OF = {t: g for g in GROUPS for t in g}
FORMID_AT_0 = {"RNAM", "WNAM", "ANAM", "PNAM", "HCLF", "FTST"}
# other fields whose first 4 bytes are a FormID; checked, never changed
RESIDUAL = ("INAM", "VTCK", "TPLT", "SPLO", "SNAM", "PRKR", "CNTO", "PKID", "CNAM", "ZNAM", "GNAM", "CSCR", "DOFT",
            "SOFT", "DPLT", "CRIF")


@dataclass
class Source:
    name: str
    masters: list[str]
    npcs: dict[tuple[str, int], list[tuple[str, bytes]]] = field(default_factory=dict)


def load_source(path: Path) -> Source:
    data = path.read_bytes()
    head, items = tes4.parse_plugin(data, path.name)
    masters = tes4.parse_header_bytes(data, path.name).masters
    src = Source(path.name, masters)
    for rec in tes4.walk_records(items):
        if rec.type == "NPC_":
            owner, oid = tes4.resolve(rec.form_id, masters, path.name)
            src.npcs[(owner.lower(), oid)] = list(tes4.iter_subrecords(rec.payload()))
    return src


def remap(fid: int, src: Source, masters: list[str], name: str) -> int | None:
    """A FormID written in src, rewritten for a plugin with these masters (None when it cannot be)."""
    if fid == 0:
        return 0
    owner, oid = tes4.resolve(fid, src.masters, src.name)
    lowered = [m.lower() for m in masters]
    if owner.lower() in lowered:
        return (lowered.index(owner.lower()) << 24) | oid
    if owner.lower() == name.lower():
        return (len(masters) << 24) | oid
    return None


def merged(subs: list[tuple[str, bytes]], donor: list[tuple[str, bytes]]) -> list[tuple[str, bytes]]:
    """The patch's subrecords with every appearance group replaced by the donor's (already remapped)."""
    runs = {g: [s for s in donor if s[0] in g] for g in GROUPS}
    out: list[tuple[str, bytes]] = []
    placed: set = set()
    for typ, data in subs:
        g = GROUP_OF.get(typ)
        if g is None:
            out.append((typ, data))
        elif g not in placed:
            out.extend(runs[g])
            placed.add(g)
    for g in GROUPS:
        if g in placed or not runs[g]:
            continue
        rank = RANK[g[0]]
        at = next((i for i, (t, _) in enumerate(out) if RANK.get(t, -1) > rank), len(out))
        out[at:at] = runs[g]
    return out


def forward(data: bytes, name: str, sources: list[Source]) -> tuple[bytes | None, list[dict], dict]:
    """(new plugin bytes or None when nothing changed, report rows, counters)."""
    masters = tes4.parse_header_bytes(data, name).masters
    rank_of = {m.lower(): i for i, m in enumerate(masters)}
    own = {s.name.lower() for s in sources}
    head, items = tes4.parse_plugin(data, name)
    rows: list[dict] = []
    stats = {"changed": 0, "same": 0, "skipped": 0, "residual": 0, "ambiguous": 0}

    def pick(key: tuple[str, int]) -> Source | None:
        found = [s for s in sources if key in s.npcs]
        if len(found) > 1:
            stats["ambiguous"] += 1
        # the source that loads last wins, as it would in game
        return max(found, key=lambda s: rank_of.get(s.name.lower(), -1)) if found else None

    def residual(npc: str, subs: list[tuple[str, bytes]], agreed: set[tuple[str, int]]) -> None:
        """Report reference fields that point at a source's own records unless the source has the same value."""
        for typ, sub in subs:
            if typ not in RESIDUAL or len(sub) < 4:
                continue
            (fid,) = struct.unpack_from("<I", sub, 0)
            owner, oid = tes4.resolve(fid, masters, name)
            if owner.lower() not in own or (typ, fid) in agreed:
                continue
            stats["residual"] += 1
            rows.append({"plugin": name, "npc": npc, "source": owner, "changed": "",
                         "note": f"{typ} 仍指向 {owner}:{oid:06X}，和來源不一致（沒有更動）"})

    def fix(rec: tes4.Record) -> tes4.Record:
        owner, oid = tes4.resolve(rec.form_id, masters, name)
        npc = f"{owner}:{oid:06X}"
        subs = list(tes4.iter_subrecords(rec.payload()))
        src = pick((owner.lower(), oid))
        if src is None:
            residual(npc, subs, set())
            return rec
        donor: list[tuple[str, bytes]] = []
        for typ, sub in src.npcs[(owner.lower(), oid)]:
            if typ not in GROUP_OF:
                continue
            if typ in FORMID_AT_0 and len(sub) >= 4:
                fid = remap(struct.unpack_from("<I", sub, 0)[0], src, masters, name)
                if fid is None:
                    stats["skipped"] += 1
                    rows.append({"plugin": name, "npc": npc, "source": src.name, "changed": "",
                                 "note": f"{typ} 指向的插件不在補丁的前置清單裡，這筆沒有更動"})
                    residual(npc, subs, set())
                    return rec
                sub = struct.pack("<I", fid) + sub[4:]
            donor.append((typ, sub))
        agreed = set()
        for typ, sub in src.npcs[(owner.lower(), oid)]:
            if typ in RESIDUAL and len(sub) >= 4:
                fid = remap(struct.unpack_from("<I", sub, 0)[0], src, masters, name)
                if fid is not None:
                    agreed.add((typ, fid))
        new_subs = merged(subs, donor)
        residual(npc, new_subs, agreed)
        if new_subs == subs:
            stats["same"] += 1
            return rec
        stats["changed"] += 1
        changed = sorted({"TINT" if t in TINT else t for t in GROUP_OF
                          if [x for x in subs if x[0] == t] != [x for x in new_subs if x[0] == t]})
        rows.append({"plugin": name, "npc": npc, "source": src.name, "changed": " ".join(changed), "note": ""})
        return rec.replace_payload(tes4.build_subrecords(new_subs))

    def walk(group_items: list) -> None:
        for i, item in enumerate(group_items):
            if isinstance(item, tes4.Group):
                walk(item.items)
            elif item.type == "NPC_":
                group_items[i] = fix(item)

    walk(items)
    if not stats["changed"]:
        return None, rows, stats
    return tes4.serialize_plugin(head, items), rows, stats


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="NPC 補丁的外觀改用我們裝的外觀 mod 的值（預設試跑；請先關閉 MO2）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--plugin", action="append", required=True, help="要修正的 NPC 補丁（名稱或檔案路徑，可重複）")
    ap.add_argument("--from", dest="sources", action="append", required=True,
                    help="提供外觀的插件（名稱或檔案路徑，可重複），例如 NITHI 的 Women、Men")
    ap.add_argument("--out", type=Path, required=True, help="寫出修正版的 mod 資料夾（要放在原 mod 之上）")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    rep = Report("forward_appearance")
    rep.add("mode", "INFO", "模式", "實際執行" if args.apply else "試跑（加 --apply 才會寫入）")
    providers = None
    if not all(Path(v).is_file() for v in args.plugin + args.sources):
        prof = vfs.open_profile(args.pm, args.profile)
        providers = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, prof.game_dir / "Data")
    sources: list[Source] = []
    for value in args.sources:
        path = locate(value, providers)
        if path is None:
            rep.add(f"from:{value}", "FAIL", "找不到外觀來源", f"{value}（mod 未啟用或名稱錯誤）")
            continue
        try:
            sources.append(load_source(path))
        except (tes4.PluginError, OSError, ValueError) as e:
            rep.add(f"from:{value}", "FAIL", "外觀來源無法讀取", f"{path.name}：{e}")
            continue
        rep.add(f"from:{path.name}", "INFO", "外觀來源", f"{path.name}（{path.parent.name}）：NPC {len(sources[-1].npcs)} 筆")
    if len(sources) != len(args.sources):
        return finish(rep, [], args.report_dir)
    out_dir = args.out
    all_rows: list[dict] = []
    for value in dict.fromkeys(args.plugin):
        src = locate(value, providers)
        name = src.name if src else value
        key = f"src:{name}"
        if src is None:
            rep.add(key, "FAIL", name, "找不到插件（mod 未啟用或名稱錯誤）")
            continue
        in_out = src.parent.resolve() == out_dir.resolve()
        try:
            new, rows, st = forward(src.read_bytes(), src.name, sources)
        except (tes4.PluginError, OSError, ValueError) as e:
            rep.add(key, "FAIL", name, f"無法處理：{e}")
            continue
        all_rows += rows
        extra = []
        if st["skipped"]:
            extra.append(f"{st['skipped']} 筆因前置不同沒有更動")
        if st["ambiguous"]:
            extra.append(f"{st['ambiguous']} 筆在多個來源裡都有（用載入順序較後的）")
        if st["residual"]:
            extra.append(f"{st['residual']} 個其他欄位仍指向來源自己的記錄且不一致（見 csv）")
        if extra:
            rep.add(f"warn:{name}", "WARN", f"{name} 需要注意", "；".join(extra))
        if new is None:
            what = f"外觀都和來源一致（{st['same']} 筆）"
            rep.add(key, "PASS", name, (f"已修正：生效的是 {out_dir.name} 裡的版本，" if in_out else "")
                    + what + ("" if in_out else f"（來源：{src.parent.name}）"))
            continue
        kinds: dict[str, int] = {}
        for r in rows:
            for t in r["changed"].split():
                kinds[t] = kinds.get(t, 0) + 1
        detail = (f"{st['changed']} 筆 NPC 的外觀改用來源的值（{', '.join(f'{k} {v}' for k, v in sorted(kinds.items()))}）；"
                  f"已一致 {st['same']} 筆；來源：{src.parent.name}" + ("（原地更新修正版）" if in_out else ""))
        write_fixed(rep, key, name, detail, new, out_dir / src.name, args.apply)
    return finish(rep, all_rows, args.report_dir)


def finish(rep: Report, rows: list[dict], out: Path) -> int:
    write_csv(out / "forward_appearance.csv", rows, FIELDS)
    rep.data = {"rows": rows}
    path = rep.save(out, stem="forward_appearance")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
