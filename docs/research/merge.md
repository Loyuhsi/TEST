# merge

## SUMMARY
Most of the merge research holds up against primary sources: MO2 source code, Nolvus Dashboard source, nolvus.net, Wabbajack source and wiki, the Nexus API docs and live calls, Microsoft docs, dyndolod.info, and a recount of the local files. The plan itself still stands: install both base lists, then build a separate third portable MO2 instance whose mod folders are NTFS hardlink clones, and download only the missing mods.

Four corrections change what the user should actually do:

1. **Missing mod folders are dropped, not shown.** When MO2 loads a profile, any modlist.txt line whose folder is missing is thrown away and the file is rewritten (profile.cpp). Plugins behave the same way. So before the first MO2 launch, create every target folder (placeholders are fine) and keep an untouched backup of both txt files.
2. **loadorder.txt is optional in a new profile.** If it is missing, MO2 takes the order from plugins.txt. If it exists, it wins when MO2 starts.
3. **The two base lists run different game versions.** The M&V changelog says v2.5 moved the list from 1.5.97 to 1.6.1170. Nolvus v6 runs 1.5.97 (it uses BEES and the Dashboard downgrader). The target's SKSE, Address Library, 'Crash Logger - 1.5.97' and 'Dynamic Armor Variants for Skyrim 1.5' are Nolvus copies, so the target runs 1.5.97. Every SKSE DLL taken from M&V has to be checked against 1.5.97.
4. **The unidentified-mod count shifts a little.** Recounting against both Nolvus snapshots gives 2614 Nolvus-only, 541 M&V-only, 343 in both and 546 in neither. About 67-70 of those are renames ending in a digit, which leaves roughly 470-480 to identify (not 493). The per-section 'none' counts in the original data block were wrong.

Smaller corrections:
- Current ReFS docs say ReFS supports hard links.
- In ModOrganizer.ini, gamePath is written as @ByteArray(...) under [General], and the directory keys belong under [Settings].
- The target has no Seasons of Skyrim.
- Three ESMs load after DynDOLOD.esm.

New facts that matter:
- **Plugin headroom:** 4244 target plugins plus 79 primary plugins make 4323. The hard cap is 254 full + 4096 light = 4350, so there are only about 27 spare slots.
- **Language settings conflict:** the Nolvus language must match the Steam language, but M&V requires Steam set to English. Skyrim SE officially supports Traditional Chinese as text only.
- **Nolvus Redux variant:** 372 GB installed + 170 GB archives, 8 GB VRAM at 1080p.
- **Shaders:** M&V 2.6.1+ ships Kauz ENB by default, and Nolvus v6 offers only ENB presets. The target uses Community Shaders.

