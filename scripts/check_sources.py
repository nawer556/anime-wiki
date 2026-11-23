#!/usr/bin/env python3
"""Enforce the immutable raw-source notes using a SHA-256 manifest.

--add-new only records brand-new sources; modified existing notes always fail.
This verifies local integrity, NOT that external websites are factually accurate.
"""
from pathlib import Path
import argparse, hashlib, json, re, sys
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'raw'/'checksums.json'
P=ROOT/'raw'/'sources'
p=argparse.ArgumentParser()
p.add_argument('--add-new', action='store_true',help='add hashes only for brand-new SRC files; never overwrite old hashes')
a=p.parse_args()
checks=json.loads(F.read_text(encoding='utf-8'))
existing=checks['files']; issues=[]; added=[]
paths={p.name:p for p in P.glob('SRC-*.md')}
for name,digest in existing.items():
    f=paths.get(name)
    if f is None:issues.append('MISSING original raw source: '+name);continue
    actual=hashlib.sha256(f.read_bytes()).hexdigest()
    if digest!=actual:issues.append('MODIFIED immutable raw source: '+name)
for name,f in sorted(paths.items()):
    if name not in existing:
        if not re.fullmatch(r'SRC-\d{3,}\.md', name):issues.append('INVALID raw source filename: '+name);continue
        if a.add_new: added.append((name,hashlib.sha256(f.read_bytes()).hexdigest()))
        else:issues.append('UNTRACKED raw source: '+name+' (review, then run --add-new)')
if not issues and added:
    for name,digest in added:existing[name]=digest
    F.write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for i in issues:print('RAW ERROR:',i)
if not issues:print(f'RAW PASS: {len(existing)} immutable source files verified' + (f' ({len(added)} new registered)' if added else ''))
sys.exit(1 if issues else 0)
