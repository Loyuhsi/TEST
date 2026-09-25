# nolvus

## SUMMARY
Most of the earlier Nolvus research holds up against primary sources. The main error was in the local analysis of the user's target list.

**Confirmed from primary sources:**
- Nolvus Awakening is at v6.0.20, dated 27 Jan 2026 (homepage and history page). The official list at nolvus.net/awakening already shows 202 rows at 6.0.21, and a video titled "V6.0.21 (Beta)" exists.
- The v6 requirements and sizes match the requirements page exactly. Ultimate is 426 GB installed with 193 GB of optional archives, and 14 GB VRAM / RTX 4060 Ti minimum at 1080p without SREX. Redux without SREX needs 8 GB / GTX 1080 and 372 GB. No RAM figure is given for v6. An SSD is mandatory.
- The runtime is 1.5.97: SKSE 2.0.0.20, SSE Fixes 3.1.5.97, Backported Extended ESL Support (BEES) 1.2, Crash Logger - 1.5.97, ENB Binaries 0.505. Behavior files use Nemesis 0.84b, and there is no Community Shaders row.
- Steam Skyrim got update 1.7.99 on 2026-08-20, plus a hotfix on Aug 27. SKSE AE 2.3.1 targets 1.7.104. Dashboard 3.8.9–3.8.11 (Aug 20–28, 2026) added downgrade signatures for both.
- The Dashboard language list is EN/FR/IT/DE/ES/RU/PL only. The install page says the Dashboard language must match the Steam language.
- Path, global MO2 instance, mega/Google Drive and customization rules are verbatim from the Nolvus pages.

**Corrections:**
- Steam officially lists Traditional Chinese (text only) for Skyrim SE and the AE Upgrade. Chinese is not in the Dashboard, so Steam must be on English during the Nolvus install.
- The target list is **not** Kauz ENB. It is a Community Shaders build: `CommunityShaders_AIO-2026-05-28`, NAT.CS III, Lux (cs), Light Placer, pgpatcher_output. It has no ENB Binaries.
- It uses Pandora (Behaviour Engine 4.3.1-beta) instead of Nemesis.
- It contains none of Nolvus' generated outputs (Synthesis, DynDOLOD, Grass Cache, LODGEN). The user regenerated them (`dyndolodCS2`, `texgenCS`, `grass CS`, `lodgen2`, `SYNTHESSIS`).
- The Dashboard source now offers four v6 ENBs: Cabbage, Kauz, PiCho and Amon Reborn.
- The LOL snapshot `nolvus-v6-ultimate-open-beta-start` is Ultimate without SREX.

**Inferred from local analysis:**
- The target's Nolvus content is about 6.0.17 (no 6.0.18–6.0.20 additions), but its Community Shaders build is dated 2026-05-28.
- Target options: Ultimate without SREX, Edge UI, 16:9, Fantasy Combat, Alternate Leveling (10/10), Boss Encounter, Gore, Exhaustion, True Nord difficulty, BodySlide Dressed.

**Chinese translation:** community Nolvus v6 translations exist on Nexus for French (6.0.19), Italian, Turkish, Brazilian Portuguese and Spanish. The only Chinese one found is off-Nexus: a Bilibili-announced "nolvus6.12" translation.

