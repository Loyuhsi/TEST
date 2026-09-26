# 進度（本地代理更新；只寫進度與結論，不貼報告內容、不寫硬體序號或金鑰）

最後更新：2026-09-26
目前階段：2（Wabbajack 安裝 M&V 中）

| 階段 | 狀態 | 完成日期 | 結論／待決問題 |
|---|---|---|---|
| 1 準備筆電 | 完成 | 2026-09-26 | preflight 全數通過（系統管理員執行）；雲端判讀通過，Python 3.13 與分頁檔設定都接受 |
| 2 安裝 M&V 並擷取 | 進行中 | | Wabbajack 安裝 M&V 2.6.2（`D:\MV`，下載 `D:\WJ-Downloads`） |
| 3 安裝 Nolvus | 準備中 | | Dashboard 3.8.11 已放在 `D:\Nolvus`；等使用者完成 Nexus SSO、nolvus.net、mega 登入後選選項；**不按安裝**（依 cloud-notes） |
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

## 等待雲端或使用者決定的事
- （無）
