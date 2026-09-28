# 雲端給本地代理的指示

雲端 Claude 對話（識別碼 `0e5bdc`；顯示名稱會變動，例如 `test-25`、`test-17`）把判讀結果、決策與修正寫在這裡，並提交到分支 `claude/sharp-faraday-b8ax3h`。
本地代理每個階段開始前 `git pull` 後閱讀；已處理的項目在 `progress/status.md` 註記。
個別資料夾的動作覆寫寫在 `data/decisions.csv`（`folder,action,note,nexus_mod_id,nexus_file_id,nexus_version`，後三欄可留空），`tools/manifest.py` 會自動採用。

## 最新指示
- 2026-09-28｜**第 5 階段回報判讀**（回應 719b045）：全部接受。
  - Madmen Simonrim 已停用；NITHI Reach 49 筆外觀已轉送，xEdit 0 錯誤。
  - Lastendell：Nolvus 用的是現成輸出，沒有記錄可比對。我們的 LOD 檔比 Nolvus 還多（52 對 47），接受。
  - **第 5 階段完成。**
- 2026-09-28｜**使用者決定：先漢化，漢化完再玩測試路線。** 第 6 階段的設計（`docs/06` 已改寫）：
  1. **先備份英文版**（`EN-baseline-未測試-日期.7z`），出問題時可以整組停用 ZH 或還原。
  2. **ZH 整組已經寫進目標清單**：
     - 排在三個 `Pages -` 修正 mod 之下、其他所有 mod 之上，以 `-ZH_separator` 分組。
     - DSD 放在 STPP 旁邊。
     - `create --apply` 會建立空的佔位資料夾，之後重建設定檔也不會弄亂順序。
  3. **遊戲語言**：新指令 `build_instance set-language`。
     - `create --ini-from` 會沿用設定檔原本的 `sLanguage`，不會被 Nolvus 的 ini 蓋回英文。
  4. **Nexus 原生繁中**（`decisions.csv` 已寫好，manifest → nexus_fetch → install_archives）：
     - VIGILANT、Unslaad 用 DSD 版（不換插件）。
     - Bruma、3DNPC、Wyrmstooth、SIRENROOT、DBReV 中文 MCM：直接安裝。
     - Project AHO：依我們的插件類型手動選檔。
     - Descriptions for Various Mods：2.6.1 對我們的 2.4.1，只下載，再用 diff_pack 比對。
     - Serana Dialogue Add-On：繁中是舊版，不採用。
     - DSD 1.4.3 新裝，STPP 更新到 1.10。
  5. **蘇禾的包**：
     - Nolvus 6.0.20 的包和我們的版本一致。
     - M&V 我們是 **2.6.2**，請使用者先找 2.6.x 的包，沒有才用 2.5.1；涵蓋率報告會算出對不上的比例。
     - 本體＋CC 包只拿來做名詞釘選，不安裝（官方繁中已涵蓋本體、DLC、CC）。
     - 有 Nexus 原生繁中的插件，要把蘇禾 DSD 裡同名的資料夾**搬到** `_replaced\zh-sohe-overridden\`。
  6. **工具修正**（審查時發現）：
     - `llm_translate apply` 以前可能把本體的中文字串表蓋回英文。現在：
       - 官方插件的字串表一律不寫。
       - 其他插件以「遊戲目前讀到的中文表」為底，只補新譯。
     - MCM 英文備援改放在 ZH 組最低的 `ZH - MCM 英文備援`。以前放在最高的 `ZH Overrides`，會蓋掉 AI 翻譯的 MCM。
     - `llm_translate run` 中斷後重跑：會先回收已送出的批次，不會重複付費。
     - 費用：
       - 試翻後，依實測（含思考 token）推估全部；報告最後一行是「剩下的估計」。
       - 和官方名詞完全相同的文字，直接用官方譯法，不花錢。
     - `coverage` 新增三項：
       - 官方插件不送 AI。
       - `zh_dsd_unmatched.csv`：每個 DSD 包有多少條目對不上我們的插件。
       - ZH 資料夾裡被蓋掉、沒有生效的插件。
     - `fontconfig` 不再讀到自己上次的輸出；`opencc --in-place` 重跑時保留第一次的 `.bak`。
     - 插件名額的說明更新為完整 253／254。
- 2026-09-28｜**使用者要先做的事**（可以和本地的第 1–6 步同時進行）：
  - 從夸克下載蘇禾的包，存到自己的下載資料夾（清單見 `docs/06` 4.1）。連結與提取碼不要寫進任何檔案。
    - Nolvus Ultimate 6.0.20：DSD＋Other。
    - M&V：DSD＋Other，先找 2.6.x。
    - 本體＋CC 包。
  - 設定 Windows 使用者環境變數 `ANTHROPIC_API_KEY`（`docs/06` 第 7 節），然後重開 Claude Desktop。金鑰不要貼進對話。
- 2026-09-28｜**接下來的順序**（照新的 `docs/06`；每步先關 MO2；遇到 `[失敗]` 或不在預期內的結果就停下回報；搬移不刪除）：
  1. `git pull --rebase`、`python -m pip install -r requirements-zh.txt`、`python -m pytest -q`。
     - 應該全過，而且翻譯工具的測試不會被略過。
  2. **英文版備份**（`docs/06` 第 0 節）：
     - 先確認 D 槽以外的空間（約 25 GB），不夠就問使用者。
     - 用 7-Zip 備份 `Pages-ZH` 設定檔、`ModOrganizer.ini`、8 個輸出資料夾、`Pages - 設定覆寫`、`Pages - 版本不符修正`、`Pages - LOTD V6 修正`。
  3. **目標清單**：
     1. `create --apply`：佔位資料夾應該是 ZH 整組、`ZH_separator`、`Dynamic String Distributor`。
     2. 開 MO2 一次再關。
     3. restore-states＋prune：名字要和已接受的 26 個相同。
     4. `check_plugins`：完整 253、輕量 4012。
     5. `verify`。
  4. **`set-language`** 試跑 → `--apply`：「英文語音」要 `[通過]`。
  5. **字型**（`docs/06` 2.1）：
     - fontconfig 試跑 → `--apply`，在 MO2 確認由 `ZH Overrides` 勝出。
     - ImGui 類 mod 的字型（2.2）先不改，等使用者遊玩時看到問號再處理。
  6. **DSD、STPP、Nexus 繁中**（`docs/06` 第 3 節）：
     1. `manifest`：預期下載 8、重裝 1。
     2. `nexus_fetch --apply`。
     3. `install_archives` 試跑 → `--apply`；判為人工的，用 MO2 裝進同名的空資料夾。
     4. 替換插件的翻譯：用 `esl_check` 比對記錄數，要和原版相同。
     5. AHO：依插件類型選檔。
     6. Descriptions：`nexus_fetch --manifest data\zh_archives.csv --apply`，解壓到 `D:\zh-packs\Descriptions`。
     7. `audit_skse`。
  7. **蘇禾的包**（`docs/06` 第 4 節）。使用者還沒下載好就先回報推送，等使用者下載。
     1. 本體＋CC 包解壓 → 名詞釘選表。
     2. 兩個 DSD 包用 MO2 裝進空的佔位資料夾 → `opencc` 試跑（連同 `ZH - DBReV 中文`）→ `--in-place`。
     3. 有原生繁中的插件：把蘇禾 DSD 裡同名的資料夾搬到 `_replaced\zh-sohe-overridden\`。
     4. `mcm_txt scan` → `make-chinese --out-mod "D:\PM\mods\ZH - MCM 英文備援"` 試跑 → `--apply`。
     5. 兩個 Other 包和 Descriptions：`diff_pack` 試跑 → 只複製 accept 的 → Other 兩個資料夾跑 `opencc`。
        - 回報各狀態的數量。
        - Other 包裡有插件就停下問。
  8. **名詞對照表** → **`coverage`**。回報：
     - 涵蓋率、待翻條數與字元數。
     - 官方插件仍是英文的條數。
     - `zh_dsd_unmatched.csv` 每個 mod 的「對不上／條目數」：M&V 包和 Nolvus 包比，比例差很多就停下回報。
     - 沒有生效的 ZH 插件。
  9. **AI 翻譯**（`docs/06` 第 7 節；每次 `run --yes` 都要先問使用者，guard 也會擋）：
     1. `estimate`：報告粗估金額。
     2. 問使用者 → 試翻 20 組：`run --limit 20 --mode sync --yes`。
     3. 回報：
        - 3–5 則短的譯文樣本（英文與中文各一行即可）。
        - 報告的「實際用量換算費用」與「剩下的估計（依實測）」。
     4. **等使用者同意金額** → 全部翻譯（batch）。
        - 可能要幾小時，照 CLAUDE.md 的長時間工作處理。
        - 中斷就重跑同一行。
     5. `apply` → `coverage`。
  10. **檢查**：
      - `check_plugins`：完整 253、輕量 4012，和英文版相同。
      - `audit_skse`。
      - 主選單測試：選單是中文、沒有方框；`DynamicStringDistributor.log` 錯誤的數量。
  11. **回報並推送**。之後請使用者照介面檢查表和測試路線玩。
      - 遊戲有問題時，先把 ZH 整組停用比較英文版。
      - 截圖只給使用者看，不要推上 GitHub。
- 2026-09-28｜**第 5 階段回報判讀**（回應 ec7d72e）。
  - **重建全部接受**：
    - Synthesis：LAND 數沒少是因為每格只輸出一筆，你的解釋對，逐筆比對也做得很好。
    - PGPatcher 重跑、DynDOLOD（Ultra，billboard 上限警告 0）、完整 253／254、第一次用 CS 啟動都接受。
    - xEdit 的做法（只列範圍內的插件、唯讀腳本、確認沒有存檔）也很好。
    - MO2 關著時改 modlist 並留備份，接受。
    - CS 記錄的 1 個 E（FullScreenBlur 在 1.5.97 沒裝上）只影響一個模糊效果，第 7 階段有需要再看。
  1. **`Madmen - Simonrim.esp`：停用**（目標 `plugins.txt` 已改，做法同 HoF 那 6 個）。
     - Nexus 上它只有一個版本（2023 年，主檔 443194 裡的 418 KB），是照舊版 Adamant 做的：
       - 引用的編號（0D01CC、51FD45…）超出輕量插件的範圍。
       - 對不上我們的 Adamant，也沒有其他版本可換。
     - Nolvus 自己的 Madmen - Patches 也沒有選它。
     - 停用後，Forsworn 拿不到 Adamant 的 perk（現在本來就拿不到），法術回到 Madmen 本身的設定。
  2. **NITHI Reach 的 AI Overhaul 補丁：做「外觀轉送」修正版**，新工具 `forward_appearance`。
     - 原因：
       - NITHI The Reach 的 Women.esp 有 4 種變體（Default 39.5 KB、UNP／CBBE 39.7 KB、RSV 38.1 KB）。
       - 補丁（Patch Hub 1.3，和 2025 年的新版同一份）是照其中一種做的，所以編號錯位。
       - 錯位的不只 xEdit 抓到的 23 個：型別剛好對上的錯誤引用，xEdit 不會報。
     - 不能只停用補丁：AI Overhaul.esp 排在 NITHI 後面，會蓋掉 NITHI 的外觀，Markarth 的 NPC 會黑臉、頭身不合。
     - 做法：
       - 每筆 NPC 保留補丁的 AI 資料。
       - 外觀改用我們裝的 NITHI 那一筆：RNAM、WNAM、ANAM、PNAM、HCLF、身高體重、FTST、QNAM、NAM9、NAMA、膚色層。
       - FormID 換算成補丁的前置編號。
       - 同名修正版寫到 `Pages - 版本不符修正`。
     - 其他欄位如果還指向 NITHI 自己的記錄、而且和 NITHI 不一致，工具會列成 `[注意]`（不更動）。
  3. `DBM_JKBluePalace_Patch.esp` 的 1 筆 NAVI：接受。
  4. **Lastendell 的 Ignoring Cell 372 個**：只影響 Midwood Isle 的遠景，先接受。
     - 請唯讀看 Nolvus 自己的 DynDOLOD 記錄有沒有同樣的訊息（找得到才看，找不到就寫「沒有記錄」）。
  5. 這兩項都是 NPC／法術記錄，**不用重跑 DynDOLOD**。
     - 但要確認輸出插件（Synthesis、PG_*、DynDOLOD.*、Occlusion）的前置裡沒有 `Madmen - Simonrim.esp`。
  6. `docs/05` 第 12 節的備份清單加上 `Pages - 版本不符修正`、`Pages - LOTD V6 修正`；常見問題加上「NPC 補丁外觀指錯」的處理。
- 2026-09-28｜**接下來的順序**（每步先關 MO2；遇到 `[失敗]` 或不在預期內的結果就停下回報）：
  1. `git pull --rebase`、`python -m pytest -q`（應該全過）。
  2. **停用 Madmen - Simonrim**：
     1. `create --apply` → 開 MO2 一次再關。
     2. `sync-order --restore-states --apply`：`Madmen - Simonrim.esp` 會是停用。
     3. `prune_dependents` 試跑：名字要都在已接受的 26 個裡，或原因是「前置是 Madmen - Simonrim.esp」；有其他新名字就先回報。
     4. `--disable-folders --apply`。
     5. `check_plugins`：
        - 全部通過。回報完整插件數（如果它原本是完整插件，會變 252）。
        - 在 `reports\check_plugins.csv` 確認輸出插件的 `masters` 欄沒有 `Madmen - Simonrim.esp`；有的話停下回報。
  3. **NITHI Reach 補丁**：
     1. （唯讀）記下我們裝的 `NITHI NPCS - The Reach - Women.esp` 大小與所在資料夾，對照上面 4 種變體。
     2. `forward_appearance` 試跑（指令在 phase-commands）：
        ```bash
        python tools/forward_appearance.py --pm "D:/PM" --plugin "NITHI NPCs - The Reach - Complete - AI Overhaul.esp" --from "NITHI NPCS - The Reach - Women.esp" --from "NITHI NPCs - The Reach - Men.esp" --out "D:/PM/mods/Pages - 版本不符修正"
        ```
        - 回報：改了幾筆 NPC、各欄位的數量、已一致幾筆。
        - `reports\forward_appearance.csv` 裡有 note 的每一列（這些只有插件名稱與 FormID，可以寫進回報）。
        - 有「前置不同沒有更動」的就先停下回報。
     3. 再加 `--apply` → `sync-order --apply` → `check_plugins`。
  4. **xEdit 唯讀檢查**（用你上次的腳本）：
     - 新的修正版要 0 錯誤。
     - 順便檢查 Nolvus 帶來的另外 4 個 NITHI AI Overhaul 補丁（Fort Dawn、Volkihar、The Rift、Whiterun）。有錯誤就回報，不用先處理。
  5. **Lastendell**：看 Nolvus 的 DynDOLOD 記錄（唯讀）。
  6. **主選單測試**（同上一輪）。
  7. 回報並推送。
  8. 之後請使用者照 `docs/測試路線.md` 玩第 11 節的新遊戲測試。
     - 馬卡斯那站多看幾個 NPC 的臉和身體：沒有黑臉，頭和脖子的膚色一致。
     - 使用者回報測試通過後，你再做第 12 節的 EN-baseline 備份（清單已更新）。
- 2026-09-28｜**第 5 階段回報判讀**（回應 75312da）。
  - 換版、兩個掃描歸零、主選單測試都接受。
  - 在 DynDOLOD 前停下是對的：Synthesis.esp 的 4 筆孤兒 LAND 很可能會讓 DynDOLOD 再停一次。
  - 你對工具狀況做的 2 個調整都接受：
    - BS Synergy 用包裝程式只略過備註關鍵字。
    - Horsepower 壓縮檔暫時移開再 `--apply`，完成後搬回。
  - 兩個工具已經修好，下次不用再這樣繞：
    1. **`install_archives`**：備註裡的關鍵字前面緊接否定詞（「沒有」「無」「不是」「不用」「no」「without」）時不算要人工。
       - 同一段備註後面又有肯定的提到（例如「…再用 FOMOD 安裝」），仍然算要人工。
       - 我用 `decisions.csv`、`extra_archives.csv` 的全部備註比對過：只有 BS Synergy 那一列的結果改變。
       - 另外，壓縮檔裡真的有 FOMOD 安裝程式時，`layout` 本來就會擋下，不靠備註。
    2. **`fill_plugins`**：檔案在 modlist 裡被停用的資料夾（已修剪或刻意停用）的插件不算缺少。
       - 報告多一行「資料夾已停用的插件（不算缺少）」。
       - 下次「找不到來源」應該只剩已接受缺少的那些。
  1. **Synthesis：重跑**（必要）。
     - 那 4 筆 LAND 的覆寫目標已經不存在，會變成多出來的新記錄。
     - 另外 Synthesis 是複製當時生效的 LAND 再調亮，重跑才會對上現在的載入順序。
     - 同一個 patcher、預設設定。`docs/05` 第 3 節新增第 8 步「重跑時」。
  2. **PGPatcher：重跑**（約 5 分鐘）。
     - `PG_1.esp` 存的是 3 個舊版補丁的記錄內容，可能把新版的模型路徑改回舊的。舊 BSA 已經在 `_replaced`，那樣會缺模型。
     - 新版 BSA 裡的模型也要經過 PGPatcher。
     - `docs/05` 第 4 節新增第 7 步「重跑時」。
  3. **草地快取、xLODGen、TexGen：不重跑**。
     - 換進來的新版都沒有 LAND／LTEX／GRAS（Lux Orbis 4.7 你已經看過；其他請在第 2 步確認）。
     - 只有舊版 Lux Orbis LotD 那 4 筆 LAND 所在的格子可能有一點差異。請記下它們的世界空間與 cell 座標寫進回報。第 7 階段看得出問題再處理。
  4. **手冊**：`docs/05` 共通原則新增「換掉插件之後」。
     - 看 `reports\check_plugins.csv` 裡輸出插件（Synthesis、PGPatcher、PG_*）的 `masters` 欄。有換過的插件就重跑那個輸出。
     - 新版帶模型就重跑 PGPatcher。
     - 有 LAND／LTEX／GRAS 就記下位置回報。
     - DynDOLOD 之後才換的，DynDOLOD 也要重跑。
     - 舊輸出一律先搬到 `_replaced`。
- 2026-09-28｜**接下來的順序**（每步先關 MO2；遇到 `[失敗]` 或不在預期內的結果就停下回報；長時間工作照 CLAUDE.md；搬移不刪除）：
  1. `git pull --rebase`、`python -m pytest -q`（應該全過）。
  2. **確認換過的插件沒有地形類記錄**（唯讀）：
     - 用 `esl_check --plugin`（可以一次給多個 `--plugin`）看記錄類型：
       - 目前生效的 8 個：5 個 DBM、Lux LotD、Lux Orbis LotD（版本不符修正裡那份）、`DBM_BSHeartlandPatch - Main.esp`。
       - `_replaced` 裡的舊版 8 個。
     - 預期只有舊版 Lux Orbis LotD 有 LAND（4 筆）。有其他的 LAND／LTEX／GRAS 就停下回報。
     - 用你的掃描方法記下那 4 筆 LAND 的世界空間與 cell 座標，並看現在那幾格是由哪個插件提供 LAND。
  3. **Synthesis**（`docs/05` 第 3 節第 8 步）：
     1. 把 `D:\PM\mods\SYNTHESSIS\Synthesis.esp` 搬到 `_replaced\synthesis-<日期時間>\`。
     2. 從 MO2 執行 Synthesis，同一個 patcher、預設設定，按執行。
     3. Overwrite 裡的 `Synthesis.esp` 用「Move content to Mod…」移到 `SYNTHESSIS`（這時是空的，不會有取代的問題）。
     4. 關 MO2：`esl_check --subrecords LAND --flag`（試跑）→ `--flag --apply`。
        - 預期 LAND 7,671 筆左右（上次 7,675 減 4），每筆都有 VCLR。
        - 前置不再有 `Lux Orbis - LotD patch.esp`。
     5. `sync-order --apply`（會把新的 Synthesis.esp 改回啟用）→ `check_plugins`。
  4. **PGPatcher**（`docs/05` 第 4 節第 7 步）：
     1. 把 `pgpatcher_output` 裡的內容整個搬到 `_replaced\pgpatcher-output-<日期時間>\`（資料夾本身留著）。
     2. 在 MO2 暫時停用 `pgpatcher_output` 和 `texgenCS`（`dyndolodCS2` 是空的，不用動）。
     3. 從 MO2 執行 PGPatcher，設定和上次相同（輸出 `D:\PM\mods\pgpatcher_output`），等它完成。
     4. 重新啟用 `pgpatcher_output`、`texgenCS`。
     5. 關 MO2 跑 restore-states＋prune 一組：
        - prune 先試跑，名單要和上一輪的 26 個相同。
        - 然後 `--disable-folders --apply`。
     6. `check_plugins`：
        - `PGPatcher.esp`、`PG_1.esp` 是輕量插件，完整 251。
        - 回報 `pgpatcher_output` 的檔案數（上次 20,432）。
  5. **兩個掃描**：
     - 覆寫掃描：只剩已接受的 16 個，Synthesis 那 4 筆消失。更新 `data/analysis/override_mismatch.csv`。
     - 未解析引用掃描：0。
  6. **主選單測試**（同上一輪）。
  7. **DynDOLOD 之後**：照 78aa2e5 那一輪的第 9–13 步。
     1. DynDOLOD：Advanced → High，Tree LOD 勾 **Ultra**。
     2. 搬輸出到 `dyndolodCS2` → `sync-order --apply` → `check_plugins`（完整 253）。
     3. `audit_skse`。
     4. 第一次用 CS 啟動。
     5. xEdit 檢查（唯讀）。
     6. 回報並推送。
- 2026-09-28｜**第 5 階段回報判讀**（回應 cef4e36）。
  - 未解析引用的完整掃描做得很好：36 筆全部追到 LOTD V5，而且新版都先驗證過。
  - 在 Solstheim 停下、搬走不完整的輸出（沒有刪除），處理都正確。
  1. **Nolvus 的 LOTD 5.6 補丁換成對應 V6 的新版**：照你的建議。
     - **LOTD 官方補丁 6.10.9**：Falskaar、Wyrmstooth、Clockwork、Gray Cowl、Forgotten City 共 5 個。
       - 用 `fill_plugins` 從 downloads 的壓縮檔取（選項資料夾例如 `04 FKP/`，連同 BSA）。
       - 目的資料夾是 `Legacy of the Dragonborn Patches (Official)2`（`data/extra_archives.csv` 第 39 行）。
     - **Lux Patch Hub 7.2**：`Lux - Legacy of the Dragonborn patch.esp`，同樣用 `fill_plugins`（第 44 行 → `Lux - Patch Hub3`）。
     - **Lux Orbis Patch Hub 4.7**：`Lux Orbis - LotD patch.esp` 有兩份大小不同的同名檔，`fill_plugins` 會判為不明確。
       - 取 `Lux Orbis (patch hub)/00 Data/` 根目錄那份（通用版）；另一份在 `Lux Orbis - Solitude LotD meshes/` 子資料夾，是給另外裝那個模型選項用的。
       - 手動放進原檔所在的資料夾（預期是 `Lux Orbis - Patch Hub2`）。
       - 它還有 4 筆覆寫指向 V6 沒有的記錄，之後用 `--drop-missing` 處理。
     - **BS Synergy 1.13.2**：`data/decisions.csv` 新增 reinstall（36074／667108）。
       - 壓縮檔根目錄就是插件，沒有 FOMOD，由 `install_archives` 整包換，舊內容移到 `_replaced`。
     - **重要：`fill_plugins` 這次不要加 `--mv`、`--nolvus`**。
       - 它會先從 Nolvus／M&V 的安裝找插件，加了就會把 5.6 版從 `D:\Nolvus` 連回來。
       - 不加就只從 downloads 的壓縮檔取。
       - 它也不覆寫已存在的檔，所以同名的舊 BSA 要先一起搬走。
       - 已寫進 `docs/04` 8.1 和 phase-commands。
  2. **剩下室內的 2 筆（`LOTD_HUB.esp`、`DBM_Lucien_Patch.esp`）：用 `strip_refs` 刪掉那 2 筆放置記錄**，不換版本。
     - 新選項 **`--drop-unresolved-base`**：刪掉基底物件（NAME）在非官方前置裡不存在的放置記錄（REFR、ACHR、PGRE、PHZD、PMIS、PARW、PBAR、PBEA、PCON、PFLA）。
       - 基底物件不存在，遊戲本來就不會顯示。
       - Lucien 那筆是覆寫 LOTD 自己的 REFR，刪掉後回到 V6 原本的那筆。
     - Follower Room Patches 4.0.16 沒驗證過，也是整套為 V6 重做的，只換 1 個插件風險比較大。HoF 維持第 8 階段再評估。
     - 另一個改變：**生效的插件已經是 `--out` 裡的修正版時，`strip_refs` 會重新檢查並原地更新**（只限單一連結的檔），沒有要改的就回報「已修正」。
       - 以前是直接略過。
       - `LOTD_HUB.esp` 的修正版已在 `Pages - 版本不符修正`，這次會在同一個檔上再刪那 1 筆。
  3. **Tamriel 的樹 LOD billboard 超過上限：勾 Ultra**。
     - 一般 tree LOD 一張貼圖集最多 256 種 billboard，我們的 TexGen 有 1,259 種。
     - Ultra 把樹改用 object LOD 產生，沒有這個上限，也不用改 ini。
     - 會比較吃效能和時間；RTX 5080 16 GB 撐得住，第 7 階段再調。
     - `docs/05` 第 8 節已更新。
  4. `akd_MorthalOldGateMill.esp` 那 1 個非致命的：照你的建議不處理。
  5. **手冊**：`docs/05` 第 8 節開頭新增「開始前先把關」。
     - DynDOLOD 前要先重跑覆寫掃描和未解析引用掃描。
     - 兩個都是 0（已接受的除外）才開始。
- 2026-09-28｜**接下來的順序**（每步先關 MO2；遇到 `[失敗]` 或不在預期內的結果就停下回報；長時間工作照 CLAUDE.md；搬移用 `_replaced\lotd56-patches-<日期時間>\<原資料夾>\`，不要刪除）：
  1. `git pull --rebase`、`python -m pytest -q`。
  2. **BS Synergy**：
     1. `manifest`：預期 reinstall 1 個（`Beyond Skyrim - Legacy of the Dragonborn Synergy Patch2`）。
     2. `nexus_fetch`（manifest）：預期下載 667108。
     3. `install_archives --only "Beyond Skyrim - Legacy of the Dragonborn Synergy Patch2"` 試跑，再 `--apply`。
  3. **把舊檔搬到 `_replaced`**（搬移，不要刪除；搬之前先列出來確認）：
     - `Legacy of the Dragonborn Patches (Official)2` 裡的 5 個插件和同名的 `.bsa`：
       - `DBM_Falskaar_Patch`、`DBM_Wyrmstooth_Patch`、`DBM_Clockwork_Patch`、`DBM_TheGrayCowlofNocturnal_Patch`、`DBM_ForgottenCity_Patch`。
       - 同名 BSA 例如 `DBM_Falskaar_Patch.bsa`；有 `- Textures.bsa` 的也一起。
     - `Lux Orbis - LotD patch.esp`、`Lux - Legacy of the Dragonborn patch.esp` 的原檔（Nolvus 擷取來的資料夾）。
     - `Pages - 版本不符修正` 裡這 3 個舊修正版：
       - `DBM_TheGrayCowlofNocturnal_Patch.esp`、`Lux Orbis - LotD patch.esp`、`Lux - Legacy of the Dragonborn patch.esp`。
       - 它們優先權比較高，不搬會蓋掉新版。
     - `LOTD_HUB.esp` 的修正版**留著**（第 7 步原地更新）。
  4. **放入新版**：
     1. `fill_plugins --pm "D:/PM"`（**不加 `--mv`、`--nolvus`**）試跑。
        - 預期 `archive` 6 個：5 個 DBM 補丁，目的 `(Official)2`，連同選項資料夾的 BSA；還有 Lux LotD，目的 `Lux - Patch Hub3`。
        - 預期 `ambiguous` 有 Lux Orbis LotD。
        - 其餘只會是之前就知道的缺少項目。
        - 有別的 `archive` 列就先停下回報，不要 `--apply`。
     2. `--apply`。
     3. Lux Orbis LotD 手動放：
        - 用 7-Zip 從 4.7 壓縮檔把 `Lux Orbis (patch hub)/00 Data/Lux Orbis - LotD patch.esp` 解到 scratchpad。
        - 再複製到原檔所在的資料夾（預期 `Lux Orbis - Patch Hub2`）。
        - 放之前用 `esl_check --plugin` 看它的前置；前置都在載入順序裡才放。
  5. `sync-order --apply` → `check_plugins`：全部通過，完整插件不會增加（251 以下）。
  6. **覆寫掃描**（唯讀）：
     1. 重跑掃描，更新 `data/analysis/override_mismatch.csv`。
     2. 預期新出現的只有 `Lux Orbis - LotD patch.esp` 4 筆；原本就接受的 17 個（70 筆）不動。
     3. `strip_refs --drop-missing --plugin "Lux Orbis - LotD patch.esp" --out "D:/PM/mods/Pages - 版本不符修正"` 試跑，再 `--apply`。
  7. **未解析引用掃描**（唯讀）：
     1. 重跑掃描，更新 `data/analysis/unresolved_refs.csv`。預期只剩 `LOTD_HUB.esp`、`DBM_Lucien_Patch.esp` 各 1 筆（NAME）。有其他插件或其他欄位（XESP 等）就先停下回報。
     2. `strip_refs --drop-unresolved-base --from-csv data/analysis/unresolved_refs.csv --out "D:/PM/mods/Pages - 版本不符修正"` 試跑，再 `--apply`：
        - `LOTD_HUB.esp`：原地更新，預期「刪除 1 筆基底物件不存在的放置記錄…（原地更新修正版）」。
        - `DBM_Lucien_Patch.esp`：新的修正版寫到 `Pages - 版本不符修正`。
     3. 兩個掃描都再跑一次：都要是 0（覆寫掃描只剩原本就接受的 17 個）。這也確認沒有其他記錄引用被刪的那 2 筆。
  8. `sync-order --apply` → `check_plugins` → 主選單測試（DataLoaded 時間、BEES、crash log，同上一輪）。
  9. **DynDOLOD**（`docs/05` 第 8 節）：
     1. Advanced → High，勾 Object／Tree LOD（**Ultra**）／Dynamic LOD、Occlusion data＋Plugin；不做草 LOD；輸出到 `D:\PM\tools\DynDOLOD\DynDOLOD_Output\`。
     2. 完成後搬到 `dyndolodCS2` → `sync-order --apply` → `check_plugins`：預期完整 253／254，`Occlusion.esp` 是輕量插件；如果是完整插件，用 `esl_check --flag` 處理。
     3. `audit_skse`。
     4. 如果又出現「Unresolved FormID」，照樣停下回報：補丁名稱、主插件、FormID 與筆數。
  10. **第一次用 CS 啟動**（`docs/05` 第 10 節）：到主選單，確認沒有當機。
  11. **xEdit 的引用檢查**（唯讀，範圍同上一輪，加上這次換進來的 7 個插件）。
  12. 回報並推送：
      - 各報告的每一行。
      - 兩個掃描的結果。
      - DynDOLOD 記錄的摘要（錯誤與警告的種類、數量；tree billboard 上限的警告應該消失）。
      - `dyndolodCS2` 的檔案數。
      - xEdit 檢查的摘要。
  13. 之後是第 11 節的測試路線（**由使用者玩**）、第 12 節的 EN-baseline 備份，然後開始第 6 階段中文化。
- 2026-09-28｜**第 5 階段回報判讀**（回應 c0badc4）。
  - 版本不符修正（59 個、683 筆，重新掃描是 0）與主選單測試都接受。
  - DynDOLOD 的分析非常清楚，比對 HoF 兩個版本的結果很有用。
  1. **HoF 的 3 個補丁：照你的建議 (B)**。
     - 停用 `DBM_HUB_TwilightPrincess_Patch.esp`、`DBM_HUB_SoulHunterArmor_Patch.esp`、`DBM_HUB_Unslaad_Patch.esp`，以及以它們為前置的 `LOTD_TCC_Twilight Princess Armor.esp`、`LOTD_TCC_Soul Hunter Armor.esp`、`LOTD_TCC_Unslaad.esp`。
     - 做法：目標 `data/target/plugins.txt` 把這 6 行改成停用（行首沒有 `*`）。
       - `create --apply` 會照目標寫入停用，`restore-states` 會維持停用。
       - fill_plugins 只補啟用的目標插件，不會再補回來。
     - 結果和 Nolvus 原本的設定相同：HoF 不展示這 3 套盔甲。
     - 整包升級 HoF 2.4.26＋TCC 4.9 (A) 牽涉 39 個插件，還要重跑 PGPatcher、重做修正版，留到第 8 階段再評估。
     - `data/extra_archives.csv` 第 57、58 行已註明。
  2. **Ice Blade of the Monarch、Oblivion Artifacts 缺 script**：不處理。這兩個 mod 屬於 Nolvus 那邊，DynDOLOD 只記為錯誤。測試路線時如果碰到相關物件沒反應，再回報。
  3. **xEdit 的引用檢查**：要做，但放在 DynDOLOD 與第一次 CS 啟動之後，避免擋住 LOD。
     - 範圍：只檢查從壓縮檔補進來的插件，也就是 `fill_plugins` 取出的、`Pages - 版本不符修正` 以外的單一連結插件。
     - 在 SSEEdit 選這些插件載入（它們的前置會自動載入），用「Check for Errors」。**不要存檔**。
     - 回報每個插件的錯誤種類與數量（特別是 Unresolved／NULL reference）。雲端再決定要不要處理。
  4. **手冊缺口**：
     - `docs/05` 共通原則新增：在 MO2 手動停用又重新啟用 mod 之後，跑 restore-states＋prune 這一組（TrueHUD.esl 的問題）；第 4、5.3 節也寫上了。
     - 第 8 節註明：先按 Advanced 再按 High；「Unresolved FormID」要停下回報。
- 2026-09-28｜**接下來的順序**（每步先關 MO2；遇到 `[失敗]` 或不在預期內的結果就停下回報；長時間工作照 CLAUDE.md）：
  1. `git pull --rebase`、`python -m pytest -q`。
  2. **重建設定檔**（目標有 6 個改成停用）：
     1. `create --apply` → 開 MO2 一次再關。
     2. `sync-order --restore-states --apply`：這 6 個會是停用。
     3. `prune_dependents` 試跑。名字要都在上一輪的 26 個裡，或者原因是「前置是這 6 個之一」（例如 `LOTD_TCC_Unslaad_Display.esp`）；有其他新名字就先回報。
     4. `--disable-folders --apply`。
  3. **檢查**：`check_plugins`（全部通過，完整 251）→ `verify` → 主選單測試。
  4. **DynDOLOD**（`docs/05` 第 8 節，選項同上一輪）：
     1. Advanced → High，勾 Object／Tree／Dynamic LOD、Occlusion data＋Plugin，不做草 LOD，輸出到 `D:\PM\tools\DynDOLOD\DynDOLOD_Output\`。
     2. 完成後搬到 `dyndolodCS2` → `sync-order --apply` → `check_plugins`：預期完整 253／254，`Occlusion.esp` 是輕量插件；如果是完整插件，用 `esl_check --flag` 處理。
     3. `audit_skse`。
     4. 如果又出現其他插件的「Unresolved FormID」，照樣停下回報：補丁名稱、主插件、FormID 與筆數。
  5. **第一次用 CS 啟動**（`docs/05` 第 10 節）：到主選單，確認沒有當機。
  6. **xEdit 的引用檢查**（見上面第 3 點，唯讀）。
  7. 回報並推送：
     - 各報告的每一行。
     - DynDOLOD 記錄的摘要（錯誤與警告的種類、數量）。
     - `dyndolodCS2` 的檔案數。
     - xEdit 檢查的摘要。
  8. 之後是第 11 節的測試路線（**由使用者玩**）、第 12 節的 EN-baseline 備份，然後開始第 6 階段中文化。
- 2026-09-27｜**第 5 階段回報判讀**（回應 282f8cf）。
  - RaySense、Synthesis（.NET 10 SDK 的安裝已經使用者同意，接受）、PGPatcher、草地快取、xLODGen、TexGen 都接受。
  - 在 DynDOLOD 前停下來是對的；覆寫掃描的分析非常好。
  1. **覆寫不存在的記錄：用 (b) 的通用版，一次處理表格裡的 59 個插件**。
     - `strip_refs` 新增 `--drop-missing`：刪掉「覆寫目標在非官方主插件裡不存在」的**整筆記錄**。
       - 刪 CELL／WRLD 時，連同它的子群組一起刪；刪完變空的群組也移除；HEDR 的記錄數跟著更新。
       - 合法的覆寫都保留。
       - 同名修正版寫到新 mod **`Pages - 版本不符修正`**（目標 modlist 第 2 行，在 LOTD 修正之上）；原檔不動、不佔名額。
     - 為什麼要刪：
       - TGTK 那 14 筆（1.70 主插件、0x800 以下）現在是蓋到 Skyrim.esm 的內建記錄（AVIF／STAT），可能 CTD。
       - 其他的會變成多出來的新記錄，室外的 REFR 還會被 DynDOLOD 做進 LOD。
       - 刪掉只是放棄這些補丁對「我們版本裡不存在的物件」的修改。
     - 不逐一換版本（TGTK 2.0、HoF、Lux 等）：59 個各自追版本成本太高。表格的來源欄留著，第 8 階段有空再改善。
     - Nolvus／M&V 原本就這樣出貨的 17 個（70 筆）照舊不處理。
  2. **`PG_2.esp`**：正常。PGPatcher 依記錄數決定要產生幾個 PG 插件，已從目標 plugins.txt 拿掉。
  3. **TexGen 找不到的貼圖**：接受。`oakleafmushroom01_n.dds` 在 Nexus 上只出現在別人清單的產出包裡，不是來自任何原始 mod。只影響少數樹葉的法線貼圖。
  4. **手冊與工具缺口**：你列的 8 點都已處理。
     - `docs/05` 更新了這些內容：
       - 第 3 節：.NET 10 SDK、Synthesis 的 Data Folder、編譯與執行的方式。
       - 第 4 節：PGPatcher 的 `settings.json`，以及執行時停用 `pgpatcher_output`。
       - 第 5.3 節：用 NGIO 記錄判斷草地快取完成（Root Builder 會重導 `PrecacheGrass.txt`）。
       - 第 6–8 節：`-SSE -D:"D:\PM\STOCK GAME\Data"`、xLODGen 的 `-o:`、只勾 Terrain、TexGen 的輸出路徑。
       - DynDOLOD 設定檔的 `D:\MV` 改成 `D:\PM`，以及選 High、Occlusion、不做草 LOD。
     - 工具修改：
       - `sync-order`：被 MO2 列成停用的輸出插件（Synthesis、PG、DynDOLOD、Occlusion…）會自動改成啟用，報告多一行。
       - `unshare_links`：`.log` 不論多大都會換成獨立副本。
     - **刪除 D:\MV 之前**，DynDOLOD／TexGen／PGPatcher 設定檔裡的 `D:\MV` 一定要都改掉。
- 2026-09-27｜**接下來的順序**（每步先關 MO2；遇到 `[失敗]` 或不在預期內的結果就停下回報；長時間工作照 CLAUDE.md）：
  1. `git pull --rebase`、`python -m pytest -q`。
  2. **重建設定檔**（目標多了一個資料夾、少了 PG_2）：
     1. `build_instance create --apply` → 開 MO2 一次再關。
     2. `sync-order --restore-states --apply` → `prune_dependents` 試跑。名字都要在已接受的名單內；有新名字就先回報。
     3. `--disable-folders --apply`。
  3. **版本不符修正**：
     ```
     python tools/strip_refs.py --pm "D:/PM" --drop-missing --from-csv data/analysis/override_mismatch.csv --out "D:/PM/mods/Pages - 版本不符修正"
     ```
     - 先試跑，確認 59 個都列出刪除筆數（總數應接近 683），再加 `--apply`。
     - 有「找不到插件」就回報（可能是被修剪了）。
  4. **檢查**：
     - `sync-order --apply` → `check_plugins`：應全部通過；完整 251、輕量數不變。
     - `verify`。
     - 重跑你的覆寫掃描：表格裡的 59 個應該都變成 0，只剩原本就有的 17 個。
     - 主選單測試（DataLoaded、到主選單）。
  5. **DynDOLOD**（`docs/05` 第 8 節）：
     1. 搜尋 `D:\PM\tools` 裡含 `D:\MV` 的設定檔（`.ini`／`.json`／`.txt`，記錄檔除外），全部改成 `D:\PM`（先備份），並列出改了哪些檔。
     2. 選 High、勾 Occlusion、不做草 LOD，輸出到 `D:\PM\tools\DynDOLOD\DynDOLOD_Output\`。
     3. 完成後搬到 `dyndolodCS2` → `sync-order --apply` → `check_plugins`：預期完整 253／254，`Occlusion.esp` 是輕量插件；如果是完整插件，用 `esl_check --flag` 處理。
     4. `audit_skse`。
  6. **`docs/05` 第 10 節**：第一次用 CS 啟動（到主選單，確認沒有當機、LOD 有顯示）。
  7. 回報並推送：
     - 各報告的每一行。
     - strip_refs 每個插件的刪除筆數摘要。
     - 覆寫掃描的新結果。
     - DynDOLOD 記錄的摘要（錯誤與警告的種類、數量）。
     - 各輸出資料夾的檔案數。
  8. 之後是第 11 節的測試路線，**由使用者玩**；通過後做第 12 節的 EN-baseline 備份，再開始第 6 階段中文化。
- 2026-09-27｜**第 5 階段回報判讀**（回應 34c8a1e）。
  - 主選單修好（176 秒）、strip_refs 的 12 個引用、OAR 3.2.1、BodySlide morphs（和 Nolvus 幾乎逐位元組相同）都接受。
  - 你照手冊在 Synthesis 停下是對的：**是我手冊寫錯了**。
  1. **Synthesis**：
     - Nolvus 手冊的截圖顯示，Nolvus 用的是 Jampi0n 的 `Skyrim-RemoveLandscapeVertexColor`。
     - 讀它的原始碼：預設 `removeAllVertexVertexColors=false`，不移除頂點顏色，而是用公式調亮（一般地形 `Pow(x/255,0.5)*255`，雪地 `Pow(x/255,0.1)*255`）。
     - 驗算：原版 115 → 171、平均 239 → 247，和你量到的 Nolvus 值（最暗 182–217、平均 248.6）吻合。
     - 所以照 Nolvus：只用這一個 patcher，**Settings 保持預設**。`docs/05` 第 3 節已改寫，也寫了產生後的檢查（LAND 每筆都要有 VCLR）。
  2. **RaySense**：升到 1.2.0（175498／796343）。說明寫明新增 RaySense_Ledge，需要 OAR 3.0.2 以上；沒有 FOMOD，插件同名。`decisions.csv` 設為 reinstall。
     - 其餘 24 行個別動畫設定檔的解析錯誤不用處理。
  3. **Knockback 的 AE 判斷**：接受限制。兩版的路徑字串相同，靜態檢查分不出來，這種個案靠 `decisions.csv` 與主選單測試處理（`pe.py` 已註明）。
  4. **手冊修正**：
     - BodySlide 第 5 步改成「勾選狀態不要動，直接 Build」，並加「TRI = True」的檢查與 `BodySlide.xml` 的做法。
     - phase-commands 註明：`create --apply` 會把修剪全部恢復，prune 的判斷標準是「名字都在已接受的清單內」。
  5. **中文化**：還沒開始，照設計在 EN-baseline（第 5 階段第 12 節）之後。現在只有第 2 階段抽出的官方繁中字串。
     - 使用者可以先從夸克下載蘇禾漢化包（`docs/06` 5.1 表中的 5 項；連結由使用者自己取得，不要寫進任何檔案）。
     - 下載好之後，你可以在長時間工具執行的空檔做下面「可平行進行」的唯讀準備。
- 2026-09-27｜**接下來的順序**（每步先關 MO2；遇到 `[失敗]` 或不在預期內的結果就停下回報；長時間工作照 CLAUDE.md）：
  1. `git pull --rebase`、`python -m pytest -q`。
  2. **RaySense**：
     1. `manifest`：預期 reinstall 1 個。
     2. `nexus_fetch`。
     3. `install_archives --only "Open Animation Replacer - RaySense3"` 試跑，再 `--apply`。
     4. `audit_skse --dll` 測新的 `OpenAnimationReplacer-RaySense.dll`。
  3. **主選單測試**：
     - 確認 `skse64.log` 有載入 RaySense，`OpenAnimationReplacer.log` 沒有「RaySense_Ledge not found」。
     - 沒載入的話，把 `_replaced` 裡的 1.1 搬回原資料夾（搬移，不要刪除）並回報。
  4. **Synthesis**：照新的 `docs/05` 第 3 節。產生後跑 `esl_check --subrecords LAND --flag`（試跑）→ `--flag --apply` → sync-order → `check_plugins`。
  5. **`docs/05` 第 4–10 節**：
     - PGPatcher → 草地快取（方案 A）→ xLODGen → TexGen → DynDOLOD（High）→ sync-order／check_plugins／audit_skse → 第一次用 CS 啟動。
     - 停止條件同上一輪：
       - 工具的輸出資料夾要是空的。
       - 每個工具跑完都跑 `check_plugins`。
       - 除了 DynDOLOD.esm／.esp，新的完整插件輸出要加 ESL 旗標；加不上就停下回報。
  6. 回報並推送：
     - 各報告的每一行。
     - 各輸出資料夾的檔案數。
     - Synthesis 的 LAND 筆數與前置數量。
     - DynDOLOD 的記錄檔摘要（有錯誤時）。
     - 第 11 節的測試路線由使用者玩；第 12 節的 EN-baseline 在測試通過後做。
- 2026-09-27｜**可平行進行的中文化準備**（只在使用者已下載蘇禾包時做；**不在 D:\PM 安裝任何中文 mod**）：
  1. 照 `docs/06` 5.3 第 1 步，把兩個 Other 包和本體＋CC 包解壓到 `D:\zh-packs`。兩個 DSD 包先不動。
  2. 照 5.3 第 2 步列出本體＋CC 包的檔案清單（`reports\zh_pack_basegame_list.txt`）。
  3. 照 5.5 第 1–2 步，對兩個 Other 包跑 `diff_pack.py` 試跑（唯讀），報告改名為 `zh_diff_pack-nolvus.*`、`zh_diff_pack-mv.*`。
  4. 在 local-report 附上這些報告的摘要（每行結果與數量，不貼網盤連結或整份清單），雲端在第 6 階段開始前判讀。
- 2026-09-27｜**第 5 階段前半回報判讀**（回應 08bcfd8）。
  - 找出卡住原因的方法（取樣執行緒、追到 LOTD NPC 的 PKID）非常好。
  - Knockback 換 SE 版、補裝 Community Shaders、Pandora 的處理（Steam 裡誤寫的檔由使用者同意後刪除）、BodySlide 的設定覆寫，都接受。
  1. **LOTD 的 NPC 補丁**：
     - **NPC Overhaul** 升到 v2（38178／514540，「Updated for Legacy v6」），`decisions.csv` 設為 reinstall。
       - 壓縮檔有 FOMOD，要用 MO2 安裝：舊內容先搬到 `_replaced`，選項和舊版相同。
       - 看舊插件的大小判斷選項：68061 bytes＝`00 Main`，68070＝`01 Option/AltAuryen`。
     - **Modpocalypse LOTD** 沒有 V6 版。新工具 `tools/strip_refs.py` 做了 Pages 自製 ErrorFixes 的事：
       - 在新 mod `Pages - LOTD V6 修正` 寫出**同名修正版**，只刪掉指向 V6 已不存在記錄的 PKID、CNTO（連同後面的 COED），並更新 COCT。
       - FormID、外觀、FaceGen 都不變，也不佔插件名額；原檔不動。
       - NPC Overhaul v2 如果也還有這種引用，一樣處理。
     - 修好後 Nolvus Awakening NPC Patch 可以保留。
     - 仍然卡住就退回 (a)（見順序第 7 步）。
  2. **OAR**：升到 3.2.1（92109／798222，官方說明支援 1.5.97，沒有 FOMOD）。`decisions.csv` 設為 reinstall，由 `install_archives` 安裝。RaySense 的外掛與 M&V 的 IED Conditions／Detection Plugin 都搭配 OAR 3 使用。
  3. **恢復項目**：
     - 加回 `AI Overhaul - USSEP Patch.esp`（輕量）。已加進目標 plugins.txt，`plugin_sources.csv` 對應 M&V 的 `AI Overhaul SSE` → `AI Overhaul`；GS 的 AIO 補丁會跟著恢復。
     - Embershard **不恢復**：SnozzResources 是完整插件，而且要壓縮 FormID，名額只剩 1 個餘裕。
  4. **Synthesis**：Nolvus v6 那份只覆寫 LAND／CELL／WRLD、沒有 WATR，所以 v6 已不用 Water Does Damage。
     - 只加 **Remove Landscape Vertex Color**，前提是 `esl_check --subrecords LAND` 顯示 Nolvus 那份的 LAND 沒有 VCLR（`docs/05` 第 3 節）。
  5. **BodySlide**：
     - 照 Nolvus 的選擇、7 組保留預設都接受。
     - 10 組頂點差異不追查（只影響兩套服裝的外觀）。
     - **Build Morphs 我先前寫錯了**：Nolvus 有建 morphs，改成勾選後再建一次（選擇已在 `BuildSelection.xml`，約 1 分鐘）。
     - `docs/05` 第 2 節已照你的做法改寫：設定覆寫、確認 `Log_BS.txt`。
     - 做成工具不需要：`BuildSelection.xml` 與 `data/analysis/bodyslide_choices.csv` 已經記錄了選擇。第 8 階段要把 `BuildSelection.xml` 一起備份。
  6. **主選單偏下被切掉**：留到第 7 階段。
  7. **工具與手冊缺口**：
     - `audit_skse`：
       - DLL 只找 `versionlib-*.bin`（AE 版 Address Library）時，判為 AE 專用，就算它匯出 Query 也一樣。
       - 新增 `--dll PATH`，可以只判斷一個檔。
       - 新增「Community Shaders」一行（找不到 `CommunityShaders.dll` → `[失敗]`）。
       - ENB 那一行不再寫「可正常運作」。
       - DLLPlugins 暫不處理（只有 1 個，你已確認）。
     - `verify`：目標有啟用、但目前沒啟用的插件也算缺少，不再隨 MO2 開關變動；另列清單外的資料夾。
     - `build_instance` 的已知工具加了 `Pandora Behaviour Engine.exe`。
     - 文件：
       - `docs/05` 第 1 節改寫：Settings.json、工作目錄、確認 Steam 沒被寫入。
       - `docs/05` 共通原則補充：被其他 mod 蓋掉的設定檔放 `Pages - 設定覆寫`。
       - `docs/04` 第 7 節加 audit_skse 的確認。
     - **目標 modlist 已加上**：`Pages - 設定覆寫`、`Pages - LOTD V6 修正`（最上方），以及 CS 4 個（放在 `CommunityShaders_AIO…` 前面，也就是 `dyndolodCS2` 上方）。
       - 名稱用 docs 的建議：`Community Shaders`、`CS - Skylighting`、`CS - Upscaling`、`CS - Grass Optimizations`。
       - 你的資料夾名稱不同的話，改 `data/target/modlist.txt` 與 `data/decisions.csv` 的這幾列，並在回報寫明。
- 2026-09-27｜**接下來的順序**（每步先關 MO2；遇到 `[失敗]` 或不在預期內的結果就停下回報；長時間的工作照 CLAUDE.md「長時間工作」）：
  1. `git pull --rebase`、`python -m pytest -q`。
  2. `build_instance create --apply`（目標改了）→ 開 MO2 一次再關。`verify` 應該沒有「MO2 移除了」。
  3. **重裝**：
     1. `manifest`：預期 reinstall 2 個（NPC Overhaul、OAR），download 0 個。
     2. `nexus_fetch`。
     3. `install_archives --only "Open Animation Replacer4"` 先試跑，再 `--apply`。
     4. NPC Overhaul 照第 1 點用 MO2 安裝。
     5. 重跑 `manifest`：reinstall 應為 0。
  4. `fill_plugins` 試跑 → `--apply`：預期取出 `AI Overhaul - USSEP Patch.esp`。
  5. **strip_refs**：
     1. 試跑：
        ```
        python tools/strip_refs.py --pm "D:/PM" --master LegacyoftheDragonborn.esm --out "D:/PM/mods/Pages - LOTD V6 修正" --plugin "Modpocalypse NPCs (v3) Legacy of the Dragonborn.esp" --plugin "LegacyoftheDragonborn - NPC Overhaul.esp" --plugin "Nolvus Awakening NPC Patch.esp" --plugin "[xPatch] Modpocalypse NPCs (v3) SSE - LegacyoftheDragonborn.esp"
        ```
        預期：Modpocalypse 約 10 筆記錄，NPC Overhaul v2 可能是 0，後兩個是 0。
     2. 同一行加 `--apply`。
     3. 確認 `Pages - LOTD V6 修正` 在 modlist 裡是啟用的，而且在最上方附近。
  6. **狀態與檢查**：
     1. `sync-order --restore-states --apply`。
     2. `prune_dependents` 試跑。預期是上一輪那 9 個，扣掉 `Grand Solitude - AI Overhaul patch.esp`；有新的名字就先回報。
     3. `--disable-folders --apply`。
     4. `check_plugins`、`verify`、`audit_skse`。
     5. `audit_skse --dll` 測 `_replaced` 裡舊的 `KnockbackPlugin.dll`（應判為 AE 專用），也測新的那個。
     6. 列出這次被判成 AE 專用的其他 DLL：上一輪它們在 `skse64.log` 都有載入的話就是誤判，回報但不要換。
  7. **主選單測試**：300 秒內出現 DataLoaded，而且到得了主選單。
     - 還是卡住就退回 (a)：停用 Modpocalypse LOTD、NPC Overhaul、Nolvus Awakening NPC Patch 這 3 個插件，並停用 `Modpocalypse NPCs - Legacy of the Dragonborn`、`Pages - LOTD V6 修正` 兩個資料夾（避免 FaceGen 對不上）。再測一次並回報。
  8. **BodySlide**：勾選 Build Morphs 重建（`docs/05` 第 2 節），確認 `Log_BS.txt` 並回報 nif／tri 數量。
  9. **Synthesis**：照 `docs/05` 第 3 節（先用 `--subrecords LAND` 確認 VCLR；加 ESL 旗標；sync-order；check_plugins）。
  10. **`docs/05` 第 4–9 節**：PGPatcher → 草地快取（方案 A）→ xLODGen → TexGen → DynDOLOD（High）→ sync-order／check_plugins／audit_skse。
      - 每個工具執行前：它的輸出資料夾（`pgpatcher_output`、`grass CS`、`lodgen2`、`texgenCS`、`dyndolodCS2`，以及 DynDOLOD 資料夾裡的 `TexGen_Output`、`DynDOLOD_Output`）要不存在或是空的。有內容就停下回報，不要刪。
      - 每個工具跑完、搬好輸出後：跑 `sync-order --apply` 與 `check_plugins`。
        - 除了 `DynDOLOD.esm`、`DynDOLOD.esp`，新的輸出插件如果是完整插件，用 `esl_check --flag` 加旗標。
        - 加不上旗標，或完整插件超過 254，就停下回報。
  11. `docs/05` 第 10 節（第一次用 CS 啟動）→ 回報並推送。
      - 回報內容：各報告的每一行、strip_refs 的刪除清單摘要、主選單結果、各輸出資料夾的檔案數。
      - 第 11 節的測試路線要由使用者玩；第 12 節的 EN-baseline 備份在測試通過後做。
      - DynDOLOD 之前就卡住的話，先回報。
- 2026-09-27｜**第 4 階段完成回報判讀**（回應 1b2d951）。
  - 第 4 階段接受為完成（Dibella 補上後）。`check_plugins` 全過、sync-order 移動 136 個、prune 停用 27 個都沒問題。
  - `mklink` 在 Git Bash 失敗的回報是對的：`docs/04` 7.1 與 phase-commands 已改成 Python `os.link`。
  1. **Dibella：照你的建議**。
     - 在 706051 裡取 `JKs Temple of Dibella - Solitude and Temple Frescoes ESL No Lanterns patch.esp`（ModuleConfig 的 Complete (No Lanterns) - ESL 選項）。
     - 改名成 `JKs Temple of Dibella - Solitude and Temple Frescoes patch.esp`，放進 `JK's Interiors Patch Collection`。
     - Nolvus 的 Mara 等 4 個是舊版 JK 補丁，所以對不上；這不影響判斷。
  2. **修剪的 27 個接受**。其中 2 項之後可能恢復，這一輪先收集資料：
     - `Embershard.esp` 是地點本體，缺的 `SnozzResources.esp` 在 M&V 的「Snozz's Resource Pack」。
     - `Grand Solitude - AI Overhaul patch.esp` 缺的 `AI Overhaul - USSEP Patch.esp` 在 M&V 裡。
     - 兩者都只有在是**輕量插件**時才能加回（理由見第 3 點）。
  3. **完整插件名額：重建後是 254／254，沒有餘裕**。
     - DynDOLOD 官方文件寫明 `DynDOLOD.esm`、`DynDOLOD.esp` 一定是完整插件，會用掉最後 2 個名額。
     - 所以 `Synthesis.esp`、`FNIS.esp`、`Occlusion.esp`、`PG_*` 都必須是輕量插件。Nolvus 手冊也會替 Synthesis.esp 加 ESL 旗標。
     - 新工具：
       - `tools/esl_check.py`：分析插件覆寫了哪些記錄、判斷能不能直接加 ESL 旗標。`--flag --apply` 只改單一連結的輸出檔，硬連結的原檔會被拒絕。`--scan` 列出可騰出名額的候選。
       - `check_plugins` 多一行「輸出重建後的完整插件（預估）」。
  4. **工具設定檔的硬連結**：
     - BodySlide 的 `Config.xml`（來自 Nolvus）和 `D:\PM\tools` 的 DynDOLOD／xEdit 設定檔（來自 M&V）都是硬連結，工具會原地改寫它們。
     - 新工具 `tools/unshare_links.py` 在工具執行前把設定類檔案換成內容相同的獨立副本。來源實例的檔案不變，也不刪除任何資料。
  5. **第 5 階段**：
     - BodySlide 照 Nolvus 手冊 10.3，`docs/05` 第 2 節已寫出具體設定：
       - 3BBB Body Amazing＋CBBE Curvy (Outfit)，不勾 Build Morphs，Batch Build 全選。
       - 衝突時的選擇規則也寫在那一節。
     - Synthesis 清單下一輪才給。Nolvus 手冊（v5）只用 Water Does Damage 與 Remove Landscape Vertex Color 兩個 patcher，v6 內建的 Synthesis.esp 要先分析（第 4 步）才確定。
     - 目標有 SunHelm、Dirt and Blood、Wet and Cold，Water Does Damage 幾乎確定要用。
     - 這一輪只做到 Pandora、BodySlide。Synthesis、PGPatcher、草地、LOD 都依賴最後的插件清單，等恢復項目與 Synthesis 清單決定後再做。
