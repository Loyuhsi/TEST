# zh_community

## SUMMARY
I re-checked the zh_community result against primary sources: Bilibili page data and comment API, a read-only Quark share listing, Nexus GraphQL, nolvus.net, the NolvusDashboard source on GitHub, SKSE, the moddingforge DSD and SSE-AT docs, Load Order Library, Bahamut and FKMods. Most claims hold. The main findings:

**Confirmed: 蘇禾's translation packs**
- The only current Chinese (Simplified) translation for Nolvus v6.0.20 is 蘇禾's (Bilibili uid 21501212, account now shows "账号已注销"; Nexus liujhsuhe; QQ group 362571190).
- Redux: DSD v2.2 (17.0 MB) plus Other v2.0 (2.3 MB). Ultimate without SR Exterior Cities: DSD v1.2 plus Other v1.0.
- Mages & Vikings (MV) packs exist only for 2.40.1 and 2.5.1. Nexus MV is now 2.6.2 (updated 2026-09-25), and there is still no 2.6.x pack.
- The licence line "禁止分流…（除了你自己玩）" (no redistribution; personal use only) is confirmed.
- The share also holds full English modlist archives of about 147–171 GB each, plus re-hosted Nexus files (DSD 1.4.3, Settings Loaders).

**Confirmed: tools, languages and Nexus coverage**
- Nolvus 6.0.20 (2026-01-27) is the latest release.
- The Dashboard offers only EN/FR/IT/DE/ES/RU/PL, and the install guide says only the base game gets translated.
- DSD 1.4.3 supports 1.5.97 and 1.6.640/1130/1170. Its 'original' field has been deprecated since 1.4.0.
- Steam lists Traditional Chinese as text only.
- Nexus tags 7,863 mods as Simplified Chinese and 8 as Traditional Chinese.
- There is no Chinese translation of Nolvus or MV on Nexus.

**Major corrections**
1. **Game version:** Nolvus Awakening runs on 1.5.97 with AE content, not 1.6.1170. Its mod list always installs SSE Fixes 3.1.5.97, Crash Logger 1.5.97 and Backported Extended ESL Support, so both base lists are 1.5.97-based.
2. **Skyrim 1.7:** Steam Skyrim moved to 1.7.99 (2026-08-20) and then 1.7.104 (2026-08-27; SKSE 2.3.1). The game must be downgraded or frozen, and DSD lists no 1.7 support.
3. **Bread:** its translations are not mostly 和光-based. Only 18 of 202 CHS entries in the 1.3 snapshot are WL-labelled, and the base translation, fonts and IME are disabled there.
4. **Terminology rules:** LordBuMing's rules convert only to ANK, 重光, 和光 or 驮鼠 terms, not to 大學 terms.
5. **SSE-AT limits:** it handles only plugins and interface txt files, not Papyrus scripts. It only finds translations linked from Nexus mod pages or a masterlist.
6. **Unconfirmed claims:** the Scaleform Translation Plus Plus "English fallback" and PX Translator's DeepL support could not be confirmed.
7. **Dates:** the Bahamut simplified-to-traditional conversion advice dates from 2016.

**Useful additions**
- The target list lacks DSD but already has Scaleform Translation Plus Plus NG.
- The target list uses the Sanguis font, which almost certainly lacks CJK glyphs.
- PX Translator has an EN→ZH-TW dictionary.
- 大學漢化 requires the game to be installed in English.

