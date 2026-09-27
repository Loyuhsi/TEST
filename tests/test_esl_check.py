"""esl_check: record summaries, whether the light flag fits as is, and setting it on outputs only."""

import os
import struct
from pathlib import Path

import pytest

import esl_check
from pm import mo2, tes4
from pm.report import read_csv


def rec(typ: bytes, form_id: int, data: bytes = b"\x00" * 4, flags: int = 0) -> bytes:
    return typ + struct.pack("<IIIIHH", len(data), flags, form_id, 0, 44, 0) + data


def grup(label: bytes, body: bytes, gtype: int = 0) -> bytes:
    return b"GRUP" + struct.pack("<I", 24 + len(body)) + label + struct.pack("<IHHHH", gtype, 0, 0, 0, 0) + body


def plugin(path: Path, records: list[bytes], masters=("Skyrim.esm",), flags=0, hedr=1.7) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    head = tes4.build_header(path.name, masters=list(masters), flags=flags, hedr_version=hedr)
    by_type: dict[bytes, list[bytes]] = {}
    for r in records:
        by_type.setdefault(r[:4], []).append(r)
    path.write_bytes(head + b"".join(grup(t, b"".join(rs)) for t, rs in by_type.items()))
    return path


def test_summary_counts_new_records_and_overrides_by_type(tmp_path):
    p = plugin(tmp_path / "Synthesis.esp", [rec(b"WATR", 0x00000100), rec(b"WATR", 0x00000200),
                                           rec(b"STAT", 0x01000800)])
    s = tes4.summarize(p)
    assert (s.records, s.new, s.overrides) == (3, 1, 2)
    assert s.overrides_by_type == {"WATR": 2} and s.new_by_type == {"STAT": 1}


def test_nested_groups_are_walked(tmp_path):
    cell = rec(b"CELL", 0x00000D00)
    refs = grup(b"\x00\x0d\x00\x00", rec(b"REFR", 0x01000801) + rec(b"LAND", 0x00000E00), gtype=9)
    p = tmp_path / "Nested.esp"
    p.write_bytes(tes4.build_header(p.name, masters=["Skyrim.esm"]) + grup(b"CELL", cell + refs))
    s = tes4.summarize(p)
    assert s.records == 3 and s.overrides_by_type == {"CELL": 1, "LAND": 1} and s.new_by_type == {"REFR": 1}


def test_overrides_only_can_take_the_flag(tmp_path):
    ok, _ = tes4.esl_ready(tes4.summarize(plugin(tmp_path / "O.esp", [rec(b"LAND", 0x00001234)])))
    assert ok


def test_new_ids_must_fit_the_light_range(tmp_path):
    fits = tes4.summarize(plugin(tmp_path / "A.esp", [rec(b"MISC", 0x01000800), rec(b"MISC", 0x01000FFF)]))
    assert tes4.esl_ready(fits)[0]
    high = tes4.summarize(plugin(tmp_path / "B.esp", [rec(b"MISC", 0x01001000)]))
    ok, why = tes4.esl_ready(high)
    assert not ok and "壓縮" in why
    low = tes4.summarize(plugin(tmp_path / "C.esp", [rec(b"MISC", 0x01000001)]))
    assert not tes4.esl_ready(low)[0]                                   # 1.70 header: 0x800 and up only
    bees = tes4.summarize(plugin(tmp_path / "D.esp", [rec(b"MISC", 0x01000001)], hedr=1.71))
    assert tes4.esl_ready(bees)[0]                                      # 1.71 header: BEES allows 0x000


def test_light_plugin_and_new_cells_are_reported(tmp_path):
    light = tes4.summarize(plugin(tmp_path / "L.esp", [], flags=tes4.FLAG_LIGHT))
    assert tes4.esl_ready(light) == (False, "已經是輕量插件")
    cells = tes4.summarize(plugin(tmp_path / "Cells.esp", [rec(b"CELL", 0x01000800)]))
    assert cells.new_cells == 1 and tes4.esl_ready(cells)[0]


def test_truncated_plugin_is_an_error(tmp_path):
    p = plugin(tmp_path / "T.esp", [rec(b"MISC", 0x01000800, data=b"\x00" * 16)])
    p.write_bytes(p.read_bytes()[:-8])
    with pytest.raises(tes4.PluginError):
        tes4.summarize(p)


def run(tmp_path, *args) -> int:
    return esl_check.main([*args, "--out", str(tmp_path / "reports")])


