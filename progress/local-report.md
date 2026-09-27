# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：5 重建輸出。照 cloud-notes f2b7958「接下來的順序」做完 1–4。**第 5 步 DynDOLOD 在 3 分鐘時被無法略過的錯誤擋下，停下回報。**
- 日期：2026-09-28
- 結論：
  - **版本不符修正完成**：
    - `strip_refs --drop-missing` 處理 59 個插件，刪掉 683 筆覆寫，連同子記錄與空群組共 800 項。每個插件的筆數都和表格相同。
    - 重跑覆寫掃描：這 59 個都變成 0，只剩原本就有的 17 個（70 筆）。0x800 以下的撞號也是 0。
  - **檢查都通過**：
    - `check_plugins` 全部 `[通過]`：完整 251／254，輕量 4018（多 1 個 `TrueHUD.esl`，說明見「工具／手冊缺口」第 1 點）。
    - 主選單：DataLoaded 166 秒，到得了主選單。
  - **DynDOLOD 停下**：
    - 載入時不再出現「being overridden」錯誤。
    - 但處理到 3 分鐘時出現 63 個「**Unresolved FormID**」錯誤，視窗只能按 Exit，**沒有產生任何輸出**。
    - 錯誤全部來自 3 個 Hall of Forgotten（HoF）補丁：`DBM_HUB_Unslaad_Patch.esp`、`DBM_HUB_SoulHunterArmor_Patch.esp`、`DBM_HUB_TwilightPrincess_Patch.esp`。
    - 這 3 個是第 4 階段依 `data/extra_archives.csv` 第 57 行從 **HoF 2.4.26** 取出的，但 `LOTD_HUB.esp` 是 Nolvus 的 **2.3.9**。
    - `--drop-missing` 只刪「覆寫」；這 3 個補丁在記錄內容裡「引用」了 2.4.26 才有的記錄，所以還在。
    - 見「需要雲端決定」第 1 點。

## 照 cloud-notes 的步驟
1. `git pull --rebase`（f2b7958）、`python -m pytest -q`：193 項全過，沒有略過。
2. **重建設定檔**：
   - `create --apply`：試跑的數字相同。佔位資料夾 1 個，就是新的 `Pages - 版本不符修正`，排在 modlist 第 2 個。
   - 開 MO2 一次再關，00:02 寫回 plugins.txt。
   - `sync-order --restore-states --apply`：啟用 0、停用 0，前置順序移動 136 個。
   - `prune_dependents` 試跑：**26 個插件、18 個資料夾，名字和上一輪完全相同**（逐一比對過）。
   - 接著 `--disable-folders --apply`。
3. **版本不符修正**：
   - 試跑列出全部 59 個，共 683 筆，沒有「找不到插件」。
   - `--apply` 後，59 個同名修正版寫到 `Pages - 版本不符修正`。
   - 每個插件的刪除筆數在 `data/analysis/strip_refs_drop_missing.csv`。最多的幾個：

     | 插件 | 刪除的記錄 | 連同子記錄／空群組 |
     |---|---|---|
     | Lux - JK's Blue Palace patch.esp | 117 | 117 |
     | Snazzy Interiors - Karthwasten Hall - The Great Town of Karthwasten Patch.esp | 93 | 93 |
     | Lux Orbis - LotD patch.esp | 88 | 150 |
     | Lux - Legacy of the Dragonborn patch.esp | 73 | 73 |
     | DBM_HUB_Unslaad_Patch.esp | 47 | 47 |
     | DBM_CCOR_Patch.esp | 38 | 38 |
     | Medieval Markets - Creation Club Fishing Patch.esp | 37 | 37 |
     | 其餘 52 個 | 1–20 | |

4. **檢查**：
   - `sync-order --apply` → `check_plugins` 全部通過 → `verify` 缺 41、待重建輸出 3（DynDOLOD.esm／.esp、Occlusion.esp）。
   - 覆寫掃描重跑：
     - 表格的 59 個全部是 0。
     - 剩下 17 個插件、70 筆（其中室外 50 筆），都是 Nolvus／M&V 原本就這樣出貨的。
     - 0x800 以下的撞號是 0。
   - **主選單測試**：
     - DataLoaded 166 秒，到得了主選單。
     - SKSE 檢查 215、載入 214；OAR E 4 行（和上次相同）。
     - BEES 1,949 行，沒有警告或錯誤；沒有新的 crash log。
