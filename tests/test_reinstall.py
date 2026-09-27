"""manifest "reinstall" decisions and nexus_fetch recognising downloads by their .meta."""

from pathlib import Path

import pytest

import manifest
import nexus_fetch
from pm import mo2

IDS = {"mod_id": "29695", "file_id": "110913", "version": "1.3", "source": "decision"}
DEC = {"folder": "Frescoes", "action": "reinstall", "note": "Complete (No Lanterns) ESL"}


def write_meta_ini(folder: Path, mod_id: str, file_id: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "meta.ini").write_text(mo2.install_meta_text(mod_id, file_id, "1.3", "x.rar"), encoding="utf-8")


def test_installed_file_ids_reads_every_installed_file(tmp_path):
    folder = tmp_path / "Frescoes"
    write_meta_ini(folder, "29695", "110909")
    with open(folder / "meta.ini", "a", encoding="utf-8") as f:     # MO2 lists merged installs as 2\\, 3\\ ...
        f.write("2\\modid=29695\r\n2\\fileid=110913\r\n")
    assert manifest.installed_file_ids(folder) == {"110909", "110913"}
    assert manifest.installed_file_ids(tmp_path / "none") == set()


def test_reinstall_waits_until_the_chosen_file_is_installed():
    assert manifest.decide({}, True, IDS, DEC, [], {"110909"})[0] == "reinstall"
    assert manifest.decide({}, True, IDS, DEC, [], set())[0] == "reinstall"
    assert manifest.decide({}, True, IDS, DEC, [], {"110909", "110913"}) == ("keep", "已重裝成指定的檔案")
    assert manifest.decide({}, False, IDS, DEC, [], set())[0] == "download"


def test_manifest_reports_reinstall_rows(tmp_path):
    pm = tmp_path / "PM"
    write_meta_ini(pm / "mods" / "Frescoes", "29695", "110909")
    (pm / "mods" / "Frescoes" / "SolitudeTempleFrescoes.esp").write_bytes(b"x")
    write_meta_ini(pm / "mods" / "Done", "1", "2")
    (tmp_path / "modlist.txt").write_text("+Done\n+Frescoes\n", encoding="utf-8")
    (tmp_path / "provenance.csv").write_text("folder,category,section,note\nFrescoes,mv,,\nDone,mv,,\n",
                                             encoding="utf-8")
    (tmp_path / "decisions.csv").write_text(
        "folder,action,note,nexus_mod_id,nexus_file_id,nexus_version\n"
        "Frescoes,reinstall,Complete (No Lanterns) ESL,29695,110913,1.3\n"
        "Done,reinstall,already swapped,1,2,1.0\n", encoding="utf-8")
    out = tmp_path / "reports"
    assert manifest.main(["--pm", str(pm), "--target", str(tmp_path / "modlist.txt"),
                          "--provenance", str(tmp_path / "provenance.csv"),
                          "--decisions", str(tmp_path / "decisions.csv"), "--reports", str(out)]) == 0
    rows = {r["folder"]: r for r in manifest.read_csv(out / "manifest.csv")}
    assert (rows["Frescoes"]["action"], rows["Frescoes"]["nexus_file_id"]) == ("reinstall", "110913")
    assert rows["Done"]["action"] == "keep"
    text = (out / "manifest.txt").read_text(encoding="utf-8")
    assert "[注意] 需整包重裝（舊內容移到 _replaced）：1 個" in text
    assert "Frescoes" in (out / "downloads.html").read_text(encoding="utf-8")


@pytest.fixture
def fetch_world(tmp_path, monkeypatch):
    pm = tmp_path / "PM"
    dl = pm / "downloads"
    dl.mkdir(parents=True)
    (dl / "Have-1-11.7z").write_bytes(b"archive")
    (dl / "Have-1-11.7z.meta").write_text("[General]\r\nmodID=1\r\nfileID=11\r\ninstalled=false\r\n",
                                          encoding="utf-8", newline="")
    (dl / "Orphan.meta").write_text("[General]\r\nmodID=3\r\nfileID=33\r\n", encoding="utf-8")   # no archive
    (tmp_path / "manifest.csv").write_text(
        "folder,action,nexus_mod_id,nexus_file_id\n"
        "Have,reinstall,1,11\nOrphan,download,3,33\nNew,download,2,22\nKept,keep,4,44\n", encoding="utf-8")
    return pm, tmp_path


def test_downloaded_needs_both_meta_and_archive(fetch_world):
    pm, _ = fetch_world
    assert nexus_fetch.downloaded(pm / "downloads") == {("1", "11"): "Have-1-11.7z"}


def test_dry_run_marks_downloads_already_there(fetch_world):
    pm, root = fetch_world
    assert nexus_fetch.main(["--pm", str(pm), "--manifest", str(root / "manifest.csv"), "--out", str(root)]) == 0
    rows = {r["folder"]: r["status"] for r in manifest.read_csv(root / "nexus_fetch.csv")}
    assert rows == {"Have": "already_downloaded", "Orphan": "planned", "New": "planned"}


def test_apply_skips_the_api_for_downloads_already_there(fetch_world, monkeypatch):
    pm, root = fetch_world
    asked = []

    def fake_api(url, key):
        asked.append(url)
        raise nexus_fetch.urllib.error.HTTPError(url, 404, "Not Found", None, None)

    monkeypatch.setenv("NEXUS_API_KEY", "test")
    monkeypatch.setattr(nexus_fetch, "api_get", fake_api)
    monkeypatch.setattr(nexus_fetch.time, "sleep", lambda s: None)
    assert nexus_fetch.main(["--pm", str(pm), "--manifest", str(root / "manifest.csv"), "--out", str(root),
                             "--apply"]) == 0
    rows = {r["folder"]: r for r in manifest.read_csv(root / "nexus_fetch.csv")}
    assert rows["Have"]["status"] == "already_downloaded" and rows["Have"]["archive"] == "Have-1-11.7z"
    assert not any("/mods/1/files/11" in u for u in asked)
    assert any("/mods/2/files/22" in u for u in asked)
