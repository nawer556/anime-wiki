# 免費 AniList API 公開搜尋整合檢查（2026-11-20）

- 來源：官方 https://docs.anilist.co/guide/graphql/ 與 terms / auth / rate-limiting 文件。
- 開發：保留舊 Wiki 與簡報；`docs/search.html` 加入 AniList 區塊，`docs/assets/anilist-api.js` 實作只讀搜尋。
- 限制：新作品**不會直接加入** `raw/` 或 `wiki/`；不會更新 `docs/index.html`。
- 單元測試：6 個 mock 案例 PASS；驗證中文別名、類型映射、安全網址、成人標記、時長約束、快取和 429。
- 回歸測試：原有 `test_workflows.py` 7 項 PASS；來源／Wiki Lint／簡報 Lint 均 PASS。
- 環境限制：目前執行環境不允許對外網域 DNS 連線，且自動瀏覽器受管理員網路封鎖，故**未能**實際從 AniList 取回資料或做真實瀏覽器端驗證。
- 使用者本機驗證：本機 HTTP 伺服器開啟 `http://localhost:8000/search.html`，搜尋 `命運石之門`。查看 AniList 結果與原站來源連結；網路失敗則顯示提示。
