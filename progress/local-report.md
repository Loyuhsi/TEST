# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：4 組合清單（**完成回報**：照 cloud-notes 27208e6 的步驟 1–11）
- 日期：2026-09-27
- 結論：
  - `check_plugins` **全部通過**：缺少前置 0、前置順序錯誤 0、完整插件 252／254、輕量 4011／4096。`audit_skse` 通過。
  - `_ResourcePack.esl／.bsa` 已用 M&V 版硬連結放進 `STOCK GAME\Data`。
  - Frescoes 已改成 Complete (No Lanterns) ESL，Grand Solitude 補丁也換成對應版本。
  - `sync-order` 移動了 **136 個**插件到它們的前置之後。
  - `prune_dependents`：停用 27 個插件、18 個資料夾。27 個 < 60，沒有 ESM，也沒有 LOTD、Grand Solitude 本體。
  - `verify`：缺少 43 個（原本 16 個＋修剪的 27 個），待重建輸出 7 個。
  - **只剩 1 項沒照指示完成：Dibella 的 Frescoes 補丁**。Mara 的三種原始檔都對不上 Nolvus 那份，依指示停下來回報，見「需要雲端決定」。

## 照 cloud-notes 的步驟
1. `git pull --rebase`、`python -m pytest -q`：161 項通過、1 項略過。
2. `_ResourcePack`：
   - `docs/04` 7.1 的 `cmd //c mklink /H "…" "…"` 在 Git Bash 執行失敗，cmd 回「參數無效」，沒有建立任何檔案（引號被 Git Bash 轉換）。
   - 改用 Python `os.link` 建立同樣的硬連結：
     - esl 78,418 bytes、bsa 916,509,890 bytes，大小符合。
     - 兩個檔都是 nlink 2，與 `D:\MV\mods\Creation Club` 的是同一個檔。
   - 建議把文件改成 PowerShell 的 `New-Item -ItemType HardLink`，或 Python 的寫法。
3. `build_instance create --apply` → 開 MO2 一次再關（10:51 寫回 plugins.txt）。
4. `manifest`：和預期相同。
   - Frescoes 是 reinstall（110913）。
   - Vanaheimr、Riverwood Falls 是 keep（「已重裝成指定的檔案」）。
   - download 0、replace_dll 0。
5. 下載與重裝：
   - `nexus_fetch` 下載 110913。
   - `install_archives --only "Solitude and Temple Frescoes 2019"` 試跑 → `--apply`：
     - 舊的 Solitude Only 內容搬到 `_replaced`，新版 85 個檔。
     - `SolitudeTempleFrescoes.esp` 102,436 bytes、有 ESL 旗標。
   - 重跑 `manifest`：那一列變成 keep，reinstall 0。
6. `fill_plugins` 試跑 → `--apply`：取出 `Grand Solitude - Solitude and Temple Frescoes Complete ESL No Lanterns patch.esp`，其他 16 個找不到來源。
7. Dibella：沒有放入，原因見下。
8. `sync-order --restore-states --apply` → `verify` → `audit_skse` → `check_plugins`：
   - verify 缺 16 個。雲端預期 15 個，多的是 Dibella。
   - check_plugins：前置順序 0、缺前置 24 個，沒有 `_ResourcePack`。
9. `prune_dependents` 試跑：27 個，沒有觸發任何停止條件。
10. `prune_dependents --disable-folders --apply` → `check_plugins` 全部通過 → `verify` 缺 43 個（16＋27）。

