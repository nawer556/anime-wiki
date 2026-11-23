# Query 實測記錄

- 日期：2026-11-18
- 測試環境：本次生成 Wiki 的本機 Python 標準函式庫工具

## 測試一：已收錄的電影偏好

```powershell
python scripts/query_wiki.py --type movie --genre 奇幻
```

**實際結果**：回傳 2 個候選《你的名字。》與《神隱少女》，各附作品 Wiki 路徑及 SRC-004、SRC-009 來源 ID。

## 測試二：Wiki 無符合結果

```powershell
python scripts/query_wiki.py --type movie --genre 科幻
```

**實際結果**：`NO_MATCH / AUTO_INGEST_REQUIRED`。

**限制**：這只是離線查詢腳本的觸發訊號，不代表真的發生了網路自動搜尋／新增作品。自動擴充需後續在具有網路權限的 Codex 進行。
