# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：6 繁中化。照 cloud-notes 129121b「接下來的順序」做完 1–6。**第 7 步（蘇禾的包）使用者還沒下載，先回報。**
  - 不需要蘇禾包的步驟先做了：4.5 MCM 英文備援、第 5 節名詞對照表、Descriptions 下載與比對、第一次 coverage（當作蘇禾包安裝前的基準）。
- 日期：2026-10-10
- 結論：
  - **英文版備份完成**：`EN-baseline-未測試-2026-10-10.7z` 放在 C 槽（D 槽以外）。
    - 內容：4,139 個資料夾、101,344 個檔，25.9 GB，壓縮後 12.9 GB。
    - `7z t` 測試通過。
  - **目標清單、語言、字型都照預期**：
    - 佔位資料夾 18 個：ZH 16 個、`ZH_separator`、`Dynamic String Distributor`。
    - prune 26 個，和已接受的相同。完整 253、輕量 4012。
    - `sLanguage=CHINESE`，「英文語音」`[通過]`。
    - `interface\fontconfig.txt` 由 `ZH Overrides` 勝出。
  - **Nexus 繁中**：manifest 是下載 8、重裝 1，符合預期。
    - 裝了 VIGILANT、Unslaad、Bruma、3DNPC、Wyrmstooth、DBReV 中文、DSD 1.4.3、STPP 1.10。
    - **SIRENROOT 和 Project AHO 沒裝**：翻譯版的記錄數和我們的不同（下面第 3 點）。
  - audit_skse、check_plugins 全過，完整插件仍是 253、輕量 4012。
  - **涵蓋率工具有誤判，AI 翻譯前要先修**（「需要雲端決定」第 1 點）。
    - 現在 VIGILANT、Unslaad 的 Nexus 繁中 DSD 被算成大半對不上。
    - 這些條目會被當成未翻譯送去 AI，而 `ZH - AI 翻譯` 的優先順序比 Nexus 繁中高，人工譯文會被 AI 譯文蓋掉。

