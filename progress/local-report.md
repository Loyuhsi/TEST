# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：3 安裝 Nolvus
- 日期：2026-09-26
- 結論：**完成**。Nolvus Awakening 6.0.20 Ultimate（無 SREX，Nudity Yes）已安裝並能開到主選單；inventory 通過；harvest `--stock-game --apply` 注意（來源缺少 12，沒有失敗）。`D:\PM` 現有 3565 個 mod 資料夾與 1.5.97 STOCK GAME。

## 工具結果（照抄 reports\*.txt 的每一行）
```
== inventory-nolvus 報告 (2026-09-26 18:16) ==
[通過] mod 資料夾數：3684（設定檔 Nolvus Awakening 啟用 3683 個）
[資訊] 含 Nexus ID 的 mod：3302/3684
[資訊] SKSE DLL 類型：ae_only=3, multi=97, not_skse=1, se=80
[資訊] mods 總大小：392.3 GB
[資訊] 遊戲執行檔版本：1.0.0.0（STOCK GAME）
[資訊] SKSE 版本檔：skse64_1_5_97.dll, skse64_steam_loader.dll
[資訊] 遊戲根目錄的 ENB/ReShade 檔：d3d11.dll, d3dcompiler_46e.dll, dxgi.dll, enbseries.ini, enblocal.ini, enbseries/
[資訊] Skyrim - Interface.bsa：存在
總結：[通過]

== harvest-nolvus 報告 (2026-09-26 18:17)（試跑）==
[資訊] 模式：試跑（未寫入任何檔案，加 --apply 才會執行）
[通過] STOCK GAME 已連結：543 個檔案；移除 ENB/ReShade：d3d11.dll, d3dcompiler_46e.dll, dxgi.dll, ReShade.ini, reshade-shaders, enbseries, enbcache, enblocal.ini, enbseries.ini
[注意] 計畫中要從 nolvus 擷取的資料夾：2931 個：完成/已存在 2919，來源缺少 12（見 harvest-nolvus.csv）
[資訊] 共享資料量（硬連結不佔額外空間）：305.1 GB
總結：[注意]

== harvest-nolvus 報告 (2026-09-26 18:18)（--apply）==
[資訊] 模式：實際執行
[通過] STOCK GAME 已連結：543 個檔案；移除 ENB/ReShade：d3d11.dll, d3dcompiler_46e.dll, dxgi.dll, ReShade.ini, reshade-shaders, enbseries, enbcache, enblocal.ini, enbseries.ini, enbcomplexparallax.ini, enbgrasscollisions.ini
[注意] 計畫中要從 nolvus 擷取的資料夾：2931 個：完成/已存在 2919，來源缺少 12（見 harvest-nolvus.csv）
[資訊] 共享資料量（硬連結不佔額外空間）：305.1 GB
總結：[注意]
```

## 說明
- **遊戲執行檔版本 1.0.0.0**：Nolvus 降版後的 `STOCK GAME\SkyrimSE.exe`（34,769,792 bytes）字串版本 FileVersion／ProductVersion 都是 **1.5.97.0**，只有 VS_FIXEDFILEINFO 的數字欄位是 1.0.0.0；`pm/pe.file_version` 讀的是後者（M&V 與 Steam 版兩個欄位一致，分別是 1.6.1170.0、1.7.104.0）。SKSE 以 runtime 01050610（1.5.97）初始化。建議工具在數字欄位是 1.0.0.0 時改讀字串版本。
- **第一次啟動（docs/03 第 6 節）**：Dashboard 的 Play 會開 Nolvus 自己的 MO2 2.4.4（設定檔 Nolvus Awakening，啟用 3615 個 mod、3765 個插件），從 MO2 以「Nolvus」執行檔 Run。遊戲載入到 Nolvus 主畫面，出現 Open Animation Replacer 2.3.6、Immersive Equipment Displays 等 SKSE 通知後關閉，沒有載入存檔。`skse64.log`：SKSE 2.0.20、**174 個外掛 loaded correctly，沒有 error／fail／incompatible**；沒有 crash log。之後關閉遊戲與 MO2。
- **Profile 備份（第 7 節）**：`D:\Backups\Nolvus-Awakening-profile-2026-09-26.zip`（modlist、plugins、loadorder、各 ini）。
- **harvest 之後**：`D:\PM\STOCK GAME\SkyrimSE.exe` 存在；ENB／ReShade 已移除，只剩 `ReShade.log`（工具的移除清單沒有它，無害）；`D:\Nolvus` 原本的 ENB 檔仍在；`harvest-nolvus.csv` 錯誤 0；`D:\PM\mods` 共 3565 個資料夾（M&V 645＋Nolvus 2919＋官方繁中字串 1）；D 槽剩 457.9 GB。
- **`[注意]` 來源缺少 12 個**（`missing_in_source`），我在 Nolvus 與 `D:\MV\mods` 找同名資料夾：

