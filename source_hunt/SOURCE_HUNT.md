# Recovered original headline-page entry point

The recovered **Times of India First File.py**, line 6, explicitly targets the [Times of India archive for January 2, 2003](https://timesofindia.indiatimes.com/2003/1/2/archivelist/year-2003,month-1,starttime-37623.cms). This is the strongest local evidence for the remembered page containing old headlines. The later annual scrapers use the same archive route.

An additional **Text scraping** folder was found directly under the home folder, outside Documents. All 17 comparable source files and all seven CSV files match their **Times of India News Headlines** copies byte-for-byte. The saved daily CSV contains **141 headlines dated January 2, 2003**. None of the 23 inspected scripts, notebooks and checkpoints supplies a different TOI backend or a saved notebook output of the old headline page. The notebooks contain unrelated scraping tutorials.

On October 27, 2026, the exact first script was executed unchanged in an isolated output folder, retaining its original headers and BeautifulSoup/lxml parser. The response was HTTP 200, but its day heading and both archive columns were empty: **zero headlines**. The [unprefixed archive route](https://timesofindia.indiatimes.com/archivelist/year-2003,month-1,starttime-37623.cms) returned the identical response hash. The [archive landing page](https://timesofindia.indiatimes.com/archive.cms) still exposes year/month navigation. These observations describe the tested responses, not every possible browser or network environment.

The source-script SHA-256 is `21900893c89ad41c324105c50da601b0d15baf699364b598ae6e2f92006353a2`.

The bounded search covered relevant home-folder filenames, Documents/Desktop/Downloads, CloudStorage filenames, and Spotlight filename matches, excluding caches, installed environments and this research's outputs. It found no additional archive-named saved HTML or separate TOI scraper. Browser history was not accessed; this was not an exhaustive content search of every file.

Audit evidence: [exact script test](exact_first_file_check/result.json), [route checks](entrypoint_variant_checks/results.json), [copy hashes](copy_hash_comparisons.json), and [source references](source_entrypoints_public.json). Personal absolute paths remain in separate private inventory files and should not be published.

A follow-up [generalized-link test](generalized_link_checks/README.md) changed every date component and serial day value across eight dates, using both daily URL forms. All 16 daily requests returned empty listings. Rendered calendar links matched the date formula, and a JavaScript-enabled browser also showed an empty October 27 daily listing.
