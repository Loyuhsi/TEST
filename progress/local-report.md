# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：4 組合清單（中途回報 3：FOMOD 全部裝完）
- 日期：2026-09-27
- 結論：
  - Nexus 批次下載完成 449/450；`install_archives.py` 自動安裝約 350 個沒有 FOMOD 的壓縮檔。
  - **FOMOD 83 個全部裝完**（這輪補完 17 個，選擇見附錄最後 17 列；每個都核對過產生的插件）。
  - 新增 `build_instance.py sync-order --restore-states`（c8fc131）：MO2 會把新裝的插件列為停用，235 個目標插件（含 LegacyoftheDragonborn.esm）因此是停用狀態；不先還原，`prune_dependents` 會誤刪大量補丁。已用它把目標插件狀態還原（目前 3575 個目標插件已啟用）。
  - **新發現、需要雲端決定：目標有 622 個插件在硬碟上找不到檔案**（不含第 5 階段才產生的 7 個）。絕大多數屬於從 M&V／Nolvus 擷取來的補丁合集：Pages 在這些合集的 FOMOD 勾了更多補丁，擷取來的版本沒有。見「需要雲端決定」第 8 點。
  - 之前的 10 個下載檔、Maerchenwald、合併安裝 3 個仍等雲端回覆；Edge UI Racemenu（DIP）尚未處理。
  - 還沒跑 `prune_dependents`：缺的 622 個插件決定前跑會停用大量補丁。

## 工具結果（照抄 reports\*.txt 的每一行）
本輪（FOMOD 全部裝完、MO2 關閉後）：
```
== build_instance-sync-order 報告 (2026-09-27 00:30) ==
[資訊] 模式：實際執行
[通過] 啟用狀態：依目標啟用 29 個、停用 0 個；檔案不在已啟用的 mod 或遊戲資料夾裡，略過 629 個（之後要再跑 prune_dependents）
[通過] 插件順序：3914 個：依目標順序 3604，新增的 310 個放在輸出插件之前
[資訊] 不在目標清單中的插件：（310 個，都是停用狀態，多半是合集裡目標沒勾的補丁，例如 41 個 DBVO Fix）
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-003058
總結：[通過]

== build_instance-verify 報告 (2026-09-27 00:30) ==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[注意] plugins.txt 與預期比對：缺少 622 個（mod 尚未安裝或已被修剪）；待重建輸出 7 個；例如：Lux Orbis - Master plugin.esm, Whiterun Has Walls - Navmeshed.esm, Lux Via - DK Nord Ships patch.esp, Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, HLIORemi - Dwemer Backpack by Xtudo.esp
總結：[注意]
```
- `--restore-states` 這輪共跑了 5 次（每次先關 MO2）：依序啟用 235、6、69、13、29 個。第一次之前 MO2 裡停用的包括 LegacyoftheDragonborn.esm、Vigilant.esm、Grand Solitude 主檔等。
- `verify` 的「缺少 622 個」＝目標插件在硬碟上找不到檔案（`_expected` 共 4233 個）。分析見「需要雲端決定」第 8 點。

前一輪：
```
== nexus_fetch 報告 (2026-09-26 19:43) ==
[通過] 本次下載：429 個
總結：[通過]
（nexus_fetch.csv：downloaded 429、already_downloaded 20、http_404 1＝The Restless Dead - At Your Own Pace Patch）

== install_archives 報告 (2026-09-26 21:08)（第 4 次 --apply；前 3 次為 20:27 --limit 3、20:36、20:43）==
[資訊] 執行：判斷了 448 個下載
[資訊] 磁碟空間：預計解壓 12.0 GB，D:\ 剩 321.3 GB
[通過] 已安裝：84 個
[通過] 已重裝（舊資料夾在 _replaced）：4 個
[資訊] FOMOD，要用 MO2 安裝：68 個
[注意] 需要人工判斷（見 install_archives.csv 的 reason 欄）：29 個
[資訊] 先前已安裝：263 個
[資訊] manifest 目標還沒有下載檔：1 個
總結：[注意]
```
- 4 次合計自動安裝 3＋212＋34＋84＝333 個，再加 replace_dll 4 個（CRDW、Face Discoloration Fix、Native EditorID Fix、Classic Sprinting Redone）。
  - 舊資料夾都搬到 `D:\PM\_replaced\`，沒有刪除。新的 DLL 分別是 CRDW.dll、FaceGenFixes.dll、NativeEditorIDFix.dll、ClassicSprinting.dll。
- 「人工判斷 29」扣除已經用 GUI 裝好的 FOMOD 之後，還剩下面「需要雲端決定」的 10 個，以及合併安裝、Maerchenwald、DIP。
- D 槽剩 290 GB。

## 新工具與修正（本地提交，尚未推送）
- `build_instance.py sync-order --restore-states`（c8fc131，本輪新增）：
  - 問題：MO2 會把新裝的插件列為停用；第一次開 MO2 時不存在的插件還會從 `plugins.txt` 移除。所以 `create` 之後才安裝的 mod，插件全是停用。`prune_dependents` 只看啟用中的插件，直接跑會把依賴它們的補丁全判成缺前置。
  - 做法：依 `_expected\plugins.txt`，把「目標有啟用、而且已啟用的 mod 或遊戲 Data 裡有檔案」的插件設成目標的狀態（啟用或停用）；檔案不在的略過；沒有 `_expected` 時拒絕執行（原始目標清單含有已捨棄 mod 的插件）。報告列出啟用、停用、略過的數量。
  - 它會把已被修剪的插件重新啟用，所以一定要在 `prune_dependents` 之前跑；docs/04 第 8 節與技能的指令已補上。
  - 也用在安裝補丁合集的 FOMOD 之前：MO2 的自動偵測看的是插件啟用狀態，插件停用時選項會變灰（Ancient Land、Vampira 的 Ashe 選項就是這樣）。
  - TDD：先寫 `tests/test_sync_states.py`（8 項），code-reviewer 審過（無 CRITICAL／HIGH；依建議補上遊戲 Data 的插件、缺 `_expected` 時拒絕、改名大小寫與有停用時標 WARN）。
- `nexus_fetch.py`：
  - 3a635ea、60ba5b7：CDN 網址的檔名含空格、`#`、`?`、`%` 時要編碼，同時保留簽章 query。
  - CDN 回 403 時只把該檔記為 `cdn_http_403`，不再誤判成「金鑰無效」而中止整批下載。
  - 錯誤訊息會去掉 query，因為 query 裡有 user_id。
  - 5a158a4：`.meta` 的換行原本寫成 `\r\r\n`（text mode），改成 `newline=""`。
