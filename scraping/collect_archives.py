"""Resumable low-rate collector of public TOI archive listings.

Archive dates are discovery dates, never assumed article publication/event dates.
No authentication, cookies, proxy rotation, challenge solving, or access bypass.
"""
from __future__ import annotations
import argparse, concurrent.futures, csv, datetime as dt, gzip, hashlib, io, json
import os, re, threading, time
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
from lxml import html

ROOT=Path(__file__).resolve().parent
TODAY=dt.datetime.now(ZoneInfo('Asia/Kolkata')).date()
PILOT_DATES=(dt.date(2024,1,1),dt.date(2026,7,8),dt.date(2026,10,27))
UA='TOIArchiveResearch/1.0 (public news archive research; low request rate)'
FIELDS=['Text','URL','City','Date','archive_date','article_id','publication_date','event_date','retrieved_at_utc','source_archive_url','current_day_partial','headline_variants_json']
ARTICLE=re.compile(r'/(?:amp_)?articleshow/(\d+)\.cms(?:$|[?#])',re.I)
DATE_RX=re.compile(r'(?<!\d)(\d{1,2})\s+(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?),?\s+(\d{4})(?!\d)',re.I)
LOCK=threading.Lock(); RATE_LOCK=threading.Lock(); NEXT_START=0.0; STOP=threading.Event()

def utcnow():return dt.datetime.now(dt.timezone.utc).isoformat()
def archive_url(day):
 serial=(day-dt.date(1899,12,30)).days
 return f'https://timesofindia.indiatimes.com/{day.year}/{day.month}/{day.day}/archivelist/year-{day.year},month-{day.month},starttime-{serial}.cms'

def atomic_json(path,obj):
 path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(obj,indent=2));os.replace(tmp,path)

def throttle():
 global NEXT_START
 with RATE_LOCK:
  delay=max(0,NEXT_START-time.monotonic())
  if delay:time.sleep(delay)
  NEXT_START=time.monotonic()+0.56  # Shared ceiling below two request starts/s.

def parse_archive(body,day,source,retrieved):
 doc=html.fromstring(body)
 title=' '.join(doc.xpath('//title/text()')).strip()
 headings=[' '.join(x.itertext()).strip() for x in doc.xpath('//b|//h1|//h2')]
 heading_dates=[]
 for text in headings:
  for m in DATE_RX.finditer(text):
   try:heading_dates.append(dt.datetime.strptime(f'{m[1]} {m[2][:3]} {m[3]}','%d %b %Y').date().isoformat())
   except ValueError:pass
 # The historical scraper used the first bold archive-date heading.
 if day.isoformat() not in heading_dates:
  return [],dict(validation='archive_day_heading_missing' if not heading_dates else 'date_mismatch',title=title,archive_heading_dates=heading_dates,headings=headings[:12])
 tds=doc.xpath('//td[translate(@align,"LEFT","left")="left" and translate(@valign,"TOP","top")="top"]')
 if not tds:
  return [],dict(validation='archive_structure_missing',title=title,archive_heading_dates=heading_dates,headings=headings[:12])
 records={}; raw_links=0; ignored_links=0
 for td in tds:
  for a in td.xpath('.//a[@href]'):
   href=a.get('href','').strip();text=' '.join(' '.join(a.itertext()).split())
   if not text:continue
   absolute=urljoin('https://timesofindia.indiatimes.com/',href)
   u=urlsplit(absolute);m=ARTICLE.search(u.path)
   if u.hostname not in {'timesofindia.indiatimes.com','m.timesofindia.com'} or not m:
    ignored_links+=1;continue
   raw_links+=1;aid=m[1]
   cleanpath=re.sub(r'/+','/',u.path).replace('/amp_articleshow/','/articleshow/')
   canonical=urlunsplit(('https','timesofindia.indiatimes.com',cleanpath,'',''))
   citymatch=re.search(r'/city/([^/]+)/',cleanpath)
   if aid not in records:
    records[aid]=dict(Text=text,URL=canonical,City=citymatch[1] if citymatch else '',Date=f'{day.day} {day.strftime("%b")}, {day.year}',archive_date=day.isoformat(),article_id=aid,publication_date='',event_date='',retrieved_at_utc=retrieved,source_archive_url=source,current_day_partial=int(day==TODAY),headline_variants_json=[])
   if text not in records[aid]['headline_variants_json']:records[aid]['headline_variants_json'].append(text)
 for row in records.values():row['headline_variants_json']=json.dumps(row['headline_variants_json'],ensure_ascii=False)
 validation='success' if records else 'empty_archive'
 return list(records.values()),dict(validation=validation,title=title,archive_heading_dates=heading_dates,headings=headings[:12],raw_article_links=raw_links,ignored_nonarticle_links=ignored_links,unique_articles=len(records))

