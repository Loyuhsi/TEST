"""fill_plugins: put missing target plugins into their folders from source installs or archives."""

import csv
import os
from pathlib import Path

import pytest

import fill_plugins
from pm import mo2, sevenzip
from pm.report import read_csv


def write_rows(path: Path, fields: list[str], rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


class World:
    def __init__(self, root: Path):
        self.root = root
        self.pm = root / "PM"
        self.mods = self.pm / "mods"
        self.dl = self.pm / "downloads"
        self.profile = self.pm / "profiles" / "Pages-ZH"
        self.mv = root / "MV"
        self.nol = root / "Nolvus"
        for d in (self.mods, self.dl, self.profile / "_expected", self.mv / "mods",
                  self.nol / "MODS" / "mods", self.pm / "STOCK GAME" / "Data"):
            d.mkdir(parents=True, exist_ok=True)
        (self.pm / "STOCK GAME" / "SkyrimSE.exe").write_bytes(b"MZ")
        (self.mv / "ModOrganizer.ini").write_text("[General]\n")
        self.folders: list[str] = []
        self.expected: list[str] = []
        self.manifest: list[dict] = []
        self.sources: list[dict] = []
        self.archives: dict[str, dict[str, bytes]] = {}
        self.extracted: list[tuple[str, list[str]]] = []

    def target(self, name: str, files: dict[str, bytes] | None = None, mod="", fid="", action="keep"):
        self.folders.append(name)
        d = self.mods / name
        d.mkdir(exist_ok=True)
        for rel, data in (files or {}).items():
            p = d / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        self.manifest.append({"folder": name, "action": action, "nexus_mod_id": mod, "nexus_file_id": fid})

    def source(self, which: str, folder: str, files: dict[str, bytes]):
        base = (self.mv / "mods") if which == "mv" else (self.nol / "MODS" / "mods")
        for rel, data in files.items():
            p = base / folder / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)

    def archive(self, name: str, mod: int, fid: int, members: dict[str, bytes]):
        (self.dl / name).write_bytes(b"7z")
        (self.dl / (name + ".meta")).write_text(f"[General]\nmodID={mod}\nfileID={fid}\ninstalled=false\n")
        self.archives[name] = members

    def args(self, *extra: str) -> list[str]:
        mo2.write_modlist(self.profile / "modlist.txt",
                          [mo2.ModEntry(n, "+") for n in self.folders])
        mo2.write_plugins(self.profile / "_expected" / "plugins.txt",
                          [mo2.PluginEntry(p, True) for p in self.expected])
        write_rows(self.root / "manifest.csv", ["folder", "action", "nexus_mod_id", "nexus_file_id"], self.manifest)
        write_rows(self.root / "sources.csv", ["kind", "source", "match", "target", "mode", "note"], self.sources)
        return ["--pm", str(self.pm), "--mv", str(self.mv), "--nolvus", str(self.nol),
                "--manifest", str(self.root / "manifest.csv"), "--extra", str(self.root / "none.csv"),
                "--sources", str(self.root / "sources.csv"), "--out", str(self.root / "reports"), *extra]

    # fakes for the 7-Zip seams
    def entries(self, archive: Path) -> list[sevenzip.Entry]:
        return [sevenzip.Entry(m, False, len(d)) for m, d in self.archives[archive.name].items()]

    def extract(self, archive: Path, dest: Path, members: list[str]) -> None:
        self.extracted.append((archive.name, sorted(members)))
        for m in members:
            p = dest / m
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(self.archives[archive.name][m])

    def rows(self) -> dict[str, dict]:
        return {r["plugin"]: r for r in read_csv(self.root / "reports" / "fill_plugins.csv")}


@pytest.fixture
def world(tmp_path, monkeypatch):
    w = World(tmp_path)
    monkeypatch.setattr(fill_plugins, "list_files", w.entries)
    monkeypatch.setattr(fill_plugins, "extract_files", w.extract)
    monkeypatch.setattr(fill_plugins, "mo2_running", lambda: False)
    return w


