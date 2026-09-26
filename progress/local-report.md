# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：4 組合清單（中途回報 2：下載與安裝）
- 日期：2026-09-26
- 結論：
  - Nexus 批次下載完成 449/450。1 個因 manifest 檔案編號錯誤而下載失敗。
  - 新寫的 `install_archives.py` 已自動安裝約 350 個沒有 FOMOD 的壓縮檔。
  - FOMOD 已在 MO2 手動安裝 66 個，另有 17 個待裝，多半是補丁集合、DBVO、Water for ENB、FWMF、CS Lights 這類要逐項對照的。
  - **需要雲端決定：10 個下載檔**（9 個版本或插件名稱和目標不符，1 個缺檔案編號），另有 1 個 note 和目標插件互相矛盾。
  - 合併安裝 3 個、Maerchenwald 2 個資料夾、Edge UI Racemenu（DIP）尚未處理。

## 工具結果（照抄 reports\*.txt 的每一行）
```
== nexus_fetch 報告 (2026-09-26 19:43) ==
[通過] 本次下載：429 個
總結：[通過]
（nexus_fetch.csv：downloaded 429、already_downloaded 20、http_404 1＝The Restless Dead - At Your Own Pace Patch）

== install_archives 報告 (2026-09-26 21:08)（第 4 次 --apply；前 3 次為 20:27 --limit 3、20:36、20:43）==
[資訊] 執行：判斷了 448 個下載
[資訊] 磁碟空間：預計解壓 12.0 GB，D:\ 剩 321.3 GB
[通過] 已安裝：84 個
[通過] 已重裝（舊資料夾在 _replaced）：4 個
[資訊] FOMOD，要用 MO2 安裝：68 個
[注意] 需要人工判斷（見 install_archives.csv 的 reason 欄）：29 個
[資訊] 先前已安裝：263 個
[資訊] manifest 目標還沒有下載檔：1 個
總結：[注意]
```
- 4 次合計自動安裝 3＋212＋34＋84＝333 個，再加 replace_dll 4 個（CRDW、Face Discoloration Fix、Native EditorID Fix、Classic Sprinting Redone）。
  - 舊資料夾都搬到 `D:\PM\_replaced\`，沒有刪除。新的 DLL 分別是 CRDW.dll、FaceGenFixes.dll、NativeEditorIDFix.dll、ClassicSprinting.dll。
- 「人工判斷 29」扣除已經用 GUI 裝好的 FOMOD 之後，還剩下面「需要雲端決定」的 10 個，以及合併安裝、Maerchenwald、DIP。
- D 槽剩 290 GB。

## 新工具與修正（本地提交，尚未推送）
- `nexus_fetch.py`：
  - 4000736、2dc3916：CDN 網址的檔名含空格、`#`、`?`、`%` 時要編碼，同時保留簽章 query。
  - CDN 回 403 時只把該檔記為 `cdn_http_403`，不再誤判成「金鑰無效」而中止整批下載。
  - 錯誤訊息會去掉 query，因為 query 裡有 user_id。
  - 2f607f1：`.meta` 的換行原本寫成 `\r\r\n`（text mode），改成 `newline=""`。
- `tools/install_archives.py` 和 `pm/layout.py`、`pm/sevenzip.py`、`pm/swap.py`，`mo2.py` 另加 `install_meta_text`／`mark_download_installed`（d218985、a1859e3、9207fad）。
  - 流程：
    1. 用 `.meta` 的 modID／fileID 對應到 manifest 的資料夾。
    2. 找資料根目錄：包括外層資料夾和 `Data` 資料夾；會用 provenance 的預期插件和目標 `plugins.txt` 檢查。
    3. 用 7-Zip 解壓到 `D:\PM\_install_staging`，再把資料根目錄整個改名放進空的佔位資料夾。
    4. 寫 MO2 的 `meta.ini`，並把下載的 `.meta` 標成 `installed=true`。
  - 交給人工的情況：FOMOD、結構不明確、插件和目標不符、note 寫 FOMOD／合併／DIP。
  - `--accept 資料夾`：人工看過壓縮檔後可放行「不認得的資料夾或檔案、預期插件不符、插件不在目標」這幾種疑慮。
  - 預設是試跑；`--apply` 時如果 MO2 還開著就拒絕執行。
  - 兩輪 code-reviewer，HIGH 都已修正：
    - 佔位資料夾中途被中斷會消失 → 改成先搬到旁邊再換上，並寫中斷紀錄，下次執行時自動還原。
    - Explorer 產生的 `desktop.ini` 讓 rmdir 失敗 → 視為空資料夾。
    - 還原時如果暫放的資料夾不見，會重建空資料夾，並用另一句訊息明確回報（`_replaced` 的內容不見時回報 FAIL）。
  - 另外修了幾個 MEDIUM：資料夾名稱比對不分大小寫、Windows 保留名稱、QSettings 值開頭是 `@` 時加引號、7-Zip 的長路徑。
  - 測試：PowerShell 下 127 項全過。
