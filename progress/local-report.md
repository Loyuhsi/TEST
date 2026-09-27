# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：5 重建輸出（前半，照 cloud-notes 4a9f006「接下來的順序」1–9）
- 日期：2026-09-27
- 結論：
  - **Dibella**：已放入。
  - **prune**：這次要停用 9 個，全都在上一輪那 27 個之內，沒有新名字。
  - **check_plugins**：全部通過。
    - 修剪後：完整插件 252。
    - 加完 FNIS 旗標後：完整插件 251，預估 253／254。
  - **verify**：缺 42 個，和預期相同。
  - **主選單：以目前的清單，遊戲會卡在載入畫面，進不了主選單。**
    - 原因：Nolvus 的 2 個 LOTD NPC 補丁是為 LOTD 5.6.5 做的，D:\PM 用的是 LOTD V6 6.10.2。
    - 暫時停用這 2 個補丁和依賴它們的 1 個插件後，就能進主選單。
    - plugins.txt 已還原成原狀，等雲端決定。見「需要雲端決定」第 1 點。
  - **另外修好 2 個會擋住開遊戲的問題**：
    - Knockback 的 DLL 是 AE 版。
    - 第 4 階段漏裝了 Community Shaders（docs/04 第 7 節）。
  - **Pandora**：輸出 41 個檔。第一次執行時 `-o` 沒有作用，輸出寫進了 Steam 的遊戲資料夾；已清掉並修正設定後重跑。`FNIS.esp` 已加上 ESL 旗標。
  - **BodySlide**：完成，`BodySlide (Nude)` 有 5,825 個 nif。
    - M&V 的 Settings Hub 自帶一份 `Config.xml`，會蓋掉 BodySlide 自己那份，路徑是錯的。已照 docs/05 的原則用 `Pages - 設定覆寫` 修正。
    - 第 1 次建置沒選到 Preset，已重建。
    - 483 組衝突：使用者選擇照 Nolvus 預先建好的輸出推回的選擇，規則判斷不了的保留預設。
    - 兩邊都有的 5,450 個檔中，5,430 個的幾何資料和 Nolvus 完全相同，包括女性身體、手、腳、男性身體。其餘 20 個（10 組）來源檔相同，但 Nolvus 的頂點數或位置不同，原因未查明，見 BodySlide 一節。
    - 和 docs 規則不同之處（手用 Hands Redone 等）與 **Nolvus 其實有建 morphs** 這兩點，見「需要雲端決定」。

## 照 cloud-notes 的步驟
1. `git pull --rebase`、`python -m pytest -q`：175 項通過、1 項略過。
2. Dibella：
   - 放入 `JK's Interiors Patch Collection\JKs Temple of Dibella - Solitude and Temple Frescoes patch.esp`：
     - 來源是 706051 的 ESL No Lanterns 版。
     - 2,323 bytes，有 ESL 旗標，單一連結。
     - 沒有覆蓋任何檔案。
   - `sync-order --restore-states --apply`：啟用 10 個。
   - `prune_dependents` 試跑：9 個，全部在上一輪的 27 個之內（逐一比對 `prune-plan.csv`）。
   - `--disable-folders --apply` → `check_plugins` 全部通過（完整 252）→ `verify` 缺 42。
3. 開到主選單：經過兩個修正和一個診斷才到得了，細節見下一節。
4. 收集資料：
   - `Synthesis.esp`：在 Nolvus 的 `Synthesis Patch - NOSREX`。
   - `SnozzResources.esp`：在 D:\MV 的 `Snozz's Resource Pack`。
   - `AI Overhaul - USSEP Patch.esp`：在 D:\MV 的 `AI Overhaul SSE`。
   - 三個都跑了 `esl_check --plugin`，另外跑了 `--scan`（報告見下方）。
5. `unshare_links`：
   - BodySlide：10 個檔換成獨立副本。
   - `D:\PM\tools`：926 個檔換成獨立副本。
6. Pandora：見「Pandora」一節。
   - 之後跑 `sync-order --apply` → `check_plugins`。
   - `FNIS.esp` 是完整插件，所以跑 `esl_check --flag` 試跑 → `--apply` → 再跑 `check_plugins`，全部通過。
7. BodySlide：見「BodySlide」一節。

## 主選單
### (a) 第一次啟動：Knockback DLL 讓遊戲結束
- 現象：跳出錯誤視窗，內容是 `KnockbackPlugin.dll` 的「REL/Relocation.h(1115): failed to open address library file」，按掉後遊戲結束。
- 原因：`Knockback SKSE (For BFCO and MCO Users)` 裡的 DLL 是 **AE 版**：
  - 檔案 718570，5,931,008 bytes。
  - 它找的是 AE 的 address library。
  - `audit_skse` 把它判成「多版本 NG（可用）」，沒有抓出來。
- 處理：
  - 下載 SE 版（718571），用 `install_archives` 重裝。舊內容在 `_replaced`。
  - 新舊檔案組合相同，都有 `knockbackMCM.esp`，只有 DLL 不同（新的是 5,934,592 bytes）。

### (b) 第二次啟動：卡在背景畫面（CPU 一直忙）
- 現象：
  - SKSE 顯示 init complete，外掛都處理完了。
  - 但畫面一直停在龍的背景圖，沒有選單，等了約 9 分鐘。
