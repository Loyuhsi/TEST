# 第 3 階段：安裝 Nolvus v6

這一階段用 Nolvus Dashboard 安裝 Nolvus Awakening **6.0.20 Ultimate（不含 SR Exterior Cities）**，再把目標需要的資料夾和 STOCK GAME（1.5.97）以硬連結放進 `D:\PM`。

- 預估時間：半天左右。Nolvus 官方說有 Premium 和快速網路約 1 小時；193 GB 在 100 Mbps 下光下載就要 4–5 小時。
- 前提：第 2 階段已完成，D 槽剩餘 500 GB 以上。
- Steam 語言仍是 English，Steam 版 Skyrim 仍是 1.7.104。第 1 階段之後沒有從 Steam 啟動過（為了換 Rare Curios 而啟動一次除外，見「常見問題」）。
- `%LOCALAPPDATA%\ModOrganizer` 不存在。

> **注意**：要盡快安裝。Nolvus 6.0.21 目前是 beta，轉正式版後 Dashboard 會改裝 6.0.21，目標用到的 55 個 mod 就會消失。

## 1. 下載 Nolvus Dashboard

1. 到 nolvus.net 的 Downloads 頁面，下載 `NolvusUpdater.exe`。
2. 把它放進 `D:\Nolvus`，按兩下執行。它會下載並安裝 Dashboard 到同一個資料夾。
3. 規則：
   - Dashboard 一定要在**短路徑**，例如 `D:\Nolvus`。否則 v6 會無法啟動。
   - 不要放在桌面、文件、Program Files 或 steamapps 裡。
   - 安裝後**永遠不要移動** `D:\Nolvus`。
4. 確認 Dashboard 版本是 **3.8.11 以上**（3.8.11 才支援 Steam 1.7.104 的降版）。

## 2. 登入

1. 用 **nolvus.net 帳號**登入 Dashboard。不要在這裡輸入 Nexus 的密碼。
2. 依畫面指示連結 **Nexus 帳號**（Nexus SSO，會開瀏覽器授權）。
3. 在 Dashboard 設定中，關閉 mega 的匿名模式，填入你的 **mega.nz** 帳號。這可以避免 402 錯誤。

## 3. 建立新實例與選項

選 **Nolvus Awakening** 建立新實例，名稱保持預設的 `Nolvus Awakening`。依下表選擇：

| 畫面／項目 | 選擇 | 原因 |
|---|---|---|
| 語言 | **English** | 必須和 Steam 相同；Dashboard 沒有中文 |
| 版本（Variant） | **Ultimate** | 目標用到 Ultimate 限定的 mod |
| SR Exterior Cities | **不要** | 目標沒有；也最吃 VRAM |
| 抗鋸齒（Anti-aliasing） | **TAA** | 依目標推定。不要選 DLAA（筆電可能偵測不到顯示卡） |
| Nolvus 內建 Frame Generation | **關閉** | 之後改用 Community Shaders 的補幀 |
| Downscaling | **關閉** | |
| 若出現 INI 設定（Low／Medium／High） | High | 之後第 7 階段再調 |
| 螢幕比例 | **16:9** | |
| 介面（UI） | **Edge** | |
| 戰鬥附加元件（Combat） | **Fantasy Combat** | |
| 其他附加元件 | **全部勾選**：Boss Encounter、Alternate Leveling、Gore、Exhaustion | Dashboard 3.8.11 裝 6.0.20 時沒有 Enemies Resistance、Stances Perk Tree 開關（6.0.21 才有），目標用的舊版 True Armor 與 Stances Perk System 已內含 |
| 裸體（Nudity） | **No** | 目標沒有這個選項的 mod |
| 難度 | **True Nord** | 細項（Combat Scaling、Exhaustion、Nerf Power Attacks、Boss Encounter）用預設 |
| BodySlide | **Dressed** | |
| ENB | 任選一個（例如 Cabbage） | 之後會整個移除 |
| 封存（Archiving） | **關閉** | 省下 193 GB |

