# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：5 重建輸出。照 cloud-notes 78aa2e5「接下來的順序」做完 1–8。**第 9 步 DynDOLOD 之前停下回報。**
- 日期：2026-09-28
- 結論：
  - **換版完成**：
    - LOTD 官方補丁 6.10.9 的 5 個（連同 BSA）。
    - Lux Patch Hub 7.2 的 LotD 補丁。
    - Lux Orbis Patch Hub 4.7 的 LotD 補丁（`00 Data` 通用版）。
    - BS Synergy 1.13.2。
  - **兩個掃描**：
    - 未解析引用 **0**。
    - 覆寫掃描只剩原本接受的 16 個：BS Synergy 換成 1.13.2 後，從原本的 17 個裡消失。
  - **檢查**：`check_plugins` 全部通過（完整 251、輕量 4012），主選單 166 秒。
  - **停在 DynDOLOD 之前的原因**：覆寫掃描多出 **`Synthesis.esp` → `Lux Orbis - LotD patch.esp` 4 筆**。
    - Synthesis.esp 是用舊版 Lux Orbis LotD 產生的，裡面有 4 筆 LAND 覆寫舊版自己新增的 LAND；4.7 版沒有這些記錄。
    - 手冊沒寫「換插件之後要重跑哪些輸出」，所以請雲端決定。
  - 有 2 處照工具的實際狀況做了小調整（install_archives、fill_plugins），見步驟 2、4，也列在「工具缺口」。

## 照 cloud-notes 的步驟
1. `git pull --rebase`（78aa2e5）、`python -m pytest -q`：198 項全過。
2. **BS Synergy**：
   - `manifest`：reinstall 1 個（Synergy Patch2，36074／667108）。
   - `nexus_fetch`：下載 1 個。
   - `install_archives --only …` 試跑判為 **「需要人工判斷：decisions 註記要人工（FOMOD）」**。
     - 原因：`NOTE_NEEDS_PERSON` 只比對字串，而 decisions 的備註寫的是「沒有 FOMOD」。
     - 壓縮檔確實沒有 FOMOD，根目錄就是插件和 1 個模型。
   - 我用一個小包裝程式呼叫 install_archives 自己的流程，**只對這一個資料夾**把備註裡含「沒有 FOMOD」的情況視為不需要人工，其他判斷都不變：
     - 試跑：「可自動重裝 1 個」。
     - `--apply`：「已重裝 1 個」，舊內容在 `_replaced\Beyond Skyrim - Legacy of the Dragonborn Synergy Patch2`。
     - meta.ini 是 1.13.2。
   - 換之前確認過：舊資料夾另外有 2 個飛艇對話 script 和 1 個 SEQ。新版插件已經不引用這些 script，也沒有開局就啟動的任務，所以整包換沒有問題。
