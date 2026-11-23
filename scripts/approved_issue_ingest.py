#!/usr/bin/env python3
"""Owner-approved GitHub Issue -> free provider lookup -> verified Wiki + slide update.

No OpenAI API, user secrets, arbitrary URLs, issue-provided commands, or dependencies.
Only labeled issues may invoke this script in the production workflow. The issue body
is untrusted metadata: title is an admin-reviewed display label; provider IDs are
looked up using fixed trusted URL templates rather than request-supplied URLs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html import unescape
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from auto_ingest import Rejected, now, normalized, public_https, validated_data, publish_candidate

ANILIST_API = 'https://graphql.anilist.co'
KITSU_API = 'https://kitsu.io/api/edge/anime/'
GENRES = {
    'Sci-Fi': '科幻', 'Science Fiction': '科幻', 'Mystery': '懸疑',
    'Romance': '戀愛', 'Fantasy': '奇幻', 'Drama': '劇情',
    'Action': '動作', 'Adventure': '冒險', 'Comedy': '喜劇',
    'Sports': '運動', 'Sport': '運動', 'Music': '音樂',
    'Slice of Life': '日常', 'Thriller': '懸疑',
    'Suspense': '懸疑', 'Psychological': '推理'
}

class IntakeError(ValueError):
    pass


def fields_from_issue(body: str) -> dict:
    """Parse a deliberately small, auditable key:value message; duplicates rejected."""
    if not isinstance(body, str) or len(body) > 12000:
        raise IntakeError('Issue 正文過長或格式錯誤')
    allowed = {'Provider', 'Provider-ID', 'Title', 'Source-URL'}
    fields = {}
    for line in body.splitlines():
        match = re.fullmatch(r'(Provider|Provider-ID|Title|Source-URL):\s*(.*?)\s*', line)
        if match:
            key, value = match.groups()
            if key in fields:
                raise IntakeError('申請欄位重複：' + key)
            fields[key] = value
    for key in ('Provider', 'Provider-ID', 'Title'):
        if not fields.get(key):
            raise IntakeError('缺少申請資料：' + key + '；請先補齊後再套用審核標籤')
    if fields['Provider'] not in ('AniList', 'Kitsu'):
        raise IntakeError('僅支援 AniList 或 Kitsu 的正式自動匯入；請先補可驗證的來源 ID')
    if not re.fullmatch(r'[1-9]\d{0,8}', fields['Provider-ID']):
        raise IntakeError('作品 ID 必須是正整數，長度至多 9 位')
    title = fields['Title']
    if not (2 <= len(title) <= 75) or re.search(r'[<>\\/:*?"|\[\]`\r\n]|\.\.', title):
        raise IntakeError('作品名稱有不安全字元或長度不符')
    provider, provider_id = fields['Provider'], int(fields['Provider-ID'])
    expected = ('https://anilist.co/anime/' if provider == 'AniList' else 'https://kitsu.io/anime/') + str(provider_id)
    if fields.get('Source-URL'):
        submitted = fields['Source-URL'].rstrip('/')
        if submitted != expected:
            raise IntakeError('來源 URL 與 Provider / ID 不一致；審核前請修正為 ' + expected)
    return {'provider': provider, 'provider_id': provider_id, 'title': title, 'source_url': expected}


def request_json(url: str, payload: dict | None = None, token: str | None = None) -> dict:
    """Call only fixed provider/API endpoints; no URLs from a visitor are fetched."""
    if not (url == ANILIST_API or url.startswith(KITSU_API) or url.startswith('https://api.github.com/repos/')):
        raise IntakeError('不在允許清單的資料來源')
    headers = {'Accept': 'application/json', 'User-Agent': 'AnimeWikiCourseProject/1.0'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
        headers['X-GitHub-Api-Version'] = '2022-11-28'
    if payload is None:
        req = Request(url, headers=headers)
    else:
        req = Request(url, data=json.dumps(payload).encode('utf-8'), headers={**headers, 'Content-Type': 'application/json'}, method='POST')
    try:
        with urlopen(req, timeout=15) as resp:
            if int(getattr(resp, 'status', 200)) != 200:
                raise IntakeError('外部服務未回傳成功')
            data = resp.read(350000)
            return json.loads(data.decode('utf-8'))
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise IntakeError('外部資料暫時無法查詢，Wiki 未修改：' + str(exc)[:130]) from exc


def api_metadata(request: dict) -> dict:
    provider, mid = request['provider'], request['provider_id']
    if provider == 'AniList':
        query = '''query ($id: Int!) { Media(id: $id, type: ANIME) { id title { romaji english native }
          format seasonYear duration genres isAdult siteUrl } }'''
        result = request_json(ANILIST_API, {'query': query, 'variables': {'id': mid}})
        item = (result.get('data') or {}).get('Media') or {}
        if item.get('id') != mid or item.get('isAdult') or item.get('format') not in ('TV', 'TV_SHORT', 'MOVIE'):
            raise IntakeError('AniList 查無對應的日本 TV 動畫／電影或作品不符合收錄範圍')
        titles = item.get('title') or {}
        original = titles.get('native') or titles.get('romaji') or titles.get('english') or ''
        aliases = [x for x in (titles.get('english'), titles.get('romaji'), titles.get('native')) if x]
        category = 'movie' if item.get('format') == 'MOVIE' else 'tv'
        return {'original': original, 'aliases': aliases, 'type': category, 'year': item.get('seasonYear'),
                'duration': item.get('duration'), 'genres': item.get('genres') or [],
                'source_url': 'https://anilist.co/anime/' + str(mid), 'publisher': 'AniList 公開動漫資料庫'}
    if provider == 'Kitsu':
        result = request_json(KITSU_API + str(mid) + '?include=categories')
        item = result.get('data') or {}
        attrs = item.get('attributes') or {}
        if item.get('type') != 'anime' or str(item.get('id')) != str(mid) or attrs.get('nsfw') or str(attrs.get('ageRating')).upper() == 'R18':
            raise IntakeError('Kitsu 作品識別或適齡範圍不符')
        media = str(attrs.get('showType') or attrs.get('subtype') or '').upper()
        if media not in ('MOVIE', 'TV'):
            raise IntakeError('Kitsu 該作品不是 TV 動畫或動畫電影')
        titles = attrs.get('titles') or {}
        original = titles.get('ja_jp') or titles.get('en_jp') or attrs.get('canonicalTitle') or ''
        aliases = [x for x in (titles.get('en'), titles.get('en_jp'), titles.get('ja_jp'), attrs.get('canonicalTitle')) if x]
        attached = {str(x.get('id')) for x in ((item.get('relationships') or {}).get('categories') or {}).get('data', [])}
        genres = [str(x.get('attributes', {}).get('title') or '') for x in result.get('included', [])
                  if x.get('type') == 'categories' and str(x.get('id')) in attached]
        start = str(attrs.get('startDate') or '')
        year = int(start[:4]) if re.match(r'^\d{4}', start) else None
        return {'original': original, 'aliases': aliases, 'type': 'movie' if media == 'MOVIE' else 'tv',
                'year': year, 'duration': attrs.get('episodeLength'), 'genres': genres,
                'source_url': 'https://kitsu.io/anime/' + str(mid), 'publisher': 'Kitsu 公開動漫資料庫'}
    raise IntakeError('未知資料來源')


def candidate_from_metadata(root: Path, issue: dict, data: dict) -> tuple[dict, str]:
    original = str(data.get('original') or '').strip()
    if not original or len(original) > 70:
        raise IntakeError('來源沒有可靠的原始作品名稱')
    available = {p.stem for p in (root/'wiki'/'genres').glob('*.md')}
    genres = list(dict.fromkeys(GENRES[g] for g in data.get('genres', []) if g in GENRES and GENRES[g] in available))[:3]
    if not genres:
        raise IntakeError('作品目前沒有可驗證且已定義的 Wiki 類型；請人工處理，未寫入')
    mid = issue['provider_id']
    year = data.get('year')
    if type(year) is not int or not 1950 <= year <= now().year + 2:
        year = None
    duration = data.get('duration') if data['type'] == 'movie' else None
    if type(duration) is not int or not (25 <= duration <= 250):
        duration = None
    # Data from the provider: only assertions supported by its structured metadata.
    # Existing verified_data() is reused to enforce duplicate/media/link checks.
    title = issue['title']
    synopsis = f'此作為{("動畫電影" if data["type"] == "movie" else "電視動畫")}，外部資料庫分類包含{"、".join(genres)}。劇情介紹仍待補充核對。'
    type_text = '映画 movie film' if data['type'] == 'movie' else 'テレビ TV anime series'
    evidence = ' '.join([title, original, *(str(x) for x in data.get('aliases', [])), type_text,
                         str(year or ''), (str(duration) + ' minutes' if duration else ''),
                         'genre ' + ', '.join(str(g) for g in data.get('genres', [])),
                         'Provider-ID ' + str(mid)])
    candidate = {'title': title, 'original_title': original, 'media_type': data['type'],
                 'release_year': year, 'duration_minutes': duration, 'genres': genres, 'themes': [],
                 'synopsis': synopsis, 'publisher': data['publisher'], 'source_url': data['source_url']}
    return candidate, evidence


def fetch_issue(number: int, repo: str, token: str) -> dict:
    if not re.fullmatch(r'[\w.-]+/[\w.-]+', repo) or not token:
        raise IntakeError('GitHub 儲存庫或工作流程權限尚未設定')
    issue = request_json(f'https://api.github.com/repos/{repo}/issues/{number}', token=token)
    if issue.get('pull_request') or issue.get('state') != 'open':
        raise IntakeError('只允許開啟中的收錄申請 Issue')
    labels = [x.get('name') for x in issue.get('labels', []) if isinstance(x, dict)]
    if 'approved-ingest' not in labels:
        raise IntakeError('管理者尚未核准收錄')
    return issue


def process(root: Path, body: str, issue_number: int) -> tuple[str, str]:
    approved = fields_from_issue(body)
    metadata = api_metadata(approved)
    candidate, evidence = candidate_from_metadata(root, approved, metadata)
    work = validated_data(root, candidate, evidence)
    work['evidence'] = evidence[:240]
    wid, sid = publish_candidate(root, work)
    with (root / 'log.md').open('a', encoding='utf-8') as f:
        f.write(f'\n### {now().isoformat(timespec="seconds")} | APPROVED-INGEST | PASS\n'
                f'- GitHub Issue: #{issue_number}\n- 作品：{wid} {work["title"]}\n'
                f'- 來源：{sid} {work["source_url"]}\n'
                '- 管理者已批准 Issue；已用免費 API 核對作品 ID、形式及分類，執行 Lint 並重建簡報。\n')
    return wid, sid


def main():
    arg = argparse.ArgumentParser()
    arg.add_argument('--issue-number', type=int, required=True)
    args = arg.parse_args()
    if args.issue_number < 1:
        return 2
    try:
        issue = fetch_issue(args.issue_number, os.environ.get('GITHUB_REPOSITORY', ''), os.environ.get('GITHUB_TOKEN', ''))
        wid, sid = process(ROOT, str(issue.get('body') or ''), args.issue_number)
        print('APPROVED INGEST PASS:', wid, sid, 'docs/index.html rebuilt')
        return 0
    except (IntakeError, Rejected) as exc:
        print('APPROVED INGEST REJECTED:', exc, file=sys.stderr)
        return 2
    except Exception as exc:
        print('APPROVED INGEST ERROR:', type(exc).__name__, str(exc)[:200], file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
