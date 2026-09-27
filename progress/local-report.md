# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：5 重建輸出（照 cloud-notes d9c97ca「接下來的順序」1–8；**第 9 步 Synthesis 照 docs/05 第 3 節停下**）
- 日期：2026-09-27
- 結論：
  - **主選單修好了**：
    - NPC Overhaul 換成 v2。
    - `strip_refs` 產生 Modpocalypse LOTD 的修正版，刪掉 10 筆 NPC 的 12 個失效引用。
    - LOTD 相關 3 個插件全部啟用，DataLoaded **176 秒**，到得了主選單。
  - **OAR 3.2.1**：
    - RaySense 的條件已經註冊成功。
    - OAR 錯誤從 533 行降到 104 行，其中 80 行是「RaySense_Ledge 條件找不到」。
  - **check_plugins 全部通過**：完整 251／254、預估 253／254、輕量 4015／4096。
  - **verify**：缺少或未啟用 41 個＝接受缺少的 15 個＋修剪的 26 個。
  - **BodySlide（勾 Build Morphs）**：5,825 個 nif＋2,929 個 tri。和 Nolvus 都有的檔中，nif 有 5,428／5,450 個、tri 有 2,735／2,741 個**逐位元組相同**。
  - **Synthesis 停下**：Nolvus 的 Synthesis.esp 裡，7,664 筆 LAND **全都有 VCLR**，而且是比原版亮的顏色，不是刪掉或全白。見「需要雲端決定」第 1 點。
  - 第 10、11 步（PGPatcher、草地、LOD、第一次用 CS 啟動）都還沒做。
  - `audit_skse --dll`：舊的 AE 版 Knockback 仍被判成「多版本 NG」。兩版的字串和版本區塊都相同，靜態檢查分不出來。

## 照 cloud-notes 的步驟
1. `git pull --rebase`（d9c97ca）、`python -m pytest -q`：188 項通過、1 項略過。
2. `build_instance create --apply`：
   - 試跑的數字和正式執行相同。
   - 佔位資料夾 1 個，是 `Pages - LOTD V6 修正`。
   - 開 MO2 一次再關，15:51 寫回 plugins.txt。
   - `verify`：modlist 一致，沒有「MO2 移除了」；清單外的資料夾 84 個（資訊）；缺少或未啟用 16 個（修剪前）。
   - CS 4 個的資料夾名稱和雲端寫的相同。順序和我上一輪放的相反，但本體和 3 個附加元件之間沒有任何同名檔案，順序不影響。
3. 重裝：
   - `manifest`：reinstall 2 個（Open Animation Replacer4、Legacy of the Dragonborn - NPC Overhaul2），download 0。
   - `nexus_fetch` 下載 2 個（798222、514540）。
   - OAR：
     - `install_archives --only "Open Animation Replacer4"` 試跑是「可自動重裝 1 個」，接著 `--apply`，舊資料夾在 `_replaced`。
     - 新舊版的內容都只有 `OpenAnimationReplacer.dll`／`.pdb`。
     - 新 DLL 用 `audit_skse --dll` 判為「多版本 NG（可用）」。
   - NPC Overhaul（MO2 GUI）：
     - 舊插件 68,061 bytes，對應 `00 Main`。FOMOD 只有一步「Choose Auryen Version」：Version 1＝`00 Main`＋AltAuryen，Version 2＝只有 `00 Main`，所以選 **Version 2**。
     - 先關 MO2，把舊內容（267 個檔）搬到 `_replaced`，再用「Install Mod」安裝。Name 改成 `Legacy of the Dragonborn - NPC Overhaul2`，「Mod Exists」時對已清空的資料夾選 Replace。
     - 結果：插件 68,095 bytes，267 個檔，`meta.ini` 的檔案編號是 514540，已啟用，位置不變（1636）。
   - 重跑 `manifest`：reinstall 0。