- 硬體檢查畫面只是參考，確認後繼續即可。
- 確認對話框會提醒：版本、選項和難度安裝後**不能更改**。按確認前請再對一次上表。

## 4. 確認套件版本是 6.0.20

- 在開始安裝前的確認畫面（或實例清單）上，找到顯示的 Nolvus 版本號。
- 必須是 **6.0.20**。
- **如果顯示 6.0.21（或標示 BETA），立刻停下來，不要安裝**，截圖回報 Claude。

## 5. 安裝

1. 按開始安裝，等它完成。可以中途關閉，重開 Dashboard 會接續安裝。
2. 下載失敗時：

| 錯誤 | 處理 |
|---|---|
| 402（mega） | 確認已填入 mega 帳號並關閉匿名模式 |
| 509（mega） | mega 每日 5 GB 限額用完，等隔天再繼續 |
| 429（Google Drive） | 稍後再試 |
| 某個檔案一直下載失敗 | 在 nolvus.net 用搜尋圖示找到該檔手動下載，放進 `D:\Nolvus\Cache\downloads`，再繼續安裝 |

Nolvus 的 FAQ 提到部分地區無法下載某些檔案、建議使用 VPN。台灣的情況未知，真的卡住再回報。

## 6. 第一次啟動

1. 在 Dashboard 的實例上按 Play（或執行實例資料夾中的 `NolvusLauncher.exe`）。
2. 進到主選單後離開遊戲。第一次啟動可能比較久。
3. 確認版本：
   - 對 `D:\Nolvus\Instances\Nolvus Awakening\STOCK GAME\SkyrimSE.exe` 按右鍵 →「內容」→「詳細資料」。
   - 檔案版本應是 **1.5.97.0**。
4. 開啟 `%USERPROFILE%\Documents\My Games\Skyrim Special Edition\SKSE\skse64.log`，看看有沒有錯誤（error／failed 字樣）。
   - 如果「文件」資料夾被 OneDrive 同步，路徑會在 `OneDrive\文件` 底下。

## 7. 備份 Nolvus 原本的 Profile

1. 開啟 `D:\Nolvus\Instances\Nolvus Awakening\MODS\profiles`。
2. 對 `Nolvus Awakening` 資料夾按右鍵 →「壓縮為 ZIP 檔案」（Windows 10 是「傳送到 → 壓縮的 (zipped) 資料夾」）。
3. 把 ZIP 移到安全的地方，例如另一顆硬碟或 `D:\Backups`。

## 8. 盤點與擷取

先關閉 Nolvus 的 MO2 和遊戲。

1. 盤點（唯讀）：
   ```bat
   cd /d C:\PagesTools
   python tools\inventory.py --source nolvus --instance "D:\Nolvus\Instances\Nolvus Awakening"
   ```
   報告中「遊戲執行檔版本」應是 1.5.97.0。
2. 擷取，**先試跑**：
   ```bat
   python tools\harvest.py --from nolvus --instance "D:\Nolvus\Instances\Nolvus Awakening" --pm D:\PM --stock-game
   ```
3. 看結果沒有 `[失敗]`，再**實際執行**：
   ```bat
   python tools\harvest.py --from nolvus --instance "D:\Nolvus\Instances\Nolvus Awakening" --pm D:\PM --stock-game --apply
   ```
4. `--stock-game` 會做兩件事：
   - 把 STOCK GAME 以硬連結放進 `D:\PM\STOCK GAME`。
   - 刪除 `D:\PM\STOCK GAME` 裡的 ENB／ReShade 檔（`d3d11.dll`、`d3dcompiler_46e.dll`、`d3dcompiler_47.dll`、`enb*` 等），因為 Community Shaders 遇到它們會停用。Nolvus 原本的那份不受影響。
5. 確認 `D:\PM\STOCK GAME\SkyrimSE.exe` 存在。

## 9. 從此以後

