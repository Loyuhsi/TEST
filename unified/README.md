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

## 完成及部署判定
GitHub Actions 測試流程：[v4 寫入工具與資安測試](https://github.com/Loyuhsi/TEST/actions/workflows/starforge-v4-write-tests.yml)。
通過測試僅代表程式可運作，**不代表 Cloudflare Worker 已上線**。Worker /api/health 必須顯示 status:ok、editing:true，WRITE_TOKEN 權限確認後才能使用。JPL 即時查詢仍需 SSD_GATE、JPL_CONTACT 和上游 JPL API 可用。

v4 程式碼由 Starforge 開發，SSE 原版完整應用保留 GPLv3 授權；HYG / OpenNGC 資料依 CC BY-SA 引用，其他資料依 NASA / JPL 來源標示。完整星圖非精確航太導航軟體。
