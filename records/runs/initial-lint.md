# 初次 Wiki Lint 實際執行紀錄

- 日期：2026-11-18
- 工具：`python scripts/lint_wiki.py`
- 測試對象：本次生成的 Anime Wiki 專案資料夾
- 結果：**PASS**
- 作品頁：10
- Source 清單：11（10 份作品來源 + 1 份補充來源）
- Markdown 頁數：59（當次檢查統計）
- Errors：0
- Warnings：7

## 首輪發現與修正（真實執行）

1. 初次檢查時出現 30 個 Wiki Link 錯誤，原因是作品頁原本使用英文檔名，連結卻使用繁體中文作品名稱；另外說明文件中有未實際指向頁面的示意語法。
2. 修正方式：改以作品中文名稱命名 Markdown 檔，並同步更新普通 Markdown 相對路徑；移除說明文件內的不實示意 Wiki Link，調整 Lint 兼容 Obsidian 作品標題解析。
3. 第二次檢查：0 Errors，7 個 informational Warnings（未知片長，不可拿來通過精確時間篩選）。

## 為什麼要提前檢查？

在後續每次 Ingest 後立即檢查 Wiki Link，避免錯誤一路進入 Query／HTML 簡報階段。

> 注意：目前只執行結構性 Lint；未宣稱已完成所有人工作品細節交叉查證。
