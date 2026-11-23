# 實測紀錄：每次搜尋後自動更新教學 HTML（2026-11-19）

## 目標與修改

舊 `query_wiki.py` 只會印出 Query 結果，`build_slides.py` 將收錄數固定為 10 部，因此新增作品後不會自動反映到靜態簡報。本次新增 `sync_slides.py`，修改 `query_wiki.py` 在每次搜尋後觸發同步，將最近一次 Query 和完整 Wiki 資料寫到新的靜態 HTML。

- 正式 Query：`python scripts/query_wiki.py --type movie --genre 戀愛 --max-minutes 120`。
- 查無結果：`python scripts/query_wiki.py --type movie --genre 科幻`。
- Ingest 後單獨刷新：`python scripts/sync_slides.py --reason ingest`。
- 同步防護：先驗證來源 checksum、Wiki Lint、Graph Audit；建置後再執行 Slide Lint，失敗則保留上一份 HTML、快照與來源對照。
- 第 5 頁作品地圖與來源統計不再固定 10 部，第 8 頁新增最近搜尋條件與候選結果；可查回 `records/last-query.json`。

## 真實執行與測試（不是模擬成功紀錄）

1. 實際查詢 `--type movie --genre 戀愛 --max-minutes 120`：回傳《你的名字。》（SRC-004、SRC-012），終端印出 `AUTO SLIDES UPDATED`。
2. 實際查詢 `--type movie --genre 科幻`：回傳 `NO_MATCH / AUTO_INGEST_REQUIRED`，**仍執行 HTML 同步**，在最新 Query 區呈現無匹配情況。沒有在此過程進行網路搜尋或新作品 Ingest。
3. `scripts/browser_smoke_local.py`：10 張投影片切換、來源清單數量、互動篩選、片長已核實推薦、無匹配顯示、JavaScript 錯誤檢查皆通過。
4. `tests/test_auto_slides.py` 的三個**隔離的暫存測試**：連續搜尋會替換最近結果；原始來源被篡改時不會覆蓋上一個有效 HTML；合成第 11 個**僅用於測試的**作品頁時不再觸發固定 10 部的斷言。合成測試作品**未**收錄正式 Wiki。
5. 原有 7 項 Wiki 流程測試繼續執行，確保 Raw 不可竄改、Lint／Query 基本行為、暫存工作不影響來源 manifest。

## 限制與反思

- 這是**每次在 VS Code 或 Codex 執行專案 Query CLI 後的自動更新**，不是任何聊天訊息或在瀏覽器點擊選項就執行 Python。Codex 必須遵循 `AGENTS.md` 真正呼叫指令。
- Wiki 中沒有作品時，CLI 不能自己連網；必須由具網路權限且獲使用者授權的 Codex 搜尋、Ingest、Lint、再重新 Query。
- 自動同步會讓新的作品頁與來源出現在第 5／8／10 頁；已有的教學示例段落在重大知識變更時仍要人工審核。
- 本機更新後，已開啟的 HTML 頁面需要重新整理；GitHub Pages 公開版則需更新遠端 Git 儲存庫。
