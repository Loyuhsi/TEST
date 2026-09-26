# 進度（本地代理更新；只寫進度與結論，不貼報告內容、不寫硬體序號或金鑰）

最後更新：2026-09-26
目前階段：2（Wabbajack 安裝 M&V 中）

| 階段 | 狀態 | 完成日期 | 結論／待決問題 |
|---|---|---|---|
| 1 準備筆電 | 完成 | 2026-09-26 | preflight 全數通過（系統管理員執行）；雲端判讀通過，Python 3.13 與分頁檔設定都接受 |
| 2 安裝 M&V 並擷取 | 工具完成 | | M&V 12:23 裝完；inventory 通過、harvest 注意（缺 2：ImmersiveHUD SKSE、Load Time Profiler）、extract_official 通過；待刪 `D:\WJ-Downloads`（先問使用者），`D:\MV` 保留到第 4 階段 |
| 3 安裝 Nolvus | 安裝中 | | 13:07 按 Start（6.0.20 Ultimate，**Nudity Yes**＝使用者要求）；遊戲檔檢查與降版完成；13:16 為 Mods 420/3626、錯誤 0 |
| 4 組合清單 | 未開始 | | |
| 5 重建輸出與英文基準 | 未開始 | | |
| 6 繁中化 | 未開始 | | |
| 7 效能調校 | 未開始 | | |
| 8 凍結備份 | 未開始 | | |

## 第 1 階段結論
- Windows 更新：沒有待安裝的更新，不需重新開機。
- VC++ x64（14.50）、.NET 6（6.0.36）與 .NET 8 Desktop Runtime 已安裝。
- Python：PATH 上是 3.13.11，符合 `pyproject.toml` 的 `>=3.12`；`pytest` 49 項全過。未另裝 3.12。
- 分頁檔：C 槽系統管理（約 4 GB）＋ D 槽固定 40960 MB，兩顆都是 NVMe SSD；preflight 通過，未更動。
- `D:\MV`、`D:\Nolvus`、`D:\PM`、`D:\WJ-Downloads` 已建立並加入 Defender 排除（D 槽 NTFS，剩約 1047 GB）。
- Steam 版 Skyrim 1.7.104.0：遊戲語言 English、Overlay 關閉、自動更新「等到我啟動遊戲的時候」。Steam 介面語言維持原設定（手冊只要求遊戲語言）。
  - 改語言只下載 928 B：`Skyrim_Default.ini` 的 `sLanguage` 改為 ENGLISH，各語言字串本來就在 `Skyrim - Interface.bsa`。
- CC 74/74（約 5.85 GB）：AE 升級的 Steam DLC 沒有內容檔，要在遊戲內 Creations 登入 Bethesda.net 後，用 OPTIONS →「Download all owned Creation Club Creations」下載；`ContentCatalog.txt` 記錄 74 項。沒有載入存檔，也沒有購買任何東西。
- `%LOCALAPPDATA%\ModOrganizer` 已改名為 `ModOrganizer.bak`（未刪除）。
- 沒有 Killer 網路軟體。
- 帳號：Nexus Premium 與 mega 已在 Wabbajack 登入；nolvus.net 帳號已有；夸克帳號已有，但 PC 客戶端要在第 6 階段前重新安裝。
- 環境變數 `NEXUS_API_KEY`（第 4 階段）、`ANTHROPIC_API_KEY`（第 6 階段）尚未設定，使用者自行設定。
- 筆電有獨顯直連開關（Armoury Crate「獨顯輸出」），目前未切換；依 `docs/07` 在第 7 階段處理（需重新開機）。
- Wabbajack 4.2.3 已在 `D:\Wabbajack`。

## 最近一次工具結果摘要
- preflight（2026-09-26 09:12，系統管理員）：通過 11、資訊 2、注意 0、失敗 0。

## 雲端指示處理紀錄（cloud-notes 2026-09-26）
- [x] 第 1 階段判讀：通過。Python 3.13.11 可用；分頁檔接受；`文件` 裡的 Skyrim.ini 不動；preflight Defender 誤報已由雲端修正（`pytest` 50 項全過）。
- [x] 改用 `git pull --rebase`；回報改寫 `progress/local-report.md` 並推送。
- [x] 不下載 M&V 2.40.1；第 4 階段 `audit_skse.py` 不加 `--mv-1597-map`。
- [ ] 第 3 階段完成前不從 Steam 啟動 Skyrim（持續遵守）。
- [ ] 刪除順序：先問使用者刪 `D:\WJ-Downloads`；`D:\MV` 保留到第 4 階段 `manifest` 跑完。
- [ ] 不同時安裝 Nolvus：只準備 Dashboard（下載、登入、建立實例、選項、確認 6.0.20），M&V 完成、第 2 階段工具跑完、刪除 `D:\WJ-Downloads` 後才按安裝。
  - Dashboard：從 nolvus.net 官方連結（作者 GitHub 發行檔）取得 NolvusUpdater 1.3.9.0；GitHub CDN 單一連線只有約 40 KB/s，改用 32 條連線分段下載同一個 `Binaries3811.zip`（大小與官方記錄相符、7-Zip CRC 檢查通過），照 Updater 原始碼的做法解壓到 `D:\Nolvus`。Updater 回報「up to date」。
  - 遊戲路徑用 Auto Detect（Steam 預設庫）；此步驟不改動 Steam 遊戲資料夾。
- [x] cloud-notes「Nolvus 何時可以和 M&V 同時安裝」：Wabbajack 下載完、進入安裝階段時（2026-09-26 11:39）D 槽剩 **974.6 GB**（≥ 950），使用者同意後在 11:46 按 Nolvus Start。

