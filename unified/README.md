# 星海工坊 Unified v3 — iPhone / SSE 3.2 / JPL SSD / TypingMind

**[直接在 iPhone Safari 開啟整合星圖（單檔）](https://raw.githack.com/Loyuhsi/TEST/starforge-v3-exosystems-sse-full-ssd/unified/offline.html)**

[多檔版本](https://raw.githack.com/Loyuhsi/TEST/starforge-v3-exosystems-sse-full-ssd/unified/index.html) · [iPhone Cloudflare 部署與 TypingMind 指南](./DEPLOY-v3.md) · [SSE v3.2 上游原始碼](https://github.com/FrunkQ/star-system-generator)

## v3 新功能

1. **非複製型系外環境**：從實際恆星光度、光譜、NASA 已確認系外行星及可修改的原行星盤/金屬量/動力參數出發，根據種子生成行星、衛星、環、碎屑帶、特洛伊候選群、類柯伊伯帶、散射盤與遠距彗星雲。輸出記錄物理估算方式、不確定性、SIMULATED 來源及種子。
2. **未知距離天體的虛構 3D**：保留 OpenNGC 真實赤經、赤緯；為缺距離的物件按類型和可重現種子抽樣徑向距離，導出 xyz(pc)。使用獨立欄位 SIMULATED_DISTANCE 與 FICTIONAL_SCENARIO，不改動原始觀測欄位。
3. **完整 SSE 工作台建置**：GitHub Actions 自原作者固定提交的 GPLv3 SSE v3.2.0 完整編譯含 GM、Newton、飛行、文明與 3D 系統；只改 Cloudflare adapter，附加使用者點擊確認才能回傳的 SSE 原生星圖通道。原版完整工作台與星海工坊快速近似引擎**不是相同物理模型**。
4. **TypingMind MCP**：Cloudflare Worker 原始碼提供 13 項唯讀 MCP 工具、快照與資源類型查詢、原生 SSE JSON 保留、虛構深空座標和生成系統查詢。不同 READ / WRITE 權杖，JPL SSD/Horizons 由後端序列化並快取。
5. **保留 v2**：真實銀河、太陽系、深空、SSD、AI／同步六種模式和原始 v1.2 太陽系地月頁面。

## 現有的部署限制

公開的 raw.githack 測試網站可操作但**已禁用私人寫入權杖**；它不是你的私人 Cloudflare 網域。Cloudflare Pages / Worker / 完整 SSE 正式部署 workflow 位於：

[GitHub Actions：Deploy Starforge v3 Cloudflare](https://github.com/Loyuhsi/TEST/actions/workflows/starforge-v3-cloudflare.yml)

**如果五項 Cloudflare 機密尚未在 GitHub Actions Secrets 設定，workflow 會成功執行憑證檢查並跳過真正部署；這不是 Cloudflare 上線成功。**

請依 [繁體中文手機部署說明](./DEPLOY-v3.md) 安全設定 CLOUDFLARE_ACCOUNT_ID、CLOUDFLARE_API_TOKEN、STARFORGE_READ_TOKEN、STARFORGE_WRITE_TOKEN、STARFORGE_JPL_CONTACT。不要在第三方測試頁或聊天公開私密權杖。

## 可驗證測試

- [GitHub Actions：完整 SSE 3.2 與 v3 回歸測試](https://github.com/Loyuhsi/TEST/actions/workflows/starforge-v3-build.yml)
- Node tests：tests/smoke.mjs、tests/exo.mjs、tests/browser.mjs
- Workflow 在 Cloudflare 授權到位之前只能驗證編譯結果、MCP mock 與近似模型，不能宣稱已完成實機 iPhone/TypingMind/JPL live 的端到端測試。

### 資料授權與科學聲明
HYG CC BY-SA 4.0、OpenNGC CC BY-SA 4.0，NASA Exoplanet Archive、JPL SSD 及 SSE GPLv3 來源需依各自授權保留歸屬。系外小天體群與遠距彗星雲僅為**物理啟發的程序式模型**，不是已觀測的帶狀天體，更不是完整 N-body 模擬；動畫位置也不代表即時 JPL 星曆。
