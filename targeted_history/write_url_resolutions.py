"""Record bounded primary-source web-search findings; no network or source mutation."""
from pathlib import Path
import csv, datetime, json
ROOT=Path(__file__).resolve().parent
targets=[('2012-08-04','Behala body was of criminal shot in police encounter'),('2011-01-12','Bullet holes put shootout story in doubt'),('2001-12-17','NLFT insurgent killed in encounter'),('2002-05-15','KLO militant killed in encounter'),('2002-05-25','KLO militant killed in encounter'),('2003-08-02','Three militants killed in Jalpaiguri encounter'),('2010-06-16','8 Maoists killed in police encounter in West Bengal'),('2010-07-26','6 Maoist killed in West Bengal encounter')]
baseline={(r['date'],r['headline']):r for r in csv.DictReader((ROOT.parent/'data/candidates.csv').open())}
def match(aid,slug,title,date,time,kind,note):
 return dict(article_id=aid,url=f'https://timesofindia.indiatimes.com/{slug}/articleshow/{aid}.cms',headline=title,source_publication_date=date,source_display_time_IST=time,match_type=kind,primary_source_observation=note,evidence='TOI primary article content returned by web-search tool; no independent HTTP body request')
records=[]
for date,title in targets:
 b=baseline[date,title]
 records.append(dict(baseline_id=b['id'],source_headline=title,source_date=date,source_date_type='dataset_publish_date',source_category=b['category'],source_provenance=b['provenance'],status='unresolved_no_exact_primary_match_found',resolved_url='',resolved_article_id='',matches=[],review_note='No exact TOI headline-and-date match recovered in this bounded search. This is retrieval failure, not evidence the event or article did not exist.'))
def rec(date):return next(r for r in records if r['source_date']==date)
for date,m in [
 ('2011-01-12',match('7263469','city/kolkata/bullet-holes-put-shootout-story-in-doubt','Bullet holes put shootout story in doubt','2011-01-12','08:21','exact_headline_and_date','Article concerns Netai villagers and disputed claims of a CPM-Maoist shootout. It describes CID doubts about rival groups exchanging fire; this is not an accused-police gun-taking episode.')),
 ('2002-05-15',match('9915881','city/kolkata/klo-militant-killed-in-encounter','KLO militant killed in encounter','2002-05-15','03:45','exact_headline_and_date','Army intelligence personnel pursued a militant vehicle near Siliguri. The report describes a militant attempting to fire and soldiers responding; it explicitly identifies an Army operation rather than police participation. No immediate taking of an officer firearm appears in the visible article narrative.')),
 ('2002-05-25',match('13909061','city/kolkata/klo-militant-killed-in-encounter','KLO militant killed in encounter','2002-05-25','02:05','exact_headline_and_date','Despite the singular headline, the body reports two suspected militants killed near Kumargram. State armed police reportedly challenged a group crossing a forest corridor; militants allegedly fired first. A pistol and ammunition were recovered. No immediate taking of a police firearm appears in the visible narrative.')),
]:
 r=rec(date);r.update(status='resolved_exact_headline_and_date',resolved_url=m['url'],resolved_article_id=m['article_id'],matches=[m],review_note='Primary headline and displayed date match the local record. Incident date and actor/outcome still require separate event coding.')
