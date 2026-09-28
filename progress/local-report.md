# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：5 重建輸出。照 cloud-notes 3f81324「接下來的順序」做完 1–6，**第 7 步回報**。第 8 步第 11 節測試路線，接著請使用者玩。
- 日期：2026-09-28
- 結論：
  - **`Madmen - Simonrim.esp` 已停用**：
    - prune 仍是已接受的 26 個，沒有插件以它為前置。
    - 它是輕量插件，所以完整插件仍是 **253**，輕量 4013 → 4012。
    - 6 個輸出插件的前置都沒有它。
  - **NITHI Reach 的 AI Overhaul 補丁**：`forward_appearance` 寫出修正版。
    - 49 筆 NPC 的外觀改用我們裝的 NITHI，另有 8 筆已經一致，沒有 `[注意]`。
  - **xEdit**：新的修正版和 Nolvus 帶來的另外 4 個 NITHI AI Overhaul 補丁，**全部 0 錯誤**。
  - **Lastendell**：Nolvus 用的是現成的 DynDOLOD 輸出，**沒有記錄**。它的輸出在 Lastendell 有 47 個 LOD 檔，我們有 52 個。
  - 主選單 176 秒，沒有當機。

## 照 cloud-notes 的步驟
1. `git pull --rebase`（3f81324）、`python -m pytest -q`：207 項全過。
2. **停用 Madmen - Simonrim**：
   - `create --apply`：試跑相同，佔位資料夾 0；plugins.txt 裡 `Madmen - Simonrim.esp` 是停用。
   - 開 MO2 一次再關，10:30 寫回。
   - `sync-order --restore-states --apply`：啟用 0、停用 0，它仍是停用。
   - `prune_dependents` 試跑：**26 個插件、18 個資料夾，名字和已接受的 26 個完全相同**，沒有「前置是 Madmen - Simonrim.esp」的新名字。接著 `--disable-folders --apply`。
   - `check_plugins` 全部通過：**完整 253／254**（它原本是輕量插件，所以不變）、輕量 4012。
   - `reports\check_plugins.csv` 裡 PGPatcher.esp、PG_1.esp、Synthesis.esp、DynDOLOD.esm、DynDOLOD.esp、Occlusion.esp 的前置，**都沒有 `Madmen - Simonrim.esp`**。
3. **NITHI Reach 補丁**：
   - 我們裝的 `NITHI NPCS - The Reach - Women.esp`：
     - **38,136 bytes（約 38.1 KB）→ 對應 RSV 變體**。
     - 在 `Nithi NPC Enhancement - The Reach`，是從 Nolvus 硬連結來的，meta 版本 0.1。
     - 同資料夾的 Men.esp 是 50,927 bytes。
     - AI Overhaul 補丁 36,604 bytes，是 fill_plugins 取出的。
   - `forward_appearance` 試跑與 `--apply` 的結果相同：
     - 外觀來源：Women.esp 有 NPC 28 筆，Men.esp 有 58 筆。
     - **49 筆 NPC 的外觀改用來源的值**，各欄位：NAM9 11、PNAM 11、QNAM 32、RNAM 1、WNAM 20。**已一致 8 筆**。
     - 49 筆裡 29 筆來自 Men.esp、20 筆來自 Women.esp。
   - `reports\forward_appearance.csv`：49 列，**沒有任何一列有 note**：沒有無法換算的欄位，也沒有其他指向 NITHI 且不一致的引用。
   - 報告裡沒有「前置不同沒有更動」。
   - 修正版寫到 `Pages - 版本不符修正`（64,734 bytes）→ `sync-order --apply` → `check_plugins` 全部通過（完整 253、輕量 4012）。現在生效的是修正版。
4. **xEdit 唯讀檢查**：
   - 用上次的方法：SSEEdit 暫時加 `-D:`／`-P:`，用上次的唯讀腳本。
   - 範圍 5 個：The Reach 修正版，加上 Nolvus 帶來的 Fort Dawn、Volkihar、The Rift、Whiterun。

     | 插件 | 記錄 | 錯誤 |
     |---|---|---|
     | NITHI NPCs - The Reach - Complete - AI Overhaul.esp（修正版） | 57 | **0** |
     | NITHI  NPCs - Dawnguard - Fort Dawn - Complete - AI Overhaul.esp | 8 | 0 |
     | NITHI NPCs - Dawnguard - Volkihar - Complete - AI Overhaul.esp | 16 | 0 |
     | NITHI NPCs - The Rift - Complete - AI Overhaul.esp | 68 | 0 |
     | NITHI NPCs - Whiterun - Complete - AI Overhaul.esp | 77 | 0 |

   - 沒有存檔：修正版的時間 10:31:50 早於 SSEEdit 開啟；mods 與 overwrite 都沒有其他新的插件。
   - SSEEdit 的參數已改回空白（備份 `ModOrganizer.ini.bak-20260928-103210`、`-103732`）。
5. **Lastendell**：
   - Nolvus 的實例裡沒有 DynDOLOD 工具和記錄，用的是現成輸出 `DynDOLOD - Output - Ultimate`，所以「Ignoring Cell」**沒有記錄可比對**。
   - 比對輸出：Nolvus 的 Lastendell 有 47 個 LOD 檔（Objects、Trees），我們的有 52 個（Objects、Trees）。那些被略過的 cell 沒有讓這個世界空間缺少 LOD。
