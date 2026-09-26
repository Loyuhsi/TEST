"""Tests for the Traditional-Chinese layer tools on synthetic data."""

import json
import struct
from pathlib import Path
from types import SimpleNamespace

import pytest

from pm import bsa, pex, strings as st, tes4
from zh import common, diff_pack, extract_official, fontconfig, llm_translate, mcm_txt, strings_glossary

opencc = pytest.importorskip("opencc")


# ---------------------------------------------------------------- common
def test_placeholders_and_keys():
    s = "Deal <Global=Dmg> damage to %s for {0} seconds. $SKI_Key [PageBreak]"
    assert common.placeholders(s) == sorted(["<Global=Dmg>", "%s", "{0}", "$SKI_Key", "[PageBreak]"])
    assert common.needs_translation("Iron Sword") and not common.needs_translation("鐵劍")
    assert not common.needs_translation("<Alias=Player> 123")
    a = common.string_key("0x0176CD|Skyrim.esm", "WEAP FULL", None)
    b = common.string_key("050176CD|skyrim.esm", "weap full", None)
    assert a == b
    c = common.string_key("FE000801|My.esl", "MISC FULL", None)
    d = common.string_key("01000801|My.esl", "MISC FULL", None, light_plugins={"my.esl"})
    assert c == d == (0x801, "my.esl", "MISC FULL", -1)


def test_translation_txt_roundtrip(tmp_path):
    p = tmp_path / "x_CHINESE.txt"
    common.write_translation_txt(p, {"$A": "設定", "$B": "Value\twith tab"})
    raw = p.read_bytes()
    assert raw.startswith(b"\xff\xfe") and common.check_translation_encoding(raw) == "utf-16le-bom"
    assert common.read_translation_txt(p) == {"$A": "設定", "$B": "Value\twith tab"}
    assert common.parse_translation_bytes("$K\tv\n".encode("utf-8")) == {"$K": "v"}


# ---------------------------------------------------------------- fontconfig
def test_fontconfig_merge():
    official = fontconfig.parse('fontlib "Interface\\fonts_cn.swf"\nmap "$EverywhereFont" = "MSJH" Normal\n'
                                'map "$ConsoleFont" = "Arial" Normal\nvalidNameChars "abc"\n')
    current = fontconfig.parse('fontlib "Interface\\fonts_edge.swf"\nmap "$EverywhereFont" = "Sanguis" Normal\n'
                               'map "$EdgeTitleFont" = "SanguisBold" Bold\n')
    text, remapped = fontconfig.merge(official, current)
    assert remapped == ["$EdgeTitleFont"]
    assert 'map "$EdgeTitleFont" = "MSJH" Normal' in text
    assert 'map "$EverywhereFont" = "MSJH" Normal' in text
    assert text.index("fonts_cn.swf") < text.index("fonts_edge.swf")
    assert 'validNameChars "abc"' in text


# ---------------------------------------------------------------- opencc
def test_opencc_convert_formats(tmp_path):
    from zh import opencc_convert as oc
    root = tmp_path / "pack"
    dsd = root / "SKSE" / "Plugins" / "DynamicStringDistributor" / "Mod.esp" / "a.json"
    dsd.parent.mkdir(parents=True)
    dsd.write_text(json.dumps([{"form_id": "0x800|Mod.esp", "type": "WEAP FULL", "string": "钢铁长剑"}],
                              ensure_ascii=False), encoding="utf-8")
    txt = root / "interface" / "translations" / "mod_chinese.txt"
    txt.parent.mkdir(parents=True)
    txt.write_bytes("$Title\t设置菜单\r\n".encode("utf-8"))          # wrong encoding on purpose
    tbl = root / "strings" / "mod_chinese.strings"
    tbl.parent.mkdir(parents=True)
    st.write(tbl, {1: "龙裔", 2: "123"})
    pins = [("鋼鐵長劍", "鋼製長劍")]
    conv = oc.Converter("s2twp", pins)
    out = oc.convert_file(dsd, conv)
    assert json.loads(out)[0]["string"] == "鋼製長劍" and json.loads(out)[0]["form_id"] == "0x800|Mod.esp"
    new_txt = oc.convert_file(txt, conv)
    assert new_txt.startswith(b"\xff\xfe") and common.parse_translation_bytes(new_txt)["$Title"] == "設定選單"
    new_tbl = oc.convert_file(tbl, conv)
    assert st.parse(new_tbl, "strings") == {1: "龍裔", 2: "123"}
    assert conv.hits["鋼鐵長劍→鋼製長劍"] == 1
    assert oc.main([str(root), "--in-place", "--out", str(tmp_path / "rep")]) == 0
    assert (dsd.parent / "a.json.bak").exists()


