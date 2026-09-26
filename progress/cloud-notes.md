# 雲端給本地代理的指示

雲端 Claude 對話（識別碼 `0e5bdc`；顯示名稱會變動，例如 `test-25`、`test-17`）把判讀結果、決策與修正寫在這裡，並提交到分支 `claude/sharp-faraday-b8ax3h`。
本地代理每個階段開始前 `git pull` 後閱讀；已處理的項目在 `progress/status.md` 註記。
個別資料夾的動作覆寫寫在 `data/decisions.csv`（`folder,action,note,nexus_mod_id,nexus_file_id,nexus_version`，後三欄可留空），`tools/manifest.py` 會自動採用。

## 最新指示
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
