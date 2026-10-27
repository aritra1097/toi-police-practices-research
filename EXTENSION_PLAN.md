# Plan to extend the TOI corpus and research panel

Prepared 27 October 2026, New York time. This is a plan; no new bulk crawl or recurring automation has been started.

## Objective and starting point

Extend the original headline corpus from 1 January 2024 onward, preserving the older files and their provenance. Use the latest completed day in Asia/Kolkata for the main release; retain the current IST day separately as provisional. For a release prepared now, the main endpoint is 27 October 2026 IST. Event dates remain separate from publication dates.

There are two deliverables: (1) a general headline/metadata extension, and (2) a more deeply reviewed police-practices event panel. Targeted police articles must not become the denominator for the general corpus.

Existing work provides approximately 1.424 million listed URLs, 1,269 distinct article-metadata records, a partial combined title supplement, and 1,132 available article bodies in the four-state review cohort. These assets will be reused. The URL inventory is a discovery frame, not proof of complete TOI coverage. Historical sitemap partitions can contain older articles modified later, while articles missing from the inventory remain unknown.

## 1. Validate the new JSON route with a bounded pilot

Use the first-party feed discovered in another scraper:

```text
https://toifeeds.indiatimes.com/treact/feeds/toi/web/show/news?path=/articleshow/{ARTICLE_ID}.cms
```

Draw 500 unique uncached IDs from the saved inventory, stratified across sitemap months and regional desks, with a fixed seed and recorded inclusion probabilities. These are discovery strata, not verified publication months or event states. Keep known police examples as separate positive controls, excluded from representative pilot success-rate estimates. Two existing successful article tests are feasibility evidence, not enough to launch an unmeasured bulk job.

For every response, validate the requested versus returned article ID, actual headline, canonical identity where available, original publication timestamp and its timezone, modified timestamp and status. Cross-check a random 50 pilot records against the corresponding article HTML/JSON-LD. Flag disagreements for review; never select a convenient timestamp silently. Retain exact title variants and distinguish title revisions from separate articles.

The pilot report must give success and failure fractions with denominators, results by stratum, latency, response/compressed bytes, and agreement with HTML. Its weighted success estimates describe the uncached queue sampled, not all TOI publications. Inspect substantive text and recommendation contamination on the cross-check sample too. Missing fields and deleted pages remain missing. A successful HTTP response alone does not count as recovered metadata. Before scaling, resolve systematic identity/date errors and measure expected runtime and disk requirements.

## 2. Build the general metadata backfill

Create a durable per-ID queue with pending, validated-success, known-unavailable, retry-needed and unresolved states. Cache by validated article ID; retain discovery URLs as a many-to-one table. Reuse existing successful records with their extraction version and source provenance. Keep feed items without article IDs in a separate URL-keyed stream.

Process all remaining listed news-article IDs through the JSON route; use article HTML as a recorded fallback when appropriate. Do not prioritize only politically relevant words for this general backfill. Interleave the queue across discovery months and desks so an interrupted run is not solely a latest-month or single-region slice. Publicly report which strata are unfinished; interleaving does not make unfinished data complete or representative automatically.

Record response status, retrieval time, response hash, metadata source, extraction version and date/identity validation for each attempt. Use compressed storage, atomic writes, checkpoints and bounded retries. Honor server retry instructions and halt on persistent access-denial responses. Changing a parser should not require downloading already cached responses again.

Deliver a deduplicated actual-headline table and an attempt/coverage manifest. Preserve publication, modification, sitemap listing, archive capture and retrieval times in distinct columns. Never convert URL slugs into headlines or sitemap modification dates into publication dates. Publication filtering happens only after actual metadata is recovered.

## 3. Pilot an independent historical recovery source

