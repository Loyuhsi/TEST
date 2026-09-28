# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：5 重建輸出。照 cloud-notes 47b1758「接下來的順序」做完 1–7：Synthesis、PGPatcher 重跑 → DynDOLOD → 第一次用 CS 啟動 → xEdit 檢查。
- 日期：2026-09-28
- 結論：
  - **DynDOLOD 完成**：High、Tree LOD 用 Ultra、Occlusion，25 分鐘，沒有致命錯誤。
    - `dyndolodCS2` 有 2,431 個檔。
    - `check_plugins` 完整 **253／254**，`Occlusion.esp` 是輕量插件。
    - 樹 billboard 超過上限的警告：**0**（上一輪 648）。
  - **第一次用 CS 啟動**：到得了主選單，沒有當機，`End` 可以開 CS 選單。
  - **Synthesis、PGPatcher 已重跑**：
    - Synthesis.esp 的前置已經沒有舊版 Lux Orbis LotD；LAND 7,675 筆，全都有 VCLR。
    - PGPatcher 輸出 20,425 個檔。
  - **兩個掃描**：未解析引用 0；覆寫掃描只剩已接受的 16 個。
  - **xEdit 檢查（唯讀）**：294 個插件裡 291 個沒有錯誤，**3 個有錯**。見「需要雲端決定」。
    - `Madmen - Simonrim.esp`：505 個 Could not be resolved。
    - NITHI 的 AI Overhaul 補丁：20 個引用類型錯誤。
    - `DBM_JKBluePalace_Patch.esp`：1 個。
  - 第 11 節的測試路線可以由使用者開始玩。xEdit 那 3 個是否要先處理，請雲端判斷。

## 照 cloud-notes 的步驟
1. `git pull --rebase`（47b1758）、`python -m pytest -q`：200 項全過。
2. **換過的插件有沒有地形類記錄**：
   - `esl_check --plugin` 一次給 17 個：目前生效的 8 個，加上 `_replaced` 裡的舊版 9 個（Lux Orbis LotD 的舊版有 Nolvus 原檔和舊修正版 2 份）。
   - 只有舊版 Lux Orbis LotD 兩份各有「新增 LAND 4」；**所有插件都沒有 LTEX、GRAS**。
   - 4 筆 LAND 的位置，以及這幾格現在由哪些插件提供 LAND：

     | 舊 LAND | 世界空間 | cell | 現在這一格有 LAND 的插件（載入順序，最後生效） |
     |---|---|---|---|
     | 000806 | RiftenWorld（Skyrim.esm:016BB4） | (42, -25) | Medieval Markets CC Fishing、RYFTEN DOWN、WiZkiD Signs INPC、Flora Additions - Waterplants |
     | 000807 | RiftenWorld | (42, -24) | Medieval Markets CC Fishing、RYFTEN DOWN、RYFTEN Defenses Canal、Flora Additions - Waterplants |
     | 000808 | WhiterunWorld（Skyrim.esm:01A26F） | (5, -2) | 14 個插件（JK's Drunken Huntsman、AI Overhaul、SKYKLFS…），最後是 HSPlayerHomes - Breezehome |
     | 000809 | WhiterunWorld | (4, -2) | 5 個插件，最後是 Ivy Whiterun Roofing |

3. **Synthesis 重跑**：
   - 舊的 Synthesis.esp 搬到 `_replaced\synthesis-20260928-085100`。
   - 從 MO2 執行：同一個 patcher（main e59abc8），Settings 確認是預設值，45.6 秒完成。
     - patcher 記錄：8,988 筆調整頂點顏色，60,857 筆沒有頂點顏色而略過，0 筆錯誤。
   - Overwrite 的 `Synthesis.esp` 搬到 `SYNTHESSIS`（71,213,851 bytes）。
   - `esl_check --subrecords LAND --flag`：
     - LAND **7,675** 筆，**VCLR 7,675**；前置 47 個。
     - 和舊版比：**少了 `Lux Orbis - LotD patch.esp`、多了 `HSPlayerHomes - Breezehome.esp`**。
   - LAND 沒有照預期少 4 筆，原因：Synthesis 每一格只輸出一筆 LAND。舊版 Lux Orbis 那 4 筆消失後，同樣 4 格改由現在生效的 LAND 補上：
     - Riften 兩格：Flora Additions - Waterplants。
     - Whiterun (5,-2)：HSPlayerHomes - Breezehome。
     - Whiterun (4,-2)：Ivy Whiterun Roofing。
     - 新舊兩份的 LAND 逐筆比對，差別只有這 4 對。
   - `--flag --apply` → `sync-order --apply` → `check_plugins`：全部通過（完整 251）。
