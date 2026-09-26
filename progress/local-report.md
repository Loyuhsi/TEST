# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：4 組合清單（中途回報 5：照 cloud-notes 8ec7ae0 的步驟 1–8；**沒有跑 `prune_dependents`**）
- 日期：2026-09-27
- 結論：
  - `verify`：modlist 一致，目標插件缺少 **16 個**（53 → 16）。
    - 15 個都在 8ec7ae0 列為「接受缺少／捨棄」的清單內。
    - 剩下的 1 個是 JKs Temple of Dibella 的 Frescoes 補丁，我沒有裝，原因見「需要雲端決定」第 2 點。
  - `audit_skse`：**通過**，沒有需替換的 DLL。
    - SMP Wind 的 `hdtSMP64.dll`、Skyrim Souls RE 原作的 `SkyrimSoulsRE.dll` 都已改名為 `.mohidden`。
    - Dova Jump 改裝 0.6.1。
  - A 組都照 decisions 重裝，舊內容都搬到 `D:\PM\_replaced`：
    - Vanaheimr：PBR 2k，239 個檔。
    - Riverwood Falls：1.2.1 FOMOD，15 個插件與目標完全一致。
  - **`check_plugins` 失敗兩項，prune 前一定要先處理第 1 項**：
    - 缺少前置 65 個，其中 41 個缺的是 **`_ResourcePack.esl`**（包含 `LegacyoftheDragonborn.esm`）。現在跑 prune 會把 LOTD 本體和它的補丁全部停用。
    - 前置順序錯誤 118 個，全都是目標清單本身的順序就是「補丁在前、主檔在後」。

## 照 cloud-notes 的步驟
1. `git pull --rebase`、`python -m pytest -q`：148 項通過、1 項略過。
2. `build_instance create --apply`（重建 `_expected`，多一個 Terrain Helper 佔位資料夾）→ 開 MO2 一次再關（MO2 有寫回 plugins.txt／loadorder.txt）。
3. `harvest --from mv --plan data/decisions.csv --apply`：Terrain Helper 已擷取（esp、DLL、Shaders ini）。
4. `manifest` → `nexus_fetch`（manifest：Dova Jump 704417、Skyrim Souls RE 27859/754726）→ `nexus_fetch --manifest data/extra_archives.csv`（新增的 8 個都下載到了，包含已封存的 TSOS 637231）。
5. 重裝與改名：
   - Dova Jump、Skyrim Souls RE - Updated：`install_archives --only … --apply`，舊資料夾搬到 `_replaced`。
     - Dova Jump 0.6.1 只有 OAR 動畫（93 個檔）。舊的 `DovaJumpMCM.esp` 不在目標清單、也沒有插件以它為前置。
     - Skyrim Souls RE 原作 3.1.2 裝好後，把它的 `SkyrimSoulsRE.dll` 改名 `.mohidden`；實際生效的 DLL 由「Skyrim Souls RE for Skyrim 1.5」提供。
   - SMP Wind：`hdtSMP64.dll` → `hdtSMP64.dll.mohidden`。
   - Vanaheimr：
     - manifest 把這列當成 keep，因為資料夾本來就有內容（上一輪回報的工具缺口 5）。
     - 所以我用只含這一列、action 暫改為 replace_dll 的臨時 manifest（放在 scratchpad）跑 `install_archives`。
     - 資料根目錄是外層的「…PBR - 2k」資料夾。裡面的 `PBRMaterialObjects` 工具不認得，看過內容（只有 1 個 json）後用 `--accept` 放行。
   - Riverwood Falls：舊內容（10 個插件＋meta.ini）先搬到 `_replaced`，再用 MO2 FOMOD 安裝到空資料夾（Merge）。選項照目標插件：
     - Patches：LFFGM、Ryn's Bleak Falls Tower、Fallen Trees、Ivy Small Addon、Riverwood Timber Rest、Natural Waterfalls。取消自動勾選的 Ancient Land 與 Wayshrines。
     - Tree Mods：只勾 NotWL。
     - Northern Roads：安裝；NR 補丁勾 Ryn's Bleak Falls、LFFGM、Lux Via；NR Extra 勾 Riverwood Timber Rest。
     - Optional Addons：勾 NR clutter（有 Northern Roads 選 Yes）、Treeless Path；不勾 Remove Fogs。
     - 不勾內建地形 LOD，和 1.0 那次相同，第 5 階段重建。