| 資料夾 | provenance 選項／版本 | Nolvus 6.0.20 | `D:\MV\mods` |
|---|---|---|---|
| Cached Recursive Directory Walk | Always Install 1.1.4 | 無 | **有同名** |
| Collision Sentinel - Crash Fix | Always Install 2.1.0 | 無 | **有同名** |
| Media Keys Fix SKSE | Always Install 1.0.1 | 無 | **有同名** |
| KreatE | Kauz ENB 1.3.1 | 無（我們選 Cabbage） | **有同名** |
| Native EditorID Fix | Kauz ENB 1.2.2 | 無（我們選 Cabbage） | **有同名** |
| SKSE Menu Framework2 | Always Install 3.9 | 無 | 只有 `SKSE Menu Framework`（無 2） |
| SkyPatcher Keyword Framework | Always Install 1.4.0 | 無（只有 `SkyPatcher`） | 無 |
| Quest Journal Overhaul | Always Install 1.3 | 無（只有 `Quest Journal Limit Bug Fixer`） | 無 |
| Prisma UI - Next-Gen Web UI Framework | Always Install 1.4.1 | 無 | 無 |
| Dirt Cliffs Enhancement - High Quality Ivy | Always Install 1.3.0 | 無 | 無 |
| Modern First Person Animation Overhaul | 6.0.21 頁面沒有（6.0.20 快照有） | 無（有 `Comprehensive First Person Animation Overhaul`） | 無 |
| Dawnguard Arsenal - Scabbardless Greatswords Loose File Replacers | 6.0.21 頁面沒有（6.0.20 快照有） | 無 | 無 |

  前 5 個可改從 `D:\MV` 擷取（`D:\MV` 保留到第 4 階段 `manifest`）。其餘應是 6.0.21 才加入或改名，需要雲端判斷來源。
- **Nolvus 安裝過程**：13:07 開始，18:08「Instance Finalized」。中途家中 Wi-Fi 斷線，41 個 mod 在重試 3 次後失敗（無法解析 api／cf-files.nexusmods.com、drive.google.com 等網路錯誤），Dashboard 顯示「Installation Failed：41 errors on 50 maximum」。網路恢復後按 Retry → Resume，41 個全部重新下載安裝，最後錯誤 0、3626/3626。
- 使用者已刪除 `D:\WJ-Downloads`。

## 雲端要求的 Nude／New Gentleman 資料（e53c04c）
1. Nolvus `MODS\profiles\Nolvus Awakening\modlist.txt`（名稱含 `New Gentleman` 或 `Nude` 的行，前後各 2 行，行號從 1 起算）：
```
   31: +Grass Cache - Ultimate
   32: +LODGEN
   33: +BodySlide (Nude)
   34: +Nemesis Output
   35: +Synthesis Patch - NOSREX

 2742: +Expressive Facegen Morphs
 2743: +Highly Improved Male Body Overhaul
 2744: +The New Gentleman - Nolvus Settings
 2745: +The New Gentleman
 2746: +Caliente's Beautiful Bodies Enhancer - 3BA - Wyrmstooth
 2747: +Caliente's Beautiful Bodies Enhancer - 3BA - The Wheels of Lull Patch
```
2. 這些資料夾的插件：
   - `BodySlide (Nude)`：沒有插件。
   - `The New Gentleman - Nolvus Settings`：沒有插件。
   - `The New Gentleman`：`TheNewGentleman.esp`，**ESL 旗標：有**（ESM 旗標也有），3 個前置檔。
3. `plugins.txt` 位置（第 133 行，前後各 2 行）：
```
  131: *IcyFixesLite.esl
  132: *WindhelmIcicles.esl
  133: *TheNewGentleman.esp
  134: *TrueHUD.esl
  135: *Draugr Armor Warrior.esl
```
4. `BodySlide (Nude)`：8292 個檔案，6527.7 MB。
- 補充：`Highly Improved Male Body Overhaul` 在官方清單是 Always Install，目標清單已有（harvest_nolvus），不屬於 Nude 選項。

## 需要雲端決定的事
1. 12 個來源缺少的資料夾要從哪裡取得（前 5 個 `D:\MV` 有同名資料夾）。
2. The New Gentleman 與 BodySlide (Nude) 加入 `D:\PM` 的方式（data/target、provenance、docs/05）。
3. 要不要把 Nolvus 6.0.20 實際安裝的 `modlist.txt`／`plugins.txt`／`loadorder.txt` 全文推上來（例如 `data/snapshots/nolvus-6.0.20-installed/`）？目前只有備份在本機。
4. `pm/pe.file_version` 讀數字欄位的問題（見上），以及 harvest 的 ENB 移除清單可加上 `ReShade.log`。
