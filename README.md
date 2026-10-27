# Times of India police-practices research

**OpenAI Codex is doing this work at Aritra Basu's direction.** Codex wrote the collection code, searched and audited the data, coded the reported cases, performed the quantitative analysis, and drafted this README and research note. Separate Codex subagents checked the methods, sources, and calculations. These are AI analytic checks, not independent human validation.

This is a public **work in progress**, dated 27 October 2026 (New York time). It studies reported police accounts and practices. It does not establish that an alleged gun seizure occurred, that an accused person was guilty, or that a shooting was unlawful.

## Questions

1. Do reports from West Bengal describe an accused person taking or attempting to take an officer's gun immediately before police shoot that person?
2. How unusual is the October 2026 temporal cluster under different timing models?
3. Have police paraded accused people in underwear or without clothing while describing the exercise as crime-scene reconstruction?
4. Can consistently collected evidence support a comparison of West Bengal before and after the May 9, 2026 government transition, including controls that have not had a BJP-led government?

## Current findings

- Three distinct 2026 custodial reconstruction cases are documented in reporting: Baruipur in July, and Gaighata and Samserganj on October 27. Repeated articles are not additional incidents.
- A separate March 2025 Jalpaiguri report describes a fatal **BSF** shooting following an alleged **group** attempt to seize a weapon. It does not expressly assign the attempt to the man killed. This is a broader border-force sensitivity case, not a fourth individual custodial reconstruction case.
- There are earlier underwear-parade precedents with an explicit reconstruction explanation: Behror, Rajasthan, in September 2019, and Howrah in May 2026. An older Dum Dum jail allegation is a different category of custodial humiliation.
- The original dated local headline files yield **3,930,496 distinct normalized date-headline records**, through December 2023. No full target sequence is explicit among the 52 historical WB-proxy weapon-taking headlines reviewed. This does **not** mean zero historical events; mechanisms can be absent from headlines and relevant bodies remain unresolved.
- **No causal BJP effect has been established.** Control eligibility, comparable ascertainment, government spells, pretrends, rare outcomes, and inference with one treated state require additional checks. Never BJP-led, never BJP in a cabinet, and never allied with the BJP are different definitions.

Sources, date uncertainty, exclusions, and the distinction between state police and central forces are recorded in the research note and evidence files.

## Collection status: the recent backfill is incomplete

The user's original scraper was tested with its original request headers and BeautifulSoup/lxml parsing logic on four isolated dates, including a known 2015 control. Every test returned empty archive columns and zero rows. A JavaScript-enabled browser showed the same problem.

The improved collector used public sitemaps instead:

| Output | Recovered |
|---|---:|
| Monthly sitemap partitions for 2024–2026 | 161 |
| Sitemap HTTP resources, including current feeds and child files | 165 |
| Distinct URL inventory records | 1,424,031 |
| Actual recent news-feed title records | 2,235 |
| Selected article metadata records with actual title, publication date and body | 362 |
| Combined actual-headline content items after ID/URL deduplication | 2,592 |

The combined title count comprises 2,421 items with article IDs and 171 other feed items keyed by URL. Recent feeds and selected article metadata overlap. There are 385 items published on October 28 IST while collection was still October 27 in New York; timestamps and a cutoff flag are retained locally.

**URLs are not headlines. Sitemap `lastmod` is not publication date or event date.** Historical metadata was selected for research relevance, so it is not an unbiased denominator or a complete 2024–2026 headline census. Empty archive pages are missing data, not zero-news days.

## Timing calculation

If exactly three independent event times are uniformly distributed over a fixed interval of `T` days, then:

```
P(any pair within 24 hours | N = 3, T) = 1 - ((T - 2) / T)^3
```

For `T = 112`, this gives **5.262%**. The analogous probability of any shared calendar date is **2.663%**.

These are mathematical benchmarks. The window was selected after noticing the events, completeness of the event list is not established, and independence may fail. They are **not calibrated p-values, not an empirical historical rate estimate, and not the probability that police accounts are true or false**. The note also reports Poisson and clustered-rate sensitivity calculations.

## Files

- `output/West_Bengal_Gun_Snatching_Research.pdf`: research note, including the parade precedents.
- `analyze.py`: deterministic historical retrieval and source audit.
- `probability.py`: timing and rate-sensitivity calculations.
- `scraping/collect_archives.py`: resumable daily-archive collector with validation and failure logs.
- `scraping/collect_sitemaps.py`: public sitemap inventory and actual article-metadata collector.
- `scraping/combine_actual_headlines.py`: combines actual titles; it never converts URL slugs into headlines.
- `events.json`, `broader_security_force_cases.json`, and `body_review.json`: case definitions, sources, uncertainty, and exclusions.
- `parade_audit/`: sourced precedent coding.
- `data/`: source hashes, derived coverage tables and calculation inputs.
- `methods_audit/`: selected AI screening and validation summaries.

Full downloaded article bodies, raw HTML, large headline corpora, URL inventories, and machine-specific diagnostics are kept out of this repository. The collection scripts generate them locally.

## Reproduction

Use Python 3.10 or later in an isolated environment:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python probability.py
python make_report.py
```

To audit a separately obtained copy of the original source files:

```sh
python analyze.py --source /path/to/Times_of_India_News_Headlines
```

To collect public sitemap data and selected article metadata:

```sh
python scraping/collect_sitemaps.py --metadata --resume
python scraping/combine_actual_headlines.py
```

The repository also provides a manually triggered **Public TOI collection** GitHub Actions workflow. Its default is a small archive pilot. A separate mode collects sitemap inventory and selected metadata. Downloadable run artifacts contain data and audit summaries; raw article HTML and full bodies are excluded. There is no recurring schedule.

Inspect manifests and coverage limits before using any generated data. The collector limits request rates, records source responses, and stops on access-denial responses. A successful HTTP response is not by itself successful data collection.

## Interpretation and causal analysis

Fatal and nonfatal shootings, individual and group weapon-taking claims, state police and BSF incidents, street parades and jail allegations, and underwear and full nudity are coded separately. Unknown mechanisms and event dates are retained as unknowns.

A party comparison requires government status on the incident date and identical retrieval, body review, and event deduplication across states. A before/after difference in selected news records is not automatically a causal effect. The work will report descriptive evidence and identification limits rather than turn missing records into zero outcomes.
