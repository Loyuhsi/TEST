# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：5 重建輸出。照 cloud-notes f92218b「接下來的順序」做完 1–3。**第 4 步 DynDOLOD 在 13 分 45 秒時，被另一個插件的 Unresolved FormID 擋下，停下回報。**
- 日期：2026-09-28
- 結論：
  - 6 個 HoF／TCC 插件已照目標停用。`check_plugins` 全部通過（完整 251、輕量 4012），主選單 166 秒。
  - DynDOLOD 這次通過了 Tamriel（上一輪 3 分鐘就停下的 HoF 問題已經沒有了）。
  - 處理 Solstheim 時出現致命錯誤：
    - 「Unresolved FormID [110072E8] LegacyoftheDragonborn.esm might be the wrong version for **Lux Orbis - LotD patch.esp**」。
    - 出錯的是 `[REFR:11007306]`（LuxOrbis_HangingLanternDesatNS），它的**啟用父項（XESP）**指向 LOTD V6 沒有的記錄。
  - 為了不再一次撞一個，我掃了整個載入順序所有放置記錄的引用欄位：
    - **未解析的引用共 36 筆、10 個插件，全部指向 LegacyoftheDragonborn.esm（V5 的記錄）**。
    - 其中 23 筆在 6 個插件的室外世界空間，DynDOLOD 之後都會一個一個撞到。
  - 這些都是 **Nolvus 對應 LOTD 5.6 的補丁**，D:\PM 是 LOTD V6。我找到的新版全部驗證過，其中 5 個 DBM 補丁的新版壓縮檔已經在 downloads。見「需要雲端決定」。

## 照 cloud-notes 的步驟
1. `git pull --rebase`（f92218b）、`python -m pytest -q`：193 項全過。
2. **重建設定檔**：
   - `create --apply`：試跑相同，佔位資料夾 0。6 個插件在 plugins.txt 是停用。
   - 開 MO2 一次再關，00:44 寫回 plugins.txt。
   - `sync-order --restore-states --apply`：啟用 0、停用 0，6 個仍是停用。
   - `prune_dependents` 試跑：**26 個插件、18 個資料夾，名字和上一輪相同**，沒有因為這 6 個多出來的名字。
   - 接著 `--disable-folders --apply`。
3. **檢查**：
   - `check_plugins` 全部通過：完整 251，輕量 4012（4018 減這 6 個），BEES 1.71 標頭 913。
   - `verify` 缺 41、待重建輸出 3。
   - 主選單：
     - DataLoaded 166 秒，到得了主選單。
     - SKSE 215／214，OAR E 4。
     - BEES 1,943 行，沒有警告；沒有 crash log。
