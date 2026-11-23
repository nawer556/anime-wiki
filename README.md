# Anime Wiki — 訪客申請加入＋管理者審核（免費）

> **2026-11-23 新增：** 搜尋網站可為未收錄動漫產生預填的 GitHub Issue。由**個人 GitHub 儲存庫擁有者**審核後，手動加上 `approved-ingest` 標籤，GitHub Actions 才會取得免費 AniList 或 Kitsu 公開資料、驗證來源、Ingest、Lint、更新 Wiki 與 10 張 HTML 教學簡報，並部署到 GitHub Pages。訪客不能直接修改 Wiki。**不需要 OpenAI API Key，也沒有額外 AI API 費用。**

- [訪客申請與管理者核准的詳細步驟](APPROVAL_SETUP.md)
- 網站：`docs/search.html`（每張外部結果卡片新增「＋ 申請加入 Anime Wiki」）
- 經驗證的入庫程式：`scripts/approved_issue_ingest.py`
- 自動化：`.github/workflows/approved-ingest.yml`
- Issue 預填連結：`docs/assets/issue-request.js`、`docs/assets/repository-config.js`
- 新增科幻分類：`wiki/genres/科幻.md`

**注意：** 離線參考或 Jikan 結果只能先提出申請，需要你核對並補入 AniList／Kitsu 正式作品 ID 才能自動匯入。Jikan 官方公共 API 已在 2026-10-01 停止服務，不可依賴它完成新作品入庫。連網 API 若暫時故障，工作流程會拒絕寫入；GitHub Issues 需要訪客登入 GitHub。這是可部署的程式碼，目前尚未替你連接或發布 GitHub。

---

# Anime Wiki — 免費多語動漫搜尋、Wiki 與 HTML 教學簡報

> **2026-11-23 多語搜尋與類型搜尋修復：** `docs/search.html` 現在支援繁體／簡體中文、英文、日文名稱；會把常見中文名稱轉成英文搜尋、將「科幻／戀愛／懸疑」轉成動漫類型條件。免費 API 無法使用時，改顯示明確標記的離線動漫參考（不寫入 Wiki）。詳細說明請看 [FREE_API_README.md](FREE_API_README.md)。


**2026-11-23 新增免費 Kitsu 備援：** 搜尋作品名稱時，如 AniList 無法使用，會嘗試 Kitsu 公開 API，並清楚標註來源。詳見 `FREE_API_README.md`。

**2026-11-20 免費 AniList API 升級：** 現在 `docs/search.html` 可以搜尋 **Wiki 之外的日本動畫**，不用 OpenAI API Key，也不必部署付費後端。公開 AniList 查詢是唯讀，不自動新增 Wiki 或更新簡報；Wiki 的永久維護仍由 Ingest → Lint → HTML 重建流程負責。

**這份是使用先前 Karpathy 風格 Wiki 升級的公開網站版。** 保留所有 10 部動漫、12 筆來源、Ingest／Query／Lint、`AGENTS.md` 與 10 張 HTML 教學簡報。

- **公開搜尋網頁**：`docs/search.html`，查既有 Wiki 並用免費 **AniList GraphQL API（異常時備援 Kitsu）** 查未收錄作品，兩種結果分區顯示；外部作品附對應資料來源連結。
- **教學 HTML 簡報**：`docs/index.html`，自動從經驗證的 Wiki 產出。
- **可選的 AI 擴充後端**：`backend/` Cloudflare Worker + `.github/workflows/auto-ingest.yml` + `scripts/auto_ingest.py`。
- **先免費**：初始 AI 關閉，不需要 OpenAI API Key；部署後可以先分享可查詢的網址。
- **開通 AI 之後**：訪客查無結果會觸發受限制的工作流程，先驗證資料、Ingest、Lint、重建 HTML，再由 GitHub Pages 發布；**可能產生 API 費用**。

## 立即測試（不用付費）

在 VS Code 終端機開啟專案根目錄：

```powershell
python -m http.server 8000 --directory docs
```

再打開 **http://localhost:8000/search.html** 搜尋動漫；**http://localhost:8000/index.html** 觀看簡報。

測試方法：搜尋「命運石之門」（會嘗試使用內建日文／羅馬拼音別名轉換搜尋 AniList），或輸入「科幻 懸疑」並指定動畫電影。**網頁需能連線到 AniList 或 Kitsu 公開 API**。若 AniList 無法使用會嘗試 Kitsu 名稱搜尋；兩者皆無法連線時 Wiki 既有作品仍可查。簡體／繁體中文作品名不一定能直接被 AniList 搜尋，建議改用原文或英文名稱。

**資料邊界：**「AniList／Kitsu · 未收錄」不等於已正式 Ingest。只有管理者核對來源、寫入 `raw/` 與 `wiki/`、執行 Lint 並重建 HTML 後，才會出現在正式 Wiki 與簡報。此版本不會因訪客搜尋就改動 GitHub 儲存庫。

