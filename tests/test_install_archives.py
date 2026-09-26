"""install_archives: plan and install plain Nexus archives into their manifest folders."""

import csv
from pathlib import Path

import pytest

import install_archives
from pm import mo2, sevenzip, swap
from pm.report import read_csv


def write_rows(path: Path, fields: list[str], rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


class World:
    """A tiny portable MO2 instance plus the repo data files install_archives reads."""

    def __init__(self, root: Path):
        self.root = root
        self.pm = root / "PM"
        self.mods = self.pm / "mods"
        self.dl = self.pm / "downloads"
        self.mods.mkdir(parents=True)
        self.dl.mkdir()
        self.archives: dict[str, list[str]] = {}
        self.manifest: list[dict] = []
        self.decisions: list[dict] = []
        self.provenance: list[dict] = []
        self.target_plugins = ["Mod.esp", "Patch.esp"]

    def download(self, name: str, mod_id: int, file_id: int, files: list[str], installed=False):
        (self.dl / name).write_bytes(b"archive")
        state = "true" if installed else "false"
        (self.dl / (name + ".meta")).write_text(
            f"[General]\r\r\ngameName=skyrimse\r\r\nmodID={mod_id}\r\r\nfileID={file_id}\r\r\n"
            f"name={name}\r\r\nversion=1.0\r\r\ninstalled={state}\r\r\nuninstalled=false\r\r\n",
            encoding="utf-8", newline="")
        self.archives[name] = files

    def folder(self, name: str, mod_id: int, file_id: int, action="download", placeholder=True,
               note="", plugins=""):
        self.manifest.append({"line": str(len(self.manifest) + 2), "folder": name, "action": action,
                              "nexus_mod_id": str(mod_id), "nexus_file_id": str(file_id)})
        if note:
            self.decisions.append({"folder": name, "action": action, "note": note})
        self.provenance.append({"folder": name, "plugins": plugins})
        if placeholder:
            (self.mods / name).mkdir(exist_ok=True)

    def args(self, *extra: str) -> list[str]:
        write_rows(self.root / "manifest.csv",
                   ["line", "folder", "action", "nexus_mod_id", "nexus_file_id"], self.manifest)
        write_rows(self.root / "decisions.csv", ["folder", "action", "note"], self.decisions)
        write_rows(self.root / "provenance.csv", ["folder", "plugins"], self.provenance)
        (self.root / "plugins.txt").write_text("".join(f"*{p}\n" for p in self.target_plugins))
        return ["--pm", str(self.pm), "--manifest", str(self.root / "manifest.csv"),
                "--decisions", str(self.root / "decisions.csv"),
                "--provenance", str(self.root / "provenance.csv"),
                "--target-plugins", str(self.root / "plugins.txt"),
                "--out", str(self.root / "reports"), *extra]

    def entries(self, archive: Path) -> list[sevenzip.Entry]:
        return [sevenzip.Entry(p, False, 10) for p in self.archives[archive.name]]

    def extract(self, archive: Path, dest: Path) -> None:
        for rel in self.archives[archive.name]:
            p = dest / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"data:" + rel.encode())

    def rows(self) -> dict[str, dict]:
        return {r["archive"]: r for r in read_csv(self.root / "reports" / "install_archives.csv")}


@pytest.fixture
def world(tmp_path, monkeypatch):
    w = World(tmp_path)
    monkeypatch.setattr(install_archives, "list_files", w.entries)
    monkeypatch.setattr(install_archives, "extract", w.extract)
    monkeypatch.setattr(install_archives, "mo2_running", lambda: False)
    return w


