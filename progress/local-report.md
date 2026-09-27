# 本地回報（本地代理每個階段結束時覆寫；雲端讀取）

> 公開倉庫：只寫摘要。不寫 Windows 使用者名稱、帳號、序號、金鑰；不附截圖或整份日誌。

- 階段：5 重建輸出。照 cloud-notes 13db1b8「接下來的順序」做完 1–4，以及第 5 步的 PGPatcher → 草地 → xLODGen → TexGen。**DynDOLOD 之前停下回報。**
- 日期：2026-09-27
- 結論：
  - **RaySense 1.2.0**：
    - OAR 錯誤從 104 行降到 **4 行**，「RaySense_Ledge not found」0 行。
    - 主選單正常，DataLoaded 171 秒。
  - **Synthesis**：照新的 docs/05 第 3 節完成。
    - `Synthesis.esp` 有 47 個前置、LAND 7,675 筆，**每筆都有 VCLR**，已加上 ESL 旗標。
    - 需要 .NET 10 SDK（使用者同意後安裝）。
  - **各工具的輸出**：
    - PGPatcher：20,432 個檔。
    - 草地快取：15,340 個 `.cgid`，沒有 `.fail`。
    - xLODGen：48,852 個檔，52 個世界空間。
    - TexGen：5,292 個檔。
  - **`check_plugins`**：每個工具之後都全部 `[通過]`。最後一次是完整 251／254、預估 253、輕量 4017／4096。
  - **停在 DynDOLOD 之前的原因**：
    - TexGen 載入插件時出現 **14 個「Record … in file Skyrim.esm is being overridden by …」錯誤**。DynDOLOD 的說明寫「可能造成 CTD，需要修正」。
    - 原因是 5 個修補檔對應的是新版主插件，而 D:\PM 裝的是 Nolvus 的舊版。見「需要雲端決定」第 1 點。
    - 我用同樣的方法掃了整個載入順序，還有其他修補檔引用了「已安裝的主插件裡不存在的記錄」，其中 195 筆在室外（第 2 點）。
    - DynDOLOD 要跑好幾個小時，室外的記錄會進 LOD。先請雲端決定要不要修，免得重跑。
  - TexGen 的輸出和這些記錄無關（TexGen 只用基底物件的模型和貼圖），所以先做完了。

## 照 cloud-notes 的步驟
1. `git pull --rebase`（13db1b8）、`python -m pytest -q`：188 項通過、1 項略過。
2. **RaySense**：
   - `manifest`：需整包重裝 1 個。
   - `nexus_fetch`：下載 1 個（175498／796343）。
   - `install_archives --only "Open Animation Replacer - RaySense3"`：試跑是「可自動重裝 1 個」，`--apply` 後已重裝，舊內容在 `_replaced`。
   - `audit_skse --dll`：`OpenAnimationReplacer-RaySense.dll` 判為多版本 NG（可用）。
3. **主選單測試**：
   - DataLoaded 171 秒，`skse64.log` 檢查 215、載入 214。
   - RaySense 1.2.0（DLL 版本 01020000）有載入。
   - 這次沒有 OAR 的「Major issue」橫幅。
   - `OpenAnimationReplacer.log`：I 1,098、W 8、E 4。
     - RaySense_Ledge not found：0 行。
     - E 4 行都是「Failed to parse file」，其中 3 行是 OAR Stance Movement／Combat Framework 裡的 `config.json`（Dagger and Shield Non Combat Idle Start、Dual Katanas Parry Layer、Battle Axe Movement Combat），1 行沒有路徑。
   - 在主選單直接結束，沒有存檔。