## 照 cloud-notes 的步驟
1. `git pull --rebase`（129121b）、`pip install -r requirements-zh.txt`（OpenCC 1.4.2、anthropic 1.13.0）、`python -m pytest -q`：**228 項全過，沒有略過**。
2. **英文版備份**：
   - C 槽空間足夠，放在 `C:\PagesBackup\`。
   - 範圍：
     - `Pages-ZH` 設定檔、`ModOrganizer.ini`。
     - 8 個輸出：Pandora Output、BodySlide (Nude)、SYNTHESSIS、pgpatcher_output、grass CS、lodgen2、texgenCS、dyndolodCS2。
     - `Pages - 設定覆寫`、`Pages - 版本不符修正`、`Pages - LOTD V6 修正`。
   - 7-Zip `-mx=1` 約 3 分鐘；`7z t`：Everything is Ok。
3. **目標清單**：
   - `create --apply`：
     - modlist 4147 行（捨棄 21），佔位 18 個。
     - `ZH - 官方繁中字串` 由停用變成啟用，在 ZH 組最低。
     - modlist 順序：`Pages -` 三個 → `NEWMODS_separator` → `ZH Overrides` … `ZH - 官方繁中字串` → `ZH_separator`。
     - DSD 排在 STPP 下一行。
   - 開 MO2 一次再關：寫回 modlist、plugins。
   - `sync-order --restore-states --apply`：啟用 0、停用 0。
   - `prune_dependents`：
     - 試跑 26 個插件、18 個資料夾。
     - 用 `create` 前的設定檔備份逐一比對：**26 個在上一輪都是修剪狀態**（停用或所在資料夾停用），沒有新名字。
     - 接著 `--disable-folders --apply`。
   - `check_plugins` 全過（完整 253／254、輕量 4012）。
   - `verify`：
     - 清單外的資料夾 84 → 83：`ZH - 官方繁中字串` 已進清單。
     - 缺少或未啟用 41 個（和上一輪相同），待重建 0。
4. **`set-language`**：試跑與 `--apply` 相同。`ENGLISH → CHINESE`，英文語音 `[通過]`。`sResourceArchiveList2` 第一個仍是 `Skyrim - Voices_en0.bsa`。
5. **字型**：
   - 生效中的 fontconfig 來自 Sanguis，只有標準的 16 個名稱，所以「額外名稱 0 個」是正確的。
   - 官方 22 個對應，`fontlib` 合併成 6 個。
   - 勝出確認改用檔案優先順序檢查（沒有開 MO2 介面）。`interface\fontconfig.txt` 有 3 個來源：
     - `ZH Overrides`：優先第 4。
     - Sanguis：第 128。
     - Edge UI：第 134。
     - overwrite 沒有這個檔，所以由 `ZH Overrides` 勝出。
   - ImGui 類 mod 照指示先不改。
6. **DSD、STPP、Nexus 繁中**：
   1. `manifest`：
      - 下載 8 個：DSD 1.4.3、VIGILANT、Unslaad、Bruma、3DNPC、Wyrmstooth、SIRENROOT、DBReV 中文。
      - 重裝 1 個：STPP 1.10。
      - `regenerate` 9 個和以前相同。
   2. `nexus_fetch --apply`：9 個。
   3. **替換插件的翻譯，先解到暫存區用 `esl_check` 比對，比對過才裝**：

      | 插件 | 翻譯版記錄（新增／覆寫） | 我們的 | 前置 | 結果 |
      |---|---|---|---|---|
      | 3DNPC.esp | 102,131（100,837／1,294） | 相同（`Interesting NPCs 3DNPC - Update` 4.54） | 5／5 | 安裝 |
      | BSAssets.esm | 9,929（9,884／45） | 相同 | 1／1 | 安裝 |
      | BSHeartland.esm | 300,425（300,332／93） | 相同 | 2／2 | 安裝 |
      | BS_DLC_patch.esp | 553（137／416） | 相同（資料夾 meta 寫 1.6.2） | 7／7 | 安裝 |
      | Wyrmstooth.esp | 103,223（103,212／11） | 相同 | 2／2 | 安裝 |
      | evgSIRENROOT.esm | **19,738**（19,729／9） | **19,834**（19,825／9） | 4／4 | **不裝** |
      | Dwarfsphere.esp（AHO） | **48,798**（48,648／150） | **48,762**（48,648／114） | 5／5 | **不裝** |

      - SIRENROOT：兩邊 meta 都寫 1.21，但我們的多 96 筆新增記錄（REFR +69、ACHR +5、INFO +2、DIAL +2、PACK +2、GLOB +1、MESG +1、SCEN +1…）。
        - 翻譯包另外帶了 `strings\ccbgssse067-daedinv_chinese.*` 和 `_English.*`，是 CC 的字串表。官方繁中資料夾裡沒有 067 的表。
        - 如果以後要用這個包，這 6 個檔要排除。
      - AHO：
        - 我們生效的是 `Project AHO - ESM Flag Edition - Clean Patch`（mod 116464）：ESM 旗標，CELL 38、NAVM 32 的覆寫。
        - 88523（ESM 旗標版 v2.0 繁中）是未清理版，覆寫 150（CELL 50、NAVM 56），和原版 AHO 2.0 的數字相同。
        - 88522 是一般版，同樣是未清理版。兩個檔都對不上，所以 `ZH - Nexus 繁中 - Project AHO` 保持空的。
        - 88523 下載在 downloads，只解到暫存區比對，沒有安裝。
      - Bruma 包另外有 `scripts\bskopenspellquestsc.pex`。
        - 它取代的是 `BSAssets.bsa` 裡同名的腳本。
        - 逐字串比對：只有 2 句提示文字換成中文（Unlocked successfully!、This lock is too complex!），其他字串（含編譯資訊）都相同。
   4. `install_archives`：
      - 試跑：可安裝 7、重裝 1、人工 1（DBReV：「資料根目錄有不認得的資料夾：DBReV」）。
      - 用 `--only` 排除 SIRENROOT，再 `--apply`：安裝 6、重裝 1（舊 STPP 1.6 在 `_replaced`）。
      - DBReV 人工看過：
        - 包裡是 `DBReV\translations\zh_CN.json`，和原 mod 的 `DBReV\translations\en_US.json` 同一層。
        - 另有一個只有譯者註解的 `DBReV_Translation_zh_CN.ini`。
        - 用 `--accept` 放行安裝。
      - 安裝內容：
        - VIGILANT、Unslaad：DSD JSON，加上 `interface\translations` 的 `_chinese`／`_english`（內容都是中文）。
        - VIGILANT 另有一個沒用的 `vigilant_english.txt.OLD000`。
        - Wyrmstooth：插件，加上只有 `wyrmstooth_english.txt`（內容是中文）。
   5. AHO：見上表，沒有安裝。
   6. Descriptions：
      - `nexus_fetch --manifest data\zh_archives.csv --apply` 下載 1 個（2.6.1），解壓到 `D:\zh-packs\Descriptions`（28 個 `*_DESC.ini`，都在根目錄）。
      - 比對結果見第 7 點。
   7. `audit_skse` 全過：NG 134、SE 81、需替換 0。之後 `check_plugins` 再跑一次也全過（253／4012）。
7. 蘇禾的包：使用者還沒下載，**未做**。下面是先做、不依賴蘇禾包的部分。
   - **MCM 英文備援**（4.5）：
     - `scan`：有英文版的翻譯檔 110 個（incomplete 35、missing 71、ok 4）。
     - `make-chinese --apply`：新建 `_CHINESE.txt` 71、補缺鍵 35、BSA 英文檔另存 21，共 127 個檔。
   - **Descriptions**（`diff_pack` 試跑）：28 個全判 `skip`（no installed counterpart）。
     - 原因：`diff_pack.vfs_index` 只索引包裡子資料夾的檔案，包在根目錄的 `*_DESC.ini` 找不到對應。
     - 就算找到，`.ini` 也只會判成 review。
     - 改用唯讀腳本分析，結果見「需要雲端決定」第 4 點。**沒有複製任何檔案。**
8. **名詞對照表**：`en-zh` 16,843 筆（213 筆有多種譯法，取最常見的）。
   - **coverage 基準**（蘇禾包安裝前）：
     - 涵蓋率 226,486／473,003（47.9%）。
     - 待翻 265,473 條，約 1,681 萬英文字元。
     - 官方插件仍是英文 2,998 條。
     - 缺中文字串表的本地化插件 1 個：`wraithguardvaultfixer.esp`。
     - ZH 資料夾裡沒有生效的插件 0 個。
   - DSD 對不上：Unslaad 2,600／3,775、VIGILANT 5,191／7,194。這是工具誤判，見「需要雲端決定」第 1 點。
   - 費用粗估（蘇禾包之前，只供參考）：opus-5 Batch 約 $256、opus-5-5 Batch 約 $205、sonnet-5 Batch 約 $102。

## 工具結果（照抄 reports\*.txt 的每一行）
```
== build_instance-create 報告 (2026-10-10 14:49)（試跑 14:47 各行相同）==
[資訊] 模式：實際執行
[資訊] 遊戲語言：沿用設定檔原本的 sLanguage=ENGLISH
[資訊] ModOrganizer.ini：已存在，保留（要重寫請加 --rewrite-ini）
[通過] 設定檔 Pages-ZH：modlist 4147 行（捨棄 21），plugins 4233 個（排除 12 個自製插件）
[資訊] 佔位資料夾：18 個（之後用 MO2 安裝到同名資料夾並選 Replace）
[通過] 遊戲 ini：Skyrim.ini, SkyrimPrefs.ini, SkyrimCustom.ini
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20261010-144916
總結：[通過]

