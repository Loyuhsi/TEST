# 星海工坊 Unified v2 — iPhone 與 TypingMind 安裝指南

## 立即試玩（只有 iPhone，不需要電腦）
公開 HTTPS 測試連結：
https://raw.githack.com/Loyuhsi/TEST/starforge-unified-v2-ssd-typingmind/unified/index.html

如果第一次看到 External Content Notice，請按 Open the page，不需輸入帳密。進入後，六個分頁可以直接操作：銀河、恆星系、太陽系、深空、SSD、AI／同步。星圖支援拖曳、雙指縮放及點選。

**安全限制**：第三方 raw.githack.com 預覽頁已禁用私人寫入權杖的輸入與提交。它仍可瀏覽、編輯本機模擬、下載 JSON 和複製聊天摘要。要啟用遠端自動同步，必須先部署到自己信任並控制的 HTTPS 網域。

## 功能與真實性
- 銀河：HYG 衍生的 47 顆已核對真實恆星 + NASA 母恆星，以及按需載入命名星表（約 3,151 筆）。
- 恆星系：NASA 確認系外行星與其母星；缺失欄位不捏造。可加入 SIMULATED 虛構世界（Kepler 兩體近似），並另行開啟原版 SSE 高階物理工具。
- 太陽系：八大行星、地球／月球、主小行星帶、木星特洛伊群、柯伊伯帶、散射／分離天體、日球層與假設歐特雲；均註明壓縮尺度與示意動畫。
- 小天體：JPL SBDB 的 Ceres、Vesta、Pallas、Juno、Pluto、Eris 六筆核對快照，另 14 筆僅有近似半長軸，不冒用完整 JPL 軌道要素。
- 深空：13 筆星雲、星團、脈衝星、黑洞與棕矮星節點。RA/Dec 與近似距離模式，距離精度與比例有限。
- 匯入匯出：starforge.unified.v2 JSON、上一版 starforge.real_milky_way.v1 JSON，還能保留原版 SSE 的 nodes/system/starSystems JSON 參考資料，而不把模擬結果說成觀測。

## Cloudflare Worker Bridge 部署（手機瀏覽器可以操作）
完整程式在本資料夾 bridge/worker.js，設定在 wrangler.toml。當前 GitHub 預覽版並沒有已部署的 JPL 即時服務與 MCP 實際連線，因此以下為必要的啟用步驟。

1. 登入 https://dash.cloudflare.com/ → Workers & Pages → Create application → Worker → Connect GitHub。
2. 選 Loyuhsi/TEST，分支 starforge-unified-v2-ssd-typingmind；Root directory 為 unified；使用 Node 與 Wrangler 4.45+，Deploy command 選 npx wrangler deploy，Wrangler config 為此目錄的 wrangler.toml。
3. Wrangler 設定包含 STARFORGE_KV（KV namespace）和 SSD_GATE（SQLite Durable Object）。KV 若無法自動建立，先於 Dashboard 建立一個 KV namespace，將分配到的 id 加入 wrangler.toml 的 kv_namespaces。
4. 在 Worker Settings > Variables and Secrets，新建兩個彼此不同的 Secret：
   - READ_TOKEN：供 TypingMind 讀取 MCP，同時可查詢 JPL 資料。
   - WRITE_TOKEN：僅供網頁上傳星圖 JSON。
   每組建議使用 40 字元以上隨機內容，由密碼管理器產生。不要貼進公開聊天室或 GitHub，不可沿用先前已被公開的測試權杖。
5. 在 Wrangler 的 ALLOWED_ORIGINS 改成你自己控制的 HTTPS 前端網站的 origin，例如 https://my-stars.example.com；正式版請移除 raw.githack.com。
6. 部署後用瀏覽器打開 https://你的-worker.workers.dev/api/health，應看到 status:ok。此項只證明 Bridge 上線，不證明 NASA 資料源完全正常。
7. 前端放到自己的可信 HTTPS 靜態網域，四個檔案 index.html、style.css、data.js、app.js 必須保持同一個資料夾。到「AI／同步」填自己的 Worker 基址及 WRITE_TOKEN，按「立即同步」。

Cloudflare Workers 於 2026 年支援 GitHub 持續部署；SQLite Durable Object 必須使用 new_sqlite_classes 遷移。請留意免費方案與用量限制，避免意外費用。

## TypingMind 遠端 MCP 設定
在 iPhone 的 TypingMind > 插件 > MCP > Add URL 輸入：
- Server URL：https://你的-worker.workers.dev/mcp（也支援 /api/mcp）。
- Connection name：星海工坊 · Unified v2
- Custom HTTP headers：開啟
- Header Name：X-Starforge-Key
- Header Value：你的 READ_TOKEN（不是 WRITE_TOKEN）
- OAuth Client：關閉
- MCP Connector：TypingMind Cloud

成功後會列出 10 項唯讀工具：
get_latest_universe、search_stars、get_star_system、list_solar_small_bodies、get_small_body、list_deep_sky_objects、get_deep_sky_object、get_imported_sse_reference、lookup_jpl_sbdb、get_horizons_vector。

可在 TypingMind 嘗試：
「請使用 get_latest_universe 取得星圖，再列出目前恆星系的 NASA 已確認行星，並查詢 Ceres 的 JPL SBDB 原始軌道要素。」
若返回 No snapshot，表示尚未從自己的可信前端按成功「立即同步」。

## JPL SSD 限制
JPL SSD Fair Use 要求一次僅一個 API 請求，且不允許直接從網站嵌入。Bridge 使用單一 SSD_GATE Durable Object 排隊、至少 1.6 秒的請求間隔，並以 KV 對 SBDB 快取 24 小時、Horizons 快取 6 小時；瀏覽器絕不直接呼叫 JPL SSD。服務會限用單一小天體查詢和少數主要行星的 Horizons 日心狀態向量，不能當成航天導航系統。
JPL 每顆小天體各有獨立軌道曆元；軌道動畫不應解釋成某一真實日期的高精度位置。歐特雲並無直接觀測的完整天體清單，是理論分布模型。

## 資料來源／授權
- HYG / Astronexus：CC BY-SA 4.0 — https://github.com/astronexus/HYG-Database
- NASA Exoplanet Archive / PSCompPars — https://exoplanetarchive.ipac.caltech.edu/
- JPL SBDB — https://ssd-api.jpl.nasa.gov/doc/sbdb.html
- JPL Horizons — https://ssd-api.jpl.nasa.gov/doc/horizons.html
- OpenNGC：CC BY-SA 4.0 — https://github.com/mattiaverga/OpenNGC
- NASA 太陽系 / 歐特雲 — https://science.nasa.gov/solar-system/oort-cloud/

## 自我檢查
在有 Node 的環境中，可執行 npm run check 檢查 JavaScript 語法；使用 npm run deploy 發布 Bridge。公開 GitHub HTML 預覽能用於手機操作與 JSON 匯出，但它的寫入／MCP 功能不會被假裝成已部署。

**舊私人星海工坊及之前的安全 MCP 站點沒有被修改。新 Worker 需另行部署，並會使用獨立資料庫與金鑰。**
