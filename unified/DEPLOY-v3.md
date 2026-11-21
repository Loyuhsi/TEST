# Starforge Unified v4 正式部署

正式來源固定為 `Loyuhsi/TEST` 的 `starforge-v3-exosystems-sse-full-ssd` 分支。

## 現有資源

- 手機 Pages：`starforge-unified-v3-loyuhsi`，https://starforge-unified-v3-loyuhsi.pages.dev/unified/
- 完整 SSE Pages：`starforge-sse-full-loyuhsi`，https://starforge-sse-full-loyuhsi.pages.dev/
- Worker：`starforge-unified-bridge-v3`，https://starforge-unified-bridge-v3.loyuhsi930821.workers.dev
- KV：`STARFORGE_KV`；使用 `wrangler.toml` 中既有 Namespace ID，不建立替代資源。
- `SSD_GATE` / `SSDGate` 及 `EDIT_GATE` / `EditGate`：保留 v1 / v2 SQLite migrations。

## 建置與部署

先執行 `cd unified && npm run check`。Worker 的 Cloudflare Git 建置 root directory 設為 `unified`，build command 設為 `npm run check`，deploy command 設為 `npx wrangler deploy`。

手機 Pages 的 root directory 為儲存庫根目錄；build command 為 `npm --prefix unified run check && node unified/scripts/build-pages.mjs`，輸出 `site-dist`。此白名單只發布前端資產，排除 bridge、測試、設定與本機檔案，並由目前的原始碼重新產生單檔版。

完整 SSE 的 root directory 為 `unified`；build command 為 `bash scripts/build-sse-cloudflare.sh`，輸出 `sse-upstream/.svelte-kit/cloudflare`。上游固定於 `f2459feb3a275ce0f7d5f8ad8115c1231eb6a9dd`，只切換 Cloudflare adapter 及加入經確認的星圖回傳按鈕。公開 `/COPYING-GPL-3.0` 與 `/starforge-source.json` 提供授權及對應來源；不修改物理核心。

## Secret 與授權

在 Cloudflare Worker 設定 `READ_TOKEN`、`WRITE_TOKEN`、`ADMIN_TOKEN`、`JPL_CONTACT`。三種權杖須彼此不同，使用密碼學安全亂數，不能寫入 GitHub、聊天、網址、公開日誌或前端資產。JPL_CONTACT 可使用專案的維護聯絡網址。

Wrangler OAuth 可用於直接部署、KV、Durable Objects 及 Pages；Workers Builds 設定 API 另需 user-scoped token 的 `Workers Builds Configuration:Edit`。若 OAuth 對 Builds API 回傳 403，可由已登入的 Cloudflare Dashboard 修正既有 Worker 的 Git 設定，不必在聊天分享 Token。

GitHub Actions 一律先測試。選用的 Actions 部署僅需 `CLOUDFLARE_API_TOKEN` 與 `CLOUDFLARE_ACCOUNT_ID`；Starforge 執行期 Secret 由 Cloudflare 管理並保留，不複製到 GitHub。未提供 Actions 憑證時，部署工作會明確標示 skipped；Cloudflare Git 自動部署為另一條獨立流程。

## 驗證上線

`/api/health` 應有 `status:ok`、`kv:true`、`editing:true`、`ssd:true` 及四種 Secret readiness。MCP URL 為 `/mcp`，驗證 Header 為 `X-Starforge-Key`，READ / WRITE / ADMIN 分別有 16 / 20 / 23 項工具。設定方式見 [TYPINGMIND-v4.md](./TYPINGMIND-v4.md)。

正式驗證須包含 MCP 寫入虛構資料後由手機讀回、HTTP 409 拒絕舊版本上傳、觀測目錄前後雜湊相同、Ceres SBDB 及有效日期的 Horizons 查詢、SSE 原生星圖回傳。沒有使用者明確批准，不執行正式刪除或還原測試。

JPL 回傳 `starforge_jpl` 來源、擷取時間與快取狀態；SBDB 軌道曆元與 Horizons 查詢時刻分別解讀。Horizons 為 TDB 時間、J2000 黃道框架、太陽系質心、AU-D 單位。星圖示意軌道與本工具不供導航。