def build(w: World) -> None:
    w.target("JK's Interiors Patch Collection", {"JKs Old patch.esp": b"old"})
    w.target("Lux - Patch Hub3")
    w.target("Lux Orbis cs", {"Lux Orbis CS.esp": b"cs", "meshes/lamp.nif": b"cs-lamp"})
    w.target("Collection Hub2")
    w.target("Snazzy Interiors Patch Collection2", mod="100", fid="1000")
    w.target("Fort Dawnguard SDA Patch", mod="200", fid="2001", action="download")
    w.target("Guild HQ Collection", mod="200", fid="2000")
    w.target("Nowhere Patch Collection", mod="400", fid="4000")
    w.target("Already", {"Present.esp": b"p"})
    w.expected = ["Present.esp", "Synthesis.esp", "JKs Blue Palace - A patch.esp", "Lux - X patch.esp",
                  "Lux Orbis.esp", "Hub Patch.esp", "Snazzy Interiors - Y patch.esp",
                  "JKs Castle Volkihar - Z patch.esp", "Twin.esp", "Nowhere - Q patch.esp"]
    w.source("nolvus", "JK's Interiors Patch Collection",
             {"JKs Blue Palace - A patch.esp": b"bp", "JKs Blue Palace - A patch.bsa": b"bsa", "other.esp": b"x"})
    w.source("mv", "Lux (patch hub)", {"Lux - X patch.esp": b"lux"})
    w.source("nolvus", "Lux Orbis", {"Lux Orbis.esp": b"orbis", "meshes/lamp.nif": b"orbis-lamp",
                                     "meshes/new.nif": b"new"})
    w.source("mv", "Collection Hub", {"Hub Patch.esp": b"hub"})
    w.sources = [{"kind": "source", "source": "mv", "match": "Lux (patch hub)", "target": "Lux - Patch Hub3"},
                 {"kind": "source", "source": "nolvus", "match": "Lux Orbis", "target": "Lux Orbis cs",
                  "mode": "whole"},
                 {"kind": "prefix", "match": "JKs ",
                  "target": "JK's Interiors Patch Collection|Guild HQ Collection"}]
    w.archive("Snazzy-100-1000.7z", 100, 1000, {"Patches/Snazzy Interiors - Y patch.esp": b"sn",
                                                "Patches/readme.txt": b"r"})
    w.archive("GuildHQ-200-2001.rar", 200, 2001, {"99 Volkihar/JKs Castle Volkihar - Z patch.esp": b"cv",
                                                  "99 Volkihar/JKs Castle Volkihar - Z patch - Textures.bsa": b"t"})
    w.archive("Twin-300-3000.zip", 300, 3000, {"A/Twin.esp": b"1", "B/Twin.esp": b"22"})


def test_dry_run_plans_every_source_and_writes_nothing(world):
    w = world
    build(w)
    assert fill_plugins.main(w.args("--plan-downloads")) == 0
    rows = w.rows()
    assert set(rows) == {"JKs Blue Palace - A patch.esp", "Lux - X patch.esp", "Lux Orbis.esp", "Hub Patch.esp",
                         "Snazzy Interiors - Y patch.esp", "JKs Castle Volkihar - Z patch.esp", "Twin.esp",
                         "Nowhere - Q patch.esp"}                        # present + generated excluded
    got = {p: (r["status"], r["dest"]) for p, r in rows.items()}
    assert got["JKs Blue Palace - A patch.esp"] == ("install", "JK's Interiors Patch Collection")
    assert got["Lux - X patch.esp"] == ("install", "Lux - Patch Hub3")
    assert got["Lux Orbis.esp"] == ("whole", "Lux Orbis cs")
    assert got["Hub Patch.esp"] == ("install", "Collection Hub2")
    assert got["Snazzy Interiors - Y patch.esp"] == ("archive", "Snazzy Interiors Patch Collection2")
    assert got["JKs Castle Volkihar - Z patch.esp"] == ("archive", "Guild HQ Collection")   # prefix map wins
    assert got["Twin.esp"][0] == "ambiguous"
    assert got["Nowhere - Q patch.esp"] == ("unresolved", "")
    assert "Nowhere Patch Collection" in rows["Nowhere - Q patch.esp"]["candidates"]
    dl = read_csv(w.root / "reports" / "fill_plugins_downloads.csv")
    assert [(r["folder"], r["nexus_mod_id"], r["nexus_file_id"], r["action"]) for r in dl] == \
        [("Nowhere Patch Collection", "400", "4000", "download")]
    assert not (w.mods / "Lux - Patch Hub3" / "Lux - X patch.esp").exists()
    assert w.extracted == []
    assert (w.root / "reports" / "fill_plugins_cache.json").exists()


def test_apply_links_merges_and_extracts_without_overwriting(world):
    w = world
    build(w)
    assert fill_plugins.main(w.args("--apply")) == 0
    jk = w.mods / "JK's Interiors Patch Collection"
    assert (jk / "JKs Blue Palace - A patch.esp").read_bytes() == b"bp"
    assert (jk / "JKs Blue Palace - A patch.bsa").exists() and not (jk / "other.esp").exists()
    assert os.stat(jk / "JKs Blue Palace - A patch.esp").st_nlink == 2               # hardlink
    assert (w.mods / "Lux - Patch Hub3" / "Lux - X patch.esp").exists()
    lox = w.mods / "Lux Orbis cs"
    assert (lox / "Lux Orbis.esp").read_bytes() == b"orbis" and (lox / "meshes" / "new.nif").exists()
    assert (lox / "meshes" / "lamp.nif").read_bytes() == b"cs-lamp"                  # existing file kept
    assert (w.mods / "Collection Hub2" / "Hub Patch.esp").exists()
    assert (w.mods / "Snazzy Interiors Patch Collection2" / "Snazzy Interiors - Y patch.esp").read_bytes() == b"sn"
    assert not (w.mods / "Snazzy Interiors Patch Collection2" / "readme.txt").exists()
    ghq = w.mods / "Guild HQ Collection"
    assert (ghq / "JKs Castle Volkihar - Z patch.esp").exists()
    assert (ghq / "JKs Castle Volkihar - Z patch - Textures.bsa").exists()          # same-stem BSA
    assert ("GuildHQ-200-2001.rar", ["99 Volkihar/JKs Castle Volkihar - Z patch - Textures.bsa",
                                     "99 Volkihar/JKs Castle Volkihar - Z patch.esp"]) in w.extracted
    assert not any("Twin" in a for a, _ in w.extracted)                               # ambiguous untouched
    assert not (w.pm / fill_plugins.STAGING_DIR).exists()
    statuses = {p: r["status"] for p, r in w.rows().items()}
    assert statuses["Twin.esp"] == "ambiguous" and statuses["Hub Patch.esp"] == "done"
    # second run: nothing left to do for the filled plugins
    assert fill_plugins.main(w.args()) == 0
    assert set(w.rows()) == {"Twin.esp", "Nowhere - Q patch.esp"}


