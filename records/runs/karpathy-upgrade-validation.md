# Karpathy 風格 Anime Wiki｜本次最終驗證紀錄

> 2026-11-18；本檔描述實際在本次專案製作時所執行的工具與產生的結果。命令預設從專案根目錄執行。

## 1. Wiki 來源完整性

`python scripts/check_sources.py`

```text
RAW PASS: 12 immutable source files verified
```

備註：這檢查本機已保存 Raw 筆記的 SHA-256，**不是自動驗證外站內容正確性**。新來源 `SRC-012` 的電影片長 107 分鐘，是根據 JFDB 頁面資料核對；舊來源完整保留。

## 2. 結構與知識關聯

`python scripts/lint_wiki.py`

```text
WIKI LINT: 10 works; 12 sources; 75 Markdown pages
Errors: 0 | Warnings: 0
```

`python scripts/audit_wiki.py`

```text
WIKI GRAPH AUDIT:
  wiki_pages = 44
  wiki_crosslinks = 81
  possible_orphans_excluding_index = []
  duplicate_page_titles_to_watch = {"青春": ["wiki/genres/青春.md", "wiki/themes/青春.md"]}
  ambiguous_wikilink_uses = []
```

同名頁採明確相對路徑連結，不用含糊的 Wiki Link。語意性矛盾、資料新舊狀態仍需 Agent 人工/模型讀取來源檢查。

## 3. Query 真正重用了新的 Wiki 知識

```powershell
python scripts/query_wiki.py --type movie --genre 戀愛 --max-minutes 120
```

```text
Wiki candidates: 1
- 你的名字。: 高度符合; genres=戀愛、奇幻; source=SRC-004,SRC-012; page=wiki/works/你的名字。.md
```

```powershell
python scripts/query_wiki.py --type movie --genre 科幻
```

```text
NO_MATCH / AUTO_INGEST_REQUIRED
Offline Wiki has no verified matching title; Codex with network access must run the Ingest-Lint-Query loop. Do not invent results.
```

**這不是已完成的自動搜尋網路示範**；本機查詢如實標出知識缺口。

## 4. 靜態 HTML 一致性

`python scripts/build_slides.py`、`python scripts/check_slides.py`

```text
BUILD PASS: 10 works, 12 sources → docs/index.html
SLIDE LINT PASS: 10 slides; 10 works; 12 sources; 12 source links
Wiki snapshot matches Markdown metadata; offline resources embedded; unknown durations excluded (6 entries).
```

附帶使用 headless Chromium（Playwright，**非專案基本必需套件**）以相同 HTML 文字載入進行互動測試：

```text
BROWSER PASS: 10 slides, navigation, 12 source links, 107-min recommendation, 90-min honest no-match, no JS errors
```

沙盒禁止 `file://` 路徑導航，改以 `page.set_content()` 載入完全相同的 `docs/index.html`；沒有驗證使用者電腦上的瀏覽器／公開 Pages。

## 5. 已實際找到並修正的錯誤

1. **索引連結先於成果紀錄**：第一輪 Lint 找到 `index.md` 引用不存在的 `records/runs/ingest-src012-jfdb.md`；先建立實際紀錄再 Lint，之後通過。
2. **Staging 目錄假設錯誤**：測試中 `prepare_ingest.py` 在乾淨目錄出現 FileNotFoundError；加上 `mkdir(..., exist_ok=True)` 後通過。
3. **瀏覽器沙盒存取限制**：`file://` 被管理員封鎖；轉為使用相同檔案內容的 `set_content()` 驗證瀏覽器行為，不代表使用者本機開檔會失敗。

**因此工作流程調整為**：先建暫存目錄 → 準備/驗證來源 → 修改相關 Wiki → 建索引與執行紀錄 → 執行完整性/Lint → 必要時更新簡報並測試。這是可由 log 重現的實際修正，而非想像的失敗案例。

## 6. 自動測試套件

`python -m unittest discover -s tests -v`

```text
Ran 7 tests
OK
```

7 項涵蓋 Raw 不可變、Wiki Lint、簡報一致性、Query 正向與無結果、在隔離暫存副本中偵測 Raw 篡改，以及 staging 不更動正式 manifest。此檢查不需額外 pip 安裝。

## 7. 仍需在使用者 VS Code / Codex 完成的操作

- 讓 Codex 在自己有權限的工作階段讀取 `AGENTS.md` 並接受一次 Ingest／Query／Lint 任務。
- 給 Codex 透過網路搜尋到新動漫的實際測試，證明受限 2 輪／最多 3 部的 Auto Ingest 能正常完成。
- 如果老師要求公開「LLM Wiki 連結」，將此儲存庫推送到 GitHub；如果要求簡報網址，再啟用 GitHub Pages `/docs`。
