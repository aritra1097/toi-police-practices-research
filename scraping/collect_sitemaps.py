"""Public TOI sitemap inventory plus transparently selected article metadata.

Static sitemap URLs/slugs are NOT headlines. Actual titles come only from news
feed news:title or article JSON-LD/HTML metadata. Dates retain their source type.
"""
import argparse,concurrent.futures,csv,datetime as dt,gzip,hashlib,json,re,sqlite3,threading,time,os
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from urllib.parse import urlsplit,urlunsplit
from lxml import etree,html
try:
 from .clean_article_text import add_clean_text_fields
except ImportError:
 from clean_article_text import add_clean_text_fields
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'sitemap_output'
NS={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','n':'http://www.google.com/schemas/sitemap-news/0.9'}
UA='TOIArchiveResearch/1.0 (public news archive research; low request rate)'
NEXT=0.;RATE=threading.Lock();WRITE=threading.Lock();STOP=threading.Event()
NOW=dt.datetime.now(dt.timezone.utc).isoformat()
CURRENT_IST_MONTH=dt.datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%B')
AS_OF_DATE_NY=dt.datetime.now(ZoneInfo('America/New_York')).date().isoformat()
SOURCE_TODAY_IST=dt.datetime.now(ZoneInfo('Asia/Kolkata')).date()
REQUEST_START=dt.date(2024,1,1);REQUEST_END=SOURCE_TODAY_IST
ARTICLE=re.compile(r'/(?:amp_)?articleshow/(\d+)\.cms',re.I)
WB=re.compile(r'\b(?:west bengal|bengal|kolkata|calcutta|howrah|hooghly|siliguri|darjeeling|jalpaiguri|cooch behar|alipurduar|dinajpur|raiganj|malda|murshidabad|nadia|24 parganas|barasat|basirhat|bongaon|gaighata|baruipur|canning|barrackpore|bidhannagar|new town|asansol|durgapur|burdwan|bardhaman|birbhum|bankura|purulia|midnapore|medinipur|jhargram|lalgarh|nandigram|kharagpur|haldia|chopra|goalpokhar)\b')
POLICE=re.compile(r'\b(?:police\w*|cops?|constables?|officers?|custody|custodial|stf|bsf|crpf)\b')
OUTCOME=re.compile(r'\b(?:shot|shoot\w*|gunned|fir\w*|kill\w*|dead|death\w*|dies?|died|encounters?|gunfights?|gunbattles?|shootouts?)\b')
WEAPON=re.compile(r'\b(?:guns?|pistols?|revolvers?|rifles?|firearms?|weapons?|arms|carbines?)\b')
TAKE=re.compile(r'\b(?:snatch\w*|grab\w*|wrest\w*|disarm\w*|overpower\w*)\b')
ENCOUNTER=re.compile(r'\b(?:encounters?|gunfights?|gunbattles?|shootouts?)\b')

def utcnow():return dt.datetime.now(dt.timezone.utc).isoformat()
def publication_day_ist(value):
 try:
  stamp=dt.datetime.fromisoformat(str(value).replace('Z','+00:00'))
  return stamp.astimezone(ZoneInfo('Asia/Kolkata')).date() if stamp.tzinfo else None
 except (TypeError,ValueError):return None
def publication_flags(value,start=None,end=None):
 start=start or REQUEST_START;end=end or REQUEST_END;day=publication_day_ist(value)
 return dict(requested_start_ist=start.isoformat(),requested_end_ist=end.isoformat(),publication_day_ist=day.isoformat() if day else '',within_requested_ist_window=int(start<=day<=end) if day else 'unknown',after_requested_ist_end=int(day>end) if day else 'unknown',before_requested_ist_start=int(day<start) if day else 'unknown')
def partition_in_window(url,start,end):
 match=re.search(r'/(\d{4})-([A-Za-z]+)-\d+\.xml$',url)
 if not match:return False
 try:partition=dt.datetime.strptime(match[1]+'-'+match[2],'%Y-%B').date()
 except ValueError:return False
 return start.replace(day=1)<=partition<=min(end,SOURCE_TODAY_IST).replace(day=1)
def finalize_article_metadata(result):
 result=add_clean_text_fields(result)
 # Lexical flags are retrieval aids, never event labels. Crucially, these use
 # cleaned main-article text rather than the preserved recommendation suffix.
 text=result['articleBody_clean'].lower()
 result['body_lexical_signals']={name:bool(rx.search(text)) for name,rx in [('police',POLICE),('outcome',OUTCOME),('weapon',WEAPON),('taking',TAKE),('encounter',ENCOUNTER)]}
 result['body_lexical_signals_status']='no_body' if not text else ('review_retained_boilerplate_marker' if result['articleBody_cleaning_review_needed'] else 'cleaned_body_retrieval_aid')
 result.update(publication_flags(result.get('publication_date','')))
 return result
def atomic(path,obj):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2));os.replace(tmp,path)
def throttle():
 global NEXT
 with RATE:
  delay=max(0,NEXT-time.monotonic())
  if delay:time.sleep(delay)
  NEXT=time.monotonic()+.56
