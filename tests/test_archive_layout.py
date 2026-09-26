"""Archive listing (7-Zip -slt), data-root detection and MO2 meta helpers used by install_archives."""

import pytest

from pm import layout, mo2, sevenzip

SLT_ZIP = """7-Zip 26.00 (x64) : Copyright (c) 1999-2026 Igor Pavlov : 2026-02-12

Scanning the drive for archives:
1 file, 12406254 bytes (12 MiB)

Listing archive: D:\\PM\\downloads\\x.zip

--
Path = D:\\PM\\downloads\\x.zip
Type = zip
Physical Size = 12406254

----------
Path = SKSE
Folder = +
Size = 0
Attributes = D

Path = SKSE\\Plugins\\a.dll
Folder = -
Size = 3634176
Attributes = A

"""

SLT_7Z = """Listing archive: y.7z

--
Path = y.7z
Type = 7z
Solid = +

----------
Path = Wrap
Size = 0
Attributes = RD

Path = Wrap\\textures\\a.dds
Size = 10
Attributes = A -rw-r--r--

Path = Wrap/docs
Size = 0
Attributes = drwxr-xr-x
"""


# ---------------------------------------------------------------- sevenzip
def test_parse_slt_zip_records():
    assert sevenzip.parse_slt(SLT_ZIP) == [
        sevenzip.Entry("SKSE", True, 0),
        sevenzip.Entry("SKSE/Plugins/a.dll", False, 3634176),
    ]


def test_parse_slt_7z_records_use_attributes_and_crlf():
    entries = sevenzip.parse_slt(SLT_7Z.replace("\n", "\r\n"))
    assert entries == [
        sevenzip.Entry("Wrap", True, 0),
        sevenzip.Entry("Wrap/textures/a.dds", False, 10),
        sevenzip.Entry("Wrap/docs", True, 0),
    ]


def test_parse_slt_without_separator_is_empty():
    assert sevenzip.parse_slt("Path = x.zip\nType = zip\n") == []


# ---------------------------------------------------------------- layout
def test_data_at_archive_root():
    lay = layout.classify(["meshes/a.nif", "textures/b.dds", "Mod.esp"])
    assert (lay.kind, lay.root, lay.plugins) == ("simple", "", ("Mod.esp",))


def test_single_wrapper_with_readme_beside_it():
    lay = layout.classify(["Wrap/meshes/a.nif", "Wrap/Mod.esp", "readme.txt"])
    assert (lay.kind, lay.root) == ("simple", "Wrap")


def test_nested_wrapper_and_data_folder():
    lay = layout.classify(["Outer/Data/SKSE/Plugins/x.dll", "Outer/readme.md"])
    assert (lay.kind, lay.root) == ("simple", "Outer/Data")


def test_backslashes_are_normalised():
    assert layout.classify(["Wrap\\textures\\a.dds"]).root == "Wrap"


def test_modern_skse_data_folders_are_known():
    for top in ("LightPlacer", "PBRNifPatcher", "Nemesis_Engine", "CalienteTools", "Seasons"):
        assert layout.classify([f"{top}/x.json"]).kind == "simple", top


def test_fomod_anywhere_goes_to_mo2():
    lay = layout.classify(["Wrap/fomod/ModuleConfig.xml", "Wrap/A/meshes/x.nif"])
    assert lay.kind == "fomod"


def test_fomod_info_only_is_not_an_installer():
    lay = layout.classify(["fomod/info.xml", "textures/a.dds"])
    assert (lay.kind, lay.root) == ("simple", "")


def test_option_folders_need_a_person():
    lay = layout.classify(["2K/textures/a.dds", "4K/textures/a.dds"])
    assert lay.kind == "manual" and "2K" in lay.reason


def test_unknown_folder_beside_data_needs_a_person():
    lay = layout.classify(["meshes/a.nif", "Optional/b.esp"])
    assert lay.kind == "manual" and "Optional" in lay.reason


def test_game_root_files_need_a_person():
    lay = layout.classify(["d3d11.dll", "enbseries.ini"])
    assert lay.kind == "manual" and "d3d11.dll" in lay.reason


def test_meta_ini_from_an_mo2_export_is_not_game_data():
    assert layout.classify(["meta.ini", "interface/x.swf"]).root == ""
    assert layout.classify(["meta.ini", "Wrap/textures/a.dds"]).root == "Wrap"


def test_expected_plugin_missing_at_root():
    lay = layout.classify(["Wrap/meshes/a.nif"], expected_plugins=["Mod.esp"])
    assert lay.kind == "manual" and "Mod.esp" in lay.reason


def test_expected_plugin_match_ignores_case():
    lay = layout.classify(["MOD.ESP", "Meshes/a.nif"], expected_plugins=["Mod.esp"])
    assert lay.kind == "simple"


