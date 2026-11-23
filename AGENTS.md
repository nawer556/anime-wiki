## 訪客提出新增動漫的審核流程（2026-11-23）

- 訪客的外部搜尋結果不能直接寫入 `wiki/` 或 `docs/index.html`。點擊「申請加入 Wiki」只建立預填的 GitHub Issue，不能包含任何存取金鑰。
- **個人 GitHub 儲存庫擁有者**需核對來源、正確的作品（TV／電影、系列與季數）以及 AniList／Kitsu ID，確認無重複後才加上 `approved-ingest` 標籤。
- `.github/workflows/approved-ingest.yml` 只在儲存庫擁有者實際加上標籤時執行。程式使用 `scripts/approved_issue_ingest.py`，只信任固定來源 API 端點，不執行 Issue 文字，也不將不明網址當作資料來源。
- 匯入時遵循現有 Ingest → Lint → 更新 `raw/manifest.json`、`raw/checksums.json`、`wiki/`、`index.md`、`log.md`、`docs/index.html`、`records/`。若查核失敗，禁止提交已驗證的知識變更。
- AniList／Kitsu 資料只達基本結構驗證，主題、推薦語意與劇情細節仍需人工校訂；不得宣稱 API 的每一項資料都經官方雙重驗證。
- 公開 Jikan API 在 2026-10-01 停止服務，且離線示例未查證；不能拿這兩類結果當正式 Ingest 的唯一資料來源。

---

# AGENTS.md — Anime Wiki 的 Codex 知識維護規範

> 這份檔案是專案的 Schema：讓 VS Code + OpenAI Codex 持續維護 Wiki，而不只是每次聊天臨時產生摘要。設計參考 Andrej Karpathy 的 LLM Wiki 模式：https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
> 操作語言：繁體中文；作品原文名稱與專有名詞可以保留原文。

## 0. Codex 的角色與最重要的要求

你是 Anime Wiki 的知識庫維護者，須以**現有 Wiki 為起點增量整理**資料。使用者負責選題與審核方向；你負責來源歸檔、整合、多頁同步、查詢、檢查與紀錄。

- **每個查詢先讀根目錄的 `index.md`**，再讀相關的 Wiki 頁面與 `raw/` 來源；不要每次跳過 Wiki 從網路零散重建答案。
- **新資料必須融入既有 Wiki**：不是只新增來源或摘要；評估是否要同步修改作品、類型、主題、系列、比較、推薦頁與索引。
- **不要杜撰事實、時間、來源、作品 ID、評分或已執行的工具結果**。不確定就用 `null`、`unknown` 或「待查證」。
- 與本專案互動時清楚區分「已實際執行」和「設計上支援／尚未執行」，尤其是網路自動搜尋與簡報更新。
- 保持無劇透；禁止大段搬運有著作權的原始網站內容或未授權圖像。
- 尊重工作目錄既有修改；**不得使用 `git reset --hard`、`git clean -fd` 或其他可能移除他人工作的命令**。

## 1. 三層知識架構

| 層 | 位置 | 目的與約束 |
|---|---|---|
| Raw Sources | `raw/sources/SRC-###.md` + `raw/manifest.json` | 永久保留來源 URL、擷取日期、可核對事實及簡短自行改寫摘要。單份 `SRC` 寫入後**不得覆寫或刪除**；發現來源變動時另增 `SRC`。`raw/checksums.json` 用於偵測篡改。manifest 可追加新條目但不可竄改歷史內容。 |
| Wiki | `wiki/` | AI 維護的持久 Markdown 知識頁；可在驗證後增量更新既有頁、交叉連結與編輯性綜合分析。 |
| Schema | **本 `AGENTS.md`** + `schema/` | 指定 frontmatter、來源、Ingest／Query／Lint／Auto-expand 工作流程和驗證條件。 |

根目錄 `index.md` 是**內容索引**，應列出每篇 Wiki 頁、相對連結、概要及來源；`log.md` 是**時間順序 append-only 日誌**，不可覆蓋舊紀錄；`records/runs/` 保存每次執行的細節與檢查輸出。`staging/` 是未驗證工作區，不得作為正式推薦依據。

## 2. 頁面規範與追溯