- 這些 `tools/`、`tests/` 的提交是否一起推送，要等使用者決定，因為平常只推 progress／data。

### `--accept` 放行清單（逐一看過壓縮檔）
- provenance 的插件欄有誤：
  - RMS Lux patch（壓縮檔只有材質，provenance 卻列 SDA - UnLux.esp）
  - YXZ …-PBR（YXZ_NRoad PBR DGS.esp 其實在 CORE 資料夾）
- 目標裡沒有、裝進去 MO2 會列為停用的插件：
  - Icy Windhelm - Windhelm Entrance Overhaul patch（note 也寫在目標是停用）
  - Dova Jump（DovaJumpMCM.esp）
  - Elden Rim - Base 3.72（RimImpactOfMob／OfPlayer）
  - Follower Dialogue Expansion - Aela（Vanilla Combat Block）
  - FuzzBeed's … Mihail Giant Club Variety
  - Grand Solitude - Landscape override
  - Orc Stronghold AIO - SkyShards Patch
  - Saviik's Solitude Overhaul（目標只載入 Grand Solitude x Saviik's Solitude 補丁）
- mod 自帶的資料夾或檔案：
  - Dragonborn ReVoiced2（DBReV）
  - Prisma UI（PrismaUI）
  - Pandora Behaviour Engine（exe；FNIS.esp 在目標裡）
  - DK's Realistic Nord Ships（.bsl）
  - SkyPlace（Data 根目錄的 json）
  - Breton Field Knight … PBR 2K（2K 材質；esp 在另一個資料夾）
- 已知資料夾清單另外加入：`DragonbornVoiceOver`、`Seasons`、`HeadPartWhitelist`、`BashTags`。
- 已確認 MO2 會把不在 `plugins.txt` 的新插件列為停用（目前 `plugins.txt` 有 257 行沒有 `*`）。

## 需要雲端決定的事
1. **下載的檔案和目標不符**：壓縮檔都還在 downloads，尚未安裝，佔位資料夾維持空的。

   | 資料夾（mod） | 目前的檔案 | 目標 | 建議 |
   |---|---|---|---|
   | Dreadful Alduin（136437） | 578734 Dreadful Alduin 8K v1.4（Dreadful Alduin.esp） | Dreadful Alduin Graphics Only.esp | 578735 Graphics Only 8K v1.4（OLD_VERSION），或 578737 Graphics Only 4K v1.4（ARCHIVED） |
   | RUSTIC SOULGEMS - Special Edition（5785） | 12944 1K Sorted | RUSTIC SOULGEMS - Unsorted.esp | 12943 1K Unsorted（或 12945 2K Unsorted） |
   | Thrones Expanded（139544） | 587744（ThronesExpanded.esp） | ThronesExpandedBOS.esp | 586268 Base Object Swapper v1.2（OPTIONAL） |
   | HFs - Whiterun bridges REDONE（158471） | 664921 (ESP) 4K（HFs_WhiterunBridges_REDONE.esp） | 目標沒有這個插件 | 沒有 ESP 的版本：662497（4K）或 662495（2K） |
   | Blubbo Trees Variations（119870） | 503101（Blubbo_Trees_Variations_Nexus.esp） | …_Nexus_noVanillaTrees.esp | 503110 noVanillaTrees（MAIN v0.9） |
   | Mostly Treeless Tundra - Northern Scenery Tundra（133515） | 560322（「Mostly Treeless Tundra - Northen Scenery.esp」） | Mostly Treeless Tundra - Northern Scenery - Whiterun Tundra Patch.esp | 這個 mod 頁面找不到同名檔案，可能出自別的頁面 |
   | Myrwatch - TnE - MyrwatchVaultFix - USCCCP Patch（97659） | 479879（「Myrwatch - TnE -  MyrwatchVaultFix - USCCCP Patch.esp」，中間兩個空格） | MyrwatchVaultFix - USCCCP Patch.esp | 這個頁面只有這一個；目標插件可能出自 MyrwatchVaultFix 自己的頁面 |
   | Orc Strongholds - AIO - EFPS Patch（89354，EFPS 頁面） | 627968（Orc Strongholds - Largashbur - EFPS Patch.esp） | Orc Strongholds - All In One - EFPS Patch.esp | 可能在 Orc Strongholds AIO 頁面的選用檔 |
   | Nature of the Wild Lands - Animations Addon（148132） | 715711 MESHES（沒有插件） | Nature of the Wild Lands - Animation Plugin.esp | 合併安裝 669507「NotW Animation - PLUGINS (FOMOD)」v1.03；FOMOD 要選一般／Less Sway／Even Less Sway 哪一個 |
   | The Restless Dead - At Your Own Pace Patch（94100） | manifest 的檔案編號是 94100（等於 mod 編號，id_source=inventory）→ HTTP 404 | 版本 1.2.6.1 | 624013「Patch - At Your Own Pace - Main Quest」v1.2.6.1（OPTIONAL） |

