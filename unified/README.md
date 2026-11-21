# 星海工坊 Unified Atlas v2

合併先前的 v1.3–v1.6 需求的 iPhone 優先星海工坊：真實銀河、恆星系、太陽系小天體、JPL SSD，以及非恆星深空天體。前端採 Canvas 2D，支援觸控與小型裝置。

## 立即使用
- **[統一星圖（推薦）](https://raw.githack.com/Loyuhsi/TEST/starforge-unified-v2-ssd-typingmind/unified/index.html)**
- **[單一 HTML 備援／離線版](https://raw.githack.com/Loyuhsi/TEST/starforge-unified-v2-ssd-typingmind/unified/offline.html)**
- [完整 iPhone + TypingMind 部署指南](https://github.com/Loyuhsi/TEST/blob/starforge-unified-v2-ssd-typingmind/unified/DEPLOY.md)

首次可能出現第三方 External Content Notice，點選 Open the page。請勿在第三方 HTML 預覽輸入任何金鑰；本版對該預覽來源的寫入金鑰控制已禁用。

## 六個模式
| 模式 | 已交付內容 | 分類 |
|---|---|---|
| 銀河 | HYG 47 顆離線恆星，載入 3,151 顆命名恆星；NASA 系外行星母星 | 觀測／衍生資料 |
| 恆星系 | 任意已載入母恆星、NASA 確認行星、虛構行星補完 | 真實和模擬分開 |
| 太陽系 | 行星、地月、主帶、特洛伊群、柯伊伯帶、歐特雲模型 | 參考值 + 示意 |
| 深空 | 13 筆星團／星雲／SNR／脈衝星／棕矮星／黑洞樣本 | 觀測參考與近似值 |
| SSD | 6 筆 JPL SBDB 核對快照及 14 筆代表性近似半長軸 | 每筆有來源／精度 |
| AI 同步 | JSON 匯出／匯入、聊天摘要、可信網域的 HTTPS Bridge 同步 | 需部署 Bridge |

## TypingMind MCP
- Worker 程式：unified/bridge/worker.js
- 設定：unified/wrangler.toml
- 10 個只讀 MCP 工具，支援最新星圖、恆星系、太陽系小天體、深空及 JPL SSD/Horizons；用 Cloudflare Workers KV 與單一 Durable Object 節流。
- **重要**：MCP Worker 原始碼已完成並測試，並沒有在此對話直接部署到你的 Cloudflare 帳戶。需依 DEPLOY.md 建立兩個私密密鑰（READ_TOKEN、WRITE_TOKEN）並自行部署才會生效。

## 維持舊版功能
此 GitHub 分支亦保留原版 v1.2 的 solar-system、real-milky-way 頁面，且增加新整合版入口。原本的私人星海工坊網站及之前的 MCP 服務並未被修改。

## 科學性限制
示意軌道及帶狀區域只供視覺化，**不是** JPL Horizons 的當日真實曆表。歐特雲沒有已觀測的完整天體分布圖；星雲和星團的距離及 RA/Dec 不是高精度 3D 實測體積。AI 與使用者應嚴格區分觀測、近似和創作資料。

來源：NASA Exoplanet Archive、JPL SSD、HYG、NASA Hubble/Chandra、OpenNGC；適用授權與引用資訊詳見 DEPLOY.md。