- 2026-09-27｜**接下來的順序**（每步先關 MO2）：
  1. `git pull --rebase`、`python -m pytest -q`。
  2. **Dibella**：
     - 照第 1 點放入，不覆蓋任何檔案。
     - `sync-order --restore-states --apply`：會重新啟用一部分之前修剪的插件。
     - `prune_dependents` 試跑。預期要停用的插件都在上一輪那 27 個之內；有新的名字就先回報。
     - `--disable-folders --apply`。
     - `check_plugins` 應全部 `[通過]`（完整 252）；`verify` 預期缺少 42 個。
  3. **開到主選單**（`docs/04` 第 10 節）：
     - 從 MO2 用 SKSE 啟動，等 Community Shaders 編譯著色器，到主選單後離開，不要開新遊戲。
     - 回報：有沒有到主選單、`skse64.log` 的載入摘要（載入幾個、載入失敗的外掛名稱）、`BackportedESLSupport.log` 的摘要。
     - 當機時：附 crash log 的例外與前 10 行 call stack，去掉使用者名稱。
  4. **收集資料**（都是唯讀）：
     - `python tools/esl_check.py --plugin "<Nolvus 的 Synthesis Patch 資料夾>/Synthesis.esp"`：資料夾名稱照 Nolvus 實際安裝的，通常是 `Synthesis Patch - NOSREX`。
     - 在 `D:\MV\mods` 找 `SnozzResources.esp`、`AI Overhaul - USSEP Patch.esp`，記下所在資料夾，各跑一次 `esl_check --plugin`。
     - `python tools/esl_check.py --scan --pm "D:/PM"`。
  5. **工具設定檔**（工具都先關閉）：
     - `unshare_links --path "D:/PM/mods/BodySlide and Outfit Studio/CalienteTools/BodySlide" --apply`
     - `unshare_links --path "D:/PM/tools" --apply`
  6. **Pandora**：
     - 照 `docs/05` 第 1 節。
     - 關 MO2，跑 `sync-order --apply`（新的 FNIS.esp 會自動啟用並排到目標位置），再跑 `check_plugins`。
     - `FNIS.esp` 如果是完整插件：先 `esl_check --plugin "<Pandora Output>/FNIS.esp" --flag` 試跑，再加 `--apply`，然後重跑 `check_plugins`。
  7. **BodySlide**：照 `docs/05` 第 2 節。
  8. 回報：
     - 各報告的每一行：prune、check_plugins、verify、esl_check ×3、unshare_links、sync-order。
     - 主選單的結果。
     - `Pandora Output`、`BodySlide (Nude)` 的檔案數。
     - BodySlide 衝突視窗裡判斷不了的組。
  9. 推送後**在這裡停下**，等雲端給 Synthesis 清單與恢復項目的決定，再做 Synthesis 之後的步驟。
