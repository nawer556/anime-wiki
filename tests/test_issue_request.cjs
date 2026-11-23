'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const tool = require('../docs/assets/issue-request.js');
test('builds a prefilled GitHub issue without write access or tokens', () => {
  const out = new URL(tool.buildUrl({provider:'AniList',id:9253,title:'命運石之門'},'example-user/Anime-Wiki'));
  assert.equal(out.origin,'https://github.com');
  assert.equal(out.pathname,'/example-user/Anime-Wiki/issues/new');
  assert.match(out.searchParams.get('body'),/Provider: AniList\nProvider-ID: 9253/);
  assert.match(out.searchParams.get('body'),/Title: 命運石之門/);
});
test('offline results are not falsely qualified for automated ingest', () => {
  const url = new URL(tool.buildUrl({provider:'離線參考',id:100001,title:'命運石之門'},'owner/repo'));
  assert.match(url.searchParams.get('body'),/Provider: 待補 AniList 或 Kitsu/);
  assert.match(url.searchParams.get('body'),/Provider-ID: 待補/);
});
test('github pages repository is derived only on github.io', () => {
  assert.equal(tool.inferRepository({hostname:'alice.github.io',pathname:'/Anime-Wiki/search.html'}),'alice/Anime-Wiki');
  assert.equal(tool.inferRepository({hostname:'localhost',pathname:'/Anime-Wiki/search.html'}),'');
  assert.throws(()=>tool.buildUrl({title:'a'},'evil//example'));
});