def test_dry_run_sorts_every_download_and_changes_nothing(world):
    w = world
    w.folder("Plain Mod", 1, 11, plugins="Mod.esp")
    w.download("Plain-1-11.7z", 1, 11, ["Plain/Mod.esp", "Plain/meshes/a.nif", "readme.txt"])
    w.folder("Fomod Mod", 2, 22)
    w.download("Fomod-2-22.zip", 2, 22, ["fomod/ModuleConfig.xml", "A/Patch.esp"])
    w.download("Stray-9-99.zip", 9, 99, ["textures/x.dds"])
    w.folder("Noted Mod", 3, 33, note="FOMOD 選 PBR")
    w.download("Noted-3-33.zip", 3, 33, ["textures/x.dds"])
    w.folder("Busy Mod", 4, 44)
    (w.mods / "Busy Mod" / "old.txt").write_text("x")
    w.download("Busy-4-44.zip", 4, 44, ["textures/x.dds"])
    w.folder("Old DLL", 5, 55, action="replace_dll")
    (w.mods / "Old DLL" / "ae.dll").write_bytes(b"ae")
    w.download("NewDll-5-55.zip", 5, 55, ["SKSE/Plugins/se.dll"])
    w.folder("Done Mod", 6, 66)
    (w.mods / "Done Mod" / "meta.ini").write_text("[General]\n")
    w.download("Done-6-66.zip", 6, 66, ["textures/x.dds"], installed=True)
    w.folder("Ghost Mod", 10, 100)
    w.download("Ghost-10-100.zip", 10, 100, ["textures/x.dds"], installed=True)
    w.folder("Twin A", 7, 77)
    w.folder("Twin B", 7, 77)
    w.download("Twin-7-77.zip", 7, 77, ["textures/x.dds"])
    w.folder("Lost Mod", 8, 88, placeholder=False)
    w.download("Lost-8-88.zip", 8, 88, ["textures/x.dds"])

    assert install_archives.main(w.args()) == 0
    rows = w.rows()
    assert (rows["Plain-1-11.7z"]["status"], rows["Plain-1-11.7z"]["root"]) == ("install", "Plain")
    assert rows["Plain-1-11.7z"]["folder"] == "Plain Mod"
    expected = {"Fomod-2-22.zip": "fomod", "Stray-9-99.zip": "unmatched", "Noted-3-33.zip": "manual",
                "Busy-4-44.zip": "skip", "NewDll-5-55.zip": "replace", "Done-6-66.zip": "already",
                "Twin-7-77.zip": "manual", "Lost-8-88.zip": "manual", "Ghost-10-100.zip": "manual"}
    assert {k: rows[k]["status"] for k in expected} == expected
    assert list((w.mods / "Plain Mod").iterdir()) == []
    assert "installed=false" in (w.dl / "Plain-1-11.7z.meta").read_text(encoding="utf-8")
    assert not (w.pm / "_replaced").exists()


def test_two_archives_for_one_folder_need_a_person(world):
    w = world
    w.folder("Plain Mod", 1, 11)
    w.download("Plain-1-11.7z", 1, 11, ["textures/a.dds"])
    w.download("Plain-1-11 (1).7z", 1, 11, ["textures/a.dds"])
    install_archives.main(w.args())
    assert {r["status"] for r in w.rows().values()} == {"manual"}


def test_apply_installs_plain_archive_and_writes_meta(world):
    w = world
    w.folder("Plain Mod", 1, 11, plugins="Mod.esp")
    w.download("Plain-1-11.7z", 1, 11,
               ["Plain/Mod.esp", "Plain/meshes/a.nif", "Plain/meta.ini", "readme.txt"])
    assert install_archives.main(w.args("--apply")) == 0
    mod = w.mods / "Plain Mod"
    assert (mod / "Mod.esp").read_bytes() == b"data:Plain/Mod.esp"
    assert (mod / "meshes" / "a.nif").exists() and not (mod / "readme.txt").exists()
    meta = mo2.read_meta_ini(mod / "meta.ini")
    assert (meta.mod_id, meta.file_id, meta.installation_file) == (1, 11, "Plain-1-11.7z")
    dl_meta = (w.dl / "Plain-1-11.7z.meta").read_text(encoding="utf-8")
    assert "installed=true" in dl_meta and "\r\r" not in dl_meta
    assert not (w.pm / "_install_staging").exists()
    assert w.rows()["Plain-1-11.7z"]["status"] == "installed"


def test_apply_replace_moves_old_folder_aside(world):
    w = world
    w.folder("Old DLL", 5, 55, action="replace_dll")
    old = w.mods / "Old DLL" / "SKSE" / "Plugins"
    old.mkdir(parents=True)
    (old / "ae.dll").write_bytes(b"ae")
    w.download("NewDll-5-55.zip", 5, 55, ["Data/SKSE/Plugins/se.dll"])
    assert install_archives.main(w.args("--apply")) == 0
    assert (old / "se.dll").exists() and not (old / "ae.dll").exists()
    assert (w.pm / "_replaced" / "Old DLL" / "SKSE" / "Plugins" / "ae.dll").read_bytes() == b"ae"
    assert w.rows()["NewDll-5-55.zip"]["status"] == "replaced"


def test_apply_refused_while_mo2_runs(world, monkeypatch):
    w = world
    monkeypatch.setattr(install_archives, "mo2_running", lambda: True)
    w.folder("Plain Mod", 1, 11)
    w.download("Plain-1-11.7z", 1, 11, ["textures/a.dds"])
    assert install_archives.main(w.args("--apply")) == 1
    assert list((w.mods / "Plain Mod").iterdir()) == []


def test_limit_counts_installs_only(world):
    w = world
    w.download("Stray-9-99.zip", 9, 99, ["textures/x.dds"])
    for i in (1, 2, 3):
        w.folder(f"Mod {i}", i, i * 11)
        w.download(f"M{i}.zip", i, i * 11, ["textures/a.dds"])
    assert install_archives.main(w.args("--apply", "--limit", "2")) == 0
    done = [i for i in (1, 2, 3) if (w.mods / f"Mod {i}" / "textures").exists()]
    assert len(done) == 2


