"""Tests for the Traditional-Chinese layer tools on synthetic data."""

import json
import struct
from pathlib import Path
from types import SimpleNamespace

import pytest

from pm import bsa, pex, strings as st, tes4
from pm.report import read_csv
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
    first_bak = (dsd.parent / "a.json.bak").read_bytes()
    dsd.write_text(json.dumps([{"form_id": "0x800|Mod.esp", "type": "WEAP FULL", "string": "设置"}],
                              ensure_ascii=False), encoding="utf-8")
    assert oc.main([str(root), "--in-place", "--out", str(tmp_path / "rep")]) == 0
    assert (dsd.parent / "a.json.bak").read_bytes() == first_bak              # the original is kept


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
    usd, basis = llm_translate.estimate([{"en": "x" * 4000}], "claude-opus-5", batch=True)
    assert usd > 0 and basis.startswith("粗估")


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
    usage = {}
    work = tmp_path / "w"
    work.mkdir()
    failed = llm_translate.run_batch(client, groups, llm_translate.GlossaryIndex([]), "claude-opus-5", "medium",
                                     work, usage, poll=0)
    cache = llm_translate.load_cache(work)
    assert len(cache) + len(failed) == 3 and all(f["problem"] == "refusal" for f in failed) and failed
    slot = usage["claude-opus-5|batch"]                                  # raw tokens of both results
    assert slot["input"] == 20 and slot["cache_read"] == 16 and slot["output"] == 10
    full = (20 * 5 + 16 * 5 * 0.1 + 10 * 25) / 1e6
    assert llm_translate.cost(usage) == pytest.approx(full / 2)          # batch price is half
    assert llm_translate.cost(usage, list_price=True) == pytest.approx(full)
    state = json.loads((work / "llm_batches.json").read_text())
    assert state["batches"][0]["id"] == "msgbatch_1" and state["batches"][0]["collected"] is True


def test_resume_collects_an_uncollected_batch_without_resending(tmp_path):
    work = tmp_path / "w"
    work.mkdir()
    (work / "llm_batches.json").write_text(json.dumps(
        {"batches": [{"id": "msgbatch_old", "groups": {"g0": ["h1", "h2"]}}]}), encoding="utf-8")
    known = {"h1": {"h": "h1", "ctx": "name", "en": "Sword"}, "h2": {"h": "h2", "ctx": "name", "en": "Shield"}}
    out = {"items": [{"id": "k0", "zh": "劍"}, {"id": "k1", "zh": "盾"}]}

    class Batches:
        created = 0

        def create(self, requests):                                      # must not be called
            Batches.created += 1

        def retrieve(self, bid):
            assert bid == "msgbatch_old"
            return SimpleNamespace(processing_status="ended", request_counts=SimpleNamespace(processing=0))

        def results(self, bid):
            msg = SimpleNamespace(content=[SimpleNamespace(type="text", text=json.dumps(out, ensure_ascii=False))],
                                  stop_reason="end_turn", model="claude-opus-5",
                                  usage=SimpleNamespace(input_tokens=10, output_tokens=6,
                                                        cache_creation_input_tokens=0, cache_read_input_tokens=0))
            yield SimpleNamespace(custom_id="g0", result=SimpleNamespace(type="succeeded", message=msg))

    client = SimpleNamespace(messages=SimpleNamespace(batches=Batches()))
    usage = {}
    n, chars = llm_translate.resume_batches(client, work, known, usage, poll=0)
    assert (n, chars) == (1, len("Sword") + len("Shield")) and Batches.created == 0
    assert {r["zh"] for r in llm_translate.load_cache(work).values()} == {"劍", "盾"}
    state = json.loads((work / "llm_batches.json").read_text())
    assert state["batches"][0]["collected"] is True
    assert llm_translate.resume_batches(client, work, known, usage, poll=0) == (0, 0)   # nothing left


def test_estimate_uses_the_measured_rate(tmp_path):
    work = tmp_path / "w"
    work.mkdir()
    llm_translate.record_usage(work, "claude-opus-5", "medium", 10, 1000,
                               {"claude-opus-5|sync": {"input": 1000, "cache_write": 0, "cache_read": 0,
                                                       "output": 2000}})
    rate = (1000 * 5 + 2000 * 25) / 1e6 / 1000                           # US$ per character
    usd, basis = llm_translate.estimate([{"en": "x" * 2000}], "claude-opus-5", True, work, "medium")
    assert usd == pytest.approx(2000 * rate / 2) and basis.startswith("依實測")
    usd2, basis2 = llm_translate.estimate([{"en": "x" * 2000}], "claude-opus-5", True, work, "high")
    assert basis2.startswith("粗估")                                     # other effort: no measurement


def test_prefill_uses_only_unambiguous_official_terms(tmp_path):
    work = tmp_path / "w"
    work.mkdir()
    gl = tmp_path / "gl.tsv"
    gl.write_text("source\ttarget\tcount\tvariants\ttable\n"
                  "Iron Sword\t鐵劍\t9\t1\tskyrim.strings\n"
                  "Bolt\t弩箭\t3\t2\tskyrim.strings\n", encoding="utf-8")
    exact = llm_translate.exact_glossary(gl)
    assert exact == {"Iron Sword": "鐵劍"}
    units = [{"h": "a", "ctx": "name", "en": "Iron Sword"}, {"h": "b", "ctx": "name", "en": "Bolt"},
             {"h": "c", "ctx": "name", "en": "Iron Sword of Doom"}]
    assert llm_translate.prefill(units, exact, work) == 1
    assert list(llm_translate.load_cache(work)) == ["a"]


