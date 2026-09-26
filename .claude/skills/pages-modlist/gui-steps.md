# 圖形介面操作要點（電腦操作）

詳細步驟以 `docs/0N-*.md` 為準。這裡只列代理容易出錯的地方。

## 通則
- 每個安裝或產生工具：
  - 開始前截圖選項頁，確認設定。
  - 完成後截圖結果頁；出錯時截圖錯誤訊息。
- 不要在程式執行中切換或關閉視窗。要等待時先告訴使用者，再結束這一輪。
- 遇到登入（Steam、Nexus、Nolvus、mega、夸克）或驗證碼：請使用者自己輸入，不要代填密碼。
- 遇到 UAC「是否允許變更」：請使用者按，並說明原因。
- 看到「Update」「更新清單」按鈕：**不要按**（Nolvus Dashboard、Wabbajack 已安裝的清單）。

## Steam（第 1 階段）
- 設定 → 介面 → 語言：English。重新啟動 Steam 後，確認 Skyrim 內容 → Language 也是 English。
- Skyrim → 內容 → 更新：選「僅在我啟動時更新」。
- 下載 CC：啟動遊戲 → 主選單 Creations → 全部下載，完成後退出，避免存檔。

## Wabbajack（第 2 階段）
- Gallery 找 Mages & Vikings 2.6.2。
- Install Location：`D:\MV`。Download Location：`D:\WJ-Downloads`，或使用者指定的其他磁碟。
- 需要 Nexus 登入時，請使用者操作。
- 完成前不要關閉。完成後讀 Wabbajack 的結果頁。

## Nolvus Dashboard（第 3 階段）
- 放在 `D:\Nolvus`，版本需為 3.8.11 以上。
- 選項照 `docs/03` 的表格：Ultimate、不含 SR Exterior Cities、TAA、16:9、Edge、Fantasy Combat、其他附加元件全勾、True Nord、語言 English、關閉封存。
- 版本若顯示 6.0.21：停止，回報雲端。

## MO2（第 4、5 階段；`D:\PM\ModOrganizer.exe`）
- 設定檔選 `Pages-ZH`。左側清單越**下面**的 mod 優先權越高。
- 安裝下載的壓縮檔：
  1. 名稱欄一律改成 `manifest.csv` 的 `folder` 值，一字不差。
  2. 跳出「已存在」時選 **Replace**（取代佔位資料夾）。資料夾已經有內容（replace_dll 重裝）時，Replace 會刪掉舊內容：先問使用者。
- FOMOD：選能產生 `data/target/plugins.txt` 所列插件的選項；`data/decisions.csv` 的 `note` 有指定時照 note。拿不準就截圖回報。
- 設定 →「Plugins」分頁：停用 **Crash Log Labeler**（crashlogtools 用 cp950 讀 crash log 會報錯）。
- 執行任何 `tools/*.py` 前先關閉 MO2，因為 MO2 關閉時會覆寫設定檔。
- 工具的輸出：
  - 看 Overwrite → 右鍵 Move content to Mod…，移到對應的輸出資料夾（`docs/05` 的對照表）。
  - 改設定檔時，建空 mod「Pages - 設定覆寫」，把檔案複製進去再改，不改原檔。

## 第 5 階段的工具
- Pandora：引數 `-o "D:\PM\mods\Pandora Output"`。
- BodySlide：Output Path 設為 `D:\PM\mods\BodySlide (Nude)`。Preset 等雲端指示。
- NGIO 草地快取：先停用 True HUD。會重啟遊戲很多次，屬正常現象；時間 0.5–2.5 小時。
- DynDOLOD：選 High。完成後依 `docs/05` 搬移輸出。

## 遊戲測試（第 5–7 階段）
- 從 MO2 選 SKSE 執行，開新遊戲，走 `docs/測試路線.md`。
- 觀察 FPS、VRAM（Display Tweaks OSD）、紫色貼圖、方框字、當機。
- 當機後收集：`Documents\My Games\Skyrim Special Edition\SKSE\` 下最新的 `crash-*.log` 與 `skse64.log`。
