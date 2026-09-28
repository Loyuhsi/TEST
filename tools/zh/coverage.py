"""Translation coverage of the whole profile + the list of strings still in English.

計算整個設定檔的中文化涵蓋率，並輸出仍是英文的字串清單（給 llm_translate.py 翻譯）。

What counts as translated:
  plugins (not localized) : a DSD entry with Chinese text for the same record/field/index,
                            or the plugin text itself is already Chinese
  plugins (localized)     : a <plugin>_chinese.* string table exists with Chinese text
  interface translation   : the winning *_CHINESE.txt has a Chinese value for the key

    python -m pip install sse-plugin-interface
    python tools\\zh\\coverage.py --pm D:\\PM --work D:\\PM\\zh-work
Outputs reports\\zh_coverage.csv, reports\\zh_coverage.txt/.json and <work>\\zh_worklist.jsonl.
Plugin parsing is cached in <work>\\plugin_cache so re-runs are fast.
Official masters (base game, DLC, Creation Club) are counted but never put on the worklist: their
Chinese comes from the official localization. reports\\zh_dsd_unmatched.csv counts, per mod, DSD
entries that point at no string of the winning plugins (a pack made for another mod version).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pm import bsa, fsutil, strings as st, tes4, vfs  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, write_csv  # noqa: E402
from zh import mcm_txt  # noqa: E402
from zh.common import (PRICES, WorkItem, has_cjk, is_official_plugin, items_to_rows, iter_dsd,  # noqa: E402
                       needs_translation, read_dsd_file, string_key, write_jsonl)

UNMATCHED_FIELDS = ["mod", "entries", "matched", "unmatched", "inactive_plugin", "localized_unchecked", "examples"]


def extract_plugin_strings(path: Path, cache_dir: Path, localized: bool) -> list[dict]:
    """[{form_id, type, index, editor_id, string}] via sse-plugin-interface, cached on disk."""
    stt = path.stat()
    key = hashlib.sha1(f"{path.name}|{stt.st_size}|{int(stt.st_mtime)}|{localized}".encode()).hexdigest()[:20]
    cache = cache_dir / f"{path.name}.{key}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    try:
        from sse_plugin_interface.plugin import SSEPlugin  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise SystemExit("需要 sse-plugin-interface：python -m pip install sse-plugin-interface") from e
    plugin = SSEPlugin.from_file(path)
    rows = [{"form_id": s.form_id, "type": s.type, "index": s.index, "editor_id": str(s.editor_id) if s.editor_id else None,
             "string": s.string} for s in plugin.extract_strings(extract_localized=localized)]
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return rows


def winning_dsd_files(prof: vfs.Profile) -> dict[str, tuple[str, Path]]:
    """'plugin/file.json' (lower case) -> (mod folder, path) of the copy MO2 serves."""
    files: dict[str, tuple[str, Path]] = {}
    for folder in reversed(prof.enabled_folders):          # low -> high priority, later overrides
        for plugin_dir, js in iter_dsd(prof.mods_dir / folder):
            files[f"{plugin_dir.lower()}/{js.name.lower()}"] = (folder, js)
    return files


def dsd_map(prof: vfs.Profile, active: list[str], light: set[str]) -> dict[tuple, str]:
    """Effective DSD strings: later plugin folders / later file names / higher mods win."""
    files = {rel: path for rel, (_folder, path) in winning_dsd_files(prof).items()}
    order = {p.lower(): i for i, p in enumerate(active)}
    order["overwrite"] = 10 ** 9
    result: dict[tuple, str] = {}
    for rel in sorted(files, key=lambda r: (order.get(r.split("/")[0], -1), r)):
        if rel.split("/")[0] not in order:
            continue                          # DSD only loads folders of active plugins
        for e in read_dsd_file(files[rel]):
            try:
                k = string_key(e["form_id"], e["type"], e.get("index"), e.get("editor_id"), light)
            except (KeyError, ValueError):
                continue
            result[k] = e["string"]
    return result


def loose_strings_index(prof: vfs.Profile) -> dict[str, Path]:
    """lower-case string-table file name -> winning loose file among enabled mods."""
    idx: dict[str, Path] = {}
    for folder in prof.enabled_folders:
        for sub in ("strings", "Strings"):
            d = prof.mods_dir / folder / sub
            if d.is_dir():
                for p in d.iterdir():
                    idx.setdefault(p.name.lower(), p)
                break
    return idx


def localized_table(provider: Path, plugin: str, language: str, ext: str,
                    loose: dict[str, Path] | None = None) -> dict[int, str]:
    """The string table the game would load: winning loose file among enabled mods, then the
    plugin's own folder, then BSAs named after the plugin in that folder. {} when there is none."""
    stem = Path(plugin).stem.lower()
    mod = provider.parent
    name = f"{stem}_{language}{ext}"
    hit = (loose or {}).get(name)
    for cand in ([hit] if hit else []) + [mod / "strings" / name, mod / "Strings" / name]:
        if cand.exists():
            return st.read(cand)
    try:
        bsas = [e.path for e in os.scandir(mod) if e.name.lower().endswith(".bsa")
                and e.name.lower().startswith(stem)]
    except OSError:
        bsas = []
    for b in bsas:
        try:
            with bsa.BSA(Path(b)) as arc:
                found = arc.find(f"strings\\{name}")
                if found:
                    return st.parse(arc.read(found[0]), st.kind_of(name))
        except (bsa.BSAError, OSError):
            continue
    return {}


