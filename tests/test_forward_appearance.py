"""forward_appearance: NPC patch keeps its AI data but takes appearance fields from the installed appearance mod."""

import os
import struct
from pathlib import Path

import forward_appearance as fa
from pm import mo2, tes4
from pm.report import read_csv


def sub(t: bytes, data: bytes) -> bytes:
    return t + struct.pack("<H", len(data)) + data


def fid(v: int) -> bytes:
    return struct.pack("<I", v)


def rec(typ: bytes, form_id: int, payload: bytes) -> bytes:
    return typ + struct.pack("<IIIIHH", len(payload), 0, form_id, 0, 44, 0) + payload


def grup(label: bytes, body: bytes) -> bytes:
    return b"GRUP" + struct.pack("<I", 24 + len(body)) + label + struct.pack("<IHHHH", 0, 0, 0, 0, 0) + body


def write(path: Path, masters: list[str], body: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(tes4.build_header(path.name, masters=masters) + body)
    return path


def f32(v: float) -> bytes:
    return struct.pack("<f", v)


def tint(i: int, color: int) -> bytes:
    return (sub(b"TINI", struct.pack("<H", i)) + sub(b"TINC", struct.pack("<I", color))
            + sub(b"TINV", struct.pack("<i", 50)) + sub(b"TIAS", struct.pack("<h", -1)))


# NITHI (masters Base.esm, Extra.esm -> its own records are 0x02......)
NITHI_900 = (sub(b"EDID", b"Nepos\x00") + sub(b"ACBS", b"\x00" * 24) + sub(b"RNAM", fid(0x00000100))
             + sub(b"WNAM", fid(0x02000800)) + sub(b"AIDT", b"\x00" * 12)
             + sub(b"PNAM", fid(0x02000801)) + sub(b"PNAM", fid(0x02000802)) + sub(b"HCLF", fid(0x00000200))
             + sub(b"NAM6", f32(1.05)) + sub(b"NAM7", f32(40.0)) + sub(b"DOFT", fid(0x02000804))
             + sub(b"FTST", fid(0x02000803)) + sub(b"QNAM", f32(0.5) * 4) + sub(b"NAM9", f32(0.1) * 19)
             + sub(b"NAMA", struct.pack("<4i", 1, -1, 2, 3)) + tint(10, 0xAABBCC) + tint(11, 0x112233))
NITHI_902 = sub(b"EDID", b"Other\x00") + sub(b"RNAM", fid(0x00000100)) + sub(b"HCLF", fid(0x01000123))

# the patch was made for another NITHI variant: its NITHI references (index 3 here) are shifted
PATCH_900 = (sub(b"EDID", b"Nepos\x00") + sub(b"ACBS", b"\x01" * 24) + sub(b"RNAM", fid(0x00000100))
             + sub(b"WNAM", fid(0x03000805)) + sub(b"ANAM", fid(0x03000808)) + sub(b"AIDT", b"\x07" * 12)
             + sub(b"PKID", fid(0x01000900)) + sub(b"PNAM", fid(0x03000806))
             + sub(b"NAM6", f32(1.0)) + sub(b"NAM7", f32(40.0)) + sub(b"DOFT", fid(0x03000807))
             + sub(b"FTST", fid(0x03000809)) + sub(b"NAM9", f32(0.1) * 19)
             + sub(b"NAMA", struct.pack("<4i", 1, -1, 2, 3)) + tint(10, 0x000000))
PATCH_902 = sub(b"EDID", b"Other\x00") + sub(b"RNAM", fid(0x00000100)) + sub(b"AIDT", b"\x07" * 12)
PATCH_903 = sub(b"EDID", b"Guard\x00") + sub(b"DOFT", fid(0x03000900))          # not in NITHI


def world(tmp_path):
    pm = tmp_path / "PM"
    mods = pm / "mods"
    write(mods / "Base" / "Base.esm", [], b"")
    write(mods / "Extra" / "Extra.esm", [], b"")
    write(mods / "Extra2" / "Extra2.esm", [], b"")
    write(mods / "AIO" / "AIOverhaul.esp", ["Base.esm"], b"")
    write(mods / "NITHI" / "NITHI.esp", ["Base.esm", "Extra.esm"],
          grup(b"NPC_", rec(b"NPC_", 0x00000900, NITHI_900) + rec(b"NPC_", 0x00000902, NITHI_902)))
    write(mods / "Hub" / "Patch.esp", ["Base.esm", "AIOverhaul.esp", "Extra2.esm", "NITHI.esp"],
          grup(b"NPC_", rec(b"NPC_", 0x00000900, PATCH_900) + rec(b"NPC_", 0x00000902, PATCH_902)
               + rec(b"NPC_", 0x00000903, PATCH_903)))
    (pm / "STOCK GAME" / "Data").mkdir(parents=True)
    pdir = pm / "profiles" / "Pages-ZH"
    pdir.mkdir(parents=True)
    mo2.write_modlist(pdir / "modlist.txt",
                      [mo2.ModEntry(n, "+") for n in ("Fix", "Hub", "NITHI", "AIO", "Extra2", "Extra", "Base")])
    mo2.write_plugins(pdir / "plugins.txt", [mo2.PluginEntry(n, True) for n in
                                             ("Base.esm", "Extra.esm", "Extra2.esm", "AIOverhaul.esp", "NITHI.esp",
                                              "Patch.esp")])
    return pm


def run(tmp_path, pm, *extra) -> int:
    return fa.main(["--pm", str(pm), "--plugin", "Patch.esp", "--from", "NITHI.esp",
                    "--out", str(pm / "mods" / "Fix"), "--report-dir", str(tmp_path / "reports"), *extra])


def npc(path: Path, form_id: int) -> tuple[list[tuple[str, bytes]], bytes]:
    _h, items = tes4.parse_plugin(path.read_bytes(), path.name)
    r = next(r for r in tes4.walk_records(items) if r.form_id == form_id)
    return list(tes4.iter_subrecords(r.payload())), r.to_bytes()


def report(tmp_path) -> str:
    return (tmp_path / "reports" / "forward_appearance.txt").read_text(encoding="utf-8")


def test_dry_run_reports_and_writes_nothing(tmp_path):
    pm = world(tmp_path)
    assert run(tmp_path, pm) == 0
    assert not (pm / "mods" / "Fix" / "Patch.esp").exists()
    rows = read_csv(tmp_path / "reports" / "forward_appearance.csv")
    changed = next(r for r in rows if r["changed"])
    assert changed["npc"] == "Base.esm:000900" and changed["source"] == "NITHI.esp"
    assert changed["changed"].split() == ["ANAM", "FTST", "HCLF", "NAM6", "PNAM", "QNAM", "TINT", "WNAM"]
    assert "1 筆 NPC 的外觀改用來源的值" in report(tmp_path)


def test_apply_forwards_appearance_and_keeps_ai_data(tmp_path):
    pm = world(tmp_path)
    src = pm / "mods" / "Hub" / "Patch.esp"
    before = src.read_bytes()
    assert run(tmp_path, pm, "--apply") == 0
    assert src.read_bytes() == before                                   # original untouched
    out = pm / "mods" / "Fix" / "Patch.esp"
    subs, _ = npc(out, 0x00000900)
    assert [t for t, _ in subs] == ["EDID", "ACBS", "RNAM", "WNAM", "AIDT", "PKID", "PNAM", "PNAM", "HCLF",
                                    "NAM6", "NAM7", "DOFT", "FTST", "QNAM", "NAM9", "NAMA",
                                    "TINI", "TINC", "TINV", "TIAS", "TINI", "TINC", "TINV", "TIAS"]
    d = dict(subs)
    assert d["WNAM"] == fid(0x03000800) and d["FTST"] == fid(0x03000803)   # NITHI's own records, patch index 3
    assert [v for t, v in subs if t == "PNAM"] == [fid(0x03000801), fid(0x03000802)]
    assert d["HCLF"] == fid(0x00000200) and d["NAM6"] == f32(1.05)
    assert d["AIDT"] == b"\x07" * 12 and d["PKID"] == fid(0x01000900)     # the patch's AI data stays
    assert d["ACBS"] == b"\x01" * 24 and d["DOFT"] == fid(0x03000807)
    assert "ANAM" not in d                                               # NITHI has none
    assert npc(out, 0x00000902)[1] == npc(src, 0x00000902)[1]            # could not be remapped: untouched
    assert npc(out, 0x00000903)[1] == npc(src, 0x00000903)[1]            # not in NITHI: untouched
    h = tes4.read_header(out)
    assert h.masters == ["Base.esm", "AIOverhaul.esp", "Extra2.esm", "NITHI.esp"]
    assert h.num_records == tes4.read_header(src).num_records


def test_warnings_for_unmappable_and_leftover_references(tmp_path):
    pm = world(tmp_path)
    assert run(tmp_path, pm) == 0
    rows = read_csv(tmp_path / "reports" / "forward_appearance.csv")
    notes = {(r["npc"], r["note"].split(" ")[0]) for r in rows if r["note"]}
    assert ("Base.esm:000902", "HCLF") in notes                          # Extra.esm is not a master of the patch
    assert ("Base.esm:000900", "DOFT") in notes                          # 807 disagrees with NITHI's 804
    assert ("Base.esm:000903", "DOFT") in notes                          # points into NITHI, nothing to compare
    assert "1 筆因前置不同沒有更動" in report(tmp_path)
    assert "2 個其他欄位仍指向來源自己的記錄且不一致" in report(tmp_path)


def test_fixed_copy_is_checked_again_in_place(tmp_path):
    pm = world(tmp_path)
    assert run(tmp_path, pm, "--apply") == 0
    out = pm / "mods" / "Fix" / "Patch.esp"                              # now the winning copy
    fixed = out.read_bytes()
    assert run(tmp_path, pm, "--apply") == 0
    assert out.read_bytes() == fixed
    assert "已修正" in report(tmp_path)


def test_hardlinked_output_is_not_overwritten(tmp_path):
    pm = world(tmp_path)
    (pm / "mods" / "Fix").mkdir()
    os.link(pm / "mods" / "AIO" / "AIOverhaul.esp", pm / "mods" / "Fix" / "Patch.esp")
    mo2.write_modlist(pm / "profiles" / "Pages-ZH" / "modlist.txt",
                      [mo2.ModEntry(n, "+") for n in ("Hub", "NITHI", "AIO", "Extra2", "Extra", "Base")])
    assert run(tmp_path, pm, "--apply") == 1
    assert (pm / "mods" / "Fix" / "Patch.esp").read_bytes() == (pm / "mods" / "AIO" / "AIOverhaul.esp").read_bytes()


def test_missing_source_fails(tmp_path):
    pm = world(tmp_path)
    assert fa.main(["--pm", str(pm), "--plugin", "Patch.esp", "--from", "Nope.esp",
                    "--out", str(pm / "mods" / "Fix"), "--report-dir", str(tmp_path / "reports")]) == 1


def test_later_source_wins_when_two_have_the_npc():
    early = fa.Source("Men.esp", ["Base.esm"], {("base.esm", 0x900): [("WNAM", fid(0x01000800))]})
    late = fa.Source("Women.esp", ["Base.esm"], {("base.esm", 0x900): [("WNAM", fid(0x01000801))]})
    data = (tes4.build_header("P.esp", masters=["Base.esm", "Men.esp", "Women.esp"])
            + grup(b"NPC_", rec(b"NPC_", 0x00000900, sub(b"EDID", b"x\x00") + sub(b"WNAM", fid(0x01000999)))))
    new, _rows, st = fa.forward(data, "P.esp", [late, early])
    _h, items = tes4.parse_plugin(new, "P.esp")
    r = next(tes4.walk_records(items))
    assert dict(tes4.iter_subrecords(r.payload()))["WNAM"] == fid(0x02000801)
    assert st["ambiguous"] == 1
