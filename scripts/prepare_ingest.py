#!/usr/bin/env python3
"""Create an unverified staging template for Codex to review and complete.

This command does not browse web, validate factual claims, or modify the Wiki.
"""
from pathlib import Path
from urllib.parse import urlparse
from datetime import date
import argparse, json, re, sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--title',required=True)
p.add_argument('--url',required=True)
p.add_argument('--publisher',required=True)
p.add_argument('--work-id',default='NEW')
a=p.parse_args()
url=urlparse(a.url)
if url.scheme!='https' or not url.netloc:sys.exit('ERROR: only HTTPS source URLs accepted')
m=json.loads((ROOT/'raw'/'manifest.json').read_text(encoding='utf-8'))
if a.url in [s['url'] for s in m['sources']]:sys.exit('ERROR: source URL already in manifest; review before adding a new SRC')
ids=[int(x['id'].split('-')[1]) for x in m['sources']]
sid=f'SRC-{max(ids+[0])+1:03d}'
f=ROOT/'staging'/f'{sid}-draft.md'
f.parent.mkdir(parents=True,exist_ok=True)
if f.exists():sys.exit(f'ERROR: existing draft not overwritten: {f}')
text=f'''# {sid}｜{a.title}｜待查證暫存資料

- **狀態**：PENDING（不得進正式 Wiki）
- **原始網址**：{a.url}
- **來源名稱**：{a.publisher}
- **日期**：{date.today().isoformat()}
- **作品 ID**：{a.work_id}

## 待查證的來源事實

1. TODO: Codex 閱讀網頁後填寫有依據的改寫摘要

## 身分與衝突檢查

- TODO: TV / Movie / franchise / season / theatrical film？
- TODO: 有無重複 URL / 作品 ID / 片長或年份衝突？
- TODO: 是否需第二來源？

## 準備更新的 Wiki 頁面

- TODO: 既有作品／新作品
- TODO: 類型、主題、比較、推薦與 index.md

## 驗證紀錄

- Status: PENDING
- 注意：這只是**準備草稿**，既未連網查證，也未完成 Ingest。
'''
f.write_text(text,encoding='utf-8')
print(f'STAGED ONLY: {f.relative_to(ROOT)}; source ID reserved by proposal, not by manifest')