def log_attempt(root,record):
 with LOCK:
  with (root/'attempts.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')
  atomic_json(root/'status'/f'{record["archive_date"]}.json',record)
  if record['status']!='success':
   with (root/'failures.jsonl').open('a') as f:f.write(json.dumps(record)+'\n')

def collect_day(day,root,max_attempts=3):
 date=day.isoformat();statusfile=root/'status'/f'{date}.json'
 if statusfile.exists():
  old=json.loads(statusfile.read_text())
  if day<TODAY-dt.timedelta(days=1) and old.get('status')=='success' and not old.get('current_day_partial') and (root/'days'/f'{date}.csv.gz').exists():return old
 source=archive_url(day)
 for attempt in range(1,max_attempts+1):
  if STOP.is_set():return dict(archive_date=date,status='not_requested_after_access_stop')
  throttle();retrieved=utcnow();status=None;body=b'';response_url=source;headers={}
  record=dict(archive_date=date,archive_url=source,retrieved_at_utc=retrieved,attempt=attempt,current_day_partial=day==TODAY)
  try:
   request=Request(source,headers={'User-Agent':UA,'Accept':'text/html,application/xhtml+xml','Accept-Encoding':'identity'})
   try:
    with urlopen(request,timeout=45) as response:
     status=response.status;body=response.read();response_url=response.url;headers=dict(response.headers)
   except HTTPError as e:
    status=e.code;body=e.read();headers=dict(e.headers);response_url=e.url
   record.update(http_status=status,response_url=response_url,response_bytes=len(body),html_sha256=hashlib.sha256(body).hexdigest(),response_content_type=headers.get('Content-Type',''))
   stamp=re.sub(r'[^0-9]','',retrieved)
   rawfile=root/'raw'/f'{date}.{stamp}.attempt-{attempt}.html.gz'
   with gzip.open(rawfile,'wb',compresslevel=6) as f:f.write(body)
   record['raw_html_file']=str(rawfile.relative_to(root))
   if status in {401,403,429}:
    record.update(status='access_stop',error=f'HTTP {status}; halted without access bypass',retry_after=headers.get('Retry-After',''))
    STOP.set();log_attempt(root,record);return record
   if status!=200:
    record.update(status='http_error',error=f'HTTP {status}')
   else:
    textprefix=body[:50000].decode('utf-8','replace').lower()
    challenge=any(x in textprefix for x in ['captcha','verify you are human','access denied','request rejected'])
    if challenge:
     record.update(status='access_stop',error='Challenge/access-denial content; halted without bypass');STOP.set();log_attempt(root,record);return record
    rows,validation=parse_archive(body,day,source,retrieved);record.update(validation)
    record['status']=validation['validation']
    if record['status']=='success':
     dayfile=root/'days'/f'{date}.csv.gz';tmp=dayfile.with_suffix('.tmp')
     with gzip.open(tmp,'wt',newline='',encoding='utf-8') as f:
      writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
     os.replace(tmp,dayfile);record['data_file']=str(dayfile.relative_to(root));log_attempt(root,record);return record
  except (URLError,TimeoutError,OSError,ValueError) as e:
   record.update(status='network_or_parse_error',error=f'{type(e).__name__}: {e}')
  except Exception as e:
   record.update(status='parse_error',error=f'{type(e).__name__}: {e}')
  log_attempt(root,record)
  if attempt<max_attempts:time.sleep(2**attempt)
 return record