4. `fill_plugins`：`AI Overhaul - USSEP Patch.esp` 從 M&V 的 `AI Overhaul SSE` 以硬連結補到 D:\PM 的 `AI Overhaul`（83,629 bytes）；找不到來源 15 個，都是已接受缺少的。
5. `strip_refs`：
   - 試跑和正式執行的結果相同。
   - 修正版 `Modpocalypse NPCs (v3) Legacy of the Dragonborn.esp` 寫在 `Pages - LOTD V6 修正`：117,725 bytes，記錄不壓縮所以比原檔大。原檔 113,904 bytes 是硬連結，沒有改動。
   - `Pages - LOTD V6 修正` 在 modlist 第 2 行（啟用，僅次於 `Pages - 設定覆寫`）。
   - 刪除清單（`reports\strip_refs.csv`，12 個引用、10 筆 NPC）：

     | NPC（LegacyoftheDragonborn.esm） | 刪掉的子記錄 → 指向的已不存在記錄 |
     |---|---|
     | 0E66A7、12537E、270365、33D910、4D1803、58B96B | CNTO → 124FCA（各 1 個） |
     | 34D536（之前卡住的那一筆） | PKID → 47C542、595CC1、595CC0 |
     | 35CC27 | PKID → 47C541 |
     | 3AF18E | PKID → 47C540 |
     | 3DCEB3 | PKID → 47C543 |

   - NPC Overhaul v2、Nolvus Awakening NPC Patch、`[xPatch] … LegacyoftheDragonborn.esp` 都是 0 個。
6. 狀態與檢查：
   - `sync-order --restore-states --apply`：啟用 1 個，前置順序移動 136 個。
   - `prune_dependents` 試跑是 **26 個插件、18 個資料夾**，比預期的 8 個多：
     - 原因：第 2 步的 `create --apply` 依目標重寫 modlist，把上一輪修剪的資料夾和插件都恢復了。
     - 我逐一比對過：26 個全在第 4 階段接受的 27 個裡，**沒有新名字**；唯一不在清單上的正是這次要恢復的 `Grand Solitude - AI Overhaul patch.esp`。
     - 18 個資料夾和第 4 階段完全相同。
     - 所以照常 `--disable-folders --apply`。
   - `check_plugins` 全部通過，`verify` 缺少或未啟用 41 個＝15＋26。
   - `audit_skse` 全部通過，新的「Community Shaders：已安裝」有出現。
   - `audit_skse --dll`：`_replaced` 裡舊的 AE 版 `KnockbackPlugin.dll`（718570）和新的（718571）**都判為「多版本 NG（可用）；Address Library：SE／AE 都支援」**，見「工具缺口」第 1 點。
   - 這次沒有任何 DLL 被判為 AE 專用（class：multi 133、se 81、not_skse 1），所以沒有誤判要回報。
7. 主選單測試：見下一節。
8. BodySlide：見「BodySlide」一節。
9. Synthesis：第 1 步的檢查就有 VCLR，照手冊停下，見「需要雲端決定」第 1 點。

## 主選單（LOTD 相關 3 個插件全部啟用）
- 從 MO2 用 SKSE 啟動：**DataLoaded 176 秒**。
- 之後出現 NGIO 的草地快取提示（預期中），以 Enter 關掉；OAR 顯示「Major issue detected」的橫幅。
- **主選單有出現**（CONTINUE／NEW／LOAD），下方一樣被切掉一部分（第 7 階段處理）。
- 在主選單直接結束，沒有開新遊戲或讀檔。
- `skse64.log`：檢查 215 個、載入 214 個，沒載入的只有 `msdia140.dll`（相依函式庫，正常）。沒有 crash log。
- `BackportedESLSupport.log`：1,943 行＝1 行版本＋1,942 行「Emulated old header version for …」（16:00:31–16:00:34，1,026 個插件），沒有警告或錯誤。
- `OpenAnimationReplacer.log`（3.2.1，格式是 `[I]/[W]/[E]`）：I 1,098、W 8、E 104。
  - RaySense 外掛以 InterfaceVersion 3 取得 API，並註冊了 5 個條件：Verticality、Slope、Wall、Obstacle、WaterDepth。
  - 80 行 E：「Condition RaySense_Ledge not found in plugin Open Animation Replacer - RaySense!」。有動畫用到 `RaySense_Ledge`，但這個外掛沒有提供。
    - 目前的外掛 DLL 自報 1.0.0.0，meta 寫 1.1.0.0。
    - Nexus 最新是 1.2.0（796343，2026-08-28），可能新增了這個條件，未驗證。
  - 其他 E：
    - 10 行「Failed to parse condition in file」，加上 10 行 json 內容傾印。
    - 3 行「Failed to parse file」，包括 OAR Stance Combat Framework 的 Dual Katanas Parry Layer、OAR Stance Movement Framework 的 Dagger and Shield Non Combat Idle Start。
  - W：DAR `_CustomConditions` 的資料夾名稱不合規或缺 `_conditions.txt`（5 行）、1 行「Failed to dispatch message to MergeMapper」等。

