"""Offline identity/date/body-quality audit of cached target-collection records."""
from pathlib import Path
import collections,datetime,json,re
ROOT=Path(__file__).resolve().parent
records=[json.loads(f.read_text()) for f in (ROOT/'collection/records').glob('*.json')]
success=[r for r in records if r.get('metadata_status')=='success']
failed=[r for r in records if r.get('metadata_status')!='success']
issues=[];dates=[];naive=[];mismatches=[];short=[]
for r in success:
 aid=r['article_id'];body=r.get('analysis_body','')
 if not r.get('response_id_matches_request') or str(r.get('returned_article_id',''))!=aid:issues.append([aid,'identity'])
 if not r.get('article_headline'):issues.append([aid,'headline'])
 # Error tokens can precede appended recommendations, so exact equality is
 # insufficient. Preserve raw responses, but do not accept such bodies.
 if not body or re.match(r'^\s*ERR[-_ ]?RTF',body,re.I) or re.fullmatch(r'\s*(?:undefined|null|error)\s*',body,re.I):issues.append([aid,'body'])
 if len(body)<120:short.append(dict(article_id=aid,body_characters=len(body),headline=r.get('article_headline','')))
 if re.search(r'We\s+also\s+published\s+(?:the\s+)?following\s+articles\s+recently',body,re.I):issues.append([aid,'recommendation_marker'])
 try:
  pub=datetime.datetime.fromisoformat(r.get('publication_date','').replace('Z','+00:00'));dates.append(pub)
  if pub.tzinfo is None:naive.append(aid)
  source_date=r.get('source_date','')
  if source_date and pub.date().isoformat()!=source_date:mismatches.append(dict(article_id=aid,source_date=source_date,source_publication_date=pub.date().isoformat(),headline=r.get('article_headline','')))
 except ValueError:issues.append([aid,'invalid_or_missing_publication_date'])
result=dict(records=len(records),statuses=dict(collections.Counter(r.get('metadata_status','') for r in records)),successful_metadata_with_nonerror_text=len(success),unresolved_records=[dict(article_id=r['article_id'],status=r['metadata_status'],headline=r.get('source_headline',''),body_characters=len(r.get('analysis_body',''))) for r in failed],success_identity_headline_body_or_date_issues=issues,naive_publication_date_ids=naive,extraction_sources=dict(collections.Counter(r.get('extraction_source','') for r in success)),html_identity_validation=dict(collections.Counter(r.get('html_object_identity_validation','') for r in success if r.get('extraction_source')=='article_html_jsonld')),short_success_bodies_under120=short,recommendation_tails_removed=sum(bool(r.get('recommendation_tail_removed')) for r in success),source_date_available=sum(bool(r.get('source_date')) for r in success),source_date_vs_publication_date_mismatches=mismatches,publication_date_min=min(dates).isoformat() if dates else None,publication_date_max=max(dates).isoformat() if dates else None,checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),body_error_validation='Reject ERR-RTF prefixes as well as exact error tokens: an error followed by recommendations is not usable article text.',correction_note='Final offline review rejected 4489279: HTML articleBody began with ERR-RTF and appended recommendations. Its cached record is unresolved; no new HTTP request was made.',limits=['Success means available identity-validated metadata and non-error text, not full body completeness, truth of police accounts, or reviewed event classification.','Source dates are dataset/archive dates; mismatches do not alone imply incorrect actual publication dates.','This audit describes the targeted 915-article collection, not complete TOI coverage or incidence.'])
(ROOT/'collection_metadata_quality_audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
print(json.dumps({k:result[k] for k in ['records','statuses','successful_metadata_with_nonerror_text','success_identity_headline_body_or_date_issues','naive_publication_date_ids','extraction_sources','short_success_bodies_under120','source_date_available']},indent=2))
