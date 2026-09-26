# 進度（本地代理更新；只寫進度與結論，不貼報告內容、不寫硬體序號或金鑰）

最後更新：2026-09-26
目前階段：1（進行中，等使用者處理 .NET 6、Defender 與帳號確認）

| 階段 | 狀態 | 完成日期 | 結論／待決問題 |
|---|---|---|---|
| 1 準備筆電 | 進行中 | | 失敗 0；CC 已 74/74；剩 .NET 6、Defender 排除、帳號確認、最終 preflight |
| 2 安裝 M&V 並擷取 | 未開始 | | |
| 3 安裝 Nolvus | 未開始 | | |
| 4 組合清單 | 未開始 | | |
| 5 重建輸出與英文基準 | 未開始 | | |
| 6 繁中化 | 未開始 | | |
| 7 效能調校 | 未開始 | | |
| 8 凍結備份 | 未開始 | | |

## 第 1 階段檢查表
- [x] Windows 更新：沒有待安裝的更新，不需重新開機。
- [x] VC++ x64（14.50）、.NET 8 Desktop Runtime 已安裝。
- [ ] .NET 6 Desktop Runtime：未安裝（只有 .NET 6 基本執行環境）。待使用者同意下載並按 UAC。
- [x] Python：PATH 上是 3.13.11，符合 `pyproject.toml` 的 `>=3.12`；`pytest` 49 項全過。未另裝 3.12。
- [x] 分頁檔：C 槽系統管理（約 4 GB）＋ D 槽固定 40960 MB，兩顆都是 NVMe SSD；preflight 通過。與手冊「C 槽 20480–40960」寫法不同，待雲端確認可否沿用。
- [x] `D:\MV`、`D:\Nolvus`、`D:\PM`、`D:\WJ-Downloads` 已建立（D 槽 NTFS，剩約 1047 GB）。
- [ ] Defender 排除：屬安全設定，待使用者自己加入。
- [x] Steam 版 Skyrim 1.7.104.0；遊戲語言改為 English、Overlay 關閉、自動更新改為「等到我啟動遊戲的時候」。已擁有 Anniversary Edition 升級。
- [x] CC 插件 74/74（約 5.85 GB）：遊戲內 Creations 需要 Bethesda.net 帳號，登入後用 OPTIONS →「Download all owned Creation Club Creations」下載；`ContentCatalog.txt` 記錄 74 項。未載入存檔，已關閉遊戲。
- [x] `%LOCALAPPDATA%\ModOrganizer` 已改名為 `ModOrganizer.bak`（未刪除，可改回）。
- [x] 沒有 Killer 網路軟體。
- [ ] 帳號：Wabbajack 已有 Nexus（OAuth）與 mega 登入；待使用者確認 Nexus Premium、nolvus.net、夸克。
- [ ] 最終 preflight：需以系統管理員身分執行，才能讀到 Defender 排除。

## 最近一次工具結果摘要
- preflight（基準）：通過 7、注意 5（CC、自動更新、.NET 6、Defender、MO2 全域實例）、失敗 1（遊戲語言）、資訊 2。
- preflight（修正後）：通過 8、注意 3（CC、.NET 6、Defender）、失敗 0、資訊 2。

## 等待雲端或使用者決定的事
- 雲端：分頁檔沿用「C 槽系統管理＋D 槽 40960 固定」可以嗎？
- 雲端：用 Python 3.13.11 代替 3.12 可以嗎？第 6 階段的 opencc 等套件到時再確認。
- 雲端：preflight 以一般權限執行時，Defender 讀到的是「N/A: Must be an administrator…」字串，被當成路徑而顯示「尚未排除」。是否要讓工具辨識這個字串並改報[資訊]？
- 雲端：使用者「文件\My Games\Skyrim Special Edition\Skyrim.ini」仍是 `sLanguage=CHINESE`（舊遊玩留下）。Wabbajack、Nolvus 用各自設定檔，應不受影響，請確認。
- 使用者：.NET 6、Defender 排除（系統管理員 PowerShell）、最終 preflight、帳號確認（Nexus Premium、nolvus.net、夸克）。
- 雲端對話 `0e5bdc` 目前不在 ListAgents 清單中，摘要改由使用者轉貼。