# ---------------------------------------------------------------- glossary
def test_glossary_en_zh_and_chs_cht(tmp_path):
    en, zh, chs = tmp_path / "en", tmp_path / "zh", tmp_path / "chs"
    for d in (en, zh, chs):
        d.mkdir()
    st.write(en / "skyrim_english.strings", {1: "Whiterun", 2: "Iron Sword", 3: "A long sentence.", 4: "Whiterun"},
             "cp1252")
    st.write(zh / "skyrim_chinese.strings", {1: "雪漫城", 2: "鐵劍", 3: "一句話。", 4: "雪漫城"})
    st.write(chs / "skyrim_chinese.strings", {1: "雪漫", 2: "铁剑"})
    rows = strings_glossary.build_en_zh(en, zh, include_dl=False, max_len=48)
    d = {r[0]: r[1] for r in rows}
    assert d == {"Whiterun": "雪漫城", "Iron Sword": "鐵劍"}
    pins = strings_glossary.build_chs_cht(chs, zh, max_cjk=16)
    assert ("雪漫", "雪漫城") in [(r[0], r[1]) for r in pins]
    assert all(r[0] != "鐵劍" for r in pins)       # s2twp already gives the official form


# ---------------------------------------------------------------- pex / diff_pack
def test_diff_pack_judge(tmp_path):
    inst = tmp_path / "inst" / "scripts" / "a.pex"
    inst.parent.mkdir(parents=True)
    inst.write_bytes(pex.build("A.psc", 111, ("Hello",)))
    good = tmp_path / "pack" / "scripts" / "a.pex"
    good.parent.mkdir(parents=True)
    good.write_bytes(pex.build("A.psc", 111, ("你好",)))
    bad = tmp_path / "pack" / "scripts" / "b.pex"
    bad.write_bytes(pex.build("B.psc", 222))
    inst_b = tmp_path / "inst" / "scripts" / "b.pex"
    inst_b.write_bytes(pex.build("B.psc", 999))
    idx = {"scripts/a.pex": inst, "scripts/b.pex": inst_b}
    assert diff_pack.judge("scripts/a.pex", good, idx, set())[0] == "accept"
    assert diff_pack.judge("scripts/b.pex", bad, idx, set())[0] == "reject"
    assert diff_pack.judge("scripts/c.pex", bad, idx, set())[0] == "skip"
    js = "SKSE/Plugins/DynamicStringDistributor/Mod.esp/x.json"
    assert diff_pack.judge(js, good, idx, {"mod.esp"})[0] == "accept"
    assert diff_pack.judge(js, good, idx, set())[0] == "skip"
    h = pex.parse(pex.build("Q.psc", 5, ("a", "b")))
    assert (h.source, h.compile_time, h.string_count) == ("Q.psc", 5, 2)


# ---------------------------------------------------------------- extract_official script check
def test_extract_official_script_summary(tmp_path):
    empty = tmp_path / "_resourcepack_chinese.dlstrings"
    trad = tmp_path / "skyrim_chinese.strings"
    simp = tmp_path / "mod_chinese.strings"
    st.write(empty, {})
    st.write(trad, {1: "這個劍與門", 2: "們說"})
    st.write(simp, {1: "这个剑与门"})
    status, detail = extract_official.script_summary([empty, trad])
    assert status == "PASS" and "繁體 1 個" in detail and "_resourcepack_chinese.dlstrings" in detail
    status, detail = extract_official.script_summary([empty, trad, simp])
    assert status == "WARN" and "mod_chinese.strings=simplified" in detail
    assert extract_official.script_summary([empty])[0] == "WARN"


# ---------------------------------------------------------------- synthetic PM with a real plugin
def grup(label: bytes, records: bytes) -> bytes:
    return b"GRUP" + struct.pack("<I", 24 + len(records)) + label + struct.pack("<IHHI", 0, 0, 0, 0) + records


def record(rtype: bytes, form_id: int, subs: list[tuple[bytes, bytes]]) -> bytes:
    body = b"".join(t + struct.pack("<H", len(d)) + d for t, d in subs)
    return rtype + struct.pack("<IIIIHH", len(body), 0, form_id, 0, 44, 0) + body


def make_plugin(path: Path, masters=("Skyrim.esm",)):
    head = tes4.build_header(path.name, masters=list(masters))
    weap = record(b"WEAP", 0x01000800, [(b"EDID", b"MyBlade\x00"), (b"FULL", b"Frost Blade\x00"),
                                        (b"DESC", b"Deals <Global=X> frost damage.\x00")])
    over = record(b"WEAP", 0x00012EB7, [(b"EDID", b"IronSword\x00"), (b"FULL", b"Iron Sword\x00")])
    path.write_bytes(head + grup(b"WEAP", weap + over))