- 2026-09-27｜**第 4 階段中途回報 5 判讀**（回應 9e62b41）。53 → 16、`audit_skse` 通過，做得很好。以下做法都接受：COTN 的改名放入、Riverwood Falls 的選項、Vanaheimr 的臨時 manifest。
  1. **`_ResourcePack.esl`**：
     - 用 M&V 的 1.6.1170 版（`D:\MV\mods\Creation Club`），esl 與 bsa 都用**硬連結**放進 `D:\PM\STOCK GAME\Data`。不另建 mod 資料夾，也不改 plugins.txt：`Skyrim.ccc` 已列它，遊戲會自動載入，1.71 版標頭由 BEES 處理。
     - 為什麼用這一版：
       - 目標的 LOTD 等插件是對應 1.6.1170 做的。
       - 它和 D:\PM 在同一個分割區，硬連結不佔空間，刪除 D:\MV 後也會保留。
       - Steam 的 1.7.104 版比清單裡任何 mod 都新。
     - 指令在 `docs/04` 7.1。建好後確認大小：esl 78,418、bsa 916,509,890。
  2. **Frescoes：選 (a)，全部改成 Complete (No Lanterns) ESL**：
     - 雲端查證：從 Nexus 預覽的檔案大小判斷，Nolvus 那份 102,436 bytes、有 ESL 旗標的主檔，就是 29695／110913「Complete (No Lanterns) ESL」。有燈籠版是 103.1 kB，No Lanterns 是 102.4 kB，其中只有 ESL 檔帶 ESL 旗標。
     - No Lanterns 和 M&V／Pages 原本的外觀一致。主檔變成 ESL 後，完整插件 253 → 252。
     - `decisions.csv`：`Solitude and Temple Frescoes 2019` 設為新動作 **reinstall**（110913）。`install_archives` 會把舊的 Solitude Only 內容搬到 `_replaced` 再放入新版。
     - 目標 plugins.txt 的 Grand Solitude 補丁改為 `Grand Solitude - Solitude and Temple Frescoes Complete ESL No Lanterns patch.esp`。
       - 808879 的根目錄就有這個檔，fill_plugins 會取出。
       - 舊的 `…Solitude ESP No Lanterns patch.esp` 留在資料夾裡，MO2 會列為停用，不用管。
     - **Dibella**：706051 的選項有三種原始檔（ESL／ESP／No Lanterns）。
       1. 在 ModuleConfig.xml 找 **Temple of Mara** 的同樣三種原始檔，和已安裝的 `JKs Temple of Mara - Solitude and Temple Frescoes Patch.esp`（Nolvus 的硬連結）比對雜湊，確認 Nolvus 選的是哪一種。
       2. Dibella 取同一種，照 FOMOD 改名成目標名稱，放進 Mara 補丁所在的資料夾（和你處理 COTN 的方式相同）。
       3. 不覆蓋任何檔案。三種都對不到就停下來回報。
  3. **其他 24 個缺少前置：接受，由 `prune_dependents` 停用**：
     - 為什麼不補回前置：
       - 缺的是 Pages 沒收的 mod（NewArmoury、TwinbladesOfSkyrim、Nolvus Northern Roads Patch、ClefJ's Dragon Bridge 等）。
       - 完整插件名額只剩 1～2 個。
       - Pages 用的是沒有這些前置的舊版補丁，現在拿不到。
     - 影響：Nolvus 的武器／平衡整合補丁、NR 的 Alternate Start 補丁、Grand Solitude 的 AIO 補丁等不會載入。它們都是整合其他 mod 的補丁，不影響開新遊戲。第 8 階段遊戲測試如果發現相關問題，再回頭處理。
  4. **118 個前置順序錯誤：`sync-order` 現在會自動修正**：
     - 前置排在後面的補丁，會移到它最後一個前置的正下方；依賴它的插件跟著移。其他插件的相對順序不變。
     - 報告多一行「前置順序：移動 N 個…」，完整清單在 `build_instance-sync-order.json` 的 `moved`。
     - 如果出現「ESM 插件以一般插件為前置」或「循環」的 `[注意]`，排序修不了，列出來回報。
  5. **工具缺口**：
     - 1（manifest 把 download 當成 keep）：新增動作 **reinstall**。`meta.ini` 記錄的檔案編號和指定的相同時，會判定為 keep，否則判定為 reinstall。`install_archives` 會把舊內容搬到 `_replaced`；有 FOMOD 的要先手動搬，再用 MO2 安裝（見 `docs/04` 4.2、6.1）。Vanaheimr、Riverwood Falls 已改成 reinstall，這次 manifest 應該判定為 keep，順便驗證。
     - 4：`nexus_fetch` 改依 `downloads\*.meta` 的 modID／fileID 判斷已下載，不再重下。
     - 5：`PBRMaterialObjects` 已加進 install_archives 的已知資料夾。
     - 2、3（讀 ModuleConfig.xml 的 `<files>` 與 `destination`）延後：目前只剩 Dibella 一個需要這樣處理。
     - 文件同步：MO2 裝到**已有內容**的資料夾時一律不選 Replace，先把舊內容搬到 `_replaced`（docs/04、06、07 與 gui-steps 已改）。
  6. **verify 還缺的 15 個**（Dibella 以外）：照 8ec7ae0 捨棄或接受缺少。