- 先發現 **docs/04 第 7 節的官方 Community Shaders 在第 4 階段漏裝了**（我的疏失），補裝 4 個：

  | mod | 版本 | 檔案編號 |
  |---|---|---|
  | Community Shaders | 1.9.1 | 810029 |
  | CS - Skylighting | 1.5.2 | 809752 |
  | CS - Upscaling | 1.4.0 | 758189 |
  | CS - Grass Optimizations | 1.0.0 | 809750 |

  - 下載用 `nexus_fetch`，安裝用 `install_archives`。
  - Community Shaders 壓縮檔裡有工具不認得的 `ParticleLights`、`Renderdoc` 兩個資料夾。確認都是 CS 官方檔案後，用 `--accept` 放行。
  - modlist 放在 `dyndolodCS2` 上方。備份在 `_backup\20260927-114848-before-cs`。
  - 裝好後重開：CS 編譯著色器約 3 分鐘，**仍然卡住**。
- 診斷方法：
  - 取樣最忙那條執行緒的暫存器。
  - 它一直在格式化「`NPC_ Form '' (1134D536)`」這個字串。
  - `0x11` 是 LegacyoftheDragonborn.esm，所以是 LOTD 的 NPC `34D536`。
- 這個 NPC 被 3 個插件覆寫：
  - LegacyoftheDragonborn.esm
  - Modpocalypse NPCs (v3) Legacy of the Dragonborn.esp
  - LegacyoftheDragonborn - NPC Overhaul.esp（最終生效）
- 後兩者的 PKID 指向 V6 已不存在的 LOTD 記錄：`47C542`、`595CC1`、`595CC0`。

### (c) 根本原因與測試
- **版本不符**：
  - Nolvus 用的是 LOTD **5.6.5**。
  - D:\PM 用的是 M&V 的 **LOTD V6 6.10.2**。
  - 下面兩個補丁都是 Nolvus 為 LOTD 5 做的。
- 對每個插件，數有幾個 NPC 引用了 V6 不存在的 LOTD 記錄：

  | 插件 | NPC 覆寫（其中 LOTD） | 引用 V6 不存在記錄的 NPC | 欄位 | 不存在的目標 |
  |---|---|---|---|---|
  | Modpocalypse NPCs (v3) Legacy of the Dragonborn.esp（56635 v1.0） | 131（131） | 10 | CNTO 6、PKID 6 | 124FCA、47C540–47C543、595CC0、595CC1 |
  | LegacyoftheDragonborn - NPC Overhaul.esp（38178 v1.2.2） | 33（33） | 8 | CNTO 6、PKID 4 | 124FCA、47C540、47C542、595CC0、595CC1 |
  | Nolvus Awakening NPC Patch.esp | 30（20） | 0 | — | — |
  | [xPatch] Modpocalypse NPCs (v3) SSE - LegacyoftheDragonborn.esp | 2（0） | 0 | — | — |

- 測試：
  - 每次只改 plugins.txt 的啟用狀態，測完立刻從備份還原。
  - 判斷依據是 SKSE 送出 DataLoaded（type 8），逾時 300 秒。

  | 停用 | 結果 |
  |---|---|
  | Modpocalypse LOTD＋NPC Overhaul＋Nolvus Awakening NPC Patch | DataLoaded（219 秒） |
  | 只停 NPC Overhaul | 卡住（302 秒逾時） |
  | Modpocalypse LOTD＋Nolvus Awakening NPC Patch（後者以前者為前置） | 卡住（302 秒逾時） |

  - 結論：兩個 LOTD 5 補丁**各自都會**造成卡住。
  - Nolvus Awakening NPC Patch 本身沒有問題，只是它以 Modpocalypse LOTD 為前置。
- 用「停用 3 個」再開一次到主選單：
  - DataLoaded 171 秒，**有到主選單**，然後離開，沒有開新遊戲。
  - 期間出現：
    - OAR 的提示框：很大，確定鈕被擠到畫面最下緣，用 Enter 關掉。
    - NGIO 的草地快取提示：預期中，草地快取還沒產生。
  - 主選單的位置偏下，有一部分被切掉。遊戲是 2560x1600（16:10）無邊框視窗；可能和 16:9 的 UI 設定有關，留到第 7 階段看。
  - 之後 plugins.txt、loadorder.txt 已從備份還原，**3 個仍是啟用**。

### (d) 記錄檔摘要（「停用 3 個」到主選單的那一次）
- `skse64.log`：
  - 檢查 215 個，載入 214 個，含這次補裝的 Community Shaders。
  - 沒載入的只有 `msdia140.dll`，訊息是「does not appear to be an SKSE plugin」。它是相依函式庫，屬正常。
  - 沒有 crash log。
- `BackportedESLSupport.log`：1,940 行。
  - 1 行版本（1.2）。
  - 1,939 行「Emulated old header version for …」，12:36:21–12:36:23，涵蓋 1,025 個不同的插件。
  - 沒有警告或錯誤。
- `OpenAnimationReplacer.log`：錯誤 533 行、警告 13 行。
  - 287 行「Missing required plugin Open Animation Replacer - RaySense version 1.0.0.0!」。
  - `RaySense - Cover Animation` 的多個 `config.json`「Failed to parse condition」。
  - 5 行「RequestPluginAPI_Conditions requested the wrong interface version」。
  - 推測原因是版本不合：
    - D:\PM 的 OAR 是 Nolvus 的 **2.3.6**（Open Animation Replacer4）。
    - RaySense 的 OAR 外掛（Open Animation Replacer - RaySense3，175498 v1.1.0.0）來自 M&V，M&V 用的是 OAR **3.2.0**。
  - 目前 RaySense 的 OAR 條件都不會生效。受影響的是 Cover Animation、Edge Lookdown、Jumping over obstacles、Wall Leaning。

