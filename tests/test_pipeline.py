"""End-to-end run of the assembly tools on tiny fake Nolvus / Mages & Vikings installs."""

import csv
import os
import shutil
from pathlib import Path

import pytest

import audit_skse
import build_instance
import check_plugins
import harvest
import inventory
import manifest
import prune_dependents
import preflight
from pm import mo2, pe, tes4


def write_plugin(path: Path, masters=(), flags=0, hedr=1.7):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(tes4.build_header(path.name, masters=list(masters), flags=flags, hedr_version=hedr))


def make_mod(mods: Path, name: str, *, modid=0, fileid=0, plugins=(), dlls=None, extra=None):
    d = mods / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "meta.ini").write_text(f"[General]\nmodid={modid}\nversion=1.0\n[installedFiles]\n1\\modid={modid}\n"
                                f"1\\fileid={fileid}\n")
    for p, masters, flags in plugins:
        write_plugin(d / p, masters, flags)
    for dll, exports in (dlls or {}).items():
        (d / "SKSE" / "Plugins").mkdir(parents=True, exist_ok=True)
        (d / "SKSE" / "Plugins" / dll).write_bytes(pe.build_dll(exports))
    for rel, data in (extra or {}).items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_bytes(data)
    return d


def make_game(root: Path, version="1.5.97.0"):
    root.mkdir(parents=True, exist_ok=True)
    a, b, c, dd = (int(x) for x in version.split("."))
    import struct
    vs = b"\xbd\x04\xef\xfe" + struct.pack("<III", 0x00010000, (a << 16) | b, (c << 16) | dd)
    (root / "SkyrimSE.exe").write_bytes(b"MZ" + b"\x00" * 64 + vs)
    (root / "skse64_loader.exe").write_bytes(b"MZ")
    (root / "skse64_1_5_97.dll").write_bytes(b"MZ")
    (root / "d3d11.dll").write_bytes(b"ENB")
    (root / "enbseries").mkdir()
    (root / "enbseries" / "x.fx").write_text("x")
    data = root / "Data"
    for m in ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"):
        write_plugin(data / m, flags=tes4.FLAG_MASTER)
    write_plugin(data / "ccbgssse001-fish.esm", ["Skyrim.esm"], tes4.FLAG_MASTER | tes4.FLAG_LIGHT)
    (root / "Skyrim.ccc").write_text("ccbgssse001-fish.esm\n")


