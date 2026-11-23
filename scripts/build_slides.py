#!/usr/bin/env python3
"""Build the self-contained Anime Wiki HTML lesson from the verified Markdown Wiki.

No external dependencies. Never invents a missing duration, source, or recommendation rating.
"""
from pathlib import Path
from datetime import datetime, timezone
from html import escape
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from lint_wiki import meta

WORKS_PATH=ROOT/'wiki'/'works'
DOCS=ROOT/'docs'
TEMPLATE=ROOT/'scripts'/'templates'/'deck.html'
MANIFEST=ROOT/'raw'/'manifest.json'


def build():
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    sources={s['id']:s for s in manifest['sources']}
    works=[]
    for p in WORKS_PATH.glob('*.md'):
        m=meta(p)
        missing=[x for x in m['source_ids'] if x not in sources]
        if missing: raise ValueError(f'{p}: Missing sources {missing}')
        works.append({
            'id':m['id'], 'title':m['title'], 'original_title':m['original_title'],
            'media_type':m['media_type'], 'release_year':m['release_year'],
            'duration_minutes':m.get('duration_minutes'), 'genres':m['genres'],
            'themes':m['themes'], 'moods':m['moods'], 'source_ids':m['source_ids'],
            'path':p.relative_to(ROOT).as_posix(),
            'sources':[{'id':sid,'url':sources[sid]['url'],'publisher':sources[sid]['publisher']} for sid in m['source_ids']]
        })
    works.sort(key=lambda x:x['id'])
    if not works or not sources: raise ValueError('Empty verified Wiki; cannot build slides')
    lastq=ROOT/'records'/'last-query.json'
    last_query=json.loads(lastq.read_text(encoding='utf-8')) if lastq.exists() else None
    if last_query is not None and not isinstance(last_query.get('matches',[]),list):
        raise ValueError('Invalid last query format')
    generated_at=datetime.now(timezone.utc).isoformat(timespec='seconds')
    tv_count=sum(w['media_type']=='tv' for w in works)
    movie_count=sum(w['media_type']=='movie' for w in works)

    snapshot={
        'as_of':manifest['as_of'], 'generated_at':generated_at, 'last_query':last_query,
        'wiki_index':'index.md',
        'origin':'wiki/works/*.md and raw/manifest.json',
        'recommendation_rules':'wiki/recommendations/推薦方法.md',
        'notes':'genre, theme, mood, and pacing tags are Wiki editorial labels, not objective ratings',
        'works':works,
        'sources':[{'id':s['id'],'title':s['title'],'url':s['url'],'publisher':s['publisher'], 'wiki_raw_file':s['raw_file']} for s in manifest['sources']]
    }
    DOCS.mkdir(parents=True,exist_ok=True)
    (DOCS/'assets').mkdir(exist_ok=True)
    (DOCS/'assets'/'wiki-snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

    colors=['teal','sky','amber','purple','pink','coral','teal','sky','amber','purple']
    symbols=['✦','☀','➶','♫','♡','◈','∞','✿','☾','★']
    cards=[]
    for i,w in enumerate(works):
        short='電影' if w['media_type']=='movie' else 'TV'
        color=colors[i%len(colors)]
        symbol=symbols[i%len(symbols)]
        cards.append(f'''<article class="atlas-card tone-{color}" data-type="{w['media_type']}" title="{escape(w['path'])}">
          <span class="atlas-symbol" aria-hidden="true">{symbol}</span>
          <div class="atlas-card-top"><span>{short} · {w['release_year']}</span><span class="work-id">{w['id']}</span></div>
          <h3>{escape(w['title'])}</h3><p>{escape(' · '.join(w['genres']))}</p>
          <div class="atlas-source">{escape(', '.join(w['source_ids']))}</div>
        </article>''')

    links=[]
    for s in snapshot['sources']:
        links.append(f'<a href="{escape(s["url"],quote=True)}" target="_blank" rel="noopener noreferrer" class="source-link" aria-label="{escape(s["id"]+" "+s["title"])}"><span class="source-key">{s["id"]}</span><span>{escape(s["title"])}</span><span class="source-open">↗</span></a>')

    html=TEMPLATE.read_text(encoding='utf-8')
    data=json.dumps(snapshot,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    movie_examples=[w for w in works if w['media_type']=='movie' and w['duration_minutes'] is not None][:3]
    movie_markup=''.join(f'<div class="item"><span>{escape(w["title"])}</span><span class="minute">{w["duration_minutes"]} 分鐘</span></div>' for w in movie_examples)
    if not movie_markup:movie_markup='<div class="item">目前沒有已核實片長的電影</div>'
    html=html.replace('<!-- BUILD:ATLAS -->','\n'.join(cards))
    html=html.replace('<!-- BUILD:WORK-COUNT -->',str(len(works)))
    html=html.replace('<!-- BUILD:TV-COUNT -->',str(tv_count))
    html=html.replace('<!-- BUILD:MOVIE-COUNT -->',str(movie_count))
    html=html.replace('<!-- BUILD:MOVIE-EXAMPLES -->',movie_markup)
    html=html.replace('<!-- BUILD:GENERATED-AT -->',escape(generated_at))
    html=html.replace('<!-- BUILD:SOURCES -->','\n'.join(links))
    html=html.replace('/* BUILD:SNAPSHOT */',data)
    html=html.replace('<!-- BUILD:DATE -->',escape(snapshot['as_of']))
    html=html.replace('<!-- BUILD:SOURCE-COUNT -->',str(len(sources)))
    (DOCS/'index.html').write_text(html,encoding='utf-8')

    rows='\n'.join(f'| {w["id"]} · {w["title"]} | `{w["path"]}` | {", ".join(w["source_ids"])} |' for w in works)
    audit=f"""# HTML 教學簡報 ↔ Anime Wiki 來源對照

> 生成時間：{generated_at}（UTC） · Wiki 來源索引日期：{manifest['as_of']}。
> 作品 {len(works)} 部（TV {tv_count}、電影 {movie_count}），來源 {len(sources)} 份。
> 由 `scripts/build_slides.py` 讀取已驗證的 Wiki 生成固定 HTML；每次本機 Query 會自動重新生成並檢查。

| 頁次 | 教學內容 | Wiki 根據 |
|---|---|---|
| 01 | 封面、知識庫統計 | `index.md`、`raw/manifest.json` |
| 02 | 如何選作品 | `wiki/recommendations/推薦方法.md` |
| 03 | TV 與電影，片長已驗證樣例 | `wiki/works/*.md` 與各自 SRC-ID |
| 04 | 類型與主題 | `wiki/genres/奇幻.md`、`wiki/themes/成長.md` |
| 05 | **全部 {len(works)} 部作品地圖** | 全部 `wiki/works/*.md`；詳見下表 |
| 06 | 類型比較案例 | `wiki/comparisons/奇幻作品比較.md`、`wiki/comparisons/運動作品比較.md` |
| 07 | 混合推薦規則 | `wiki/recommendations/推薦方法.md`、`workflow.md` |
| 08 | **最近一次 Query 結果 + 互動推薦** | `records/last-query.json`、`docs/assets/wiki-snapshot.json`、作品各自 SRC-ID |
| 09 | Wiki → 投影片工作流程 | `workflow.md`、`log.md`、`raw/manifest.json` |
| 10 | 全部原始來源連結 | `raw/manifest.json` |

## 第 5 頁作品清單與來源追溯

| 作品 | Wiki 頁 | 來源 ID |
|---|---|---|
{rows}

## 最近一次 Wiki 搜尋

{json.dumps(last_query,ensure_ascii=False,indent=2) if last_query else '尚未執行 CLI Query；未顯示最近搜尋結果。'}

## 說明與限制

- 每次本機 CLI 查詢（含無結果）都更新靜態 HTML、作品地圖、互動推薦快照、來源清單與最近 Query；瀏覽器本身不會連網或自動 Ingest。
- 新作品經驗證 Ingest 後，須再次 Query 或執行 `python scripts/sync_slides.py --reason ingest`。
- 第 2、4、6、7、9 頁包含固定教學或比較敘述；若相關 Wiki 內容有重大更動，Codex 應人工核對並修改模板，不應宣稱完全語意自動更新。
- 只有經證實的片長才參與精確分鐘篩選，來源可沿作品頁追至 Raw Source URL。
- 類型／主題／情緒標籤是 Wiki 編輯歸納，非客觀評分。
"""
    (ROOT/'records'/'slide-sources.md').write_text(audit,encoding='utf-8')
    print(f'BUILD PASS: {len(works)} works, {len(sources)} sources → docs/index.html')

if __name__=='__main__':build()