下一步要讓別人能用網址打開，請跟著 [DEPLOYMENT.md](DEPLOYMENT.md) 操作 GitHub Pages。**目前交付的是可下載程式，不是已部署的公開網址。**

## 零費用測試

```powershell
python scripts/auto_ingest.py --query "科幻懸疑動畫電影" --dry-run
python -m unittest discover -s tests -p "test_*.py"
cd backend
node --test
```

`--dry-run` 不上網、不消耗 API、不更動 Wiki。`test_public_expansion.py` 的虛構第 11 部動畫只存在暫時目錄，**不會混入正式知識庫**。

---

# Anime Wiki — Karpathy 風格 LLM Wiki（Codex 專案）

> **主題：動漫百科＋混合式智慧推薦。** 這不是單純的動漫網站，而是一個會在新來源進入時由 Codex **增量維護**的 Markdown 知識庫。參考 [Andrej Karpathy 的 LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)：Raw Sources（不可變）＋Wiki（LLM 持續編輯）＋Schema（`AGENTS.md`），並落實 Ingest、Query、Lint、`index.md`、`log.md`。

## 打開就能交作業的成果

- **LLM Wiki**：`index.md` 是所有內容索引；`wiki/` 收錄 **10 部動漫：6 部 TV + 4 部電影**，有分類／主題／系列／推薦／比較共 44 頁 Wiki Markdown；作品頁中標示來源 ID。
- **Raw Sources**：`raw/sources/SRC-001.md` ～ `SRC-012.md` 共 **12 份**可追溯的來源摘要；`raw/manifest.json` 對應 URL、發行方及日期；`raw/checksums.json` 避免歷史來源被覆寫。
- **Schema**：`AGENTS.md` 供 VS Code + Codex 讀取，詳細規定來源驗證、增量 Ingest、Query、Lint、網路擴充條件及紀錄。
- **實際增量 Ingest**：新加入 `SRC-012`（JFDB），將 **《你的名字。》片長從未知改成有來源的 107 分鐘**，新增「兩小時內的動畫電影」推薦頁，更新索引及來源；見 `records/runs/ingest-src012-jfdb.md`。
- **HTML 教學簡報（搜尋後自動重新建置）**：`docs/index.html` 有 10 張可離線操作的教學投影片；每次透過本專案 CLI 搜尋就會先做資料驗證再自動生成 HTML，最新搜尋會顯示在第 8 張；`records/slide-sources.md` 是 Wiki 與來源對照；`docs/assets/wiki-snapshot.json` 是靜態資料快照。
- **記錄與工作流程**：`log.md` 記錄時間序列事件；`records/runs/` 保留實際檢查、錯誤、修正及測試紀錄；`workflow.md` 和 `schema/operations.md` 說明 Loop／Graph。

## 重要：已完成與未完成

**已實際完成**：Wiki 初始化、12 筆來源筆記與來源追蹤、Codex 版 `AGENTS.md`、增量修改既有 Wiki、原始來源完整性與結構 Lint、離線 Query、HTML 快照建置與一致性檢查。

**尚未在使用者 VS Code 實測**：Codex 自行連網搜尋新動漫→Ingest→Lint→重新 Query 的完整自動擴充。`AGENTS.md` 已提供可執行的 Agent 規範，但此功能需要你在有網路權限的 Codex 工作階段實際操作；`scripts/query_wiki.py` 只會輸出 `AUTO_INGEST_REQUIRED`，不是爬蟲或常駐服務。專案尚未部署 GitHub Pages，沒有憑空建立公開網址。

## Windows + VS Code + Codex 快速開始

1. 解壓縮檔案，於 VS Code 選擇 **File → Open Folder**，開啟此專案根目錄（含 `AGENTS.md` 的資料夾）。
2. 使用 VS Code 的 Codex 擴充套件（已安裝並登入）；**重新開一個 Codex 工作階段**讓它讀到 `AGENTS.md`。
3. 先開啟 `index.md`，點擊作品 Wiki 或使用 Obsidian 開啟專案根目錄作為 Vault，瀏覽 Wiki Links 形成的知識圖譜（Obsidian 可選）。
4. 在 VS Code 終端機（PowerShell）執行：

```powershell
python scripts/check_sources.py
python scripts/lint_wiki.py
python scripts/audit_wiki.py
python scripts/query_wiki.py --type movie --genre 戀愛 --max-minutes 120
python scripts/query_wiki.py --type movie --genre 科幻
python scripts/check_slides.py
python -m unittest discover -s tests -v
```

如果 Windows 是 `py` 指令，以上 `python` 換成 `py`。一般 Wiki 工具和 7 項測試只用 Python 3 標準函式庫，不需要安裝 pip 套件；`scripts/browser_smoke_local.py` 是**額外的** Playwright 瀏覽器測試，只有安裝 Playwright／Chromium 的環境才需要執行。

