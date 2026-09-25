"""Optional: download the manifest's Nexus files with your own Premium API key, slowly.

（選用）以你自己的 Nexus Premium API 金鑰，限速下載 manifest 中待下載的檔案到 D:\\PM\\downloads。

The key is read ONLY from the environment variable NEXUS_API_KEY (never written to disk):
    set NEXUS_API_KEY=你的金鑰
    python tools\\nexus_fetch.py --pm D:\\PM --limit 20            (dry run: lists what it would fetch)
    python tools\\nexus_fetch.py --pm D:\\PM --limit 20 --apply
Uses the official v1 endpoints (files/{id}.json, download_link.json), identifies itself with
Application-Name headers, waits between files and stops when the hourly quota runs low.
Each archive gets an MO2 .meta file so MO2's Downloads tab shows the source. Install the
archives from MO2 into the folder name given in reports\\manifest.csv.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil  # noqa: E402
from pm.report import DEFAULT_REPORT_DIR, Report, read_csv, write_csv  # noqa: E402

API = "https://api.nexusmods.com/v1/games/skyrimspecialedition"
HEADERS = {"Application-Name": "pages-modlist-tools", "Application-Version": "0.1",
           "User-Agent": "pages-modlist-tools/0.1 (personal use)", "Accept": "application/json"}


def api_get(url: str, key: str) -> tuple[object, dict]:
    req = urllib.request.Request(url, headers={**HEADERS, "apikey": key})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8")), dict(r.headers)


def meta_text(mod_id: str, file_id: str, info: dict, url: str) -> str:
    return ("[General]\r\ngameName=skyrimse\r\n"
            f"modID={mod_id}\r\nfileID={file_id}\r\nurl=\"{url}\"\r\n"
            f"name={info.get('name', '')}\r\nversion={info.get('version', '')}\r\n"
            "installed=false\r\nuninstalled=false\r\npaused=false\r\nremoved=false\r\n")


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="限速下載 Nexus 檔案（需要 Premium 與 NEXUS_API_KEY）")
    ap.add_argument("--pm", type=Path, default=Path("D:/PM"))
    ap.add_argument("--manifest", type=Path, default=DEFAULT_REPORT_DIR / "manifest.csv")
    ap.add_argument("--limit", type=int, default=20, help="本次最多下載幾個檔案")
    ap.add_argument("--sleep", type=float, default=4.0, help="每個檔案之間等待秒數（最少 3）")
    ap.add_argument("--min-hourly", type=int, default=30, help="每小時額度低於此值就停止")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args(argv)
    rep = Report("nexus_fetch")
    key = os.environ.get("NEXUS_API_KEY", "").strip()
    todo = [r for r in read_csv(args.manifest)
            if r["action"] in ("download", "replace_dll") and r.get("nexus_mod_id") and r.get("nexus_file_id")]
    dl_dir = args.pm / "downloads"
    rows = []
    if not args.apply:
        for r in todo[: args.limit]:
            rows.append({"folder": r["folder"], "mod": r["nexus_mod_id"], "file": r["nexus_file_id"], "status": "planned"})
        rep.add("mode", "INFO", "試跑", f"待下載 {len(todo)} 個（含檔案 ID），本次上限 {args.limit}")
    elif not key:
        rep.add("key", "FAIL", "未設定 NEXUS_API_KEY", "在命令列先執行：set NEXUS_API_KEY=你的金鑰")
    else:
        dl_dir.mkdir(parents=True, exist_ok=True)
        done = 0
        for r in todo:
            if done >= args.limit:
                break
            mid, fid = r["nexus_mod_id"], r["nexus_file_id"]
            row = {"folder": r["folder"], "mod": mid, "file": fid}
            try:
                info, _ = api_get(f"{API}/mods/{mid}/files/{fid}.json", key)
                fname = info.get("file_name") or f"{mid}-{fid}.7z"
                dest = dl_dir / fname
                if dest.exists() and info.get("size_in_bytes") and dest.stat().st_size == int(info["size_in_bytes"]):
                    row["status"] = "already_downloaded"
                    rows.append(row)
                    continue
                links, hdr = api_get(f"{API}/mods/{mid}/files/{fid}/download_link.json", key)
                url = links[0]["URI"]
                tmp = dest.with_suffix(dest.suffix + ".part")
                req = urllib.request.Request(url, headers={"User-Agent": HEADERS["User-Agent"]})
                with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as fh:
                    while chunk := resp.read(1 << 20):
                        fh.write(chunk)
                tmp.replace(dest)
                page = f"https://www.nexusmods.com/skyrimspecialedition/mods/{mid}"
                (dl_dir / (fname + ".meta")).write_text(meta_text(mid, fid, info, page), encoding="utf-8")
                row["status"] = "downloaded"
                row["archive"] = fname
                done += 1
                remaining = int(hdr.get("x-rl-hourly-remaining") or hdr.get("X-RL-Hourly-Remaining") or 999)
                if remaining < args.min_hourly:
                    row["status"] += f" (hourly quota {remaining}, stopping)"
                    rows.append(row)
                    break
            except urllib.error.HTTPError as e:
                row["status"] = f"http_{e.code}"
                if e.code in (401, 403):
                    rows.append(row)
                    rep.add("auth", "FAIL", "Nexus 拒絕", f"HTTP {e.code}：金鑰無效或非 Premium")
                    break
                if e.code == 429:
                    rows.append(row)
                    rep.add("rate", "WARN", "達到速率上限", "請一小時後再執行")
                    break
            except (OSError, ValueError, KeyError, IndexError) as e:
                row["status"] = f"error: {e}"
            rows.append(row)
            time.sleep(max(3.0, args.sleep))
        rep.add("done", "PASS", "本次下載", f"{sum(1 for x in rows if str(x.get('status','')).startswith('downloaded'))} 個")
    write_csv(args.out / "nexus_fetch.csv", rows, ["folder", "mod", "file", "status", "archive"])
    path = rep.save(args.out, stem="nexus_fetch")
    print(rep.text())
    print(f"\n報告：{path}")
    return 0 if rep.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