@pytest.fixture
def pm(tmp_path):
    pm = tmp_path / "PM"
    mods = pm / "mods"
    game = pm / "STOCK GAME"
    (game / "Data").mkdir(parents=True)
    (game / "SkyrimSE.exe").write_bytes(b"MZ")
    for m in ("Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"):
        (game / "Data" / m).write_bytes(tes4.build_header(m, flags=tes4.FLAG_MASTER | tes4.FLAG_LOCALIZED))
    (mods / "Blade Mod").mkdir(parents=True)
    make_plugin(mods / "Blade Mod" / "Blade.esp")
    tr_en = common.translation_bytes({"$Title": "Blade Settings", "$Num": "100"})
    (mods / "Blade Mod" / "Blade.bsa").write_bytes(bsa.build_bsa({"interface\\translations\\blade_english.txt": tr_en}))
    dsd = mods / "ZH Pack" / "SKSE" / "Plugins" / "DynamicStringDistributor" / "Blade.esp" / "a.json"
    dsd.parent.mkdir(parents=True)
    dsd.write_text(json.dumps([{"form_id": "0x012EB7|Skyrim.esm", "type": "WEAP FULL", "string": "鐵劍"}],
                              ensure_ascii=False), encoding="utf-8")
    prof = pm / "profiles" / "Pages-ZH"
    prof.mkdir(parents=True)
    (prof / "modlist.txt").write_text("+ZH Pack\n+Blade Mod\n")
    (prof / "plugins.txt").write_text("*Blade.esp\n")
    (pm / "ModOrganizer.ini").write_text("[General]\n")
    return pm


def test_mcm_collect_and_make(pm, tmp_path):
    found = mcm_txt.collect(pm, "Pages-ZH")
    assert found[("blade", "ENGLISH")].where == "Blade.bsa"
    rows = mcm_txt.analyse(found)
    assert rows[0]["status"] == "missing"
    out = pm / "mods" / "ZH Overrides"
    assert mcm_txt.main(["make-chinese", "--pm", str(pm), "--out-mod", str(out), "--apply",
                         "--out", str(tmp_path / "r")]) == 0
    zh = common.read_translation_txt(out / "interface" / "translations" / "blade_CHINESE.txt")
    assert zh["$Title"] == "Blade Settings"
    assert (out / "interface" / "translations" / "blade_ENGLISH.txt").exists()


def test_coverage_and_llm_pipeline(pm, tmp_path, monkeypatch):
    pytest.importorskip("sse_plugin_interface")
    from zh import coverage
    work = tmp_path / "work"
    assert coverage.main(["--pm", str(pm), "--work", str(work), "--out", str(tmp_path / "r")]) == 0
    items = common.read_jsonl(work / "zh_worklist.jsonl")
    srcs = sorted(i["source"] for i in items)
    assert "Frost Blade" in srcs and "Deals <Global=X> frost damage." in srcs
    assert "Iron Sword" not in srcs                        # covered by the DSD pack
    assert "Blade Settings" in srcs and "100" not in srcs

    # fake Claude client: returns Chinese for each item, keeping placeholders
    fake_zh = {"Frost Blade": "霜凍之刃", "Deals <Global=X> frost damage.": "造成 <Global=X> 點冰霜傷害。",
               "Blade Settings": "刀刃設定"}

    def respond(params):
        payload = json.loads(params["messages"][0]["content"])
        out = {"items": [{"id": it["id"], "zh": fake_zh[it["en"]]} for it in payload["items"]]}
        assert params["output_config"]["format"]["type"] == "json_schema"
        assert params["system"][0]["cache_control"] == {"type": "ephemeral"}
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps(out, ensure_ascii=False))],
                               stop_reason="end_turn", model="claude-opus-5",
                               usage=SimpleNamespace(input_tokens=100, output_tokens=50,
                                                     cache_creation_input_tokens=0, cache_read_input_tokens=0))

    class FakeBeta:
        def create(self, betas, fallbacks, **params):
            assert fallbacks == "default" and betas == [llm_translate.FALLBACK_BETA]
            return respond(params)

    fake = SimpleNamespace(beta=SimpleNamespace(messages=FakeBeta()))
    monkeypatch.setattr(llm_translate, "client_factory", lambda: fake)
    pytest.importorskip("anthropic")  # run_sync uses the SDK's exception classes
    gl = tmp_path / "gl.tsv"
    gl.write_text("source\ttarget\nFrost\t冰霜\n", encoding="utf-8")
    assert llm_translate.main(["run", "--work", str(work), "--mode", "sync", "--glossary", str(gl),
                               "--out", str(tmp_path / "r")]) == 0
    assert not (work / "llm_cache.jsonl").exists()          # no --yes: nothing is sent
    assert llm_translate.main(["run", "--work", str(work), "--mode", "sync", "--glossary", str(gl), "--yes",
                               "--out", str(tmp_path / "r")]) == 0
    cache = llm_translate.load_cache(work)
    assert len(cache) == 3
    # nothing is pending any more, so a second run makes no API calls
    assert llm_translate.pending_units(common.read_jsonl(work / "zh_worklist.jsonl"), cache) == []
    out = pm / "mods" / "ZH - AI"
    assert llm_translate.main(["apply", "--work", str(work), "--pm", str(pm), "--out-mod", str(out),
                               "--out", str(tmp_path / "r")]) == 0
    dsd = json.loads((out / "SKSE/Plugins/DynamicStringDistributor/Blade.esp/zz_pages_ai_zh.json")
                     .read_text(encoding="utf-8"))
    by = {e["type"]: e for e in dsd}
    assert by["WEAP FULL"]["string"] == "霜凍之刃" and by["WEAP FULL"]["form_id"].endswith("|Blade.esp")
    zh = common.read_translation_txt(out / "interface" / "translations" / "blade_CHINESE.txt")
    assert zh == {"$Title": "刀刃設定", "$Num": "100"}


