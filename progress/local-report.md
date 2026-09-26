# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：4 組合清單（中途回報：manifest 與 build_instance verify 之後，下載之前）
- 日期：2026-09-26
- 結論：補擷取完成、`D:\PM` 實例建立、MO2 第一次開啟正常（修正了一個 OpenSSL 載入問題）、modlist 比對 `[通過]`。**等雲端判讀 review 54 個、replace_dll 8 個**。另外依 192f48e 推送了 Nolvus 實際安裝清單。

## 工具結果（照抄 reports\*.txt 的每一行）
```
== harvest-mv 報告 (2026-09-26 18:39)（--plan data/decisions.csv，試跑與 --apply 相同）==
[資訊] 模式：實際執行
[通過] 計畫中要從 mv 擷取的資料夾：6 個：完成/已存在 6，來源缺少 0（見 harvest-mv.csv）
[資訊] 共享資料量（硬連結不佔額外空間）：77.6 MB
[資訊] 下一步：刪除 D:\MV 前，先執行 tools\zh\extract_official.py 取出官方繁中字串與字型
總結：[通過]
（6 個：Cached Recursive Directory Walk、Collision Sentinel - Crash Fix、Media Keys Fix SKSE、KreatE、Native EditorID Fix、SKSE Menu Framework2 ← SKSE Menu Framework）

== harvest-nolvus 報告 (2026-09-26 18:39)（不加 --stock-game；試跑與 --apply 相同）==
[資訊] 模式：實際執行
[注意] 計畫中要從 nolvus 擷取的資料夾：2933 個：完成/已存在 2921，來源缺少 12（見 harvest-nolvus.csv）
[資訊] 共享資料量（硬連結不佔額外空間）：345.0 MB
總結：[注意]
（新連結 2 個：The New Gentleman - Nolvus Settings、The New Gentleman。來源缺少 12 個＝上次的 12 個：其中 6 個已從 D:\MV 補進 D:\PM，6 個是 decisions.csv 的 download）

== manifest 報告 (2026-09-26 18:40) ==
[資訊] 目標資料夾：4046 個
[資訊] 已就位：3564 個
[資訊] 需從 Nexus 下載：395 個
[資訊] 第五階段重建：9 個
[注意] 需換成 1.5.97 版 DLL：8 個
[注意] 尚無來源，需人工確認：54 個
[資訊] 捨棄：16 個
[資訊] 輸出：reports\manifest.csv、reports\downloads.html
總結：[注意]

== build_instance-create 報告 (2026-09-26 18:40 試跑／18:41 --apply，內容相同) ==
[資訊] 模式：實際執行
[通過] ModOrganizer.ini：寫入：遊戲路徑 D:\PM\STOCK GAME，工具 BethINI Pie, BodySlide, DynDOLOD, PGPatcher, SSEEdit, SSEEdit QuickAutoClean, TexGen, xLODGen
[通過] 設定檔 Pages-ZH：modlist 4125 行（捨棄 16），plugins 4233 個（排除 12 個自製插件）
[資訊] 佔位資料夾：553 個（之後用 MO2 安裝到同名資料夾並選 Replace）
[通過] 遊戲 ini：Skyrim.ini, SkyrimPrefs.ini, SkyrimCustom.ini
總結：[通過]

== build_instance-verify 報告 (2026-09-26 18:58)（MO2 第一次開啟並關閉之後）==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[注意] plugins.txt 與預期比對：缺少 973 個（mod 尚未安裝或已被修剪）；待重建輸出 8 個；例如：LegacyoftheDragonborn.esm, Water for ENB.esm, Vigilant.esm, Snazzy Interiors - Sarethi Farm.esp, Snazzy Black Briar Lodge.esp
總結：[注意]

== audit_skse 報告 (2026-09-26 18:58)（不加 --mv-1597-map；額外先跑一次供判讀）==
[資訊] 生效的 SKSE DLL：AE 專用（1.5.97 無法載入）=7, 多版本 NG（可用）=103, 非 SKSE 外掛（相依函式庫）=1, SE 版（可用）=67
[失敗] 需替換的 DLL：7 個：BakaWorldMapSpeed.dll（Flat World Map Framework2）, ClassicSprintingRedone.dll（Classic Sprinting Redone (SKSE64)）, CRDW.dll（Cached Recursive Directory Walk）, DynamicArmorVariants.dll（Dynamic Armor Variants）, FaceGenFixes.dll（Face Discoloration Fix）, FlatMapMarkersSSE.dll（Flat World Map Framework2）, NativeEditorIDFix.dll（Native EditorID Fix）
[通過] STOCK GAME 遊戲版本：1.5.97.0（需要 1.5.97.0）
[通過] SKSE 1.5.97：skse64_loader.exe + skse64_1_5_97.dll
[通過] Address Library（version-1-5-97-0.bin）：已找到
[通過] 遊戲根目錄的 ENB/ReShade 殘留：無（Community Shaders 可正常運作）
[資訊] 含 Root 資料夾的 mod（Root Builder 會部署到遊戲資料夾）：無
總結：[失敗]
```
- `pe.file_version` 修正有效：STOCK GAME 顯示 1.5.97.0。

