"""Combine actual feed/article titles only; URL slugs are never headlines.

Default cutoff is today in Asia/Kolkata. Use --end 2026-10-27 to reproduce the
original snapshot. Publication extras remain in the output, explicitly flagged.
"""
from pathlib import Path
import argparse, csv, gzip, json, re, datetime as dt, collections
from zoneinfo import ZoneInfo

R = Path(__file__).resolve().parent
LEGACY_START = dt.date(2024, 1, 1)
LEGACY_END = dt.date(2026, 10, 27)
FIELDS = ['content_key', 'article_id', 'headline', 'url', 'city_url_proxy',
          'publication_date', 'publication_date_type', 'publication_date_variants_json',
          'retrieved_at_utc', 'retrieval_timestamps_json', 'headline_source',
          'selection_frame', 'archive_or_sitemap_lastmod', 'source_sitemap',
          'metadata_selection_routes', 'requested_start_ist', 'requested_end_ist',
          'publication_day_ist', 'within_requested_ist_window',
          'after_requested_ist_end', 'before_requested_ist_start',
          'within_2024_to_oct27_2026_ist', 'after_oct27_2026_ist',
          'headline_variants_json']


def publication_day_ist(value):
    try:
        stamp = dt.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return stamp.astimezone(ZoneInfo('Asia/Kolkata')).date() if stamp.tzinfo else None
    except (TypeError, ValueError):
        return None


def cutoff_flags(publication, start, end):
    day = publication_day_ist(publication)
    return dict(requested_start_ist=start.isoformat(), requested_end_ist=end.isoformat(),
        publication_day_ist=day.isoformat() if day else '',
        within_requested_ist_window=int(start <= day <= end) if day else 'unknown',
        after_requested_ist_end=int(day > end) if day else 'unknown',
        before_requested_ist_start=int(day < start) if day else 'unknown',
        # These legacy fields retain their fixed snapshot-reference meaning.
        within_2024_to_oct27_2026_ist=int(LEGACY_START <= day <= LEGACY_END) if day else 'unknown',
        after_oct27_2026_ist=int(day > LEGACY_END) if day else 'unknown')


