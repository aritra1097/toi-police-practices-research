"""Declare supplemental targeted retrieval before body screening.

All candidate rows remain in the catalogue, including those outside this fetch
cohort. Selection is not a random sample and cannot estimate event prevalence.
"""
from pathlib import Path
import csv,json,re,collections,hashlib
R=Path(__file__).resolve().parent
jobs={x['article_id']:x for x in json.loads((R/'queue.json').read_text())}
base_ids=set(jobs)
cloth=re.compile(r'naked|\bnude\b|semi.?clad|semi.?nude|underwear|innerwear|underclothes|undergarment|boxers?|chaddi|bare.?chest',re.I)
parade=re.compile(r'\bparad(?:ed|ing|e|es)\b',re.I)
actor=re.compile(r'police|\bcops?\b|constable|officer|accused|suspect|prisoner|convict|inmate|criminal|goon|robber|thief|thieves',re.I)
owner=re.compile(r'(?:(?:cop|police|constable|officer|guard|sentry|jawan).{0,20}(?:gun|rifle|revolver|pistol|weapon|arm)|(?:gun|rifle|revolver|pistol|weapon).{0,20}(?:cop|police|constable|officer|guard|sentry|jawan))',re.I)
strong=re.compile(r'snatch|grab|wrest|overpower|disarm|steal|stole|loot|escape|flee|fled|fired|shot',re.I)
idrx=re.compile(r'/(?:amp_)?articleshow/(\d+)\.cms')
counts=collections.Counter();missing=[];additions=[]
for x in csv.DictReader((R/'supplemental_candidates.csv').open()):
 t=x['headline'];routes=[]
 if cloth.search(t) and (parade.search(t) or x['police']=='1'):routes.append('supplement_specific_clothing_parade_or_police')
 if parade.search(t) and actor.search(t) and x['ceremonial_or_identification_hint']=='0':routes.append('supplement_literal_nonceremonial_actor_parade')
 if owner.search(t) and strong.search(t):routes.append('supplement_officer_weapon_with_taking_or_shooting')
 if not routes:continue
 counts.update(routes)
 urls=json.loads(x['all_urls_json']);ids=json.loads(x['all_article_ids_json'])
 if not ids:missing.append(dict(candidate_id=x['id'],headline=t,date=x['date'],routes=routes));continue
 for aid in ids:
  u=next((u for u in urls if (m:=idrx.search(u)) and m[1]==aid),f'https://timesofindia.indiatimes.com/articleshow/{aid}.cms')
  z=dict(article_id=aid,source_headline=t,source_date=x['date'],source_date_type=x['date_type'],url=re.sub(r'(?<!:)/{2,}','/',u).replace('http://','https://'),wb_headline_proxy=False,retrieval_routes=routes,source_provenance=x['provenance_json'])
  additions.append(z)
def all_strings(x):
 if isinstance(x,str):yield x
 elif isinstance(x,dict):
  for v in x.values():yield from all_strings(v)
 elif isinstance(x,list):
  for v in x:yield from all_strings(v)
web_files=['independent_web_leads.json','national_gun_leads.json','missing_url_resolution.json']
for file in web_files:
 p=R/file
 if not p.exists():continue
 for value in all_strings(json.loads(p.read_text())):
  for u in re.findall(r'https?://(?:timesofindia\.indiatimes\.com|m\.timesofindia\.com)/[^\s\"<>]+',value):
   m=idrx.search(u)
   if not m:continue
   aid=m[1];u=u[:m.end()]
   additions.append(dict(article_id=aid,source_headline='',source_date='',source_date_type='external_web_lead_publication_or_event_date_not_assigned',url=u,wb_headline_proxy=False,retrieval_routes=['external_source_verification_lead'],source_provenance=file))
additions.sort(key=lambda x:('clothing' not in str(x['retrieval_routes']),'external' not in str(x['retrieval_routes']),x['source_date'],x['article_id']))
for x in additions:
 aid=x['article_id']
 if aid not in jobs:jobs[aid]=x
 else:jobs[aid]['retrieval_routes']=sorted(set(jobs[aid]['retrieval_routes'])|set(x['retrieval_routes']))
# Keep new clothing reports early in the resumed queue; cached records are reused.
ordered=[jobs[x['article_id']] for x in additions if x['article_id'] not in base_ids]
unique=[];seen=set()
for x in ordered+list(jobs.values()):
 if x['article_id'] not in seen:unique.append(x);seen.add(x['article_id'])
(R/'extended_queue.json').write_text(json.dumps(unique,indent=2,ensure_ascii=False))
(R/'supplement_selected_missing_urls.json').write_text(json.dumps(missing,indent=2,ensure_ascii=False))
summary=dict(baseline_unique_ids=len(base_ids),extended_unique_ids=len(unique),additional_unique_ids=len(unique)-len(base_ids),supplement_routes=dict(counts),supplement_selected_missing_url_rows=len(missing),source_supplement_sha256=hashlib.sha256((R/'supplemental_candidates.csv').read_bytes()).hexdigest(),source_web_files_present=[x for x in web_files if (R/x).exists()],selection_interpretation='Declared purposive retrieval; all other candidate rows remain unreviewed, not negative incidents.')
(R/'extended_queue_manifest.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