4. **PGPatcher 重跑**：
   - `pgpatcher_output` 的 20,432 個檔整個搬到 `_replaced\pgpatcher-output-20260928-085523`（資料夾留著）。
   - 暫時停用 `pgpatcher_output`、`texgenCS`（MO2 關著時改 modlist.txt，備份 `_backup\20260928-085534-pgpatcher-rerun`）。
   - 從 MO2 執行，設定和上次相同（MO2 模式、輸出 `D:\PM\mods\pgpatcher_output`）。**253 秒完成**，critical 0。
     - error 9：6 個 weighted mesh 的 _0／_1 不一致、1 個模型、2 個貼圖處理失敗。
     - warning 218。
   - 輸出 **20,425 個檔（5,843 MB）**：`PGPatcher.esp`、`PG_1.esp`、meshes、textures、lightplacer。
   - 重新啟用兩個資料夾（備份 `_backup\20260928-090142-pgpatcher-reenable`）。
   - restore-states＋prune 一組：
     - `sync-order --restore-states --apply`：依目標啟用 8 個，並多一行「啟用重建出來的輸出插件：PGPatcher.esp, PG_1.esp」。它們在資料夾停用期間被 MO2 從 plugins.txt 拿掉了。
     - prune 試跑：**8 個，全在上一輪的 26 個裡，沒有新名字**。
       - 另外 18 個所在的 18 個資料夾本來就已停用，restore-states 會略過（「略過 36 個」），所以這次不會出現。
       - 接著 `--disable-folders --apply`（資料夾 0 個）。
   - `check_plugins` 全部通過：完整 251；PGPatcher.esp、PG_1.esp、Synthesis.esp 都是輕量插件。
5. **兩個掃描**：
   - 未解析引用 **0**：61,646 筆 PlayerRef 等引擎內建編號不算。
   - 覆寫掃描：16 個插件、68 筆，**都在已接受的名單內**，Synthesis 那 4 筆已經消失。`data/analysis/override_mismatch.csv` 現在只剩表頭。
6. **主選單測試**：
   - DataLoaded 191 秒，到得了主選單。
   - SKSE 215／214，OAR E 4。
   - BEES 1,953 行，沒有警告；沒有 crash log。