5. **DynDOLOD**（docs/05 第 8 節）：
   - **`D:\MV` 改成 `D:\PM`**：`D:\PM\tools` 裡有 3 個設定檔，都是單一連結，備份是 `.bak-20260928-001002`。
     - `Bethini Pie\Bethini.ini`（2 處）：遊戲路徑改成 `D:\PM\STOCK GAME\`。INI 路徑直接替換會變成不存在的 `D:\PM\profiles\Default\`，所以指到實際使用的 `D:\PM\profiles\Pages-ZH\`。
     - `PGPatcher\cfg\ignored_messages.json`（1 處，是訊息文字裡的路徑）。
     - `DynDOLOD\Edit Scripts\DynDOLOD\Presets\DynDOLOD_SSE_Default.ini`（294 處＝OutputPath＋293 行 LODGen 規則路徑）。
     - 改完再掃，0 個。TexGen 的設定檔在上一輪按 Start 時已經自己存成 D:\PM。
   - 從 MO2 啟動（`-SSE -D:"D:\PM\STOCK GAME\Data"`），載入時沒有跳出錯誤視窗。
   - 設定（在 Advanced 畫面確認）：
     - 按 High 後記錄出現「Loading High rules」，世界空間全部勾選。
     - 勾 Object LOD、Tree LOD、Dynamic LOD、Occlusion data＋Plugin；Grass LOD 是灰的、沒有勾。
     - 輸出路徑 `D:\PM\tools\DynDOLOD\DynDOLOD_Output\`。
     - 精靈畫面的 Low／Medium／High 會直接開始產生，所以我改到 Advanced 確認選項後才按 OK。
   - **3 分 01 秒時跳出錯誤視窗**，只有「Exit DynDOLOD」可按：
     - 訊息是「Unresolved FormID [352259DF] LOTD_HUB.esp might be the wrong version for DBM_HUB_TwilightPrincess_Patch.esp」。
     - 按 Exit 後 DynDOLOD、MO2 都已關閉。`DynDOLOD_Output` 是空的，`dyndolodCS2` 也是空的。
   - 操作上的一個失誤：
     - 我想把 DynDOLOD 視窗叫到前面時，操作工具在 MO2 外又啟動了第二個 DynDOLOD。
     - 不到 1 分鐘就發現並結束它。它沒有寫入任何檔案（檢查過工具資料夾與 STOCK GAME 的修改時間）。

## DynDOLOD 記錄摘要（只算這次的工作階段）
- **錯誤 67 個**：
  - **Unresolved FormID 63 個**，全部指向 `LOTD_HUB.esp` 裡不存在的 4 筆記錄：1DB739、231CFB、231CFC、231CFD。這 4 筆在 HoF 2.4.26 裡都是 SNDR（音效描述）。
    - 各補丁的錯誤數：

      | 補丁 | 錯誤數 |
      |---|---|
      | DBM_HUB_Unslaad_Patch.esp | 55 |
      | DBM_HUB_SoulHunterArmor_Patch.esp | 5 |
      | DBM_HUB_TwilightPrincess_Patch.esp | 3 |

    - 出錯的都是展示用 ACTI，例如 `hub_hof_DISP_zzzCrb…`。
  - **File not found（script）3 個**：
    - `hub_hof_armorytoysact.pex`：TwilightPrincess 補丁用到，是 HoF 2.4 才有的檔案。
    - `ffibbarrierscript.pex`：icebladeofthemonarch.esp。
    - `wzobadisableactivatetest.pex`：WZOblivionArtifacts.esp。
    - 後兩個屬於 Nolvus 那邊的 mod，M&V 自己的 DynDOLOD 記錄沒有。
  - **Path not allowed 1 個**：輸出路徑的固定訊息，TexGen 也有，沒有影響。
- **警告 139 個**：
  - File not found 76 個：大多是 Beyond Skyrim 的資源，bscyrodiil 41、bstamriel 12、bsmorrowind 8。
  - 其他：檔名不合慣例 36、Textures do not match 11、非主插件的大型參照 7、LOD model 4、extended FormID range 3、File not loaded 1、Billboard 1。
- 對照 M&V 自己的 DynDOLOD 記錄：錯誤 112、警告 378。它們的清單不同，這次的錯誤種類裡只有 Unresolved FormID 會擋住產生。

## 需要雲端決定
1. **3 個 HoF 補丁（加上依賴它們的 3 個 TCC 插件）怎麼處理**：
   - 依賴關係：
     - `LOTD_TCC_Unslaad.esp`、`LOTD_TCC_Twilight Princess Armor.esp`、`LOTD_TCC_Soul Hunter Armor.esp` 以這 3 個補丁為前置。
     - 這 3 個 TCC 插件同樣是依 extra_archives 第 58 行，從 TCC 4.9 取出的；Nolvus 是 4.3。
   - 我比對了 HoF 兩個版本（2.4.26 壓縮檔已在 downloads，只把插件解到 scratchpad 看）：
     - `LOTD_HUB.esp`：2.3.9 有 27,465 筆，2.4.26 有 42,067 筆、HEDR 1.71，新增前置 `_ResourcePack.esl`。
     - **2.3.9 的記錄有 5,063 筆在 2.4.26 裡不存在**，另有 4 筆類型不同、26 筆 EDID 不同。**所以不是單純的延伸版。**
     - `LOTD_HUB_ST.esp`、`LOTD_HUB_FINH.esp` 在 2.4.26 改成 1.71，編號全部重排。
     - Nolvus 裝的 17 個 DBM_HUB 補丁，2.4.26 都有內容不同的版本。那 3 個新補丁和 2.4.26 壓縮檔裡的完全相同。
     - 啟用中的插件有 39 個以 HoF 插件為前置：
       - HoF 自己 17 個、TCC 16 個。
       - `Pages - 版本不符修正` 裡 4 個。
       - `Nolvus Awakening DLC Patch.esp`、`PG_1.esp`。
   - 可能的做法：
     - **(A) 整包升級到 HoF 2.4.26＋TCC 4.9**：
       - 比較接近目標清單原作者的版本（目標有這 3 個補丁）。
       - 要做的事：
         - 用 FOMOD 重裝 HoF，選項對應目標的 17 個 DBM_HUB 補丁。
         - 升級 TCC。
         - 檢查 Nolvus Awakening DLC Patch 能不能用。
         - 重做覆寫掃描與 `strip_refs`，舊的修正版要移走。
         - 重跑 PGPatcher（`PG_1.esp` 以 HoF 為前置）。
     - **(B) 停用這 6 個插件**（3 個 DBM_HUB 補丁＋3 個 TCC）：
       - 都是輕量插件，不影響完整插件名額。
       - 結果是 HoF 不展示這 3 套盔甲，和 Nolvus 原本的設定相同（Nolvus 的 2.3.9 沒有這 3 個補丁）。
       - `Pages - 版本不符修正` 裡的 3 個修正版會跟著不生效。
   - 我建議先用 (B) 做完第 5 階段，(A) 留到第 8 階段再評估。
2. **Ice Blade of the Monarch、Oblivion Artifacts 缺 script**：DynDOLOD 只記為錯誤，沒有停下。要不要處理？
3. **extra_archives 的其他項目**：
   - 第 57、58 行的備註寫「Nolvus 的 2.3.9／4.3 沒有」，也就是從比已安裝的主插件更新的壓縮檔補插件。
   - 這種項目的「引用」問題，`--drop-missing` 處理不到。
   - 這次 DynDOLOD 只抓到這 3 個，但它只檢查它處理的記錄類型。如果需要，我可以對 extra_archives 補進來的所有插件，用 xEdit 的 Check for Errors 做完整檢查。

## 工具／手冊缺口（建議）
1. **`TrueHUD.esl` 會留在停用**：
   - 草地快取前停用 True HUD，之後重新啟用資料夾時，MO2 會把 `TrueHUD.esl` 加回成停用，一般的 `sync-order` 不會恢復它。
   - 上一輪的輕量數 4017 其實少了它；這次 `create --apply` 照目標恢復，所以是 4018。
   - 建議：docs/05 第 5.3 節第 6 步後加 `sync-order --restore-states --apply`，或讓 sync-order 恢復目標中已啟用、但被 MO2 停用的插件。
2. **DynDOLOD 精靈模式**：Low／Medium／High 按下就直接開始。docs/05 第 8 節可以註明「先按 Advanced 確認選項，再按 High 和 OK」。
3. **引用的檢查**：`strip_refs --drop-missing` 只看記錄本身的 FormID。DynDOLOD 會把「引用不存在的記錄」當成致命錯誤，建議在 DynDOLOD 之前先對版本不同的插件做引用檢查。

## 輸出資料夾的檔案數（和上一輪相同，只有 DynDOLOD 還沒有輸出）
| 資料夾 | 檔案數 |
|---|---|
| `SYNTHESSIS` | 1 |
| `pgpatcher_output` | 20,432 |
| `grass CS` | 15,340 |
| `lodgen2` | 48,852 |
| `texgenCS` | 5,292 |
| `dyndolodCS2` | 0 |
| `Pages - 版本不符修正`（新） | 59 |

## 工具結果（照抄 reports\*.txt 的每一行）
```
== build_instance-create 報告 (2026-09-27 23:58)（試跑的各行相同）==
[資訊] 模式：實際執行
[資訊] ModOrganizer.ini：已存在，保留（要重寫請加 --rewrite-ini）
[通過] 設定檔 Pages-ZH：modlist 4128 行（捨棄 21），plugins 4233 個（排除 12 個自製插件）
[資訊] 佔位資料夾：1 個（之後用 MO2 安裝到同名資料夾並選 Replace）
[通過] 遊戲 ini：Skyrim.ini, SkyrimPrefs.ini, SkyrimCustom.ini
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-235832
總結：[通過]

