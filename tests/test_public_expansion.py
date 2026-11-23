"""Offline integration tests: no OpenAI account, GitHub, or live internet necessary."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from auto_ingest import validated_data, publish_candidate, consume_budget, Rejected, validate_query

FAKE={
 'title':'星際謎團','original_title':'星際謎團','media_type':'movie','release_year':2024,
 'duration_minutes':95,'genres':['懸疑'],'themes':['成長'],
 'synopsis':'一群年輕人前往遙遠星球，發現了一段奇妙的訊號，決定共同找出訊號的來源與秘密。',
 'publisher':'測試用的虛構資料站','source_url':'https://example.org/fictional-anime-only-for-test'
}
EVIDENCE='測試頁面 星際謎團 是 2024 年上映的電影。movie 電影 片長 95 分鐘。此頁內容僅供本地單元測試。'

class PublicExpansionTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.root=Path(self.temp.name)/'Anime-Wiki'
  shutil.copytree(ROOT,self.root,ignore=shutil.ignore_patterns('__pycache__','.git'))
 def tearDown(self):self.temp.cleanup()
 def run_script(self,name):
  return subprocess.run([sys.executable,str(self.root/'scripts'/name)],cwd=self.root,encoding='utf-8',capture_output=True)
 def test_all_existing_still_valid(self):
  self.assertEqual(self.run_script('lint_wiki.py').returncode,0)
  self.assertEqual(self.run_script('check_slides.py').returncode,0)
 def test_query_is_rejected_when_unsafe(self):
  with self.assertRaises(Rejected):validate_query('https://evil.test')
 def test_budget_fails_closed_on_daily_max(self):
  consume_budget(self.root,limit=1)
  with self.assertRaises(Rejected):consume_budget(self.root,limit=1)
 def test_no_evidence_does_not_write_wiki(self):
  original=(self.root/'raw'/'manifest.json').read_bytes()
  with self.assertRaises(Rejected):validated_data(self.root,FAKE,'毫不相關的電影頁')
  self.assertEqual((self.root/'raw'/'manifest.json').read_bytes(),original)
 def test_typed_verified_11th_work_updates_html_and_sources(self):
  w=validated_data(self.root,FAKE,EVIDENCE)
  wid,sid=publish_candidate(self.root,w)
  self.assertEqual((wid,sid),('W011','SRC-013'))
  for name in ('check_sources.py','lint_wiki.py','check_slides.py'):
   r=self.run_script(name);self.assertEqual(r.returncode,0,r.stdout+r.stderr)
  data=json.loads((self.root/'docs'/'assets'/'wiki-snapshot.json').read_text(encoding='utf-8'))
  self.assertEqual(len(data['works']),11)
  self.assertIn('星際謎團',(self.root/'docs'/'index.html').read_text(encoding='utf-8'))
  self.assertIn('星際謎團',(self.root/'wiki'/'genres'/'懸疑.md').read_text(encoding='utf-8'))
  self.assertIn('W011',(self.root/'records'/'last-query.json').read_text(encoding='utf-8'))
 def test_failed_slide_update_rolls_back_wiki(self):
  old=(self.root/'docs'/'index.html').read_bytes()
  # Break the slide template to ensure that a previously valid Wiki stays intact.
  (self.root/'scripts'/'templates'/'deck.html').write_text('broken',encoding='utf-8')
  work=validated_data(self.root,FAKE,EVIDENCE)
  with self.assertRaises(Rejected):publish_candidate(self.root,work)
  self.assertEqual((self.root/'docs'/'index.html').read_bytes(),old)
  self.assertFalse((self.root/'wiki'/'works'/'星際謎團.md').exists())
  self.assertFalse((self.root/'raw'/'sources'/'SRC-013.md').exists())
  self.assertEqual(self.run_script('check_sources.py').returncode,0)

if __name__=='__main__':unittest.main()
