# Other public TOI scrapers: source-code audit

Inspected 27 October2026 using the GitHub connector, on each repository's `main` branch. This is a static review of primary source code, not execution or a claim that old CSS selectors still work. No repository code was run and no embedded cookie was replayed.

**Finding:** None of the five repositories supplies a verified, complete historical TOI headline backfill. Two contain useful topic-result discovery patterns; two only process current headlines or supplied article URLs; the last exposes an e-paper advertisement-image workflow rather than its README's advertised TOI archive class.

| Repository / primary file | Endpoint and method actually implemented | Historical reach and usefulness |
|---|---|---|
| [Vedant-Baldwa, Scraping.py](https://github.com/Vedant-Baldwa/Times-of-India-Headlines-scraping/blob/main/Scraping.py) | Requests `https://timesofindia.indiatimes.com/home/headlines`; parses `div.headlines-list > ul.clearfix > li` into headline/link CSV. | **Current snapshot only.** No calendar, date parameter, pagination or historical traversal. Useful for prospective collection if the page structure is revalidated. |
| [AtishayJain71, 4.py](https://github.com/AtishayJain71/Time-of-India-Article-Scraper/blob/main/4.py) | Requests an explicit list of three `/articleshow/{id}.cms` URLs; extracts `h1`, byline class `_3Mkg- byline`, and body class `_s30J clearfix`. | **Article enrichment, not URL discovery.** Can in principle read historical articles whose URLs are already known, but has no historical listing/backfill mechanism. |
| [fedemoss, times_of_india.py](https://github.com/fedemoss/times_of_india-scraper/blob/main/times_of_india.py) | Selenium opens `https://timesofindia.indiatimes.com/topic/{topic}/news`; reads total from `#Articles`, repeatedly clicks a View More selector `._3BnB0`, extracts result links/titles/date strings, then follows articles. | **Topic-limited retrospective lead.** Intended to load older result pages, not a date-complete archive. Current availability, result limits, ranking and selectors require independent testing. |
| [priti0802, NEWS.py](https://github.com/priti0802/TIMES_OF_INDIA_SCRAPER/blob/main/NEWS.py) | Starts at `https://timesofindia.indiatimes.com/topic/Sanitizer/news/`; requests numbered suffixes 1 through 20; extracts `span.title`, `span.meta`, `.content a` and article container `._3WlLe`. | **Limited topic pagination.** Potentially older topic stories, capped at 20 pages by code. No arbitrary date-range archive or complete-state coverage. |
| [harsha20032020, TOI img_to_ocr.py](https://github.com/harsha20032020/Code_and_Data_for_Analyzing_Patterns_and_Influence_of_Advertising_in_Print_Newspaper/blob/main/metadata_and_scrapers/toi/scraper/img_to_ocr.py) | Reads existing story IDs from a local CSV's `ad_column`, constructs dated advertisement JPG URLs on `asset.harnscloud.com`, downloads them, and applies PaddleOCR. | **E-paper advertisement images given known IDs.** No web-headline archive traversal. Date components in image paths do not establish an enumerable archive. |

## Material implementation issues

**Vedant:** the URL is fixed to the current headline page. It blindly prepends the TOI origin to every link; any absolute URLs need separate handling. There is no HTTP-status, empty-result or date validation in the script. A zero-row extraction would not prove no news existed. The [README explicitly describes latest headlines](https://github.com/Vedant-Baldwa/Times-of-India-Headlines-scraping/blob/main/README.md).

**Atishay:** [1.py](https://github.com/AtishayJain71/Time-of-India-Article-Scraper/blob/main/1.py) is a generic example with `example.com/news-article`, not a historical scraper. The [2.ipynb saved output](https://github.com/AtishayJain71/Time-of-India-Article-Scraper/blob/main/2.ipynb) recovers a TOI title but explicitly records date/content as not found. The improved 4.py still uses brittle DOM selectors and does not distinguish an updated byline from original publication metadata. Its functions can inspire per-URL extraction, not solve missing URL coverage.

**fedemoss:** helper functions refer to `driver`, `time`, `BS` and `pd` as globals, while the main function creates/imports them locally; as a standalone module the shown implementation has unresolved scope errors. `topic.replace(' ','-')` is not assigned, and the integer floor in `(total-20)/15` can omit a final partial page. Selenium APIs and CSS classes also need updating. Thus the endpoint pattern is the useful discovery lead; the code is not a ready-to-run reliable collector. No browser/IP rotation advice in that repository was adopted.

**priti:** the publication-date comprehension reads `soup.select('span.meta')[0]` for **every** result, so it repeats the first result's date across the page. Its printed oldest date would therefore be unreliable even if requests and selectors succeeded. Fixed 20-page traversal and broad exception handling can also silently truncate retrieval. Dates and bodies would need re-extraction from identified article metadata.

**harsha:** the [README](https://github.com/harsha20032020/Code_and_Data_for_Analyzing_Patterns_and_Influence_of_Advertising_in_Print_Newspaper/blob/main/README.md) advertises `TOIScraper().scrape_archive(year=2022, month=1)`. However, the [published TOI directory](https://github.com/harsha20032020/Code_and_Data_for_Analyzing_Patterns_and_Influence_of_Advertising_in_Print_Newspaper/tree/main/metadata_and_scrapers/toi) contains a scraper subdirectory with only `img_to_ocr.py`; the advertised class/method is absent from the inspected code. Its implemented image template is:

```
https://asset.harnscloud.com/PublicationData/TOI/{edition}/{year}/{month}/{day}/Advertisement/{page}/{story_id}.jpg
```

Story IDs are parsed from `DD_MM_YYYY_PAGE_PART_EDITION`-style strings and must already exist in a local CSV. The code embeds an old short-lived challenge cookie and uses e-paper request headers; neither was reused. This is a distinct print/advertisement data source, with separate access, edition and OCR questions, not an equivalent source of TOI online news headlines.

## Practical alternative lead

The strongest new public-web lead from these repositories is **topic-result discovery**, using `/topic/{topic}/news` and any publicly exposed pagination/View More responses. Test the current site independently on bounded topics, preserve each returned article ID, and enrich original publication dates/headlines from the article itself. Topics such as the place, police unit and suspect's name may recover reports outside URL-slug screens. Do not treat the result count, a 20-page cap or the oldest visible date as archive completeness.

None of these repositories supplies a new working date-enumerable endpoint that repairs the failed legacy `/archivelist` responses. Topic search can complement the existing sitemap inventory; it cannot turn the current detected-case panel into an incidence census. A successful endpoint test must be recorded separately before calling this lead currently working.

## Observed primary source blobs

These Git blob hashes identify the bytes inspected (no project code was copied into the research pipeline):

| File | Git blob SHA |
|---|---|
| Vedant `Scraping.py` | `6df108a75499edbf3c72a3dee9da20ca026fdf69` |
| Atishay `4.py` | `167d0174babf90b95e829fdae0039dbc636b31df` |
| Atishay `1.py` | `5758981e8903495424319151dcb53d1f6e5e8060` |
| Atishay `2.ipynb` | `1d635816877fd0132704d0a1771929bd096aff8e` |
| fedemoss `times_of_india.py` | `c67d54222b54fe3691ada88c1c6f7349c047aa8b` |
| priti `NEWS.py` | `9135a0d8f22b059265333dea719809eaf0a94717` |
| harsha `img_to_ocr.py` | `3a2d89ce9eb39ab1c312f3039f66c358e3569872` |
