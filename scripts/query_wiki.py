#!/usr/bin/env python3
"""Offline Wiki query, then automatically rebuild the *static* HTML presentation.

Search does not access the internet. For no match, Codex may independently run
an authorized source-search/Ingest, then this command must be rerun.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).parent))
from lint_wiki import meta
from sync_slides import sync_slides

def main():
    parser=argparse.ArgumentParser(description='Query Anime Wiki and auto-update docs/index.html')
    parser.add_argument('--type',choices=['tv','movie'])
    parser.add_argument('--genre',help='genre tag, e.g. 奇幻')
    parser.add_argument('--theme',help='theme tag, e.g. 成長')
    parser.add_argument('--mood',help='mood tag, e.g. 感動')
    parser.add_argument('--max-minutes',type=int,help='only works with verified known duration')
    parser.add_argument('--no-sync',action='store_true',help='read-only developer diagnostics; normal searches MUST sync')
    args=parser.parse_args()
    if args.max_minutes is not None and args.max_minutes<1:
        parser.error('--max-minutes must be positive')

    matches=[];unknown=[]
    for p in sorted((ROOT/'wiki'/'works').glob('*.md')):
        m=meta(p)
        if args.type and m.get('media_type')!=args.type:continue
        if args.max_minutes is not None:
            d=m.get('duration_minutes')
            if d is None:
                unknown.append((m['title'],'片長未知，不能視為符合硬性條件'))
                continue
            if d>args.max_minutes:continue
        score=sum(bool(a and a in m.get(k,[])) for a,k in ((args.genre,'genres'),(args.theme,'themes'),(args.mood,'moods')))
        n=sum(bool(x) for x in (args.genre,args.theme,args.mood))
        if n and score==0:continue
        matches.append((score,m,p))
    matches.sort(key=lambda x:(-x[0],x[1]['title']))

    if matches:
        print(f'Wiki candidates: {len(matches)}')
        for score,m,p in matches[:3]:
            n=sum(bool(x) for x in [args.genre,args.theme,args.mood])
            level='高度符合' if n and score==n else '部分符合' if n else '符合硬性條件（未指定軟性偏好）'
            print(f'- {m["title"]}: {level}; genres={"、".join(m["genres"])}; source={",".join(m["source_ids"])}; page={p.relative_to(ROOT)}')
    else:
        print('NO_MATCH / AUTO_INGEST_REQUIRED')
        print('Offline Wiki has no verified matching title; Codex with network access must run the Ingest-Lint-Query loop. Do not invent results.')
    for title,why in unknown:print(f'UNKNOWN: {title} — {why}')

    if args.no_sync:
        print('SYNC SKIPPED (--no-sync was supplied)')
        return 0

    query={
        'searched_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'filters':{'type':args.type,'genre':args.genre,'theme':args.theme,'mood':args.mood,'max_minutes':args.max_minutes},
        'status':'MATCH' if matches else 'NO_MATCH',
        'total_matches':len(matches),
        'matches':[{'id':m['id'],'title':m['title'],'score':score,'wiki_path':p.relative_to(ROOT).as_posix(),'source_ids':m['source_ids']} for score,m,p in matches[:3]],
        'unknown_durations':[t for t,_ in unknown],
        'note':'Offline query only. NO_MATCH requires a separate, authorized Codex auto-ingest; re-query after Ingest.'
    }
    ok,message=sync_slides(reason='query',last_query=query)
    print(('AUTO SLIDES UPDATED: ' if ok else 'AUTO SLIDES NOT UPDATED: ')+message)
    return 0 if ok else 2

if __name__=='__main__':sys.exit(main())
