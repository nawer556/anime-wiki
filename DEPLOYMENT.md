## 使用訪客申請與管理者審核（免費）

請先依 [APPROVAL_SETUP.md](APPROVAL_SETUP.md) 設定 GitHub Issues、`docs/assets/repository-config.js`、GitHub Pages 的 **GitHub Actions** 部署方式。訪客不需後端或 API Key；只有你在 Issue 加上 `approved-ingest` 標籤，才會執行免費來源驗證、Wiki 入庫與簡報部署。

---

# Anime Wiki 公開網站部署指南（先免費，確認後再開 AI）

> 本版已建立前端、Cloudflare Worker 請求佇列、GitHub Actions 自動 Ingest / Lint / HTML 重建流程。**交付時並未替你連接 GitHub、Cloudflare 或 OpenAI 帳號，也未呼叫付費 API。** 你必須用自己的帳號完成以下部署；目前**沒有現成公開網址**。

## AniList 故障時自動備援 Kitsu（2026-11-23）

搜尋作品名稱時，如果 AniList 回傳 HTTP 500／403／429 或發生逾時，系統會自動改用 Kitsu 免費公開資料 API；只有已查證的 Wiki 頁面才會用於教學簡報。詳見 `FREE_API_README.md`。

## 免費 AniList API 擴充（2026-11-20）

