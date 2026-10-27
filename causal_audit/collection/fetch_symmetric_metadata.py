"""Recover every symmetrically selected four-state report, reusing cached IDs.

Outputs are a selected article review cohort, not an incident census. Full article
bodies and raw HTML stay local for research and should not be publicly packaged.
"""
import argparse,concurrent.futures,csv,datetime,gzip,json,re,sys,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent
WORK=ROOT.parents[1]
sys.path.insert(0,str(WORK/'scraping'))
import collect_sitemaps as c
OUT=ROOT/'output';OUT.mkdir(exist_ok=True)
for d in ['raw','statuses']:(OUT/d).mkdir(exist_ok=True)
c.OUT=OUT
CACHE=WORK/'scraping/sitemap_output/selected_article_metadata.jsonl'
TAKE=re.compile(r'\b(?:snatch\w*|grab\w*|wrest\w*|disarm\w*|overpower\w*)\b',re.I)
WEAPON=re.compile(r'\b(?:guns?|pistols?|revolvers?|rifles?|firearms?|weapons?|arms|carbines?)\b',re.I)
PARADE=re.compile(r'\b(?:parade[ds]?|parading|strip(?:ped|ping|s)?|naked|underwear|undergarments?|boxers?|chaddi)\b',re.I)
POLICE=re.compile(r'\b(?:police\w*|cops?|constables?|officers?|custody|custodial|stf|bsf|crpf|cisf)\b',re.I)
RELATED_TAIL=re.compile(r'We\s+also\s+published\s+(?:the\s+)?following\s+articles\s+recently',re.I)

