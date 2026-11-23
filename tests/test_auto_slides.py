"""Integration tests for automatic post-query HTML rebuild and safe rollback.

Temp fixtures are not published: the extra work page is only a synthetic test.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class AutoSlidesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'Anime-Wiki'
        shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('__pycache__'))

    def run_tool(self,name,*args):
        return subprocess.run([sys.executable,str(self.root/'scripts'/name),*args],cwd=self.root,capture_output=True,text=True)

    def test_every_search_updates_snapshot_even_no_match(self):
        q=self.run_tool('query_wiki.py','--type','movie','--genre','科幻')
        self.assertEqual(q.returncode,0,q.stdout+q.stderr)
        self.assertIn('AUTO SLIDES UPDATED',q.stdout)
        obj=json.loads((self.root/'docs/assets/wiki-snapshot.json').read_text(encoding='utf-8'))
        self.assertEqual(obj['last_query']['status'],'NO_MATCH')
        self.assertEqual(obj['last_query']['filters']['genre'],'科幻')
        self.assertIn('最近一次搜尋', (self.root/'docs/index.html').read_text(encoding='utf-8'))
        q=self.run_tool('query_wiki.py','--type','movie','--genre','戀愛','--max-minutes','120')
        self.assertEqual(q.returncode,0,q.stdout+q.stderr)
        obj=json.loads((self.root/'docs/assets/wiki-snapshot.json').read_text(encoding='utf-8'))
        self.assertEqual(obj['last_query']['matches'][0]['title'],'你的名字。')
        self.assertEqual(obj['last_query']['status'],'MATCH')

    def test_corrupt_source_does_not_replace_published_html(self):
        olddeck=(self.root/'docs/index.html').read_bytes()
        oldsnap=(self.root/'docs/assets/wiki-snapshot.json').read_bytes()
        f=self.root/'raw/sources/SRC-001.md'
        f.write_text(f.read_text(encoding='utf-8')+'\nCORRUPTED TEST ONLY\n',encoding='utf-8')
        r=self.run_tool('query_wiki.py','--type','movie','--genre','戀愛')
        self.assertNotEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertIn('NOT UPDATED',r.stdout)
        self.assertEqual(olddeck,(self.root/'docs/index.html').read_bytes())
        self.assertEqual(oldsnap,(self.root/'docs/assets/wiki-snapshot.json').read_bytes())

    def test_new_work_count_no_longer_fixed_to_ten(self):
        src=self.root/'wiki/works/葬送的芙莉蓮.md'
        text=src.read_text(encoding='utf-8').replace('id: "W001"','id: "W099"',1).replace('title: "葬送的芙莉蓮"','title: "額外測試作品"',1)
        (self.root/'wiki/works/額外測試作品.md').write_text(text,encoding='utf-8')
        r=self.run_tool('query_wiki.py','--type','tv','--genre','奇幻')
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        obj=json.loads((self.root/'docs/assets/wiki-snapshot.json').read_text(encoding='utf-8'))
        self.assertEqual(len(obj['works']),11)
        self.assertIn('全部 11', (self.root/'docs/index.html').read_text(encoding='utf-8'))
        self.assertEqual(self.run_tool('check_slides.py').returncode,0)

if __name__=='__main__':unittest.main()