4. **Synthesis**（docs/05 第 3 節）：
   - MO2 加了第 14 個執行檔 `Synthesis`（0.36.6，`D:\PM\tools\Synthesis`）。
   - Patcher：用 Git 儲存庫加入 Jampi0n 的 Remove Landscape Vertex Color。
     - main 分支 e59abc8，專案 `RemoveLandscapeVertexColor.csproj`。
     - **Settings 保持預設**。
   - 編譯：
     - Synthesis 0.36.6 會把 patcher 的編譯用副本改成 net10.0，沒有 .NET 10 SDK 就 Compilation Error。
     - 使用者同意後安裝 .NET 10 SDK，就編譯成功了。
   - 執行：
     - Synthesis 的 Profile 要把 Data Folder 手動指定成 `D:\PM\STOCK GAME\Data`，否則 mod 都顯示 Missing。
     - 照 MO2 mode 的做法：在 MO2 外編譯，再從 MO2 執行。
   - 輸出：`SYNTHESSIS\Synthesis.esp`。
     - `esl_check --subrecords LAND`：LAND 7,675 筆，VCLR 7,675。
     - 試跑「可以加旗標」→ `--flag --apply`。
   - MO2 事先把 `Synthesis.esp` 加成**停用**，`sync-order --apply` 不會啟用它。
     - 我手動在 plugins.txt 啟用，備份在 `_backup\20260927-164954-enable-synthesis`。
     - 之後 `check_plugins` 全部通過。
5. **PGPatcher**（第 4 節）：
   - 設定檔 `cfg\settings.json` 裡的路徑是 M&V 的（D:\MV），改成 D:\PM，有備份。
   - 第一次執行出現 Critical Error，原因是輸出 mod `pgpatcher_output` 在 MO2 裡是啟用的。
     - 執行期間先停用，完成後再啟用，modlist 都有備份。
   - 257 秒完成，20,432 個檔。`PGPatcher.esp`、`PG_1.esp` 都是輕量插件。
   - **目標 plugins.txt 有 `PG_2.esp`，這次沒有產生**。`check_plugins` 沒有把它列為待重建。
6. **草地快取**（第 5 節，方案 A）：
   - `GrassControl.ini` 放在 `Pages - 設定覆寫`，設成方案 A 的 5 行。
   - 照手冊暫時停用 True HUD。
   - 第 1 輪：啟動 1 次、41 分鐘，產生 9,044 個 `.cgid`、1 個 `.fail`。
     - NGIO 把 `PrecacheGrass.txt` 改寫到 `overwrite\Root`（Root Builder 的重導），不在 `STOCK GAME`。我的監看腳本因此誤判為完成。
   - 改好判斷後繼續：第 2 輪重開 7 次，18:38 記錄出現「Grass generation finished successfully!」。
   - 總共約 95 分鐘，**15,340 個 `.cgid`，沒有 `.fail`**。
     - 已搬到 `grass CS\grass`，True HUD 已重新啟用。
     - 殘留的標記檔搬到 `_replaced\grass-precache-marker-20260927-183958`。
7. **xLODGen**（第 6 節）：
   - 參數設為 `-SSE -D:"D:\PM\STOCK GAME\Data" -o:"D:\PM\gen\lodgen"`。M&V 的參數本來就有 `-D:`。
   - 第一次由使用者照預設勾選執行，產生了 Tamriel 的 Objects＋Trees LOD。這份輸出已搬到 `_replaced\xlodgen-objects-trees-20260927-223430`。
   - 第二次由我操作：全選世界空間，只勾 **Terrain LOD**，細項用預設。
     - 17 分鐘完成，最後一行是「LOD generation done.」，記錄沒有錯誤。
     - **48,852 個檔、52 個世界空間**（M&V 是 14 個），已搬到 `lodgen2`。
