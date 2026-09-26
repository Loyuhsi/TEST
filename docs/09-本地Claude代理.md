# 讓筆電上的本地 Claude 代你操作

雲端的 Claude 碰不到你的筆電，所以改由你在筆電上開一個 **Claude Desktop 的 Code 分頁**對話。它會：
- 讀倉庫裡的 `CLAUDE.md` 與技能 `pages-modlist`。
- 跑工具、判讀報告。
- 用「電腦操作」幫你點 Steam、Wabbajack、Nolvus Dashboard、MO2 等程式。

你授權的是**幾乎全自動**：它只會在以下情況停下來問你。
- 刪除檔案或資料夾
- 花錢（例如 LLM 翻譯）
- 修改 Windows 安全設定
- 推送到 GitHub

需要登入、輸入密碼或按 UAC 時，它也會叫你。

## 1. 準備（一次就好）

| 項目 | 做法 |
|---|---|
| Claude Desktop | 到 claude.com/download 下載 Windows 版並登入。**電腦操作需要 Pro 或 Max 方案**（Team／Enterprise 目前沒有）。 |
| 開啟電腦操作 | Claude Desktop → Settings → General → 開啟 **Computer use**。這是預覽功能。 |
| Git for Windows | 到 git-scm.com 下載安裝，選項用預設即可（會一起裝 Git Bash）。 |
| Python 3.12 | 到 python.org 下載，安裝時勾選 **Add python.exe to PATH**。 |

安裝完開啟「PowerShell」，確認三個指令都有版本號：
```powershell
git --version
python --version
claude --version   # 沒有這個指令也沒關係，Desktop 的 Code 分頁不需要它
```

## 2. 取得倉庫
在 PowerShell 執行：
```powershell
git clone -b claude/sharp-faraday-b8ax3h https://github.com/Loyuhsi/TEST C:\PagesTools
```
之後要拿雲端的更新，本地代理會自己執行 `git pull`。

## 3. 設定 API 金鑰（不要貼進任何對話）
1. **Nexus**：登入 nexusmods.com → 頭像 → Site preferences → API Keys → 最下方的 Personal API Key，按 Request 後複製。
2. **Claude API**（第 6 階段翻譯才需要）：到 console.anthropic.com → API Keys 建立一把，並確認帳戶已設定付款。
3. 在 PowerShell 設成「使用者環境變數」（把引號內換成你的金鑰）：
   ```powershell
   [Environment]::SetEnvironmentVariable("NEXUS_API_KEY", "你的Nexus金鑰", "User")
   [Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "你的Claude金鑰", "User")
   ```
4. **完全結束 Claude Desktop**（工作列右下角圖示 → Quit）再重新開啟，它才讀得到新的環境變數。

## 4. 開啟本地對話
1. Claude Desktop → **Code** 分頁 → 選擇資料夾 `C:\PagesTools`。
2. 第一次開啟會問是否信任這個專案的設定（`.claude/settings.json` 裡的權限與防護 hook）→ 選信任。
3. 貼上以下開場指令：

```
請使用 pages-modlist 技能。先 git pull，讀 CLAUDE.md、progress/status.md、progress/cloud-notes.md，
確認 Python 3.12、Git 與 D 槽空間都正常後，從第 1 階段開始。
我授權你照 CLAUDE.md 幾乎全自動執行：只有刪除檔案或資料夾、花錢、修改 Windows 安全設定、
git push 之前要先問我；需要登入、輸入密碼或按 UAC 時叫我。
每個階段結束時更新 progress/status.md 並提交，再用 SendMessage 把摘要傳給雲端對話 test-25；
傳不過去就把摘要給我，我會貼到雲端。
```

## 5. 測試與雲端直連（Remote Control）
本地與雲端要互相傳話，有三條路，依序嘗試：
1. **本地 → 雲端**：本地代理會試著用 SendMessage 傳摘要給雲端對話 `test-25`。成功的話，雲端對話會直接收到。
2. **雲端 → 本地**：雲端把判讀與決定提交到 GitHub，寫在 `progress/cloud-notes.md` 與 `data/decisions.csv`。本地代理每個階段開始前會 `git pull` 讀取。
3. **直連（實驗性）**：
   1. 在本地對話輸入 `/remote-control`。如果 Code 分頁沒有這個指令，改在 PowerShell 執行（第一次要先用 `irm https://claude.ai/install.ps1 | iex` 安裝 Claude Code 指令列版本，並用 `claude` 登入 claude.ai 帳號）：
      ```powershell
      cd C:\PagesTools
      claude remote-control
      ```
   2. 回到雲端對話告訴我「本地已開」。
   3. 我會檢查能不能直接傳訊息給它。這需要 Pro／Max／Team／Enterprise 方案，並用 claude.ai 帳號登入，不能用 API 金鑰登入。

三條路都不通時：本地代理把摘要給你，由你貼到雲端對話，或上傳 `reports\` 的檔案。
倉庫是**公開的**，所以報告檔不會推上 GitHub。

## 6. 它會在什麼時候叫你

| 時機 | 你要做什麼 |
|---|---|
| 登入 Steam、Nexus、Nolvus、mega、夸克 | 自己輸入帳號密碼 |
| UAC「是否允許變更」 | 看清楚是哪個程式再按「是」 |
| 刪除 `D:\MV`、下載資料夾、`D:\Nolvus` 或 mod | 確認它說的報告都沒有失敗，再同意 |
| Windows Defender 排除 D:\MV、D:\Nolvus、D:\PM | 同意，或自己照 `docs/01` 設定 |
| LLM 翻譯前會先報出估計金額 | 同意才會開始花錢 |
| `git push` | 確認只推 `progress/` 或 `data/decisions.csv` |
| 等候下載、安裝或產生（數小時） | 讓電腦插電保持開機；完成後回來說「繼續」 |

## 7. 使用中的注意事項
- **電腦操作進行時不要同時動滑鼠鍵盤**。關掉與這件事無關的視窗，例如網銀、私人訊息。
- **要接手時直接在對話裡說「暫停」**，或按停止鈕。
- **關掉 Claude Desktop 也沒關係**：重新開啟 Code 分頁、選同一個資料夾，說「繼續」即可。它會讀 `progress/status.md` 從上次的地方接著做。
- **它不會做的事**：推送報告到公開倉庫、顯示金鑰、下載蘇禾分享中的英文整包、按 Nolvus／Wabbajack 的更新，也不會新增翻譯用 ESP。

## 8. 疑難排解

| 狀況 | 處理 |
|---|---|
| 權限提示太多 | 允許清單已經涵蓋 `python tools/*` 與常用 git 指令。其他指令它會問；可在提示中選擇「這次專案都允許」。刪除、花錢、推送仍然會問。 |
| hook 錯誤訊息（找不到 python） | Python 沒加入 PATH。重新安裝 Python 並勾選 Add to PATH，再重啟 Claude Desktop。 |
| `nexus_fetch.py` 顯示未設定 NEXUS_API_KEY | 確認第 3 節設定了使用者環境變數，並完全重啟 Claude Desktop。 |
| 電腦操作無法使用 | 確認方案是 Pro 或 Max，且 Settings → General 已開啟 Computer use。不行的話，圖形介面步驟由你照手冊操作，本地代理只負責指令與判讀。 |