- 作品頁：`wiki/works/<中文作品名>.md`；frontmatter 主要欄位 `id`、`title`、`original_title`、`media_type` (`tv`/`movie`)、`release_year`、`duration_minutes`、`genres`、`themes`、`moods`、`pacing_editorial`、`source_ids`、`verification`、`last_reviewed`。依 `schema/work-page.md` 製作。
- `W###` 是不可重複的作品 ID；**系列、季度與劇場版要先辨識**，不得把 TV 季數當成電影片長、將同一作品的新資料建成重複條目。
- 已知片長填整數分鐘；未知填 `null`，絕對不能通過「N 分鐘以內」的硬性條件。年代、集數與首播/上映日期也不可用推測補足。
- 作品的客觀事實需有引用 `SRC-###`，並能找到相應的 Raw Source URL；主題、情緒與節奏等推薦標籤需明確註明是**Wiki 編輯性歸納**，不冒充官方評分。
- 建立/維持 `[[Obsidian Wiki Links]]` 與可點擊的相對 Markdown 連結；相對路徑必須有效；避免孤兒頁與同名衝突。例如「青春」同時是 `genres/` 和 `themes/` 頁面，請使用有明確路徑的相對 Markdown 連結，不要使用含糊的 `[[青春]]`。

## 3. Ingest：新來源 → 更新既有知識

啟動條件：使用者指定新來源，或符合 Query 無結果時的受限自動擴充。**逐個來源處理**，同一輪不要無限制批量匯入。

1. `git status --short` 記錄起始狀態；讀 `index.md`、相關 works/genres/themes/series、`raw/manifest.json` 和最近的 `log.md`。先確認此來源 URL 是否已存在、作品是新條目或既有作品的補充資料。
2. 以可靠來源取得事實：官方網站／發行商優先，可信資料庫補充；如關鍵事實互相矛盾，再找第二個獨立來源。閱讀網頁須依使用者的網路權限與工具實際可用性；**不能假裝已讀取無法開啟的網頁**。
3. 在 `staging/` 形成來源筆記與修改計畫，可執行 `python scripts/prepare_ingest.py --title "..." --url "https://..." --publisher "..." --work-id W###` 建立未驗證範本；這個腳本**不會上網、不會自行驗證或更新正式 Wiki**。
4. 核對來源身分、作品/系列/季度/劇場版、片長等硬性欄位及引用依據。確認至少一份可信來源；有重要衝突要留在 staging 待查，不能以最新或最方便的敘述無聲覆蓋。
5. 僅通過驗證後，**新建** `raw/sources/SRC-###.md`，向 manifest 追加來源 metadata，並在確認新檔可信且沒有更動舊來源後執行 `python scripts/check_sources.py --add-new` 建立新 source checksum；舊 `SRC` 檔案嚴禁修改。來源筆記只保留足夠證據的精簡改寫，不複製整篇文章。
6. 更新相關作品頁（frontmatter、事實、SRC 與註腳），**同步檢查并修改**必要的類型／主題／系列／推薦／比較頁；重建 `index.md` 的摘要與計數。新來源若只改變既有資料，也要顯示它如何改進既有知識。
7. 執行 `python scripts/check_sources.py`、`python scripts/lint_wiki.py`、`python scripts/audit_wiki.py`。**正式 Ingest 通過後要執行** `python scripts/sync_slides.py --reason ingest`。若本次 Ingest 是由查無結果觸發，接著必須再執行原始條件的 `python scripts/query_wiki.py ...`，它會自動更新「最近一次搜尋」及簡報。
8. 如任何檢查失敗，停止宣稱 Ingest 成功，將不合格修改留在 staging 或只回退**本次自己改動**；記錄 FAIL、原因及 Retry。檢查通過才追加成功日誌，寫 `records/runs/<run-id>.md`，列出來源、受影響頁、Lint、仍存在的警告、是否實測網路。

## 4. Query：從 Wiki 回答，而非重新發明資料

1. 先讀 `index.md` → 相關作品/類型/主題/比較頁 → 必要時查 `raw/sources` 與 manifest。
2. 抽取需求：**硬性**（tv/movie、片長、單部可看完、排除題材等），**軟性**（類型、主題、心情、節奏），以及資訊不足欄位。
3. 硬性先排除不符合／未知的作品；其餘依軟偏好篩選，回覆最多 3 部，使用「高度符合／部分符合／資訊不足」，**不得編造精確百分比**。
4. 每個作品提供 `Wiki 作品頁 → SRC-### → 原始網址` 的追溯鏈；分清官方事實與 Wiki 推薦觀點。
5. 有價值的新比較可以經驗證後回寫 Wiki；不是所有聊天內容都自動寫入。
- **每次推薦／搜尋必須使用** `python scripts/query_wiki.py ...` 完成最後的可重現 Query。它預設會自動執行 `check_sources → lint_wiki → audit_wiki → build_slides → check_slides`，更新 `records/last-query.json`、`docs/assets/wiki-snapshot.json`、`docs/index.html`、`records/slide-sources.md`，並在 `log.md` 留下 PASS / FAIL。
- 例如 `python scripts/query_wiki.py --type movie --genre 奇幻 --max-minutes 120`；若使用者用自然語言詢問，應先轉成可支援的篩選條件再執行。原有離線工具不能代表所有複雜語意篩選；未支援的需求要坦白說明，必要時交由 Codex 查閱 Wiki 並在答覆後執行 `python scripts/sync_slides.py --reason query`（這種方式只重建快照，不會把完整語意查詢紀錄寫入 `last-query.json`）。
- **即使沒有匹配作品也要完成同步**，在簡報第 8 頁呈現最近查詢的「查無結果」。若使用了授權的自動 Ingest，完成後必須**重新執行同條件 `query_wiki.py`**，讓新作品出現在簡報。
- 查詢腳本**不會上網**，`AUTO_INGEST_REQUIRED` 是交給有權限的 Codex 的信號，不是自動連網已完成的證明。`--no-sync` 僅供唯讀開發診斷，不得用於一般搜尋。

