"""Classify every folder of the target modlist by where it can be obtained.

依來源分類目標清單的每個 mod 資料夾（Nolvus／M&V／Nexus／需重建／捨棄）。

This is the cloud-side, *preliminary* classification built from public
snapshots. On the laptop, tools/manifest.py redoes it with exact folder names
from the real installs (inventory CSVs) and takes precedence.

Inputs (all in the repo):
  data/target/modlist.txt, data/target/plugins.txt
  data/snapshots/nolvus-official-awakening.csv     (nolvus.net full list, 6.0.21-beta page)
  data/snapshots/lol-*/modlist.txt                  (Load Order Library snapshots)
  data/analysis/mv_folder_map.csv                   (optional: MV .wabbajack folder map)
  data/analysis/nexus_candidates.csv                (optional: Nexus identification)
Outputs:
  data/analysis/provenance.csv, data/analysis/drop_list.csv, data/analysis/provenance_summary.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from pm import mo2  # noqa: E402

# Folders produced by tools on the author's machine: regenerate locally, never download.
GENERATED = {
    "Pandora Output": "Pandora Behaviour Engine output (run Pandora with -o)",
    "BodySlide (Dressed)": "BodySlide batch build output",
    "SYNTHESSIS": "Synthesis patcher output (Synthesis.esp)",
    "pgpatcher_output": "PGPatcher output (PGPatcher.esp, PG_1.esp, PG_2.esp)",
    "grass CS": "NGIO grass cache",
    "lodgen2": "xLODGen terrain LOD",
    "texgenCS": "DynDOLOD TexGen output",
    "dyndolodCS2": "DynDOLOD output (DynDOLOD.esm/.esp, Occlusion.esp)",
    "overwrite2": "author's MO2 overwrite folder (tool leftovers); contents unknown",
}
GENERATED_PLUGINS = {
    "Synthesis.esp": "SYNTHESSIS", "PGPatcher.esp": "pgpatcher_output", "PG_1.esp": "pgpatcher_output",
    "PG_2.esp": "pgpatcher_output", "DynDOLOD.esm": "dyndolodCS2", "DynDOLOD.esp": "dyndolodCS2",
    "Occlusion.esp": "dyndolodCS2", "FNIS.esp": "Pandora Output",
}
# Author-made local folders that cannot be downloaded.
CUSTOM = {
    "CustomFixes1": "author's private fixes (likely holds the [FIX]*.esp plugins)",
    "CS shaders": "probably a Community Shaders shader cache or local tweak",
    "Vanilla CS rain TEXTURES": "probably a local texture tweak for CS rain",
}
CUSTOM_PLUGIN_PREFIXES = ("[FIX]",)
# Not on Nexus (Patreon / Discord / blogs). User decision: drop + remove dependent patches.
NON_NEXUS = {
    "CommunityShaders_AIO-2026-05-28T17-09Z": "Jiaye CS fork build (Wabbajack authored file); replaced by official Community Shaders",
    "[full_inu] Armor Pack 01 SSE": "blog/Patreon",
    "[Kirax] BDOR 2024 Female Collection": "ModBooru/LoversLab",
    "[Dint999] BDOR Hairs SSE 0.23": "Patreon/Discord",
    "[SSE] H2135 Fantasy Series8": "Patreon/Discord",
    "Curious Adventurer": "Aokili Patreon (free tier)",
    "SC_HorseReplacer_SSE": "ShinglesCat Patreon",
    "SC_HorseReplacer": "ShinglesCat Patreon",
    "[TalesOfStar] Air Balloons": "Patreon/site",
    "anchor animation v2 Part": "Anchor Patreon",
    "Grapple a1.7": "Smooth Patreon (paid tier)",
    "For Honor in Skyrim Black Prior": "Smooth Patreon/Discord",
    "Lamas Tiny Hud - Edge version (SUKI)": "SUKI Patreon",
}
# Mods removed by MV 2.6 that the target still uses (MV 2.5.x era content).
MV26_REMOVED_HINTS = [
    "Parrying RPG", "One Click Power Attack NG", "True Flasks NG", "Simple Hunting Overhaul",
    "Madmen", "STB Widgets", "STB Active Effects", "Relationship Dialogue Overhaul",
    "New Creature Animation - Werewolf",
]

LOL_NOLVUS = ["lol-nolvus-awekening-redux", "lol-nolvus-awakening-v6", "lol-nolvus-v6-ultimate-open-beta-start"]
LOL_MV = "lol-mages-vikings"


def load_names(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {mo2.fold(e.name) for e in mo2.read_modlist(path) if not e.is_separator}


def section_map(entries: list[mo2.ModEntry]) -> dict[int, str]:
    """Map line_no -> separator name. In modlist.txt a separator line comes
    *after* (below) the mods it groups, because the file is in descending priority."""
    out: dict[int, str] = {}
    pending: list[int] = []
    for e in entries:
        if e.is_separator:
            sep = e.name[: -len(mo2.SEPARATOR_SUFFIX)]
            for ln in pending:
                out[ln] = sep
            pending = []
        else:
            pending.append(e.line_no)
    for ln in pending:
        out[ln] = ""
    return out


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def classify(root: Path) -> tuple[list[dict], dict]:
    data = root / "data"
    target = mo2.read_modlist(data / "target" / "modlist.txt")
    sections = section_map(target)

    official: dict[str, dict] = {}
    for r in read_csv(data / "snapshots" / "nolvus-official-awakening.csv"):
        official.setdefault(mo2.fold(r["mod"]), r)
    lol_n = {slug: load_names(data / "snapshots" / slug / "modlist.txt") for slug in LOL_NOLVUS}
    lol_mv = load_names(data / "snapshots" / LOL_MV / "modlist.txt")
    mvmap = {mo2.fold(r["folder"]): r for r in read_csv(data / "analysis" / "mv_folder_map.csv")}
    mv_names = lol_mv | set(mvmap)
    nexus = {mo2.fold(r["folder"]): r for r in read_csv(data / "analysis" / "nexus_candidates.csv")}

    rows = []
    for e in target:
        if e.is_separator or not e.enabled:
            continue
        key = mo2.fold(e.name)
        base = mo2.strip_dup_suffix(e.name)
        base_key = mo2.fold(base) if base else None

        def lookup(k):
            in_off = k in official
            in_old = [s for s in LOL_NOLVUS if k in lol_n[s]]
            in_mv = k in mv_names
            return in_off, in_old, in_mv

        in_off, in_old, in_mv = lookup(key)
        matched_via = "exact"
        if not (in_off or in_old or in_mv) and base_key:
            b_off, b_old, b_mv = lookup(base_key)
            if b_off or b_old or b_mv:
                in_off, in_old, in_mv, matched_via = b_off, b_old, b_mv, "dup_suffix"
        in_nolvus = in_off or bool(in_old)
        section = sections.get(e.line_no, "")
        mv_section = section.upper().startswith("MV")
        off = official.get(key) or (official.get(base_key) if matched_via == "dup_suffix" else None) or {}
        mvr = mvmap.get(key) or (mvmap.get(base_key) if base_key else None) or {}
        nx = nexus.get(key) or {}

        if e.name in GENERATED:
            category, action, note = "generated", "regenerate", GENERATED[e.name]
        elif e.name in CUSTOM:
            category, action, note = "custom", "drop", CUSTOM[e.name]
        elif e.name in NON_NEXUS:
            category, action, note = "non_nexus", "drop", NON_NEXUS[e.name]
        elif in_nolvus and in_mv:
            category = "both"
            action = "harvest_mv" if mv_section else "harvest_nolvus"
            note = "section suggests MV copy" if mv_section else "section suggests Nolvus copy"
        elif in_nolvus:
            category = "nolvus" if in_off else "nolvus_old"
            action = "harvest_nolvus"
            note = "" if in_off else "not on the current nolvus.net page (6.0.21 beta); present in 6.0.20 snapshots"
        elif in_mv:
            category, action, note = "mv", "harvest_mv", ""
            if any(mo2.fold(h) in key for h in map(str, MV26_REMOVED_HINTS)):
                note = "removed in MV 2.6 - may be absent from an MV 2.6.2 install; download from Nexus"
        else:
            nx_cat = nx.get("category", "")
            if nx_cat in ("nexus_found", "nexus_ambiguous", "adult_gated"):
                sure = nx_cat == "nexus_found" and nx.get("confidence") in ("high", "medium")
                category, action = "nexus_other", ("download_nexus" if sure else "review")
                note = f"{nx_cat}, confidence {nx.get('confidence','')}" + ("" if sure else " - confirm the Nexus page by hand")
            elif nx_cat in ("generated", "custom", "non_nexus"):
                category, action, note = nx_cat, ("regenerate" if nx_cat == "generated" else "drop"), nx.get("notes", "")
            else:
                category, action, note = "unknown", "review", "not in any snapshot; identify on Nexus"
        if mvr.get("skse_dlls") and action == "harvest_mv":
            note = (note + "; " if note else "") + "has SKSE DLL from MV (1.6.1170 build) - replace with 1.5.97/NG build"

        rows.append({
            "line": e.line_no,
            "folder": e.name,
            "section": section,
            "category": category,
            "action": action,
            "matched_via": matched_via,
            "nolvus_official_option": off.get("option", ""),
            "nolvus_official_version": off.get("version", ""),
            "nolvus_snapshots": ";".join(s.replace("lol-", "") for s in in_old),
            "in_mv": "yes" if in_mv else "",
            "mv_skse_dlls": mvr.get("skse_dlls", ""),
            "nexus_mod_id": mvr.get("nexus_mod_id") or nx.get("nexus_mod_id", ""),
            "nexus_file_id": mvr.get("nexus_file_id") or nx.get("suggested_file_id", ""),
            "nexus_version": mvr.get("nexus_version") or nx.get("suggested_file_version", ""),
            "plugins": mvr.get("plugins") or nx.get("related_plugins", ""),
            "note": note,
        })

    plugins = mo2.read_plugins(data / "target" / "plugins.txt")
    counts = Counter(r["category"] for r in rows)
    actions = Counter(r["action"] for r in rows)
    summary = {
        "enabled_mods": len(rows),
        "separators": sum(1 for e in target if e.is_separator),
        "plugins": len(plugins),
        "plugins_by_ext": dict(Counter(Path(p.name).suffix.lower() for p in plugins)),
        "by_category": dict(sorted(counts.items())),
        "by_action": dict(sorted(actions.items())),
        "generated_plugins": [p.name for p in plugins if p.name in GENERATED_PLUGINS],
        "custom_plugins": [p.name for p in plugins if p.name.startswith(CUSTOM_PLUGIN_PREFIXES)],
        "inputs": {
            "mv_folder_map": bool(mvmap),
            "nexus_candidates": bool(nexus),
        },
    }
    return rows, summary


def write_outputs(root: Path, rows: list[dict], summary: dict) -> None:
    out = root / "data" / "analysis"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "provenance.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    drops = [r for r in rows if r["action"] == "drop"]
    with open(out / "drop_list.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["kind", "name", "line", "category", "reason"])
        for r in drops:
            w.writerow(["folder", r["folder"], r["line"], r["category"], r["note"]])
        for p in summary["custom_plugins"]:
            w.writerow(["plugin", p, "", "custom", "author-made [FIX] plugin (not downloadable)"])
        for r in drops:
            for p in filter(None, (r.get("plugins") or "").split(";")):
                w.writerow(["plugin", p, r["line"], r["category"], f"plugin of dropped folder {r['folder']}"])
    (out / "provenance_summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n",
                                                 encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    rows, summary = classify(args.root)
    write_outputs(args.root, rows, summary)
    print(json.dumps({k: summary[k] for k in ("enabled_mods", "by_category", "by_action")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
