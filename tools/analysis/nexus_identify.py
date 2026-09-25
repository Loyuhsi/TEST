#!/usr/bin/env python3
"""Identify Nexus Mods pages (and files) for target MO2 folders missing from every known source list.

The target list (data/target/modlist.txt, native MO2 order, first line = highest priority)
is compared case-insensitively against the official Nolvus CSV and the Load Order Library
snapshots under data/snapshots/.  Every enabled, non-separator folder that is not found
(also after stripping an MO2 duplicate digit suffix such as "Wyrmstooth2") is looked up on
Nexus Mods (Skyrim Special Edition, gameId 1704) through the public GraphQL v2 API, which
works without an API key for these read-only queries:

* ``mods(filter: {name: WILDCARD})``      case-insensitive exact mod-name lookup
* ``mods(filter: {nameStemmed: [...]})``  one value per word; values are AND-ed and stemmed
* ``modFiles(modId, gameId)``             every file of a mod, including OLD_VERSION/ARCHIVED
* ``legacyMods(ids: [...])``              mod metadata by id
* ``modFileContents(fileNameWildcard)``   which mod archives contain a given plugin file name

Target plugins that appear in none of the source plugin lists are used as extra evidence:
they are linked to folders by name similarity and searched in Nexus file contents.

Every GraphQL sub-query result is cached on disk (one JSON file per sub-query, keyed by its
SHA-256), so re-runs are cheap and deterministic.  Requests are throttled (``--sleep``),
batched with GraphQL aliases (``--batch-size``) and retried with back-off on 429/5xx.

繁體中文：為目標 MO2 清單中所有已知來源都找不到的資料夾，透過 Nexus Mods GraphQL 查出最可能的模組頁面與檔案。
"""

from __future__ import annotations

import argparse
import csv
import difflib
import hashlib
import http.client
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENDPOINT = "https://api.nexusmods.com/v2/graphql"
GAME_ID = 1704
APP_NAME = "pages-modlist-tools"
APP_VERSION = "0.1"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Application-Name": APP_NAME,
    "Application-Version": APP_VERSION,
    "User-Agent": f"{APP_NAME}/{APP_VERSION} (+stdlib urllib)",
}

CSV_COLUMNS = [
    "folder", "target_line", "category", "nexus_mod_id", "nexus_mod_name", "nexus_author",
    "match_method", "confidence", "suggested_file_id", "suggested_file_name",
    "suggested_file_version", "file_category", "related_plugins", "notes",
]

# Folders that are tool outputs (regenerated locally, never downloaded).
GENERATED_FOLDERS = {
    "pandora output": "Pandora Behaviour Engine output",
    "dyndolodcs2": "DynDOLOD output",
    "texgencs": "TexGen output",
    "grass cs": "grass cache / grass precache output",
    "lodgen2": "xLODGen / LODGen output",
    "pgpatcher_output": "ParallaxGen / PG Patcher output",
    "synthessis": "Synthesis patcher output",
    "bodyslide (dressed)": "BodySlide batch-build output",
}
# Folders that are local/custom content (hand-made fixes, renamed overwrite, local builds).
CUSTOM_FOLDERS = {
    "overwrite2": "renamed MO2 overwrite contents",
    "customfixes1": "user's custom fixes",
    "cs shaders": "locally assembled Community Shaders shader files",
    "vanilla cs rain textures": "user-made texture set for Community Shaders rain",
    "communityshaders_aio-2026-05-28t17-09z": "timestamped Community Shaders AIO build (CI/nightly artifact, not a Nexus release)",
}
# Folders known to come from Patreon / Discord / other non-Nexus sources.
NON_NEXUS_FOLDERS = {
    "[full_inu] armor pack 01 sse": "full_inu armor pack (Patreon/non-Nexus)",
    "[kirax] bdor 2024 female collection": "Kirax BDOR collection (Patreon/non-Nexus)",
    "[dint999] bdor hairs sse 0.23": "Dint999 BDOR hairs (Patreon/non-Nexus)",
    "[sse] h2135 fantasy series8": "H2135 Fantasy Series (non-Nexus)",
    "curious adventurer": "Curious Adventurer (non-Nexus)",
    "sc_horsereplacer_sse": "SC Horse Replacer (Patreon/non-Nexus)",
    "sc_horsereplacer": "SC Horse Replacer (Patreon/non-Nexus)",
    "[talesofstar] air balloons": "TalesOfStar Air Balloons (non-Nexus)",
    "anchor animation v2 part": "Anchor animations (Patreon/non-Nexus)",
    "grapple a1.7": "Grapple alpha build (Patreon/non-Nexus)",
    "for honor in skyrim black prior": "For Honor in Skyrim armor (non-Nexus)",
    "lamas tiny hud - edge version (suki)": "Lama's Tiny HUD Edge skin by SUKI (non-Nexus)",
}

# Manually verified hints: folder (lower-case) -> (mod id, note).  Kept intentionally small;
# every entry was checked by hand against the Nexus API.
MANUAL_HINTS: dict[str, tuple[int, str]] = {}

# Words that carry little identifying value (dropped for "core" comparisons/queries).
NOISE_TOKENS = {
    "se", "sse", "ae", "le", "1k", "2k", "4k", "8k", "esl", "esp", "esm", "zip", "7z", "rar",
    "version", "latest", "new", "ver",
}
# Generic words dropped for the "distinctive words" query variant.
GENERIC_TOKENS = NOISE_TOKENS | {
    "pbr", "patch", "patches", "addon", "add", "on", "fix", "fixes", "fixed", "and", "the",
    "of", "for", "a", "an", "to", "in", "with", "by", "x", "compatibility", "replacer",
    "texture", "textures", "retexture", "hd", "mod", "mods", "skyrim", "special", "edition",
    "optional", "standalone", "stand", "alone", "files", "file", "main", "plugin", "esp",
    "complex", "material", "cm", "parallax", "hub", "collection", "aio",
}
# Tokens that mark a translation / localisation upload.
LANG_TOKENS = {
    "translation", "translations", "translated", "traduction", "traduzione", "traducción",
    "traduccion", "übersetzung", "uebersetzung", "russian", "rus", "ru", "french", "fr",
    "vf", "francais", "français", "german", "deutsch", "ger", "spanish", "español",
    "espanol", "castellano", "italian", "italiano", "ita", "polish", "pl", "polski",
    "portuguese", "ptbr", "chinese", "chs", "cht", "cn", "zh", "japanese", "jp", "jpn",
    "korean", "kor", "kr", "turkish", "ukrainian", "belarusian", "czech", "cz", "hungarian",
    "swedish", "dutch", "thai", "vietnamese", "brazilian",
}
# Bracketed or trailing language codes: 'Unslaad SE (PT-BR)', 'Lux CS - PL', 'X [RU]'.
LANG_CODE_RE = re.compile(
    r"(?:[(\[]\s*|\s-\s*)(pt[-_ ]?br|ru|fr|de|es|it|pl|cz|jp|ja|kr|ko|cn|zh|tr|ua|hu|chs|cht)"
    r"\s*(?:[)\]]|$)", re.I)
CJK_RE = re.compile("[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]")
FILE_CAT_RANK = {"MAIN": 6, "UPDATE": 5, "OPTIONAL": 5, "MISCELLANEOUS": 4,
                 "OLD_VERSION": 2, "ARCHIVED": 1, "REMOVED": 0}
STALE_CATS = {"OLD_VERSION", "ARCHIVED", "REMOVED"}

