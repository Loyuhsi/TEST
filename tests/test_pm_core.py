import os
import struct

import pytest

from pm import bsa, fsutil, mo2, pe, strings, tes4


# ---------------------------------------------------------------- mo2
def test_modlist_roundtrip(tmp_path):
    src = tmp_path / "modlist.txt"
    src.write_bytes(b"\xef\xbb\xbf# header\r\n+Top Mod\r\n-Off Mod\r\n-Stuff_separator\r\n*DLC: Dawnguard\r\n")
    entries = mo2.read_modlist(src)
    assert [e.name for e in entries] == ["Top Mod", "Off Mod", "Stuff_separator", "DLC: Dawnguard"]
    assert entries[0].enabled and not entries[1].enabled
    assert entries[2].is_separator and entries[3].is_foreign
    assert entries[0].line_no == 2
    out = tmp_path / "out.txt"
    mo2.write_modlist(out, entries)
    assert out.read_bytes().startswith(b"# This file")
    assert b"\r\n+Top Mod\r\n" in out.read_bytes()
    assert [e.name for e in mo2.read_modlist(out)] == [e.name for e in entries]


def test_plugins_roundtrip(tmp_path):
    p = tmp_path / "plugins.txt"
    p.write_text("# x\n*A.esp\nB.esp\n*C.esl\n")
    entries = mo2.read_plugins(p)
    assert [(e.name, e.enabled) for e in entries] == [("A.esp", True), ("B.esp", False), ("C.esl", True)]
    mo2.write_plugins(tmp_path / "o.txt", entries)
    assert [e.name for e in mo2.read_plugins(tmp_path / "o.txt")] == ["A.esp", "B.esp", "C.esl"]


@pytest.mark.parametrize("name,expected", [
    ("Wyrmstooth2", "Wyrmstooth"),
    ("Lux - Via (patch hub)2", "Lux - Via (patch hub)"),
    ("Northern Roads Patch Collection3", "Northern Roads Patch Collection"),
    ("Plain Name", None),
    ("1234", None),
])
def test_strip_dup_suffix(name, expected):
    assert mo2.strip_dup_suffix(name) == expected


def test_meta_ini(tmp_path):
    d = tmp_path / "Some Mod"
    d.mkdir()
    (d / "meta.ini").write_text(
        "[General]\ngameName=SkyrimSE\nmodid=12345\nversion=1.2.3\n"
        "installationFile=Some Mod-12345-1-2-3.7z\nrepository=Nexus\n"
        "[installedFiles]\n1\\modid=12345\n1\\fileid=67890\nsize=1\n")
    m = mo2.read_meta_ini(d / "meta.ini")
    assert (m.folder, m.mod_id, m.file_id, m.version) == ("Some Mod", 12345, 67890, "1.2.3")
    assert mo2.nexus_url(m.mod_id, m.file_id).endswith("mods/12345?tab=files&file_id=67890")


def test_find_instance_paths(tmp_path):
    (tmp_path / "ModOrganizer.ini").write_text(
        "[General]\ngamePath=@ByteArray(D:\\\\Nolvus\\\\STOCK GAME)\n"
        "[Settings]\nmod_directory=%BASE_DIR%/MODS/mods\n")
    paths = mo2.find_instance_paths(tmp_path)
    assert str(paths["mods"]).replace("\\", "/").endswith("MODS/mods")
    assert str(paths["game"]) == "D:\\Nolvus\\STOCK GAME"
    assert mo2.qt_bytearray("D:\\PM\\STOCK GAME") == "@ByteArray(D:\\\\PM\\\\STOCK GAME)"


def test_locate_instance_skips_a_mods_container_folder(tmp_path):
    # Nolvus keeps mods/ and profiles/ inside MODS/. On NTFS "root\mods" opens "root\MODS",
    # so the default "<root>/mods" guess lands on that container; a folder named "mods"
    # holding mods/ and profiles/ reproduces it on any file system.
    container = tmp_path / "mods"
    for sub in ("mods/Some Mod", "profiles/Default", "downloads", "overwrite"):
        (container / sub).mkdir(parents=True)
    paths = mo2.locate_instance(tmp_path)
    assert paths["mods"] == container / "mods"
    assert paths["profiles"] == container / "profiles"


def test_locate_instance_keeps_a_plain_mods_folder(tmp_path):
    (tmp_path / "ModOrganizer.ini").write_text("[General]\n")
    (tmp_path / "mods" / "Some Mod").mkdir(parents=True)
    (tmp_path / "profiles" / "Default").mkdir(parents=True)
    assert mo2.locate_instance(tmp_path)["mods"] == tmp_path / "mods"