## 5. 無結果自動擴充（使用者已選 B）

當 Query 找不到符合硬性限制／足夠偏好的候選時，在**具網路權限且使用者同意其存取設定**的 Codex 工作階段：

- 最多 **2 輪搜尋／查證**，同次最多**新增 3 部**經驗證的新作品；不可無限重試。
- 用原定硬性條件搜索候選，重複作品先補充既有頁；新來源依第 3 節 Ingest（staging → 來源驗證 → 多頁更新 → Lint → log）。
- 僅合格作品才能重新 Query；未通過者不進正式推薦。仍找不到則說明無結果／已達上限，**不擅自放寬**使用者條件。
- **這是 Codex 按規則在任務執行期間採取的動作**；本 repo 未內建長駐自動監控、排程、無人值守網路爬蟲。離線腳本提示 `AUTO_INGEST_REQUIRED` 不等於已經連網完成。
- 不要把 AI 自己推測的來源存成已驗證 Raw Source。

## 6. Lint：結構檢查 + 內容審核

- 每次 Ingest 前/後、重要 Query 前、生成 HTML 前都跑結構工具，檢查來源 ID 與 URL、重複 ID、media_type、必填欄、跨頁連結、片長未知狀態。
- 結構工具**不能取代** Codex 對來源事實、同系列重複建檔、來源更新、互相矛盾、過時內容、缺失概念和孤兒頁的語意審查。
- 持續保存實際 FAIL→修正→PASS 的詳情，不把模擬錯誤寫成真實結果。

## 7. HTML 簡報與交付

- `docs/index.html` 仍是**靜態**教學投影片；瀏覽器開啟本身不會連網查詢或 Ingest。**但每次在 VS Code／Codex 呼叫 `python scripts/query_wiki.py` 搜尋後，會自動重新建置 `docs/index.html`**，第 5 頁作品地圖、第 8 頁最近搜尋結果／互動推薦資料、來源清單都會更新。
- 正式 Ingest 後也要透過 `python scripts/sync_slides.py --reason ingest` 更新簡報，若源於查無結果，必須重新 Query。同步失敗時**保留上一次有效 HTML**，不可宣稱成功。
- HTML 靜態教學比較段落仍可能需要 Codex 人工複核，不能把自動重新建置等同於所有敘述均已語意驗證。資料對照記錄：`records/slide-sources.md`。本機瀏覽器原有開啟的頁面需要重新整理（Live Server 可自動重載）。
- 來源與 Wiki 成果可上傳 GitHub；`docs/` 可用 GitHub Pages 發布。未部署前**不宣稱有公開 URL**。

## 8. 完成任務前報告格式

- 本次操作：Ingest / Query / Lint / Slides，實際處理的來源及作品。
- 修改頁面：列出相對路徑和更新原因。
- 驗證結果：實際執行的指令、PASS／FAIL 與已知警告。
- 來源與局限：Raw SRC ID、URL；未確認欄位；有無執行網路擴充。
- 紀錄位置：`log.md` 與 `records/runs/<run-id>.md`。

## 9. 建議起始指令（Windows VS Code 終端機）

```powershell
python scripts/check_sources.py
python scripts/lint_wiki.py
python scripts/audit_wiki.py
python scripts/query_wiki.py --type movie --genre 戀愛 --max-minutes 120  # 這個指令同時更新簡報
python scripts/sync_slides.py --reason ingest  # Ingest 完成後使用
python scripts/check_slides.py
```

Windows 若找不到 `python`，請用 `py`；不要為了本專案引入未必要的套件。若要大量改動檔案，先讓使用者看懂改動規劃，保持可回復的 Git checkpoint。

## 10. 公開搜尋網站與後端擴充（2026-11 新增）