def combine(root,days):
 label=f'{min(days).isoformat()}_to_{max(days).isoformat()}'
 combined=root/f'toi_archive_{label}.csv.gz';count=0;distinct={};dates=[]
 with gzip.open(combined,'wt',newline='',encoding='utf-8') as f:
  writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader()
  for day in days:
   path=root/'days'/f'{day.isoformat()}.csv.gz'
   if not path.exists():continue
   dates.append(day.isoformat())
   with gzip.open(path,'rt',newline='',encoding='utf-8') as r:
    for row in csv.DictReader(r):
     writer.writerow(row);count+=1;aid=row['article_id']
     if aid not in distinct:
      distinct[aid]=dict(Text=row['Text'],URL=row['URL'],City=row['City'],article_id=aid,publication_date='',event_date='',first_archive_date=row['archive_date'],last_archive_date=row['archive_date'],archive_listing_occurrences=0)
     distinct[aid]['last_archive_date']=row['archive_date'];distinct[aid]['archive_listing_occurrences']+=1
 unique=root/f'toi_unique_article_ids_{label}.csv.gz'
 with gzip.open(unique,'wt',newline='',encoding='utf-8') as f:
  fields=['Text','URL','City','article_id','publication_date','event_date','first_archive_date','last_archive_date','archive_listing_occurrences']
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(distinct.values())
 requested={d.isoformat() for d in days}
 statuses=[json.loads(p.read_text()) for p in sorted((root/'status').glob('*.json')) if p.stem in requested]
 summary=dict(requested_start=min(days).isoformat(),requested_end=max(days).isoformat(),requested_days=len(days),successful_days=len(dates),archive_article_rows=count,distinct_article_ids=len(distinct),earliest_success=min(dates,default=None),latest_success=max(dates,default=None),current_day_partial=TODAY in days,status_counts=dict(__import__('collections').Counter(x['status'] for x in statuses)),combined_csv=str(combined),article_id_deduplicated_csv=str(unique),completed_at_utc=utcnow(),date_warning='Archive date is listing/discovery date. Publication and event dates remain unknown until independently read from articles.')
 atomic_json(root/'summary.json',summary)
 with (root/'manifest.csv').open('w',newline='') as f:
  fields=['archive_date','status','http_status','unique_articles','raw_article_links','html_sha256','retrieved_at_utc','current_day_partial','error','raw_html_file','data_file']
  writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(statuses)
 return summary

