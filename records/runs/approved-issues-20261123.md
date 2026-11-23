# 管理者審核收錄開發與模擬驗證｜2026-11-23

## 實作範圍

- 搜尋網頁的外部作品卡片新增「申請加入 Wiki」，透過 GitHub Issues 預填來源資訊。
- 經個人儲存庫擁有者手動套用 `approved-ingest` 標籤後，GitHub Actions 執行免費 AniList / Kitsu 來源核對、Ingest、Lint、重建簡報、提交並重新部署。
- 將無法核對的 Jikan 或離線參考標記為「待補來源」，不自動寫入 Wiki。

## 實際執行的測試（不連線／不付費）

1. Python `test_approved_issue_ingest.py`：4 項測試。包含格式驗證、未授權來源拒絕、固定 API 端點，以及在暫存副本新增第 11 部《命運石之門》、第 13 份來源、更新科幻分類與 HTML。
2. Node `test_issue_request.cjs`：3 項測試。包含預填 GitHub Issue、離線來源待補欄位與 GitHub Pages 儲存庫偵測。
3. Browser 模擬：用本地 HTML 與測試資料模擬 AniList 找到《命運石之門》，確認申請按鈕出現並指向預填的 `.../issues/new`，JavaScript 無執行錯誤。
4. `check_sources.py`、`lint_wiki.py`、`check_slides.py`：原始 10 部 Wiki、12 份來源與 10 張簡報仍通過。

## 未完成與限制

- **尚未上傳至使用者 GitHub 或啟用 GitHub Actions 實際工作流程。** 真實 GitHub Issue 申請與自動部署需要使用者在自己的 GitHub 儲存庫實測。
- 網路環境限制：**沒有實際對 AniList／Kitsu 發出成功請求**；測試中由固定資料模擬 API 回覆。
- Jikan 官方公共 API 已在 2026-10-01 停止，不能作為新的正式收錄來源。
- 未使用付費 OpenAI API，也沒有 AI 自動補寫完整劇情；新增的作品頁只記錄資料庫基本事實與保守介紹。