3. **舊檔搬到 `_replaced\lotd56-patches-20260928-014302\`**（15 個檔，搬移前逐一列出確認）：
   - `(Official)2`：Clockwork、Falskaar、ForgottenCity、TheGrayCowlofNocturnal、Wyrmstooth 的 esp＋bsa，共 10 個。沒有「- Textures.bsa」。
   - `Lux Orbis - Patch Hub2\Lux Orbis - LotD patch.esp`、`Lux - Patch Hub3\Lux - Legacy of the Dragonborn patch.esp`。
   - `Pages - 版本不符修正` 的 3 個舊修正版：Gray Cowl、Lux Orbis LotD、Lux LotD。
   - `LOTD_HUB.esp` 的修正版照指示留著。
4. **放入新版**：
   - `fill_plugins`（不加 `--mv`、`--nolvus`）第一次試跑：
     - archive 是 **7 個**，比預期多 1 個 `Horsepower_Ragdoll - SC Horses Patch.esp`。
     - 它是已修剪的 26 個之一，資料夾已被停用，所以 fill_plugins 當成缺少，想從 downloads 的壓縮檔補到 `Horsepower - Pandora Cache`。
     - ambiguous 是 Lux Orbis LotD（預期）和 `full_inu ArmorPack01 SPID.esp`（第 4 階段就知道：前置不存在、已修剪）。
   - 照指示**沒有直接 `--apply`**。我把那 1 個壓縮檔（加上 .meta）暫時搬到 `D:\PM\_hold_downloads`，再試跑一次，archive 剛好是預期的 6 個：
     - 5 個 DBM → `(Official)2`，來源是 6.10.9 的 `04 CWP`／`04 FKP`／`04 FCP`／`04 GCN`／`04 WTP`。
     - Lux LotD → `Lux - Patch Hub3`。
   - `--apply`：解壓放入 10 個檔（5 esp、4 bsa、Lux 1 esp），錯誤 0。完成後立刻把壓縮檔搬回 downloads。
   - **Lux Orbis LotD**：
     - 從 4.7 壓縮檔的 `Lux Orbis (patch hub)/00 Data/` 取出，161,197 bytes，和壓縮檔一致。
     - `esl_check --plugin`：輕量、HEDR 1.71、前置 10 個（都在載入順序裡）、282 筆。
     - 複製到 `Lux Orbis - Patch Hub2`，雜湊相同。
5. `sync-order --apply` → `check_plugins`：全部通過。完整 251 沒有增加，輕量 4012，BEES 1.71 標頭 918（多出的 5 個是新版）。
6. **覆寫掃描**：
   - 重跑後，不在已接受名單內的只有 2 個：
     - `Lux Orbis - LotD patch.esp` → LOTD：4 筆（預期中）。
     - **`Synthesis.esp` → `Lux Orbis - LotD patch.esp`：4 筆（LAND 000806、000807、000808…，都在室外）**，不在預期內。
   - `DBM_HUB_BillyRoW_Patch.esp` → LOTD_HUB 4 筆也列出來，但它就是原本接受的其中一個。它的前置 LOTD_HUB.esp 現在由修正版提供，所以被我的分類算成「來源不同」。
   - `strip_refs --drop-missing --plugin "Lux Orbis - LotD patch.esp"`：試跑相同，`--apply` 刪 4 筆（連同空群組共 6 項），寫到 `Pages - 版本不符修正`。
7. **未解析引用掃描**：
   - 重跑：只剩 `LOTD_HUB.esp`、`DBM_Lucien_Patch.esp` 各 1 筆（NAME → 143345，都在室內），和預期相同。表格在 `data/analysis/unresolved_refs.csv`。
   - `strip_refs --drop-unresolved-base --from-csv …`：試跑相同；`--apply` 後：
     - LOTD_HUB：刪 1 筆（原地更新修正版）。
     - Lucien：刪 1 筆，新的修正版寫到 `Pages - 版本不符修正`。
   - 兩個掃描都再跑（先跑 `check_plugins` 更新「生效的是哪一份檔」）：
     - 未解析引用 **0**。
     - 覆寫掃描：已接受的 16 個（68 筆）＋ **Synthesis.esp 4 筆**。
     - `data/analysis/override_mismatch.csv` 現在只有 Synthesis 這一列。
8. `sync-order --apply` → `check_plugins` 全部通過（同第 5 步）→ **主選單**：
   - DataLoaded 166 秒，到得了主選單。
   - SKSE 215／214，OAR E 4。
   - BEES 1,953 行，沒有警告；沒有 crash log。

## 需要雲端決定
1. **換插件之後，已經產生的輸出要不要重跑**（DynDOLOD 之前）：
   - **Synthesis.esp**：前置有 `Lux Orbis - LotD patch.esp`。它有 4 筆 LAND 覆寫舊版自己新增的記錄，新版沒有這些，所以會變成多出來的 LAND。
     - 另外，Synthesis 是複製「當時生效的 LAND」再調亮，換過的插件如果改過 LAND，Synthesis 會用舊資料蓋過新版。
     - 我建議照 docs/05 第 3 節**重跑 Synthesis**：同一個 patcher、預設設定，約 10 分鐘。之後加 ESL 旗標、sync-order、check_plugins，覆寫掃描應該只剩 16 個。
   - **PG_1.esp**：前置有換過的 `DBM_ForgottenCity_Patch.esp`、`DBM_Falskaar_Patch.esp`、`DBM_BSHeartlandPatch - Main.esp`。
     - 覆寫都還對得上，沒有指向不存在的記錄。
     - 但它存的是舊版那些記錄的內容，會蓋掉新版的改動；新版 BSA 裡的模型也沒有經過 PGPatcher。
     - 重跑 PGPatcher 約 5 分鐘，要先停用 `pgpatcher_output`。
   - 草地快取、xLODGen、TexGen：換的都是 LOTD 展示類的補丁，影響應該很小。只有舊版 Lux Orbis LotD 的那 4 筆 LAND 會影響地形或草。請指示要不要重跑。
2. **工具缺口**：
   - `install_archives`：decisions 備註寫「沒有 FOMOD」也會被當成要人工。
   - `fill_plugins`：在 prune 之後執行時，會把「資料夾被停用的已修剪插件」當成缺少，從壓縮檔補到別的資料夾（這次是 Horsepower）。建議排除 prune 停用的資料夾。
   - `docs/05`：建議寫明「換掉任何插件後，要重跑以它為前置的輸出（Synthesis、PGPatcher…）」。

## 兩個掃描的結果
- 未解析引用（放置記錄）：**0**。
  - 另有 61,646 筆是 PlayerRef 等引擎內建的編號，正常，不計。
  - 刪掉的 2 筆列在 `data/analysis/unresolved_refs.csv`。
- 覆寫掃描：不在已接受名單內的只有 `Synthesis.esp` 4 筆（`data/analysis/override_mismatch.csv`）。
  - 已接受的從 17 個變成 16 個（68 筆）：BS Synergy 1.13.2 沒有不符的覆寫了。
  - 0x800 以下的撞號：0。

## 輸出資料夾的檔案數
| 資料夾 | 檔案數 |
|---|---|
| `SYNTHESSIS` | 1（舊版，可能要重跑） |
| `pgpatcher_output` | 20,432 |
| `grass CS` | 15,340 |
| `lodgen2` | 48,852 |
| `texgenCS` | 5,292 |
| `dyndolodCS2` | 0 |
| `Pages - 版本不符修正` | 58（原本 59，搬走 3 個舊修正版，加上新的 Lux Orbis LotD 和 Lucien） |

## 工具結果（照抄 reports\*.txt 的每一行）
```
== manifest 報告 (2026-09-28 01:41) ==
[資訊] 目標資料夾：4054 個
[資訊] 已就位：4023 個
[資訊] 需從 Nexus 下載：0 個
[資訊] 第五階段重建：9 個
[資訊] 需換成 1.5.97 版 DLL：0 個
[注意] 需整包重裝（舊內容移到 _replaced）：1 個
[資訊] 尚無來源，需人工確認：0 個
[資訊] 捨棄：21 個
[資訊] 輸出：reports\manifest.csv、reports\downloads.html
總結：[注意]

