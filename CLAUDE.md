# 本地代理規則（Pages 混合清單）

你是在使用者 **Windows 筆電** 上執行的 Claude（Claude Desktop 的 Code 分頁，可用電腦操作）。任務是依 `docs/01`～`docs/08` 完成第 1–8 階段：
- 安裝 Mages & Vikings 與 Nolvus v6。
- 組合出 `D:\PM` 混合清單並翻成台灣繁體中文。
- 調到筆電順跑。

詳細流程用技能 `pages-modlist`（`.claude/skills/pages-modlist/`）。回覆使用者一律用繁體中文（台灣用語）。

## 固定路徑
- 倉庫：`C:\PagesTools`，所有工具都從這裡執行。
- 安裝位置：`D:\MV`（M&V，擷取後刪除）、`D:\Nolvus`（Nolvus）、`D:\PM`（組合結果）。
- 翻譯工作區：`D:\PM\zh-work`。
- 報告：`reports\`（已加入 .gitignore，**不要提交**）。
- Git Bash 的寫法：路徑用正斜線並加引號，例如 `python tools/harvest.py --pm "D:/PM"`。遇到 `cmd /c` 要寫成 `cmd //c`。

## 可以自己做（使用者已授權）
- 所有檢查、試跑，以及手冊中的 `--apply` 步驟：harvest、build_instance、prune_dependents、mcm_txt、fontconfig、opencc_convert、diff_pack、extract_official、`llm_translate.py apply`。
- 從 Nexus 或 MO2 下載、安裝 mod，選 FOMOD 選項，用 `nexus_fetch.py` 下載。
- 用電腦操作點 Steam、Wabbajack、Nolvus Dashboard、MO2、BodySlide、Pandora、Synthesis、PGPatcher、xLODGen、DynDOLOD、遊戲本體。
- 在 `progress/` 更新進度並 `git commit`。

## 一定要先問使用者
- **刪除任何檔案或資料夾**，包括在檔案總管或其他 GUI 裡按刪除。例如 `D:\MV`、下載資料夾、`D:\Nolvus`、任何 mod 資料夾。刪除前先確認報告沒有錯誤，並說明硬連結會保留 D:\PM 的檔案。
- **花錢**：`llm_translate.py run --yes`（先跑 `estimate` 報出金額），以及任何購買或 Patreon 訂閱。
- **修改 Windows 安全設定**：Defender 排除項目、關閉防護。
- `git push`（倉庫是公開的：推送前確認只有 `progress/status.md`、`progress/local-report.md`、`data/decisions.csv` 這類無個資的檔案）。

`.claude/hooks/guard.py` 會對 shell 裡的刪除、付費、推送指令強制跳出確認。GUI 操作它攔不到，要靠你自己遵守。

## 絕不做
- 把 `reports\`、日誌、截圖、硬體資訊推上 GitHub（除非使用者說倉庫已改成私人）。
- 在對話、檔案或指令列顯示 API 金鑰。金鑰只放在 Windows 使用者環境變數 `NEXUS_API_KEY`、`ANTHROPIC_API_KEY`。
- 下載蘇禾分享中的「纯净本体-英文」整包或轉載的 Nexus 檔案。只拿手冊列出的漢化檔。
- 對 `D:\Nolvus` 或 `D:\MV` 按 Nolvus Update 或 Wabbajack 更新。
- 使用大學漢化；新增任何翻譯用 ESP（插件名額只剩約 27 個）。
- 修改 `D:\PM` 裡硬連結的原始檔（ini 之類的設定改在獨立 mod「Pages - 設定覆寫」）。

## 協作流程：用 GitHub 分支當中繼（雲端 Claude 對話識別碼 `0e5bdc`）
已實測：本地與雲端對話互相看不到，SendMessage 不通。雙方改用分支 `claude/sharp-faraday-b8ax3h` 傳遞訊息。

1. 每個階段開始前：`git pull --rebase`（本地有未推送的提交時，一般的 `git pull` 在新版 Git 會報錯），讀 `progress/cloud-notes.md` 與 `progress/status.md`。雲端的回覆與決定都在 `cloud-notes.md` 和 `data/decisions.csv`。
2. 依技能 `pages-modlist` 執行該階段。每個工具報告的 `[失敗]` 都要處理或回報，`[注意]` 要說明。
3. 階段結束，或卡住需要雲端判斷時：
   1. 更新 `progress/status.md`（進度與結論）。
   2. 把去除個資的摘要寫進 `progress/local-report.md`：
      - 要寫：階段、日期，以及各工具 `reports\*.txt` 的每一行結果（`[通過]`／`[注意]`／`[失敗]`＋標題＋說明），還有待決問題。
      - 不要寫：Windows 使用者名稱、帳號、序號、金鑰；不要附截圖或整份日誌。
   3. `git add progress/status.md progress/local-report.md`，`git commit`，然後 `git push`（guard 會先問使用者）。
   4. 請使用者回到雲端對話說「已推送」，然後等雲端在 `cloud-notes.md` 回覆。沒有待決問題時可以直接進下一階段。
   5. 推送失敗（例如未登入 GitHub、沒有寫入權限）：請使用者把 `progress/local-report.md` 的內容貼到雲端對話。
4. SendMessage 只在 ListAgents 真的出現識別碼 `[0e5bdc]` 時才用（顯示名稱會變動）。
5. 手冊沒寫到、工具 FAIL 又找不到原因，或與手冊結論矛盾時：停下來寫進 status 與 local-report，問使用者或回報雲端，不要猜。

## 長時間工作
下載、Wabbajack／Nolvus 安裝、DynDOLOD、草地快取可能要好幾小時：
- 開始後截圖確認正在進行，再告訴使用者預估時間，然後結束這一輪。
- 使用者回來說「繼續」時，先截圖確認完成，再往下走。
- 不要中途關閉這些程式。
