"""Translate the remaining English strings to Taiwan Traditional Chinese with the Claude API.

以 Claude API 將剩餘英文字串翻成台灣繁體中文，並輸出成 DSD JSON／介面翻譯檔／字串表（不新增任何插件）。

Steps (the API key comes from ANTHROPIC_API_KEY or an `ant auth login` profile; never stored here):
    python -m pip install anthropic
    python tools\\zh\\llm_translate.py estimate --work D:\\PM\\zh-work
    python tools\\zh\\llm_translate.py run --work D:\\PM\\zh-work --glossary D:\\PM\\zh-work\\glossary_en_zh.tsv --yes
    python tools\\zh\\llm_translate.py apply --work D:\\PM\\zh-work --pm D:\\PM --out-mod "D:\\PM\\mods\\ZH - AI 翻譯"

run --mode batch (default) uses the Message Batches API (50 % price, results within ~1 h, max 24 h);
items the model refuses or that fail placeholder checks are retried one by one with
--mode sync, which uses server-side fallbacks ("default") on refusals.
Every translation is cached in <work>\\llm_cache.jsonl, so runs can be interrupted and resumed: a run
first collects the batches an earlier run submitted (<work>\\llm_batches.json) before sending anything.
Texts that exactly match an unambiguous glossary entry take the official translation without an API call.
Each run appends its real token usage to <work>\\llm_usage.jsonl; estimate then extrapolates from it.
apply never writes string tables of official masters, and builds every table on the Chinese table the
game currently loads, so it can only add translations.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pm import fsutil, strings as st, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report  # noqa: E402
from zh.common import (PRICES, has_cjk, is_official_plugin, placeholders, read_jsonl,  # noqa: E402
                       source_hash, write_dsd_file, write_translation_txt)
from zh.coverage import localized_table, loose_strings_index  # noqa: E402

DEFAULT_MODEL = "claude-opus-5"
THINKING_ALLOWANCE = 1.0     # rough estimate only: thinking can add as many output tokens as the answer
FALLBACK_BETA = "server-side-fallback-2026-07-01"
MAX_BATCH_CHARS = 6000
MAX_BATCH_ITEMS = 40
OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {"items": {"type": "array", "items": {
        "type": "object",
        "properties": {"id": {"type": "string"}, "zh": {"type": "string"}},
        "required": ["id", "zh"], "additionalProperties": False}}},
    "required": ["items"], "additionalProperties": False,
}
SYSTEM_PROMPT = """You translate text from The Elder Scrolls V: Skyrim Special Edition and its mods from English into Traditional Chinese as written in Taiwan (繁體中文，台灣用語).

Follow the style of Bethesda's official Traditional Chinese localization of Skyrim: an archaic, epic fantasy register; concise item and spell names; natural spoken dialogue that fits each speaker; no internet slang and no Mainland Chinese vocabulary.

Names and terms:
- Each request may include a glossary of official translations. When an English term from the glossary appears, use its Chinese form exactly.
- For names not in the glossary, translate meaningful names and transliterate personal names in the manner of the official localization, and keep the same rendering for the same name within the request.

Markup and placeholders must survive unchanged, character for character: anything inside angle brackets such as <Alias=Player>, <Global=GameHour>, <font face='$HandwrittenFont'>, <p align='center'>, <br>; printf fields such as %s, %d, %.1f, %%; {0}; tokens that start with $ such as $SKI_Settings; [PageBreak]. Keep the original line breaks and their count. Keep numbers as digits.

Item types tell you where the text appears: name (short in-game names; no trailing punctuation), description (item/spell/perk descriptions), dialogue (spoken lines), prompt (a player dialogue choice; keep it short), quest (journal entries and objectives), ui (menu and MCM labels; keep them as short as the English), book (book or note text that may contain HTML; translate only the visible text), text (anything else).
Use full-width Chinese punctuation (，。！？：「」) in Chinese sentences; leave punctuation inside markup untouched.