m=match('6053152','india/8-maoists-killed-in-police-encounter-in-bengal','8 Maoists killed in police encounter in Bengal','2010-06-17','05:24','likely_same_incident_related_report_not_exact_headline_date','Reports eight deaths in a prolonged Ranjya/Salboni forest operation on Wednesday, consistent with an incident on 16 June. Police describe surrounding an armed rebel camp and exchanging fire. The displayed headline differs and publication is one day later than the local record.')
rec('2010-06-16').update(status='related_primary_report_found_exact_record_unresolved',matches=[m],review_note='Likely same incident, but do not overwrite the original headline/date, assign this article ID as an exact match, or count a second incident without event review.')
rec('2001-12-17')['rejected_title_match']=match('251850','india/nlft-insurgent-killed-in-encounter','NLFT insurgent killed in encounter','2003-10-26','12:20','rejected_different_date_and_distinct_local_record','This Tripura/Dhalai report matches the title but is dated October 2003, not December 2001. The baseline independently contains this October 2003 headline; it cannot resolve the December 2001 record. A Kolkata desk label alone does not establish a West Bengal event.')
queries=[
'site:timesofindia.indiatimes.com "Behala body" "criminal"',
'site:timesofindia.indiatimes.com "Bullet holes put shootout story in doubt"',
'site:timesofindia.indiatimes.com "NLFT insurgent killed in encounter"',
'site:timesofindia.indiatimes.com "KLO militant killed in encounter"',
'site:timesofindia.indiatimes.com "Behala body was of criminal shot in police encounter"',
'site:timesofindia.indiatimes.com "Three militants killed in Jalpaiguri encounter"',
'site:timesofindia.indiatimes.com "8 Maoists killed" "June 16, 2010"',
'site:timesofindia.indiatimes.com "6 Maoist killed in West Bengal encounter"',
'site:timesofindia.indiatimes.com Behala body criminal police encounter August 4 2012',
'site:timesofindia.indiatimes.com Jalpaiguri encounter "August 2, 2003"',
'site:timesofindia.indiatimes.com "Maoist" "July 26, 2010" "encounter"',
'site:timesofindia.indiatimes.com "NLFT" "December 17, 2001"',
'"Behala body" encounter',
'"Three militants killed" "Jalpaiguri" "2003"',
'"6 Maoist killed" "West Bengal"',
'"NLFT insurgent killed" "2001"',
'site:timesofindia.indiatimes.com/city/kolkata/ behala "encounter" "2012"',
'site:timesofindia.indiatimes.com "Jalpaiguri encounter" "Three"',
'site:timesofindia.indiatimes.com "6 Maoists" "Jul 26, 2010"',
'site:timesofindia.indiatimes.com "NLFT" "Dec 17, 2001"',
]
result=dict(recorded_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),task='Resolve eight historical headline records missing URLs, using bounded web search and primary TOI evidence.',search_scope='20 finite queries in five batched web-tool calls; not an exhaustive search of TOI, other publishers or web archives.',exact_resolutions=3,related_report_only=1,unresolved_without_related_exact_record=4,article_bodies_independently_fetched=False,queries=queries,records=records,limitations=['Search indexes omit or de-rank old articles; unresolved is not a negative event code.','A related report is not an exact bibliographic match.','Original dataset date fields and headline text remain unchanged.','Article narratives are reported accounts, not independent verification of police claims.'])
(ROOT/'missing_url_resolution.json').write_text(json.dumps(result,indent=2,ensure_ascii=False))
lines=['# Targeted historical URL resolution','', 'Eight specified headline records were checked with 20 finite web queries on 27 October 2026 (New York date). Three exact headline-and-date matches were recovered. One likely same-incident report was found with a different title/date; four remain unresolved. Search failure is not evidence that an article or event did not exist. No independent HTTP body requests were made.','', '| Local date | Headline | Resolution |','|---|---|---|']
for r in records:
 if r['resolved_url']:resolution=f"[Exact TOI match, ID {r['resolved_article_id']}]({r['resolved_url']})"
 elif r['matches']:
  m=r['matches'][0];resolution=f"[Related report, ID {m['article_id']}]({m['url']}); published {m['source_publication_date']}; exact record unresolved"
 else:resolution='Unresolved in bounded search'
 lines.append(f"| {r['source_date']} | {r['source_headline']} | {resolution} |")
lines+=['','The May 15 KLO report describes an **Army** operation; the May 25 body reports **two** deaths despite its singular headline. The January 2011 article concerns Netai villagers and disputed rival-group gunfire, rather than an accused taking a police firearm. These distinctions matter for actor and outcome coding. The visible narratives in the resolved KLO reports do not describe an immediate police-gun-taking mechanism.','', 'The June 17 Salboni/Ranjya report likely concerns the June 16 incident, but its article ID must not silently replace the different local headline/date. Likewise, the [October 26, 2003 NLFT article](https://timesofindia.indiatimes.com/india/nlft-insurgent-killed-in-encounter/articleshow/251850.cms) is a distinct local record and does not resolve December 17, 2001. It concerns Tripura: a Kolkata desk label is not event geography.','', 'Exact local IDs, source references, queries, observed publication dates and uncertainty labels are in `missing_url_resolution.json`. These are bibliographic resolution and preliminary contextual observations; reported police accounts remain allegations requiring event-level review.']
(ROOT/'missing_url_resolution.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:result[k] for k in ['exact_resolutions','related_report_only','unresolved_without_related_exact_record']}))
