#!/usr/bin/env python3
"""Deterministic Anime Wiki structural lint (stdlib only).

Checks identity, provenance, Markdown links and fields; factual truth still requires
Codex/human review against the original publisher website.
"""
from pathlib import Path
from urllib.parse import urlparse,unquote
import json, re, sys
ROOT=Path(__file__).resolve().parents[1]
WORKS=ROOT/'wiki'/'works'


def meta(path):
    s=path.read_text(encoding='utf-8')
    if not s.startswith('---\n'):raise ValueError('missing frontmatter')
    parts=s.split('\n---\n',1)
    if len(parts)<2:raise ValueError('missing closing frontmatter')
    out={}
    for line in parts[0].splitlines()[1:]:
        if ':' not in line:continue
        key,val=line.split(':',1);val=val.strip()
        try:out[key.strip()]=json.loads(val)
        except json.JSONDecodeError:out[key.strip()]=val
    return out


def uncode(text):
    text=re.sub(r'(?ms)^\s*(```|~~~).*?^\s*\1[^\n]*$', '',text)
    text=re.sub(r'`[^`\n]+`','',text)
    return text


def main():
    errors=[];warnings=[]
    manifest=json.loads((ROOT/'raw'/'manifest.json').read_text(encoding='utf-8'))
    raw_sources=manifest.get('sources',[]);src_ids=set();src_urls=set()
    for s in raw_sources:
        sid=s.get('id');url=s.get('url','');raw_file=s.get('raw_file','')
        if sid in src_ids:errors.append(f'duplicate raw source ID: {sid}')
        src_ids.add(sid)
        if url in src_urls:errors.append(f'duplicate source URL in manifest: {url}')
        src_urls.add(url)
        if urlparse(url).scheme!='https' or not urlparse(url).netloc:errors.append(f'{sid}: invalid source HTTPS URL')
        if raw_file!=f'raw/sources/{sid}.md':errors.append(f'{sid}: raw_file does not match source ID')
        if not (ROOT/raw_file).is_file():errors.append(f'{sid}: missing raw source file {raw_file}')
        for required in ('publisher','title','retrieved_on','work_id'):
            if not s.get(required):errors.append(f'{sid}: missing {required}')
    wpaths=sorted(WORKS.glob('*.md'))
    id_set=set();title_set=set();all_meta=[]
    for w in wpaths:
        try:m=meta(w)
        except Exception as e:errors.append(f'{w.relative_to(ROOT)}: {e}');continue
        all_meta.append(m)
        for key in ('id','title','media_type','release_year','genres','themes','source_ids','verification','last_reviewed'):
            if key not in m:errors.append(f'{w.name}: missing frontmatter {key}')
        wid=m.get('id');title=m.get('title')
        if not isinstance(wid,str) or not re.fullmatch(r'W\d{3,}',wid):errors.append(f'{w.name}: bad work id {wid!r}')
        if wid in id_set:errors.append(f'{w.name}: duplicate work ID {wid}')
        id_set.add(wid)
        if title in title_set:errors.append(f'{w.name}: duplicate title {title}')
        title_set.add(title)
        if m.get('media_type') not in ('tv','movie'):errors.append(f'{w.name}: invalid media_type')
        if m.get('release_year') is not None and (not isinstance(m.get('release_year'),int) or isinstance(m.get('release_year'),bool)):errors.append(f'{w.name}: invalid release_year')
        if m.get('duration_minutes') is not None and (not isinstance(m['duration_minutes'],int) or m['duration_minutes']<1):errors.append(f'{w.name}: invalid duration_minutes')
        if m.get('media_type')=='movie' and m.get('duration_minutes') is None:warnings.append(f'{w.name}: movie duration unknown; exact minute filters must exclude')
        for key in ('source_ids','genres','themes','moods'):
            if not isinstance(m.get(key),list):errors.append(f'{w.name}: {key} must be an array')
        if not m.get('source_ids'):errors.append(f'{w.name}: no source references')
        for sid in m.get('source_ids',[]):
            if sid not in src_ids:errors.append(f'{w.name}: unknown source {sid}')
            else:
                owner=next((s.get('work_id') for s in raw_sources if s['id']==sid),None)
                if owner!=wid:warnings.append(f'{w.name}: {sid} belongs to {owner}; check cross-work citation')
        for field,folder in [('genres','genres'),('themes','themes')]:
            for tag in m.get(field,[]):
                if not (ROOT/'wiki'/folder/f'{tag}.md').exists():errors.append(f'{w.name}: missing {folder} page {tag}')
        # Evidence presence: a claim must be traceable to the specific raw note
        text=w.read_text(encoding='utf-8')
        for sid in m.get('source_ids',[]):
            if sid not in text:errors.append(f'{w.name}: {sid} missing in page body')
    stems={p.stem for p in ROOT.rglob('*.md')}
    stems|={m.get('title') for m in all_meta if m.get('title')}
    wiki_count=0
    for p in ROOT.rglob('*.md'):
        wiki_count+=1;txt=uncode(p.read_text(encoding='utf-8'))
        for target in re.findall(r'\[\[([^\]]+)\]\]',txt):
            name=target.split('|',1)[0].split('#',1)[0]
            if name and name not in stems:errors.append(f'{p.relative_to(ROOT)}: unresolved wikilink [[{target}]]')
        for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)',txt):
            if link.startswith(('http://','https://','mailto:','#')):continue
            target=unquote(link.split('#',1)[0])
            if target and not (p.parent/target).exists():errors.append(f'{p.relative_to(ROOT)}: broken relative link {link}')
    if len(wpaths)!=10:warnings.append(f'Initial corpus expected 10 works; now has {len(wpaths)} (auto-expansion may explain)')
    print(f'WIKI LINT: {len(wpaths)} works; {len(raw_sources)} sources; {wiki_count} Markdown pages')
    print(f'Errors: {len(errors)} | Warnings: {len(warnings)}')
    for e in errors:print('ERROR:',e)
    for w in warnings:print('INFO:',w)
    return 1 if errors else 0
if __name__=='__main__':sys.exit(main())