# ---------------------------------------------------------------- tes4
def test_tes4_header(tmp_path):
    p = tmp_path / "Patch.esp"
    p.write_bytes(tes4.build_header("Patch.esp", masters=["Skyrim.esm", "Update.esm"],
                                    flags=tes4.FLAG_LIGHT, hedr_version=1.71, author="me") + b"GRUP")
    h = tes4.read_header(p)
    assert h.masters == ["Skyrim.esm", "Update.esm"]
    assert h.is_light and not h.is_master and h.kind == "light"
    assert h.needs_bees and h.author == "me"
    full = tes4.parse_header_bytes(tes4.build_header("X.esp"), "X.esp")
    assert full.kind == "full" and not full.needs_bees
    assert tes4.parse_header_bytes(tes4.build_header("M.esm"), "M.esm").kind == "master"
    with pytest.raises(tes4.PluginError):
        tes4.parse_header_bytes(b"NOPE" + b"\x00" * 30, "bad.esp")


def test_tes4_xxxx_subrecord():
    body = b"XXXX" + struct.pack("<H", 4) + struct.pack("<I", 12)
    body += b"HEDR" + struct.pack("<H", 0) + struct.pack("<fiI", 1.7, 5, 0x800)
    data = b"TES4" + struct.pack("<IIIIHH", len(body), 1, 0, 0, 44, 0) + body
    h = tes4.parse_header_bytes(data, "Big.esm")
    assert h.num_records == 5 and h.is_master


# ---------------------------------------------------------------- pe
@pytest.mark.parametrize("exports,cls,loads", [
    (["SKSEPlugin_Query", "SKSEPlugin_Load"], "se", True),
    (["SKSEPlugin_Version", "SKSEPlugin_Load"], "ae_only", False),
    (["SKSEPlugin_Query", "SKSEPlugin_Version", "SKSEPlugin_Load"], "multi", True),
    (["SomethingElse"], "not_skse", None),
])
def test_pe_exports(tmp_path, exports, cls, loads):
    p = tmp_path / "plugin.dll"
    p.write_bytes(pe.build_dll(exports))
    info = pe.read_dll(p)
    assert info.exports == set(exports)
    assert info.runtime_class == cls
    assert info.loads_on_1597 is loads


# ---------------------------------------------------------------- strings
@pytest.mark.parametrize("ext", [".STRINGS", ".DLSTRINGS", ".ILSTRINGS"])
def test_strings_roundtrip(tmp_path, ext):
    table = {1: "Iron Sword", 2: "鐵劍", 70000: "多行\n文字"}
    p = tmp_path / f"skyrim_chinese{ext}"
    strings.write(p, table)
    assert strings.read(p) == table


def test_strings_cp1252_fallback():
    data = strings.build({5: "Caf\u00e9"}, "strings", encoding="cp1252")
    assert strings.parse(data, "strings") == {5: "Caf\u00e9"}


# ---------------------------------------------------------------- bsa
@pytest.mark.parametrize("version,compress", [(105, False), (105, True), (104, True)])
def test_bsa_extract(tmp_path, version, compress):
    if compress and version == 105:
        pytest.importorskip("lz4")
    files = {
        "strings\\skyrim_chinese.strings": strings.build({1: "天際"}, "strings"),
        "interface\\fonts_cn.swf": b"FWS" + b"\x01" * 64,
        "interface\\fontconfig_cn.txt": b'fontlib "Interface\\fonts_cn.swf"\n',
    }
    p = tmp_path / "Skyrim - Interface.bsa"
    p.write_bytes(bsa.build_bsa(files, version=version, compress=compress))
    with bsa.BSA(p) as archive:
        assert len(archive.entries) == 3
        written = archive.extract(["strings\\*_chinese.*", "interface/font*_cn.*"], tmp_path / "out")
    assert len(written) == 3
    assert strings.read(tmp_path / "out" / "strings" / "skyrim_chinese.strings") == {1: "天際"}
    assert (tmp_path / "out" / "interface" / "fonts_cn.swf").read_bytes() == files["interface\\fonts_cn.swf"]


# ---------------------------------------------------------------- fsutil
def test_clone_tree_hardlinks_survive_source_delete(tmp_path):
    src = tmp_path / "src" / "Mod A"
    (src / "meshes").mkdir(parents=True)
    (src / "meshes" / "a.nif").write_bytes(b"x" * 100)
    (src / "meta.ini").write_text("[General]\nmodid=1\n")
    dst = tmp_path / "dst" / "Mod A"
    dry = fsutil.clone_tree(src, dst, apply=False)
    assert dry.linked == 1 and dry.copied == 1 and not dst.exists()
    st = fsutil.clone_tree(src, dst, apply=True)
    assert st.linked == 1 and st.copied == 1 and not st.errors
    assert os.stat(dst / "meshes" / "a.nif").st_nlink == 2
    assert os.stat(dst / "meta.ini").st_nlink == 1          # copied, not linked
    import shutil
    shutil.rmtree(tmp_path / "src")
    assert (dst / "meshes" / "a.nif").read_bytes() == b"x" * 100
    again = fsutil.clone_tree(dst, dst.parent / "B", apply=True)
    assert again.linked == 1


def test_human_and_free():
    assert fsutil.human(1536) == "1.5 KB"
    assert fsutil.free_bytes(fsutil.Path(".")) > 0
