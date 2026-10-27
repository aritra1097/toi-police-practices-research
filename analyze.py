"""Reproducible, deterministic headline retrieval; original files are read only."""
from pathlib import Path
import csv, re, unicodedata, hashlib, json, datetime, collections, random, argparse

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source',type=Path,default=Path('data/raw/Times_of_India_News_Headlines'))
SRC=parser.parse_args().source
OUT=ROOT/'data'; OUT.mkdir(parents=True,exist_ok=True)
norm=lambda s: re.sub(r'\s+',' ',re.sub(r'[^\w\s]',' ',unicodedata.normalize('NFKC',s).lower())).strip()
patterns={
 'wb_place':r'\b(?:west bengal|bengal|kolkata|calcutta|howrah|hooghly|hugli|siliguri|darjeeling|jalpaiguri|cooch behar|coochbehar|alipurduar|dinajpur|raiganj|malda|maldah|murshidabad|berhampore|nadia|krishnanagar|24 parganas|barasat|basirhat|bongaon|gaighata|baruipur|canning|barrackpore|bidhannagar|new town|newtown|asansol|durgapur|burdwan|bardhaman|birbhum|bolpur|bankura|purulia|midnapore|medinipur|jhargram|lalgarh|nandigram|singur|kharagpur|tamluk|haldia|balurghat|chopra|goalpokhar)\b',
 'encounter':r'\b(?:encounters?|gunfights?|shootouts?|crossfire)\b',
 'shoot':r'\b(?:shot|shoot\w*|gunned|firing|fire[ds]?|bullet\w*)\b',
 'death':r'\b(?:kill\w*|dead|death\w*|dies?|died|gunned)\b',
 'police':r'\b(?:police\w*|cops?|constables?|officers?|custody|custodial|stf|security forces|crpf|bsf)\b',
 'weapon':r'\b(?:guns?|pistols?|revolvers?|rifles?|firearms?|weapons?|arms|carbines?)\b',
 'snatch':r'\b(?:snatch\w*|grab\w*|wrest\w*|seiz\w*|disarm\w*|overpower\w*)\b',
 'suspect':r'\b(?:accused|suspects?|criminals?|gangsters?|undertrials?|prisoners?|convicts?|dacoits?|robbers?|rapists?|custody|custodial|escape\w*|flee\w*)\b'
}
rx={k:re.compile(v,re.I) for k,v in patterns.items()}
seen=set(); wb_seen=set(); region_seen=set(); day_seen=set(); annual=collections.defaultdict(collections.Counter); datecache={}
candidates={}; manifest=[]; hashes={}; primary_stats={}; source_days={}
files=['india-news-headlines 3.csv','links_data_with_city_and_date_years_2002_2003.csv','links_data_2005_2014.csv','links_data_2015_2023.csv','links_data_with_city_and_date.csv','links_data_with_city_and_date_years_2005_2014.csv','links_data_with_city_and_date_years_2015_2023.csv','links_data_with_city_and_date_years.csv','links_data.csv','links_data_with_city.csv']
for name in files:
 f=SRC/name
 h=hashlib.sha256()
 with f.open('rb') as s:
  for chunk in iter(lambda:s.read(2**20),b''):h.update(chunk)
 digest=h.hexdigest()
 if digest in hashes:
  manifest.append(dict(file=name,bytes=f.stat().st_size,sha256=digest,alias_of=hashes[digest]));continue
 hashes[digest]=name
 stat=collections.Counter(); dates=collections.Counter(); local=set(); cats=collections.Counter()
 with f.open(newline='',encoding='utf-8-sig') as s:
  for line,row in enumerate(csv.DictReader(s),2):
   stat['rows']+=1
   text=row.get('headline_text',row.get('Text','')).strip(); url=row.get('URL','').strip()
   category=row.get('headline_category',row.get('City','')).strip(); cats[category]+=1
   rawdate=row.get('publish_date',row.get('Date','')).strip()
   if not rawdate:stat['missing_date']+=1;continue
   try:
    if rawdate not in datecache:
     datecache[rawdate]=datetime.datetime.strptime(rawdate,'%Y%m%d' if len(rawdate)==8 and rawdate.isdigit() else '%d %b, %Y').strftime('%Y-%m-%d')
    date=datecache[rawdate]
   except ValueError:stat['invalid_date']+=1;continue
   if not text:stat['empty_headline']+=1;continue
   dates[date]+=1; year=int(date[:4]); t=norm(text)
   key=hashlib.blake2b((date+'|'+t).encode(),digest_size=16).digest()
   local.add(key)
   if key not in seen:seen.add(key);annual[year]['unique_date_headlines']+=1;stat['new_to_union']+=1
   flags={k:bool(v.search(t)) for k,v in rx.items()}
   regional=bool(re.search(r'(?:^|[./-])(?:kolkata|calcutta|siliguri|darjeeling)(?:$|[./-])',category.lower()) or re.search(r'/city/(?:kolkata|calcutta|siliguri|darjeeling)/',url.lower()))
   wb=regional or flags['wb_place']
   if regional and key not in region_seen:region_seen.add(key);annual[year]['wb_desk_proxy']+=1
   if wb and key not in wb_seen:wb_seen.add(key);annual[year]['wb_screen_proxy']+=1
   if name==files[0] and wb:primary_stats.setdefault(year,collections.Counter())['wb_raw']+=1
   if wb:
    daykey=(year,date);day_seen.add(daykey)
   # Broad recall route A: geographic proxy + encounter, any shooting, or police+death.
   route_a=wb and (flags['encounter'] or flags['shoot'] or (flags['police'] and flags['death']))
   # Route B drops geography, retrieves any weapon-taking language nationally.
   route_b=flags['snatch'] and flags['weapon']
   # Route C police + encounter nationwide catches missing/incorrect geography.
   route_c=flags['encounter'] and (flags['police'] or flags['suspect'] or flags['death'])
   if route_a or route_b or route_c:
    id=key.hex()
    if id not in candidates:
     candidates[id]=dict(id=id,date=date,headline=text,category=category,url=url,wb_proxy=int(wb),regional_proxy=int(regional),route_a=int(route_a),route_b=int(route_b),route_c=int(route_c),**{k:int(v) for k,v in flags.items()},provenance=[])
    c=candidates[id]
    if url and not c['url']:c['url']=url
    c['wb_proxy']=max(c['wb_proxy'],int(wb));c['regional_proxy']=max(c['regional_proxy'],int(regional));c['route_a']=max(c['route_a'],int(route_a))
    c['provenance'].append(f'{name}:{line}')
   if stat['rows']%100000==0: print(name,stat['rows'],flush=True)
 stat['unique_date_headlines']=len(local)
 m=dict(file=name,bytes=f.stat().st_size,sha256=digest,**stat,min_date=min(dates,default=None),max_date=max(dates,default=None),observed_days=len(dates),categories=cats.most_common(10))
 manifest.append(m);source_days[name]=dates
 print('DONE',m,flush=True)

