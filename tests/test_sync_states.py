"""build_instance sync-order --restore-states: MO2 lists newly installed plugins as disabled,
so the target's enabled flags must be put back before prune_dependents runs."""

from pathlib import Path

import pytest

import build_instance
from pm import mo2, tes4


def write_plugin(path: Path, masters=(), flags=0):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(tes4.build_header(path.name, masters=list(masters), flags=flags, hedr_version=1.7))


@pytest.fixture
def pm(tmp_path):
    root = tmp_path / "PM"
    mods = root / "mods"
    for folder, plugin in (("A", "A.esp"), ("B", "B.esp"), ("C", "C.esp"), ("D", "D.esp"),
                           ("E", "E.esp"), ("M", "Master.esm")):
        flags = tes4.FLAG_MASTER if plugin.endswith(".esm") else 0
        write_plugin(mods / folder / plugin, ["Skyrim.esm"], flags)
    (root / "STOCK GAME").mkdir(parents=True)
    pdir = root / "profiles" / "Pages-ZH"
    (pdir / "_expected").mkdir(parents=True)
    mo2.write_modlist(pdir / "modlist.txt", [mo2.ModEntry(n, s) for n, s in
                                             (("A", "+"), ("B", "+"), ("C", "+"), ("D", "+"),
                                              ("E", "-"), ("M", "+"))])
    # target: A, B, Master enabled; C disabled; E enabled but its mod is off; Gone.esp not on disk
    mo2.write_plugins(pdir / "_expected" / "plugins.txt",
                      [mo2.PluginEntry("Master.esm", True), mo2.PluginEntry("A.esp", True),
                       mo2.PluginEntry("B.esp", True), mo2.PluginEntry("C.esp", False),
                       mo2.PluginEntry("E.esp", True), mo2.PluginEntry("Gone.esp", True)])
    # what MO2 left behind: new plugins disabled or missing, C switched on by hand
    mo2.write_plugins(pdir / "plugins.txt",
                      [mo2.PluginEntry("B.esp", False), mo2.PluginEntry("C.esp", True),
                       mo2.PluginEntry("D.esp", False)])
    return root


def run(pm_root: Path, tmp_path: Path, *flags: str) -> int:
    return build_instance.main(["sync-order", "--pm", str(pm_root), "--out", str(tmp_path / "reports"), *flags])


def states(pm_root: Path) -> dict[str, bool]:
    return {p.name: p.enabled for p in mo2.read_plugins(pm_root / "profiles" / "Pages-ZH" / "plugins.txt")}


def test_restore_states_applies_target_flags_for_plugins_on_disk(pm, tmp_path):
    assert run(pm, tmp_path, "--restore-states", "--apply") == 0
    assert states(pm) == {"Master.esm": True, "A.esp": True, "B.esp": True, "C.esp": False, "D.esp": False}


def test_restore_states_keeps_target_order_with_masters_first(pm, tmp_path):
    assert run(pm, tmp_path, "--restore-states", "--apply") == 0
    order = [p.name for p in mo2.read_plugins(pm / "profiles" / "Pages-ZH" / "plugins.txt")]
    assert order == ["Master.esm", "A.esp", "B.esp", "C.esp", "D.esp"]


def test_restore_states_reports_what_changed(pm, tmp_path):
    assert run(pm, tmp_path, "--restore-states", "--apply") == 0
    text = (tmp_path / "reports" / "build_instance-sync-order.txt").read_text(encoding="utf-8")
    line = next(ln for ln in text.splitlines() if "啟用狀態" in ln)
    assert "啟用 3 個" in line and "停用 1 個" in line and "略過 2 個" in line


def test_restore_states_dry_run_writes_nothing(pm, tmp_path):
    before = (pm / "profiles" / "Pages-ZH" / "plugins.txt").read_bytes()
    assert run(pm, tmp_path, "--restore-states") == 0
    assert (pm / "profiles" / "Pages-ZH" / "plugins.txt").read_bytes() == before


def test_without_flag_states_are_left_alone(pm, tmp_path):
    assert run(pm, tmp_path, "--apply") == 0
    assert states(pm) == {"B.esp": False, "C.esp": True, "D.esp": False}


def test_restore_states_keeps_the_casing_mo2_wrote(pm, tmp_path):
    pdir = pm / "profiles" / "Pages-ZH"
    mo2.write_plugins(pdir / "plugins.txt", [mo2.PluginEntry("b.ESP", False)])
    assert run(pm, tmp_path, "--restore-states", "--apply") == 0
    assert states(pm)["b.ESP"] is True and "B.esp" not in states(pm)


def test_restore_states_covers_plugins_in_the_game_data_folder(pm, tmp_path):
    write_plugin(pm / "STOCK GAME" / "Data" / "ccTest.esl", ["Skyrim.esm"], tes4.FLAG_MASTER | tes4.FLAG_LIGHT)
    pdir = pm / "profiles" / "Pages-ZH"
    expected = mo2.read_plugins(pdir / "_expected" / "plugins.txt")
    mo2.write_plugins(pdir / "_expected" / "plugins.txt", [mo2.PluginEntry("ccTest.esl", True), *expected])
    assert run(pm, tmp_path, "--restore-states", "--apply") == 0
    assert states(pm)["ccTest.esl"] is True


def test_restore_states_needs_the_expected_list(pm, tmp_path):
    pdir = pm / "profiles" / "Pages-ZH"
    (pdir / "_expected" / "plugins.txt").unlink()
    before = (pdir / "plugins.txt").read_bytes()
    assert run(pm, tmp_path, "--restore-states", "--apply") == 1
    assert (pdir / "plugins.txt").read_bytes() == before
