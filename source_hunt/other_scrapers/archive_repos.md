# Audit of five public TOI scraper repositories

Reviewed primary source code on 27 October 2026. Repository code was read, never executed. Dates below are latest default-branch commit dates, not GitHub's mutable repository `updated_at` field. Exact commits, blob hashes and endpoint excerpts are retained in `archive_repos_evidence.json`.

| Repository / inspected source | Latest commit | Discovery or extraction surface | Implication |
|---|---|---|---|
| [deedy/times-of-india-scraper](https://github.com/deedy/times-of-india-scraper/blob/76c8712e1c76aa0fe16faa2de6ea969e77e246fd/src/toi_scraper.py) | 29 Oct 2015 | Dated `/YYYY/M/D/archivelist/year-Y,month-M,starttime-N.cms`; a styled archive DIV; SQLite storage | Same historical archive backend as the user's code. Different selectors/storage provide no evidence the empty archive listings are recoverable. |
| [jabhishek87/toi-scraper](https://github.com/jabhishek87/toi-scraper/blob/a53068746e0a5d4b2477b250da0cc15162097603/toi_scrapper.py) | 3 Sep 2022 | Same daily archive for IDs; **different `toifeeds.indiatimes.com` JSON endpoint** for individual article content | Useful metadata backfill route when article IDs are known. Does not supply a complete historical article inventory. |
| [shyamsundar2007/TOI-scraper](https://github.com/shyamsundar2007/TOI-scraper/blob/8f7e78c9ba364d453bae6e313854d58fcc426e21/toiScraper.py) | 1 Mar 2018 | `/entertainment/{language}/movie-reviews/` HTML and review pages | Movie ratings/notifications, not a news archive. Commit wording mentions an API, but inspected code uses HTML. |
| [shyamsundar2007/toi-scraper-go](https://github.com/shyamsundar2007/toi-scraper-go/blob/759851b1ede3a4d776760509878c14f73b37d811/toi_api/toi_api.go) | 28 Apr 2023 | Same entertainment movie-review HTML, Goquery selectors | Internal package name `toi_api` is not a distinct server API. No historical news-discovery solution. |
| [VigneshKarthikN/TOI_scraper](https://github.com/VigneshKarthikN/TOI_scraper/blob/23152af10a31870da3e9f8b25609734e14247da2/TOI_scraper.ipynb) | 14 Apr 2019 | `/topic/Alcoholics-Anonymous-India/` followed by pages 1–9, then article HTML | Genuinely different topic-discovery route, but a selected-topic sample rather than a chronological all-news archive. Current pagination requires separate validation. |

## Important validation risk

The jabhishek scraper accepts **all** archive-page anchors containing `articleshow` and assigns the loop's archive date. An empty historical listing can still contain current sidebar article links. Reusing this parser could therefore create seemingly historical observations from current promotions. A nonzero row count alone is not a successful archive repair: validate the archive-specific container and heading, article identity and actual publication date independently.

## Working individual-article JSON route

The endpoint documented in jabhishek's source is:

`https://toifeeds.indiatimes.com/treact/feeds/toi/web/show/news?path=/articleshow/{ARTICLE_ID}.cms`

Two small direct checks returned HTTP 200 JSON with an actual headline (`hl`), `story` content and explicit `seo.datePublished`. IDs 118806741 and 135245318 correspond to the already-known 2025 BSF report and 2026 two-encounters report. Both response IDs matched the requested IDs. The latter publication timestamp is **28 October 2026, 01:24 IST**, already available on 27 October in New York; preserve the timezone and distinguish publication from incident date. Exact status, identity, dates, response hashes and retrieval times are in `article_feed_checks.json`; full bodies were not saved by this check.

This is a practical alternative to article HTML for enriching **known IDs**. Availability of two articles does not validate every article, authenticate the reported police account, establish historical discovery coverage, or turn a selected URL inventory into a complete incidence denominator. Date fields such as update time and e-paper date must not silently replace publication date.
