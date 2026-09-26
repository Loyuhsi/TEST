# 雲端給本地代理的指示

雲端 Claude 對話（識別碼 `0e5bdc`；顯示名稱會變動，例如 `test-25`、`test-17`）把判讀結果、決策與修正寫在這裡，並提交到分支 `claude/sharp-faraday-b8ax3h`。
本地代理每個階段開始前 `git pull` 後閱讀；已處理的項目在 `progress/status.md` 註記。
個別資料夾的動作覆寫寫在 `data/decisions.csv`（`folder,action,note`），`tools/manifest.py` 會自動採用。

## 最新指示
- 2026-09-26｜**不要同時安裝 Nolvus**：M&V 未完成前，D 槽峰值會達約 1050–1070 GB，超過剩餘的約 1047 GB。現在可以先做 Nolvus 的準備，但停在按安裝之前：
  1. 下載 Nolvus Dashboard 到 `D:\Nolvus` 並完成安裝，確認版本 ≥ 3.8.11。
  2. 登入 nolvus.net 帳號，連結 Nexus（SSO）與 mega。
  3. 建立 Nolvus Awakening 實例，照 `docs/03` 的表格選好所有選項（Ultimate、不含 SR Exterior Cities、TAA、16:9、Edge、Fantasy Combat、其他附加元件全勾、True Nord、English、關閉封存），並截圖確認。
  4. 確認提供的版本是 **6.0.20**；若是 6.0.21，停下來回報。
  5. **不要按開始安裝。** 等 M&V 完成、第 2 階段的工具跑完、`D:\WJ-Downloads` 刪除後（刪除前問使用者），才開始安裝 Nolvus。
  - Wabbajack 正在跑時，不要從 Steam 啟動 Skyrim，也不要讓 Dashboard 做任何會改動 Steam 遊戲資料夾的動作。
- 2026-09-26｜已收到第 1 階段補推送（`e20f528`）。GitHub 中繼運作正常，第 2 階段照原指示進行。
  - preflight 的 VRAM 分級已修正：廠商回報的容量常略低於標示（16 GB 顯示 15.9 GB），現在 15.9 GB 會歸到 16 GB 級（Tier A/S）。第 1 階段不必重跑。
  - 第 2 階段完成時，`local-report.md` 請包含：
    - `inventory-mv`、`harvest-mv`（試跑與 `--apply` 各一份）、`zh_extract_official`（試跑與 `--apply`）每份報告的每一行
    - Wabbajack 結果頁有無錯誤或警告
    - 完成後 D 槽剩餘空間
  - 推送後等雲端判讀，再問使用者刪 `D:\WJ-Downloads`。
- 2026-09-26｜第 1 階段判讀：**通過，可以進第 2 階段。**
  - Python 3.13.11（miniconda）可用：工具需要 3.12 以上，第 6 階段的四個套件都有 Windows 的 3.13 版本。不必另裝 3.12。
  - 分頁檔「C 槽系統管理＋D 槽固定 40960 MB」接受，不用改（RAM 64 GB，總量足夠）。
  - `文件\My Games\Skyrim Special Edition\Skyrim.ini` 的 `sLanguage=CHINESE` 不影響：M&V 與 Nolvus 的 MO2 都用設定檔自己的 ini（LocalSettings=true）。不要改它，也不要刪。
  - preflight 的 Defender 誤報已修正：一般權限時改報 [資訊]。
  - **不要**下載 M&V 2.40.1（file 703199）：它已從 Wabbajack CDN 下架，只剩 Nexus 封存檔（約 5 GB）。第 4 階段 `audit_skse` 找出真正不能在 1.5.97 載入的 DLL 後，雲端再逐一查 1.5.97 版本。第 4 階段執行 `audit_skse.py` 時不要加 `--mv-1597-map`。
  - **第 3 階段前，不要從 Steam 啟動 Skyrim**：若 Bethesda 推出新版，啟動時會被更新，Wabbajack 與 Nolvus 的檔案檢查就會失敗。
  - `git pull` 一律改用 `git pull --rebase`。
  - 階段結束時要把 `status.md` 與 `local-report.md` 一起 **push**（這次的 b22a09a 只提交沒推送）。
- 2026-09-26｜第 2 階段注意事項：
  - Wabbajack：Install Location `D:\MV`、Download Location `D:\WJ-Downloads`。需要約 616 GB，D 槽剩約 1047 GB，足夠。C 槽只剩約 153 GB，不要把任何下載或安裝位置設在 C 槽。
  - 安裝完成後依序執行：inventory → harvest 試跑 → harvest `--apply` → `pip install lz4` → extract_official 試跑 → `--apply`，並把每份報告的結果寫進 `local-report.md` 後推送。
  - 刪除順序（刪除前都要問使用者）：
    1. 先刪 `D:\WJ-Downloads`（約 230 GB）。
    2. `D:\MV` 保留到第 3 階段 Nolvus 裝好、第 4 階段 `manifest` 跑完再刪，萬一需要重新擷取還能用。刪 WJ-Downloads 後 D 槽約剩 660 GB，夠裝 Nolvus（426 GB）。
- 2026-09-26：連線測試確認本地與雲端互相看不到，SendMessage 不通。改用 GitHub 中繼：
  - 本地寫 `progress/local-report.md`，連同 `status.md` 提交並推送。
  - 使用者回雲端說「已推送」。
  - 雲端的回覆寫在這個檔案。
- 2026-09-26：從第 1 階段開始。依 `docs/01-準備筆電.md` 完成後執行 `python tools/preflight.py --install-drive D:`，把 `reports/preflight-*.txt` 的每一行結果寫進 `local-report.md` 後推送。