== build_instance-sync-order 報告 (2026-10-10 14:51)（--restore-states --apply；試跑相同）==
[資訊] 模式：實際執行
[通過] 啟用狀態：依目標啟用 0 個、停用 0 個；檔案不在已啟用的 mod 或遊戲資料夾裡，略過 15 個（之後要再跑 prune_dependents）
[通過] 插件順序：4527 個：依目標順序 4218，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 137 個插件到它的前置之後，例如：Natural Waterfalls - Blackreach.esp, Natural Waterfalls - Dawnguard.esp, Natural Waterfalls - Dragonborn.esp, DynDOLOD.esm, Occ_Skyrim_Lux_Via.esp, …
[資訊] 不在目標清單中的插件：DBVO Fix - Belethor's Sister.esp, ULPSC - Praedy's Soul Cairn - Soul Husks Patch.esp, DBM_TreasureHunter_Patch.esp, …
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20261010-145120
總結：[通過]

== prune_dependents 報告 (2026-10-10 14:52)（--disable-folders --apply；試跑數字與名字相同）==
[資訊] 模式：實際執行
[注意] 要停用的插件：26 個，例如：Horsepower_Ragdoll - SC Horses Patch.esp, TSOSRefinedCreationClub.esp, Embershard.esp, Lux Orbis - Embershard patch.esp, Lux - Embershard patch.esp, Northern Roads - Alternate Perspective Patch.esp, …
[資訊] 建議停用的資料夾：18 個：Leveled List Patch, Nolvus Awakening Consistency Patch, Horsepower Ragdoll - SC Horses Skeleton Patch, Nolvus Awakening AI Patch, Nolvus Awakening Economy Patch, …
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20261010-145200
總結：[注意]

