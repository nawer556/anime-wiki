# Operations：Ingest、Query、Lint 實作手冊

本檔是 `AGENTS.md` 的補充說明。Karpathy 的模式與本專案差異：

- **Ingest**：新 Raw Source 不只成為新文章，而是進一步更新相關 Wiki 知識並留下改動證據。
- **Query**：優先從 `index.md` 與 Wiki 檢索，必要時追查 Raw；答覆可回寫綜合頁，但必須驗證。
- **Lint**：結構檢查 + 語意審核；追查無來源事實、矛盾、過時、孤兒頁及應交叉連結卻未連結的概念。

## Ingest 的最小完整回合

1. `python scripts/check_sources.py`、`python scripts/lint_wiki.py` 記下基線。
2. 查重 + `staging/` 修改計畫 + 可信 URL 及具體來源事實。
3. 新 Raw / manifest / checksum → 作品 Wiki + 相關分類與指南 + `index.md`。
4. `python scripts/check_sources.py`、`python scripts/lint_wiki.py`、`python scripts/audit_wiki.py`。
5. `records/runs/` 記錄失敗、修復與測試命令；append `log.md`。
6. **正式 Ingest 通過即同步 `docs/`**：執行 `python scripts/sync_slides.py --reason ingest`；如源自 Query 無結果，必須再次用相同條件執行 `scripts/query_wiki.py`，其預設每次 Query 都同步簡報。

## 透明度準則

- 整套工具均可離線檢查本機檔案。
- **自動上網搜尋與資料理解是 Codex 工作階段的 Agent 行為，不是 Python 查詢腳本內建的能力**；取決於授權網路連線。
- 新資料的查證，不可只靠 Lint 回傳 PASS；Lint PASS 不等於事實真實。
- 對 AI 生成的「情緒」／「類型」判斷與客觀作品資料要清楚區分。

## Query 後自動同步 HTML（已實作）

- 將使用者需求轉成 Query CLI 支援的條件，例如 `python scripts/query_wiki.py --type movie --genre 奇幻`；每次查詢都會觸發 `sync_slides.py`，不需要手動編輯 HTML。
- 同步順序：Raw checksum → Wiki Lint → Graph Audit → 最新 Query 紀錄 → 產生靜態 HTML 和快照 → 簡報 Lint → 保存新版本 / 失敗保留舊版本。
- HTML 的第 5 頁作品地圖、第 8 頁最近 Query／互動推薦和來源清單使用最新知識資料；其他固定教學敘述若涉及更新作品，須人工複核。
- Codex 不能僅回答自然語言而跳過 CLI；未呼叫 Query 工具的對話不會觸發本機檔案更新。使用者在簡報瀏覽器操作篩選也不會回寫 Wiki。
