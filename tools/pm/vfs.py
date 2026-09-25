"""Approximate MO2's virtual Data folder for one profile (who provides which file).

模擬 MO2 虛擬 Data 資料夾：依設定檔優先順序找出每個插件或 DLL 由哪個 mod 提供。
The highest-priority enabled mod wins a conflict, as in MO2.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from . import mo2

PLUGIN_EXT = (".esp", ".esm", ".esl")
BASE_MASTERS = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]
GENERATED_PLUGINS = {"Synthesis.esp", "PGPatcher.esp", "PG_1.esp", "PG_2.esp", "DynDOLOD.esm",
                     "DynDOLOD.esp", "Occlusion.esp", "FNIS.esp"}


@dataclass
class Profile:
    pm_root: Path
    name: str
    mods_dir: Path
    profile_dir: Path
    game_dir: Path
    modlist: list[mo2.ModEntry] = field(default_factory=list)
    plugins: list[mo2.PluginEntry] = field(default_factory=list)

    @property
    def enabled_folders(self) -> list[str]:
        """Enabled, non-separator folders in priority order (highest first)."""
        return [e.name for e in self.modlist if e.enabled and not e.is_separator]


def open_profile(pm_root: Path, profile: str | None = None) -> Profile:
    paths = mo2.locate_instance(pm_root)
    profiles = mo2.list_profiles(paths["profiles"])
    if profile is None:
        if not profiles:
            raise FileNotFoundError(f"no profiles under {paths['profiles']}")
        profile = profiles[0]
    pdir = paths["profiles"] / profile
    game = Path(paths.get("game") or (Path(pm_root) / "STOCK GAME"))
    p = Profile(Path(pm_root), profile, paths["mods"], pdir, game)
    if (pdir / "modlist.txt").exists():
        p.modlist = mo2.read_modlist(pdir / "modlist.txt")
    if (pdir / "plugins.txt").exists():
        p.plugins = mo2.read_plugins(pdir / "plugins.txt")
    return p


def root_plugins(folder: Path) -> list[str]:
    out = []
    try:
        for e in os.scandir(folder):
            if e.is_file() and e.name.lower().endswith(PLUGIN_EXT):
                out.append(e.name)
    except OSError:
        pass
    return out


def plugin_providers(mods_dir: Path, folders_high_first: list[str], game_data: Path | None) -> dict[str, Path]:
    """Map lower-case plugin name -> winning file path."""
    prov: dict[str, Path] = {}
    for folder in folders_high_first:
        for name in root_plugins(mods_dir / folder):
            prov.setdefault(name.lower(), mods_dir / folder / name)
    if game_data and game_data.is_dir():
        for name in root_plugins(game_data):
            prov.setdefault(name.lower(), game_data / name)
    return prov


def skse_dll_providers(mods_dir: Path, folders_high_first: list[str]) -> dict[str, list[Path]]:
    """Map lower-case DLL name -> providing paths (index 0 wins)."""
    out: dict[str, list[Path]] = {}
    for folder in folders_high_first:
        base = mods_dir / folder
        sp = None
        for cand in ("SKSE/Plugins", "skse/plugins", "Skse/Plugins", "SKSE/plugins"):
            if (base / cand).is_dir():
                sp = base / cand
                break
        if sp is None:
            continue
        for d in sp.glob("*.dll"):
            out.setdefault(d.name.lower(), []).append(d)
    return out


def primary_plugins(game_dir: Path) -> list[str]:
    """Base masters + Creation Club plugins listed in Skyrim.ccc that exist in Data."""
    data = game_dir / "Data"
    present = {n.lower() for n in root_plugins(data)} if data.is_dir() else set()
    prim = [m for m in BASE_MASTERS if m.lower() in present or not present]
    ccc = game_dir / "Skyrim.ccc"
    if ccc.exists():
        for line in ccc.read_text(encoding="utf-8", errors="replace").splitlines():
            n = line.strip()
            if n and (n.lower() in present or not present):
                prim.append(n)
    return prim
