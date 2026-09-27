# 各階段指令（Git Bash 寫法）

先進入倉庫：`cd "C:/PagesTools"`。路徑一律用正斜線並加引號。每個有 `--apply` 的指令都先不加跑一次（試跑），看過報告再加。
報告都在 `reports/`，檔名如下表。PowerShell 也能執行同樣的指令（反斜線或正斜線皆可）。

## 第 1 階段：準備筆電
```bash
python tools/preflight.py --install-drive D:
```
- 報告：`reports/preflight-*.txt`。
- `[失敗]` 常見原因：D 槽空間不足、Steam 語言不是 English、找不到 Steam 版 Skyrim、D 槽不是 NTFS。
- `[注意]` 常見原因：分頁檔、Defender 排除、CC 不足 74、.NET 未安裝。照 `docs/01` 處理。

## 第 2 階段：安裝 M&V 並擷取
```bash
python tools/inventory.py --source mv --instance "D:/MV"
python tools/harvest.py --from mv --instance "D:/MV" --pm "D:/PM" --mo2-and-tools
python tools/harvest.py --from mv --instance "D:/MV" --pm "D:/PM" --mo2-and-tools --apply
python -m pip install lz4
python tools/zh/extract_official.py --game-dir "D:/MV/Stock Game" \
  --extra-bsa "D:/MV/mods/Creation Club/_ResourcePack.bsa" \
  --out-mod "D:/PM/mods/ZH - 官方繁中字串" --work "D:/PM/zh-work" --fallback-english
python tools/zh/extract_official.py --game-dir "D:/MV/Stock Game" \
  --extra-bsa "D:/MV/mods/Creation Club/_ResourcePack.bsa" \
  --out-mod "D:/PM/mods/ZH - 官方繁中字串" --work "D:/PM/zh-work" --fallback-english --apply
# 選做：M&V 2.40.1 的 .wabbajack（1.5.97 版 DLL 對照）
python tools/analysis/mv_wabbajack_map.py --wabbajack "D:/WJ-Downloads/Mages & Vikings.wabbajack" --out-dir data/analysis --out-prefix mv2401
```
- 報告：`inventory-mv.txt/.csv`、`harvest-mv.txt/.csv`、`zh_extract_official.txt`。
- `harvest-mv` 的「來源缺少」有幾個是正常的（M&V 2.6 已移除、另由 Nolvus 或 Nexus 提供）。
- 刪除 `D:/MV` 與 Wabbajack 下載資料夾前**必須問使用者**，並確認三份報告都沒有 `[失敗]`。

## 第 3 階段：安裝 Nolvus
```bash
python tools/inventory.py --source nolvus --instance "D:/Nolvus/Instances/Nolvus Awakening"
python tools/harvest.py --from nolvus --instance "D:/Nolvus/Instances/Nolvus Awakening" --pm "D:/PM" --stock-game
python tools/harvest.py --from nolvus --instance "D:/Nolvus/Instances/Nolvus Awakening" --pm "D:/PM" --stock-game --apply
```
- 報告：`inventory-nolvus.txt/.csv`、`harvest-nolvus.txt/.csv`。
- `inventory-nolvus` 的「遊戲執行檔版本」必須是 `1.5.97.0`。
- Dashboard 若提供 6.0.21 而不是 6.0.20：先停下來回報雲端，不要安裝。

