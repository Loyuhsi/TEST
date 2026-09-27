"""strip_refs: drop NPC package/item references to forms the new master no longer defines."""

import os
import struct
import zlib
from pathlib import Path

import strip_refs
from pm import mo2, tes4
from pm.report import read_csv


def sub(t: bytes, data: bytes) -> bytes:
    return t + struct.pack("<H", len(data)) + data


def fid(v: int) -> bytes:
    return struct.pack("<I", v)


def rec(typ: bytes, form_id: int, payload: bytes, compress=False) -> bytes:
    flags = 0
    if compress:
        payload = struct.pack("<I", len(payload)) + zlib.compress(payload)
        flags = tes4.FLAG_COMPRESSED
    return typ + struct.pack("<IIIIHH", len(payload), flags, form_id, 0, 44, 0) + payload


def grup(label: bytes, body: bytes) -> bytes:
    return b"GRUP" + struct.pack("<I", 24 + len(body)) + label + struct.pack("<IHHHH", 0, 0, 0, 0, 0) + body


def write(path: Path, masters: list[str], body: bytes, flags=0) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(tes4.build_header(path.name, masters=masters, flags=flags) + body)
    return path


NPC_A = (sub(b"EDID", b"LotdCurator\x00") + sub(b"PKID", fid(0x01000801)) + sub(b"PKID", fid(0x01000900))
         + sub(b"COCT", fid(2)) + sub(b"CNTO", fid(0x01000801) + fid(1)) + sub(b"CNTO", fid(0x01000901) + fid(3))
         + sub(b"COED", b"\x00" * 12) + sub(b"FULL", b"Auryen\x00"))
NPC_B = sub(b"EDID", b"Other\x00") + sub(b"PKID", fid(0x01000902)) + sub(b"PKID", fid(0x00000123))


def world(tmp_path):
    pm = tmp_path / "PM"
    mods = pm / "mods"
    write(mods / "LOTD" / "LOTD.esm", ["Skyrim.esm"],
          grup(b"NPC_", rec(b"NPC_", 0x01000800, sub(b"EDID", b"a\x00")) + rec(b"PACK", 0x01000801, b"")),
          flags=tes4.FLAG_MASTER)
    body = (grup(b"NPC_", rec(b"NPC_", 0x01000800, NPC_A) + rec(b"NPC_", 0x01000810, NPC_B, compress=True))
            + grup(b"MISC", rec(b"MISC", 0x02000800, sub(b"EDID", b"m\x00"))))
    write(mods / "Modpocalypse" / "Patch.esp", ["Skyrim.esm", "LOTD.esm"], body)
    write(mods / "Clean" / "Clean.esp", ["Skyrim.esm", "LOTD.esm"],
          grup(b"NPC_", rec(b"NPC_", 0x01000800, sub(b"PKID", fid(0x01000801)))))
    (pm / "STOCK GAME" / "Data").mkdir(parents=True)
    pdir = pm / "profiles" / "Pages-ZH"
    pdir.mkdir(parents=True)
    mo2.write_modlist(pdir / "modlist.txt", [mo2.ModEntry(n, "+") for n in ("Fix", "Clean", "Modpocalypse", "LOTD")])
    mo2.write_plugins(pdir / "plugins.txt", [mo2.PluginEntry(n, True) for n in ("LOTD.esm", "Patch.esp", "Clean.esp")])
    return pm


def run(tmp_path, pm, *extra) -> int:
    return strip_refs.main(["--pm", str(pm), "--master", "LOTD.esm", "--out", str(pm / "mods" / "Fix"),
                            "--report-dir", str(tmp_path / "reports"), *extra])


def subs_of(path: Path, form_id: int):
    _h, items = tes4.parse_plugin(path.read_bytes(), path.name)
    r = next(r for r in tes4.walk_records(items) if r.form_id == form_id)
    return list(tes4.iter_subrecords(r.payload())), r


def test_dry_run_reports_and_writes_nothing(tmp_path):
    pm = world(tmp_path)
    assert run(tmp_path, pm, "--plugin", "Patch.esp") == 0
    assert not (pm / "mods" / "Fix" / "Patch.esp").exists()
    rows = read_csv(tmp_path / "reports" / "strip_refs.csv")
    assert {(r["record"], r["subrecord"], r["target"]) for r in rows} == {
        ("NPC_ LOTD.esm:000800", "PKID", "LOTD.esm:000900"),
        ("NPC_ LOTD.esm:000800", "CNTO", "LOTD.esm:000901"),
        ("NPC_ LOTD.esm:000800", "COED", ""),
        ("NPC_ LOTD.esm:000810", "PKID", "LOTD.esm:000902")}