7. **DynDOLOD**：
   - 從 MO2 啟動 → 精靈按 Advanced → 按 High（記錄「Loading High rules」）→ 勾 **Ultra**。
     - 勾 Ultra 時「Tree LOD」自動取消，說明是「所有樹放進 object LOD，停用傳統樹 LOD」。
     - 其他選項：Object LOD、Dynamic LOD、Occlusion data＋Plugin、Terrain underside；Grass LOD 灰的、沒勾。
     - 世界空間全選，輸出 `D:\PM\tools\DynDOLOD\DynDOLOD_Output\`。
   - **25 分 09 秒完成**：「DynDOLOD plugins generated successfully」「Occlusion.esp completed successfully」，所有世界空間的 LODGen 都 successfully。
   - 按「Save and Exit」。
   - 輸出 **2,431 個檔、9,016 MB**：DynDOLOD.esm 2,636,570、DynDOLOD.esp 2,490,935、Occlusion.esp 14,760,912 bytes。
   - 整包搬到 `dyndolodCS2`。
   - `sync-order`（試跑後 `--apply`）：多一行「啟用重建出來的輸出插件：DynDOLOD.esm, DynDOLOD.esp, Occlusion.esp」。
   - `check_plugins` 全部通過：**完整 253／254**、輕量 4013。DynDOLOD.esm 是 master、DynDOLOD.esp 是完整、**Occlusion.esp 是輕量**，所以不用 `esl_check --flag`。
   - `audit_skse` 全部通過。
8. **第一次用 CS 啟動**（docs/05 第 10 節）：
   - DataLoaded 176 秒，到得了主選單。
   - 左上角沒有出現「Compiling Shaders」：著色器快取在之前幾次測主選單時已經建好，overwrite 的 ShaderCache 有 3,472 個檔。
   - 按 `End` 開得了 CS 選單（Community Shaders 1.9.1 的歡迎頁）。之後遊戲失去焦點，就直接結束遊戲，沒有存檔。
   - SKSE 215／214，沒有 crash log。
   - `CommunityShaders.log`：I 513、W 9、E 1。
     - E：「Legacy FullScreenBlur stage-count opcode contexts do not match the verified 1.5.97/1.6.1170 sequences; no blur adapters installed」。
     - W：2 行 I18n（es、fr 語系沒有額外的 CJK 字型候選），7 行「Failed to dispatch message to devbench」。
9. **xEdit 的引用檢查**（唯讀）：
   - 範圍 294 個：
     - 第 4 階段 `fill_plugins` 從壓縮檔取出、目前啟用、生效檔不在 `Pages - 版本不符修正`、而且是單一連結的 286 個。來源是當時的兩份執行紀錄，共 306 個「done」。
     - 加上這次換進來的 8 個（5 個 DBM、Lux LotD、Lux Orbis LotD、BS Synergy）。
   - 做法：
     - 給 SSEEdit 一份只列這 294 個的 plugins.txt（MO2 的 SSEEdit 參數暫時加 `-D:` 與 `-P:`，用完已改回空白）。前置由 xEdit 自動載入，ModGroups 不啟用。
     - 新增腳本 `Edit Scripts\Pages - Check listed plugins.pas`：和 xEdit 內建「Check for errors.pas」一樣呼叫 `Check()`，逐筆檢查清單上的插件，結果寫到文字檔。**沒有修改或存任何插件**：結束後確認 mods 與 overwrite 都沒有新的插件。
     - 載入 3 分 10 秒，檢查 47 秒。
   - 結果：**291 個 0 錯誤，3 個有錯誤**（529 行；表格在 `data/analysis/xedit_check_summary.csv`）：

     | 插件（來源） | 錯誤 | 種類 | 原因（我的追查） |
     |---|---|---|---|
     | Madmen - Simonrim.esp（Madmen - Patches 2.0.2，fill_plugins） | 505 | Could not be resolved：NPC 的 Perk 472、法術的 Base Effect 33 | 全部指向 `Adamant.esp`。補丁用的是**完整版** Adamant 的編號（例如 0D01CC、51FD45），我們裝的 Adamant 是**輕量（ESL）版**，編號不同 |
     | NITHI NPCs - The Reach - Complete - AI Overhaul.esp（AI Overhaul - Nithi Patch Hub 1.3，fill_plugins） | 23 | Found a TXST／HDPT／ARMA reference, expected ARMO（WNAM 皮膚）20；PNAM 頭部 Could not be resolved 2；TINI 1 | 指向 `NITHI NPCS - The Reach - Women.esp`。補丁對應的是另一版，編號錯位，**這 20 位 NPC 的皮膚會指到錯的東西** |
     | DBM_JKBluePalace_Patch.esp | 1 | NAVI 的 navmesh 引用 Could not be resolved | 和 JK's Blue Palace 版本不同，影響很小 |

   - 我第一次申請 SSEEdit 的畫面操作權限時，使用者沒看到提示，被判為拒絕；使用者之後允許，由我操作。

## DynDOLOD 記錄摘要（這次的工作階段）
- **錯誤 748**：

  | 種類 | 數量 | 說明 |
  |---|---|---|
  | Ignoring Cell | 372 | 全部在 Midwood Isle 的 Lastendell 世界空間：Midwood Isle - Trees Fix 220、Midwood Isle.esp 142、Grass Patch 9。記錄沒有寫原因；上一輪在 Solstheim 就停了，沒跑到這裡 |
  | Texture resolution（不是 2 的次方） | 309 | |
  | Deleted reference | 59 | Karthwasten 23、maerchenwald 11、Orc 7 等 |
  | Root block is NiNode | 3 | |
  | File not found | 2 | |
  | Unresolved FormID | 1 | 就是已接受、不處理的 akd_MorthalOldGateMill；沒有擋住 |
  | 其他 | 2 | Path not allowed、No LOD model 各 1 |

- **警告 2,274**：

  | 種類 | 數量 |
  |---|---|
  | File not found | 850 |
  | 檔名不合慣例 | 465 |
  | Texture resolution | 260 |
  | Textures do not match | 203 |
  | Duplicate reference | 202 |
  | Reference attached to wrong cell | 113 |
  | Property not found | 70 |
  | LOD model | 41 |
  | NULL reference | 11 |
  | Root block、大型參照、extended FormID 等 | 共約 30 |

- **「Max tree LOD billboard count」：0**，Ultra 解決了上限問題。

## 需要雲端決定
1. **xEdit 找到的 3 個插件**：
   - **Madmen - Simonrim.esp**：
     - 要改用對應 ESL 版 Adamant 的補丁（如果 Madmen - Patches 有），或停用這個補丁？
     - 目標裡的 Adamant 是哪一版也請確認。
     - 目前這些 Forsworn NPC 拿不到補丁給的 Adamant perk，33 個法術效果不存在。
   - **NITHI AI Overhaul 補丁**：
     - 20 位 NPC 的皮膚會指到錯的東西（看起來可能會壞），建議先處理。
     - 可以換對應版本的補丁、做只拿掉 WNAM／PNAM 的修正版，或停用。
   - `DBM_JKBluePalace_Patch.esp` 的 1 筆 NAVI：建議接受。
   - 這 3 個都不影響 LOD，DynDOLOD 不用重跑。
2. **Lastendell 的「Ignoring Cell」372 個**：只影響那個世界空間的 LOD，要不要追查？
3. 之後照順序：第 11 節測試路線（使用者玩）→ 第 12 節 EN-baseline。
   - 如果要先修第 1 點，只要修完的插件不影響室外 LOD，就不用重跑 DynDOLOD。

## 輸出資料夾的檔案數
| 資料夾 | 檔案數 | 大小 |
|---|---|---|
| `SYNTHESSIS` | 1 | 71 MB |
| `pgpatcher_output` | 20,425 | 5,843 MB |
| `grass CS` | 15,340 | 915 MB |
| `lodgen2` | 48,852 | 933 MB |
| `texgenCS` | 5,292 | 519 MB |
| `dyndolodCS2` | **2,431** | 9,016 MB |
| `Pandora Output` | 41 | 13 MB |
| `BodySlide (Nude)` | 8,754 | 7,447 MB |
| `Pages - 版本不符修正` | 58 | |

## 工具結果（照抄 reports\*.txt 的每一行）
```
== esl_check 報告 (2026-09-28 08:4x)（17 個 --plugin，只列記錄類型）==
（17 行 [資訊]：新版 8 個與舊版 9 個的記錄類型。只有舊版 Lux Orbis - LotD patch.esp 兩份有「新增類型：… LAND 4」；沒有任何 LTEX、GRAS。）