def decorate(result):
 raw=result.get('articleBody','');marker=RELATED_TAIL.search(raw)
 body=raw[:marker.start()].rstrip() if marker else raw
 result['analysis_body']=body
 result['analysis_body_cleaning']='explicit_vendor_related_articles_tail_removed' if marker else 'none'
 result['analysis_body_truncation_marker']=marker.group() if marker else ''
 result['raw_article_body_characters']=len(raw);result['analysis_body_characters']=len(body)
 # Do not truncate at generic 'You Can Also Check' or 'Also read': substantive
 # reporting sometimes resumes after those inline inserts.
 contexts=[]
 for m in TAKE.finditer(body):
  text=body[max(0,m.start()-240):m.end()+300]
  if WEAPON.search(text):contexts.append(text)
 result['body_weapon_taking_contexts']=contexts[:3]
 result['body_weapon_taking_context_flag']=int(bool(contexts))
 result['body_parade_or_stripping_flag']=int(bool(PARADE.search(body)))
 result['body_police_flag']=int(bool(POLICE.search(body)))
 result['manual_event_geography_and_outcome_review']='required; flags are retrieval aids, not event labels'
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--confirm-count-over-2000',action='store_true');args=p.parse_args()
 candidates=json.loads((ROOT/'symmetric_candidates.json').read_text());counts=json.loads((ROOT/'candidate_counts.json').read_text())
 if counts['new_http_requests_required']>2000 and not args.confirm_count_over_2000:raise SystemExit('More than2000newrequests: reportcounts andobtain scope decision before running.')
 cache={}
 for line in CACHE.read_text().splitlines():
  if line.strip():
   r=json.loads(line);cache[r['article_id']]=r
 configuration=dict(started_at_utc=c.utcnow(),source_candidate_counts=counts,all_selected_reports_requested=True,selection_frame='Saved public2024-26 static-sitemap URL inventory and late-day newsfeed URLs; identical language rules for WB/Kerala/TamilNadu/Telangana',state_assignment='provisional geographic phrase/desk proxies until body review',cached_existing_article_ids_used=True,maximum_workers=2,shared_minimum_request_start_interval_seconds=.56,full_state_news_or_event_coverage=False)
 c.atomic(OUT/'configuration.json',configuration)
 results=[];fresh=[]
 keys=['article_headline','headline_source','publication_date','modified_date','articleBody','article_body_source','canonical_url','raw_file','metadata_status','metadata_retrieved_at_utc','jsonld_identity_check','jsonld_article_object_count']
 with (OUT/'article_review_cohort_private.jsonl').open('w') as log:
  for candidate in candidates:
   if candidate['article_id'] in cache:
    old=cache[candidate['article_id']];r=dict(candidate,**{k:old.get(k,'') for k in keys},metadata_reused_from_original_362=True,cached_requested_URL=old['URL'])
    r=decorate(r);results.append(r);log.write(json.dumps(r,ensure_ascii=False)+'\n')
   else:fresh.append(candidate)
  log.flush();print(json.dumps(dict(cached_records_written=len(results),new_metadata_requests=len(fresh))),flush=True)
  def fetch(candidate):
   request=dict(candidate,metadata_selection_routes=';'.join(candidate['routes']),wb_url_proxy=int('West Bengal' in candidate['state_candidates']))
   r=c.article_metadata(request);r['metadata_reused_from_original_362']=False
   return decorate(r)
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
   for i,r in enumerate(pool.map(fetch,fresh),1):
    results.append(r);log.write(json.dumps(r,ensure_ascii=False)+'\n');log.flush()
    if i%25==0 or r['metadata_status']!='success':print(json.dumps(dict(new_completed=i,new_total=len(fresh),all_completed=len(results),status=r['metadata_status'],states=r['state_candidates'],title=r['article_headline'][:120])),flush=True)
 fields=['article_id','URL','state_candidates','routes','geography_evidence','source_sitemap_lastmod','source_sitemap','source_inventory_retrieved_at_utc','article_headline','headline_source','publication_date','modified_date','metadata_status','metadata_retrieved_at_utc','metadata_reused_from_original_362','canonical_url','jsonld_identity_check','jsonld_article_object_count','article_body_source','body_weapon_taking_context_flag','body_parade_or_stripping_flag','body_police_flag','analysis_body_cleaning','analysis_body_truncation_marker','raw_article_body_characters','analysis_body_characters','manual_event_geography_and_outcome_review','raw_file']
 with gzip.open(OUT/'symmetric_article_metadata.csv.gz','wt',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
  for r in results:
   x=dict(r)
   for k in ['state_candidates','routes','geography_evidence']:x[k]=json.dumps(x[k],ensure_ascii=False)
   w.writerow(x)
 summary=dict(candidate_counts=counts,total_selected_article_ids=len(candidates),processed_records=len(results),cached_records=sum(bool(x['metadata_reused_from_original_362']) for x in results),new_http_article_records=len(fresh),metadata_status_counts=dict(collections.Counter(x['metadata_status'] for x in results)),headlines_recovered=sum(bool(x['article_headline']) for x in results),publication_dates_recovered=sum(bool(x['publication_date']) for x in results),bodies_recovered=sum(bool(x['articleBody']) for x in results),weapon_taking_context_candidate_articles=sum(x['body_weapon_taking_context_flag'] for x in results),parade_context_candidate_articles=sum(x['body_parade_or_stripping_flag'] for x in results),state_counts={state:dict(selected_articles=sum(state in x['state_candidates'] for x in results),headlines_recovered=sum(state in x['state_candidates'] and bool(x['article_headline']) for x in results),bodies_recovered=sum(state in x['state_candidates'] and bool(x['articleBody']) for x in results),body_weapon_taking_context_candidates=sum(state in x['state_candidates'] and x['body_weapon_taking_context_flag'] for x in results),body_parade_context_candidates=sum(state in x['state_candidates'] and x['body_parade_or_stripping_flag'] for x in results)) for state in ['West Bengal','Kerala','Tamil Nadu','Telangana']},full_state_incidence_census=False,all_selected_article_bodies_recovered=all(bool(x['articleBody']) for x in results),finished_at_utc=c.utcnow(),inference_warning='Symmetric selected-report ascertainment permits review-cohort comparisons only. URL listing coverage, reporting selection, event geography, coding and event dedup must be validated before any event-rate comparison. No causal effect is identified solely by these counts.')
 c.atomic(OUT/'collection_summary.json',summary);print(json.dumps(summary,indent=2),flush=True)
 if c.STOP.is_set():raise SystemExit(3)

if __name__=='__main__':main()
