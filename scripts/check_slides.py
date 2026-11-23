#!/usr/bin/env python3
"""Static build checks for docs/index.html, linked to current Anime Wiki."""
from html.parser import HTMLParser
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from lint_wiki import meta

class SlideParser(HTMLParser):
    def __init__(self):
        super().__init__();self.slides=0;self.source_links=[];self.ids=set();self.external_assets=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.add(d['id'])
        if tag=='section' and 'slide' in d.get('class','').split():self.slides+=1
        if tag=='a' and 'source-link' in d.get('class','').split():self.source_links.append(d.get('href',''))
        if tag=='script' and d.get('src'):self.external_assets.append(d['src'])
        if tag in ('img','iframe') and d.get('src'):self.external_assets.append(d['src'])
        if tag=='link' and d.get('rel')=='stylesheet':self.external_assets.append(d.get('href',''))

def main():
    errors=[]
    deck=ROOT/'docs'/'index.html'
    snap=ROOT/'docs'/'assets'/'wiki-snapshot.json'
    for p in (deck,snap,ROOT/'records'/'slide-sources.md'):
        if not p.is_file():errors.append(f'missing output: {p}')
    if errors:return fail(errors)
    raw=deck.read_text(encoding='utf-8')
    data=json.loads(snap.read_text(encoding='utf-8'))
    manifest=json.loads((ROOT/'raw'/'manifest.json').read_text(encoding='utf-8'))
    parsed=SlideParser();parsed.feed(raw)
    if parsed.slides!=10:errors.append(f'expected 10 slides, got {parsed.slides}')
    for id_ in ('lastQuery','stage','quizMedia','quizGenre','quizMood','quizMinutes','quizResults','sourcesOverlay','sourcesTopBtn'):
        if id_ not in parsed.ids:errors.append(f'missing HTML control: {id_}')
    if parsed.external_assets:errors.append(f'external assets: {parsed.external_assets}')
    if not data['works']:errors.append('no Wiki works in HTML')
    actual_works=list((ROOT/'wiki'/'works').glob('*.md'))
    if len(data['works'])!=len(actual_works):errors.append(f'snapshot has {len(data["works"])} works, Wiki has {len(actual_works)}')
    if len(data['sources'])!=len(manifest['sources']):errors.append(f'snapshot source count {len(data["sources"])} differs from manifest {len(manifest["sources"])}')
    if len(parsed.source_links)!=len(manifest['sources']):errors.append(f'sources overlay has {len(parsed.source_links)} links')
    if set(parsed.source_links)!={s['url'] for s in manifest['sources']}:errors.append('sources overlay URLs differ from raw manifest')
    if 'last_query' not in data or 'generated_at' not in data:errors.append('snapshot missing query/build metadata')
    if '<!-- BUILD:' in raw:errors.append('unfilled dynamic placeholders')
    for token in (f'全部 {len(data["works"])}',f'電影 {sum(w["media_type"]=="movie" for w in data["works"])}'):
        if token not in raw:errors.append(f'missing updated work count: {token}')
    if 'AUTO_INGEST_REQUIRED' not in raw:errors.append('no honest missing-result state')
    if 'duration_minutes===null' not in raw:errors.append('no unknown duration guard in interactive recommendation')
    if 'wikiData' not in parsed.ids:errors.append('no embedded snapshot for offline HTML')
    if '/* BUILD:SNAPSHOT */' in raw:errors.append('unresolved snapshot placeholder')
    query_file=ROOT/'records'/'last-query.json'
    if query_file.exists():
        if data['last_query']!=json.loads(query_file.read_text(encoding='utf-8')):errors.append('last query differs from built deck')
    for w in data['works']:
        matches=list((ROOT/'wiki'/'works').glob('*.md'))
        wp=ROOT/w['path']
        if not wp.exists():errors.append(f'Wiki page missing: {w["path"]}');continue
        m=meta(wp)
        for k in ('id','title','media_type','release_year','duration_minutes','genres','themes','moods','source_ids'):
            if w[k]!=m[k]:errors.append(f'{w["id"]}: snapshot mismatch in {k}')
        for s in w['sources']:
            if s['id'] not in {i['id'] for i in manifest['sources']}:errors.append(f'{w["id"]}: bad source {s["id"]}')
    if errors:return fail(errors)
    n_unknown=sum(w['duration_minutes'] is None for w in data['works'])
    print(f'SLIDE LINT PASS: {parsed.slides} slides; {len(data["works"])} works; {len(data["sources"])} sources; {len(parsed.source_links)} source links')
    print(f'Wiki snapshot matches Markdown metadata; offline resources embedded; unknown durations excluded ({n_unknown} entries).')
    return 0

def fail(errors):
    for e in errors:print('SLIDE LINT ERROR:',e)
    return 1
if __name__=='__main__':sys.exit(main())