for year in annual:
 annual[year]['wb_observed_days']=sum(y==year for y,d in day_seen)
 annual[year]['all_observed_days']=len({d for dd in source_days.values() for d in dd if d.startswith(str(year))})
rows=sorted(candidates.values(),key=lambda x:(x['date'],x['headline']))
for row in rows:row['provenance']='; '.join(row['provenance'])
def save_csv(file,rows):
 with (OUT/file).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ['id']);w.writeheader();w.writerows(rows)
save_csv('candidates.csv',rows)
save_csv('annual_coverage.csv',[dict(year=y,**annual[y]) for y in sorted(annual)])
save_csv('daily_source_coverage.csv',[dict(file=f,date=d,raw_rows=n) for f,days in source_days.items() for d,n in sorted(days.items())])
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
(OUT/'retrieval_patterns.json').write_text(json.dumps(patterns,indent=2))
summary=dict(unique_date_headlines=len(seen),wb_screen_proxy=len(wb_seen),wb_desk_proxy=len(region_seen),candidate_count=len(rows),route_a=sum(r['route_a'] for r in rows),route_b=sum(r['route_b'] for r in rows),route_c=sum(r['route_c'] for r in rows))
(OUT/'summary.json').write_text(json.dumps(summary,indent=2));print(summary,flush=True)