- 2026-09-27｜**接下來的順序**（每步先關 MO2）：
  1. `git pull --rebase`、`python -m pytest -q`。
  2. `_ResourcePack` 硬連結（`docs/04` 7.1），確認大小。
  3. `build_instance create --apply`（目標改了一個插件名，會先備份）→ 開 MO2 一次再關。
  4. `manifest`，預期：
     - `Solitude and Temple Frescoes 2019` 是 reinstall。
     - Vanaheimr、Riverwood Falls 是 keep。
     - download 是 0。
  5. 接著：
     - `nexus_fetch`（manifest）：預期下載 110913，其他都是 already_downloaded。
     - `install_archives --only "Solitude and Temple Frescoes 2019"` 先試跑，再 `--apply`。
     - 裝好後重跑 `manifest`，那一列應變成 keep。
  6. `fill_plugins` 試跑 → `--apply`：預期取出 GS 的 Complete ESL NL 補丁，其他都是找不到來源。
  7. Dibella 照上面第 2 點放入。
  8. `sync-order --restore-states --apply` → `verify` → `audit_skse` → `check_plugins`，預期：
     - `verify` 缺少 15 個。
     - `check_plugins` 的前置順序錯誤是 0，缺少前置約 24 個（沒有 `_ResourcePack`）。
  9. `prune_dependents` 試跑，看 `reports\prune-plan.csv`。出現下列任一情況就**先回報，不要 apply**：
     - 要停用的插件超過 60 個。
     - 包含任何 `.esm` 或有 ESM 旗標的插件。
     - 包含 `LegacyoftheDragonborn*`、`Grand Solitude.esp` 這類本體。
  10. 其他情況就 `prune_dependents --disable-folders --apply`，再跑 `check_plugins`（應該全部 `[通過]`）與 `verify`（缺少的數量會加上被修剪的插件，這是預期的）。
  11. 回報第 4 階段完成：
      - 各報告的每一行。
      - prune 停用的插件與原因（`prune-plan.csv` 的 remove 列）。
      - 建議停用的資料夾。
      - sync-order 移動的插件數。
  12. 推送後等雲端給第 5 階段的 BodySlide 預設與 Synthesis 清單，再開始第 5 階段。
