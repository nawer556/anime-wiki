/* GitHub Issues is the free moderation queue; no visitor has Wiki write permission.
   Open a prefilled Issue; the site never directly writes to GitHub or exposes tokens. */
(function(root){
  'use strict';
  const PATTERN=/^[a-zA-Z0-9-]+\/[a-zA-Z0-9_.-]+$/;
  const safeText=s=>String(s||'').replace(/[\r\n\x00-\x1f]/g,' ').trim().slice(0,100);
  function inferRepository(location){
    const host=String(location?.hostname||'').toLowerCase();
    if(!host.endsWith('.github.io'))return '';
    const owner=host.slice(0,-'.github.io'.length);
    const repo=String(location?.pathname||'').split('/').filter(Boolean)[0]||'';
    return PATTERN.test(owner+'/'+repo)?owner+'/'+repo:'';
  }
  function repository(){
    const configured=String(root.ANIME_GITHUB_REPOSITORY||'').trim();
    const candidate=configured||inferRepository(root.location);
    return PATTERN.test(candidate)?candidate:'';
  }
  function buildUrl(work,repo){
    if(!PATTERN.test(String(repo||'')))throw new Error('請先在 docs/assets/repository-config.js 設定 GitHub 儲存庫 owner/repo');
    const provider=String(work?.provider||'');
    const id=String(work?.id||'');
    // Real AniList / Kitsu records can be imported after approval. Jikan and
    // cached offline examples are suggestions only until a valid ID is supplied.
    const ready=(provider==='AniList'||provider==='Kitsu')&&/^[1-9]\d{0,8}$/.test(id);
    const title=safeText(work?.title||work?.original||'新動漫');
    const url=ready?(provider==='AniList'?'https://anilist.co/anime/':'https://kitsu.io/anime/')+id:'';
    const body=[
      'Anime Wiki 收錄申請',
      '',
      'Provider: '+(ready?provider:'待補 AniList 或 Kitsu'),
      'Provider-ID: '+(ready?id:'待補'),
      'Title: '+title,
      'Source-URL: '+url,
      '',
      '訪客建議，尚未 Ingest。管理者請先核對作品頁與版本，並確認 Provider 與 ID。',
      '完成檢查後，才套用 approved-ingest 標籤；無需 OpenAI API。'
    ].join('\n');
    const params=new URLSearchParams({title:'[收錄申請] '+title,body});
    return 'https://github.com/'+repo+'/issues/new?'+params.toString();
  }
  root.AnimeIssueRequest={buildUrl,inferRepository,repository};
  if(typeof module!=='undefined'&&module.exports)module.exports=root.AnimeIssueRequest;
})(typeof window!=='undefined'?window:globalThis);