VERSION_RE = re.compile(r"(?<![\w.])v?\d+(?:\.\d+)+[a-z]?(?![\w.])|(?<![\w.])v\d+(?![\w.])", re.I)
BRACKET_RE = re.compile(r"\([^)]*\)|\[[^\]]*\]|\{[^}]*\}")
ARCHIVE_EXT_RE = re.compile(r"\.(zip|7z|rar|esp|esm|esl)$", re.I)
DUP_SUFFIX_RE = re.compile(r"^(.*[^\W\d_]|.*[)\]])\d{1,2}$")
SEGMENT_SPLIT_RE = re.compile(r"\s+[-–—|:]\s+|\s*_-_\s*")


# --------------------------------------------------------------------------------------
# Text normalisation and similarity
# --------------------------------------------------------------------------------------

def strip_dup_suffix(name: str) -> str:
    """Strip an MO2 duplicate-install digit suffix ('Wyrmstooth2' -> 'Wyrmstooth').

    A trailing version word such as 'V3' ('Bow Rapid Combo V3') is kept.
    """
    if re.search(r"(?:^|[\s_-])[vV]\d{1,2}$", name):
        return name
    m = DUP_SUFFIX_RE.match(name)
    return m.group(1).rstrip() if m else name


def camel_split(s: str) -> str:
    """Insert spaces at lower->Upper boundaries ('TitanOfSkyrim' -> 'Titan Of Skyrim')."""
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)


def tokenize(s: str, camel: bool = False) -> list[str]:
    """Lower-case word tokens; apostrophes are removed so "Praedy's" -> 'praedys'."""
    s = ARCHIVE_EXT_RE.sub("", s.strip())
    if camel:
        s = camel_split(s)
    s = re.sub(r"['’´`]", "", s).lower()
    return re.findall(r"[^\W_]+", s)


def core_string(s: str) -> str:
    """Name without bracketed text and version numbers (falls back to the full name)."""
    base = ARCHIVE_EXT_RE.sub("", s.strip())
    t = BRACKET_RE.sub(" ", base)
    t = VERSION_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip(" -_")
    return t if tokenize(t) else base


def core_tokens(s: str, camel: bool = False) -> list[str]:
    toks = [t for t in tokenize(core_string(s), camel) if t not in NOISE_TOKENS]
    # Drop leading ordinal numbers such as '1-Elden Rim' / '01 Rim Parry'.
    while len(toks) > 1 and toks[0].isdigit():
        toks.pop(0)
    return toks or tokenize(s, camel)


def _dice(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return 2.0 * len(sa & sb) / (len(sa) + len(sb))


def _pair_sim(ta: list[str], tb: list[str]) -> float:
    if not ta or not tb:
        return 0.0
    if "".join(ta) == "".join(tb):
        return 1.0
    dice = _dice(ta, tb)
    seq = difflib.SequenceMatcher(None, " ".join(ta), " ".join(tb), autojunk=False).ratio()
    return 0.5 * dice + 0.5 * seq


def name_sim(a: str, b: str) -> float:
    """Similarity in [0, 1]; 1.0 = same words, 0.97 = same after dropping versions/noise."""
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0.0
    if "".join(ta) == "".join(tb):
        return 1.0
    tac, tbc = tokenize(a, camel=True), tokenize(b, camel=True)
    if "".join(tac) == "".join(tbc):
        return 1.0
    ca, cb = core_tokens(a), core_tokens(b)
    if ca and cb and "".join(ca) == "".join(cb):
        return 0.97
    score = max(_pair_sim(ta, tb), _pair_sim(tac, tbc), _pair_sim(ca, cb))
    return min(score, 0.96)


def lang_penalty(folder: str, cand: str) -> float:
    """Penalty for translation uploads (language markers the folder does not have)."""
    ft = set(tokenize(folder, camel=True))
    ct = set(tokenize(cand, camel=True))
    if (ct & LANG_TOKENS) - ft:
        return 0.15
    if CJK_RE.search(cand) and not CJK_RE.search(folder):
        return 0.15
    codes = {m.lower().replace("_", "-").replace(" ", "-") for m in LANG_CODE_RE.findall(cand)}
    if codes - {m.lower().replace("_", "-").replace(" ", "-") for m in LANG_CODE_RE.findall(folder)}:
        return 0.15
    return 0.0


def versions_in(s: str) -> set[str]:
    out = set()
    for m in VERSION_RE.finditer(s):
        out.add(norm_version(m.group(0)))
    return out


def norm_version(v: str) -> str:
    v = (v or "").strip().lower().lstrip("v")
    parts = v.split(".")
    while len(parts) > 1 and parts[-1] == "0":
        parts.pop()
    return ".".join(parts)


def uri_stem(uri: str, mod_id: int) -> str:
    """'Lux CS-153919-2-6-0-1734.7z' -> 'Lux CS'."""
    stem = ARCHIVE_EXT_RE.sub("", uri or "")
    m = re.match(rf"^(.*?)-{mod_id}-", stem)
    return m.group(1) if m else stem


def gql_str(s: str) -> str:
    """GraphQL string literal (JSON escaping is valid GraphQL escaping)."""
    return json.dumps(s)


def wildcard_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("*", "\\*").replace("?", "\\?")


# --------------------------------------------------------------------------------------
# Nexus GraphQL client with per-sub-query disk cache and alias batching
# --------------------------------------------------------------------------------------

class NexusClient:
    TRANSIENT_HINTS = ("rate", "too many", "timeout", "timed out", "internal", "unavailable",
                       "try again")

    def __init__(self, cache_dir: Path, sleep: float, batch_size: int, offline: bool,
                 verbose: bool = False):
        self.cache_dir = cache_dir
        self.sleep = max(0.0, sleep)
        self.batch_size = max(1, batch_size)
        self.offline = offline
        self.verbose = verbose
        self._last = 0.0
        self.stats = {"http_requests": 0, "cache_hits": 0, "cache_misses": 0, "retries": 0,
                      "errors": 0, "offline_misses": 0}
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # -- cache ------------------------------------------------------------------------
    def _key(self, subquery: str) -> str:
        return hashlib.sha256(subquery.encode("utf-8")).hexdigest()

    def _path(self, key: str) -> Path:
        return self.cache_dir / key[:2] / f"{key}.json"

    def _load(self, subquery: str):
        p = self._path(self._key(subquery))
        if p.is_file():
            try:
                obj = json.loads(p.read_text(encoding="utf-8"))
                if obj.get("q") == subquery:
                    return obj
            except (OSError, ValueError):
                return None
        return None

    def _store(self, subquery: str, data, errors) -> None:
        p = self._path(self._key(subquery))
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps({"q": subquery, "data": data, "errors": errors,
                                   "fetched_at": int(time.time())}, ensure_ascii=False),
                       encoding="utf-8")
        os.replace(tmp, p)

    # -- HTTP -------------------------------------------------------------------------
    def _throttle(self) -> None:
        wait = self._last + self.sleep - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

    def _post(self, query: str, max_retries: int = 6) -> dict:
        body = json.dumps({"query": query}).encode("utf-8")
        delay = 2.0
        last_err = None
        for attempt in range(max_retries + 1):
            self._throttle()
            self.stats["http_requests"] += 1
            req = urllib.request.Request(ENDPOINT, data=body, headers=HEADERS, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=90) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                text = e.read().decode("utf-8", "replace")
                if e.code == 429 or e.code >= 500:
                    retry_after = e.headers.get("Retry-After") if e.headers else None
                    wait = delay
                    if retry_after and retry_after.strip().isdigit():
                        wait = max(wait, float(retry_after))
                    last_err = f"HTTP {e.code}"
                    self.stats["retries"] += 1
                    print(f"  [nexus] HTTP {e.code}; retrying in {wait:.0f}s", file=sys.stderr)
                    time.sleep(wait)
                    delay = min(delay * 2, 120)
                    continue
                try:
                    return json.loads(text)
                except ValueError:
                    raise RuntimeError(f"HTTP {e.code}: {text[:300]}") from None
            except (urllib.error.URLError, TimeoutError, ConnectionError,
                    http.client.HTTPException, ValueError) as e:
                last_err = repr(e)
                self.stats["retries"] += 1
                print(f"  [nexus] {e!r}; retrying in {delay:.0f}s", file=sys.stderr)
                time.sleep(delay)
                delay = min(delay * 2, 120)
        raise RuntimeError(f"giving up after {max_retries + 1} attempts: {last_err}")

    def _is_transient(self, errors) -> bool:
        for err in errors or []:
            msg = (str(err.get("message", "")) + " " +
                   json.dumps(err.get("extensions", {}))).lower()
            if any(h in msg for h in self.TRANSIENT_HINTS):
                return True
        return False

    def _send_batch(self, subqueries: list[str]) -> list[tuple]:
        aliases = [f"q{i}" for i in range(len(subqueries))]
        query = "query {\n" + "\n".join(f"  {a}: {sq}" for a, sq in zip(aliases, subqueries)) + "\n}"
        try:
            payload = self._post(query)
        except RuntimeError as e:
            self.stats["errors"] += 1
            return [(None, [{"message": str(e), "transient": True}])] * len(subqueries)
        data = payload.get("data") or {}
        errors = payload.get("errors") or []
        per_alias: dict[str, list] = {a: [] for a in aliases}
        global_errors = []
        for err in errors:
            path = err.get("path") or []
            hit = next((p for p in path if isinstance(p, str) and p in per_alias), None)
            if hit:
                per_alias[hit].append(err)
            else:
                global_errors.append(err)
        out = []
        for a in aliases:
            if per_alias[a] or (a in data and data[a] is not None):
                out.append((data.get(a), per_alias[a]))
            elif global_errors and len(subqueries) > 1:
                out.append("RETRY_SINGLE")
            else:
                out.append((data.get(a), global_errors))
        return out

    def run(self, subqueries: list[str]) -> list[dict]:
        """Run sub-queries (cached); returns [{'data': ..., 'errors': [...]}] in input order."""
        results: list = [None] * len(subqueries)
        pending: list[int] = []
        seen: dict[str, int] = {}
        for i, sq in enumerate(subqueries):
            cached = self._load(sq)
            if cached is not None:
                self.stats["cache_hits"] += 1
                results[i] = {"data": cached.get("data"), "errors": cached.get("errors") or []}
            elif sq in seen:
                continue
            else:
                seen[sq] = i
                pending.append(i)
        if pending and self.offline:
            for i in pending:
                self.stats["offline_misses"] += 1
                results[i] = {"data": None, "errors": [{"message": "offline cache miss"}]}
            pending = []
        while pending:
            chunk, pending = pending[: self.batch_size], pending[self.batch_size:]
            self.stats["cache_misses"] += len(chunk)
            outs = self._send_batch([subqueries[i] for i in chunk])
            singles = []
            for i, res in zip(chunk, outs):
                if res == "RETRY_SINGLE":
                    singles.append(i)
                    continue
                self._finish(subqueries[i], i, res, results)
            for i in singles:
                res = self._send_batch([subqueries[i]])[0]
                self._finish(subqueries[i], i, res, results)
        # Duplicated sub-queries within one call share the first result.
        for i, sq in enumerate(subqueries):
            if results[i] is None:
                results[i] = results[seen[sq]]
        return results

    def _finish(self, subquery: str, idx: int, res: tuple, results: list) -> None:
        data, errors = res
        if errors:
            self.stats["errors"] += 1
            if self.verbose:
                print(f"  [nexus] error: {errors[0].get('message')} :: {subquery[:120]}",
                      file=sys.stderr)
        transient = any(e.get("transient") for e in errors) or self._is_transient(errors)
        if not transient:
            self._store(subquery, data, errors)
        results[idx] = {"data": data, "errors": errors}