6. `fill_plugins --apply`：取出 26 個，連同選項資料夾共寫入 250 個檔，錯誤 0。
   - Praedy's Banner 的選項另外還有 2 張材質（不同資料夾），fill_plugins 沒帶到，我用上一輪的一次性腳本補上。
   - COTN Dawnstar 的 2 個 LotD 補丁：725411 裡的檔名是「(regular)」「(SFCO)」，FOMOD 安裝時會改成**目標的名稱**。
     - 目標沒有 SFCO，所以取 regular 版並照 FOMOD 改名放入。
     - 這兩個 FOMOD 選項只有插件本身，沒有其他檔案，目標名稱也不需要改。
   - Ryn's Water for ENB (Shades of Skyrim)：755856（1.7）的 228 個插件中沒有 Water／ENB／Shades 相關的，依指示捨棄。
   - JKs Temple of Dibella Frescoes：沒有裝，見「需要雲端決定」第 2 點。
7. `sync-order --restore-states --apply` → `verify` → `audit_skse` → `check_plugins`。

## 工具結果（照抄 reports\*.txt 的每一行）
```
== build_instance-create 報告 (2026-09-27 04:07) ==
[資訊] 模式：實際執行
[資訊] ModOrganizer.ini：已存在，保留（要重寫請加 --rewrite-ini）
[通過] 設定檔 Pages-ZH：modlist 4121 行（捨棄 21），plugins 4233 個（排除 12 個自製插件）
[資訊] 佔位資料夾：1 個（之後用 MO2 安裝到同名資料夾並選 Replace）
[通過] 遊戲 ini：Skyrim.ini, SkyrimPrefs.ini, SkyrimCustom.ini
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-040724
總結：[通過]

== harvest-mv 報告 (2026-09-27 04:08) ==
[資訊] 模式：實際執行
[通過] 計畫中要從 mv 擷取的資料夾：5 個：完成/已存在 5，來源缺少 0（見 harvest-mv.csv）
[資訊] 共享資料量（硬連結不佔額外空間）：34.8 MB
[資訊] 下一步：刪除 D:\MV 前，先執行 tools\zh\extract_official.py 取出官方繁中字串與字型
總結：[通過]

== manifest 報告 (2026-09-27 04:27) ==
[資訊] 目標資料夾：4047 個
[資訊] 已就位：4015 個
[資訊] 需從 Nexus 下載：0 個
[資訊] 第五階段重建：9 個
[注意] 需換成 1.5.97 版 DLL：2 個
[資訊] 尚無來源，需人工確認：0 個
[資訊] 捨棄：21 個
[資訊] 輸出：reports\manifest.csv、reports\downloads.html
總結：[注意]
（需換 DLL 的 2 個＝Dova Jump 704417、Skyrim Souls RE - Updated 27859/754726，已在步驟 5 重裝）

== nexus_fetch 報告 (2026-09-27 04:27)（manifest）==
[通過] 本次下載：2 個
總結：[通過]

== nexus_fetch 報告 (2026-09-27 04:28)（--manifest data/extra_archives.csv --limit 100）==
[通過] 本次下載：11 個
總結：[通過]
（nexus_fetch.csv：downloaded 11、already_downloaded 52。11 個中有 3 個是重複下載：LOTD Patches 783661、Watertowers 767948、Apothecary 763154。Nexus 沒有回報這 3 個檔的 size_in_bytes，工具就判斷不出已下載過）

== install_archives 報告 (2026-09-27 04:32)（--only Dova Jump --only Skyrim Souls RE - Updated）==
[資訊] 執行：判斷了 2 個下載
[資訊] 磁碟空間：預計解壓 23.3 MB，D:\ 剩 267.7 GB
[通過] 已重裝（舊資料夾在 _replaced）：2 個
總結：[通過]

== install_archives 報告 (2026-09-27 04:33)（Vanaheimr，臨時 manifest＋--accept）==
[資訊] 執行：判斷了 1 個下載
[資訊] 磁碟空間：預計解壓 747.3 MB，D:\ 剩 267.6 GB
[通過] 已重裝（舊資料夾在 _replaced）：1 個
總結：[通過]

== fill_plugins 報告 (2026-09-27 04:41)（--apply）==
[資訊] 模式：實際執行
[資訊] 目標插件缺少檔案：42 個（已排除第 5 階段的輸出插件）
[通過] 從壓縮檔取出：26 個
[注意] 找不到來源：16 個
[通過] 寫入結果：連結 0、解壓放入 250、已存在略過 3、錯誤 0
[資訊] 下一步：關 MO2 跑 build_instance.py sync-order --restore-states --apply，再 verify
總結：[注意]

== build_instance-sync-order 報告 (2026-09-27 04:45)（--restore-states --apply）==
[資訊] 模式：實際執行
[通過] 啟用狀態：依目標啟用 35 個、停用 0 個；檔案不在已啟用的 mod 或遊戲資料夾裡，略過 23 個（之後要再跑 prune_dependents）
[通過] 插件順序：4518 個：依目標順序 4210，新增的 308 個放在輸出插件之前
[資訊] 不在目標清單中的插件：COTN Falkreath - TGR Patch.esp, Lux - Auri Song of the Green patch.esp, COTN Falkreath - Mihail Haystacks patch.esp, Lux Orbis - ClefJ's Dragon Bridge Enhanced patch.esp, JKs Raven Rock - Daedric Shrines patch.esp, Lux - WindPath patch.esp, Ivy Riften Docks Overhaul - Fishermen Fish Patch.esp, JKs Nightingale Hall - Daedric Shrines patch.esp, Occ_Skyrim_GraniteHill_patch.esp, DBVO Fix - Missives Wyrmstooth.esp, Spaghetti's Towns - Rorikstead - NavCuts.esp, Northern Roads - Alpine Forest of Whiterun Valley Patch.esp, Occ_Skyrim_Jk's-Whiterun-Outskirts_patch.esp, DBM_DawnofSkyrimDC_Patch.esp, Snazzy Interiors - Whiterun AIO - TGR patch.esp
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-044527
總結：[通過]

== build_instance-verify 報告 (2026-09-27 04:45) ==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[注意] plugins.txt 與預期比對：缺少 16 個（mod 尚未安裝或已被修剪）；待重建輸出 7 個；例如：Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, Anchor Animations Spell V2.esp, FH_Grapple.esp, AnchorShdSwd.esp, SC_HorseReplacer.esp
總結：[注意]

== audit_skse 報告 (2026-09-27 04:45) ==
[資訊] 生效的 SKSE DLL：多版本 NG（可用）=132, 非 SKSE 外掛（相依函式庫）=1, SE 版（可用）=81
[通過] 需替換的 DLL：無
[通過] STOCK GAME 遊戲版本：1.5.97.0（需要 1.5.97.0）
[通過] SKSE 1.5.97：skse64_loader.exe + skse64_1_5_97.dll
[通過] Address Library（version-1-5-97-0.bin）：已找到
[通過] 遊戲根目錄的 ENB/ReShade 殘留：無（Community Shaders 可正常運作）
[資訊] 含 Root 資料夾的 mod（Root Builder 會部署到遊戲資料夾）：無
總結：[通過]

== check_plugins 報告 (2026-09-27 04:45) ==
[通過] 完整插件數（含本體）：253 / 254
[通過] 輕量插件數（ESL）：4036 / 4096
[失敗] 缺少前置的插件：65 個（見 reports\check_plugins.csv）
[失敗] 前置順序錯誤：118 個（見 reports\check_plugins.csv）
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 922 個；BEES 已安裝；遊戲 1.5.97.0
總結：[失敗]
```

