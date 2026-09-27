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


def test_already_fixed_copy_is_skipped(tmp_path):
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