## FACTS
- [high] The current Nolvus release is v6.0.20. The homepage reads: 'Last update Tuesday, January 27, 2026 (v 6.0.20)'. The homepage still says Awakening 'is in beta and don't have a manual installation guide yet'. (https://www.nolvus.net/)
- [high] v6 changelog dates: 6.0.4 2024-12-04, 6.0.5 2025-01-09, 6.0.6 2025-02-15, 6.0.7 2025-03-15, 6.0.8 04-01, 6.0.9 04-09, 6.0.10/6.0.11 04-17, 6.0.12 04-19, 6.0.13 05-19, 6.0.14 06-30, 6.0.15 10-14, 6.0.16 11-14, 6.0.17 11-17, 6.0.18 12-01, 6.0.19 2025-12-10, 6.0.20 2026-01-27. 6.0.16–6.0.20 each say 'doesn't require a new game'. 6.0.15 says '***REQUIRES A NEW GAME AND A NEW INSTALL***'. (https://www.nolvus.net/appendix/history)
- [medium] 6.0.21 appears to be in beta. The public full list shows 202 rows at version 6.0.21, including Synthesis Patch, LODGEN, Grass Cache, DynDOLOD outputs and Nemesis Output. It also shows ENB Binaries 0.505, Amon ENB 5.0, and Nolvus Reshade presets 2026a/b/c. A YouTube video is titled 'Nolvus Update Showcase + DLSS 5 | V6.0.21 (Beta)'. The history page has no 6.0.21 entry yet. (https://www.nolvus.net/awakening ; https://www.youtube.com/watch?v=K-O8wjA0YH0 (title via web search) ; https://www.nolvus.net/appendix/history)
- [high] The official v6 full list is public (fetched with curl and a browser user-agent, no login). It is an accordion of 68 category tables with 4,250 Mod/Version/Option rows. Option tags include Always Install, Not Graphics Only, Ultimate, Ultra, Redux, Graphics Only, SREX/Not SREX, the ENB names (Kauz, Cabbage, PI-CHO, Amon), the UIs (Edge, Untarnished, Norden, Oathvein, Vel'dun), 16:9/21:9/32:9, the addons (Fantasy Combat, Conventional Combat, Boss Encounter, Alternate Leveling, Gore, Exhaustion, Enemies Resistance, Stances Perk Tree), the difficulty presets (Milk Drinker, Hack and Slash, True Nord, Prepare to Die), Nude/Dressed, DLAA and FSR. (https://www.nolvus.net/awakening)
- [high] The v6 runtime is 1.5.97 with AE content. The official list has Skyrim Script Extender 2.0.0.20, SSE Fixes 3.1.5.97, Backported Extended ESL Support 1.2, SSE Engine Fixes 7.0.20, Crash Logger - SSE 1.16.0 and Crash Logger - 1.5.97 1.15.0, Address Library 2.0, and Scaleform Translation Plus Plus NG 1.6. SKSE's site lists build 2.0.20 as the 1.5.97 build. The standalone Nolvus Downgrade Patcher is described as downgrading 'Skyrim Anniversary Edition 1.6 to 1.5.97 while keeping Creation Club content'. (https://www.nolvus.net/awakening ; https://skse.silverlock.org/ ; https://www.nolvus.net/downloads/installer)
- [high] Graphics are ENB/ReShade based: ENB Binaries 0.505, ENB Extender/KiLoader (tagged 'Not Amon ENB'), Reshade Binaries 6.3.1 and Nolvus Reshade presets. There is no Community Shaders row in the official list. Behavior files use Nemesis Unlimited Behavior Engine 0.84b plus 'Nemesis Output'. The Dashboard registers 'Nemesis Unlimited Behavior Engine.exe' as an MO2 executable. (https://www.nolvus.net/awakening ; https://raw.githubusercontent.com/vektor9999/NolvusDashboard/main/Vcc.Nolvus.Package/Mods/ModOrganizer.cs)
- [high] The Dashboard's v6 ENB list (Statics.cs GetAvailableENBsForV6, main branch) has four entries: Cabbage, Kauz, PiCho and 'Amon Reborn' ('The definitive lightweight AMON Preset for NAT 3 Weather'). The install page text lists Cabbage, Cabbaval (Cabbage Edit), KAUZ and PI-CHO. The ENB 'can not be changed after installtion (except if you install it manually)'. (https://raw.githubusercontent.com/vektor9999/NolvusDashboard/main/Vcc.Nolvus.Core/Misc/Statics.cs ; https://www.nolvus.net/appendix/installer/install)
- [high] Variants: Ultimate is 4K-2K textures with heavily overhauled towns and cities. Ultra is 2K with medium overhaul. Redux is 2K-1K with slight overhaul and no trees in cities. All three share the same gameplay. SR Exterior Cities is 'performance heavy and consume lot of VRAM'. A Graphics Only variant was added by Dashboard 3.8.4 (2026-01-15, 'Added The graphic only version support'). (https://www.nolvus.net/appendix/installer/install ; https://github.com/vektor9999/NolvusDashboard/releases)
- [high] v6 sizes (installed / optional download): Ultimate 426/193 GB, Ultra 406/188 GB, Redux 372/170 GB, Graphics Only 235/105 GB. The page says 'The mentionned download size is OPTIONAL!!! You can disable archiving before installing.' (https://www.nolvus.net/appendix/installer/requirements)
- [high] v6 minimum requirements at 1920x1080:
- Ultimate without SREX: 14 GB, RTX 4060 Ti, i7-10000 series (15 GB at 1440p, 16 GB at 4K).
- Ultimate with SREX: 16 GB, RTX 4080.
- Ultra without SREX: Performance LODs 10 GB RTX 3080, Ultra LODs 11 GB RTX 3080 Ti, Ultra Performance LODs 10 GB RTX 2080 Ti.
- Ultra with SREX: 13–14 GB, RTX 4060 Ti.
- Redux without SREX: 8 GB, GTX 1080, i7-7000 series (recommended RTX 2070; 10 GB GTX 1080 Ti at 1440p).
- Redux with SREX: 10 GB, GTX 1080 Ti, i7-10000.
- Graphics Only without SREX: 11 GB, RTX 3080 Ti. With SREX: 14 GB, RTX 4060 Ti.
No RAM figure is given for v6; 'RAM : 32 Gb' appears only in the v5 tables. An optional .NET 5.0 SDK is listed. (https://www.nolvus.net/appendix/installer/requirements)
- [high] A 20000–40000 MB page file on the Nolvus drive is advised 'specially if you have only 16 gb of RAM'. 'DON'T INSTALL THE MOD LIST ON A HDD!!!' The archive directory may be on an HDD. (https://www.nolvus.net/appendix/pagefile ; https://www.nolvus.net/appendix/installer/requirements ; https://www.nolvus.net/appendix/installer/install)
- [high] The OS must be Windows 10/11 64-bit. The game must be a legal Skyrim AE, or SE plus the Anniversary Upgrade, 'from STEAM ONLY. GOG or other versions ARE NOT SUPPORTED!!!'. All Creation Club files must be downloaded, and uninstalling Skyrim and removing leftovers first is 'highly recommended'. The NVIDIA 'Prefer Maximum Performance' setting for skyrimse.exe is part of the setup. (https://www.nolvus.net/appendix/installer/skyrim_setup)
- [high] The Steam game must be at the latest Steam version. Integrity errors are listed when 'The game has not been updated to the latest version available from Steam'. The Dashboard runs CheckIntegrity, then CopyGameFiles, then PatchGameFiles into '<Instance>\STOCK GAME'. The tech page says 'Your Steam install remains absolutely clean and if Skyrim gets an update it will not break the Nolvus installation.' (https://www.nolvus.net/appendix/installer/faq ; https://www.nolvus.net/appendix/installer/tech ; https://raw.githubusercontent.com/vektor9999/NolvusDashboard/main/Vcc.Nolvus.Dashboard/Frames/Installer/StockGameFrame.cs)
- [high] Steam 'Update 1.7.99 (Updated Aug 27)' was posted 2026-08-20, with an additional hotfix on August 27. The notes mention 'localized strings fixes' but no new languages. SKSE lists 'Current Anniversary Edition build 2.3.1 (game version 1.7.104)' and a 2026-08-14 warning about an incoming update. That 1.7.104 is the Aug 27 hotfix build is an inference. (https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=489830 ; https://skse.silverlock.org/)
- [high] Dashboard GitHub releases:
- 3.8.11 (28 Aug): 'Added Downgrade signature info for Skyrim 1.7.104.0'
- 3.8.10 (21 Aug): 'Added languages pack management for Skyrim 1.7.99.0'
- 3.8.9 (20 Aug): 'Added Downgrade signature info for Skyrim 1.7.99.0'
- 3.8.8 (2026-03-02): CPU core count setting
- 3.8.7 (02-18): remap instance and long-path fix
- 3.8.5 (01-29): Oathvein UI, PICHO ENB, multi-instance tagging
- 3.8.4 (01-15): Graphics Only
The newest release is 3.8.11. Commits 'Update 3.8.12', '(2)' and '(3)' landed 2026-09-18, 09-23 and 09-24 but are not released. (https://github.com/vektor9999/NolvusDashboard/releases ; https://github.com/vektor9999/NolvusDashboard/commits/main)
- [medium] The 3.8.10 'languages pack management' commit (8f836c0) threads the selected language code into game-file patching. GameFile.IsPatchingRequired matches 'Skyrim - Voices_{lgcode}0.bsa', so only the chosen language's voice BSA is patched. No new languages were added. (https://github.com/vektor9999/NolvusDashboard/commit/8f836c03ac8d8ca6b6a4b365d4481eb0e90b9b9a)
- [high] The Dashboard language dropdown is hard-coded to EN, FR, IT, DE, ES, RU and PL. Its UI label reads 'Language only affects base game not the mods. Be sure you have setup the same language for Skyrim SE in steam too.' The install page says 'The language you select has to be the same than the one you selected in steam. Only the base game will be translated'. (https://raw.githubusercontent.com/vektor9999/NolvusDashboard/main/Vcc.Nolvus.Dashboard/Frames/Installer/SelectInstanceFrame.cs ; SelectInstanceFrame.Designer.cs ; https://www.nolvus.net/appendix/installer/install)
- [high] Steam officially lists Traditional Chinese (interface/subtitles, no full audio) for Skyrim Special Edition and the Anniversary Upgrade, alongside English, French, Italian, German, Spanish, Polish, Russian and Japanese. The Nolvus Dashboard does not offer Chinese, Japanese or Traditional Chinese. (https://store.steampowered.com/api/appdetails?appids=489830 ; https://store.steampowered.com/api/appdetails?appids=1746860)
- [high] Nexus: Premium is needed for automatic downloads. Without it you 'manually click for each mods' and total bandwidth is limited to 3 MB/s. Login is via Nexus SSO ('The Nolvus Dashboard is a nexus approved application'). A separate Nolvus website account is required, and the install page warns not to enter Nexus credentials there. (https://www.nolvus.net/appendix/installer/requirements ; https://www.nolvus.net/appendix/installer/install)
- [high] Download hazards:
- Error 402 on non-Nexus files: create a free mega.nz account, disable anonymous mode and enter your credentials.
- mega's 5 GB/day limit shows as error 509.
- Google Drive can return error 429.
- 'I'm from Russia/China/South America and i can't download some files': the answer is to use a VPN.
- Failed files can be downloaded manually via the nolvus.net search icon and dropped into cache\downloads. (https://www.nolvus.net/appendix/installer/faq)
- [high] Path rules:
- Don't run NolvusUpdater.exe from Desktop, Documents, Program Files (x86) or steamapps.
- 'x:\Nolvus (this kind of short path is mandatory if you want to install Nolvus Awakening v6)'.
- 'Nolvus Awakening (v6) WON'T BOOT if you DON'T INSTALL the Dashboard in a short path'.
- Do not move the Dashboard during installation.
- If %LOCALAPPDATA%\ModOrganizer exists, the Dashboard errors with 'Global ModOrganizer instance has been detected'. (https://www.nolvus.net/appendix/installer/install ; https://www.nolvus.net/appendix/installer/faq)
- [high] Folder layout (from source):
- Instances go in <Dashboard>\Instances\<Name>, or '<Name> - <Tag>' for tagged extra instances.
- Each instance has MO2\ModOrganizer.exe (portable) and NolvusLauncher.exe, plus MODS\{mods,downloads,overwrite,profiles,webcache}, STOCK GAME\ and TOOLS\SSE Edit.
- Archives go to Instances\ARCHIVE by default.
- InstancesData.xml carries the header 'DO NOT MODIFY this file yourself'.
- The cache is Cache\downloads|extract. Settings live in 'Nolvus Dashboard.ini'. (https://raw.githubusercontent.com/vektor9999/NolvusDashboard/main/Vcc.Nolvus.Package/Mods/ModOrganizer.cs ; .../Vcc.Nolvus.Instance/Core/NolvusInstance.cs ; .../Vcc.Nolvus.Instance/Services/InstanceService.cs ; https://www.nolvus.net/appendix/installer/tech)
- [high] v6 installer options (from source):
- Anti-aliasing: TAA, DLAA (NVIDIA RTX only) or FSR, with a Frame Generation toggle. Downscaling is incompatible with DLAA, FSR and Frame Generation.
- LODs for Ultra: Ultra, Performance or Ultra Performance. INI profile: Low, Medium or High.
- Aspect ratio: 16:9, 21:9 or 32:9. UI: Untarnished, Edge, Oathvein, Norden or Vel'dun. Combat addon: Conventional or Fantasy.
- Difficulty presets: Milk Drinker, Hack and Slash, True Nord, Prepare to Die (or Customized).
- Confirmation dialogs say the variant, options and difficulty cannot be changed after installation.
- The hardware check is advisory: it shows CPU, RAM, GPUs and a 'Supported GPUS' grid, then asks for confirmation. (https://raw.githubusercontent.com/vektor9999/NolvusDashboard/main/Vcc.Nolvus.Dashboard/Frames/Installer/v6/PerformanceFrame.cs ; .../OptionsFrame.cs ; .../DifficultyFrame.cs ; .../GPUFrame.cs)
- [high] On laptops the Dashboard may not recognize the NVIDIA GPU, which blocks selecting DLAA. Setting [Misc] ForceAA = True in 'Nolvus Dashboard.ini' bypasses the check and shows '(CHECK BYPASSED)'. Selecting DLAA without an NVIDIA card will crash the game. (https://www.nolvus.net/appendix/installer/tech ; PerformanceFrame.cs)
- [high] Customization rules:
- 'Never rename, delete or move a mod installed by the installer!!!'. To drop a mod, deactivate it.
- To modify or upgrade a mod (e.g. 4K), deactivate it, install a renamed copy and place it just before the original.
- New ESPs you add get placed at the end of the load order when the installer updates, so you manage load order yourself.
- Regenerated LODs and animations follow the same renamed-copy rule.
- If you heavily customize and still press Update you 'will get 100% chance of error'. (https://www.nolvus.net/appendix/installer/customization)
- [medium] 'No official support is given for modified installation. We have a channel dedicated for customized Nolvus on our discord'. This quote is from the v5 Ascension manual-guide setup page, not a v6 page. (https://www.nolvus.net/guide/asc/setup)
- [high] Install time is about 1 hour with Premium and a good connection (15 minutes with archives). Parallel downloads scale with CPU cores ([Process] Count; since 3.8.8 also set in the global settings). Retry defaults to 3 and ErrorsThreshold defaults to 50 (max 100). The installer resumes after closing. After installation the Dashboard is only needed for updates, settings or re-applying the default load order. Manage > Report to PDF exports instance data. (https://www.nolvus.net/appendix/installer/install ; https://www.nolvus.net/appendix/installer/tech ; https://www.nolvus.net/appendix/installer/faq)
- [high] Downloads page: NolvusUpdater.exe and a standalone 'Nolvus Downgrade Patcher' (DowngraderBinaries11.zip). Both are GitHub release assets from tag v3.5.23, under GPLv3. The downgrader is 'completely independant from the Nolvus mod lists'. Whether that old standalone build knows the 1.7.99/1.7.104 signatures was not verified. (https://www.nolvus.net/downloads/installer)
- [medium] The instance version comes from the Nolvus API (GetNolvusVersions, GetLatestPackage, GetGamePackage(Instance.Version)). The instance list shows a BETA disclaimer for beta packages. No UI to pick an older package such as 6.0.17 was found. (https://raw.githubusercontent.com/vektor9999/NolvusDashboard/main/Vcc.Nolvus.Instance/Core/NolvusInstance.cs ; .../SelectInstanceFrame.cs)
- [high] Load Order Library snapshots (API):
- nolvus0-20: no version field, created 2026-04-07 by Svartsot. 3,633 enabled mods, 70 separators, 19 disabled, 3,688 plugins. Ultimate without SREX; includes Twinblades of Skyrim and Animated Armoury (6.0.20 additions).
- victolvus: v6.00, created 2026-09-04, expires 2026-10-04, 'Nolvus forked with victis'. Ultimate without SREX, 3,815 enabled.
- nolvus-awekening-redux: v6.0.20, created 2025-02-08, updated 2026-05-29 by Railyn. Redux without SREX, 3,494 enabled, modlist only.
- nolvus-awakening-v6: 2025-02-09 by vg7307. Ultimate with SREX, 3,665 enabled.
- nolvus-v6-ultimate-open-beta-start: 2024-12-28. Ultimate without SREX (Synthesis Patch - NOSREX, DynDOLOD - Output - Ultimate (NO SREX)), 3,480 enabled. (https://api.loadorderlibrary.com/v1/lists/<slug>)
- [high] Overlap with the user's 4,044 enabled mods: nolvus0-20 2,950, victolvus 2,961, redux 2,864, nolvus-awakening-v6 (2025-02) 2,767, open-beta 2,743, official website list (all variants) 2,920. 174 of the 716 'neither' mods are in the current official list. 129 enabled mods and 53 plugins contain 'Nolvus'. (local analysis: user__modlist.txt, user__plugins.txt, neither_mods.txt vs https://www.nolvus.net/awakening and the LOL API)
- [medium] The target's Nolvus content is about 6.0.17. From the changelog's 'Added new mod' entries it has 6.0.17 (1/1), 6.0.16 (1/1), 6.0.15 (86/135), 6.0.14 (27/42) and 6.0.7 (41/52), but 0/7 of 6.0.18, 0/7 of 6.0.19 and 0/28 of 6.0.20. (local analysis: user__modlist.txt vs https://www.nolvus.net/appendix/history)
- [high] The target list is a Community Shaders build, not ENB.
- It contains 'CommunityShaders_AIO-2026-05-28T17-09Z', 'CS shaders', 'NAT.CS III', 'Vanilla CS rain TEXTURES', 'Lux (cs)', 'Lux Orbis cs', 'Dancing LUX CS', 'CS Lights2', 'Light Placer', 'Water for ENB [cs]2' and 'pgpatcher_output'.
- It has no ENB Binaries, KiLoader, ENB Extender or any ENB preset mod.
- The '11. ENB & RESHADE' separator holds paper-map mods; 'MV - ENB' and 'CS' are disabled separators.
- KreatE and Native EditorID Fix, the only 'Kauz ENB'-tagged rows present, are also in the Mages & Vikings list. (local analysis: user__modlist.txt (lines 1-110) vs https://www.nolvus.net/awakening and mages-vikings__modlist.txt)
- [high] The target replaces Nolvus' generated outputs and behavior engine.
- No 'Synthesis Patch*', 'DynDOLOD - Output - Ultimate (NO SREX)', 'Grass Cache - Ultimate', 'LODGEN' or 'Nemesis Output'.
- Instead: 'dyndolodCS2', 'texgenCS', 'grass CS', 'lodgen2', 'SYNTHESSIS', 'pgpatcher_output', 'Pandora Output' and 'Pandora Behaviour Engine v4.3.1-beta'.
- So the user regenerated LODs, grass, Synthesis, ParallaxGen/PGPatcher and behaviors for their own list. (local analysis: user__modlist.txt)
- [medium] Nolvus install options inferred from option tags:
- Ultimate without SREX: 19 of 77 Ultimate-only rows present, 0 of 180 SREX rows.
- Edge UI; 16:9 (no 21:9 or 32:9 rows).
- Fantasy Combat Addon (21/21 present; Conventional 0/13).
- Alternate Leveling (10/10), Boss Encounter (11/12), Gore (5/6), Exhaustion (2/2); Enemies Resistance 1/4 and Stances Perk Tree 1/4 (partial).
- Difficulty True Nord ('Combat Scaling Overhaul - Moderate' present; Milk Drinker/Hack and Slash/Prepare to Die rows absent).
- BodySlide (Dressed). (local analysis: user__modlist.txt vs option tags at https://www.nolvus.net/awakening)
- [medium] Community full-text translation patches for Nolvus v6 exist on Nexus:
- French: 'Nolvus Awakening V6.0.19 - Patch Francais Non Officiel', mod 164621.
- Italian: mod 171712, updated about Feb 2026.
- Also Turkish (164744), Brazilian Portuguese (164341) and Spanish ('Traduccion Nolvus 6.0.14', 163858).
No Chinese one was found on Nexus. (https://www.nexusmods.com/skyrimspecialedition/mods/164621 ; https://www.nexusmods.com/skyrimspecialedition/mods/171712 ; https://www.nexusmods.com/skyrimspecialedition/mods/164744 ; https://www.nexusmods.com/skyrimspecialedition/mods/163858 (titles via web search; Nexus returned 403 to direct fetch))
- [low] A community Simplified-Chinese Nolvus translation exists off-Nexus. Bilibili video BV1o5EPzPEWw is titled 'nolvus6.12完美汉化 发布【张裕汉化】', uploaded 2025-05-14 by 精灵团娜娜. It credits 小寶與劍魂 and links an afdian page. '6.12' probably means 6.0.12. Contents, completeness and licensing are unverified. (https://www.bilibili.com/video/BV1o5EPzPEWw/)
- [low] Estimated mod counts per configuration (TAA, Cabbage, 16:9, Untarnished, addons none or all): Ultimate without SREX about 3,643–3,697; with SREX about 3,785–3,839; Ultra 3,614–3,797; Redux 3,558–3,722; Graphics Only 1,612–1,719. Not re-verified; tag semantics are partly inferred. (local analysis by the original agent of https://www.nolvus.net/awakening)

## RISKS
- CORRECTION: The target list is NOT a Kauz ENB setup. It is a Community Shaders build: CommunityShaders_AIO-2026-05-28, NAT.CS III, Lux (cs), Light Placer, CS Lights and pgpatcher_output, with no ENB Binaries or ENB preset. KreatE and Native EditorID Fix, the only Kauz-tagged mods present, also come from Mages & Vikings. The Dashboard's ENB choice therefore barely matters for the target, since all ENB content ends up disabled.
- CORRECTION: The target uses Pandora Behaviour Engine 4.3.1-beta and Pandora Output instead of Nolvus' Nemesis 0.84b and Nemesis Output. It also has none of Nolvus' generated outputs (Synthesis Patch, DynDOLOD/LODGEN/Grass Cache outputs), using self-generated dyndolodCS2, texgenCS, grass CS, lodgen2, SYNTHESSIS and pgpatcher_output instead. Installing Nolvus does NOT supply these outputs. They must be regenerated for the final hybrid list (DynDOLOD/TexGen, grass cache, Synthesis, PGPatcher/ParallaxGen, Pandora), which takes many hours of tool runs and is a major laptop bottleneck.
- CORRECTION: Steam officially offers Traditional Chinese (text/subtitles) for Skyrim SE and the AE Upgrade. The earlier open question saying Steam Skyrim has no official Chinese option is wrong. But the Nolvus Dashboard only offers EN/FR/IT/DE/ES/RU/PL and says the Steam language must match. If Steam is set to Traditional Chinese, the Dashboard's integrity and patch steps may fail (unverified), so keep Steam on English during the Nolvus install.
- CORRECTION: The Dashboard's current v6 ENB list (main-branch source) has four entries (Cabbage, Kauz, PiCho, Amon Reborn), not three.
- CORRECTION: The LOL snapshot 'nolvus-v6-ultimate-open-beta-start' is Ultimate WITHOUT SREX (Synthesis Patch - NOSREX, DynDOLOD - Output - Ultimate (NO SREX)), not 'SREX files present'. 'nolvus-awekening-redux' was created 2025-02-08 and last updated 2026-05-29.
- CORRECTION: ForceAA=True does not generally fix GPU detection. It bypasses the check so DLAA can be selected, and DLAA without an NVIDIA card crashes the game.
- CORRECTION: The mega.nz daily-limit error is 509. Error 402 is fixed by creating a free mega account and disabling anonymous mode.
- CORRECTION: The 'no official support for modified installation' quote comes from the v5 Ascension manual-guide page. The v6 installer customization page instead warns that pressing Update after heavy customization gives '100% chance of error'.
- CORRECTION (clarification): Dashboard 3.8.10's 'languages pack management' only patches the selected language's 'Skyrim - Voices_<lg>0.bsa'. It adds no languages.
- Version drift: the Dashboard installs the current package (6.0.20, or 6.0.21 when it leaves beta), not the ~6.0.17 base the target was built on. Nolvus patch plugins, 6.0.15-era requirements and changed mod versions will differ. The target's Community Shaders build is dated 2026-05-28, so the list was maintained into mid-2026 with non-Nolvus updates.
- Laptop hardware: v6 minimums are desktop cards, from 8 GB VRAM (Redux without SREX) to 14–18 GB (Ultimate). The target is Ultimate-based with 4,044 mods plus MV content. Community Shaders is usually cheaper than ENB, but texture VRAM (4K-2K Ultimate textures) still dominates. Mobile GPUs are slower than same-named desktop parts (inference).
- Disk: Ultimate needs 426 GB installed plus up to 193 GB of archives, plus extraction cache, a 20–40 GB page file, Steam's own copy and the Mages & Vikings install. All game data must be on an SSD.
- Game version: Steam is now 1.7.99/1.7.104 (Aug 2026). The Dashboard (3.8.11+) handles it, but the standalone Nolvus Downgrade Patcher (release v3.5.23) and Wabbajack lists such as MV (1.5.97 Best of Both Worlds) may not recognise the new executable hashes. Unverified here.
- Chinese: no official or Nexus Chinese translation of Nolvus v6 was found. The only one is a Bilibili/afdian 'nolvus6.12' (probably 6.0.12) Simplified-Chinese pack of unknown scope and license. The 129 Nolvus-authored mods and 53 Nolvus plugins need custom translation. Edge UI/Sanguis font mods may lack CJK glyphs; Nolvus ships Scaleform Translation Plus Plus NG and an 'Edge UI - Missing Font Patch', but CJK coverage is unverified.
- Install options (variant, LODs, ratio, UI, addons, difficulty, ENB, DLAA) cannot be changed after install; a wrong choice means reinstalling from archives. Short path mandatory (v6 'WON'T BOOT' otherwise). A global %LOCALAPPDATA%\ModOrganizer folder blocks the Dashboard. mega/Google Drive quotas and regional blocks: the FAQ explicitly lists China, and Taiwan's status is unknown.

## RECS
- Before installing Nolvus:
1. Update Steam Skyrim to the current build (1.7.104).
2. Set Steam's game language to ENGLISH, since the Dashboard language must match Steam and has no Chinese.
3. Launch the game once and download all Creations.
4. Remove %LOCALAPPDATA%\ModOrganizer if it exists.
5. Set a 20000–40000 MB page file on the NVMe SSD.
6. Create a Nolvus account and a free mega.nz account.
- Put NolvusUpdater.exe in a short root folder on an NVMe SSD (e.g. D:\Nolvus) and make sure the Dashboard is 3.8.11 or newer. Log in with Nexus SSO (Premium) and your Nolvus account, and choose English.
- To gather assets for the target, install Ultimate without SREX with:
- Edge UI, 16:9, BodySlide Dressed
- Fantasy Combat, Boss Encounter, Alternate Leveling, Gore, Exhaustion, Enemies Resistance and Stances Perk Tree addons
- True Nord difficulty
The ENB choice barely matters because the target replaces ENB with Community Shaders; confirm with the user. Keep archiving on (archives can go on an HDD) so the hybrid build and any reinstall reuse downloads.
- Treat the Nolvus instance as read-only source data. Build the hybrid in a separate MO2 instance or profile and never press Update on it. Follow the customization rules: deactivate rather than delete, and place renamed modified copies before the originals.
- Plan explicit regeneration steps for the hybrid, because the target does not use Nolvus outputs:
- Pandora behaviors (instead of Nemesis)
- PGPatcher/ParallaxGen
- Synthesis
- TexGen and DynDOLOD
- Grass cache
- Community Shaders install and settings
Budget hours of tool runs and verify each tool supports the chosen 1.5.97 runtime.
- Use https://www.nolvus.net/awakening (4,250 rows with option tags) and the history page as the authoritative diff source. Use LOL 'nolvus0-20' (Ultimate without SREX, about 6.0.20) as the closest vanilla load-order reference. Re-run the 'neither' analysis against the official list: 174 of the 716 are current Nolvus mods.
- For Chinese:
1. Verify an English build first.
2. Then add Chinese as a separate top-priority mod group:
   - Base game and AE Creations strings: Steam officially offers Traditional Chinese text, so the official strings could be sourced from a Traditional-Chinese Steam install. Test on a copy, since STOCK GAME is down-patched.
   - Per-mod ESP/MCM/interface translations.
   - Custom translations for the Nolvus-authored patches, using the FR/IT Nexus Nolvus translation patches as a structural model.
3. Evaluate the Bilibili 'nolvus6.12' Chinese pack only after checking version match and licensing.
- Laptop tuning: in NVIDIA Control Panel set 'Prefer Maximum Performance' for SkyrimSE.exe and force the dGPU. Use ForceAA=True only if the Dashboard can't see a real NVIDIA RTX GPU and you want DLAA. If VRAM is 12 GB or less, plan texture downscaling or 2K swaps in the hybrid, keep SREX off, or install a tagged Redux instance (3.8.5+) as a fallback.

## OPEN
- What are the laptop's exact specs: GPU model and VRAM, RAM, CPU, free NVMe space, and screen resolution and aspect ratio?
- Does the Dashboard's integrity check or patching fail if Steam is set to Traditional Chinese? If so, the user must stay on English until STOCK GAME is built.
- How were the target's Traditional/Simplified Chinese strings meant to be sourced? Should Nolvus-authored patches be translated by hand, or with a tool such as xTranslator/ESP-ESM Translator batch dictionaries?
- Can the Dashboard install an older package such as 6.0.17 to match the target? No such UI was found; it appears to install the latest only.
- Will 6.0.21 (currently beta) go live during the project, and what will Dashboard 3.8.12 (commits Sep 18–24, 2026) change?
- Do the standalone Nolvus Downgrade Patcher (v3.5.23 assets) and the Mages & Vikings Wabbajack game-file hashes support Steam 1.7.99/1.7.104 executables?
- Which Community Shaders build and add-ons does the target use (CommunityShaders_AIO-2026-05-28 is a user-packed AIO)? Are they compatible with the 1.5.97 runtime the list runs on?
- What does the target use for Pandora and Synthesis settings, and for the DynDOLOD/TexGen/grass-cache parameters, to reproduce its self-generated outputs?
- What is the official RAM requirement for v6? It is not stated; v5 listed 32 GB.

## DATA
NOLVUS v6 REQUIREMENTS (verified at nolvus.net/appendix/installer/requirements, 2026-09-25)
Variant / SREX           | Min 1080p (VRAM, GPU)   | Rec 1080p              | CPU      | Installed | Download (optional)
Ultimate, no SREX        | 14 GB, RTX 4060 Ti      | 14 GB, RTX 4070 Ti S   | i7-10xxx | 426 GB    | 193 GB   (1440p 15 GB, 4K 16 GB)
Ultimate, SREX           | 16 GB, RTX 4080         | 16 GB, RTX 4080 S      | i7-10xxx | 426 GB    | 193 GB   (1440p 17, 4K 18)
Ultra, no SREX (Perf/Ultra/UltraPerf LODs) | 10 GB 3080 / 11 GB 3080 Ti / 10 GB 2080 Ti | 10 GB 3080 Ti / 11 GB 4070 / 10 GB 3080 | i7-10xxx | 406 GB | 188 GB
Ultra, SREX              | 13-14 GB, RTX 4060 Ti   | 13-14 GB, 4070 Ti S    | i7-10xxx | 406 GB    | 188 GB
Redux, no SREX           | 8 GB, GTX 1080          | 8 GB, RTX 2070         | i7-7xxx  | 372 GB    | 170 GB   (1440p 10 GB 1080 Ti)
Redux, SREX              | 10 GB, GTX 1080 Ti      | 10 GB, RTX 3080        | i7-10xxx | 372 GB    | 170 GB
Graphics Only, no SREX   | 11 GB, RTX 3080 Ti      | 11 GB, RTX 4070        | i7-10xxx | 235 GB    | 105 GB
Graphics Only, SREX      | 14 GB, RTX 4060 Ti      | 14 GB, 4070 Ti S       | i7-10xxx | 235 GB    | 105 GB
No RAM figure for v6 (v5 tables: 32 GB). Optional: .NET 5.0 SDK.

OFFICIAL LIST KEY RUNTIME ROWS (nolvus.net/awakening; 68 categories, 4,250 rows)
SKSE 2.0.0.20 | SSE Fixes 3.1.5.97 | BEES 1.2 | SSE Engine Fixes 7.0.20 | Crash Logger - 1.5.97 1.15.0 | Address Library 2.0 | Scaleform Translation++ NG 1.6 | ENB Binaries 0.505 | Amon ENB 5.0 | Reshade 6.3.1 | Nemesis Unlimited 0.84b + Nemesis Output 6.0.21 | Community Shaders: none | Rows at 6.0.21: 202

DASHBOARD (github releases/commits)
3.8.11 (Aug 28 2026) 1.7.104 downgrade signature | 3.8.10 (Aug 21) language-pack patching (Voices_<lg>0.bsa) | 3.8.9 (Aug 20) 1.7.99 signature | 3.8.8 (Mar 2) CPU cores setting | 3.8.7 (Feb 18) remap and long-path fix | 3.8.5 (Jan 29) Oathvein UI, PICHO ENB, instance tags | 3.8.4 (Jan 15) Graphics Only | 3.8.12 commits Sep 18/23/24 (unreleased)
Languages: EN FR IT DE ES RU PL (Steam Skyrim SE also offers Traditional Chinese and Japanese; the Dashboard does not)
v6 ENBs (source): Cabbage, Kauz, PiCho, Amon Reborn

USER TARGET vs NOLVUS (local)
Nolvus changelog additions present: 6.0.20 0/28 | 6.0.19 0/7 | 6.0.18 0/7 | 6.0.17 1/1 | 6.0.16 1/1 | 6.0.15 86/135 | 6.0.14 27/42 | 6.0.13 11/25 | 6.0.7 41/52 -> Nolvus base about 6.0.17
Options: Ultimate (19/77 Ultimate-only rows present, city overhauls removed), no SREX (0/180), Edge UI, 16:9, Fantasy Combat 21/21, Alternate Leveling 10/10, Boss Encounter 11/12, Gore 5/6, Exhaustion 2/2, Enemies Resistance 1/4, Stances 1/4, True Nord 1/1, BodySlide Dressed
Graphics: Community Shaders (CommunityShaders_AIO-2026-05-28T17-09Z, CS shaders, NAT.CS III, Lux cs, Light Placer, pgpatcher_output). No ENB binaries or presets. Behavior engine: Pandora 4.3.1-beta. Outputs self-generated: dyndolodCS2, texgenCS, grass CS, lodgen2, SYNTHESSIS, Pandora Output.
Name overlap with the user's 4,044 enabled mods: official list 2,920 | nolvus0-20 2,950 | victolvus 2,961 | redux 2,864 | v6 (2025-02) 2,767 | open-beta 2,743. 'neither' mods in the official list: 174/716. 'Nolvus' in name: 129 mods, 53 plugins.

LOAD ORDER LIBRARY
nolvus0-20 (2026-04-07, Svartsot): Ultimate, no SREX, about 6.0.20, 3,633 enabled / 70 separators / 19 disabled / 3,688 plugins
victolvus (v6.00, 2026-09-04, expires 2026-10-04): Victis fork, Ultimate, no SREX, 3,815 enabled
nolvus-awekening-redux (v6.0.20, created 2025-02-08, updated 2026-05-29, Railyn): Redux, no SREX, 3,494 enabled
nolvus-awakening-v6 (2025-02-09): Ultimate WITH SREX, 3,665 enabled
nolvus-v6-ultimate-open-beta-start (2024-12-28): Ultimate, NO SREX, 3,480 enabled

TRANSLATIONS FOUND
Nexus: FR 164621 (v6.0.19), IT 171712, TR 164744, PT-BR 164341, ES 163858 (6.0.14). Chinese: only off-Nexus, Bilibili BV1o5EPzPEWw 'nolvus6.12完美汉化' (2025-05-14; credits 小寶與劍魂; afdian link).