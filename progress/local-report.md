# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：4 組合清單（中途回報 4：照 cloud-notes b3477ea 做完步驟 1–8；**依指示沒有跑 `prune_dependents`**）
- 日期：2026-09-27
- 結論：
  - 目標插件缺少檔案：622 → 337（上一輪 fill_plugins）→ **53 個**（`verify` 缺少 53、待重建輸出 7）。
  - `--plan-downloads` 的清單不能直接下載：50 筆中有 34 筆的檔案編號是佔位值（＝mod 編號），一定會 404；另外有 11 個候選合集在 manifest 沒有檔案編號，工具直接略過（COTN Dawnstar、COTN Falkreath、COTN Winterhold 等，共 84 個插件）。
    - 我改用 Nexus 的檔案清單和壓縮檔內容預覽逐一對照，把 50 個真正的檔案寫進 `data/extra_archives.csv`（50cdaa3）。
    - 用 `nexus_fetch --manifest data/extra_archives.csv` 下載 49 個（約 5.5 GB），另 6 個本來就有。
  - fill_plugins 再從壓縮檔取出 280 個插件。有 7 個插件的 FOMOD 選項還附帶模型／材質，另外補了 43 個檔，見「本輪手動處理」。
  - MO2 GUI 安裝完成：Load Screen 16:9、NotWL Animations MESHES（合併）、Fortified Morthal 磚＋屋頂、Modern Hay＋Hay Bale Fix、Dwemer Backpack HDT-SMP＋Lantern。
  - 剩下 53 個的分類：
    - 6 個：版本不符，我暫緩，建議整包重裝。
    - 8 個：屬於已捨棄的 Patreon 資料夾。
    - 2 個：只有 M&V 有。
    - 37 個：找不到來源。
  - 要在遊戲啟動前處理：SMP Wind 的 AE 版 `hdtSMP64.dll` 蓋掉 Faster HDT-SMP 的 SE 版（見「需要雲端決定」第 3 點）。

## 照 cloud-notes 的步驟
1. `git pull --rebase`、`python -m pytest -q`：通過（目前 146 項通過、1 項略過）。
2. crashlogtools 與 PageFile Manager 已搬到 `D:\PM\_disabled_plugins\`（搬移，沒有刪除）。
3. `manifest` → `nexus_fetch`（manifest 與 extra_archives）→ `install_archives`（01:12 裝了 9 個）→ MO2 合併安裝：全部完成。
   - Load Screen 用 625267（16:9 2K），資料夾名稱不變。FOMOD 選 All-Inclusive、Creation Club 版插件，與 21:9 那次相同。
   - 21:9 版的舊內容在 `D:\PM\_replaced`。
   - 裝好後有 883 個檔，`LoadScreenCompendium.esp` 就是 All-Inclusive CC 版（大小相符）。
   - NotWL Animations：MESHES 用 MO2 合併進 `Nature of the Wild Lands - Animations Addon`，共 721 個模型。
     - PLUGINS FOMOD 沒有再裝。原因：資料夾裡的兩個目標插件（fill_plugins 取出）和 PLUGINS 的「00 Main」（預設擺動幅度）雜湊相同。
     - 再裝一次只會多出目標沒有的 `NotWL - Autumn Tundra Animated.esp`。
   - Fortified Morthal 707429（2K PBR Roof）、Modern Hay 652905（Hay Bale Fix）、Dwemer Backpack 723624（Remi Lantern）：都先裝第一個檔，再用 MO2 選 Merge。
     - Hay Bale 模型確認是修正版。
     - Dwemer Backpack 的 HDT-SMP 檔（模型、材質、SMP xml）也一起合併了。上一輪只有取出插件，所以缺這 11 個檔。
   - Thrones Expanded／Myrwatch VaultFix 照原樣（插件不啟用）；Maerchenwald 只用 3418。
4. `harvest --from nolvus --plan data/decisions.csv --apply`：通過（The Restless Dead AYOP）。
5. `fill_plugins` 試跑 → 看過 csv → `--apply`（上一輪，622 → 337）。
6. `--plan-downloads` → 改寫下載清單（見上）→ `nexus_fetch` → `fill_plugins --apply`（本輪，337 → 54；其中 Load Screen 由 GUI 補上 → 53）。
7. `sync-order --restore-states --apply`：依目標啟用 570 個 → `verify`：缺少 53。
8. 回報：本檔。沒有跑 `prune_dependents`。

## 工具結果（照抄 reports\*.txt 的每一行）
```
== manifest 報告 (2026-09-27 01:05) ==
[資訊] 目標資料夾：4046 個
[資訊] 已就位：3999 個
[資訊] 需從 Nexus 下載：13 個
[資訊] 第五階段重建：9 個
[注意] 需換成 1.5.97 版 DLL：3 個
[資訊] 尚無來源，需人工確認：0 個
[資訊] 捨棄：21 個
[資訊] 輸出：reports\manifest.csv、reports\downloads.html
總結：[注意]