def test_existing_destination_file_is_never_overwritten(world):
    w = world
    w.target("Hub")
    w.expected = ["Hub Patch.esp"]
    w.source("mv", "Hub", {"Hub Patch.esp": b"new", "Hub Patch.bsa": b"new-bsa"})
    (w.mods / "Hub" / "Hub Patch.bsa").write_bytes(b"mine")
    assert fill_plugins.main(w.args("--apply")) == 0
    assert (w.mods / "Hub" / "Hub Patch.bsa").read_bytes() == b"mine"
    assert (w.mods / "Hub" / "Hub Patch.esp").read_bytes() == b"new"


def test_mapping_to_a_folder_outside_the_modlist_is_reported(world):
    w = world
    w.target("Real")
    w.expected = ["X.esp"]
    w.source("mv", "Src", {"X.esp": b"x"})
    w.sources = [{"kind": "source", "source": "mv", "match": "Src", "target": "Not In Modlist"}]
    assert fill_plugins.main(w.args()) == 0
    r = w.rows()["X.esp"]
    assert r["status"] == "unresolved" and "Not In Modlist" in r["note"]


def test_refuses_to_apply_while_mo2_runs(world, monkeypatch):
    w = world
    build(w)
    monkeypatch.setattr(fill_plugins, "mo2_running", lambda: True)
    assert fill_plugins.main(w.args("--apply")) == 1
    assert not (w.mods / "Lux - Patch Hub3" / "Lux - X patch.esp").exists()


def test_helpers():
    assert fill_plugins.plugin_prefix("COTN Dawnstar - 3DNPC Patch.esp") == "COTN Dawnstar"
    assert fill_plugins.plugin_prefix("DBM_HUB_TwilightPrincess_Patch.esp") == "DBM"
    assert fill_plugins.tokens("JK's Blue Palace2") == {"jks", "blue", "palace2"}
    assert fill_plugins.same_stem_archives(["A.bsa", "A - Textures.bsa", "AB.bsa", "A.esp"], "A.esp") == \
        ["A.bsa", "A - Textures.bsa"]


def test_extract_files_uses_a_utf8_list_file(tmp_path, monkeypatch):
    seen = {}

    def fake_run(args):
        listfile = Path(args[-1][1:])
        seen["args"] = args
        seen["list"] = listfile.read_text(encoding="utf-8")

        class R:
            returncode = 0
            stderr = b""
        return R()

    monkeypatch.setattr(sevenzip, "_run", fake_run)
    sevenzip.extract_files(tmp_path / "a.7z", tmp_path / "out", ["A/Ünïcode patch.esp", "B/x.bsa"])
    assert "-scsUTF-8" in seen["args"] and seen["args"][-1].startswith("@")
    assert seen["list"].splitlines() == [p.replace("/", os.sep) for p in ("A/Ünïcode patch.esp", "B/x.bsa")]
    assert not Path(seen["args"][-1][1:]).exists()                                   # list file removed


def test_folder_with_same_prefix_plugins_becomes_the_candidate(world):
    w = world
    w.target("Occlusion Mod", {"Occ_Skyrim_Tamriel.esp": b"t"}, mod="500", fid="5000")
    w.target("Unrelated")
    w.expected = ["Occ_Skyrim_Tamriel.esp", "Occ_Skyrim_COTN-Dawnstar_patch.esp"]
    assert fill_plugins.main(w.args("--plan-downloads")) == 0
    r = w.rows()["Occ_Skyrim_COTN-Dawnstar_patch.esp"]
    assert r["status"] == "unresolved" and r["candidates"] == "Occlusion Mod"
    dl = read_csv(w.root / "reports" / "fill_plugins_downloads.csv")
    assert [(d["folder"], d["nexus_file_id"]) for d in dl] == [("Occlusion Mod", "5000")]
    # once the folder's archive is downloaded, the plugin is taken from it
    w.archive("Occ-500-5000.7z", 500, 5000, {"Occ_Skyrim_COTN-Dawnstar_patch.esp": b"d"})
    assert fill_plugins.main(w.args("--apply")) == 0
    assert (w.mods / "Occlusion Mod" / "Occ_Skyrim_COTN-Dawnstar_patch.esp").read_bytes() == b"d"

