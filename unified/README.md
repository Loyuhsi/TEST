# 星海工坊 Unified v4 — TypingMind 雙向 AI 控制

## iPhone 星圖
- [Cloudflare Pages 正式網站](https://starforge-unified-v3-loyuhsi.pages.dev/unified/)（GitHub v3 生產分支合併部署後才會呈現 v4）
- [v4 單檔安全預覽](https://raw.githack.com/Loyuhsi/TEST/starforge-v4-typingmind-bidirectional/unified/offline.html)（第三方預覽禁止輸入私人金鑰）
- [iPhone TypingMind v4 操作與 Cloudflare Secret 設定](./TYPINGMIND-v4.md)
- [原版完整 SSE 3.2 物理工作台](https://starforge-sse-full-loyuhsi.pages.dev/)

## 雙向 AI 工具
- READ（16 工具）：查詢真實恆星、NASA 確認行星、JPL 小天體、虛構世界、編輯版本與歷史紀錄。
- WRITE（20 工具）：READ + 建立虛構恆星/恆星系/行星/衛星/環/小天體帶/文明/太空基地、修改虛構參數、依真實星表重新生成多元系外環境、為無真實距離天體建立虛構 3D XYZ。
- ADMIN（23 工具）：WRITE + 管理員限時確認的刪除與版本還原。
- NASA／HYG／JPL 觀測資料不可經 MCP 覆寫。AI 自訂內容單獨使用 user: ID、SIMULATED／SIMULATED_DISTANCE 標記。
- 版本鎖定：每次寫入必須提供 get_edit_state 取得的 expected_revision；Cloudflare SQLite EditGate Durable Object 原子更新，保留近期版本紀錄，避免多裝置互相覆蓋。

## 基礎技術
- Cloudflare Worker：unified/bridge/worker.js
- Writable overlay：unified/bridge/edit-engine.js
- 多元系外環境生成器：unified/exo-engine.js
- 手機星圖：unified/index.html、app.js、style.css、data.js、offline.html
- Worker 綁定：STARFORGE_KV、SSD_GATE（原 JPL）、EDIT_GATE（新增虛構資料編輯）
- Secret（均不可寫入 GitHub）：READ_TOKEN、WRITE_TOKEN、ADMIN_TOKEN（可選）、JPL_CONTACT

## v4.0.1 同步與正式部署
- 正式分支固定為 `starforge-v3-exosystems-sse-full-ssd`。Worker 專案根目錄為 `unified`，先執行 `npm run check`，再執行 `npx wrangler deploy`。
- `wrangler.toml` 明確綁定既有帳戶與 KV Namespace；保留 SSDGate 的 v1、EditGate 的 v2 SQLite migrations，不能重新建立或刪除既有 namespace。
- 手機上傳攜帶 `expected_revision`（AI 編輯）及 `expected_snapshot_revision`（基礎星圖）。兩者在 EditGate 中檢查；衝突回傳 HTTP 409。DO 為即時讀取的權威來源，KV 保存星圖鏡像，避免 KV 的最終一致性回傳舊版本。
- 既有觀測紀錄不能被上傳修改或移除；可加入新目錄紀錄。讀取 AI 修改後，伺服器端的虛構 overlay 不會被複製回基礎星圖，避免日後還原時復活舊資料。
- 虛構恆星與恆星系可作為行星、衛星、環及文明的母星；虛構恆星生成環境使用 `SIMULATED_STAR_WITH_SIMULATED_ENVIRONMENT`，不冒充觀測星表。
- SSE 回傳同時檢查固定來源及由本頁開啟的視窗；使用者仍須在 SSE 確認後才會傳送。
- JPL 查詢在單一 SSDGate 中檢查 KV 快取、去除重複請求、序列化並保存請求時間，間隔至少 1600 ms。回傳 `starforge_jpl` 擷取時間、來源 URL 與 HIT/MISS；Horizons 明確標記 TDB、J2000 黃道框架與太陽系質心。
- 手機 Pages 建置命令：`npm --prefix unified run check && node unified/scripts/build-pages.mjs`，輸出 `site-dist`，只包含公開前端資產。

## 完成及部署判定
GitHub Actions 測試流程：[v4 寫入工具與資安測試](https://github.com/Loyuhsi/TEST/actions/workflows/starforge-v4-write-tests.yml)。
通過測試僅代表程式可運作，**不代表 Cloudflare Worker 已上線**。Worker /api/health 必須顯示 status:ok、editing:true，WRITE_TOKEN 權限確認後才能使用。JPL 即時查詢仍需 SSD_GATE、JPL_CONTACT 和上游 JPL API 可用。

v4 程式碼由 Starforge 開發，SSE 原版完整應用保留 GPLv3 授權；HYG / OpenNGC 資料依 CC BY-SA 引用，其他資料依 NASA / JPL 來源標示。完整星圖非精確航太導航軟體。