## Pandora
- **第一次執行（失敗）**：
  - Pandora 4.3.1-beta 沒有採用 `-o` 引數。
  - 它讀寫的是自己 `Settings.json` 裡的路徑（`%LOCALAPPDATA%\Pandora Behaviour Engine\Settings.json`），而這個路徑指向 Steam 的遊戲資料夾。
  - 結果只看到 1 個 mod，並把 9 個檔寫進 Steam 的 `Data`。
  - 處理：
    - 這 9 個檔先複製到 `D:\PM\_replaced\SteamData-Pandora-20260927-125332`。
    - 使用者同意後自己刪除 Steam 裡的原檔。已確認 Steam `Data` 沒有殘留。
- **修正**：
  - `Settings.json` 改成：
    - `gameDataPath`：`D:\PM\STOCK GAME\Data`
    - `outputPath`：`D:\PM\mods\Pandora Output`
    - 舊檔另存為 `.bak-*`。
  - MO2 的 Pandora 執行檔：工作目錄改成 `D:/PM/STOCK GAME/Data`。
  - 另外，`build_instance` 沒有把 Pandora 加進 MO2 的執行檔清單（docs/05 說有），我手動加了第 13 項。`ModOrganizer.ini` 有備份。
- **第二次執行**：Pandora 的視窗不能由我操作，由使用者按開始。
  - `Pandora Output` **41 個檔**：
    - `meshes` 37 個
    - `Pandora_Engine` 2 個
    - `SKSE` 1 個
    - `Engine.log` 1 個
  - `Engine.log`：218 行，其中 ERROR 2 行、WARN 149 行。`ActiveMods.json` 有 34 項。
    - 2 個 ERROR 都來自 Precision Creatures：`colisc\draugrbehavior\#0115.txt`、`#0119.txt` 解析失敗（「The 'hkobject' start tag … does not match the end tag of 'hkparam'」）。
- **`FNIS.esp`**：
  - 不在 `Pandora Output`，而是 `Pandora Behaviour Engine v4.3.1-beta` 資料夾本身附的空插件（131 bytes，0 筆記錄，單一連結）。
  - 它原本就啟用、是完整插件。
  - 加 ESL 旗標後：完整 252 → 251，預估 254 → 253。