- `tools/install_archives.py` 和 `pm/layout.py`、`pm/sevenzip.py`、`pm/swap.py`，`mo2.py` 另加 `install_meta_text`／`mark_download_installed`（a01fdfe、271074c、9ee798a）。
  - 流程：
    1. 用 `.meta` 的 modID／fileID 對應到 manifest 的資料夾。
    2. 找資料根目錄：包括外層資料夾和 `Data` 資料夾；會用 provenance 的預期插件和目標 `plugins.txt` 檢查。
    3. 用 7-Zip 解壓到 `D:\PM\_install_staging`，再把資料根目錄整個改名放進空的佔位資料夾。
    4. 寫 MO2 的 `meta.ini`，並把下載的 `.meta` 標成 `installed=true`。
  - 交給人工的情況：FOMOD、結構不明確、插件和目標不符、note 寫 FOMOD／合併／DIP。
  - `--accept 資料夾`：人工看過壓縮檔後可放行「不認得的資料夾或檔案、預期插件不符、插件不在目標」這幾種疑慮。
  - 預設是試跑；`--apply` 時如果 MO2 還開著就拒絕執行。
  - 兩輪 code-reviewer，HIGH 都已修正：
    - 佔位資料夾中途被中斷會消失 → 改成先搬到旁邊再換上，並寫中斷紀錄，下次執行時自動還原。
    - Explorer 產生的 `desktop.ini` 讓 rmdir 失敗 → 視為空資料夾。
    - 還原時如果暫放的資料夾不見，會重建空資料夾，並用另一句訊息明確回報（`_replaced` 的內容不見時回報 FAIL）。
  - 另外修了幾個 MEDIUM：資料夾名稱比對不分大小寫、Windows 保留名稱、QSettings 值開頭是 `@` 時加引號、7-Zip 的長路徑。
  - 測試：PowerShell 下 127 項全過（加上下面的 restore-states 後為 135 項全過、1 項略過）。
- 這些 `tools/`、`tests/` 的提交是否一起推送，要等使用者決定，因為平常只推 progress／data。

### `--accept` 放行清單（逐一看過壓縮檔）
- provenance 的插件欄有誤：
  - RMS Lux patch（壓縮檔只有材質，provenance 卻列 SDA - UnLux.esp）
  - YXZ …-PBR（YXZ_NRoad PBR DGS.esp 其實在 CORE 資料夾）
- 目標裡沒有、裝進去 MO2 會列為停用的插件：
  - Icy Windhelm - Windhelm Entrance Overhaul patch（note 也寫在目標是停用）
  - Dova Jump（DovaJumpMCM.esp）
  - Elden Rim - Base 3.72（RimImpactOfMob／OfPlayer）
  - Follower Dialogue Expansion - Aela（Vanilla Combat Block）
  - FuzzBeed's … Mihail Giant Club Variety
  - Grand Solitude - Landscape override
  - Orc Stronghold AIO - SkyShards Patch
  - Saviik's Solitude Overhaul（目標只載入 Grand Solitude x Saviik's Solitude 補丁）
- mod 自帶的資料夾或檔案：
  - Dragonborn ReVoiced2（DBReV）
  - Prisma UI（PrismaUI）
  - Pandora Behaviour Engine（exe；FNIS.esp 在目標裡）
  - DK's Realistic Nord Ships（.bsl）
  - SkyPlace（Data 根目錄的 json）
  - Breton Field Knight … PBR 2K（2K 材質；esp 在另一個資料夾）
- 已知資料夾清單另外加入：`DragonbornVoiceOver`、`Seasons`、`HeadPartWhitelist`、`BashTags`。
- 已確認 MO2 會把不在 `plugins.txt` 的新插件列為停用（目前 `plugins.txt` 有 257 行沒有 `*`）。

## 需要雲端決定的事
1. **下載的檔案和目標不符**：壓縮檔都還在 downloads，尚未安裝，佔位資料夾維持空的。

   | 資料夾（mod） | 目前的檔案 | 目標 | 建議 |
   |---|---|---|---|
   | Dreadful Alduin（136437） | 578734 Dreadful Alduin 8K v1.4（Dreadful Alduin.esp） | Dreadful Alduin Graphics Only.esp | 578735 Graphics Only 8K v1.4（OLD_VERSION），或 578737 Graphics Only 4K v1.4（ARCHIVED） |
   | RUSTIC SOULGEMS - Special Edition（5785） | 12944 1K Sorted | RUSTIC SOULGEMS - Unsorted.esp | 12943 1K Unsorted（或 12945 2K Unsorted） |
   | Thrones Expanded（139544） | 587744（ThronesExpanded.esp） | ThronesExpandedBOS.esp | 586268 Base Object Swapper v1.2（OPTIONAL） |
   | HFs - Whiterun bridges REDONE（158471） | 664921 (ESP) 4K（HFs_WhiterunBridges_REDONE.esp） | 目標沒有這個插件 | 沒有 ESP 的版本：662497（4K）或 662495（2K） |
   | Blubbo Trees Variations（119870） | 503101（Blubbo_Trees_Variations_Nexus.esp） | …_Nexus_noVanillaTrees.esp | 503110 noVanillaTrees（MAIN v0.9） |
   | Mostly Treeless Tundra - Northern Scenery Tundra（133515） | 560322（「Mostly Treeless Tundra - Northen Scenery.esp」） | Mostly Treeless Tundra - Northern Scenery - Whiterun Tundra Patch.esp | 這個 mod 頁面找不到同名檔案，可能出自別的頁面 |
   | Myrwatch - TnE - MyrwatchVaultFix - USCCCP Patch（97659） | 479879（「Myrwatch - TnE -  MyrwatchVaultFix - USCCCP Patch.esp」，中間兩個空格） | MyrwatchVaultFix - USCCCP Patch.esp | 這個頁面只有這一個；目標插件可能出自 MyrwatchVaultFix 自己的頁面 |
   | Orc Strongholds - AIO - EFPS Patch（89354，EFPS 頁面） | 627968（Orc Strongholds - Largashbur - EFPS Patch.esp） | Orc Strongholds - All In One - EFPS Patch.esp | 可能在 Orc Strongholds AIO 頁面的選用檔 |
   | Nature of the Wild Lands - Animations Addon（148132） | 715711 MESHES（沒有插件） | Nature of the Wild Lands - Animation Plugin.esp | 合併安裝 669507「NotW Animation - PLUGINS (FOMOD)」v1.03；FOMOD 要選一般／Less Sway／Even Less Sway 哪一個 |
   | The Restless Dead - At Your Own Pace Patch（94100） | manifest 的檔案編號是 94100（等於 mod 編號，id_source=inventory）→ HTTP 404 | 版本 1.2.6.1 | 624013「Patch - At Your Own Pace - Main Quest」v1.2.6.1（OPTIONAL） |