## `verify` 還缺的 16 個插件
| 插件 | 8ec7ae0 的處理 |
|---|---|
| FH_Grapple.esp、AnchorShdSwd.esp、Anchor Animations Spell V2.esp、H2135FantasySeries8.esp、Curious Adventurer Light.esp、HorseAnimaTest.esp、SC_HorseReplacer.esp、[Dint999] BDOr_Hairstyles.esp | 捨棄（表 B，Patreon） |
| [Fix] Lux Orbis - Windhelm Entrance Overhaul patch - Revert Bridge.esp、Ancientland - Valtheim Statues Patch.esp、ModpocalypseNPCs-LotDV6-ErrorFixes.esp | 捨棄 |
| Northern Roads - Fortified Morthal.esp | 接受缺少（目標另有新名） |
| Orc Exiles - Bilegulch - Ryn's Dragon Mounds patch.esp、Orc Exiles - Bilegulch - Ryn's Lost Valley - 3DNPCs patch.esp | 接受缺少（2.0 已移除） |
| Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp | 755856 沒有新名稱 → 捨棄 |
| JKs Temple of Dibella - Solitude and Temple Frescoes patch.esp | **沒裝，等雲端決定**（第 2 點） |

## 需要雲端決定
1. **`_ResourcePack.esl`（prune 前一定要先處理）**
   - 現況：
     - `check_plugins` 有 41 個插件缺這個前置，包括 `LegacyoftheDragonborn.esm`、`LegacyoftheDragonborn0.esp`、Grand Solitude 本體、Hall of Forgotten 補丁、Flora Additions 等。
     - `D:\PM\STOCK GAME\Skyrim.ccc` 第 75 行有列 `_ResourcePack.esl`（遊戲會自動載入），但檔案不在 `STOCK GAME\Data`，任何 mod 也都沒有。
     - Nolvus 的 STOCK GAME 也沒有這個檔（Nolvus 的 LOTD 版本不需要它）。目標 modlist 沒有 Creation Club 資料夾。
   - 可用的來源有兩份，esl 大小不同：
     - Steam 遊戲資料夾（1.7.104）：`_ResourcePack.esl` 78,483 bytes、`_ResourcePack.bsa` 916,509,890 bytes。
     - `D:\MV\mods\Creation Club`（M&V 的 1.6.1170）：esl 78,418 bytes、bsa 大小相同。
   - 請決定：用哪一版，放到 `STOCK GAME\Data` 還是另建 mod 資料夾。如果放 mod 資料夾，是否還要在 plugins.txt 加一行。
   - 在這之前如果跑 prune，LOTD 本體與依賴它的大量補丁會被停用。