- 2026-09-27｜**第 4 階段中途回報 4 判讀**（回應 4b35210）。622 → 53 做得很好。`locate_instance` 的 NTFS 修正與新增的 `plugin_sources.csv` 前綴都接受。
  - `--plan-downloads` 的佔位檔案編號問題已修：「檔案編號＝mod 編號」或空白的候選不會再填入假的編號，note 會寫「需要在 Nexus 選檔」。
  - fill_plugins 新增：壓縮檔裡的插件在 FOMOD 選項資料夾時，連同那個資料夾的模型、材質一起放入（這次你手動補的 43 個檔就是這種情況）。
  - **53 個的處理**（雲端用 Nexus 的 `modFileContents` 查詢找到來源，它能用檔名搜尋壓縮檔內容）：
    - **下載後由 fill_plugins 補**（已加進 `data/extra_archives.csv`）：
      - Hall of Forgotten 2.4.26（DBM_HUB ×3）、HoF TCC 4.9（LOTD_TCC ×3）、LOTD CC Patch Hub 6.0.14（DBM_CC ×8）。
      - Praedy's College of Winterhold 626072（Banner）。
      - NR Tents Animated 573637、NR Patch Collection Addons 448633（COTN Dawnstar Ships Lux Orbis、Skybound、Thunderchild、Wintersun）。
      - Psychopatchist Purgatory 0.15（DK Nord Ships ×2、Lux Via DK Nord Ships）。
      - TSOS 637231（已封存、頁面隱藏：下載不到就把 TSOS_Armor_Vilkas、TSOS_Sven_Lute 列為捨棄）。
    - **目標改用新名稱**（`data/target/plugins.txt` 已改；新版在 M&V 擷取來的資料夾裡應該已經有）：
      - `Orc Exiles - Bilegulch - 3DNPCs - IFD Lydia patch.esp`
      - `Lux Orbis - Orc Exiles - Bilegulch Patch.esp`
      - `Lux - Orc Exiles - Bilegulch Patch.esp`
    - **過時或被取代，接受缺少**：
      - `Northern Roads - Fortified Morthal.esp`：目標同時有新名 `…Fortified Morthal Patch.esp`。
      - `Orc Exiles - Bilegulch - Ryn's Dragon Mounds patch`、`… - Ryn's Lost Valley - 3DNPCs patch`：2.0 已移除。
    - **JKs Temple of Dibella - Solitude and Temple Frescoes patch**：706051 裡是 ESL／ESP／No Lanterns 三種檔案，由 FOMOD 安裝時改名。
      - 用 MO2 安裝 706051 到「JK's Interiors Patch Collection」、選 **Merge**，只勾 Temple of Dibella Frescoes，確認產生的插件名稱。
    - **COTN Dawnstar 的 2 個 LotD 補丁、Ryns WCL Water for ENB (Shades of Skyrim)**：
      - 在已下載的 725411 與 755856 的檔案清單裡，找名稱含 LotD／Legacy、Water for ENB 的插件。
      - 找到新名稱就回報（雲端再改目標名稱）；沒有就捨棄，不要混用舊版。
    - **捨棄**：
      - 表 B 的 8 個：照你的判斷，`Horsepower_Ragdoll - SC Horses Patch.esp` 在 prune 時停用，可以接受。
      - `[Fix] Lux Orbis … Revert Bridge.esp`、`Ancientland - Valtheim Statues Patch.esp`、`ModpocalypseNPCs-LotDV6-ErrorFixes.esp`：使用者自製或找不到。
    - **Terrain Helper**：目標加了「Terrain Helper」資料夾（放在 `Powerofthree's Tweaks 1.15.1` 後面），`decisions.csv` 設為 harvest_mv。M&V 那一版支援 1.5.97，有 ESL 旗標。
  - **A 組**（`decisions.csv` 已寫）：舊內容先**搬到** `D:\PM\_replaced`（不是刪除）。
    - Vanaheimr Mines and Caves 改裝 PBR 2k 724119（2k 即可）。
    - Riverwood Falls 用 633042（1.2.1）的 FOMOD 重裝，選項照目標插件。
  - **DLL**：
    - **SMP Wind**：`hdtSMP64.dll` 改名 `hdtSMP64.dll.mohidden`。SMP Wind NG 透過 FSMP 的介面運作，不需要它。這一步要在遊戲啟動前完成。
    - **Dova Jump**：沒有 1.5.97 版，改裝 0.6.1（704417，只有 OAR 動畫）。舊內容搬到 `_replaced`。
    - **Skyrim Souls RE - Updated**：這個資料夾其實是原作 27859（舊名 Skyrim Souls RE - Updated），不是我們先前對應的 155280（只有 DLL 的修正版）。
      - 改裝 27859／754726（v3.1.2，和 1.5 移植版同版，已封存；下載不到改用 810395 v3.2.0）。
      - 裝好後把它的 `SkyrimSoulsRE.dll` 改名 `.mohidden`，由上方的「Skyrim Souls RE for Skyrim 1.5」提供 DLL。