== esl_check 報告 (2026-09-28 08:54)（Synthesis.esp --subrecords LAND --flag，試跑）==
[資訊] Synthesis.esp：full，HEDR 1.71，前置 47 個；記錄 15392 筆（新增 0、覆寫 15392）；覆寫類型：CELL 7675, LAND 7675, WRLD 42；ESL：可以直接加 ESL 旗標
[資訊] LAND 子記錄：LAND 記錄 7675 筆；各子記錄出現在幾筆記錄：DATA 7675, VCLR 7675, VHGT 7652, VNML 7652, ATXT 7522, VTXT 7522, BTXT 7346
[資訊] 加 ESL 旗標（試跑）：可以
總結：[資訊]

== esl_check 報告 (2026-09-28 08:55)（--flag --apply）==
[資訊] Synthesis.esp：full，HEDR 1.71，前置 47 個；記錄 15392 筆（新增 0、覆寫 15392）；覆寫類型：CELL 7675, LAND 7675, WRLD 42；ESL：可以直接加 ESL 旗標
[通過] 加 ESL 旗標：Synthesis.esp 已是輕量插件
總結：[通過]

== build_instance-sync-order 報告 (2026-09-28 09:01)（PGPatcher 後 --restore-states --apply）==
[資訊] 模式：實際執行
[通過] 啟用狀態：依目標啟用 8 個、停用 0 個；檔案不在已啟用的 mod 或遊戲資料夾裡，略過 36 個（之後要再跑 prune_dependents）
[通過] 插件順序：4506 個：依目標順序 4197，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 135 個插件到它的前置之後，例如：…
[資訊] 啟用重建出來的輸出插件：PGPatcher.esp, PG_1.esp
[資訊] 不在目標清單中的插件：…
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-090143
總結：[通過]

