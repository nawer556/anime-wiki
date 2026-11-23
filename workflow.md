# Anime Wiki｜工作流程設計（由 AGENTS.md 正式執行）

## 資料分層

1. `raw/sources/`：每個 SRC 不可覆寫的來源摘要，含原始 URL／日期；原網站保持真正權威來源。`manifest.json` 只是索引。
2. `staging/`：新來源的暫存整理，先核對作品身分、來源與關鍵硬性條件。
3. `wiki/`：由 AI 持續維護的 Markdown 資料庫，包含 Works、Series、Genres、Themes、Recommendations、Comparisons。
4. `index.md`：內容索引；`log.md`：append-only 操作歷史；`records/runs/`：每次詳細執行報告。

## Ingest：來源 → Wiki

1. 讀取 URL 或使用者提供的授權資料，為每份來源指派唯一 `SRC-###`。
2. 保存可追溯的來源 metadata 和短篇自行改寫摘要，不重製他人文章全文。
3. 核實作品身分 (`media_type`, 作品／系列／季度／劇場版)、來源可讀性與關鍵資訊。
4. 先將新作品的更新計畫置於 `staging/`，檢查是否與現有 ID 或欄位衝突。
5. 僅將合格欄位寫入 Wiki；不確定的片長／季數等留空或標示 unknown。
6. 同步維護 genre/theme/series/index 及來源引用，檢查通過才接受本次更新。
7. 在 `log.md` 追加事件，另於 `records/runs/` 保存檢查結果和問題。

## Query：Wiki → 有來源的答案

1. 讀取 `index.md`，依問題找到相關的 Works、Genres、Themes 頁面。
2. 硬性條件優先，例如電影格式或片長上限；未知不能視為符合。
3. 再比較軟性條件，給出高度符合／部分符合／資訊不足，不捏造百分比。
4. 回答時提供 `[[葬送的芙莉蓮]]` + `SRC-ID` + 原始 URL，將編輯標籤和事實明確區分。
5. 有價值的比較可經驗證後另建比較頁；單次回答不可無條件自動寫回 Wiki。
6. 如無符合作品，輸出 `AUTO_INGEST_REQUIRED`，由可上網的 Codex 工作階段啟動受限搜尋 → Ingest → Lint → 重新 Query。

## 自動擴充上限

- 最多 2 輪搜尋／驗證、每次最多新增 3 部已驗證新作品。
- 基本資料至少 1 個可靠來源，關鍵衝突再找第 2 個來源。
- 不能無限搜尋，也不能放寬明確限制；仍無匹配應誠實回報。
- 目前純本機查詢腳本不含網路搜索；本專案由根目錄 AGENTS.md 指導有網路授權的 Codex 工作階段執行；純 Python 查詢仍不連網。

## Lint

檢查作品 ID、來源 ID、必要欄位、格式、相對 Markdown 連結、Obsidian Wiki Links、genre/theme 檔案是否存在，另外以人工或 Codex 複核內容是否和來源一致，以及是否出現過時或矛盾敘述。

## 更新衝突與回滾

- 不直接覆寫 raw source；有新資訊就另存新來源。
- 舊作品如果出現資料衝突，將衝突欄位放在 staging，先查證再更新。
- 建議以 Git commit 保存每個合格 Ingest checkpoint，避免半完成的 Wiki 被保留。
- 日誌追加不可用成功事件抹掉失敗事件；真實錯誤與修正需分別紀錄。

## 製作 HTML 簡報（已完成第一版：2026-11-18）

1. 以 `raw/manifest.json` 和 `wiki/works/*.md` 建立固定 Wiki 快照：`docs/assets/wiki-snapshot.json`。
2. `scripts/build_slides.py` 以 `scripts/templates/deck.html` 產生 `docs/index.html`，其中嵌入相同資料快照，可離線操作。
3. 透過 `records/slide-sources.md` 保存每張投影片 → Wiki 頁面 → SRC-ID 對照，保持事實與主觀推薦標籤分離。
4. `scripts/check_slides.py` 驗證投影片數、來源連結、Wiki 欄位一致性與未知片長處理；另以瀏覽器執行鍵盤切換、作品篩選、推薦與查無結果測試。
5. 正式輸出為 10 張靜態教學投影片。**每次本機 Query 都自動重建快照與 HTML**，新作品也會加入作品地圖、互動推薦和來源清單；固定的教學比較段落仍需 Codex 內容複核。
6. 本機推薦試玩不執行網路搜尋或 Ingest；後續 Codex Agent 才能在獲授權的環境中擴充 Wiki。

