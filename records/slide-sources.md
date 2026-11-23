# HTML 教學簡報 ↔ Anime Wiki 來源對照

> 生成時間：2026-11-20T06:40:42+00:00（UTC） · Wiki 來源索引日期：2026-11-18。
> 作品 10 部（TV 6、電影 4），來源 12 份。
> 由 `scripts/build_slides.py` 讀取已驗證的 Wiki 生成固定 HTML；每次本機 Query 會自動重新生成並檢查。

| 頁次 | 教學內容 | Wiki 根據 |
|---|---|---|
| 01 | 封面、知識庫統計 | `index.md`、`raw/manifest.json` |
| 02 | 如何選作品 | `wiki/recommendations/推薦方法.md` |
| 03 | TV 與電影，片長已驗證樣例 | `wiki/works/*.md` 與各自 SRC-ID |
| 04 | 類型與主題 | `wiki/genres/奇幻.md`、`wiki/themes/成長.md` |
| 05 | **全部 10 部作品地圖** | 全部 `wiki/works/*.md`；詳見下表 |
| 06 | 類型比較案例 | `wiki/comparisons/奇幻作品比較.md`、`wiki/comparisons/運動作品比較.md` |
| 07 | 混合推薦規則 | `wiki/recommendations/推薦方法.md`、`workflow.md` |
| 08 | **最近一次 Query 結果 + 互動推薦** | `records/last-query.json`、`docs/assets/wiki-snapshot.json`、作品各自 SRC-ID |
| 09 | Wiki → 投影片工作流程 | `workflow.md`、`log.md`、`raw/manifest.json` |
| 10 | 全部原始來源連結 | `raw/manifest.json` |

## 第 5 頁作品清單與來源追溯

| 作品 | Wiki 頁 | 來源 ID |
|---|---|---|
| W001 · 葬送的芙莉蓮 | `wiki/works/葬送的芙莉蓮.md` | SRC-001 |
| W002 · SPY×FAMILY 間諜家家酒 | `wiki/works/SPY×FAMILY 間諜家家酒.md` | SRC-002 |
| W003 · 排球少年！！ | `wiki/works/排球少年！！.md` | SRC-003 |
| W004 · 孤獨搖滾！ | `wiki/works/孤獨搖滾！.md` | SRC-006 |
| W005 · 輝夜姬想讓人告白 | `wiki/works/輝夜姬想讓人告白.md` | SRC-007 |
| W006 · ODDTAXI 奇巧計程車 | `wiki/works/ODDTAXI 奇巧計程車.md` | SRC-008 |
| W007 · 你的名字。 | `wiki/works/你的名字。.md` | SRC-004, SRC-012 |
| W008 · 聲之形 | `wiki/works/聲之形.md` | SRC-005, SRC-011 |
| W009 · 神隱少女 | `wiki/works/神隱少女.md` | SRC-009 |
| W010 · 灌籃高手 THE FIRST SLAM DUNK | `wiki/works/灌籃高手 THE FIRST SLAM DUNK.md` | SRC-010 |

## 最近一次 Wiki 搜尋

{
  "searched_at": "2026-11-20T06:40:38+00:00",
  "filters": {
    "type": "movie",
    "genre": "戀愛",
    "theme": null,
    "mood": null,
    "max_minutes": 120
  },
  "status": "MATCH",
  "total_matches": 1,
  "matches": [
    {
      "id": "W007",
      "title": "你的名字。",
      "score": 1,
      "wiki_path": "wiki/works/你的名字。.md",
      "source_ids": [
        "SRC-004",
        "SRC-012"
      ]
    }
  ],
  "unknown_durations": [],
  "note": "Offline query only. NO_MATCH requires a separate, authorized Codex auto-ingest; re-query after Ingest."
}

## 說明與限制

- 每次本機 CLI 查詢（含無結果）都更新靜態 HTML、作品地圖、互動推薦快照、來源清單與最近 Query；瀏覽器本身不會連網或自動 Ingest。
- 新作品經驗證 Ingest 後，須再次 Query 或執行 `python scripts/sync_slides.py --reason ingest`。
- 第 2、4、6、7、9 頁包含固定教學或比較敘述；若相關 Wiki 內容有重大更動，Codex 應人工核對並修改模板，不應宣稱完全語意自動更新。
- 只有經證實的片長才參與精確分鐘篩選，來源可沿作品頁追至 Raw Source URL。
- 類型／主題／情緒標籤是 Wiki 編輯歸納，非客觀評分。