== build_instance-sync-order 報告 (2026-09-28 00:02)（--restore-states --apply；試跑相同）==
[資訊] 模式：實際執行
[通過] 啟用狀態：依目標啟用 0 個、停用 0 個；檔案不在已啟用的 mod 或遊戲資料夾裡，略過 18 個（之後要再跑 prune_dependents）
[通過] 插件順序：4524 個：依目標順序 4215，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 136 個插件到它的前置之後，例如：Natural Waterfalls - Blackreach.esp, Natural Waterfalls - Dawnguard.esp, Natural Waterfalls - Dragonborn.esp, Occ_Skyrim_Lux_Via.esp, Rainbows over Waterfalls - Bruma addon.esp, Rainbows over Waterfalls - Natural Waterfalls patch.esp, Complementary Grass Fixes - CRF Patch.esp, Additional Dremora Faces - VIGILANT Patch.esp, Skyshards - TGC Winterhold Patch.esp, FDE Aela Part 2.esp
[資訊] 不在目標清單中的插件：JK's Whiterun Outskirts Grass Fix.esp, Lux Orbis - Ryn's Lover Stone patch.esp, COTN Dawnstar - SK Unique Signs Patch.esp, Lux - The Great City of Winterhold V4 patch.esp, DBM_RuinsClutterImproved_Patch.esp, Lux Orbis - Ryn's Lord Stone patch.esp, DBVO Fix - Farming.esp, JKs Winking Skeever - Thieves Guild Requirements Patch.esp, JKs Thieves Guild - Daedric Shrines patch.esp, Gourmet - Auri.esp, DBVO Fix - Missives - Midwood Isle.esp, Lux Orbis - Ryn's Shadow Stone patch.esp, DBM_JKSkyrim_Patch.esp, Snazzy Interiors - Karthwasten Hall - AI Overhaul pat…
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-000235
總結：[通過]