## BodySlide
- **問題**：從 MO2 開 BodySlide 時跳出「No read/write permission for game data path!」。
- **原因**：
  - M&V 的 `Mages & Vikings - Settings Hub`（modlist 第 73 行，優先順序高）自帶 `CalienteTools\BodySlide\Config.xml`。
  - 在 MO2 的虛擬資料夾裡，它蓋掉了 `BodySlide and Outfit Studio` 自己那份（已經換成獨立副本、路徑已改的那份）。
  - 它的路徑是 `D:\Mages & Vikings\Stock Game\data\` 和 `D:\Mages & Vikings\overwrite\`，這台電腦都沒有。
  - BodySlide 5.6.0 啟動時會檢查輸出路徑能不能讀寫（對照原始碼 `BodySlideApp::OnInit`）。
  - 清單是空的，是因為警告視窗擋在載入清單之前。
- **手冊缺口**：
  - 照 docs/05 第 2 節第 3 步在 Settings 按 OK，BodySlide 會把設定寫回 Settings Hub 那份。
  - 那份和 D:\MV 是硬連結，所以會直接改到 D:\MV 的原檔。
  - 這次沒有按：已確認那份的修改時間仍是 2026-09-26、內容沒變。
- **修正**：照 docs/05「共通原則」。
  - 建立 `Pages - 設定覆寫` mod，放在 modlist.txt 第一行，也就是最高優先。modlist 備份在 `_backup\20260927-132407-before-override`。
  - 在裡面放 `CalienteTools\BodySlide\Config.xml`，內容是 BodySlide 自己那份的副本，路徑已改好：
    - `GameDataPath`：`D:\PM\STOCK GAME\Data\`
    - `OutputDataPath`：`D:\PM\mods\BodySlide (Nude)\`
  - 重開後不再有警告。
  - 關閉 BodySlide 時只會寫 `BodySlide.xml`。只有 BodySlide 自己的資料夾有這個檔，而且是獨立副本。
- **Batch Build**：由使用者操作，BodySlide 的視窗不能由我操作。我從 `Log_BS.txt`、`BuildSelection.xml` 和輸出檔核對，一共建了 5 次。
  - **第 1 次（13:44）不能用，輸出已搬走**：
    - 記錄裡沒有任何「Activating set」或「Applying preset」，所以 Outfit 停在清單第一個（Cold Foreigner F - Dress），Preset 是空的。
    - 批次建置用的是 `SelectedPreset`，空白時每個滑桿都取預設值，做出來的是基本體型，不是 CBBE Curvy (Outfit)。
    - 「Choose output set」有 483 組，大多保留預設：女性身體是一般的 `CBBE Body`，手、腳是 CBBE 版，還有 13 組是 BHUNP。
    - 另有 1 組因為平行建立資料夾衝突而失敗。
    - 5,823 個檔已搬到 `D:\PM\_replaced\BodySlide (Nude)-20260927-141101-empty-preset`，沒有刪除。
  - **選擇的來源**：
    - 用腳本照 BodySlide 5.6.0 的做法（`LoadSliderSets`，輸出路徑不分大小寫）重建 483 組的候選。算出的 2,929 個輸出組和 BodySlide 處理的數量一致。
    - 先照 docs/05 第 2 節的規則判斷。
    - 再比對 Nolvus 實例預先建好的 `BodySlide (Nude)`（6.0.18：5,516 個 nif、2,775 個 tri），用輸出檔的區塊結構推回 Nolvus 每組選了誰。
    - 規則和 Nolvus 不一致，**使用者選擇「照 Nolvus 實際選擇」**。
    - 最終：Nolvus 100 組、docs 規則 360 組、保留預設 23 組。
    - 寫進 `BuildSelection.xml`（BodySlide 自己資料夾的獨立副本，每次都有 `.bak-*` 備份）。BodySlide 開 Batch Build 清單時，會依這個檔先取消各組落選的候選，所以不會再跳出「Choose output set」。
    - 逐組的表：`data/analysis/bodyslide_choices.csv`，含最終選擇、來源、第 1 次的選擇、規則、Nolvus 比對結果與候選。
  - **第 2 次（14:16）**：483 組都照表套用，但 Preset 還是空的。
  - **第 3 次（14:43）**：
    - 記錄有「Applying preset 'CBBE Curvy (Outfit)'」，5,825 個檔全部更新，「All sets processed successfully!」。
    - 逐檔和 Nolvus 比對後，發現還有 3 組不一致，修正後再建：第一人稱的手 ×2（改用 Hands Redone），以及 Miraak 靴子（改用 Frankly HD）。
  - **第 4、5 次（14:51、15:04）**：
    - 第 4 次套用那 3 組，「All sets processed successfully!」。
    - 第 5 次再把長老議會護身符改用替換版（Elder Council Amulet Replacer [2K]）。這一版是用檔頭比對確認的：Nolvus 的輸出是替換版的 41 個區塊加 BODYTRI，原版只有 11 個區塊。
    - 兩次都更新了 5,825 個檔，沒有失敗記錄。
- **結果**（第 5 次）：
  - `BodySlide (Nude)`：**5,825 個 nif**，約 4.2 GB。Overwrite 沒有 `meshes`。沒有勾 Build Morphs（照 docs）。
  - 和 Nolvus 逐檔比對幾何資料：
    - 比法：`NiSkinPartition` 逐位元組比對；`BSTriShape` 跳過區塊參照，比頂點與三角形資料。
    - **兩邊都有的 5,450 個檔中，5,430 個完全相同。**
    - 女性身體（_0、_1）、手、腳、男性身體都和 Nolvus 逐位元組相同。唯一差別是 Nolvus 的身體檔多一個 BODYTRI 參照，那是它勾了 Build Morphs 的結果。
    - Nolvus 沒有的：375 個，是 Pages 才有的服裝。
    - 仍不同的 20 個檔（10 組），**原因未查明**：
      - `Twilight Princess Armor Mashup2` 8 組 16 個檔：
        - 兩邊的 BodySlide 檔（38 個）逐位元組相同，也沒有被其他 mod 蓋掉。
        - 但 Nolvus 的輸出有部分形狀的頂點位置不同，胸甲裡的身體形狀頂點數也不同（Nolvus 多）。
        - 看起來是滑桿或 zap 值不同，例如 Nolvus 對這套用了它自帶的「Twilight Princess Preset 3BA」。
      - 原版黑暗兄弟會路徑的 `dbarmortorso_f`、`dbarmorboots_f` 2 組 4 個檔：
        - 兩邊的候選相同：3BA Vanilla、CBBE Vanilla、CBBE Vanilla Physics。
        - 但 Nolvus 的輸出結構差很多（胸甲 274 KB 對我們的 1.45 MB），和任何一個候選都對不上。
        - 可能也是 zap 值不同。
        - 盔甲的紀錄應該是指向 4thUnknown 的新路徑，這條原版路徑的網格可能用不到。
      - 這 10 組影響的只是兩套服裝的外觀，不影響載入。需要的話下一輪再查。
- **和 docs/05 規則不同、改照 Nolvus 的地方**（請雲端確認）：
  1. 手與手套 47 組，包含第一人稱：Nolvus 一律用 Female Hands Redone（`Hands Redone F …`）；docs 規則會選 `CBBE 3BBB Hands`／`CBBE Vanilla - Hands …`。Female Hands Redone（含 3BA 附加包）在目標清單裡。
  2. 男性身體：`HIMBO Body - SOS High Poly Phys CBPC`。Nolvus 的檔頭沒有「HDT Skinned Mesh Physics Object」字串，所以是 CBPC 版不是 SMP 版。docs 規則在 16 個 HIMBO 變體中判斷不了，視窗預設是 `HDT Collision Resource`。
  3. 男性內褲選 Briefs。
  4. 夜鶯盔甲身體用 `AltairNightingaleHDTCapeArmor`（披風替換版）；照規則會選 3BA Vanilla，蓋掉替換版。
  5. Chevalier 胸甲 4 組（No Physics）、Soul Hunter Cloak（NO-SMP）：規則判斷不了，保留預設，和 Nolvus 相同。原本我想用「物理版優先」類推，Nolvus 的選擇正好相反，所以沒有用。
  6. 長老議會護身符用替換版；Miraak 靴子用 Frankly HD 版。
- **保留預設的 23 組**（規則判斷不了）：
  - 16 組的幾何資料和 Nolvus 相同。
  - 7 組是 Nolvus 沒有的服裝，需要雲端判斷：
    - #43 `[Dint999] SecretChildofTalos Dress`：只有 TBD 身體版，沒有 3BA／CBBE 版。
    - #50、#52、#54 Aokili Shattered Royal Armor：Miniskirt 有物理／No Physics、Necklace 一般／Transparent、Sabatons 一般／Flat；都選了一般版。
    - #161 Cumulative Boots：選了 Non Heels（另一個是有跟）。
    - #197、#441 Cumulative Vest：選了無物理版（另一個是 Physics）。

## 工具結果（照抄 reports\*.txt 的每一行）
```
== build_instance-sync-order 報告 (2026-09-27 11:29)（--restore-states --apply）==
[資訊] 模式：實際執行
[通過] 啟用狀態：依目標啟用 10 個、停用 0 個；檔案不在已啟用的 mod 或遊戲資料夾裡，略過 40 個（之後要再跑 prune_dependents）
[通過] 插件順序：4502 個：依目標順序 4193，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 135 個插件到它的前置之後，例如：Natural Waterfalls - Blackreach.esp, Natural Waterfalls - Dawnguard.esp, Natural Waterfalls - Dragonborn.esp, Occ_Skyrim_Lux_Via.esp, Rainbows over Waterfalls - Bruma addon.esp, Rainbows over Waterfalls - Natural Waterfalls patch.esp, Complementary Grass Fixes - CRF Patch.esp, Additional Dremora Faces - VIGILANT Patch.esp, Skyshards - TGC Winterhold Patch.esp, FDE Aela Part 2.esp
[資訊] 不在目標清單中的插件：JKs College of Winterhold - 4thUnknowns Scamps patch.esp, Nolvus Awakening Follower Patch.esp, JKs Solitude Outskirts - Mihail Haystacks patch.esp, DBVO Fix - AYOP Dawnguard.esp, Lux - JK's Eek Bannered Mare patch.esp, Lux Orbis - JK's Riverfall Cottage patch.esp, JK's Temple of the Divines.esp, DBVO Fix - The Gray Cowl Returns.esp, Gorgeous Giant Camps Compilation - Mihail Giant Club Variety patch.esp, Lux - Granite Hill.esp, JKs Dark Brotherhood Sanctuary - Destroy the Dark Brotherhood Quest Expasnion patch.esp, COTN Falkreath - TGR Patch.esp, TGC Winterhold - Mihail House Cats patch.esp, Nature of the Wild Lands - Wizkid Hunters Camp Overhaul.esp, DBVO Fix - Dawnguard DLC.esp
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-112909
總結：[通過]