== prune_dependents 報告 (2026-09-28 09:02)（--disable-folders --apply；試跑相同）==
[資訊] 模式：實際執行
[注意] 要停用的插件：8 個，例如：TSOSRefinedCreationClub.esp, Lux Orbis - Embershard patch.esp, Lux - Embershard patch.esp, Northern Roads - Alternate Perspective Patch.esp, Nolvus Awake…
[資訊] 建議停用的資料夾：0 個
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-090202
總結：[注意]

== build_instance-sync-order 報告 (2026-09-28 09:37)（DynDOLOD 後 --apply；試跑相同）==
[資訊] 模式：實際執行
[通過] 插件順序：4509 個：依目標順序 4200，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 136 個插件到它的前置之後，例如：Natural Waterfalls - Blackreach.esp, Natural Waterfalls - Dawnguard.esp, Natural Waterfalls - Dragonborn.esp, DynDOLOD.esm, Occ_Skyrim_Lux_Via.esp, …
[資訊] 啟用重建出來的輸出插件：DynDOLOD.esm, DynDOLOD.esp, Occlusion.esp
[資訊] 不在目標清單中的插件：…
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260928-093800
總結：[通過]

== check_plugins 報告 (2026-09-28 09:38)（DynDOLOD 後；Synthesis、PGPatcher 後那兩次是完整 251、輕量 4012，其餘各行相同）==
[通過] 完整插件數（含本體）：253 / 254
[通過] 輕量插件數（ESL）：4013 / 4096
[通過] 缺少前置的插件：0 個
[通過] 前置順序錯誤：0 個
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 921 個；BEES 已安裝；遊戲 1.5.97.0
總結：[通過]

== audit_skse 報告 (2026-09-28 09:38) ==
[資訊] 生效的 SKSE DLL：多版本 NG（可用）=133, 非 SKSE 外掛（相依函式庫）=1, SE 版（可用）=81
[通過] 需替換的 DLL：無
[通過] STOCK GAME 遊戲版本：1.5.97.0（需要 1.5.97.0）
[通過] SKSE 1.5.97：skse64_loader.exe + skse64_1_5_97.dll
[通過] Address Library（version-1-5-97-0.bin）：已找到
[通過] 遊戲根目錄的 ENB/ReShade 殘留：無
[通過] Community Shaders：已安裝（Community Shaders）
[資訊] 含 Root 資料夾的 mod（Root Builder 會部署到遊戲資料夾）：無
總結：[通過]
```
- `[注意]` 的說明：prune 的 8 個都在已接受的 26 個裡。

## 本輪手動處理（只搬移或新增，沒有刪除）
- 搬到 `_replaced`：
  - 舊 Synthesis.esp：`synthesis-20260928-085100`。
  - 舊 PGPatcher 輸出：`pgpatcher-output-20260928-085523`。
- modlist 暫時停用、再啟用 `pgpatcher_output`、`texgenCS`，都有備份。
- MO2 的 SSEEdit 參數：暫時加 `-D:`／`-P:`，已改回空白（備份 `ModOrganizer.ini.bak-20260928-094724`、`-100746`）。
- 新增 xEdit 腳本 `D:\PM\tools\SSEEdit 4.1.5\Edit Scripts\Pages - Check listed plugins.pas`（唯讀用，可以留著）。
- 測試主選單和第一次用 CS 啟動時，到主選單就結束遊戲，沒有存檔。

## 本地提交（尚未推送）
- 本回報、status、`data/analysis/override_mismatch.csv`（只剩表頭）、`data/analysis/xedit_check_summary.csv`（插件名稱、錯誤數與種類，沒有個資）。
