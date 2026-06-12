# PLAN.md — Theta Desk 作戰交接文件

> 給平行協作的 AI agent(Agent B)。讀完這份你就有全部 context。
> 主 agent(Claude/Fable,Agent A)擁有 `services/pipeline/`;**你不要改那個目錄**。
> 時間極度有限(黑客松剩 <2 小時),只做你的任務清單,不要重構、不要美化既有代碼。

## 1. 專案一句話

**Theta Desk** = 自治選擇權收益研究台:每日掃描美股選擇權鏈 → ClickHouse 量化篩選
(年化權利金、IV 百分位、流動性、財報迴避)→ Claude 寫附引用風險簡報 → 發佈到
cited.md 掛 $0.01 x402 付費牆 → 交易機器人 Wheeler 付費購買並模擬下單。
參賽:Context Engineering Challenge(評分:Idea/Tech/Tool Use/Demo/Autonomy 各 20%)。

## 2. 目前狀態(全部已驗證可跑)

| 元件 | 狀態 | 證據 |
|---|---|---|
| ClickHouse Cloud | ✅ 真資料 | 10 檔股票、4,015 合約、2,510 歷史價 |
| 篩選引擎 | ✅ | `python services/pipeline/screener.py` 直接跑 |
| Claude 分析 | ✅ | 5 篇簡報/run,有 fallback 文案保險絲 |
| Senso → cited.md | ✅ 已上線 | https://cited.md/article/47e2fb3c-7ff0-4f1c-a3a2-c40673ee6e33 |
| x402 付費牆 | ✅ | `GET /briefs/today` 無 header 回 402;`POST /consumer/buy` 模擬購買 |
| 完整 API | ✅ 本地 | `uvicorn api:app --port 8000`(在 services/pipeline,用 ../../.venv)|
| 儀表板 (Next.js+OpenUI) | ✅ build 過 | `apps/dashboard`,mock 優先設計,`npm run dev` 零依賴可跑 |
| Render 服務 | ✅ 已建立,**等 push 觸發部署** | 見下方 |
| Senso 知識庫/GEO | ✅ 完成 | 12 docs、40 prompts、3+2 citeables live |

Render 服務(已用 API 建好,free 方案):
- API:`srv-d8m6nmk8aovs73dt603g` → https://thetadesk-api-jpll.onrender.com
- 儀表板:`srv-d8m6nvrsq97s73a3m8a0` → https://thetadesk-agent.onrender.com
- 每日排程:API 內建 scheduler 執行緒(平日 13:45 UTC),不需 cron 服務。

Keys 都在根目錄 `.env`(已 gitignore,**絕不能 commit**):ClickHouse、Senso、
Anthropic、Render(`RENDER_API_KEY`)、Pioneer。

## 3. 鐵律(不可違反)

1. **絕不 commit/印出任何 key。**
2. **不改 `services/pipeline/` 和 `contracts/`**(Agent A 領地)。你的領地:
   `apps/dashboard/`、`docs/`、`README.md`、git/Render 操作。
3. Demo 不能報錯:儀表板已有 mock fallback(壞 API 自動切 SIM 模式),不要破壞它。
4. 改完必跑 `npm run build`(在 apps/dashboard)再 commit。

## 4. 你的任務清單(按優先序)

### T1 — push + 盯 Render 部署(最急)
```
git push origin main
```
然後用 Render API 盯兩個服務的 deploy(key 在 .env 的 RENDER_API_KEY):
```
GET https://api.render.com/v1/services/<srv-id>/deploys?limit=1
Authorization: Bearer $RENDER_API_KEY
```
- 若 **dashboard** build 失敗:修 `apps/dashboard` 內的問題(你的領地)。
- 若 **API** build 失敗:不要修代碼,把錯誤訊息完整記到 `docs/DEPLOY_ISSUES.md`
  並告訴使用者轉交 Agent A。
- 部署成功後驗證:
  - `https://thetadesk-api-jpll.onrender.com/healthz` 回 `{"ok":true,...}`
  - 儀表板開得起來、`POST .../runs?mode=replay` 後動畫會跑完四階段
  - 注意 free 方案冷啟動約 1 分鐘,demo 前要先「暖機」(先打一次 healthz)

### T2 — `docs/DEMO_SCRIPT.md`(3 分鐘逐秒腳本)
節拍(已定,把它寫成可照唸的講稿,中英都可):
1. 0:00 Hook:「選擇權研究員每天 2 小時的功課,這個 agent 90 秒做完,只賣 1 美分——而且買家可以是另一個機器人。」
2. 0:20 按 Run Daily Scan(replay 模式)→ 四階段管線動畫(Ingest→Screen→Analyze→Publish)
3. 1:20 點開 cited.md 真實連結展示已發佈簡報(附引用、Powered by Senso)
4. 2:00 按 Wake Wheeler → 402 → 付 $0.01 → 解鎖 → 模擬掛單(demo 高潮)
5. 2:40 收尾:5+ 贊助商工具各司其職、Render 上全自治每日循環、「這就是 agent 經濟」
務必含:備援方案(網路掛了→本地 mock 模式照演)、每一步點哪裡的操作註記。

### T3 — README.md 升級(評審第一眼)
加:架構圖(ASCII 即可)、3 個 live 連結(cited.md 文章、API healthz、儀表板)、
贊助商使用表(每家「真的做了什麼」一句話)、60 秒 quickstart、
disclaimer。語氣:量化、自信、不吹牛。

### T4 — `docs/DEVPOST.md`(提交文案草稿)
Devpost 欄位:Inspiration / What it does / How we built it / Challenges /
Accomplishments / What we learned / What's next。每段 3-5 句,
強調:真資料、全自治、agent-pays-agent 閉環、5+ 贊助商深度整合。

### T5(行有餘力)— 儀表板擦亮
1920×1080 投影檢查、字體大小、TOP PICK 效果、sponsor footer 是否齊全。

## 5. Demo 數字小抄(來自真實 run,寫進腳本用)

- Universe:AAPL MSFT NVDA AMD TSLA GOOGL AMZN META PLTR SOFI(10 檔)
- Top pick(2026-06-12 snapshot):AMD 2026-06-26 495P,bid $20.90,
  年化權利金 110.1%,IV 百分位 72,score 80.5
- Wheeler 購買 log:402 → pay $0.01 USDC → unlock → queue SELL 1x AMD 495P
- 對比:傳統篩選器訂閱 $30–150/月 vs Theta Desk $0.01/份(≈$0.21/月)
