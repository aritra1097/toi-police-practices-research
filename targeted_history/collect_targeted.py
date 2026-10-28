"""Recover a declared targeted historical article cohort; never an event census.

Raw responses and full text remain local. All queue rules precede body screening.
"""
from pathlib import Path
import argparse,csv,datetime as dt,gzip,hashlib,json,re,threading,time,concurrent.futures
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from urllib.parse import urljoin
from lxml import html
R=Path(__file__).resolve().parent;BASE=R.parent
OUT=R/'collection';OUT.mkdir(exist_ok=True)
for d in ['raw','records']:(OUT/d).mkdir(exist_ok=True)
LOCK=threading.Lock();NEXT=0.;STOP=threading.Event()
UA='TOIArchiveResearch/1.0 (targeted public historical news research; low request rate)'
ID=re.compile(r'/(?:amp_)?articleshow/(\d+)\.cms')
RELATED=re.compile(r'We\s+also\s+published\s+(?:the\s+)?following\s+articles\s+recently',re.I)
GUN=re.compile(r'\b(?:guns?|rifles?|pistols?|revolvers?|firearms?|carbines?|weapons?|arms)\b',re.I)
TAKE=re.compile(r'\b(?:snatch\w*|grab\w*|wrest\w*|disarm\w*|overpower\w*|seiz\w*|steal\w*|stole\w*|loot\w*|tak\w*|took|taken)\b',re.I)
POLICE=re.compile(r'\b(?:police\w*|cops?|constables?|officers?|custody|custodial|bsf|cisf|crpf|stf|homeguards?)\b',re.I)
PARADE=re.compile(r'\b(?:parad\w*|strip\w*|naked|nude|semi.?clad|semi.?nude|underwear|underclothes|undergarments?|boxers?|innerwear)\b',re.I)
RECON=re.compile(r'reconstruct|re.enact|recreat|spot verification',re.I)
def now():return dt.datetime.now(dt.timezone.utc).isoformat()
def save(path,x):
 if path.parent.name=='records' and path.exists():
  old=path.read_bytes();history=OUT/'record_history';history.mkdir(exist_ok=True)
  backup=history/f'{path.stem}.{hashlib.sha256(old).hexdigest()[:16]}.json'
  if not backup.exists():backup.write_bytes(old)
 t=path.with_suffix('.tmp');t.write_text(json.dumps(x,ensure_ascii=False,indent=2));t.replace(path)
def fetch(url):
 global NEXT
 with LOCK:
  delay=max(0,NEXT-time.monotonic())
  if delay:time.sleep(delay)
  NEXT=time.monotonic()+.56
 try:
  with urlopen(Request(url,headers={'User-Agent':UA,'Accept-Encoding':'identity'}),timeout=30) as h:return h.status,h.read(),h.url
 except HTTPError as e:return e.code,e.read(),e.url
def clean(s):
 s=str(s or '')
 if '<' in s:
  try:s=html.fromstring('<div>'+s+'</div>').text_content()
  except Exception:pass
 return re.sub(r'[ \t]+',' ',s).strip()
def json_story(x):
 s=x.get('story',[])
 if isinstance(s,str):return clean(s)
 if not isinstance(s,list):return ''
 parts=[]
 for z in s:
  if isinstance(z,dict):
   if z.get('tn')=='text' and isinstance(z.get('value'),str):parts.append(z['value'])
   elif z.get('tn') in ['br','p']:parts.append('\n')
 return clean(''.join(parts))
def usable_body(value):
 return bool(value) and not re.match(r'^\s*ERR[-_ ]?RTF',value,re.I) and not re.fullmatch(r'\s*(?:undefined|null|error)\s*',value,re.I)
def ld_nodes(x):
 if isinstance(x,dict):
  yield x
  for v in x.values():
   if isinstance(v,(dict,list)):yield from ld_nodes(v)
 elif isinstance(x,list):
  for v in x:yield from ld_nodes(v)
