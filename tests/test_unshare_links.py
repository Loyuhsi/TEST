"""unshare_links: hardlinked tool settings get their own copy; the other link keeps its data."""

import os

import unshare_links


def setup(tmp_path):
    src = tmp_path / "Nolvus" / "BodySlide"
    dst = tmp_path / "PM" / "BodySlide"
    (src / "SliderPresets").mkdir(parents=True)
    dst.mkdir(parents=True)
    (dst / "SliderPresets").mkdir()
    for rel, data in (("Config.xml", b"<Config/>"), ("SliderPresets/Curvy.xml", b"<Preset/>"),
                      ("body.nif", b"NIF"), ("BodySlide.log", b"log")):
        (src / rel).write_bytes(data)
        os.link(src / rel, dst / rel)
    return src, dst


def run(tmp_path, dst, *flags):
    return unshare_links.main(["--path", str(dst), "--out", str(tmp_path / "reports"), *flags])


def test_dry_run_changes_nothing(tmp_path):
    src, dst = setup(tmp_path)
    assert run(tmp_path, dst) == 0
    assert os.stat(dst / "Config.xml").st_nlink == 2
    text = (tmp_path / "reports" / "unshare_links.txt").read_text(encoding="utf-8")
    assert "硬連結的設定檔 3 個" in text


def test_apply_gives_settings_their_own_copy(tmp_path):
    src, dst = setup(tmp_path)
    assert run(tmp_path, dst, "--apply") == 0
    for rel in ("Config.xml", "SliderPresets/Curvy.xml", "BodySlide.log"):
        assert os.stat(dst / rel).st_nlink == 1 and os.stat(src / rel).st_nlink == 1
        assert (dst / rel).read_bytes() == (src / rel).read_bytes()
    assert os.stat(dst / "body.nif").st_nlink == 2                      # game data stays shared
    (dst / "Config.xml").write_bytes(b"<Config changed/>")              # the tool rewrites its copy
    assert (src / "Config.xml").read_bytes() == b"<Config/>"
    assert not list(dst.glob("*.unshare-tmp"))


def test_missing_folder_fails(tmp_path):
    assert run(tmp_path, tmp_path / "nope") == 1