@pytest.fixture
def world(tmp_path, monkeypatch):
    # --- fake Nolvus (Nolvus Dashboard layout)
    nol = tmp_path / "Nolvus" / "Instances" / "Nolvus Awakening"
    (nol / "MO2").mkdir(parents=True)
    (nol / "MO2" / "ModOrganizer.ini").write_text("[General]\ngameName=Skyrim Special Edition\n")
    nmods = nol / "MODS" / "mods"
    make_mod(nmods, "SKSE Core", modid=30379, fileid=1,
             dlls={"BackportedESLSupport.dll": ["SKSEPlugin_Query", "SKSEPlugin_Load"]},
             extra={"SKSE/Plugins/version-1-5-97-0.bin": b"a"})
    make_mod(nmods, "Quest Mod", modid=111, fileid=222, plugins=[("Quest.esp", ["Skyrim.esm"], 0)])
    make_mod(nmods, "Wyrmstooth", modid=333, fileid=444, plugins=[("Wyrmstooth.esp", ["Skyrim.esm"], 0)])
    make_mod(nmods, "Unused Nolvus Tree", modid=5, fileid=6)
    prof = nol / "MODS" / "profiles" / "Nolvus Awakening"
    prof.mkdir(parents=True)
    (prof / "modlist.txt").write_text("+Quest Mod\n+SKSE Core\n")
    (prof / "Skyrim.ini").write_text("[General]\nsLanguage=ENGLISH\n")
    make_game(nol / "STOCK GAME")
    # --- fake MV (Wabbajack layout, same volume)
    mv = tmp_path / "MV"
    (mv / "profiles" / "Default").mkdir(parents=True)
    (mv / "ModOrganizer.ini").write_text("[General]\ngameName=Skyrim Special Edition\n")
    (mv / "ModOrganizer.exe").write_bytes(b"MZ")
    (mv / "tools" / "SSEEdit").mkdir(parents=True)
    (mv / "tools" / "SSEEdit" / "SSEEdit.exe").write_bytes(b"MZ")
    mmods = mv / "mods"
    make_mod(mmods, "City Overhaul", modid=777, fileid=888,
             plugins=[("City.esp", ["Skyrim.esm"], tes4.FLAG_LIGHT)],
             dlls={"CityHelper.dll": ["SKSEPlugin_Version", "SKSEPlugin_Load"]})
    make_mod(mmods, "Patreon Hair", plugins=[("Hair.esp", ["Skyrim.esm"], 0)])
    (mv / "profiles" / "Default" / "modlist.txt").write_text("+City Overhaul\n+Patreon Hair\n")
    make_game(mv / "Stock Game", "1.6.1170.0")

    # --- target list + plan (top line = highest priority)
    tgt = tmp_path / "target"
    tgt.mkdir()
    (tgt / "modlist.txt").write_text(
        "+Pandora Output\n+Patch For Hair\n+Patreon Hair\n+City Overhaul\n-MV_separator\n"
        "+Wyrmstooth2\n+Quest Mod\n+Needs Download\n+SKSE Core\n-1.1 SKSE_separator\n")
    (tgt / "plugins.txt").write_text("*Hair.esp\n*HairPatch.esp\n*City.esp\n*Wyrmstooth.esp\n*Quest.esp\n"
                                     "*Needs.esp\n*Synthesis.esp\n")
    plan = tmp_path / "provenance.csv"
    rows = [("Pandora Output", "generated", "regenerate"), ("Patch For Hair", "unknown", "review"),
            ("Patreon Hair", "non_nexus", "drop"), ("City Overhaul", "mv", "harvest_mv"),
            ("Wyrmstooth2", "nolvus", "harvest_nolvus"), ("Quest Mod", "nolvus", "harvest_nolvus"),
            ("Needs Download", "unknown", "review"), ("SKSE Core", "nolvus", "harvest_nolvus")]
    with open(plan, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["folder", "section", "category", "action", "note"])
        for name, cat, act in rows:
            w.writerow([name, "", cat, act, ""])
    reports = tmp_path / "reports"
    pm = tmp_path / "PM"
    return dict(tmp=tmp_path, nol=nol, mv=mv, pm=pm, tgt=tgt, plan=plan, reports=reports)


def run_harvest(w, src, instance, *flags):
    args = ["--from", src, "--instance", str(instance), "--pm", str(w["pm"]), "--plan", str(w["plan"]),
            "--out", str(w["reports"]), *flags]
    return harvest.main(args)