2. **JKs Temple of Dibella - Solitude and Temple Frescoes patch**：Frescoes 的版本對不上，我沒有裝。
   - D:\PM 的「Solitude and Temple Frescoes 2019」是 M&V 的 **Solitude Only（無燈籠）ESP** 版：`SolitudeTempleFrescoes.esp` 6,166 bytes，完整插件。provenance 的 110909 也是這一版。
   - 目標的 Grand Solitude 補丁也是對應這一版：`…Solitude ESP No Lanterns patch.esp`。
   - 目標另外啟用了 5 個 JK Frescoes 補丁（Haelga、Kynareth、Mara、Talos、Dibella）：
     - 在 JK's Interiors 的 FOMOD 裡，這 5 個只在「Complete」版才會安裝；選 Solitude Only 時不會產生任何 Dibella 補丁。
     - 已在 D:\PM 的 4 個（Haelga、Kynareth、Mara、Talos）是從 **Nolvus** 擷取的硬連結。Nolvus 用的是「Temple Frescoes - Complete」：`SolitudeTempleFrescoes.esp` 102,436 bytes，有 ESL 旗標。
     - 這 4 個補丁都以 `SolitudeTempleFrescoes.esp` 為前置，所以目前是「Complete 版的補丁＋Solitude Only 的主檔」。
   - 請決定：
     - (a) 主檔改用 Complete 版（Nolvus 有），Grand Solitude 補丁改成對應版本，Dibella 選 Complete 版安裝；或
     - (b) 維持 Solitude Only，捨棄這 5 個 JK Frescoes 補丁（包含已安裝的 4 個）；或
     - (c) 照現狀，另外指定 Dibella 用哪個版本。
