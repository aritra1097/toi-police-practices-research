"""Combine actual feed/article titles only; URL slug text is never a headline."""
from pathlib import Path
import csv,gzip,json,re,datetime as dt,collections
R=Path(__file__).resolve().parent;P=R/'sitemap_output';out={}
for file,kind in [('actual_headlines_recent_news_feeds.csv.gz','recent_news_feed'),('selected_article_actual_headlines.csv.gz','selected_article_metadata')]:
 with gzip.open(P/file,'rt',newline='') as f:
  for x in csv.DictReader(f):
   headline=x.get('article_headline') if kind=='selected_article_metadata' else x.get('news_title')
   if not headline:continue
   if kind=='selected_article_metadata' and x.get('metadata_status')!='success':continue
   url=x.get('canonical_url') or x['URL'];article_id=x.get('article_id') or '';aid=article_id or url
   pub=x.get('publication_date') if kind=='selected_article_metadata' else x.get('news_publication_date')
   fetched=x.get('metadata_retrieved_at_utc') or x.get('retrieved_at_utc','')
   city=re.search(r'/city/([^/]+)/',url)
   row=dict(content_key=aid,article_id=article_id,headline=headline,url=url,city_url_proxy=city[1] if city else '',publication_date=pub or '',publication_date_type='publisher metadata, not event date',retrieved_at_utc=fetched,headline_source=x.get('headline_source') or 'news_sitemap_title',selection_frame=kind,archive_or_sitemap_lastmod=x.get('sitemap_lastmod',''),source_sitemap=x.get('sitemap_source',''),metadata_selection_routes=x.get('metadata_selection_routes',''),within_2024_to_oct27_2026_ist='unknown',after_oct27_2026_ist='unknown',headline_variants_json='')
   if pub:
    try:
     stamp=dt.datetime.fromisoformat(pub.replace('Z','+00:00'))
     if stamp.tzinfo:
      day=stamp.astimezone(dt.timezone(dt.timedelta(hours=5,minutes=30))).date()
     else:day=None
     if day is not None:
      row['within_2024_to_oct27_2026_ist']=int(dt.date(2024,1,1)<=day<=dt.date(2026,10,27));row['after_oct27_2026_ist']=int(day>dt.date(2026,10,27))
    except ValueError:pass
   if aid in out:
    old=out[aid];variants=json.loads(old['headline_variants_json'])
    if headline not in variants:variants.append(headline)
    frames=old['selection_frame'].split(';')
    if kind not in frames:frames.append(kind)
    if kind=='selected_article_metadata':
     if not row['publication_date']:
      for col in ['publication_date','within_2024_to_oct27_2026_ist','after_oct27_2026_ist']:row[col]=old[col]
     old.update(row)
    old['selection_frame']=';'.join(frames);old['headline_variants_json']=json.dumps(variants,ensure_ascii=False)
   else:row['headline_variants_json']=json.dumps([headline],ensure_ascii=False);out[aid]=row
rows=sorted(out.values(),key=lambda x:(x['publication_date'],x['article_id']))
dest=R/'toi_actual_headlines_PARTIAL_2024_to_current.csv.gz'
with gzip.open(dest,'wt',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=dict(actual_headline_content_items=len(rows),distinct_nonempty_article_ids=len({x['article_id'] for x in rows if x['article_id']}),items_without_article_id=sum(not x['article_id'] for x in rows),within_2024_to_oct27_2026_ist=sum(x['within_2024_to_oct27_2026_ist']==1 for x in rows),after_oct27_2026_ist=sum(x['after_oct27_2026_ist']==1 for x in rows),unknown_publication_date_or_timezone=sum(x['within_2024_to_oct27_2026_ist']=='unknown' for x in rows),selection_frames=dict(collections.Counter(x['selection_frame'] for x in rows)),full_headline_backfill_complete=False,output=str(dest),date_caution='Cutoff calendar uses IST; Oct28IST extras can occur while collection date is Oct27 NewYork. Publication date is not incident date.')
(R/'actual_headlines_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