== prune_dependents 報告 (2026-09-27 11:29)（試跑）==
[資訊] 模式：試跑（加 --apply 才會寫入）
[注意] 要停用的插件：9 個，例如：TSOSRefinedCreationClub.esp, Grand Solitude - AI Overhaul patch.esp, Lux Orbis - Embershard patch.esp, Lux - Embershard patch.esp, Northern Roads - Alternate Perspective Patch.esp, Nolvus Awakening Combat Scaling Overhaul - Boss.esp, Nolvus Awakening Combat Scaling Overhaul - Consistency Patch.esp, Orc Exiles - Bilegulch - Ryn's Lost Valley Redoubt patch.esp
[資訊] 建議停用的資料夾：0 個
總結：[注意]
（第 9 個是 Nolvus Awakening Combat Scaling Overhaul - Enemy Level Mult.esp；9 個全在上一輪的 27 個之內）

== prune_dependents 報告 (2026-09-27 11:29)（--disable-folders --apply）==
[資訊] 模式：實際執行
[注意] 要停用的插件：9 個，例如：（同上）
[資訊] 建議停用的資料夾：0 個
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-112921
總結：[注意]

== check_plugins 報告 (2026-09-27 11:29)（修剪後）==
[通過] 完整插件數（含本體）：252 / 254
[通過] 輸出重建後的完整插件（預估）：254 / 254：DynDOLOD.esm, DynDOLOD.esp 一定是完整插件；Synthesis.esp、FNIS.esp、Occlusion.esp、PG_* 必須是輕量插件
[通過] 輕量插件數（ESL）：4012 / 4096
[通過] 缺少前置的插件：0 個
[通過] 前置順序錯誤：0 個
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 914 個；BEES 已安裝；遊戲 1.5.97.0
總結：[通過]

== build_instance-verify 報告 (2026-09-27 11:29) ==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[注意] plugins.txt 與預期比對：缺少 42 個（mod 尚未安裝或已被修剪）；待重建輸出 7 個；例如：Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, Anchor Animations Spell V2.esp, FH_Grapple.esp, AnchorShdSwd.esp, SC_HorseReplacer.esp
總結：[注意]

== nexus_fetch 報告 (2026-09-27 11:34)（Knockback SE 718571）==
[通過] 本次下載：1 個
總結：[通過]

== install_archives 報告（--only "Knockback SKSE (For BFCO and MCO Users)" --apply）==
[資訊] 執行：判斷了 1 個下載
[資訊] 磁碟空間：預計解壓 5.7 MB，D:\ 剩 266.8 GB
[通過] 已重裝（舊資料夾在 _replaced）：1 個
總結：[通過]