def combine(source, dest, summary_path, start, end, additional_metadata=()):
    out = {}
    inputs_present, inputs_missing = [], []
    sources = [(source / 'actual_headlines_recent_news_feeds.csv.gz', 'recent_news_feed'),
               (source / 'selected_article_actual_headlines.csv.gz', 'selected_article_metadata')]
    sources.extend((Path(path), 'selected_additional_article_metadata') for path in additional_metadata)
    for path, kind in sources:
        file = path.name
        if not path.exists():
            inputs_missing.append(file)
            continue
        inputs_present.append(file)
        with gzip.open(path, 'rt', newline='', encoding='utf-8') as handle:
            for x in csv.DictReader(handle):
                metadata = kind != 'recent_news_feed'
                headline = x.get('article_headline') if metadata else x.get('news_title')
                if not headline or (metadata and x.get('metadata_status') != 'success'):
                    continue
                url = x.get('canonical_url') or x['URL']
                article_id = x.get('article_id') or ''
                key = article_id or url
                pub = (x.get('publication_date') if metadata else x.get('news_publication_date')) or ''
                fetched = x.get('metadata_retrieved_at_utc') or x.get('retrieved_at_utc', '')
                city = re.search(r'/city/([^/]+)/', url)
                row = dict(content_key=key, article_id=article_id, headline=headline, url=url,
                    city_url_proxy=city[1] if city else '', publication_date=pub,
                    publication_date_type='publisher metadata, not event date',
                    retrieved_at_utc=fetched, headline_source=x.get('headline_source') or 'news_sitemap_title',
                    selection_frame=kind, archive_or_sitemap_lastmod=x.get('sitemap_lastmod', ''),
                    source_sitemap=x.get('sitemap_source', ''), metadata_selection_routes=x.get('metadata_selection_routes', ''),
                    publication_date_variants_json=json.dumps([dict(value=pub, source=kind)] if pub else []),
                    retrieval_timestamps_json=json.dumps([fetched] if fetched else []),
                    headline_variants_json=json.dumps([headline], ensure_ascii=False))
                if key in out:
                    old = out[key]
                    variants = json.loads(old['headline_variants_json'])
                    if headline not in variants: variants.append(headline)
                    dates = json.loads(old['publication_date_variants_json'])
                    entry = dict(value=pub, source=kind)
                    if pub and entry not in dates: dates.append(entry)
                    stamps = json.loads(old['retrieval_timestamps_json'])
                    if fetched and fetched not in stamps: stamps.append(fetched)
                    frames = old['selection_frame'].split(';')
                    if kind not in frames: frames.append(kind)
                    if metadata:
                        if not row['publication_date']: row['publication_date'] = old['publication_date']
                        old.update(row)
                    old.update(selection_frame=';'.join(frames),
                        headline_variants_json=json.dumps(variants, ensure_ascii=False),
                        publication_date_variants_json=json.dumps(dates), retrieval_timestamps_json=json.dumps(stamps))
                else: out[key] = row
    rows = sorted(out.values(), key=lambda x: (x['publication_date'], x['article_id']))
    for row in rows: row.update(cutoff_flags(row['publication_date'], start, end))
    dest.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(dest, 'wt', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader(); writer.writerows(rows)
    summary = dict(actual_headline_content_items=len(rows),
        distinct_nonempty_article_ids=len({x['article_id'] for x in rows if x['article_id']}),
        items_without_article_id=sum(not x['article_id'] for x in rows),
        requested_start_ist=start.isoformat(), requested_end_ist=end.isoformat(),
        within_requested_ist_window=sum(x['within_requested_ist_window'] == 1 for x in rows),
        after_requested_ist_end=sum(x['after_requested_ist_end'] == 1 for x in rows),
        before_requested_ist_start=sum(x['before_requested_ist_start'] == 1 for x in rows),
        within_2024_to_oct27_2026_ist=sum(x['within_2024_to_oct27_2026_ist'] == 1 for x in rows),
        after_oct27_2026_ist=sum(x['after_oct27_2026_ist'] == 1 for x in rows),
        legacy_reference_window_ist=[LEGACY_START.isoformat(), LEGACY_END.isoformat()],
        unknown_publication_date_or_timezone=sum(x['within_requested_ist_window'] == 'unknown' for x in rows),
        selection_frames=dict(collections.Counter(x['selection_frame'] for x in rows)),
        inputs_present=inputs_present, inputs_missing=inputs_missing,
        full_headline_backfill_complete=False, output=str(dest),
        combined_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        date_caution='Requested cutoff uses IST. Publication extras are retained and flagged. '
                     'Naive/unparseable dates remain unknown; publication date is not incident date. '
                     'Legacy cutoff-named fields always refer to the original 2024-01-01 through 2026-10-27 snapshot.')
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))
    return summary


def main():
    today = dt.datetime.now(ZoneInfo('Asia/Kolkata')).date()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sitemap-output', type=Path, default=R / 'sitemap_output')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--start', help='First publication cutoff date; default 2024-01-01')
    group.add_argument('--start-year', type=int, help='First publication cutoff year (January 1)')
    parser.add_argument('--end', help='Last publication cutoff date, default source-calendar today in Asia/Kolkata')
    parser.add_argument('--output', type=Path, help='Combined gzip CSV output')
    parser.add_argument('--summary', type=Path, default=R / 'actual_headlines_summary.json')
    parser.add_argument('--additional-metadata', action='append', type=Path, default=[],
        help='Additional actual-metadata gzip CSV, e.g. the four-state cohort; repeatable')
    args = parser.parse_args()
    start = dt.date(args.start_year, 1, 1) if args.start_year is not None else dt.date.fromisoformat(args.start or '2024-01-01')
    end = dt.date.fromisoformat(args.end) if args.end else today
    if start > end or end > today: parser.error('Require start <= end <= today in Asia/Kolkata')
    # Preserve the scheduled workflow's default name. Explicit windows receive
    # honest date-qualified names unless --output is supplied.
    default_name = ('toi_actual_headlines_PARTIAL_2024_to_current.csv.gz'
        if args.end is None and start == LEGACY_START else
        f'toi_actual_headlines_PARTIAL_{start.isoformat()}_to_{end.isoformat()}.csv.gz')
    summary = combine(args.sitemap_output, args.output or R / default_name, args.summary, start, end,
        args.additional_metadata)
    print(json.dumps(summary, indent=2))
    if not summary['inputs_present']: raise SystemExit(2)


if __name__ == '__main__': main()
