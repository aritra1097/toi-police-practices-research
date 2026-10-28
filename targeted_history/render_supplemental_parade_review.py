"""Stage independent parade review without treating unread text as negative."""
from pathlib import Path
import json,csv,re,collections,datetime as dt
ROOT=Path(__file__).resolve().parent
ROUTES=('supplement_specific_clothing','supplement_literal_nonceremonial_actor_parade')
queue=json.loads((ROOT/'extended_queue.json').read_text())
queue=[r for r in queue if any(x in str(r.get('retrieval_routes',[])) for x in ROUTES)]
D=json.loads((ROOT/'supplemental_parade_review_decisions.json').read_text())
under=re.compile(r'under.?wear|inner.?wear|under.?pants|under.?garment|naked|nude|shirtless|semi.?clad|half.?clad|bare.?bod|bare.?chest|stripp|without.{0,12}clothes|chaddi|kachch',re.I)
recon=re.compile(r're.?construc|re.?creat|re.?enact|spot.?verif|scene.?verif|physical.?verif|moka|mauka',re.I)
actor=re.compile(r'\b(?:police|cops?|constables?|inspectors?|jail|wardens?)\b',re.I)
parade=re.compile(r'parad\w*|march\w*|drag\w*',re.I)
rows=[];cases=[]
for q in queue:
 aid=q['article_id'];file=ROOT/'collection/records'/f'{aid}.json';r=json.loads(file.read_text()) if file.exists() else {};b=r.get('analysis_body','')
 u=bool(under.search(b));rc=bool(recon.search(b));ac=bool(actor.search(b));pa=bool(parade.search(b));joint=u and rc and ac
 known=D.get(aid)
 if r and r.get('response_id_matches_request') is False:stage='source_identity_mismatch_not_event_evidence'
 elif known:stage=known['review_stage']
 elif not r:stage='awaiting_retrieval'
 elif not b.strip():stage='retrieved_body_unavailable_not_negative'
 elif joint:stage='joint_underclothing_actor_reconstruction_signal_unreviewed'
 elif u and ac and pa:stage='underclothing_actor_parade_signal_unreviewed'
 elif rc and ac and pa:stage='reconstruction_actor_parade_signal_unreviewed'
 else:stage='lexical_triage_no_joint_target_signal_not_case_reviewed'
 rows.append(dict(article_id=aid,URL=r.get('url',q.get('url','')),headline=r.get('article_headline',q.get('source_headline','')),publication_date=r.get('publication_date',''),source_listing_date=q.get('source_date',''),retrieval_routes=';'.join(q.get('retrieval_routes',[])),metadata_status=r.get('metadata_status','not_yet_retrieved'),response_id_matches_request=r.get('response_id_matches_request','not_yet_retrieved'),body_available=int(bool(b.strip())),body_quality_flags=';'.join(r.get('body_quality_flags',[])),underclothing_signal=int(u),reconstruction_signal=int(rc),actor_signal=int(ac),parade_movement_signal=int(pa),review_stage=stage,reviewed_classification=known.get('classification','') if known else '',case_specific_reconstruction_reported=known.get('reconstruction','unknown') if known else 'unreviewed',underclothed_or_naked_reported=known.get('underclothed','unknown') if known else 'unreviewed',evidence_paraphrase=known.get('evidence','') if known else '',event_id=known.get('event_id','') if known else '',reviewer='independent_AI_source_context_review' if known else '',full_available_body_read=int(bool(known and known.get('full_body_read'))),record_retrieved_at_utc=r.get('retrieved_at_utc','')))
 if known and known.get('event') and r.get('response_id_matches_request') is not False:
  e=dict(known['event']);e['source_article_ids']=aid;e['source_publication_dates']=r.get('publication_date','');e['source_urls']=r.get('url',q.get('url',''));e['evidence_paraphrase']=known['evidence'];e['review_method']='AI_full_available_body_review_not_human_verified';e['actual_truth_or_legality_established']='no';cases.append(e)