## BodySlide（Build Morphs）
- 第一次（15:42）：使用者操作時沒勾到 Build Morphs，記錄是「TRI = False」，沒有 tri。
- 我把 BodySlide 自己資料夾裡 `BodySlide.xml` 的 `BuildMorphs` 改成 true（獨立副本，有 `.bak-*`）。這個檔也記下了 Outfit 和 Preset，所以重開後三項都已經設好。
- 從 MO2 重開：
  - 16:04 Applying preset 'CBBE Curvy (Outfit)'。
  - 16:08「TRI = True」開始。
  - 16:11「All sets processed successfully!」。
- 結果：`BodySlide (Nude)` **5,825 個 nif＋2,929 個 tri**。Overwrite 沒有 `meshes`。
- 和 Nolvus 的 `BodySlide (Nude)` 比對：
  - nif：兩邊都有的 5,450 個中，**5,428 個逐位元組相同**。幾何資料相同的 5,430 個，其餘 20 個是上一輪回報、原因未查明的 10 組。
  - tri：兩邊都有的 2,741 個中，**2,735 個逐位元組相同**，6 個不同；Nolvus 沒有的 188 個。

## 工具結果（照抄 reports\*.txt 的每一行）
```
== build_instance-create 報告 (2026-09-27 15:47)（試跑的各行相同，只有模式為「試跑」）==
[資訊] 模式：實際執行
[資訊] ModOrganizer.ini：已存在，保留（要重寫請加 --rewrite-ini）
[通過] 設定檔 Pages-ZH：modlist 4127 行（捨棄 21），plugins 4234 個（排除 12 個自製插件）
[資訊] 佔位資料夾：1 個（之後用 MO2 安裝到同名資料夾並選 Replace）
[通過] 遊戲 ini：Skyrim.ini, SkyrimPrefs.ini, SkyrimCustom.ini
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-154744
總結：[通過]

== build_instance-verify 報告 (2026-09-27 15:51)（create 後、MO2 開關後）==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[資訊] 清單外的資料夾：84 個：ZH - 官方繁中字串, Unslaad PBR, Smooth Special Idle, Maerchenwald - Archwood Lite - Giant Fantasy Trees, horseAnimations2, clockwork pbr, Creation Club: _ResourcePack, Creation Club: ccafdsse001-dwesanctuary, Creation Club: ccasvsse001-almsivi, Creation Club: ccbgssse001-fish
[注意] plugins.txt 與預期比對：缺少或未啟用 16 個（mod 尚未安裝或已被修剪）；待重建輸出 7 個；例如：Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, Anchor Animations Spell V2.esp, FH_Grapple.esp, AnchorShdSwd.esp, AI Overhaul - USSEP Patch.esp
總結：[注意]

== manifest 報告 (2026-09-27 15:51) ==
[資訊] 目標資料夾：4053 個
[資訊] 已就位：4021 個
[資訊] 需從 Nexus 下載：0 個
[資訊] 第五階段重建：9 個
[資訊] 需換成 1.5.97 版 DLL：0 個
[注意] 需整包重裝（舊內容移到 _replaced）：2 個
[資訊] 尚無來源，需人工確認：0 個
[資訊] 捨棄：21 個
[資訊] 輸出：reports\manifest.csv、reports\downloads.html
總結：[注意]

== nexus_fetch 報告 (2026-09-27 15:51) ==
[通過] 本次下載：2 個
總結：[通過]
（Open Animation Replacer4 92109/798222、Legacy of the Dragonborn - NPC Overhaul2 38178/514540）

== install_archives 報告（--only "Open Animation Replacer4"，試跑）==
[資訊] 試跑（除了還原中斷的安裝，不改動檔案）：判斷了 1 個下載
[資訊] 磁碟空間：預計解壓 48.0 MB，D:\ 剩 257.5 GB
[通過] 可自動重裝（舊資料夾移到 _replaced，不刪除）：1 個
總結：[通過]

== install_archives 報告 (2026-09-27 15:52)（--apply）==
[資訊] 執行：判斷了 1 個下載
[資訊] 磁碟空間：預計解壓 48.0 MB，D:\ 剩 257.5 GB
[通過] 已重裝（舊資料夾在 _replaced）：1 個
總結：[通過]

== audit_skse-dll 報告（新的 OpenAnimationReplacer.dll）==
[通過] OpenAnimationReplacer.dll：多版本 NG（可用）；Address Library：SE／AE 都支援
總結：[通過]

== manifest 報告 (2026-09-27 15:55)（NPC Overhaul 裝好後）==
[資訊] 目標資料夾：4053 個
[資訊] 已就位：4023 個
[資訊] 需從 Nexus 下載：0 個
[資訊] 第五階段重建：9 個
[資訊] 需換成 1.5.97 版 DLL：0 個
[資訊] 需整包重裝（舊內容移到 _replaced）：0 個
[資訊] 尚無來源，需人工確認：0 個
[資訊] 捨棄：21 個
[資訊] 輸出：reports\manifest.csv、reports\downloads.html
總結：[資訊]

== fill_plugins 報告 (2026-09-27 15:55)（試跑的前 4 行相同）==
[資訊] 模式：實際執行
[資訊] 目標插件缺少檔案：16 個（已排除第 5 階段的輸出插件）
[通過] 從 M&V／Nolvus 安裝補上（硬連結）：1 個
[注意] 找不到來源：15 個
[通過] 寫入結果：連結 1、解壓放入 0、已存在略過 0、錯誤 0
[資訊] 下一步：關 MO2 跑 build_instance.py sync-order --restore-states --apply，再 verify
總結：[注意]

== strip_refs 報告 (2026-09-27 15:56)（試跑相同，第 3 行為 [注意]「會寫到」）==
[資訊] 模式：實際執行
[資訊] 前置：LegacyoftheDragonborn.esm：自己新增的記錄 119898 筆
[通過] Modpocalypse NPCs (v3) Legacy of the Dragonborn.esp：10 筆記錄有失效引用：PKID 6、CNTO 6（COED 0）；來源：Modpocalypse NPCs - Legacy of the Dragonborn；已寫到 Pages - LOTD V6 修正
[通過] LegacyoftheDragonborn - NPC Overhaul.esp：沒有指向 LegacyoftheDragonborn.esm 已不存在記錄的引用（來源：Legacy of the Dragonborn - NPC Overhaul2）
[通過] Nolvus Awakening NPC Patch.esp：沒有指向 LegacyoftheDragonborn.esm 已不存在記錄的引用（來源：Nolvus Awakening NPC Patch）
[通過] [xPatch] Modpocalypse NPCs (v3) SSE - LegacyoftheDragonborn.esp：沒有指向 LegacyoftheDragonborn.esm 已不存在記錄的引用（來源：Modpocalypse NPCs - Patch Collection）
總結：[通過]

== build_instance-sync-order 報告 (2026-09-27 15:56)（--restore-states --apply）==
[資訊] 模式：實際執行
[通過] 啟用狀態：依目標啟用 1 個、停用 0 個；檔案不在已啟用的 mod 或遊戲資料夾裡，略過 22 個（之後要再跑 prune_dependents）
[通過] 插件順序：4521 個：依目標順序 4212，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 136 個插件到它的前置之後，例如：Natural Waterfalls - Blackreach.esp, Natural Waterfalls - Dawnguard.esp, Natural Waterfalls - Dragonborn.esp, Occ_Skyrim_Lux_Via.esp, Rainbows over Waterfalls - Bruma addon.esp, Rainbows over Waterfalls - Natural Waterfalls patch.esp, Complementary Grass Fixes - CRF Patch.esp, Additional Dremora Faces - VIGILANT Patch.esp, Skyshards - TGC Winterhold Patch.esp, FDE Aela Part 2.esp
[資訊] 不在目標清單中的插件：Lux - JK's Dragonsreach patch.esp, Lux Orbis - Reich Corigate.esp, Nolvus Awakening Darkwater Crossing Patch.esp, Northern Roads - Strongholds - Dushnikh Yal Patch.esp, DBVO Fix - Missives Wyrmstooth.esp, JKs Raven Rock - USMP patch.esp, Orc Strongholds AIO - Skyshards Patch.esp, Occ_Skyrim_Jk's-Whiterun-Outskirts_patch.esp, DBVO Fix - The Gray Cowl Returns.esp, COTN Falkreath - Book Covers Skyrim patch.esp, JKs Thieves Guild - Daedric Shrines patch.esp, Grand Solitude - Landscape override.esp, Dawn of Skyrim - AI Overhaul Patch.esp, Nolvus Awakening Mixwater Mill Patch.esp, DBM_CC_HOWTemperingEnabler.esp
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-155615
總結：[通過]

== prune_dependents 報告 (2026-09-27 15:56)（--disable-folders --apply；試跑數字相同）==
[資訊] 模式：實際執行
[注意] 要停用的插件：26 個，例如：Horsepower_Ragdoll - SC Horses Patch.esp, TSOSRefinedCreationClub.esp, Embershard.esp, Lux Orbis - Embershard patch.esp, Lux - Embershard patch.esp, Northern Roads - Alternate Perspective Patch.esp, Nolvus Awakening Armors Balance Patch.esp, Nolvus Awakening Weapons Balance Patch.esp
[資訊] 建議停用的資料夾：18 個：Leveled List Patch, Nolvus Awakening Consistency Patch, Horsepower Ragdoll - SC Horses Skeleton Patch, Nolvus Awakening AI Patch, Nolvus Awakening Economy Patch, Nolvus Awakening Combat & Enemies Patch, Nolvus Awakening Boss Integration, Nolvus Awakening Crafting Patch
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-155644
總結：[注意]

== check_plugins 報告 (2026-09-27 15:56) ==
[通過] 完整插件數（含本體）：251 / 254
[通過] 輸出重建後的完整插件（預估）：253 / 254：DynDOLOD.esm, DynDOLOD.esp 一定是完整插件；Synthesis.esp、FNIS.esp、Occlusion.esp、PG_* 必須是輕量插件
[通過] 輕量插件數（ESL）：4015 / 4096
[通過] 缺少前置的插件：0 個
[通過] 前置順序錯誤：0 個
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 916 個；BEES 已安裝；遊戲 1.5.97.0
總結：[通過]

== build_instance-verify 報告 (2026-09-27 15:56)（修剪後）==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[資訊] 清單外的資料夾：84 個：ZH - 官方繁中字串, Unslaad PBR, Smooth Special Idle, Maerchenwald - Archwood Lite - Giant Fantasy Trees, horseAnimations2, clockwork pbr, Creation Club: _ResourcePack, Creation Club: ccafdsse001-dwesanctuary, Creation Club: ccasvsse001-almsivi, Creation Club: ccbgssse001-fish
[注意] plugins.txt 與預期比對：缺少或未啟用 41 個（mod 尚未安裝或已被修剪）；待重建輸出 7 個；例如：Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, Anchor Animations Spell V2.esp, FH_Grapple.esp, AnchorShdSwd.esp, SC_HorseReplacer.esp
總結：[注意]

== audit_skse 報告 (2026-09-27 15:57) ==
[資訊] 生效的 SKSE DLL：多版本 NG（可用）=133, 非 SKSE 外掛（相依函式庫）=1, SE 版（可用）=81
[通過] 需替換的 DLL：無
[通過] STOCK GAME 遊戲版本：1.5.97.0（需要 1.5.97.0）
[通過] SKSE 1.5.97：skse64_loader.exe + skse64_1_5_97.dll
[通過] Address Library（version-1-5-97-0.bin）：已找到
[通過] 遊戲根目錄的 ENB/ReShade 殘留：無
[通過] Community Shaders：已安裝（Community Shaders）
[資訊] 含 Root 資料夾的 mod（Root Builder 會部署到遊戲資料夾）：無
總結：[通過]

== audit_skse-dll 報告 (2026-09-27 15:57)（舊的 AE 版 Knockback，在 _replaced；新的 SE 版結果相同）==
[通過] KnockbackPlugin.dll：多版本 NG（可用）；Address Library：SE／AE 都支援
總結：[通過]

== esl_check 報告 (2026-09-27 16:05)（--plugin Nolvus 的 Synthesis Patch - NOSREX\Synthesis.esp --subrecords LAND）==
[資訊] Synthesis.esp：light，HEDR 1.71，前置 55 個；記錄 15368 筆（新增 0、覆寫 15368）；覆寫類型：CELL 7664, LAND 7664, WRLD 40；ESL：已經是輕量插件
[資訊] LAND 子記錄：LAND 記錄 7664 筆；各子記錄出現在幾筆記錄：DATA 7664, VCLR 7664, VHGT 7641, VNML 7641, ATXT 7507, VTXT 7507, BTXT 7338
總結：[資訊]
```
- `[注意]` 的說明：
  - manifest 的 reinstall 2 個已處理，重跑變 0。
  - fill_plugins 找不到來源的 15 個，都是已接受缺少的。
  - prune 的 26 個全在第 4 階段接受的名單內（見步驟 6）。
  - verify 的 41 個＝15＋26。