def add_localized_plugin(pm):
    """Loc.esp (localized) with English tables in its mod and a Chinese table in the ZH pack."""
    mods = pm / "mods"
    (mods / "Loc Mod" / "strings").mkdir(parents=True)
    (mods / "Loc Mod" / "Loc.esp").write_bytes(tes4.build_header("Loc.esp", flags=tes4.FLAG_LOCALIZED))
    st.write(mods / "Loc Mod" / "strings" / "loc_english.strings", {5: "Hello", 6: "World"})
    (mods / "ZH Pack" / "strings").mkdir(parents=True)
    st.write(mods / "ZH Pack" / "strings" / "loc_chinese.strings", {6: "世界"})
    game_strings = pm / "STOCK GAME" / "Data" / "strings"
    game_strings.mkdir(parents=True)
    st.write(game_strings / "skyrim_english.strings", {1: "Whiterun"})
    prof = pm / "profiles" / "Pages-ZH"
    (prof / "modlist.txt").write_text("+ZH Pack\n+Loc Mod\n+Blade Mod\n")
    (prof / "plugins.txt").write_text("*Blade.esp\n*Loc.esp\n")


def test_apply_builds_tables_on_the_current_chinese_and_skips_official(pm, tmp_path):
    add_localized_plugin(pm)
    items = [{"kind": "strings", "plugin": "Loc.esp", "file": "loc", "key": "5", "source": "Hello"},
             {"kind": "strings", "plugin": "Skyrim.esm", "file": "skyrim", "key": "1", "source": "Whiterun"}]
    cache = {llm_translate.cache_key("text", "Hello"): {"zh": "哈囉"},
             llm_translate.cache_key("text", "Whiterun"): {"zh": "雪漫城"}}
    out = pm / "mods" / "ZH - AI"
    stats = llm_translate.apply_results(items, cache, pm, "Pages-ZH", out)
    assert st.read(out / "strings" / "loc_chinese.strings") == {5: "哈囉", 6: "世界"}   # superset of the pack
    assert not (out / "strings" / "skyrim_chinese.strings").exists()
    assert stats["official_skipped"] == 1 and stats["string_tables"] == 1


def test_coverage_skips_official_and_counts_unmatched_dsd(pm, tmp_path):
    pytest.importorskip("sse_plugin_interface")
    from zh import coverage
    add_localized_plugin(pm)
    base = pm / "mods" / "ZH Pack" / "SKSE" / "Plugins" / "DynamicStringDistributor"
    (base / "Blade.esp" / "b.json").write_text(json.dumps(
        [{"form_id": "0x000999|Blade.esp", "type": "WEAP FULL", "string": "不存在"}], ensure_ascii=False),
        encoding="utf-8")
    (base / "Gone.esp").mkdir()
    (base / "Gone.esp" / "a.json").write_text(json.dumps(
        [{"form_id": "0x000800|Gone.esp", "type": "WEAP FULL", "string": "x"}]), encoding="utf-8")
    zh_mod = pm / "mods" / "ZH - Nexus"
    zh_mod.mkdir()
    (zh_mod / "Blade.esp").write_bytes(b"translated copy")                # loses to Blade Mod below
    (pm / "profiles" / "Pages-ZH" / "modlist.txt").write_text("+Blade Mod\n+ZH Pack\n+ZH - Nexus\n+Loc Mod\n")
    work = tmp_path / "work"
    assert coverage.main(["--pm", str(pm), "--work", str(work), "--out", str(tmp_path / "r")]) == 0
    items = common.read_jsonl(work / "zh_worklist.jsonl")
    assert {i["plugin"] for i in items if i["kind"] == "strings"} == {"Loc.esp"}   # Skyrim.esm is official
    assert [i["source"] for i in items if i["kind"] == "strings"] == ["Hello"]
    rows = {r["mod"]: r for r in read_csv(tmp_path / "r" / "zh_dsd_unmatched.csv")}
    assert rows["ZH Pack"]["entries"] == "2" and rows["ZH Pack"]["unmatched"] == "1"
    assert rows["ZH Pack"]["inactive_plugin"] == "1"
    text = (tmp_path / "r" / "zh_coverage.txt").read_text(encoding="utf-8")
    assert "Blade.esp（ZH - Nexus 被 Blade Mod 蓋掉）" in text
    assert "官方插件（本體、DLC、CC）仍是英文的字串：1 條" in text


def test_fontconfig_ignores_its_own_output(pm):
    mods = pm / "mods"
    for folder, font in (("ZH Overrides", "MSJH"), ("Edge UI", "Sanguis")):
        (mods / folder / "interface").mkdir(parents=True)
        (mods / folder / "interface" / "fontconfig.txt").write_text(f'map "$EverywhereFont" = "{font}" Normal\n')
    (pm / "profiles" / "Pages-ZH" / "modlist.txt").write_text("+ZH Overrides\n+Edge UI\n+ZH Pack\n+Blade Mod\n")
    assert fontconfig.winning_fontconfig(pm, "Pages-ZH").parent.parent.name == "ZH Overrides"
    found = fontconfig.winning_fontconfig(pm, "Pages-ZH", skip=mods / "ZH Overrides")
    assert found.parent.parent.name == "Edge UI"