## FACTS
- [high] MO2 writes modlist.txt from highest to lowest priority: the top line is the highest priority and the bottom line the lowest. '+' means enabled and '-' disabled. '*' marks a foreign entry and is read like '+'. Separators are folders whose names end in '_separator'. The file is read and written as UTF-8. (https://github.com/ModOrganizer2/modorganizer/blob/master/src/profile.cpp (refreshModStatus / doWriteModlist); https://github.com/ModOrganizer2/modorganizer/blob/master/src/modinfo.cpp (isSeparatorName '.*_separator'); https://www.nolvus.net/appendix/installer/customization)
- [high] When MO2 loads a profile, it discards any modlist.txt entry whose mod folder does not exist (it only logs 'mod not found' at debug level). It then rewrites modlist.txt without those entries. Mods found in mods\ but not listed get high priority, above the listed mods. (https://github.com/ModOrganizer2/modorganizer/blob/master/src/profile.cpp (refreshModStatus: modIndex==UINT_MAX -> modStatusModified=true -> m_ModListWriter.write()))
- [high] How MO2 (SSE plugin, GamebryoGamePlugins/CreationGamePlugins) picks the plugin order:
- At MO2 startup (m_LastRead invalid), or whenever loadorder.txt is newer, the order comes from loadorder.txt and the enabled state from plugins.txt.
- If loadorder.txt does not exist, reading it fails and MO2 falls back to plugins.txt for the order.
- If only plugins.txt changed since the last read, plugins.txt sets the order.
- plugins.txt is written with '*' marking an enabled plugin; primary plugins (base game, DLC and the CC files in Skyrim.ccc) are not written. (https://github.com/ModOrganizer2/modorganizer-game_gamebryo/blob/master/src/gamebryo/gamebryogameplugins.cpp (readPluginLists, readLoadOrderList); https://github.com/ModOrganizer2/modorganizer-game_gamebryo/blob/master/src/creation/creationgameplugins.cpp)
- [high] MO2 portable mode is triggered by portable.txt next to ModOrganizer.exe; the config file is ModOrganizer.ini.
- Default sub-folders: mods, profiles, downloads, overwrite, webcache.
- base_directory, download_directory, mod_directory, profiles_directory, overwrite_directory and cache_directory go under [Settings].
- gameName, gamePath and selected_profile go under [General]; gamePath and selected_profile are stored as @ByteArray(...), as the Nolvus template writes them. (https://github.com/ModOrganizer2/modorganizer/blob/master/src/shared/appconfig.inc ; https://github.com/ModOrganizer2/modorganizer/blob/master/src/settings.cpp ; https://github.com/vektor9999/NolvusDashboard/blob/main/Vcc.Nolvus.Package/Mods/ModOrganizer.cs (IniFile template))
- [high] MO2 meta.ini [General] keys include modid, version, newestVersion, installationFile, repository, gameName, url, nexusFileStatus and category; an [installedFiles] array holds modid/fileid pairs. MO2 download .meta files hold gameName, modID, fileID, url, name, modName, version, fileTime, installed, uninstalled, removed and more. (https://github.com/ModOrganizer2/modorganizer/blob/master/src/modinforegular.cpp ; https://github.com/ModOrganizer2/modorganizer/blob/master/src/downloadmanager.cpp)
- [high] MO2's mod-list CSV export can include #Mod_Priority, #Mod_Status, #Mod_Name, #Primary_Category, #Nexus_ID, #Mod_Nexus_URL, #Mod_Version, #Install_Date and #Download_File_Name. It has no Nexus file ID column. The file ID can be recovered by matching #Download_File_Name against GraphQL modFiles. (https://github.com/ModOrganizer2/modorganizer/blob/master/src/modlistviewactions.cpp)
- [high] Nolvus Dashboard instance layout: <Inst>\MO2 and <Inst>\MODS\{downloads, mods, overwrite, profiles\<Instance.Name>, webcache}. gamePath points to <Inst>\STOCK GAME. The ModOrganizer.ini template has version=2.4.4 and settings for an MO2 plugin called 'CRDW Automatic Mode'. The MO2 executables it adds are Nolvus launcher, SKSE, SkyrimSE, the Launcher, Explorer++, Nemesis, xEdit (TOOLS\SSE Edit), 'xEdit Cleaning' (SSEEditQuickAutoClean) and BodySlide. (https://github.com/vektor9999/NolvusDashboard/blob/main/Vcc.Nolvus.Package/Mods/ModOrganizer.cs ; https://www.nolvus.net/appendix/installer/tech)
- [high] Nolvus writes each mod's meta.ini with modid, version, installationFile and [installedFiles] 1\modid / 1\fileid. Non-Nexus mods get modid=0 and fileid=0. No gameName is written. Archives are verified by CRC32, and no MO2 .meta files were found in the archive-handling code. (https://github.com/vektor9999/NolvusDashboard/blob/main/Vcc.Nolvus.Package/Mods/MOElement.cs ; .../Mods/NexusMod.cs ; .../Mods/Mod.cs (line ~226) ; .../Files/ModFile.cs)
- [high] On install or apply-order, the Nolvus Dashboard rewrites MODS\profiles\<Instance>\modlist.txt, loadorder.txt and plugins.txt. Before (re)installing a mod, PrepareDirectrory deletes that mod's folder and creates it again. (https://github.com/vektor9999/NolvusDashboard/blob/main/Vcc.Nolvus.Dashboard/Frames/Installer/LoadOrderFrame.cs ; https://github.com/vektor9999/NolvusDashboard/blob/main/Vcc.Nolvus.Package/Mods/Mod.cs)
- [high] Official Nolvus customization rules:
- Never rename, delete or move an installer mod; deactivate it instead.
- A customized copy gets a new name and goes just before the original.
- Plugins the installer doesn't know end up at the end after each update.
- An extra profile shares the mods folder and must be re-sorted after every update.
- If you customize heavily, never press update again: '100% chance of error'. (https://www.nolvus.net/appendix/installer/customization)
- [high] Nolvus install rules:
- v6 won't boot unless the Dashboard is in a short path such as X:\Nolvus.
- Never install the list on an HDD; the archive directory may be on an HDD.
- Don't edit InstancesData.xml.
- A Nolvus website account is required (in addition to Nexus SSO); some files need a mega.nz account.
- The Dashboard language must match the Steam language, and only the base game is translated, not the mods. (https://www.nolvus.net/appendix/installer/install ; https://www.nolvus.net/appendix/installer/faq ; https://www.nolvus.net/appendix/installer/requirements)
- [high] Nolvus Awakening v6 requirements per nolvus.net. Size is installed + archives; archives are optional. VRAM is the minimum at 1920x1080.

| Variant | Size | VRAM at 1080p |
| --- | --- | --- |
| Ultimate | 426 GB + 193 GB | 14 GB (RTX 4060 Ti); 16 GB with SR Exterior Cities |
| Ultra | 406 GB + 188 GB | 10-11 GB depending on LOD; 13-14 GB with SR Exterior Cities |
| Redux | 372 GB + 170 GB | 8 GB (GTX 1080 min, RTX 2070 recommended); 10 GB with SR Exterior Cities |
| Graphics Only | 235 GB + 105 GB | not recorded here |

32 GB RAM is listed only for the v5 variants. (https://www.nolvus.net/appendix/installer/requirements)
- [high] Nolvus v6 Dashboard options:
- Variants: Ultimate, Ultra, Redux.
- Optional SR Exterior Cities.
- TAA or DLAA (DLAA needs NVIDIA RTX; laptops may need [Misc] ForceAA=True).
- ENB presets: Cabbage, Cabbaval, KAUZ, PI-CHO. There is no Community Shaders option.
- Most options can't be changed after install.
- In Nolvus's own guide, ENB and ReShade binaries go into the STOCK GAME root. (https://www.nolvus.net/appendix/installer/install ; https://www.nolvus.net/appendix/installer/tech ; https://www.nolvus.net/guide/asc/enb)
- [high] Nolvus Dashboard releases:
- v3.8.11 (28 Aug): 'Added Downgrade signature info for Skyrim 1.7.104.0'.
- v3.8.10: 'Added languages pack management for Skyrim 1.7.99.0'.
- v3.8.7: remap an instance to another directory.
- v3.8.5: several instances of the same list via tags. (https://github.com/vektor9999/NolvusDashboard/releases)
- [high] Mages & Vikings 2.6.2 (gallery metadata, updated 2026-09-05):
- 3,772 archives, 229,998,290,486 bytes (about 230 GB).
- 374,545 files, 386,316,461,236 bytes (about 386 GB) installed; 616 GB total.
- The .wabbajack file is 5,416,496,998 bytes.
- Nexus Collection 503539 (slug agq2zq); author SEEYOULHATER. (https://raw.githubusercontent.com/nicolasbertolino/MagesAndVikings/main/modlists.json)
- [high] Mages & Vikings README pre-install requirements:
- Steam game with all Creation Club content, updated to 1.7.104.
- Steam overlay off.
- Steam game language set to English.
- Run the game once and let the CC content download.
- VC++ redistributable, .NET 6 desktop runtime and .NET 8 desktop runtime.
- Recommended hardware: RTX 4070+ and 32 GB RAM.
- Downloads can be deleted after install but must be downloaded again for updates. (https://github.com/nicolasbertolino/MagesAndVikings/blob/main/README.md)
- [high] Mages & Vikings changelog:
- v2.5: 'The list has been updated from version 1.5.97 to version 1.6.1170.' So M&V 2.6.2 runs SkyrimSE 1.6.1170, not 1.5.97 or Best of Both Worlds.
- v2.6.1: 'the list now ships with Kauz ENB enabled by default'.
- The list uses its own MO2 plugin ('Mod Bundle Trigger'). (https://gist.github.com/nicolasbertolino/a303a48fcc5f22a0c0e37822a7b786e9)
- [high] The target runs 1.5.97 on the Nolvus base. Its lowest-priority base layer is Nolvus's: 'Skyrim Script Extender', 'Skyrim Script Extender - Nolvus Settings', Address Library in '1.1 SKSE PLUGINS'. It also has 'Crash Logger - 1.5.97', 'Dynamic Armor Variants for Skyrim 1.5' and 'Backported Extended ESL Support'. It does not include M&V's '1.6.1170 Missing Files', 'AddItemMenu AE', 'Cleaned Vanilla Masters' or 'Creation Club' base mods. (local analysis: user__modlist.txt lines 3990-4139 vs mages-vikings__modlist.txt lines 1-20)
- [high] The Wabbajack Stock Game method keeps a copy of the game in the MO2 folder, so several lists can coexist and game updates can't break them; it costs about 12 GB. Install location rules: not the Wabbajack folder, not the game folder, not the same folder as another list ('lists can't be merged'), not an OS-managed folder. The downloads folder can be shared. (https://wiki.wabbajack.org/modlist_author_documentation/Keeping%20the%20Game%20Folder%20clean.html ; https://wiki.wabbajack.org/user_documentation/Installing%20a%20Modlist.html)
- [high] The Wabbajack installer:
- forces portable.txt and writes download_directory into ModOrganizer.ini;
- writes a .meta file for each download;
- on reinstall/update, deletes every file not in the modlist after confirmation. It keeps the downloads folder, the .wabbajack file, anything under profiles\<p>\saves, paths containing '[NoDelete]' (spaces ignored) and up-to-date BSAs. (https://github.com/wabbajack-tools/wabbajack/blob/main/Wabbajack.Installer/StandardInstaller.cs ; https://github.com/wabbajack-tools/wabbajack/blob/main/Wabbajack.Installer/FileDeletionRules.cs ; https://github.com/wabbajack-tools/wabbajack/blob/main/Wabbajack.Installer/AInstaller.cs)
- [high] A .wabbajack file is a zip holding a 'modlist' JSON. Archives[] entries carry Hash (xxHash64), Meta, Name, Size and State. For Nexus files, State is 'NexusDownloader, Wabbajack.Lib' with GameName, ModID, FileID, Name, Author and Version. SSE is Nexus 'skyrimspecialedition', Nexus game id 1704, MO2 archive name 'skyrimse'. (https://github.com/wabbajack-tools/wabbajack/blob/main/Wabbajack.DTOs/Archive.cs ; .../Wabbajack.DTOs/DownloadStates/Nexus.cs ; .../Wabbajack.DTOs/Game/GameRegistry.cs)
- [high] wabbajack-cli verbs include compile, install, download-all, download-url (-u url, -o output, -p proxy default true), modlist-report, install-compile-install-verify and verify-modlist-install. Wabbajack authoring rules:
- Use the zipped MO2 release.
- Never upload VRAMr or ParallaxGen output folders wholesale. (https://wiki.wabbajack.org/wabbajack_cli/Commands.html ; https://github.com/wabbajack-tools/wabbajack/blob/main/Wabbajack.CLI/Verbs/DownloadUrl.cs ; https://wiki.wabbajack.org/modlist_author_documentation/Pre-Compilation.html)
- [high] Nexus API v1 download_link.json (apikey header): Premium users get an array of CDN links, preferred location first. Non-Premium users must pass key and expires from an nxm link. Errors: 403 without Premium, 404 file not found, 410 link expired. The md5_search endpoint returns HTTP 401 without a key (tested live). (https://api.swaggerhub.com/apis/NexusMods/nexus-mods_public_api_params_in_form_data/1.0 ; live curl 2026-09-25)
- [high] Nexus API limits: 20,000 requests per 24 hours, then 500 per hour, resetting at 00:00 GMT (the older Swagger text still says 2,500/day). The API policy tolerates a personal key only for personal or in-testing apps. It requires Application-Name and Application-Version headers and forbids mass fetching to rehost data. ToS §10 bans downloading 'in a manner that significantly exceeds normal and expected usage'; §11 bans bots, scrapers and data mining. (https://help.nexusmods.com/article/105-i-have-reached-a-daily-or-hourly-limit-api-requests-have-been-consumed-rate-limit-exceeded-what-does-this-mean ; https://help.nexusmods.com/article/114-api-acceptable-use-policy ; https://help.nexusmods.com/article/18-terms-of-service)
- [high] Nexus GraphQL v2 (POST https://api.nexusmods.com/v2/graphql) answered three queries without login in live tests:
- modFiles(modId, gameId:1704) lists files including ARCHIVED ones (tested on USSEP).
- modFileContents(filter:{gameId:[{value:1704}] (Int), fileNameWildcard:[{value:'X.esp', op:EQUALS}]}) returns filePath, fileId and modId (tested on FWMF_Darkend.esp).
- fileHash(md5) returns matching files. (live queries against https://api.nexusmods.com/v2/graphql on 2026-09-25)
- [high] Since July 2021, Nexus archives mod files instead of deleting them. Archived files stay downloadable through collections and, outside collections, with the mod ID and file ID. Authors could ask for their files to be deleted until 5 Aug 2021. The Wabbajack wiki notes 'the Nexus no longer deleting files'. (https://www.nexusmods.com/news/14538 ; https://wiki.wabbajack.org/technical_talk/Auto-healing%20&%20Force-healing%20Overview.html)
- [high] Hard links are file-only and must stay on one volume, with at most 1023 links per file. Changes to a hard-linked file are 'instantly visible' through every link. The Windows 8-era CreateHardLink table says ReFS is not supported, but Microsoft's current ReFS overview lists hard links as supported on ReFS. (https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions ; https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-createhardlinka ; https://learn.microsoft.com/en-us/windows-server/storage/refs/refs-overview)
- [high] Pandora README: create an empty 'Pandora Output' mod and pass -o "<absolute path>" as an argument. This is recommended over MO2's 'create files in mod' option, because under the MO2 VFS Pandora overwrites existing files at their origin, even in another mod. (https://github.com/Monitor221hz/Pandora-Behaviour-Engine-Plus/blob/main/README.md)
- [high] DynDOLOD 3 order:
1. Finalize the load order, then clean and error-check it in xEdit; clean every plugin LOOT flags.
2. Create all other patches first.
3. Run xLODGen terrain LOD before DynDOLOD.
4. Run PGPatcher (ParallaxGen) before TexGen and DynDOLOD.
5. For grass LOD, build the NGIO grass precache before DynDOLOD.
6. Run TexGen, then DynDOLOD; install each output as a mod that overwrites everything.
Occlusion.esp must be the last plugin, right after DynDOLOD.esp. DynDOLOD.esm should be the highest-priority ESM possible, just before the first non-ESM. (https://dyndolod.info/Generation-Instructions)
- [high] PGPatcher wiki patching order:
1. Run BodySlide if needed.
2. Disable the DynDOLOD and TexGen outputs and the previous PGPatcher output.
3. Run PGPatcher, with its output set to an MO2 mod via Output > Location.
Synthesis goes to a dedicated folder outside the game and mod-manager folders and writes Synthesis.esp (one file per patcher group); MO2 catches its output unless redirected. BodySlide's Advanced 'Output Path' builds into a separate folder. (https://modding.wiki/en/skyrim/developers/community-shaders/pgpatcher-home ; https://mutagen-modding.github.io/Synthesis/Installation/ ; https://mutagen-modding.github.io/Synthesis/Typical-Usage/ ; https://github.com/ousnius/BodySlide-and-Outfit-Studio/wiki/Installation-and-Settings)
- [high] Recount of the target against the Feb-2025 Nolvus v6 and M&V 2.6.2 snapshots:
- 4044 enabled mods and 95 separators (65 enabled); 0 disabled mods.
- Nolvus-only 2444, M&V-only 561, both 323, neither 716.
- Of the 716, 170 are in Redux 6.0.20 and 177 in Redux ∪ Victolvus.
- With both Nolvus snapshots combined: Nolvus-only 2614, M&V-only 541, both 343, neither 546.
- About 67-70 of the leftover names are renames ending in a digit, leaving about 470-480 to identify by hand. (local analysis: user__modlist.txt, nolvus-awakening-v6__modlist.txt, mages-vikings__modlist.txt, neither_mods.txt; https://api.loadorderlibrary.com/v1/lists/nolvus-awekening-redux ; https://api.loadorderlibrary.com/v1/lists/victolvus)
- [high] Where the 323 name collisions sit: 246 under Nolvus numbered separators and 77 under 'MV …' separators. That hints at which copy was used but doesn't prove it. Mods found in neither snapshot sit as follows: 431 under Nolvus numbered separators, 264 under MV separators, 21 under other separators (NEWMODS, CS, city separators). (local analysis: user__modlist.txt separator mapping (a separator line sits below the mods it groups))
- [high] Target plugins.txt: 4244 plugins (4140 .esp, 76 .esl, 28 .esm).
- PGPatcher.esp is at line 138 and DynDOLOD.esm at 160; three ESMs load after DynDOLOD.esm (Praedys_Soulcairn, BetterDynamicAsh-DisableRefs, High Poly Head).
- The tail is FNIS.esp, Synthesis.esp, PG_1.esp, PG_2.esp, DynDOLOD.esp, Occlusion.esp, then 20 FWMF paper-map plugins.
- Adding 79 primary plugins (5 base + 74 CC per the Nolvus loadorder.txt) gives 4323, against a hard cap of 254 full + 4096 light = 4350. (local analysis: user__plugins.txt, nolvus-awakening-v6__loadorder.txt; https://tes5edit.github.io/docs/8-managing-mod-files.html (254 + 4096 light))
- [high] The target's generated and personal folders sit at the top:
- Outputs: Pandora Output, dyndolodCS2, texgenCS, 'grass CS', lodgen2, pgpatcher_output, SYNTHESSIS, 'BodySlide (Dressed)'.
- Personal folders: CustomFixes1, overwrite2.
- Also: 'CommunityShaders_AIO-2026-05-28T17-09Z', a date-stamped build.
The target has no Seasons of Skyrim or Grass Cache Helper NG, both of which Nolvus v6 has. It keeps 'NAT.ENB III' enabled next to 'NAT.CS III'. It includes 'Cached Recursive Directory Walk' and 'Scaleform Translation Plus Plus NG'. (local analysis: user__modlist.txt lines 1-40, 90-101, 4018, 4127; nolvus-awakening-v6__modlist.txt lines 897, 939)
- [high] Steam lists these languages for Skyrim Special Edition: English, French, Italian, German, Spanish, Polish, Traditional Chinese, Russian and Japanese. Traditional Chinese is text only, with no full audio. (https://store.steampowered.com/api/appdetails?appids=489830)
- [medium] PGPatcher splits its output into PG_1.esp, PG_2.esp and so on when the master limit would be exceeded, next to PGPatcher.esp. (https://deepwiki.com/hakasapl/PGPatcher (secondary); consistent with user__plugins.txt)

## RISKS
- CORRECTION: STEP 6 said 'open MO2 and check it shows no missing-mod entries'. That is wrong. MO2 silently drops any modlist.txt line whose folder is missing and rewrites the file, and the same happens for plugins. Opening MO2 too early destroys the target order. Create all 4044 mod folders and 95 separator folders first (empty placeholders are fine), keep untouched backups of both txt files, and compare them after the first launch.
- CORRECTION: 'A matching loadorder.txt must be written' is too strong. In a new profile with no loadorder.txt, MO2 falls back to plugins.txt. If a loadorder.txt exists, it wins when MO2 starts. Either leave it out or make it match exactly.
- CORRECTION: Mages & Vikings 2.6.2 runs SkyrimSE 1.6.1170 (the list moved from 1.5.97 in v2.5), not 1.5.97 with Best of Both Worlds. Nolvus v6 and the target run 1.5.97. SKSE DLLs from the roughly 541-561 M&V-only mods may be AE-only builds that will not load on 1.5.97 and must be swapped for SE or multi-runtime builds.
- CORRECTION: The '≈46 renamed duplicates / ≈493 remaining' figures depend on method. A recount finds about 67-70 renames ending in a digit, and about 470-480 mods remain unidentified. The data block's per-section 'none' counts (357/219) were wrong; the actual figures are 431, 264 and 21 others.
- CORRECTION: ReFS is not unsupported for hard links today; Microsoft's current ReFS overview lists hard links as supported. Using one NTFS volume is still the safest choice.
- CORRECTION: The ModOrganizer.ini example is wrong. It should read gamePath=@ByteArray(D:\\PM\\Stock Game) and selected_profile=@ByteArray(Pages) under [General]. The directory keys belong under [Settings], not [General].
- CORRECTION: The target has no Seasons of Skyrim, so no seasonal .cgid caches are needed. It also means Nolvus's own grass cache and LOD outputs cannot be reused.
- CORRECTION: 'DynDOLOD.esm high in the ESMs' should read 'the highest-priority ESM possible, just before the first non-ESM'. In the target, three ESMs load after it.
- Language conflict: the Nolvus Dashboard language must match Steam's, but M&V requires Steam set to English. Install both bases in English. Skyrim SE supports Traditional Chinese as text only. The merged Stock Game is a copy and will not pick up a later Steam language switch.
- Plugin cap: 4323 plugins including primaries against a hard cap of 4350. At least about 4069 must be light (ESL-flagged), and only about 27 slots are left for new patches or translation add-ons.
- Updaters and hardlinks: a Nolvus Dashboard update rewrites its own profile's order files and deletes and recreates each updated mod folder. A Wabbajack update deletes every file not in the list, except saves, downloads and [NoDelete] paths. Both replace files with new ones, so the hardlinked D:\PM keeps the old content.
- In-place writes through MO2's VFS change a file at its origin mod, as Pandora's README warns. With hardlinks, that change also reaches the source instance. This applies to BodySlide without an Output Path, Pandora without -o, and INI edits. Always direct tool output to dedicated output mods.
- Shaders: Nolvus v6 offers only ENB presets and M&V ships Kauz ENB, but the target uses Community Shaders. Remove d3d11.dll, d3dcompiler_46e.dll, enbseries/ and enb*.ini from the merged Stock Game. The 'CommunityShaders_AIO-2026-05-28…' build is date-stamped, so its exact source and 1.5.97 support must be confirmed.
- Disk: peak SSD need is about 372-426 GB (Nolvus) plus 386 GB (M&V), new mods, outputs and install caches, so plan for roughly 800+ GB. Archives are optional: Nolvus can skip archiving or store archives on an HDD, and M&V downloads can be deleted after install. Most laptop SSDs are too small.
- Hardware: M&V recommends an RTX 4070 and 32 GB RAM. Nolvus Ultimate needs 14-16 GB VRAM at 1080p; Redux needs 8 GB. Laptop GPUs often have less VRAM than their desktop namesakes, so check the actual VRAM before choosing a variant.
- Version drift: both installers deliver only their current builds. The target's exact mod versions are unknown, so patches and FormIDs may mismatch.
- The FWMF plugins load after Occlusion.esp, against DynDOLOD's guidance. Check in xEdit for WRLD/CELL conflicts.
- MO2 plugins: Nolvus configures a 'CRDW Automatic Mode' MO2 plugin and M&V uses 'Mod Bundle Trigger'. The target includes Cached Recursive Directory Walk. Copy the needed MO2\plugins or those features may silently break.
- Nexus ToS §10/§11: bulk scripted downloads or GraphQL data mining could be treated as abuse even with Premium. Prefer MO2 or Wabbajack downloads and throttle any script.
- User-made folders (CustomFixes1, overwrite2 and all outputs) cannot be downloaded. They must be rebuilt or obtained from the list's author.
- Nolvus support and M&V support will not help with a hybrid list, and redistributing Nolvus's non-Nexus files is unconfirmed. Keep any compiled .wabbajack private.

## RECS
- STEP 0: Use one NTFS SSD volume with short roots: D:\Nolvus, D:\MV, D:\PM. Put archives on an HDD, or turn archiving off.
- Steam Skyrim: latest version (1.7.104 accepted by both lists), all CC content downloaded, language English, overlay off.
- Install VC++, .NET 6 and .NET 8 desktop runtimes.
- Accounts: Nolvus and mega.nz.
- Add Defender exclusions for these folders.
- STEP 1: Install Nolvus v6 with the Dashboard and pick English. Choose a variant that fits the laptop's real VRAM (Redux 8 GB, Ultra 10-11 GB, Ultimate 14 GB+ at 1080p). Record the STOCK GAME SkyrimSE.exe version (expected 1.5.97), the SKSE build, and the MO2\plugins contents.
- STEP 2: Install M&V 2.6.2 with Wabbajack into D:\MV. Record its game folder, the exe version (expected 1.6.1170) and its MO2 plugins.
- STEP 3: Inventory with a read-only script:
- Nolvus: mods\*\meta.ini (modid, version, installationFile, fileid).
- M&V: downloads\*.meta, or the 'modlist' JSON inside the .wabbajack.
- Build a CSV mapping target name → source → modId/fileId/version.
- STEP 3b: Resolve collisions and duplicates.
- Default: an 'MV …' separator means the M&V copy; a numbered separator means the Nolvus copy.
- Confirm with fileid, version and plugin lists.
- For every M&V-sourced SKSE DLL, check 1.5.97 support; replace AE-only builds with SE builds.
- STEP 4: Create D:\PM with a zipped MO2 release and portable.txt.
- Put gameName, gamePath=@ByteArray(...) and selected_profile=@ByteArray(Pages) under [General]; put path keys under [Settings].
- Copy the MO2 plugins you need (CRDW Automatic Mode and similar).
- Hardlink-clone the Nolvus 1.5.97 STOCK GAME, then remove the ENB binaries, since the target uses Community Shaders.
- STEP 5: For each target folder, create D:\PM\mods\<exact name> and hardlink the source files. Make real copies of meta.ini and of any file you will edit. For names not yet identified, create empty placeholder folders so MO2 cannot drop them. Create all '<name>_separator' folders.
- STEP 6: With MO2 closed, place the target modlist.txt and plugins.txt in profiles\Pages. Keep a backup copy of both. Either leave loadorder.txt out or generate it to match exactly. Add settings.ini (LocalSaves=true, LocalSettings=true) and Nolvus's INIs. After the first launch, diff both txt files against the backups.
- STEP 7: Identify the remaining ~470-480 mods one by one:
- Search Nexus for the name.
- GraphQL modFileContents with plugin names from neither_plugins.txt finds the archive.
- GraphQL modFiles (including ARCHIVED files) picks the version.
- Download with MO2 Mod Manager Download or `wabbajack-cli download-url`.
- Throttle any script and send the Application-Name/Version headers.
- STEP 8: Ask the target's author for the MO2 CSV export. It has #Nexus_ID, #Mod_Version and #Download_File_Name, but no file ID; match the file name via modFiles. Also ask for their meta.ini files (which contain the file IDs), a private .wabbajack, and the CustomFixes1 and overwrite2 folders.
- STEP 9: Before generating outputs:
- Resolve missing masters.
- Confirm at most 254 full plugins and at most 4096 light ones; there is only about 27 slots of headroom.
- Run xEdit Check for Errors, then QuickAutoClean on LOOT-flagged plugins. Do not use LOOT sorting.
- STEP 10: Disable the old outputs, then regenerate in order:
1. Pandora (-o)
2. BodySlide (Output Path)
3. Synthesis
4. PGPatcher
5. NGIO grass precache (no seasonal caches needed)
6. xLODGen terrain
7. TexGen
8. DynDOLOD, with DynDOLOD.esm as the highest-priority ESM and Occlusion.esp after DynDOLOD.esp.
Then review the FWMF plugins that load after it, and start a new game.
- Chinese translation: plan it as a layer in the merged instance, applied before step 10. Translated plugins go at the same priority as the originals. Base-game Traditional Chinese strings must go into the D:\PM Stock Game or a mod. Translation must not add plugins beyond the remaining ~27 slots.
- After D:\PM is verified, stop updating the source instances, or delete them; the hardlinked files remain valid. Keep the archives if you may need to rebuild.

## OPEN
- What GPU (actual VRAM), RAM and free NVMe space does the laptop have? This decides the Nolvus variant and whether both bases fit at once (about 800 GB or more).
- Which Nolvus v6 variant and options did the target author use? The target overlaps more with the Redux 6.0.20 snapshot (2864 names) than with the Feb-2025 v6 snapshot (2767), but that may just be version drift.
- How many of the M&V-sourced mods contain SKSE DLLs without 1.5.97 support? This needs checking after install, by DLL.
- Can the author ('Pages') provide the CSV export, meta.ini files, CustomFixes1, overwrite2, or a private .wabbajack?
- Where does the date-stamped 'CommunityShaders_AIO-2026-05-28T17-09Z' build come from (nightly or GitHub artifact), and does it support 1.5.97?
- How will Traditional Chinese base-game strings get into the 1.5.97 Stock Game? Does the Dashboard's new language-pack management (v3.8.10) help, and do translated interface files conflict with Scaleform Translation Plus Plus NG?
- Does MO2 write meta.ini through QSettings in place, or via a temporary file and rename? This decides whether meta.ini edits reach the source instance through hardlinks; keep real copies until this is known.
- Does Nexus v1 download_link.json serve ARCHIVED files to Premium users in every case? The news post says they are downloadable with mod ID and file ID, but this was not tested with a key.
- Does GraphQL modFileContents index every archive, including contents packed inside BSAs? Coverage for this list is unknown.

## DATA
VERIFIED NUMBERS (local recount, 2026-09-25)
- Enabled mods: 4044. Separators: 95 (65 enabled). Disabled mods: 0.
- Vs Nolvus v6 (Feb 2025) + M&V 2.6.2: Nolvus-only 2444 | MV-only 561 | both 323 | neither 716.
- Vs (Nolvus v6 ∪ Redux 6.0.20) + M&V: Nolvus-only 2614 | MV-only 541 | both 343 | neither 546 (only 7 more are in Victolvus).
- Renames ending in a digit: about 67-70. Unidentified: about 470-480.
- Section vs origin:
  - Nolvus-numbered sections: N 2381, MV 79, both 246, none 431.
  - MV sections: MV 481, N 63, both 77, none 264.
  - Other separators: 22 (21 of them none).
- Plugins: 4244 (esp 4140 / esl 76 / esm 28).
  - Primary plugins: 79 (15 esm / 64 esl), so 4323 in total against a cap of 4350.
  - PGPatcher.esp is at line 138 and DynDOLOD.esm at 160; 3 ESMs come after it.
  - After Occlusion.esp: 20 FWMF plugins.

GAME VERSIONS
- Nolvus v6: 1.5.97. Evidence: BEES, Crash Logger 1.5.97, the Dashboard downgrader, v3.8.11 signature for Steam 1.7.104.
- M&V 2.6.2: 1.6.1170 (changelog v2.5).
- Target: 1.5.97 on the Nolvus base (SKSE, Address Library, Crash Logger - 1.5.97, DAV for 1.5).

MO2 FILE MECHANICS (source-verified)
- modlist.txt: top line = highest priority. Lines for missing folders are dropped and the file is rewritten. Unlisted mods get high priority.
- Plugin order: loadorder.txt wins at startup if it exists. If it is missing, plugins.txt sets the order. Primary plugins are not written.
- ModOrganizer.ini:
  - [General]: gameName, gamePath=@ByteArray(...), selected_profile=@ByteArray(...)
  - [Settings]: base_directory, download_directory, mod_directory, profiles_directory, overwrite_directory, cache_directory
- CSV export: #Nexus_ID, #Mod_Version, #Download_File_Name, #Mod_Nexus_URL, … (no file ID column).

NOLVUS v6 SIZES (installed + archives, minimum VRAM at 1080p)
- Ultimate 426+193 GB, 14 GB (16 GB with SR Exterior Cities)
- Ultra 406+188 GB, 10-11 GB (13-14 GB with SR)
- Redux 372+170 GB, 8 GB (10 GB with SR)
- Graphics Only 235+105 GB

M&V 2.6.2
- 3772 archives, about 230 GB. Installed about 386 GB, 374,545 files. .wabbajack 5.42 GB. Collection 503539.

NEXUS
- v1 limits: 20k per day, then 500 per hour. md5_search needs a key (401).
- GraphQL, no auth: modFiles (includes ARCHIVED), modFileContents (gameId Int 1704), fileHash.
- Archiving: news/14538 (July 2021).

UPDATE BEHAVIOUR
- Nolvus: rewrites modlist.txt, loadorder.txt and plugins.txt in its own profile; deletes and recreates updated mod folders.
- Wabbajack: deletes everything not in the list except downloads, the .wabbajack file, profiles\*\saves, [NoDelete] paths and up-to-date BSAs.
- Hardlinked D:\PM: unaffected by those (files are replaced with new ones); affected by in-place writes (VFS tools, text edits).