"""Small dated-link validation matrix, including calendar-derived links."""
from pathlib import Path
import csv,datetime as dt,gzip,hashlib,json,time
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from urllib.parse import urljoin
from lxml import html
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'generalized_link_checks';OUT.mkdir(exist_ok=True)
DATES=['2003-01-02','2015-01-01','2023-06-30','2024-01-01','2025-01-01','2026-07-08','2026-10-26','2026-10-27']
BASE='https://timesofindia.indiatimes.com'
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
results=[]
def get(url,label,kind,day=''):
 time.sleep(.65)
 rec=dict(label=label,kind=kind,requested_date=day,request_url=url,retrieved_at_utc=dt.datetime.now(dt.timezone.utc).isoformat())
 try:
  try:
   with urlopen(Request(url,headers={'User-Agent':UA,'Accept-Encoding':'identity'}),timeout=35) as response:
    body=response.read();status=response.status;resolved=response.url
  except HTTPError as e:body=e.read();status=e.code;resolved=e.url
  with gzip.open(OUT/f'{label}.html.gz','wb') as f:f.write(body)
  rec.update(http_status=status,response_url=resolved,response_bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
  if status in [401,403,429]:
   rec['result']='access_stop';results.append(rec);return None
  doc=html.fromstring(body)
  columns=doc.xpath('//td[translate(@align,"LEFT","left")="left" and translate(@valign,"TOP","top")="top"]')
  links=[a for c in columns for a in c.xpath('.//a[@href]') if 'articleshow/' in a.get('href','') and ' '.join(a.itertext()).strip()]
  rec.update(title=' '.join(doc.xpath('//title/text()')).strip(),archive_column_count=len(columns),archive_article_links=len(links),bold_headings=[' '.join(x.itertext()).strip() for x in doc.xpath('//b')][:8],sample_archive_headlines=[' '.join(a.itertext()).strip() for a in links[:3]])
  rec['result']='headlines_found_requires_date_check' if links else 'no_archive_headlines'
  if kind=='calendar':
   rec['calendar_day_links']=[dict(day=' '.join(a.itertext()).strip(),href=urljoin(BASE,a.get('href'))) for a in doc.xpath('//a[@href]') if 'archivelist/' in a.get('href','') and ' '.join(a.itertext()).strip()]
  results.append(rec);print(json.dumps({k:rec[k] for k in ['label','http_status','archive_article_links','result']}),flush=True)
  return doc
 except Exception as e:
  rec.update(result='error',error=f'{type(e).__name__}: {e}');results.append(rec);print(json.dumps(rec),flush=True)
 return None
for value in DATES:
 day=dt.date.fromisoformat(value);serial=(day-dt.date(1899,12,30)).days
 tail=f'archivelist/year-{day.year},month-{day.month},starttime-{serial}.cms'
 for kind,prefix in [('dated',f'/{day.year}/{day.month}/{day.day}/'),('unprefixed','/')]:
  get(BASE+prefix+tail,f'{value}-{kind}',kind,value)
  if results[-1]['result']=='access_stop':break
 if results[-1]['result']=='access_stop':break
if not any(r['result']=='access_stop' for r in results):
 for year,month in [(2003,1),(2026,10)]:get(f'{BASE}/archive/year-{year},month-{month}.cms',f'{year}-{month:02d}-calendar','calendar')
summary=dict(date_serial_rule='Days since1899-12-30; all year/month/day components and starttime changed together.',dates=DATES,requests=len(results),dated_requests=sum(x['kind']!='calendar' for x in results),dated_requests_with_archive_headlines=sum(x['kind']!='calendar' and x.get('archive_article_links',0)>0 for x in results),results=results,interpretation='HTTP200 alone does not establish a working headline listing. Sidebar/footer headlines are excluded from archive counts. No missing archive is treated as a zero-news day.')
(OUT/'results.json').write_text(json.dumps(summary,indent=2))
with (OUT/'matrix.csv').open('w',newline='') as f:
 fields=['requested_date','kind','request_url','http_status','archive_column_count','archive_article_links','result','sha256']
 w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(results)
print(json.dumps({k:v for k,v in summary.items() if k!='results'},indent=2),flush=True)
