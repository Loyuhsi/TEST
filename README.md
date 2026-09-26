# Pages 混合清單：下載、組合與繁中化工具包

這份清單源自 `Pages_Modlist_WIP`，以 **Nolvus Awakening（v6）** 為基底，加上 **Mages & Vikings（M&V）** 和其他 mod。這個工具包負責三件事：

- 在 Windows 筆電上把清單組合出來。
- 翻成**台灣繁體中文**。
- 調整到筆電能順跑。

**想讓筆電上的本地 Claude 代你操作？** 照 [`docs/09-本地Claude代理.md`](docs/09-本地Claude代理.md) 設定 Claude Desktop 的 Code 分頁與電腦操作，貼上開場指令即可。它依 [`CLAUDE.md`](CLAUDE.md) 與技能 `.claude/skills/pages-modlist/` 執行，刪除、花錢、推送前一定會先問你。

完整計畫與研究結論見 [`docs/00-計畫.md`](docs/00-計畫.md)，查證過的研究筆記（英文）在 [`docs/research/`](docs/research/)。

> **分工**
> - 雲端的 Claude 不能操作你的筆電，只負責產生資料、工具和手冊。
> - 你照手冊逐步執行，每個階段把 `reports\` 資料夾裡的報告（`.txt` + `.json`）上傳回對話，由 Claude 判讀並決定下一步。

## 階段地圖

| 階段 | 做什麼 | 手冊 | 主要工具 |
|---|---|---|---|
| 1 | 準備筆電：Steam、CC、執行環境、分頁檔、Defender | [01-準備筆電](docs/01-準備筆電.md) | `tools\preflight.py` |
| 2 | 安裝 M&V，擷取需要的資料夾，取出官方繁中字串，再刪除 M&V | [02-安裝MV並擷取](docs/02-安裝MV並擷取.md) | `inventory.py`、`harvest.py`、`zh\extract_official.py` |
| 3 | 安裝 Nolvus v6（6.0.20 Ultimate，不含 SREX），擷取並連結 STOCK GAME | [03-安裝Nolvus](docs/03-安裝Nolvus.md) | `inventory.py`、`harvest.py --stock-game` |
| 4 | 組合 D:\PM：建立清單、下載其餘 mod、修剪相依、檢查插件與 DLL | [04-組合清單](docs/04-組合清單.md) | `manifest.py`、`build_instance.py`、`nexus_fetch.py`、`prune_dependents.py`、`check_plugins.py`、`audit_skse.py` |
| 5 | 重建輸出檔，完成英文基準測試並凍結 | [05-重建輸出](docs/05-重建輸出.md) | `build_instance.py sync-order` |
| 6 | 繁中化（不新增任何插件） | [06-繁中化](docs/06-繁中化.md) | `tools\zh\*.py` |
| 7 | 筆電效能調校 | [07-效能調校](docs/07-效能調校.md) | — |
| 8 | 凍結、備份與維護 | [08-凍結備份與維護](docs/08-凍結備份與維護.md) | — |

輔助文件：
- [本地 Claude 代理](docs/09-本地Claude代理.md)
- [回報格式](docs/回報格式.md)
- [介面檢查表](docs/介面檢查表.md)
- [測試路線](docs/測試路線.md)

## 在筆電上開始

1. 安裝 [Python 3.12](https://www.python.org/downloads/windows/)，安裝時勾選 **Add python.exe to PATH**。
2. 把這個倉庫下載到短路徑，例如 `C:\PagesTools`（GitHub 的 **Code → Download ZIP**，或 `git clone`）。
3. 開啟「命令提示字元」：
   ```bat
   cd /d C:\PagesTools
   python tools\preflight.py --install-drive D:
   ```
4. 把產生的 `reports\preflight-*.txt` 和 `.json` 上傳回對話。

第 6 階段的翻譯工具需要額外套件：`python -m pip install -r requirements-zh.txt`。

## 安全原則

- **會寫入檔案的工具預設都只是「試跑」**，要加 `--apply` 才會真的寫入，並且會先備份。
- **Nexus 與 Claude 的 API 金鑰只從環境變數讀取**（`NEXUS_API_KEY`、`ANTHROPIC_API_KEY`），不會寫入任何檔案。
- **報告會自動把 Windows 使用者名稱遮成 `%USERPROFILE%`。**
- **用硬連結組合**：D:\PM 以硬連結共用 Nolvus 與 M&V 的檔案，不佔額外空間。原始安裝刪除後，檔案仍然存在。
- **不重新散佈任何 mod 或翻譯**。蘇禾的漢化包只限個人使用，整合結果不得分享。

## 雲端分析結果（`data/analysis/`）

| 檔案 | 內容 |
|---|---|
| `provenance.csv` | 目標清單 4044 個 mod 的來源分類與建議動作。分類：Nolvus 2583（另有舊版 55）、M&V 556、兩者皆有 384、其他 Nexus mod 415（可直接下載 386，需人工確認 29）、找不到來源 26、需重建 9、自製 3、非 Nexus 13 |
| `mv_folder_map.csv` | M&V 2.6.2 的 3694 個資料夾 → Nexus 模組／檔案 ID、SKSE DLL、插件 |
| `nexus_candidates.csv` | 兩份基底清單都沒有的 467 個資料夾在 Nexus 上的候選來源（找到 418 個，其中 390 個附建議檔案） |
| `drop_list.csv` | 依決定捨棄的項目，以及作者自製的 `[FIX]` 插件 |
| `data/decisions.csv` | 你或 Claude 手動覆寫個別資料夾動作的地方（`folder,action,note`） |

重新產生：
```
python tools/analysis/mv_wabbajack_map.py --out-dir data/analysis
python tools/analysis/nexus_identify.py
python tools/analysis/provenance.py
```

## 開發

```
python -m pip install -r requirements-zh.txt pytest
python -m pytest
```