8. **TexGen**（第 7 節）：
   - 參數設為 `-SSE -D:"D:\PM\STOCK GAME\Data"`。
   - 載入插件時跳出 14 個「being overridden」錯誤，都按 Ignore（見第 1 點）。另有 1 個「PBR textures detected」說明，按 OK。
   - 輸出路徑：
     - TexGen 的設定檔 `Presets\DynDOLOD_SSE_TexGen.ini` 是 M&V 上次的設定，輸出路徑是 `D:\MV\tools\DynDOLOD\TexGen_Output\`。
     - 在畫面上改成 `D:\PM\tools\DynDOLOD\TexGen_Output\`。
     - 記錄出現「Path not allowed」後又「Resetting … to」同一個路徑。M&V 自己的記錄也有這一行，所以沒有影響。
   - 其他設定照預設：
     - Stitched／Rendered 都是 256、PBR 0.65。
     - Billboard 8.0 (1440p)，大小 32–1024，PBR 0.70。
     - 勾 Tree 和 Rendered；不勾 Grass、HD Grass、HD Tree。
   - 5 分 54 秒「TexGen completed successfully」，按 **Exit TexGen**（不是 Zip and Exit）。
   - 產生 1,259 個 billboard（M&V 是 777 個）。
   - 記錄（只看這次的工作階段）：
     - 42 個 `<Error>`：
       - 41 個是 File not found。
         - `textures\oak\oakleafmushroom01_n.dds` 有 34 個，都是 `Ancient City of Markarth.esp` 和 `maerchenwald - the archwood lite.esp` 的 rainforest 樹木模型用到的。
         - 其餘：`TreePineForestBarkCompSnow_p.dds` 2 個、`dlc02\…\WoodEdgeTrim01_p.dds` 2 個、`high poly project\stonewall.dds` 2 個、`giantforest\mossybark01_n.dds` 1 個。
       - 1 個是上面的 Path not allowed。
     - 3 個 `<Warning>`：「extended FormID range 的模組第一個前置應該是遊戲主檔」，出現在 `GOOSE_Mages of Skyrim.esp`、`Lux CS Templates - Bright.esp`、`Praedys_SoulCairn PBR.esp`。
   - 輸出 **5,292 個檔（519 MB）搬到 `texgenCS`**，`TexGen_Output` 已清空。
   - 之後跑 `sync-order`（試跑後 `--apply`）和 `check_plugins`，全部通過。

## 輸出資料夾的檔案數
| 資料夾 | 檔案數 | 大小 | 備註 |
|---|---|---|---|
| `SYNTHESSIS` | 1 | 69 MB | `Synthesis.esp`（輕量） |
| `pgpatcher_output` | 20,432 | 5,898 MB | `PGPatcher.esp`、`PG_1.esp`（輕量） |
| `grass CS` | 15,340 | 915 MB | 全是 `grass\*.cgid` |
| `lodgen2` | 48,852 | 933 MB | 地形 LOD，52 個世界空間 |
| `texgenCS` | 5,292 | 519 MB | |
| `dyndolodCS2` | 0 | | 未做 |
| `Pandora Output` | 41 | 13 MB | 上一輪 |
| `BodySlide (Nude)` | 8,754 | 7,447 MB | 5,825 nif＋2,929 tri，上一輪 |

- Synthesis 的 LAND 筆數：7,675（每筆都有 VCLR）；前置數量：47。
- DynDOLOD 還沒執行，沒有記錄檔。

## 工具結果（照抄 reports\*.txt 的每一行）
每個工具之後都跑了 `sync-order --apply` 和 `check_plugins`，全部 `[通過]`；檔案只留最後一次，以下是最後一次的全文。
```
== manifest 報告 (2026-09-27 16:27) ==
[資訊] 目標資料夾：4053 個
[資訊] 已就位：4022 個
[資訊] 需從 Nexus 下載：0 個
[資訊] 第五階段重建：9 個
[資訊] 需換成 1.5.97 版 DLL：0 個
[注意] 需整包重裝（舊內容移到 _replaced）：1 個
[資訊] 尚無來源，需人工確認：0 個
[資訊] 捨棄：21 個
[資訊] 輸出：reports\manifest.csv、reports\downloads.html
總結：[注意]

== nexus_fetch 報告 (2026-09-27 16:27) ==
[通過] 本次下載：1 個
總結：[通過]

== install_archives 報告（--only "Open Animation Replacer - RaySense3"，試跑）==
[通過] 可自動重裝（舊資料夾移到 _replaced，不刪除）：1 個

== install_archives 報告 (2026-09-27 16:27)（--apply）==
[資訊] 執行：判斷了 1 個下載
[資訊] 磁碟空間：預計解壓 1.2 MB，D:\ 剩 253.9 GB
[通過] 已重裝（舊資料夾在 _replaced）：1 個
總結：[通過]

