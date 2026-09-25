# provenance

## SUMMARY
Adversarial re-check of the "provenance" result. Most of it holds up. I re-derived the classification from the live nolvus.net/awakening table (4,250 rows), the Load Order Library (LOL) snapshots and the target modlist.txt, and the numbers reproduce within ±3: current-Nolvus 2,556 vs 2,554, MV-only 541 (+3 renamed = 544), both 429/430, old-Nolvus-only 55. The plugin split also reproduces exactly (2105/717/672/107/643). Nexus IDs and file mappings were spot-checked via the Nexus GraphQL API and are correct: PBR Hub, Margot/Jinx DBVO, Elden Rim, Blubbo, Pandora 4.3.1-beta, NGIO 1.5.11, CS 1.5.2/1.6/1.9.1.

Material corrections:
(1) Version status. nolvus.net's History page and homepage give v6.0.20 (27 Jan 2026) as the latest public release. The 6.0.21 rows on the mod-list page look like the 6.0.21 beta. So the 55 "dropped" mods (Wet and Cold, Footprints, Curse of the Hound Amulet, At Your Own Pace, True Armor…) were still in 6.0.20.
(2) The target's Nolvus base is about 6.0.18. It contains the 6.0.17 and 6.0.18 additions, none of the 7 mods added in 6.0.19 and none of the 28 added in 6.0.20.
(3) The target is not "Nolvus + MV". A Dashboard install with the implied options would add about 730 rows that the target lacks. That is an upper-bound estimate that includes renamed/replacement versions. The missing rows are concentrated in the visual/world layer: trees 35/39, grass 22/22, weathers/seasons 19/24, the five cities, towns 71/115, interiors 53/108, lighting 54/102, ENB 16/18. The author kept Nolvus' gameplay, combat, quest, NPC and armor layers and replaced the world and visuals with MV plus PBR, Community Shaders (CS) and Lux.
(4) "Crash Logger - 1.5.97" is an Always-Install Nolvus row shipped next to "Crash Logger - SSE", and the target has both, so it proves nothing about the runtime. 1.5.97 is still correct, based on SKSE 2.0.0.20, BEES and the 1.5-only ports.
(5) The "Legacy of the Dragonborn V6" file name is used for every V6 release from 6.0.0 to 6.10.2, so the version cannot be pinned.
(6) Pandora comes from MV. It is not a target-only swap.
(7) The target uses Dragonborn ReVoiced instead of DBVO 2.
(8) The YXZ xEdit script is optional.
(9) "SKSE Output" is not a Nolvus row.
(10) Curious Adventurer is now free for free Patreon members.
Laptop-critical sizes: Nolvus Ultimate needs 14 GB VRAM minimum at 1080p, 426 GB installed and 193 GB download. MV 2.6.2 is about 386 GB installed plus 230 GB of archives.