== install_archives 報告 (2026-09-27 01:12) ==
[資訊] 執行：判斷了 9 個下載
[資訊] 磁碟空間：預計解壓 5.2 GB，D:\ 剩 285.6 GB
[通過] 已安裝：9 個
總結：[通過]

== harvest-nolvus 報告 (2026-09-27 01:13) ==
[資訊] 模式：實際執行
[通過] 計畫中要從 nolvus 擷取的資料夾：1 個：完成/已存在 1，來源缺少 0（見 harvest-nolvus.csv）
[資訊] 共享資料量（硬連結不佔額外空間）：5.3 KB
總結：[通過]

== nexus_fetch 報告 (2026-09-27 01:51)（--manifest data/extra_archives.csv --limit 100 --apply）==
[通過] 本次下載：49 個
總結：[通過]
（nexus_fetch.csv：downloaded 49、already_downloaded 6，沒有錯誤）

== fill_plugins 報告 (2026-09-27 02:02)（--apply）==
[資訊] 模式：實際執行
[資訊] 目標插件缺少檔案：337 個（已排除第 5 階段的輸出插件）
[通過] 從壓縮檔取出：280 個
[注意] 不明確（見 csv 的 note）：4 個
[注意] 找不到來源：53 個
[通過] 寫入結果：連結 0、解壓放入 280、已存在略過 0、錯誤 0
[資訊] 下一步：關 MO2 跑 build_instance.py sync-order --restore-states --apply，再 verify
總結：[注意]

== audit_skse 報告 (2026-09-27 02:09) ==
[資訊] 生效的 SKSE DLL：AE 專用（1.5.97 無法載入）=2, 多版本 NG（可用）=131, 非 SKSE 外掛（相依函式庫）=1, SE 版（可用）=80
[失敗] 需替換的 DLL：2 個：DovaJump.dll（Dova Jump）, hdtSMP64.dll（SMP Wind）
[通過] STOCK GAME 遊戲版本：1.5.97.0（需要 1.5.97.0）
[通過] SKSE 1.5.97：skse64_loader.exe + skse64_1_5_97.dll
[通過] Address Library（version-1-5-97-0.bin）：已找到
[通過] 遊戲根目錄的 ENB/ReShade 殘留：無（Community Shaders 可正常運作）
[資訊] 含 Root 資料夾的 mod（Root Builder 會部署到遊戲資料夾）：無
總結：[失敗]