MOD_FIELDS = ("modId name author uploader { name } adultContent status downloads "
              "endorsements version updatedAt")
FILE_FIELDS = "fileId name version category date uri primary"


def q_mods_exact(name: str) -> str:
    """Name lookup.  WILDCARD without '*' matches every word as a case-insensitive
    substring (so 'lux' also hits 'Claralux'); relevance sort puts the exact name first."""
    val = gql_str(wildcard_escape(name.lower()))
    return (f'mods(filter: {{gameId: [{{value: "{GAME_ID}"}}], name: [{{value: {val}, op: WILDCARD}}]}}, '
            f'sort: [{{relevance: {{direction: DESC}}}}], count: 10) '
            f'{{ totalCount nodes {{ {MOD_FIELDS} }} }}')


def q_mods_words(words: list[str], english: bool, count: int = 12) -> str:
    vals = ", ".join(f"{{value: {gql_str(w)}}}" for w in words)
    lang = ', languageName: [{value: "English"}]' if english else ""
    return (f'mods(filter: {{gameId: [{{value: "{GAME_ID}"}}], nameStemmed: [{vals}]{lang}}}, '
            f'sort: [{{relevance: {{direction: DESC}}}}], count: {count}) '
            f'{{ totalCount nodes {{ {MOD_FIELDS} }} }}')


def q_mod_files(mod_id: int) -> str:
    return f'modFiles(modId: "{mod_id}", gameId: "{GAME_ID}") {{ {FILE_FIELDS} }}'


def q_legacy_mods(ids: list[int]) -> str:
    vals = ", ".join(f"{{gameId: {GAME_ID}, modId: {i}}}" for i in ids)
    return f"legacyMods(ids: [{vals}]) {{ nodes {{ {MOD_FIELDS} }} }}"


def q_contents(plugin: str, exact_case: bool = False) -> str:
    """Archive contents lookup by file name.  EQUALS is exact and case-sensitive; WILDCARD
    is a case-insensitive substring match, so its nodes are filtered by exact name later."""
    if exact_case:
        val, op = gql_str(plugin), "EQUALS"
    else:
        val, op = gql_str(wildcard_escape(plugin.lower())), "WILDCARD"
    return (f"modFileContents(filter: {{gameId: [{{value: {GAME_ID}}}], "
            f"fileNameWildcard: [{{value: {val}, op: {op}}}]}}, count: 100) "
            f"{{ totalCount nodes {{ modId fileId fileName }} }}")


def errors_text(errors) -> str:
    return "; ".join(sorted({str(e.get("message", ""))[:120] for e in errors or []}))


def is_adult_block(errors) -> bool:
    return any("adult" in (json.dumps(e) or "").lower() for e in errors or [])


# --------------------------------------------------------------------------------------
# Local data
# --------------------------------------------------------------------------------------

def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig", errors="replace").splitlines()


def load_target_modlist(path: Path) -> list[tuple[int, bool, str]]:
    out = []
    for no, line in enumerate(read_lines(path), 1):
        line = line.rstrip("\r\n")
        if not line or line.startswith("#") or line[0] not in "+-*":
            continue
        out.append((no, line[0] == "+", line[1:]))
    return out


def load_known_folders(snap_dir: Path) -> set[str]:
    known: set[str] = set()
    for csv_path in sorted(snap_dir.glob("*.csv")):
        with csv_path.open(encoding="utf-8-sig", newline="") as fh:
            for row in csv.DictReader(fh):
                name = (row.get("mod") or "").strip()
                if name:
                    known.add(name.lower())
    for ml in sorted(snap_dir.glob("lol-*/modlist.txt")):
        for line in read_lines(ml):
            if line[:1] in "+-*" and len(line) > 1:
                known.add(line[1:].strip().lower())
    return known


