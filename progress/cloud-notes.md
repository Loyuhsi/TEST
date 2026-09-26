# 雲端給本地代理的指示

雲端 Claude 對話（識別碼 `0e5bdc`；顯示名稱會變動，例如 `test-25`、`test-17`）把判讀結果、決策與修正寫在這裡，並提交到分支 `claude/sharp-faraday-b8ax3h`。
本地代理每個階段開始前 `git pull` 後閱讀；已處理的項目在 `progress/status.md` 註記。
個別資料夾的動作覆寫寫在 `data/decisions.csv`（`folder,action,note`），`tools/manifest.py` 會自動採用。

## 最新指示
- 2026-09-26：雲端對話的顯示名稱會變。傳訊息前先執行 ListAgents，找標示為雲端、識別碼 `[0e5bdc]` 的那一列，用那一列當下顯示的名稱傳送。
- 2026-09-26：從第 1 階段開始。依 `docs/01-準備筆電.md` 完成後執行 `preflight.py`，並把摘要傳給雲端對話。
