# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：2 安裝 M&V 並擷取（工具全部跑完）＋ 3 Nolvus（安裝中）
- 日期：2026-09-26
- 結論：第 2 階段的報告都沒有 `[失敗]`。Rare Curios 照 45e52d6 處理完成，Nolvus 已在 13:07 開始安裝並通過遊戲檔檢查。待決：刪 `D:\WJ-Downloads`（會先問使用者），以及 Nudity 改 Yes 對 `D:\PM` 的影響。

## 工具結果（照抄 reports\*.txt 的每一行）
```
== inventory-mv 報告 (2026-09-26 13:08) ==
[通過] mod 資料夾數：3694（設定檔 Default 啟用 3577 個）
[資訊] 含 Nexus ID 的 mod：3547/3694
[資訊] SKSE DLL 類型：ae_only=74, multi=239, not_skse=1, se=2
[資訊] mods 總大小：336.1 GB
[資訊] 遊戲執行檔版本：1.6.1170.0（Stock Game）
[資訊] SKSE 版本檔：無
[資訊] 遊戲根目錄的 ENB/ReShade 檔：無
[資訊] Skyrim - Interface.bsa：存在
總結：[通過]

== harvest-mv 報告 (2026-09-26 13:09)（試跑）==
[資訊] 模式：試跑（未寫入任何檔案，加 --apply 才會執行）
[通過] MO2 程式與工具：30 項（含 tools\）
[注意] 計畫中要從 mv 擷取的資料夾：647 個：完成/已存在 645，來源缺少 2（見 harvest-mv.csv）
[資訊] 共享資料量（硬連結不佔額外空間）：27.6 GB
[資訊] 下一步：刪除 D:\MV 前，先執行 tools\zh\extract_official.py 取出官方繁中字串與字型
總結：[注意]

== harvest-mv 報告 (2026-09-26 13:10)（--apply）==
[資訊] 模式：實際執行
[通過] MO2 程式與工具：30 項（含 tools\）
[注意] 計畫中要從 mv 擷取的資料夾：647 個：完成/已存在 645，來源缺少 2（見 harvest-mv.csv）
[資訊] 共享資料量（硬連結不佔額外空間）：27.6 GB
[資訊] 下一步：刪除 D:\MV 前，先執行 tools\zh\extract_official.py 取出官方繁中字串與字型
總結：[注意]

== zh_extract_official 報告 (2026-09-26 13:10)（試跑）==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] 中文字串表：21 個
[通過] 中文字型與介面檔：fonts_cn.swf, fontconfig_cn.txt, translate_chinese.txt
[通過] 有英文但沒有中文字串的插件：無
總結：[通過]

== zh_extract_official 報告 (2026-09-26 13:10)（--apply）==
[資訊] 模式：實際執行
[通過] 中文字串表：21 個
[通過] 中文字型與介面檔：fonts_cn.swf, fontconfig_cn.txt, translate_chinese.txt
[通過] 有英文但沒有中文字串的插件：無
[資訊] 字形判斷：_resourcepack_chinese.dlstrings：unknown
總結：[通過]
```