def test_full_pipeline(world, monkeypatch):
    w = world
    # Phase 2: inventory + harvest MV (dry run first writes nothing)
    assert inventory.main(["--source", "mv", "--instance", str(w["mv"]), "--out", str(w["reports"])]) == 0
    inv = list(csv.DictReader(open(w["reports"] / "inventory-mv.csv", encoding="utf-8-sig")))
    city = next(r for r in inv if r["folder"] == "City Overhaul")
    assert city["mod_id"] == "777" and "CityHelper.dll:ae_only" in city["dll_classes"]
    assert run_harvest(w, "mv", w["mv"], "--mo2-and-tools") == 0
    assert not w["pm"].exists() or not (w["pm"] / "mods" / "City Overhaul").exists()
    assert run_harvest(w, "mv", w["mv"], "--mo2-and-tools", "--apply") == 0
    assert (w["pm"] / "ModOrganizer.exe").exists() and (w["pm"] / "tools" / "SSEEdit" / "SSEEdit.exe").exists()
    assert os.stat(w["pm"] / "mods" / "City Overhaul" / "City.esp").st_nlink == 2
    shutil.rmtree(w["mv"])                                     # user deletes D:\MV
    assert (w["pm"] / "mods" / "City Overhaul" / "City.esp").exists()

    # Phase 3: Nolvus harvest with STOCK GAME, ENB stripped, dup-suffix folder resolved
    assert inventory.main(["--source", "nolvus", "--instance", str(w["nol"]), "--out", str(w["reports"])]) == 0
    assert run_harvest(w, "nolvus", w["nol"], "--stock-game", "--apply") == 0
    assert (w["pm"] / "mods" / "Wyrmstooth2" / "Wyrmstooth.esp").exists()
    assert not (w["pm"] / "mods" / "Unused Nolvus Tree").exists()
    assert (w["pm"] / "STOCK GAME" / "SkyrimSE.exe").exists()
    assert not (w["pm"] / "STOCK GAME" / "d3d11.dll").exists()
    assert (w["nol"] / "STOCK GAME" / "d3d11.dll").exists()    # source untouched
    assert not (w["pm"] / "STOCK GAME" / "enbseries").exists()

    # Phase 4: manifest
    dec = w["tmp"] / "decisions.csv"
    dec.write_text("folder,action,note\nPatch For Hair,drop,patch for dropped Patreon Hair\n")
    assert manifest.main(["--pm", str(w["pm"]), "--target", str(w["tgt"] / "modlist.txt"),
                          "--provenance", str(w["plan"]), "--decisions", str(dec),
                          "--reports", str(w["reports"])]) == 0
    man = {r["folder"]: r for r in csv.DictReader(open(w["reports"] / "manifest.csv", encoding="utf-8-sig"))}
    assert man["City Overhaul"]["action"] == "replace_dll"
    assert man["Quest Mod"]["action"] == "keep"
    assert man["Pandora Output"]["action"] == "regenerate"
    assert man["Patreon Hair"]["action"] == "drop"
    assert man["Patch For Hair"]["action"] == "drop"
    assert man["Needs Download"]["action"] == "review"
    assert (w["reports"] / "downloads.html").read_text(encoding="utf-8").count("<tr>") >= 2

    # build instance
    bi = ["--pm", str(w["pm"]), "--manifest", str(w["reports"] / "manifest.csv"),
          "--target", str(w["tgt"] / "modlist.txt"), "--target-plugins", str(w["tgt"] / "plugins.txt"),
          "--out", str(w["reports"])]
    assert build_instance.main(["create", *bi, "--ini-from",
                                str(w["nol"] / "MODS" / "profiles" / "Nolvus Awakening"), "--apply"]) == 0
    pdir = w["pm"] / "profiles" / "Pages-ZH"
    names = [e.name for e in mo2.read_modlist(pdir / "modlist.txt")]
    assert "Patreon Hair" not in names and "Needs Download" in names and "MV_separator" in names
    assert (w["pm"] / "mods" / "Needs Download").is_dir()            # placeholder so MO2 keeps the line
    assert (w["pm"] / "mods" / "MV_separator" / "meta.ini").exists()
    assert (pdir / "Skyrim.ini").exists() and (w["pm"] / "portable.txt").exists()
    ini = (w["pm"] / "ModOrganizer.ini").read_text()
    assert "gamePath=@ByteArray(" in ini and "SSEEdit" in ini and "selected_profile=@ByteArray(Pages-ZH)" in ini
    assert build_instance.main(["verify", *bi]) == 0

    # simulate MO2 dropping a line, verify catches it
    raw = (pdir / "modlist.txt").read_bytes()
    assert b"+Needs Download\r\n" in raw
    (pdir / "modlist.txt").write_bytes(raw.replace(b"+Needs Download\r\n", b""))
    assert build_instance.main(["verify", *bi]) == 1
    shutil.copy2(pdir / "_expected" / "modlist.txt", pdir / "modlist.txt")

    # prune: Hair.esp (dropped folder) and HairPatch.esp (not provided) are removed; Synthesis pending
    make_mod(w["pm"] / "mods", "Needs Download", plugins=[("Needs.esp", ["Hair.esp"], 0)])
    assert prune_dependents.main(["--pm", str(w["pm"]), "--out", str(w["reports"]), "--apply",
                                  "--disable-folders"]) == 0
    plan = {r["plugin"]: r for r in csv.DictReader(open(w["reports"] / "prune-plan.csv", encoding="utf-8-sig"))}
    assert plan["Needs.esp"]["action"] == "remove" and "Hair.esp" in plan["Needs.esp"]["reason"]
    assert plan["Quest.esp"]["action"] == "keep" and plan["Synthesis.esp"]["action"] == "keep"
    kept = [p.name for p in mo2.read_plugins(pdir / "plugins.txt")]
    assert "Needs.esp" not in kept and "Quest.esp" in kept
    ml = {e.name: e for e in mo2.read_modlist(pdir / "modlist.txt")}
    assert not ml["Needs Download"].enabled                      # patch-only folder disabled

    # checks
    assert check_plugins.main(["--pm", str(w["pm"]), "--out", str(w["reports"])]) == 0
    cp = {r["plugin"]: r for r in csv.DictReader(open(w["reports"] / "check_plugins.csv", encoding="utf-8-sig"))}
    assert cp["Synthesis.esp"]["status"] == "pending"
    assert cp["City.esp"]["kind"] == "light" and cp["ccbgssse001-fish.esm"]["kind"] == "light"
    assert audit_skse.main(["--pm", str(w["pm"]), "--out", str(w["reports"])]) == 1   # CityHelper.dll is AE-only
    au = {r["dll"]: r for r in csv.DictReader(open(w["reports"] / "audit_skse.csv", encoding="utf-8-sig"))}
    assert au["CityHelper.dll"]["class"] == "ae_only" and au["BackportedESLSupport.dll"]["class"] == "se"

    # Phase 5: outputs generated -> restore order (Synthesis.esp goes back to its target slot)
    make_mod(w["pm"] / "mods", "SYNTH OUT", plugins=[("Synthesis.esp", ["Skyrim.esm"], 0)])
    ml_lines = (pdir / "modlist.txt").read_text()
    (pdir / "modlist.txt").write_text("+SYNTH OUT\r\n" + ml_lines)
    (pdir / "plugins.txt").write_text("*City.esp\n*Wyrmstooth.esp\n*Quest.esp\n*NewThing.esp\n")
    assert build_instance.main(["sync-order", *bi, "--apply"]) == 0
    order = [p.name for p in mo2.read_plugins(pdir / "plugins.txt")]
    assert order == ["City.esp", "Wyrmstooth.esp", "Quest.esp", "NewThing.esp", "Synthesis.esp"]