## 需要雲端決定
1. **Synthesis：Nolvus 那份有 VCLR**，所以照 docs/05 第 3 節停下。唯讀檢查結果（腳本在 scratchpad）：
   - 7,664 筆 LAND **都有 VCLR，而且都不是全白**。最暗的位元組約 182–217，原版 Skyrim.esm 約 115–117。
   - 和 Skyrim.esm 同一筆 LAND 比對（5,811 筆）：VCLR 完全相同的 **0 筆**；平均亮度 248.6，原版 239.3；**比原版亮 4,962 筆**，暗 14 筆。
   - 也就是 Nolvus 的 Synthesis.esp 把頂點顏色**調亮**（或轉交了其他地形 mod 調亮過的值），不是移除。
   - 請決定：照 Nolvus 的結果另找對應的 patcher、仍然只用 Remove Landscape Vertex Color，或其他做法。
   - 第 10 步的草地快取、xLODGen、DynDOLOD 都會受地形影響，所以我也還沒做 PGPatcher。PGPatcher 只看網格和貼圖，理論上可以先做，要的話請指示。
2. **OAR**：還剩 80 行「RaySense_Ledge not found」。要不要把 RaySense 的 OAR 外掛換成 1.2.0（796343）？其餘 24 行是個別動畫設定檔的解析錯誤，影響很小。
3. 下一輪的順序：Synthesis 決定後，再接第 10、11 步。

