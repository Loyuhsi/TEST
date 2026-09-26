# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：1 準備筆電（補推送），並回報第 2 階段已開始
- 日期：2026-09-26
- 結論：第 1 階段完成（雲端已在 cloud-notes 判讀通過）；第 2 階段已開始，Wabbajack 正在下載 M&V 2.6.2

## 工具結果（照抄 reports\*.txt 的每一行）
```
== preflight 報告 (2026-09-26 09:12) ==
系統：Windows 11  Python 3.13.11

[通過] 顯示卡 VRAM：Intel(R) Graphics, NVIDIA GeForce RTX 5080 Laptop GPU（15.9 GB）→ 達 Nolvus Ultimate 最低需求，需降部分 4K 材質
[通過] 記憶體：63.4 GB
[通過] 分頁檔：?:\pagefile.sys / d:\pagefile.sys 40960 40960
[通過] 安裝磁碟 D:：剩餘 1047 GB / 共 1863 GB，檔案系統 NTFS
[通過] Skyrim 版本：1.7.104.0（預期 1.7.104.0；Nolvus Dashboard 3.8.11+ 與 M&V 2.6.2 皆以此為準）
[通過] Creation Club 內容：74 個 CC 插件（完整 AE 為 74）
[通過] Steam 遊戲語言：english
[通過] Visual C++ 2015–2022 x64：v14.50.35719.00
[通過] .NET 6 Desktop Runtime：已安裝
[通過] .NET 8 Desktop Runtime：已安裝
[通過] Windows Defender 排除：已設定
[資訊] 螢幕：2560x1600 @ 60 Hz
[資訊] CPU：Intel(R) Core(TM) Ultra 9 275HX

總結：[通過]
```
（以系統管理員身分執行；這份是雲端修正 Defender 判讀之前的版本。）

## 已做的處理
- 第 1 階段：詳見 `progress/status.md`。重點：遊戲語言改 English、Overlay 關閉、更新改為「等到我啟動遊戲的時候」；CC 74/74 由遊戲內 Creations 下載；`%LOCALAPPDATA%\ModOrganizer` 改名為 `.bak`；.NET 6 Desktop 6.0.36 與 Defender 排除由使用者在系統管理員終端機完成。
- 已照辦 cloud-notes 第 1 階段判讀：改用 `git pull --rebase`；不下載 M&V 2.40.1；第 3 階段完成前不從 Steam 啟動 Skyrim；`文件` 裡的 Skyrim.ini 不動。
- 拉取雲端的 preflight 修正後，`pytest` 50 項全過。
- 第 2 階段：Wabbajack 4.2.3 已開始下載 M&V 2.6.2 的 `.wabbajack`（存在 `D:\Wabbajack\4.2.3.0\downloaded_mod_lists`，不在 C 槽）；安裝位置 `D:\MV`、下載位置 `D:\WJ-Downloads`。

## 需要雲端決定的事
- 無。第 2 階段安裝完成、各工具報告跑完後再回報。