2. **Yggdrasil - Floating Tree Redux**：note 寫「FOMOD 選 Floating Tree」，但目標插件是 `Yggdrasil Trees.esp`，只有 Redux 的「Yggdrasil Trees (both)」會產生。選 Floating Tree 會產生目標沒有的 `Yggdrasil - Floating.esp`。我照目標插件選了 both，請確認。
3. **Maerchenwald**：`Maerchenwald - The Archwood Lite - Giant Fantasy Trees` 和 `Maerchenwald - Archwood Lite - Giant Fantasy Trees` 在目標 modlist 相鄰（3418／3419），對應同一個檔案（150187／628849）。兩個都裝同一份，還是捨棄一個？
4. **合併安裝的第二個檔**：Fortified Morthal 707429、Modern Hay 652905、Dwemer Researcher Backpack 723624 不在 manifest，所以 `nexus_fetch` 不會下載。要改 decisions 讓工具下載，還是由我手動下載？
5. **請確認幾個 FOMOD 選擇**（完整表格在附錄）：
   - BnP female small update 選了「I use no frostnip CBBE skin」（預設）；目標皮膚是不是 no frostnip 版不確定。
   - Lux CS Patch 另勾了 LightPlacer addon。
   - Vigilant 和 Unslaad 都選英文加 Silent Voice。
   - Bladedancer's Edge 用 ESL 旗標版。
   - 為了筆電改選的：CVEO 512p、High Quality PBR Ivy 2k、Wolves of Skyrim 2k、Texture Downscaler BALANCED。
   - Lore-Friendly Load Screen Compendium 是 21:9 版（約 7 GB），筆電螢幕是 16:10。
6. **MO2 外掛**：
   - Crash Log Labeler 雖然已在設定裡停用，每次開 MO2 仍會跳出 cp950 錯誤；`ModOrganizer.ini` 的 [Plugins] 看不到它的 `enabled=false`。
   - M&V 的 MO2 有 `PageFile Manager\autostart=true`（pagefile_size=20480）。這個外掛可能會去改 Windows 分頁檔，屬於系統設定，要停用嗎？
7. **guard.py**：在 Git Bash 下 cp950 輸出會讓 `test_guard_hook` 12 項失敗（guard 本身的判斷正確），建議改成 UTF-8／ASCII 輸出。
8. **目標有 622 個插件在硬碟上找不到檔案**（`_expected` 4233 個中；不含第 5 階段產生的 7 個）。完整清單在 `data/analysis/missing_target_plugins.csv`（只有插件名稱）。欄位：
   - `target_order`、`plugin`、`prefix`（檔名 ` - ` 之前的字）；
   - `candidate_folders`：目標 modlist 裡名稱相近的合集資料夾與它的 manifest action；
   - `in_downloaded_archive`：D:\PM\downloads 裡含有它的壓縮檔；
   - `in_mv_loadorder`、`in_nolvus_plugins`：來源清單快照有沒有它；
   - `in_mv_install`、`in_nolvus_install`：D:\MV、D:\Nolvus 實際安裝裡哪個資料夾有這個檔案。
   - 結論：幾乎都是**補丁合集的 FOMOD 選項不同**。Pages 在這些合集勾的補丁比我們擷取來的那一份多。
     - **264 個在來源安裝裡就有**，只是我們擷取了另一邊（或選項較少的那一份）。最多的是：
       - Nolvus「JK's Interiors Patch Collection」79 個、「JKs Guild HQ Interiors Patch Collection」54 個；
       - M&V「Lux (patch hub)」18、「Lux Orbis (patch hub)」16、「Lux Orbis」5；
       - Nolvus「Northern Roads Patch Collection」14、「The Great City of Winterhold Patch Collection」10、「JS Dragon Claws AE」7、「JK's Solitude Outskirts - Patch Collection」6；
       - M&V「Skyrim Landscape and Water Fixes」6、「Psychopatchist Purgatory」5。
       - 例子：`Lux Orbis - Master plugin.esm`、`Lux Orbis.esp` 在 M&V 的「Lux Orbis」資料夾，但目標 modlist 沒有同名資料夾；目標的「Lux Orbis cs」對應到 Lux CS（153919），裡面沒有這兩個檔。
     - **78 個只在已下載的壓縮檔裡**：
       - JK's Guild HQ Interiors Patch Collection 70 個（和上面 Nolvus 那份重疊）；
       - Tiny Patch Hub 6 個；
       - Dwemer Researcher Backpack（合併安裝的第二檔）、Maerchenwald 各 1。
     - **約 340 個在哪裡都找不到**，要下載該合集再依目標插件重裝 FOMOD。最多的是：
       - Snazzy Interiors（72，目標資料夾「Snazzy Interiors Patch Collection2」為 keep）；
       - COTN Dawnstar（22）、COTN Falkreath（18）、COTN Winterhold（11）；
       - LOTD 的 DBM_*（20，「Madmen - DBM Patch」？）；
       - Nightgate Inn Revived（10）、Occ_*（7）、Orc Exiles（7）、JKs Raven Rock（7）、JKs Blue Palace（11）等。
   - 請雲端決定處理方式：
     - (a) 對「來源安裝就有」的資料夾改從另一邊補擷取，或把兩邊合併；
     - (b) 其餘合集用 `nexus_fetch` 下載，我用 MO2 依目標插件重裝（Replace）；
     - (c) 接受缺漏，交給 `prune_dependents` 停用依賴它們的補丁。
   - 在決定之前我**不會**跑 `prune_dependents`：它會把依賴這些缺漏插件的補丁全部停用。
