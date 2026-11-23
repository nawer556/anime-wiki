# Step 2：HTML 教學簡報製作與測試紀錄

- 日期：2026-11-18（台灣時間；不虛構具體執行時分）
- 操作：`build-slides` → `check-slides` → `wiki-lint` → `browser-test`
- Wiki 資料版本：`raw/manifest.json` 的 `as_of=2026-11-18`
- 輸出：`docs/index.html`、`docs/assets/wiki-snapshot.json`、`records/slide-sources.md`
- 模板：`scripts/templates/deck.html`

## 真正執行的結果

1. `python scripts/build_slides.py`：**PASS**。10 部作品、11 筆來源，成功產生 HTML 與 JSON 快照。
2. `python scripts/check_slides.py`：**PASS**。10 張投影片、10 部作品、11 筆來源、11 個可見來源連結；Wiki 快照與作品頁 frontmatter 的重要欄位一致；未知片長不會誤通過時間限制。
3. `python scripts/lint_wiki.py`：**PASS**。0 個結構錯誤，7 個篇幅未知提醒（不是錯誤，故沒有猜測補值）。
4. Chromium（Playwright `set_content` 執行內嵌 HTML）：**PASS**。10 張投影片可用鍵盤及進度點切換；第 5 頁「全部／TV／電影」對應 10／6／4 部；第 8 頁「電影＋奇幻」得到《你的名字。》和《神隱少女》，再加「120 分鐘內」則回報 `AUTO_INGEST_REQUIRED`；來源視窗含 11 筆連結，Esc 可以關閉；JavaScript 執行錯誤為 0。
5. 已擷取並人工查看投影片 1–10 的 Chromium 畫面，確認排版與控制項正常顯示。

## 來源可追溯性

- 完整表格：`records/slide-sources.md`
- 示例：`SRC-009` 吉卜力官方 → `wiki/works/神隱少女.md` → 投影片 03、04、06、09 的作品資訊與示例。
- 情緒、節奏、主題歸類為 Wiki 編輯性標籤，不宣稱官方客觀評分。

## 限制與後續

- 這次是在工具隔離環境中使用 Chromium 的 `set_content` 測試內嵌 HTML。該環境禁止直接以 `file://` 或本機 HTTP URL 導覽，因此**尚未在使用者自己的 Edge／Chrome 或 GitHub Pages 公開網址測試**。使用者解壓後應在 Windows 瀏覽器實際開啟 `docs/index.html` 做最後確認。
- 來源網址已嵌入且符合 Wiki manifest，但因網路限制，本次沒有在瀏覽器逐一點擊全部外部官方連結。
- 靜態 HTML 的本機互動推薦**不是**自動連網 Ingest；Codex Agent 自動擴充仍待後續串接。
- GitHub 儲存庫／GitHub Pages 尚未建立或公開；需要使用者自行上傳或授權後部署。
- 沒有建立 `AGENTS.md`。
