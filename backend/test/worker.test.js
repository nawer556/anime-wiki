import test from 'node:test';
import assert from 'node:assert/strict';
import worker,{cleanQuery} from '../src/index.js';
function kv(){const m=new Map();return {get:async k=>m.get(k),put:async(k,v)=>{m.set(k,v)}}}
function env(overrides={}){return {SITE_ORIGIN:'https://student.github.io',DISPATCH_ENABLED:'false',REQUEST_KV:kv(),GITHUB_OWNER:'student',GITHUB_REPO:'Anime-Wiki',GITHUB_DISPATCH_TOKEN:'test-token',RATE_LIMIT_SALT:'test-salt',...overrides}}
function req(body,origin='https://student.github.io'){return new Request('https://worker.example/request',{method:'POST',headers:{origin,'content-type':'application/json','cf-connecting-ip':'203.0.113.1'},body:JSON.stringify(body)})}
const payload={query:'科幻 懸疑',media_type:'movie',genre:'all',duration:'all'};
test('query validation excludes unsafe input',()=>{assert.equal(cleanQuery(' https://example.org '),'');assert.equal(cleanQuery('科幻 懸疑'),'科幻 懸疑');assert.equal(cleanQuery('a'.repeat(90)),'')});
test('health does not leak any secrets',async()=>{const r=await worker.fetch(new Request('https://worker.example/health'),env());assert.equal(r.status,200);assert.equal((await r.text()).includes('test-token'),false)});
test('reject cross-origin before any other work',async()=>{const r=await worker.fetch(req(payload,'https://evil.example'),env());assert.equal(r.status,403)});
test('free mode never dispatches or uses AI',async()=>{const r=await worker.fetch(req(payload),env());assert.equal(r.status,503);assert.match(await r.text(),/尚未啟用/)});
test('valid request dispatched once, repeated query deduplicated',async()=>{
 let calls=0;const orig=globalThis.fetch;globalThis.fetch=async(url,options)=>{calls++;assert.match(String(url),/api.github.com/);assert.equal(JSON.parse(options.body).event_type,'anime_search');return new Response(null,{status:204})};
 try{const e=env({DISPATCH_ENABLED:'true'});let r=await worker.fetch(req(payload),e);assert.equal(r.status,202);r=await worker.fetch(req(payload),e);assert.equal(r.status,200);assert.equal(calls,1)}finally{globalThis.fetch=orig}
});
test('backend caps daily queued requests per IP',async()=>{
 const orig=globalThis.fetch;globalThis.fetch=async()=>new Response(null,{status:204});
 try{const e=env({DISPATCH_ENABLED:'true',MAX_IP_JOBS:'1'});assert.equal((await worker.fetch(req(payload),e)).status,202);assert.equal((await worker.fetch(req({...payload,query:'神秘 動畫'}),e)).status,429)}finally{globalThis.fetch=orig}
});