## 工具／手冊缺口（建議）
1. **`audit_skse` 的 AE 判斷**：
   - 舊的 718570 和新的 718571 兩個 Knockback DLL 裡，Address Library 路徑字串完全相同，都同時有 `Data/SKSE/Plugins/version-{}.bin` 和 `versionlib-{}.bin`，所以「只有 versionlib」的規則抓不到。
   - `SKSEPlugin_Version` 區塊也相同：versionIndependence 0x1、versionIndependenceEx 0x1。
   - 差別只在編譯後的程式碼，靜態分不出來。建議這類個案繼續用 `decisions.csv` 的檔案編號處理（718570 已標記 replace_dll）。
2. **docs/05 第 2 節第 5 步**：「確認全部勾選」和 `BuildSelection.xml` 預先取消落選項的行為衝突。如果照字面全選，會跳出「Choose output set」視窗。建議改成「勾選狀態不要動，直接 Build」。
3. **Build Morphs 容易漏勾**：這次第一次重建沒勾到。
   - 建議手冊加「Batch Build 後確認 `Log_BS.txt` 有『TRI = True』」。
   - 或像這次一樣，先把 `BodySlide.xml` 的 `BuildMorphs` 設成 true。
4. **prune 的預期數量**：`create --apply` 會把上一輪的修剪全部恢復，所以接在後面的 prune 會是完整的名單（這次是 26 個），不是差額。建議 cloud-notes 的預期寫法改成「名字都在已接受的名單內」。
5. `strip_refs` 的輸出不壓縮記錄（117,725 對原檔 113,904 bytes），不影響功能。

## 本輪手動處理（只新增或搬移，沒有刪除）
- NPC Overhaul：舊內容（267 個檔）搬到 `D:\PM\_replaced\Legacy of the Dragonborn - NPC Overhaul2`，再用 MO2 安裝 v2（FOMOD Version 2）。
- OAR：舊資料夾由 `install_archives` 搬到 `_replaced`。
- `BodySlide.xml` 的 `BuildMorphs` 改成 true（有備份）。
- 主選單測試：在主選單直接結束遊戲，沒有存檔。

## 本地提交（尚未推送）
- 本回報與 status 的提交。
