"""Uniform PASS/WARN/FAIL reports that the user uploads back after each phase.

統一的檢查報告格式（PASS／WARN／FAIL），每個階段結束後回傳給 Claude 判讀。
Reports never contain the Windows user name: home paths are replaced by %USERPROFILE%.
"""

from __future__ import annotations

import csv
import datetime as _dt
import json
import os
import platform
from dataclasses import asdict, dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = REPO_ROOT / "reports"

ICON = {"PASS": "[通過]", "WARN": "[注意]", "FAIL": "[失敗]", "INFO": "[資訊]"}


def scrub(text: str) -> str:
    home = os.path.expanduser("~")
    if home and home not in ("~", "/"):
        text = text.replace(home, "%USERPROFILE%")
    user = os.environ.get("USERNAME") or os.environ.get("USER")
    if user and len(user) > 2:
        text = text.replace(f"\\{user}\\", "\\%USERNAME%\\").replace(f"/{user}/", "/%USERNAME%/")
    return text


@dataclass
class Check:
    key: str
    status: str          # PASS / WARN / FAIL / INFO
    title: str           # Chinese, shown to the user
    detail: str = ""
    value: object = None


@dataclass
class Report:
    tool: str
    checks: list[Check] = field(default_factory=list)
    data: dict = field(default_factory=dict)
    created: str = field(default_factory=lambda: _dt.datetime.now().strftime("%Y-%m-%d %H:%M"))

    def add(self, key: str, status: str, title: str, detail: str = "", value: object = None) -> Check:
        c = Check(key, status, title, detail, value)
        self.checks.append(c)
        return c

    @property
    def worst(self) -> str:
        order = {"INFO": 0, "PASS": 1, "WARN": 2, "FAIL": 3}
        return max((c.status for c in self.checks), key=order.get, default="PASS")

    def text(self) -> str:
        lines = [f"== {self.tool} 報告 ({self.created}) ==",
                 f"系統：{platform.system()} {platform.release()}  Python {platform.python_version()}", ""]
        for c in self.checks:
            lines.append(f"{ICON.get(c.status, c.status)} {c.title}" + (f"：{c.detail}" if c.detail else ""))
        lines += ["", f"總結：{ICON.get(self.worst, self.worst)}"]
        return scrub("\n".join(lines))

    def save(self, out_dir: Path | None = None, stem: str | None = None) -> Path:
        out_dir = Path(out_dir or DEFAULT_REPORT_DIR)
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M")
        stem = stem or f"{self.tool}-{stamp}"
        payload = {"tool": self.tool, "created": self.created, "worst": self.worst,
                   "checks": [asdict(c) for c in self.checks], "data": self.data}
        (out_dir / f"{stem}.json").write_text(scrub(json.dumps(payload, ensure_ascii=False, indent=1,
                                                               default=str)), encoding="utf-8")
        (out_dir / f"{stem}.txt").write_text(self.text() + "\n", encoding="utf-8")
        return out_dir / f"{stem}.txt"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not fieldnames:
        fieldnames = list(rows[0].keys()) if rows else ["empty"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:   # BOM so Excel shows Chinese
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: scrub(str(v)) if isinstance(v, str) else v for k, v in r.items()})
    return path


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def stamp() -> str:
    return _dt.datetime.now().strftime("%Y%m%d-%H%M")