## 第 4 階段：組合清單（執行前先關閉 MO2）
```bash
# 先補擷取：decisions.csv 的 harvest_mv 項目，以及目標新加入的 Nolvus 資料夾（不加 --stock-game）
python tools/harvest.py --from mv --instance "D:/MV" --pm "D:/PM" --plan data/decisions.csv
python tools/harvest.py --from mv --instance "D:/MV" --pm "D:/PM" --plan data/decisions.csv --apply
python tools/harvest.py --from nolvus --instance "D:/Nolvus/Instances/Nolvus Awakening" --pm "D:/PM"
python tools/harvest.py --from nolvus --instance "D:/Nolvus/Instances/Nolvus Awakening" --pm "D:/PM" --apply
python tools/manifest.py --pm "D:/PM"
python tools/build_instance.py create --pm "D:/PM" --ini-from "D:/Nolvus/Instances/Nolvus Awakening/MODS/profiles/Nolvus Awakening"
python tools/build_instance.py create --pm "D:/PM" --ini-from "D:/Nolvus/Instances/Nolvus Awakening/MODS/profiles/Nolvus Awakening" --apply
# 第一次開 MO2（D:/PM/ModOrganizer.exe，設定檔 Pages-ZH）後關閉，再：
python tools/build_instance.py verify --pm "D:/PM"
# 下載（需要環境變數 NEXUS_API_KEY；也可以在 downloads.html 逐一按 Mod Manager Download）
python tools/nexus_fetch.py --pm "D:/PM" --limit 20
python tools/nexus_fetch.py --pm "D:/PM" --limit 20 --apply
# 沒有 FOMOD 的下載（含 replace_dll／reinstall：舊內容會搬到 D:/PM/_replaced）：
python tools/install_archives.py --pm "D:/PM"
python tools/install_archives.py --pm "D:/PM" --apply
# _ResourcePack（docs/04 7.1）：STOCK GAME\Data 沒有才建（Git Bash 下 mklink 的引號會被改掉，用 Python）
python -c "import os; os.link(r'D:\MV\mods\Creation Club\_ResourcePack.esl', r'D:\PM\STOCK GAME\Data\_ResourcePack.esl')"
python -c "import os; os.link(r'D:\MV\mods\Creation Club\_ResourcePack.bsa', r'D:\PM\STOCK GAME\Data\_ResourcePack.bsa')"
# 補齊缺少的插件（docs/04 8.1；先試跑，再 --apply；剩下的回報雲端）：
python tools/fill_plugins.py --pm "D:/PM" --mv "D:/MV" --nolvus "D:/Nolvus/Instances/Nolvus Awakening"
python tools/fill_plugins.py --pm "D:/PM" --mv "D:/MV" --nolvus "D:/Nolvus/Instances/Nolvus Awakening" --apply
python tools/fill_plugins.py --pm "D:/PM" --mv "D:/MV" --nolvus "D:/Nolvus/Instances/Nolvus Awakening" --plan-downloads
python tools/nexus_fetch.py --pm "D:/PM" --manifest reports/fill_plugins_downloads.csv --limit 100 --apply
python tools/nexus_fetch.py --pm "D:/PM" --manifest data/extra_archives.csv --apply
# 全部安裝完、沒有 download／review 項目後才做：
python tools/manifest.py --pm "D:/PM"
# MO2 會把新裝的插件列為停用；先依 _expected 還原啟用狀態，修剪才不會誤刪依賴它們的補丁
python tools/build_instance.py sync-order --pm "D:/PM" --restore-states
python tools/build_instance.py sync-order --pm "D:/PM" --restore-states --apply
python tools/prune_dependents.py --pm "D:/PM"
python tools/prune_dependents.py --pm "D:/PM" --disable-folders --apply
python tools/build_instance.py sync-order --pm "D:/PM" --apply
python tools/build_instance.py verify --pm "D:/PM"
python tools/check_plugins.py --pm "D:/PM"
python tools/audit_skse.py --pm "D:/PM"
```
- 報告：`manifest.txt` + `manifest.csv` + `downloads.html`、`build_instance-*.txt`、`nexus_fetch.txt/.csv`、`prune_dependents.txt` + `prune-plan.csv`、`check_plugins.txt/.csv`、`audit_skse.txt/.csv`。
- `manifest.csv` 的 `action`：
  - `keep`：已就位
  - `download`：下載並用 MO2 安裝，名稱照 `folder` 欄，遇到同名的空佔位資料夾選 Replace
  - `regenerate`：第 5 階段重建
  - `replace_dll`：改裝 1.5.97／NG 版
  - `reinstall`：版本不對，整包換成 decisions 指定的檔案（舊內容搬到 `_replaced`，不要在 MO2 選 Replace）；`meta.ini` 記錄到指定的檔案編號後會變成 `keep`
  - `review`：回報雲端，由雲端寫入 `data/decisions.csv`
  - `harvest_mv`／`harvest_nolvus`：還沒擷取，先跑上面的補擷取再重跑 manifest
  - `drop`：捨棄
- `audit_skse` 不加 `--mv-1597-map`（2.40.1 對照表不做）。
- `sync-order` 會把「前置排在後面」的補丁移到它最後一個前置的正下方（報告的「前置順序」）；「ESM 插件以一般插件為前置」的 `[注意]` 要回報雲端。
- `nexus_fetch` 依 `downloads\*.meta` 的 modID／fileID 判斷已下載，這些不呼叫 API、不算進 `--limit`。