## 工具結果（照抄 reports\*.txt 的每一行）
```
== build_instance-create 報告 (2026-09-27 10:50) ==
[資訊] 模式：實際執行
[資訊] ModOrganizer.ini：已存在，保留（要重寫請加 --rewrite-ini）
[通過] 設定檔 Pages-ZH：modlist 4121 行（捨棄 21），plugins 4233 個（排除 12 個自製插件）
[資訊] 佔位資料夾：0 個（之後用 MO2 安裝到同名資料夾並選 Replace）
[通過] 遊戲 ini：Skyrim.ini, SkyrimPrefs.ini, SkyrimCustom.ini
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-105008
總結：[通過]

== manifest 報告 (2026-09-27 10:51) ==
[資訊] 目標資料夾：4047 個
[資訊] 已就位：4016 個
[資訊] 需從 Nexus 下載：0 個
[資訊] 第五階段重建：9 個
[資訊] 需換成 1.5.97 版 DLL：0 個
[注意] 需整包重裝（舊內容移到 _replaced）：1 個
[資訊] 尚無來源，需人工確認：0 個
[資訊] 捨棄：21 個
[資訊] 輸出：reports\manifest.csv、reports\downloads.html
總結：[注意]

== nexus_fetch 報告 (2026-09-27 10:51) ==
[通過] 本次下載：1 個
總結：[通過]
（nexus_fetch.csv：Solitude and Temple Frescoes 2019 29695/110913 downloaded）

== install_archives 報告 (2026-09-27 10:52)（--only "Solitude and Temple Frescoes 2019" --apply；試跑時為「可自動重裝 1 個」）==
[資訊] 執行：判斷了 1 個下載
[資訊] 磁碟空間：預計解壓 17.6 MB，D:\ 剩 266.8 GB
[通過] 已重裝（舊資料夾在 _replaced）：1 個
總結：[通過]

== manifest 報告（重裝後重跑）==
[資訊] 目標資料夾：4047 個
[資訊] 已就位：4017 個
[資訊] 需從 Nexus 下載：0 個
[資訊] 第五階段重建：9 個
[資訊] 需換成 1.5.97 版 DLL：0 個
[資訊] 需整包重裝（舊內容移到 _replaced）：0 個
[資訊] 尚無來源，需人工確認：0 個
[資訊] 捨棄：21 個
[資訊] 輸出：reports\manifest.csv、reports\downloads.html

== fill_plugins 報告 (2026-09-27 10:52)（--apply）==
[資訊] 模式：實際執行
[資訊] 目標插件缺少檔案：17 個（已排除第 5 階段的輸出插件）
[通過] 從壓縮檔取出：1 個
[注意] 找不到來源：16 個
[通過] 寫入結果：連結 0、解壓放入 1、已存在略過 0、錯誤 0
[資訊] 下一步：關 MO2 跑 build_instance.py sync-order --restore-states --apply，再 verify
總結：[注意]

== build_instance-sync-order 報告 (2026-09-27 10:53)（--restore-states --apply）==
[資訊] 模式：實際執行
[通過] 啟用狀態：依目標啟用 1 個、停用 0 個；檔案不在已啟用的 mod 或遊戲資料夾裡，略過 23 個（之後要再跑 prune_dependents）
[通過] 插件順序：4519 個：依目標順序 4210，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 136 個插件到它的前置之後，例如：Natural Waterfalls - Blackreach.esp, Natural Waterfalls - Dawnguard.esp, Natural Waterfalls - Dragonborn.esp, Occ_Skyrim_Lux_Via.esp, Rainbows over Waterfalls - Bruma addon.esp, Rainbows over Waterfalls - Natural Waterfalls patch.esp, Complementary Grass Fixes - CRF Patch.esp, Additional Dremora Faces - VIGILANT Patch.esp, Skyshards - TGC Winterhold Patch.esp, FDE Aela Part 2.esp
[資訊] 不在目標清單中的插件：JKs College of Winterhold - 4thUnknowns Scamps patch.esp, Nolvus Awakening Follower Patch.esp, JKs Solitude Outskirts - Mihail Haystacks patch.esp, DBVO Fix - AYOP Dawnguard.esp, Lux - JK's Eek Bannered Mare patch.esp, Lux Orbis - JK's Riverfall Cottage patch.esp, JK's Temple of the Divines.esp, DBVO Fix - The Gray Cowl Returns.esp, Gorgeous Giant Camps Compilation - Mihail Giant Club Variety patch.esp, Lux - Granite Hill.esp, JKs Dark Brotherhood Sanctuary - Destroy the Dark Brotherhood Quest Expasnion patch.esp, COTN Falkreath - TGR Patch.esp, TGC Winterhold - Mihail House Cats patch.esp, Nature of the Wild Lands - Wizkid Hunters Camp Overhaul.esp, DBVO Fix - Dawnguard DLC.esp
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-105320
總結：[通過]
（沒有出現「ESM 插件以一般插件為前置」或「循環」的注意）

== build_instance-verify 報告 (2026-09-27 10:53)（修剪前）==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[注意] plugins.txt 與預期比對：缺少 16 個（mod 尚未安裝或已被修剪）；待重建輸出 7 個；例如：Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, Anchor Animations Spell V2.esp, FH_Grapple.esp, AnchorShdSwd.esp, SC_HorseReplacer.esp
總結：[注意]

== audit_skse 報告 (2026-09-27 10:53) ==
[資訊] 生效的 SKSE DLL：多版本 NG（可用）=132, 非 SKSE 外掛（相依函式庫）=1, SE 版（可用）=81
[通過] 需替換的 DLL：無
[通過] STOCK GAME 遊戲版本：1.5.97.0（需要 1.5.97.0）
[通過] SKSE 1.5.97：skse64_loader.exe + skse64_1_5_97.dll
[通過] Address Library（version-1-5-97-0.bin）：已找到
[通過] 遊戲根目錄的 ENB/ReShade 殘留：無（Community Shaders 可正常運作）
[資訊] 含 Root 資料夾的 mod（Root Builder 會部署到遊戲資料夾）：無
總結：[通過]

== check_plugins 報告 (2026-09-27 10:53)（修剪前）==
[通過] 完整插件數（含本體）：252 / 254
[通過] 輕量插件數（ESL）：4038 / 4096
[失敗] 缺少前置的插件：24 個（見 reports\check_plugins.csv）
[通過] 前置順序錯誤：0 個
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 923 個；BEES 已安裝；遊戲 1.5.97.0
總結：[失敗]

== prune_dependents 報告 (2026-09-27 10:53)（--disable-folders --apply；之前的試跑數字相同）==
[資訊] 模式：實際執行
[注意] 要停用的插件：27 個，例如：Horsepower_Ragdoll - SC Horses Patch.esp, TSOSRefinedCreationClub.esp, Embershard.esp, Grand Solitude - AI Overhaul patch.esp, Lux Orbis - Embershard patch.esp, Lux - Embershard patch.esp, Northern Roads - Alternate Perspective Patch.esp, Nolvus Awakening Armors Balance Patch.esp
[資訊] 建議停用的資料夾：18 個：Leveled List Patch, Nolvus Awakening Consistency Patch, Horsepower Ragdoll - SC Horses Skeleton Patch, Nolvus Awakening AI Patch, Nolvus Awakening Economy Patch, Nolvus Awakening Combat & Enemies Patch, Nolvus Awakening Boss Integration, Nolvus Awakening Crafting Patch
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-105357
總結：[注意]

== check_plugins 報告 (2026-09-27 10:54)（修剪後）==
[通過] 完整插件數（含本體）：252 / 254
[通過] 輕量插件數（ESL）：4011 / 4096
[通過] 缺少前置的插件：0 個
[通過] 前置順序錯誤：0 個
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 913 個；BEES 已安裝；遊戲 1.5.97.0
總結：[通過]

== build_instance-verify 報告 (2026-09-27 10:54)（修剪後）==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[注意] plugins.txt 與預期比對：缺少 43 個（mod 尚未安裝或已被修剪）；待重建輸出 7 個；例如：Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, Anchor Animations Spell V2.esp, FH_Grapple.esp, AnchorShdSwd.esp, SC_HorseReplacer.esp
總結：[注意]
```