== check_plugins 報告（prune 後與 Nexus 繁中安裝後兩次，各行相同）==
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

== build_instance-verify 報告 (2026-10-10 14:52) ==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[資訊] 清單外的資料夾：83 個：Unslaad PBR, Smooth Special Idle, Maerchenwald - Archwood Lite - Giant Fantasy Trees, horseAnimations2, clockwork pbr, Creation Club: _ResourcePack, …
[注意] plugins.txt 與預期比對：缺少或未啟用 41 個（mod 尚未安裝或已被修剪）；待重建輸出 0 個；例如：Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, Anchor Animations Spell V2.esp, FH_Grapple.esp, AnchorShdSwd.esp, SC_HorseReplacer.esp
總結：[注意]

== build_instance-set-language 報告 (2026-10-10 14:52)（--apply；試跑的第 2 行是「（試跑）」）==
[資訊] 模式：實際執行
[通過] 遊戲語言：sLanguage：ENGLISH → CHINESE；備份 D:\PM\profiles\Pages-ZH\_backup\20261010-145217
[通過] 英文語音：sResourceArchiveList2 仍有 Skyrim - Voices_en0.bsa（官方繁中沒有配音）
總結：[通過]

== zh_fontconfig 報告 (2026-10-10 14:52)（--apply；試跑少最後一行）==
[資訊] 目前生效的 fontconfig.txt：Sanguis - Mist's Font Replacer
[通過] 字型對應：官方 22 個；介面 mod 額外名稱改指向中文字型 0 個
[通過] 已寫入：D:\PM\mods\ZH Overrides\interface\fontconfig.txt
總結：[通過]

== manifest 報告 (2026-10-10 14:52) ==
[資訊] 目標資料夾：4072 個
[資訊] 已就位：4033 個
[資訊] 需從 Nexus 下載：8 個
[資訊] 第五階段重建：9 個
[資訊] 需換成 1.5.97 版 DLL：0 個
[注意] 需整包重裝（舊內容移到 _replaced）：1 個
[資訊] 尚無來源，需人工確認：0 個
[資訊] 捨棄：21 個
[資訊] 輸出：reports\manifest.csv、reports\downloads.html
總結：[注意]

== nexus_fetch 報告（manifest 14:53；AHO 88523 與 data\zh_archives.csv 另外各 1 個）==
[通過] 本次下載：9 個
總結：[通過]

== install_archives 報告 (2026-10-10 14:54)（試跑，全部）==
[資訊] 試跑（除了還原中斷的安裝，不改動檔案）：判斷了 539 個下載
[資訊] 磁碟空間：預計解壓 164.0 MB，D:\ 剩 221.5 GB
[通過] 可自動安裝：7 個
[通過] 可自動重裝（舊資料夾移到 _replaced，不刪除）：1 個
[注意] 需要人工判斷（見 install_archives.csv 的 reason 欄）：1 個
[資訊] 不在 manifest 的下載：530 個
[資訊] manifest 目標還沒有下載檔：0 個
總結：[注意]

== install_archives 報告（--only 6 個＋STPP，--apply；試跑相同）==
[資訊] 執行：判斷了 7 個下載
[資訊] 磁碟空間：預計解壓 162.0 MB，D:\ 剩 221.5 GB
[通過] 已安裝：6 個
[通過] 已重裝（舊資料夾在 _replaced）：1 個
總結：[通過]

== install_archives 報告（--only/--accept "ZH - DBReV 中文"，--apply；試跑相同）==
[資訊] 執行：判斷了 1 個下載
[資訊] 磁碟空間：預計解壓 9.5 KB，D:\ 剩 221.4 GB
[通過] 已安裝：1 個
總結：[通過]

== audit_skse 報告 (2026-10-10 14:58) ==
[資訊] 生效的 SKSE DLL：多版本 NG（可用）=134, 非 SKSE 外掛（相依函式庫）=1, SE 版（可用）=81
[通過] 需替換的 DLL：無
[通過] STOCK GAME 遊戲版本：1.5.97.0（需要 1.5.97.0）
[通過] SKSE 1.5.97：skse64_loader.exe + skse64_1_5_97.dll
[通過] Address Library（version-1-5-97-0.bin）：已找到
[通過] 遊戲根目錄的 ENB/ReShade 殘留：無
[通過] Community Shaders：已安裝（Community Shaders）
[資訊] 含 Root 資料夾的 mod（Root Builder 會部署到遊戲資料夾）：無
總結：[通過]