== build_instance-sync-order 報告 (2026-09-27 02:30)（--restore-states --apply，MO2 已關閉）==
[資訊] 模式：實際執行
[通過] 啟用狀態：依目標啟用 570 個、停用 0 個；檔案不在已啟用的 mod 或遊戲資料夾裡，略過 60 個（之後要再跑 prune_dependents）
[通過] 插件順序：4484 個：依目標順序 4173，新增的 311 個放在輸出插件之前
[資訊] 不在目標清單中的插件：DBM_HUB_Kozakowy_CBBE_Patch.esp, Occ_Skyrim_COTN-Morthal_patch.esp, TGC Winterhold - TGR patch.esp, Ivy - Riverwood Windmill Garden - USSEP Patch.esp, COTN Falkreath - SK Unique Signs Patch.esp, Dunmeri Furniture - man_DaedricShrines patch.esp, Snazzy Interiors - Karthwasten Hall - AI Overhaul patch.esp, Dawn of Skyrim - AI Overhaul Patch.esp, JKs Raven Rock - Daedric Shrines patch.esp, Nolvus Awakening Divine Elegance Grass Fix.esp, Nolvus Awakening Mixwater Mill Patch.esp, DBM_JKDragonsreach_Patch.esp, DBM_WheelsofLull_Patch.esp, JKs Bards College - Book Covers Skyrim Patch.esp, ACatsLife - JK's Dragonsreach Patch.esp
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-023047
總結：[通過]

== build_instance-verify 報告 (2026-09-27 02:30) ==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[注意] plugins.txt 與預期比對：缺少 53 個（mod 尚未安裝或已被修剪）；待重建輸出 7 個；例如：Lux Via - DK Nord Ships patch.esp, Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, DBM_HUB_TwilightPrincess_Patch.esp, LOTD_TCC_Twilight Princess Armor.esp, DBM_HUB_SoulHunterArmor_Patch.esp
總結：[注意]

== fill_plugins 報告 (2026-09-27 02:30)（試跑）==
[資訊] 模式：試跑（加 --apply 才會寫入）
[資訊] 目標插件缺少檔案：53 個（已排除第 5 階段的輸出插件）
[注意] 找不到來源：53 個
總結：[注意]

