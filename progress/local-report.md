# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：2 安裝 M&V（進行中）＋ 3 Nolvus（已按 Start，但在遊戲檔檢查失敗，暫停）
- 日期：2026-09-26
- 結論：**需要雲端決定**：Rare Curios（`ccbgssse037-curios.bsa/.esl`）M&V 與 Nolvus 要的版本不同

## 工具結果（照抄關鍵行；第 2 階段的 tools 報告還沒產生）
Wabbajack 4.2.3 日誌（第一次安裝，11:14 中止）：
```
[ERROR] (Wabbajack.Installer.StandardInstaller) Missing game file Data_ccbgssse037-curios.bsa. This could be caused by missing DLC or a modified installation.
[ERROR] (Wabbajack.Installer.StandardInstaller) Missing game file Data_ccbgssse037-curios.esl. This could be caused by missing DLC or a modified installation.
[FATAL] (Wabbajack.Installer.StandardInstaller) Unable to download Data_ccbgssse037-curios.bsa (GameFileSourceDownloader+State|SkyrimSpecialEdition|1.7.104.0|data\ccbgssse037-curios.bsa)
[FATAL] (Wabbajack.Installer.StandardInstaller) Unable to download Data_ccbgssse037-curios.esl (GameFileSourceDownloader+State|SkyrimSpecialEdition|1.7.104.0|data\ccbgssse037-curios.esl)
[FATAL] (Wabbajack.Installer.StandardInstaller) Cannot continue, was unable to download one or more archives
```
Wabbajack 重試後（11:37 起）：`Next Step: Priming VFS` → `Building Folder Structure` → `Installing files`，之後沒有新的 ERROR／FATAL。12:07 進度 `[12/14] Installing files (227.4GB/359.8GB)`，D 槽剩 679.6 GB。

Nolvus Dashboard 3.8.11 的 `Log.txt`（11:47）：
```
Loading game meta data package using Skyrim AE 1.7.104.0 template
Checking game file : ccbgssse036-petbwolf.esl
Checking game file : ccbgssse037-curios.bsa
Error detected, rollbacking changes...
Error Form => Hash for game file : C:\program files (x86)\steam\steamapps\common\Skyrim Special Edition\Data\ccbgssse037-curios.bsa does not match!
```
（前面的 CC 依字母順序都通過，包括 ccbgssse001-fish、ccbgssse025-advdsgs。）

## 已做的處理
- 起因：第 1 階段在遊戲內用 Creations「Download all owned Creation Club Creations」下載 AE 內容時，74 個 CC 全部重新下載，連 Steam 本來就附的 4 個免費 CC 也被覆寫（檔案修改時間 09:03–09:05，建立時間仍是 Steam 安裝時）。
- 雜湊比對（Wabbajack xxHash64，base64）：

| 檔案 | M&V 2.6.2 modlist 預期 | Creations 版（第 1 階段下載後） | 備註 |
|---|---|---|---|
| ccbgssse037-curios.bsa（111,740,475 bytes） | `DG3YZQj7xwk=` | `FQbA20bA5Dw=` | 大小相同、內容不同 |
| ccbgssse037-curios.esl（37,476 bytes） | `STK4THfMHzw=` | `it6+eSu4OCw=` | 大小相同、內容不同 |
| ccbgssse001-fish.bsa／.esm | `FC+yJIfHEZY=`／`+LybF813t+s=` | 相同 | 重寫後內容不變 |

- 使用者同意後，用 Steam「驗證遊戲檔案完整性」：只有 Curios 的 2 個檔驗證失敗並重新下載，換回 Steam 版後雜湊 = M&V 預期。遊戲仍是 1.7.104.0、build 24914197、CC 74 個、語言 English。Wabbajack Retry 後順利進入 Installing files。
- Nolvus 準備：
  - Dashboard：nolvus.net 官方連結（作者 GitHub 發行檔）的 NolvusUpdater 1.3.9.0。GitHub CDN 單一連線只有約 40 KB/s，改用 32 條連線分段下載同一個 `Binaries3811.zip`（大小與 GitHub 記錄相同、7-Zip CRC 通過），照 Updater 原始碼的做法解壓到 `D:\Nolvus`；Updater 回報 up to date，版本 3.8.11.0。
  - 使用者自己完成 Nexus SSO（Premium）、nolvus.net、mega 登入。
  - 實例清單顯示 **Nolvus Awakening v6.0.20**（不是 6.0.21）。
  - 選項（Installation Summary）：16:9、2560x1600、`D:\Nolvus\Instances\Nolvus Awakening`、Archiving No、Downscaling No、**Ultimate**、TAA、Ini High、SR Exterior Cities No、Frame Generation No、Nudity No、Fantasy、Alternate Leveling Yes、Gore Yes、Controller No、ENB Cabbage、Edge UI、難度 True Nord 預設（Combat Scaling Medium、Exhaustion Yes、Nerf Power Attacks Both、Boss Encounter Yes）、CDN Nexus、錯誤處理「50 個錯誤才停」。
  - Dashboard 3.8.11 沒有提供 **Enemies Resistance**、**Stances Perk Tree** 的開關。
  - 11:39 Wabbajack 進入安裝階段時 D 槽剩 **974.6 GB**（≥ 950），使用者同意後 11:46 按 Start → 遊戲檔檢查在 Curios 失敗 → Dashboard 自動 rollback，`InstancesData.xml` 仍是空的，沒有留下任何變更。
- M&V 的 `Stock Game\Data` 目前還沒有 Curios；Wabbajack 此刻正在從 Steam 遊戲資料夾的 BSA 解出檔案，所以裝完前不能動 Steam 資料夾。

## 需要雲端決定的事
1. **Curios 衝突的處理方式**。使用者已同意的做法（等雲端意見後才執行）：
   1. M&V 裝完、確認 Curios 已複製進 `D:\MV\Stock Game`。
   2. 把 Steam 資料夾裡 Steam 版的 2 個 Curios 檔搬到備份資料夾（不刪除）。
   3. 先確認 Steam 公開版本仍是 build 24914197，再從 Steam 啟動遊戲一次，用 Creations 重新下載 Curios，不載入存檔就離開。這與「第 3 階段完成前不從 Steam 啟動 Skyrim」相牴觸，請確認。
   4. 重開 Dashboard，同樣選項再選一次，接著安裝 Nolvus。
2. **最終 `D:\PM` 要用哪一版 Curios**：`D:\PM\STOCK GAME` 來自 Nolvus，會是 Creations 版；但 M&V 的 Rare Curios 相關 mod（例如 `Apothecary - Rare Curios Patch`、`Argentum - Rare Curios Add-On 01`）是照 Steam 版做的。兩版 `.esl` 大小相同、內容不同，差異是否影響這些 patch？
3. Dashboard 3.8.11 沒有 Enemies Resistance、Stances Perk Tree 的開關，這樣可以嗎？
4. 下次在遊戲內下載 CC 時，是否應改用「只下載缺少的」而不是「Download all owned」？這可以寫進 `docs/01`。