def test_preflight_evaluate():
    facts = {"windows": True, "install_drive": "D:", "gpus": [{"name": "RTX 5080 Laptop", "vram_gb": 16.0}],
             "ram_gb": 32.0, "pagefile": ["C:\\pagefile.sys 20480 40960"],
             "drives": {"D:": {"free_gb": 1000, "total_gb": 1863, "fs": "NTFS"}},
             "skyrim_dir": "x", "skyrim_exe_version": "1.7.104.0", "cc_plugins": 74, "skyrim_language": "english",
             "skyrim_auto_update": "1", "vcredist_x64": "v14.40", "defender_exclusions": ["D:\\MV", "D:\\Nolvus", "D:\\PM"],
             "dotnet": ["Microsoft.WindowsDesktop.App 6.0.36", "Microsoft.WindowsDesktop.App 8.0.10"]}
    assert preflight.evaluate(facts).worst == "PASS"
    bad = dict(facts, skyrim_language="tchinese", drives={"D:": {"free_gb": 500, "total_gb": 1000, "fs": "exFAT"}})
    r = preflight.evaluate(bad)
    fails = {c.key for c in r.checks if c.status == "FAIL"}
    assert {"lang", "disk", "disk_fs"} <= fails


def test_vdf_parser():
    text = '"AppState"\n{\n "appid" "489830"\n "installdir" "Skyrim Special Edition"\n' \
           ' "UserConfig"\n {\n  "language" "english"\n }\n}\n'
    d = preflight.parse_vdf(text)
    assert d["AppState"]["UserConfig"]["language"] == "english"
    assert pe.fixed_file_version(b"xx\xbd\x04\xef\xfe" + (0x00010000).to_bytes(4, "little")
                                 + ((1 << 16) | 5).to_bytes(4, "little") + ((97 << 16) | 0).to_bytes(4, "little")) \
        == "1.5.97.0"


def test_preflight_defender_placeholder_not_a_path():
    assert preflight.parse_exclusions("N/A: Must be an administrator to view exclusions\r\n") is None
    assert preflight.parse_exclusions("D:\\MV\r\nD:\\Nolvus\r\n") == ["D:\\MV", "D:\\Nolvus"]
    assert preflight.parse_exclusions("") == []
    facts = {"windows": True, "install_drive": "D:", "defender_exclusions": None}
    checks = {c.key: c for c in preflight.evaluate(facts).checks}
    assert checks["defender"].status == "INFO"


@pytest.mark.parametrize("vram,status,text", [(15.9, "PASS", "Tier A/S"), (13.9, "PASS", "Ultimate"),
                                              (11.9, "WARN", "Tier B"), (7.9, "FAIL", "Redux")])
def test_preflight_vram_rounding(vram, status, text):
    facts = {"windows": True, "gpus": [{"name": "GPU", "vram_gb": vram}]}
    gpu = next(c for c in preflight.evaluate(facts).checks if c.key == "gpu")
    assert gpu.status == status and text in gpu.detail and f"{vram} GB" in gpu.detail