== zh_mcm-scan 報告 (2026-10-10 14:59) ==
[資訊] 有英文版的翻譯檔：110 個：incomplete=35, missing=71, ok=4
[資訊] 已完整中文化：4 個
總結：[資訊]

== zh_mcm-make-chinese 報告 (2026-10-10 14:59)（--apply；試跑多一行「模式：試跑」）==
[資訊] 有英文版的翻譯檔：110 個：incomplete=35, missing=71, ok=4
[通過] 新建 _CHINESE.txt（先放英文）：71 個
[通過] 補齊缺鍵／修正編碼：35 個
[通過] BSA 內英文檔另存為散檔：21 個
[資訊] 已完整中文化：4 個
總結：[通過]

== zh_diff_pack 報告 (2026-10-10 14:59)（--pack D:\zh-packs\Descriptions，試跑）==
[資訊] 比對結果：skip=28
[通過] 版本不符而拒絕的檔案：0 個
[資訊] 模式：試跑
總結：[通過]

== zh_coverage 報告 (2026-10-10 15:02)（蘇禾包安裝前的基準）==
[資訊] 整體涵蓋率：226486/473003（47.9%）
[資訊] 待翻譯：265473 條；去除重複後約 16,813,822 個英文字元
[注意] 缺中文字串表的本地化插件：1 個：wraithguardvaultfixer.esp
[資訊] 官方插件（本體、DLC、CC）仍是英文的字串：2998 條（不送 AI；官方繁中本來就有的名詞保持官方譯法）
[注意] DSD 對不上的條目（依 mod）：ZH - Nexus 繁中 - Unslaad 2600/3775；ZH - Nexus 繁中 - VIGILANT 5191/7194（見 reports\zh_dsd_unmatched.csv）
[通過] ZH 資料夾裡沒有生效的插件：0 個
[資訊] 機器翻譯費用粗估（含思考的預留；準確數字看 llm_translate 試翻後的 estimate）：claude-opus-5：約 $512（Batch 約 $256）；claude-opus-5-5：約 $410（Batch 約 $205）；claude-sonnet-5：約 $205（Batch 約 $102）；claude-haiku-4-5：約 $102（Batch 約 $51）；claude-fable-5-1：約 $1,025（Batch 約 $512）
總結：[注意]
```
- `[注意]` 的說明：
  - prune 26 個和已接受的相同。
  - verify 41 個和上一輪相同。
  - manifest 的重裝 1 個是 STPP。
  - install_archives 的人工 1 個是 DBReV，已人工放行。
  - coverage 的兩項見下面第 1、5 點。

## 需要雲端決定
1. **coverage 的 DSD 比對要忽略「不分段欄位」的 index**（AI 翻譯前要修）。
   - 問題：VIGILANT、Unslaad 的 Nexus 繁中 DSD（`status: TranslationComplete` 格式）在 FULL、DESC、DNAM 這類不分段的欄位都寫 `"index": 1`。
     - sse-plugin-interface 抽出的同一欄位 index 是 `None`。
     - `string_key` 把 `None` 當 -1，所以對不上。
   - 逐筆分析：
     - VIGILANT：5,191 筆對不上的**全部**是「同一筆記錄、同一欄位、只有 index 不同」。
     - Unslaad：2,600 筆中 2,440 筆是這種，真正找不到記錄的只有 160 筆（約 4%）。
     - INFO NAM1、QUST NNAM 這類分段欄位的 index 兩邊一致，都有對上。
   - 影響：
     - 這約 7,600 條會被當成未翻譯放進 worklist。
     - `apply` 寫出的 `ZH - AI 翻譯` 優先順序高於 Nexus 繁中，會用 AI 譯文蓋掉人工譯文，也多花錢。
     - 推測遊戲裡 DSD 對這些欄位不看 index，所以人工譯文本身會生效。主選單測試時可以看 DSD 的記錄確認。
2. **SIRENROOT 繁中（19,738 對我們的 19,834）**：
   - 依手冊不裝，空資料夾保留。
   - 這兩個 mod 的新增記錄 FormID 大多相同。可以考慮寫一個工具把翻譯版插件的文字轉成 DSD JSON（依 FormID＋欄位，只取兩邊都有、而且英文原文相同的記錄），就不用換插件。
   - 不做的話，這部分就靠蘇禾的包或 AI。請決定。
3. **Project AHO 繁中**：我們用的是 Clean Patch 版，88522、88523 都是未清理版（覆寫 150 對 114），不裝。可以用第 2 點同樣的方式處理。請決定。
4. **Descriptions for Various Mods 繁中 2.6.1**：
   - 工具缺口：`diff_pack` 不索引根目錄的檔案，Description Framework 的 `*_DESC.ini` 都在根目錄。
   - 唯讀分析（鍵是 EditorID，用 `EditorID\0` 在啟用中的插件裡找）：
     - 和我們 2.4.1 同名的 2 個：
       - `Remiel_DESC.ini`：我們的 2 鍵都在，多 12 鍵，14 鍵都找得到。
       - `Sirenroot_DESC.ini`：我們的 8 鍵都在，多 8 鍵，16 鍵都找得到。
     - 我們 2.4.1 沒有、但鍵全部找得到的 16 個：Adamant、Alternate Perspective、Daedric Shrines、JK 的 7 個、JS Instruments、Lux Via、Mihail Crystal Golem、Missives、Snazzy Treasury House、Snazzy BlackBriar Manor。
       - 裝了就是替原本沒有描述的物品新增中文描述，英文版沒有這些內容。
     - 找不到或只找到一部分的 10 個：Cidhna Mine Expanded、GORE、Heart of Ice、Kaidan、Mehrunes Dagon's Shrine Unlocked、More To Do Soul Cairn、Obscure's College、Snazzy Silver Inkwells、Sorcerer、Snazzy Nepos House（1／7）。
     - 我們 2.4.1 另外 14 個 `*_DESC.ini`（Inigo、Ordinator、Wintersun…）繁中包沒有，會維持英文。coverage 似乎不處理 `*_DESC.ini`，AI 也不會翻到。
   - 建議：至少採用同名的 2 個。另外 16 個要不要加，請決定。
5. **`wraithguardvaultfixer.esp` 缺中文字串表**：它是本地化插件，`sLanguage=CHINESE` 後名稱可能變空白。確認 `llm_translate apply` 會替它寫出 `_chinese` 字串表，或者要另外處理。
6. **Wyrmstooth 的 MCM**：
   - 繁中譯者把中文放在 `wyrmstooth_english.txt`（38 鍵）。
   - `Wyrmstooth - Settings Loader` 自己帶了全英文的 `wyrmstooth_chinese.txt`（55 鍵）。
   - `make-chinese` 以後者為底，寫出 55 鍵、0 個中文。遊戲讀 `_chinese`，所以這 38 句繁中用不到。
   - 建議 `mcm_txt` 遇到內容是中文的 `_english.txt` 時，拿它當翻譯來源。
7. 小事（不用處理也可以）：
   - VIGILANT 包多一個 `vigilant_english.txt.OLD000`，遊戲不讀。
   - DBReV 的語言名稱轉繁體後會是「簡體中文」字樣；要改成 `zh_TW.json`、名稱「繁體中文」再說。

## 使用者要做的事（網路上查到的情況，連結與提取碼沒有寫進任何檔案）
- 蘇禾的 B 站帳號顯示已註銷，但影片還在：
  - **Nolvus Ultimate 6.0.20 漢化 v1.0（插件＋介面＋MCM）**：和我們的版本一致，影片的置頂留言有網盤連結。
  - **M&V：只找到 2.5.1（漢化 v1.0）和 2.40.1 的包，沒有 2.6.x**。依 `docs/06` 4.1 用 2.5.1。
  - 本體＋CC 包在同一個網盤分享裡。
- 使用者要自己取得連結與提取碼，登入自己的夸克下載，存到下載資料夾。
- `ANTHROPIC_API_KEY` 還沒設定（使用者環境變數讀不到）。

## 本輪手動處理（只修改設定或新增，沒有刪除）
- 建立 `D:\zh-packs`、`D:\zh-packs\Descriptions`、`C:\PagesBackup`。
- 翻譯包的比對都只解到暫存區；SIRENROOT、AHO 的壓縮檔留在 downloads，沒有安裝。

## 本地提交（尚未推送）
- 本回報與 status。