== nexus_fetch 報告 (2026-09-27 11:48)（Community Shaders 等 4 個）==
[通過] 本次下載：4 個
總結：[通過]

== install_archives 報告 (2026-09-27 11:49)（--accept "Community Shaders" --apply）==
[資訊] 執行：判斷了 4 個下載
[資訊] 磁碟空間：預計解壓 268.2 MB，D:\ 剩 266.5 GB
[通過] 已安裝：4 個
總結：[通過]

== audit_skse 報告 (2026-09-27 11:49)（補裝 CS 後）==
[資訊] 生效的 SKSE DLL：多版本 NG（可用）=133, 非 SKSE 外掛（相依函式庫）=1, SE 版（可用）=81
[通過] 需替換的 DLL：無
[通過] STOCK GAME 遊戲版本：1.5.97.0（需要 1.5.97.0）
[通過] SKSE 1.5.97：skse64_loader.exe + skse64_1_5_97.dll
[通過] Address Library（version-1-5-97-0.bin）：已找到
[通過] 遊戲根目錄的 ENB/ReShade 殘留：無（Community Shaders 可正常運作）
[資訊] 含 Root 資料夾的 mod（Root Builder 會部署到遊戲資料夾）：無
總結：[通過]

== esl_check 報告 (2026-09-27 12:41)（--plugin Nolvus: Synthesis Patch - NOSREX\Synthesis.esp）==
[資訊] Synthesis.esp：light，HEDR 1.71，前置 55 個；記錄 15368 筆（新增 0、覆寫 15368）；覆寫類型：CELL 7664, LAND 7664, WRLD 40；ESL：已經是輕量插件
總結：[資訊]

== esl_check 報告 (2026-09-27 12:41)（--plugin D:\MV: Snozz's Resource Pack\SnozzResources.esp）==
[資訊] SnozzResources.esp：master，HEDR 1.71，前置 5 個；記錄 260 筆（新增 253、覆寫 7）；覆寫類型：STAT 4, LVLI 3；新增類型：STAT 174, LVLI 19, NPC_ 18, FLOR 12, WEAP 9, ACTI 7, CONT 4, ARMO 3, TXST 3, OTFT 2, FURN 1, MSTT 1；ESL：253 筆新增記錄的編號超出 0x000–0xFFF（需要壓縮 FormID）
總結：[資訊]

== esl_check 報告 (2026-09-27 12:41)（--plugin D:\MV: AI Overhaul SSE\AI Overhaul - USSEP Patch.esp）==
[資訊] AI Overhaul - USSEP Patch.esp：light，HEDR 1.71，前置 4 個；記錄 29 筆（新增 2、覆寫 27）；覆寫類型：NPC_ 11, PACK 8, REFR 4, CELL 2, QUST 1, WRLD 1；新增類型：PACK 2；ESL：已經是輕量插件
總結：[資訊]

== esl_check 報告 (2026-09-27 12:41)（--scan --pm "D:/PM"）==
[資訊] 已啟用的完整插件（不含本體與 CC）：237 個
[資訊] 可以直接加 ESL 旗標：22 個，其中沒有新增 CELL 的 20 個，例如：SkyUI_SE.esp, RaceMenu.esp, RaceMenuPlugin.esp, KSWigsSMP.esp, XPMSE.esp, SPERG - ZIA Patch.esp, DEST_ISL.esp, RUSTIC SOULGEMS - Unsorted.esp, RimExecutionHitSA.esp, timescale10.esp
[資訊] 說明：這只是騰出名額的候選清單，不要自行加旗標；需要時由雲端決定
總結：[資訊]

== unshare_links 報告 (2026-09-27 12:41)（BodySlide，試跑）==
[資訊] 模式：試跑（加 --apply 才會寫入）
[資訊] BodySlide：硬連結的設定檔 10 個
總結：[資訊]

== unshare_links 報告 (2026-09-27 12:41)（BodySlide，--apply）==
[資訊] 模式：實際執行
[通過] BodySlide：硬連結的設定檔 10 個，已換成獨立副本 10 個
總結：[通過]

== unshare_links 報告 (2026-09-27 12:41)（D:\PM\tools，試跑）==
[資訊] 模式：試跑（加 --apply 才會寫入）
[資訊] tools：硬連結的設定檔 926 個
總結：[資訊]

== unshare_links 報告 (2026-09-27 12:41)（D:\PM\tools，--apply）==
[資訊] 模式：實際執行
[通過] tools：硬連結的設定檔 926 個，已換成獨立副本 926 個
總結：[通過]

== build_instance-sync-order 報告 (2026-09-27 13:00)（Pandora 後，--apply）==
[資訊] 模式：實際執行
[通過] 插件順序：4502 個：依目標順序 4193，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 135 個插件到它的前置之後，例如：（同 11:29）
[資訊] 不在目標清單中的插件：（同 11:29 的 15 個）
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-130052
總結：[通過]

== esl_check 報告 (2026-09-27 13:01)（--plugin "…\Pandora Behaviour Engine v4.3.1-beta\FNIS.esp" --flag）==
[資訊] FNIS.esp：full，HEDR 1.70，前置 0 個；記錄 0 筆（新增 0、覆寫 0）；覆寫類型：無；ESL：可以直接加 ESL 旗標
[資訊] 加 ESL 旗標（試跑）：可以
總結：[資訊]