3. **`check_plugins` 其他的「缺少前置」（24 個）**：大多是 Nolvus Awakening 自家補丁的前置不在目標裡。目標有啟用這些補丁，D:\PM 的檔案來自 Nolvus 擷取，前置是 Nolvus 清單的 mod。
   - 缺 NewArmoury.esp：Nolvus Awakening 的 Leveled Weapons、Weapons、Perk、Economy、Combat Scaling Overhaul - Consistency 補丁。
   - 缺 NewArmoury＋TwinbladesOfSkyrim：Weapons Balance、Leveled List Patch。
   - 缺 Nolvus Northern Roads Patch.esp：Northern Roads - Alternate Perspective Patch、Nolvus Awakening Alternate Start。
   - 缺 ClefJ's Dragon Bridge.esp：Combat & Enemies、Boss Integration。
   - 其他各 1 個：
     - EpicSolitude／EEKs Whiterun Interiors：AI Patch。
     - EpicSolitude：TSOS Patch。
     - AnotherOakwood：Consistency Patch。
     - Eli_Sicarius' Refuge：Armors Balance。
     - This Is Jorrvaskr：Clothes Patch。
     - BOOBIES_potions：Crafting Patch。
     - Populated Dungeons／Seranade／EEKs：CSO Enemy Level Mult。
   - 不是 Nolvus 補丁的：
     - SC_HorseReplacer：`Horsepower_Ragdoll - SC Horses Patch.esp`。
     - RedguarddiasporaRefinedSeries：`TSOSRefinedCreationClub.esp`。
     - SnozzResources：`Embershard.esp`。
     - AI Overhaul - USSEP Patch：`Grand Solitude - AI Overhaul patch.esp`。
     - Orc Exiles - Bilegulch Fixes：`Orc Exiles - Bilegulch - Ryn's Lost Valley Redoubt patch.esp`。
     - [full_inu] Armor Pack 01：`full_inu ArmorPack01 SPID.esp`。
   - prune 會停用這些插件。請確認可以接受，或是否要補回前置。
4. **`check_plugins` 的「前置順序錯誤」118 個（127 組）**：全部在目標 plugins.txt 的順序裡就已經是補丁在前、主檔在後（`check_plugins` 已把 ESM 旗標提前載入算進去）。
   - 最多的前置：
     - `COTN Dawnstar - Snazzy Interiors - Dawnstar AIO patch.esp`：10 組。
     - `JK's Jorrvaskr.esp`：7 組。
     - `Ivy Replacer BOS.esp`：5 組。
     - `JK's The Bannered Mare.esp`、`RealisticNordShips2.0.esp`、`Climb Watertowers of Skyrim.esp`、`JK's Palace of the Kings.esp`：各 4 組。
     - `Natural Waterfalls.esp`（目標第 150 列，它的 3 個補丁在第 147–149 列）。
   - 推測原因：Pages 用的補丁版本可能不需要這些前置，而我們擷取或下載的版本需要。請決定是否依前置關係重新排序（例如讓 sync-order 把前置排到依賴它的插件之前），或逐一處理。
5. 表 B 等「捨棄」的 11 個，以及接受缺少的 3 個：照 8ec7ae0 處理，prune 時一併停用依賴它們的插件。

## 本輪手動處理（非工具；只新增或搬移檔案，沒有刪除）
- Praedy's College of Winterhold - SE：Banner 選項的 `Textures/Architecture/WinterHold/winterholdbanner01.dds`、`_N.dds`（fill_plugins 只帶同一個子資料夾的檔案）。
- COTN Dawnstar Patch Collection2：`… Legacy of the Dragonborn (regular) patch.esp` → `COTN Dawnstar - Legacy of the Dragonborn patch.esp`；`… Dawnstar AIO + LotD (regular) patch.esp` → `… + LotD patch.esp`。與 FOMOD 的做法相同，都是改名放入。
- Riverwood Falls 的舊內容搬到 `_replaced`（Vanaheimr、Dova Jump、Skyrim Souls RE 由 install_archives 搬）。
- `D:\PM\_hold_downloads` 的兩個壓縮檔已搬回 `downloads`，空資料夾已移除。

## 工具缺口（建議雲端修改）
1. `manifest`：decisions 設為 download 的資料夾，如果裡面已經有內容，就會被當成 keep（Vanaheimr、Riverwood Falls），`install_archives` 也因此不會處理。
2. `fill_plugins` 的選項檔案：只帶「插件所在的子資料夾」。Praedy's Banner 這種選項的材質在另一個資料夾，就會漏掉。改讀 ModuleConfig.xml 找選項的 `<files>` 會比較完整（本輪與上一輪我都是這樣檢查的）。
3. `fill_plugins` 不處理 FOMOD 的改名（`destination`）。COTN Dawnstar 的 LotD 補丁、JK's 的 Frescoes 補丁都是改名後才是目標名稱。
4. `nexus_fetch`：Nexus 沒有回報 `size_in_bytes` 時，已下載的檔案會被重新下載（本輪 3 個）。可以改用 `.meta` 的 fileID 判斷已下載。
5. `install_archives` 不認得 PBR 相關的資料夾（`PBRMaterialObjects`，`PBRTextureSets` 則通過了），可以加進已知清單。

## 本地提交（尚未推送）
- 本回報與 status 的提交。