def localized_tables(provider: Path, plugin: str, language: str,
                     loose: dict[str, Path] | None = None) -> dict[int, str]:
    out: dict[int, str] = {}
    for ext in (".strings", ".dlstrings", ".ilstrings"):
        out.update(localized_table(provider, plugin, language, ext, loose))
    return out


def dsd_unmatched(prof: vfs.Profile, active: list[str], light: set[str], localized: set[str],
                  effective: dict[tuple, tuple]) -> list[dict]:
    """Per mod: DSD entries of the winning files that match no string of the winning plugins."""
    active_low = {p.lower() for p in active}
    stats: dict[str, dict] = {}
    for rel, (folder, path) in winning_dsd_files(prof).items():
        s = stats.setdefault(folder, {"mod": folder, "entries": 0, "matched": 0, "unmatched": 0,
                                      "inactive_plugin": 0, "localized_unchecked": 0, "examples": []})
        plugin = rel.split("/")[0]
        entries = read_dsd_file(path)
        if plugin not in active_low:
            s["inactive_plugin"] += len(entries)
            continue
        if plugin in localized:
            s["localized_unchecked"] += len(entries)
            continue
        for e in entries:
            try:
                k = string_key(e["form_id"], e["type"], e.get("index"), e.get("editor_id"), light)
            except (KeyError, ValueError):
                k = None
            s["entries"] += 1
            if k is not None and k in effective:
                s["matched"] += 1
            else:
                s["unmatched"] += 1
                if len(s["examples"]) < 3:
                    s["examples"].append(f"{e.get('form_id', '?')} {e.get('type', '?')}")
    rows = sorted(stats.values(), key=lambda r: r["mod"].lower())
    for r in rows:
        r["examples"] = "; ".join(r["examples"])
    return rows