## FACTS
- [high] Target modlist.txt has 4,044 enabled non-separator mods and 95 separators (65 enabled, 30 disabled). The zip contains only modlist.txt and plugins.txt: no meta.ini, no .wabbajack file (local: /tmp/claude-0/-home-user-TEST/c9c8e05c-da49-5853-b77c-d18f7c1a40e3/scratchpad/user__modlist.txt; unzip -l /root/.claude/uploads/c9c8e05c-da49-5853-b77c-d18f7c1a40e3/ccbc51c3-Pages_Modlist_WIP.zip)
- [high] The classification reproduces within ±3 using the same normalization. The live nolvus.net table plus the LOL snapshots give: in current Nolvus list only 2,556; MV only 541 (544 once 3 renamed MV folders are added); both 429–430; only in older Nolvus v6 snapshots 55; matched by neither about 462 (the original split: 431 f + 13 g + 9 d + 3 e + 5 u). About 70 folders (not 72) match only after removing a trailing MO2 digit (re-computed from https://www.nolvus.net/awakening + https://api.loadorderlibrary.com/v1/lists/{nolvus-awakening-v6,nolvus-awekening-redux,nolvus-v6-ultimate-open-beta-start,mages-vikings})
- [high] The plugin overlap reproduces exactly: of 4,244 target plugins, Nolvus-only 2105, MV-only 717, both 672, only in Nolvus forks 107, in none 643 (re-computed vs LOL plugins/loadorder for nolvus-awakening-v6, nolvus-v6-ultimate-open-beta-start, victolvus, nolvus0-20, cust-nolvus, nolvus-awekening-redux, mages-vikings)
- [high] nolvus.net/awakening currently lists 4,250 mod rows (Mod / Version / Option). The highest Nolvus patch version on the page is 6.0.21 (202 rows) (https://www.nolvus.net/awakening)
- [medium] The official Nolvus History page's newest entry is v6.0.20 (Tuesday, 27 January 2026), and the nolvus.net homepage says 'Last update Tuesday, January 27, 2026 (v 6.0.20)'. There is no 6.0.21 changelog entry. A YouTube showcase posted about a week ago is titled 'Nolvus Update Showcase + DLSS 5 | V6.0.21 (Beta)'. So 6.0.21 appears to be a beta, and the list page may reflect the beta package set (https://www.nolvus.net/appendix/history ; https://www.nolvus.net/ ; https://www.youtube.com/watch?v=K-O8wjA0YH0 (oEmbed title))
- [high] The 55 target mods absent from the nolvus.net page were still in Nolvus 6.0.20. Examples: Wet and Cold, Footprints, Curse of the Hound Amulet, iWant Widgets NG, At Your Own Pace - Main Quest, Nolvus Awakening Stances Perk System. They appear in the LOL 'nolvus-awekening-redux' 6.0.20 snapshot (updated 2026-05-29), and the History page shows them being added or updated up to 6.0.17. The current page replaces some of them with Dynamic Footprints, True Armor - Evolved and Stances Perk System NG (https://api.loadorderlibrary.com/v1/lists/nolvus-awekening-redux ; https://www.nolvus.net/appendix/history ; https://www.nolvus.net/awakening)
- [medium] The target's Nolvus base is most likely v6.0.18 (1 Dec 2025). It contains the 6.0.16, 6.0.17 and 6.0.18 additions: Hall of secrets - LOTD Fix, Curse of the Hound Amulet - True HUD Patch, Vanilla Hair Remake - SMP, Vanilla Hair - Salt and Wind. It contains none of the 7 mods added in 6.0.19 (e.g. Armor Filter Framework, B.O.O.B.I.E.S - Potions) and none of the 28 added in 6.0.20 (Claws/Twinblades movesets, SIGMA 1st-person, Oathvein UI, Animated Armoury) (History 'Added new mod' entries on https://www.nolvus.net/appendix/history compared with local user__modlist.txt)
- [medium] The target is a selective merge, not Nolvus plus MV. I evaluated the nolvus.net option logic with the implied choices (Ultimate, Edge UI, 16:9, addons, not SREX, not Milk Drinker). About 3,700 rows would be installed, and about 731 of them have no same-name folder in the target. These are concentrated in: Trees 35/39, Grass 22/22, Weathers/Seasons 19/24, Whiterun 36/40, Solitude 20/28, Riften 14/17, Markarth 11/14, Windhelm 13/16, Towns 71/115, Interiors 53/108, Lighting 54/102, Player homes 7/7, ENB & Reshade 16/18, LotD section 12/19. Name matching overstates the count, because some rows are replaced by renamed or other versions (Base Object Swapper 3.41, Splashes of Skyrim 1.5, Faster HDT-SMP 4.01, VIGILANT SE 1.8, LotD V6) (https://www.nolvus.net/awakening option column evaluated against local user__modlist.txt)
- [high] The target has no Seasons layer: Seasons of Skyrim, Seasonal Landscapes, Seasons of Nolvus and Seasonal Weathers Framework are all absent. It also has no ENB Binaries, ENB Helper or Nemesis Unlimited Behavior Engine (https://www.nolvus.net/awakening vs local user__modlist.txt/user__plugins.txt)
- [high] The target runs on Skyrim SE 1.5.97. It includes Nolvus' 'Skyrim Script Extender' 2.0.0.20 (the 1.5.97 SKSE build), 'Backported Extended ESL Support' (a 1.5.97-only mod) and 1.5.97 ports: Dynamic Armor Variants for Skyrim 1.5 (88302, 'Port ... to Skyrim version 1.5.97'), Skyrim Souls RE for Skyrim 1.5 (120085), Splashes of Skyrim 1.5, and NGIO - NG (1.5.11) (https://www.nolvus.net/awakening ; https://www.nexusmods.com/skyrimspecialedition/mods/88302 ; https://www.nexusmods.com/skyrimspecialedition/mods/120085 ; local user__modlist.txt)
- [high] Nolvus ships BOTH 'Crash Logger - SSE' (1.16.0) and 'Crash Logger - 1.5.97' (1.15.0) as Always Install, and the target contains both. Their presence therefore says nothing on its own about the runtime (https://www.nolvus.net/awakening ; local user__modlist.txt lines 4029-4030)
- [high] Nolvus provides a Downgrade Patcher (AE 1.6 → 1.5.97, keeping CC content). The Dashboard requires the latest Steam Skyrim Anniversary Edition with all Creations downloaded (https://www.nolvus.net/downloads/installer ; https://www.nolvus.net/appendix/installer/faq)
- [medium] MV 2.6.2 uses the 1.5.97 runtime with Best of Both Worlds and requires all Creation Club content. The README says to set the Steam game language to English before installing, and recommends an RTX 4070, 32 GB RAM and a modern CPU. The English and hardware statements are confirmed in the README. The 1.5.97+BOTW statement comes from a search snippet of the Nexus page (https://github.com/nicolasbertolino/MagesAndVikings/blob/main/README.md ; https://www.nexusmods.com/skyrimspecialedition/mods/136238)
- [high] The MV 2.6.2 Wabbajack metadata lists 3,772 archives, archives 229,998,290,486 bytes (~230 GB), installed files 386,316,461,236 bytes (~386 GB), total ~616 GB. MV also has a Nexus Collection (collectionId 503539, slug agq2zq) (https://raw.githubusercontent.com/nicolasbertolino/MagesAndVikings/main/modlists.json (via https://raw.githubusercontent.com/wabbajack-tools/mod-lists/master/repositories.json))
- [high] Nolvus Awakening v6 requirements. Ultimate without SREX: minimum 14 GB VRAM (RTX 4060 Ti) at 1080p; 426 GB installed; 193 GB download. Ultra: 406 GB / 188 GB; minimum 10 GB VRAM (RTX 3080 or 2080 Ti) at 1080p. Redux without SREX: minimum 8 GB VRAM (GTX 1080) at 1080p; 372 GB / 170 GB. SSD is mandatory. Archiving the download is optional (https://www.nolvus.net/appendix/installer/requirements)
- [high] The Nolvus Dashboard needs a Nolvus.net account in addition to Nexus. Premium gives automatic downloads; free Nexus accounts are capped at 3 MB/s. Some files come from mega.nz and Google Drive. v6 must be installed under a short path such as X:\Nolvus or it will not boot. The Dashboard language choice must match Steam's, and 'Only the base game will be translated, not the mods' (https://www.nolvus.net/appendix/installer/install ; https://www.nolvus.net/appendix/installer/requirements)
- [high] The current Nolvus list uses Nemesis Unlimited Behavior Engine 0.84b, Legacy of the Dragonborn 5.6.5, Vigilant 1.7.3 and Unslaad 3.0.2. It has no Pandora or Community Shaders rows. The target instead has Pandora Behaviour Engine v4.3.1-beta, a CommunityShaders_AIO build, 'Legacy of the Dragonborn V6', 'VIGILANT SE 1.8' and 'Unslaad SE2', and has no Nemesis engine folder (https://www.nolvus.net/awakening ; local user__modlist.txt)
- [high] Pandora comes from MV, not the target author: MV 2.6.2 contains 'Pandora Behaviour Engine Plus'. On Nexus 133232, v4.3.1-beta (2026-04-16) is OLD_VERSION/ARCHIVED and the current MAIN is v4.4.0-beta (2026-08-11) (local mages-vikings__modlist.txt line 55 ; https://www.nexusmods.com/skyrimspecialedition/mods/133232 (modFiles))
- [high] On LotD SSE (11802), the file name 'Legacy of the Dragonborn V6' is used for every V6 release, from 6.0.0 (2024-06-23, ARCHIVED) through 6.9.x/6.10.x (OLD_VERSION) to the current MAIN 6.10.2 (2026-09-04). The target's exact LotD version cannot be determined (https://www.nexusmods.com/skyrimspecialedition/mods/11802 (Nexus GraphQL modFiles))
- [high] VIGILANT SE (11849) and its English translation (11894) are now 1.8.2 (2026-07-16). Unslaad SE (11789) is 3.0.6 (https://www.nexusmods.com/skyrimspecialedition/mods/11849 ; https://www.nexusmods.com/skyrimspecialedition/mods/11894 ; https://www.nexusmods.com/skyrimspecialedition/mods/11789)
- [high] NGIO - NG (1.5.11) is an OLD_VERSION file (2025-12-18) on 'No Grass In Objects' (42161) (https://www.nexusmods.com/skyrimspecialedition/mods/42161)
- [high] Community Shaders on Nexus (86492) has files 1.5.2 (2026-05-15), 1.6 (2026-05-31) and a current MAIN of 1.9.1 (2026-09-24). CS supports 1.5.97 or the latest Steam/GOG build, and it disables itself if ENB is detected ('You must pick one or the other') (https://www.nexusmods.com/skyrimspecialedition/mods/86492)
- [medium] GitHub release assets for Community Shaders are named like 'CommunityShaders_AIO-2026-09-24T12-32Z.7z'. The repo also publishes many PR pre-release builds, and no stable release falls on 2026-05-28 (v1.5.0 on 1 May, v1.6.0 on 31 May). 'CommunityShaders_AIO-2026-05-28T17-09Z' is therefore probably a PR or pre-release build and may no longer be downloadable (https://github.com/community-shaders/skyrim-community-shaders/releases)
- [high] The target replaces DBVO 2 (84329) with Dragonborn ReVoiced / DBReV (184221, v1.5.2): the folder is 'Dragonborn ReVoiced2', and there is no DBVO framework folder and no DBVO.esp. DBReV supports DBVO 1.0 voice packs and gives them automatic locale mappings for non-English game clients, covering Skyrim/DLC plus an optional pack for 500+ mods including full Nolvus. A CHS translation of DBReV exists (187113) (https://www.nexusmods.com/skyrimspecialedition/mods/184221 ; https://www.nexusmods.com/skyrimspecialedition/mods/187113 ; local user__modlist.txt line 247)
- [high] 'Leveled List Patch' (6.0.21, 'Not Milk Drinker, Not Graphics Only'), 'Descriptions for Various Mods' (2.4.1, Always Install) and 'Psychopatchist Purgatory' (0.5, Not Graphics Only) are official Nolvus rows placed just before '10. OUTPUTS'. 'Nolvus HUD Settings (Edge UI)' is an official Nolvus row (Edge UI, 16:9) (https://www.nolvus.net/awakening)
- [high] Psychopatchist Purgatory is Nexus 87016 by Czasior (Nexus version 0.15). Descriptions for Various Mods is 106229 by SauteedPanda (2.6.1). Its Traditional Chinese (CHT) translation is 153964 (v2.6.1, by Vagrant999) (https://www.nexusmods.com/skyrimspecialedition/mods/87016 ; https://www.nexusmods.com/skyrimspecialedition/mods/106229 ; https://www.nexusmods.com/skyrimspecialedition/mods/153964)
- [medium] Page's SmoothCam Preset is Nexus 189799 by page804 (created 2026-09-01, 'My preset based on Zeuscam'). That page804 is the author of 'Pages_Modlist_WIP' is an inference (https://www.nexusmods.com/skyrimspecialedition/mods/189799)
- [medium] The Nolvus-option rows matched by the target (exact names) imply: Ultimate (28 of 112 Ultimate rows kept, 0 Ultra); not Redux (only 1 Redux row: "Spaghetti's Towns - Dragon Bridge"); SREX off (0 of 180); Edge UI and 16:9; Not Milk Drinker (30 of 34, 0 Milk Drinker); addons Fantasy Combat 21/21, Boss Encounter 11/12, Alternate Leveling 10/10, Gore 6/6, Exhaustion 2/2, True Nord 1/1, plus 1 row each of Stances Perk Tree and Enemies Resistance. No ENB preset rows match (the two 'Kauz ENB'-tagged rows present are Native EditorID Fix and KreatE) (https://www.nolvus.net/awakening option column vs local user__modlist.txt)
- [high] Nolvus' prebuilt outputs (section 10) include: Synthesis Patch (by variant/SREX), Nemesis Output, BodySlide (Dressed/Nude), LODGEN, Grass Cache, DynDOLOD Textures/Output, CRDW - Cache and the Paper Map outputs. Photo Mode - Output and KiLoader - Output also appear elsewhere on the page. There is NO 'SKSE Output' row (https://www.nolvus.net/awakening)
- [high] MV ships these outputs: 'Mages & Vikings - Pandora Output', '- BodySlide Output', '- PGPatcher Output', '- Grass Cache Output', '- xLODGen Output', '- DynDOLOD Output - Full/No Floating Islands/Performance', plus '- Settings Hub' and '- Custom Files' (local mages-vikings__modlist.txt lines 3645-3654 (LOL mages-vikings 2.6.2))
- [high] Many target folders map to individual files on Nexus pages. All 'BTS01Margot - * DBVO Patch' folders are OPTIONAL files on 167746. 'dbvo_jinx_*' folders are files on 124428. Blubbo_Solitude_2023.zip and Blubbo_trees_in_solitude_Skyfall_BPCourtyard.zip are on 86739. Blubbos_Whiterun_2023_V2 and Blubbos_Whiterun_2023V2esl_patch are on 65232. Unslaad PBR and Clockwork PBR are on 167663. Jiaye's Vigilant PBR AIO and the HDT SMP Silver/Infantry Armor PBR patches are on 167174 (GTS repository). 'Dancing LUX CS' is an ARCHIVED file on 113926 (Nexus GraphQL modFiles for https://www.nexusmods.com/skyrimspecialedition/mods/{167746,124428,86739,65232,167663,167174,113926})
- [high] On 'PBR Hub' (139889), every Praedy's PBR file is ARCHIVED: Skeleton, College, Soul Cairn, Castle Volkihar, Apocrypha, Chantry. Improved Dwemer Glass PBR, Thrones Expanded PBR, Northern Roads PBR (1.0.2) and Reinforced Civil War Camps PBR (1.0.2) are MAIN (https://www.nexusmods.com/skyrimspecialedition/mods/139889)
- [high] Elden Rim (65625, page title 'Elden Rim - Weapon Arts 3.7.5') hosts all Elden Rim parts. The target's 'Elden Rim - Base 3.72' is the OLD_VERSION file '0-Elden Rim-Base 3.7.2' (2026-02-18). The page also carries '6-EldenRim Chinese Patch' files (4.0.0/4.0.2 from Feb 2026, 4.0.5 OPTIONAL from 2026-09-25). The translation version must match the base version. Whether the patch is Simplified or Traditional Chinese is not verified (probably Simplified) (https://www.nexusmods.com/skyrimspecialedition/mods/65625)
- [high] 'Northern Roads - Overgrowing Grass Remover' matches the exact name of an ARCHIVED prebuilt file (1.0.0alt, 2024-08-17) on Northern Roads - Patches Compendium (77893). The same page also has an xEdit variant (current OPTIONAL 8.0.0). The folder may therefore be a downloaded archived file rather than local output (https://www.nexusmods.com/skyrimspecialedition/mods/77893)
- [high] The YXZ True Diverse Northern Roads Reforged page (182981) offers two methods. Method 1 is load order only and accepts texture seams. Method 2 runs the optional 'Perfect_Land_Fixer' Pascal script in SSEEdit on the YXZ ESP. Both then generate meshes with PGPatcher for ENB/CS users. Running the script is optional, not mandatory (https://www.nexusmods.com/skyrimspecialedition/mods/182981)
- [medium] LOTDV6 - Blubbos Solitude - Tree Patch is Nexus 87785 ('Legacy of the Dragonborn - Blubbo's Solitude 2023 - Trees Patch'; high confidence). ModpocalypseNPCs-LotDV6-ErrorFixes.esp most likely comes from 123275 ('Modpocalypse NPCs - Legacy of the Dragonborn for LOTD V6'; inference) (https://www.nexusmods.com/skyrimspecialedition/mods/87785 ; https://www.nexusmods.com/skyrimspecialedition/mods/123275)
- [high] The plugin line numbers are confirmed. Generated plugins: PGPatcher.esp 138, DynDOLOD.esm 160, FNIS.esp 4219, Synthesis.esp 4220, PG_1.esp 4221, PG_2.esp 4222, DynDOLOD.esp 4223, Occlusion.esp 4224. Locally modified: YXZ_NRoad PBR DGS.esp 3971. Eight [FIX]*.esp at 4155-4162. PG_2.esp is in neither base list; PGPatcher.esp and PG_1.esp exist only in MV. TerrainHelper.esp comes from MV's 'Terrain Helper' (local user__plugins.txt; nolvus-awakening-v6__plugins.txt; mages-vikings__loadorder.txt)
- [medium] The full_inu Armor Pack 01 comes from the author's blog/Patreon, and only its SPID distribution patch is on Nexus (161148). Kirax BDOR 2024 Female Collection is on ModBooru. The Dint999 BDOR Hairs SSE 0.23 ESPFE repack is on DwemerMods. H2135 Fantasy Series 8 has only a CHS translation on Nexus (131766). SC Horses is ShinglesCat (Annie Lenine) Patreon-only. Air Balloons comes from TalesOfStar Patreon/site and Bethesda Creations. SUKI's LamasTinyHUD Edge replacer is on Patreon (2023-12-01). Patreon pages are Cloudflare-blocked, so these were confirmed via search snippets (https://inu-workshop.blogspot.com/2021/07/fullinu-armor-pack-01.html ; https://www.nexusmods.com/skyrimspecialedition/mods/161148 ; https://modbooru.com/mods/bdor-2024-female-collection-by-kirax.1883 ; https://www.dwemermods.com/mods/617 ; https://www.nexusmods.com/skyrimspecialedition/mods/131766 ; https://www.patreon.com/shinglescat/posts/sc-horses-35289631 ; https://creations.bethesda.net/en/skyrim/details/28121c41-6046-4336-b0e7-2bd9e2b6e705/Flying_Air_Balloons ; https://www.patreon.com/posts/lamas-tiny-hud-93893216)
- [medium] Curious Adventurer (Aokili) was a Patreon release and, per the author's X post (Dec 2025), is now available to FREE Patreon members (https://www.patreon.com/posts/curious-release-136173471 ; https://x.com/AokiliMods/status/1998072651470844138)
- [medium] Smooth's 'For Honor in Skyrim Grapple' (v1.3) is available only to Tier 1+ Patreon supporters, through Discord, until official release (https://www.patreon.com/SmoothAanimation/posts/for-honor-in-1-3-151072992 ; https://www.patreon.com/posts/for-honor-in-rko-149225636)
- [low] Anchor Animations are distributed through Anchor's Patreon (https://www.patreon.com/posts/anchor-3-0-44174035 (not re-verifiable, Cloudflare))
- [medium] No Chinese Nolvus translation was found on Nexus. Unofficial full translations of Nolvus v6 exist for French (164621, 6.0.19), Italian (171712), PT-BR (164341), Turkish (164744) and Spanish (163858, 6.0.14). A Simplified Chinese 'nolvus6.12' full translation (张裕汉化) is announced on Bilibili (2025-05-14) and distributed via Afdian, not Nexus; the Bilibili details are low confidence (Nexus GraphQL name search ; https://www.nexusmods.com/skyrimspecialedition/mods/164621 ; https://www.nexusmods.com/skyrimspecialedition/mods/171712 ; https://www.nexusmods.com/skyrimspecialedition/mods/164341 ; https://www.nexusmods.com/skyrimspecialedition/mods/164744 ; https://www.nexusmods.com/skyrimspecialedition/mods/163858 ; https://www.bilibili.com/video/BV1o5EPzPEWw/)
- [high] These Chinese translations exist on Nexus for target mods: Skybound Underhang Camp CHT 139969, Thrones Expanded CHS 165123, Lore-Friendly Load Screen Compendium CHS 152652, Conditional Expressions Extended CHS 160059, CC Myrwatch Tweaks and Enhancements CHS 121447 (https://www.nexusmods.com/skyrimspecialedition/mods/139969 ; https://www.nexusmods.com/skyrimspecialedition/mods/165123 ; https://www.nexusmods.com/skyrimspecialedition/mods/152652 ; https://www.nexusmods.com/skyrimspecialedition/mods/160059 ; https://www.nexusmods.com/skyrimspecialedition/mods/121447)

## RISKS
- CORRECTION: The original called 6.0.21 the current official Nolvus release. nolvus.net's History page and homepage list v6.0.20 (27 Jan 2026) as the latest release, and a Sept-2026 YouTube video labels 6.0.21 '(Beta)'. The mod-list page seems to show the 6.0.21 package set. Which version the Dashboard installs for a normal user today (6.0.20 or 6.0.21) is unverified.
- CORRECTION: The original said the 55 '(a-old)' mods were dropped and would never be installed by the Dashboard. All of them were in 6.0.20: LOL 6.0.20 snapshot dated 2026-05-29, and History entries up to 6.0.17. A 6.0.20 install would still provide them. Only a 6.0.21 install would not.
- CORRECTION: The target is not Nolvus-current plus MV plus extras. It matches Nolvus about 6.0.18: it includes the 6.0.17/6.0.18 additions and none of the 6.0.19 (7) or 6.0.20 (28) additions. It also deliberately leaves out about 730 Nolvus rows, mostly the world/visual layer (trees, grass, seasons/weathers, cities, towns, interiors, lighting, ENB). A fresh Dashboard install therefore needs hundreds of mods disabled, not just MV folders added.
- CORRECTION: 'Crash Logger - 1.5.97' does not show the runtime. Nolvus installs both Crash Logger builds, and the target keeps both. The 1.5.97 conclusion stands on SKSE 2.0.0.20, BEES and the 1.5-specific ports.
- CORRECTION: 'Legacy of the Dragonborn V6' is not specifically the archived 6.0.0 file. That file name covers every V6 release from 6.0.0 to MAIN 6.10.2, so the version is unknown.
- CORRECTION: Pandora is not a target-specific swap. MV 2.6.2 already uses 'Pandora Behaviour Engine Plus'. Only the version (4.3.1-beta) is target-specific.
- CORRECTION: The YXZ Perfect_Land_Fixer xEdit script is an optional second method on Nexus 182981. It is not required.
- CORRECTION: 'Northern Roads - Overgrowing Grass Remover' exactly matches an ARCHIVED prebuilt file (1.0.0alt) on 77893, so it is not necessarily locally generated.
- CORRECTION: 'SKSE Output' is not a Nolvus row; remove it from the disable list. Add 'CRDW - Cache', 'ENB Binaries' and the ENB section rows. CS disables itself when ENB is present.
- CORRECTION: Curious Adventurer is no longer paywalled. It was made free for free Patreon members (Dec 2025).
- CORRECTION: 70 (not 72) folders match only after removing the MO2 duplicate digit. That suffix shows a name collision at install time. It does not necessarily mean the folder was imported from both base lists.
- CORRECTION: The target also swaps DBVO 2 for Dragonborn ReVoiced (184221). There is no DBVO.esp. Nolvus' 'Dragonborn Voice Over 2' and its UI patches must not be enabled alongside it, because DBReV is incompatible with DBVO/DBVO 2 and their dialoguemenu.swf patches.
- The Community Shaders build 'CommunityShaders_AIO-2026-05-28T17-09Z' matches no stable release. It is probably a GitHub PR/pre-release build that may have been pruned. Substitute Nexus 1.6 (2026-05-31) or newer and re-check CS feature/preset compatibility (NAT.CS III, Lux CS).
- Without meta.ini or a .wabbajack file, exact file versions are unknown. Many mapped files are ARCHIVED or OLD_VERSION on Nexus (all Praedy's PBRs on 139889, NGIO 1.5.11, Pandora 4.3.1-beta, Dancing LUX CS, Elden Rim Base 3.7.2, Faultier's PBR files). Authors can hide archived files, and current versions may not support 1.5.97.
- Disk space on a laptop: Nolvus Ultimate is 426 GB installed plus 193 GB download (archiving optional). MV 2.6.2 is about 386 GB installed plus about 230 GB of archives. Installing both base lists side by side needs roughly 0.8–1.2 TB of SSD, before the extra ~430 Nexus mods and regenerated outputs.
- Hardware: Nolvus Ultimate lists a 14 GB VRAM minimum at 1080p, and MV recommends an RTX 4070 and 32 GB RAM. Most laptop GPUs have 8–12 GB VRAM, and the target adds a large PBR/4K layer on top. Texture Downscaler (187049) and Redux-level choices may be required.
- Language conflict: MV's README requires Steam language = English during install. The Nolvus Dashboard requires its language to match Steam, and it translates only the base game, not mods. The Chinese conversion must be done after installation as a separate override layer.
- Mixed engines and quest versions (LotD V6 vs Nolvus' 5.6.5 patches, e.g. 'Legacy of the Dragonborn Patches (Official)' 5.6.2 is still in the target; Vigilant 1.8; CS instead of ENB; DBReV instead of DBVO 2) mean Nolvus' Consistency, Leveled List and Synthesis patches were built against different masters. This is probably why CustomFixes1 exists.
- Patreon or off-Nexus mods cannot be automated. If they are skipped, the dependent plugins lose masters: full_inu ArmorPack01 SPID.esp needs [full_inu] Armor Pack 01.esp; Horsepower_Ragdoll - SC Horses Patch.esp needs SC_HorseReplacer.esp. Smooth's Grapple is Tier-1 paid.
- CustomFixes1 and the eight [FIX]*.esp plugins cannot be obtained. Whether other plugins list them as masters cannot be checked without the files.
- LOL snapshots and forks (victolvus, nolvus0-20, cust-nolvus) are user-uploaded and may contain customizations.
- The count of ~730 absent Nolvus rows is an upper bound from exact-name matching. Some are renamed or version-bumped equivalents (e.g. Base Object Swapper → 3.41, Faster HDT-SMP → 4.01, Water for ENB [4K] → Water for ENB [cs]2).

## RECS
- Do not assume the Dashboard reproduces the target's Nolvus base. Before installing, check in the Dashboard or on the Nolvus Discord whether it offers 6.0.20 or the 6.0.21 beta. Prefer 6.0.20, because it still contains the 55 mods the target uses (Wet and Cold, Footprints, At Your Own Pace, Curse of the Hound Amulet, iWant, True Armor, old Stances Perk System).
- Nolvus Dashboard options implied by the target: Ultimate, SREX off, Edge UI, 16:9, Not Milk Drinker, TAA. Addons: Fantasy Combat, Boss Encounter, Alternate Leveling, Gore, Exhaustion, Stances Perk Tree, Enemies Resistance and True Nord (Moderate). Any ENB preset may be chosen because it will be disabled. Install to a short SSD path (e.g. D:\Nolvus) with a Nolvus.net account. Disable archiving if space is tight.
- After the Nolvus install, turn Nolvus into the target by disabling the ~730 rows the target lacks. Build a script that diffs the installed MO2 modlist.txt against the user's target modlist.txt, rather than doing this by hand. The main blocks are trees, grass, seasons/weathers, cities, towns, interiors, lighting, ENB & Reshade, Nemesis and Nemesis Output, DBVO 2, LotD 5.6.5 and its DBVO patches, Vigilant 1.7.3 and all Nolvus section-10 outputs.
- Install MV 2.6.2 with Wabbajack into a separate folder, with Steam language set to English. Note its ~386 GB installed and ~230 GB archives, and consider the MV Nexus Collection (503539) as a lighter reference. Copy only the ~544 MV-only folders into the Nolvus MO2 instance. Do not copy MV's Settings Hub, Custom Files or any MV output folders unless the target lists them; the target does keep 'Mages & Vikings - Settings Hub'.
- Before downloading both lists in full, collect the laptop's GPU model and VRAM, RAM, and free SSD space. At under 12 GB VRAM, plan to drop or downscale the PBR/4K layer with Texture Downscaler (187049). Consider reducing Nolvus choices toward the Redux-level texture tier, keeping the target's mod set otherwise.
- Regenerate every output for the merged order in this order: Pandora (→ Pandora Output/FNIS.esp) → BodySlide (Dressed) → (optional) YXZ Perfect_Land_Fixer → PGPatcher (PGPatcher.esp, PG_1/PG_2) → Synthesis → xLODGen terrain → TexGen → DynDOLOD (DynDOLOD.esm/.esp, Occlusion.esp) → NGIO grass cache. Let Community Shaders rebuild its shader cache. Replace the missing CS GitHub build with Nexus CS 1.6 or later, and remove ENB Binaries and dxgi/d3d11 ENB files because CS refuses to run with ENB present.
- Get the ~431 public-Nexus folders with Nexus Premium. Record each chosen file ID and version, since archived files may disappear. Afterwards consider packaging the result as a private Wabbajack list or Nexus Collection so it can be reproduced.
- Treat the 13 non-Nexus mods as optional and drop their dependent patches if skipped. Curious Adventurer only needs a free Patreon account; Smooth Grapple needs a paid tier.
- Chinese plan: no CHT/CHS translation of Nolvus exists on Nexus; the only CHS one found (张裕汉化 'nolvus6.12') is on Afdian and targets an older version. Treat translation as a custom layer. Base game: switch Steam/INI language to Chinese after installation, keeping MV's English requirement in mind during the install itself. Mods: use per-mod CHT/CHS translations found on Nexus: 153964, 139969, 165123, 152652, 160059, 121447, the Elden Rim Chinese Patch matching Base 3.7.2, and DBReV CHS 187113. Handle the rest with xTranslator/ESP-ESM Translator dictionaries and MCM translation files. Translate Nolvus/MV-authored patches last. DBReV's locale mappings keep DBVO 1.0 voice packs working in a non-English client.
- Ask the list author (probably Nexus user page804) for the MO2 meta.ini files or a .wabbajack/Collection, plus CustomFixes1 and the [FIX] plugins.

## OPEN
- Does the Nolvus Dashboard currently install 6.0.20 or the 6.0.21 beta for a normal user, and can it install an older version such as 6.0.18? No official statement was found.
- Was the target built on Nolvus 6.0.18, or on 6.0.19 with all seven 6.0.19 additions deliberately removed?
- How many of the ~730 absent Nolvus rows are deliberate removals, and how many are renamed or version-bumped equivalents? This needs a per-row review or the author's meta.ini files.
- What are the laptop specs (GPU and VRAM, RAM, free SSD space)? They decide whether both ~400 GB base installs are feasible and which texture tier to keep.
- Can the user get the author's (page804?) meta.ini files, .wabbajack file, CustomFixes1 and the eight [FIX]*.esp plugins?
- What are 'CS shaders' and 'Vanilla CS rain TEXTURES'? Likely a CS shader cache and raindrop textures, but unconfirmed.
- Five folders remain unresolved: RMS Lux patch, horseAnimations2 (HorseAnimaTest.esp), "Wayshrines - JK's Skyhaven patch", "Yet another patch hub for Ryn's Skyrim2" and Smooth Special Idle.
- Does the Nolvus Dashboard language list include Chinese (it only translates the base game)? Is the Elden Rim Chinese Patch Simplified or Traditional?
- Will the user pay for Patreon-only content (Smooth Grapple and others) or drop it?

## DATA
VERIFICATION METHOD: Re-fetched https://www.nolvus.net/awakening (4,250 rows parsed from <td class='text-main-1'>name</td><td>ver</td><td>option</td>). Re-fetched the LOL API lists nolvus-awakening-v6 (V6, 2025-02-09), nolvus-awekening-redux (6.0.20, 2026-05-29), nolvus-v6-ultimate-open-beta-start (2024-12-28), mages-vikings (2.6.2, 2026-09-05), victolvus, nolvus0-20 and cust-nolvus. Checked the Nexus GraphQL v2 (legacyMods, mods search, modFiles) and the nolvus.net History, requirements, install and FAQ pages. Read the MV README and the Wabbajack modlists.json.

REPRODUCED COUNTS (same normalization): nolvus_current 2556 | mv_only 541 (+3 renamed = 544) | both 429 (+1 both_old) | nolvus_old_only 55 | neither 462. Plugins: 2105 / 717 / 672 / 107 fork / 643 none (exact match). Duplicate-digit folders: 70.

NOLVUS VERSION DATING (History 'Added new mod' vs target):
- 6.0.15 (2025-10-14): 88 of 135 additions present
- 6.0.16 (2025-11-14): 1/1 present (Hall of secrets - LOTD Fix)
- 6.0.17 (2025-11-17): 1/1 present (Curse of the Hound Amulet - True HUD Patch)
- 6.0.18 (2025-12-01): 2/7 present (Vanilla Hair Remake - SMP, Vanilla Hair - Salt and Wind)
- 6.0.19 (2025-12-10): 0/7 present. Absent: Bone Wolf Shutdown Fix, Alternate Perspective - CC Plugins Universal Start Fix, B.O.O.B.I.E.S - Potions, Armor Filter Framework (+Patches), Armor and Clothing Extension - SPID Patch, Apothecary - B.O.O.B.I.E.S patch.
- 6.0.20 (2026-01-27): 0/28 present. Absent: Claws/Twinblades movesets, SIGMA 1st-person, Animated Armoury, Unlocked 1st Person Combat, Vanilla Attack Annotation Fix, Oathvein UI.
- 6.0.21: no changelog; YouTube calls it 'Beta'. The list page shows 6.0.21-only replacements: Dynamic Footprints, True Armor - Evolved (+Settings), Nolvus Awakening Stances Perk System NG, Simple Follower Framework.

NOLVUS ROWS A DASHBOARD INSTALL WOULD ADD BUT THE TARGET LACKS (implied options; exact-name match; ~731 of ~3,702; upper bound), by section:
- 1.1 SKSE 4/36 (ENB Helper, ENB Input Disabler, Base Object Swapper 2.6.1 [target has 3.41], DLL Plugin Loader)
- 1.2 Fixes 9/74 (Powerofthree's Tweaks [target 1.15.1], Auto Parallax, …)
- 2.1 HUDs 15/96
- 2.3 Fonts/Map 5/13
- 3 Sound 2/85 (Dragonborn Voice Over 2 → DBReV)
- 4.2 LotD 12/19 (LotD 5.6.5 → V6)
- 4.3 Quests 26/256 (Vigilant 1.7.3 → VIGILANT SE 1.8, …)
- 5.2 LODs 3/5
- 5.3 Landscape 7/27 (Seasonal Landscapes, Nolvus Awakening Seasonal Ground, Northern Roads - Nolvus Fixes)
- 5.4 Snow 7/16
- 5.6.1 Trees 35/39
- 5.6.2 Grass 22/22
- 5.6.3 Plants 25/42
- 5.7 Weathers 19/24 (Seasons of Skyrim, Seasons of Nolvus, Seasonal Weathers Framework, …)
- 5.9 Water 2/16
- 5.10.x NPC 20
- Cities 12/13; Whiterun 36/40; Solitude 20/28; Riften 14/17; Markarth 11/14; Windhelm 13/16
- 5.11.2 Towns 71/115
- 5.11.4 Player homes 7/7
- 5.11.5 Other 6/8
- 5.12.1 Lands 49/80
- 5.12.2 Ruins 2/2
- 5.13 Interiors 53/108
- 5.14 Armor/Clothes/Weapons 15/587
- 5.15 Creatures 14/123
- 5.16 Objects 18
- 5.17 Lighting 54/102
- 6.x Animations 27 (Nemesis Unlimited Behavior Engine, Faster HDT-SMP [→ 4.01], claws/twinblades)
- 7.x Gameplay 42
- 8 Immersion 5/65
- 9 Late loaders 19/32 (Edge UI Explorer Addon set)
- 10 Outputs 10/28 (Synthesis Patch - NOSREX, Nemesis Output, Grass Cache - Ultimate, DynDOLOD Textures/Output - Ultimate, …)
- 11 ENB & Reshade 16/18 (ENB Binaries 0.505, ENB - ShaderCache, …)
Interpretation: the target keeps Nolvus' gameplay, combat, quest, NPC, armor and UI layers and takes the world and visual layer from MV plus the extra PBR/CS/Lux mods.

SIZES:
- Nolvus Awakening Ultimate (no SREX): 426 GB installed, 193 GB download, min 14 GB VRAM at 1080p.
- Ultra: 406 / 188 GB.
- Redux (no SREX): 372 / 170 GB, min 8 GB VRAM (GTX 1080) at 1080p.
- Graphics Only: 235 / 105 GB.
- MV 2.6.2: 3,772 archives, 229,998,290,486 B archives, 386,316,461,236 B installed, total 616,314,751,722 B.

=== (d) GENERATED OUTPUTS: regenerate, never download (9) ===
Pandora Output | dyndolodCS2 | texgenCS | grass CS | lodgen2 | pgpatcher_output | SYNTHESSIS | overwrite2 | BodySlide (Dressed) (matches a Nolvus row name; regenerate for added armors). Generated plugins: Synthesis.esp, FNIS.esp, PGPatcher.esp, PG_1.esp, PG_2.esp, DynDOLOD.esm, DynDOLOD.esp, Occlusion.esp. Optional local edit: YXZ_NRoad PBR DGS.esp (Perfect_Land_Fixer, optional method). 'Northern Roads - Overgrowing Grass Remover' matches an ARCHIVED prebuilt Nexus file (77893).
Base-list outputs to disable:
- Nolvus: Synthesis Patch*, Nemesis Output, BodySlide (Nude/Dressed), LODGEN*, Grass Cache - *, DynDOLOD - Textures/Output - *, CRDW - Cache, Photo Mode - Output, KiLoader - Output, ENB Binaries, ENB - ShaderCache. ('SKSE Output' does not exist; removed.)
- MV: Mages & Vikings - Pandora/BodySlide/PGPatcher/Grass Cache/xLODGen Output, DynDOLOD Output(s), Custom Files.

=== (e) CUSTOM / LOCAL (3) ===
CustomFixes1 (high) | CS shaders (low: probably a CS shader cache) | Vanilla CS rain TEXTURES (low)

=== (u) UNRESOLVED (5) ===
RMS Lux patch | horseAnimations2 (HorseAnimaTest.esp) | Wayshrines - JK's Skyhaven patch | Yet another patch hub for Ryn's Skyrim2 | Smooth Special Idle

=== (g) NON-NEXUS (13) ===
- CommunityShaders_AIO-2026-05-28T17-09Z: GitHub, probably a PR/pre-release build; no stable release on that date
- [full_inu] Armor Pack 01 SSE: blog/Patreon
- [Kirax] BDOR 2024 Female Collection: ModBooru/LoversLab
- [Dint999] BDOR Hairs SSE 0.23: Patreon/Discord; DwemerMods ESPFE repack
- [SSE] H2135 Fantasy Series8: Patreon/Discord
- Curious Adventurer: Aokili Patreon, now free-member access
- SC_HorseReplacer_SSE, SC_HorseReplacer: ShinglesCat Patreon
- [TalesOfStar] Air Balloons: Patreon/site/Bethesda Creations
- anchor animation v2 Part: Anchor Patreon (low)
- Grapple a1.7: Smooth Patreon, Tier 1+
- For Honor in Skyrim Black Prior: Smooth Patreon/Discord
- Lamas Tiny Hud - Edge version (SUKI): SUKI Patreon

=== (a-old) IN NOLVUS 6.0.20 AND EARLIER, NOT ON THE CURRENT (6.0.21?) PAGE (55) ===
Go to bed - Complete Crafting Overhaul Patch | Go to bed - Patches | Go to bed | Skyrim's Paraglider - Vampire And Werewolf Patch | Skyrim's Paraglider - Fix | Smart Optimal Salves - Duration Patch | Nether's Follower Framework - Settings Loader | Nether's Follower Framework | Equipment Durability System NG - Angelic Preset | Armor Rating Redux | True Armor - Nolvus Settings | True Armor - Settings Loader | ADXP - MCO - First Person Patch | Dirt and Blood - Widget Addon - Nolvus Settings | Nolvus Awakening Stances Perk System | Modern First Person Animation Overhaul | Stances - Animal Themed Combat Icons | Parallax Earth Floor Whiterun | Dawnguard Arsenal - Scabbardless Greatswords Loose File Replacers | RSV Patch Collection | Inigo - At Your Own Pace Patch | Racial Skin Variance - SPID (Player Vanilla) | Wet And Cold - Creation Club Patch | Wet and Cold - Nolvus Settings | Wet and Cold - Settings Loader | Wet and Cold - Gear | Wet and Cold | Vivid Landscapes - Complex Parallax Occulsion Snow - ProjectedDiffuse [2K] | Footprints - Beyond Skyrim Bruma Patch | Footprints - Gray Cowl of Nocturnal Patch | Footprints - Soul Cairn Patch | Footprints - Vigilant Patch | Footprints - SPID - Player Footprints | Footprints - SPID - Fix | Footprints - SPID | Footprints | Curse of the Hound Amulet - BodySlide | Curse of the Hound Amulet - True HUD Patch | Curse of the Hound Amulet - Fixes | Curse of the Hound Amulet | Falskaar - Comprehensive Fixes | Cutting Room Floor - At your Own Pace | Companions - Dialogue Bundle - At Your Own Pace Patch | At Your Own Pace - DBVO - Bella | At Your Own Pace - DBVO - Karat | At Your Own Pace - Dawnguard | At Your Own Pace - Thieves Guild | At Your Own Pace - Dark Brotherhood | At Your Own Pace - Companions | At Your Own Pace - College of Winterhold | At Your Own Pace - Main Quest | iWant Widgets NG | iWant Widgets | Sky UI - Nolvus Settings | Fast Travel Crash Fix
(Note: 'Dawnguard Arsenal - Scabbardless Greatswords Loose File Replacers' was already listed under 'Removed mods' in an earlier History entry.)

=== VERSION/ENGINE SWAPS VS BASE LISTS ===
- LotD 5.6.5 → 'Legacy of the Dragonborn V6' (11802; any 6.x, current 6.10.2)
- Vigilant 1.7.3 → VIGILANT SE 1.8 (+HiRes Pack 180, English Translation (Silent), English Voices Addon 1.8 esp); Nexus now 1.8.2
- Unslaad 3.0.2 → 'Unslaad SE2' (11789, now 3.0.6)
- Nemesis → Pandora v4.3.1-beta (MV uses Pandora; current 4.4.0-beta)
- ENB → CommunityShaders AIO (GitHub build) + NAT.CS III (139567) + Lux CS (153919), with NAT.ENB III kept
- DBVO 2 (84329) → Dragonborn ReVoiced (184221)
- Faster HDT-SMP → 4.01 (57339, now 4.1.1)
- Core Impact Framework → (EXPERIMENTAL) 2.0 (146873)
- 1.5.97 ports: Base Object Swapper 3.41 (60805, now 3.5.0), po3 Tweaks 1.15.1 (51073, now 1.17.1), Splashes of Skyrim 1.5 (47710), DAV for Skyrim 1.5 (88302), Skyrim Souls RE for Skyrim 1.5 (120085), NGIO - NG (1.5.11) (42161)
- Water for ENB → [cs] (37061)

=== (f) PUBLIC NEXUS, NOT IN EITHER BASE LIST (431) ===
Unchanged from the original result's full list; the spot-checked pages are correct. Correction: 'Prisma UI - Next-Gen Web UI Framework' is a Nolvus row, category (a), not (f). Key verified mappings:
- PBR Hub 139889 (Praedy's files ARCHIVED)
- 145417 Chantry
- 182981 YXZ
- 113926 Dancing LUX CS (archived)
- 87785 LOTDV6 Blubbo tree patch
- 86739 / 65232 Blubbo
- 167663 Unslaad/Clockwork PBR
- 167174 GTS PBR
- 167746 Margot, 124428 Jinx
- 65625 Elden Rim (Base 3.7.2 OLD_VERSION)
- 11802 LotD V6
- 11849 / 11894 / 11789 Vigilant/Unslaad
- 133232 Pandora
- 42161 NGIO
- 184221 DBReV
- 189799 Page's SmoothCam
- 187049 Texture Downscaler
- 161148 full_inu SPID

=== (b) MV-ONLY (544) and (c) BOTH (430) ===
Unchanged from the original result. Reproduced by name matching (541 + 3 renamed; 429 + 1). Regenerate mechanically by diffing user__modlist.txt against mages-vikings__modlist.txt and the nolvus.net table.

=== PLUGINS ===
- Generated: Synthesis.esp 4220, FNIS.esp 4219, PGPatcher.esp 138, PG_1.esp 4221, PG_2.esp 4222, DynDOLOD.esm 160, DynDOLOD.esp 4223, Occlusion.esp 4224
- Locally editable: YXZ_NRoad PBR DGS.esp 3971
- [FIX] plugins, origin unknown: 4155-4162
- From non-Nexus mods: [full_inu] Armor Pack 01.esp 1941 (needed by full_inu ArmorPack01 SPID.esp 4188); SC_HorseReplacer.esp 2155 (needed by Horsepower_Ragdoll - SC Horses Patch.esp 2158); H2135FantasySeries8.esp 2162; Curious Adventurer(.esp/ Light.esp) 2164-2165; [Kirax] BDOR 2024 Female Collection.esp 2188; [Dint999] BDOr_Hairstyles.esp 2192; AirBalloons.esp 2422; Anchor Animations Spell V2.esp 1937; AnchorShdSwd.esp 1947; FH_Grapple.esp 1943; HorseAnimaTest.esp 2172 (unresolved)
- Leveled List Patch.esp 4187 is Nolvus-provided. TerrainHelper.esp 4211 comes from MV (Terrain Helper).
- No DBVO.esp: DBReV replaces DBVO.
- LegacyoftheDragonborn0.esp (336): origin unverified (low).