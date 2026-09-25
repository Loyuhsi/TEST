# runtime

## SUMMARY
Fact-check verdict: the original runtime analysis mostly holds up. The core conclusion stands. The target list sits on Nolvus Awakening's STOCK GAME, which runs the Skyrim SE 1.5.97 executable with the full Anniversary Edition Creation Club content. The evidence for this:
- The lowest-priority Nolvus core block is intact: SKSE 2.0.0.20, Address Library, Backported Extended ESL Support (BEES) 1.2, SSE Fixes 3.1.5.97, and "Crash Logger - 1.5.97" placed above "Crash Logger - SSE".
- Mages & Vikings' (MV) runtime mods ("1.6.1170 Missing Files", "Cleaned Vanilla Masters", CC plugins) are absent.
- The user added 1.5.97-specific builds of Dynamic Armor Variants and Skyrim Souls RE at higher priority than the generic ones.

I re-checked the local counts and they are all exact:
- 4,044 enabled mods and 95 separators.
- 4,244 plugins: 28 .esm, 4,140 .esp, 76 .esl.
- Plugin origin: 2,103 Nolvus-only, 717 MV-only, 672 in both, 752 in neither.
- 79 implicit plugins (5 base masters + 74 CC), so about 4,323 load. That means 227 to 254 must be full plugins.

The external facts are confirmed:
- Nolvus versions and dates.
- The SKSE builds (2.0.20 for 1.5.97; 2.3.1 for 1.7.104).
- Bethesda's runtime 1.7.99 update on 20 Aug 2026, now 1.7.104.
- MV 2.5 moved to 1.6.1170; MV 2.6.2 metadata and README.
- BEES and CommonLibSSE-NG details.
- The Community Shaders (CS) migration guide and FAQ.
- Pandora's README.

Key corrections:
1. The Nolvus Dashboard does support the current Steam build. v3.8.9 added a downgrade signature for 1.7.99.0, v3.8.10 added "languages pack management" for 1.7.99.0, and v3.8.11 (28 Aug 2026) added a downgrade signature for 1.7.104.0. The main "can Nolvus install at all" risk goes away if the user runs Dashboard 3.8.11 or later.
2. "Nolvus Downgrade Patcher" merged two different tools. The v5 guide uses NolvusDowngrader.exe. /appendix/downgrade describes an older third-party full patcher (explicitly not Best of Both Worlds).
3. BEES covers 1.5.97 through 1.6.659, not 1.6.640.
4. Pandora Output is at line 5, not the very top.
5. The target uses Nolvus's "SkyUI AIO Survival (SAS)", not SkyUI 5.2. "Edge UI - Modern Skyrim Interface" is in both Nolvus and MV.
6. Auto Parallax is not a new addition; it was already in the Feb-2025 snapshot.
7. Mfg Fix NG is officially "version independent", so the earlier low-confidence claim is upgraded.
8. CS also requires removing d3dcompiler_47.dll from the game root.

Important missing facts that affect the translation:
- The Nolvus Dashboard's language choice must match the Steam language, and only the base game gets translated, not the mods.
- Steam Skyrim SE officially supports Traditional Chinese, as text only.
- The MV README requires Steam set to English.
- CS v1.9.0 (23 Sep 2026) added support for 1.7.99+. The user's CS build is dated 2026-05-28.

