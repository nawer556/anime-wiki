#!/usr/bin/env python3
"""Lightweight cross-link and provenance audit; no factual inference/network."""
from pathlib import Path
import re,sys,json
ROOT=Path(__file__).resolve().parents[1]
WIKI=ROOT/'wiki'
files=list(WIKI.rglob('*.md'))
stems={p.stem:[] for p in files}
for p in files:stems[p.stem].append(p)
inbound={p:0 for p in files}
links=[]
for p in files:
    raw=p.read_text(encoding='utf-8')
    for name in re.findall(r'\[\[([^\]]+)\]\]',raw):
        stem=name.split('|')[0].split('#')[0]
        candidates=stems.get(stem,[])
        if len(candidates)==1 and candidates[0]!=p:
            inbound[candidates[0]]+=1
            links.append((p,candidates[0]))
    for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)',raw):
        if target.startswith(('http:','https:','#','mailto:')):continue
        resolved=(p.parent/target.split('#')[0]).resolve()
        if resolved in inbound and resolved!=p:inbound[resolved]+=1
orphans=[p.relative_to(ROOT).as_posix() for p,count in inbound.items() if count==0]
ambiguous={k:[str(x.relative_to(ROOT)) for x in v] for k,v in stems.items() if len(v)>1}
ambiguous_uses=[]
for p in files:
    for target in re.findall(r'\[\[([^\]]+)\]\]', p.read_text(encoding='utf-8')):
        if target.split('|',1)[0].split('#',1)[0] in ambiguous:
            ambiguous_uses.append(str(p.relative_to(ROOT))+': '+target)
report={'wiki_pages':len(files),'wiki_crosslinks':len(links),'possible_orphans_excluding_index':orphans,'duplicate_page_titles_to_watch':ambiguous,'ambiguous_wikilink_uses':ambiguous_uses}
print('WIKI GRAPH AUDIT:',json.dumps(report,ensure_ascii=False,indent=2))
print('NOTE: Orphans are suggestions, not a structural error; index links deliberately excluded.')
