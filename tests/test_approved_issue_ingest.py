"""Zero-network tests for public suggestions + owner-approved ingest."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import approved_issue_ingest as intake

BODY = '''Anime Wiki 收錄申請
Provider: AniList
Provider-ID: 9253
Title: 命運石之門
Source-URL: https://anilist.co/anime/9253
'''

class TestApproval(unittest.TestCase):
    def test_parser_ok(self):
        value = intake.fields_from_issue(BODY)
        self.assertEqual(value['provider_id'], 9253)
        self.assertEqual(value['title'], '命運石之門')

    def test_reject_unverified_and_bad_url(self):
        with self.assertRaises(intake.IntakeError):
            intake.fields_from_issue(BODY.replace('AniList', '離線參考'))
        with self.assertRaises(intake.IntakeError):
            intake.fields_from_issue(BODY.replace('anilist.co', 'evil.example'))
        with self.assertRaises(intake.IntakeError):
            intake.fields_from_issue(BODY + 'Provider-ID: 9999\n')

    def test_canonical_fetch_no_visitor_url(self):
        fake = {'data': {'Media': {'id': 9253, 'title': {'native': 'シュタインズ・ゲート', 'english': 'Steins;Gate', 'romaji': 'Steins;Gate'},
                    'format': 'TV', 'seasonYear': 2011, 'duration': 24, 'genres': ['Sci-Fi', 'Drama'],
                    'isAdult': False, 'siteUrl': 'https://anilist.co/anime/9253'}}}
        with patch.object(intake, 'request_json', return_value=fake) as fn:
            v = intake.api_metadata(intake.fields_from_issue(BODY))
        self.assertEqual(v['source_url'], 'https://anilist.co/anime/9253')
        self.assertEqual(v['type'], 'tv')
        self.assertEqual(fn.call_args.args[0], intake.ANILIST_API)

    def test_integrated_approval_writes_wiki_sources_slides(self):
        # Only a temporary copy is changed, never the real 10-work Wiki.
        with tempfile.TemporaryDirectory() as temp:
            copy = Path(temp)/'Anime-Wiki'
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('__pycache__', '.git'))
            data = {'original': 'シュタインズ・ゲート', 'aliases': ['Steins;Gate', 'シュタインズ・ゲート'],
                    'type': 'tv', 'year': 2011, 'duration': 24, 'genres': ['Sci-Fi', 'Drama'],
                    'source_url': 'https://anilist.co/anime/9253', 'publisher': 'AniList 公開動漫資料庫'}
            with patch.object(intake, 'api_metadata', return_value=data):
                wid, sid = intake.process(copy, BODY, 21)
            self.assertEqual(wid, 'W011')
            self.assertEqual(sid, 'SRC-013')
            self.assertTrue((copy/'wiki/works/命運石之門.md').exists())
            self.assertIn('命運石之門', (copy/'wiki/genres/科幻.md').read_text(encoding='utf-8'))
            self.assertEqual(len(json.loads((copy/'docs/assets/wiki-snapshot.json').read_text(encoding='utf-8'))['works']), 11)
            self.assertIn('Issue: #21', (copy/'log.md').read_text(encoding='utf-8'))
            self.assertIn('命運石之門', (copy/'docs/index.html').read_text(encoding='utf-8'))
            # Re-submitting must not mutate anything.
            with patch.object(intake, 'api_metadata', return_value=data):
                with self.assertRaises(intake.Rejected):
                    intake.process(copy, BODY, 22)

if __name__ == '__main__':
    unittest.main()