5. 在 Codex 貼上 `prompts/01-ingest.md` 或 `prompts/03-lint.md` 的內容，讓 Codex 實際操作一輪。**不要把設計流程當成已完成的真實執行記錄**。
6. 開啟 `docs/index.html`，可以用 Chrome、Edge 或 VS Code Live Preview 預覽教學簡報。
7. **每次搜尋後自動更新簡報（已實作，無需額外按更新）**：

```powershell
python scripts/query_wiki.py --type movie --genre 戀愛 --max-minutes 120
# Query 會印出 AUTO SLIDES UPDATED；docs/index.html 第 8 頁會顯示最新搜尋結果
```

完成新來源 Ingest 但不打算立即查詢時，也可執行：

```powershell
python scripts/sync_slides.py --reason ingest
```

本機簡報開啟後請重新整理頁面，VS Code Live Server 可以偵測檔案更新並自動重載。**GitHub Pages 上的公開簡報仍必須先 commit/push，才能看到新版本**；無法只靠電腦本機搜尋更新遠端網站。

## 目錄與三層架構

```text
Anime-Wiki/
  AGENTS.md                    ← Schema：Codex 全域專案規則
  schema/                      ← 作品頁格式與工作流程細節
  raw/                         ← Raw：來源筆記、manifest、checksum（已存來源不可覆寫）
    sources/SRC-001.md ... SRC-012.md
  staging/                     ← 待驗證 Ingest 暫存
  wiki/                        ← LLM 持續維護的相互連結 Markdown
    works/ genres/ themes/ series/ recommendations/ comparisons/
  index.md                     ← 每次 Ingest 更新的內容總索引
  log.md                       ← append-only 時間序列操作記錄
  records/runs/                ← 真正的 Lint、Query、Ingest 執行證據
  docs/index.html              ← 步驟二的靜態 HTML 教學簡報
  docs/assets/wiki-snapshot.json
  scripts/                     ← 查詢、檢查、準備暫存、建簡報工具
  tests/                       ← 本機流程與原始資料完整性測試
  prompts/                     ← 可直接貼給 Codex 的操作範例
  workflow.md                  ← Workflow / Graph 解釋
```

## 直接展示的三個操作

**Ingest（知識累積）**：比較 `SRC-004` 和 `SRC-012`，查看 `wiki/works/你的名字。.md` 與 `wiki/recommendations/兩小時內的動畫電影.md` 的更新，再讀 `records/runs/ingest-src012-jfdb.md`。

**Query（已有知識再利用）**：執行 `python scripts/query_wiki.py --type movie --genre 戀愛 --max-minutes 120`，目前可得到《你的名字。》；查詢 `--type movie --genre 科幻`，會輸出 `AUTO_INGEST_REQUIRED` 而非編造結果。

**Lint（可驗證的維護）**：`python scripts/check_sources.py` 防篡改；`lint_wiki.py` 查連結、欄位與來源；`audit_wiki.py` 輔助檢查孤兒頁、跨頁連結與同名問題。工具不能取代 Codex 的事實審核。

## 操作注意事項

- `raw/sources/` 是已記錄當時取得資料的**精簡改寫筆記**，不是來源網站的完整 HTML/合法全文授權備份。
- 推薦中的節奏、情緒、類型標籤是 Wiki 編輯歸納，必須與來源事實區分。
- 本 Wiki 與 HTML 不能擅自使用受著作權保護的動畫劇照；網頁採原創 CSS 設計。
- 根目錄 `AGENTS.md` 由 Codex 於新工作階段讀取；這個檔案不等於「已啟動自動監控服務」。
- `docs/` 可由 GitHub Pages 發布，詳細操作見 `docs/README.md`；本資料包尚未代替你建立 GitHub 儲存庫。

最後更新：2026-11-18。

## 自動更新簡報的範圍

- **已實作**：每次透過 `scripts/query_wiki.py` 查詢（包含查無結果），會檢查 Raw、Wiki 和 Graph，並重新生成 HTML 與最近查詢紀錄。增加作品後不再被 10 部的硬編碼卡住。
- **已實作**：`scripts/sync_slides.py --reason ingest` 可於已驗證 Ingest 後主動同步；失敗時保留舊的 HTML、快照及來源對照。
- **仍需 Codex／使用者**：把自然語言需求映射成 Query 條件、獲授權的連網搜尋與來源 Ingest、重新查詢；查詢腳本本身不能爬網或持續背景運作。
- **其他限制**：這仍是靜態 HTML，每次需要更新檔案、瀏覽器重載；若已部署 GitHub Pages，須推送新檔案。作品比較與教學例子等固定文案有重大變動時，Codex 應另外檢閱並更新模板。

**免費分類搜尋修復（2026-11-23）：** 修正「科幻」查詢時因 AniList 500 且 Kitsu 僅能名稱搜尋而無結果的問題。現在加入 Jikan v4 免費類型備援，詳見 `FREE_API_README.md`。