## prune 停用的 27 個插件（`prune-plan.csv` 的 remove 列）
全部是輕量插件（ESL 旗標），沒有任何 `.esm` 或 ESM 旗標。

| 插件 | 資料夾 | 原因 |
|---|---|---|
| Horsepower_Ragdoll - SC Horses Patch.esp | Horsepower Ragdoll - SC Horses Skeleton Patch | 前置 SC_HorseReplacer.esp 不存在 |
| TSOSRefinedCreationClub.esp | True Sons of Skyrim Refined | 前置 RedguarddiasporaRefinedSeries.esp 不存在 |
| Embershard.esp | Embershard | 前置 SnozzResources.esp 不存在 |
| Lux Orbis - Embershard patch.esp | Lux Orbis - Patch Hub2 | 前置 Embershard.esp 已被移除 |
| Lux - Embershard patch.esp | Lux - Patch Hub3 | 前置 Embershard.esp 已被移除 |
| Grand Solitude - AI Overhaul patch.esp | Grand Solitude Patch Collection | 前置 AI Overhaul - USSEP Patch.esp 不存在 |
| Northern Roads - Alternate Perspective Patch.esp | Northern Roads Patch Compendium | 前置 Nolvus Northern Roads Patch.esp 不存在 |
| Nolvus Awakening Alternate Start.esp | Nolvus Awaknening Alternate Start | 前置 Nolvus Northern Roads Patch.esp 不存在 |
| Nolvus Awakening Weapons Balance Patch.esp | Nolvus Awakening Weapons Balance Patch | 前置 NewArmoury.esp 不存在 |
| Nolvus Awakening Leveled Weapons Patch.esp | Nolvus Awakening Leveled Weapons Patch | 前置 NewArmoury.esp 不存在 |
| Nolvus Awakening Weapons Patch.esp | Nolvus Awakening Weapons Patch | 前置 NewArmoury.esp 不存在 |
| Nolvus Awakening Perk Patch.esp | Nolvus Awakening Perk Patch | 前置 NewArmoury.esp 不存在 |
| Nolvus Awakening Economy Patch.esp | Nolvus Awakening Economy Patch | 前置 NewArmoury.esp 不存在 |
| Nolvus Awakening Combat Scaling Overhaul - Consistency Patch.esp | Nolvus Awakening Combat Scaling Overhaul - Moderate | 前置 NewArmoury.esp 不存在 |
| Leveled List Patch.esp | Leveled List Patch | 前置 NewArmoury.esp 不存在 |
| Nolvus Awakening Armors Balance Patch.esp | Nolvus Awakening Armors Balance Patch | 前置 Eli_Sicarius' Refuge.esp 不存在 |
| Nolvus Awakening Clothes Patch.esp | Nolvus Awakening Clothes Patch | 前置 This Is Jorrvaskr.esp 不存在 |
| Nolvus Awakening Crafting Patch.esp | Nolvus Awakening Crafting Patch | 前置 BOOBIES_potions.esp 不存在 |
| Nolvus Awakening Combat & Enemies Patch.esp | Nolvus Awakening Combat & Enemies Patch | 前置 ClefJ's Dragon Bridge.esp 不存在 |
| Nolvus Awakening Boss Integration.esp | Nolvus Awakening Boss Integration | 前置 ClefJ's Dragon Bridge.esp 不存在 |
| Nolvus Awakening Combat Scaling Overhaul - Boss.esp | Nolvus Awakening Combat Scaling Overhaul - Moderate | 前置 Nolvus Awakening Boss Integration.esp 已被移除 |
| Nolvus Awakening AI Patch.esp | Nolvus Awakening AI Patch | 前置 EpicSolitude.esp 不存在 |
| Nolvus Awakening TSOS Patch.esp | True Sons of Skyrim Refined - Nolvus Patch | 前置 EpicSolitude.esp 不存在 |
| Nolvus Awakening Consistency Patch.esp | Nolvus Awakening Consistency Patch | 前置 AnotherOakwood.esp 不存在 |
| Nolvus Awakening Combat Scaling Overhaul - Enemy Level Mult.esp | Nolvus Awakening Combat Scaling Overhaul - Moderate | 前置 Populated Dungeons Caves Ruins Reborn.esp 不存在 |
| full_inu ArmorPack01 SPID.esp | full_inu Armor Pack 01 SPID Distribution | 前置 [full_inu] Armor Pack 01.esp 不存在 |
| Orc Exiles - Bilegulch - Ryn's Lost Valley Redoubt patch.esp | Orc Exiles - Bilegulch - Patch Collection | 前置 Orc Exiles - Bilegulch Fixes.esp 不存在 |

