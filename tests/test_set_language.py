"""build_instance set-language and the ini helpers behind it."""

import build_instance as bi


def test_set_ini_value_replaces_inserts_and_keeps_line_endings():
    text = "[General]\r\nsLanguage=ENGLISH\r\nuGridsToLoad=5\r\n[Archive]\r\nsResourceArchiveList2=A.bsa\r\n"
    out = bi.set_ini_value(text, "General", "sLanguage", "CHINESE")
    assert out == text.replace("ENGLISH", "CHINESE")
    assert bi.ini_value(out, "general", "SLANGUAGE") == "CHINESE"
    added = bi.set_ini_value("[General]\nuGridsToLoad=5\n", "General", "sLanguage", "CHINESE")
    assert added == "[General]\nsLanguage=CHINESE\nuGridsToLoad=5\n"
    assert bi.set_ini_value("[Display]\nx=1\n", "General", "sLanguage", "CHINESE").startswith("[General]\nsLanguage=")
    assert bi.ini_value("[Archive]\nsLanguage=X\n", "General", "sLanguage") is None     # other section


def profile(tmp_path, archives="Skyrim - Voices_en0.bsa, Skyrim - Patch.bsa"):
    pm = tmp_path / "PM"
    pdir = pm / "profiles" / "Pages-ZH"
    pdir.mkdir(parents=True)
    ini = pdir / "Skyrim.ini"
    ini.write_bytes(f"[General]\r\nsLanguage=ENGLISH\r\nsIntroSequence=\xe9\r\n[Archive]\r\n"
                    f"sResourceArchiveList2={archives}\r\n".encode("latin-1"))
    return pm, ini


def run(pm, tmp_path, *extra):
    return bi.main(["set-language", "--pm", str(pm), "--out", str(tmp_path / "r"), *extra])


def test_set_language_dry_run_then_apply(tmp_path):
    pm, ini = profile(tmp_path)
    before = ini.read_bytes()
    assert run(pm, tmp_path) == 0
    assert ini.read_bytes() == before                                    # dry run
    assert run(pm, tmp_path, "--apply") == 0
    assert bi.ini_value(bi.read_ini(ini), "General", "sLanguage") == "CHINESE"
    assert ini.read_bytes() == before.replace(b"ENGLISH", b"CHINESE")    # other bytes untouched
    assert list((ini.parent / "_backup").glob("*/Skyrim.ini"))
    text = (tmp_path / "r" / "build_instance-set-language.txt").read_text(encoding="utf-8")
    assert "Voices_en0" in text and "[注意]" not in text
    assert run(pm, tmp_path, "--apply") == 0                            # already set
    assert "已經是 sLanguage=CHINESE" in (tmp_path / "r" / "build_instance-set-language.txt").read_text(encoding="utf-8")


def test_missing_english_voices_is_flagged(tmp_path):
    pm, _ini = profile(tmp_path, archives="Skyrim - Patch.bsa")
    assert run(pm, tmp_path) == 0
    assert "[注意]" in (tmp_path / "r" / "build_instance-set-language.txt").read_text(encoding="utf-8")


def test_missing_profile_ini_fails(tmp_path):
    (tmp_path / "PM" / "profiles" / "Pages-ZH").mkdir(parents=True)
    assert run(tmp_path / "PM", tmp_path) == 1
