# Anime Wiki 公開搜尋與後端擴充 — 實際開發測試紀錄

## 功能與完成狀態（2026-11-19）

- 保留 Karpathy 風格的 Raw/Wiki/Schema 三層結構與 `AGENTS.md`。
- 新增 `docs/search.html` 供公開瀏覽器端搜尋；保留 `docs/index.html` 10 張 Wiki HTML 教學簡報。
- 新增 Cloudflare Worker 入口 `backend/src/index.js`：Origin 檢查、輸入過濾、去重、KV 日限額、GitHub dispatch。預設關閉。
- 新增 `.github/workflows/auto-ingest.yml` 與 `scripts/auto_ingest.py`：受限制的 API 搜尋、來源檢查、Wiki 新增、Lint、HTML 重建與 GitHub Pages 更新。
- 新增 `.github/workflows/pages.yml` 與 `DEPLOYMENT.md`。

## 真實執行的測試

- `python scripts/check_sources.py`：PASS — 12 筆原始來源 SHA-256 完整性。
- `python scripts/lint_wiki.py`：PASS — 10 部作品、12 筆來源、0 error。
- `python scripts/check_slides.py`：PASS — 10 張簡報、來源連結與 Wiki snapshot 一致。
- `python -m unittest discover -s tests -p test_workflows.py -v`：7/7 PASS。
- `python -m unittest discover -s tests -p test_auto_slides.py -v`：3/3 PASS。
- `python -m unittest discover -s tests -p test_public_expansion.py -v`：6/6 PASS：包含虛構的第 11 部作品在**暫存專案副本**的新增、同步和失敗回復；不是真實新作品，不會寫入發布中的 Wiki。
- `cd backend && node --test`：6/6 PASS：包含拒絕陌生 Origin、免費模式、重複請求去重、每日 IP 次數限制。
- Chromium 瀏覽器執行真實 JS、以本機 snapshot 模擬網路回覆：初始 10 部、搜尋「你的名字」命中一部、搜尋「科幻 懸疑」電影查無結果、免費模式呈現不啟用說明，頁面 JS 無錯誤。瀏覽器環境禁止直接連 localhost，因此未宣稱端到端真實 HTTP 瀏覽器測試通過；另產出搜尋網頁截圖供檢閱。

## 開發過程的真實錯誤與調整

1. 初次新增模擬作品的測試把新 `SRC` 編成 `SRC001`（缺少 `-`），已將來源 ID 格式修正為 `SRC-013`，重新跑檢查通過。
2. 初次測試的同步工具使用匯入模組時綁定的專案根目錄，使**測試副本** Wiki 已增為 11 部，但測試副本簡報仍是 10 部。修正為在**正在修改的專案根目錄**呼叫 `scripts/sync_slides.py`，重新執行後通過。
3. 模擬破壞簡報模板時，Ingest 整體流程會拒絕更新並回復舊版 Wiki 與來源；測試結果 PASS。

## 尚未驗證的部分（不可冒稱完成）

- 沒有使用真實 OpenAI API Key，**沒有付費 API 搜尋**。
- 沒有在使用者的 GitHub 帳號建立儲存庫，也沒有真的觸發 GitHub `repository_dispatch` 或 Cloudflare 正式 Worker。
- 沒有實際公開網站 URL；需使用者依 `DEPLOYMENT.md` 完成授權、部署。
- 真實網站的官方來源驗證成功率與 OpenAI Responses `web_search` 輸出格式，必須在啟用 API 後用少量配額測試；失敗時系統拒絕提交 Wiki，不會假裝收錄成功。
- 網頁本機分類搜尋是確定性字串匹配，**不等於前端具有 AI 語意搜尋**。