== nexus_fetch 報告 ==
[通過] 本次下載：1 個
總結：[通過]

== install_archives 報告 (2026-09-28 01:41)（--only …，照原工具試跑）==
[資訊] 試跑（除了還原中斷的安裝，不改動檔案）：判斷了 1 個下載
[資訊] 磁碟空間：預計解壓 0 B，D:\ 剩 242.0 GB
[注意] 需要人工判斷（見 install_archives.csv 的 reason 欄）：1 個
總結：[注意]

== install_archives 報告 (2026-09-28 01:42)（只對這個資料夾略過備註關鍵字；試跑）==
[資訊] 試跑（除了還原中斷的安裝，不改動檔案）：判斷了 1 個下載
[資訊] 磁碟空間：預計解壓 698.2 KB，D:\ 剩 242.0 GB
[通過] 可自動重裝（舊資料夾移到 _replaced，不刪除）：1 個
總結：[通過]

== install_archives 報告 (2026-09-28 01:42)（同上，--apply）==
[資訊] 執行：判斷了 1 個下載
[資訊] 磁碟空間：預計解壓 698.2 KB，D:\ 剩 242.0 GB
[通過] 已重裝（舊資料夾在 _replaced）：1 個
總結：[通過]

== fill_plugins 報告 (2026-09-28 01:43)（第一次試跑）==
[資訊] 模式：試跑（加 --apply 才會寫入）
[資訊] 目標插件缺少檔案：40 個（已排除第 5 階段的輸出插件）
[通過] 從壓縮檔取出：7 個
[注意] 不明確（見 csv 的 note）：2 個
[注意] 找不到來源：31 個
總結：[注意]

== fill_plugins 報告 (2026-09-28 01:45)（Horsepower 壓縮檔暫時移開後 --apply；試跑的前 5 行相同，找不到來源 32 個）==
[資訊] 模式：實際執行
[資訊] 目標插件缺少檔案：40 個（已排除第 5 階段的輸出插件）
[通過] 從壓縮檔取出：6 個
[注意] 不明確（見 csv 的 note）：2 個
[注意] 找不到來源：32 個
[通過] 寫入結果：連結 0、解壓放入 10、已存在略過 0、錯誤 0
[資訊] 下一步：關 MO2 跑 build_instance.py sync-order --restore-states --apply，再 verify
總結：[注意]