## FACTS
- [high] The target's lowest-priority core block is Nolvus's. It sits under the separators '1.1 SKSE PLUGINS' and '1.2 BUG FIXES UTILITIES & TWEAKS'; '0. MASTER FILES' is at the bottom. It contains 'Skyrim Script Extender', '... - Nolvus Settings', 'Address Library for SKSE Plugins', 'Backported Extended ESL Support', 'SSE Engine Fixes2', 'SSE Fixes', 'Bug Fixes', 'SSE Display Tweaks', 'Mfg Fix NG' (line 4089, above) plus 'Mfg Fix' (4090), and 'Crash Logger - 1.5.97' (line 4029), which is above and so beats 'Crash Logger - SSE' (4030). (local analysis: user__modlist.txt)
- [high] The user placed 1.5.97-specific builds above the generic ones: 'Dynamic Armor Variants for Skyrim 1.5' (4034) over 'Dynamic Armor Variants' (4035), and 'Skyrim Souls RE for Skyrim 1.5' (444) over 'Skyrim Souls RE - Updated' (445). All four are in neither snapshot. (local analysis: user__modlist.txt, neither_mods.txt)
- [high] MV's runtime-root mods ('Cleaned Vanilla Masters', 'Creation Club', 'Cleaned Creation Club Plugins', '1.6.1170 Missing Files') and 'IFrame Generator RE AE Support' are not in the target. The target has Nolvus's 'IFrame Generator RE', which the official list shows as 1.03. (local analysis: user__modlist.txt vs mages-vikings__modlist.txt; https://www.nolvus.net/awakening)
- [high] The official Nolvus Awakening mod list shows these versions: Skyrim Script Extender 2.0.0.20, Address Library 2.0, BEES 1.2, SSE Engine Fixes 7.0.20, SSE Fixes 3.1.5.97, Mfg Fix 1.5.4, Powerofthree's Tweaks 1.16, Base Object Swapper 2.6.1, Crash Logger - SSE 1.16.0, Crash Logger - 1.5.97 1.15.0, Nemesis Unlimited Behavior Engine 0.84b, ENB Binaries 0.505, RaceMenu SE 0.4.16, Faster HDT-SMP 3.0.6, Open Animation Replacer 2.3.6. Many components are marked 6.0.21. (https://www.nolvus.net/awakening (fetched 2026-09-25))
- [high] Nolvus 'Always Install' mods absent from the target: ENB Helper 1.5, ENB Input Disabler 1.1.1, DLL Plugin Loader 1.0, Auto Parallax 1.0.27, Bone Wolf Shutdown Fix 1.0.0, Worker Spin Lock Fix 2.6.0, Exit Sneak On Sprint 1.2.1, Alt-Tab Stuck Key Fix 1.3.1, and Seasons of Skyrim 1.7.5. ENB Anti-Aliasing 1.2.3 is a conditional 'Not TAA' option, not Always Install. (https://www.nolvus.net/awakening; local user__modlist.txt)
- [high] The SKSE homepage lists the current Anniversary Edition build as 2.3.1 (game 1.7.104), the Special Edition build as 2.0.20 (game 1.5.97) and the GOG AE build as 2.2.6 (1.6.1179). It says the 1.5.97 build remains for people who downgraded. The SKSE whatsnew file shows 2.2.6 'support for 1.6.1170'. (https://skse.silverlock.org/ ; https://skse.silverlock.org/skse64_whatsnew.txt)
- [high] Nolvus STOCK GAME: the Dashboard copies the Steam files, after a binary check that they are legal and the right version, into Instances\[Instance]\STOCK GAME. The Steam install stays clean, and Skyrim updates do not break Nolvus. (https://www.nolvus.net/appendix/installer/tech)
- [high] The Nolvus Dashboard supports the current Steam runtimes. v3.8.9: 'Added Downgrade signature info for Skyrim 1.7.99.0'. v3.8.10 (21 Aug): 'Added languages pack management for Skyrim 1.7.99.0'. v3.8.11 (28 Aug 2026, latest): 'Added Downgrade signature info for Skyrim 1.7.104.0'. (https://github.com/vektor9999/NolvusDashboard/releases ; https://github.com/vektor9999/NolvusDashboard/releases/tag/v3.8.11 ; https://github.com/vektor9999/NolvusDashboard/releases/tag/v3.8.10)
- [high] Nolvus requires Windows 10/11 64-bit and Steam Skyrim Anniversary Edition (or SE plus the Anniversary Upgrade) with all Creation Club files downloaded. GOG and other versions are not supported. The integrity check fails with 'hash for game file does not match' (e.g. SkyrimSE.exe, Skyrim.ccc, CC .bsa files) when the game is not the latest Steam version or CC is missing. (https://www.nolvus.net/appendix/installer/skyrim_setup ; https://www.nolvus.net/appendix/installer/faq)
- [high] Nolvus Dashboard language: 'The language you select has to be the same than the one you selected in steam. Only the base game will be translated, not the mods.' Archiving is optional, and the archive folder may be on an HDD, but the list itself must be on an SSD. (https://www.nolvus.net/appendix/installer/install)
- [high] Steam lists these languages for Skyrim Special Edition: English, French, Italian, German, Spanish, Polish and Russian with full audio; Traditional Chinese (text only); and Japanese. Simplified Chinese is not listed. (https://store.steampowered.com/api/appdetails?appids=489830)
- [high] Nolvus v5 Stock Game step: run NolvusDowngrader.exe, pointed at the Steam Anniversary install that has all CC downloaded, with output to SSD:\NOLVUS\STOCK GAME, then verify that the CC files are present. The separate /appendix/downgrade page is an older manual method using the third-party 'Unofficial Skyrim Special Edition Downgrade Patcher' full patcher ('NOT BEST OF BOTH WORLD'), shown for 1.6.353. (https://www.nolvus.net/guide/asc/stockgame ; https://www.nolvus.net/appendix/downgrade)
- [high] Nolvus history: v6.0.7 (Saturday, 15 Mar 2025) added Crash Logger - SSE 1.15.0 and Crash Logger - 1.5.97 1.15.0. v6.0.15 (14 Oct 2025, new game and new install) 'Added optional built-in Frame Generation' and updated Crash Logger - SSE to 1.16.0. The latest dated entry is v6.0.20 (Tuesday, 27 Jan 2026); no dated 6.0.21 entry exists, although the mod list shows 6.0.21 components. (https://www.nolvus.net/appendix/history)
- [high] Nolvus v6 requirements, Ultimate without SR Exterior Cities at 1080p: minimum i7 10th gen, 14 GB VRAM, RTX 4060 Ti, 426 GB installed, 193 GB download. Redux without SR Exterior Cities at 1080p: minimum i7 7th gen, 8 GB VRAM, GTX 1080 (recommended RTX 2070), 372 GB installed, 170 GB download. The download size is optional because archiving can be disabled. (https://www.nolvus.net/appendix/installer/requirements)
- [high] Newer Nolvus-based snapshots still contain BEES, 'Crash Logger - SSE', 'Crash Logger - 1.5.97', 'Nemesis Unlimited Behavior Engine' and 'Nemesis Output': Redux 6.0.20 (updated 2026-05-29) and Victolvus 6.00 (2026-09-04). Neither has Pandora or ENB Binaries. The 2025-02 v6 snapshot had Net Script Framework and Auto Parallax but no Crash Logger. (https://api.loadorderlibrary.com/v1/lists/nolvus-awekening-redux ; https://api.loadorderlibrary.com/v1/lists/victolvus ; local nolvus-awakening-v6__modlist.txt)
- [high] MV changelog v2.5: 'The list has been updated from version 1.5.97 to version 1.6.1170'. The same version fixed animations broken by the switch to Pandora (Bathing in Skyrim, Immersive Interactions). v2.4 switched from Nemesis to Pandora Behaviour Engine Plus. v2.6.1 made Kauz ENB the default. The latest version is 2.6.2. (https://gist.github.com/nicolasbertolino/a303a48fcc5f22a0c0e37822a7b786e9)
- [high] Wabbajack featured-status request #37 (opened 26 Feb 2025): 'The modlist is built for the 1.5.97 version of Skyrim, utilizing the Best of Both Worlds patcher to integrate the additional content from version 1.6.1170.' This describes a pre-2.5 MV. (https://github.com/wabbajack-tools/Requests-Reports/issues/37)
- [high] The MV README requires a legal copy with 'all Creation Club content updated to 1.7.104 (the latest version)'. It says to disable the Steam Overlay and set the Steam game language to English. Recommended hardware is an RTX 4070 or higher, 32 GB RAM and a modern CPU. Dependencies are the VC++ x64 redistributable, .NET 6.0 Desktop Runtime and .NET 8 Desktop Runtime. (https://github.com/nicolasbertolino/MagesAndVikings/blob/main/README.md)
- [high] MV 2.6.2 Wabbajack metadata: 3,772 archives, 229,998,290,486 bytes of archives (~230 GB), 374,545 installed files, 386,316,461,236 bytes installed (~386 GB), total ~616 GB. The .wabbajack file itself is ~5.4 GB. Updated 2026-09-05. (https://raw.githubusercontent.com/nicolasbertolino/MagesAndVikings/main/modlists.json)
- [high] The MV 2.6.2 snapshot contains AE/1.6.1170 markers: '1.6.1170 Missing Files', 'AddItemMenu AE', 'Crash Logger SSE AE VR - PDB support', 'IFrame Generator RE AE Support', 'Combat Pathing Revolution AE', and '_ResourcePack.esl' in its load order. It also has 'Pandora Behaviour Engine Plus', 'ENB Binaries', 'ENB Frame Generation', 'ENB Anti-Aliasing - AMD FSR 3.1 - NVIDIA DLAA', and 'BFCO - Attack Behavior Framework' plus 'BFCO NG'. It has no BEES. Both 'Mfg Fix' and 'Mfg Fix NG' are present. (local analysis: mages-vikings__modlist.txt, mages-vikings__loadorder.txt)
- [high] DynDOLOD: 'On August 20, 2026 Bethesda released a disruptive update with runtime version 1.7.99 (now 1.7.104). All DLL plugins need to be updated.' From runtime 1.6.1130 there can be version 1.71 plugins, which need BEES on older runtimes. A 1.5.97 runtime with 1.6.640 game plugins is 'a so called best of both worlds downgrade'. (https://dyndolod.info/Mods/Skyrim-Special-Edition-Skyrim-Anniversary-Edition)
- [medium] A 'Steam 1.7.104 - 1.6.1170 - 1.5.97 Best of Both Worlds Downgrade Patcher' is on Nexus (mod 169962). It is said to ship Skyrim_1_7_104_to_1_5_97_patcher.exe and Skyrim_1_7_104_to_1_6_1170_patcher.exe and to downgrade only the exe, DLLs and needed files. STEP 2.3 also points to BoBW to get back to 1.6.1170. (https://www.nexusmods.com/skyrimspecialedition/mods/169962 (search-result summary; page not fetched) ; https://stepmodifications.org/wiki/SkyrimSE:2.3)
- [high] The BEES README says it 'adds support for the extended plugin (ESL) range introduced in game version 1.6.1130 to versions 1.5.97, 1.6.659, and anything in between'. The 1.6.1130 update raised headers from 1.70 to 1.71, and a 1.71 plugin on an old build will likely crash. Maximum new records per ESL went from 2048 to 4096. It logs to Documents\My Games\Skyrim Special Edition\SKSE\BackportedESLSupport.log. (https://github.com/Nukem9/skyrimse-backported-esl-support (README.md))
- [high] CommonLibSSE-NG loads Address Library from Data/SKSE/Plugins/versionlib-<ver>.bin on AE and version-<ver>.bin on SE. It can build a single DLL that works on SE, AE and VR. (https://github.com/CharmedBaryon/CommonLibSSE-NG (include/REL/ID.h lines ~308-317; README))
- [high] STEP SkyrimSE 2.3 requires 1.6.1170 and SKSE 2.2.8. It says to install Engine Fixes with the 'Anniversary Edition' FOMOD option, put the SKSE64 Preloader's d3dx9_42.dll manually in the game root, and delete tbb.dll and tbbmalloc.dll left from older versions. It uses the Address Library 'All in one (1.6.X)' file. (https://stepmodifications.org/wiki/SkyrimSE:2.3)
- [high] CS ENB Migration Guide: 'Skyrim will crash if CS and ENB DLLs are installed at the same time'. Delete d3d11.dll and d3dcompiler_46e.dll from the game root (or from a Root Builder mod). ENB Input Disabler, ENB Helper Plus, ENB AO Toggler and similar tools should be removed. ENB Anti-Aliasing and ENB Frame Generation are replaced by CS Upscaling, and Skyrim Upscaler is not supported. ENB Light mods have limited support. Water for ENB is fully compatible and has CS options. Lux should be reinstalled without optimized or particle meshes. (https://modding.wiki/en/skyrim/developers/community-shaders/ENB-Migration-Guide)
- [high] CS FAQ points:
- The team has no plans to support versions other than the latest Steam version and 1.5.97, and 1.5.97 is the only long-term-support version.
- Remove d3d11.dll, d3dcompiler_46e.dll and, on Windows, d3dcompiler_47.dll.
- Skyrim Souls makes menus transparent; disable frame generation.
- The Display Tweaks borderless upscale is incompatible, and exclusive fullscreen is unsupported.
- Improved Camera darkens the moons (fixed in a test version).
- Particle/ENB lights have had limited support since 1.8.
- With PBR, use only PGPatcher, not Auto Parallax.
- Only official builds get support. (https://modding.wiki/en/skyrim/developers/community-shaders/faq)
- [medium] Community Shaders v1.9.0 (23 Sep 2026) added 'support Skyrim 1.7.99+'. v1.9.1 (24 Sep 2026) is the latest, with asset CommunityShaders_AIO-2026-09-24T12-32Z.7z. The user's CommunityShaders_AIO-2026-05-28T17-09Z matches no GitHub release date: releases around it are 1.6.0 PR build on 19 May and v1.6.0 on 31 May. It is probably the v1.6.0 build or a PR test build. (https://github.com/community-shaders/skyrim-community-shaders/releases (pages 1, 2, 4))
- [high] The target uses Community Shaders: 'CommunityShaders_AIO-2026-05-28T17-09Z', 'CS shaders', 'NAT.CS III', 'Lux (cs)', 'Lux Orbis cs', 'Light Placer', 'Water for ENB [cs]2', and pgpatcher_output, texgenCS, dyndolodCS2 and 'grass CS' outputs. It has no ENB Binaries, ENB Helper, ENB Input Disabler, ENB Anti-Aliasing or DLL Plugin Loader. 'NAT.ENB III - Natural and Atmospheric Tamriel ENB 3.1.1C' is still enabled. (local analysis: user__modlist.txt)
- [high] The target has 'Pandora Behaviour Engine v4.3.1-beta' (line 1211) and 'Pandora Output' (line 5, the third enabled entry after 'Skyshards - CS Light Addon' and 'CS shaders'). 'Nemesis Unlimited Behavior Engine' and 'Nemesis Output' are absent. Nemesis-format patches remain: 'Nemesis - Creatures Behaviour', its WereWolf addon, 'Nemesis - Offset Movement Animation', and 'Shadow of Skyrim - Nemesis and Alternative Death System'. Also present: 'Horsepower - Pandora Cache' and 'Additional Pandora Patch For CRC32 Cache'. (local analysis: user__modlist.txt)
- [high] The Pandora README says it 'supports the patch formats of both Nemesis Behavior Engine and FNIS' ('almost all of Nemesis patch format') and extends the folder system for creature compatibility. For MO2: create an empty 'Pandora Output' mod and pass -o "path" (or --output), not MO2's 'create files in mod'. Use --tesv:"path" to point at a Wabbajack Stock Game when FNIS mods are not found. All releases are betas; the latest are v4.3.1-beta (16 Apr) and v4.4.0-beta (11 Aug). (https://github.com/Monitor221hz/Pandora-Behaviour-Engine-Plus (README.md; releases))
- [high] Skyrim SE/AE limits: 254 full plugins (0x00-0xFD, ESM + ESP) and 4096 light plugins at 0xFE. In MO2, hover over the active-plugin count on the Plugins tab to see the ESM+ESP and ESL counts. SSE Engine Fixes raises the file-handle limit. (https://dyndolod.info/Messages/Plugin-Limit)
- [high] Target plugins.txt has 4,244 enabled plugins: 28 .esm, 4,140 .esp and 76 .esl. By origin: 2,103 Nolvus snapshot only, 717 MV only, 672 both, 752 neither (745 of them .esp). Base masters and CC are implicit. The Nolvus loadorder minus plugins.txt is exactly 79 entries (5 base masters + 74 CC, none of them in the user's plugins.txt). So about 4,323 load, and full plugins must number 227-254 (4,323 - 4,096 = 227). (local analysis: user__plugins.txt, nolvus-awakening-v6__plugins.txt, nolvus-awakening-v6__loadorder.txt, mages-vikings__loadorder.txt)
- [medium] Of the 4,044 enabled target mods, by name against nolvus.net plus the MV snapshot: roughly 2,570-2,620 are Nolvus-only, ~535-557 MV-only, ~350-366 both, and ~520-590 neither. The exact numbers depend on how the nolvus.net list is parsed. Against snapshots only, 716 are in neither. (local analysis: user__modlist.txt vs https://www.nolvus.net/awakening and mages-vikings__modlist.txt; neither_mods.txt)
- [high] 66-67 enabled target folders end in a numeric suffix and have a base name from Nolvus or MV. Examples: 'SSE Engine Fixes2', 'SKSE Menu Framework2', 'Open Animation Replacer4', 'Better Third Person Selection2', 'Unslaad SE2', 'Wyrmstooth2', 'The Wheels of Lull2', 'Edge UI - Modern Skyrim Interface3', 'DynDOLOD Resources SE2'. Only 3 are side-by-side duplicates with the base folder also enabled: 'Northern Roads Patch Collection' + '...3', 'Vigilant - Character Overhaul' + '...2', and 'Legacy of the Dragonborn - Follower Room Patches' + '...2'. (local analysis: user__modlist.txt)
- [high] The user replaced Nolvus's quest-mod main folders: 'Legacy of the Dragonborn V6' (Nolvus: 5.6.5), 'VIGILANT SE 1.8' (Nolvus: 'Vigilant' 1.7.3), 'Unslaad SE2' (Nolvus: 'Unslaad' 3.0.2), 'Wyrmstooth2' (Nolvus: 1.20.2) and 'The Wheels of Lull2' (Nolvus: 5.1.13.3). The original folder names are absent. A 'VIGILANT - English Translation (Silent)' folder is present. (local analysis: user__modlist.txt; https://www.nolvus.net/awakening)
- [high] UI stack in the target: Nolvus's 'SkyUI AIO Survival (SAS)' (Nolvus 7.2), not MV's plain 'SkyUI'. The Nolvus base 'Edge UI' folder is absent, but 'Edge UI - Modern Skyrim Interface3', 'Edge UI - Loading Screen Fix' and 'Nolvus HUD Settings (Edge UI)' are present. 'Edge UI - Modern Skyrim Interface' is in both Nolvus (0.6.1, Edge UI option) and MV. 'Sanguis - Mist's Font Replacer' replaces Nolvus's 'Edge UI - Missing Font Patch'. 'Scaleform Translation Plus Plus NG' and 'MCM Helper' are present. (local analysis: user__modlist.txt, mages-vikings__modlist.txt; https://www.nolvus.net/awakening)
- [high] The Mfg Fix NG README describes it as a 'Version independent implementation of MfgFix'. (https://github.com/KrisV-777/Mfg-Fix-NG (README.md))
- [high] ImprovedCameraSE-NG supports 'multiple SkyrimSE versions from 1.5.97 to 1.6.1179' through CommonLibSSE-NG and Address Library. Its README does not claim 1.7.x. (https://github.com/ArranzCNL/ImprovedCameraSE-NG)
- [medium] RaceMenu 0.4.16 (Nolvus's version) is the SE 1.5.97 build, and 0.4.19.16 is tested on AE 1.6.1170. (https://www.nexusmods.com/skyrimspecialedition/mods/19080 (search-result summary; the page was not fetched))
- [medium] The Nolvus Dashboard's MO2 executables point at the instance's STOCK GAME skse64_loader.exe and SkyrimSE.exe, and ENB packages are patched into the STOCK GAME folder. (https://github.com/vektor9999/NolvusDashboard (Vcc.Nolvus.Package/Mods/ModOrganizer.cs, ENB.cs; not re-fetched in this check))

## RISKS
- CORRECTION: The original said Nolvus Dashboard support for Steam 1.7.104 could not be confirmed. It is confirmed. Dashboard v3.8.9 added a downgrade signature for 1.7.99.0, v3.8.10 added 'languages pack management' for 1.7.99.0, and v3.8.11 (28 Aug 2026) added a downgrade signature for 1.7.104.0. The risk remains only if an older Dashboard is used, or if Steam moves past 1.7.104 before Nolvus adds a new signature.
- CORRECTION: 'The Nolvus Downgrade Patcher downgrades AE to 1.5.97 while keeping CC' merged two tools. The v5 guide uses NolvusDowngrader.exe (all CC required, output to STOCK GAME). /appendix/downgrade is an older manual method with the third-party Unofficial SSE Downgrade Patcher full patcher (not BoBW, 1.6.353 era). For v6 the Dashboard does this internally.
- CORRECTION: BEES covers 1.5.97 through 1.6.659 per its README, not '1.5.97–1.6.640'.
- CORRECTION: 'Pandora Output' is not the top-priority mod. It is on line 5, below 'Skyshards - CS Light Addon' and 'CS shaders'. This matters only if those contain behaviour files, which is unlikely.
- CORRECTION: The UI stack was misdescribed. The target uses Nolvus's 'SkyUI AIO Survival (SAS)', not 'SkyUI 5.2'; MV's plain 'SkyUI' is absent. 'Edge UI - Modern Skyrim Interface' is a Nolvus Edge-UI option (0.6.1) as well as an MV mod, not MV-only. The Nolvus base 'Edge UI' folder is absent from the target.
- CORRECTION: Auto Parallax is not a '6.0.21-era addition'. It was already in the Feb-2025 v6 snapshot. Its absence is consistent with the CS FAQ advice to use only PGPatcher with PBR; the target has pgpatcher_output. Worker Spin Lock Fix, Exit Sneak On Sprint and Alt-Tab Stuck Key Fix are missing even from Redux 6.0.20 (May 2026), so they are plausibly newer. Bone Wolf Shutdown Fix was already in Redux 6.0.20.
- CORRECTION: ENB Anti-Aliasing is a conditional Nolvus option ('Not TAA'), not 'Always Install'.
- CORRECTION: The low-confidence Mfg Fix NG claim, which relied on a PR search summary, is replaced. The Mfg Fix NG README officially calls it 'Version independent'. Keep one of Mfg Fix or Mfg Fix NG. NG currently wins because it has higher priority.
- CORRECTION: CS cleanup must also remove d3dcompiler_47.dll from the Windows game root, not only d3d11.dll and d3dcompiler_46e.dll.
- CORRECTION: The mod-origin counts (2,598 / 557 / 366 / 523) depend on how nolvus.net is parsed. My independent re-parse gave about 2,570–2,620 / 535 / 350 / 540–590. Treat them as approximate. The numeric-suffix folder count is 66–67. The plugin counts were re-verified exactly.
- CORRECTION: The alternative-path note 'replace SKSE with 2.2.6 for 1.6.1170' is outdated. STEP 2.3 now pins SKSE 2.2.8 for 1.6.1170, while the SKSE homepage lists 2.2.6 only as the GOG 1.6.1179 build. This only matters for the path that is not recommended.
- TRANSLATION CONFLICT: MV's README requires the Steam language set to English. The Nolvus Dashboard requires its language choice to match Steam and translates only the base game, not the mods. Changing the Steam language between the two installs may trip the Nolvus and Wabbajack hash checks. Traditional Chinese is officially text-only on Steam; Simplified Chinese is not offered.
- Launching with the Steam SkyrimSE.exe (1.7.104) instead of the Nolvus STOCK GAME (1.5.97) breaks every SKSE plugin in the target.
- ENB DLLs that the Nolvus Dashboard placed in STOCK GAME crash the game together with Community Shaders.
- The user's CS build (2026-05-28) is four months old and matches no GitHub stable release date, so it may be a PR/test build. The CS FAQ says only official builds get support. Current stable is v1.9.1 (24 Sep 2026), which still includes 1.5.97 support.
- CS known interactions in this list:
- Skyrim Souls RE with CS frame generation gives transparent menus.
- The SSE Display Tweaks borderless upscale is incompatible, and exclusive fullscreen is unsupported.
- Improved Camera darkens the moons.
- Rudy/Cathedral ENB-light mods have only limited support.
- SKSE DLLs brought from MV (built for 1.6.1170) or newly downloaded after Aug 2026 (possibly 1.7.104-only) may fail on 1.5.97. ImprovedCameraSE-NG, for example, documents support only up to 1.6.1179, which is fine for 1.5.97.
- Plugin budget: about 4,323 loaded plugins leave only a 227–254 window for full plugins. This can only be verified on the user's PC.
- Pandora is beta-only. Nolvus's Stances, OAR, MCO, SCAR and TDM stack was validated on Nemesis 0.84b, and MV needed follow-up fixes after it switched to Pandora.
- Re-downloaded quest mods (LotD V6, VIGILANT SE 1.8, and others) may not match Nolvus's pinned versions or its integration patches.
- The Nexus mod pages (19080, 169962) were not fetched directly. The claims based on them rest on search-result summaries.

## RECS
- Keep the combined list on the Nolvus v6 1.5.97 STOCK GAME. Update the Nolvus Dashboard to 3.8.11 or later before installing, because it has the 1.7.104 downgrade signature. Launch only through MO2's STOCK GAME SKSE executable.
- Install order and language:
1. Keep Steam Skyrim at English, with the Steam Overlay off, and download all CC in-game.
2. Install Mages & Vikings 2.6.2 with Wabbajack into its own folder, as a reference and archive source only (~616 GB total).
3. Install Nolvus v6 through the Dashboard. For the base-game language, either keep English and translate everything with mods (simplest and consistent with MV), or switch Steam to Traditional Chinese and pick the same language in the Dashboard. Only the base game is translated either way; mods always need Chinese translation files.
Test whether a Steam language change breaks the Wabbajack or Nolvus hash checks before relying on it.
- Never copy MV root files into the Nolvus instance: '1.6.1170 Missing Files', the Cleaned Vanilla Masters/CC, ENB binaries, SKSE, and the Engine Fixes preloader.
- Check on disk:
- STOCK GAME\SkyrimSE.exe is version 1.5.97.0, and skse64_1_5_97.dll and skse64_loader.exe are present.
- d3d11.dll, d3dcompiler_46e.dll and d3dcompiler_47.dll are absent.
- The Address Library mod has SKSE\Plugins\version-1-5-97-0.bin.
- 'SSE Engine Fixes2' is the SE variant, and its preloader is in the root.
- Scan every enabled mod for SKSE\Plugins\*.dll. For each DLL that did not come from Nolvus, use a CommonLibSSE-NG multi-runtime build or the SE/1.5.97 file. Then launch and read skse64.log, BackportedESLSupport.log and the Crash Logger output.
- Community Shaders:
- Update from the 2026-05-28 AIO build to the current official release (v1.9.1 or later) and matching feature packs.
- Turn off frame generation if Skyrim Souls' transparent menus bother you, or drop Skyrim Souls.
- Disable Display Tweaks' borderless upscale and use CS Upscaling, which suits a laptop.
- Keep NAT.ENB III only for its plugin and weathers.
- Resolve the duplicate pairs: Mfg Fix/NG (keep NG), Skyrim Souls RE Updated/1.5, DAV/DAV 1.5, SMP Wind/NG, iWant Widgets/NG, Northern Roads Patch Collection/3, the Northern Roads compendium pair, Vigilant Character Overhaul/2, and LotD Follower Room Patches/2.
- Check the plugin budget in MO2 (hover over the plugin counter) or in xEdit: at most 254 full and at most 4,096 light. With ~4,323 loaded, 227–254 must be full. ESL-flag or compact plugins if needed; BEES handles 1.71 headers.
- Regenerate outputs after the mod set is final: LOOT or manual sort, Synthesis, BodySlide, Pandora (-o to the Pandora Output mod), PGPatcher, xLODGen/TexGen/DynDOLOD, the grass cache, and ESP translation last so the translated plugins are not overwritten. Test with a new game.
- For the laptop: get GPU model, VRAM, RAM and free SSD space first. Nolvus Ultimate 1080p minimum is an RTX 4060 Ti with 14 GB VRAM; Redux 1080p minimum is a GTX 1080 with 8 GB. MV recommends an RTX 4070 or higher and 32 GB RAM. Nolvus 6.0.15+ also has optional built-in frame generation, but in a CS-based target CS Upscaling replaces it.

## OPEN
- What exactly does Nolvus Dashboard 3.8.10's 'languages pack management for Skyrim 1.7.99.0' do? Did 1.7.99 split language files into separate Steam packs, and does it support Traditional Chinese Stock Game builds?
- Can Wabbajack install MV 2.6.2 if the Steam language is Traditional Chinese, given that the README requires English? How does MV derive its 1.6.1170 executable from a 1.7.104 Steam install (Wabbajack game-file patching or the '1.6.1170 Missing Files' mod)?
- Which exact CS release is 'CommunityShaders_AIO-2026-05-28T17-09Z' (v1.6.0 or a PR test build)? Are all of the target's CS feature packs matched to it?
- Does the user already have a working Nolvus v6 instance, and which 6.0.x version? Is it the 6.0.20 in the history, or with the 6.0.21 components the mod list shows?
- What is the ESL-flag status of the 4,140 .esp and 28 .esm files? This decides the 254-full / 4,096-light budget.
- Which runtime variants are inside the renamed or pinned folders ('SSE Engine Fixes2', 'Open Animation Replacer4', 'SKSE Menu Framework2', 'Base Object Swapper 3.41', 'Powerofthree's Tweaks 1.15.1', 'Faster HDT-SMP 4.01', 'NGIO - NG (1.5.11)')? Do Base Object Swapper 3.x and Faster HDT-SMP 4.x still support 1.5.97?
- Does 'Sanguis - Mist's Font Replacer' include CJK glyphs? Which Traditional Chinese fontconfig and font mod must load last?
- What are the laptop's GPU/VRAM, RAM and free SSD space? MV's ~616 GB plus Nolvus's ~426 GB, or 372 GB for Redux, would exceed most laptop SSDs.
- What is on Nexus mod 169962 (the BoBW patcher 1.7.104 files)? It was confirmed only through search summaries.

## DATA
RUNTIME MATRIX (verified)
- Target (user__modlist.txt): Skyrim SE 1.5.97 executable (Nolvus STOCK GAME, downgraded by the Dashboard) with all AE Creation Club content. Uses SKSE 2.0.20, BEES 1.2, SSE Fixes 3.1.5.97, Crash Logger 1.5.97 overriding SSE, Community Shaders (build 2026-05-28), and Pandora v4.3.1-beta instead of Nemesis.
- Nolvus Awakening v6: latest history entry 6.0.20 (2026-01-27); the mod page shows 6.0.21 components. Runs 1.5.97 + AE CC with SKSE 2.0.0.20, BEES, Nemesis 0.84b and ENB 0.505. Dashboard 3.8.11 (2026-08-28) accepts Steam 1.7.104 for the downgrade.
- Mages & Vikings 2.6.2 (2026-09-05): 1.6.1170 since v2.5 (was 1.5.97 + BoBW in Feb 2025). Uses Pandora (since v2.4), ENB (Kauz by default since 2.6.1) and BFCO+MCO. The README asks for game and CC at 1.7.104 and the Steam language set to English.
- Steam today: 1.7.99 (2026-08-20), now 1.7.104. SKSE AE build 2.3.1 targets 1.7.104. CS v1.9.0+ supports 1.7.99+.

LANGUAGE / TRANSLATION-RELEVANT RUNTIME FACTS
- Steam Skyrim SE offers Traditional Chinese as text only; Simplified Chinese is not listed.
- The Nolvus Dashboard's language must equal the Steam language. Only the base game is translated, never the mods.
- MV requires Steam set to English.
- The target already has Scaleform Translation Plus Plus NG, MCM Helper and SkyUI AIO Survival (SAS). The font stack is Sanguis (Mist's Font Replacer) with Edge UI - Modern Skyrim Interface3; CJK glyph coverage is unverified.

RECOMMENDED PATH: MV MODS ONTO NOLVUS 1.5.97
- For each MV SKSE DLL, use a CommonLibSSE-NG multi-runtime build or the SE/1.5.97 file.
- Form 1.71 plugins are fine because BEES is present.
- Do not import MV root, master or CC mods.
- _ResourcePack.esl/.bsa exists only on 1.6.1130+ (it is in the MV load order); assets that reference it may be missing on 1.5.97. Not verified.

GAME ROOT (STOCK GAME) CHECKLIST
- Must be present: SkyrimSE.exe 1.5.97.0, skse64_loader.exe, skse64_1_5_97.dll, and the Engine Fixes preloader d3dx9_42.dll.
- Must be absent (CS): d3d11.dll, d3dcompiler_46e.dll, d3dcompiler_47.dll.

RUNTIME-SENSITIVE MOD GROUPS
- Core, must be 1.5.97 variants:
  - SKSE, Address Library, SSE Engine Fixes2, BEES, Crash Logger 1.5.97/SSE, SSE Fixes, Bug Fixes, Scrambled Bugs, SSE Display Tweaks
  - Powerofthree's Tweaks 1.15.1, Papyrus Tweaks NG, NGIO - NG (1.5.11)
  - Mfg Fix NG / Mfg Fix, DAV 1.5 / DAV
  - RaceMenu SE 0.4.16 + Hotfix
  - CommunityShaders_AIO-2026-05-28, DynDOLOD DLL NG, Faster HDT-SMP 4.01, CBPC
  - Improved Camera SE (NG supports 1.5.97–1.6.1179), SmoothCam
  - Skyrim Souls RE 1.5 / Updated
- MV-origin DLL mods to verify on 1.5.97: SKSE Menu Framework2, Classic Sprinting Redone, Saving on Steed, Stuck Underwater fix, Load Time Profiler, Face Discoloration Fix, Model Swapper, ImmersiveHUD SKSE, Knockback SKSE, Horsepower, SkyPrompt, Collision Dialogue Overhaul, and others.
- User-added DLL mods (highest risk): Base Object Swapper 3.41, S.L.A.C.K., PhotoMode, Prisma UI, SkyPlace, In-Game Patcher, Compass Navigation Overhaul, LamasTinyHUD, SkyParkour, True Flasks NG, Core Impact Framework, the Elden Rim set, Rim Parry and Execution, Grapple, Dynamic Bloodpool, Cinematic Conversation Camera, SMP Wind NG, ParticleWind NG, Light Placer, Intellightent, and others.
- Outputs to regenerate: Pandora Output, BodySlide (Dressed), SYNTHESSIS, pgpatcher_output, lodgen2, texgenCS, dyndolodCS2, grass CS.

FRAMEWORK MAP (corrected)
- Renderer: CS only in MO2. NAT.CS III is active and NAT.ENB III is still enabled. ENB-light mods have only partial CS support. Auto Parallax is absent, consistent with the CS PBR/PGPatcher guidance.
- Behaviour: Pandora only; Nemesis-format patches are read by Pandora ('almost all' of the Nemesis format).
- UI: SkyUI AIO Survival (SAS), not SkyUI 5.2. Edge UI - Modern Skyrim Interface3 (in both Nolvus and MV). The Nolvus base 'Edge UI' folder is absent. Sanguis font replacer. Many HUD frameworks coexist: TrueHUD, SkyHUD, ImmersiveHUD, moreHUD, Infinity UI, dMenu, Prisma UI, Wheeler, LamasTinyHUD.
- Nolvus 'Always Install' mods missing from the target: ENB Helper, ENB Input Disabler and DLL Plugin Loader (all expected with CS), Auto Parallax (expected with PGPatcher), Bone Wolf Shutdown Fix, Worker Spin Lock Fix, Exit Sneak On Sprint, Alt-Tab Stuck Key Fix, and Seasons of Skyrim 1.7.5. ENB Anti-Aliasing is conditional ('Not TAA').

PLUGIN LIMIT (re-verified exactly)
- plugins.txt: 4,244 plugins (28 esm, 4,140 esp, 76 esl). Adding 5 base masters and 74 CC (none of which are in plugins.txt) gives 4,323 loaded.
- Limits are 254 full and 4,096 light, so full plugins must number 227–254.