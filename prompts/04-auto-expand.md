# 貼給 Codex｜依查詢結果受限自動擴充

請先讀 AGENTS.md、index.md 及推薦方法，執行查詢：

推薦一部具科幻主題、電影形式、適合第一次接觸動畫的作品。

若現有 Wiki 沒有經驗證的候選，依我先前選擇的模式 B，**在獲得本次工作階段的網路權限下**自動搜尋並 Ingest：最多兩輪搜尋、最多新增三部合格作品。先檢查來源可信度、影片身分、資料衝突，再進 staging，驗證通過後同步更新 raw/manifest、作品頁、相關主題頁、推薦規則、index、log。執行 Lint 後重新 Query。

若網路存取未獲允許、來源不足或已達上限，請回報真實情況，不得虛構推薦或假裝已完成匯入。


## 必做：無論是否找到結果，都同步投影片

先將需求轉為 CLI 條件執行 `python scripts/query_wiki.py --type movie --genre 科幻`，這會先自動刷新 HTML。若 `AUTO_INGEST_REQUIRED` 且網路權限已授予，再執行有限次來源搜尋／Ingest／Lint；資料驗證通過後必須用**相同條件**再次執行 `python scripts/query_wiki.py --type movie --genre 科幻`。第二次 Query 會把新作品、原始來源、最新搜尋推薦結果寫入 `docs/index.html`。請核實回報 `AUTO SLIDES UPDATED`，失敗不可聲稱同步完成。使用者開啟的瀏覽器可能需要刷新頁面，遠端 GitHub Pages 還需要 git push。