== manifest 報告 (2026-09-27 02:33)（全部安裝後重跑）==
[資訊] 目標資料夾：4046 個
[資訊] 已就位：4013 個
[資訊] 需從 Nexus 下載：0 個
[資訊] 第五階段重建：9 個
[注意] 需換成 1.5.97 版 DLL：3 個
[資訊] 尚無來源，需人工確認：0 個
[資訊] 捨棄：21 個
[資訊] 輸出：reports\manifest.csv、reports\downloads.html
總結：[注意]
```
- `fill_plugins` 02:02 的「不明確 4 個」處理如下：
  - Load Screen：GUI 裝好 16:9 後就補上了。
  - Watertowers 2 個：資料夾現有的 2 個補丁和壓縮檔的 `Climbable` 版大小相同，所以取 Climbable 版。
  - Freak's Floral Fields 主插件：M&V 放在 `optional\` 的那份，大小和壓縮檔的有懸崖版相同（`No Cliffs` 版不同），我在資料夾根目錄建了它的硬連結。
- 剩下 53 個缺少的插件中，只有 `SC_HorseReplacer.esp` 還是已安裝插件的前置（`Horsepower_Ragdoll - SC Horses Patch.esp`）。其他 52 個都沒有已安裝的插件依賴。
- `sync-order` 不在目標清單中的 311 個插件都是停用狀態，多半是合集裡目標沒勾的補丁。

## 剩下 53 個缺少的插件（步驟 8：插件、候選、說明）
**A 暫緩：資料夾內容版本和目標不同，建議整包重裝，等雲端決定（6 個）**

| 插件 | fill_plugins 的候選 | 說明 |
|---|---|---|
| Vanaheimr - Mines and Caves - PBR.esp | Vanaheimr - Mines and Caves - Complex Material - PBR; Texture Patch for Vanaheimr PBR Landscapes; Vanaheimr Mountains | 資料夾是非 PBR 2k（724570）的內容；這個插件只在 PBR 版（2k 724119／4k 724122）。已下載 724119，放在 `D:\PM\_hold_downloads` |
| Riverwood Falls - fallentreesbridgesSSE.esp | Riverwood Falls - Waterfall Additions for Riverwood2 | 資料夾是 1.0（628325）；這 5 個插件只在 1.2.1（633042）。資料夾現有的 10 個插件有 8 個和 1.2.1 版大小不同（含主插件 `Riverwood Falls.esp`），只補這 5 個會混用兩版。已下載 633042，放在 `_hold_downloads` |
| Riverwood Falls - Natural Waterfalls.esp | Riverwood Falls - Waterfall Additions for Riverwood2 | 同上 |
| Riverwood Falls - Ivy Riverwood Small Addon.esp | Riverwood Falls - Waterfall Additions for Riverwood2 | 同上 |
| Riverwood Falls - Riverwood Timber Rest.esp | Riverwood Falls - Waterfall Additions for Riverwood2 | 同上 |
| Riverwood Falls - Northern Roads - Riverwood Timber Rest.esp | Riverwood Falls - Waterfall Additions for Riverwood2 | 同上 |

**B 屬於已捨棄（drop）的 Patreon 資料夾：預期會缺（8 個）**

| 插件 | fill_plugins 的候選 | 說明 |
|---|---|---|
| FH_Grapple.esp | — | Grapple a1.7 |
| AnchorShdSwd.esp | — | anchor animation v2 Part |
| Anchor Animations Spell V2.esp | Goetia Animations - Magic Spell Casting | anchor animation v2 Part（候選 Goetia 是誤判，Goetia 1.5b 的壓縮檔沒有它） |
| H2135FantasySeries8.esp | — | [SSE] H2135 Fantasy Series8 |
| Curious Adventurer Light.esp | — | Curious Adventurer |
| HorseAnimaTest.esp | — | horseAnimations2 |
| SC_HorseReplacer.esp | Horsepower Ragdoll - SC Horses Skeleton Patch; SC Horses - Glowing Horse Fix; SC Horse Eye Replacer | SC_HorseReplacer／SC_HorseReplacer_SSE。**唯一還是已安裝插件前置的缺檔**：`Horsepower_Ragdoll - SC Horses Patch.esp` 以它為前置，prune 時會被停用 |
| [Dint999] BDOr_Hairstyles.esp | [Dint999] Forgotten Princess; [Dint999] Secret Child Of Talos; Dint BDOR Hair - Salt and Wind (Sassy) | [Dint999] BDOR Hairs SSE 0.23 |

**C 只有 M&V 有檔案、目標沒有對應資料夾（2 個）**

| 插件 | fill_plugins 的候選 | 說明 |
|---|---|---|
| TerrainHelper.esp | — | `D:\MV\mods\Terrain Helper`（M&V 載入順序有）。目標 modlist 沒有 Terrain Helper 資料夾 |
| [Fix] Lux Orbis - Windhelm Entrance Overhaul patch - Revert Bridge.esp | Lux Orbis - Patch Hub2; High Hrothgar Fixed - Lux Orbis Parallax Patch; Tel Mithryn Overhaul - High Poly and Improved Meshes - Lux Orbis Patch | `D:\MV\mods\Mages & Vikings - Custom Files`。在目標裡應該屬於已捨棄的 CustomFixes1 |

**D 已下載的壓縮檔和 Nexus 預覽（含舊版）都找不到（37 個）**

| 插件 | fill_plugins 的候選 | 說明 |
|---|---|---|
| DBM_HUB_TwilightPrincess_Patch.esp | Legacy of the Dragonborn Patches (Official)2 | 6.10.9（783661，178 個插件）沒有；LOTD 本體（11802）有預覽的各版也沒有。DBM_HUB／LOTD_TCC／DBM_CC 共 14 個同樣情況 |
| LOTD_TCC_Twilight Princess Armor.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| DBM_HUB_SoulHunterArmor_Patch.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| LOTD_TCC_Soul Hunter Armor.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| DBM_HUB_Unslaad_Patch.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| LOTD_TCC_Unslaad.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| DBM_CC_DMD_OAPSynergy.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| DBM_CC_Fish_ToKSynergy.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| DBM_CC_Gold_AoBSynergy.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| DBM_CC_GotT_MaSSynergy.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| DBM_CC_GrayCowlReturnsPatchMGTGCoNPatch.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| DBM_CC_Shad_AoBSynergy.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| DBM_CC_SoS_CheeseSynergy.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| DBM_CC_SunderWraithguardToKPatch.esp | Legacy of the Dragonborn Patches (Official)2 | 同上 |
| Northern Roads - Fortified Morthal.esp | Northern Roads Patch Collection; Northern Roads Patch Collection3; Northern Roads - Patches Compendium; Northern Roads Patch Compendium | NR Patch Collection 791369 與 NR Patches Compendium 794461 都沒有（這兩個已補出 15 個 NR 補丁） |
| Northern Roads Tents - Animated.esp | 同上 | 同上 |
| Northern Roads - COTN Dawnstar - Realistic Nord Ships - Lux Orbis patch.esp | 同上 | 同上 |
| Northern Roads - Skybound Underhang Camp patch.esp | 同上 | 同上 |
| Northern Roads - Thunderchild patch.esp | 同上 | 同上 |
| Northern Roads - Wintersun patch.esp | 同上 | 同上 |
| Orc Exiles - Bilegulch - IFD Lydia - 3DNPCs patch.esp | Orc Exiles - Bilegulch - Patch Collection; Orc Exiles - Rift Watchtower - Patches Collection | Bilegulch Patch Collection 2.0.2（761387）沒有（它補出另外 3 個） |
| Orc Exiles - Bilegulch - Ryn's Dragon Mounds patch.esp | 同上 | 同上 |
| Orc Exiles - Bilegulch - Ryn's Lost Valley - 3DNPCs patch.esp | 同上 | 同上 |
| Lux Orbis - Orc Exiles - Bilegulch Patch 1.3.esp | Lux Orbis - Patch Hub2 | Lux Orbis Patch Hub 695720 沒有 |
| Lux - Orc Exiles - Bilegulch.esp | Lux - Patch Hub3 | Lux Patch Hub 810478（7.2）沒有 |
| COTN Dawnstar - Legacy of the Dragonborn patch.esp | COTN Dawnstar Patch Collection2 | 只在 COTN Dawnstar 舊版 5.0／5.1（444311、477652）；5.9（725411）沒有，可能改名 |
| COTN Dawnstar - Snazzy Interiors - Dawnstar AIO + LotD patch.esp | COTN Dawnstar Patch Collection2 | 5.9 沒有，預覽也找不到 |
| DK Nord Ships - CC Fishing patch.esp | SilentStorm's Patches for DK's Realistic Nord Ships; DK's Realistic Nord Ships SSE | 兩個 mod 已下載的檔案和有預覽的檔案都沒有 |
| DK Nord Ships - Fixes.esp | 同上 | 同上 |
| Lux Via - DK Nord Ships patch.esp | Lux - Via (patch hub)2 | Lux Via 2.2（490655）與更新檔都沒有 |
| TSOS_Armor_Vilkas.esp | True Sons of Skyrim Refined | True Sons of Skyrim Refined（96246）在 Nexus 已隱藏；已安裝的副本沒有這兩個 FOMOD 選項 |
| TSOS_Sven_Lute.esp | True Sons of Skyrim Refined | 同上 |
| JKs Temple of Dibella - Solitude and Temple Frescoes patch.esp | JK's Interiors Patch Collection; JKs Guild HQ Interiors Patch Collection | JK's Interiors 706051 與 Guild HQ 745001 都沒有 |
| Ancientland - Valtheim Statues Patch.esp | Ancient Land Patches | Ancient Land Patches（409513）沒有 |
| ModpocalypseNPCs-LotDV6-ErrorFixes.esp | — | Modpocalypse NPCs - LotD（56635）只有 v1／v2／v3 三個主插件 |
| Praedy's WinterholdCollegeBanner.esp | Praedy's Chantry of Auriel - PBR; Praedy's Chantry of Auriel AIO - SE; Praedys College of Winterhold PBR | 三個候選都沒有 |
| Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp | Ryn's Whiterun City Limits - Patch Collection | 只在 78920 舊版 1.2.1／1.2.2；1.7（755856，已裝）沒有 |

- `verify` 還缺 **53 個**（＝上表），另有 7 個第 5 階段才產生的輸出插件。

## 需要雲端決定
1. **Vanaheimr - Mines and Caves**：目標資料夾名稱是「Complex Material - PBR」，目標插件是 PBR 版才有的 `Vanaheimr - Mines and Caves - PBR.esp`，但擷取來的是非 PBR 2k（manifest 的 724570 來自 M&V 的 meta.ini）。
   - 建議：舊內容搬到 `D:\PM\_replaced`，改裝 PBR 2k（724119，已下載）。筆電用 2k，要 4k 請說。
2. **Riverwood Falls**：建議把舊內容搬到 `_replaced`，用 1.2.1（633042，已下載）的 FOMOD 重裝。
   - 選項依目標插件決定：現有 10 個（主插件、NotWL、Treeless Path、Ryn's Bleakfalls Tower、Landscape Fixes for Grass Mods、Northern Roads 系列 5 個）加上表 A 的 5 個。
3. **SMP Wind 的 `hdtSMP64.dll`（遊戲啟動前一定要處理）**
   - 現況：
     - SMP Wind 1.1.0（76776/323734，就是 manifest 的 replace_dll 目標）的 `hdtSMP64.dll` 是 AE 專用（1,626,112 bytes）。
     - 它的優先順序高於 Faster HDT-SMP 4.01（SE 版 1,796,096 bytes），會蓋掉 Faster HDT-SMP 的 DLL，1.5.97 上 HDT-SMP 物理會整個失效。
     - SMP Wind 的 `SMP Wind.dll` 已被 SMP Wind NG（107718，NG 版）蓋過。
   - 建議：把 SMP Wind 資料夾的 `hdtSMP64.dll` 改名 `.mohidden`（和 FWMF 的 Baka DLL 做法相同），或整個停用 SMP Wind（76776）。請決定。
4. **Dova Jump**：已裝的 0.9.1.3（125550/781053，replace_dll 目標）的 `DovaJump.dll` 仍是 AE 專用。請決定捨棄或改用其他版本。
5. **Skyrim Souls RE - Updated**：manifest 仍列 replace_dll（155280/650644，AE 專用）。但「Skyrim Souls RE for Skyrim 1.5」（120085/809466，SE 版）優先順序較高，實際生效的是 SE 版，所以 audit_skse 沒有列出。可以改成 keep 或 drop。
6. 表 B（8 個）是 drop 的預期結果。其中只有 `Horsepower_Ragdoll - SC Horses Patch.esp` 會在 prune 時因缺 `SC_HorseReplacer.esp` 被停用。請確認可以接受。
7. 表 C：`TerrainHelper.esp` 要不要在目標加一個「Terrain Helper」資料夾（M&V 有），或捨棄？`[Fix] Lux Orbis … Revert Bridge.esp`（M&V 自訂檔）要不要比照？
8. 表 D 的 37 個：請雲端查來源，或決定捨棄。捨棄後 prune 不會影響其他插件，因為它們都不是已安裝插件的前置。
9. Freak's Floral Fields：M&V 把 `Freak's Floral Fields.ini` 藏起來（`.mohidden`，53 bytes），目前維持隱藏。Pages 有沒有用這個 ini 無法判斷，請決定。
10. 上一輪提到的工具問題請一併看：`locate_instance` 大小寫（1f4d624、a2c56b4，本地已修並有測試）。