def test_llm_validation_and_grouping():
    assert llm_translate.validate("Hit %d times", "命中 %d 次") is None
    assert llm_translate.validate("Hit %d times", "命中次") == "placeholders changed"
    assert llm_translate.validate("Two\nlines", "兩行") == "line breaks changed"
    assert llm_translate.validate("Iron Sword", "Iron Sword") == "not translated"
    units = [{"h": str(i), "ctx": "name", "en": "x" * 100} for i in range(100)]
    groups = llm_translate.make_groups(units, max_chars=1000, max_items=40)
    assert all(len(g) <= 10 for g in groups) and sum(len(g) for g in groups) == 100
    g = llm_translate.GlossaryIndex([("Whiterun", "雪漫城"), ("Iron", "鐵"), ("Iron Sword", "鐵劍")])
    terms = g.terms_for(["An Iron Sword from Whiterun", "Ironwood"])
    assert ["Iron Sword", "鐵劍"] in terms and ["Whiterun", "雪漫城"] in terms
    assert all(t[0] != "Ironwood" for t in terms)
    item = {"kind": "dsd", "type": "BOOK DESC", "source": "x"}
    assert llm_translate.context_of(item) == "book"
    assert llm_translate.estimate([{"en": "x" * 4000}], "claude-opus-5", batch=True) > 0


def test_llm_batch_path(tmp_path):
    pytest.importorskip("anthropic")
    units = [{"h": f"h{i}", "ctx": "name", "en": f"Sword {i}"} for i in range(3)]
    groups = llm_translate.make_groups(units, max_items=2)
    submitted = {}

    def msg(payload, refuse=False):
        out = {"items": [{"id": it["id"], "zh": "劍 " + it["en"].split()[-1]} for it in payload["items"]]}
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps(out, ensure_ascii=False))],
                               stop_reason="refusal" if refuse else "end_turn", model="claude-opus-5",
                               usage=SimpleNamespace(input_tokens=10, output_tokens=5,
                                                     cache_creation_input_tokens=0, cache_read_input_tokens=8))

    class Batches:
        def create(self, requests):
            for r in requests:
                submitted[r["custom_id"]] = json.loads(r["params"]["messages"][0]["content"])
            return SimpleNamespace(id="msgbatch_1")

        def retrieve(self, bid):
            return SimpleNamespace(processing_status="ended", request_counts=SimpleNamespace(processing=0))

        def results(self, bid):
            ids = sorted(submitted)
            for n, cid in enumerate(reversed(ids)):              # results arrive in any order
                yield SimpleNamespace(custom_id=cid, result=SimpleNamespace(
                    type="succeeded", message=msg(submitted[cid], refuse=(n == 0))))

    client = SimpleNamespace(messages=SimpleNamespace(batches=Batches()))
    usage = {"input": 0.0, "cache_write": 0.0, "cache_read": 0.0, "output": 0.0}
    work = tmp_path / "w"
    work.mkdir()
    failed = llm_translate.run_batch(client, groups, llm_translate.GlossaryIndex([]), "claude-opus-5", "medium",
                                     work, usage, poll=0)
    cache = llm_translate.load_cache(work)
    assert len(cache) + len(failed) == 3 and all(f["problem"] == "refusal" for f in failed) and failed
    assert usage["input"] == 10 and usage["cache_read"] == 8            # batch usage counted at 50 %
    state = json.loads((work / "llm_batches.json").read_text())
    assert state["batches"][0]["id"] == "msgbatch_1"