## 第 5 階段：重建輸出（照 docs/05 的順序；工具從 MO2 執行）
```bash
# 工具第一次執行前（工具要先關閉）：把它的設定檔硬連結換成獨立副本
python tools/unshare_links.py --path "D:/PM/mods/BodySlide and Outfit Studio/CalienteTools/BodySlide" --apply
python tools/unshare_links.py --path "D:/PM/tools" --apply
# 每個工具的輸出搬好、MO2 關閉後：
python tools/build_instance.py sync-order --pm "D:/PM"
python tools/build_instance.py sync-order --pm "D:/PM" --apply
python tools/check_plugins.py --pm "D:/PM"
python tools/audit_skse.py --pm "D:/PM"
# 輸出插件是完整插件時（DynDOLOD.esm／.esp 以外）：先試跑，再加 --apply
python tools/esl_check.py --plugin "D:/PM/mods/SYNTHESSIS/Synthesis.esp" --flag
python tools/esl_check.py --plugin "D:/PM/mods/SYNTHESSIS/Synthesis.esp" --flag --apply
# 分析插件覆寫了哪些記錄（唯讀）；掃描可騰出名額的候選（唯讀）
python tools/esl_check.py --plugin "路徑\某插件.esp"
python tools/esl_check.py --scan --pm "D:/PM"
```
```bash
# DLL 單檔判斷（例如確認換下來的舊 DLL 是 AE 版）
python tools/audit_skse.py --dll "路徑/某.dll"
# 舊版前置補丁的失效引用：先試跑，再加 --apply；輸出寫到另一個 mod（放在原 mod 之上）
python tools/strip_refs.py --pm "D:/PM" --plugin "Modpocalypse NPCs (v3) Legacy of the Dragonborn.esp" --master LegacyoftheDragonborn.esm --out "D:/PM/mods/Pages - LOTD V6 修正"
# 看某種記錄帶了哪些子記錄（例如 Synthesis.esp 的 LAND 有沒有 VCLR）
python tools/esl_check.py --plugin "路徑/Synthesis.esp" --subrecords LAND
```
- `strip_refs --drop-missing`：刪掉「覆寫目標在非官方主插件裡不存在」的整筆記錄（對應新版主插件的補丁）：
  ```bash
  python tools/strip_refs.py --pm "D:/PM" --drop-missing --from-csv data/analysis/override_mismatch.csv --out "D:/PM/mods/Pages - 版本不符修正"
  ```
- `strip_refs --drop-unresolved-base`：刪掉「基底物件（NAME）在非官方主插件裡不存在」的放置記錄（REFR、ACHR…）。只用在未解析引用掃描表格列出的插件；可以和 `--drop-missing` 一起用：
  ```bash
  python tools/strip_refs.py --pm "D:/PM" --drop-unresolved-base --from-csv data/analysis/unresolved_refs.csv --out "D:/PM/mods/Pages - 版本不符修正"
  ```
- 生效的插件已經是 `--out` 裡的修正版時，`strip_refs` 會重新檢查並原地更新（只限單一連結的檔）；沒有要改的就回報「已修正」。
- `strip_refs` 的報告目錄參數是 `--report-dir`（`--out` 是輸出的 mod 資料夾）。
- 換補丁版本時用 `fill_plugins` **不加 `--mv`、`--nolvus`**：這樣只從 `downloads` 的壓縮檔取；加了會先從 Nolvus／M&V 的安裝連回舊版。同名的舊 BSA 要一起先搬走（`fill_plugins` 不覆寫已存在的檔）。
- 在 MO2 手動停用又重新啟用 mod 之後：`sync-order --restore-states --apply` → `prune_dependents` 試跑 → `--disable-folders --apply`（一組一起做）。
- `build_instance create --apply` 會依目標重寫 modlist／plugins，把之前的修剪全部恢復；之後的 `prune_dependents` 會列出完整名單，不是差額。判斷標準是「名字都在已接受的清單內」。
- 完整插件名額：目前 251，重建後 `DynDOLOD.esm`、`DynDOLOD.esp` 會再用掉 2 個（253/254）。其他輸出（Synthesis、FNIS、Occlusion、PG_*）一定要是輕量插件；`check_plugins` 的「輸出重建後的完整插件（預估）」超過 254 就停下來回報。
- `esl_check --flag` 只會改單一連結的檔案（重建出來的輸出），硬連結的原檔會被拒絕。
- Synthesis 的 patcher 清單：等雲端在 `progress/cloud-notes.md` 給出後才做。BodySlide 照 `docs/05` 第 2 節。

