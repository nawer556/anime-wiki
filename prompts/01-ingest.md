# 貼給 Codex｜Ingest 新來源

請先讀根目錄 AGENTS.md、index.md、schema/operations.md 與 raw/manifest.json。

我想把下列動畫資料來源 Ingest 到 Anime Wiki：

- 來源 URL：〔請貼上真實網址〕
- 預計作品：〔作品名或「未知」〕
- 想知道：〔新增的知識問題〕

請先查有沒有重複來源、是否為 TV / Movie / 系列／季度／劇場版，以及哪些來源事實可以確認。先將摘要與更新計畫放 staging，不要直接把未查證資料寫入正式 Wiki。資料可信後，新增 Raw Source、更新既有或新作品、必要的分類／主題／比較／推薦頁、index.md，檢查後把真實執行結果寫入 log.md 和 records/runs/。保留原始來源檔不覆寫。若無法上網，說明限制並停在 staging。


**Ingest 成功之後還要自動更新教學 HTML**：請確實執行 `python scripts/sync_slides.py --reason ingest`，檢查 `AUTO SLIDES PASS`。如果是為了回應一個未成功的 Query 而 Ingest，再用原本條件重跑 `python scripts/query_wiki.py ...`，讓最近搜尋結果同步顯示。