4. **DynDOLOD**：
   - 從 MO2 啟動，精靈 → Advanced → High。選項和上一輪相同：
     - Object／Tree／Dynamic LOD、Occlusion data＋Plugin；Grass LOD 灰的、沒勾。
     - 輸出 `D:\PM\tools\DynDOLOD\DynDOLOD_Output\`，世界空間全選。
   - Tamriel 完成物件與樹的貼圖集、Dynamic LOD、地形底面。
   - 開始處理 `[DLC2SolstheimWorld]` 的 26,537 個參照時，13 分 45 秒跳出上面那個錯誤，只能按 Exit。
   - 這時已產生 1,577 個輸出檔（1.5 GB），是不完整的。已**搬到** `_replaced\dyndolod-partial-20260928-0106`，沒有刪除，`DynDOLOD_Output` 現在是空的。
   - `dyndolodCS2` 仍是空的；`sync-order`、`check_plugins`、`audit_skse` 都還沒跑。

## DynDOLOD 記錄摘要（這次的工作階段）
- **錯誤 172 個**：

  | 種類 | 數量 | 說明 |
  |---|---|---|
  | Texture resolution | 113 | 貼圖尺寸不是 2 的次方；M&V 的記錄也有 |
  | Deleted reference | 51 | 被刪除的參照；M&V 也有 |
  | Unresolved FormID | 2 | 致命的是 Lux Orbis LotD 那 1 個；另 1 個是 `akd_MorthalOldGateMill.esp` 的 ACTI，沒有擋住，M&V 自己跑也有 |
  | Root block is NiNode | 2 | |
  | File not found | 2 | |
  | 其他 | 3 | Path not allowed、No LOD model、按 Exit 時中斷的貼圖轉換各 1 |

- **警告 2,642 個**：

  | 種類 | 數量 |
  |---|---|
  | File not found | 850 |
  | Max tree LOD billboard count of 256 on atlas exceeded | 648 |
  | 檔名不合慣例 | 465 |
  | Textures do not match | 203 |
  | Duplicate reference | 157 |
  | Reference attached to wrong cell | 91 |
  | Property not found | 68 |
  | LOD model | 41 |
  | NULL reference | 11 |
  | 貼圖尺寸、Root block、大型參照、extended FormID 等 | 約 70 |

- **「Max tree LOD billboard count of 256」**：648 個中有 647 個在 Tamriel，這些樹會沒有遠景樹 LOD。
  - 一張貼圖集最多放 256 種 billboard。這次 TexGen 做了 1,259 種，M&V 是 777 種。
  - 這是畫面品質問題，請雲端判斷要不要調整（例如 TexGen 或 Tree LOD 的設定）。

## 未解析引用的完整掃描（唯讀；表格在 `data/analysis/unresolved_refs.csv`）
- 方法：
  - 先收集整個載入順序每一筆記錄的 FormID（含覆寫與注入的記錄）。
  - 再檢查非官方插件所有放置記錄的引用欄位：NAME（基底物件）、XESP（啟用父項）、XLKR、XTEL、XLCN 等。
  - PlayerRef（0x14）這種引擎內建的編號不算，有 61,360 筆，都是正常用法。
- 結果：36 筆、10 個插件，**全部指向 LegacyoftheDragonborn.esm**。

  | 插件（目前生效的來源） | 筆數（室外） | 欄位 → 缺的 LOTD 記錄 | 新版（都驗證過：沒有未解析的引用） |
  |---|---|---|---|
  | DBM_Falskaar_Patch.esp（Nolvus 5.6.2） | 6（6，Falskaar） | NAME → 02B9F2、02B9FD、381251 | LOTD 官方補丁 **6.10.9**（已在 downloads） |
  | DBM_Wyrmstooth_Patch.esp（Nolvus 5.6.2） | 4（4，Wyrmstooth） | 同上 | 6.10.9 |
  | DBM_Clockwork_Patch.esp（Nolvus 5.6.2） | 3（3，Clockwork） | 同上 | 6.10.9 |
  | DBM_TheGrayCowlofNocturnal_Patch.esp（修正版，原檔 Nolvus 5.6.2） | 3（3） | 同上 | 6.10.9 |
  | DBM_ForgottenCity_Patch.esp（Nolvus 5.6.2） | 1（室內） | NAME → 381251 | 6.10.9 |
  | DBM_BSHeartlandPatch - Main.esp（Nolvus 的 BS Synergy 1.12） | 6（6，BS Bruma） | NAME → 同上 3 筆 | Synergy **1.13.2**（36074／667108，151 KB；我下載到 scratchpad 驗證過，沒有安裝） |
  | Lux Orbis - LotD patch.esp（修正版，原檔 Nolvus Lux Orbis Patch Hub） | 1（1，Solstheim） | XESP → 0072E8 | Lux Orbis Patch Hub **4.7**（已在 downloads）：沒有未解析的引用，但還有 4 筆覆寫指向 V6 沒有的記錄，`--drop-missing` 可以處理 |
  | Lux - Legacy of the Dragonborn patch.esp（修正版，原檔 Nolvus Lux Patch Hub） | 10（室內） | XESP → 5A95BA | Lux Patch Hub **7.2**（已在 downloads）：沒有問題 |
  | DBM_Lucien_Patch.esp（Nolvus Follower Room Patches 3.0.1） | 1（室內） | NAME → 143345 | Nexus 最新 4.0.16（771654），沒有下載驗證 |
  | LOTD_HUB.esp（修正版，原檔 HoF 2.3.9） | 1（室內） | NAME → 143345 | HoF 2.4.26（(A) 方案，已決定留到第 8 階段） |

- 5 個 DBM 補丁的新舊版比較：6.10.9 版的記錄數不同（例如 Falskaar 自己的記錄 212 → 105），3 個改成 1.71 並多一個前置 `_ResourcePack.esl`。每個都附一個 BSA，Wyrmstooth 除外。
- 新版的前置都已經在載入順序裡。

## 需要雲端決定
1. **Nolvus 的 LOTD 5.6 補丁換成對應 V6 的新版**（這樣 DynDOLOD 才能跑完）：
   - 室外 6 個一定要處理，否則 DynDOLOD 會在各自的世界空間停下：
     - Falskaar、Wyrmstooth、Clockwork、Gray Cowl → 6.10.9。
     - BS Synergy → 1.13.2。
     - Lux Orbis LotD → 4.7。
   - 室內 4 個可以一起處理：
     - ForgottenCity → 6.10.9。
     - Lux LotD → 7.2。
     - Lucien → 4.0.16。
     - LOTD_HUB 那 1 筆。
   - 我的建議：
     - 用 `decisions.csv`／`plugin_sources` 的方式指定來源，由 `fill_plugins` 或 `install_archives` 放入。原檔搬到 `_replaced`，BSA 跟著換。
     - 然後**重做版本不符修正**：`Pages - 版本不符修正` 裡已有 Gray Cowl、Lux Orbis LotD、Lux LotD、LOTD_HUB 的舊版修正檔。它們優先權較高，會蓋掉新版，要先移走再重跑覆寫掃描與 `--drop-missing`。
     - 室內 1 筆的 LOTD_HUB 和 Lucien，如果不想換版本，也可以讓 `strip_refs` 刪掉這種放置記錄（基底物件不存在，遊戲本來就不會顯示）。
   - 新版的 FOMOD 選項（例如 Lux Orbis 4.7 有 `00 Data` 與「Solitude LotD meshes」兩種 LotD 補丁）需要對應目標，請指定。
2. **Tamriel 的樹 LOD billboard 超過上限**（647 個參照沒有樹 LOD）：要不要處理？
3. 另外 1 個非致命的 Unresolved FormID（akd_MorthalOldGateMill.esp）M&V 也有，我建議不處理。

## 其他
- MO2 的 overwrite 有 3,471 個 `ShaderCache` 檔（Community Shaders 在測試主選單時產生）和幾個執行時的設定檔，和 DynDOLOD 無關，沒有動。
- xEdit 的引用檢查（cloud-notes 第 6 步）在 DynDOLOD 完成後才做，還沒開始。

## 工具結果（照抄 reports\*.txt 的每一行）
```
== build_instance-create 報告 (2026-09-28 00:42)（試跑的各行相同）==
[資訊] 模式：實際執行
[資訊] ModOrganizer.ini：已存在，保留（要重寫請加 --rewrite-ini）
[通過] 設定檔 Pages-ZH：modlist 4128 行（捨棄 21），plugins 4233 個（排除 12 個自製插件）
[資訊] 佔位資料夾：0 個（之後用 MO2 安裝到同名資料夾並選 Replace）
[通過] 遊戲 ini：Skyrim.ini, SkyrimPrefs.ini, SkyrimCustom.ini
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-004259
總結：[通過]

