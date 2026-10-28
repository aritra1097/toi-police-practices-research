"""Build readable discovery tables; full article text is deliberately excluded."""
from pathlib import Path
import argparse,csv,json,collections,hashlib,datetime as dt
R=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--use-existing-article-index',action='store_true',help='Reproduce public case/headline tables using the published derived article index when private source records are absent.')
args=parser.parse_args()
record_paths=sorted((R/'collection/records').glob('*.json'))
if not record_paths and not args.use_existing_article_index:
 raise SystemExit('Private acquisition records are absent. Supply them or pass --use-existing-article-index to retain the published derived index.')
def read(name):
 p=R/name
 return list(csv.DictReader(p.open())) if p.exists() else []
def save(name,rows,fields=None):
 if not rows:return
 with (R/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(rows)
cases=[];dedup=[]
national=[]
for file in ['national_gun_events_simple.csv','national_body_events_simple.csv']:
 for x in read(file):
  national.append(x)
  cases.append(dict(case_id=x['event_id'],event_date_ist=x.get('event_date_ist',''),date_basis=x.get('date_basis',''),state=x.get('state_actual',''),locality=x.get('locality',''),case_name=x.get('case_name',''),practice='gun_taking_and_shooting_report',context=x.get('context_category',''),comparison_class='ordinary_crime_report' if x.get('ordinary_crime_main_scope')=='yes' else 'special_or_delayed_context_report',gun_taking_scope=x.get('gun_taking_claim_scope',''),gun_taking_stage=x.get('gun_taking_claim_stage',''),reported_outcome=x.get('reported_shooting_outcome',''),clothing='not_applicable',reconstruction='see_context_and_source',source_article_ids=x.get('source_article_ids',''),source_publication_dates=x.get('source_publication_dates',''),source_urls=x.get('source_urls',''),evidence_notes=x.get('gun_taking_attribution','')+' '+x.get('temporal_link',''),uncertainties=x.get('uncertainties',''),review_status=x.get('review_status','AI source-context review; human verification outstanding'),input_table=file))
for file in ['parade_and_wb_context_events.csv','supplemental_parade_events.csv']:
 for x in read(file):
  cases.append(dict(case_id=x['event_id'],event_date_ist=x.get('event_date_display',''),date_basis=x.get('date_basis',''),state=x.get('state_actual',''),locality=x.get('locality',''),case_name=x.get('subjects',''),practice=x.get('event_type',''),context=x.get('context_category',''),comparison_class=x.get('comparison_class',''),gun_taking_scope=x.get('gun_taking_claim_scope',''),gun_taking_stage=x.get('gun_taking_claim_stage',''),reported_outcome=x.get('reported_shooting_outcome',''),clothing=x.get('clothing_description',''),reconstruction=x.get('case_specific_reconstruction_reported',''),source_article_ids=x.get('source_article_ids',''),source_publication_dates=x.get('source_publication_dates',''),source_urls=x.get('source_urls',''),evidence_notes=x.get('evidence_paraphrase',''),uncertainties=x.get('uncertainties_and_exclusions',''),review_status=x.get('source_report_status','')+'; '+x.get('review_method',''),input_table=file))
for x in read('wb_historical_special_contexts.csv'):
 # This source-backed overlap was independently reviewed in both inputs.
 if '37424220' in x.get('article_ids','').split(';'):
  dedup.append(dict(input='wb_historical_special_contexts.csv',event_key=x['event_key'],reason='Haridevpur2014 already represented in independent web event table; preserve its separate article-review row.'));continue
 cases.append(dict(case_id=x['event_key'],event_date_ist=x.get('event_date',''),date_basis=x.get('event_date_note',''),state=x.get('actual_state',''),locality=x.get('place',''),case_name=x.get('person',''),practice='WB_special_context_or_exclusion',context=x.get('context_group',''),comparison_class=x.get('strict_state_police_individual_mechanism','')+' strict state-police individual match; '+x.get('expanded_security_force_individual_mechanism','')+' expanded force individual match',gun_taking_scope=x.get('weapon_taking_actor',''),gun_taking_stage=x.get('taking_claim_stage',''),reported_outcome=x.get('outcome',''),clothing='not_applicable',reconstruction=x.get('custody_or_crime_reconstruction',''),source_article_ids=x.get('article_ids',''),source_publication_dates='',source_urls=x.get('source_url',''),evidence_notes=x.get('source_context',''),uncertainties=x.get('event_date_note',''),review_status=x.get('evidence_status',''),input_table='wb_historical_special_contexts.csv'))
ids=[x['case_id'] for x in cases];assert len(ids)==len(set(ids)),'Duplicate event IDs need substantive deduplication'
assert all(x['source_urls'] for x in cases)
cases.sort(key=lambda x:(x['state']!='West Bengal',x['event_date_ist'],x['case_id']))
save('evidence_table.csv',cases)
save('ordinary_crime_gun_reports.csv',[x for x in national if x.get('ordinary_crime_main_scope')=='yes'])
catalogue=[]
for x in read('combined_candidate_inventory.csv'):
 catalogue.append(dict(candidate_id=x['id'],source_date=x['date'],source_date_type=x.get('date_type','source-date semantics in provenance'),headline=x['headline'],category_proxy=x.get('category',''),url=x.get('url',''),article_id=x.get('article_id',''),retrieval_routes=x.get('retrieval_routes',''),review_priority=x.get('review_priority',''),status='retrieval_candidate_not_confirmed_event'))
assert len({x['candidate_id'] for x in catalogue})==len(catalogue)
save('headline_catalogue.csv',catalogue)
reviews=collections.defaultdict(list)
for file in ['wb_historical_body_review.csv','supplemental_parade_body_review.csv','national_body_review.csv']:
 for x in read(file):
  aid=x.get('article_id','')
  if aid:reviews[aid].append(dict(table=file,decision=x))
article_rows=[]
for p in record_paths:
 x=json.loads(p.read_text());rs=reviews.get(x['article_id'],[])
 stages=[];reasons=[]
 for item in rs:
  a=item['decision'];stage=a.get('body_review_status',a.get('review_stage',a.get('review_depth','review_state_not_supplied')))
  stages.append(item['table']+': '+stage)
  reason=a.get('reason',a.get('evidence_paraphrase',a.get('decision_reason',a.get('notes',''))))
  if reason:reasons.append(item['table']+': '+reason)
 article_rows.append(dict(article_id=x['article_id'],headline=x.get('article_headline',''),source_headline=x.get('source_headline',''),source_date=x.get('source_date',''),source_date_type=x.get('source_date_type',''),publication_date=x.get('publication_date',''),modified_date=x.get('modified_date',''),url=x.get('url',''),metadata_status=x.get('metadata_status',''),body_characters=x.get('body_characters',0),body_quality_flags=';'.join(x.get('body_quality_flags',[])),retrieval_routes=';'.join(x.get('retrieval_routes',[])),manual_review_status='; '.join(stages) if stages else 'not_manually_reviewed',review_reason='; '.join(reasons),body_text_in_public_table='no'))
if not record_paths:
 article_rows=read('article_index.csv')
 if not article_rows:raise SystemExit('Published derived article index is absent too.')
save('article_index.csv',article_rows)
inputs=['national_gun_events_simple.csv','national_body_events_simple.csv','parade_and_wb_context_events.csv','wb_historical_special_contexts.csv','supplemental_parade_events.csv','combined_candidate_inventory.csv','wb_historical_body_review.csv','supplemental_parade_body_review.csv','national_body_review.csv','extended_queue.json']
summary=dict(generated_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),catalogue_candidate_headlines=len(catalogue),source_linked_case_or_context_rows=len(cases),cases_by_input=dict(collections.Counter(x['input_table'] for x in cases)),article_record_files=len(article_rows),metadata_statuses=dict(collections.Counter(x['metadata_status'] for x in article_rows)),duplicate_case_rows_suppressed=dedup,interpretation='Purposive discovery catalogue. Rows mix reported target patterns, near matches, special contexts and exclusions; do not sum as one outcome or treat unread articles as negatives.',inputs_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [R/name for name in inputs] if p.exists()})
(R/'catalogue_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