2. **Yggdrasil - Floating Tree Redux**：note 寫「FOMOD 選 Floating Tree」，但目標插件是 `Yggdrasil Trees.esp`，只有 Redux 的「Yggdrasil Trees (both)」會產生。選 Floating Tree 會產生目標沒有的 `Yggdrasil - Floating.esp`。我照目標插件選了 both，請確認。
3. **Maerchenwald**：`Maerchenwald - The Archwood Lite - Giant Fantasy Trees` 和 `Maerchenwald - Archwood Lite - Giant Fantasy Trees` 在目標 modlist 相鄰（3418／3419），對應同一個檔案（150187／628849）。兩個都裝同一份，還是捨棄一個？
4. **合併安裝的第二個檔**：Fortified Morthal 707429、Modern Hay 652905、Dwemer Researcher Backpack 723624 不在 manifest，所以 `nexus_fetch` 不會下載。要改 decisions 讓工具下載，還是由我手動下載？
5. **請確認幾個 FOMOD 選擇**（完整表格在附錄）：
   - BnP female small update 選了「I use no frostnip CBBE skin」（預設）；目標皮膚是不是 no frostnip 版不確定。
   - Lux CS Patch 另勾了 LightPlacer addon。
   - Vigilant 和 Unslaad 都選英文加 Silent Voice。
   - Bladedancer's Edge 用 ESL 旗標版。
   - 為了筆電改選的：CVEO 512p、High Quality PBR Ivy 2k、Wolves of Skyrim 2k、Texture Downscaler BALANCED。
   - Lore-Friendly Load Screen Compendium 是 21:9 版（約 7 GB），筆電螢幕是 16:10。
6. **MO2 外掛**：
   - Crash Log Labeler 雖然已在設定裡停用，每次開 MO2 仍會跳出 cp950 錯誤；`ModOrganizer.ini` 的 [Plugins] 看不到它的 `enabled=false`。
   - M&V 的 MO2 有 `PageFile Manager\autostart=true`（pagefile_size=20480）。這個外掛可能會去改 Windows 分頁檔，屬於系統設定，要停用嗎？
7. **guard.py**：在 Git Bash 下 cp950 輸出會讓 `test_guard_hook` 12 項失敗（guard 本身的判斷正確），建議改成 UTF-8／ASCII 輸出。

## 尚未完成（下一步）
- 17 個 FOMOD：Ancient Land Patches、Ashe 3、CS Lights2、DBVO Vampira、Flat World Map Framework2（replace_dll）、Grand Solitude Patch Collection、JK's Fort Dawnguard - SDA Patch、Riverwood Falls - Waterfall Additions、Ryn's Whiterun City Limits - Patch Collection、SDA - Standing stones patch、SDA Patch Hub SE、SilentStorm's Patches for DK's Realistic Nord Ships、Skyrim Main Menu - Edge Edition、Tiny Light Placer Hub2、Water for ENB [cs]2、Wayshrines - JK's Skyhaven patch、Yet another patch hub for Ryn's Skyrim2。
- 合併安裝 3 個、Maerchenwald、Edge UI Racemenu（DIP）。
- 全部裝完後：`prune_dependents` → `sync-order` → `verify` → `check_plugins` → `audit_skse`。