- 注意：
  - `Embershard.esp` 是 Embershard 本體（地點改造），不是補丁。因為它停用，Lux 與 Lux Orbis 的 Embershard 補丁也跟著停用。
  - 「Nolvus Awakening Combat Scaling Overhaul - Moderate」停用了 3 個插件，但 Core、Nerf PowerAttacks、Encounter Zone 仍啟用，所以資料夾保持啟用。

## 已停用的資料夾（`--disable-folders`，18 個；modlist 中都已是 `-`）
Leveled List Patch、Nolvus Awakening Consistency Patch、Horsepower Ragdoll - SC Horses Skeleton Patch、Nolvus Awakening AI Patch、Nolvus Awakening Economy Patch、Nolvus Awakening Combat & Enemies Patch、Nolvus Awakening Boss Integration、Nolvus Awakening Crafting Patch、Nolvus Awakening Perk Patch、Nolvus Awakening Weapons Patch、Nolvus Awakening Leveled Weapons Patch、Nolvus Awakening Weapons Balance Patch、Nolvus Awakening Clothes Patch、full_inu Armor Pack 01 SPID Distribution、Nolvus Awakening Armors Balance Patch、True Sons of Skyrim Refined - Nolvus Patch、Embershard、Nolvus Awaknening Alternate Start。