== audit_skse-dll 報告 (2026-09-27 16:27) ==
[通過] OpenAnimationReplacer-RaySense.dll：多版本 NG（可用）；Address Library：SE／AE 都支援
總結：[通過]

== esl_check 報告 (2026-09-27 16:48)（--subrecords LAND --flag，試跑）==
[資訊] Synthesis.esp：full，HEDR 1.71，前置 47 個；記錄 15392 筆（新增 0、覆寫 15392）；覆寫類型：CELL 7675, LAND 7675, WRLD 42；ESL：可以直接加 ESL 旗標
[資訊] LAND 子記錄：LAND 記錄 7675 筆；各子記錄出現在幾筆記錄：DATA 7675, VCLR 7675, VHGT 7652, VNML 7652, ATXT 7522, VTXT 7522, BTXT 7346
[資訊] 加 ESL 旗標（試跑）：可以
總結：[資訊]

== esl_check 報告 (2026-09-27 16:49)（--flag --apply）==
[資訊] Synthesis.esp：full，HEDR 1.71，前置 47 個；記錄 15392 筆（新增 0、覆寫 15392）；覆寫類型：CELL 7675, LAND 7675, WRLD 42；ESL：可以直接加 ESL 旗標
[通過] 加 ESL 旗標：Synthesis.esp 已是輕量插件
總結：[通過]

== build_instance-verify 報告 (2026-09-27 16:50) ==
[資訊] 模式：試跑（加 --apply 才會寫入）
[通過] modlist.txt 與預期比對：一致
[資訊] 清單外的資料夾：84 個：ZH - 官方繁中字串, Unslaad PBR, Smooth Special Idle, Maerchenwald - Archwood Lite - Giant Fantasy Trees, horseAnimations2, clockwork pbr, Creation Club: _ResourcePack, Creation Club: ccafdsse001-dwesanctuary, Creation Club: ccasvsse001-almsivi, Creation Club: ccbgssse001-fish
[注意] plugins.txt 與預期比對：缺少或未啟用 41 個（mod 尚未安裝或已被修剪）；待重建輸出 6 個；例如：Ryns Whiterun City Limits - Water for ENB (Shades of Skyrim).esp, Anchor Animations Spell V2.esp, FH_Grapple.esp, AnchorShdSwd.esp, SC_HorseReplacer.esp
總結：[注意]

== build_instance-sync-order 報告 (2026-09-27 23:29)（TexGen 後，--apply；試跑的數字相同）==
[資訊] 模式：實際執行
[通過] 插件順序：4506 個：依目標順序 4197，新增的 309 個放在輸出插件之前
[通過] 前置順序：移動 135 個插件到它的前置之後，例如：Natural Waterfalls - Blackreach.esp, Natural Waterfalls - Dawnguard.esp, Natural Waterfalls - Dragonborn.esp, Occ_Skyrim_Lux_Via.esp, Rainbows over Waterfalls - Bruma addon.esp, Rainbows over Waterfalls - Natural Waterfalls patch.esp, Complementary Grass Fixes - CRF Patch.esp, Additional Dremora Faces - VIGILANT Patch.esp
[資訊] 不在目標清單中的插件：Lux - JK's Dragonsreach patch.esp, Lux Orbis - Reich Corigate.esp, Nolvus Awakening Darkwater Crossing Patch.esp, Northern Roads - Strongholds - Dushnikh Yal Patch.esp, DBVO Fix - Missives Wyrmstooth.esp, JKs Raven Rock - USMP patch.esp, Orc Strongholds AIO - Skyshards Patch.esp, Occ_Skyrim_Jk's-Whiterun-Outskirts_patch.esp, DBVO Fix - The Gray Cowl Return
[資訊] 備份：D:\PM\profiles\Pages-ZH\_backup\20260927-232944
總結：[通過]