def load_plugin_names(path: Path) -> list[str]:
    out = []
    for line in read_lines(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        out.append(line.lstrip("*"))
    return out


def load_source_plugins(snap_dir: Path) -> set[str]:
    src: set[str] = set()
    for pattern in ("lol-*/plugins.txt", "lol-*/loadorder.txt"):
        for p in sorted(snap_dir.glob(pattern)):
            src.update(x.lower() for x in load_plugin_names(p))
    return src


# --------------------------------------------------------------------------------------
# Identification logic
# --------------------------------------------------------------------------------------

def segments(name: str) -> list[str]:
    parts = [p.strip() for p in SEGMENT_SPLIT_RE.split(core_string(name)) if p.strip()]
    return parts


def query_word_list(tokens: list[str]) -> list[str]:
    """Words for a nameStemmed AND query (single characters are dropped)."""
    out, seen = [], set()
    for t in tokens:
        if len(t) < 2 or t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out[:10]


def stage_a_queries(folder: str) -> list[str]:
    base = strip_dup_suffix(folder)
    core = core_string(base)
    qs = [q_mods_exact(folder)]
    for extra in (base, core):
        if extra.lower() != folder.lower():
            qs.append(q_mods_exact(extra))
    all_words = query_word_list(tokenize(base))
    core_words = query_word_list(core_tokens(base))
    qs.append(q_mods_words(all_words, english=True))
    qs.append(q_mods_words(core_words, english=True))
    segs = segments(base)
    if len(segs) > 1:
        first = query_word_list(core_tokens(segs[0]))
        if first:
            qs.append(q_mods_words(first, english=True))
    distinct = [w for w in core_words if w not in GENERIC_TOKENS]
    if distinct:
        qs.append(q_mods_words(distinct, english=True))
    return list(dict.fromkeys(q for q in qs if "nameStemmed: []" not in q))


def stage_c_queries(folder: str) -> list[str]:
    base = strip_dup_suffix(folder)
    core_words = query_word_list(core_tokens(base))
    camel_words = query_word_list(core_tokens(base, camel=True))
    distinct = [w for w in core_words if w not in GENERIC_TOKENS]
    distinct_camel = [w for w in camel_words if w not in GENERIC_TOKENS]
    segs = segments(base)
    qs = [q_mods_words(core_words, english=False)]
    if segs and len(segs) > 1:
        qs.append(q_mods_words(query_word_list(core_tokens(segs[0])), english=False))
        qs.append(q_mods_words(query_word_list(core_tokens(segs[-1])), english=True))
    if camel_words != core_words:
        qs.append(q_mods_words(camel_words, english=True))
        if distinct_camel:
            qs.append(q_mods_words(distinct_camel, english=True))
    if len(distinct) >= 3:
        qs.append(q_mods_words(distinct[1:], english=True))
        qs.append(q_mods_words(distinct[:2], english=True))
    elif len(distinct) == 2:
        qs.append(q_mods_words(distinct[1:], english=True))
    if len(distinct) >= 2:
        # First distinctive word alone: finds author "hub" mods such as "Praedy's PBR Hub".
        qs.append(q_mods_words(distinct[:1], english=True))
    if re.search(r"['’´`]s\b", base):
        # Possessive dropped instead of fused ("Mahrlek1´s" -> "mahrlek1").
        poss = re.sub(r"['’´`]s\b", "", base)
        pwords = [w for w in query_word_list(core_tokens(poss)) if w not in GENERIC_TOKENS]
        if pwords:
            qs.append(q_mods_words(pwords[:3], english=False))
    return list(dict.fromkeys(q for q in qs if "nameStemmed: []" not in q))


# Words in mod names that mark "container" pages whose files are separate MO2 folders.
CONTAINER_TOKENS = {"hub", "collection", "compendium", "repository", "resources", "aio",
                    "patches", "conversions", "pack", "series", "compilation", "misc"}

# Tokens that denote a materially different variant of the same asset.
VARIANT_TOKENS = {"pbr", "smp", "hdt", "3ba", "cbbe", "bhunp", "ube", "unp", "himbo", "cm"}


def variant_penalty(folder: str, cand: str) -> float:
    """Penalty when folder and candidate disagree on variant words such as 'PBR'."""
    ft = set(tokenize(folder, camel=True)) & VARIANT_TOKENS
    ct = set(tokenize(cand, camel=True)) & VARIANT_TOKENS
    return min(0.2, 0.1 * len(ft ^ ct))


def light_stem(tok: str) -> str:
    return tok[:-1] if len(tok) > 3 and tok.endswith("s") and not tok.endswith("ss") else tok


class Candidate:
    __slots__ = ("mod", "sources", "files", "files_err", "score", "detail", "best_file",
                 "file_score", "plugin_hits", "plugin_files", "equal_files", "best_vmatch")

    def __init__(self, mod: dict):
        self.mod = mod
        self.sources: set[str] = set()
        self.files: list[dict] | None = None
        self.files_err = ""
        self.score = 0.0
        self.detail = ""
        self.best_file: dict | None = None
        self.file_score = 0.0
        self.plugin_hits: set[str] = set()
        self.plugin_files: set[int] = set()
        self.equal_files: list[str] = []
        self.best_vmatch = False

    @property
    def mod_id(self) -> int:
        return int(self.mod["modId"])

    @property
    def name(self) -> str:
        return self.mod.get("name") or ""

    @property
    def downloads(self) -> int:
        return int(self.mod.get("downloads") or 0)

    @property
    def live_best(self) -> bool:
        return bool(self.best_file) and self.best_file.get("category") not in STALE_CATS


def author_of(mod: dict) -> str:
    author = (mod.get("author") or "").strip()
    uploader = ((mod.get("uploader") or {}).get("name") or "").strip()
    if author and uploader and uploader.lower() not in author.lower():
        return f"{author} (uploader {uploader})"
    return author or uploader


def prelim_score(folder: str, cand: Candidate) -> float:
    s = name_sim(folder, cand.name) - lang_penalty(folder, cand.name)
    if "exact" in cand.sources:
        s += 0.05
    if cand.plugin_hits:
        s += 0.2
    ctoks = set(tokenize(cand.name))
    if ctoks & CONTAINER_TOKENS and ctoks & set(core_tokens(folder)) - GENERIC_TOKENS:
        s += 0.25
    return s + math.log10(cand.downloads + 1) / 200.0


def file_sort_key(f: dict) -> tuple:
    return (FILE_CAT_RANK.get(f.get("category", ""), 0), int(f.get("date") or 0),
            int(f.get("fileId") or 0))


def version_match(file_version: str, folder_versions: set[str]) -> bool:
    """True when the file version equals (or extends, '3.0' -> '3.0.1') a folder version."""
    fv = norm_version(file_version)
    if not fv or not folder_versions:
        return False
    return any(fv == v or fv.startswith(v + ".") for v in folder_versions)


def score_files(folder: str, cand: Candidate) -> None:
    """Pick the best-matching file of a candidate mod and compute the mod-level score.

    A file only counts as evidence when its own name (or archive name, or
    '<mod name> <file name>') matches the folder better than the mod name alone does.
    Among files whose score is within 0.04 of the best (or within 0.2 when the file
    version equals the version written in the folder name), the pick prefers a version
    match, then a current (non-archived) file, then a file containing a linked plugin.
    """
    base = strip_dup_suffix(folder)
    fvers = versions_in(folder)
    pen = lang_penalty(folder, cand.name)
    mod_s = max(name_sim(folder, cand.name), name_sim(base, cand.name)) \
        - variant_penalty(base, cand.name)
    mod_norm = "".join(tokenize(cand.name))
    entries = []
    for f in cand.files or []:
        fname = f.get("name") or ""
        stem = uri_stem(f.get("uri") or "", cand.mod_id)
        comp = f"{cand.name} {fname}"
        options = [(name_sim(base, fname) - variant_penalty(base, fname), "file")]
        # An archive name that merely repeats the mod name adds no information.
        if "".join(tokenize(stem)) not in (mod_norm, "".join(tokenize(fname))):
            options.append((name_sim(base, stem) - variant_penalty(base, stem), "archive"))
        comp_s = name_sim(base, comp) - variant_penalty(base, comp)
        if comp_s > mod_s + 0.02:
            options.append((comp_s, "mod+file"))
        fs, how = max(options, key=lambda x: x[0])
        vmatch = 1 if version_match(f.get("version", ""), fvers) else 0
        pfile = 1 if int(f.get("fileId") or 0) in cand.plugin_files else 0
        live = 0 if f.get("category") in STALE_CATS else 1
        entries.append((fs, how, vmatch, live, pfile, f))
    cand.best_file = None
    cand.file_score = 0.0
    cand.equal_files = []
    cand.best_vmatch = False
    top_fs = max((e[0] for e in entries), default=0.0)
    if entries:
        pool = [e for e in entries if e[0] >= top_fs - 0.04 or (e[2] and e[0] >= top_fs - 0.2)]
        pick = max(pool, key=lambda e: (e[2], e[3], e[4], round(e[0], 2)) + file_sort_key(e[5]))
        cand.best_file = pick[5]
        cand.file_score = pick[0]
        cand.best_vmatch = bool(pick[2])
        bname = "".join(tokenize(pick[5].get("name") or ""))
        cand.equal_files = sorted({e[5].get("name") or "" for e in pool
                                   if round(e[0], 2) >= round(pick[0], 2) and e[3]
                                   and "".join(tokenize(e[5].get("name") or "")) != bname})
        best_how = max(entries, key=lambda e: e[0])[1]
    if top_fs >= mod_s:
        cand.score = top_fs - pen
        cand.detail = best_how
    else:
        cand.score = mod_s - pen
        cand.detail = "mod"


def choose_file(folder: str, cand: Candidate, notes: list[str]) -> dict | None:
    """Return the file to suggest (or None when no file can be picked with confidence)."""
    files = cand.files or []
    if not files:
        if cand.files_err:
            notes.append(f"file list unavailable: {cand.files_err}")
        else:
            notes.append("mod has no listed files")
        return None
    if cand.best_file is not None and (cand.file_score >= 0.85
                                       or (cand.best_vmatch and cand.file_score >= 0.7)):
        if cand.equal_files:
            notes.append("other files match equally well: " + " | ".join(cand.equal_files[:3]))
        return cand.best_file
    live = [f for f in files if f.get("category") not in STALE_CATS]
    # Files that contain a plugin linked to this folder.
    pfiles = [f for f in files if int(f.get("fileId") or 0) in cand.plugin_files]
    pool = [f for f in pfiles if f.get("category") not in STALE_CATS]
    if pool:
        names = sorted({f.get("name") or "" for f in pool})
        if len(names) == 1:
            notes.append("file chosen because it contains the linked plugin")
            return max(pool, key=file_sort_key)
    mains = [f for f in live if f.get("category") == "MAIN"]
    if len(mains) == 1:
        notes.append("no file name matches the folder; the only current MAIN file is suggested")
        return mains[0]
    if mains:
        names = sorted({m.get("name", "") for m in mains})
        if len(names) == 1:
            notes.append("no file name matches the folder; newest MAIN file suggested")
            return max(mains, key=file_sort_key)
        notes.append("no file name matches the folder; several MAIN files: "
                     + " | ".join(names[:4]))
        return None
    notes.append("no current MAIN file and no file name matching the folder")
    return None


def fmt_alt(c: Candidate) -> str:
    return f"{c.name} (#{c.mod_id}, s={c.score:.2f}, dl={c.downloads})"


class Identifier:
    def __init__(self, client: NexusClient, args):
        self.client = client
        self.args = args
        self.mod_cache: dict[int, dict] = {}
        self.plugin_nodes: dict[str, list[tuple[int, int]]] = {}
        self.plugin_total: dict[str, int] = {}
        self.plugin_err: dict[str, str] = {}

    def plugin_mods(self, plugin: str) -> set[int]:
        return {m for m, _f in self.plugin_nodes.get(plugin, [])}

    # -- plugins ----------------------------------------------------------------------
    def search_plugins(self, plugins: list[str]) -> None:
        todo = sorted(set(plugins), key=str.lower)
        print(f"[plugins] searching Nexus file contents for {len(todo)} plugin names",
              file=sys.stderr)
        step = 50
        for start in range(0, len(todo), step):
            chunk = todo[start:start + step]
            queries = []
            for p in chunk:
                queries += [q_contents(p, exact_case=True), q_contents(p)]
            res = self.client.run(queries)
            for i, p in enumerate(chunk):
                nodes = set()
                total = 0
                errs = []
                for r in res[2 * i: 2 * i + 2]:
                    data = r["data"] or {}
                    errs += r["errors"] or []
                    for node in data.get("nodes") or []:
                        if (node.get("fileName") or "").lower() != p.lower():
                            continue
                        mid = int(node.get("modId") or 0)
                        fid = int(node.get("fileId") or 0)
                        if mid:
                            nodes.add((mid, fid))
                    total = max(total, int(data.get("totalCount") or 0))
                self.plugin_nodes[p] = sorted(nodes)
                self.plugin_total[p] = total
                if errs:
                    self.plugin_err[p] = errors_text(errs)

    def fetch_mods(self, ids: list[int]) -> None:
        ids = sorted({i for i in ids if i not in self.mod_cache})
        for start in range(0, len(ids), 25):
            chunk = ids[start:start + 25]
            res = self.client.run([q_legacy_mods(chunk)])[0]
            for node in ((res["data"] or {}).get("nodes") or []):
                self.mod_cache[int(node["modId"])] = node
            for i in chunk:
                self.mod_cache.setdefault(i, {"modId": i, "name": "", "_missing": True,
                                              "_error": errors_text(res["errors"])})

    # -- folders ----------------------------------------------------------------------
    def _collect(self, results: list[dict], queries: list[str], cands: dict[int, Candidate],
                 flags: dict) -> None:
        for q, r in zip(queries, results):
            if r["errors"]:
                flags.setdefault("errors", set()).add(errors_text(r["errors"]))
                if is_adult_block(r["errors"]):
                    flags["adult_blocked"] = True
            for node in ((r["data"] or {}).get("nodes") or []):
                mid = int(node["modId"])
                self.mod_cache.setdefault(mid, node)
                c = cands.get(mid)
                if c is None:
                    c = cands[mid] = Candidate(node)
                if "op: WILDCARD" in q:
                    m = re.search(r'name: \[\{value: ("(?:[^"\\]|\\.)*")', q)
                    val = json.loads(m.group(1)) if m else ""
                    exact = "".join(tokenize(val)) == "".join(tokenize(node.get("name") or ""))
                    c.sources.add("exact" if exact else "words")
                else:
                    c.sources.add("words")

    def _mark_plugins(self, cands: dict[int, Candidate], assoc: list[tuple[str, float]]) -> None:
        for p, _s in assoc:
            for mid, fid in self.plugin_nodes.get(p, []):
                c = cands.get(mid)
                if c is not None:
                    c.plugin_hits.add(p)
                    c.plugin_files.add(fid)

    def _fetch_files(self, folder: str, cands: list[Candidate], flags: dict) -> None:
        need = [c for c in cands if c.files is None]
        if not need:
            return
        res = self.client.run([q_mod_files(c.mod_id) for c in need])
        for c, r in zip(need, res):
            c.files = list(r["data"] or [])
            if r["errors"]:
                c.files_err = errors_text(r["errors"])
                if is_adult_block(r["errors"]):
                    flags["adult_blocked"] = True
            score_files(folder, c)

    def identify(self, folder: str, assoc_plugins: list[tuple[str, float]]) -> dict:
        flags: dict = {}
        cands: dict[int, Candidate] = {}
        qa = stage_a_queries(folder)
        self._collect(self.client.run(qa), qa, cands, flags)

        # Mods whose archives contain plugins associated with this folder by name.
        plugin_mod_ids: dict[int, set[str]] = {}
        for p, _s in assoc_plugins:
            for mid in self.plugin_mods(p):
                plugin_mod_ids.setdefault(mid, set()).add(p)
        extra = [m for m in plugin_mod_ids if m not in cands]
        # Only follow plugins that point to a handful of mods (unique identifiers).
        if extra and len(plugin_mod_ids) <= 6:
            self.fetch_mods(extra)
            for mid in sorted(extra):
                node = self.mod_cache.get(mid)
                if node and not node.get("_missing"):
                    cands[mid] = Candidate(node)
                    cands[mid].sources.add("plugin")
        self._mark_plugins(cands, assoc_plugins)

        ranked = sorted(cands.values(), key=lambda c: (-prelim_score(folder, c), c.mod_id))
        k = self.args.files_per_folder
        first = ranked[:k] + [c for c in ranked[k:] if c.plugin_hits][:4]
        self._fetch_files(folder, first, flags)
        best = self._best(cands)
        if best is None or best.score < 0.9:
            qc = [q for q in stage_c_queries(folder) if q not in qa]
            if qc:
                before = set(cands)
                self._collect(self.client.run(qc), qc, cands, flags)
                self._mark_plugins(cands, assoc_plugins)
                new = [c for c in cands.values() if c.mod_id not in before]
                if new:
                    new.sort(key=lambda c: (-prelim_score(folder, c), c.mod_id))
                    self._fetch_files(folder, new[:5], flags)
        return self.decide(folder, (cands, assoc_plugins, plugin_mod_ids, flags))

    def decide(self, folder: str, ctx: tuple) -> dict:
        """Classify a folder from its candidate context; keeps the context for later passes."""
        cands = ctx[0]
        row = self._decide(folder, *ctx)
        row["_ctx"] = ctx
        ranked = sorted((c for c in cands.values() if c.files is not None), key=self._rank_key)
        row["_debug"] = [
            f"{c.score:.3f} {c.detail} #{c.mod_id} {c.name!r} -> "
            f"{(c.best_file or {}).get('name')!r} [{(c.best_file or {}).get('category')}]"
            f"{' plugins=' + ','.join(sorted(c.plugin_hits)) if c.plugin_hits else ''}"
            for c in ranked[:6]]
        return row

    def hub_pass(self, rows: list[dict]) -> int:
        """Match unresolved folders against the files of mods already chosen for others.

        Container mods ('PBR Hub', "Praedy's PBR Hub", patch collections, voice packs) hold
        one Nexus file per MO2 folder, and sibling folders often come from the same page.
        Their file lists are already loaded, so this pass needs no extra requests; only a
        file-level match of at least 0.9 is accepted.
        """
        chosen: dict[int, Candidate] = {}
        for row in rows:
            cand = row.get("_cand")
            if cand is not None and row.get("category") == "nexus_found" and cand.files:
                chosen.setdefault(cand.mod_id, cand)
        hubs = []
        for mid in sorted(chosen):
            cand = chosen[mid]
            ftoks = set()
            for f in cand.files:
                ftoks.update(core_tokens(f.get("name") or ""))
            hubs.append((cand, ftoks - GENERIC_TOKENS))
        changed = 0
        for row in rows:
            if row.get("category") not in ("not_found", "nexus_ambiguous") or "_ctx" not in row:
                continue
            folder = row["folder"]
            cands, assoc, plugin_mod_ids, flags = row["_ctx"]
            fdist = set(core_tokens(strip_dup_suffix(folder))) - GENERIC_TOKENS
            need = 1 if len(fdist) <= 1 else 2
            added = False
            for hub, htoks in hubs:
                if len(fdist & htoks) < need:
                    continue
                old = cands.get(hub.mod_id)
                if old is not None and old.files is not None:
                    continue
                c = Candidate(hub.mod)
                c.files = hub.files
                c.sources.add("hub")
                probe = {hub.mod_id: c}
                self._mark_plugins(probe, assoc)
                score_files(folder, c)
                if c.score >= 0.9 and c.detail != "mod":
                    cands[hub.mod_id] = c
                    added = True
            if not added:
                continue
            new = self.decide(folder, (cands, assoc, plugin_mod_ids, flags))
            if new.get("_cand") is not None and "hub" in new["_cand"].sources \
                    and new["category"] == "nexus_found":
                new["notes"].append("matched a file of a mod already identified for other "
                                    "folders (second pass)")
                for k in [k for k in row if k not in ("folder", "target_line", "_related")]:
                    row.pop(k)
                row.update(new)
                changed += 1
        return changed

    @staticmethod
    def _rank_key(c: Candidate) -> tuple:
        return (-(c.score + (0.1 if c.plugin_hits else 0.0)), -int(c.live_best),
                -c.downloads, c.mod_id)

    def _best(self, cands: dict[int, Candidate]) -> Candidate | None:
        scored = [c for c in cands.values() if c.files is not None]
        return min(scored, key=self._rank_key) if scored else None

    def _decide(self, folder: str, cands: dict[int, Candidate],
                assoc_plugins: list[tuple[str, float]], plugin_mod_ids: dict[int, set[str]],
                flags: dict) -> dict:
        notes: list[str] = []
        row = {"category": "not_found", "confidence": "", "match_method": ""}
        scored = sorted((c for c in cands.values() if c.files is not None), key=self._rank_key)
        strong_plugins = {p for p, s in assoc_plugins if s >= 0.9}
        if not scored:
            if flags.get("adult_blocked"):
                row["category"] = "adult_gated"
                notes.append("search blocked by adult-content gate")
            if flags.get("errors"):
                notes.append("API errors: " + "; ".join(sorted(flags["errors"]))[:200])
            if assoc_plugins and all(not self.plugin_nodes.get(p) for p, _ in assoc_plugins):
                notes.append("linked plugin(s) not found in Nexus file contents")
            notes.append("no Nexus candidates")
            row["notes"] = notes
            return row
        best = scored[0]
        others = [c for c in scored[1:] if c.mod_id != best.mod_id]
        second = others[0] if others else None
        margin = best.score - (second.score if second else 0.0)
        pc = bool(best.plugin_hits)
        # Strongly linked plugins that Nexus places in other mods but never in `best`.
        contra = sorted(p for p, s in assoc_plugins
                        if s >= 0.9 and self.plugin_nodes.get(p)
                        and best.mod_id not in self.plugin_mods(p))

        exact = best.score >= 0.97
        if exact:
            method = "name_exact"
            if second is None or second.score < 0.97 or margin >= 0.03:
                cat, conf = "nexus_found", "high"
            elif pc and not second.plugin_hits:
                cat, conf = "nexus_found", "medium"
                notes.append("another mod has an equally exact name; the linked plugin "
                             "points to this one")
            elif best.live_best and not second.live_best:
                cat, conf = "nexus_found", "medium"
                notes.append("another mod has an equally exact name but only as an "
                             "archived/old file")
            elif best.downloads >= 5 * max(1, second.downloads):
                cat, conf = "nexus_found", "medium"
                notes.append("another mod has an equally exact name; picked the far more "
                             "downloaded one")
            else:
                cat, conf = "nexus_ambiguous", "low"
                notes.append("several mods match the name exactly")
        elif best.score >= 0.82 and (margin >= 0.08 or pc):
            cat, conf, method = "nexus_found", "medium", "name_fuzzy"
        elif pc and best.score >= 0.5:
            cat, conf, method = "nexus_found", "medium", "plugin_contents"
        elif pc and best.plugin_hits & strong_plugins and len(plugin_mod_ids) == 1:
            cat, conf, method = "nexus_found", "medium", "plugin_contents"
        elif pc:
            cat, conf, method = "nexus_ambiguous", "low", "plugin_contents"
        elif best.score >= 0.65:
            cat, conf, method = "nexus_ambiguous", "low", "name_fuzzy"
        else:
            cat, conf, method = "not_found", "", ""

        if pc and cat == "nexus_found" and conf == "medium" and method == "name_fuzzy":
            conf = "high"
        if pc:
            notes.append("linked plugin(s) found in this mod's files: "
                         + ", ".join(sorted(best.plugin_hits, key=str.lower)))
        if contra and cat != "not_found":
            notes.append("linked plugin(s) found only in other mods: " + ", ".join(contra[:4]))
            if not pc:
                conf = {"high": "medium", "medium": "low"}.get(conf, conf)
                if conf == "low" and cat == "nexus_found":
                    cat = "nexus_ambiguous"

        row["notes"] = notes
        if cat == "not_found":
            notes.append(f"closest: {fmt_alt(best)}" if best.score >= 0.4 else "no close name match")
            if flags.get("adult_blocked"):
                row["category"] = "adult_gated"
                notes.append("some results blocked by adult-content gate")
            return row

        row.update(category=cat, confidence=conf, match_method=method)
        row["_cand"] = best
        mod = best.mod
        row["nexus_mod_id"] = best.mod_id
        row["nexus_mod_name"] = best.name
        row["nexus_author"] = author_of(mod)
        row["_mod_id"] = best.mod_id
        row["_files"] = best.files or []
        if best.detail in ("file", "mod+file", "archive") and best.file_score >= 0.85:
            notes.append({"file": "folder matches a file name",
                          "mod+file": "folder matches '<mod name> <file name>'",
                          "archive": "folder matches an archive file name"}[best.detail])
        if exact and best.score < 1.0:
            notes.append("match after dropping version/edition tokens")
        if (mod.get("status") or "published") != "published":
            notes.append(f"mod status: {mod.get('status')}")
        if mod.get("adultContent"):
            notes.append("mod flagged adult content")
        f = choose_file(folder, best, notes)
        if f is not None:
            row["suggested_file_id"] = f.get("fileId")
            row["suggested_file_name"] = f.get("name")
            row["suggested_file_version"] = f.get("version")
            row["file_category"] = f.get("category")
            row["_file_name"] = f.get("name") or ""
            if version_match(f.get("version", ""), versions_in(folder)):
                notes.append("file version matches the version in the folder name")
            if f.get("category") in STALE_CATS:
                live = [x for x in best.files or [] if x.get("category") == "MAIN"]
                msg = f"suggested file only exists as {f.get('category')}"
                if live:
                    cur = max(live, key=file_sort_key)
                    msg += (f"; current MAIN: {cur.get('name')} v{cur.get('version')} "
                            f"(#{cur.get('fileId')})")
                notes.append(msg)
        close = [c for c in others if c.score >= max(0.6, best.score - 0.12)][:3]
        if close:
            notes.append("alternatives: " + "; ".join(fmt_alt(c) for c in close))
        return row


# --------------------------------------------------------------------------------------
# Plugin <-> folder association
# --------------------------------------------------------------------------------------

def associate_plugins(plugins: list[str], folders: list[str], threshold: float,
                      exact_only: bool = False) -> dict[str, tuple[str, float]]:
    """Map plugin -> (folder, score) when a plugin name clearly resembles one folder.

    With exact_only, only plugins whose name equals the folder name (ignoring case,
    spacing, punctuation and CamelCase) are linked.
    """
    ftoks = {}
    fjoin = {}
    for f in folders:
        b = strip_dup_suffix(f)
        ftoks[f] = {light_stem(t) for t in
                    set(tokenize(b, camel=True)) | set(tokenize(b)) | set(core_tokens(b, camel=True))}
        fjoin[f] = {"".join(tokenize(b)), "".join(core_tokens(b))}
    out: dict[str, tuple[str, float]] = {}
    for p in plugins:
        pname = ARCHIVE_EXT_RE.sub("", p)
        if exact_only:
            pj = {"".join(tokenize(pname)), "".join(core_tokens(pname))}
            hits = sorted(f for f in folders if pj & fjoin[f])
            if len(hits) == 1:
                out[p] = (hits[0], 1.0)
            continue
        ptoks = {light_stem(t) for t in set(tokenize(pname, camel=True)) | set(tokenize(pname))}
        pcore = {light_stem(t) for t in core_tokens(pname, camel=True)
                 if t not in GENERIC_TOKENS and not t.isdigit()}
        scored = []
        for f in folders:
            if not (ptoks & ftoks[f]):
                continue
            base_s = name_sim(pname, strip_dup_suffix(f))
            # Distinctive plugin words missing from the folder name weaken the link.
            missing = len(pcore - ftoks[f])
            s = base_s - 0.15 * missing
            # Every distinctive word of the plugin name appears in the folder name
            # ('Valtheim Guardians.esp' -> 'Guardians of Valtheim'); the more of the
            # folder's distinctive words the plugin covers, the stronger the link.
            fdist = {t for t in ftoks[f] if t not in GENERIC_TOKENS and not t.isdigit()}
            if len(pcore) >= 2 and not missing and fdist:
                coverage = len(pcore & fdist) / len(fdist)
                if coverage >= 0.65:
                    s = max(s, 0.8 + 0.2 * min(1.0, coverage))
            if s >= threshold - 0.1:
                scored.append((s, base_s, f))
        if not scored:
            continue
        scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
        s1, b1, f1 = scored[0]
        s2, b2 = (scored[1][0], scored[1][1]) if len(scored) > 1 else (0.0, 0.0)
        if s1 >= threshold and (s1 - s2 >= 0.04 or (s1 >= 0.99 and b1 - b2 >= 0.04)):
            out[p] = (f1, round(s1, 3))
    return out


# --------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--target-modlist", type=Path, default=REPO_ROOT / "data/target/modlist.txt")
    ap.add_argument("--target-plugins", type=Path, default=REPO_ROOT / "data/target/plugins.txt")
    ap.add_argument("--snapshots", type=Path, default=REPO_ROOT / "data/snapshots")
    ap.add_argument("--out", type=Path, default=REPO_ROOT / "data/analysis/nexus_candidates.csv")
    ap.add_argument("--cache-dir", type=Path,
                    default=Path(os.environ.get("NEXUS_CACHE_DIR",
                                                Path.home() / ".cache/pages-modlist-tools/nexus")))
    ap.add_argument("--limit", type=int, default=0,
                    help="only process the first N unknown folders (0 = all)")
    ap.add_argument("--sleep", type=float, default=1.0,
                    help="minimum seconds between HTTP requests (default 1.0)")
    ap.add_argument("--batch-size", type=int, default=8,
                    help="GraphQL sub-queries sent per HTTP request as aliases (default 8)")
    ap.add_argument("--files-per-folder", type=int, default=4,
                    help="candidate mods whose file lists are fetched per folder")
    ap.add_argument("--plugin-threshold", type=float, default=0.75,
                    help="minimum name similarity to link a plugin to a folder")
    ap.add_argument("--offline", action="store_true", help="use only the cache, never the network")
    ap.add_argument("--details", type=Path, default=None,
                    help="optional JSON dump of per-folder decisions for review")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    target = load_target_modlist(args.target_modlist)
    known = load_known_folders(args.snapshots)
    unknown: list[tuple[int, str]] = []
    for line_no, enabled, name in target:
        if not enabled or name.endswith("_separator"):
            continue
        low = name.lower()
        if low in known or strip_dup_suffix(name).lower() in known:
            continue
        unknown.append((line_no, name))
    print(f"[target] {len(target)} entries, {len(unknown)} enabled folders missing from sources",
          file=sys.stderr)
    unknown_names = {n for _, n in unknown}
    # Normalised names of target folders that ARE found in the sources.
    known_target_norms = {"".join(tokenize(n)) for _, e, n in target
                          if e and n not in unknown_names and not n.endswith("_separator")}
    if args.limit > 0:
        unknown = unknown[: args.limit]

    # Plugins: target plugins absent from all source plugin lists are strong identifiers.
    target_plugins = load_plugin_names(args.target_plugins)
    src_plugins = load_source_plugins(args.snapshots)
    new_plugins = [p for p in target_plugins if p.lower() not in src_plugins]
    folder_names = [n for _, n in unknown]
    assoc = associate_plugins(new_plugins, folder_names, args.plugin_threshold)
    # Known-source plugins that look exactly like an unknown folder are also useful.
    # (skipped when a known target folder carries the plugin's own name, e.g. 'Lux.esp' and
    # a folder 'Lux' that is already in the sources)
    known_plugins = [p for p in target_plugins if p.lower() in src_plugins
                     and "".join(tokenize(p)) not in known_target_norms]
    assoc_known = associate_plugins(known_plugins, folder_names, 1.0, exact_only=True)
    folder_assoc: dict[str, list[tuple[str, float]]] = {}
    for p, (f, s) in list(assoc.items()) + list(assoc_known.items()):
        folder_assoc.setdefault(f, []).append((p, s))
    print(f"[plugins] {len(new_plugins)} target plugins not in source lists; "
          f"{len(assoc)} linked to folders by name (+{len(assoc_known)} known-source plugins)",
          file=sys.stderr)

    client = NexusClient(args.cache_dir, args.sleep, args.batch_size, args.offline, args.verbose)
    ident = Identifier(client, args)
    plugins_to_search = sorted(set(new_plugins) | set(assoc_known), key=str.lower)
    ident.search_plugins(plugins_to_search)

    rows = []
    details = []
    for idx, (line_no, folder) in enumerate(unknown, 1):
        low = folder.lower()
        related = sorted(folder_assoc.get(folder, []), key=lambda x: (-x[1], x[0].lower()))
        row = {"folder": folder, "target_line": line_no}
        if low in GENERATED_FOLDERS:
            row.update(category="generated", match_method="manual_hint", confidence="high",
                       notes=[GENERATED_FOLDERS[low]])
        elif low in CUSTOM_FOLDERS:
            row.update(category="custom", match_method="manual_hint", confidence="high",
                       notes=[CUSTOM_FOLDERS[low]])
        elif low in NON_NEXUS_FOLDERS:
            row.update(category="non_nexus", match_method="manual_hint", confidence="medium",
                       notes=[NON_NEXUS_FOLDERS[low]])
        elif low in MANUAL_HINTS:
            mod_id, note = MANUAL_HINTS[low]
            ident.fetch_mods([mod_id])
            mod = ident.mod_cache.get(mod_id, {})
            cand = Candidate(mod if mod.get("modId") else {"modId": mod_id, "name": ""})
            res = client.run([q_mod_files(mod_id)])[0]
            cand.files = list(res["data"] or [])
            score_files(folder, cand)
            notes = [note]
            row.update(category="nexus_found", match_method="manual_hint", confidence="high",
                       nexus_mod_id=mod_id, nexus_mod_name=cand.name,
                       nexus_author=author_of(mod), _mod_id=mod_id, _files=cand.files)
            f = choose_file(folder, cand, notes)
            if f:
                row.update(suggested_file_id=f.get("fileId"), suggested_file_name=f.get("name"),
                           suggested_file_version=f.get("version"),
                           file_category=f.get("category"), _file_name=f.get("name") or "")
            row["notes"] = notes
        else:
            print(f"[{idx}/{len(unknown)}] line {line_no}: {folder}", file=sys.stderr)
            row.update(ident.identify(folder, related))
        row["_related"] = related
        rows.append(row)

    changed = ident.hub_pass(rows)
    print(f"[second pass] {changed} folder(s) resolved from files of mods chosen for other "
          f"folders", file=sys.stderr)

    # related_plugins: plugins linked by name (unless Nexus file contents place them only in
    # other mods), plus every searched plugin that Nexus file contents place inside the
    # suggested file (same file name, any version) or, when no file is suggested, the mod.
    plugin_by_mod: dict[int, list[tuple[str, int]]] = {}
    for p in sorted(ident.plugin_nodes, key=str.lower):
        for mid, fid in ident.plugin_nodes[p]:
            plugin_by_mod.setdefault(mid, []).append((p, fid))

    def norm_name(x: str) -> str:
        return "".join(tokenize(x or ""))

    out_rows = []
    for row in sorted(rows, key=lambda r: (int(r["target_line"]), r["folder"])):
        related = row.pop("_related")
        mid = row.pop("_mod_id", None)
        files = row.pop("_files", None) or []
        fname = row.pop("_file_name", "")
        notes = row.get("notes") or []
        plugins: list[str] = []
        dropped: list[str] = []
        for p, _s in related:
            mods = ident.plugin_mods(p)
            if mid is not None and mods and int(mid) not in mods:
                dropped.append(p)
            else:
                plugins.append(p)
        if mid is not None:
            fids = None
            if fname:
                fids = {int(f.get("fileId") or 0) for f in files
                        if norm_name(f.get("name")) == norm_name(fname)}
            extra = sorted({p for p, fid in plugin_by_mod.get(int(mid), [])
                            if p not in plugins and (fids is None or fid in fids)},
                           key=str.lower)
            plugins += extra
        if dropped:
            notes.append("name-linked plugin(s) that Nexus places in other mods: "
                         + ", ".join(dropped[:4]))
        row["related_plugins"] = ";".join(plugins)
        row["notes"] = " | ".join(n for n in notes if n)
        row.pop("_ctx", None)
        row.pop("_cand", None)
        details.append(dict(row))
        out_rows.append({c: ("" if row.get(c) is None else row.get(c, "")) for c in CSV_COLUMNS})

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)
    if args.details:
        args.details.parent.mkdir(parents=True, exist_ok=True)
        args.details.write_text(json.dumps(details, ensure_ascii=False, indent=1), encoding="utf-8")

    counts: dict[str, int] = {}
    for r in out_rows:
        k = f"{r['category']}/{r['confidence'] or '-'}"
        counts[k] = counts.get(k, 0) + 1
    print(f"[done] wrote {len(out_rows)} rows to {args.out}", file=sys.stderr)
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}", file=sys.stderr)
    print(f"[nexus] {json.dumps(client.stats, sort_keys=True)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
