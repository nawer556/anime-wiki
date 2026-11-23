# 2026-11-23 多語搜尋與離線備援更新

`search.html` 支援中文／英文／日文作品名稱和「科幻、戀愛、懸疑」等類型搜尋；免費 API 逾時或錯誤時改顯示清楚標註的離線參考作品，並保留原有 Wiki。詳見根目錄 `FREE_API_README.md`。

# Anime Wiki｜教學 HTML 簡報（步驟二）

## AniList 故障時自動備援 Kitsu（2026-11-23）

搜尋作品名稱時，如果 AniList 回傳 HTTP 500／403／429 或發生逾時，系統會自動改用 Kitsu 免費公開資料 API；只有已查證的 Wiki 頁面才會用於教學簡報。詳見 `FREE_API_README.md`。

## 免費 AniList API 擴充（2026-11-20）

- `docs/search.html` 透過 `docs/assets/anilist-api.js` 以 GraphQL POST 查詢公開的 `https://graphql.anilist.co`，**不需要 AniList API Key 或 OpenAI API 費用**。
- Wiki 已收錄作品與 AniList 即時查詢顯示於不同區塊；AniList 只是外部資料參考，**不代表 Wiki 已經查證、Ingest 或更新簡報**。
- 可直接用 GitHub Pages 分享網址（`/search.html`），不需要 Cloudflare Worker；原來的 Worker 是**另外可選的管理員 AI 擴充機制**，預設關閉。
- 支援日文、羅馬拼音、英文名稱以及少量繁體中文常見譯名對照；中文全名搜尋可能因 AniList 資料索引限制而查無結果。
- 請求有兩秒最短間隔及十分鐘本機記憶體快取，不會大量抓取或下載整個 AniList。API 回傳 429／403／網路錯誤時，網站會顯示錯誤但保留 Wiki 搜尋。
- 本站不是 AniList 官方服務。非商業教育用途請遵循 [AniList API 使用條款](https://docs.anilist.co/guide/terms-of-use) 與 [Rate Limiting](https://docs.anilist.co/guide/rate-limiting)，**不要用 API 作為備份或大量資料儲存服務，也不要未經驗證就把 AniList 資料寫入 Wiki**。

## 開啟方式

- **最簡單**：直接雙擊 `index.html`，在 Chrome／Edge 開啟。HTML 已包含全部 CSS、JavaScript 和 Wiki 快照資料，不需要網路或伺服器才能播放。
- **在 VS Code**：開啟 `docs/index.html`，使用瀏覽器或 Live Preview 預覽。
- **切換投影片**：按鍵盤 `←` / `→`、點選底部左右箭頭或進度點；`F` 全螢幕、`Esc` 離開全螢幕。
- **第 5 頁**：點選「全部／TV／電影」篩選作品。
- **第 8 頁**：可調整作品形式、類型、心情與精確片長限制，查看 Wiki 快照的離線推薦結果。
- **資料追溯**：右上角「資料來源」可開啟 12 筆原始來源連結；每頁底部標出 Wiki 與來源 ID。

## 本專案的來源關係

`raw/manifest.json` → `wiki/works/*.md` → `scripts/query_wiki.py`（每次搜尋自動執行同步）→ `docs/assets/wiki-snapshot.json` → `docs/index.html`

`records/slide-sources.md` 提供每張投影片對應的 Wiki 頁面和 SRC 編號。內容隨每次本機 Query 以最新 Wiki 快照重新生成；作品介紹與片長依據原始 Wiki，類型／主題／情緒屬 Wiki 編輯分類。

**注意**：瀏覽器中的互動推薦是使用固定資料快照，不具備連網搜尋新作品或自動 Ingest 能力。Codex 工作階段未來可按 `workflow.md` 完成自動擴充。

## 搜尋後自動產生簡報

在專案根目錄執行（需要 Python 3，只有標準函式庫）：

```powershell
python scripts/query_wiki.py --type movie --genre 戀愛 --max-minutes 120
# 查詢結束會自動執行來源檢查、Wiki Lint、Graph Audit、簡報建置及檢查
# 顯示 AUTO SLIDES UPDATED 代表這次成功刷新本機簡報
```

新增已驗證作品、但沒有搜尋時，可主動執行：

```powershell
python scripts/sync_slides.py --reason ingest
```

每次搜尋後請重新整理已開啟的瀏覽器頁面。Live Server 可在 HTML 改變時自動重新載入。若要讓 GitHub Pages 的公開頁面更新，仍須把 `docs/` 的變更 commit / push。

更改 Wiki 之後，請核對投影片的固定教學敘述、來源對照表與實際瀏覽器畫面。修改簡報模板時編輯 `scripts/templates/deck.html`，**不要只修改 `docs/index.html`**，否則重新建置會覆寫。

## GitHub Pages 發布

專案上傳至 GitHub 後，在儲存庫 **Settings → Pages → Build and deployment** 選擇 **Deploy from a branch**，設定分支 `main`、來源資料夾 `/docs`，儲存後依 GitHub 顯示的網址查看網站。

`docs/index.html` 可獨立發布；整個 Wiki 原始檔仍應留在儲存庫中，讓評分者能確認資料來源。**此專案包尚未替你建立 GitHub 儲存庫或公開網址。**

## 圖片授權

本版使用原創 CSS 造型與文字，不內嵌動畫劇照、官方海報或第三方圖片，以避免圖片授權問題。

## Wiki 的 Karpathy 式維護

本版加入根目錄 `AGENTS.md`，Codex 可以依 Schema 逐份 Ingest、同步更新相關 Wiki 頁、Query 與 Lint。靜態簡報在 VS Code 的本機 Query 後會自動重新生成版本快照；瀏覽器端仍不會直接搜尋網路或修改來源。

**2026-11-23：** 「科幻」類型搜尋已加入 Jikan 備援；詳見根目錄 `FREE_API_README.md`。

## 申請收錄（免費）

`search.html` 的外部卡片提供「＋ 申請加入 Anime Wiki」，使用 `assets/issue-request.js` 生成 GitHub Issue 預填連結；設定自己的儲存庫位於 `assets/repository-config.js`。申請不會直接更新公開 Wiki。管理者核准後，GitHub Actions 會重新查證資料、Ingest／Lint 並重建簡報。詳見專案根目錄 `APPROVAL_SETUP.md`。