def get(url,kind='sitemap',refresh=False):
 key=hashlib.sha256(url.encode()).hexdigest();statuspath=OUT/'statuses'/f'{key}.json'
 if statuspath.exists() and not refresh:
  s=json.loads(statuspath.read_text())
  if s.get('status')=='success' and Path(s['raw_file']).exists():return gzip.open(s['raw_file'],'rb').read(),s
 for attempt in range(1,4):
  if STOP.is_set():return b'',dict(url=url,status='not_requested_after_access_stop')
  throttle();retrieved=utcnow();s=dict(url=url,kind=kind,attempt=attempt,retrieved_at_utc=retrieved)
  try:
   try:
    with urlopen(Request(url,headers={'User-Agent':UA,'Accept-Encoding':'identity'}),timeout=45) as r:status=r.status;body=r.read();s['response_url']=r.url
   except HTTPError as e:status=e.code;body=e.read();s['response_url']=e.url
   path=OUT/'raw'/f'{key}.{re.sub(r"[^0-9]","",retrieved)}.gz'
   with gzip.open(path,'wb',compresslevel=6) as f:f.write(body)
   s.update(http_status=status,response_bytes=len(body),raw_file=str(path),sha256=hashlib.sha256(body).hexdigest())
   if status in {401,403,429}:s.update(status='access_stop',error=f'HTTP{status}; no access bypass');STOP.set()
   elif status!=200:s.update(status='http_error',error=f'HTTP{status}')
   else:
    prefix=body[:20000].decode('utf-8','replace').lower()
    if '<title>access denied' in prefix or 'verify you are human' in prefix:s.update(status='access_stop',error='Access challenge; no bypass');STOP.set()
    else:s['status']='success'
   with WRITE:
    atomic(statuspath,s)
    with (OUT/'attempts.jsonl').open('a') as f:f.write(json.dumps(s)+'\n')
   if s['status']=='success':return body,s
   if STOP.is_set():return body,s
  except Exception as e:
   s.update(status='network_error',error=repr(e))
   with WRITE:
    atomic(statuspath,s)
    with (OUT/'attempts.jsonl').open('a') as f:f.write(json.dumps(s)+'\n')
  if attempt<3:time.sleep(2**attempt)
 return b'',s

def select(url):
 t=re.sub(r'[^a-z0-9]+',' ',urlsplit(url).path.lower()).strip()
 wb=bool(WB.search(t));police=bool(POLICE.search(t));outcome=bool(OUTCOME.search(t));take=bool(TAKE.search(t));weapon=bool(WEAPON.search(t));encounter=bool(ENCOUNTER.search(t))
 routes=[]
 if wb and encounter:routes.append('WB_proxy_encounter')
 if wb and police and outcome:routes.append('WB_proxy_police_outcome')
 if take and weapon:routes.append('national_weapon_taking')
 return wb,';'.join(routes)
