> **重要更新（2026-11-23）：** Jikan 官方公共 API 已在 2026 年 10 月 1 日停止服務，舊版搜尋程式可能仍會嘗試備援，但正式審核後入庫**僅使用 AniList／Kitsu**，不可依賴已停用的 Jikan。來源：<https://github.com/jikan-me/jikan-rest/issues/613>。

# Anime Wiki｜多語名稱＋動漫類型搜尋（2026-11-23）

本次升級修正兩件事：**中文名稱不能搜尋**、**搜尋「科幻」時外部 API 連線失敗或一直等候**。

## 如何使用

從 VS Code 以 Live Server 開啟 `docs/search.html`，或在專案根目錄執行：

```powershell
python -m http.server 8000 --directory docs
```

瀏覽器開啟 `http://localhost:8000/search.html`。

建議測試：

| 輸入 | 預期解讀 |
| --- | --- |
| `命運石之門`／`命运石之门` | 轉為 `Steins;Gate`，搜尋同一部動漫 |
| `Steins;Gate` | 英文名稱搜尋 |
| `シュタインズ・ゲート` | 日文名稱搜尋 |
| `科幻`／`science fiction`／`サイファイ` | Sci-Fi 類型搜尋，**不是作品名稱** |
| `戀愛`／`恋爱`／`romance` | Romance 類型搜尋 |
| `推薦科幻懸疑動畫電影` | Sci-Fi＋Mystery＋Movie 篩選 |

## 運作方式

1. 本站先搜尋原有的 Markdown Wiki 快照（已驗證作品）。
2. 外部查詢在瀏覽器執行；中文作品名稱先以內建**常見譯名對照表**轉成英文查詢。若名稱不在表中，且是中文，會嘗試 Wikipedia 的中文條目跨語言連結。後者需要網路，不保證所有中文名稱都能找到對照。
3. 中文、英文與日文類型關鍵字會轉成資料 API 的 `genre`；Jikan 支援以類型 ID（例如科幻 24）搜尋，AniList 也能用 `genre_in` 過濾。
4. Jikan 和 AniList 同時查詢、採用最先成功回傳非空結果的資料；都沒有結果才在作品名稱搜尋時嘗試 Kitsu。每次 API 有逾時上限，不會無限制等待。
5. 當免費 API 故障、受流量限制或找不到結果時，如有可用條件，**顯示預先整理的離線參考清單**。它不是即時 API 結果，也不是已驗證的 Wiki；頁面會明確顯示「離線參考 · 非即時」。點選連結可到 MyAnimeList 搜尋核對作品。
6. 外部搜尋和離線參考**都不會寫入正式 Wiki，也不會更新 HTML 教學簡報**。正式 Ingest 仍須由管理者執行來源驗證 → Lint → 簡報重新建置。

**限制：** 免費 API 的網路穩定性由第三方決定。對照表並非涵蓋所有中文譯名；Wikipedia 跨語言連結若查不到，仍可能需要英文或日文作品名稱。離線參考資料只有名稱、類型與形式，缺少已驗證片長時絕不通過片長上限篩選。

## 驗證方式

```powershell
node --test tests/test_anilist_api.cjs
python scripts/lint_wiki.py
python scripts/check_sources.py
python scripts/check_slides.py
```

本版實際驗證：11 項 JavaScript 測試、Wiki/Raw/簡報檢查通過；瀏覽器使用**模擬 API 全故障**的情境驗證「科幻」顯示 12 部離線參考，以及三種語言查詢《命運石之門》的結果。**未在此執行環境驗證真實外部 API 連線成功**。

API 參考：
- AniList：<https://docs.anilist.co/guide/graphql/>
- Jikan：<https://jikan.moe/>
- MediaWiki 跨網域存取：<https://www.mediawiki.org/wiki/API:Cross-site_requests>
- Kitsu：<https://kitsu.docs.apiary.io/>

這是唯讀、非商業課程展示搜尋，不應大量抓取資料。請遵守各服務條款與使用頻率限制。