## 本輪手動處理（非工具；都只新增檔案，沒有覆寫或刪除）
- 7 個插件的 FOMOD 選項附帶的檔案，用一次性腳本從同一個壓縮檔補上，共 43 個：
  - BeastHHBB RDO Replacer：4 個 facegen。
  - NotWL - Bruma：14 個 bstamriel 材質。
  - Green Thumb Solitude：19 個模型／材質（略過 Thumbs.db）。
  - COTN Falkreath Addons：1 個模型。
  - Lux - Grand Solitude：2 個模型。
  - Northern Roads - Grand Solitude：1 個模型。
  - Watertowers 的 2 個 Climbable 插件。
  - 檢查方法：讀 ModuleConfig.xml，找出安裝這個插件的選項，列出該選項的其他檔案，再和目標資料夾比對。
  - 上一輪取出的 32 個也用同樣方法查過，只有 Dwemer Backpack 缺檔（已在本輪 GUI 合併補上）。
- Freak's Floral Fields：`optional\Freak's Floral Fields.esp` 在根目錄建硬連結（大小與壓縮檔的有懸崖版相同）。5 個選項插件由 fill_plugins 取出；它們的 FOMOD 選項只有插件，沒有其他檔案。
- 為了不在雲端決定前混用版本，Vanaheimr PBR 2k 與 Riverwood Falls 1.2.1 的壓縮檔（含 .meta）暫時從 `D:\PM\downloads` 搬到 `D:\PM\_hold_downloads`，fill_plugins 因此沒有取出這 6 個插件。沒有刪除任何東西。
- `data/plugin_sources.csv` 新增 6 列：
  - Tiny Patch Hub 的 5 個補丁指定到 Hub3 資料夾。
  - `NotWL - Autumn Rift` 指定到 NotWL 主檔資料夾「…forest and trees improvement mod2」。原本工具依同前綴把它放進補丁合集；這個插件在 3.14 主檔的 `optional\`，版本與資料夾相同。

## 工具缺口（建議雲端修改）
1. `fill_plugins --plan-downloads`：
   - manifest 的佔位檔案編號（file id＝mod id）會照樣寫進清單。
   - 沒有檔案編號的資料夾會直接略過。
   - 已下載的壓縮檔裡沒有目標插件時（合集版本比目標舊），也不會提示要換新版。
2. `fill_plugins` 只取插件本體（加同名 BSA）。FOMOD 選項附帶的模型／材質不會一起裝（本輪 7 個）。建議依 ModuleConfig.xml 找出安裝該插件的選項，把選項的檔案一起裝，或至少列成「注意」。
3. `fill_plugins` 不看目標資料夾裡的 `optional\`：Freak's Floral Fields 主插件、Medieval Markets 2 個補丁都在那裡。
4. `fill_plugins` 用同前綴插件的位置猜資料夾：NotWL Autumn Rift 被放進補丁合集（已用 mapping 修正）。
5. manifest 的 keep 只看資料夾存在，不看內容版本。Vanaheimr（非 PBR vs PBR）、Riverwood Falls（1.0 vs 1.2.1）、Freak's Floral Fields（M&V 把插件藏起來）都是擷取內容和目標不同。
6. Nexus 的壓縮檔內容預覽，較新的檔案多半是 404（例如 Snazzy、JK's Interiors、Lux），只能靠下載後再比對。

## 本地提交（尚未推送）
- 1f4d624、a2c56b4：`locate_instance` 在 NTFS 上分辨 Nolvus 的 MODS 容器（上一輪）；fill_plugins 測試改用真實的 Nolvus 結構。
- 50cdaa3：`data/extra_archives.csv`（50 個下載）與 `data/plugin_sources.csv`（6 列）。
- 本回報與 status 的提交。