- **不要在 Dashboard 按 Update**，也不要按套用預設載入順序。它會改寫 Nolvus 的 Profile 並重建 mod 資料夾。
- 不要在 Nolvus 的 MO2 裡改名、刪除或移動 mod。把 `D:\Nolvus` 當成唯讀的來源。
- 第 8 階段確認 `D:\PM` 一切正常後，才刪除 `D:\Nolvus`。

## 常見問題

**Dashboard 報「Global ModOrganizer instance has been detected」？**
`%LOCALAPPDATA%\ModOrganizer` 還在。改名成 `ModOrganizer.bak` 後重開 Dashboard。

**Dashboard 說遊戲檔案雜湊不符（hash does not match）？**
先看 Dashboard 的 `Log.txt` 是哪個檔：
- **`ccbgssse037-curios.bsa`／`.esl`**：Steam 資料夾裡是 Steam 版 Rare Curios（第 2 階段為了 M&V 換回來的），Nolvus 要 Bethesda.net 版。
  1. 確認 M&V 已經裝完，而且 `D:\MV\Stock Game\Data` 裡有這 2 個檔。
  2. 把 Steam 資料夾裡的這 2 個檔**搬到** `D:\Backup\Curios-Steam`。
  3. 如果 `D:\Backup\Curios-Creations` 有第 1 階段的備份，把它**複製**回 Steam 的 `Data`。
  4. 沒有備份時，只好從 Steam 啟動遊戲一次，到 CREATIONS 重新下載 Rare Curios，不載入存檔就離開。
     - 遊戲失去焦點時下載會暫停，下載期間不要切到別的視窗。
     - 啟動器可能重建 `文件` 裡原版的 `Skyrim.ini`／`SkyrimPrefs.ini`，想保留就先備份。
     - 啟動前先確認三件事，否則遊戲可能被更新：
       - 遊戲庫的按鈕是「開始遊戲」，不是「更新」。
       - 下載頁沒有 Skyrim 的排程。
       - 公開 build 沒有變：看 SteamDB；進不去時，看 `steamapps\appmanifest_489830.acf` 的 `buildid` 與 `TargetBuildID` 是否相同。
  5. 重開 Dashboard，用同樣的選項再試一次。還是不符就回報 Claude。
- **其他檔案**：通常是 Steam 版不是最新、CC 沒下載齊，或 Steam 語言不是 English。先回到第 1 階段檢查，並回報 Claude。

**Dashboard 認不出筆電的 NVIDIA 顯示卡？**
這只影響 DLAA。我們選 TAA，可以直接繼續。

**想改選項怎麼辦？**
安裝後不能改，只能重裝。所以按確認前請仔細對照第 3 節。

## 退出條件

- [ ] Dashboard 3.8.11 以上，安裝的是 **6.0.20** Ultimate（無 SR Exterior Cities），選項與第 3 節相同，封存已關閉。
- [ ] 能用 Nolvus 啟動器開到主選單；`STOCK GAME\SkyrimSE.exe` 是 1.5.97.0；`skse64.log` 沒有錯誤。
- [ ] Nolvus 的 Profile 已壓縮備份。
- [ ] `inventory-nolvus` 已完成；`harvest-nolvus` 已用 `--apply` 執行且沒有 `[失敗]`。
- [ ] `D:\PM\STOCK GAME\SkyrimSE.exe` 存在。

## 要回傳的檔案

- `reports\inventory-nolvus.txt`、`inventory-nolvus.json`、`inventory-nolvus.csv`
- `reports\harvest-nolvus.txt`、`harvest-nolvus.json`、`harvest-nolvus.csv`（`--apply` 之後的那一份）
- `D:\Nolvus\Instances\Nolvus Awakening\MODS\profiles\Nolvus Awakening\` 裡的 `modlist.txt`、`plugins.txt`、`loadorder.txt`
- Dashboard 確認畫面（顯示版本與選項）的截圖
- `skse64.log`（上傳前先把裡面你的 Windows 使用者名稱取代成 `USER`，見 [回報格式](回報格式.md)）