Evaluate [Fundus's TOI parser](https://github.com/flairNLP/fundus/blob/master/src/fundus/publishers/ind/times_of_india.py) and its [CC-NEWS support](https://github.com/flairNLP/fundus/blob/master/docs/2_crawl_from_cc_news.md). Pin the tested version and compare its extracted title/date/body against the existing method on cached articles first.

Use a bounded historical capture pilot across early, middle and recent portions of 2024–2026. Proposed first-run limits are one worker, 30 minutes or 2 GB transferred, whichever is reached first; enforce and record these limits before scanning. `max_articles` alone may not bound how much archive data must be searched. Do not launch the default multi-terabyte/all-CPU crawl. Measure TOI yield, recovered IDs absent from our sitemap inventory, unavailable known IDs and extraction disagreements. Reaching a cap without finding TOI articles is inconclusive about wider coverage. A capture-date window is not a publication-date window; allow and document capture lag.

Scale only if the pilot produces useful additional coverage at reasonable measured cost. Maintain capture provenance, deduplicate with the main corpus by ID, and preserve source-specific missingness. Use Wayback and topic search for targeted gap-finding and case verification; successful examples from either cannot certify a complete daily series. The already timed-out broad Wayback query is unresolved, not a negative census.

## 4. Validate the text-as-data research layer

Apply the same explicitly versioned retrieval and coding definitions across West Bengal and comparator states and across time. Re-run the existing case pipeline against the expanded actual-headline table. Search bodies for mechanism details absent from headlines, while distinguishing suspect gun-taking from earlier possession, private weapons, group attempts, central forces and retrospective background accounts.

Review a probability sample outside the candidate set, stratified across states and pre/post periods. Record known inclusion probabilities and separately audit URL/headline-stage and body-stage misses. Do not estimate overall recall from a convenience sample or only from already-retrieved positive signals. An audit inside the listed corpus cannot quantify all unlisted news or unreported incidents.

Keep article-to-event links, inferred date intervals, duplicate-event decisions and unresolved coding explicit. Treat sparse parade clothing descriptions as unknown, not proof of nudity or of ordinary clothing. Seek independent human adjudication of a defined validation sample before strong substantive conclusions; AI/subagent agreement remains an AI diagnostic. Without human review, publish labels as provisional AI source-context coding.

For the long historical comparison, expand body checks of older candidate articles too. The pre-2024 headline search cannot be interpreted as a validated historical zero while newer evidence receives much deeper body review.

## 5. Reassess comparisons and release versioned results

Publish state-month acquisition and review diagnostics: discovered IDs, recovered metadata, unknown publication dates, body availability, candidates, reviewed cases and unresolved decisions. Report both state-assignment uncertainty and URL-stage coverage limits. Even a fully processed inventory supports a listed-frame measure, not a census of real police incidents.

Retain Kerala and Tamil Nadu as non-BJP-led controls despite their May 2026 turnovers. Keep government turnover, BJP chief-minister status, cabinet participation and central-force command separate. Use the dated political ledger before adding other never-BJP-led candidate states; do not choose donors because their post-period outcomes favor a conclusion.

Refresh descriptive counts and the synthetic comparison only with identically defined measures, transparent unknown cells and the documented pre/post windows. More headlines cannot by themselves identify a BJP effect. If WB's pre-period remains flat, continue reporting weight ambiguity. A broader police-shooting outcome or a share of reported shootings with gun-taking claims requires complete, comparable coding of that broader denominator first; it is not risk per suspect or reconstruction.

Release code, provenance, small derived tables, coverage diagnostics, source links and analysis snapshots on GitHub. Keep raw article bodies and large response inventories in local research storage. Preserve the current results as a dated version rather than overwriting them. Use GitHub Actions for tests and bounded reproducibility jobs; start no recurring schedule without a separate request.

## Resources and sequence

The first execution milestone is the 500-ID pilot and its measurement report, followed by a refined capacity estimate. At 1–2 request starts per second, 1.4 million single requests imply roughly 8–17 days of continuous request budget before retries or other overhead. The present collector's 0.56-second spacing alone implies about nine days; actual throughput can be lower. These are arithmetic lower bounds, not a promised completion date or authorization to increase request rates.

Prefer a resumable local backfill initially, since the large inventory is already local. Estimate compressed storage from the representative pilot before retaining all raw JSON responses. A 60-minute cloud job without persistent queue/cache transfer is not an effective replacement for a multi-day backfill. Maintain a manual incremental command for new RSS/sitemap entries while bulk work is unfinished.

Work order: JSON/HTML pilot → measured queue/storage implementation → broad metadata backfill, with the bounded Common Crawl pilot in parallel → expanded, symmetrically audited case coding → versioned descriptive analysis and release. The main completion claim should be **all eligible IDs in the declared discovery frame processed, with explicit unresolved cases**. Claiming a complete TOI publication census would require independent evidence of discovery coverage that we do not currently possess.