def test_apply_writes_a_fixed_same_name_copy(tmp_path):
    pm = world(tmp_path)
    src = pm / "mods" / "Modpocalypse" / "Patch.esp"
    before = src.read_bytes()
    assert run(tmp_path, pm, "--plugin", "Patch.esp", "--apply") == 0
    assert src.read_bytes() == before                                   # original untouched
    out = pm / "mods" / "Fix" / "Patch.esp"
    subs, r = subs_of(out, 0x01000800)
    assert [t for t, _ in subs] == ["EDID", "PKID", "COCT", "CNTO", "FULL"]
    assert dict(subs)["PKID"] == fid(0x01000801) and dict(subs)["COCT"] == fid(1)
    assert dict(subs)["CNTO"] == fid(0x01000801) + fid(1)
    subs_b, rb = subs_of(out, 0x01000810)                               # compressed record rewritten plainly
    assert [d for t, d in subs_b if t == "PKID"] == [fid(0x00000123)]
    assert not rb.flags & tes4.FLAG_COMPRESSED
    h = tes4.read_header(out)
    assert h.masters == ["Skyrim.esm", "LOTD.esm"]
    assert [t for t, _f, _i in tes4.iter_records(out.read_bytes())] == ["NPC_", "NPC_", "MISC"]
    misc = lambda b: b[b.index(b"MISC", 60):]                          # noqa: E731
    assert misc(out.read_bytes()) == misc(before)                        # untouched group kept byte for byte


def test_clean_plugin_is_left_alone(tmp_path):
    pm = world(tmp_path)
    assert run(tmp_path, pm, "--plugin", "Clean.esp", "--apply") == 0
    assert not (pm / "mods" / "Fix" / "Clean.esp").exists()


def test_already_fixed_copy_is_left_as_is(tmp_path):
    pm = world(tmp_path)
    assert run(tmp_path, pm, "--plugin", "Patch.esp", "--apply") == 0
    fixed = (pm / "mods" / "Fix" / "Patch.esp").read_bytes()
    assert run(tmp_path, pm, "--plugin", "Patch.esp", "--apply") == 0   # the Fix mod now wins
    assert (pm / "mods" / "Fix" / "Patch.esp").read_bytes() == fixed
    assert "已修正" in (tmp_path / "reports" / "strip_refs.txt").read_text(encoding="utf-8")


def test_hardlinked_output_is_not_overwritten(tmp_path):
    pm = world(tmp_path)
    (pm / "mods" / "Fix").mkdir()
    os.link(pm / "mods" / "Clean" / "Clean.esp", pm / "mods" / "Fix" / "Patch.esp")
    mo2.write_modlist(pm / "profiles" / "Pages-ZH" / "modlist.txt",
                      [mo2.ModEntry(n, "+") for n in ("Clean", "Modpocalypse", "LOTD")])  # Fix not active
    assert run(tmp_path, pm, "--plugin", "Patch.esp", "--apply") == 1
    assert (pm / "mods" / "Fix" / "Patch.esp").read_bytes() == (pm / "mods" / "Clean" / "Clean.esp").read_bytes()


def test_missing_plugin_fails(tmp_path):
    pm = world(tmp_path)
    assert run(tmp_path, pm, "--plugin", "Nope.esp") == 1


def test_tree_round_trip_keeps_bytes(tmp_path):
    pm = world(tmp_path)
    data = (pm / "mods" / "Modpocalypse" / "Patch.esp").read_bytes()
    head, items = tes4.parse_plugin(data)
    assert tes4.serialize_plugin(head, items) == data


def test_big_subrecords_use_xxxx():
    big = b"\x01" * 70000
    out = tes4.build_subrecords([("EDID", b"x\x00"), ("DATA", big)])
    assert list(tes4.iter_subrecords(out)) == [("EDID", b"x\x00"), ("DATA", big)]


# ---------------------------------------------------------------- --drop-missing
def cell_children(cell_id: int, body: bytes) -> bytes:
    return b"GRUP" + struct.pack("<I", 24 + len(body)) + fid(cell_id) + struct.pack("<IHHHH", 6, 0, 0, 0, 0) + body