== esl_check 報告 (2026-09-27 13:01)（同上，--flag --apply）==
[資訊] FNIS.esp：full，HEDR 1.70，前置 0 個；記錄 0 筆（新增 0、覆寫 0）；覆寫類型：無；ESL：可以直接加 ESL 旗標
[通過] 加 ESL 旗標：FNIS.esp 已是輕量插件
總結：[通過]

== check_plugins 報告 (2026-09-27 13:01)（FNIS 加旗標後）==
[通過] 完整插件數（含本體）：251 / 254
[通過] 輸出重建後的完整插件（預估）：253 / 254：DynDOLOD.esm, DynDOLOD.esp 一定是完整插件；Synthesis.esp、FNIS.esp、Occlusion.esp、PG_* 必須是輕量插件
[通過] 輕量插件數（ESL）：4013 / 4096
[通過] 缺少前置的插件：0 個
[通過] 前置順序錯誤：0 個
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 914 個；BEES 已安裝；遊戲 1.5.97.0
總結：[通過]
```
BodySlide 完成後再跑一次（唯讀）：
```
== build_instance-verify 報告 (2026-09-27 15:07) ==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[注意] plugins.txt 與預期比對：缺少 33 個（mod 尚未安裝或已被修剪）；待重建輸出 7 個；例如：Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, Anchor Animations Spell V2.esp, FH_Grapple.esp, AnchorShdSwd.esp, SC_HorseReplacer.esp
總結：[注意]