def lost_zh_plugins(prof: vfs.Profile, providers: dict[str, Path]) -> list[str]:
    """Plugins inside enabled ZH folders that some higher-priority mod overrides (the translation is not used)."""
    out = []
    for folder in prof.enabled_folders:
        if not folder.upper().startswith("ZH"):
            continue
        for name in vfs.root_plugins(prof.mods_dir / folder):
            win = providers.get(name.lower())
            if win is not None and win.parent.name != folder:
                out.append(f"{name}（{folder} 被 {win.parent.name} 蓋掉）")
    return out


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="中文化涵蓋率與待翻譯清單（唯讀，只寫報告與 work 資料夾）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--profile", default="Pages-ZH")
    ap.add_argument("--work", type=Path, default=Path("D:/PM/zh-work"))
    ap.add_argument("--skip-plugins", action="store_true", help="只檢查介面翻譯檔")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    prof = vfs.open_profile(args.pm, args.profile)
    data_dir = prof.game_dir / "Data"
    providers = vfs.plugin_providers(prof.mods_dir, prof.enabled_folders, data_dir)
    primaries = vfs.primary_plugins(prof.game_dir)
    active = primaries + [p.name for p in prof.plugins if p.enabled and p.name not in primaries]
    headers = {}
    for name in active:
        path = providers.get(name.lower())
        if path:
            try:
                headers[name.lower()] = tes4.read_header(path)
            except (tes4.PluginError, OSError):
                pass
    light = {n for n, h in headers.items() if h.is_light}
    dsd = dsd_map(prof, active, light)
    rows: list[dict] = []
    work: list[WorkItem] = []
    official_todo = 0
    effective: dict[tuple, tuple[str, dict]] = {}     # key -> (plugin, entry): last override wins
    if not args.skip_plugins:
        cache_dir = args.work / "plugin_cache"
        loose = loose_strings_index(prof)
        for i, name in enumerate(active, start=1):
            path = providers.get(name.lower())
            h = headers.get(name.lower())
            if not path or not h or name in vfs.GENERATED_PLUGINS:
                continue
            if i % 200 == 0:
                print(f"  已分析 {i}/{len(active)} 個插件 …", flush=True)
            if h.is_localized:
                zh = localized_tables(path, name, "chinese", loose)
                en = localized_tables(path, name, "english", loose)
                done = sum(1 for v in zh.values() if has_cjk(v))
                todo = {sid: v for sid, v in en.items() if needs_translation(v) and not has_cjk(zh.get(sid, ""))}
                official = is_official_plugin(name)
                if official:
                    official_todo += len(todo)
                else:
                    for sid, text in todo.items():
                        work.append(WorkItem(WorkItem.make_id("strings", name, sid), "strings", text, "localized",
                                             plugin=name, file=Path(name).stem.lower(), key=str(sid)))
                note = "" if zh else "沒有 _chinese 字串表：畫面可能出現空白名稱"
                if official and todo:
                    note = (note + "；" if note else "") + "官方插件：不送 AI"
                rows.append({"kind": "localized_plugin", "name": name, "total": len(en), "translated": done,
                             "untranslated": len(todo), "chars": sum(len(t) for t in todo.values()),
                             "note": note})
                continue
            try:
                entries = extract_plugin_strings(path, cache_dir, localized=False)
            except Exception as e:  # noqa: BLE001 - one bad plugin must not stop the scan
                rows.append({"kind": "plugin", "name": name, "total": 0, "translated": 0, "untranslated": 0,
                             "chars": 0, "note": f"無法解析：{e}"})
                continue
            for e in entries:
                k = string_key(e["form_id"], e["type"], e["index"], e.get("editor_id"), light)
                effective[k] = (name, e)
        per_plugin: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
        for k, (plugin, e) in effective.items():
            c = per_plugin[plugin]
            c[0] += 1
            text = e["string"]
            if has_cjk(dsd.get(k, "")) or has_cjk(text) or not needs_translation(text):
                c[1] += 1
                continue
            c[2] += 1
            c[3] += len(text)
            work.append(WorkItem(WorkItem.make_id(*k), "dsd", text, e["type"], plugin=plugin, form_id=e["form_id"],
                                 type=e["type"], index=e["index"], editor_id=e.get("editor_id")))
        for plugin, (total, done, todo, chars) in sorted(per_plugin.items()):
            rows.append({"kind": "plugin", "name": plugin, "total": total, "translated": done,
                         "untranslated": todo, "chars": chars, "note": ""})
    found = mcm_txt.collect(args.pm, args.profile)
    for r in mcm_txt.analyse(found):
        en = found[(r["base"], "ENGLISH")]
        zh = found.get((r["base"], "CHINESE"))
        todo = {k: v for k, v in en.table.items() if needs_translation(v) and not has_cjk((zh.table if zh else {}).get(k, ""))}
        for k, v in todo.items():
            work.append(WorkItem(WorkItem.make_id("mcm", r["base"], k), "mcm", v, k, file=r["base"], key=k))
        rows.append({"kind": "interface", "name": r["base"], "total": len(en.table),
                     "translated": len(en.table) - len(todo), "untranslated": len(todo),
                     "chars": sum(len(v) for v in todo.values()), "note": r["status"]})

    args.work.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.work / "zh_worklist.jsonl", items_to_rows(work))
    write_csv(args.out / "zh_coverage.csv", rows, ["kind", "name", "total", "translated", "untranslated", "chars", "note"])
    total = sum(r["total"] for r in rows)
    done = sum(r["translated"] for r in rows)
    unique_chars = sum(len(t) for t in {w.source for w in work})
    rep = Report("zh_coverage")
    rep.add("coverage", "INFO", "整體涵蓋率", f"{done}/{total}（{(done / total * 100 if total else 100):.1f}%）")
    rep.add("todo", "INFO", "待翻譯", f"{len(work)} 條；去除重複後約 {unique_chars:,} 個英文字元")
    blanks = [r["name"] for r in rows if r["kind"] == "localized_plugin" and r["note"].startswith("沒有")]
    rep.add("blank", "WARN" if blanks else "PASS", "缺中文字串表的本地化插件",
            f"{len(blanks)} 個" + (f"：{', '.join(blanks[:8])}" if blanks else ""))
    rep.add("official", "INFO", "官方插件（本體、DLC、CC）仍是英文的字串",
            f"{official_todo} 條（不送 AI；官方繁中本來就有的名詞保持官方譯法）")
    if not args.skip_plugins:
        localized = {n for n, h in headers.items() if h.is_localized}
        unmatched = dsd_unmatched(prof, active, light, localized, effective)
        write_csv(args.out / "zh_dsd_unmatched.csv", unmatched, UNMATCHED_FIELDS)
        worst = [r for r in unmatched if r["entries"] and r["unmatched"] / r["entries"] > 0.2]
        rep.add("dsd_unmatched", "WARN" if worst else "INFO", "DSD 對不上的條目（依 mod）",
                ("；".join(f"{r['mod']} {r['unmatched']}/{r['entries']}"
                          + (f"（插件未啟用 {r['inactive_plugin']}）" if r["inactive_plugin"] else "")
                          for r in unmatched if r["entries"] or r["inactive_plugin"]) or "沒有 DSD 檔")
                + "（見 reports\\zh_dsd_unmatched.csv）")
    lost = lost_zh_plugins(prof, providers)
    rep.add("lost", "WARN" if lost else "PASS", "ZH 資料夾裡沒有生效的插件",
            f"{len(lost)} 個" + (f"：{'；'.join(lost[:8])}" if lost else ""))
    in_tok = unique_chars / 4 * 1.3 + len(work) * 12        # text + JSON/id overhead
    out_tok = (unique_chars / 4 * 1.6 + len(work) * 10) * 2  # x2: room for thinking tokens
    est = [f"{m}：約 ${(in_tok * a + out_tok * b) / 1e6:,.0f}（Batch 約 ${(in_tok * a + out_tok * b) / 2e6:,.0f}）"
           for m, (a, b, _c) in PRICES.items()]
    rep.add("cost", "INFO", "機器翻譯費用粗估（含思考的預留；準確數字看 llm_translate 試翻後的 estimate）",
            "；".join(est))
    rep.data = {"worklist": str(args.work / "zh_worklist.jsonl"), "items": len(work), "unique_chars": unique_chars}
    path = rep.save(args.out, stem="zh_coverage")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
