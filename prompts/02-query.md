# 貼給 Codex｜從 Wiki 智慧推薦

請依 AGENTS.md 的 Query 規則，先讀 index.md，再查相關 Wiki 頁與 raw sources。

我的需求：推薦 120 分鐘以內、包含戀愛題材、可以單部看完的日本動畫電影。

請依硬性條件先過濾，再用 Wiki 的主題與情緒標籤排序。提供最多三部，逐部標示 Wiki 頁、SRC ID 與原始網址，並註明哪些屬於 Wiki 編輯性推薦判斷。不要把未知片長當成符合。


## 必做：搜尋結束時自動更新 HTML

請將上述條件轉為 `python scripts/query_wiki.py --type movie --genre 戀愛 --max-minutes 120`，**必須真正執行 CLI**（不用 `--no-sync`）。腳本會自動完成來源檢查、Wiki Lint、HTML 重建及檢查，並把最新搜尋結果放進第 8 張投影片。最後確認輸出包含 `AUTO SLIDES UPDATED`，並告訴我 `docs/index.html` 已更新。若查詢結果不足且需要 Auto Ingest，先依規範擴充後再 Query 一次。
