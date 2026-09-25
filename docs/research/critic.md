# critic

## SUMMARY
Completeness critique of the 8 research results.

**Contradictions, and how I resolved them.** Each has a primary-source or local check.
1. **Mages & Vikings (MV) runtime.** zh_community and provenance say MV runs 1.5.97 or Best of Both Worlds (BOBW). That is wrong for MV 2.6.2. The MV CHANGELOG (v2.5, line 206) says the list moved from 1.5.97 to 1.6.1170, and the validation report lists SKSE 2.2.8, Engine Fixes for 1.6.1170+, and '1.6.1170 Missing Files'. The last 1.5.97 release was MV 2.40.1 (Nexus file 703199, dated 2025-12-29).
2. **Target's Nolvus base.** Provenance's '6.0.18' is a matching error. The target's hair folders ('Vanilla hair remake SMP', 'Vanilla hair - Salt and Wind') are MV folder names. The mods Nolvus added in 6.0.18 are named 'Vanilla Hair Remake - SMP/Patches/Addon' and none of them are in the target. So the base is about 6.0.17.
3. **Target's MV content.** It dates from the MV 2.5.x era: the target has MV 2.5 additions (True Flasks NG, HorsePower, Knockback SKSE) and 9 of the 35 mods MV 2.6 removed. So even the target's MV DLLs were originally 1.6.1170 builds.
4. **Community Shaders (CS) build.** The file 'CommunityShaders_AIO-2026-05-28T17-09Z.7z' exists as a Wabbajack authored file in the Kirbylite list report. It is described as Jiaye's CS fork, not an official release.
5. **STPP-NG version.** 1.10 is the current MAIN file (2026-08-24); 1.9 is from 2026-08-14.
6. **RAM.** The Nolvus v6 requirement tables give no RAM figure; zh_tooling's '32 GB for v6' is wrong. MV's README recommends 32 GB.
7. **Nolvus variant.** The recommendations conflict (Ultimate vs Redux). The target disables about 730 of Nolvus's world and visual rows and replaces them with MV plus PBR, so the Nolvus variant does not set the target's VRAM load.

**Critical gaps the research left open.**
- **Who executes.** This session is a remote Linux container. It cannot run the Dashboard or Wabbajack, or log into Nexus, on the user's laptop.
- **Disk.** Installing both base lists in full peaks at about 1.05 TB of SSD, plus about 420 GB of archives on a secondary drive.
- **Time.** About 423 GB of downloads (roughly 9 h at 100 Mbps), plus hours of tool runs to regenerate outputs.
- **Plugin slots.** There are about 27 free, so the translation must add no plugins. Use Dynamic String Distributor (DSD) or JSON overrides only.
- **Missing masters.** Nolvus 6.0.20 patch plugins may depend on 6.0.18–6.0.20 mods that the target lacks.
- **Version timing.** If Nolvus 6.0.21 leaves beta before the install, 55 target mods lose their source.
- **Licences.** Personal use only for 蘇禾 and 和光. Do not download the pirated full-list folders. Patreon-paid mods need the user to pay.
- **Saves.** Every path needs a new game.
- **Freeze and backup.** No freeze, backup or update strategy was defined.
- **Cannot be reproduced exactly:** CustomFixes1, overwrite2, the eight [FIX] plugins, exact mod versions, and all generated outputs.