## sync-order 移動的插件
- 共 **136 個**。完整清單在 `reports\build_instance-sync-order.json` 的 `moved`。
- 例子：Natural Waterfalls 的 3 個補丁、Rainbows over Waterfalls 的 2 個、COTN Dawnstar Snazzy AIO 的補丁群、JK's Jorrvaskr 補丁群。
- 沒有「ESM 以一般插件為前置」或「循環」的注意。

## 需要雲端決定
1. **Dibella 的 Frescoes 補丁（唯一沒完成的指示）**
   - 比對結果：706051 的 Temple of Mara 三種原始檔都對不上。
     - ESL、ESP、ESL No Lanterns 都是 920 bytes，雜湊各不相同。
     - 已安裝的 Nolvus 版是 1,061 bytes，前置多了 Update／Dawnguard／HearthFires／Dragonborn，是較舊版本的 JK 補丁。
     - 依指示沒有放入。
   - 佐證：解析 ModuleConfig.xml，Temple of Dibella 的 Frescoes 群組各選項對應的原始檔如下。
     - Complete - ESP、Complete (No Lanterns) - ESP、SSE → `…ESP patch.esp`
     - Complete - ESL → `…ESL patch.esp`
     - **Complete (No Lanterns) - ESL → `…ESL No Lanterns patch.esp`**
     - Solitude Only 四種 → 不裝任何插件
   - 建議：我們現在的 Frescoes 就是 Complete (No Lanterns) ESL，所以取 `JKs Temple of Dibella - Solitude and Temple Frescoes ESL No Lanterns patch.esp`（2,323 bytes），改名成目標名稱，放進 `JK's Interiors Patch Collection`（Mara 補丁所在的資料夾）。同意的話下一輪開頭就做。
2. 第 4 階段是否算完成？verify 的 43 個缺少＝15 個捨棄或接受缺少、Dibella 1 個、修剪 27 個。
3. 請給第 5 階段的 BodySlide 預設與 Synthesis 清單。

## 本輪手動處理（只新增或搬移，沒有刪除）
- `_ResourcePack.esl／.bsa` 用 Python `os.link` 建立硬連結（`docs/04` 的 mklink 指令在 Git Bash 失敗）。
- 舊的 `Grand Solitude - Solitude and Temple Frescoes Solitude ESP No Lanterns patch.esp` 照指示留在 Grand Solitude Patch Collection（非目標插件，停用）。

## 本地提交（尚未推送）
- 本回報與 status 的提交。