def canonical(url):
 u=urlsplit(url);return urlunsplit(('https',u.netloc.lower(),re.sub('/+','/',u.path).replace('/amp_articleshow/','/articleshow/'),'',''))
def process_sitemap(url):
 body,status=get(url,'sitemap',refresh=url.endswith('/today') or url.endswith('/yesterday') or 'sitemap-yesterday-' in url or 'sitemap-today-' in url or f'/{CURRENT_IST_MONTH}-' in url)
 if status['status']!='success':return [],status
 try:
  doc=etree.fromstring(body);rows=[]
  if etree.QName(doc).localname=='sitemapindex':
   children=[x.findtext('s:loc',namespaces=NS) for x in doc.findall('s:sitemap',NS)]
   child_statuses=[]
   for child in children:
    if not child or urlsplit(child).hostname!='timesofindia.indiatimes.com':continue
    if re.search(r'/\d{4}-[A-Za-z]+-\d+\.xml$',child) and not partition_in_window(child,REQUEST_START,REQUEST_END):continue
    child_rows,child_status=process_sitemap(child);rows.extend(child_rows);child_statuses.append(child_status)
   status.update(sitemap_kind='index',child_sitemaps=child_statuses,parsed_records=len(rows),news_title_records=sum(bool(x['news_title']) for x in rows))
   status['status']='success' if rows and all(x['status']=='success' for x in child_statuses) else 'partial_or_empty_index'
   atomic(OUT/'statuses'/(hashlib.sha256(url.encode()).hexdigest()+'.json'),status)
   return rows,status
  for entry in doc.findall('s:url',NS):
   loc=entry.findtext('s:loc',namespaces=NS)
   if not loc:continue
   loc=canonical(loc);m=ARTICLE.search(loc);wb,routes=select(loc)
   rows.append(dict(URL=loc,article_id=m[1] if m else '',sitemap_lastmod=entry.findtext('s:lastmod',default='',namespaces=NS),news_title=entry.findtext('n:news/n:title',default='',namespaces=NS),news_publication_date=entry.findtext('n:news/n:publication_date',default='',namespaces=NS),sitemap_source=url,wb_url_proxy=int(wb),metadata_selection_routes=routes,retrieved_at_utc=status['retrieved_at_utc']))
  if not rows:raise ValueError('No sitemap URL records')
  status['parsed_records']=len(rows);status['news_title_records']=sum(bool(x['news_title']) for x in rows)
  atomic(OUT/'statuses'/(hashlib.sha256(url.encode()).hexdigest()+'.json'),status)
  return rows,status
 except Exception as e:
  status.update(status='xml_parse_failure',error=repr(e));return [],status

def walk_json(obj):
 if isinstance(obj,dict):
  yield obj
  for v in obj.values():yield from walk_json(v)
 elif isinstance(obj,list):
  for v in obj:yield from walk_json(v)
