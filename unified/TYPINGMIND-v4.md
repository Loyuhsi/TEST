# 星海工坊 v4 · TypingMind 雙向 MCP 與 iPhone 同步

## 版本狀態
正式分支為 `starforge-v3-exosystems-sse-full-ssd`，版本 v4.0.1。GitHub Actions 測試成功並不代表 Cloudflare Worker 已上線；正式服務須健康檢查 editing:true，且 EDIT_GATE、STARFORGE_KV、SSD_GATE 與必要 Secret 就緒後才可使用。SSE 原版 3.2 物理工作台與 JPL 查詢功能仍保留。

## READ / WRITE / ADMIN 權限

| 類型 | 預期工具 | Cloudflare Secret | 操作 |
|---|---:|---|---|
| READ | 16 | READ_TOKEN | 檢索天體、星表、AI 自訂物件與歷史 |
| WRITE | 20 | WRITE_TOKEN | 全部唯讀加上建立、修改、生成虛構星系與深空座標 |
| ADMIN | 23 | ADMIN_TOKEN | 全部寫入，加上經確認的刪除與版本回復 |

AI MCP 不修改 HYG、NASA 或 JPL 真實觀測欄位。自訂物件 ID 以 user: 開頭，origin = SIMULATED，虛構徑向位置來源為 SIMULATED_DISTANCE。真實觀測資料保留原始來源。

## Cloudflare Worker：設定 Secret

在 Cloudflare Dashboard → Workers & Pages → starforge-unified-bridge-v3 → Settings → Variables and Secrets → Add，選 Secret。

需要互不相同的高強度金鑰（建議 40 字元以上）：
1. READ_TOKEN：TypingMind 唯讀連接使用
2. WRITE_TOKEN：TypingMind 寫入連接及可信手機網頁同步使用
3. ADMIN_TOKEN：管理員刪除或版本還原使用，可選；日常不建議啟用
4. JPL_CONTACT：維護聯絡信箱，用於 JPL 請求識別，不是 NASA API Key

不要在 GitHub 公開檔案、聊天、未受信任的瀏覽器或網址參數放入任何金鑰。正式網站可以在運作時輸入 WRITE_TOKEN，但不應儲存在程式碼內。

Worker wrangler.toml 必須包含 STARFORGE_KV（星圖快照）、SSD_GATE（JPL 節流）、EDIT_GATE（新增的 SQLite Durable Object）以及 v1/v2 遷移。

## TypingMind 手機設定
在 TypingMind → Plugins → MCP → Add URL 設定以下兩條獨立連接；如客戶端不允許重複 URL，改為需要寫入時切換驗證金鑰。

A. READ（日常推薦）
- MCP URL：https://starforge-unified-bridge-v3.loyuhsi930821.workers.dev/mcp
- Custom HTTP header Name：X-Starforge-Key
- Header Value：你的 READ_TOKEN
- OAuth Client：關閉
- 選 16 項唯讀工具

B. WRITE（需要創建或編輯虛構世界）
- 同一 MCP URL
- Header Name：X-Starforge-Key
- Header Value：你的 WRITE_TOKEN
- 可使用 20 項工具（含 16 項唯讀）

C. ADMIN（可選，勿在一般聊天啟用）
- 同一 URL，Header Value 設為 ADMIN_TOKEN
- 23 項工具
- 刪除需先使用 prepare_destructive_change 取得有效 2 分鐘確認碼，再使用 delete_simulated_object 與精確 DELETE user:<id> 確認文字。版本還原也需 prepare_destructive_change，並提供 RESTORE <revision> 確認文字。
- 管理員工具雖有二步驟確認，仍應先由使用者明確批准刪除。

## 從手機實際雙向同步
1. 在可信 Cloudflare Pages 正式網站開啟 https://starforge-unified-v3-loyuhsi.pages.dev/unified/，不要在 raw.githack 預覽頁輸入金鑰。
2. 「AI／同步」輸入 Worker 基址與 WRITE_TOKEN，先按測試 Bridge。
3. 按「上傳本地星圖」，讓 Worker 知道初始 HYG／NASA 星表。
4. 在 TypingMind WRITE 模式先執行 get_edit_state，取得 expected_revision，再呼叫 create_simulated_object、update_simulated_object、generate_system_environment 或 create_fictional_deep_position。
5. 回到手機「AI／同步」按「讀取 TypingMind 的修改」，再到恆星系或深空頁查看 AI 虛構物件。
6. 欲保留資料，可匯出完整版 JSON；所有虛構資料均獨立標記，不會偷偷替換觀測資料。

### AI 對話範例
- 先取得最新編輯版本，再為 Proxima Centauri（ID hyg:70666）建立一顆虛構岩石行星，a=0.12 AU，e=0.04，質量 1.3 地球質量；完成後回報 user: ID。
- 請用 TRAPPIST-1 的觀測資料與種子 story-A13 建立多樣化模擬環境。保留 NASA 已確認行星，不要複製太陽系配置。
- 僅對沒有可靠距離的目錄天體生成虛構 3D XYZ；保留 RA／Dec 並標記 SIMULATED_DISTANCE。
- 查詢前先用 get_edit_state，所有寫入都帶 expected_revision。

## 防覆寫與還原
每次寫入需提供 expected_revision。兩個裝置同時編輯時，較舊版本會被拒絕並回報最新 revision，而不會默默覆蓋資料。EDIT_GATE 保存近期歷史，管理員可在確認後還原有限的近期編輯狀態。還原只影響虛構資料層，不回滾 NASA、HYG、JPL 觀測紀錄。

手機上傳另帶 `expected_snapshot_revision`，由伺服器同時檢查星圖版本及 AI revision。若雲端已有星圖，新裝置須先「讀取 TypingMind 的修改」再上傳。HTTP 409 表示版本衝突，應重新讀取後再操作；不會自行重試覆蓋。既有觀測紀錄不能透過上傳改寫或移除。

建立新恆星時可使用 `kind:star` 或 `star_system`，並在 attributes 指定 `mass_solar`、`luminosity_solar`、`spectral_class`。指定 `ra_deg`、`dec_deg`、`distance_ly` 或 XYZ（pc）即可在銀河圖定位；這些座標仍標記為虛構。建立行星時將新 `user:` ID 作為 `host_star_id`。衛星、環與基地可用 `parent_id` 指向同一恆星系中的虛構行星。

大型 SSE 星圖可透過 `get_imported_sse_reference` 逐層讀取原生資料：先查摘要取得各系統的 `path`，再用例如 `path:["systems","0"]`、`include_raw:true` 讀取；陣列另支援 `offset` / `limit` 分頁。單次原生資料超過 150 KB 時，依回傳欄位名稱選取更小的路徑，完整原始星圖仍保存在 Worker 中。

## 常見錯誤
- 401：金鑰錯誤
- 404：Worker 未成功部署或 URL 不正確
- editing:false：缺少 EDIT_GATE 綁定或 migration 未完成
- No baseline star catalogue：請先在可信手機網站上傳第一份星圖
- Revision conflict：重新執行 get_edit_state 後再提交
- JPL 即時查詢仍需 SSD_GATE、JPL_CONTACT 和官方服務可用，MCP 工具清單出現不代表 JPL 已連線

原始碼：https://github.com/Loyuhsi/TEST/tree/starforge-v3-exosystems-sse-full-ssd/unified
本功能不取代 SSE 原版 GPLv3 物理核心，SSE 程式仍須遵守其原有授權。
