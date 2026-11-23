# RUN-20261118-SRC012｜Karpathy 式增量 Ingest 實作紀錄

> 本記錄來自本次實際操作，不是模擬對話。來源核對使用 JFDB 的公開網頁資料；Wiki 與 Python 工具在本機執行。

## 本次任務

- Operation: `ingest` → `lint` → `query` → `slide-build`（補充舊作品，不新增重複條目）
- 新來源：`SRC-012` → https://jfdb.jp/en/title/6450 （JFDB 的《your name.》作品頁）
- 新來源事實：片長 107 分鐘、2016 年上映、導演新海誠（根據 JFDB 頁面）
- 對應舊作品：`W007` → `wiki/works/你的名字。.md`，之前只有 SRC-004，片長未知。

## 計畫與實際資料變更

1. 保存 **新** Raw Note `raw/sources/SRC-012.md`；`raw/sources/SRC-004.md` 原封不動。
2. 在 `raw/manifest.json` 新增 SRC-012 並於 `raw/checksums.json` 紀錄來源檔 SHA-256。
3. 更新 **既有** `wiki/works/你的名字。.md`：新增 `source_ids`、片長由 `null` 更新為 107，並加入來源網址與註腳。
4. 更新 `wiki/recommendations/推薦方法.md`，新增 `wiki/recommendations/兩小時內的動畫電影.md` 的可追溯推薦案例。
5. 更新 `index.md`；修正作品與系列雙向連結，排除名稱同為「青春」的 Wikilink 歧義。
6. 為 Codex 建立 `AGENTS.md` 與 `schema/`，使日後 Ingest 流程可依固定規則重現。

## 先行發現的錯誤（真實測試）

- 第一次執行 `python scripts/lint_wiki.py`：`ERROR: index.md: broken relative link records/runs/ingest-src012-jfdb.md`。
- 原因：先在索引登記了本篇執行紀錄，當時還沒有實際寫出紀錄檔。
- 修正：建立並完成本篇紀錄，再重新跑 Lint。這證明檢查索引連結應放在**寫入紀錄之後、發布之前**。

## 第二個實際失敗與修正：暫存工具

- 第一次 `python -m unittest discover -s tests -v`：7 個測試中 1 個失敗（`test_stage_does_not_change_manifest`）。
- 原因：`scripts/prepare_ingest.py` 假定 `staging/` 一定已存在；在新的乾淨暫存測試資料夾中寫檔失敗。
- 修正：於建立暫存範本前呼叫 `f.parent.mkdir(parents=True, exist_ok=True)`，再重跑整組測試。
- 這使**暫存驗證前置**，新專案初次使用也不會直接失敗，更符合 Auto Ingest 可重複執行的要求。

## 驗證結果

以下項目需以本回合最後執行的終端機輸出為準：

- Raw immutability：`python scripts/check_sources.py`
- Wiki link + metadata structural lint：`python scripts/lint_wiki.py`
- Wiki graph health：`python scripts/audit_wiki.py`
- Query hard-filter positive：`python scripts/query_wiki.py --type movie --genre 戀愛 --max-minutes 120`
- Query no-match：`python scripts/query_wiki.py --type movie --genre 科幻`
- Slides：`python scripts/build_slides.py` 與 `python scripts/check_slides.py`

結論：本次示範了**新來源更新既有知識並影響推薦篩選**，而不是把 Raw 資料讀一次就丟棄。此操作由本次專案編修完成；**尚非使用者本機 Codex 自動連網 Ingest 的測試**。