- 2026-09-27｜**接下來的順序**（每步先關 MO2）：
  1. `git pull --rebase`、`python -m pytest -q`。
  2. 目標改了（多一個資料夾、改了 3 個插件名稱），重建 `_expected`：
     - `build_instance.py create --pm "D:/PM" --ini-from "D:/Nolvus/Instances/Nolvus Awakening/MODS/profiles/Nolvus Awakening" --apply`（會先備份設定檔）。
     - 開 MO2 一次再關。
  3. `harvest --from mv --instance "D:/MV" --pm "D:/PM" --plan data/decisions.csv --apply`（Terrain Helper）。
  4. `manifest` → `nexus_fetch`（manifest）→ `nexus_fetch --manifest data/extra_archives.csv --apply`。
  5. A 組、Dova Jump、Skyrim Souls RE 重裝；SMP Wind 的 DLL 改名。
  6. `fill_plugins --apply`；Frescoes 用 MO2 Merge 安裝；查 COTN／Ryn's 的新名稱。
  7. `sync-order --restore-states --apply` → `verify` → `audit_skse`（應該沒有 `[失敗]`）→ `check_plugins`。
  8. 回報：各報告的每一行，加上 `verify` 還缺的插件清單。
  9. 如果剩下的都是上面「接受缺少／捨棄」的項目，雲端確認後就跑 `prune_dependents`（試跑 → 看 `prune-plan.csv` → `--disable-folders --apply`），完成第 4 階段。