詳見 `docs/README.md` 與 `records/runs/slide-build-check.md`。

## 2026-11-18：增量 Ingest 實作示範

本版已新增 SRC-012（JFDB《你的名字。》107 分鐘），修改既有 W007 作品頁，新增「兩小時內的動畫電影」的可追溯推薦頁，同步更新索引與歷史記錄；SRC-004 未被覆寫。新增 `raw/checksums.json` 及 `scripts/check_sources.py`。檢查命令與限制見 `records/runs/ingest-src012-jfdb.md`。

本例為**已完成的單筆外部來源核對與 Wiki 更新**，不是 Codex 自動啟動的無人值守網路搜尋測試；後者仍須在使用者的 Codex 工作階段檢查網路權限與實際工具行為。

## 2026-11-19：每次搜尋完成自動更新 HTML（新增）

`Query CLI` → `Raw Sources 檢查` → `Wiki Lint` → `Graph Audit` → `寫入 last-query.json` → `重新建立 10 張靜態 HTML / Wiki 快照 / 引用對照` → `Slide Lint` → `保留成功版本 + append-only log`。

- 查詢有結果或查無結果都執行更新。若 Wiki 不合格、建置或檢查失敗，保留原 HTML，不用損壞的新資料覆蓋。
- `AUTO_INGEST_REQUIRED` 本身不會連網。由 Codex 取得授權、依規範有限次 Ingest，再重跑相同 Query 觸發第二次更新。
- 新增的作品不再受到「只能 10 部」的建置限制，作品圖譜超過十部時可捲動。
- **本機檔案自動更新 ≠ GitHub Pages 自動部署**；公開網址需 commit/push。瀏覽器離線快照本身也不具自動爬蟲能力。

## 公開網站的自動擴充工作流程（新增）

訪客搜尋 → GitHub Pages 已驗證 Wiki JSON 篩選 → 若沒有結果且已啟用後端，Cloudflare Worker 受限入隊 → GitHub repository_dispatch → Actions 日額度檢查 → OpenAI Responses web_search → 來源頁基本核對 → 原始來源新增（絕不覆寫） → Wiki 作品／類型／主題／索引增量更新 → sources/Lint/graph → 重新生成 10 張 HTML → check_slides → GitHub push → Pages 部署。

- 預設關閉 AI：`DISPATCH_ENABLED=false`、`AUTO_INGEST_ENABLED` 不為 `true` 或無 `OPENAI_API_KEY` 時不會產生付費模型呼叫。
- 初版每次只找 1 部作品；若來源無法核對或對應硬性片長條件不符，拒絕加入正式知識庫。
- Worker 的 KV 限額只能提供基本防護，並不保證完全防止並發；為控制 API 費用，Actions 以序列化流程與日記帳減少重複收費，仍需 OpenAI 平台的預算保護。
- 目前 `docs/search.html` 是**瀏覽器離線快照查詢**而不是語意 LLM Query；查無結果不代表全網沒有該作品。
- 來源網頁可取得且有片名僅達最低來源驗證，對來源的專業性、語意與版權仍應做人工檢查。

## 訪客提交收錄申請 → 管理者審核的免付費工作流程（2026-11-23）

```
訪客搜尋 Wiki 外作品
    ↓
AniList / Kitsu / 離線參考結果
    ↓
「申請加入 Wiki」→ GitHub Issue（需訪客登入）
    ↓
管理者核對來源／ID／媒體類型與是否重複
    ↓
[管理者套用 approved-ingest 標籤]
    ↓
GitHub Actions 依 ID 重新查免費 AniList 或 Kitsu API
    ↓
基本來源驗證 → Ingest Raw & Wiki → Lint
    ↓
更新 index / log / slides / 靜態 Wiki 快照
    ↓
commit → GitHub Pages deploy → 關閉 Issue

如果 API 失敗、來源矛盾或 Lint 失敗：停止，不提交 Wiki 更新，Issue 保留待修正。
```

這個系統不需要訪客取得 GitHub 寫入憑證或公開 API 金鑰。`approved-ingest` 由**個人儲存庫擁有者**加上才可觸發。Jikan 與離線參考作品必須補充 AniList／Kitsu 可核對 ID，才能進入自動 Ingest。

部署細節參閱 [APPROVAL_SETUP.md](APPROVAL_SETUP.md)。