## FACTS
- [high] The Bilibili video '【我独自汉化】上古卷轴5 Nolvus整合包 更新v6.0.20汉化 v1.3' was published 2026-01-16 by mid 21501212, whose name now shows as '账号已注销' (account deleted). Its description changelog runs to 2026-03-06 and includes '修复2处ai错误翻译' (fixed 2 AI mistranslations) and a fix for '把提示词放进翻译' (the prompt leaking into the translation). The uploader's top comment gives Quark https://pan.quark.cn/s/bbf3491d44b2 ([redacted]), Baidu https://pan.baidu.com/s/1phyXQJlrg8yTuYXPefVOhg (t1c5), QQ group 362571190, and the notice '禁止分流和未授权使用本人汉化进行任何形式的汉化发布（除了你自己玩）' (no redistribution or unauthorized release in any form; personal play only). (https://www.bilibili.com/video/BV116rrBhEjF/ (page videoData) + api.bilibili.com/x/v2/reply?type=1&oid=115904322996651 (upper.top))
- [high] The same uploader (mid 21501212) published 'Nolvus整合包Redux v6.0.20 更新修正汉化 v2.0（插件+界面+MCM）' on 2026-05-06 and 'Nolvus整合包Ulitmate v6.0.20 汉化 v1.0（插件+界面+MCM）' on 2026-05-09. The same uploader also published Mages & Vikings v2.40.1 汉化 v1.0 (2026-04-08) and v2.5.1 汉化 v1.0 (2026-04-16), both described as '含文本+界面+脚本 MCM基本完全汉化' (text, interface and scripts; MCM essentially fully translated). (https://www.bilibili.com/video/BV1JvR4B1EcE/ ; https://www.bilibili.com/video/BV1SxRdB5EYx/ ; https://www.bilibili.com/video/BV1AnDrBmEAp/ ; https://www.bilibili.com/video/BV1o3d8BQE8n/)
- [high] The Quark share (title '苏禾的汉化小屋', owner nick '苏*', no expiry) contains the following:
- Nolvus/Redux（低配）/V6.0.20/汉化: '2. Nolvus Awakening Redux DSD v2.2.7z' (17.0 MB, 2026-05-10) and '3. Other [使用我的排序插件还原排序 v2.0].7z' (2.3 MB, 2026-05-06).
- Nolvus/Ultimate（顶配-无开放城市）/V6.0.20/汉化: 'Ultimate DSD v1.2' (17.0 MB) and 'Other v1.0' (2.3 MB).
- An older Redux V6.0.19 pack (DSD v1.3).
- Mages & Vikings/V2.5.1/汉化: 'Mages & Vikings DSD v1.1' (7.5 MB) and 'Other v1.0' (143.1 MB).
- Mages & Vikings/V2.40.1: DSD v1.0 plus Other (142.4 MB) plus a modlist backup.
- There is no MV 2.6.x folder; the MV folder was last updated 2026-06-12.
- '[Misc] 苏禾汉化mod的MO2排序插件/SortChineseLocMods.py' (2026-03-28). (local analysis: read-only listing via drive-pc.quark.cn/1/clouddrive/share/sharepage/token + /detail (access code redacted))
- [high] The same share re-hosts complete English modlist installs in '纯净本体-英文' folders:
- Nolvus Awakening Redux 6.0.20: 6×24.2 GB + 4.2 GB ≈ 149 GB
- Ultimate 6.0.20: 7×24.2 GB + 1.5 GB ≈ 171 GB
- MV 2.5.1: ≈ 148 GB
- MV 2.40.1: ≈ 143 GB
- Plus Apostasy, LoreRim, Authoria, GTSAV and others
It also re-hosts Nexus files in '[Misc] 共享缺失MCM及DSD', e.g. 'Dynamic String Distributor-107676-1-4-3-….7z' and several Settings Loaders. (local analysis: Quark share listing (access code redacted))
- [high] The translator's base-game pack evolved from 'skyrim本体+CC Su DSD v4.4–v5.5' (Jan–Mar 2026) to 'AE+CC Su DSD/STRINGS 6.0–7.6' (Mar–Jun 2026), then 'Skyrim AE & CC Su v7.7' (37.6 MB, 2026-06-17). The current file is '1.Skyrim AE & CC Dwiirok v1.4.7z' (37.6 MB, 2026-08-27). The jump from about 5.6 MB to 37.6 MB suggests fonts or more assets were added (inference). (local analysis: Quark share listing '[Main] 1.Skyrim AE & CC Dwiirok汉化' and its 'old version' subfolder)
- [high] The Nolvus Awakening install tutorial (蘇禾 translation, published 2026-03-10 by 无声的颂者) credits '蘇禾丶汉化BV116rrBhEjF' and QQ group 362571190. Its pinned comment of 2026-07-22 says fonts are now bundled with the translation and that load order is restored with the py plugin instead of a modlist file. (https://www.bilibili.com/video/BV16MNczeEgu/ (desc + upper.top via api.bilibili.com/x/v2/reply))
- [high] Nexus mod 166304 'LoreRim … Simplified Chinese Translation V5' is by uploader liujhsuhe, author 'suhe' (v5.0.3, updated 2026-06-15). Its description says it is based on ANK terminology, gives QQ group 362571190, mentions '1600+脚本的8000多字符串' (8,000+ strings from 1,600+ scripts), and mentions 'skyrim AE+CC Su汉化'. This ties the Nexus and Bilibili identities together. (Nexus GraphQL legacyModsByDomain(166304) ; https://www.nexusmods.com/skyrimspecialedition/mods/166304)
- [high] The latest Nolvus release is v6.0.20 (Tuesday, January 27, 2026). The previous releases were 6.0.19 (2025-12-10), 6.0.18 (2025-12-01) and 6.0.17 (2025-11-17). Nolvus has no '6.12' version. (https://www.nolvus.net/appendix/history)
- [high] The NolvusDashboard source populates the language dropdown with EN, FR, IT, DE, ES, RU and PL only. The install guide says: 'The language you select has to be the same than the one you selected in steam. Only the base game will be translated, not the mods.' So Steam must stay on English during a Nolvus install. (https://raw.githubusercontent.com/vektor9999/NolvusDashboard/main/Vcc.Nolvus.Dashboard/Frames/Installer/SelectInstanceFrame.cs ; https://www.nolvus.net/appendix/installer/install)
- [medium] Nolvus Awakening v6 runs on Skyrim 1.5.97 with Anniversary Edition content, not on 1.6.1170. The nolvus.net Awakening mod list marks 'SSE Fixes 3.1.5.97', 'Crash Logger - 1.5.97' and 'Backported Extended ESL Support 1.2' as 'Always Install'. The Nolvus Downgrade Patcher 'downgrade[s] your Skyrim Anniversary Edition 1.6 to 1.5.97 while keeping Creation Club content'. The local Nolvus v6 snapshot also contains Backported Extended ESL Support. (https://www.nolvus.net/awakening ; https://www.nolvus.net/downloads/installer ; local nolvus-awakening-v6__modlist.txt)
- [high] Steam Skyrim SE updated to 1.7.99 on 2026-08-20 and then to 1.7.104 on 2026-08-27. The current SKSE AE build 2.3.1 targets 1.7.104; SKSE 2.0.20 is still offered for 1.5.97. Coverage of 1.7.99 says it included 'localized strings fixes for UI and platform terminology' and recommends downgrading or freezing the version. (https://skse.silverlock.org/ ; https://wccftech.com/skyrim-1-7-99-update-modded-save-freeze-version/)
- [high] Nolvus Awakening v6 Redux WITHOUT SR Exterior Cities has these minimum specs: GTX 1080 with 8 GB VRAM at 1080p, i7 7000-series CPU, 372 GB install and 170 GB download. Ultimate needs 426 GB install and 193 GB download, and 14+ GB VRAM (RTX 4060 Ti) at 1080p. (https://www.nolvus.net/appendix/installer/requirements)
- [high] Nexus hosts Nolvus v6 translations in French (164621, for 6.0.19), Italian (171712), Brazilian Portuguese (164341), Turkish (164744) and Spanish (163858, for 6.0.14). A name search finds no Chinese Nolvus or Mages & Vikings translation on Nexus. (Nexus GraphQL mods(nameStemmed:'Nolvus'), legacyModsByDomain)
- [high] A Bahamut Skyrim-board search for 'nolvus' returns 7 threads, none of them a Nolvus translation. One is a CHT Apostasy modlist translation thread by johnex2x (2025-08-05), which matches Nexus 153938 'Apostasy … Traditional Chinese (CHT)' 3.1.4 by Vagrant999. (https://forum.gamer.com.tw/search.php?bsn=2526&q=nolvus ; Nexus GraphQL 153938)
- [high] Steam lists Traditional Chinese as a supported language for Skyrim Special Edition, as text only (no full-audio asterisk). (https://store.steampowered.com/api/appdetails?appids=489830&cc=us)
- [high] 大學漢化 (Nexus 1333) is v8.20.1, last updated 2021-11-30. It supports game versions 1.6.342.0 and 1.5.97, and says the game install language must be English. It covers Traditional and Simplified text, interface, fonts (with embedded dragon-script glyphs) and localized textures. A Bahamut guide notes that 大學漢化 does not cover Creation Club content. (https://www.nexusmods.com/skyrimspecialedition/mods/1333 ; https://forum.gamer.com.tw/C.php?bsn=2526&snA=45570)
- [high] The Bahamut guide '重零開始的SSE版漢化…1.6.1170' by 蘭泣露 was first posted 2024-02-25 and last edited 2025-01-08. It uses CHIOUSF's integrated package and states '大學漢化，不包括CCB部份的漢化' (大學漢化 does not include the Creation Club portion). (https://forum.gamer.com.tw/C.php?bsn=2526&snA=45570 (datePublished/dateModified))
- [high] Active CHT translators on Nexus include:
- Vagrant999 (memberId 3648424, 256 SSE uploads). Examples: Apostasy CHT 3.1.4 (153938), VIGILANT CHT 1.8.2 (158886, 2026-07-12), Unslaad CHT 3.0.6 (160631, 2026-07-12).
- zeinman55: Wyrmstooth CHT 85745 (1.20.1) and SIRENROOT CHT 123735.
- sedna1795: Bruma CHT 13821 (1.6.3, 2024-10-30); Ordinator 8081, Wintersun 29236 and Summermyst 6848, which are 正體+簡體 (Traditional + Simplified) and '請搭配《大學漢化》' (use with 大學漢化).
- hor0303: 3DNPC CHT 134422 (4.54) and Serana Dialogue Add-On CHT 32324 (2025-11-15).
- HappyToGoodJob: Project AHO CHT 24004. (Nexus GraphQL (mods filter uploaderId 3648424; legacyModsByDomain for listed IDs))
- [high] Nexus language tags: 'Simplified Chinese' returns 7,863 SSE mods, 'Traditional Chinese' returns 8, and 'Chinese' returns 0. CHT uploads are therefore usually tagged as Simplified Chinese. (Nexus GraphQL mods(filter languageName) totalCount)
- [high] 151 of the 752 'neither' plugins also appear in Load Order Library snapshots of other modlists: Apostasy 3.3.1 (52), LoreRim 4.5.3 (72), Gate to Sovngarde v115 (28) and Bread 2.0.3 (50), counted as a union. (local analysis: neither_plugins.txt vs api.loadorderlibrary.com/v1/lists/{apostasy,lorerim-4-5-3,gate-to-sovngarde-ae-wabbajack-conversion,bread-wabbajack-modlist})
- [high] All Nexus IDs cited for quest-mod Chinese translations exist:
- LOTD: CHS 125245 (6.10.0, LordBuMing); 和光 189600 (6.10.2FIX3, 2026-09-24); older 32693 (5.6.5, 2023); Patches 67206 and Curator 67173 (2023); Patches CHS 125248 and Curator CHS 125254.
- Bruma: 107140 and 33079; CHT 13821.
- Falskaar: 95876 and WL 191575.
- Wyrmstooth: CHT 85745, CHS 113345, WL 153952.
- Vigilant: WL 148389, 157383, CHT 158886.
- Unslaad: 113238; CHT 160631.
- 3DNPC: 81468 and 50349; CHT 134422.
- Moonpath: 113342 and WL 153942.
- Clockwork: 120497 and WL 166648.
- Forgotten City: 103429 and WL 172782.
- Others: Wheels of Lull 126084, Carved Brink 159435/191934, SIRENROOT 91393 (CHT 123735), Project AHO (CHT 24004, CHS 113341), Midwood Isle WL 169070, Konahrik WL 155936, Ordinator 8081/163696, Wintersun 29236/154392, Summermyst 6848/152848. (Nexus GraphQL legacyModsByDomain)
- [high] 和光汉化 (139134) is at v1.61 (2026-09-08). Its description states '1.6a版使用的是1.6.1170为基础，适配除SE1.7以外的全版本' (1.6a is built on 1.6.1170 and fits every version except SE1.7) and '1.6b版则是1.7专供' (1.6b is for 1.7 only). Its licence says '不接受任何形式的整合，不允许将本汉化词典用于盈利的mod翻译上' (no integration of any kind; the dictionary may not be used for paid mod translations). The Bilibili 1.6 video (2026-09-03) links the DSD pack 139300, WL DSD HUB 156602 (v1.51.7), and USSEP 139151, SkyUI 139844 and terminology rules 163518. (https://www.nexusmods.com/skyrimspecialedition/mods/139134 ; https://www.bilibili.com/video/BV19ato6REei/)
- [high] LordBuMing (= 望山) publishes 'General Terminology Transfer Rules for Simplified Chinese translation' (163518, v1.0.6). These are xTranslator batch search-and-replace files. It provides conversion rules only for ANK, 重光/汤镬, 和光 and 驮鼠 terms. 大學 terms (Simplified version) were used as a source, but no conversion target to 大學 terms is offered. 望山 also authors the FKMods '天际汉化索引' (Skyrim translation index; QQ 861430472), which recommends quality quest and follower translations. (https://www.nexusmods.com/skyrimspecialedition/mods/163518 ; https://fkmods.com/api/discussions/2844 (author 望山))
- [high] DSD 1.4.3 (107676, updated 2026-05-19) works on SE 1.5.97 and AE 1.6.640/1.6.1130/1.6.1170 (plus GOG and VR); 1.7.x is not listed. JSON files live in Data/SKSE/Plugins/DynamicStringDistributor/<Plugin>/*.json, and 'form_id' and 'type' are required. The 'original' field is 'Deprecated since version 1.4.0!'. DSD is described as 'ESP/ESM/ESL version independent', which lowers but does not remove the risk of version mismatch. (https://www.nexusmods.com/skyrimspecialedition/mods/107676 ; https://moddingforge.com/docs/dsd)
- [high] SSE Auto Translator (111491, v3.2.5, 2026-09-19):
- It scans a modlist, searches Nexus (and La Confrérie for French), downloads translations, converts them to DSD, and merges them into an Output Mod at the end of the list.
- Limitations: only plugin files and interface/*_<language>.txt translations are supported (Papyrus scripts are not yet). It finds only translations linked from the original Nexus mod page, or listed in a masterlist (only a small German masterlist exists).
- It supports the game languages, including 'Chinese' as a single language. Its FAQ says to set sLanguage in Skyrim.ini. (https://www.nexusmods.com/skyrimspecialedition/mods/111491 ; https://moddingforge.com/docs/sse-at ; https://moddingforge.com/docs/sse-at/faqs)
- [high] Bread (impaomian, Nexus 149063) is a Wabbajack list whose current version is 2.0.3.
- The Load Order Library 'Bilingual' 1.3 snapshot (2025-06-03) has 202 CHS or Chinese entries, only 18 of them WL-labelled, all installed as separate MO2 mods and disabled by default.
- Only 'Scaleform Translation Plus Plus NG' is enabled. 'Unofficial Chinese Translation (CHS WL)', 'HuaJianCi - Fonts CHS', 'Skyrim IME Support CHS', xTranslator and ESP-ESM Translator are present but disabled.
- The 2.0.3 snapshot still has about 470 disabled CHS entries. (https://api.loadorderlibrary.com/v1/lists/bread-an-immersive-modern-cs-modlist-bilingual ; https://api.loadorderlibrary.com/v1/lists/bread-wabbajack-modlist ; Nexus GraphQL 149063)
- [high] Scaleform Translation Plus Plus NG (77359, v1.9, 2026-08-24) is a CLib-NG port of Scaleform Translation Plus Plus (22603). The original adds nested translations with {} placeholders in interface/translations/*.txt files. The NG page warns it 'will break if a new Skyrim update comes along'. Nolvus Awakening always installs it (v1.6), and the target modlist already has it enabled. (https://www.nexusmods.com/skyrimspecialedition/mods/77359 ; https://www.nexusmods.com/skyrimspecialedition/mods/22603 ; https://www.nolvus.net/awakening ; local user__modlist.txt)
- [medium] The target modlist has no Dynamic String Distributor and no Chinese or CJK font mod. It enables 'Sanguis - Mist's Font Replacer' (Nexus 37001), for which separate Turkish (130112) and Cyrillic (117826) character variants exist. That strongly suggests the base font has no CJK glyphs. (local analysis: user__modlist.txt ; Nexus GraphQL nameStemmed 'Sanguis Font')
- [high] PX Translator (Nexus 143056, v5.1.5.9, 2026-08-08; GitHub YD525/PXTranslator, now branded SSE Lexicon/Lex Translator, GPL-3.0):
- Handles PEX, ESP/ESM/ESL and MCM, and writes DSD JSON.
- Supported target languages include Traditional Chinese and Simplified Chinese.
- Supports Cloud AI and Local AI (an LM Studio tutorial is provided).
- Offers an optional 'External Dictionary – EN TO ZH-TW' (by 傑基吾郎) and an EN TO ZH-CN dictionary (167033). (https://www.nexusmods.com/skyrimspecialedition/mods/143056 ; https://github.com/YD525/PXTranslator)
- [high] Other AI translation tools:
- iambupu/SkyrimModTranslation: a CHS workflow for Codex, opencode or Claude Code.
- fqscfqj/skyrim-xml-translator: PyQt6, OpenAI-compatible LLM, RAG glossary, DeepSeek-tuned options.
- XML Lore Translator (166599, v2.2.2) with a 和光 EN-ZH dictionary (166917).
- A Bilibili guide of 2026-04-11 shows xTranslator (134) with the DeepSeek API (deepseek-chat) plus DSD and SSEEdit. (https://github.com/iambupu/SkyrimModTranslation ; https://github.com/fqscfqj/skyrim-xml-translator ; https://www.nexusmods.com/skyrimspecialedition/mods/166917 ; https://www.bilibili.com/video/BV1A1DkBnEox/)
- [high] A 2016-11-06 Bahamut post advises against xTranslator's built-in simplified-to-traditional conversion, with the examples 只有→隻有 and 皇后→皇後. It recommends terminology conversion followed by Convertz802 with custom vocabulary. OpenCC separately provides a Taiwan-phrase profile, s2twp. (https://forum.gamer.com.tw/Co.php?bsn=2526&sn=136132 ; https://github.com/BYVoid/OpenCC)
- [high] The Bahamut Wabbajack guide (first post 2023-10-25) lists '沒有中文' (no Chinese) as a drawback. A 2025-01-23 reply says most modlists are English and suggests installing 大學漢化 and sorting the load order yourself. (https://forum.gamer.com.tw/C.php?bsn=2526&snA=45452)
- [medium] The 张裕汉化 release 'nolvus6.12完美汉化' (2025-05-14, uploader 精灵团娜娜, translation credited to @小寶與劍魂) exists. The same uploader's 2025-01-28 'nolvus V6 测试包 汉化/补丁' pinned comment says the package is 400 GB (200+ GB compressed) on Baidu and about 70% translated. It is unclear whether the 6.12 release shipped as a patch or a repack. (https://www.bilibili.com/video/BV1o5EPzPEWw/ ; https://www.bilibili.com/video/BV1FUFHeDEuL/ (upper.top))
- [medium] Two older Nolvus v5 Chinese packages exist:
- 吃虫子的橙 (2024-05-07): 'nolvus整合包redux中文汉化最新5.25版', a pre-installed package on Baidu, with most MCMs untranslated.
- 火鸡味锅巴粥 (2024-04-16): 'Nolvus 老滚整合包完全汉化版'. Its description only says 'ENB为TKV公开版' (the ENB is TKV's public version); distribution via a QQ group is not confirmed. (https://www.bilibili.com/video/BV1aw4m197zo/ ; https://www.bilibili.com/video/BV1HZ421v7JQ/)
- [high] LOREVUS (Nolvus 6 plus LoreRim), posted on Bilibili 2026-01-04, is built on the top N6 variant with open cities. It states '无汉化，汉不动' (no Chinese; too big to translate), and the pack is handed out by private message only. (https://www.bilibili.com/video/BV1TjinBfE3K/)
- [medium] The share also contains '[Misc] Project Skyrim/全天际中文配音/CNVoice-v1.1.7z' (about 1.98 GB, 2026-08-25), a Chinese voice-over pack, and SSEUpscaler v1.1. Where the voice pack comes from, and whether it is AI-generated, is not verified. (local analysis: Quark share listing)

## RISKS
- CORRECTION: The original risk said 'Nolvus v6 targets AE 1.6.1170 and MV targets 1.5.97'. This is wrong. Nolvus Awakening v6 also runs on 1.5.97 with AE content, via the Nolvus Downgrade Patcher. Its mod list always installs SSE Fixes 3.1.5.97, Crash Logger 1.5.97 and Backported Extended ESL Support. Both base lists are therefore 1.5.97-based, which makes merging them easier.
- CORRECTION: The '1.7' build that 和光 mentions is real. Steam Skyrim moved to 1.7.99 on 2026-08-20 and to 1.7.104 on 2026-08-27, and SKSE 2.3.1 targets 1.7.104. DSD 1.4.3 does not list 1.7, and Scaleform Translation Plus Plus NG warns that it breaks on game updates. The game must be downgraded to 1.5.97 or frozen before installing. Base-game Chinese packs built for 1.7 (和光 1.6b) must not be used; use 和光 1.6a or equivalent.
- CORRECTION: Bread's Chinese translations are not 'mostly 和光-based'. Only 18 of 202 CHS entries in the Bilingual 1.3 snapshot carry the WL label. Also, Unofficial Chinese Translation (CHS WL), HuaJianCi fonts and Skyrim IME Support CHS are disabled in that snapshot; only Scaleform Translation Plus Plus NG is enabled.
- CORRECTION: LordBuMing's rules (163518) cannot bridge into 大學漢化 (Taiwan) terminology. They provide conversion targets only for ANK, 重光/汤镬, 和光 and 驮鼠.
- CORRECTION: The 'English fallbacks' feature of Scaleform Translation Plus Plus NG could not be confirmed; only nested {} translations are documented. It is also not guaranteed to work on all versions: the NG page warns that it breaks on new Skyrim updates.
- CORRECTION: Two Bahamut dates were wrong. The 1.6.1170 guide was first posted 2024-02-25 (edited 2025-01-08). The Wabbajack guide was posted 2023-10-25. The advice against xTranslator's simplified-to-traditional converter dates from 2016, so it may not reflect the current tool. OpenCC s2twp is our suggestion, not stated community consensus.
- CORRECTION: 'Nolvus 6.12' is not a real Nolvus version (Nolvus uses 6.0.x numbering). The 400 GB repack statement is confirmed only for the 2025-01-28 V6 test pack. The afdian link and 火鸡味锅巴粥's QQ-group distribution are unverified.
- CORRECTION: PX Translator's DeepL support is not confirmed; its Nexus page confirms Cloud AI and Local AI (LM Studio). The tool has been renamed SSE Lexicon / Lex Translator.
- CORRECTION: SSE-AT cannot handle Papyrus (.pex) scripts; it handles plugins and interface txt only. It only auto-finds translations linked from Nexus mod pages or a masterlist, so it will not pick up 蘇禾's Quark-hosted packs.
- Piracy and malware risk. The 蘇禾 share, and the 张裕汉化 and 吃虫子的橙 packages, contain full pre-installed English modlists (about 143–171 GB each; 400 GB for 张裕). The 蘇禾 share also re-hosts Nexus files (DSD, Settings Loaders). Downloading these breaks Nexus and author permissions and risks tampered files. Take only the '汉化' subfolders, the base-game pack and SortChineseLocMods.py.
- Licence. 蘇禾's packs are personal-use only ('禁止分流…除了你自己玩'). 和光 forbids any integration. Any Traditional-converted or merged output must stay private and cannot go into a shareable Wabbajack list.
- Version drift. The MV packs target 2.5.1, but Nexus MV is 2.6.2, updated 2026-09-25. DSD no longer validates the original text, so changed records can show wrong strings. The 143 MB MV 'Other' pack replaces interface, MCM and script files that may be older than the 2.6.2 or target versions.
- Script breakage. The replacement .pex files in the 'Other' packs are compiled for specific mod versions. Each overridden script must be hash- or version-checked against the target's mod before it is allowed to win.
- Hybrid conflicts. The Nolvus and MV DSD packs may both hold JSON for shared plugins (e.g. LOTD) with different terminology. The translator's sort plugin (SortChineseLocMods.py) assumes a pure Nolvus or pure MV order.
- Unknown variant match. 蘇禾 has packs only for Redux and for Ultimate without SR Exterior Cities. There is no pack for the Ultra variant, and it is not stated whether the Redux pack assumes SR Exterior Cities on or off.
- Fonts and language. The target uses the Sanguis font, which almost certainly lacks CJK glyphs, so Chinese will render as boxes unless a CJK font overrides it. SSE-AT's FAQ says to set sLanguage, but Nolvus's ini uses sLanguage=ENGLISH, and most Chinese packs are designed for the English slot. Changing sLanguage=CHINESE can break interface *_english.txt lookups (unverified).
- Steam language. The Nolvus Dashboard requires the in-installer language to match Steam, and 大學漢化 requires English install files. Switching Steam to Traditional Chinese before or while installing would likely break Nolvus or Wabbajack file validation (likely, not directly verified).
- Quality. The 蘇禾 packs are partly AI-translated: the changelog records AI mistranslations and prompt leakage. Terminology differs across 大學, ANK, Su/Dwiirok and 和光. Simplified-to-Traditional conversion needs a phrase-aware converter.
- Distribution fragility. The Bilibili account is deleted, updates flow through QQ group 362571190, and Quark or Baidu may throttle downloads or require login to download (listing works without login).

## RECS
- Before anything else, freeze or downgrade Skyrim. Steam is now 1.7.104. Both base lists are 1.5.97-based: Nolvus through its Downgrade Patcher, which keeps CC content; MV through Wabbajack. Keep Steam on English throughout both installs.
- For a laptop, install Nolvus Awakening 6.0.20 Redux without SR Exterior Cities through the Nolvus Dashboard (minimum GTX 1080 with 8 GB VRAM at 1080p; 372 GB install, 170 GB download). This is also the variant with the most mature 蘇禾 pack (Redux DSD v2.2 plus Other v2.0). Install Mages & Vikings 2.6.2 through Wabbajack.
- From the 蘇禾 Quark share (link and access code: see the translator's Bilibili announcement / QQ group; intentionally not stored here), download only:
- Nolvus/Redux/V6.0.20/汉化 (DSD v2.2 and Other v2.0)
- Mages & Vikings/V2.5.1/汉化 (DSD v1.1 and Other v1.0)
- '1.Skyrim AE & CC Dwiirok v1.4'
- SortChineseLocMods.py
Never download the '纯净本体-英文' folders or the re-hosted Nexus files; get DSD from Nexus 107676 instead. Ask QQ group 362571190 whether an MV 2.6.x pack exists.
- Add the missing infrastructure to the target list: DSD 1.4.3 (107676), a CJK font placed after 'Sanguis - Mist's Font Replacer' (or the fonts bundled in 蘇禾's pack), and optionally Skyrim IME support. Scaleform Translation Plus Plus NG is already in the target list; keep it.
- Layer the translations in this order: base game, then the Nolvus DSD, then the MV DSD, then the 'Other' packs. Admit files from an 'Other' pack only when the target mod version matches; diff every .pex, .swf and .txt file first. Then run an SSE-AT scan of the final target list to pull Nexus-linked translations as DSD, for plugins and interface only.
- AI-translate what is still missing: leftover plugins, MCM files and .pex strings. Use PX Translator, which supports Traditional Chinese output, has an EN→ZH-TW dictionary and writes DSD, or xTranslator with DeepSeek, or skyrim-xml-translator. Seed a glossary from the base translation you choose.
- For big quest mods, prefer curated translations: the FKMods index (https://fkmods.com/d/2844) and the Nexus IDs listed in 'data'. Where native CHT versions exist, use them for dialogue-heavy mods: Vagrant999 (Vigilant, Unslaad, Apostasy), sedna1795 (Bruma, Ordinator, Wintersun, Summermyst), hor0303 (3DNPC, Serana), zeinman55 (Wyrmstooth, SIRENROOT) and HappyToGoodJob (Project AHO).
- For Traditional Chinese output, keep one Simplified master. Then run a phrase-aware conversion (OpenCC s2twp, or Convertz802 with a custom vocabulary) over the DSD 'string' values, the interface translation txt files and the MCM json. Proof-read names by hand, because no automated rules convert into 大學 terminology. Keep the result private.
- Follow Bread's MO2 practice: put each translation in its own mod directly below the original, or collect them into a single DSD output mod at the end, so English and Chinese can be toggled for troubleshooting.

## OPEN
- Does the Nolvus Downgrade Patcher, or the Dashboard's stock-game creation, handle 1.7.104 → 1.5.97 yet? The patcher page predates the August 2026 update.
- Does 蘇禾's Redux 6.0.20 pack assume SR Exterior Cities on or off? And is there any pack for the Ultra variant?
- Is there an MV 2.6.x pack, or one planned? The MV folder was last updated 2026-06-12, and Nexus MV 2.6.2 was updated 2026-09-25.
- Which terminology base does the 蘇禾 Nolvus/MV pack use (ANK, Su/Dwiirok, or something else)? ANK is confirmed only for his LoreRim pack.
- What do the 'Other' packs contain? Specifically: how many .pex scripts, which mod versions, why the MV pack is 143 MB versus 2.3 MB for Nolvus, and whether they expect sLanguage=ENGLISH with Chinese *_english.txt overrides. Answering this requires downloading the packs.
- Does the Dwiirok base-game pack (37.6 MB) include the CJK fonts mentioned in the 2026-07-22 tutorial comment? Does it work on 1.5.97 with AE content?
- Does SSE-AT's 'Chinese' setting pick up both Simplified- and Traditional-tagged Nexus translations, and does it require sLanguage=CHINESE?
- Does the user specifically want Traditional Chinese with Taiwan/大學 terminology, or is Simplified acceptable?
- How many of the roughly 600 uncovered 'neither' plugins actually carry translatable strings? This needs an SSE-AT or PX Translator scan of the installed target.
- What are the laptop's GPU, VRAM, RAM and free SSD space? Nolvus Redux alone needs 372 GB installed; MV and the hybrid add more.

## DATA
VERIFIED CHINESE PACKS (Quark share bbf3491d44b2, listed read-only on 2026-09-25)
| Pack | Latest file | Size | Date | Target |
|---|---|---|---|---|
| Nolvus Redux 6.0.20 | 2. Nolvus Awakening Redux DSD v2.2.7z + 3. Other [使用我的排序插件还原排序 v2.0].7z | 17.0 MB + 2.3 MB | 2026-05-10 / 05-06 | Nolvus 6.0.20 Redux |
| Nolvus Ultimate (no open cities) 6.0.20 | Ultimate DSD v1.2 + Other v1.0 | 17.0 MB + 2.3 MB | 2026-05-10 / 05-09 | Nolvus 6.0.20 Ultimate w/o SR Exterior Cities |
| Nolvus Redux 6.0.19 (old) | Nolvus DSD v1.3 + 其他汉化 v1.3 | 16.9 MB + 2.7 MB | 2026-02-07 | 6.0.19 |
| MV 2.5.1 | Mages & Vikings DSD v1.1 + Other v1.0 | 7.5 MB + 143.1 MB | 2026-04-16 / 04-15 | MV 2.5.1 (target 2.6.2) |
| MV 2.40.1 | DSD v1.0 + Other v1.0 + modlist backup | 6.9 MB + 142.4 MB | 2026-03-19 | MV 2.40.1 |
| Base game | 1.Skyrim AE & CC Dwiirok v1.4.7z | 37.6 MB | 2026-08-27 | AE + CC |
| MO2 sort plugin | SortChineseLocMods.py | <0.1 MB | 2026-03-28 | - |
| Do not download | 纯净本体-英文 folders: Redux ≈149 GB, Ultimate ≈171 GB, MV 2.5.1 ≈148 GB; re-hosted DSD and Settings Loaders | - | - | - |

GAME RUNTIME (corrected)
- Steam now: 1.7.104 (1.7.99 released 2026-08-20; 1.7.104 on 2026-08-27). SKSE AE 2.3.1 targets 1.7.104; SKSE SE 2.0.20 targets 1.5.97.
- Nolvus Awakening v6: runs on 1.5.97 with AE content (SSE Fixes 3.1.5.97, Crash Logger 1.5.97, BEES 1.2 always installed; Nolvus Downgrade Patcher 1.6→1.5.97 keeps CC).
- MV: 1.5.97 (per task context).
- DSD 1.4.3: 1.5.97 and 1.6.640/1130/1170 only.
- 和光 1.6a: all versions except 1.7. 和光 1.6b: 1.7 only.

NOLVUS v6 REQUIREMENTS (nolvus.net)
| Variant | Minimum GPU/VRAM @1080p | Install | Download |
|---|---|---|---|
| Redux w/o SR Exterior Cities | GTX 1080 / 8 GB | 372 GB | 170 GB |
| Ultra (Performance LOD) w/o cities | RTX 3080 / 10 GB | 406 GB | 188 GB |
| Ultimate w/o cities | RTX 4060 Ti / 14 GB | 426 GB | 193 GB |

TARGET LIST TRANSLATION INFRASTRUCTURE (local analysis)
- Present: Scaleform Translation Plus Plus NG; 'Sanguis - Mist's Font Replacer' (Nexus 37001; separate Turkish and Cyrillic variants exist, so it likely has no CJK glyphs).
- Missing: Dynamic String Distributor, any CJK font, IME support.
- Nolvus ini: sLanguage=ENGLISH.

BIG QUEST/CONTENT MODS: Nexus Chinese translations (IDs verified; CHS unless noted)
- LOTD: 125245 (6.10.0), WL 189600 (6.10.2FIX3, 2026-09-24), Patches 125248 (6.10.2), Curator 125254; older 32693 (5.6.5), 67206, 67173
- Bruma: 107140, 33079; CHT 13821 (1.6.3)
- Falskaar: 95876 (2.2), WL 191575
- Wyrmstooth: CHT 85745 (1.20.1), 113345, WL 153952
- Vigilant: WL 148389 (1.8.2), 157383; CHT 158886 (1.8.2)
- Unslaad: 113238 (3.06); CHT 160631 (3.0.6)
- 3DNPC: 81468, 50349; CHT 134422 (4.54)
- Moonpath: 113342, WL 153942 | Clockwork: 120497, WL 166648 | Forgotten City: 103429, WL 172782
- Wheels of Lull: 126084 (6.0.0.1) | Undeath: 71730, 63318 | Carved Brink: 159435, WL 191934
- SIRENROOT: 91393 (1.30); CHT 123735 | Project AHO: CHT 24004, 113341 | Midwood Isle: WL 169070 | Konahrik: WL 155936
- Ordinator: 8081 (正體+簡體, 9.30.0, 2021), 163696 (9.35.0) | Wintersun: 29236 (正體+簡體), WL 154392 | Summermyst: 6848 (正體+簡體), WL 152848
- USSEP: 1354 (大學, 2021), WL 139151 (4.3.9a) | SkyUI: 1342 (2017), WL 139844 (6.7)
- Base game: 大學 1333 (CHT+CHS, 8.20.1, 2021, 1.6.342/1.5.97, no CC), 和光 139134 (1.61), WOK 10845 (2021)
- Apostasy modlist: CHT 153938 (Vagrant999, 3.1.4)

TOOLS
- DSD 107676 (1.4.3)
- SSE-AT 111491 (v3.2.5; plugins and interface only)
- xTranslator 134 (1.4.5)
- ESP-ESM Translator 921 (4.35), with CHS UI 152795 and databases 76743/137292
- PX Translator / Lex 143056 (5.1.5.9; ZH-TW dictionary as an optional file; ZH-CN dictionary 167033)
- XML Lore Translator 166599, with WL dictionary 166917
- Scaleform Translation++ NG 77359 (1.9)
- HuaJianCi fonts 118230
- Terminology rules 163518 (1.0.6)
- WL DSD HUB 156602 (1.51.7)
- OpenCC s2twp or Convertz802 for Simplified→Traditional conversion

NEXUS LANGUAGE TAGS: Simplified Chinese 7,863; Traditional Chinese 8; Vagrant999 has 256 SSE uploads.
OVERLAP: 151 of 752 'neither' plugins appear in Apostasy 3.3.1 (52), LoreRim 4.5.3 (72), GtS v115 (28) and Bread 2.0.3 (50).