## 第 6 階段：繁中化
```bash
python -m pip install -r requirements-zh.txt
python tools/zh/fontconfig.py --pm "D:/PM" --official "D:/PM/mods/ZH - 官方繁中字串/interface/fontconfig_cn.txt" --out-mod "D:/PM/mods/ZH Overrides"
python tools/zh/fontconfig.py --pm "D:/PM" --official "D:/PM/mods/ZH - 官方繁中字串/interface/fontconfig_cn.txt" --out-mod "D:/PM/mods/ZH Overrides" --apply
python tools/zh/strings_glossary.py chs-cht --a "D:/zh-packs/本體CC" --b "D:/PM/mods/ZH - 官方繁中字串/strings" --out "D:/PM/zh-work/pins_chs_cht.tsv"
python tools/zh/opencc_convert.py "D:/PM/mods/ZH - 蘇禾 Nolvus DSD" "D:/PM/mods/ZH - 蘇禾 MV DSD" --pins "D:/PM/zh-work/pins_chs_cht.tsv"
python tools/zh/opencc_convert.py "D:/PM/mods/ZH - 蘇禾 Nolvus DSD" "D:/PM/mods/ZH - 蘇禾 MV DSD" --pins "D:/PM/zh-work/pins_chs_cht.tsv" --in-place
python tools/zh/diff_pack.py --pack "D:/zh-packs/Nolvus Other" --pm "D:/PM"
python tools/zh/diff_pack.py --pack "D:/zh-packs/Nolvus Other" --pm "D:/PM" --accept-to "D:/PM/mods/ZH - 蘇禾 Nolvus Other" --apply
python tools/zh/strings_glossary.py en-zh --a "D:/PM/zh-work/official_english/strings" --b "D:/PM/mods/ZH - 官方繁中字串/strings" --out "D:/PM/zh-work/glossary_en_zh.tsv"
python tools/zh/mcm_txt.py scan --pm "D:/PM"
python tools/zh/mcm_txt.py make-chinese --pm "D:/PM" --out-mod "D:/PM/mods/ZH Overrides"
python tools/zh/mcm_txt.py make-chinese --pm "D:/PM" --out-mod "D:/PM/mods/ZH Overrides" --apply
python tools/zh/coverage.py --pm "D:/PM" --work "D:/PM/zh-work"
python tools/zh/llm_translate.py estimate --work "D:/PM/zh-work"
# 以下兩行會花錢：先把 estimate 的金額告訴使用者，得到同意才執行
python tools/zh/llm_translate.py run --work "D:/PM/zh-work" --glossary "D:/PM/zh-work/glossary_en_zh.tsv" --limit 5 --yes
python tools/zh/llm_translate.py run --work "D:/PM/zh-work" --glossary "D:/PM/zh-work/glossary_en_zh.tsv" --yes
python tools/zh/llm_translate.py apply --work "D:/PM/zh-work" --pm "D:/PM" --out-mod "D:/PM/mods/ZH - AI 翻譯"
python tools/zh/coverage.py --pm "D:/PM" --work "D:/PM/zh-work"
```
- 報告：`zh_fontconfig.txt`、`zh_opencc.txt`、`zh_diff_pack.txt/.csv`、`zh_mcm-*.txt` + `zh_mcm.csv`、`zh_coverage.txt/.csv`、`zh_llm-*.txt`。
- 蘇禾漢化包的實際資料夾名稱依解壓結果調整。基底遊戲包的檔案清單先交給雲端判斷要保留哪些（`docs/06`）。
- `llm_translate` 需要環境變數 `ANTHROPIC_API_KEY`。

## 第 7、8 階段
- 沒有專用工具，依 `docs/07`、`docs/08` 操作。
- 新增或更新 mod 後，重跑 `check_plugins.py`、`audit_skse.py`、`zh/coverage.py`。
