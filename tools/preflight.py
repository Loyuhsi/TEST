"""Phase 1 laptop check: disk, GPU/VRAM, RAM, Steam Skyrim version/language, CC, runtimes.

第一階段：筆電環境檢查（磁碟、顯示卡、記憶體、Steam 版 Skyrim、CC、執行環境）。

Usage (Windows, from the repo folder):
    python tools\\preflight.py --install-drive D:
The report is written to reports\\preflight-<time>.txt/.json; upload both back.
Nothing on the system is changed.
"""

from __future__ import annotations

import argparse
import ctypes
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pm import fsutil, pe  # noqa: E402
from pm.report import Report  # noqa: E402

SKYRIM_APPID = "489830"
EXPECTED_STEAM_EXE = "1.7.104.0"          # current Steam build that Nolvus 3.8.11+ and MV 2.6.2 accept
EXPECTED_CC_PLUGINS = 74                  # all Anniversary Edition Creations
GB = 1024 ** 3
IS_WINDOWS = os.name == "nt"


# ------------------------------------------------------------------ VDF (Steam KeyValues)
def parse_vdf(text: str) -> dict:
    tokens = re.findall(r'"((?:\\.|[^"\\])*)"|([{}])', text)
    stack: list[dict] = [{}]
    key = None
    for quoted, brace in tokens:
        if brace == "{":
            new: dict = {}
            stack[-1][key] = new
            stack.append(new)
            key = None
        elif brace == "}":
            stack.pop()
            key = None
        elif key is None:
            key = quoted.replace("\\\\", "\\")
        else:
            stack[-1][key] = quoted.replace("\\\\", "\\")
            key = None
    return stack[0]


def find_skyrim(steam_path: Path) -> dict:
    """Return {'library', 'game_dir', 'manifest'} for Skyrim SE, or {}."""
    libs = [steam_path]
    lf = steam_path / "steamapps" / "libraryfolders.vdf"
    if lf.exists():
        data = parse_vdf(lf.read_text(encoding="utf-8", errors="replace"))
        for v in data.get("libraryfolders", {}).values():
            if isinstance(v, dict) and v.get("path"):
                libs.append(Path(v["path"]))
    for lib in libs:
        acf = lib / "steamapps" / f"appmanifest_{SKYRIM_APPID}.acf"
        if acf.exists():
            m = parse_vdf(acf.read_text(encoding="utf-8", errors="replace")).get("AppState", {})
            return {"library": lib, "manifest": m,
                    "game_dir": lib / "steamapps" / "common" / m.get("installdir", "Skyrim Special Edition")}
    return {}


# ------------------------------------------------------------------ Windows probes
def _reg(root_name: str, path: str, value: str):
    if not IS_WINDOWS:
        return None
    import winreg
    root = getattr(winreg, root_name)
    try:
        with winreg.OpenKey(root, path) as k:
            return winreg.QueryValueEx(k, value)[0]
    except OSError:
        return None


