# Anime Wiki 的作品頁 Schema

> 寫 Wiki 請以現有 `wiki/works/*.md` 頁面作具體範例；本文件記載一致性和新增規則。

| 欄位 | 型別 | 規則 |
|---|---|---|
| `id` | string | 唯一 ID，如 `W011`；已使用 ID 不改號 |
| `title` | string | Wiki 常用繁體中文作品名 |
| `original_title` | string | 日文正式作品名或官方原名 |
| `media_type` | string | 僅 `tv` 或 `movie`；作品影視改編衍生作要先辨識 |
| `release_year` | integer/null | 首播或上映年份，沒有來源時 null；不得假裝已驗證 |
| `duration_minutes` | integer/null | 單部電影片長；未知用 null；TV 不用總集數冒充 |
| `genres` / `themes` | string array | Wiki 編輯性標籤；每個項目應有對應分類 Markdown 頁 |
| `moods` | string array | Wiki 編輯性解讀，不是官方品質分數 |
| `pacing_editorial` | string | 節奏的編輯性歸納，不得冒充客觀評分 |
| `source_ids` | string array | 每筆重要可核查資訊需對應 Raw Source，不得指向不存在的 ID |
| `verification` | string | `basic_verified` / `needs_review` 等，不要假造已驗證 |
| `last_reviewed` | date string | 最後實際校對日（YYYY-MM-DD） |

正文最少包括：無劇透簡介、基本資料、類型/主題與雙向關聯、適合/不適合的觀眾、可核對的來源事實、原始來源 URL、資料缺口與維護提醒。

## 新來源處理

- Raw 是不可變的歷史筆記；官方網站或資料庫原始網址為核對的依據，不把 AI 改寫稱為原文。
- 若新增內容支持更精確的事實（例如確切片長），要修改**既有**作品頁而非重建相同作品。
- Wiki 頁的每一條新增事實應能追查到新舊來源 `SRC-###`；衝突時保留舊觀察並留註記，必要時暫緩發布。
- 更新索引和相關指南；有內容變化才更新推薦或比較頁，不為了湊數修改無關頁。

## 同名分類／主題的處理

目前「青春」同時出現在 `wiki/genres/` 與 `wiki/themes/`。此時不要使用沒有上下文的 `[[青春]]`，而應依實際頁面位置使用明確的相對 Markdown 連結，例如由作品頁指向 `../genres/青春.md` 或 `../themes/青春.md`。
