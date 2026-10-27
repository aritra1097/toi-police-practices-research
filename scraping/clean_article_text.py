"""Conservatively remove recognizable TOI recommendation/promotion suffixes.

The original articleBody is never overwritten. This is a text-cleaning helper,
not an event classifier. Offsets always refer to the exact raw input string.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

VERSION = 'toi-tail-cleaner-1.0'
RECOMMEND = re.compile(r'We also published the following articles recently', re.I)
ALSO_CHECK = re.compile(r'You Can Also Check\s*:\s*', re.I)
CHECK_CONTENT = re.compile(r'(?:Gold Rate|Silver Rate|Bank Holidays|Public Holidays|'
                           r'[A-Za-z ]+ AQI|Weather in|Petrol Price|Diesel Price|CNG Price|LPG Price)', re.I)
PROMOTION = re.compile(r'(?:Stay updated with (?:the )?latest [^.!?\n]{0,120}news\.\s*)?'
                       r'Download the TOI App\.?\s*$', re.I)


def _section_boundary(prefix: str) -> bool:
    # TOI JSON-LD commonly joins a footer without spaces, e.g. "said.tnnWe...".
    # A quoted or incidental mention inside a sentence does not pass this gate.
    return not prefix.strip() or bool(re.search(r'(?:[.!?][\"\'\u2019\u201d]*\s*(?:tnn\s*)?|\n\s*)$', prefix, re.I))


def clean_article_text(raw: str) -> dict:
    if not isinstance(raw, str):
        raise TypeError('article text must be a string')
    cuts = []
    for match in RECOMMEND.finditer(raw):
        suffix = raw[match.end():]
        # Actual recommendation headings concatenate an uppercase title or an
        # article ID; quoted prose followed by a comma/closing quote is retained.
        following = suffix.lstrip(' \t\r\n:\"\'\u201c\u2018')
        if (_section_boundary(raw[:match.start()]) and following
                and (following[0].isupper() or following[0].isdigit())):
            cuts.append((match.start(), 'recommendation_articles_suffix'))
    for match in ALSO_CHECK.finditer(raw):
        suffix = raw[match.end():]
        if (_section_boundary(raw[:match.start()]) and CHECK_CONTENT.match(suffix)
                and suffix[:1500].count('|') >= 2):
            cuts.append((match.start(), 'city_links_suffix'))
    for match in PROMOTION.finditer(raw):
        if _section_boundary(raw[:match.start()]):
            cuts.append((match.start(), 'toi_app_promotion_suffix'))
    cut = min((position for position, _ in cuts), default=len(raw))
    cleaned = raw[:cut].rstrip() if cuts else raw
    flags = sorted({flag for position, flag in cuts if position >= cut})
    retained_markers = []
    if RECOMMEND.search(cleaned): retained_markers.append('recommendation_heading_retained')
    if ALSO_CHECK.search(cleaned): retained_markers.append('also_check_heading_retained')
    return dict(articleBody_raw=raw, articleBody_clean=cleaned,
                articleBody_cleaning_applied=bool(cuts), articleBody_cleaning_flags=flags,
                articleBody_cleaning_flags_json=json.dumps(flags),
                articleBody_removed_tail_chars=len(raw) - len(cleaned),
                articleBody_cleaner_version=VERSION,
                articleBody_cleaning_review_needed=bool(retained_markers),
                articleBody_cleaning_review_flags_json=json.dumps(retained_markers),
                articleBody_cleaning_cut_offset=cut if cuts else None)


def add_clean_text_fields(record: dict) -> dict:
    result = dict(record)
    raw = result.get('articleBody_raw', result.get('articleBody', ''))
    result.update(clean_article_text(raw if isinstance(raw, str) else ''))
    return result


def self_test() -> None:
    # Offline fixtures, including the observed no-whitespace JSON-LD joins.
    main = 'Police said the suspect escaped. An inquiry remains open. tnn'
    footer = ('We also published the following articles recently'
              'Gun snatched in another state112345678You Can Also Check: '
              'Gold Rate in Kolkata | Silver Rate in Kolkata | Bank Holidays in Kolkata'
              'Stay updated with the latest Kolkata news. Download the TOI App.')
    result = clean_article_text(main + footer)
    assert result['articleBody_clean'] == main
    assert result['articleBody_raw'] == main + footer
    assert result['articleBody_cleaning_applied']
    assert 'Gun snatched' not in result['articleBody_clean']
    for genuine in [
        'The editor discussed the phrase "We also published the following articles recently" in court. Police replied.',
        'A witness said, "You Can Also Check: Gold Rate in Kolkata | Silver Rate in Kolkata | Bank Holidays". The trial continued.',
        'We also published the following articles recently, the editor said. The inquiry continued.',
        'Police explained that Download the TOI App was written on a poster.',
        'The entire long body must remain. ' * 1000,
    ]:
        assert clean_article_text(genuine)['articleBody_clean'] == genuine
    city_tail = 'Main article ends here.You Can Also Check: Gold Rate in Kolkata | Silver Rate in Kolkata | Bank Holidays'
    assert clean_article_text(city_tail)['articleBody_clean'] == 'Main article ends here.'
    assert clean_article_text('The officer said, “The inquiry is open.”We also published the following articles recently"Related headline"')['articleBody_clean'] == 'The officer said, “The inquiry is open.”'
    assert clean_article_text('Main article ends. Download the TOI App.')['articleBody_clean'] == 'Main article ends.'
    assert clean_article_text('')['articleBody_clean'] == ''
    print('Offline cleaner fixtures passed: raw preservation, suffix removal, incidental mentions and untruncated long body.')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true', help='Run offline text fixtures; no network')
    parser.add_argument('--input', type=Path, help='Existing metadata JSONL to enrich without changing articleBody')
    parser.add_argument('--output', type=Path, help='Separate cleaned metadata JSONL')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.input or not args.output:
        parser.error('Provide --input and --output, or --self-test')
    if args.input.resolve() == args.output.resolve():
        parser.error('Use a separate output so raw metadata remains available')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.input.open() as source, args.output.open('w') as target:
        for line in source:
            if line.strip():
                target.write(json.dumps(add_clean_text_fields(json.loads(line)), ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