- `docs/search.html` 是公開動漫搜尋與推薦入口；`docs/index.html` 保留為 10 頁 HTML 教學簡報。二者都讀取 `docs/assets/wiki-snapshot.json`，正式上線由 GitHub Pages 提供。
- **訪客查詢已有作品只用瀏覽器 JS**，不消耗 OpenAI API；網站提供作品與 SRC 原始來源連結。
- 當訪客主動提交搜尋且無匹配作品、並已配置 `window.ANIME_API_BASE` 時，前端呼叫 Cloudflare Worker `POST /request`，Worker 過濾不安全輸入、做每日/每 IP 和重複搜尋限制，然後用秘密 GitHub Token 觸發 `repository_dispatch`。絕不能在 `docs/` 儲存金鑰。
- **費用安全預設關閉**：`backend/wrangler.jsonc` 的 `DISPATCH_ENABLED` 必須是 `false`，且 GitHub 變數 `AUTO_INGEST_ENABLED` 未明確設 `true` 時不得呼叫 OpenAI。只有使用者自行設定 GitHub Secret `OPENAI_API_KEY` 後才能真正啟用。
- GitHub Workflow `.github/workflows/auto-ingest.yml` 串行處理，預設每天最多 3 次付費搜尋嘗試，每次最多 1 部作品；`scripts/auto_ingest.py` 會驗證來源可取得、頁面含作品名稱與 TV/電影形式線索，檢查 metadata、來源不可覆寫、跨頁引用、Lint 和 HTML，再把合格作品推送並重新部署網站。
- 已存在作品或來源、來源無法存取、來源形式不清楚、時長無證據、或驗證失敗時**不要上傳到正式 Wiki**；片長未知不能被當成通過精確片長限制。來源可取得不等於所有內容已二次事實查核。
- 以 GitHub Actions 自動更新前，必須保留 `raw/`、`wiki/`、`index.md`、`log.md` 與 HTML 的一致性；任何資料／簡報驗證失敗都保留上次有效版本。
- 部署與權限設定參考 `DEPLOYMENT.md`。本專案現在提供可運行程式與免費模式，不代表已替使用者在第三方帳號部署或啟用付費 API。不要宣稱後端已上線，除非實際在公開網址驗證成功。

## 11. AniList 公開搜尋（2026-11-20 新增）

- `docs/assets/anilist-api.js` 在**瀏覽器**中呼叫 AniList GraphQL 公開端點 `https://graphql.anilist.co`，僅作**唯讀的外部動漫搜尋**；`docs/search.html` 以獨立區塊顯示「Wiki 已驗證」與「AniList 未收錄」。
- 其結果不得冒充 Wiki 的真實作品，不能直接增加 `raw/manifest.json`、`wiki/works/`、`index.md` 或簡報。若使用者希望收錄某作品，須明確執行 Ingest → 來源驗證 → Lint → HTML 重建。AniList 是外部資料庫來源，不等於權威的官方製作資訊。
- 須尊重 AniList 使用條款、請求頻率限制、禁止大量收集與以 API 作為備份資料庫；**非商業課程展示**可以用唯讀搜尋。前端不用金鑰，不得要求訪客付費。
- 任何 API 不可用／429／403 應顯示來源不暫時可用，不能虛構外部作品；Wiki 內原有資料仍可使用。
- `docs/index.html` 是 Wiki 快照的靜態教學簡報。**訪客透過 AniList 搜尋不會更新簡報**，若要更新需正式匯入經驗證作品並跑 `scripts/sync_slides.py`，重新發布網站。
- 來源與條款：https://docs.anilist.co/guide/graphql/ 、https://docs.anilist.co/guide/terms-of-use 、https://docs.anilist.co/guide/rate-limiting 。


## 12. 多語及類型搜尋（2026-11-23）

- `docs/search.html` 使用 `docs/assets/anilist-api.js` 提供唯讀的多語名稱搜尋、類型查詢（Jikan／AniList／Kitsu），以及 Wikipedia 中文名稱跨語言對照；此功能只在瀏覽器端執行。
- 免費 API 連線錯誤時，搜尋網頁可能顯示「離線參考 · 非即時」作品清單；這些是未經本專案來源驗證的候選範例，不能視為 Raw Sources 或 Wiki 事實，也不能直接用於正式教學簡報。
- 對任何外部候選，必須執行來源擷取、正式 Ingest、Lint、Wiki 連結與簡報重建後，才可以宣稱內容更新；訪客查詢不會自動寫入。
- 內容展示應明確分開三種來源：已驗證的 Wiki、即時第三方查詢、離線候選參考；不得將 API 逾時或無結果當成「不存在這部作品」。
- 中文名稱翻譯由對照表及 Wikipedia 跨語言連結輔助，沒有對照時必須說明限制，不可以假裝涵蓋全世界所有動畫。
- 詳見 `FREE_API_README.md`；可執行 `node --test tests/test_anilist_api.cjs` 驗證。