def article_metadata(candidate):
 url=candidate['URL'];body,status=get(url,'selected_article')
 result=dict(candidate,metadata_status=status['status'],metadata_retrieved_at_utc=status.get('retrieved_at_utc',''),article_headline='',headline_source='',publication_date='',modified_date='',articleBody='',article_body_source='',canonical_url='',raw_file=status.get('raw_file',''))
 if status['status']!='success':return finalize_article_metadata(result)
 try:
  doc=html.fromstring(body);objects=[]
  can=doc.xpath('//link[@rel="canonical"]/@href');result['canonical_url']=can[0] if can else ''
  canonical_id=ARTICLE.search(result['canonical_url'])
  if canonical_id and candidate.get('article_id') and canonical_id[1]!=candidate['article_id']:
   result.update(metadata_status='canonical_article_id_mismatch',metadata_error='Returned article canonical ID differs from requested ID; excluded from headline recovery.')
   return finalize_article_metadata(result)
  for script in doc.xpath('//script[contains(@type,"ld+json")]/text()'):
   try:objects.extend(walk_json(json.loads(script)))
   except Exception:pass
  articles=[x for x in objects if any(v in str(x.get('@type','')) for v in ['NewsArticle','Article','ReportageNewsArticle']) and (x.get('headline') or x.get('datePublished'))]
  requested_id=candidate.get('article_id','')
  def identity_matches(a):
   identity=[a.get('url',''),a.get('@id',''),a.get('mainEntityOfPage','')]
   return any(requested_id and re.search(r'(?<!\d)'+re.escape(requested_id)+r'(?!\d)',str(x)) for x in identity)
  matching=[a for a in articles if identity_matches(a)]
  single_conflicting=False
  if len(articles)==1:
   identities=' '.join(str(articles[0].get(k,'')) for k in ['url','@id','mainEntityOfPage'])
   ids=ARTICLE.findall(identities)
   single_conflicting=bool(ids and requested_id not in ids)
  selected=matching[0] if matching else (articles[0] if len(articles)==1 and not single_conflicting else None)
  if selected:
   a=selected;result.update(article_headline=a.get('headline',''),headline_source='article_JSON-LD_headline',publication_date=a.get('datePublished',''),modified_date=a.get('dateModified',''),jsonld_identity_check='requested_article_id_matched' if matching else 'single_Article_object_no_explicit_id',jsonld_article_object_count=len(articles))
   if isinstance(a.get('articleBody'),str):result.update(articleBody=a['articleBody'],article_body_source='article_JSON-LD_articleBody')
  elif len(articles)>1:
   result.update(jsonld_identity_check='multiple_Article_objects_no_matching_ID_use_og_title_only',jsonld_article_object_count=len(articles))
  elif single_conflicting:
   result.update(jsonld_identity_check='single_Article_object_foreign_ID_use_og_title_only',jsonld_article_object_count=1)
  if not result['article_headline']:
   titles=doc.xpath('//meta[@property="og:title"]/@content')
   if titles:result.update(article_headline=titles[0],headline_source='article_og_title')
  if not result['publication_date']:
   dates=doc.xpath('//meta[@property="article:published_time"]/@content|//meta[@itemprop="datePublished"]/@content')
   if dates:result['publication_date']=dates[0]
  can=doc.xpath('//link[@rel="canonical"]/@href');result['canonical_url']=can[0] if can else ''
  if not result['articleBody']:
   nodes=doc.xpath('//*[@itemprop="articleBody"]')
   if nodes:result.update(articleBody=' '.join(' '.join(n.itertext()).strip() for n in nodes),article_body_source='HTML_itemprop_articleBody')
  if not result['article_headline']:result['metadata_status']='headline_not_found'
  return finalize_article_metadata(result)
 except Exception as e:result.update(metadata_status='parse_failure',metadata_error=repr(e));return finalize_article_metadata(result)

