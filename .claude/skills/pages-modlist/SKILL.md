---
name: pages-modlist
description: 在這台 Windows 筆電上依階段執行 Pages 混合清單（Nolvus v6＋Mages & Vikings）的安裝、組合、繁中化與調校。使用者說「開始／繼續／下一階段／第 N 階段」、要跑 tools/ 裡的工具，或要判讀 reports/ 的報告時使用。
---

# Pages 混合清單：階段執行流程

每次被叫用（包括使用者說「繼續」）都照這個循環走，不要跳步。

## 1. 先同步、再判斷位置
1. `git pull`（在 `C:\PagesTools`）。
2. 讀 `progress/status.md`，找出目前階段與上次停在哪一步。
3. 讀 `progress/cloud-notes.md` 的「最新指示」。雲端的指示優先於你自己的判斷。
4. 開啟該階段手冊 `docs/0N-*.md`，從上次停下的那一步接著做。

## 2. 執行該階段
- 指令：依 `phase-commands.md`（Git Bash 寫法）。
  - 有 `--apply` 的步驟一律先試跑、看報告，確認合理後才加 `--apply`。
  - 參數只能用工具 `--help` 列出的，不要自己發明。
- 圖形介面：依 `gui-steps.md` 與手冊，用電腦操作完成。
  - 關鍵畫面要截圖確認：選項頁、完成畫面、錯誤訊息。
- 每個工具都會在 `reports\` 產生 `.txt`（人看）和 `.json`（詳細資料）。
  - 讀 `.txt`：`[失敗]` 必須解決；`[注意]` 要判斷，必要時照手冊處理；`[通過]`／`[資訊]` 記下重點即可。
  - 需要細節時讀 `.json` 或對應的 `.csv`。
- 會刪除檔案、會花錢、會推送的動作：先停下來問使用者（見 `CLAUDE.md`）。
- 長時間工作：開始後截圖確認、告訴使用者預估時間，然後結束這一輪，等使用者說「繼續」。

## 3. 階段收尾
1. 逐條對照手冊最後的「退出條件」。還沒全部達成就不算完成。
2. 更新 `progress/status.md`：
   - 狀態、日期、一行結論
   - 工具結果統計（例如「通過 12、注意 2、失敗 0」）
   - 待決問題
   - 不要貼報告全文、硬體序號、使用者名稱或金鑰。
3. 提交進度：`git add progress/status.md && git commit -m "Phase N: <結論>"`（不要 push，除非使用者同意）。
4. 回報雲端：先執行 ListAgents，找標示為雲端、識別碼 `[0e5bdc]` 的那一列，用它當下顯示的名稱（會變動，例如 `test-25`、`test-17`）以 SendMessage 傳送。內容：
   - 階段、結果
   - 各報告的關鍵行（例如 `[注意]` 項目原文）
   - 需要雲端決定的事
   - 如果傳送失敗，請使用者把同樣內容貼到雲端對話。
5. 等雲端回覆（會以提交 `progress/cloud-notes.md` 或 `data/decisions.csv` 的形式出現）。沒有待決問題就直接進下一階段。

## 4. 卡住時
- 手冊沒寫到、兩份資料互相矛盾、工具 FAIL 找不到原因，或遊戲當機：
  1. 收集證據：報告、`Documents\My Games\Skyrim Special Edition\SKSE\` 下的 `skse64.log`、Crash Logger 的 `crash-*.log`。
  2. 在 status 記下「卡在哪一步、看到什麼」。
  3. 回報雲端或問使用者。不要自行大改清單。
- 研究結論與背景都在 `docs/research/`（英文）與 `docs/00-計畫.md`，判斷前先查。
