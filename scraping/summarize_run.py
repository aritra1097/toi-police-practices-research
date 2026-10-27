"""Display validated collection results, independent of workflow exit status."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
print('# TOI collection result')
found=False
for file in [R/'output/summary.json',R/'sitemap_output/summary.json']:
 if not file.exists():continue
 found=True;s=json.loads(file.read_text());print(f'\n## {file.parent.name}\n')
 if 'archive_article_rows' in s:
  print(f'- Validated archive rows: **{s["archive_article_rows"]:,}**')
  print(f'- Successful dates: **{s["successful_days"]}/{s["requested_days"]}**')
  print(f'- Status counts: `{json.dumps(s["status_counts"])}`')
  if not s['archive_article_rows']:print('\n**No headline backfill was recovered. A completed workflow is not complete data coverage.**')
 else:
  for key in ['distinct_urls','actual_news_feed_headline_rows','metadata_titles_recovered']:
   if key in s:print(f'- {key}: **{s[key]:,}**')
  print('\nStatic URLs and modification dates are not headlines or publication dates. Selected metadata is a partial supplement.')
if not found:print('\nNo collection summary was produced; inspect the preceding job failure.')