6. **主選單測試**：
   - DataLoaded 176 秒，到得了主選單。
   - SKSE 215／214，OAR E 4。
   - BEES 1,959 行，沒有警告；沒有 crash log。

## 工具結果（照抄 reports\*.txt 的每一行）
```
== build_instance-create 報告 (2026-09-28 10:29)（試跑的各行相同）==
[資訊] 模式：實際執行
[資訊] ModOrganizer.ini：已存在，保留（要重寫請加 --rewrite-ini）
[通過] 設定檔 Pages-ZH：modlist 4128 行（捨棄 21），plugins 4233 個（排除 12 個自製插件）
[資訊] 佔位資料夾：0 個（之後用 MO2 安裝到同名資料夾並選 Replace）
[通過] 遊戲 ini：Skyrim.ini, SkyrimPrefs.ini, SkyrimCustom.ini
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-102930
總結：[通過]

== build_instance-sync-order 報告 (2026-09-28 10:30)（--restore-states --apply）==
[資訊] 模式：實際執行
[通過] 啟用狀態：依目標啟用 0 個、停用 0 個；檔案不在已啟用的 mod 或遊戲資料夾裡，略過 15 個（之後要再跑 prune_dependents）
[通過] 插件順序：4527 個：依目標順序 4218，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 137 個插件到它的前置之後，例如：Natural Waterfalls - Blackreach.esp, Natural Waterfalls - Dawnguard.esp, Natural Waterfalls - Dragonborn.esp, DynDOLOD.esm, Occ_Skyrim_Lux_Via.esp, …
[資訊] 不在目標清單中的插件：DBM_CC_SunderWraithguardPatchV4.esp, DBVO Fix - The Gray Cowl Returns.esp, JKs Castle Volkihar - Xelzaz patch.esp, …
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-103050
總結：[通過]

== prune_dependents 報告 (2026-09-28 10:31)（--disable-folders --apply；試跑數字與名字相同）==
[資訊] 模式：實際執行
[注意] 要停用的插件：26 個，例如：Horsepower_Ragdoll - SC Horses Patch.esp, TSOSRefinedCreationClub.esp, Embershard.esp, Lux Orbis - Embershard patch.esp, Lux - Embershard patch.esp, Northern Roads - Alternate Perspective Patch.esp, …
[資訊] 建議停用的資料夾：18 個：Leveled List Patch, Nolvus Awakening Consistency Patch, Horsepower Ragdoll - SC Horses Skeleton Patch, Nolvus Awakening AI Patch, Nolvus Awakening Economy Patch, …
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-103105
總結：[注意]

== forward_appearance 報告 (2026-09-28 10:31)（--apply；試跑相同，第 4 行為 [注意]「會寫到」）==
[資訊] 模式：實際執行
[資訊] 外觀來源：NITHI NPCS - The Reach - Women.esp（Nithi NPC Enhancement - The Reach）：NPC 28 筆
[資訊] 外觀來源：NITHI NPCs - The Reach - Men.esp（Nithi NPC Enhancement - The Reach）：NPC 58 筆
[通過] NITHI NPCs - The Reach - Complete - AI Overhaul.esp：49 筆 NPC 的外觀改用來源的值（NAM9 11, PNAM 11, QNAM 32, RNAM 1, WNAM 20）；已一致 8 筆；來源：AI Overhaul - Nithi NPC Enhancements Patch Hub；已寫到 Pages - 版本不符修正
總結：[通過]

== build_instance-sync-order 報告 (2026-09-28 10:31)（--apply）==
[資訊] 模式：實際執行
[通過] 插件順序：4501 個：依目標順序 4192，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 134 個插件到它的前置之後，例如：Natural Waterfalls - Blackreach.esp, Natural Waterfalls - Dawnguard.esp, Natural Wa…
[資訊] 不在目標清單中的插件：（同上）
總結：[通過]

== check_plugins 報告 (2026-09-28 10:31)（prune 後與 forward_appearance 後兩次，各行相同）==
[通過] 完整插件數（含本體）：253 / 254
[通過] 輕量插件數（ESL）：4012 / 4096
[通過] 缺少前置的插件：0 個
[通過] 前置順序錯誤：0 個
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 921 個；BEES 已安裝；遊戲 1.5.97.0
總結：[通過]
```
- `[注意]` 的說明：prune 的 26 個和已接受的相同。

## 需要雲端決定
- 沒有。接下來請使用者照 `docs/測試路線.md` 玩第 11 節的新遊戲測試：
  - 馬卡斯那站多看幾個 NPC 的臉和身體，確認沒有黑臉，頭和脖子的膚色一致。
  - 使用者回報通過後，我做第 12 節的 EN-baseline 備份。

## 本輪手動處理（只修改設定或新增，沒有刪除）
- MO2 的 SSEEdit 參數：暫時加 `-D:`／`-P:`，已改回空白。
- 測試主選單時，到主選單就結束遊戲，沒有存檔。

## 本地提交（尚未推送）
- 本回報與 status。