def diagnose(root):
 urls=['https://timesofindia.indiatimes.com/robots.txt','https://timesofindia.indiatimes.com/archive/year-2024,month-1.cms',archive_url(dt.date(2015,1,1)),'https://timesofindia.indiatimes.com/staticsitemap/toi/news/sitemap-index.xml']
 results=[]
 for i,url in enumerate(urls):
  throttle();retrieved=utcnow();result=dict(url=url,retrieved_at_utc=retrieved)
  try:
   try:
    with urlopen(Request(url,headers={'User-Agent':UA,'Accept-Encoding':'identity'}),timeout=45) as response:status=response.status;body=response.read()
   except HTTPError as e:status=e.code;body=e.read()
   path=root/f'diagnostic-{i}-{re.sub(r"[^0-9]","",retrieved)}.gz'
   with gzip.open(path,'wb') as f:f.write(body)
   result.update(http_status=status,response_bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),raw_file=str(path))
   if url.endswith('robots.txt'):result['text']=body.decode('utf-8','replace')
   elif status==200:
    doc=html.fromstring(body);result.update(title=doc.xpath('//title/text()'),headings=[' '.join(x.itertext()).strip() for x in doc.xpath('//b|//h1|//h2')][:12],links=[dict(text=' '.join(a.itertext())[:200],href=a.get('href')) for a in doc.xpath('//a[@href]') if any(k in a.get('href','') for k in ['archivelist','sitemap'])][:40],xml_locations=re.findall(r'<loc>(.*?)</loc>',body.decode('utf-8','replace'))[:40])
   results.append(result);print(json.dumps(result),flush=True)
   if status in {401,403,429}:break
  except Exception as e:result['error']=f'{type(e).__name__}: {e}';results.append(result);print(json.dumps(result),flush=True)
 atomic_json(root/'diagnostics.json',results)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pilot',action='store_true',help='Fixed historical parser test dates: 2024-01-01, 2026-07-08, 2026-10-27, clipped to requested range; not a current-coverage run');p.add_argument('--diagnose',action='store_true');p.add_argument('--output',default=str(ROOT/'output'));p.add_argument('--workers',type=int,default=2)
 group=p.add_mutually_exclusive_group();group.add_argument('--start',help='First requested archive date, default 2024-01-01');group.add_argument('--start-year',type=int,help='First requested calendar year (January 1)')
 p.add_argument('--end',default=TODAY.isoformat(),help='Last requested date, inclusive; defaults to source-calendar today in Asia/Kolkata. Use 2026-10-27 to reproduce the original cutoff.');args=p.parse_args()
 root=Path(args.output);root.mkdir(parents=True,exist_ok=True)
 if args.diagnose:diagnose(root);return
 for sub in ['raw','days','status']:(root/sub).mkdir(exist_ok=True)
 start=dt.date(args.start_year,1,1) if args.start_year is not None else dt.date.fromisoformat(args.start or '2024-01-01');end=dt.date.fromisoformat(args.end)
 if start>end or end>TODAY:p.error('Require start <= end <= today in Asia/Kolkata')
 days=[day for day in PILOT_DATES if start<=day<=end] if args.pilot else [start+dt.timedelta(days=i) for i in range((end-start).days+1)]
 if not days:p.error('The requested range contains none of the fixed pilot dates')
 if not 1<=args.workers<=2:raise ValueError('workers must be 1 or 2')
 atomic_json(root/'run_configuration.json',dict(start=start.isoformat(),end=end.isoformat(),source_calendar='Asia/Kolkata',source_today_ist=TODAY.isoformat(),pilot=args.pilot,pilot_fixed_dates=[d.isoformat() for d in PILOT_DATES] if args.pilot else [],requested_days=len(days),workers=args.workers,shared_minimum_request_interval_seconds=0.56,user_agent=UA,run_started_utc=utcnow(),method='Public daily archives only; stops on 401/403/429 or challenge, three attempts for transient/empty/mismatch failures; resumes older complete daily files; refreshes today, yesterday and previously partial days.'))
 completed=0
 # Keep at most two tasks in flight so an access stop does not leave a queued backlog.
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
  remaining=iter(days);futures={}
  for _ in range(args.workers):
   day=next(remaining,None)
   if day:futures[pool.submit(collect_day,day,root)]=day
  while futures:
   ready,_=concurrent.futures.wait(futures,return_when=concurrent.futures.FIRST_COMPLETED)
   for future in ready:
    day=futures.pop(future);result=future.result();completed+=1
    if args.pilot or completed%20==0 or result['status']!='success':print(json.dumps(dict(completed=completed,total=len(days),date=day.isoformat(),status=result['status'],articles=result.get('unique_articles'),error=result.get('error'))),flush=True)
    if not STOP.is_set():
     nxt=next(remaining,None)
     if nxt:futures[pool.submit(collect_day,nxt,root)]=nxt
 print(json.dumps(combine(root,days),indent=2),flush=True)
 if STOP.is_set():raise SystemExit(3)

if __name__=='__main__':main()