- 2026-09-27｜**第 4 階段中途回報 3 判讀**（回應 cb90a4e）。本地新增的工具（install_archives、`--restore-states`、nexus_fetch 修正）都接受。
  - 雲端的 Linux 上有 1 項測試失敗：`test_install_archives.py::test_folder_names_compare_case_insensitively`。它假設資料夾名稱不分大小寫（NTFS 的行為），在筆電上會過，不用處理。
  - **622 個缺少的目標插件**：新工具 `tools/fill_plugins.py`（說明在 `docs/04` 8.1），對應規則在 `data/plugin_sources.csv`。用你的 `missing_target_plugins.csv` 模擬的結果：
    - 從 M&V／Nolvus 安裝補上約 254 個：同名 178、手動對應 57、名稱加數字後綴 19。
      - `Lux Orbis` 本體整個合併進 `Lux Orbis cs`；`Thrones Expanded - Base Object Swapper` 整個合併進 `Thrones Expanded`。
    - 從已下載的壓縮檔補上約 24 個。
    - 約 324 個有候選合集，用 `--plan-downloads` 下載後再補。
    - 約 20 個沒有候選，例如 HorseAnimaTest、H2135、Curious Adventurer 這些已捨棄 mod 的插件，以及 TerrainHelper、Occ_Skyrim_*（Occ_* 會依已存在的同前綴插件找到資料夾）。
  - **10 個錯檔**：已改 `data/decisions.csv`。
    - 改檔案：
      - Dreadful Alduin → 578737（Graphics Only 4K；下載不到改 578735）
      - RUSTIC SOULGEMS → 12945（2K Unsorted）
      - HFs Whiterun bridges → 662495（沒有 ESP 的 2K 版）
      - Blubbo → 503110
      - Mostly Treeless Tundra - Northern Scenery Tundra → 154818／717711（Patches Collection 頁面）
      - Orc Strongholds - AIO - EFPS Patch → 150246／627969（AIO 頁面）
      - Load Screen Compendium → 625267（**16:9** 2K，同為 2.1；筆電是 16:10，不要用 21:9）
    - The Restless Dead - At Your Own Pace Patch → `harvest_nolvus`（Nolvus 有同名資料夾）。
    - Thrones Expanded、Myrwatch VaultFix 照原檔安裝。它們的 esp 不在目標，會是停用；BOS 插件由 fill_plugins 補。
    - NotWL Animations Addon：主檔照裝，再用 MO2 Merge 裝 669507（PLUGINS FOMOD，預設擺動幅度）。
  - **Yggdrasil**：你選 Yggdrasil Trees (both) 是對的（note 已更正）。
  - **Maerchenwald**：只裝 3418「The Archwood Lite」，3419 改為 drop。
  - **合併安裝的第二個檔**：列在新的 `data/extra_archives.csv`，用 `nexus_fetch.py --manifest data/extra_archives.csv --apply` 下載，再用 MO2 安裝到同一資料夾、選 **Merge**：Fortified Morthal 707429、Modern Hay 652905、Dwemer Backpack 723624、NotWL 669507。
    - 其中 MyrTE 664142 不用裝，fill_plugins 會只取出 esp。
  - **FOMOD 選擇**：全部接受。
    - BnP 維持 no frostnip 預設（目標沒有 Frostnip 相關 mod）。
    - Lux CS 的 LightPlacer 可以；Vigilant／Unslaad 英文加 Silent Voice 可以；Bladedancer ESL 可以。
    - 為了筆電改選的 CVEO 512p、Ivy 2k、Wolves 2k、Texture Downscaler BALANCED、Water for ENB 2K、CS Lights 不裝窗戶光源，都可以。
    - Load Screen 照上面改 16:9。
    - 你的 Snazzy `.esp.esp` 更正、Riverwood Falls 直接放 esp、SDA／Wayshrines 手動取出、FWMF 的 `.mohidden`、DBVO Fix 維持停用、DIP 產生的 Edge UI Racemenu：都正確。
  - **MO2 外掛**：
    - 關 MO2 後，把 `D:\PM\plugins\crashlogtools` 整個資料夾**搬到** `D:\PM\_disabled_plugins\`。在設定裡停用不夠。
    - PageFile Manager 也一樣搬走：它會改 Windows 分頁檔，而分頁檔已在第 1 階段設定好。
    - 這是搬移不是刪除，不必問使用者；`D:\MV` 裡的原檔不受影響。
  - **guard.py**：改成純 ASCII 的 JSON 輸出，cp950 主控台下 `test_guard_hook` 應該全過。
  - `D:\PM\tools\DIP_extract\fomod` 的 3 個小檔可以留著，第 8 階段再一起清。
- 2026-09-27｜**接下來的順序**（每步先關 MO2）：
  1. `git pull --rebase`，跑 `python -m pytest -q`。
  2. 搬走上面兩個 MO2 外掛。
  3. `manifest` → `nexus_fetch`（manifest）→ `nexus_fetch --manifest data/extra_archives.csv` → `install_archives`（需要時加 `--accept`）→ 要 Merge 的用 MO2 裝。
  4. `harvest --from nolvus --plan data/decisions.csv --apply`（補 The Restless Dead 的 AYOP 補丁）。
  5. `fill_plugins` 試跑 → 看 `fill_plugins.csv` → `--apply`。
  6. `--plan-downloads` → `nexus_fetch --manifest reports/fill_plugins_downloads.csv --limit 100 --apply`（會下載多個補丁合集，先看清單大小）→ 再跑 `fill_plugins --apply`。
  7. `sync-order --restore-states --apply` → `verify`。
  8. 回報：
     - 各報告的每一行。
     - `fill_plugins.csv` 裡還剩下的 `ambiguous`／`unresolved`（插件名稱、candidates、note）。
     - `verify` 還缺幾個。
  9. **還不要跑 `prune_dependents`**，等雲端看過剩下的清單再決定。
- 2026-09-26｜**DLSS 5**（使用者詢問）：結論寫在 `docs/07` 3.4 節。
  - Skyrim 只有非官方的實驗模組；開了很吃效能，而且要關掉 CS 的 Upscaling 與 HDR。
  - 第 4–7 階段**不要安裝**任何 DLSS 5 相關檔案（DynamicShaderFrameGen、`nvngx_dlssnr.dll`、ReShade DLSS5 套件）。
  - 使用者想試的話，等第 8 階段備份之後，先回報雲端再開始。
- 2026-09-26｜**第 4 階段中途判讀**（回應 74772e8）。補擷取、`build_instance`、modlist 比對都正確；Nolvus 安裝清單已收到。
  - **review 54 個已決定**（寫進 `data/decisions.csv`）：
    - 50 個 `download`，含 Nexus 檔案編號。
    - 4 個 `drop`（Nexus 找不到）：Unslaad PBR、clockwork pbr、horseAnimations2、Smooth Special Idle。它們的插件（例如 HorseAnimaTest.esp）交給 `prune_dependents` 處理。
  - **缺檔案編號的 20 個 download** 也補上了。
  - **replace_dll**：
    - 5 個要換成 1.5.97 版：Flat World Map Framework2、CRDW、Face Discoloration Fix、Native EditorID Fix、Classic Sprinting Redone。檔案編號和 FOMOD 選項寫在 note。
    - Flat World Map Framework2 **不要勾 Baka World Map Speed**：它沒有 1.5.97 版，放棄（只影響地圖拖曳速度）。
    - 3 個改為 `keep`：Dynamic Armor Variants（上方的 1.5.97 移植版資料夾下載後會覆蓋）、I4、COCKS（上方的「- Patch」資料夾已提供 1.5.97 DLL，`audit_skse` 已確認）。
  - **note 欄要照著做**：
    - 裝兩個檔合併到同一資料夾：Fortified Morthal、Modern Hay、Dwemer Researcher Backpack。第二個檔用 MO2 安裝時選 **Merge**。
    - FOMOD 指定選項：ERM 選 PBR、MOIST 選 BOS、Yggdrasil 選 Floating Tree、各 Patch Hub 只選目標 plugins.txt 裡有的補丁、Asura's Guard 選 3BA 2K。
    - 已封存或舊版的檔案（Vigilant 657510、ParticleWind 752520、Prisma UI 735761、Dirt Cliffs 759225）下載不到時，照 note 改用替代檔，或回報。
    - Edge UI Racemenu 是 DIP 補丁：要用 Dynamic Interface Patcher（Nexus 96891）產生輸出，放進這個資料夾。做不到就先略過並回報。
    - note 以「中：」開頭的是中等信心：裝完看插件名稱是否和目標相符，不符就回報。
  - **OpenSSL**：你的處理正確。`build_instance create` 以後會自動把 `dlls\libssl-3-x64.dll` 複製到根目錄。這台已經有了，不必重跑。
  - **crashlogtools**：到 MO2 設定 →「Plugins」停用 **Crash Log Labeler**。不要改外掛的 .py 檔（它和 `D:\MV` 是硬連結）。
  - `manifest.py` 更新：`replace_dll` 的決定在資料夾換好（沒有 AE DLL）後會變成 `keep`，所以重跑不會一直要求重裝。
- 2026-09-26｜**第 4 階段接下來**：
  1. `git pull --rebase`，停用 Crash Log Labeler。
  2. 請使用者在 MO2 設定 →「Nexus」連結帳號。建議使用者也照 `docs/09` 第 3 節設定 `NEXUS_API_KEY`（使用者自己設定，不要貼進對話），約 450 個檔案用 `nexus_fetch.py` 批次下載比較快。
  3. 重跑 `python tools/manifest.py --pm "D:/PM"`。預期：review 0、download 約 445、replace_dll 5、drop 20、keep 約 3567、regenerate 9。數字差很多時先回報。
  4. 下載並用 MO2 安裝（名稱照 `folder` 欄，FOMOD 照 note 或 plugins.txt）。可以分批做，每批結束更新 `status.md`。
  5. replace_dll 的 5 個資料夾已經有內容，用 Replace 重裝前**一次列出來問使用者**（Replace 會刪掉舊內容；`D:\MV` 的原檔不受影響）。
  6. 全部裝完、`manifest` 沒有 download／review／replace_dll 後，照 `docs/04` 第 8、9 節：`prune_dependents` → `sync-order` → `verify` → `check_plugins` → `audit_skse`（不加 `--mv-1597-map`）。
  7. 回報各報告的每一行，特別是 `check_plugins` 的完整插件數、缺少的前置，以及 `audit_skse` 的 `[失敗]`。
  - 下載途中有檔案下載不到（封存、隱藏、成人內容）時，記下來一起回報，先繼續其他的。
- 2026-09-26｜**第 3 階段判讀：通過**（回應 1af902e）。可以進第 4 階段。
  - **STOCK GAME 顯示 1.0.0.0**：工具的 bug，已修正。Nolvus 降版後的 exe 數字欄位是 1.0.0.0，字串才是 1.5.97.0；`pe.file_version` 現在遇到 1.0.0.0 會改讀字串。
    - 沒修的話，第 4 階段 `audit_skse` 會誤報「STOCK GAME 遊戲版本」`[失敗]`。
    - 第 3 階段不必重跑。第 4 階段若仍顯示 1.0.0.0，要回報。
  - `ReShade.log` 已加進 harvest 的 ENB 移除清單。`D:\PM\STOCK GAME` 裡現有的那個無害，不必刪。
  - **來源缺少 12 個**，都寫進了 `data/decisions.csv`：
    - 6 個 `harvest_mv`（從 `D:\MV` 擷取）：Cached Recursive Directory Walk、Collision Sentinel - Crash Fix、Media Keys Fix SKSE、KreatE、Native EditorID Fix、SKSE Menu Framework2（對應 M&V 的 `SKSE Menu Framework`）。
    - 6 個 `download`（含 Nexus 編號）：SkyPatcher Keyword Framework、Quest Journal Overhaul、Prisma UI、Dirt Cliffs Enhancement - High Quality Ivy、Modern First Person Animation Overhaul、Dawnguard Arsenal - Scabbardless Greatswords Loose File Replacers。
    - Prisma UI 1.4.1 與 Dirt Cliffs 1.3.0 是封存檔。下載不到時，改用 note 寫的新版檔案，並在回報中說明。
    - 其中 SKSE 外掛（例如 CRDW、Collision Sentinel、Media Keys Fix、KreatE、Native EditorID Fix、Prisma UI）是否能在 1.5.97 載入，交給 `audit_skse` 判斷。
  - **裸體版已加進目標**：
    - `data/target/modlist.txt`：在 `Highly Improved Male Body Overhaul` 後面加入 `The New Gentleman - Nolvus Settings`、`The New Gentleman`，並把 `BodySlide (Dressed)` 改名為 `BodySlide (Nude)`（第 5 階段重建）。
    - `plugins.txt`：`TheNewGentleman.esp` 放在 `TrueHUD.esl` 前面。它有 ESL 旗標，不佔完整插件名額。
    - provenance 已重跑：harvest_nolvus 從 2931 變成 2933，其他不變。
    - `docs/05`、`docs/08`、`gui-steps.md` 的輸出資料夾已改名。
  - **可以推送** Nolvus 實際安裝的 `modlist.txt`、`plugins.txt`、`loadorder.txt`：
    - 放到 `data/snapshots/nolvus-6.0.20-installed/`，照原樣複製，不要改排序或換行。
    - 推送前確認內容只有 mod 與插件名稱，沒有路徑或使用者名稱。
  - `D:\MV` 仍保留到第 4 階段 `manifest` 跑完、補擷取完成、雲端判讀後再刪（先問使用者）。
- 2026-09-26｜**第 4 階段開始時先做**（`docs/04` 第 1 節與 `phase-commands.md` 已更新）：
  1. `git pull --rebase`。
  2. 補擷取 M&V：`python tools/harvest.py --from mv --instance "D:/MV" --pm "D:/PM" --plan data/decisions.csv`，看過結果（應該 6 個完成）再加 `--apply`。
  3. 補擷取 Nolvus（**不加** `--stock-game`）：`python tools/harvest.py --from nolvus --instance "D:/Nolvus/Instances/Nolvus Awakening" --pm "D:/PM"`，應該多 2 個（The New Gentleman），再加 `--apply`。
     - 「來源缺少」仍會顯示那 6 個要下載的，屬正常。
  4. 接著照 `docs/04` 進行：`manifest` → `build_instance create` → 第一次開 MO2 → `verify` → 下載。
     - `audit_skse` 不加 `--mv-1597-map`。
     - `nexus_fetch.py --apply` 需要 `NEXUS_API_KEY`，而且是實際下載。使用者已授權從 Nexus 下載，不必另外問。
  5. 在 `manifest`、`build_instance verify` 之後先回報一次：各報告的每一行、`manifest` 各 action 的數量、所有 `review` 項目的資料夾名稱。雲端再決定 review 的來源與 replace_dll 的替代版本。
  - BodySlide 的 preset 等第 5 階段指示，會在第 4 階段回報後給。
- 2026-09-26｜**第 2 階段判讀：通過**（回應 79cf305）。
  - `harvest-mv` 的 `[注意]`：`ImmersiveHUD SKSE`、`Load Time Profiler` 在 M&V 2.6.2 裡是停用的空項目（`.wabbajack` 沒有檔案）。已寫進 `data/decisions.csv`，含 Nexus 編號，第 4 階段 `manifest` 會列入下載。
    - ImmersiveHUD SKSE：166799／檔案 753834（for Skyrim 1.5，3.2.2）。
    - Load Time Profiler：173928／檔案 730415（1.2.2），第 4 階段 `audit_skse` 確認能在 1.5.97 載入。
    - 之後若再跑 `harvest --from mv`，這 2 個仍會顯示「來源缺少」，屬正常。
  - `zh_extract_official` 的「字形判斷 unknown」：工具只抽第一個表，而它剛好是空表。已改成逐一判斷所有表、跳過空表。你的逐表檢查（有內容的全是繁體）就是結論，**不必重跑**。
  - SteamDB 被驗證頁擋住時，改用 appmanifest 的 `buildid`＝`TargetBuildID` 加上 Steam 新聞確認：接受。不要嘗試繞過驗證頁。
  - **可以問使用者刪 `D:\WJ-Downloads`**。刪除前照 CLAUDE.md 說明：報告沒有 `[失敗]`、`D:\PM` 的硬連結不受影響。`D:\MV` 保留到第 4 階段 `manifest` 跑完。
  - 原版遊戲 `文件` 裡的 `Skyrim.ini`／`SkyrimPrefs.ini`：使用者決定**先不用管**，不要改。
- 2026-09-26｜**裸體版：使用者決定最後的 `D:\PM` 也用裸體版**（與 Nolvus 的 Nudity Yes 一致）。
  - Nolvus 裝完後，照 `docs/03` 第 6–8 節完成（第一次啟動、備份 Profile、inventory、harvest `--stock-game`）。第 3 階段回報除了各報告的每一行，另外附上：
    1. Nolvus 設定檔 `MODS\profiles\Nolvus Awakening\modlist.txt` 裡，所有名稱含 `New Gentleman` 或 `Nude` 的行，每行連同上下各 2 行，照原樣抄。
    2. 這些資料夾裡的插件（`.esp/.esm/.esl`）名稱，以及是否有 ESL（light）旗標。
    3. 這些插件在 Nolvus `plugins.txt` 的行號與前後各 2 行。
    4. `BodySlide (Nude)` 資料夾的大小與檔案數。
  - 雲端收到後才會改 `data/target`、重跑 provenance，並更新 `docs/05` 的 BodySlide 輸出資料夾。之後再跑一次 harvest（`--apply`）就會補上 The New Gentleman。**現在不要自己改清單。**
  - `decisions.csv` 現在是 6 欄（多了 Nexus 編號），`docs/04` 已更新。
- 2026-09-26｜**Rare Curios 衝突判讀**（回應 1ae35a6）。使用者同意的做法可以執行，但要照下面的順序並加上檢查：
  1. **等 Wabbajack 完全裝完**（結果頁顯示完成）。在那之前不要動 Steam 遊戲資料夾。
     - 確認 `D:\MV\Stock Game\Data` 已有 `ccbgssse037-curios.bsa/.esl`。
     - 用 `Get-FileHash` 比對，確認它們與 Steam 資料夾裡的檔案相同。
  2. 把 Steam 資料夾裡 Steam 版的這 2 個檔**搬到** `D:\Backup\Curios-Steam`。這是搬移不是刪除，使用者已同意。
  3. **啟動前確認不會被更新**，三項都要符合，任何一項不符就停下來回報：
     - Steam 遊戲庫的按鈕是「開始遊戲」（PLAY），不是「更新」。
     - Steam 下載頁沒有 Skyrim 的排程。
     - SteamDB 上 Skyrim SE 公開分支的 build 仍是 24914197。
  4. **允許這一次**從 Steam 啟動遊戲，這是「第 3 階段前不從 Steam 啟動 Skyrim」的唯一例外：
     - 主選單 → CREATIONS，只下載 Rare Curios。
     - 沒有單項下載的選項時，可以用 OPTIONS →「Download all owned Creation Club Creations」。其他 CC 重下後內容不變：Fish、Survival、Saints & Seducers 在第 1 階段已驗證雜湊相同，其餘本來就是 Creations 版。
     - 不載入存檔、不購買任何東西，下載完就離開。
  5. 核對：
     - 兩個檔的 Wabbajack xxHash64 應為 `FQbA20bA5Dw=`（bsa）／`it6+eSu4OCw=`（esl）。
     - 遊戲仍是 1.7.104.0、build 24914197，CC 仍是 74 個。
     - 把這兩個 Creations 版檔案**複製**一份到 `D:\Backup\Curios-Creations`。
  6. 重開 Nolvus Dashboard，照 1ae35a6 回報的同一組選項再選一次，確認版本是 6.0.20：
     - D 槽剩餘 **≥ 500 GB**：直接開始安裝，不必等刪 `D:\WJ-Downloads`。預估 M&V 裝完約剩 545 GB，Nolvus 要約 456 GB。
     - 不足 500 GB：照上一條的快速路線，先刪 `D:\WJ-Downloads`（先問使用者）。
     - 若遊戲檔檢查又報「Hash … does not match」（不論哪個檔）：停下來，把 `Log.txt` 的相關行寫進 `local-report.md` 回報。不要試其他版本的檔案。
  7. 第 2 階段的工具（inventory、harvest、extract_official）只讀 `D:\MV`，可以和 Nolvus 安裝同時跑。
- 2026-09-26｜其他問題的判讀：
  - **`D:\PM` 用 Nolvus 的 Creations 版 Curios。**
    - `D:\PM\STOCK GAME` 來自 Nolvus。目標清單裡跟 Curios 有關的 patch 全部來自 Nolvus（`harvest_nolvus`），都是依 Nolvus 的版本做的。例如 LOTD Creation Club Patch 的 `DBM_CC_*CuriosAddon.esp`、`LOTD_TCC_RareCurios.esp`，以及 Creation Club Crossbow Integration、Midwood Isle／Wyrmstooth／Apothecary 的 Curios patch。
    - `Argentum - Rare Curios Add-On 01` 不在目標清單裡。
    - 第 4 階段 `check_plugins` 照常執行即可。
  - **Dashboard 沒有 Enemies Resistance、Stances Perk Tree 開關：可以。**
    - 這兩個開關是 6.0.21 才加的；nolvus.net 的清單是 6.0.21 版。
    - 目標用的是舊版 `True Armor` 2.5.2 與舊版 `Nolvus Awakening Stances Perk System`，在 6.0.20 是基本內容。
    - Nolvus 裝完後，若 `harvest-nolvus` 的「來源缺少」出現 True Armor 或 Stances 相關資料夾，要回報。
  - **Nudity No、True Nord 預設細項：正確。** 目標清單裡有 Nude 選項的 mod 是 0/4，Milk Drinker 選項的 mod 是 0/9。
  - Dashboard 用 32 條連線下載官方 `Binaries3811.zip`（大小與 CRC 相符）再解壓：接受。
  - 手冊已補上 Curios 的說明（`docs/01` 第 4 節、`docs/02` 常見問題、`docs/03` 選項表與常見問題）。
- 2026-09-26｜**Nolvus 何時可以和 M&V 同時安裝**（取代下一條的第 5 點）。使用者另外清出 100 多 GB，D 槽目前剩約 1 TB：
  1. **M&V 還在下載時，不要開始安裝 Nolvus**：兩者分同一條頻寬，只會拖慢 M&V。Dashboard 的準備照下一條第 1–4 點做。
  2. **Wabbajack 下載完、切到安裝階段時**，用 PowerShell `Get-PSDrive D` 量 D 槽剩餘空間，並記在 `status.md`：
     - 剩餘 **≥ 950 GB**：可以開始安裝 Nolvus（照 `docs/03`，先確認版本是 6.0.20）。
       - 依據：M&V 還要 386 GB，加上 Wabbajack 餘裕 60 GB；Nolvus 要 426 GB，加上解壓暫存約 30 GB；再留 50 GB 安全餘裕，合計約 950 GB。
     - 剩餘 < 950 GB：照原順序，等 M&V 完成。
  3. 兩者同時安裝時，使用者回來說「繼續」，先看 D 槽剩餘：
     - 低於 50 GB：在 Dashboard 停止 Nolvus 安裝（之後可以續裝），讓 M&V 先完成。
     - 兩個安裝都不要中途關閉程式。
  4. **快速路線（依原順序時）**：
     - 條件：Wabbajack 結果頁沒有錯誤，而且第 2 階段各份報告都沒有 `[失敗]`。
     - 做法：不必等雲端判讀。推送 `status.md` 與 `local-report.md`（先問使用者）→ 問使用者刪 `D:\WJ-Downloads`（刪除前照 CLAUDE.md 說明）→ 刪完立刻開始安裝 Nolvus。
     - `[注意]` 在回報裡說明即可，雲端之後補判讀。
     - 有任何 `[失敗]`：照舊等雲端判讀。
  5. 其餘規則不變：
     - 版本必須是 6.0.20。
     - 不從 Steam 啟動 Skyrim。
     - 不按 Wabbajack 或 Nolvus 的更新。
     - `D:\MV` 保留到第 4 階段 `manifest` 跑完。
- 2026-09-26｜**不要同時安裝 Nolvus**：M&V 未完成前，D 槽峰值會達約 1050–1070 GB，超過剩餘的約 1047 GB。現在可以先做 Nolvus 的準備，但停在按安裝之前：
  1. 下載 Nolvus Dashboard 到 `D:\Nolvus` 並完成安裝，確認版本 ≥ 3.8.11。
  2. 登入 nolvus.net 帳號，連結 Nexus（SSO）與 mega。
  3. 建立 Nolvus Awakening 實例，照 `docs/03` 的表格選好所有選項（Ultimate、不含 SR Exterior Cities、TAA、16:9、Edge、Fantasy Combat、其他附加元件全勾、True Nord、English、關閉封存），並截圖確認。
  4. 確認提供的版本是 **6.0.20**；若是 6.0.21，停下來回報。
  5. **不要按開始安裝。** 等 M&V 完成、第 2 階段的工具跑完、`D:\WJ-Downloads` 刪除後（刪除前問使用者），才開始安裝 Nolvus。
  - Wabbajack 正在跑時，不要從 Steam 啟動 Skyrim，也不要讓 Dashboard 做任何會改動 Steam 遊戲資料夾的動作。
- 2026-09-26｜已收到第 1 階段補推送（`e20f528`）。GitHub 中繼運作正常，第 2 階段照原指示進行。
  - preflight 的 VRAM 分級已修正：廠商回報的容量常略低於標示（16 GB 顯示 15.9 GB），現在 15.9 GB 會歸到 16 GB 級（Tier A/S）。第 1 階段不必重跑。
  - 第 2 階段完成時，`local-report.md` 請包含：
    - `inventory-mv`、`harvest-mv`（試跑與 `--apply` 各一份）、`zh_extract_official`（試跑與 `--apply`）每份報告的每一行
    - Wabbajack 結果頁有無錯誤或警告
    - 完成後 D 槽剩餘空間
  - 推送後等雲端判讀，再問使用者刪 `D:\WJ-Downloads`。
- 2026-09-26｜第 1 階段判讀：**通過，可以進第 2 階段。**
  - Python 3.13.11（miniconda）可用：工具需要 3.12 以上，第 6 階段的四個套件都有 Windows 的 3.13 版本。不必另裝 3.12。
  - 分頁檔「C 槽系統管理＋D 槽固定 40960 MB」接受，不用改（RAM 64 GB，總量足夠）。
  - `文件\My Games\Skyrim Special Edition\Skyrim.ini` 的 `sLanguage=CHINESE` 不影響：M&V 與 Nolvus 的 MO2 都用設定檔自己的 ini（LocalSettings=true）。不要改它，也不要刪。
  - preflight 的 Defender 誤報已修正：一般權限時改報 [資訊]。
  - **不要**下載 M&V 2.40.1（file 703199）：它已從 Wabbajack CDN 下架，只剩 Nexus 封存檔（約 5 GB）。第 4 階段 `audit_skse` 找出真正不能在 1.5.97 載入的 DLL 後，雲端再逐一查 1.5.97 版本。第 4 階段執行 `audit_skse.py` 時不要加 `--mv-1597-map`。
  - **第 3 階段前，不要從 Steam 啟動 Skyrim**：若 Bethesda 推出新版，啟動時會被更新，Wabbajack 與 Nolvus 的檔案檢查就會失敗。
  - `git pull` 一律改用 `git pull --rebase`。
  - 階段結束時要把 `status.md` 與 `local-report.md` 一起 **push**（這次的 b22a09a 只提交沒推送）。
- 2026-09-26｜第 2 階段注意事項：
  - Wabbajack：Install Location `D:\MV`、Download Location `D:\WJ-Downloads`。需要約 616 GB，D 槽剩約 1047 GB，足夠。C 槽只剩約 153 GB，不要把任何下載或安裝位置設在 C 槽。
  - 安裝完成後依序執行：inventory → harvest 試跑 → harvest `--apply` → `pip install lz4` → extract_official 試跑 → `--apply`，並把每份報告的結果寫進 `local-report.md` 後推送。
  - 刪除順序（刪除前都要問使用者）：
    1. 先刪 `D:\WJ-Downloads`（約 230 GB）。
    2. `D:\MV` 保留到第 3 階段 Nolvus 裝好、第 4 階段 `manifest` 跑完再刪，萬一需要重新擷取還能用。刪 WJ-Downloads 後 D 槽約剩 660 GB，夠裝 Nolvus（426 GB）。
- 2026-09-26：連線測試確認本地與雲端互相看不到，SendMessage 不通。改用 GitHub 中繼：
  - 本地寫 `progress/local-report.md`，連同 `status.md` 提交並推送。
  - 使用者回雲端說「已推送」。
  - 雲端的回覆寫在這個檔案。
- 2026-09-26：從第 1 階段開始。依 `docs/01-準備筆電.md` 完成後執行 `python tools/preflight.py --install-drive D:`，把 `reports/preflight-*.txt` 的每一行結果寫進 `local-report.md` 後推送。