def decorate(r):
 body=r.get('article_body_raw','');m=RELATED.search(body)
 r['analysis_body']=(body[:m.start()].rstrip() if m else body) if usable_body(body) else ''
 r['recommendation_tail_removed']=bool(m)
 r['body_characters']=len(r['analysis_body'])
 r['body_quality_flags']=(['source_error_marker'] if not usable_body(r['analysis_body']) else [])+(['short_body_under_120_characters'] if len(r['analysis_body'])<120 else [])
 r['body_contexts']=[]
 for hit in TAKE.finditer(r['analysis_body']):
  text=r['analysis_body'][max(0,hit.start()-260):hit.end()+340]
  if GUN.search(text) and POLICE.search(text):
   r['body_contexts'].append(dict(offset=hit.start(),text=text))
 r['body_weapon_taking_signal']=bool(r['body_contexts'])
 r['body_parade_signal']=bool(PARADE.search(r['analysis_body']))
 r['body_reconstruction_signal']=bool(RECON.search(r['analysis_body']))
 try:
  d=dt.datetime.fromisoformat(str(r.get('publication_date','')).replace('Z','+00:00'))
  r['publication_date_timezone_aware']=d.tzinfo is not None
 except ValueError:r['publication_date_timezone_aware']=False
 r['manual_source_context_review']='required; lexical signals are not event labels'
 return r
def collect(job):
 aid=job['article_id'];dest=OUT/'records'/f'{aid}.json'
 if dest.exists():
  old=json.loads(dest.read_text())
  validated_html=old.get('extraction_source')!='article_html_jsonld' or bool(old.get('html_object_identity_validation'))
  if old.get('metadata_status')=='success' and usable_body(old.get('article_body_raw','')) and validated_html:
   routes=sorted(set(old.get('retrieval_routes',[]))|set(job.get('retrieval_routes',[])))
   if routes!=old.get('retrieval_routes'):
    old['retrieval_routes']=routes
    old.setdefault('additional_queue_provenance',[]).append(job.get('source_provenance',''))
    save(dest,old)
   return decorate(old)
 r=dict(job,retrieved_at_utc=now(),metadata_status='pending',attempts=[])
 if STOP.is_set():r['metadata_status']='not_requested_after_access_stop';return r
 u=f'https://toifeeds.indiatimes.com/treact/feeds/toi/web/show/news?path=/articleshow/{aid}.cms'
 try:
  status,b,resolved=fetch(u)
  with gzip.open(OUT/'raw'/f'{aid}.{hashlib.sha256(b).hexdigest()[:16]}.feed.json.gz','wb') as f:f.write(b)
  r['attempts'].append(dict(url=u,http_status=status,response_url=resolved,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b)))
  if status in [401,403,429]:STOP.set();r['metadata_status']='access_stop';save(dest,r);return r
  if status==200:
   x=json.loads(b);r['returned_article_id']=str(x.get('id',''));r['response_id_matches_request']=r['returned_article_id']==aid
   if r['response_id_matches_request']:
    r.update(article_headline=clean(x.get('hl','')),article_body_raw=json_story(x),publication_date=x.get('seo',{}).get('datePublished',''),modified_date=x.get('seo',{}).get('dateModified',''),extraction_source='first_party_article_json_story_text_nodes')
    if r['article_headline'] and usable_body(r['article_body_raw']):r['metadata_status']='success'
 except Exception as e:r['feed_error']=f'{type(e).__name__}: {e}'
 if r['metadata_status']!='success' and not STOP.is_set():
  try:
   status,b,resolved=fetch(job['url'])
   with gzip.open(OUT/'raw'/f'{aid}.{hashlib.sha256(b).hexdigest()[:16]}.article.html.gz','wb') as f:f.write(b)
   r['attempts'].append(dict(url=job['url'],http_status=status,response_url=resolved,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b)))
   if status in [401,403,429]:STOP.set();r['metadata_status']='access_stop'
   elif status==200:
    doc=html.fromstring(b);nodes=[]
    for s in doc.xpath('//script[@type="application/ld+json"]/text()'):
     try:nodes.extend(ld_nodes(json.loads(s)))
     except (ValueError,TypeError):pass
    articles=[z for z in nodes if 'NewsArticle' in str(z.get('@type','')) and z.get('headline')]
    if articles:
     canonical=doc.xpath('//link[@rel="canonical"]/@href')
     identity=ID.search(canonical[0] if canonical else resolved)
     matching=[]
     for candidate in articles:
      references=[candidate.get('url',''),candidate.get('@id',''),candidate.get('mainEntityOfPage','')]
      article_ids=set(ID.findall(json.dumps(references)))
      if aid in article_ids:matching.append(candidate)
     unambiguous_single=len(articles)==1 and not any(ID.search(json.dumps(articles[0].get(k,''))) for k in ['url','@id','mainEntityOfPage'])
     z=matching[0] if len(matching)==1 else (articles[0] if unambiguous_single else None)
     r['html_newsarticle_object_count']=len(articles)
     if identity and identity[1]==aid and z is not None:
      r.update(article_headline=clean(z.get('headline')),article_body_raw=clean(z.get('articleBody')),publication_date=z.get('datePublished',''),modified_date=z.get('dateModified',''),response_id_matches_request=True,returned_article_id=aid,extraction_source='article_html_jsonld')
      r['html_object_identity_validation']='matched_unique_article_object_id' if len(matching)==1 else 'single_article_object_without_id_on_matching_canonical_page'
      if r['article_headline'] and usable_body(r['article_body_raw']):r['metadata_status']='success'
   if r['metadata_status']=='pending':r['metadata_status']='unresolved_body_or_identity'
  except Exception as e:r.update(html_error=f'{type(e).__name__}: {e}',metadata_status='network_or_parse_error')
 if r['metadata_status']=='pending':r['metadata_status']='unresolved_body_or_identity'
 r=decorate(r);save(dest,r);return r