9. **本輪的其他處理，請確認**：
   - **Snazzy Misc Locations AIO**：FOMOD 作者把 JK's Palace of the Kings 的目的檔名寫成 `….esp.esp`，所以上輪摘要判定成「不在目標」而沒勾。目標其實有 `Snazzy Interiors - JKs Palace of the Kings.esp`（還有 10 多個它的補丁）。已用 FOMOD 加勾重裝，並把檔名改回 `.esp`。
   - **Riverwood Falls**：目標的 `Riverwood Falls - Landscape Fixes for Grass Mods.esp` 在壓縮檔的 Patches 資料夾，但 FOMOD 沒有任何選項會裝它，已直接從壓縮檔放入。
   - **SDA - Standing stones patch**：FOMOD 第一步會強制裝 SES 主檔，而主檔已由擷取的資料夾提供，所以改用 MO2 Manual 安裝，只放 SDA 補丁。
   - **Wayshrines - JK's Skyhaven patch**：Tiny Patch Hub 有 389 個根目錄項目，只需其中 1 個 esp。已關閉 MO2 後用 7-Zip 取出，並用 `mo2.install_meta_text` 寫 meta.ini。
   - **Flat World Map Framework2（replace_dll）**：逐檔比對 M&V 版還原它的所有選項，結果除 Flat Map Markers 換成 SE 版 DLL 外完全相同。「World Map Panning Speed」只有一個選項、無法不選，會裝 AE 版 BakaWorldMapSpeed.dll；依 decisions 放棄，已改名成 `.mohidden`。M&V 舊內容搬到 `D:\PM\_replaced\` 保留。
   - **DBVO Vampira**：語音包註冊必需的「Skyrim Base Game」選項會附帶 41 個 `DBVO Fix - *.esp`，目標都沒有（目標另外的語音包也都不含插件）。它們維持停用。
   - **為了筆電選的**：Water for ENB 貼圖和瀑布 2K（預設 4K）；CS Lights 不裝窗戶光源（室內是選用，Lux 已處理；室外作者不建議）。
   - **JK's Fort Dawnguard - SDA Patch**：照資料夾名稱只放 SDA 補丁。目標另外要的 Cloaks、Arsenal、RDO、WACCF 4 個屬於第 8 點的合集問題。
   - **MO2 當機一次**：00:08 在 Manual 安裝完成後、檢查更新時，ntdll 0xc0000374。安裝內容完整；重開後 `verify` 的 modlist 比對一致。

## 尚未完成（下一步）
- 等雲端回覆：第 1 點的 10 個下載檔、Maerchenwald、合併安裝 3 個、第 8 點的 622 個缺漏插件。
- Edge UI Racemenu（DIP）：Dynamic Interface Patcher v2.1.5（96891，約 63 MB）可以當 MO2 工具執行，輸出會到 overwrite。下一步先試做；做不到再回報。
- 全部處理完後：`sync-order --restore-states --apply` → `prune_dependents` → `sync-order` → `verify` → `check_plugins` → `audit_skse`。

## MO2 GUI 操作的注意事項（給手冊）
- MO2 2.5.2 的 Downloads 分頁在篩選狀態下，右鍵選單會對到錯的列。這次跳出的是 LOTD PBR Odds and Ends 的 Quick Install，已取消。改用 File → Install Mod 輸入完整路徑。
- 大型壓縮檔解壓時，對話框有 Cancel 按鈕；這時按 Enter 會中斷安裝。Load Screen Compendium 第一次因此少了 esp，已重裝並確認完整。
- 在 MO2 裡已確認：新插件預設是停用；FOMOD 的 1.5.97 DLL 選項（Light Placer、BOS、PhotoMode、po3 Tweaks、Splashes、SLACK）MO2 都會依遊戲版本自動選。
- FOMOD 的自動偵測看的是插件「啟用」狀態：剛裝的插件在 MO2 裡是停用，依賴它的選項會變灰。補丁合集要先關 MO2 跑 `sync-order --restore-states --apply` 再裝。
- 自動偵測常會勾到「目標有這個 mod、但 Pages 沒用它的補丁」的選項（例如 Grand Solitude 的 JK's Bards College、Remiel，Water for ENB 的 Wyrmstooth／Falskaar／Bruma），要逐項對照目標 `plugins.txt` 取消。
- 安裝對話框的 Name 欄會自動完成（例如打「DBVO Vampira」自動補成「DBVO Vampira FOMOD」），打完要按 Delete 清掉反白的補字。
- 對話框第一次點選項有時只會取得焦點、沒有勾到；每頁按 Next 前都要放大確認。

## 附錄：FOMOD 選擇與產生的插件（已核對：產生的插件都在目標裡，例外見表內說明）
| 資料夾 | 選項 | 產生的插件 |
|---|---|---|
| Light Placer | SSE v1.5.97（MO2 依遊戲版本自動選） | 無插件；po3_LightPlacer.dll 大小與壓縮檔 SE 版相同 |
| Lux Orbis cs | No Effect 11；Lux Orbis Tweaks；Templates = Bright | Lux - HDR、Lux CS - Bulbs、Lux CS Templates - Bright、Lux Orbis CS（4 個預期插件全符） |
| Lux CS Patch | Tonemapping addon＋LightPlacer addon（說明：以 Light Placer 補回 CS 不支援的 Lux 粒子光源，需 ISL） | Lux - HDR |
| Lux (cs) | 選用效果全不勾；rugs/pelts/tables=None；Embers XD 只勾自動選的 BYOH fireplace；optimized meshes=Vanilla 與其後各群組預設；Improved Dwemer Glass meshes 勾（目標有 IDG）；SMIM／CC meshes 預設；Tomato Whiterun window models 勾（目標有 Tomato's Whiterun Remake），Mrf 不勾；Fixes：No Grass In Caves＋SLaWF，MEZF 不勾；USSEP pre update（目標 USSEP 4.2.9a）；Brighter Interior Cells Nights；templates 全 None | Lux、Lux - Master plugin.esm、Brighter interior nights、No grass in caves、SLaWF、USSEP patch（全在目標；provenance 只列 2 個，不完整） |
| NAT.CS III | NAT.CS；Mist mesh、Vanilla Sky Statics 不勾（Sky Statics 插件不在目標） | NAT-CS |
| YXZ …-PBR CORE | 確認已裝基礎包；DGS PBR | YXZ_NRoad PBR DGS |
| Realistic PBR Footprints | PBR footprints＋Sand Patch；Ultimate Fix 不勾 | Footprints - PBR Patch、SandPatch PBR Patch |
| Skeleton Replacer HD 2K SE | ESL；SkeletonsWithEyeGlow（保留原版眼窩發光）；SoulcairnSkeletons AE（作者的動態特效）；BeastSkeletons、M'Rissi 不勾（目標沒有這兩個 mod） | PraedysSkeletons.esl |
| Serana Re-Imagined | Vampire version CBBE（預設） | Serana Re-Imagined |
| Hood Plus Hair for Serana Re-Imagined | No Hair Physics + Re-Imagined Vamp Paleness（預設，與上一個一致） | Serana Re-Imagined（覆蓋同名插件） |
| Serana Re-Imagined - Eyes Re-Visited | 全預設：非 VR、黑髮、紅眼、Full glow | 無 |
| Immersive Flying Books | Arcaneum＋JK's Arcadia's Cauldron、COTN Dawnstar、JK's Blue Palace、JK's Elgrims Elixirs、JK's The Hag's Cure、LOTD（LOTD 本體尚未安裝，手動勾）；JKEEK Arcadia、JK's Dragonsreach 不勾 | 8 個，全符預期 |
| Improved Follower Dialogue - Lydia | Core＋Wyrmstooth＋LOTD；Bruma、停用 AA 不勾；外觀補丁 None | ImprovedCompanionsBoogaloo、LydiaPatchForLOTD、LydiaPatchForWyrmstooth |
| 3D Whiterun Trellis pbr | Metal（預設）；Shader = PBR（note） | 無 |
| Ancient City of Markarth | Required＋Lighting = Lux Orbis；Anti-Moss、Add-on 不選 | ACoM、ACoM Lux Orbis Patch |
| Ancient City of Markarth no Worldspace edits | 只有 Required | Ancient City of Markarth.esp（與上一個同名） |
| Ashe - A Visual Replacer2 | 全預設（作者推薦）：Alternative hair、Blue eyes、不加妝 | Ashe - Visual Replacer |
| [Dint999] Secret Child Of Talos | MAIN；Heels Sound = Yes（預設） | [Dint999] SecretChildOfTalos |
| Base Object Swapper 3.41 | SSE v1.5.97（自動選） | 無 |
| BiR's Remiel Replacer | High Poly Head（預設，不需另一個 mod）；Custom Skin - CBBE；Extras 不勾（2K 眼睛只為特寫；Glasses 插件不在目標） | HLIORemi-Replacer-Belladonna |
| Bladedancer's Edge | 3BA；外觀全預設；esp = default esl flagged（作者推 default；ESL 版省一個完整插件名額，目標沒有以它為前置的補丁） | BDE_Armor（ESL 旗標） |
| Bow Rapid Combo V3 | 不勾任何選項（Archer Dodge 可能與目標的 Dynamic Dodge Shot 重複；Spaghetti Western 是槍械 mod，目標沒有） | BowRapidCombo |
| BnP female small update | I use no frostnip CBBE skin（預設；不確定目標皮膚是否為 no frostnip 版，請確認） | 無 |
| Breezehome Exterior Overgrown | HS Breezehome（MO2 依已裝插件自動選） | Breezehome - Exterior Overgrown |
| Asura's Guard | 3BA 2K 檔；各步驟預設（Heavy、Heels Sound No、Never Nude No、材質 Default）；GND = Box Normal（效能好、非 NSFW；第一次操作時 MO2 預選 Box Figure [NSFW]，已取消重裝） | Asuras Guard [Armor] |
| Complete Vanilla Eye Overhaul (CVEO) by LDD | Core；各解析度 512p（作者說 512p 最適合遊玩，1024p 以上給特寫／截圖）；AO 1x；Carancula UV Original | CompleteVanillaEyeOverhaul_CVEObyLDD |
| Caliente's Beautiful Bodies Enhancer - 3BA NORMALMAPS | Normalmap = Fat（預設） | 無 |
| Daughter of Coldharbour - Reimplemented | Main；MCO（目標用 MCO）；NPC = Serana（預設） | DaughterOfColdharbourReimplemented |
| EVG Animation Variance | Recommended（安裝全部） | 無 |
| ERM - Textures pbr | Let's Start；Shader = PBR（note）；Mountain = Default | 無 |
| Fancy Morthal Swamp Overhaul | Continue；外觀預設（Original swampy color、Slick）；Patches 只勾 Nature of the Wild Lands | Fancy Morthal Swamp Overhaul、Fancy Swamp NotWL Patch |
| Faster HDT-SMP 4.01 | 1.5.97（自動）；NOT CUDA（推薦）；AVX（推薦，預設是 No AVX）；No MCM - Extreme performance（推薦）。先裝的 FSMPM MCM 版會多出目標沒有的 FSMPM esp，已重裝 | 無 |
| Grand Solitude - The Walls of High King Erling | Main＋Parallax meshes（必裝）；SMIM Rotor 勾（目標有 SMIM）；Majestic Mountains 不勾（目標沒有）；LOD = 窗戶隨日夜變化（推薦） | Grand Solitude - The Walls of High King Erling |
| Helmet Toggle 2 NEW2 | Core；DAV/FLM/KID/SPID（預設）；MCM Helper、Dragon Masks - SkyPatcher、Guards Pose with Helmets、Immersive Equipping Animations、Apophysis（目標都有對應 mod）；Immersive Speechcraft 不勾 | Helmet Toggle 2 |
| Hogwarts in Skyrim | IED Condition（推薦）；Dodge Shout 不勾 | Dovapotter |
| Immersive Weapon Switch | I4 = No, Thanks（I4 選項會產生目標沒有的 ImmersiveWeaponSwitch.esp） | 無 |
| Ivy - Riverwood Small Addon | Main；No Trees；JK's 補丁不選；Lux = Lux Orbis - Northern Vanilla Farmhouses；Statue of Mara 不選 | Riverwood Addon Standalone、Without Trees Patch、Northern Vanilla Farmhouses - Lux Orbis |
| Guards Pose with Weapons | Required＋5 種武器（單手盾、矛盾、雙手、長柄、弓）；Helmet 不勾（改用 Helmet Toggle 的 Guards Pose with Helmets） | 無 |
| Ivy Stendarr Beacon Overhaul | Main；Patches 只勾 Lux Orbis（note；自動勾的 3DNPC 補丁不在目標，已取消）；Frescoes = None | Ivy Stendarrs Beacon Overhaul、Lux Orbis Patch |
| Landscape Fixes For Grass Mods - Great Cities patch | 只勾 Mixwater Mill、Karthwasten（目標只有這兩個） | 2 個補丁 |
| Lod Model Library for DynDOLOD | Required；Saints and Seducers（SEC）不勾（目標沒有） | 無 |
| Lore-Friendly Load Screen Compendium (21-9) (4K) | 1.6.640 and earlier（依說明這是給舊版執行檔的超寬螢幕處理，本機 1.5.97；走這條分支實際是 21:9 2K 版）；All-Inclusive；Creation Club 版插件。注意：筆電螢幕是 16:10，這是 21:9 版，約 7 GB；第一次安裝被中斷（沒有 esp），已重裝確認完整 | LoadScreenCompendium |
| M.O.I.S.T. | BOS 版（note）；Without Random Swaps（推薦）；No Seasons Support（Seasons 插件不在目標） | Massive Outstandingly Insane Swamp Tree |
| Mahrlek1´s trees compilation - Whiterun Trees module | Vanilla（目標沒有 Fortified/Capital Whiterun、JK's Skyrim、DoS 本體、Spaghetti's Whiterun）；Breezehome universal patch（note） | Whiterun trees、Breezehome universal patch |
| Modern First Person Animation Overhaul | all weapon＋Daedric bow fix | 無 |
| PC Head Tracking and Voice Type SE | Main＋Patch | PC Head Tracking - MCM、PC Head Tracking - Patch |
| PhotoMode | SSE v1.5.97（自動） | PhotoMode |
| Powerofthree's Tweaks 1.15.1 | SSE v1.5.97（自動） | 無 |
| Phantom Horse | +70（推薦）；Shadowmere Rework 不勾 | Phantom Horse |
| RaySense - Jumping over obstacles2 | Hybrid（推薦） | 無 |
| Petroglyphs of Skyrim | Required；Mountain = ERM - Default（說明：可配 PBR 材質；目標有 ERM 本體與 PBR 材質）；Cave = Vanilla（目標的 ERM 本體沒有洞穴 mesh） | Petroglyphs of Skyrim |
| Petite to Plenty v9.0 | 全預設（v9 Movement、Scrotum collision Enable、Female config 預設） | 無 |
| Ruins Across Skyrim | Ruins Over Riverwood＋NOTWL、Northern Roads 補丁；Ruins of the Swamp；Falkreath Fort Ruins；Hjorn 補丁不勾 | 5 個，全符預期 |
| Save & Load Accelerator for SKSE Cosaves (S.L.A.C.K.) | Skyrim SE v1.5.97; SKSE64 v2.0.20（自動） | 無 |
| Splashes of Skyrim 1.5 | SSE v1.5.97（自動） | 無 |
| Shattered Royal Armor | UBE = None（自動）；PBR（目標有 Shattered Royal Armor PBR 4k） | ShatteredRoyalArmor |
| Skyrim Outfit Equipment System NG | Core；OStim 不勾 | SkyrimOutfitEquipmentSystemNG |
| Skyrim Tranquil ponds | 2k；CC Fishing、NotWL（目標沒有 Seasons of Skyrim 等其他對應 mod） | Skyrim Tranquil Ponds、STP - CC Fishing integration、STP - NotWL patch |
| Snazzy Misc Locations AIO | Black Briar Lodge、Drelas' Cottage、Honningbrew、Sarethi Farm；JK's Dragonsreach、JK's Palace、Wayward Rest 取消（插件不在目標） | 4 個 |
| Texture Downscaler | BALANCED（推薦；第 7 階段可再調） | 無 |
| VIGILANT SE 1.8 | Core；English（說明：英文使用者不要裝日文版，字型不符）；Silent Voice 勾（note：English Voices Addon 裝在 Silent 之上；目標另有 VIGILANT - English Translation (Silent) 與 Voices Addon 在上層） | Vigilant.esm（2.1 GB，完整） |
| Unslaad SE2 | Core；English；Silent Voice 勾（比照 Vigilant；目標有 Unslaad - English Voices Addon2 在上層，避免語音包沒涵蓋的台詞出現日文語音。先裝成不勾，確認後以 Replace 重裝） | Unslaad.esm（1.95 GB，完整） |
| Vanaheimr Mountains | True PBR；Smoother Normal None；Grey Textures 不勾 | Vanaheimr Mountains PBR |
| True Flasks NG | TrueFlasks Plugin；Upgradable Flasks（推薦）＋Flasks Restore Duration；Replace Vanilla Potions 不勾 | TrueFlasks、Upgradable Flasks、Restore Duration |
| Windhelm Mighty Statues Reforged | Talos（預設） | Windhelm Mighty Talos Reforged |
| Tomato's Riften PBR - 2k | 全推薦預設（原木紫漆、新紫色石板屋頂） | 無 |
| Tomato's Whiterun Remake - PBR or Complex Material | 全推薦預設（TomatoRim PBR Tundra Grass、Remake 屋頂／雕刻、新木盾、New Walls 2.3、Multilayer Parallax 窗） | 無 |
| Nature of the Wild Lands - Rock Replacer | PBR（目標有 NotWL PBR）；Grey（預設） | 無 |
| High Quality PBR Ivy | Main；Variant 1 2k（預設是 4k；目標沒指定，筆電用 2k） | 無 |
| nordic stonewalls pbr | 全預設（四項 Yes、Dark Grey、Style 1） | 無 |
| NordwarUA Legions PBR | 只勾 New Legion（目標只有 New Legion） | 無 |
| Complex Silverware PBR | Yes＋Rudy HQ 補丁（目標有 Rudy HQ - Miscellaneous）；Silver Object SMIMed 不勾 | 無 |
| Praedy's Chantry of Auriel AIO - SE | damaged（預設）；ruins Default、Ancient Falmer Armor、Bow Option 1、Shield Default、gems Default（這一步預設全是 None，等於不裝材質，已改；非 ENBL）；throne Default；ghosu 不勾；CPM 不勾 | Praedy's AncientFalmerThrone |
| Wolves of Skyrim | 2k（說明建議低規格電腦用 2k）；Fluffy Wolves（推薦）；SIC 補丁不勾（目標沒有 SIC） | 無 |
| Yggdrasil - Floating Tree Redux | Redux；Yggdrasil Trees (both)（推薦）；Magical Stairs。注意：note 寫「選 Floating Tree」，但目標插件是 Yggdrasil Trees.esp（只有 both 會產生），選 Floating Tree 會產生目標沒有的 Yggdrasil - Floating.esp，所以照目標插件選 | Yggdrasil Trees |
| Skyrim Wayshrines - Immersive Fast Travel - SWIFT SE | Core；Gray Cowl、Falskaar、Wyrmstooth、Darkend；Landscape and Water Fixes 補丁；Cathedral facegen 不勾（目標沒有） | 6 個，全符預期 |
| Seasonal Wigfrid's Erdtrees Replacer | Autumn Yellow（預設）；相容補丁不勾（插件不在目標） | 無 |
| UNDERDOG - Animations 3.0 | Install everything（預設是 Custom，已改）：Underdog Experience＋UA - EVG CLAMBER Patch（目標有 EVG Clamber） | 無 |
| Vanaheimr - Landscapes - AIO - PBR | Core；各選項預設（Ice Blue、Fieldgrass01 Green、Tundra01 Mixed，選用項都不勾）；Patch 勾 NGIO（目標有 NGIO - NG），Seasons 不勾。核心附帶的 SnowShader.esp 目標沒有（MO2 會列為停用） | Vanaheimr Landscapes（＋SnowShader，停用） |
| Tiny Light Placer Hub2 | Vanilla：Blood Potion、Daedric Reliquary、Elytra、Falmer Eye、Falmer Pullchain、Fungal Pods、Gemstones、Ground Cover、Ore Veins、Shellbug、Skull-keys、Taproot、Volendrung、Wisp Wrappings；不勾 4 個 ⚠️（Arrows、Azura's Statue、Briarhearts、Sigil Stones：說明要配發光模型替換，目標沒有）與 Oil Lamp Trap（Lux CS Patch 和 CS Lights 已對同一模型放光源）。Mods：Cathedral 3D Dragon's Tongues、Clockwork、College of Winterhold - Glowing Symbols、Rudy HQ - Daedric Weapons and Armor；Skyshards (Arthmoor) 不勾（目標的 Skyshards 是 Deadmano 版，已由 Skyshards - CS Light Addon 處理），其餘 mod 目標沒有。MO2 顯示「沒有有效遊戲資料」旗標（只含 LightPlacer 資料夾，MO2 不認得，但檔案照常載入） | 無 |
| CS Lights2 | 光源類型 = 使用 LUX（跳過蠟燭、火焰、吊燈、火把、矮人、燈籠；目標用 Lux 系列）；AE：Ghosts of the Tribunal、Saints and Seducers（本體有這兩個 CC）；Mods：Wyrmstooth、Rustic Soulgems、Dwemer Pipework Reworked（目標都有）；藥水 = Default（同路徑檔會被 CS Potion Lights - Awesome Potions Simplified 覆蓋）；CS Light.esp 勾；窗戶光源內外都不勾（外部作者不建議、效能差；內部是選用，Lux 已處理室內光源，筆電效能優先，可再議）；Custom：推薦項全勾，但 Paragon Gems 不勾（目標已有 Iconic's Paragon Gems 粒子光源補丁，同一批模型）、Soulgems 不勾（與 Rustic Soulgems 同模型）；CS Light.ini 不勾；Particle Patch LP 不勾（實驗性，與 LUX Particle Lights LP 重疊） | CS Light |
| Ancient Land Patches | Fancy Morthal Swamp Overhaul、Leaps of Faith、Northern Roads（MO2 依已啟用插件自動勾）；Ryn's Whiterun City Limits 取消（自動勾，但補丁插件不在目標）。註：第一次開時 Fancy Morthal 選項是灰的，因為 MO2 把新裝的插件列為停用；關 MO2 跑 `sync-order --restore-states` 後正常 | 3 個，全符預期 |
| Ashe 3 | 3BA（目標用 CBBE 3BA）；EFA Ver.（目標有 Expressive Facial Animation - Female Edition）；HDT 頭髮 No（SMP_Hair.esp 不在目標）；Impressionist VO = Disable the voices!（產生目標的 Ashe Impressionist Patches.esp）；眼睛、皮膚 Default；OAR 動作 = Idle and Movement - Redux（作者的新版）；戰鬥動作 = Warden MCO（目標用 ADXP MCO＋SCAR，也有 Warden 系列）；Conditional Animations 安裝（預設）；RCO Patch Yes | Ashe - Fire and Blood、Ashe Impressionist Patches、Ashe RCO Patch |
| DBVO Vampira | MO2 自動偵測（依已啟用插件）全部接受，含 Skyrim Base Game（語音包註冊必需）、USSEP、Remnant、Player Names；手動項只勾本體有的 AE CC：Creation Club AIO、Daedric Mail、Bittercup、Farming、Gray Cowl Returns（較新的付費 Creations 本體沒有，不勾）；At Your Own Pace - Dragonborn 手動勾（目標有）；ezPG、Simpler Knock、OStim、Requiem 不勾。第一次安裝時 Ashe 選項是灰的（Ashe 插件剛裝、MO2 列為停用），取消後再跑一次 restore-states 重裝 | 附帶 41 個「DBVO Fix」插件，目標都沒有（目標另外的語音包也都不含插件），MO2 會列為停用 |
| Flat World Map Framework2（replace_dll） | 依 M&V 原本的檔案逐一比對還原選項：Flat Map Markers **SE（1.5.97）**（M&V 是 AE 版）；白名單 = Skyrim + Regional maps + DLCs + Add-ons（設定檔與 M&V 相同）；FOV = No、Filter = No（M&V 沒有 BakaWorldMapFOV.dll／Filter 設定）；Fantasy Paper Maps；天氣 = Vanilla and ready-to-go；Water for ENB Yes；RW2 不勾；EVLaS Yes（M&V 有 Tamriel_Underside.nif；第一次誤選 No，已重裝）；Lux Yes；背景 Plain Black（雜湊相同）；MCM 不裝。結果：除 FlatMapMarkersSSE.dll 與 meta.ini 外，檔案與 M&V 完全相同。「World Map Panning Speed」群組只有一個選項、無法不選，會裝 AE 版 BakaWorldMapSpeed.dll；依 decisions 放棄，已改名為 `.mohidden`（MO2 的隱藏，可還原）。M&V 的舊內容先整包搬到 `D:\PM\_replaced\Flat World Map Framework2` 保留，沒有刪除 | FWMF for Fantasy Paper Maps、Lux patch for FWMF、Water for ENB - Patch - FWMF for Fantasy Paper Maps |
| Grand Solitude Patch Collection | 讀過警告；Bards College = None（自動偵測選了 JK's，但目標沒有 GS 的 JK's BC 補丁與相關一致性補丁）；CC 5 個全勾；Lord's Mail = Rebalancing AE（目標有 RAEQuestRequirements.esp）；雜項 31 個照目標（自動偵測結果逐一核對，全部相符）；雕像 Gaius Mucius、Jason 手動勾；Patches 2：EmbersXD（手動，只有 mesh，目標有 Embers XD；ElSopa 鐵砧版不選）、Remiel = None（自動選了 regular，目標沒有）、壁畫 = Solitude Only (No Lanterns) - ESP；其餘 None | 40 個目標插件全到；條件式多裝「Grand Solitude - Undeath + Sewers navpatch.esp」（目標沒有，停用） |
| JK's Fort Dawnguard - SDA Patch | 讀過警告；JKs Interiors 只勾 Fort Dawnguard（自動偵測全部 11 個都勾了，取消其他 10 個）；Fort Dawnguard 補丁只留 Serana Dialogue Addon；屋頂 None、Ice Claws None。注意：自動偵測勾了目標要的 7 個 Fort Dawnguard 補丁，但硬碟上（已擷取的 JKs Guild HQ Interiors Patch Collection）只有 LAWF、LFFGM；Cloaks of Dawnguard、Dawnguard Arsenal、RDO、WACCF 缺，待回報決定放哪個資料夾 | JKs Fort Dawnguard - SDA patch |
| Riverwood Falls - Waterfall Additions for Riverwood2 | Main；Ryn's Bleakfalls Tower；Ancient Land 取消（自動勾，但補丁不在目標）；NotWL；Northern Roads＋NR 補丁 LFFGM、Lux Via、Ryn's Bleak Falls；Treeless Path、Northern Roads Clutter（Yes，有 Northern Roads）；Remove Fogs 不勾；Built-in Terrain LOD 不勾（第 5 階段重建 LOD）。目標的「Riverwood Falls - Landscape Fixes for Grass Mods.esp」在壓縮檔 Patches 資料夾，但 FOMOD 沒有任何選項會裝它，已從壓縮檔直接放入 | 10 個全符預期 |
| Ryn's Whiterun City Limits - Patch Collection | 讀過警告；主要 mod 只勾 Ryn's Whiterun City Limits（目標沒有 JK's Whiterun Outskirts、HS Battle-Born Farm）；Capital Whiterun、Iggath = None；自動偵測的 15 個補丁與目標完全相符（CC Fishing、Tundra Homestead、A Cat's Life、BadGremlins、Better Courier、Clockwork、CRF、Fallen Tree Bridges、LAWF、LFFGM、LOTD、Lux Via、NotWL、Ryn's White River Watch、Skyrim Sewers）；Windmill placement fix 不勾；一致性補丁 CRF + Skyrim Sewers、Lux Via + CRF | 17 個 |
| SDA - Standing stones patch | 壓縮檔是 Solstheim Exterior Soundscapes；主檔已由擷取的「Solstheim Exterior Soundscapes」資料夾提供，而 FOMOD 第一步會強制裝主檔，所以改用 MO2 的 Manual 安裝：資料根目錄設為 Patches，只勾 SES All Maker Stones - SDA Patch.esp（Pilgrim 兩個不勾） | SES All Maker Stones - SDA Patch |
| SDA Patch Hub SE | 動作框架 None；覺察：Campfire、Wintersun（一般版；目標沒有 CACO，自動偵測沒勾，手動補）、IFD Lydia、House of Horrors；相容：NFF、Amulets of Mara、RDO、Remiel、CC Umbra（自動偵測全對）；偏好補丁不勾；Necklace of Vivacity = CBBE | 9 個全符目標 |
| SilentStorm's Patches for DK's Realistic Nord Ships | DynDOLOD、The Great City of Winterhold (4.1)、The Great Village of Mixwater Mill；Unique Red Wave（目標沒有）、Icerunner、Ivarstead、Kynesgrove（補丁不在目標）不勾 | 3 個全符預期 |
| Skyrim Main Menu - Edge Edition | Standard (16:9)（筆電是 16:10，只有 16:9／21:9 可選）；背景、版面、Loadframe、存檔框、Logo、進度圖示、游標、粒子、音樂全用預設（第一項） | 無 |
| Wayshrines - JK's Skyhaven patch | manifest note：Tiny Patch Hub 只選 Skyrim Wayshrines - JK's Sky Haven Temple Patch。此 FOMOD 根目錄有 389 個項目、341 個條件選項，GUI 逐一取消不可行，改為關閉 MO2 後用 7-Zip 只取出這一個 esp，並用 `pm.mo2.install_meta_text` 寫 meta.ini（modid 62050、fileid 721698、2.5.1），download 的 .meta 標為已安裝（與 install_archives 相同做法） | Skyrim Wayshrines - JK's Sky Haven Temple Patch |
| Yet another patch hub for Ryn's Skyrim2 | ELFX = No；依已啟用插件自動偵測的結果逐頁核對，與目標完全相符：Azura's Shrine 3DNPC／ACE／Moon and Star、Bleak Falls NotWL、Broken Tower Redoubt NotWL（完整版；目標沒有 Reach Shrub 裁切插件）、Goldenglow LAWF／NotWL／USSEP、Karthspire LAWF／NotWL、Lost Valley Redoubt LOTD／NotWL、Saarthal NotWL／USSEP、Ustengrav USSEP、Western Watchtower NotWL／USSEP | 17 個 |
| Water for ENB [cs]2 | Style = Shades of Skyrim for ENB（目標有 Water for ENB.esm，只有 ENB 系列 Shades 會產生；目標的 Mirele、Lux Ragged Flagon 補丁也只在 ENB 路徑；M&V、Nolvus 同樣是這個組合）；貼圖 2K、瀑布 Transparent＋2K＋Parallax（筆電改選 2K，預設 4K）；LOD 亮度 Default；自訂項全不勾；相容：Atlas、JK's Bannered Mare、JK's Solitude Outskirts、LFFGM、Lux - JK's Ragged Flagon、MEZF、Mirele；取消自動勾的 JK's Candlehearth Hall、Winking Skeever、Bruma、Falskaar、Wyrmstooth（補丁不在目標）；新世界 Midwood Isle、Forgotten City；FWMF = Fantasy Paper Map；No Legacy iNeed | 12 個全符目標 |
| Snazzy Misc Locations AIO（重裝更正） | 加勾 JK's Palace of the Kings（FOMOD 目的檔名是 `….esp.esp`，裝好後改回 `.esp`；目標有這個插件）；JK's Dragonsreach、Wayward Rest 仍不勾 | Snazzy Interiors - JKs Palace of the Kings（共 5 個，全在目標） |
