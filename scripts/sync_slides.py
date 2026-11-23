#!/usr/bin/env python3
"""Safely regenerate the *static* HTML deck after each local query / verified ingest.

The browser does not query Wiki. This command validates Wiki first, builds the HTML,
then validates the new deck. Failed updates restore the previous deck and snapshot.
Only Python stdlib is required.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = [
    ROOT / 'docs' / 'index.html',
    ROOT / 'docs' / 'assets' / 'wiki-snapshot.json',
    ROOT / 'records' / 'slide-sources.md',
    ROOT / 'records' / 'last-query.json',
]

def cmd(name: str):
    env=os.environ.copy()
    env['PYTHONIOENCODING']='utf-8'
    return subprocess.run([sys.executable, str(ROOT / 'scripts' / name)],
                          cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                          errors='replace', env=env)

def sync_slides(*, reason='manual', last_query=None, record=True):
    # Validate *before* touching the published artifacts.
    checked=[]
    for name in ('check_sources.py', 'lint_wiki.py', 'audit_wiki.py'):
        res=cmd(name)
        checked.append((name,res))
        if res.returncode:
            info=f'{name} FAIL: {(res.stdout+res.stderr).strip()[-1000:]}'
            _record(reason, 'FAIL', info, last_query, record)
            return False,info

    backup={p:p.read_bytes() if p.is_file() else None for p in ARTIFACTS}
    try:
        if last_query is not None:
            p=ROOT/'records'/'last-query.json'
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps(last_query,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        for name in ('build_slides.py', 'check_slides.py'):
            result=cmd(name)
            if result.returncode:
                raise RuntimeError(f'{name} FAIL: {(result.stdout+result.stderr).strip()[-1000:]}')
        info='Sources + Wiki Lint + Graph + HTML build + Slide Lint PASS'
        _record(reason, 'PASS', info, last_query, record)
        return True,info
    except Exception as ex:
        for path,data in backup.items():
            if data is None:
                path.unlink(missing_ok=True)
            else:
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(data)
        info=f'Slide update rejected; previous deck retained: {ex}'
        _record(reason, 'FAIL', info, last_query, record)
        return False,info

def _record(reason,status,info,last_query,record):
    if not record:return
    stamp=datetime.now(timezone.utc).isoformat(timespec='seconds')
    q=''
    if last_query:
        q=f"; filters={last_query.get('filters')}; matches={len(last_query.get('matches',[]))}"
    with (ROOT/'log.md').open('a',encoding='utf-8') as f:
        f.write(f'\n### {stamp} | AUTO-SLIDE-SYNC | {status}\n'
                f'- Trigger: `{reason}`{q}\n- Result: {info}\n'
                '- Outputs: `docs/index.html`, `docs/assets/wiki-snapshot.json`, `records/slide-sources.md`'
                ' (on PASS only)\n')

if __name__ == '__main__':
    p=argparse.ArgumentParser(description='Validate and rebuild static HTML from current verified Wiki')
    p.add_argument('--reason',default='manual',choices=['manual','ingest','query'])
    args=p.parse_args()
    success,message=sync_slides(reason=args.reason)
    print(('AUTO SLIDES PASS: ' if success else 'AUTO SLIDES FAIL: ')+message)
    sys.exit(0 if success else 1)
