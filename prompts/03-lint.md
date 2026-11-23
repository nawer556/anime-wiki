# 貼給 Codex｜執行 Lint 與健康檢查

請先讀 AGENTS.md、index.md 和 log.md 最近的事件。依序執行：

python scripts/check_sources.py
python scripts/lint_wiki.py
python scripts/audit_wiki.py
python scripts/check_slides.py

另外請你親自閱讀相關頁面，找出可能的跨頁矛盾、過時資訊、缺失來源、系列與電影混淆、孤兒頁、應補充的交叉連結。工具 PASS 不代表事實已被查證。請將發現、修正建議與實際驗證結果存到 records/runs/ 並追加 log.md。不要把模擬錯誤當成真實執行結果。