## FACTS
- [high] Mages & Vikings 2.6.2 runs on SkyrimSE 1.6.1170, not 1.5.97 or BOBW. The CHANGELOG v2.5 says 'The list has been updated from version 1.5.97 to version 1.6.1170'. The Wabbajack validation report lists SKSE Steam 2.2.8, Engine Fixes AIO for 1.6.1170 and newer, Address Library AIO (1.7.99.0) v12, PrivateProfileRedirector AE (RT 1.6.1170) and 1.6.1170 Missing Files. The zh_community and provenance claims ('MV = 1.5.97 + BOBW') are outdated; they describe MV before v2.5. (https://raw.githubusercontent.com/nicolasbertolino/MagesAndVikings/main/CHANGELOG.md (line 206) ; https://raw.githubusercontent.com/wabbajack-tools/mod-lists/master/reports/MagesAndVikings/MagesAndVikings/status.md)
- [high] On Nexus 136238, the MV .wabbajack file history shows 2.40.1 (file 703199, 2025-12-29) as the last 1.5.97-era build. 2.5 followed on 2026-03-14 and 2.5.1 (file 731790) on 2026-03-15; both are 1.6.1170. 2.6.2 (MAIN 800961) is from 2026-09-05. The older files are ARCHIVED but still listed. Their embedded modlist JSON can serve as a lookup table of Nexus file IDs. They probably cannot be installed as-is, because their game-file hashes predate Steam 1.7.104 (inference). (Nexus GraphQL modFiles(modId 136238, gameId 1704) queried 2026-09-25)
- [high] The target's Nolvus base is about 6.0.17, not 6.0.18. The 6.0.18 changelog's 'Added new mod' entries are 'Vanilla Hair Remake - SMP' (1.0.3), 'Vanilla Hair Remake - Patches' (3.4) and 'Vanilla Hair Remake - Addon' (3.4); none are in the target. The target's 'Vanilla hair remake SMP', 'Vanilla hair - Salt and Wind' and 'Vanilla Hair Remake - High Poly Head - Expressive Facegen Morphs - Patches' (lines 2669-2671) are exact MV folder names (MV snapshot lines 1536-1538). Provenance's 2/7 match was a normalization false positive. (https://www.nolvus.net/appendix/history ; local user__modlist.txt lines 2669-2671 ; local mages-vikings__modlist.txt lines 1536-1538)
- [medium] The target's MV content dates from the MV 2.5.x era. It contains MV 2.5 additions: True Flasks NG, Knockback SKSE, HorsePower, and the Stuck Underwater fix. It also contains 9 of the 35 mods MV 2.6 removed: Parrying RPG, One Click Power Attack NG, True Flasks NG, Simple Hunting Overhaul, Madmen, STB Widgets, STB Active Effects, Relationship Dialogue Overhaul and New Creature Animation - Werewolf. An MV 2.6.2 install will not supply those 9. Because MV 2.5 was already 1.6.1170, the target's author must have swapped their DLLs to 1.5.97 builds. (local analysis: substring match of the MV CHANGELOG Added/Removed lists (v2.3–v2.6) against user__modlist.txt)
- [high] The target's exact CS build, CommunityShaders_AIO-2026-05-28T17-09Z.7z, is a Wabbajack authored file listed in the Kirbylite Modlist validation report (repo folder 'SkyrimKIRBYKINGSNSFWEditionModlist'). It is not an official CS GitHub or Nexus release. NAT.CS III preset pages call the 05/28/2026 build 'Jiaye's CS'. CS support covers official builds only. (https://raw.githubusercontent.com/wabbajack-tools/mod-lists/master/reports/SkyrimKIRBYKINGSNSFWEditionModlist/KirbyliteModlist/status.md (line 272: https://authored-files.wabbajack.org/CommunityShaders_AIO-2026-05-28T17-09Z.7z_d43cd921-b790-47d8-b108-f0d89e1f56b4))
- [high] Scaleform Translation Plus Plus NG version history: 1.10 is MAIN (2026-08-24); 1.9 (2026-08-14, UTF-16 fix) and 1.8 (2024-02-28) are OLD_VERSION. The official Nolvus list ships 1.6. zh_community's 'v1.9 2026-08-24' is wrong. (Nexus GraphQL modFiles(modId 77359) ; https://www.nolvus.net/awakening)
- [high] The Nolvus v6 requirement tables give no RAM figure; 32 GB appears only in the v5 tables. zh_tooling's '32 GB RAM for v6 Ultra' is wrong. MV's README recommends 32 GB. Nolvus advises a 20–40 GB pagefile, especially with 16 GB RAM. (https://www.nolvus.net/appendix/installer/requirements ; https://www.nolvus.net/appendix/pagefile ; https://raw.githubusercontent.com/nicolasbertolino/MagesAndVikings/main/README.md)
- [medium] The target's world and visual layer comes from MV plus PBR, CS and Lux, not from the Nolvus variant. About 730 Nolvus rows are absent: trees, grass, weathers, cities, towns, interiors, lighting and ENB. So picking Nolvus Redux instead of Ultimate cuts VRAM much less for the target than the Nolvus tables suggest. The target's weight is MV's visual stack plus 81 PBR entries plus Freak's Floral Fields plus about 14 mods at 4K or above. (provenance result (nolvus.net/awakening option evaluation vs user__modlist.txt) ; perf result (81 PBR entries))
- [high] Plugin headroom is about 27 slots. The target has 4,244 plugins plus 79 implicit primaries (5 base masters and 74 Creation Club), giving 4,323 against a hard cap of 254 full + 4,096 light = 4,350. The Chinese layer therefore cannot add translation ESPs. It must use DSD JSON or loose-file overrides, or replace plugins in place under the same filename. (runtime and merge results (local counts) ; https://dyndolod.info/Messages/Plugin-Limit)
- [medium] Disk arithmetic (my calculation from verified figures):
- Steam game files: about 21 GB (MV's 178 game-file archives total 20.76 GB).
- Nolvus Ultimate: 426 GB installed, plus 193 GB of optional archives.
- MV 2.6.2: 386 GB installed, 230 GB of downloads, and a 5.4 GB .wabbajack file.
- Pagefile: 20–40 GB. Wabbajack also asks for 40–60 GB of spare space.
With both lists fully installed and archives and downloads on a secondary drive, peak SSD use is about 21 + 426 + 386 + 5 + 40 + 50 ≈ 0.93 TB. Adding the hybrid's new mods and outputs (unmeasured) brings it to about 1.0–1.1 TB. Keeping archives and downloads on the SSD adds about 423 GB, for roughly 1.5 TB. (https://www.nolvus.net/appendix/installer/requirements ; https://raw.githubusercontent.com/nicolasbertolino/MagesAndVikings/main/modlists.json ; https://wiki.wabbajack.org/user_documentation/Installing%20a%20Modlist.html ; mv result (GameFileSource 20.76 GB))
- [medium] Download time (my calculation) for 193 + 230 = 423 GB of archives: about 9.4 h at 100 Mbps, 3.1 h at 300 Mbps and 0.9 h at 1 Gbps, before per-file overhead and extraction. Nolvus says its install takes about 1 h with Premium and a good connection. NGIO grass precache takes 30 min to 2.5 h on heavy lists. The MV Wabbajack install time and the DynDOLOD, PGPatcher and Synthesis times on a 4,000-mod list were not found in primary sources. (arithmetic ; https://www.nolvus.net/appendix/installer/install ; https://www.nexusmods.com/skyrimspecialedition/mods/42161)
- [medium] The Chinese community packs line up with what the user will actually install. 蘇禾's packs cover Nolvus 6.0.20 (Redux DSD v2.2, and Ultimate without SR Exterior Cities DSD v1.2), which is the version the Dashboard currently installs, not the target's 6.0.17. The MV pack is for 2.5.1, which matches the target's MV era rather than MV 2.6.2. The packs are Simplified Chinese, partly AI-translated, and licensed for personal use only; the same share also re-hosts full English modlists that must not be downloaded. (zh_community result (Quark share bbf3491d44b2 listing; https://www.bilibili.com/video/BV116rrBhEjF/))
- [high] Nolvus official customization rules: never rename, delete or move installer mods. The unofficial French v5 manual-guide page says no support is given for modified installs. The Wabbajack install rules say lists can't be merged into one folder. The hybrid is therefore unsupported by both Nolvus and MV support channels. (https://www.nolvus.net/appendix/installer/customization ; https://wiki.wabbajack.org/user_documentation/Installing%20a%20Modlist.html)
- [medium] Save compatibility: MV 2.6 is marked 'New Game Required', Nolvus 6.0.15 required a new game and new install, and the hybrid changes masters. Every path therefore needs a new game. A DSD- or loose-file-based translation layer changes no plugins, so updating it mid-playthrough should not break saves (inference). (https://raw.githubusercontent.com/nicolasbertolino/MagesAndVikings/main/CHANGELOG.md ; https://www.nolvus.net/appendix/history ; https://moddingforge.com/docs/dsd)
- [low] Nolvus-authored patch plugins at 6.0.20 (Consistency, Leveled List, Armors and Clothes patches, etc.) were built with 6.0.18–6.0.20 content present. The target had 0/7 of the 6.0.19 additions and 0/28 of the 6.0.20 additions. Disabling those mods to match the target may leave 6.0.20 Nolvus patch plugins with missing masters. This is untested and needs a masters check after install. (inference from https://www.nolvus.net/appendix/history and the nolvus and provenance results)
- [medium] The Dashboard installs the current package only; no UI for choosing an older one was found. The nolvus.net list page already shows 6.0.21 rows, and a video calls 6.0.21 '(Beta)'. If 6.0.21 goes live before installation, 55 target mods present in 6.0.20 (Wet and Cold, Footprints, At Your Own Pace, iWant Widgets, and others) will not be installed. (https://www.nolvus.net/awakening ; https://www.nolvus.net/appendix/history ; nolvus and provenance results)
- [medium] The official Skyrim SE Chinese text is Traditional Chinese: Steam lists 'Traditional Chinese' as text only, and no Simplified. MV's rebuilt Interface.bsa contains *_chinese strings for the base game and DLC, plus fonts_cn.swf and fontconfig_cn.txt. Whether the Nolvus 1.5.97 STOCK GAME Interface.bsa also contains them has not been verified. (https://store.steampowered.com/api/appdetails?appids=489830 ; mv result (range-read of MV .wabbajack))
- [high] This session runs in a remote Linux container. It cannot run the Nolvus Dashboard, Wabbajack or MO2 on the user's Windows laptop, and it cannot use the user's Nexus login. Execution must be done by the user from checklists and scripts produced here, or through a computer-use or Remote Control link if one is available. (session environment (Platform: linux; scratchpad-only file access))

## RISKS
- EXECUTION GAP: no plan can have Claude 'download for you' on the laptop. Every install step needs the user, or a linked computer-use or Remote Control session. The plan must spell out who does each step and what gets reported back after each phase (screenshots, log files, a folder listing).
- DISK: installing both base lists in full peaks at about 1.0–1.1 TB of NVMe, plus about 0.42 TB of archives and downloads. That exceeds most laptop SSDs. Hardlink-based assembly needs all instances on one NTFS volume. Without an external drive or a lean path (below), the user's stated approach ('install both first') may simply not fit.
- WASTE: the target uses only about 880 of MV's 3,694 folders. A full MV install is roughly 616 GB of I/O to harvest those. On the other hand, about 60,600 MV directives are PatchedFromArchive, so MV-installed files can differ from raw Nexus downloads. A lean alternative (download only the needed files by ID from the .wabbajack JSON) loses those patched files.
- RUNTIME: the hybrid runs 1.5.97 (Nolvus STOCK GAME), while both MV 2.6.2 and the MV 2.5-era content in the target were built for 1.6.1170. Every SKSE DLL taken from MV must be replaced with a 1.5.97 or multi-runtime build, or dropped. The MV 2.40.1 .wabbajack JSON (the last 1.5.97 build) is the best lookup table for the matching file IDs.
- VERSION DRIFT: the Dashboard gives Nolvus 6.0.20 (or 6.0.21 if it leaves beta), not the target's 6.0.17, and Wabbajack gives MV 2.6.2, not 2.5.x. Nine target mods removed in MV 2.6 and 55 mods removed in Nolvus 6.0.21 must then be fetched separately. Nolvus 6.0.20 patches may need masters that the target disables. The result is 'target-inspired', not identical.
- PLUGIN CAP: only about 27 free slots. Any translation, compatibility or 'fix' plugin added beyond that breaks the game. The translation layer must add no plugins, and ESL-flagging changes must be checked in xEdit.
- UNREPRODUCIBLE ITEMS: CustomFixes1, overwrite2 and the eight [FIX]*.esp plugins; YXZ_NRoad PBR DGS.esp edits; exact mod file versions (no meta.ini); all generated outputs (Pandora, Synthesis, PGPatcher, TexGen/DynDOLOD, grass cache, BodySlide); and the Jiaye CS build unless fetched from the Wabbajack authored-file CDN. Regenerated outputs will differ from the author's.
- CS BUILD: the target's CS is Jiaye's experimental fork build (Kirbylite authored file), not an official release, so CS support won't help. Moving to official CS 1.9.1 changes behaviour, and NAT.CS III, Lux CS and Upscaling 1.4.0 were validated on the 1.6-era build.
- LEGAL/ToS: Nexus ToS bans bulk scraping or bots, so throttle any script and prefer MO2/Wabbajack downloads. The Nolvus/mega/Google Drive files need the user's own accounts. The 蘇禾 and 和光 translations are personal use only, and the share's '纯净本体-英文' full-list mirrors and re-hosted Nexus files are piracy and malware risks. Patreon-tier mods (Smooth Grapple and others) must be paid for or dropped. The translated hybrid must never be redistributed, even as a private .wabbajack shared with others.
- LANGUAGE ORDER: Nolvus requires the Dashboard language to equal the Steam language, which has no Chinese option, and MV requires Steam set to English. A Taiwan user with Steam set to Traditional Chinese must switch Steam to English before both installs, and switch the in-game language only afterwards, via sLanguage in the MO2 profile INI. Unverified: whether the 1.5.97 executable automatically picks up the official CN fontconfig. Japanese reports suggest it does not, so an explicit CJK fontconfig is needed.
- SIMPLIFIED vs TRADITIONAL: most packs (蘇禾, 和光, SSE-AT output) are Simplified, and SSE-AT's scraper cannot find translations tagged 'Traditional Chinese'. Nouns are mixed across the official, 大學, 和光 and ANK translations. Without an OpenCC s2twp pass plus a pinned glossary, the game will show inconsistent names.
- UPDATE HAZARDS: pressing Nolvus Update or running a Wabbajack update on the source instances rewrites their profiles and deletes or recreates mod folders. A Steam update can break the Wabbajack or Nolvus hash checks before install. There is no freeze or backup plan yet.
- HARDWARE: most laptop GPUs are 8–12 GB. The Nolvus Ultimate minimum is 14 GB at 1080p and MV recommends a desktop-class RTX 4070 plus 32 GB RAM. On 8 GB, the full target is not realistic. Thermals and power limits during multi-hour DynDOLOD, NGIO, PGPatcher and VRAMr runs are also a risk.
- WIP SOURCE: the target is someone's 'WIP' list with only modlist.txt and plugins.txt. There is no evidence it boots or is stable, so reproducing it faithfully may reproduce its bugs.
- KIRBYLITE: the third-source list that shares the CS build is an NSFW-edition list. Treat it as a lookup source for file identities only.

## RECS
- PHASE 0 – Decide and inventory (no downloads).
- Goal: answer the user questions below and record the laptop's specs (dxdiag, DirectX VRAM, free space on each drive, panel refresh rate, MUX).
- Pick a fidelity mode: (A) faithful 1.5.97 + CS + all 4,044 mods, or (B) a laptop-tuned build inspired by the target.
- Pick a disk layout: full install of both lists, or the lean path.
- Pick a translation canon: official Traditional nouns, or 和光/ANK converted to Traditional.
- Exit criteria: written decisions; confirmed ≥1 TB on one NTFS SSD volume (or a lean path chosen); confirmed which Nolvus package (6.0.20 vs 6.0.21 beta) the Dashboard currently offers.
- PHASE 1 – Prepare the machine.
- Steam Skyrim SE plus the Anniversary Upgrade at 1.7.104, all Creation Club content downloaded from the in-game menu, language ENGLISH, overlay off, 'only update when launched'.
- Install VC++, .NET 6 and .NET 8.
- Pagefile 20–40 GB on the SSD.
- Delete %LOCALAPPDATA%\ModOrganizer if it exists.
- Add Defender exclusions and disable the Killer Prioritization Engine if present.
- Create a Nolvus account and a free mega.nz account.
- Folders: D:\Nolvus, D:\MV and D:\PM on one NTFS volume; archives and downloads on a secondary drive.
- Exit criteria: vanilla game launches once from Steam; all accounts ready; free space verified.
- PHASE 2 – Install Nolvus v6 with Dashboard 3.8.11 or later.
- Use the options implied by the target: no SREX, Edge UI, 16:9, BodySlide Dressed, TAA, True Nord, and the addons Fantasy Combat, Boss Encounter, Alternate Leveling, Gore, Exhaustion, Enemies Resistance and Stances.
- Variant: Ultimate if VRAM is 14 GB or more; otherwise decide deliberately. Redux changes texture folders and removes the Ultimate-only rows the target uses.
- The ENB choice doesn't matter, because ENB will be removed.
- Install promptly while 6.0.20 is current.
- Exit criteria: boots to the main menu in English; STOCK GAME SkyrimSE.exe is 1.5.97; skse64.log is clean; a Manage > Report PDF and a zipped copy of the profile folder are saved.
- PHASE 3 – Install MV 2.6.2 via the Wabbajack 4.2.3 gallery into D:\MV, with downloads on the secondary drive.
- The alternative lean path: read the .wabbajack 'modlist' JSON and fetch only the needed MV files by mod/file ID. This accepts the loss of Wabbajack-patched files.
- Also fetch the ARCHIVED MV 2.40.1 .wabbajack (Nexus file 703199) purely as a 1.5.97 file-ID lookup table.
- Exit criteria: MV boots to the menu, or the lean manifest is complete; the folder → Nexus modId/fileId table is exported.
- PHASE 4 – Build the provenance manifest with read-only scripts.
1. Match the target's folder names exactly against the installed Nolvus and MV mods folders. Do not use normalized matching, which produced false positives such as 'Vanilla hair'.
2. Classify each folder as Nolvus, MV, both, public Nexus, non-Nexus/Patreon, generated, or custom.
3. Audit every SKSE DLL for 1.5.97 compatibility.
4. Identify the roughly 470–550 unknown mods: throttled Nexus GraphQL searches, the MV 2.40.1/2.5.1 JSONs, Kirbylite, and LOL snapshots of Bread, LoreRim, Apostasy and Gate to Sovngarde.
5. List the 9 MV 2.6-removed mods and the 55 mods Nolvus drops in 6.0.21.
- Exit criteria: a CSV mapping every target folder to a source, fileId, version and action, with a list of what can't be obtained. The user approves the paid and dropped items.
- PHASE 5 – Assemble the hybrid in a new portable MO2 at D:\PM.
- Hardlink-clone mod folders; make real copies of meta.ini and any file you will edit.
- Before the first MO2 launch, create placeholder folders for every entry, or MO2 will silently drop those lines.
- Keep backups of modlist.txt and plugins.txt.
- Use Nolvus's 1.5.97 STOCK GAME with d3d11.dll, d3dcompiler_46e.dll, d3dcompiler_47.dll and the enb* files removed.
- Choose the CS build: the Jiaye authored file, or official 1.9.1 plus a retest.
- Download the missing mods through MO2 with Premium.
- Exit criteria: all 4,044 folders present; no missing masters (checked in xEdit); 254 or fewer full plugins and 4,096 or fewer light; skse64.log shows every DLL loaded; the game reaches the main menu.
- PHASE 6 – Regenerate outputs and validate in English.
- Disable the old Nolvus and MV outputs, then run in order: Pandora (-o), BodySlide (output path), Synthesis, PGPatcher, NGIO precache (iMinGrassSize=60 for Freak's Floral Fields), xLODGen terrain, TexGen, DynDOLOD, and optionally VRAMr. Let CS build its shader cache.
- Exit criteria: a new game passes a 30–60 minute fixed test route (Whiterun, Riverwood forest, Solitude, a Freak's Floral Fields meadow) without a crash to desktop. VRAM stays under budget in the SSE Display Tweaks on-screen display. Freeze the build as 'EN-baseline' with a backup.
- PHASE 7 – Chinese layer: no new plugins, applied after the English baseline.
1. Set sLanguage=CHINESE in the profile INI and verify official Traditional vanilla text.
2. Add a CJK font (subset) and a fontconfig that wins over Sanguis and Edge UI; also cover the ImGui mods (Wheeler, Dialogue History, PhotoMode, SkyPrompt 2.3.13 or later).
3. Update STPP-NG to 1.10 and add DSD 1.4.3.
4. Layer the community packs: 蘇禾 Nolvus 6.0.20 DSD for the chosen variant, and the MV 2.5.1 DSD after diffing its 'Other' pack files. Add native Traditional Nexus translations by hand, including Vagrant999's Vigilant, Unslaad and Apostasy translations.
5. Run an SSE-AT scan and build.
6. Convert with OpenCC s2twp plus a noun glossary.
7. Translate what remains to Traditional (DeepL ZH-HANT or an LLM), using xTranslator 1.7.2 or PX Translator.
- Exit criteria: a report of untranslated strings; no boxes, '?' or raw $KEYs across a UI checklist; the plugin count is unchanged.
- PHASE 8 – Laptop tuning and acceptance.
- Plugged in, Best performance power mode, MUX set to discrete GPU, High-performance GPU preference for the Stock Game exe, NVIDIA 'Prefer maximum performance', Windows scaling at 100%.
- CS Upscaling (DLSS or FSR) with FSR frame generation, borderless at 120 Hz or more, with an SSE Display Tweaks frame cap.
- On 12 GB or less, texture reductions: 2K swaps, Faultier's PBR 2k/1k, VRAMr, Freak's Floral Meadows.
- Exit criteria: agreed FPS target (e.g. 50–60 fps) on the test route, a stable 2-hour session and acceptable temperatures.
- PHASE 9 – Freeze, back up and maintain.
- Never press Nolvus Update or run a Wabbajack update on the source instances.
- Keep Steam frozen; the Stock Game copies are isolated from Steam updates.
- Snapshot the profile, INIs, outputs, the translation layer and the manifest CSV (git or dated 7z), and keep the archives on a secondary drive.
- Optionally compile a private .wabbajack for personal reinstalls only.
- After verifying D:\PM, delete the source instances to reclaim space; hardlinked files survive.
- Exit criteria: restoring from backup has been tested once.

## OPEN
- ASK USER 1 (laptop): exact laptop model, GPU and VRAM, and GPU power limit (W); CPU; RAM and whether it can be upgraded; screen resolution, refresh rate and aspect ratio (16:10?); whether it has a MUX switch; the internal SSDs and free space on each; whether you have an external SSD or HDD. / 筆電型號、GPU與VRAM及功耗、CPU、RAM(可否升級)、螢幕解析度/更新率/比例、是否有MUX、各SSD剩餘空間、是否有外接SSD/HDD？
- ASK USER 2 (storage and network): can you dedicate about 1 TB on one NTFS SSD volume plus about 450 GB elsewhere for archives? What are your internet speed and any data cap? If space is short, is a leaner path acceptable (Nolvus archiving off, only the needed MV files)? / 能否在同一顆SSD分割區預留約1TB+另約450GB放壓縮檔？網速/流量上限？不夠時是否接受精簡路線？
- ASK USER 3 (fidelity): do you want the target reproduced as closely as possible (1.5.97, Jiaye's Community Shaders build, all 4,044 mods, very heavy)? Or a playable laptop build inspired by it (current Nolvus 6.0.20 and MV 2.6.2 versions, official CS, lighter textures and grass)? / 要盡量1:1重現，還是以此為藍本、為筆電調整的可玩版本？
- ASK USER 4 (Chinese scope): Traditional Chinese with Taiwan wording? Which names: official Traditional (least work), 大學漢化 style, or 和光/ANK converted to Traditional? How deep: plugins and MCM only, or also scripts, SWF menus and ImGui overlays? Is machine translation with light review acceptable, and would you pay for DeepL or LLM API costs? / 繁中台灣用語？名詞以官方繁中/大學/和光轉繁為準？翻譯深度？接受機器翻譯與API費用嗎？
- ASK USER 5 (source of the list): where did Pages_Modlist_WIP come from, and can you contact its author (probably Nexus user page804) for the MO2 CSV export or meta.ini files, CustomFixes1, overwrite2, the [FIX] plugins and the CS build? Do you know whether this WIP list actually runs? / 清單來源？能否聯絡作者取得meta.ini/CSV、CustomFixes1、overwrite2、[FIX]插件？此WIP清單是否確認可運行？
- ASK USER 6 (game and accounts): do you own Steam Skyrim Special Edition plus the Anniversary Upgrade (not GOG), with every Creation Club item downloaded? What is Steam's current language? Can you switch Steam to English during installation? Do you have, or can you create, Nolvus.net and mega.nz accounts? / 是否擁有Steam版SE+AE升級且下載全部CC？Steam目前語言？安裝期間可改英文嗎？可否註冊Nolvus與mega帳號？
- ASK USER 7 (how we work): since this session cannot operate your Windows laptop directly, will you run each step yourself with checklists and scripts I provide and send back logs and screenshots? Or can you connect a computer-use or Remote Control session? Do you have admin rights, and can you add Defender exclusions? / 我無法直接操作你的筆電：你要依我提供的步驟/腳本執行並回傳日誌，還是可連線遠端操作？有系統管理員權限嗎？
- ASK USER 8 (paid and community content): will you pay for Patreon-only mods (e.g. Smooth's Grapple, Tier 1) or drop them? Do you accept community Chinese packs that are licensed for personal use only (蘇禾's packs on Quark, which need Quark or Baidu to download), knowing the result must never be redistributed? / 是否付費取得Patreon限定模組或捨棄？是否接受僅限個人使用的社群漢化包(夸克/百度下載)，且成品不得散佈？
- VERIFY: which package does the Nolvus Dashboard (3.8.11, with 3.8.12 commits unreleased) install today, 6.0.20 or 6.0.21 beta? Does 6.0.21 go live soon?
- VERIFY: does the Nolvus 1.5.97 STOCK GAME's Skyrim - Interface.bsa contain the *_chinese strings and fonts_cn.swf? Does the 1.5.97 executable honor sFontConfigFile=Interface\fontconfig_cn.txt, or does it need a CJK fontconfig.txt override?
- VERIFY: do 蘇禾's DSD and 'Other' packs expect sLanguage=ENGLISH with overridden *_english.txt files, or sLanguage=CHINESE? What .pex scripts do the MV 2.5.1 'Other' pack's 143 MB contain?
- VERIFY: after installing Nolvus 6.0.20 and disabling the 6.0.18–6.0.20 additions to match the target, do any Nolvus patch plugins have missing masters?
- VERIFY: are STPP-NG 1.10, DSD 1.4.3, SkyPrompt 2.3.13 and later, and FontConfig Extended 1.1.0 stable on 1.5.97? Does official CS 1.9.1 work with NAT.CS III 2.0.0 and Lux CS if the Jiaye build is replaced?
- VERIFY: for each MV-sourced SKSE DLL, is there a 1.5.97 build? Cross-check against the MV 2.40.1 JSON (Nexus file 703199).

## DATA
CONTRADICTIONS AND RESOLUTIONS
| # | Topic | Conflicting claims | Resolution (check) | Confidence |
|---|---|---|---|---|
| 1 | MV runtime | zh_community/provenance: 1.5.97+BOBW; mv/perf/merge: 1.6.1170 | 1.6.1170 since v2.5 (2026-03-14). CHANGELOG line 206; report shows SKSE 2.2.8, EF 1.6.1170+, AL 1.7.99 AIO. Last 1.5.97 release: 2.40.1 (Nexus file 703199, 2025-12-29) | high |
| 2 | Target Nolvus base | nolvus: about 6.0.17; provenance: about 6.0.18 | 6.0.17. The target's hair folders are MV names (MV lines 1536-1538); the 6.0.18 additions 'Vanilla Hair Remake - SMP/Patches/Addon' are absent | high |
| 3 | Target MV era | implicitly MV 2.6.2 | MV 2.5.x: 2.5 additions present (True Flasks NG, HorsePower, Knockback); 9 of 35 mods removed in 2.6 present | medium |
| 4 | CS build origin | Jiaye/Discord vs PR build vs WJ authored file | Same file on the WJ authored-files CDN (Kirbylite report line 272); called 'Jiaye's CS' | high |
| 5 | STPP-NG version | 1.9 on 08-24 vs 1.10 on 08-24 | 1.10 MAIN 2026-08-24; 1.9 2026-08-14 (Nexus GraphQL) | high |
| 6 | v6 RAM | zh_tooling: 32 GB; nolvus/perf: not stated | Not stated for v6 (v5 only); MV recommends 32 GB | high |
| 7 | Nolvus Downgrade support for 1.7.104 | zh_community: unknown | Dashboard 3.8.11 (2026-08-28) adds the 1.7.104 signature | high |
| 8 | Variant choice | nolvus: Ultimate; zh_community: Redux; perf: tiered | Depends on VRAM, but the target's VRAM load comes mostly from MV and PBR; Redux also removes the Ultimate-only rows the target uses | medium |
| 9 | Official CN text | Stock game is English-only vs Chinese inside | MV Interface.bsa contains official Chinese (= Traditional); Nolvus STOCK GAME unverified | medium |
| 10 | Mod-origin counts | 2444/2556/2614… Nolvus-only | Method-dependent; recompute by exact match against the installed folders | - |

DISK BUDGET (installed / transient; my arithmetic)
- Steam Skyrim AE + all CC: about 21 GB
- Nolvus v6: Ultimate 426 GB (archives +193 optional; can be on HDD) | Ultra 406 (+188) | Redux 372 (+170)
- MV 2.6.2: 386 GB installed + 230 GB downloads + 5.4 GB .wabbajack; Wabbajack wants 40-60 GB spare
- Hybrid D:\PM (hardlinks): about 0 for reused files + new mods (unmeasured, guess 50-150 GB) + outputs (guess 15-30 GB)
- Pagefile: 20-40 GB
- Peak SSD, both lists fully installed, archives elsewhere: about 1.0-1.1 TB; with archives on SSD: about 1.5 TB
- Steady state after deleting sources: about the size of the target (unmeasured, guess 450-600 GB)

TIME BUDGET (estimates unless cited)
- Downloads, 423 GB: 100 Mbps about 9.4 h | 300 Mbps about 3.1 h | 1 Gbps about 0.9 h
- Nolvus install: about 1 h with Premium and a good connection (nolvus.net); MV install and extraction: several hours (unverified)
- Manifest and assembly (human): 1-3 days
- Output regeneration: NGIO 0.5-2.5 h (primary); DynDOLOD, TexGen, PGPatcher, Synthesis, xLODGen: several hours in total (unverified)
- Chinese layer: automated passes in hours; review days to weeks
- Overall: roughly 1-3 weeks of part-time work

CANNOT BE REPRODUCED EXACTLY
CustomFixes1, overwrite2, [FIX]*.esp x8, YXZ_NRoad PBR DGS.esp edits, exact mod versions (no meta.ini), all generated outputs, Nolvus 6.0.17 package (Dashboard installs latest), MV 2.5.x state (2.6.2 only), the Jiaye CS build (unless fetched from the WJ CDN), 13 off-Nexus/Patreon mods (some paid), and the 5 unresolved folders.

PHASES (goal → exit criteria)
0 Decide → specs, fidelity, disk layout and translation canon recorded
1 Prep → vanilla game launches; accounts and space ready; Steam English and frozen
2 Nolvus → main menu reached; STOCK GAME 1.5.97; profile backed up
3 MV (full or lean) → main menu reached or lean manifest done; folder→fileId table exported
4 Manifest → every target folder mapped or flagged; paid and dropped items approved
5 Assemble → 4,044 folders; no missing masters; ≤254 full plugins; SKSE DLLs all load
6 Outputs + EN test → 30-60 min route without crash; VRAM under budget; 'EN-baseline' frozen
7 Chinese (DSD/loose files only) → coverage report; no boxes or $KEYs; plugin count unchanged
8 Tune → FPS target met; 2 h stable; temperatures OK
9 Freeze/backup → restore tested

USER QUESTIONS (Chinese, ready to paste): see open_questions items 'ASK USER 1-8'.