def test_only_restricts_to_named_folders(world):
    w = world
    for i in (1, 2):
        w.folder(f"Mod {i}", i, i * 11)
        w.download(f"M{i}.zip", i, i * 11, ["textures/a.dds"])
    assert install_archives.main(w.args("--apply", "--only", "Mod 2")) == 0
    assert not (w.mods / "Mod 1" / "textures").exists()
    assert (w.mods / "Mod 2" / "textures").exists()
    assert set(w.rows()) == {"M2.zip"}


def test_extract_failure_is_reported_and_cleaned_up(world, monkeypatch):
    w = world
    w.folder("Plain Mod", 1, 11)
    w.download("Plain-1-11.7z", 1, 11, ["textures/a.dds"])

    def broken(archive, dest):
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "partial.tmp").write_bytes(b"x")
        raise sevenzip.SevenZipError("CRC Failed")

    monkeypatch.setattr(install_archives, "extract", broken)
    assert install_archives.main(w.args("--apply")) == 1
    row = w.rows()["Plain-1-11.7z"]
    assert row["status"] == "error" and "CRC Failed" in row["reason"]
    assert (w.mods / "Plain Mod").is_dir() and list((w.mods / "Plain Mod").iterdir()) == []
    assert not (w.pm / "_install_staging").exists()
    assert "installed=false" in (w.dl / "Plain-1-11.7z.meta").read_text(encoding="utf-8")


def test_unreadable_archive_is_an_error(world, monkeypatch):
    w = world
    w.folder("Plain Mod", 1, 11)
    w.download("Plain-1-11.7z", 1, 11, ["textures/a.dds"])

    def unreadable(archive):
        raise sevenzip.SevenZipError("Can not open the file as archive")

    monkeypatch.setattr(install_archives, "list_files", unreadable)
    assert install_archives.main(w.args()) == 1
    assert w.rows()["Plain-1-11.7z"]["status"] == "error"


def test_folder_names_with_path_parts_are_refused(world):
    w = world
    w.folder("..\\Evil", 1, 11, placeholder=False)
    w.download("Plain-1-11.7z", 1, 11, ["textures/a.dds"])
    install_archives.main(w.args("--apply"))
    assert w.rows()["Plain-1-11.7z"]["status"] == "manual"
    assert not (w.pm / "Evil").exists()


@pytest.mark.parametrize("name", ["CON", "nul", "COM1", "Trailing dot.", "Trailing space "])
def test_reserved_windows_folder_names_are_refused(world, name):
    w = world
    w.folder(name, 1, 11, placeholder=False)
    w.download("Plain-1-11.7z", 1, 11, ["textures/a.dds"])
    install_archives.main(w.args())
    row = w.rows()["Plain-1-11.7z"]
    assert row["status"] == "manual" and "不合法" in row["reason"]


def test_accept_lets_a_checked_folder_through(world):
    w = world
    w.folder("Dova Jump", 1, 11)
    w.download("Dova-1-11.zip", 1, 11, ["DOVAJUMP/DovaJumpMCM.esp", "DOVAJUMP/SKSE/Plugins/x.dll"])
    w.folder("Noted Mod", 3, 33, note="兩個檔合併安裝：1＋2")
    w.download("Noted-3-33.zip", 3, 33, ["textures/x.dds"])
    install_archives.main(w.args())
    assert w.rows()["Dova-1-11.zip"]["status"] == "manual"
    assert install_archives.main(w.args("--apply", "--accept", "dova jump", "--accept", "Noted Mod")) == 0
    rows = w.rows()
    assert rows["Dova-1-11.zip"]["status"] == "installed" and "放行" in rows["Dova-1-11.zip"]["reason"]
    assert (w.mods / "Dova Jump" / "DovaJumpMCM.esp").exists()
    assert rows["Noted-3-33.zip"]["status"] == "manual"       # notes still need a person


def test_placeholder_with_explorer_junk_counts_as_empty(world):
    w = world
    w.folder("Plain Mod", 1, 11)
    (w.mods / "Plain Mod" / "desktop.ini").write_text("[.ShellClassInfo]\n")
    (w.mods / "Plain Mod" / "Thumbs.db").write_bytes(b"x")
    w.download("Plain-1-11.7z", 1, 11, ["textures/a.dds"])
    assert install_archives.main(w.args("--apply")) == 0
    assert w.rows()["Plain-1-11.7z"]["status"] == "installed"
    assert (w.mods / "Plain Mod" / "textures" / "a.dds").exists()


