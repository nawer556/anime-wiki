'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const api = require('../docs/assets/anilist-api.js');
const jikan = (title='Steins;Gate',genres=['Sci-Fi','Mystery'])=>({
  mal_id:9253,title,title_english:title,title_japanese:'シュタインズ・ゲート',type:'TV',year:2011,
  url:'https://myanimelist.net/anime/9253/Steins_Gate',
  genres:genres.map(name=>({name})),themes:[],duration:'24 min per ep',rating:'PG-13',synopsis:'Test synopsis.'
});
const anilist = {id:9253,title:{english:'Steins;Gate',native:'シュタインズ・ゲート'},
  synonyms:[],format:'TV',genres:['Sci-Fi','Mystery'],isAdult:false,
  siteUrl:'https://anilist.co/anime/9253/SteinsGate'};
function mock(handler, fn) {
  const old=global.fetch;
  global.fetch=handler;
  return Promise.resolve().then(fn).finally(()=>{global.fetch=old});
}
test('Traditional/Simplified Chinese title, English and Japanese all parsed',()=>{
  assert.equal(api.parse('命運石之門').search,'Steins;Gate');
  assert.equal(api.parse('命运石之门').search,'Steins;Gate');
  assert.equal(api.parse('Steins;Gate').search,'Steins;Gate');
  assert.equal(api.parse('シュタインズ・ゲート').search,'シュタインズ・ゲート');
  assert.equal(api.parse('推薦葬送的芙莉蓮').search,'Frieren');
});
test('Chinese/English/Japanese genre queries become discovery, not title search',()=>{
  for(const t of ['科幻','科学幻想','science fiction','Sci-Fi','サイファイ']){
    const f=api.parse(t); assert.equal(f.search,null,t); assert.deepEqual(f.genres,['Sci-Fi'],t);
  }
  assert.deepEqual(api.parse('推薦科幻懸疑動畫電影').formats,['MOVIE']);
  assert.deepEqual(api.parse('推薦科幻懸疑動畫電影').genres,['Sci-Fi','Mystery']);
  assert.deepEqual(api.parse('戀愛').genres,['Romance']);
  assert.deepEqual(api.parse('恋爱').genres,['Romance']);
  assert.deepEqual(api.parse('ミステリー').genres,['Mystery']);
});
test('Jikan genre request supplies correct genres ID, returns matching results',async()=>{
  const calls=[];
  await mock(async url=>{
    calls.push(String(url));
    if(String(url).includes('jikan.moe')){
      const p=new URL(url).searchParams;
      assert.equal(p.get('genres'),'24');
      assert.equal(p.get('q'),null);
      return {ok:true,json:async()=>({data:[jikan()]})};
    }
    return {ok:false,status:500};
  },async()=>{
    const res=await api.search('科幻');
    assert.equal(res.items[0].provider,'Jikan');
    assert.equal(res.items[0].title,'Steins;Gate');
    assert.equal(res.items.length,1);
  });
  assert.equal(calls.length,2);
});
test('Every external API failure still displays labeled offline Sci-Fi examples',async()=>{
  await mock(async()=>({ok:false,status:503}),async()=>{
    const res=await api.search('科幻動作');
    assert.equal(res.provider,'離線參考');
    assert.ok(res.items.length>=2);
    assert.ok(res.items.every(x=>x.provider==='離線參考'));
    assert.ok(res.items.every(x=>x.genres.includes('Sci-Fi')&&x.genres.includes('Action')));
  });
});
test('Title search works with English fallback and never requires API key',async()=>{
  const calls=[];
  await mock(async url=>{
    calls.push(String(url));
    if(String(url).startsWith('https://graphql.anilist.co'))
      return {ok:true,json:async()=>({data:{Page:{media:[anilist]}}})};
    return {ok:false,status:503};
  },async()=>{
    const result=await api.search('Steins;Gate');
    assert.equal(result.items[0].title,'Steins;Gate');
    assert.equal(result.provider,'AniList');
  });
  assert.ok(calls.some(s=>s.includes('graphql.anilist.co')));
});
test('Unknown Chinese title can be translated through Wikipedia language links',async()=>{
  const calls=[];
  await mock(async(url,options)=>{
    calls.push(String(url));
    if(String(url).includes('wikipedia.org')){
      assert.equal(new URL(String(url)).searchParams.get('titles'),'魔法少女小圓');
      return {ok:true,json:async()=>({query:{pages:{'123':{pageid:123,langlinks:[{lang:'en','*':'Puella Magi Madoka Magica'}]}}}})};
    }
    if(String(url).includes('jikan.moe')){
      assert.equal(new URL(String(url)).searchParams.get('q'),'Puella Magi Madoka Magica');
      return {ok:true,json:async()=>({data:[jikan('Puella Magi Madoka Magica', ['Fantasy'])]})};
    }
    return {ok:false,status:500};
  },async()=>{
    const res=await api.search('魔法少女小圓');
    assert.equal(res.items[0].title,'Puella Magi Madoka Magica');
    assert.match(res.notice,/中文名稱已對照/);
  });
  assert.ok(calls.some(s=>s.includes('wikipedia.org')));
});
test('Strict film duration never guesses unknown runtime in fallback results',()=>{
  const f=api.parse('科幻動畫電影');
  const results=api.offlineMatches(f,'120');
  assert.equal(results.length,0);
  assert.equal(api.offlineMatches(f,'all').every(x=>x.format==='MOVIE'),true);
});
test('Sanitizers block unsafe links and adult records',()=>{
  assert.equal(api.sanitize({...anilist,siteUrl:'https://phish.invalid'}),null);
  assert.equal(api.sanitize({...anilist,isAdult:true}),null);
  assert.equal(api.sanitizeJikan({...jikan(),rating:'Rx - Hentai'}),null);
  assert.equal(api.sanitizeKitsu({type:'anime',id:'12',attributes:{ageRating:'R18'}}),null);
});
test('Empty query without filters never sends a request',async()=>{
  await mock(async()=>{throw new Error('Should not fetch')},async()=>{
    assert.equal((await api.search('')).skipped,true);
  });
});
test('API calls settle without indefinite loading, even when providers never respond',async()=>{
  // Inject a rejected request rather than actually waiting 5 seconds in unit test.
  await mock(async()=>{throw new Error('Connection failed')},async()=>{
    const res=await api.search('音樂');
    assert.equal(res.provider,'離線參考');
    assert.ok(res.items.length>=1);
  });
});
test('Unresponsive providers settle within bounded timeout with offline genre references',async()=>{
  const started=Date.now();
  await mock(async()=>new Promise(()=>{}),async()=>{
    const res=await api.search('懸疑');
    assert.equal(res.provider,'離線參考');
    assert.ok(res.items.length>0);
    assert.ok(Date.now()-started<6800,'Should not hang indefinitely');
  });
});