def mismatch_world(tmp_path):
    pm = tmp_path / "PM"
    mods = pm / "mods"
    # old master (1.70 header): defines 0x800 and 0x950 only
    write(mods / "TGTK" / "TGTK.esp", ["Skyrim.esm"],
          grup(b"STAT", rec(b"STAT", 0x01000800, b"") + rec(b"STAT", 0x01000950, b"")))
    body = (grup(b"CELL",
                 rec(b"CELL", 0x000139D1, sub(b"EDID", b"KarthwastenHall\x00"))          # Skyrim cell: official
                 + cell_children(0x000139D1,
                                 rec(b"REFR", 0x01000800, sub(b"NAME", fid(0x01000999)))  # exists: kept (base missing)
                                 + rec(b"REFR", 0x01000429, b"")                           # below 0x800: gone
                                 + rec(b"REFR", 0x01000900, b""))                          # not in master: gone
                 + rec(b"CELL", 0x01000A00, b"")                                           # cell not in master
                 + cell_children(0x01000A00, rec(b"REFR", 0x02000800, b"")))               # goes with its cell
            + grup(b"NPC_", rec(b"NPC_", 0x0100009C, b""))                                 # whole group emptied
            + grup(b"STAT", rec(b"STAT", 0x00000123, b"")))                                # Skyrim.esm: not checked
    p = mods / "Snazzy" / "Patch.esp"
    p.parent.mkdir(parents=True, exist_ok=True)
    head = tes4.build_header(p.name, masters=["Skyrim.esm", "TGTK.esp"], flags=tes4.FLAG_LIGHT, hedr_version=1.71,
                             num_records=tes4.count_items(tes4.parse_items(body, 0, len(body))))
    p.write_bytes(head + body)
    (pm / "STOCK GAME" / "Data").mkdir(parents=True)
    pdir = pm / "profiles" / "Pages-ZH"
    pdir.mkdir(parents=True)
    mo2.write_modlist(pdir / "modlist.txt", [mo2.ModEntry(n, "+") for n in ("Fix2", "Snazzy", "TGTK")])
    mo2.write_plugins(pdir / "plugins.txt", [mo2.PluginEntry(n, True) for n in ("TGTK.esp", "Patch.esp")])
    return pm


def run_drop(tmp_path, pm, *extra) -> int:
    return strip_refs.main(["--pm", str(pm), "--drop-missing", "--out", str(pm / "mods" / "Fix2"),
                            "--report-dir", str(tmp_path / "reports"), *extra])


def test_drop_missing_removes_overrides_of_records_the_master_lacks(tmp_path):
    pm = mismatch_world(tmp_path)
    assert run_drop(tmp_path, pm, "--plugin", "Patch.esp", "--apply") == 0
    out = pm / "mods" / "Fix2" / "Patch.esp"
    data = out.read_bytes()
    kept = [(t, i) for t, _f, i in tes4.iter_records(data)]
    assert kept == [("CELL", 0x000139D1), ("REFR", 0x01000800), ("STAT", 0x00000123)]
    rows = read_csv(tmp_path / "reports" / "strip_refs.csv")
    assert {r["record"] for r in rows} == {"REFR TGTK.esp:000429", "REFR TGTK.esp:000900",
                                           "CELL TGTK.esp:000A00", "NPC_ TGTK.esp:00009C"}
    assert next(r for r in rows if r["record"].startswith("CELL"))["target"] == "含子記錄 1 筆"
    h = tes4.read_header(out)
    assert h.num_records == tes4.count_items(tes4.parse_plugin(data)[1]) and h.is_light
    assert h.masters == ["Skyrim.esm", "TGTK.esp"]


def test_drop_missing_reads_the_plugin_list_from_csv(tmp_path):
    pm = mismatch_world(tmp_path)
    csv_path = tmp_path / "mismatch.csv"
    csv_path.write_text("plugin,master\nPatch.esp,TGTK.esp\n", encoding="utf-8")
    assert run_drop(tmp_path, pm, "--from-csv", str(csv_path)) == 0      # dry run
    assert not (pm / "mods" / "Fix2" / "Patch.esp").exists()
    text = (tmp_path / "reports" / "strip_refs.txt").read_text(encoding="utf-8")
    assert "刪除 4 筆覆寫不存在記錄的記錄" in text