def test_folder_names_compare_case_insensitively(world):
    w = world
    w.folder("Mod A", 1, 11)
    w.manifest.append({"line": "99", "folder": "mod a", "action": "download",
                       "nexus_mod_id": "2", "nexus_file_id": "22"})
    w.download("A1.zip", 1, 11, ["textures/a.dds"])
    w.download("A2.zip", 2, 22, ["textures/b.dds"])
    install_archives.main(w.args("--only", "MOD A"))
    rows = w.rows()
    assert set(rows) == {"A1.zip", "A2.zip"}
    assert {r["status"] for r in rows.values()} == {"manual"}


def test_failed_swap_restores_placeholder_and_journal_is_cleared(world, monkeypatch):
    w = world
    w.folder("Plain Mod", 1, 11)
    w.download("Plain-1-11.7z", 1, 11, ["textures/a.dds"])
    real_rename = install_archives.os.rename

    def locked(src, dst):
        if Path(dst).name == "Plain Mod" and "_install_staging" in str(src) and "placeholder" not in str(src):
            raise PermissionError(32, "being used by another process")
        return real_rename(src, dst)

    monkeypatch.setattr(install_archives.os, "rename", locked)
    monkeypatch.setattr(swap.time, "sleep", lambda s: None)
    assert install_archives.main(w.args("--apply")) == 1
    assert w.rows()["Plain-1-11.7z"]["status"] == "error"
    assert (w.mods / "Plain Mod").is_dir() and list((w.mods / "Plain Mod").iterdir()) == []
    assert not (w.pm / "_install_staging").exists()


def _journal(w: World, target: str, aside: str) -> Path:
    staging = w.pm / "_install_staging"
    staging.mkdir(exist_ok=True)
    j = staging / "swap-in-progress.txt"
    j.write_text(f"{target}\n{aside}\n", encoding="utf-8")
    return j


def _report_text(w: World) -> str:
    return (w.root / "reports" / "install_archives.txt").read_text(encoding="utf-8")


def test_interrupted_swap_is_repaired_on_next_run(world):
    w = world
    w.folder("Plain Mod", 1, 11)
    w.folder("Old DLL", 5, 55, action="replace_dll")
    # a run that died mid-swap leaves the journal behind; only one swap runs at a time,
    # so recover one folder per journal: first the placeholder parked in staging ...
    parked = w.pm / "_install_staging" / "20260926-1" / "placeholder"
    (w.mods / "Plain Mod").rename(parked.parent.mkdir(parents=True) or parked)
    j = _journal(w, w.mods / "Plain Mod", parked)
    assert install_archives.main(w.args()) == 0
    assert (w.mods / "Plain Mod").is_dir() and not parked.exists() and not j.exists()
    # ... then a replace_dll folder that had been moved to _replaced
    aside = w.pm / "_replaced" / "Old DLL"
    aside.parent.mkdir()
    (w.mods / "Old DLL").rename(aside)
    (aside / "ae.dll").write_bytes(b"ae")
    j = _journal(w, w.mods / "Old DLL", aside)
    assert install_archives.main(w.args()) == 0
    assert (w.mods / "Old DLL" / "ae.dll").read_bytes() == b"ae"
    assert not aside.exists() and not j.exists()


def test_missing_parked_placeholder_is_rebuilt_and_said_so(world):
    w = world
    w.folder("Plain Mod", 1, 11)
    (w.mods / "Plain Mod").rmdir()
    _journal(w, w.mods / "Plain Mod", w.pm / "_install_staging" / "gone" / "placeholder")
    assert install_archives.main(w.args()) == 0
    assert (w.mods / "Plain Mod").is_dir()
    assert "重建" in _report_text(w)


def test_missing_replaced_content_is_a_failure_but_keeps_the_folder(world):
    w = world
    w.folder("Old DLL", 5, 55, action="replace_dll")
    (w.mods / "Old DLL").rmdir()
    _journal(w, w.mods / "Old DLL", w.pm / "_replaced" / "Old DLL")
    assert install_archives.main(w.args("--apply")) == 1
    assert (w.mods / "Old DLL").is_dir()        # MO2 must keep its modlist line
    assert "_replaced" in _report_text(w)


@pytest.mark.parametrize("aside", ["", "\x00bad"])
def test_corrupt_journal_is_reported_not_guessed(world, aside):
    w = world
    w.folder("Plain Mod", 1, 11)
    (w.mods / "Plain Mod").rmdir()
    _journal(w, w.mods / "Plain Mod", aside)
    assert install_archives.main(w.args("--apply")) == 1
    assert not (w.mods / "Plain Mod").exists()
    assert "中斷" in _report_text(w)


def test_journal_pointing_outside_mods_is_ignored(world):
    w = world
    staging = w.pm / "_install_staging"
    staging.mkdir()
    outside = w.root / "elsewhere"
    (staging / "swap-in-progress.txt").write_text(f"{outside}\n\n", encoding="utf-8")
    assert install_archives.main(w.args()) == 1
    assert not outside.exists()
