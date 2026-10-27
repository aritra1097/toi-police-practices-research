"""Build a panel of detected, AI-validated reports, never real-incidence zeros.

Run only after acquisition, positive-signal review and low-signal audit finish.
"""
from pathlib import Path
import csv,json,datetime as dt,calendar,hashlib,collections
R=Path(__file__).resolve().parent;OUT=R/'analysis';OUT.mkdir(exist_ok=True)
ledger=R/'event_coding/event_ledger.json';events=json.loads(ledger.read_text())
review=json.loads((R/'event_coding/summary.json').read_text())
cohort=R/'collection/output/article_review_cohort_private.jsonl'
articles=[json.loads(x) for x in cohort.read_text().splitlines() if x.strip()]
assert len(articles)==len({x['article_id'] for x in articles})==1132
assert all(x['metadata_status']=='success' for x in articles)
assert review.get('unresolved_flagged_articles',0)==0,'Positive signals remain unresolved/unreviewed'
audit_path=R/'collection/audit_negatives/review_summary.json'
audit=json.loads(audit_path.read_text())
assert audit['full_selected_cohort']==len(articles)
assert audit['reviewed_records']==audit['selected_unique_article_ids']==48
assert sum(audit['reviewed_by_state'].values())==48
assert audit['expanded_signal_articles']==review['expanded_target_signal_articles']==245
STATES={'West Bengal':'WB','Kerala':'KL','Tamil Nadu':'TN','Telangana':'TG'}
FIELDS={
 'gun_taking_police_shooting':'main_reported_gun_taking_then_police_shot',
 'fatal_gun_taking_police_shooting':'main_fatal_subset',
 'nonfatal_gun_taking_police_shooting':'main_nonfatal_subset',
 'police_public_parade_broad':'secondary_reported_police_public_parade_broad',
 'police_reconstruction_parade':'secondary_reported_reconstruction_public_parade',
 'police_reconstruction_shirtless':'secondary_reported_reconstruction_shirtless_police_parade_strict'
}
counts=collections.Counter();counted=[]
for e in events:
 if e['state_actual'] not in STATES:continue
 try:day=dt.date.fromisoformat(e['event_date_ist'])
 except ValueError:continue
 if not dt.date(2024,1,1)<=day<=dt.date(2026,10,27):continue
 for outcome,col in FIELDS.items():
  if int(e.get(col,0))==1:
   counts[(STATES[e['state_actual']],day.strftime('%Y-%m'),outcome)]+=1
   counted.append(dict(event_id=e['event_id'],event_date_ist=str(day),state=STATES[e['state_actual']],outcome=outcome,date_quality=e['date_quality']))
rows=[]
for state in STATES.values():
 for year in [2024,2025,2026]:
  for month in range(1,13):
   if (year,month)>(2026,10):continue
   ym=f'{year}-{month:02d}';days=27 if (year,month)==(2026,10) else calendar.monthrange(year,month)[1]
   for outcome in FIELDS:
    rows.append(dict(state=state,month=ym,outcome=outcome,count=counts[(state,ym,outcome)],observed=1,complete_frame=1,eligible_days=days,unresolved_count=0,measurement='confirmed_detected_case_count_within_closed_retrieval_pipeline',population_incidence_observed=0,zero_means='no_positive_identified_by_this_pipeline_not_zero_real_events'))
def save(name,data):
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
save('detected_case_panel.csv',rows);save('counted_event_outcomes.csv',counted)
window_rows=[]
for state in STATES.values():
 for outcome in FIELDS:
  for label,start,end in [('pre_all',dt.date(2024,1,1),dt.date(2026,4,30)),('post_main',dt.date(2026,6,1),dt.date(2026,10,27)),('pre_season_2025',dt.date(2025,6,1),dt.date(2025,10,27)),('post_transition_inclusive',dt.date(2026,5,9),dt.date(2026,10,27))]:
   n=sum(x['state']==state and x['outcome']==outcome and start<=dt.date.fromisoformat(x['event_date_ist'])<=end for x in counted)
   days=(end-start).days+1
   window_rows.append(dict(state=state,outcome=outcome,window=label,start=str(start),end=str(end),days=days,detected_case_count=n,detected_cases_per_30_days=30*n/days))
save('detected_case_window_counts.csv',window_rows)
meta=dict(cohort_unique_articles=len(articles),ledger_sha256=hashlib.sha256(ledger.read_bytes()).hexdigest(),cohort_sha256=hashlib.sha256(cohort.read_bytes()).hexdigest(),outcome_fields=FIELDS,states=STATES,pre_end='2026-04-30',post_start='2026-06-01',post_end='2026-10-27',post_days=149,may_excluded_main=True,complete_frame_definition='The fixed listed-URL acquisition plus lexical signal screening and AI source-context adjudication is complete. This flag does not assert complete TOI coverage, complete human review of every background body, known recall, or population event ascertainment.',observed_definition='Counts of confirmed positives identified by the completed pipeline are known; the number of real incidents outside this measurement process remains unknown.',causal_effect_identified=False,limitations=['Same search terms can have different recall across states and periods.','News attention and political salience may alter reporting and visibility.','Source-context coding is AI, not independent human verification.','All-zero detected pretreatment WB outcome leaves synthetic weights weakly or non-identified.','Detected-case contrast is an association in this measurement process, not a causal BJP effect.'])
(OUT/'panel_provenance.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