def test_drop_missing_leaves_consistent_plugins_alone(tmp_path):
    pm = mismatch_world(tmp_path)
    ok = pm / "mods" / "Snazzy" / "Fine.esp"
    ok.write_bytes(tes4.build_header(ok.name, masters=["Skyrim.esm", "TGTK.esp"])
                   + grup(b"STAT", rec(b"STAT", 0x01000950, b"")))
    mo2.write_plugins(pm / "profiles" / "Pages-ZH" / "plugins.txt",
                      [mo2.PluginEntry(n, True) for n in ("TGTK.esp", "Patch.esp", "Fine.esp")])
    assert run_drop(tmp_path, pm, "--plugin", "Fine.esp", "--apply") == 0
    assert not (pm / "mods" / "Fix2" / "Fine.esp").exists()


# ---------------------------------------------------------------- --drop-unresolved-base
def base_world(tmp_path):
    pm = tmp_path / "PM"
    mods = pm / "mods"
    write(mods / "LOTD" / "LOTD.esm", ["Skyrim.esm"],
          grup(b"STAT", rec(b"STAT", 0x01000800, b"") + rec(b"STAT", 0x01000950, b"")), flags=tes4.FLAG_MASTER)
    name = lambda base: sub(b"EDID", b"r\x00") + sub(b"NAME", fid(base)) + sub(b"DATA", b"\x00" * 24)  # noqa: E731
    body = (grup(b"STAT", rec(b"STAT", 0x02000900, b""))                                   # own base object
            + grup(b"CELL",
                   rec(b"CELL", 0x000139D1, b"")
                   + cell_children(0x000139D1,
                                   rec(b"REFR", 0x02000800, name(0x01000800))              # base exists: kept
                                   + rec(b"REFR", 0x02000801, name(0x01000900))            # base missing: gone
                                   + rec(b"ACHR", 0x01000950, name(0x01000990), compress=True)  # override: gone
                                   + rec(b"REFR", 0x02000802, name(0x00000123))            # Skyrim base: kept
                                   + rec(b"REFR", 0x02000803, name(0x02000900)))           # own base: kept
                   + rec(b"CELL", 0x02000A00, b"")
                   + cell_children(0x02000A00, rec(b"REFR", 0x02000804, name(0x01000901)))))  # group emptied
    p = mods / "Hub" / "Hub.esp"
    p.parent.mkdir(parents=True, exist_ok=True)
    head = tes4.build_header(p.name, masters=["Skyrim.esm", "LOTD.esm"],
                             num_records=tes4.count_items(tes4.parse_items(body, 0, len(body))))
    p.write_bytes(head + body)
    (pm / "STOCK GAME" / "Data").mkdir(parents=True)
    pdir = pm / "profiles" / "Pages-ZH"
    pdir.mkdir(parents=True)
    mo2.write_modlist(pdir / "modlist.txt", [mo2.ModEntry(n, "+") for n in ("Fix3", "Hub", "LOTD")])
    mo2.write_plugins(pdir / "plugins.txt", [mo2.PluginEntry(n, True) for n in ("LOTD.esm", "Hub.esp")])
    return pm


def test_drop_unresolved_base_removes_references_to_missing_base_objects(tmp_path):
    pm = base_world(tmp_path)
    csv_path = tmp_path / "unresolved.csv"
    csv_path.write_text("plugin,record,field\nHub.esp,REFR:1,NAME\nHub.esp,REFR:2,NAME\n", encoding="utf-8-sig")
    args = ["--pm", str(pm), "--drop-unresolved-base", "--from-csv", str(csv_path),
            "--out", str(pm / "mods" / "Fix3"), "--report-dir", str(tmp_path / "reports")]
    assert strip_refs.main(args) == 0                                    # dry run
    assert not (pm / "mods" / "Fix3" / "Hub.esp").exists()
    text = (tmp_path / "reports" / "strip_refs.txt").read_text(encoding="utf-8")
    assert "刪除 3 筆基底物件不存在的放置記錄" in text
    assert len(read_csv(tmp_path / "reports" / "strip_refs.csv")) == 3   # the plugin listed twice runs once
    assert strip_refs.main(args + ["--apply"]) == 0
    out = pm / "mods" / "Fix3" / "Hub.esp"
    data = out.read_bytes()
    kept = [(t, i) for t, _f, i in tes4.iter_records(data)]
    assert kept == [("STAT", 0x02000900), ("CELL", 0x000139D1), ("REFR", 0x02000800), ("REFR", 0x02000802),
                    ("REFR", 0x02000803), ("CELL", 0x02000A00)]
    rows = read_csv(tmp_path / "reports" / "strip_refs.csv")
    assert {(r["record"], r["subrecord"], r["target"]) for r in rows} == {
        ("REFR Hub.esp:000801", "NAME", "LOTD.esm:000900"),
        ("ACHR LOTD.esm:000950", "NAME", "LOTD.esm:000990"),
        ("REFR Hub.esp:000804", "NAME", "LOTD.esm:000901")}
    h = tes4.read_header(out)
    assert h.num_records == tes4.count_items(tes4.parse_plugin(data)[1])


