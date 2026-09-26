---
name: pages-modlist
description: 在這台 Windows 筆電上依階段執行 Pages 混合清單（Nolvus v6＋Mages & Vikings）的安裝、組合、繁中化與調校。使用者說「開始／繼續／下一階段／第 N 階段」、要跑 tools/ 裡的工具，或要判讀 reports/ 的報告時使用。
---

# Pages 混合清單：階段執行流程

每次被叫用（包括使用者說「繼續」）都照這個循環走，不要跳步。

## 1. 先同步、再判斷位置
1. `git pull --rebase`（在 `C:\PagesTools`）。本地有未推送的提交時，一般的 `git pull` 在新版 Git 會報「divergent branches」錯誤。
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
3. 寫回報：覆寫 `progress/local-report.md`（格式見檔案內範本）：
   - 階段、日期、結論
   - 每個工具報告（`reports\*.txt`）的每一行結果，原文照抄 `[通過]`／`[注意]`／`[失敗]` 行
   - 需要雲端決定的事
   - 不寫 Windows 使用者名稱、帳號、序號、金鑰，不附截圖或整份日誌。
4. 提交並推送：
   ```bash
   git add progress/status.md progress/local-report.md
   git commit -m "Phase N: <結論>"
   git push
   ```
   push 會先跳出確認，由使用者核准。第一次推送時 Git 會跳出 GitHub 登入視窗，請使用者登入。
5. 請使用者回到雲端對話說「已推送」。雲端會把判讀寫進 `progress/cloud-notes.md` 或 `data/decisions.csv` 並推送；下一次 `git pull` 就會看到。
   - 沒有待決問題就直接進下一階段。
   - 推送失敗時，請使用者把 `local-report.md` 的內容貼到雲端對話。
   - SendMessage 只在 ListAgents 出現識別碼 `[0e5bdc]` 時使用（本地與雲端互相看不到，已實測）。

## 4. 卡住時
- 手冊沒寫到、兩份資料互相矛盾、工具 FAIL 找不到原因，或遊戲當機：
  1. 收集證據：報告、`Documents\My Games\Skyrim Special Edition\SKSE\` 下的 `skse64.log`、Crash Logger 的 `crash-*.log`。
  2. 在 status 記下「卡在哪一步、看到什麼」。
  3. 回報雲端或問使用者。不要自行大改清單。
- 研究結論與背景都在 `docs/research/`（英文）與 `docs/00-計畫.md`，判斷前先查。
