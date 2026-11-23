# 貼給 Codex｜每次搜尋動漫後自動更新 HTML 簡報

請先閱讀 `AGENTS.md` 與 `index.md`，我現在要搜尋日本動漫。**每次搜尋完成後，必須真的執行專案的查詢 CLI，讓 `docs/index.html` 自動重新建置**，不能只回答推薦文字。

這次我的需求：推薦 120 分鐘內、戀愛類型的日本動畫電影。

執行規則：
1. 先查看 Wiki 已驗證作品，按硬性條件與軟偏好推薦。
2. 用 `python scripts/query_wiki.py --type movie --genre 戀愛 --max-minutes 120` 執行搜尋，檢查 `AUTO SLIDES UPDATED`。
3. 如果沒有符合的作品且具網路權限，依 `AGENTS.md` 進行最多 2 輪、最多 3 部的安全搜尋、來源驗證與 Ingest，通過 Lint 後再次執行**同一條** Query。
4. 完成後告訴我推薦結果、是否真的新增 Wiki，以及 `docs/index.html` 是否更新成功。提醒我如已開啟瀏覽器要刷新頁面。
5. 若失敗，說明阻礙並保留原本可用的簡報；不得說已自動更新或已連網。

以後更換搜尋條件時，請保持「Query → 自動重新生成簡報 → Lint → 記錄」這個流程，除非我明確要求唯讀診斷。