def write_csv(path,rows,fields):
 with gzip.open(path,'wt',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def main():
 global OUT,REQUEST_START,REQUEST_END
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true');p.add_argument('--metadata-limit',type=int);p.add_argument('--resume',action='store_true',help='Compatibility flag; successful immutable cached sources are reused by default');p.add_argument('--output',type=Path,default=OUT)
 group=p.add_mutually_exclusive_group();group.add_argument('--start',help='First discovery-partition date; default 2024-01-01');group.add_argument('--start-year',type=int,help='First discovery-partition year (January 1)')
 p.add_argument('--end',default=SOURCE_TODAY_IST.isoformat(),help='Inclusive IST discovery-partition cutoff, default source-calendar today; use 2026-10-27 for reproduction. Publication extras are retained and flagged.');args=p.parse_args()
 REQUEST_START=dt.date(args.start_year,1,1) if args.start_year is not None else dt.date.fromisoformat(args.start or '2024-01-01');REQUEST_END=dt.date.fromisoformat(args.end)
 if REQUEST_START>REQUEST_END or REQUEST_END>SOURCE_TODAY_IST:p.error('Require start <= end <= today in Asia/Kolkata')
 if args.metadata_limit is not None and args.metadata_limit<1:p.error('--metadata-limit must be positive')
 OUT=args.output;OUT.mkdir(parents=True,exist_ok=True)
 for d in ['raw','statuses']:(OUT/d).mkdir(exist_ok=True)
 atomic(OUT/'configuration.json',dict(as_of_started_at_utc=NOW,requested_start=REQUEST_START.isoformat(),collection_calendar_today_ny=AS_OF_DATE_NY,source_calendar_today_ist=SOURCE_TODAY_IST.isoformat(),requested_calendar_end_ist=REQUEST_END.isoformat(),partition_selection_warning='Month/year discovery partitions are filtered; lastmod is not publication/event date. Live feeds can include separately flagged publication extras.',save_publication_after_ist_end_as_flagged_extras=True,refresh_index_each_run=True,refresh_current_ist_month=True,refresh_today_yesterday_and_nested_news_feeds=True,older_static_cache_has_explicit_retrieved_at=True,rate_limit_request_start_interval_seconds=.56,workers=2,selection='WB URL geographic proxy and encounter/gunfight OR WB URL geographic proxy and police+shooting/death OR any national URL with weapon+taking. URL slugs are retrieval features, never treated as headlines.'))
 index='https://timesofindia.indiatimes.com/staticsitemap/toi/news/sitemap-index.xml'
 # Dynamic index and current sources must refresh on future resume runs.
 body,index_provenance=get(index,'index',refresh=True)
 if index_provenance.get('status')!='success':
  atomic(OUT/'summary.json',dict(status='index_unavailable',index_provenance=index_provenance,actual_full_historical_headline_extension=False,completed_at_utc=utcnow()))
  raise SystemExit(3 if STOP.is_set() else 2)
 doc=etree.fromstring(body);urls=[]
 for entry in doc.findall('s:sitemap',NS):
  url=entry.findtext('s:loc',namespaces=NS)
  if url:
   if partition_in_window(url,REQUEST_START,REQUEST_END):urls.append(url)
 urls+=['https://timesofindia.indiatimes.com/sitemap/today','https://timesofindia.indiatimes.com/sitemap/yesterday']
 atomic(OUT/'requested_sitemap_sources.json',dict(index_provenance=index_provenance,urls=urls))
 db=sqlite3.connect(OUT/'inventory.sqlite');db.execute('PRAGMA journal_mode=WAL');db.execute('CREATE TABLE IF NOT EXISTS inventory (url TEXT PRIMARY KEY, article_id TEXT, payload TEXT)');db.execute('DELETE FROM inventory');db.commit()
 statuses=[];feed=[];total=0
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  # executor.map bounded per163 sources; STOP prevents new network starts on denials.
  for i,(rows,status) in enumerate(pool.map(process_sitemap,urls),1):
   statuses.append(status);total+=len(rows)
   db.executemany('INSERT OR REPLACE INTO inventory VALUES (?,?,?)',[(x['URL'],x['article_id'],json.dumps(x)) for x in rows]);db.commit()
   feed.extend(x for x in rows if x['news_title'])
   if i%10==0 or status['status']!='success':print(json.dumps(dict(sitemaps_completed=i,total_sitemaps=len(urls),status=status['status'],records_so_far=total)),flush=True)
 atomic(OUT/'sitemap_manifest.json',statuses)
 inventory=(json.loads(x[0]) for x in db.execute('SELECT payload FROM inventory ORDER BY url'))
 fields=['URL','article_id','sitemap_lastmod','news_title','news_publication_date','sitemap_source','wb_url_proxy','metadata_selection_routes','retrieved_at_utc']
 write_csv(OUT/'sitemap_url_inventory.csv.gz',inventory,fields)
 for row in feed:
  row.update(publication_flags(row['news_publication_date']))
  day=publication_day_ist(row['news_publication_date'])
  # Legacy field keeps its original fixed reference meaning; generic flags
  # above describe the actual requested window on every future run.
  row['after_oct27_ist_calendar']=int(day>dt.date(2026,10,27)) if day else 'unknown'
 cutoff_fields=['requested_start_ist','requested_end_ist','publication_day_ist','within_requested_ist_window','after_requested_ist_end','before_requested_ist_start']
 write_csv(OUT/'actual_headlines_recent_news_feeds.csv.gz',feed,fields+cutoff_fields+['after_oct27_ist_calendar'])
 candidates=[json.loads(x[0]) for x in db.execute('SELECT payload FROM inventory') if json.loads(x[0])['metadata_selection_routes'] and ARTICLE.search(json.loads(x[0])['URL'])]
 # Collapse slug variants by article ID before any article requests.
 candidates=list({x['article_id']:x for x in candidates}.values());candidates.sort(key=lambda x:(x['sitemap_lastmod'],x['URL']),reverse=True)
 atomic(OUT/'selected_metadata_candidates.json',candidates)
 summary=dict(sitemaps_requested=len(urls),sitemap_successes=sum(x['status']=='success' for x in statuses),sitemap_records_before_url_dedup=total,distinct_urls=db.execute('SELECT count(*) FROM inventory').fetchone()[0],distinct_nonempty_article_ids=db.execute("SELECT count(DISTINCT article_id) FROM inventory WHERE article_id!=''").fetchone()[0],actual_news_feed_headline_rows=len(feed),actual_news_feed_distinct_article_ids=len({x['article_id'] for x in feed if x['article_id']}),selected_article_metadata_candidates=len(candidates),requested_start_ist=REQUEST_START.isoformat(),requested_end_ist=REQUEST_END.isoformat(),actual_full_historical_headline_extension=False,limitation='Static sitemap inventory provides URL and lastmod only. Real headline recovery from recent feeds and transparently selected article metadata is partial, not a complete headline corpus for the requested window.',as_of_started_at_utc=NOW,inventory_finished_at_utc=utcnow())
 atomic(OUT/'summary.json',summary);print(json.dumps(summary,indent=2),flush=True)
 if args.metadata and not STOP.is_set():
  chosen=candidates[:args.metadata_limit] if args.metadata_limit else candidates;results=[]
  with (OUT/'selected_article_metadata.jsonl').open('w') as log:
   with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    for i,result in enumerate(pool.map(article_metadata,chosen),1):
     results.append(result);log.write(json.dumps(result,ensure_ascii=False)+'\n');log.flush()
     if i%20==0 or result['metadata_status']!='success':print(json.dumps(dict(metadata_completed=i,total=len(chosen),status=result['metadata_status'],title=result['article_headline'][:120])),flush=True)
  fields+=['metadata_status','metadata_retrieved_at_utc','article_headline','headline_source','publication_date','modified_date','article_body_source','canonical_url','raw_file']+cutoff_fields+['articleBody_cleaning_applied','articleBody_cleaning_flags_json','articleBody_removed_tail_chars','articleBody_cleaner_version','articleBody_cleaning_review_needed','articleBody_cleaning_review_flags_json','body_lexical_signals_status']
  write_csv(OUT/'selected_article_actual_headlines.csv.gz',results,fields)
  summary.update(metadata_requested=len(chosen),metadata_titles_recovered=sum(bool(x['article_headline']) for x in results),metadata_bodies_recovered=sum(bool(x['articleBody']) for x in results),metadata_clean_bodies_recovered=sum(bool(x['articleBody_clean']) for x in results),metadata_bodies_with_recognized_tails_removed=sum(x['articleBody_cleaning_applied'] for x in results),metadata_status_counts=dict(__import__('collections').Counter(x['metadata_status'] for x in results)),metadata_finished_at_utc=utcnow())
  atomic(OUT/'summary.json',summary);print(json.dumps(summary,indent=2),flush=True)
 db.close()
 if STOP.is_set():raise SystemExit(3)

if __name__=='__main__':main()