== prune_dependents 報告 (2026-09-28 00:02)（--disable-folders --apply；試跑數字與名字相同）==
[資訊] 模式：實際執行
[注意] 要停用的插件：26 個，例如：Horsepower_Ragdoll - SC Horses Patch.esp, TSOSRefinedCreationClub.esp, Embershard.esp, Lux Orbis - Embershard patch.esp, Lux - Embershard patch.esp, Northern Roads - Alternate Perspective Patch.esp, Nolvus Awakening Armors Balance Patch.esp, Nolvus Awakening Weapons Balance Patch.esp
[資訊] 建議停用的資料夾：18 個：Leveled List Patch, Nolvus Awakening Consistency Patch, Horsepower Ragdoll - SC Horses Skeleton Patch, Nolvus Awakening AI Patch, Nolvus Awakening Economy Patch, Nolvus Awakening Combat & Enemies Patch, Nolvus Awakening Boss Integration, Nolvus Awakening Crafting Patch
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-000258
總結：[注意]

== strip_refs 報告 (2026-09-28 00:03)（--drop-missing --from-csv …；試跑的 59 行相同，狀態為 [注意]「會寫到」）==
[資訊] 模式：刪除覆寫不存在記錄的整筆記錄；實際執行
[通過] <59 行，每行一個插件>：刪除 N 筆覆寫不存在記錄的記錄（連同子記錄與空群組共 M 項）；來源：…；已寫到 Pages - 版本不符修正
       （59 行的 N、M 見 data/analysis/strip_refs_drop_missing.csv；N 合計 683、M 合計 800）