def test_drop_unresolved_base_alone_keeps_overrides_of_missing_records(tmp_path):
    pm = mismatch_world(tmp_path)
    assert run_drop(tmp_path, pm, "--plugin", "Patch.esp") == 0          # --drop-missing only: REFR 800 stays
    rows = read_csv(tmp_path / "reports" / "strip_refs.csv")
    assert "REFR TGTK.esp:000800" not in {r["record"] for r in rows}
    assert strip_refs.main(["--pm", str(pm), "--drop-unresolved-base", "--plugin", "Patch.esp",
                            "--out", str(pm / "mods" / "Fix2"), "--report-dir", str(tmp_path / "reports")]) == 0
    rows = read_csv(tmp_path / "reports" / "strip_refs.csv")
    assert [(r["record"], r["subrecord"]) for r in rows] == [("REFR TGTK.esp:000800", "NAME")]


def test_both_modes_together(tmp_path):
    pm = mismatch_world(tmp_path)
    assert run_drop(tmp_path, pm, "--drop-unresolved-base", "--plugin", "Patch.esp", "--apply") == 0
    kept = [(t, i) for t, _f, i in tes4.iter_records((pm / "mods" / "Fix2" / "Patch.esp").read_bytes())]
    assert kept == [("CELL", 0x000139D1), ("STAT", 0x00000123)]          # emptied cell children group removed
    text = (tmp_path / "reports" / "strip_refs.txt").read_text(encoding="utf-8")
    assert "刪除 4 筆覆寫不存在記錄的記錄、1 筆基底物件不存在的放置記錄" in text


def test_fixed_copy_in_out_is_updated_in_place(tmp_path):
    pm = mismatch_world(tmp_path)
    assert run_drop(tmp_path, pm, "--plugin", "Patch.esp", "--apply") == 0
    fixed = pm / "mods" / "Fix2" / "Patch.esp"                           # now the winning copy
    base = ["--pm", str(pm), "--drop-unresolved-base", "--plugin", "Patch.esp",
            "--out", str(pm / "mods" / "Fix2"), "--report-dir", str(tmp_path / "reports")]
    assert strip_refs.main(base + ["--apply"]) == 0
    assert [(t, i) for t, _f, i in tes4.iter_records(fixed.read_bytes())] == [("CELL", 0x000139D1),
                                                                              ("STAT", 0x00000123)]
    assert "原地更新" in (tmp_path / "reports" / "strip_refs.txt").read_text(encoding="utf-8")
    before = fixed.read_bytes()
    assert strip_refs.main(base + ["--apply"]) == 0                      # nothing left to change
    assert fixed.read_bytes() == before
    assert "已修正" in (tmp_path / "reports" / "strip_refs.txt").read_text(encoding="utf-8")


def test_hardlinked_copy_in_out_is_not_updated(tmp_path):
    pm = mismatch_world(tmp_path)
    assert run_drop(tmp_path, pm, "--plugin", "Patch.esp", "--apply") == 0
    fixed = pm / "mods" / "Fix2" / "Patch.esp"
    os.link(fixed, tmp_path / "elsewhere.esp")
    before = fixed.read_bytes()
    assert strip_refs.main(["--pm", str(pm), "--drop-unresolved-base", "--plugin", "Patch.esp", "--apply",
                            "--out", str(pm / "mods" / "Fix2"), "--report-dir", str(tmp_path / "reports")]) == 1
    assert fixed.read_bytes() == before
