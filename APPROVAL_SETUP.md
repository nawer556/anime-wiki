# Anime Wiki｜訪客申請 → 管理者審核 → 免費 API Ingest → 自動更新簡報

## 這個版本能做到什麼？

- 任何訪客可以在搜尋網站查閱未收錄動漫，點擊 **「＋ 申請加入 Anime Wiki」**。
- 瀏覽器開啟預填的 GitHub Issue；**訪客要有 GitHub 帳號並按提交**，申請才會成立。
- 訪客**沒有 Wiki 修改權限**，也無法透過搜尋觸發付費 AI。
- 你（個人 GitHub 儲存庫擁有者）核對來源與編號，**手動**套用 `approved-ingest` 標籤，啟動 GitHub Actions。
- 程式從免費 AniList／Kitsu API 重新取得作品，查核類型與身份、檢查重複、寫入 Raw Sources、Wiki、Index、Log、執行 Lint，接著重建 `docs/index.html` 和 `docs/assets/wiki-snapshot.json`，通過後才推送至 GitHub 並部署 Pages。

**不需要 Cloudflare Worker、OpenAI API 或額外 AI API 費用。** GitHub Issues、GitHub Pages 和公開儲存庫標準 GitHub Actions 可按其免費規範使用，但不保證 API 永遠可用。這不是即時自動批准：你仍需逐件審核。

## 一、上線前必做設定

1. 在 GitHub **個人帳號**建立一個公開儲存庫，例如 `Anime-Wiki`，將完整專案推送到 `main`。
2. 在儲存庫 **Settings → General → Features** 確認 Issues 已啟用。
3. 在 `docs/assets/repository-config.js` 設定 `window.ANIME_GITHUB_REPOSITORY = '你的GitHub帳號/Anime-Wiki';`，commit 並推送。若使用標準 GitHub Pages 網址，一般也可由程式自動辨識。
4. **Settings → Actions → General → Workflow permissions**：允許 GitHub Actions 具備讀取／寫入儲存庫權限（實際畫面名稱以 GitHub 為準），以便工作流程在核准後提交 Wiki 與簡報。
5. **Settings → Pages**：在 **Build and deployment** 選擇 **GitHub Actions**，不要改用「Deploy from a branch」，因為本專案工作流程會自行部署 `docs/`。
6. 若你啟用了 `main` 分支保護，須允許這個自動化以被允許的方式提交，或改為 Pull Request 人工合併；否則入庫流程可能無法 push。第一版可以先在測試用公開儲存庫驗證。

GitHub Pages 網址範例：`https://你的帳號.github.io/Anime-Wiki/search.html`。這只是格式範例，**不是目前已上線網址**。

## 二、訪客怎麼申請？

1. 在公開的 `search.html` 輸入名稱或類型，按「搜尋動漫」。
2. 在一張尚未收錄的作品卡片點 **「＋ 申請加入 Anime Wiki」**。
3. GitHub 新 Issue 頁會預填作品名稱與來源資料，訪客登入 GitHub 並按 **Submit new issue**。
4. 若看到 Jikan 或「離線參考」卡片，申請仍可建立，但 `Provider-ID` 會是「待補」；由你先找出 AniList／Kitsu 作品編號，再編輯 Issue，不能直接加審核標籤。

> Issue 正文最少包含這四行，管理者確認後才准許執行：

```text
Provider: AniList
Provider-ID: 9253
Title: 命運石之門
Source-URL: https://anilist.co/anime/9253
```

`Title` 是管理者核對的繁中顯示名稱；日期、作品形式、類型和來源事實以 API 重新擷取為準。只支援 TV / TV_SHORT / MOVIE 的基本資料匯入，其他形式需人工處理。

## 三、管理者如何核准？

1. 前往 GitHub 儲存庫的 **Issues**，開啟申請。
2. 檢查外部作品網址、ID 是否一致，是否與 `wiki/works/` 的既有作品重複，避免把漫畫、不同季數或劇場版當成同一條目。
3. 如果申請中的資料不足，先回覆對方或編輯 Issue，補上有效的 `Provider`、`Provider-ID`、`Title`、`Source-URL`。
4. **由儲存庫擁有者新增標籤 `approved-ingest`**，觸發工作流程。可在套用標籤的介面新增同名標籤。
5. 至 **Actions → Approved community anime import (free)** 查看執行狀況。
6. 通過後會由程式寫入 Wiki、Lint、推送、部署，並關閉 Issue；若失敗會留下錯誤提示、保持申請待處理，並移除標籤以便修正後重試。
7. 重新開啟 GitHub Pages 的 `search.html` 與 `index.html`，應看到作品數增加、Wiki 出現新頁、HTML 作品地圖更新。若網站尚未部署成功，檢查 Actions Pages 步驟。

**限制：** 為確保「只有你能核准」，工作流程額外檢查加標籤者的 GitHub 帳號等於儲存庫擁有者，因此第一版建議使用**個人儲存庫**。若使用組織儲存庫，需另設可信審核者白名單並修改流程條件。

## 四、不用上網、不用付費的本機測試

在 VS Code 專案根目錄執行：

```powershell
python -m unittest discover -s tests -p "test_approved_issue_ingest.py" -v
node --test tests/test_issue_request.cjs
python scripts/check_sources.py
python scripts/lint_wiki.py
python scripts/check_slides.py
```

`test_approved_issue_ingest.py` 會建立暫存副本，模擬《命運石之門》入庫。它**不會修改正式的 10 部 Wiki**，也**不會真的對外呼叫 API**。

## 五、限制與安全

- Wiki 寫入只在管理者核准後執行；無法防止 GitHub Issues 上出現無關申請，必要時可以刪除或關閉。
- **Jikan 公開 API 已於 2026-10-01 停止服務**，不依賴它做自動入庫。來源：https://github.com/jikan-me/jikan-rest/issues/613
- AniList 或 Kitsu 若斷線／格式異常，該次匯入可能失敗。請保留 Issue，稍後重試。
- 這是「可信來源基本欄位驗證」，不是 AI 自動撰寫完整劇情介紹；後續可以由 Codex 依官方來源補充 Wiki 頁面，再跑 Lint。
- 不能將 API 金鑰或 GitHub Token 填入 HTML。網站只產生 GitHub 申請連結，真正寫入使用 GitHub Actions 的短期 `GITHUB_TOKEN`。
- 此版本不會因「任何人按一下」就自動更新 Wiki；必須由你明確核准，避免被濫用。