def test_plugin_not_in_target_list_needs_a_person():
    lay = layout.classify(["Extra.esp"], target_plugins={"mod.esp"})
    assert lay.kind == "manual" and "Extra.esp" in lay.reason


def test_dbvo_voice_pack_folder_is_known():
    lay = layout.classify(["DragonbornVoiceOver/voice_packs/x.json", "Sound/DBVO/x/a.fuz"])
    assert (lay.kind, lay.root) == ("simple", "")


def test_accepted_folder_skips_soft_checks_and_says_so():
    files = ["DBReV.esp", "DBReV/settings/global.json", "Interface/DBReV/cover.swf"]
    assert layout.classify(files, target_plugins={"dbrev.esp"}).kind == "manual"
    lay = layout.classify(files, target_plugins={"dbrev.esp"}, accept=True)
    assert lay.kind == "simple" and "DBReV" in lay.reason and "放行" in lay.reason
    lay = layout.classify(["Wrap/textures/a.dds"], expected_plugins=["Gone.esp"], accept=True)
    assert (lay.kind, lay.root) == ("simple", "Wrap") and "Gone.esp" in lay.reason
    lay = layout.classify(["Extra.esp"], target_plugins={"mod.esp"}, accept=True)
    assert lay.kind == "simple" and "Extra.esp" in lay.reason


def test_accepted_tool_mod_keeps_its_executable():
    files = ["Pandora Behaviour Engine+.exe", "Pandora_Engine/mod/x.txt", "FNIS.esp"]
    lay = layout.classify(files, target_plugins={"fnis.esp"})
    assert lay.kind == "manual" and ".exe" in lay.reason
    lay = layout.classify(files, target_plugins={"fnis.esp"}, accept=True)
    assert (lay.kind, lay.root) == ("simple", "") and ".exe" in lay.reason


@pytest.mark.parametrize("files", [["fomod/ModuleConfig.xml", "A/x.esp"], ["2K/textures/a.dds", "4K/textures/a.dds"],
                                   ["readme.txt"], ["../evil.dll", "textures/a.dds"]])
def test_accept_does_not_bypass_hard_checks(files):
    assert layout.classify(files, accept=True).kind != "simple"


@pytest.mark.parametrize("files", [[], ["readme.txt"], ["a/b/c/d/e/f/textures/x.dds"]])
def test_no_usable_data_root(files):
    assert layout.classify(files).kind == "manual"


@pytest.mark.parametrize("bad", ["../evil.dll", "/abs/x.esp", "C:/x.esp", "Wrap/../../x.esp"])
def test_unsafe_paths_are_refused(bad):
    lay = layout.classify(["textures/a.dds", bad])
    assert lay.kind == "manual"


# ---------------------------------------------------------------- mo2 meta helpers
def test_install_meta_roundtrip(tmp_path):
    text = mo2.install_meta_text("150715", "633538", "1.0.0", "Skyshards-150715-1-0-0.zip")
    assert "\r\r" not in text and text.endswith("\r\n")
    d = tmp_path / "Skyshards"
    d.mkdir()
    (d / "meta.ini").write_text(text, encoding="utf-8", newline="")
    m = mo2.read_meta_ini(d / "meta.ini")
    assert (m.mod_id, m.file_id, m.version) == (150715, 633538, "1.0.0")
    assert m.installation_file == "Skyshards-150715-1-0-0.zip"
    assert m.repository == "Nexus"


@pytest.mark.parametrize("name", ["@odd.7z", "A, B.7z", "semi;colon.7z", " lead.7z"])
def test_install_meta_quotes_values_qsettings_would_misread(name):
    text = mo2.install_meta_text("1", "2", "1.0", name)
    assert f'installationFile="{name}"' in text


def test_mark_download_installed_fixes_doubled_line_ends():
    text = ("[General]\r\r\ngameName=skyrimse\r\r\nmodID=1\r\r\nfileID=2\r\r\nname=A # B\r\r\n"
            "installed=false\r\r\nuninstalled=false\r\r\n")
    out = mo2.mark_download_installed(text)
    assert "\r\r" not in out
    assert out.count("installed=true") == 1 and "uninstalled=false" in out
    assert "modID=1\r\n" in out and "name=A # B\r\n" in out


def test_mark_download_installed_adds_missing_key_in_general():
    out = mo2.mark_download_installed("[General]\nmodID=1\nInstalled=False\n[Other]\nx=1\n")
    general = out.split("[Other]")[0]
    assert "installed=true" in general and "Installed=False" not in out
    out = mo2.mark_download_installed("[General]\nmodID=1\n[Other]\nx=1\n")
    assert "installed=true" in out.split("[Other]")[0]