== check_plugins 報告 (2026-09-27 15:07) ==
[通過] 完整插件數（含本體）：251 / 254
[通過] 輸出重建後的完整插件（預估）：253 / 254：DynDOLOD.esm, DynDOLOD.esp 一定是完整插件；Synthesis.esp、FNIS.esp、Occlusion.esp、PG_* 必須是輕量插件
[通過] 輕量插件數（ESL）：4013 / 4096
[通過] 缺少前置的插件：0 個
[通過] 前置順序錯誤：0 個
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 914 個；BEES 已安裝；遊戲 1.5.97.0
總結：[通過]
```
- `[注意]` 的說明：
  - prune 的 9 個都是上一輪已經接受的。
  - verify 在 11:29 缺 42 個，是預期的：15 個捨棄或接受缺少，加上修剪的 27 個。
  - 15:07 變成 33 個，只是計算方式的關係，見「工具／手冊缺口」第 5 點。

## 需要雲端決定
1. **LOTD 的 NPC 補丁（會讓遊戲卡在載入）**。現在 3 個都還是啟用，所以目前的清單進不了主選單。
   - **NPC Overhaul**：
     - Nexus 上有 **v2（檔案 514540，MAIN，2024-06-24，說明「Updated for Legacy v6」）**。
     - D:\PM 的是 v1.2.2（181699，已是 OLD_VERSION），來自 Nolvus。
     - 建議用 decisions.csv 的 reinstall 換成 514540。
   - **Modpocalypse NPCs - LOTD（56635）**：
     - Nexus 只有 v1.0（2021），沒有 V6 版。
     - 目標清單裡有 `ModpocalypseNPCs-LotDV6-ErrorFixes.esp`，看名稱應該是原作者修這個問題的補丁。但它在 verify 缺少的 42 個裡，而且找不到來源。
     - 可選：
       - (a) 停用 Modpocalypse LOTD 與 Nolvus Awakening NPC Patch（已測試可進主選單）。代價是 LOTD 的 131 個 NPC 外觀，以及 Nolvus 對 30 個 NPC 的整合覆寫。
       - (b) 另做一個 ESL 修正補丁：只覆寫那 10 個 NPC，拿掉不存在的 PKID／CNTO。這會用到 1 個輕量名額（目前 4013／4096），也不改原檔。
     - 請決定。
2. **OAR 與 RaySense 版本不合**（533 行錯誤）：
   - 可選：
     - 把 OAR 換成 3.x。M&V 用 3.2.0，Nexus 最新是 3.2.1（798222）。repo 的 PE 讀取器判定 M&V 的 3.2.0 DLL 是「多版本」，但 Knockback 的例子顯示這個判定可能不準，是否支援 1.5.97 要再確認。
     - 或停用 RaySense 的 OAR 外掛與相關動畫。
   - 請決定。
3. **恢復項目**（第 4 階段第 2 點）：
   - `AI Overhaul - USSEP Patch.esp` 已經是輕量插件。
     - 它的前置 USSEP、`AI Overhaul.esp` 在 D:\PM 都已啟用。
     - 加回 `AI Overhaul SSE` 的這個插件，就能恢復 `Grand Solitude - AI Overhaul patch.esp`，而且不佔完整名額。
   - `SnozzResources.esp` 是 ESM 旗標的完整插件，只以本體為前置，有 253 筆新增記錄，編號超出輕量範圍。
     - 要壓縮 FormID 才能改成輕量。
     - 否則恢復 Embershard 會用掉 1 個完整名額，預估變成 254／254，沒有餘裕。
4. **Synthesis 清單**：依上一輪說明，等雲端給。
5. **BodySlide**：
   - (a) **Build Morphs**：Nolvus 的 `BodySlide (Nude)` 有 2,775 個 `.tri`，身體檔裡也有 BODYTRI，表示 Nolvus 有建 morphs。docs/05 寫「Nolvus 也不建 morphs」，和實際不符。
     - 這次照 docs 沒勾。
     - 要改的話，只要勾選後再按一次 Batch Build→Build，約 1 分鐘，選擇都已存在 `BuildSelection.xml`。
   - (b) 手與手套 47 組照 Nolvus 用 Female Hands Redone，而不是 docs 規則的 CBBE／3BBB 版。其餘 5 組照 Nolvus 的見 BodySlide 一節。是否接受？
   - (c) Nolvus 沒有的 7 組保留預設：#43、#50、#52、#54、#161、#197、#441，詳見 BodySlide 一節。要不要改？
   - (d) Twilight Princess 8 組、原版黑暗兄弟會路徑 2 組：和 Nolvus 的頂點不同，原因未查明（可能是 Preset 或 zap）。要不要追查？
6. **主選單偏下被切掉**：2560x1600 的 16:10 螢幕配 16:9 UI 設定的可能性高，是否留到第 7 階段處理？

## 工具／手冊缺口（建議）
1. **`audit_skse`**：
   - 把 AE 版的 `KnockbackPlugin.dll`（718570）判成「多版本 NG（可用）」，實際上會找 AE 的 address library 而讓遊戲結束。建議也檢查 DLL 裡 address library 檔名的字串（`versionlib` 與 `version-1-5-`）。
   - 它也不看 Preloader 載入的 `DLLPlugins` 資料夾。目前只有 SSE Fixes 的 `FPSFixPlugin.dll`（3.1.5.97，1.5.97 版）。
2. **docs/04 第 7 節（Community Shaders）**：
   - 這次在第 4 階段漏做，直到開遊戲才發現。
   - 建議 `audit_skse` 或 `check_plugins` 檢查 `CommunityShaders.dll` 是否存在。現在 audit_skse 的那一行寫「Community Shaders 可正常運作」，容易誤會已經裝好。
3. **docs/05 第 1 節（Pandora）**：
   - 4.3.1-beta 不吃 `-o`，要先改 `%LOCALAPPDATA%\Pandora Behaviour Engine\Settings.json` 的 `gameDataPath`／`outputPath`，否則會寫進 Steam 的遊戲資料夾。
   - `build_instance` 也沒有把 Pandora 加進 MO2 執行檔。
4. **docs/05 第 2 節（BodySlide）**：
   - 第 3 步之前要先建 `Pages - 設定覆寫\CalienteTools\BodySlide\Config.xml`，否則 Settings 的 OK 會改到 D:\MV 的硬連結檔。
   - `unshare_links` 只看工具自己的資料夾，看不到被其他 mod 蓋掉的同名設定檔。建議檢查 VFS 中實際生效的那一份。
5. **`build_instance verify`**（15:07 重跑）：
   - modlist 仍是「一致」。它只檢查預期的資料夾在不在，不會列出清單外新增的 5 個（CS 4 個、`Pages - 設定覆寫`）。需要追蹤的話，建議加一行資訊。
   - plugins.txt 的缺少數從 42 變成 33：
     - 少掉的 9 個正是這輪修剪的那 9 個。
     - 原因：MO2 在 13:23 關閉時，把已啟用 mod 裡的插件都以**停用**狀態寫回 plugins.txt，而 verify 只把「整行不存在」算成缺少。
     - 它們仍是停用，check_plugins 也全部通過。
   - 建議 verify 把「有列出但停用」的目標插件也算進缺少，或另列一行，數字才不會因為 MO2 開關而變動。
6. **docs/05 第 2 節（BodySlide）的其他缺口**：
   - 選 Preset 很容易漏掉，這次第 1、2 次都漏了。建議在手冊加一步確認：Batch Build 前滑桿應已移動。或者由本地代理在 Batch Build 後檢查 `Log_BS.txt` 有沒有「Applying preset 'CBBE Curvy (Outfit)'」。
   - 衝突有 483 組，靠人工逐組照規則選不實際。第 1 次在 39 秒內就按了 OK，大多是預設。
     - 建議把「照 Nolvus 輸出推回選擇、寫入 `BuildSelection.xml`」做成工具，目前是 scratchpad 腳本。
     - BodySlide 會依 `BuildSelection.xml` 在 Batch Build 清單先取消落選項，之後就不會再跳出選擇視窗。
   - 手冊的規則和 Nolvus 的實際做法有出入：手、男性身體變體、替換版盔甲、Build Morphs。

## 本輪手動處理（只新增或搬移，沒有刪除；Steam 裡 Pandora 誤寫的 9 個檔由使用者同意後自己刪除）
- 放入 Dibella 補丁（新檔）。
- 用 SE 版重裝 Knockback（舊內容在 `_replaced`）。
- 補裝 CS 4 個，並插入 modlist（有備份）。
- `ModOrganizer.ini` 新增 Pandora 執行檔（有備份）。
- 改 Pandora 的 `Settings.json`（有備份）。
- `FNIS.esp` 加 ESL 旗標。
- BodySlide 的 `Config.xml`（獨立副本）改路徑（有備份）。
- 建立 `Pages - 設定覆寫`，並插入 modlist（有備份）。
- BodySlide 第 1 次的輸出（5,823 個檔）搬到 `D:\PM\_replaced\BodySlide (Nude)-20260927-141101-empty-preset`，沒有刪除。
- `BuildSelection.xml`（BodySlide 資料夾的獨立副本）寫入 483 組選擇，每次都有 `.bak-*` 備份。
- 新增 `data/analysis/bodyslide_choices.csv`：483 組的選擇表，無個資。
- 主選單測試時，暫時停用 3 個插件，測完都已還原。

## 本地提交（尚未推送）
- 本回報與 status 的提交。
