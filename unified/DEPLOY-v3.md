# 星海工坊 v3 — iPhone / Cloudflare / 完整 SSE 3.2 / JPL SSD / TypingMind

## 完成與未完成（請分清楚）
- 星海工坊 v3：已建立多樣化系外環境生成器。資料依恆星光度、光譜先驗、盤質量、金屬量、動力演化與種子改變。產生岩石／氣態／冰巨行星、月球、環、碎屑帶、特洛伊群、冰質外側帶、散射盤與遠距彗星雲，不是複製太陽系。保留 NASA 已確認行星。
- 深空 3D：可對無可靠距離天體保留真實赤經赤緯，另外產生 SIMULATED_DISTANCE 虛構徑向距離、xyz（pc）與可重現種子。不能引用為真實觀測。
- 完整 SSE 3.2：CI 會從 GPLv3 上游固定提交 f2459feb3a275ce0f7d5f8ad8115c1231eb6a9dd 建置完整物理模擬與 GM 工作台，保留原始模組；額外加入明確使用者同意的星圖回傳按鈕，不修改原版物理核心。原始碼 https://github.com/FrunkQ/star-system-generator。
- 原版 SSE 的所有進階機能要在完成 Cloudflare Pages 部署後於另一個完整工作台運作；v3 自有的快速生成器不是 SSE 的 N-body、潮汐與飛行模擬替代品。
- Cloudflare Pages/Worker：目前只備好自動部署程式。若未設定 Cloudflare 帳戶憑證，GitHub Actions 將跳過部署，不能稱為已上線。
- JPL 即時查詢：只有 Worker 正式部署、授權並配置聯絡方式後才會生效，離線 JPL 快照永遠不能冒稱即時。

## iPhone 立即試玩
https://raw.githack.com/Loyuhsi/TEST/starforge-v3-exosystems-sse-full-ssd/unified/offline.html

在 Safari 開啟；如果看到 External Content Notice，按 Open the page，不需登入，也不要在該第三方網站輸入私人金鑰。單檔版可離線顯示、生成環境、下載 JSON、複製 AI 摘要；第三方預覽已封鎖寫入金鑰及遠端同步。

## 在手機完成 Cloudflare 的一次性授權
自動工作流程：https://github.com/Loyuhsi/TEST/actions/workflows/starforge-v3-cloudflare.yml

1. 使用 Safari 登入 https://dash.cloudflare.com ，從 Workers & Pages 找到 Cloudflare Account ID，並建立具最小所需 Workers Scripts、KV、Durable Objects、Pages 部署權限的 API token。
2. 在 GitHub 手機網頁打開 Loyuhsi/TEST → Settings → Secrets and variables → Actions → New repository secret。要新增五項機密：
   - CLOUDFLARE_ACCOUNT_ID：帳戶 ID
   - CLOUDFLARE_API_TOKEN：Cloudflare 限權 token
   - STARFORGE_READ_TOKEN：隨機 40 字元以上唯讀 token
   - STARFORGE_WRITE_TOKEN：不同的隨機 40 字元以上寫入 token
   - STARFORGE_JPL_CONTACT：你替星海工坊建立的應用程式維護聯絡方式，供 JPL SSD User-Agent 使用
3. 這五組數值只能存進 GitHub 加密 Secrets，不要貼進聊天室、公開 GitHub、網址或第三方 HTML 預覽。
4. 開啟上方 GitHub Actions → Run workflow → 選擇 starforge-v3-exosystems-sse-full-ssd 分支執行。需確認所有部署工作 Success，不是 Skipped。
5. 預期兩個 Cloudflare Pages 網址：
   - https://starforge-unified-v3-loyuhsi.pages.dev/unified/
   - https://starforge-sse-full-loyuhsi.pages.dev/
   並有 Worker 名稱 starforge-unified-bridge-v3。Worker 網址與 Cloudflare 帳戶的子網域有關，務必以 Cloudflare Dashboard 或部署日誌顯示的實際網址為準。
6. Worker 的 /api/health 成功不代表 JPL 正常；仍要帶正確金鑰查 /api/ssd/body?name=Ceres，再測 MCP tools/list。

## SSE 整套工作台與使用者同意同步
從可信 Cloudflare 星海工坊開啟 SSE v3.2 全工作台，在 SSE 完成天體／太空船／GM 修改。完整工作台新增「發送星圖到星海工坊」按鈕。你必須主動點擊並確認：**回傳的原生資料可能包含 GM 私密備註與文明設定**。它會透過固定來源驗證的 postMessage 傳回開啟它的星海工坊視窗。
收到後存為 imported_sse 而不是 HYG/NASA 觀測欄位。如果該使用者另外啟用可信域名上的安全 Worker 自動同步，TypingMind 才可在下一次 MCP 呼叫時讀取。較大的 SSE 星圖要使用原版匯出／匯入。

## TypingMind 設定
iPhone TypingMind → 插件 → MCP → Add URL：
- Server URL：https://你實際Worker域名/mcp
- Custom HTTP headers：開啟
- Header Name：X-Starforge-Key
- Header Value：STARFORGE_READ_TOKEN 的值（不能是 WRITE token）
- OAuth Client：先關閉
- Connector：TypingMind Cloud

預期 13 個唯讀 MCP 工具，包含 get_latest_universe、get_star_system、get_generated_system、list_generated_systems、list_simulated_deep_positions、get_imported_sse_reference、lookup_jpl_sbdb、get_horizons_vector 等。需要先從可信星海工坊進行一次有效的 POST 快照，才能讀到新資料。

## JPL SSD 官方政策與科學界線
JPL SSD 要求一次僅一個請求、重複內容使用快取、退避處理錯誤及具有效聯絡方式的應用 User-Agent。星海工坊 Worker 透過單一 Durable Object 排隊並以 KV 暫存；手機不直連 JPL API。SBDB 的軌道要素各自有資料曆元，不能當作某個共同日期的即時位置。
- https://ssd-api.jpl.nasa.gov/doc/
- https://developers.cloudflare.com/workers/ci-cd/external-cicd/github-actions/
- https://developers.cloudflare.com/pages/framework-guides/deploy-a-svelte-kit-site/

## 安全與授權
SSE 3.2 保留 GPL-3.0-or-later，原作品及修改版的源碼存取連結與授權需提供給使用者。HYG CC BY-SA、OpenNGC CC BY-SA、NASA/JPL 資料各保留來源與真實性標記。請輪替以前曾在聊天中公開過的測試權杖。本分支沒有修改你早期的私人 ChatGPT Sites 或既有 MCP 服務。
