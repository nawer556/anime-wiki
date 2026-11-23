/* Anime Wiki — multilingual, genre-aware, free anime discovery.
 * Data tiers: verified Wiki (elsewhere) > live AniList/Jikan/Kitsu > labeled offline examples.
 * Public searches never write to the Wiki or rebuild the slides.
 * API references: https://docs.anilist.co/guide/graphql/ ; https://docs.api.jikan.moe/ ;
 *                 https://www.mediawiki.org/wiki/API:Cross-site_requests
 */
(function (root) {
  'use strict';
  const ANILIST = 'https://graphql.anilist.co';
  const JIKAN = 'https://api.jikan.moe/v4/anime';
  const KITSU = 'https://kitsu.io/api/edge/anime';
  const WIKIPEDIA = 'https://zh.wikipedia.org/w/api.php';
  const CACHE_MS = 10 * 60 * 1000;
  const cache = new Map();
  let lastAttempt = 0;

  // Jikan / MyAnimeList genre codes; only verified codes are used in API requests.
  const JIKAN_GENRES = {
    Action: 1, Adventure: 2, Comedy: 4, Mystery: 7, Drama: 8,
    Fantasy: 10, Horror: 14, Mecha: 18, Music: 19, Romance: 22,
    'Sci-Fi': 24, Sports: 30, 'Slice of Life': 36,
    Supernatural: 37, Psychological: 40, Suspense: 41
  };
  const GENRE_GROUPS = {
    'Sci-Fi': ['科幻', '科學幻想', '科学幻想', 'science fiction', 'sci-fi', 'sci fi', 'sf', 'サイエンスフィクション', 'サイファイ'],
    Mystery: ['懸疑', '悬疑', '推理', '解謎', '解谜', 'mystery', 'thriller', 'ミステリー', 'サスペンス'],
    Romance: ['戀愛', '恋爱', '愛情', '爱情', 'romance', 'romantic', 'ラブコメ', '恋愛'],
    Fantasy: ['奇幻', 'fantasy', 'ファンタジー'],
    Action: ['動作', '动作', '戰鬥', '战斗', 'action', 'アクション', 'バトル'],
    Adventure: ['冒險', '冒险', 'adventure', '冒険'],
    Comedy: ['喜劇', '喜剧', '搞笑', 'comedy', 'コメディ'],
    Drama: ['劇情', '剧情', 'drama', 'ドラマ'],
    Horror: ['恐怖', '驚悚', '惊悚', 'horror', 'ホラー'],
    Sports: ['運動', '运动', '體育', '体育', 'sports', 'スポーツ'],
    Music: ['音樂', '音乐', 'music', '音楽'],
    'Slice of Life': ['日常', 'slice of life', '日常系'],
    Supernatural: ['超自然', 'supernatural', '超常現象'],
    Psychological: ['心理', 'psychological', '心理'],
    Mecha: ['機器人', '机器人', '機甲', '机甲', 'mecha', 'ロボット']
  };
  const GENRES = Object.fromEntries(Object.entries(GENRE_GROUPS).flatMap(([v, keys]) => keys.map(k => [k, v])));
  // Common Traditional Chinese, Simplified Chinese and Japanese names. Not an exhaustive dictionary.
  const TITLE_ALIASES = {
    '命運石之門':'Steins;Gate', '命运石之门':'Steins;Gate', '石頭門':'Steins;Gate', '石头门':'Steins;Gate',
    '進擊的巨人':'Attack on Titan', '进击的巨人':'Attack on Titan',
    '鬼滅之刃':'Demon Slayer', '鬼灭之刃':'Demon Slayer',
    '咒術迴戰':'Jujutsu Kaisen', '咒术回战':'Jujutsu Kaisen',
    '我推的孩子':'Oshi no Ko', '【我推的孩子】':'Oshi no Ko',
    '鏈鋸人':'Chainsaw Man', '链锯人':'Chainsaw Man',
    '鋼之鍊金術師':'Fullmetal Alchemist Brotherhood', '钢之炼金术师':'Fullmetal Alchemist Brotherhood',
    '藥師少女的獨語':'The Apothecary Diaries', '药师少女的独语':'The Apothecary Diaries',
    '天氣之子':'Weathering with You', '天气之子':'Weathering with You',
    '鈴芽之旅':'Suzume', '铃芽之旅':'Suzume',
    '紫羅蘭永恆花園':'Violet Evergarden', '紫罗兰永恒花园':'Violet Evergarden',
    '新世紀福音戰士':'Neon Genesis Evangelion', '新世纪福音战士':'Neon Genesis Evangelion',
    '刀劍神域':'Sword Art Online', '刀剑神域':'Sword Art Online',
    '寶可夢':'Pokemon', '宝可梦':'Pokemon',
    '排球少年':'Haikyu', '排球少年！！':'Haikyu',
    '葬送的芙莉蓮':'Frieren', '葬送的芙莉莲':'Frieren',
    '孤獨搖滾':'Bocchi the Rock', '孤独摇滚':'Bocchi the Rock',
    '輝夜姬想讓人告白':'Kaguya-sama Love is War', '辉夜大小姐想让我告白':'Kaguya-sama Love is War',
    '間諜家家酒':'Spy x Family', '间谍过家家':'Spy x Family',
    '聲之形':'A Silent Voice', '声之形':'A Silent Voice',
    '神隱少女':'Spirited Away', '千與千尋':'Spirited Away', '千与千寻':'Spirited Away',
    '你的名字':'Your Name', '你的名字。':'Your Name',
    '死亡筆記本':'Death Note', '死亡笔记':'Death Note',
    '夏日大作戰':'Summer Wars', '夏日大作战':'Summer Wars',
    '攻殼機動隊':'Ghost in the Shell', '攻壳机动队':'Ghost in the Shell',
    '星際牛仔':'Cowboy Bebop', '星际牛仔':'Cowboy Bebop',
    '心靈判官':'Psycho-Pass', '心理測量者':'Psycho-Pass', '心理测量者':'Psycho-Pass',
    '86 不存在的戰區':'86 Eighty Six', '86不存在的战区':'86 Eighty Six',
    '薇薇螢石眼之歌':'Vivy Fluorite Eyes Song', '薇薇萤石眼之歌':'Vivy Fluorite Eyes Song',
    '電馭叛客邊緣行者':'Cyberpunk Edgerunners', '赛博朋克边缘行者':'Cyberpunk Edgerunners',
    '冥王':'Pluto', '阿基拉':'Akira', '亞基拉':'Akira',
    '夏日時光':'Summer Time Rendering', '夏日重現':'Summer Time Rendering', '夏日重现':'Summer Time Rendering',
    '只有我不存在的城市':'Erased', '未來日記':'Future Diary', '未来日记':'Future Diary',
    '約定的夢幻島':'The Promised Neverland', '约定的梦幻岛':'The Promised Neverland',
    '怪物':'Monster', '冰菓':'Hyouka',
    '堀與宮村':'Horimiya', '堀与宫村':'Horimiya', '龍與虎':'Toradora', '龙与虎':'Toradora',
    '水果籃子':'Fruits Basket', '水果篮子':'Fruits Basket',
    '四月是你的謊言':'Your Lie in April', '四月是你的谎言':'Your Lie in April',
    '躍動青春':'Skip and Loafer', '跃动青春':'Skip and Loafer',
    '我內心的糟糕念頭':'The Dangers in My Heart', '我心里危险的东西':'The Dangers in My Heart',
    '轉生史萊姆':'That Time I Got Reincarnated as a Slime', '关于我转生变成史莱姆这档事':'That Time I Got Reincarnated as a Slime',
    '無職轉生':'Mushoku Tensei', '无职转生':'Mushoku Tensei',
    '來自深淵':'Made in Abyss', '来自深渊':'Made in Abyss',
    'Re從零開始的異世界生活':'Re Zero', '從零開始的異世界生活':'Re Zero', '从零开始的异世界生活':'Re Zero',
    '魔法使的新娘':'The Ancient Magus Bride',
    '灌籃高手':'Slam Dunk', '灌篮高手':'Slam Dunk',
    '藍色監獄':'Blue Lock', '蓝色监狱':'Blue Lock',
    '影子籃球員':'Kuroko no Basket', '黑子的篮球':'Kuroko no Basket',
    '飆速宅男':'Yowamushi Pedal', '飙速宅男':'Yowamushi Pedal',
    '食戟之靈':'Food Wars', '食戟之灵':'Food Wars',
    '吹響吧上低音號':'Sound Euphonium', '吹响吧上低音号':'Sound Euphonium',
    '輕音少女':'K-On', '轻音少女':'K-On',
    '暗殺教室':'Assassination Classroom', '暗杀教室':'Assassination Classroom',
    '夏目友人帳':'Natsume Book of Friends', '夏目友人帐':'Natsume Book of Friends',
    '名偵探柯南':'Detective Conan', '名侦探柯南':'Detective Conan',
    '航海王':'One Piece', '海賊王':'One Piece', '海贼王':'One Piece',
    '獵人':'Hunter x Hunter', '全職獵人':'Hunter x Hunter', '全职猎人':'Hunter x Hunter',
    '火影忍者':'Naruto', '我的英雄學院':'My Hero Academia', '我的英雄学院':'My Hero Academia',
    '一拳超人':'One Punch Man', '靈能百分百':'Mob Psycho 100', '灵能百分百':'Mob Psycho 100'
  };
  const TITLE_KEYS = Object.keys(TITLE_ALIASES).sort((a,b)=>b.length-a.length);
  const QUERY = `query PublicAnimeSearch($search: String, $formats: [MediaFormat], $genres: [String]) {
    Page(page: 1, perPage: 25) {
      media(type: ANIME, search: $search, format_in: $formats, genre_in: $genres, isAdult: false, sort: POPULARITY_DESC) {
        id title { romaji english native } synonyms format seasonYear episodes duration
        genres description(asHtml: false) averageScore siteUrl isAdult
      }
    }
  }`;
  const offlineEntries = [
    ['Steins;Gate','命運石之門','シュタインズ・ゲート','TV',['Sci-Fi','Mystery','Drama']],
    ['Psycho-Pass','心靈判官','サイコパス','TV',['Sci-Fi','Mystery','Action']],
    ['86 Eighty Six','86－不存在的戰區－','86―エイティシックス―','TV',['Sci-Fi','Action','Drama']],
    ['Vivy: Fluorite Eye\'s Song','Vivy -螢石眼之歌-','ヴィヴィ','TV',['Sci-Fi','Action','Drama','Music']],
    ['Cyberpunk: Edgerunners','電馭叛客：邊緣行者','サイバーパンク エッジランナーズ','TV',['Sci-Fi','Action','Drama']],
    ['Cowboy Bebop','星際牛仔','カウボーイビバップ','TV',['Sci-Fi','Action','Adventure']],
    ['Ghost in the Shell','攻殼機動隊','攻殻機動隊','MOVIE',['Sci-Fi','Action','Mystery']],
    ['AKIRA','阿基拉','AKIRA','MOVIE',['Sci-Fi','Action','Drama']],
    ['Summer Wars','夏日大作戰','サマーウォーズ','MOVIE',['Sci-Fi','Adventure','Drama']],
    ['Neon Genesis Evangelion','新世紀福音戰士','新世紀エヴァンゲリオン','TV',['Sci-Fi','Drama','Mecha','Psychological']],
    ['PLUTO','冥王','PLUTO','ONA',['Sci-Fi','Mystery','Drama']],
    ['Erased','只有我不存在的城市','僕だけがいない街','TV',['Mystery','Drama','Supernatural']],
    ['Monster','MONSTER 怪物','MONSTER','TV',['Mystery','Drama','Psychological']],
    ['Death Note','死亡筆記本','デスノート','TV',['Mystery','Supernatural','Psychological']],
    ['Hyouka','冰菓','氷菓','TV',['Mystery','Slice of Life']],
    ['The Promised Neverland','約定的夢幻島','約束のネバーランド','TV',['Mystery','Fantasy','Psychological']],
    ['Horimiya','堀與宮村','ホリミヤ','TV',['Romance','Comedy','Slice of Life']],
    ['Toradora!','龍與虎','とらドラ！','TV',['Romance','Comedy','Drama']],
    ['Fruits Basket','水果籃子','フルーツバスケット','TV',['Romance','Drama','Fantasy']],
    ['Your Lie in April','四月是你的謊言','四月は君の嘘','TV',['Romance','Drama','Music']],
    ['Weathering with You','天氣之子','天気の子','MOVIE',['Romance','Fantasy','Drama']],
    ['Suzume','鈴芽之旅','すずめの戸締まり','MOVIE',['Fantasy','Adventure','Drama']],
    ['Made in Abyss','來自深淵','メイドインアビス','TV',['Fantasy','Adventure','Drama']],
    ['Re:ZERO','Re：從零開始的異世界生活','Re:ゼロから始める異世界生活','TV',['Fantasy','Adventure','Drama']],
    ['Mushoku Tensei','無職轉生','無職転生','TV',['Fantasy','Adventure','Drama']],
    ['Demon Slayer','鬼滅之刃','鬼滅の刃','TV',['Fantasy','Action','Adventure']],
    ['Blue Lock','藍色監獄','ブルーロック','TV',['Sports','Drama']],
    ['Kuroko\'s Basketball','影子籃球員','黒子のバスケ','TV',['Sports','Comedy']],
    ['K-ON!','輕音少女','けいおん！','TV',['Music','Comedy','Slice of Life']],
    ['Sound! Euphonium','吹響吧！上低音號','響け！ユーフォニアム','TV',['Music','Drama','Slice of Life']],
    ['Jujutsu Kaisen','咒術迴戰','呪術廻戦','TV',['Action','Fantasy','Supernatural']],
    ['One Punch Man','一拳超人','ワンパンマン','TV',['Action','Comedy','Sci-Fi']]
  ].map(([title, chinese, original, format, genres],i) => ({
    provider:'離線參考', id:100000+i, title:chinese, original,
    synonyms:[title,chinese,original], format, year:null,episodes:null,duration:null,
    genres,description:'即時資料庫暫時無法使用；此為預先整理的作品範例，請至來源網站核對詳細資訊。',score:null,
    url:'https://myanimelist.net/anime.php?q='+encodeURIComponent(title)
  }));

  const normalized = value => String(value||'').normalize('NFKC').toLocaleLowerCase().replace(/[\s\p{P}\p{S}]/gu, '');
  const isChinese = value => /[\u3400-\u9fff]/.test(String(value||'')) && !/[\u3040-\u30ff]/.test(String(value||''));
  const cleanText = (value, limit=270) => String(value||'').replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().slice(0,limit);
  const notify = (options, msg) => {if (typeof options?.onProgress==='function') options.onProgress(msg);};

  function parse(query, media='all', genre='all') {
    const raw=String(query||'').trim().slice(0,80);
    // Recognize known anime names before removing request words (for example 葬送的芙莉蓮).
    const rawAlias=TITLE_KEYS.find(key=>normalized(raw)===normalized(key)||
      (key.length>=4&&normalized(raw).includes(normalized(key))));
    let leftover=rawAlias ? raw.replace(rawAlias,' ') : raw;
    const found=[];
    const aliases=Object.entries(GENRES).sort((a,b)=>b[0].length-a[0].length);
    for (const [alias,genreValue] of aliases) {
      const literal=alias.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
      const ascii=/^[\x00-\x7f]+$/.test(alias);
      const regex=new RegExp(ascii?`(^|[^a-z])(${literal})(?=$|[^a-z])`:literal,'gi');
      if (regex.test(leftover)) {
        if (!found.includes(genreValue)) found.push(genreValue);
        leftover=leftover.replace(regex, ascii?'$1 ':' ');
      }
    }
    const mediaRequested=media==='all'&&/電影|电影|劇場版|剧场版|\b(movie|film)\b|映画/i.test(raw)?'movie':media;
    const formats=mediaRequested==='movie'?['MOVIE']:mediaRequested==='tv'?['TV','TV_SHORT']:null;
    leftover=leftover.replace(/(?:\d+|[一二三兩两四五六七八九十])\s*(?:部|個|个)?|推薦|推荐|幫我|帮我|搜尋|搜索|尋找|查找|想看|請|请|給我|给我|日本|動漫|动漫|動畫|动画|電影|电影|電視|电视|TV|影集|作品|類型|类型|可以|有哪些|有什麼|有什么|看看|一部|三部|好看|幾部|几部/gi,' ')
      .replace(/\b(?:anime|recommend|find|show|me|some|of|a)\b/gi,' ')
      .replace(/[，,。!！?？、\s]+/g,' ').trim();
    const aliasKey=rawAlias||TITLE_KEYS.find(key=>normalized(key)===normalized(leftover) || normalized(key)===normalized(raw));
    const titleSearch=aliasKey?TITLE_ALIASES[aliasKey]:leftover||null;
    const fromFilter=GENRES[String(genre||'')]||GENRES[String(genre||'').toLowerCase()];
    if (fromFilter && !found.includes(fromFilter)) found.push(fromFilter);
    return {search:titleSearch,formats,genres:found.length?found:null,original:raw,translated:!!aliasKey,needsTranslation:!!(titleSearch&&isChinese(titleSearch)&&!aliasKey)};
  }

  function sanitize(entry) {
    if (!entry || !Number.isInteger(entry.id)||entry.id<=0||entry.isAdult) return null;
    const url=String(entry.siteUrl||'');
    if (!/^https:\/\/anilist\.co\/anime\/\d+(?:\/|$)/i.test(url)) return null;
    const title=entry.title||{};
    return {provider:'AniList',id:entry.id,title:cleanText(title.english||title.romaji||title.native,160),
      original:cleanText(title.native||title.romaji,160),synonyms:Array.isArray(entry.synonyms)?entry.synonyms.filter(x=>typeof x==='string').slice(0,12):[],
      format:String(entry.format||''),year:Number.isInteger(entry.seasonYear)?entry.seasonYear:null,
      episodes:Number.isInteger(entry.episodes)?entry.episodes:null,duration:Number.isInteger(entry.duration)?entry.duration:null,
      genres:Array.isArray(entry.genres)?entry.genres.filter(x=>typeof x==='string').slice(0,10):[],
      description:cleanText(entry.description),score:Number.isFinite(entry.averageScore)?entry.averageScore:null,url};
  }
  function parseJikanDuration(text) {
    const v=String(text||'').toLowerCase();
    const h=v.match(/(\d+)\s*(?:hr|hour)/),m=v.match(/(\d+)\s*(?:min|minute)/);
    const n=(h?Number(h[1])*60:0)+(m?Number(m[1]):0);
    return n||null;
  }
  function sanitizeJikan(entry) {
    const id=Number(entry?.mal_id); const url=String(entry?.url||'');
    if (!Number.isSafeInteger(id)||id<=0||!/^https:\/\/myanimelist\.net\/anime\/\d+(?:\/|$)/i.test(url))return null;
    if (/rx|hentai|erotica/i.test(String(entry.rating||'')))return null;
    const genres=[...(entry.genres||[]),...(entry.themes||[])].map(x=>String(x?.name||'')).filter(Boolean);
    if (genres.some(g=>/^(Hentai|Erotica)$/i.test(g)))return null;
    const score=Number(entry.score),year=Number(entry.year||entry.aired?.prop?.from?.year);
    return {provider:'Jikan',id,title:cleanText(entry.title_english||entry.title||entry.title_japanese,160),
      original:cleanText(entry.title_japanese||entry.title,160),
      synonyms:[...(Array.isArray(entry.title_synonyms)?entry.title_synonyms:[]),...(Array.isArray(entry.titles)?entry.titles.map(x=>x?.title).filter(Boolean):[])].slice(0,12),
      format:String(entry.type||'').toUpperCase().replace(/ /g,'_'),year:Number.isInteger(year)&&year>1900?year:null,
      episodes:Number.isInteger(entry.episodes)&&entry.episodes>0?entry.episodes:null,
      duration:parseJikanDuration(entry.duration),genres,description:cleanText(entry.synopsis),
      score:Number.isFinite(score)&&score>0?Math.round(score*10):null,url};
  }
  const KITSU_GENRES={Action:'Action',Adventure:'Adventure',Comedy:'Comedy',Drama:'Drama',Fantasy:'Fantasy',
    Mystery:'Mystery',Music:'Music',Romance:'Romance',Horror:'Horror',Psychological:'Psychological',Sports:'Sports',
    'Science Fiction':'Sci-Fi','Sci-Fi':'Sci-Fi','Sci Fi':'Sci-Fi','Slice of Life':'Slice of Life',
    Supernatural:'Supernatural',Mecha:'Mecha'};
  function sanitizeKitsu(entry,included=[]) {
    if (!entry||entry.type!=='anime'||!/^[0-9]+$/.test(String(entry.id)))return null;
    const a=entry.attributes||{};
    if(a.nsfw===true||String(a.ageRating||'').toUpperCase()==='R18')return null;
    const id=Number(entry.id);if(!Number.isSafeInteger(id)||id<=0)return null;
    const slug=String(a.slug||'');const path=/^[a-z0-9-]+$/i.test(slug)?slug:String(id);
    const formatValue=String(a.showType||a.subtype||'').toUpperCase();
    const format=formatValue==='MOVIE'?'MOVIE':formatValue==='TV'?'TV':formatValue;
    const catIds=new Set((entry.relationships?.categories?.data||[]).map(x=>String(x.id)));
    const genres=[...new Set(included.filter(x=>x.type==='categories'&&catIds.has(String(x.id)))
      .map(x=>KITSU_GENRES[String(x.attributes?.title||'')]).filter(Boolean))];
    const titles=a.titles||{},ep=Number(a.episodeCount),duration=Number(a.episodeLength),rating=Number(a.averageRating);
    return {provider:'Kitsu',id,title:cleanText(titles.en||a.canonicalTitle||titles.en_jp||titles.ja_jp,160),
      original:cleanText(titles.ja_jp||titles.en_jp||a.canonicalTitle,160),
      synonyms:[titles.en_jp,titles.en,titles.ja_jp,...(Array.isArray(a.abbreviatedTitles)?a.abbreviatedTitles:[])].filter(x=>typeof x==='string').slice(0,12),
      format,year:/^\d{4}/.test(String(a.startDate||''))?Number(String(a.startDate).slice(0,4)):null,
      episodes:Number.isInteger(ep)&&ep>0?ep:null,duration:Number.isInteger(duration)&&duration>0?duration:null,
      genres,description:cleanText(a.synopsis||a.description),score:Number.isFinite(rating)&&rating>0?rating:null,
      url:'https://kitsu.io/anime/'+path};
  }
  function satisfies(item,filters,duration) {
    if (filters.formats && !filters.formats.includes(item.format))return false;
    if (filters.genres && !filters.genres.every(g=>item.genres.includes(g)))return false;
    if (duration!=='all'&&(item.format!=='MOVIE'||item.duration===null||item.duration>Number(duration)))return false;
    return true;
  }
  async function fetchJSON(url,request={},ms=4400) {
    const ctrl=new AbortController();let timer;
    const timeout=new Promise((_,reject)=>{timer=setTimeout(()=>{ctrl.abort();reject(new Error('連線逾時'))},ms)});
    try {
      const response=await Promise.race([fetch(url,{...request,signal:ctrl.signal}),timeout]);
      if(!response.ok)throw new Error('HTTP '+response.status);
      return await Promise.race([response.json(),timeout]);
    } finally {clearTimeout(timer)}
  }
  async function requestAniList(filters,duration) {
    const payload=await fetchJSON(ANILIST,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},
      body:JSON.stringify({query:QUERY,variables:{search:filters.search,formats:filters.formats,genres:filters.genres}})},4600);
    if (payload?.errors?.length)throw new Error('GraphQL 回應錯誤');
    const rows=payload?.data?.Page?.media;
    if (!Array.isArray(rows))throw new Error('回傳格式不正確');
    return rows.map(sanitize).filter(Boolean).filter(w=>satisfies(w,filters,duration)).slice(0,18);
  }
  async function requestJikan(filters,duration) {
    const params=new URLSearchParams({limit:'25',sfw:'true',order_by:'popularity'});
    if(filters.search)params.set('q',filters.search);
    if(filters.genres?.length){
      const ids=filters.genres.map(g=>JIKAN_GENRES[g]);
      if(ids.some(id=>!id))throw new Error('不支援的類型');
      params.set('genres',ids.join(','));
    }
    if(filters.formats?.length===1&&filters.formats[0]==='MOVIE')params.set('type','movie');
    else if(filters.formats?.includes('TV'))params.set('type','tv');
    const payload=await fetchJSON(JIKAN+'?'+params.toString(),{headers:{Accept:'application/json'}},5000);
    if(!Array.isArray(payload?.data))throw new Error('回傳格式不正確');
    return payload.data.map(sanitizeJikan).filter(Boolean).filter(w=>satisfies(w,filters,duration)).slice(0,18);
  }
  async function requestKitsu(filters,duration) {
    if(!filters.search)throw new Error('僅支援作品名稱');
    const query=encodeURIComponent(filters.search);
    const payload=await fetchJSON(KITSU+'?filter%5Btext%5D='+query+'&page%5Blimit%5D=20&include=categories',
      {headers:{Accept:'application/vnd.api+json'}},3000);
    if(!Array.isArray(payload?.data))throw new Error('回傳格式不正確');
    return payload.data.map(w=>sanitizeKitsu(w,payload.included||[])).filter(Boolean)
      .filter(w=>satisfies(w,filters,duration)).slice(0,18);
  }
  // Chinese title not in local aliases: use Wikipedia's Chinese→English interlanguage link.
  // Works only if the exact Chinese Wikipedia page exists; failed lookups leave the title untouched.
  async function translateChineseTitle(title) {
    if(!isChinese(title)||title.length>60)return null;
    const params=new URLSearchParams({action:'query',format:'json',origin:'*',titles:title,redirects:'1',
      prop:'langlinks',lllang:'en',lllimit:'5'});
    try {
      const data=await fetchJSON(WIKIPEDIA+'?'+params.toString(),{headers:{Accept:'application/json'}},2500);
      const pages=Object.values(data?.query?.pages||{});
      const page=pages.find(p=>p && !p.missing && Array.isArray(p.langlinks)&&p.langlinks.length);
      const english=page?.langlinks?.find(x=>x.lang==='en')?.['*'];
      if(typeof english==='string'&&english.length>1&&english.length<90){
        return english.replace(/\s*\((?:TV series|anime|film|manga|Japanese TV series|animated film)\)\s*$/i,'').trim();
      }
    }catch(_error){/* Normal fallback: no translation service required for offline aliases. */}
    return null;
  }
  function offlineMatches(filters,duration) {
    const q=normalized(filters.search||'');
    return offlineEntries.filter(w=>satisfies(w,filters,duration))
      .filter(w=>!q||[w.title,w.original,...w.synonyms].some(name=>normalized(name).includes(q)))
      .slice(0,18);
  }
  async function firstNonempty(jobs,failures) {
    // Launch both public APIs at once; avoid long sequential 5+5+3 second stalls.
    const tasks=jobs.map(([name,lookup])=>lookup().then(items=>{
      if(items.length)return {items,provider:name};
      failures.push(name+' 無符合資料');throw new Error('empty');
    }).catch(error=>{
      if(error.message!=='empty')failures.push(name+' '+error.message);
      throw error;
    }));
    try{return await Promise.any(tasks)}catch(_e){return null}
  }
  async function search(query,options={}) {
    const original=parse(query,options.media||'all',options.genre||'all');
    const duration=String(options.duration||'all');
    if(!original.search&&!original.genres&&!original.formats)return {items:[],skipped:true};
    const key=JSON.stringify({filters:original,duration});
    const previous=cache.get(key);
    if(previous && Date.now()-previous.time<(previous.ttl||CACHE_MS))return {...previous.result,cached:true};
    const wait=Math.max(0,600-(Date.now()-lastAttempt));
    if(wait)await new Promise(resolve=>setTimeout(resolve,wait));
    lastAttempt=Date.now();
    const filters={...original};
    let translated='';
    if(filters.needsTranslation){
      notify(options,'正在把中文名稱轉換為英文／日文查詢…');
      const name=await translateChineseTitle(filters.search);
      if(name){filters.search=name;translated=name}
    }
    notify(options,(filters.genres?.length?'類型：'+filters.genres.join('、')+'；':'')+
      (filters.search?'名稱：'+filters.search+'；':'')+'正在查詢免費動漫資料庫…');
    const failures=[];
    let result=await firstNonempty([
      ['Jikan',()=>requestJikan(filters,duration)],
      ['AniList',()=>requestAniList(filters,duration)]
    ],failures);
    if(!result && filters.search){
      notify(options,'主要免費資料庫沒有結果，正在嘗試 Kitsu 備援…');
      try{
        const items=await requestKitsu(filters,duration);
        if(items.length)result={items,provider:'Kitsu'};
        else failures.push('Kitsu 無符合資料');
      }catch(error){failures.push('Kitsu '+error.message)}
    }
    if(!result){
      const offline=offlineMatches(filters,duration);
      if(offline.length){
        result={items:offline,provider:'離線參考',fallback:true,
          notice:'免費 API 暫時無法提供符合條件的結果，以下是預先整理的離線動漫參考清單（非即時資料、尚未經 Wiki 驗證）。可點連結至外部網站核對。'};
      }else{
        result={items:[],provider:'外部資料庫',fallback:true,
          notice:'免費 API 查詢未取得結果（'+failures.slice(0,3).join('；')+'）。請確認網路連線、放寬篩選或稍後再試。'};
      }
    }else{
      result={...result,fallback:result.provider!=='AniList',
        notice:(translated?'中文名稱已對照為「'+translated+'」；':'')+
          (result.provider==='Jikan'?'已使用 Jikan 類型／名稱搜尋。':'已從 '+result.provider+' 取得結果。')};
    }
    cache.set(key,{time:Date.now(),result,ttl:result.provider==='離線參考'?60000:CACHE_MS});
    return {...result,cached:false};
  }
  const api={search,parse,sanitize,sanitizeJikan,sanitizeKitsu,satisfies,translateChineseTitle,offlineMatches,
    GENRES,TITLE_ALIASES,offlineEntries};
  root.AnimeExternalSearch=api;
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