## manifest 各 action 數量
keep 3564、download 395（有檔案編號 375、沒有 20）、regenerate 9、replace_dll 8、review 54、drop 16，合計 4046。

- regenerate：Pandora Output、dyndolodCS2、texgenCS、grass CS、lodgen2、pgpatcher_output、SYNTHESSIS、overwrite2、BodySlide (Nude)
- drop：CS shaders、CustomFixes1、CommunityShaders_AIO-2026-05-28T17-09Z、Vanilla CS rain TEXTURES、SC_HorseReplacer_SSE、SC_HorseReplacer、Grapple a1.7、anchor animation v2 Part、For Honor in Skyrim Black Prior、Curious Adventurer、[full_inu] Armor Pack 01 SSE、[SSE] H2135 Fantasy Series8、[Kirax] BDOR 2024 Female Collection、[TalesOfStar] Air Balloons、[Dint999] BDOR Hairs SSE 0.23、Lamas Tiny Hud - Edge version (SUKI)

## replace_dll（8 個；行號｜資料夾｜AE 專用 DLL｜目前 Nexus 編號）
- 24｜Flat World Map Framework2｜BakaWorldMapSpeed.dll; FlatMapMarkersSSE.dll｜29932/29932 1.85
- 3942｜Inventory Interface Information Injector｜InventoryInjector.dll｜85702/85702 1.1.0
- 3980｜Constructible Object Custom Keyword System｜CraftingCategories.dll｜81409/81409 1.0.1
- 4020｜Cached Recursive Directory Walk｜CRDW.dll｜186434/784136 1.1.4.0
- 4026｜Face Discoloration Fix｜FaceGenFixes.dll｜42441/319047 1.0.3.0
- 4037｜Dynamic Armor Variants｜DynamicArmorVariants.dll｜65963/65963 1.0.5
- 4101｜Native EditorID Fix｜NativeEditorIDFix.dll｜85260/488800 1.2.2.0
- 4103｜Classic Sprinting Redone (SKSE64)｜ClassicSprintingRedone.dll｜20166/474483 2.3.1.0
- 注意：`audit_skse`（看生效的 DLL）只列 6 個 mod；`InventoryInjector.dll` 與 `CraftingCategories.dll` 沒被列入，可能被後面的 mod 以 1.5.97 可用版本覆蓋。

## review（54 個；行號｜資料夾｜category）
```
   42 | NordwarUA Legions PBR | unknown
  118 | Edge UI Racemenu | nexus_other
  120 | Quest Journal Overhaul - Wide Screen | nexus_other
  125 | Seasonal Wigfrid's Erdtrees Replacer | unknown
  138 | RMS Lux patch | nexus_other
  141 | ErdtreeGildergreen - PBR 2.0 | unknown
  147 | Faultier's PBR Windows | unknown
  148 | Faultier's PBR Road Signs | unknown
  149 | Unslaad PBR | unknown
  155 | clockwork pbr | unknown
  158 | Children of the North Wind - PBR | nexus_other
  160 | Kvetchi Mercenary Set - PBR | nexus_other
  161 | Colovian Prince Set - PBR | nexus_other
  162 | Armors of the Velothi Pt. I - PBR | nexus_other
  163 | TMD The Rift Leaves PBR 2k | nexus_other
  164 | Flora Additions Waterplants PBR | nexus_other
  165 | A PBR Nirnroot - 2k | nexus_other
  168 | HDT-SMP Silver Armor PBR Patch | nexus_other
  178 | Tomato's Windhelm PBR - 2K | unknown
  179 | Tomato's Riften PBR - 2k | unknown
  194 | Faultier's PBR Skyrim AIO 2k | unknown
  198 | ERM - Textures pbr | unknown
  218 | 3D Whiterun Trellis pbr | nexus_other
  224 | Icy Windhelm - Windhelm Entrance Overhaul patch | nexus_other
  238 | Ashe 3 | nexus_other
  239 | JK's Fort Dawnguard - SDA Patch | nexus_other
  240 | SDA - Standing stones patch | nexus_other
  242 | SDA Patch Hub SE | unknown
  268 | Immersive Magic Brooms Legacy of the Dragonborn Patch (Optional) | nexus_other
  276 | ParticleWind NG 3.5 | unknown
  280 | Wayshrines - JK's Skyhaven patch | unknown
  428 | horseAnimations2 | nexus_other
  515 | Immersive Dialogue Expansion - Stormcloaks | nexus_other
  518 | IDE Jorrvaskr | unknown
  590 | Dismembering Framework - Wolves of Skyrim | unknown
  591 | Dismembering Framework - 4thUnknown Trolls | nexus_other
 1099 | Smooth Special Idle | unknown
 1296 | Skurkbro's Retexture Project - Dwemer Pipe Patch | unknown
 1523 | Wolves of Skyrim - Wolf Pelts | nexus_other
 1908 | Breton Field Knight Armor Set - with PBR 2K | nexus_other
 1909 | Breton Field Knight Armor Set - with PBR | nexus_other
 2746 | Caliente's Beautiful Bodies Enhancer - 3BA NORMALMAPS | unknown
 2812 | Ulvenwald Series - Erdtrees of Skyrim | nexus_other
 3017 | Landscape Fixes For Grass Mods - Great Cities patch | nexus_other
 3128 | Mahrlek1´s trees compilation - Whiterun Trees module | unknown
 3141 | Ryn's Whiterun City Limits - Patch Collection | nexus_other
 3209 | Ivy Stendarr Beacon Overhaul | nexus_other
 3271 | FuzzBeed's Giant Camps AIO - USSEP patch | unknown
 3272 | FuzzBeed's Giant Camps AIO - Mihail Giant Club Variety | unknown
 3273 | FuzzBeed's Giant Camps AIO - LFFGM patch | unknown
 3274 | FuzzBeed's Giant Camps - Flora Aloe and Agave | unknown
 3285 | Yet another patch hub for Ryn's Skyrim2 | unknown
 3350 | Yggdrasil - Floating Tree Redux | nexus_other
 3677 | Vigilant - English Voices Addon 1.8 esp | unknown
```
（note 都是「no Nexus ID yet - identify manually and add to data/decisions.csv」。分類：unknown 26、nexus_other 28）