== esl_check 報告（--plugin Lux Orbis 4.7 的 LotD patch）==
[資訊] Lux Orbis - LotD patch.esp：light，HEDR 1.71，前置 10 個；記錄 282 筆（新增 6、覆寫 276）；覆寫類型：REFR 203, CELL 68, WRLD 4, NAVI 1；新增類型：REFR 6；ESL：已經是輕量插件
總結：[資訊]

== strip_refs 報告 (2026-09-28 01:47)（--drop-missing --plugin "Lux Orbis - LotD patch.esp"；試跑相同，狀態為 [注意]「會寫到」）==
[資訊] 模式：刪除覆寫不存在記錄的整筆記錄；實際執行
[通過] Lux Orbis - LotD patch.esp：刪除 4 筆覆寫不存在記錄的記錄（連同子記錄與空群組共 6 項）；來源：Lux Orbis - Patch Hub2；已寫到 Pages - 版本不符修正
總結：[通過]

== strip_refs 報告 (2026-09-28 01:48)（--drop-unresolved-base --from-csv data/analysis/unresolved_refs.csv；試跑相同）==
[資訊] 模式：刪除基底物件不存在的放置記錄；實際執行
[通過] LOTD_HUB.esp：刪除 1 筆基底物件不存在的放置記錄（連同子記錄與空群組共 1 項）；來源：Pages - 版本不符修正（原地更新修正版）；已寫到 Pages - 版本不符修正
[通過] DBM_Lucien_Patch.esp：刪除 1 筆基底物件不存在的放置記錄（連同子記錄與空群組共 1 項）；來源：Legacy of the Dragonborn - Follower Room Patches；已寫到 Pages - 版本不符修正
總結：[通過]

== build_instance-sync-order 報告（01:45 與 01:48 兩次 --apply，各行相同）==
[資訊] 模式：實際執行
[通過] 插件順序：4506 個：依目標順序 4197，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 135 個插件到它的前置之後，例如：Natural Waterfalls - Blackreach.esp, Natural Waterfalls - Dawnguard.esp, Natural Waterfalls - Dragonborn.esp, Occ_Skyrim_Lux_Via.esp, Rainbows over Waterfalls - Bruma addon.esp, Rainbows over Waterfalls - Natural Waterfalls…
[資訊] 不在目標清單中的插件：Northern Roads - Man Those Borders Reborn Patch.esp, Snazzy Interiors - Riften AIO - TGR patch.esp, Lux - JK's Whiterun Outskirts patch.esp, DBVO Fix - Remiel.esp, …
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-014537（第二次另一個時間）
總結：[通過]

== check_plugins 報告 (2026-09-28 01:48)（01:45 那次各行相同）==
[通過] 完整插件數（含本體）：251 / 254
[通過] 輸出重建後的完整插件（預估）：253 / 254：DynDOLOD.esm, DynDOLOD.esp 一定是完整插件；Synthesis.esp、FNIS.esp、Occlusion.esp、PG_* 必須是輕量插件
[通過] 輕量插件數（ESL）：4012 / 4096
[通過] 缺少前置的插件：0 個
[通過] 前置順序錯誤：0 個
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 918 個；BEES 已安裝；遊戲 1.5.97.0
總結：[通過]
```
- `[注意]` 的說明：
  - manifest 的 reinstall 1 個就是 BS Synergy，已重裝。
  - fill_plugins 的「不明確 2」是 Lux Orbis LotD（已手動放入）和 full_inu（前置不存在、已修剪）。
  - 「找不到來源 32」是已接受缺少的 15 個，加上被停用資料夾裡的已修剪插件。

## 本輪手動處理（只搬移或新增，沒有刪除）
- 搬到 `_replaced`：
  - 舊 BS Synergy 資料夾：由 install_archives 搬。
  - 15 個舊 LOTD 5.6 補丁與舊修正版：`lotd56-patches-20260928-014302`。
- Horsepower 壓縮檔：暫時搬到 `_hold_downloads`，`--apply` 後搬回 downloads。
- Lux Orbis LotD 4.7：從壓縮檔解出，放進 `Lux Orbis - Patch Hub2`。
- 主選單測試後直接結束遊戲，沒有存檔。

## 本地提交（尚未推送）
- 本回報、status、`data/analysis/override_mismatch.csv`、`data/analysis/unresolved_refs.csv`（都只有插件名稱與數字，沒有個資）。