## Rare Curios 版本衝突（手冊沒寫到，已問使用者）
- 起因：第 1 階段在遊戲內用 Creations「Download all owned Creation Club Creations」下載 AE 內容時，74 個 CC 全部重新下載，連 Steam 本來就附的 4 個免費 CC 也被覆寫。其中只有 Rare Curios（`ccbgssse037-curios.bsa/.esl`）的 Bethesda.net 版與 Steam 版內容不同（大小相同）。
- M&V 2.6.2 要 **Steam 版**：Wabbajack 以「Missing game file Data_ccbgssse037-curios.bsa/.esl」中止（FATAL）。modlist 預期雜湊 `DG3YZQj7xwk=`／`STK4THfMHzw=`；Creations 版為 `FQbA20bA5Dw=`／`it6+eSu4OCw=`（Wabbajack xxHash64）。Fish、Survival Mode、AdvDSGS 重寫後雜湊不變。
  - 處理（使用者同意）：Steam「驗證遊戲檔案完整性」→ 只有這 2 個檔驗證失敗並重新下載 → 雜湊與 M&V 預期相符 → Wabbajack Retry，已順利進入 Installing files。遊戲仍是 1.7.104.0、build 24914197、CC 74 個。
- Nolvus 6.0.20 要 **另一版**（應為 Creations 版）：Stock Game 檢查到 `ccbgssse037-curios.bsa` 時「Hash … does not match!」，已自動 rollback，沒有留下變更。
- 使用者已同意的後續做法：M&V 裝完（Curios 已複製進 `D:\MV\Stock Game`）後，① 把 Steam 資料夾的 Steam 版 Curios 搬到備份資料夾（不刪除）；② 先確認 Steam 沒有新版 Skyrim，再從 Steam 啟動遊戲一次，用 Creations 重新下載 Curios，不載入存檔就離開；③ 重開 Nolvus Dashboard 接著安裝。
- 雲端 45e52d6 判讀：照做並加檢查；`D:\PM` 用 Nolvus 的 Creations 版；沒有 Enemies Resistance／Stances 開關正常；Nudity No 正確（但使用者之後要求改 Yes）。
- 執行結果（2026-09-26）：
  - M&V 的 Curios 在 `D:\MV\mods\Creation Club\ccBGSSSE037-Curios.*`（不在 `Stock Game\Data`），SHA256 與 Steam 資料夾相同，且是獨立副本（不同磁碟）。
  - Steam 版搬到 `D:\Backup\Curios-Steam`（雜湊相同）。
  - 啟動前檢查：遊戲庫按鈕「開始遊戲」、下載頁無 Skyrim 排程、`appmanifest` 的 build／TargetBuildID 都是 24914197、StateFlags 4。SteamDB 被瀏覽器驗證頁擋住，改看 Steam 官方新聞 API：最新更新仍是 1.7.99（8/27 更新）。
  - 啟動器因 `Skyrim_Default.ini` 變新（第 1 階段改語言）而重新偵測硬體，**重建了 `文件` 裡的 `Skyrim.ini`（現為 sLanguage=ENGLISH）與 `SkyrimPrefs.ini`**（Ultra、2560x1600、全螢幕）。使用者原本的中文與畫面設定被覆蓋，只影響原版遊戲，不影響 M&V／Nolvus／`D:\PM`。
  - 第一次啟動下載中途遊戲失去焦點而暫停，後來遊戲結束；使用者同意後再啟動一次，Creations 補完下載（148 個 cc 檔重寫、74 個插件），出現「All Creations Downloaded」後關閉遊戲。沒有載入存檔、沒有購買。
  - 核對：Curios 為 `FQbA20bA5Dw=`／`it6+eSu4OCw=`（Creations 版）；Fish、Survival、AdvDSGS 雜湊不變；遊戲 1.7.104.0、build 24914197、74 個 CC。Creations 版複製到 `D:\Backup\Curios-Creations`。
  - Nolvus Dashboard 在遊戲切換解析度時跳出 .NET 例外（NullReference），當時它停在錯誤頁、沒有安裝在跑，已結束後重開。
  - 重選選項（與 1ae35a6 相同，只有 **Nudity 改為 Yes**），D 槽剩 676 GB（≥ 500），13:07 按 Start；遊戲檔檢查已通過 CC。

## 最近一次工具結果摘要（第 2 階段）
- inventory-mv：通過 1、資訊 7、注意 0、失敗 0（3694 個 mod、336.1 GB、Stock Game 1.6.1170.0）。
- harvest-mv（試跑與 --apply）：通過 1、注意 1（647 個計畫中 645 完成、來源缺少 2）、資訊 3、失敗 0；`D:\PM` 有 645 個 mod、MO2 與 tools。
- zh_extract_official（試跑與 --apply）：通過 3、資訊 1、失敗 0；21 個字串表，有內容的全是繁體（工具抽樣到空檔才顯示 unknown）。

## 等待雲端或使用者決定的事
- 雲端：Nudity Yes 是否延伸到 `D:\PM`；`extract_official` 字形判斷抽樣；是否在手冊提醒改語言後啟動器會重建 ini（詳見 `local-report.md`）。
- 使用者：已同意刪除 `D:\WJ-Downloads`（194.9 GB、7188 個檔，抽查硬連結數皆為 1，不影響 `D:\PM`／`D:\MV`），但本機工具擋下刪除磁碟第一層資料夾，**請使用者自己刪**（Shift+Delete 或 `rmdir /s /q D:\WJ-Downloads`）。Wabbajack 已關閉。
- 使用者：原版遊戲的 `Skyrim.ini` 維持英文（使用者決定）。
- 已推送 79cf305（第 2 階段回報），等雲端判讀。