== build_instance-sync-order 報告 (2026-09-28 00:44)（--restore-states --apply）==
[資訊] 模式：實際執行
[通過] 啟用狀態：依目標啟用 0 個、停用 0 個；檔案不在已啟用的 mod 或遊戲資料夾裡，略過 18 個（之後要再跑 prune_dependents）
[通過] 插件順序：4524 個：依目標順序 4215，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 136 個插件到它的前置之後，例如：Natural Waterfalls - Blackreach.esp, Natural Waterfalls - Dawnguard.esp, Natural Waterfalls - Dragonborn.esp, Occ_Skyrim_Lux_Via.esp, Rainbows over Waterfalls - Bruma addon.esp, Rainbows over Waterfalls - Natural Waterfalls patch.esp, Complementary Gras…
[資訊] 不在目標清單中的插件：Northern Roads - Man Those Borders Reborn Patch.esp, Snazzy Interiors - Riften AIO - TGR patch.esp, Lux - JK's Whiterun Outskirts patch.esp, DBVO Fix - Remiel.esp, DBVO Fix - AYOP Main Quest.esp, Orc Strongholds - AIO - 4thUnknown Ogrims Patch.esp, Lux - Sunthgat.esp, DBVO Fix - Headhunt…
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-004413
總結：[通過]

