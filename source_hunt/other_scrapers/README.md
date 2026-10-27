# Search for alternative TOI scrapers

Searched and reviewed 27 October 2026 (New York date). This audit reads primary public source code and separately tests a few endpoints. Finding code on GitHub does not establish that its selectors, pagination or data coverage currently work. Existing research counts remain frozen; these feasibility tests do not silently add observations.

## Strongest new lead: Fundus

[Fundus](https://github.com/flairNLP/fundus) has an explicit [Times of India parser](https://github.com/flairNLP/fundus/blob/master/src/fundus/publishers/ind/times_of_india.py), including a newer layout version and an April 16, 2026 [TOI-specific fix](https://github.com/flairNLP/fundus/commit/c6e5b54927fb5e3b564576af2de0039996ed39f7). Its [publisher configuration](https://github.com/flairNLP/fundus/blob/master/src/fundus/publishers/ind/__init__.py) uses today's/yesterday's news sitemaps plus top-stories and most-recent RSS. It does not depend on the failing daily archivelist endpoint.

The project's [CC-NEWS crawler](https://github.com/flairNLP/fundus/blob/master/docs/2_crawl_from_cc_news.md) can parse historical captured news through Common Crawl. This is a genuinely different acquisition source worth a bounded pilot. The date filter refers to when Common Crawl captured the page, not original publication or event date. We have not established TOI capture coverage, installed/executed Fundus, or demonstrated that this route can fill the whole 2024–2026 gap. Scanning its multi-terabyte source requires an explicit bounded design. See [Common Crawl's primary description](https://commoncrawl.org/blog/news-dataset-available).

## Live endpoint checks

Local, read-only HTTP/lxml probes confirmed:

| Endpoint | Observation |
|---|---|
| `rssfeedstopstories.cms` | HTTP 200, valid RSS with 44 items. |
| `rssfeedmostrecent.cms` | HTTP 200, valid RSS with 50 items. |
| `/home/headlines` | Redirects to `/news`; the old Das scraper's exact nested selector finds zero matches. Article links exist on the new page, including unrelated footer material; whole-page links are not a validated headline count. |
| `/topic/police-encounter/news/2` | Redirects to `/topic/police-encounter/news`; appending a page number did not preserve the tested second page. This does not test a browser's View More button. |

The two RSS feeds contain recent timestamps (including October 28 IST while the New York date is October 27). They support prospective discovery, not arbitrary historical date retrieval. Complete source counts and response URLs are in [endpoint_checks.json](endpoint_checks.json).

## Working article-JSON lead

[jabhishek87/toi-scraper](https://github.com/jabhishek87/toi-scraper) revealed a separate first-party article feed:

```text
https://toifeeds.indiatimes.com/treact/feeds/toi/web/show/news?path=/articleshow/{ARTICLE_ID}.cms
```

Two bounded locally written probes succeeded for known 2025 and 2026 article IDs: HTTP 200, JSON headline and story fields, plus explicit `seo.datePublished` and `seo.dateModified` timestamps matching the known reports. See [article_feed_checks.json](article_feed_checks.json). No raw bodies were saved. This is a confirmed metadata-extraction alternative for known IDs. It is not an archive-enumeration endpoint; that repository still discovers historical IDs through the failing legacy archive pages. The existing sitemap inventory could supply IDs, subject to coverage, rate and identity checks.

## Other repositories and interpretation

See [archive and article-feed projects](archive_repos.md) and the [five other repository audit](other_repos.md). Several archive scrapers repeat the same legacy endpoint. Other projects collect topic results, current headlines, individual known article URLs, movie reviews or advertisement images. Those are different discovery frames and must not be treated as a complete date-by-state news census.

[Debjyoti Das's TOITopHeadlines](https://github.com/dasdebjyoti/TOITopHeadlines/blob/main/toi_topheadlines.py) is another simple current-headlines implementation. We inspected its code and checked its exact selector against the current page; no old-selector matches were found. [shyamsundar2007/toi-scraper-python](https://github.com/shyamsundar2007/toi-scraper-python/blob/main/toi_scraper.py) is a movie-review and Telegram-alert program, not a general newspaper archive collector. No notification function or third-party repository code was run.

A search also found [FreeNewsApi's indiatimes catalogue](https://freenewsapi.ai/sources/indiatimes-com). Its own page pools twelve Times Group hosts, gives a recent July–October 2026 archive window and acknowledges upstream gaps. Its API was not successfully tested here. The displayed large publisher total is not a count of TOI-only articles, a complete archive, or evidence that the 2024 gap can be filled.

**Assessment:** Fundus is the most useful maintained general framework identified in this search. Its Common Crawl mode is a historical-recovery lead, not a demonstrated complete replacement. The separate article JSON feed is confirmed working on two known articles; RSS is confirmed working for current discovery. Historical daily-archive discovery remains unresolved.