## MO2 GUI 操作的注意事項（給手冊）
- MO2 2.5.2 的 Downloads 分頁在篩選狀態下，右鍵選單會對到錯的列。這次跳出的是 LOTD PBR Odds and Ends 的 Quick Install，已取消。改用 File → Install Mod 輸入完整路徑。
- 大型壓縮檔解壓時，對話框有 Cancel 按鈕；這時按 Enter 會中斷安裝。Load Screen Compendium 第一次因此少了 esp，已重裝並確認完整。
- 在 MO2 裡已確認：新插件預設是停用；FOMOD 的 1.5.97 DLL 選項（Light Placer、BOS、PhotoMode、po3 Tweaks、Splashes、SLACK）MO2 都會依遊戲版本自動選。

## 附錄：FOMOD 選擇與產生的插件（已核對：產生的插件都在目標裡，例外見表內說明）
| 資料夾 | 選項 | 產生的插件 |
|---|---|---|
| Light Placer | SSE v1.5.97（MO2 依遊戲版本自動選） | 無插件；po3_LightPlacer.dll 大小與壓縮檔 SE 版相同 |
| Lux Orbis cs | No Effect 11；Lux Orbis Tweaks；Templates = Bright | Lux - HDR、Lux CS - Bulbs、Lux CS Templates - Bright、Lux Orbis CS（4 個預期插件全符） |
| Lux CS Patch | Tonemapping addon＋LightPlacer addon（說明：以 Light Placer 補回 CS 不支援的 Lux 粒子光源，需 ISL） | Lux - HDR |
| Lux (cs) | 選用效果全不勾；rugs/pelts/tables=None；Embers XD 只勾自動選的 BYOH fireplace；optimized meshes=Vanilla 與其後各群組預設；Improved Dwemer Glass meshes 勾（目標有 IDG）；SMIM／CC meshes 預設；Tomato Whiterun window models 勾（目標有 Tomato's Whiterun Remake），Mrf 不勾；Fixes：No Grass In Caves＋SLaWF，MEZF 不勾；USSEP pre update（目標 USSEP 4.2.9a）；Brighter Interior Cells Nights；templates 全 None | Lux、Lux - Master plugin.esm、Brighter interior nights、No grass in caves、SLaWF、USSEP patch（全在目標；provenance 只列 2 個，不完整） |
| NAT.CS III | NAT.CS；Mist mesh、Vanilla Sky Statics 不勾（Sky Statics 插件不在目標） | NAT-CS |
| YXZ …-PBR CORE | 確認已裝基礎包；DGS PBR | YXZ_NRoad PBR DGS |
| Realistic PBR Footprints | PBR footprints＋Sand Patch；Ultimate Fix 不勾 | Footprints - PBR Patch、SandPatch PBR Patch |
| Skeleton Replacer HD 2K SE | ESL；SkeletonsWithEyeGlow（保留原版眼窩發光）；SoulcairnSkeletons AE（作者的動態特效）；BeastSkeletons、M'Rissi 不勾（目標沒有這兩個 mod） | PraedysSkeletons.esl |
| Serana Re-Imagined | Vampire version CBBE（預設） | Serana Re-Imagined |
| Hood Plus Hair for Serana Re-Imagined | No Hair Physics + Re-Imagined Vamp Paleness（預設，與上一個一致） | Serana Re-Imagined（覆蓋同名插件） |
| Serana Re-Imagined - Eyes Re-Visited | 全預設：非 VR、黑髮、紅眼、Full glow | 無 |
| Immersive Flying Books | Arcaneum＋JK's Arcadia's Cauldron、COTN Dawnstar、JK's Blue Palace、JK's Elgrims Elixirs、JK's The Hag's Cure、LOTD（LOTD 本體尚未安裝，手動勾）；JKEEK Arcadia、JK's Dragonsreach 不勾 | 8 個，全符預期 |
| Improved Follower Dialogue - Lydia | Core＋Wyrmstooth＋LOTD；Bruma、停用 AA 不勾；外觀補丁 None | ImprovedCompanionsBoogaloo、LydiaPatchForLOTD、LydiaPatchForWyrmstooth |
| 3D Whiterun Trellis pbr | Metal（預設）；Shader = PBR（note） | 無 |
| Ancient City of Markarth | Required＋Lighting = Lux Orbis；Anti-Moss、Add-on 不選 | ACoM、ACoM Lux Orbis Patch |
| Ancient City of Markarth no Worldspace edits | 只有 Required | Ancient City of Markarth.esp（與上一個同名） |
| Ashe - A Visual Replacer2 | 全預設（作者推薦）：Alternative hair、Blue eyes、不加妝 | Ashe - Visual Replacer |
| [Dint999] Secret Child Of Talos | MAIN；Heels Sound = Yes（預設） | [Dint999] SecretChildOfTalos |
| Base Object Swapper 3.41 | SSE v1.5.97（自動選） | 無 |
| BiR's Remiel Replacer | High Poly Head（預設，不需另一個 mod）；Custom Skin - CBBE；Extras 不勾（2K 眼睛只為特寫；Glasses 插件不在目標） | HLIORemi-Replacer-Belladonna |
| Bladedancer's Edge | 3BA；外觀全預設；esp = default esl flagged（作者推 default；ESL 版省一個完整插件名額，目標沒有以它為前置的補丁） | BDE_Armor（ESL 旗標） |
| Bow Rapid Combo V3 | 不勾任何選項（Archer Dodge 可能與目標的 Dynamic Dodge Shot 重複；Spaghetti Western 是槍械 mod，目標沒有） | BowRapidCombo |
| BnP female small update | I use no frostnip CBBE skin（預設；不確定目標皮膚是否為 no frostnip 版，請確認） | 無 |
| Breezehome Exterior Overgrown | HS Breezehome（MO2 依已裝插件自動選） | Breezehome - Exterior Overgrown |
| Asura's Guard | 3BA 2K 檔；各步驟預設（Heavy、Heels Sound No、Never Nude No、材質 Default）；GND = Box Normal（效能好、非 NSFW；第一次操作時 MO2 預選 Box Figure [NSFW]，已取消重裝） | Asuras Guard [Armor] |
| Complete Vanilla Eye Overhaul (CVEO) by LDD | Core；各解析度 512p（作者說 512p 最適合遊玩，1024p 以上給特寫／截圖）；AO 1x；Carancula UV Original | CompleteVanillaEyeOverhaul_CVEObyLDD |
| Caliente's Beautiful Bodies Enhancer - 3BA NORMALMAPS | Normalmap = Fat（預設） | 無 |
| Daughter of Coldharbour - Reimplemented | Main；MCO（目標用 MCO）；NPC = Serana（預設） | DaughterOfColdharbourReimplemented |
| EVG Animation Variance | Recommended（安裝全部） | 無 |
| ERM - Textures pbr | Let's Start；Shader = PBR（note）；Mountain = Default | 無 |
| Fancy Morthal Swamp Overhaul | Continue；外觀預設（Original swampy color、Slick）；Patches 只勾 Nature of the Wild Lands | Fancy Morthal Swamp Overhaul、Fancy Swamp NotWL Patch |
| Faster HDT-SMP 4.01 | 1.5.97（自動）；NOT CUDA（推薦）；AVX（推薦，預設是 No AVX）；No MCM - Extreme performance（推薦）。先裝的 FSMPM MCM 版會多出目標沒有的 FSMPM esp，已重裝 | 無 |
| Grand Solitude - The Walls of High King Erling | Main＋Parallax meshes（必裝）；SMIM Rotor 勾（目標有 SMIM）；Majestic Mountains 不勾（目標沒有）；LOD = 窗戶隨日夜變化（推薦） | Grand Solitude - The Walls of High King Erling |
| Helmet Toggle 2 NEW2 | Core；DAV/FLM/KID/SPID（預設）；MCM Helper、Dragon Masks - SkyPatcher、Guards Pose with Helmets、Immersive Equipping Animations、Apophysis（目標都有對應 mod）；Immersive Speechcraft 不勾 | Helmet Toggle 2 |
| Hogwarts in Skyrim | IED Condition（推薦）；Dodge Shout 不勾 | Dovapotter |
| Immersive Weapon Switch | I4 = No, Thanks（I4 選項會產生目標沒有的 ImmersiveWeaponSwitch.esp） | 無 |
| Ivy - Riverwood Small Addon | Main；No Trees；JK's 補丁不選；Lux = Lux Orbis - Northern Vanilla Farmhouses；Statue of Mara 不選 | Riverwood Addon Standalone、Without Trees Patch、Northern Vanilla Farmhouses - Lux Orbis |
| Guards Pose with Weapons | Required＋5 種武器（單手盾、矛盾、雙手、長柄、弓）；Helmet 不勾（改用 Helmet Toggle 的 Guards Pose with Helmets） | 無 |
| Ivy Stendarr Beacon Overhaul | Main；Patches 只勾 Lux Orbis（note；自動勾的 3DNPC 補丁不在目標，已取消）；Frescoes = None | Ivy Stendarrs Beacon Overhaul、Lux Orbis Patch |
| Landscape Fixes For Grass Mods - Great Cities patch | 只勾 Mixwater Mill、Karthwasten（目標只有這兩個） | 2 個補丁 |
| Lod Model Library for DynDOLOD | Required；Saints and Seducers（SEC）不勾（目標沒有） | 無 |
| Lore-Friendly Load Screen Compendium (21-9) (4K) | 1.6.640 and earlier（依說明這是給舊版執行檔的超寬螢幕處理，本機 1.5.97；走這條分支實際是 21:9 2K 版）；All-Inclusive；Creation Club 版插件。注意：筆電螢幕是 16:10，這是 21:9 版，約 7 GB；第一次安裝被中斷（沒有 esp），已重裝確認完整 | LoadScreenCompendium |
| M.O.I.S.T. | BOS 版（note）；Without Random Swaps（推薦）；No Seasons Support（Seasons 插件不在目標） | Massive Outstandingly Insane Swamp Tree |
| Mahrlek1´s trees compilation - Whiterun Trees module | Vanilla（目標沒有 Fortified/Capital Whiterun、JK's Skyrim、DoS 本體、Spaghetti's Whiterun）；Breezehome universal patch（note） | Whiterun trees、Breezehome universal patch |
| Modern First Person Animation Overhaul | all weapon＋Daedric bow fix | 無 |
| PC Head Tracking and Voice Type SE | Main＋Patch | PC Head Tracking - MCM、PC Head Tracking - Patch |
| PhotoMode | SSE v1.5.97（自動） | PhotoMode |
| Powerofthree's Tweaks 1.15.1 | SSE v1.5.97（自動） | 無 |
| Phantom Horse | +70（推薦）；Shadowmere Rework 不勾 | Phantom Horse |
| RaySense - Jumping over obstacles2 | Hybrid（推薦） | 無 |
| Petroglyphs of Skyrim | Required；Mountain = ERM - Default（說明：可配 PBR 材質；目標有 ERM 本體與 PBR 材質）；Cave = Vanilla（目標的 ERM 本體沒有洞穴 mesh） | Petroglyphs of Skyrim |
| Petite to Plenty v9.0 | 全預設（v9 Movement、Scrotum collision Enable、Female config 預設） | 無 |
| Ruins Across Skyrim | Ruins Over Riverwood＋NOTWL、Northern Roads 補丁；Ruins of the Swamp；Falkreath Fort Ruins；Hjorn 補丁不勾 | 5 個，全符預期 |
| Save & Load Accelerator for SKSE Cosaves (S.L.A.C.K.) | Skyrim SE v1.5.97; SKSE64 v2.0.20（自動） | 無 |
| Splashes of Skyrim 1.5 | SSE v1.5.97（自動） | 無 |
| Shattered Royal Armor | UBE = None（自動）；PBR（目標有 Shattered Royal Armor PBR 4k） | ShatteredRoyalArmor |
| Skyrim Outfit Equipment System NG | Core；OStim 不勾 | SkyrimOutfitEquipmentSystemNG |
| Skyrim Tranquil ponds | 2k；CC Fishing、NotWL（目標沒有 Seasons of Skyrim 等其他對應 mod） | Skyrim Tranquil Ponds、STP - CC Fishing integration、STP - NotWL patch |
| Snazzy Misc Locations AIO | Black Briar Lodge、Drelas' Cottage、Honningbrew、Sarethi Farm；JK's Dragonsreach、JK's Palace、Wayward Rest 取消（插件不在目標） | 4 個 |
| Texture Downscaler | BALANCED（推薦；第 7 階段可再調） | 無 |
| VIGILANT SE 1.8 | Core；English（說明：英文使用者不要裝日文版，字型不符）；Silent Voice 勾（note：English Voices Addon 裝在 Silent 之上；目標另有 VIGILANT - English Translation (Silent) 與 Voices Addon 在上層） | Vigilant.esm（2.1 GB，完整） |
| Unslaad SE2 | Core；English；Silent Voice 勾（比照 Vigilant；目標有 Unslaad - English Voices Addon2 在上層，避免語音包沒涵蓋的台詞出現日文語音。先裝成不勾，確認後以 Replace 重裝） | Unslaad.esm（1.95 GB，完整） |
| Vanaheimr Mountains | True PBR；Smoother Normal None；Grey Textures 不勾 | Vanaheimr Mountains PBR |
| True Flasks NG | TrueFlasks Plugin；Upgradable Flasks（推薦）＋Flasks Restore Duration；Replace Vanilla Potions 不勾 | TrueFlasks、Upgradable Flasks、Restore Duration |
| Windhelm Mighty Statues Reforged | Talos（預設） | Windhelm Mighty Talos Reforged |
| Tomato's Riften PBR - 2k | 全推薦預設（原木紫漆、新紫色石板屋頂） | 無 |
| Tomato's Whiterun Remake - PBR or Complex Material | 全推薦預設（TomatoRim PBR Tundra Grass、Remake 屋頂／雕刻、新木盾、New Walls 2.3、Multilayer Parallax 窗） | 無 |
| Nature of the Wild Lands - Rock Replacer | PBR（目標有 NotWL PBR）；Grey（預設） | 無 |
| High Quality PBR Ivy | Main；Variant 1 2k（預設是 4k；目標沒指定，筆電用 2k） | 無 |
| nordic stonewalls pbr | 全預設（四項 Yes、Dark Grey、Style 1） | 無 |
| NordwarUA Legions PBR | 只勾 New Legion（目標只有 New Legion） | 無 |
| Complex Silverware PBR | Yes＋Rudy HQ 補丁（目標有 Rudy HQ - Miscellaneous）；Silver Object SMIMed 不勾 | 無 |
| Praedy's Chantry of Auriel AIO - SE | damaged（預設）；ruins Default、Ancient Falmer Armor、Bow Option 1、Shield Default、gems Default（這一步預設全是 None，等於不裝材質，已改；非 ENBL）；throne Default；ghosu 不勾；CPM 不勾 | Praedy's AncientFalmerThrone |
| Wolves of Skyrim | 2k（說明建議低規格電腦用 2k）；Fluffy Wolves（推薦）；SIC 補丁不勾（目標沒有 SIC） | 無 |
| Yggdrasil - Floating Tree Redux | Redux；Yggdrasil Trees (both)（推薦）；Magical Stairs。注意：note 寫「選 Floating Tree」，但目標插件是 Yggdrasil Trees.esp（只有 both 會產生），選 Floating Tree 會產生目標沒有的 Yggdrasil - Floating.esp，所以照目標插件選 | Yggdrasil Trees |
| Skyrim Wayshrines - Immersive Fast Travel - SWIFT SE | Core；Gray Cowl、Falskaar、Wyrmstooth、Darkend；Landscape and Water Fixes 補丁；Cathedral facegen 不勾（目標沒有） | 6 個，全符預期 |
| Seasonal Wigfrid's Erdtrees Replacer | Autumn Yellow（預設）；相容補丁不勾（插件不在目標） | 無 |
| UNDERDOG - Animations 3.0 | Install everything（預設是 Custom，已改）：Underdog Experience＋UA - EVG CLAMBER Patch（目標有 EVG Clamber） | 無 |
| Vanaheimr - Landscapes - AIO - PBR | Core；各選項預設（Ice Blue、Fieldgrass01 Green、Tundra01 Mixed，選用項都不勾）；Patch 勾 NGIO（目標有 NGIO - NG），Seasons 不勾。核心附帶的 SnowShader.esp 目標沒有（MO2 會列為停用） | Vanaheimr Landscapes（＋SnowShader，停用） |