def test_flag_apply_sets_the_light_flag(tmp_path):
    p = plugin(tmp_path / "SYNTHESSIS" / "Synthesis.esp", [rec(b"WATR", 0x00000100)])
    assert run(tmp_path, "--plugin", str(p), "--flag") == 0
    assert not tes4.read_header(p).is_light                             # dry run
    assert run(tmp_path, "--plugin", str(p), "--flag", "--apply") == 0
    h = tes4.read_header(p)
    assert h.is_light and h.masters == ["Skyrim.esm"]
    assert tes4.summarize(p).records == 1


def test_flag_refuses_hardlinked_originals(tmp_path):
    p = plugin(tmp_path / "PM" / "Mod.esp", [rec(b"WATR", 0x00000100)])
    os.link(p, tmp_path / "Nolvus-Mod.esp")
    assert run(tmp_path, "--plugin", str(p), "--flag", "--apply") == 1
    assert not tes4.read_header(p).is_light
    text = (tmp_path / "reports" / "esl_check.txt").read_text(encoding="utf-8")
    assert "硬連結" in text


def test_flag_refuses_ids_outside_the_light_range(tmp_path):
    p = plugin(tmp_path / "Big.esp", [rec(b"MISC", 0x01002000)])
    assert run(tmp_path, "--plugin", str(p), "--flag", "--apply") == 1
    assert not tes4.read_header(p).is_light


def test_summary_line_names_the_override_types(tmp_path):
    p = plugin(tmp_path / "Synthesis.esp", [rec(b"WATR", 0x100), rec(b"LAND", 0x200), rec(b"LAND", 0x300)])
    assert run(tmp_path, "--plugin", str(p)) == 0
    text = (tmp_path / "reports" / "esl_check.txt").read_text(encoding="utf-8")
    assert "覆寫類型：LAND 2, WATR 1" in text and "可以直接加 ESL 旗標" in text


def test_scan_lists_enabled_full_plugins(tmp_path):
    pm = tmp_path / "PM"
    mods = pm / "mods"
    plugin(mods / "A" / "Fits.esp", [rec(b"MISC", 0x01000800)])
    plugin(mods / "B" / "TooBig.esp", [rec(b"MISC", 0x01002000)])
    plugin(mods / "C" / "Light.esp", [], flags=tes4.FLAG_LIGHT)
    plugin(mods / "D" / "Cell.esp", [rec(b"CELL", 0x01000800)])
    plugin(mods / "E" / "Off.esp", [])
    (pm / "STOCK GAME" / "Data").mkdir(parents=True)
    pdir = pm / "profiles" / "Pages-ZH"
    pdir.mkdir(parents=True)
    mo2.write_modlist(pdir / "modlist.txt", [mo2.ModEntry(n, "+") for n in "ABCDE"])
    mo2.write_plugins(pdir / "plugins.txt", [mo2.PluginEntry(n, n != "Off.esp") for n in
                                             ("Fits.esp", "TooBig.esp", "Light.esp", "Cell.esp", "Off.esp")])
    assert run(tmp_path, "--scan", "--pm", str(pm)) == 0
    rows = {r["plugin"]: r for r in read_csv(tmp_path / "reports" / "esl_check.csv")}
    assert set(rows) == {"Fits.esp", "TooBig.esp", "Cell.esp"}
    assert rows["Fits.esp"]["esl_ready"] == "yes" and rows["TooBig.esp"]["esl_ready"] == ""
    text = (tmp_path / "reports" / "esl_check.txt").read_text(encoding="utf-8")
    assert "可以直接加 ESL 旗標：2 個，其中沒有新增 CELL 的 1 個，例如：Fits.esp" in text


def test_subrecord_counts_show_which_fields_records_carry(tmp_path):
    def sub(t, d):
        return t + struct.pack("<H", len(d)) + d
    land_a = sub(b"DATA", b"\x00" * 4) + sub(b"VHGT", b"\x00" * 8) + sub(b"VCLR", b"\x00" * 6)
    land_b = sub(b"DATA", b"\x00" * 4) + sub(b"VHGT", b"\x00" * 8)
    p = plugin(tmp_path / "Synthesis.esp", [rec(b"LAND", 0x100, land_a), rec(b"LAND", 0x200, land_b)])
    assert run(tmp_path, "--plugin", str(p), "--subrecords", "LAND") == 0
    text = (tmp_path / "reports" / "esl_check.txt").read_text(encoding="utf-8")
    assert "LAND 記錄 2 筆；各子記錄出現在幾筆記錄：DATA 2, VHGT 2, VCLR 1" in text