## MO2 第一次開啟時遇到的問題（已處理，請確認）
1. **OpenSSL 載入錯誤**：`D:\PM\ModOrganizer.exe`（M&V 的 MO2 2.5.2）啟動時跳出系統錯誤「無法找到程序輸入點 OSSL_LIB_CTX_get_data（在 `…\miniconda3\Library\bin\libssl-3-x64.DLL`）」。MO2 自己的 `libssl-3-x64.dll`（3.3.0）只在 `D:\PM\dlls\`，根目錄只有 `libcrypto-3-x64.dll`；載入時 Windows 先在 PATH 找到 miniconda 的 libssl 3.5.5（miniconda 在使用者 PATH；本機工作階段的 PATH 另有 Git mingw64 的 3.5.4，也會中）。使用者同意後，把 `D:\PM\dlls\libssl-3-x64.dll` **複製一份到 `D:\PM\libssl-3-x64.dll`**（新檔案、不是硬連結、不改任何原檔）。之後即使 PATH 有 miniconda／Git，MO2 也從 `D:\PM` 載入自己的 libssl，正常開啟。建議把這步加進 `build_instance create` 或手冊。
2. **crashlogtools 外掛錯誤**：MO2 啟動後跳出 Error：`UnicodeDecodeError: 'cp950' codec can't decode byte 0x94 …`（`D:\PM\plugins\crashlogtools\crashlogutil.py(128) read_file ← crashloglabeler.py(88) onUserInterfaceInitializedCallback`）。這是 MO2 的 Python 外掛用系統編碼 cp950 讀取「文件」裡舊的 crash log。按 OK 後 MO2 正常運作，但之後每次開啟應該都會跳。要停用這個外掛，還是有其他做法？
3. 首次提示「Category Migration」選 Close（不改分類）。Nexus 尚未連結（Connect to Nexus 需使用者在瀏覽器授權），下載前會請使用者做。

## 其他
- 已推送 `data/snapshots/nolvus-6.0.20-installed/`：`modlist.txt`（3762 行）、`plugins.txt`（3687 行）、`loadorder.txt`（3766 行），與 Nolvus Profile 的檔案雜湊相同，內容只有 mod／插件名稱（檢查過沒有路徑、使用者名稱）。Git 在倉庫內會以 LF 儲存換行。
- `NEXUS_API_KEY`、`ANTHROPIC_API_KEY` 目前都還沒設定。下載會先用 `downloads.html`＋MO2（需使用者先在 MO2 連結 Nexus），或等使用者設好金鑰後用 `nexus_fetch.py`。
- D 槽剩約 458 GB。

## 需要雲端決定的事
1. review 54 個的來源（寫進 `data/decisions.csv`）。
2. replace_dll 8 個的 1.5.97 替代版本（含 audit_skse 沒列的 2 個是否還要換）。
3. MO2 的 libssl 修正是否要納入工具／手冊；crashlogtools 外掛的處理方式。
