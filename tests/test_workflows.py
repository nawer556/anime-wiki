"""Standard-library smoke/integrity tests for Anime Wiki."""
from pathlib import Path
import json, subprocess, sys, shutil, tempfile, unittest
ROOT=Path(__file__).resolve().parents[1]
PY=sys.executable

def execute(name,*args,root=ROOT):
    return subprocess.run([PY,str(root/'scripts'/name),*args],cwd=root,text=True,capture_output=True)

class WikiTests(unittest.TestCase):
    def test_raw_unchanged(self):
        x=execute('check_sources.py');self.assertEqual(0,x.returncode,x.stdout+x.stderr)
    def test_wiki_lint(self):
        x=execute('lint_wiki.py');self.assertEqual(0,x.returncode,x.stdout+x.stderr)
    def test_slide_lint(self):
        x=execute('check_slides.py');self.assertEqual(0,x.returncode,x.stdout+x.stderr)
    def test_query_uses_incremental_fact(self):
        x=execute('query_wiki.py','--type','movie','--genre','戀愛','--max-minutes','120')
        self.assertEqual(0,x.returncode,x.stderr)
        self.assertIn('你的名字。',x.stdout)
        self.assertIn('SRC-012',x.stdout)
    def test_no_match_is_honest(self):
        x=execute('query_wiki.py','--type','movie','--genre','科幻')
        self.assertEqual(0,x.returncode,x.stderr)
        self.assertIn('AUTO_INGEST_REQUIRED',x.stdout)
    def test_tampering_raw_source_is_detected(self):
        with tempfile.TemporaryDirectory() as d:
            temp=Path(d)/'Anime-Wiki'
            shutil.copytree(ROOT/'raw',temp/'raw')
            (temp/'scripts').mkdir()
            shutil.copy(ROOT/'scripts'/'check_sources.py',temp/'scripts'/'check_sources.py')
            old=temp/'raw'/'sources'/'SRC-001.md'
            old.write_text(old.read_text(encoding='utf-8')+'\nTAMPER DEMO\n',encoding='utf-8')
            x=execute('check_sources.py',root=temp)
            self.assertNotEqual(0,x.returncode)
            self.assertIn('MODIFIED immutable raw source: SRC-001.md',x.stdout)
    def test_stage_does_not_change_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            temp=Path(d)/'Anime-Wiki'
            (temp/'scripts').mkdir(parents=True)
            (temp/'raw').mkdir()
            shutil.copy(ROOT/'scripts'/'prepare_ingest.py',temp/'scripts'/'prepare_ingest.py')
            shutil.copy(ROOT/'raw'/'manifest.json',temp/'raw'/'manifest.json')
            original=(temp/'raw'/'manifest.json').read_bytes()
            x=execute('prepare_ingest.py','--title','測試候選','--url','https://example.org/verified-later','--publisher','待查','--work-id','NEW',root=temp)
            self.assertEqual(0,x.returncode,x.stdout+x.stderr)
            self.assertEqual(original,(temp/'raw'/'manifest.json').read_bytes())
            self.assertTrue(list((temp/'staging').glob('SRC-*-draft.md')))

if __name__=='__main__': unittest.main()