總結：[通過]

== build_instance-sync-order 報告 (2026-09-28 00:03)（--apply）==
[資訊] 模式：實際執行
[通過] 插件順序：4498 個：依目標順序 4189，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 133 個插件到它的前置之後，例如：Natural Waterfalls - Blackreach.esp, Natural Waterfalls - Dawnguard.esp, Natural Waterfalls - Dragonborn.esp, Occ_Skyrim_Lux_Via.esp, Rainbows over Waterfalls - Bruma addon.esp, Rainb…
[資訊] 不在目標清單中的插件：（同上一份）
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-000339
總結：[通過]

== check_plugins 報告 (2026-09-28 00:03) ==
[通過] 完整插件數（含本體）：251 / 254
[通過] 輸出重建後的完整插件（預估）：253 / 254：DynDOLOD.esm, DynDOLOD.esp 一定是完整插件；Synthesis.esp、FNIS.esp、Occlusion.esp、PG_* 必須是輕量插件
[通過] 輕量插件數（ESL）：4018 / 4096
[通過] 缺少前置的插件：0 個
[通過] 前置順序錯誤：0 個
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 919 個；BEES 已安裝；遊戲 1.5.97.0
總結：[通過]

== build_instance-verify 報告 (2026-09-28 00:03) ==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[資訊] 清單外的資料夾：84 個：ZH - 官方繁中字串, Unslaad PBR, Smooth Special Idle, Maerchenwald - Archwood Lite - Giant Fantasy Trees, horseAnimations2, clockwork pbr, Creation Club: _ResourcePack, Creation Club: ccafdsse001-dwesanctuary, Creation Club: ccasvsse001-almsivi, Creation Club: ccbgssse001-fish
[注意] plugins.txt 與預期比對：缺少或未啟用 41 個（mod 尚未安裝或已被修剪）；待重建輸出 3 個；例如：Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, Anchor Animations Spell V2.esp, FH_Grapple.esp, AnchorShdSwd.esp, SC_HorseReplacer.esp
總結：[注意]
```
- `[注意]` 的說明：
  - prune 的 26 個和上一輪名字相同。
  - verify 的 41 個＝15＋26；待重建輸出 3 個是 DynDOLOD.esm、DynDOLOD.esp、Occlusion.esp。
- `audit_skse` 還沒跑，它在 DynDOLOD 之後。

## 本輪手動處理（只修改設定或新增，沒有刪除）
- 3 個工具設定檔的 `D:\MV` 改成 `D:\PM`，都有備份。
- 誤開的第二個 DynDOLOD 被強制結束。它還在啟動中，沒有寫入任何檔案。
- 主選單測試後直接結束遊戲，沒有存檔。

## 本地提交（尚未推送）
- 本回報、status、`data/analysis/strip_refs_drop_missing.csv`（插件名稱與數字，沒有個資）。