== check_plugins 報告 (2026-09-27 23:29)（TexGen 後）==
[通過] 完整插件數（含本體）：251 / 254
[通過] 輸出重建後的完整插件（預估）：253 / 254：DynDOLOD.esm, DynDOLOD.esp 一定是完整插件；Synthesis.esp、FNIS.esp、Occlusion.esp、PG_* 必須是輕量插件
[通過] 輕量插件數（ESL）：4017 / 4096
[通過] 缺少前置的插件：0 個
[通過] 前置順序錯誤：0 個
[通過] 找不到的插件：0 個
[通過] 無法讀取：0 個
[通過] 待重建的輸出插件：0 個
[通過] 依賴待重建輸出：0 個
[通過] BEES：1.71 標頭插件 919 個；BEES 已安裝；遊戲 1.5.97.0
總結：[通過]
```
- `[注意]` 的說明：
  - manifest 的 reinstall 1 個就是 RaySense，已重裝。
  - verify 的 41 個＝接受缺少的 15 個＋修剪的 26 個。待重建輸出 6 個是當時還沒做的 PG、DynDOLOD、Occlusion。

## 需要雲端決定
1. **TexGen 的 14 個「being overridden」錯誤**：
   - 來源：5 個輕量修補檔（都是 HEDR 1.71）引用了主插件裡 **0x800 以下的物件編號**，但它們的主插件是 1.70 版的舊標頭。
     - xEdit 會把 1.70 版主插件的這種編號當成 Skyrim.esm 的內建記錄。其中 14 筆剛好撞到 Skyrim.esm 的 STAT／AVIF，所以跳出錯誤。
     - 其餘 90 筆沒撞到，不會跳視窗，但一樣指向不存在的記錄。

     | 修補檔（來源） | 主插件 | 0x800 以下的筆數 | 撞到 Skyrim.esm | 位置 |
     |---|---|---|---|---|
     | Snazzy Interiors - Karthwasten Hall - The Great Town of Karthwasten Patch.esp（Snazzy Interiors Patch Collection 2.8） | The Great Town of Karthwasten.esp | 93 筆 REFR | 13（AVIF 44C–45B） | 室內（Karthwasten Hall 000139D1） |
     | Great Town of Karthwasten - AI Overhaul Patch.esp（TGTK Patch Collection 3.4） | 同上 | 5 筆 NPC_ | 0 | — |
     | Snazzy Interiors - Karthwasten Hall - Lux (TGTK) patch.esp（Snazzy 2.8） | 同上 | 3 筆 REFR | 0 | 室內 |
     | Great Town of Karthwasten - Nature of the Wild Lands patch.esp（TGTK Patch Collection 3.4） | 同上 | 2 筆 REFR | 0 | **室外**（Tamriel 00007079） |
     | Snazzy Interiors - Markarth AIO - Forgotten in History patch.esp（Snazzy 2.8） | LOTD_HUB_FINH.esp | 1 筆 REFR | 1（STAT 005） | 室內（00016E00） |

   - 原因：這 5 個都是 `fill_plugins` 從**最新版壓縮檔**取出的（檔案都是單一連結），但對應的主插件用的是 Nolvus v6 的舊版。
     - TGTK：D:\PM 用的是 Nolvus 的 1.2（2021）＋Rob's Bug Fixes 1.0，兩者都沒有 0x800 以下的記錄。Nexus 上 2026-02-10 出了 **TGTK 2.0**。
     - TGTK Patch Collection：Nolvus 是 2.5.1，fill_plugins 取的是 MAIN 檔 **3.4**（2026-09-23）。3.0.1 在 TGTK 2.0 的隔天發布，看起來 3.x 是對應 2.0 的。
     - Snazzy Interiors Patch Collection 2.8（2026-08-08，和 M&V 同一版）：M&V 用的是 Spaghetti's Towns 的 Karthwasten，沒有裝這些 TGTK 補丁，所以是 fill_plugins 補進來的 77 個之一。
     - AI Overhaul 補丁的 5 筆 NPC_ 用的是 TGTK 的 NPC 名稱（MaddockTGCoKW 等），但 1.2 版裡這些 NPC 的編號不同。
     - Hall of Forgotten：Nolvus 是 2.3.9，Nexus 最新是 2.4.26。
   - Snazzy 的 TGTK 補丁是另外 4 個 Snazzy TGTK 補丁（3DNPC、AYOP TG、Cheesemod、Lux）的前置，那 3 個本身沒有不符的覆寫。
   - 可能的做法（請選）：
     - (a) 改用對應舊版主插件的補丁：TGTK Patch Collection 的 2.6.1（592870，2025-02-10）以前的版本、TGTK 2.0 之前的 Snazzy 版本（例如 2.3.1，672616）；Hall of Forgotten 的補丁同理。需要確認這些版本有那幾個插件。
     - (b) 用類似 `strip_refs` 的方式做同名修正版，刪掉指向不存在記錄的那幾筆。
     - (c) 停用這 5 個（和依賴它們的 4 個）。
     - (d) 升級 TGTK 到 2.0：Nolvus 其他對應 1.2 的 TGTK 補丁有十幾個，會連帶不符，不建議。
2. **整個載入順序的版本不符**（唯讀掃描；表格在 `data/analysis/override_mismatch.csv`）：
   - 方法：對每個啟用的插件，檢查它覆寫的每一筆非官方主插件記錄，確認已安裝的主插件裡真的有這個編號。
   - 結果：59 個插件、683 筆覆寫指向不存在的記錄，其中 **195 筆在室外**。
     - 這 59 個都屬於「插件和主插件來自不同清單」，或「插件是 Pages 補進來的」（其中 25 個是 Pages 補的）。
     - 另外有 17 個插件、70 筆，是 Nolvus／M&V 原本就這樣出貨的，沒有列進表格。
   - 室外筆數多、或總筆數多的：

     | 插件 | 主插件 | 不存在 | 室外 | 說明 |
     |---|---|---|---|---|
     | Lux Orbis - LotD patch.esp | LegacyoftheDragonborn.esm | 88 | 88 | Nolvus 的補丁，對應 LOTD 5，D:\PM 是 V6 |
     | Medieval Markets - Creation Club Fishing Patch.esp | Medieval Markets.esp | 37 | 37 | Pages 補的 |
     | Riverwood Falls - fallentreesbridgesSSE.esp | fallentreebridgesSSE.esp | 19 | 19 | Riverwood Falls 1.2.1 對 Nolvus 的 Fallen Tree Bridges |
     | JKs Raven Rock - Better Dynamic Ash patch.esp | Better Dynamic Ash.esp | 15 | 15 | Pages 補的 |
     | Ruins Over Riverwood - Northern Roads Patch.esp | Ruins Over Riverwood.esp | 7 | 7 | Pages 補的 |
     | Lux - JK's Blue Palace patch.esp | JK's Blue Palace.esp | 117 | 0 | Lux 補丁是 1.70 標頭，D:\PM 的 JK's Blue Palace 是 1.71（ESL），版本不同 |
     | Lux - Legacy of the Dragonborn patch.esp | LegacyoftheDragonborn.esm | 73 | 0 | LOTD V6 |
     | DBM_HUB_Unslaad_Patch.esp | LOTD_HUB.esp | 47 | 0 | Pages 補的 |
     | DBM_CCOR／AetheriumWeapons／RelicNotifications 等 DBM 補丁 | LegacyoftheDragonborn.esm | 1–38 | 0 | LOTD V6 |

   - 影響：遊戲會把這些覆寫當成新記錄。停用類的修改只是沒效果，但有位置的 REFR 可能在室外多出物件，DynDOLOD 也會把它們做進 LOD。
   - 請決定：哪些要修（換版本、做修正版或停用），還是接受後直接做 DynDOLOD。
   - 另外有 EDID 不同（152 個插件）和所在儲存格不同（135 個插件）的結果。這兩項在同一清單內也大量出現，誤判多，沒有列入。
3. **`PG_2.esp`**：目標有，這次 PGPatcher 只產生 `PG_1.esp`。請確認是否正常；如果是正常的，目標 plugins.txt 可以拿掉它。
4. **TexGen 找不到的貼圖**：`oakleafmushroom01_n.dds` 等 5 種（見步驟 8）。M&V 自己的 TexGen 記錄沒有這些錯誤，應該是 Pages 組合出來的（Ancient City of Markarth、Maerchenwald 的 rainforest 樹）。遊戲裡這些樹可能缺法線貼圖。

## 工具／手冊缺口（建議）
1. **docs/05 第 3 節（Synthesis）**：
   - 要先裝 **.NET 10 SDK**。Synthesis 0.36.6 會把 patcher 改成 net10.0 編譯。
   - Profile 的 Data Folder 要指定 `D:\PM\STOCK GAME\Data`。
2. **輸出插件被 MO2 加成停用**：
   - `Synthesis.esp` 在 sync-order 之前就被 MO2 列成停用，`sync-order --apply` 不會啟用它。
   - 建議 sync-order 自動啟用目標裡的輸出插件（Synthesis、PG_*、DynDOLOD、Occlusion）。
3. **docs/05 第 4 節（PGPatcher）**：
   - 執行前要在 MO2 **停用 `pgpatcher_output`**，完成後再啟用。
   - `cfg\settings.json` 的路徑是 M&V 的，要改成 D:\PM。
4. **docs/05 第 6–8 節的參數**：
   - 只寫 `-sse` 不夠。三個工具都要 `-D:"D:\PM\STOCK GAME\Data"`（M&V 的參數也有）。
   - xLODGen 另外要 `-o:` 指到 VFS 以外的空資料夾。
   - 已照這樣設定 ModOrganizer.ini（有備份）。
5. **xLODGen 的預設勾選**：
   - 預設會勾 Objects LOD 和 Trees LOD。使用者照預設跑了一次，做出多餘的輸出，已搬到 `_replaced`。
   - 建議手冊寫明「取消 Objects 和 Trees，只勾 Terrain」。
6. **TexGen／DynDOLOD 的預設設定檔來自 M&V，路徑指向 D:\MV**：
   - TexGen 的 `OutputPath` 我已在畫面上改好。
   - DynDOLOD 的 `Presets\DynDOLOD_SSE_Default.ini`：
     - `OutputPath=D:\MV\tools\DynDOLOD\DynDOLOD_Output\`。
     - LODGen 規則有 9 行指到 `D:\MV\...\Rules\DynDOLOD_SSE_all.ini`。
     - `Preset=Low`，M&V 用的是 Low。
   - 這些都是單一連結的副本。執行 DynDOLOD 時我會在畫面上選 High 並改輸出路徑；也可以先把檔案裡的 D:\MV 改成 D:\PM。刪除 D:\MV 之前一定要處理。
7. **`unshare_links` 沒處理的大記錄檔**：
   - `D:\PM\tools` 裡有 3 個和 D:\MV 硬連結的記錄檔，工具會改寫它們：
     - DynDOLOD_SSE_Debug_log 213 MB。
     - TexGen_SSE_Debug_log 41 MB。
     - xLODGen 的 LODGen_log 24 MB。
   - 它們超過 unshare 的大小上限，我已搬到 `_replaced\tools-hardlinked-logs-20260927-170727`。
   - 建議工具對記錄檔改成搬移，不做複製。
8. **草地快取的完成判斷**：
   - `PrecacheGrass.txt` 會被 Root Builder 重導到 `overwrite\Root`。
   - 手冊第 5.3 節可以註明：用 NGIO 記錄的「Grass generation finished successfully!」判斷完成，不要看 `STOCK GAME` 裡有沒有這個檔。

## 本輪手動處理（只新增、修改設定或搬移，沒有刪除）
- 使用者同意後安裝 .NET 10 SDK。
- MO2 設定（ModOrganizer.ini，有備份）：
  - 加入 Synthesis 執行檔。
  - 設定 xLODGen、TexGen、DynDOLOD 的參數。
- `Synthesis.esp` 在 plugins.txt 手動啟用，有備份。
- 暫時停用、之後重新啟用（modlist 都有備份）：
  - PGPatcher 執行時的 `pgpatcher_output`。
  - 草地快取時的 True HUD。
- 搬到 `_replaced`：RaySense 1.1、多餘的 xLODGen 輸出、草地標記檔、3 個大記錄檔。
- TexGen 的輸出路徑只在畫面上改，設定檔沒有另外修改。

## 本地提交（尚未推送）
- 本回報、status、`data/analysis/override_mismatch.csv`（插件名稱與 FormID，沒有個資）。