- `docs/search.html` 透過 `docs/assets/anilist-api.js` 以 GraphQL POST 查詢公開的 `https://graphql.anilist.co`，**不需要 AniList API Key 或 OpenAI API 費用**。
- Wiki 已收錄作品與 AniList 即時查詢顯示於不同區塊；AniList 只是外部資料參考，**不代表 Wiki 已經查證、Ingest 或更新簡報**。
- 可直接用 GitHub Pages 分享網址（`/search.html`），不需要 Cloudflare Worker；原來的 Worker 是**另外可選的管理員 AI 擴充機制**，預設關閉。
- 支援日文、羅馬拼音、英文名稱以及少量繁體中文常見譯名對照；中文全名搜尋可能因 AniList 資料索引限制而查無結果。
- 請求有兩秒最短間隔及十分鐘本機記憶體快取，不會大量抓取或下載整個 AniList。API 回傳 429／403／網路錯誤時，網站會顯示錯誤但保留 Wiki 搜尋。
- 本站不是 AniList 官方服務。非商業教育用途請遵循 [AniList API 使用條款](https://docs.anilist.co/guide/terms-of-use) 與 [Rate Limiting](https://docs.anilist.co/guide/rate-limiting)，**不要用 API 作為備份或大量資料儲存服務，也不要未經驗證就把 AniList 資料寫入 Wiki**。

## 一、免費：本機看到別人會看到的網站

在 VS Code 開啟專案根目錄，輸入：

```powershell
python -m http.server 8000 --directory docs
```

用 Chrome / Edge 開啟：

- `http://localhost:8000/search.html` —— 公開搜尋動漫介面
- `http://localhost:8000/index.html` —— 10 張 Wiki 教學簡報

不用 API Key、不用 Node.js，也不會產生 OpenAI API 費用。請不要直接雙擊 `search.html` 以 `file://` 開啟，因為瀏覽器通常不允許從 `file://` 讀取 JSON 檔。

## 二、免費：先公開 GitHub Pages

1. 登入 GitHub，建立新的 **Public** 儲存庫，例如 `Anime-Wiki`（不需要另外建立 README）。
2. 在 VS Code 終端機進入專案根目錄。若不是 Git 專案，執行：

   ```powershell
   git init
   git add .
   git commit -m "Publish Anime Wiki search website"
   git branch -M main
   git remote add origin https://github.com/你的帳號/Anime-Wiki.git
   git push -u origin main
   ```

   如果已有 Git 歷史或 `origin`，請先使用 `git remote -v` 確認，不要重複執行 `git remote add`；GitHub 使用者名稱必須換成你自己的。

3. GitHub 儲存庫 → **Settings → Pages → Build and deployment → Source → GitHub Actions**。
4. 檢查 **Actions → Publish Anime Wiki website** 是否成功。GitHub Pages 公開網址通常像：
   - 搜尋：`https://你的帳號.github.io/Anime-Wiki/search.html`
   - 簡報：`https://你的帳號.github.io/Anime-Wiki/`
5. 在此階段，其他人已能**免費查詢 Wiki 現有作品和 AniList 外部作品**，但「查無結果自動新增至 Wiki／更新簡報」尚未開啟。

註：請勿在公開儲存庫提交真實 API Key、Cloudflare Token 或 GitHub PAT。

## 三、想啟用 AI 時才做：Cloudflare Worker

> 這個階段**可能產生 OpenAI API 費用**。不需要為了免費的 Wiki 網站預先做這一步。

1. 建立 Cloudflare 帳號；電腦需 Node.js（建議當前 LTS）和 npm。
2. 在 VS Code 終端機：

   ```powershell
   cd backend
   npm install
   npx wrangler login
   npx wrangler kv namespace create REQUEST_KV
   ```

3. 從指令輸出取得 KV namespace ID，填入 `backend/wrangler.jsonc` 的 `REPLACE_WITH_YOUR_KV_NAMESPACE_ID`。
4. 修改 `backend/wrangler.jsonc` 中的公開變數：
   - `SITE_ORIGIN` = `https://你的帳號.github.io`（**只有來源，不含 `/Anime-Wiki/` 路徑**）
   - `GITHUB_OWNER` = 你的 GitHub 帳號
   - `GITHUB_REPO` = 你的儲存庫名稱
   - `DISPATCH_ENABLED` **先保留 `false`**
   - 每日總上限建議 3，每個 IP 建議 2。
5. 在 GitHub 建立 Fine-grained PAT，**只限你的 Anime-Wiki 儲存庫**，`Contents` 權限為 Write，設定期限。這個 token 只讓 Cloudflare Worker 觸發 GitHub `repository_dispatch`，不是讓訪客直接操作 GitHub。
6. 在 `backend/` 下執行以下指令，依序於終端機輸入 secret 值：

   ```powershell
   npx wrangler secret put GITHUB_DISPATCH_TOKEN
   npx wrangler secret put RATE_LIMIT_SALT
   npx wrangler deploy
   ```

   `RATE_LIMIT_SALT` 請使用自行產生的長隨機字串；不應放入程式庫。
7. Wrangler 部署後記下 `https://...workers.dev`，將它寫入根目錄 `docs/assets/backend-config.js`：

   ```js
   window.ANIME_API_BASE = 'https://你的-worker.workers.dev';
   ```

   只填公開的 Worker 網址。**切勿在前端設定任何 API Key 或 PAT。** 修改後提交與推送，讓 GitHub Pages 重新發布。

## 四、真正開啟 AI：OpenAI API + GitHub Actions

1. 到 OpenAI API 平台建立**獨立的專案金鑰**，考慮最小預付額度、關閉自動儲值、設定預算警示或支出限制。ChatGPT Plus 不包含 API 用量。
2. GitHub 儲存庫 → Settings → Secrets and variables → Actions：
   - `Secrets` → 新增 `OPENAI_API_KEY`（只放 GitHub Secret）。
   - `Variables` → 新增 `AUTO_INGEST_ENABLED` = `true`。
   - 可以新增 `OPENAI_MODEL` = `gpt-5-mini`，但請先確認所選模型在你的 API 帳戶支援 Responses `web_search`，且有足夠額度。
3. 在 `backend/wrangler.jsonc` 修改 `DISPATCH_ENABLED` 為 `true`，執行 `npx wrangler deploy`。
4. 讓別人打開 `/Anime-Wiki/search.html`。當使用者按「搜尋動漫」且查不到結果，網站會自動提交擴充請求。
5. Worker 通過來源檢查與速率限制後，發出 `repository_dispatch`；GitHub Actions 在後台處理**一部**候選作品：

   `網路搜尋 → 確認官方來源 URL 與作品名稱 → Ingest → Wiki Lint → HTML 重建與驗證 → commit → GitHub Pages 部署`

6. 作品需通過驗證與部署後才能公開；若網站資料缺失或驗證不過，舊 Wiki 和簡報保留原狀。不保證每筆查無結果都能找到可信的新作品。

> **費用限制不是絕對金額保證。** Worker 使用 KV 的次數限制屬最終一致，可能遇到並行競態；GitHub Action 亦設每天 3 次的序列化嘗試計數，仍請務必設 OpenAI 平台的預算控制。Web Search 與模型 Token 可能另外計費。不要將本版公開佇列當成可承受大量惡意請求的成熟商用服務。

## 五、部署成功後怎麼驗證？

- 開啟搜尋網頁，搜尋 `你的名字`：應顯示作品及其 SRC 來源，可免費完成。
- 搜尋 `科幻 懸疑` 並選「動畫電影」：如果 Wiki 暫無結果且 AI 已啟用，會顯示已排入佇列。
- GitHub → Actions → **Controlled public Anime Wiki auto-ingest**：檢查執行結果。
- GitHub 儲存庫 `raw/`、`wiki/`、`index.md`、`log.md`、`records/runs/`：查看是否真正新增並通過驗證。
- `docs/index.html` 和 `docs/assets/wiki-snapshot.json`：確認新作品與來源數同步。

## 六、常見問題

- **顯示「尚未啟用」**：正常，AI 開關是預設關閉，網站搜尋現有作品仍可用。
- **收到佇列訊息但 Wiki 沒更新**：AI 可能沒找到能證實作品的來源、用量上限已到，或 GitHub Actions 尚未完成。到 Actions 查看錯誤。
- **本機可以搜尋，公開網站讀不到 JSON**：確認 GitHub Pages 發布的是 `docs/` 產物、網站根路徑使用相對連結。
- **已更新 GitHub 但網頁看不到新作**：查 Actions 的 Pages 部署；等待 CDN 快取更新後再重新整理。
- **查詢現有動漫也觸發 AI**：前端關鍵字是字串匹配，不等於 LLM 自然語言理解；修改為更短的作品名／類型，或透過類型選單篩選。

## 官方說明

- GitHub Pages：https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- GitHub `repository_dispatch`：https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- Cloudflare KV：https://developers.cloudflare.com/kv/get-started/
- Cloudflare Worker secrets：https://developers.cloudflare.com/workers/configuration/secrets/
- OpenAI Web Search：https://developers.openai.com/api/docs/guides/tools-web-search

**2026-11-23 類型搜尋修正：** 對「科幻」「懸疑」等純類型搜尋，當 AniList 不可用時改用 Jikan 依類型查詢；名稱搜尋仍優先使用 Kitsu。詳見 `FREE_API_README.md`。