def write(name,data):
 with (ROOT/name).open('w',newline='') as f:
  fields=list(dict.fromkeys(k for r in data for k in r)) if data else ['article_id'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
# Event rows collapse repeated reports rather than counting articles as events.
merged={}
for e in cases:
 key=e['event_id']
 if key not in merged:merged[key]=e
 else:
  old=merged[key]
  for field in ['source_article_ids','source_publication_dates','source_urls']:
   old[field]+=';'+e[field]
cases=list(merged.values())
write('supplemental_parade_body_review.csv',rows);write('supplemental_parade_case_events.csv',cases)
# New episodes only, with exactly the shared public event-table schema.
with (ROOT/'parade_and_wb_context_events.csv').open() as f:shared_fields=csv.DictReader(f).fieldnames
new_cases=[]
for e in cases:
 if not e.get('new_vs_known','').startswith('new_'):continue
 z={k:e.get(k,'unknown') for k in shared_fields}
 z['gun_taking_personally_attributed_to_fatal_victim']='not_applicable'
 z['context_evidence_paraphrase']=e['evidence_paraphrase']
 z['case_specific_reconstruction_reported']=e.get('case_specific_reconstruction_reported','unknown')
 z['review_method']='independent_AI_full_available_body_source_review_not_human_verified'
 new_cases.append(z)
with (ROOT/'supplemental_parade_events.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=shared_fields);w.writeheader();w.writerows(new_cases)
s=collections.Counter(r['review_stage'] for r in rows)
summary=dict(snapshot_utc=dt.datetime.now(dt.timezone.utc).isoformat(),selected_supplemental_articles=len(rows),retrieved_records=sum(r['metadata_status']!='not_yet_retrieved' for r in rows),full_available_bodies_read=sum(r['full_available_body_read'] for r in rows),manual_decisions=len(D),stage_counts=dict(s),case_rows=len(cases),exact_reconstruction_underclothing_rows=sum(e.get('comparison_class')=='exact_underclothed_public_police_reconstruction_report' for e in cases),interpretation='Staged independent source review; unread and lexical no-signal rows are not verified negatives.')
(ROOT/'supplemental_parade_body_review_summary.json').write_text(json.dumps(summary,indent=2))
text=['# Supplemental historical parade body review','',f"Snapshot: {summary['snapshot_utc']}. The declared route-specific queue contains {len(rows)} article IDs; {summary['retrieved_records']} have retrieved records at this snapshot. Only explicit manual decisions represent source-context review. Lexical triage and unread statuses are not negative event labels.",'','## Stages','']
for k,v in sorted(s.items()):text.append(f'- `{k}`: {v}')
text+=['','Full-body review means the entire available `analysis_body` was read. It does not guarantee the publisher returned its complete original article; empty/error bodies remain unknown. Promoted case rows require full available-body review and use reported-text labels consistent with `event_table_codebook.md`. No legal or truth finding is made.','','## Reviewed reports','']
for row in rows:
 if row['reviewer']:text.append(f"- [{row['article_id']}]({row['URL']}): **{row['reviewed_classification']}**. {row['evidence_paraphrase']}")
text+=['','## Files','','`supplemental_parade_body_review.csv` retains the complete staged queue, including awaiting/unread rows. `supplemental_parade_events.csv` contains only newly promoted episodes with the shared35-column event-table schema. `supplemental_parade_case_events.csv` also retains reconfirmed known episodes for source joins; do not count these duplicates as new. Neither is a census. `supplemental_parade_review_decisions.json` records manual judgements, and the rendering script regenerates this snapshot as acquisition continues.','','The primary exact target is an underclothed/naked public police parade explicitly linked to a case-specific scene reconstruction. Ordinary escorts, court transport, private mobs, prison discipline, foreign episodes, artistic reenactments and generic investigation are separate categories.']
(ROOT/'supplemental_parade_body_review.md').write_text('\n'.join(text)+'\n')
print(json.dumps(summary,indent=2))