Return every input id exactly once, with its translation in "zh". If a text has nothing to translate (only numbers, symbols or markup), return it unchanged."""

CONTEXT = {"FULL": "name", "SHRT": "name", "TNAM": "name", "RNAM": "prompt", "RDMP": "name", "NAM1": "dialogue",
           "DESC": "description", "DNAM": "description", "CNAM": "description", "NNAM": "quest", "ITXT": "ui",
           "EPF2": "ui", "EPFD": "ui"}


def context_of(item: dict) -> str:
    if item["kind"] == "mcm":
        return "ui"
    if item["kind"] == "strings":
        return "text"
    rtype, _, sub = (item.get("type") or "").partition(" ")
    if rtype == "BOOK" and sub == "DESC":
        return "book"
    if rtype == "QUST" and sub == "CNAM":
        return "quest"
    if rtype == "INFO" and sub == "RNAM":
        return "prompt"
    return CONTEXT.get(sub, "text")


# ------------------------------------------------------------------ glossary / cache
def glossary_rows(path: Path | None) -> list[list[str]]:
    if not path or not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return [row for row in csv.reader(f, delimiter="\t") if len(row) >= 2 and row[0] != "source"]


def load_glossary(path: Path | None, limit_len: int = 48) -> list[tuple[str, str]]:
    return [(row[0], row[1]) for row in glossary_rows(path) if 1 < len(row[0]) <= limit_len]


def exact_glossary(path: Path | None) -> dict[str, str]:
    """English text -> official Chinese, only for entries with a single official rendering."""
    out = {}
    for row in glossary_rows(path):
        variants = row[3] if len(row) > 3 else "1"
        if variants.strip() in ("", "1") and has_cjk(row[1]):
            out[row[0]] = row[1]
    return out


def prefill(units: list[dict], exact: dict[str, str], work: Path) -> int:
    """Cache units whose whole text is an official term; returns how many."""
    rows = []
    for u in units:
        zh = exact.get(u["en"].strip())
        if zh and validate(u["en"], zh) is None:
            rows.append({"h": u["h"], "ctx": u["ctx"], "en": u["en"], "zh": zh, "model": "official-glossary"})
    if rows:
        append_cache(work, rows)
    return len(rows)


class GlossaryIndex:
    def __init__(self, pairs: list[tuple[str, str]]):
        self.by_first: dict[str, list[tuple[str, str, re.Pattern]]] = defaultdict(list)
        for en, zh in pairs:
            words = re.findall(r"[A-Za-z']+", en)
            if words:
                pat = re.compile(r"(?<![A-Za-z])" + re.escape(en) + r"(?![A-Za-z])", re.I)
                self.by_first[words[0].lower()].append((en, zh, pat))

    def terms_for(self, texts: list[str], limit: int = 150) -> list[list[str]]:
        found: dict[str, str] = {}
        for text in texts:
            for w in set(re.findall(r"[A-Za-z']+", text.lower())):
                for en, zh, pat in self.by_first.get(w, ()):
                    if en not in found and pat.search(text):
                        found[en] = zh
        ranked = sorted(found.items(), key=lambda kv: -len(kv[0]))[:limit]
        return [[en, zh] for en, zh in ranked]


def cache_key(ctx: str, source: str) -> str:
    return source_hash(ctx + "\x1f" + source)


def load_cache(work: Path) -> dict[str, dict]:
    return {r["h"]: r for r in read_jsonl(work / "llm_cache.jsonl")}


def append_cache(work: Path, rows: list[dict]) -> None:
    with open(work / "llm_cache.jsonl", "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------ grouping / validation
def pending_units(items: list[dict], cache: dict) -> list[dict]:
    """Unique (context, source) pairs not yet cached."""
    seen: dict[str, dict] = {}
    for it in items:
        ctx = context_of(it)
        h = cache_key(ctx, it["source"])
        if h not in cache and h not in seen:
            seen[h] = {"h": h, "ctx": ctx, "en": it["source"]}
    return sorted(seen.values(), key=lambda u: (u["ctx"], len(u["en"])))


def make_groups(units: list[dict], max_chars: int = MAX_BATCH_CHARS, max_items: int = MAX_BATCH_ITEMS) -> list[list[dict]]:
    groups, cur, chars = [], [], 0
    for u in units:
        n = len(u["en"])
        if cur and (len(cur) >= max_items or chars + n > max_chars):
            groups.append(cur)
            cur, chars = [], 0
        cur.append(u)
        chars += n
    if cur:
        groups.append(cur)
    return groups


def user_message(group: list[dict], gloss: GlossaryIndex) -> str:
    payload = {"glossary": gloss.terms_for([u["en"] for u in group]),
               "items": [{"id": f"k{i}", "type": u["ctx"], "en": u["en"]} for i, u in enumerate(group)]}
    return json.dumps(payload, ensure_ascii=False)


def validate(en: str, zh: str) -> str | None:
    if not zh.strip():
        return "empty"
    if placeholders(en) != placeholders(zh):
        return "placeholders changed"
    if en.count("\n") != zh.count("\n"):
        return "line breaks changed"
    if re.search(r"[A-Za-z]{3}", re.sub(r"<[^>]*>|\$\w+|%\w", "", en)) and not has_cjk(zh):
        return "not translated"
    return None


def parse_result(group: list[dict], text: str, model: str) -> tuple[list[dict], list[dict]]:
    """Return (good cache rows, failed units)."""
    try:
        data = json.loads(text)
        got = {d["id"]: d["zh"] for d in data.get("items", [])}
    except (ValueError, KeyError, TypeError, AttributeError):
        return [], list(group)
    good, bad = [], []
    for i, u in enumerate(group):
        zh = got.get(f"k{i}")
        problem = "missing" if zh is None else validate(u["en"], zh)
        if problem:
            bad.append({**u, "problem": problem})
        else:
            good.append({"h": u["h"], "ctx": u["ctx"], "en": u["en"], "zh": zh, "model": model})
    return good, bad


# ------------------------------------------------------------------ API calls
def client_factory():
    try:
        import anthropic  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise SystemExit("需要 anthropic 套件：python -m pip install anthropic") from e
    return anthropic.Anthropic()


def request_params(group: list[dict], gloss: GlossaryIndex, model: str, effort: str) -> dict:
    return {
        "model": model,
        "max_tokens": 16000,
        "system": [{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        "output_config": {"effort": effort, "format": {"type": "json_schema", "schema": OUTPUT_SCHEMA}},
        "messages": [{"role": "user", "content": user_message(group, gloss)}],
    }


def text_of(message) -> str:
    return next((b.text for b in message.content if getattr(b, "type", "") == "text"), "")


def run_sync(client, groups, gloss, model, effort, work, usage) -> list[dict]:
    import anthropic  # type: ignore
    failed = []
    for n, group in enumerate(groups, start=1):
        params = request_params(group, gloss, model, effort)
        try:
            resp = client.beta.messages.create(betas=[FALLBACK_BETA], fallbacks="default", **params)
        except anthropic.BadRequestError as e:
            failed += [{**u, "problem": f"bad request: {e.message}"} for u in group]
            continue
        except anthropic.RateLimitError:
            time.sleep(60)
            failed += [{**u, "problem": "rate limited"} for u in group]
            continue
        except (anthropic.APIStatusError, anthropic.APIConnectionError) as e:
            failed += [{**u, "problem": f"api error: {e}"} for u in group]
            continue
        add_usage(usage, resp.usage, batch=False, model=resp.model or model)
        if resp.stop_reason == "refusal":
            failed += [{**u, "problem": "refusal"} for u in group]
            continue
        good, bad = parse_result(group, text_of(resp), resp.model)
        append_cache(work, good)
        failed += bad
        if n % 20 == 0:
            print(f"  同步翻譯 {n}/{len(groups)} 組 …", flush=True)
    return failed


def batch_state(work: Path) -> tuple[Path, dict]:
    path = work / "llm_batches.json"
    return path, (json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"batches": []})


def wait_and_collect(client, batch_id: str, by_id: dict[str, list[dict]], work: Path, usage: dict,
                     poll: int) -> list[dict]:
    """Wait for one batch to end, cache its good results, return the failed units."""
    while True:
        b = client.messages.batches.retrieve(batch_id)
        if b.processing_status == "ended":
            break
        print(f"  批次 {batch_id} 處理中：{b.request_counts.processing} 組待完成 …", flush=True)
        time.sleep(poll)
    failed = []
    for result in client.messages.batches.results(batch_id):
        group = by_id.get(result.custom_id, [])
        if result.result.type != "succeeded":
            failed += [{**u, "problem": f"batch {result.result.type}"} for u in group]
            continue
        msg = result.result.message
        add_usage(usage, msg.usage, batch=True, model=msg.model)
        if msg.stop_reason == "refusal":
            failed += [{**u, "problem": "refusal"} for u in group]
            continue
        good, bad = parse_result(group, text_of(msg), msg.model)
        append_cache(work, good)
        failed += bad
    return failed


def resume_batches(client, work: Path, known: dict[str, dict], usage: dict, poll: int) -> tuple[int, int]:
    """Collect batches an earlier run submitted but never collected (they are already paid for).

    Returns (batches collected, source characters they covered). Items that failed stay uncached and
    are simply pending again."""
    path, state = batch_state(work)
    n = chars = 0
    for entry in state["batches"]:
        if entry.get("collected"):
            continue
        by_id = {cid: [known[h] for h in hashes if h in known] for cid, hashes in entry["groups"].items()}
        print(f"  回收上次送出的批次 {entry['id']} …", flush=True)
        wait_and_collect(client, entry["id"], by_id, work, usage, poll)
        entry["collected"] = True
        path.write_text(json.dumps(state), encoding="utf-8")
        n += 1
        chars += sum(len(u["en"]) for group in by_id.values() for u in group)
    return n, chars


def run_batch(client, groups, gloss, model, effort, work, usage, poll: int) -> list[dict]:
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming  # type: ignore
    from anthropic.types.messages.batch_create_params import Request  # type: ignore
    state_path, state = batch_state(work)
    by_id = {}
    requests = []
    for i, group in enumerate(groups):
        cid = f"g{i:06d}-{group[0]['h'][:12]}"
        by_id[cid] = group
        requests.append(Request(custom_id=cid, params=MessageCreateParamsNonStreaming(
            **request_params(group, gloss, model, effort))))
    failed = []
    for start in range(0, len(requests), 5000):
        chunk = requests[start:start + 5000]
        batch = client.messages.batches.create(requests=chunk)
        entry = {"id": batch.id, "groups": {r["custom_id"]: [u["h"] for u in by_id[r["custom_id"]]] for r in chunk}}
        state["batches"].append(entry)
        state_path.write_text(json.dumps(state), encoding="utf-8")
        print(f"  已送出批次 {batch.id}（{len(chunk)} 組）", flush=True)
        failed += wait_and_collect(client, batch.id, by_id, work, usage, poll)
        entry["collected"] = True
        state_path.write_text(json.dumps(state), encoding="utf-8")
    return failed


TOKEN_FIELDS = (("input", "input_tokens"), ("cache_write", "cache_creation_input_tokens"),
                ("cache_read", "cache_read_input_tokens"), ("output", "output_tokens"))


def add_usage(usage: dict, u, batch: bool, model: str) -> None:
    """Raw token counts per 'model|batch' or 'model|sync' (output tokens include thinking)."""
    slot = usage.setdefault(f"{model}|{'batch' if batch else 'sync'}", dict.fromkeys(k for k, _ in TOKEN_FIELDS))
    for k, attr in TOKEN_FIELDS:
        slot[k] = (slot[k] or 0) + (getattr(u, attr, 0) or 0)


def price(model: str) -> tuple[float, float, float]:
    return PRICES.get(model, PRICES[DEFAULT_MODEL])


def cost(usage: dict, list_price: bool = False) -> float:
    """US$ for recorded usage; list_price=True ignores the batch discount (for per-character rates)."""
    total = 0.0
    for slot, t in usage.items():
        model, _, mode = slot.partition("|")
        a, b, c = price(model)
        usd = ((t["input"] or 0) * a + (t["cache_write"] or 0) * a * 1.25 + (t["cache_read"] or 0) * a * c
               + (t["output"] or 0) * b) / 1e6
        total += usd * (0.5 if mode == "batch" and not list_price else 1.0)
    return total


def record_usage(work: Path, model: str, effort: str, units: int, chars: int, usage: dict) -> None:
    if not usage:
        return
    with open(work / "llm_usage.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"model": model, "effort": effort, "units": units, "chars": chars, "usage": usage},
                           ensure_ascii=False) + "\n")


def observed_rate(work: Path | None, model: str, effort: str) -> tuple[float, int] | None:
    """(list-price US$ per source character, characters measured) from earlier runs with this model/effort."""
    if work is None:
        return None
    rows = [r for r in read_jsonl(work / "llm_usage.jsonl") if r.get("model") == model and r.get("effort") == effort]
    chars = sum(r.get("chars", 0) for r in rows)
    if not chars:
        return None
    return sum(cost(r["usage"], list_price=True) for r in rows) / chars, chars


def estimate(units: list[dict], model: str, batch: bool, work: Path | None = None,
             effort: str = "medium") -> tuple[float, str]:
    """(US$, basis). Uses the measured cost per character of earlier runs when there is one."""
    chars = sum(len(u["en"]) for u in units)
    factor = 0.5 if batch else 1.0
    seen = observed_rate(work, model, effort)
    if seen:
        rate, measured = seen
        return chars * rate * factor, f"依實測（已翻 {measured:,} 字元的實際用量）"
    groups = max(1, len(make_groups(units)))
    in_tok = chars / 4 * 1.3 + len(units) * 12 + groups * (300 + 500)   # items, glossary, system prompt (no cache)
    out_tok = (chars / 4 * 1.6 + len(units) * 10) * (1 + THINKING_ALLOWANCE)
    a, b, _c = price(model)
    return (in_tok * a + out_tok * b) / 1e6 * factor, "粗估（還沒有試翻的實測，含思考的預留）"


# ------------------------------------------------------------------ apply
def apply_results(items: list[dict], cache: dict, pm: Path, profile: str, out_mod: Path) -> dict:
    dsd: dict[str, list[dict]] = defaultdict(list)
    mcm: dict[str, dict[str, str]] = defaultdict(dict)
    tables: dict[tuple[str, str], dict[int, str]] = defaultdict(dict)
    missing = 0
    for it in items:
        hit = cache.get(cache_key(context_of(it), it["source"]))
        if not hit:
            missing += 1
            continue
        zh = hit["zh"]
        if it["kind"] == "dsd":
            dsd[it["plugin"]].append({"form_id": it["form_id"], "type": it["type"], "index": it.get("index"),
                                      "editor_id": it.get("editor_id"), "string": zh})
        elif it["kind"] == "mcm":
            mcm[it["file"]][it["key"]] = zh
        elif it["kind"] == "strings":
            tables[(it["plugin"], it["file"])][int(it["key"])] = zh
    for plugin, entries in dsd.items():
        write_dsd_file(out_mod / "SKSE" / "Plugins" / "DynamicStringDistributor" / plugin / "zz_pages_ai_zh.json",
                       entries)
    if mcm:
        from zh import mcm_txt
        found = mcm_txt.collect(pm, profile)
        for base, new in mcm.items():
            en = found.get((base, "ENGLISH"))
            zh = found.get((base, "CHINESE"))
            merged = dict(en.table) if en else {}
            if zh:
                merged.update({k: v for k, v in zh.table.items() if has_cjk(v)})
            merged.update(new)
            write_translation_txt(out_mod / "interface" / "translations" / f"{base}_CHINESE.txt", merged)
    skipped_official = 0
    if tables:
        prof = vfs.open_profile(pm, profile)
        providers = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, prof.game_dir / "Data")
        loose = loose_strings_index(prof)
        for (plugin, stem), new in tables.items():
            path = providers.get(plugin.lower())
            if not path:
                continue
            if is_official_plugin(plugin):
                skipped_official += 1             # the official Chinese tables must never be replaced
                continue
            for ext in (".strings", ".dlstrings", ".ilstrings"):
                en = localized_table(path, plugin, "english", ext, loose)
                if not en:
                    continue
                current = localized_table(path, plugin, "chinese", ext, loose)   # what the game loads now
                merged = {**en, **current, **{k: v for k, v in new.items() if k in en}}
                dest = out_mod / "strings" / f"{stem}_chinese{ext}"
                dest.parent.mkdir(parents=True, exist_ok=True)
                st.write(dest, merged, "utf-8")
    return {"dsd_plugins": len(dsd), "dsd_entries": sum(len(v) for v in dsd.values()), "mcm_files": len(mcm),
            "string_tables": len(tables) - skipped_official, "official_skipped": skipped_official,
            "not_translated_yet": missing}


# ------------------------------------------------------------------ CLI
def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="以 Claude API 翻譯剩餘英文字串")
    ap.add_argument("command", choices=["estimate", "run", "apply"])
    ap.add_argument("--work", type=Path, default=Path("D:/PM/zh-work"))
    ap.add_argument("--worklist", type=Path, default=None, help="預設 <work>/zh_worklist.jsonl")
    ap.add_argument("--glossary", type=Path, default=None)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--mode", default="batch", choices=["batch", "sync"])
    ap.add_argument("--limit", type=int, default=0, help="只處理前 N 組（試翻用）")
    ap.add_argument("--poll", type=int, default=60)
    ap.add_argument("--yes", action="store_true", help="確認願意支付估計的 API 費用")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--out-mod", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    args.work.mkdir(parents=True, exist_ok=True)
    items = read_jsonl(args.worklist or args.work / "zh_worklist.jsonl")
    cache = load_cache(args.work)
    units = pending_units(items, cache)
    groups = make_groups(units)
    if args.limit:
        groups = groups[: args.limit]
        units = [u for g in groups for u in g]
    rep = Report(f"zh_llm-{args.command}")
    exact = exact_glossary(args.glossary)
    free = sum(1 for u in units if u["en"].strip() in exact)
    paid = [u for u in units if u["en"].strip() not in exact]
    est, basis = estimate(paid, args.model, args.mode == "batch", args.work, args.effort)
    rep.add("todo", "INFO", "待翻譯", f"{len(items)} 條，去重後 {len(units)} 條，{len(groups)} 組；已快取 {len(cache)} 條"
            + (f"；其中 {free} 條和官方名詞完全相同，直接用官方譯法（不花錢）" if free else ""))
    rep.add("estimate", "INFO", f"費用估計（{args.model}，effort {args.effort}，{args.mode}）",
            f"約 US${est:,.2f}（{basis}）")

    if args.command == "run":
        if not args.yes:
            rep.add("confirm", "WARN", "尚未執行", "確認費用後加上 --yes 再執行（可先用 --limit 5 試翻）")
        else:
            client = client_factory()
            usage: dict = {}
            gloss = GlossaryIndex(load_glossary(args.glossary))
            known = {}
            for it in items:
                ctx = context_of(it)
                h = cache_key(ctx, it["source"])
                known.setdefault(h, {"h": h, "ctx": ctx, "en": it["source"]})
            resumed, resumed_chars = resume_batches(client, args.work, known, usage, args.poll)
            if resumed:
                rep.add("resumed", "INFO", "回收上次的批次", f"{resumed} 批（已付費，不重送）")
            prefilled = prefill(pending_units(items, load_cache(args.work)), exact, args.work)
            if prefilled:
                rep.add("prefill", "INFO", "直接用官方譯法", f"{prefilled} 條")
            cache = load_cache(args.work)
            units = pending_units(items, cache)
            groups = make_groups(units)
            if args.limit:
                groups = groups[: args.limit]
                units = [u for g in groups for u in g]
            failed = []
            if not groups:
                pass
            elif args.mode == "batch":
                failed = run_batch(client, groups, gloss, args.model, args.effort, args.work, usage, args.poll)
                retry = [[u] for u in failed]
                if retry:
                    print(f"  逐條重試 {len(retry)} 條（同步模式，含 fallbacks）…", flush=True)
                    failed = run_sync(client, retry, gloss, args.model, args.effort, args.work, usage)
            else:
                failed = run_sync(client, groups, gloss, args.model, args.effort, args.work, usage)
                retry = [[u] for u in failed if u.get("problem") != "refusal"]
                if retry:
                    failed = [u for u in failed if u.get("problem") == "refusal"] + \
                        run_sync(client, retry, gloss, args.model, args.effort, args.work, usage)
            (args.work / "llm_failed.jsonl").write_text(
                "".join(json.dumps(u, ensure_ascii=False) + "\n" for u in failed), encoding="utf-8")
            record_usage(args.work, args.model, args.effort, len(units),
                         sum(len(u["en"]) for u in units) + resumed_chars, usage)
            rep.add("done", "PASS" if not failed else "WARN", "翻譯結果",
                    f"送出 {len(units)} 條，失敗 {len(failed)} 條（保留英文；見 llm_failed.jsonl）")
            rep.add("spent", "INFO", "實際用量換算費用", f"約 US${cost(usage):,.2f}（含思考的輸出 token）")
            left = [u for u in pending_units(items, load_cache(args.work)) if u["en"].strip() not in exact]
            if left:
                rest, basis = estimate(left, args.model, True, args.work, args.effort)
                rep.add("rest", "INFO", "剩下的估計（Batch）", f"{len(left)} 條，約 US${rest:,.2f}（{basis}）")
            rep.data = {"usage": usage}
    elif args.command == "apply":
        if not args.out_mod:
            rep.add("out", "FAIL", "需要 --out-mod", "")
        else:
            stats = apply_results(items, load_cache(args.work), args.pm, args.profile, args.out_mod)
            rep.add("apply", "PASS", "已輸出到 " + str(args.out_mod),
                    f"DSD {stats['dsd_entries']} 條／{stats['dsd_plugins']} 個插件；介面檔 {stats['mcm_files']} 個；"
                    f"字串表 {stats['string_tables']} 組；尚未翻譯 {stats['not_translated_yet']} 條")
            if stats["official_skipped"]:
                rep.add("official", "WARN", "略過官方插件的字串表",
                        f"{stats['official_skipped']} 組（官方中文不覆蓋；請重跑新版 coverage.py）")
    path = rep.save(args.out, stem=f"zh_llm-{args.command}")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