def probe_gpus() -> list[dict]:
    gpus: list[dict] = []
    if IS_WINDOWS:
        base = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        for i in range(16):
            sub = f"{base}\\{i:04d}"
            name = _reg("HKEY_LOCAL_MACHINE", sub, "DriverDesc")
            if not name:
                continue
            mem = _reg("HKEY_LOCAL_MACHINE", sub, "HardwareInformation.qwMemorySize")
            if mem is None:
                raw = _reg("HKEY_LOCAL_MACHINE", sub, "HardwareInformation.MemorySize")
                if isinstance(raw, bytes):
                    mem = int.from_bytes(raw[:8], "little")
                elif isinstance(raw, int):
                    mem = raw
            gpus.append({"name": name, "vram_gb": round((mem or 0) / GB, 1),
                         "driver": _reg("HKEY_LOCAL_MACHINE", sub, "DriverVersion") or ""})
    smi = shutil.which("nvidia-smi")
    if smi:
        try:
            out = subprocess.run([smi, "--query-gpu=name,memory.total,power.limit,driver_version",
                                  "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20).stdout
            for line in out.strip().splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 2:
                    gpus.append({"name": parts[0], "vram_gb": round(float(parts[1]) / 1024, 1),
                                 "power_limit_w": parts[2] if len(parts) > 2 else "",
                                 "driver": parts[3] if len(parts) > 3 else "", "source": "nvidia-smi"})
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
    return gpus


def probe_ram_gb() -> float | None:
    if not IS_WINDOWS:
        return None

    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    st = MEMORYSTATUSEX()
    st.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
        return round(st.ullTotalPhys / GB, 1)
    return None


def probe_display() -> dict:
    if not IS_WINDOWS:
        return {}
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        w = ctypes.windll.user32.GetSystemMetrics(0)
        h = ctypes.windll.user32.GetSystemMetrics(1)
        hdc = ctypes.windll.user32.GetDC(0)
        hz = ctypes.windll.gdi32.GetDeviceCaps(hdc, 116)
        ctypes.windll.user32.ReleaseDC(0, hdc)
        return {"width": w, "height": h, "refresh_hz": hz}
    except (AttributeError, OSError):
        return {}


def probe_fs_type(drive: str) -> str | None:
    if not IS_WINDOWS:
        return None
    buf = ctypes.create_unicode_buffer(64)
    root = drive.rstrip("\\/") + "\\"
    ok = ctypes.windll.kernel32.GetVolumeInformationW(ctypes.c_wchar_p(root), None, 0, None, None, None, buf, 64)
    return buf.value if ok else None


def probe_dotnet() -> list[str]:
    exe = shutil.which("dotnet")
    if not exe:
        return []
    try:
        out = subprocess.run([exe, "--list-runtimes"], capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    return [" ".join(line.split()[:2]) for line in out.splitlines() if line.strip()]


def probe_defender_exclusions() -> list[str] | None:
    if not IS_WINDOWS:
        return None
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-MpPreference).ExclusionPath"],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0 or "denied" in out.stderr.lower():
        return None
    return parse_exclusions(out.stdout)


def parse_exclusions(text: str) -> list[str] | None:
    """Exclusion paths, or None when Windows hides them from non-admin users.

    Without admin rights Get-MpPreference prints the placeholder
    'N/A: Must be an administrator to view exclusions' instead of the paths.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if any(line.upper().startswith("N/A") or "administrator" in line.lower() for line in lines):
        return None
    return lines


def gather(install_drive: str) -> dict:
    facts: dict = {"windows": IS_WINDOWS, "install_drive": install_drive}
    facts["cpu"] = _reg("HKEY_LOCAL_MACHINE", r"HARDWARE\DESCRIPTION\System\CentralProcessor\0",
                        "ProcessorNameString")
    facts["gpus"] = probe_gpus()
    facts["ram_gb"] = probe_ram_gb()
    facts["display"] = probe_display()
    facts["pagefile"] = _reg("HKEY_LOCAL_MACHINE",
                             r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "PagingFiles")
    drives = {}
    letters = "CDEFGHIJ" if IS_WINDOWS else ""
    for letter in letters:
        root = f"{letter}:\\"
        if os.path.exists(root):
            try:
                u = shutil.disk_usage(root)
                drives[f"{letter}:"] = {"free_gb": round(u.free / GB), "total_gb": round(u.total / GB),
                                        "fs": probe_fs_type(root)}
            except OSError:
                pass
    facts["drives"] = drives
    steam = _reg("HKEY_CURRENT_USER", r"Software\Valve\Steam", "SteamPath")
    facts["steam_language"] = _reg("HKEY_CURRENT_USER", r"Software\Valve\Steam", "Language")
    sk = find_skyrim(Path(steam)) if steam else {}
    if sk:
        gd = Path(sk["game_dir"])
        facts["skyrim_dir"] = str(gd)
        facts["skyrim_exe_version"] = pe.file_version(gd / "SkyrimSE.exe")
        m = sk["manifest"]
        facts["skyrim_buildid"] = m.get("buildid")
        facts["skyrim_language"] = (m.get("UserConfig") or {}).get("language")
        facts["skyrim_auto_update"] = m.get("AutoUpdateBehavior")
        data = gd / "Data"
        facts["cc_plugins"] = len([p for p in data.glob("cc*.es[lm]")]) if data.is_dir() else 0
        facts["skyrim_ccc"] = (gd / "Skyrim.ccc").exists()
        facts["skyrim_drive"] = gd.drive
    facts["vcredist_x64"] = _reg("HKEY_LOCAL_MACHINE", r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
                                 "Version")
    facts["dotnet"] = probe_dotnet()
    facts["defender_exclusions"] = probe_defender_exclusions()
    local = os.environ.get("LOCALAPPDATA")
    facts["global_mo2_instance"] = bool(local and (Path(local) / "ModOrganizer").exists())
    facts["python"] = sys.version.split()[0]
    return facts


# ------------------------------------------------------------------ evaluation (pure, tested)
def evaluate(f: dict) -> Report:
    r = Report("preflight")
    r.data = f
    if not f.get("windows"):
        r.add("os", "WARN", "不是 Windows 環境", "此工具需在筆電的 Windows 上執行")

    gpus = f.get("gpus") or []
    vram = max((g.get("vram_gb") or 0 for g in gpus), default=0)
    names = ", ".join(sorted({g["name"] for g in gpus})) or "未偵測到"
    if vram >= 16:
        r.add("gpu", "PASS", "顯示卡 VRAM", f"{names}（{vram} GB）→ Tier A/S，可跑完整清單", vram)
    elif vram >= 14:
        r.add("gpu", "PASS", "顯示卡 VRAM", f"{names}（{vram} GB）→ 達 Nolvus Ultimate 最低需求，需降部分 4K 材質", vram)
    elif vram >= 12:
        r.add("gpu", "WARN", "顯示卡 VRAM", f"{names}（{vram} GB）→ Tier B，需 VRAMr、2K 材質、較輕的草", vram)
    elif vram > 0:
        r.add("gpu", "FAIL", "顯示卡 VRAM", f"{names}（{vram} GB）→ 不建議完整清單，請回報以改用 Redux 路線", vram)
    else:
        r.add("gpu", "WARN", "顯示卡 VRAM", "無法偵測，請手動回報顯示卡型號與 VRAM")

    ram = f.get("ram_gb")
    if ram is None:
        r.add("ram", "WARN", "記憶體", "無法偵測")
    elif ram >= 31:
        r.add("ram", "PASS", "記憶體", f"{ram} GB", ram)
    elif ram >= 15:
        r.add("ram", "WARN", "記憶體", f"{ram} GB：請把分頁檔設為 20–40 GB（M&V 建議 32 GB）", ram)
    else:
        r.add("ram", "FAIL", "記憶體", f"{ram} GB：不足 16 GB", ram)

    pf = f.get("pagefile")
    pf_text = " / ".join(pf) if isinstance(pf, (list, tuple)) else str(pf or "")
    sized = re.findall(r"pagefile\.sys\s+(\d+)\s+(\d+)", pf_text, re.I)
    if sized and max(int(b) for _a, b in sized) >= 20000:
        r.add("pagefile", "PASS", "分頁檔", pf_text)
    else:
        r.add("pagefile", "WARN", "分頁檔", (pf_text or "未知") + "：建議手動設定 20480–40960 MB（見 docs/01）")

    drive = (f.get("install_drive") or "D:").upper().rstrip("\\/")
    d = (f.get("drives") or {}).get(drive)
    if not d:
        r.add("disk", "FAIL" if f.get("windows") else "WARN", f"安裝磁碟 {drive}", "找不到這個磁碟")
    else:
        free = d["free_gb"]
        status = "PASS" if free >= 700 else ("WARN" if free >= 620 else "FAIL")
        detail = f"剩餘 {free} GB / 共 {d['total_gb']} GB，檔案系統 {d.get('fs') or '?'}"
        if status != "PASS":
            detail += "（M&V 安裝＋下載需約 616 GB，另需 40–60 GB 餘裕）"
        r.add("disk", status, f"安裝磁碟 {drive}", detail, free)
        if d.get("fs") and d["fs"].upper() != "NTFS":
            r.add("disk_fs", "FAIL", "檔案系統", f"{drive} 是 {d['fs']}，硬連結需要 NTFS")

    if not f.get("skyrim_dir"):
        r.add("skyrim", "FAIL" if f.get("windows") else "WARN", "Steam 版 Skyrim SE", "找不到 Steam 安裝（需要 Steam 版，GOG 不適用）")
    else:
        ver = f.get("skyrim_exe_version") or "?"
        r.add("skyrim_ver", "PASS" if ver == EXPECTED_STEAM_EXE else "WARN", "Skyrim 版本",
              f"{ver}（預期 {EXPECTED_STEAM_EXE}；Nolvus Dashboard 3.8.11+ 與 M&V 2.6.2 皆以此為準）", ver)
        cc = f.get("cc_plugins", 0)
        r.add("cc", "PASS" if cc >= EXPECTED_CC_PLUGINS else "WARN", "Creation Club 內容",
              f"{cc} 個 CC 插件（完整 AE 為 {EXPECTED_CC_PLUGINS}）" +
              ("" if cc >= EXPECTED_CC_PLUGINS else "：請在遊戲主選單 Creations 下載全部內容"), cc)
        lang = (f.get("skyrim_language") or f.get("steam_language") or "").lower()
        r.add("lang", "PASS" if lang in ("english", "") else "FAIL", "Steam 遊戲語言",
              (lang or "未指定（沿用 Steam 介面語言）") +
              ("" if lang in ("english", "") else "：安裝 Nolvus 與 M&V 前請改成 English"))
        if f.get("skyrim_auto_update") not in ("1", 1):
            r.add("autoupdate", "WARN", "Steam 自動更新", "建議設為「僅在啟動時更新」，避免安裝途中遊戲被更新")

    if not f.get("vcredist_x64"):
        r.add("vcredist", "WARN", "Visual C++ 2015–2022 x64", "未偵測到，請安裝")
    else:
        r.add("vcredist", "PASS", "Visual C++ 2015–2022 x64", str(f["vcredist_x64"]))
    rt = " ".join(f.get("dotnet") or [])
    for major in ("6", "8"):
        ok = re.search(rf"Microsoft\.WindowsDesktop\.App {major}\.", rt)
        r.add(f"dotnet{major}", "PASS" if ok else "WARN", f".NET {major} Desktop Runtime",
              "已安裝" if ok else "未偵測到，請安裝（Wabbajack／Synthesis 需要）")
    ex = f.get("defender_exclusions")
    if ex is None:
        r.add("defender", "INFO", "Windows Defender 排除", "一般權限看不到排除清單；以系統管理員執行 preflight 才能檢查，或依 docs/01 手動確認")
    else:
        need = [p for p in (f"{drive}\\MV", f"{drive}\\Nolvus", f"{drive}\\PM")
                if not any(e.lower().rstrip("\\") == p.lower() for e in ex)]
        r.add("defender", "PASS" if not need else "WARN", "Windows Defender 排除",
              "已設定" if not need else "尚未排除：" + ", ".join(need))
    if f.get("global_mo2_instance"):
        r.add("mo2global", "WARN", "MO2 全域實例", "%LOCALAPPDATA%\\ModOrganizer 已存在，Nolvus 安裝前建議先移除或改名")
    disp = f.get("display") or {}
    if disp:
        r.add("display", "INFO", "螢幕", f"{disp.get('width')}x{disp.get('height')} @ {disp.get('refresh_hz')} Hz")
    if f.get("cpu"):
        r.add("cpu", "INFO", "CPU", str(f["cpu"]).strip())
    return r


def main(argv=None) -> int:
    fsutil.enable_utf8_console()
    ap = argparse.ArgumentParser(description="第一階段筆電環境檢查（不會修改系統）")
    ap.add_argument("--install-drive", default="D:", help="安裝用磁碟，預設 D:")
    ap.add_argument("--out", type=Path, default=None, help="報告資料夾，預設 reports/")
    args = ap.parse_args(argv)
    report = evaluate(gather(args.install_drive))
    path = report.save(args.out)
    print(report.text())
    print(f"\n報告已存到：{path}（請把 .txt 與 .json 一起回傳）")
    return 0 if report.worst != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