def queue():
 candidates=list(csv.DictReader((BASE/'data/candidates.csv').open()))
 selected=[]
 for x in candidates:
  wb=x['wb_proxy']=='1';p=x['police']=='1';s=x['suspect']=='1';routes=[]
  if wb and x['encounter']=='1':routes.append('WB_any_encounter')
  if wb and p and x['shoot']=='1':routes.append('WB_police_shooting')
  if wb and p and s and x['death']=='1':routes.append('WB_police_suspect_death')
  if wb and x['route_b']=='1':routes.append('WB_weapon_taking')
  if x['route_b']=='1' and (p or s):routes.append('national_weapon_taking_police_or_suspect')
  if routes:selected.append(dict(source_headline=x['headline'],source_date=x['date'],source_date_type='source_dataset_or_archive_listing_date_not_verified_event_date',url=x['url'],wb_headline_proxy=wb,retrieval_routes=routes,source_provenance=x['provenance']))
 supplemental=R/'supplemental_candidates.csv'
 if supplemental.exists():
  for x in csv.DictReader(supplemental.open()):
   # Supplemental fetch selection is explicitly recorded after inspecting
   # its schema; --supplement file is added separately once scan completes.
   pass
 jobs={};missing=[]
 for x in selected:
  m=ID.search(x['url'])
  if not m:missing.append(x);continue
  aid=m[1];x['article_id']=aid;x['url']=re.sub(r'(?<!:)/{2,}','/',x['url']).replace('http://','https://')
  if aid not in jobs:jobs[aid]=x
  else:
   jobs[aid]['retrieval_routes']=sorted(set(jobs[aid]['retrieval_routes'])|set(x['retrieval_routes']))
 save(R/'queue.json',list(jobs.values()));save(R/'missing_url_candidates.json',missing)
 return list(jobs.values())
def outputs(records):
 with (OUT/'articles_private.jsonl').open('w') as f:
  for r in records:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 fields=['article_id','source_date','source_date_type','source_headline','article_headline','url','publication_date','modified_date','metadata_status','response_id_matches_request','publication_date_timezone_aware','extraction_source','body_characters','body_weapon_taking_signal','body_parade_signal','body_reconstruction_signal','retrieval_routes','retrieved_at_utc']
 with (R/'retrieved_headlines.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(records)
 from collections import Counter
 summary=dict(records=len(records),statuses=dict(Counter(r['metadata_status'] for r in records)),body_weapon_taking_signals=sum(r.get('body_weapon_taking_signal',False) for r in records),body_parade_signals=sum(r.get('body_parade_signal',False) for r in records),body_reconstruction_signals=sum(r.get('body_reconstruction_signal',False) for r in records),selection='Declared targeted historical cohort; not complete news or incidence coverage',finished_at_utc=now())
 save(R/'collection_summary.json',summary);print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--queue-only',action='store_true');p.add_argument('--input',type=Path);p.add_argument('--workers',type=int,default=2);args=p.parse_args()
 jobs=json.loads(args.input.read_text()) if args.input else queue()
 print(json.dumps(dict(queued_unique_ids=len(jobs),queue_only=args.queue_only)),flush=True)
 if not args.queue_only:
  records=[]
  with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
   for i,r in enumerate(pool.map(collect,jobs),1):
    records.append(r)
    if i%25==0:print(json.dumps(dict(completed=i,total=len(jobs),latest_status=r['metadata_status'])),flush=True)
  outputs(records)