## 說明與已做的處理
- **`[注意]` harvest 來源缺少 2 個**：`ImmersiveHUD SKSE`、`Load Time Profiler`（`missing_in_source`）。M&V 2.6.2 的 mods 裡找不到改名的對應資料夾。照手冊第 4 階段從 Nexus 下載。
- **字形判斷 unknown**：工具只抽樣排序第一個的字串表，這次是 `_resourcepack_chinese.dlstrings`，但它是**空檔（0 筆）**。我用同一個 `script_guess` 逐一檢查 21 個表：所有有內容的表都是 traditional（例如 `skyrim_chinese.ilstrings` 繁體特徵字 63162、簡體特徵字 0）。空的只有 `_resourcepack_chinese.dlstrings/.ilstrings` 與 `update_traditional.*`。建議工具改成抽樣最大的表，或跳過空檔。
- `D:\PM`：`ModOrganizer.exe` 存在；`tools\` 有 Bethini Pie、DynDOLOD、PGPatcher、Resaver、SSEEdit 4.1.5、xLODGen；`mods` 有 645 個資料夾；`harvest-mv.csv` 錯誤 0。
- **Wabbajack 結果頁**：「Finished Installing Mages & Vikings」，沒有錯誤或警告。日誌在 Retry 之後沒有新的 ERROR／FATAL（第一次中止的原因是 Curios，已在 1ae35a6 回報）。
- **D 槽剩餘**：M&V 裝完時 676 GB；harvest 與擷取後 658 GB（Nolvus 開始寫入後會持續下降）。
- **Rare Curios（照 45e52d6）**：
  - M&V 的 Curios 在 `D:\MV\mods\Creation Club\ccBGSSSE037-Curios.*`（不在 `Stock Game\Data`），SHA256 與當時 Steam 資料夾的相同，而且是獨立副本（C 槽與 D 槽，不是硬連結）。
  - Steam 版搬到 `D:\Backup\Curios-Steam`。
  - 啟動前檢查：按鈕「開始遊戲」、下載頁沒有 Skyrim 排程、`appmanifest` 的 buildid／TargetBuildID 都是 24914197、StateFlags 4。**SteamDB 被瀏覽器驗證頁擋住（自動化無法通過，也不應繞過）**，改以 Steam 官方新聞 API 確認：最新更新仍是 2026-08-20 的「Update 1.7.99 (Updated Aug 27)」。
  - 第一次啟動時，Skyrim 啟動器因為第 1 階段改語言而更新了 `Skyrim_Default.ini`，於是重新偵測硬體，**重建了使用者 `文件` 裡的 `Skyrim.ini`（現為 sLanguage=ENGLISH）與 `SkyrimPrefs.ini`（Ultra、2560x1600、全螢幕）**。原本的中文與畫面設定被覆蓋，只影響不用 mod 的原版遊戲。
  - 遊戲失去焦點時 Creations 下載會暫停，中途遊戲也結束過一次；使用者同意後再啟動一次，補完下載（148 個 cc 檔全部重寫、74 個插件），出現「All Creations Downloaded」後關閉遊戲。沒有載入存檔，點數仍是 0。
  - 核對：Curios 為 `FQbA20bA5Dw=`／`it6+eSu4OCw=`；Fish、Survival、AdvDSGS 雜湊不變；1.7.104.0、build 24914197、74 個 CC。Creations 版複製到 `D:\Backup\Curios-Creations`。
- **Nolvus**：
  - Dashboard 在遊戲切換解析度時跳出 .NET 例外（NullReference）。當時它停在錯誤頁、沒有安裝在跑，已結束並重開。
  - 重選的選項與 1ae35a6 相同，**只有 Nudity 改為 Yes（使用者要求）**。版本仍是 6.0.20，D 槽 676 GB（≥ 500）。13:07 按 Start，遊戲檔檢查全部通過（含 Curios），13:11 進行到「Stock Game Installation 3/4 Patching game files」。

## 需要雲端決定的事
1. **Nudity Yes 對 `D:\PM` 的影響**：Nolvus 會多裝 `The New Gentleman` 與 `The New Gentleman - Nolvus Settings`，BodySlide 輸出改為 `BodySlide (Nude)`。目標清單的 `BodySlide (Dressed)` 在 provenance 是 regenerate，所以不影響重現目標。請問最終 `D:\PM` 要不要也改成 nude（擷取 The New Gentleman、第 5 階段 BodySlide 用 nude 設定與資料夾名稱）？這要在第 4、5 階段的指示裡寫明。
2. **刪 `D:\WJ-Downloads`（約 195 GB）**：第 2 階段沒有 `[失敗]`，照快速路線我會先問使用者再刪。Nolvus 已經在裝，D 槽空間足夠，不急。`D:\MV` 保留到第 4 階段 `manifest` 跑完。
3. `extract_official.py` 的字形判斷抽樣方式（見上）。
4. 使用者 `文件` 裡的 `Skyrim.ini`／`SkyrimPrefs.ini` 被啟動器重建。要不要在手冊提醒「改 Steam 語言後第一次啟動會重建 ini」？原版遊戲的中文設定是否要幫使用者改回，請使用者決定。