== prune_dependents 報告 (2026-09-28 00:44)（--disable-folders --apply；試跑數字與名字相同）==
[資訊] 模式：實際執行
[注意] 要停用的插件：26 個，例如：Horsepower_Ragdoll - SC Horses Patch.esp, TSOSRefinedCreationClub.esp, Embershard.esp, Lux Orbis - Embershard patch.esp, Lux - Embershard patch.esp, Northern Roads - Alternate Perspective Patch.esp, Nolvus Awakening Armors Balance Patch.esp, Nolvus Awakening Weapons Balance Patch.esp
[資訊] 建議停用的資料夾：18 個：Leveled List Patch, Nolvus Awakening Consistency Patch, Horsepower Ragdoll - SC Horses Skeleton Patch, Nolvus Awakening AI Patch, Nolvus Awakening Economy Patch, Nolvus Awakening Combat & Enemies Patch, Nolvus Awakening Boss Integration, Nolvus Awakening Crafting Patch
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-004425
總結：[注意]

== check_plugins 報告 (2026-09-28 00:44) ==
[通過] 完整插件數（含本體）：251 / 254
[通過] 輸出重建後的完整插件（預估）：253 / 254：DynDOLOD.esm, DynDOLOD.esp 一定是完整插件；Synthesis.esp、FNIS.esp、Occlusion.esp、PG_* 必須是輕量插件
[通過] 輕量插件數（ESL）：4012 / 4096
[通過] 缺少前置的插件：0 個
[通過] 前置順序錯誤：0 個
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 913 個；BEES 已安裝；遊戲 1.5.97.0
總結：[通過]

== build_instance-verify 報告 (2026-09-28 00:44) ==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[資訊] 清單外的資料夾：84 個：ZH - 官方繁中字串, Unslaad PBR, Smooth Special Idle, Maerchenwald - Archwood Lite - Giant Fantasy Trees, horseAnimations2, clockwork pbr, Creation Club: _ResourcePack, Creation Club: ccafdsse001-dwesanctuary, Creation Club: ccasvsse001-almsivi, Creation Club: ccbgssse001-fish
[注意] plugins.txt 與預期比對：缺少或未啟用 41 個（mod 尚未安裝或已被修剪）；待重建輸出 3 個；例如：Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, Anchor Animations Spell V2.esp, FH_Grapple.esp, AnchorShdSwd.esp, SC_HorseReplacer.esp
總結：[注意]
```
- `[注意]` 的說明：
  - prune 的 26 個和上一輪相同。
  - verify 的 41 個＝15＋26（目標裡停用的 6 個不算缺少）；待重建輸出 3 個是 DynDOLOD.esm、DynDOLOD.esp、Occlusion.esp。

## 本輪手動處理（只搬移或下載到 scratchpad，沒有刪除）
- DynDOLOD 不完整的輸出（1,577 檔）搬到 `_replaced\dyndolod-partial-20260928-0106`。
- 為了驗證，只把新版補丁解到 scratchpad：
  - LOTD 官方補丁 6.10.9、Lux／Lux Orbis Patch Hub、HoF 2.4.26 的壓縮檔原本就在 downloads。
  - BS Synergy 1.13.2 是從 Nexus 下載到 scratchpad。
  - 都沒有放進 D:\PM。

## 本地提交（尚未推送）
- 本回報、status、`data/analysis/unresolved_refs.csv`（插件名稱與 FormID，沒有個資）。
