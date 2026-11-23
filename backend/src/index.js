/** Cloudflare Worker: controlled request queue, NEVER runs the LLM in a browser. */
function reply(body,status=200,origin='',extra={}){
 const headers={'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff',...extra};
 if(origin){headers['access-control-allow-origin']=origin;headers['vary']='Origin';}
 return new Response(JSON.stringify(body),{status,headers});
}
function hashKey(bytes){return crypto.subtle.digest('SHA-256',new TextEncoder().encode(bytes)).then(x=>Array.from(new Uint8Array(x),b=>b.toString(16).padStart(2,'0')).join(''))}
function cleanQuery(s){
 if(typeof s!=='string')return '';
 const q=s.normalize('NFKC').trim().replace(/\s+/g,' ');
 if(q.length<2||q.length>80||/[<>\r\n\x00-\x1f]/.test(q)||/https?:\/\/|@|api[_-]?key|密碼|token/i.test(q))return '';
 if(!/[\p{L}\p{N}]/u.test(q))return '';
 return q;
}
const types=new Set(['all','movie','tv']);
const durations=new Set(['all','90','120']);
const validGenre=x=>typeof x==='string'&&x.length<=24&&!/[<>\r\n]/.test(x);
export default {
 async fetch(request,env){
  const origin=request.headers.get('origin')||'';
  const allowed=origin===env.SITE_ORIGIN||Boolean(env.DEV_ORIGIN&&origin===env.DEV_ORIGIN);
  const u=new URL(request.url);
  if(u.pathname==='/health'&&request.method==='GET')return reply({ok:true,dispatch_enabled:env.DISPATCH_ENABLED==='true',service:'Anime Wiki request queue'});
  if(u.pathname!=='/request')return reply({message:'Not found'},404);
  if(request.method==='OPTIONS')return allowed?new Response(null,{status:204,headers:{'access-control-allow-origin':origin,'access-control-allow-methods':'POST, OPTIONS','access-control-allow-headers':'content-type','access-control-max-age':'3600','vary':'Origin'}}):reply({message:'Origin not allowed'},403);
  if(request.method!=='POST')return reply({message:'Method not allowed'},405);
  if(!allowed)return reply({message:'此網站來源尚未獲准提交請求'},403);
  if(request.headers.get('content-type')?.split(';')[0]!=='application/json')return reply({message:'Expected JSON'},415,origin);
  const bodyText=await request.text();if(bodyText.length>2500)return reply({message:'輸入過長'},413,origin);
  let data;try{data=JSON.parse(bodyText)}catch{return reply({message:'JSON 格式錯誤'},400,origin)}
  const query=cleanQuery(data?.query);
  if(!query||!types.has(data?.media_type)||!durations.has(data?.duration)||!validGenre(data?.genre))return reply({message:'請輸入有效的動漫搜尋條件'},400,origin);
  if(env.DISPATCH_ENABLED!=='true')return reply({message:'公開 AI 自動擴充尚未啟用；你仍可免費搜尋現有動漫。'},503,origin);
  if(!env.REQUEST_KV||!env.GITHUB_DISPATCH_TOKEN||!env.GITHUB_OWNER||!env.GITHUB_REPO||!env.RATE_LIMIT_SALT)return reply({message:'後端尚未完成安全設定'},503,origin);
  const ip=request.headers.get('cf-connecting-ip')||'unknown';const day=new Date().toISOString().slice(0,10);
  const ipHash=await hashKey(ip+day+env.RATE_LIMIT_SALT);
  const jobHash=await hashKey(JSON.stringify([query,data.media_type,data.genre,data.duration]));
  const ipKey=`ip:${day}:${ipHash}`,totalKey=`global:${day}`,dedupeKey=`dedupe:${jobHash}`;
  const [prev,used,globalUsed]=await Promise.all([env.REQUEST_KV.get(dedupeKey),env.REQUEST_KV.get(ipKey),env.REQUEST_KV.get(totalKey)]);
  if(prev)return reply({ok:true,status:'already_requested',message:'相同條件已經提交過，請稍後重新搜尋。'},200,origin);
  const ipLimit=Math.min(Math.max(Number(env.MAX_IP_JOBS)||2,1),10),globalLimit=Math.min(Math.max(Number(env.MAX_DAILY_JOBS)||3,1),20);
  if(Number(used||0)>=ipLimit||Number(globalUsed||0)>=globalLimit)return reply({message:'今日擴充次數已達上限，請明天再試。'},429,origin,{'retry-after':'3600'});
  const target=`https://api.github.com/repos/${encodeURIComponent(env.GITHUB_OWNER)}/${encodeURIComponent(env.GITHUB_REPO)}/dispatches`;
  let dispatched;try{
   dispatched=await fetch(target,{method:'POST',headers:{'authorization':`Bearer ${env.GITHUB_DISPATCH_TOKEN}`,'accept':'application/vnd.github+json','x-github-api-version':'2022-11-28','user-agent':'anime-wiki-worker','content-type':'application/json'},body:JSON.stringify({event_type:'anime_search',client_payload:{query,media_type:data.media_type,genre:data.genre,duration:data.duration}})});
  }catch{return reply({message:'排程服務暫時無法連線'},502,origin)}
  if(!dispatched.ok)return reply({message:'排程服務尚未就緒，請通知網站管理者。'},502,origin);
  // KV limits are best effort / eventually consistent; GitHub Actions also has a stricter serialized attempt budget.
  await Promise.all([
   env.REQUEST_KV.put(dedupeKey,'queued',{expirationTtl:21600}),
   env.REQUEST_KV.put(ipKey,String(Number(used||0)+1),{expirationTtl:90000}),
   env.REQUEST_KV.put(totalKey,String(Number(globalUsed||0)+1),{expirationTtl:90000})
  ]);
  return reply({ok:true,status:'queued',message:'已接受擴充請求；完成驗證及部署後才會公開。'},202,origin);
 }
};
export {cleanQuery};
