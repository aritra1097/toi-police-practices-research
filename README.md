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
- In a separate, symmetrically selected 2024–2026 four-state cohort, all **1,132 articles** yielded actual titles, dated metadata and available bodies. AI source-context review identified the counts below. These are detected cases within an incomplete news-retrieval process, not population event totals.
- **No causal BJP effect has been established.** Never BJP-led, never BJP in a cabinet, and never allied with the BJP are different definitions. Kerala and Tamil Nadu remain in the primary non-BJP-led pool despite their May 2026 government turnovers; Telangana supplies a third comparator.

Sources, date uncertainty, exclusions, and the distinction between state police and central forces are recorded in the research note and evidence files.

## Collection status: the recent backfill is incomplete

The user's original scraper was tested with its original request headers and BeautifulSoup/lxml parsing logic on four isolated dates, including a known 2015 control. Every test returned empty archive columns and zero rows. A JavaScript-enabled browser showed the same problem. A wider computer search then recovered another `Text scraping` folder and the exact first-script URL for [2 January 2003](https://timesofindia.indiatimes.com/2003/1/2/archivelist/year-2003,month-1,starttime-37623.cms). Executing that first script unchanged also returned two empty archive columns and zero headlines. See `source_hunt/` for the separate diagnostic; these tests do not establish that every TOI archive entry point fails.

The improved collector used public sitemaps instead:

| Output | Recovered |
|---|---:|
| Monthly sitemap partitions for 2024–2026 | 161 |
| Sitemap HTTP resources, including current feeds and child files | 165 |
| Distinct URL inventory records | 1,424,031 |
| Actual recent news-feed title records | 2,235 |
| Distinct selected article metadata records, initial collection plus four-state cohort | 1,269 |
| Combined actual-headline content items after ID/URL deduplication | 3,493 |

The combined title count comprises 3,322 items with article IDs and 171 other feed items keyed by URL. Recent feeds and selected article metadata overlap. There are 3,108 items within the January 2024–October 27, 2026 IST window and 385 published on October 28 IST while collection was still October 27 in New York; timestamps and cutoff flags are retained locally. The four-state cohort contributes 907 metadata records beyond the initial 362; 225 are reused.

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

The [first cloud archive pilot](https://github.com/aritra1097/toi-police-practices-research/actions/runs/40586045573) completed on October 27, 2026 and returned **zero validated rows on all three dates**, reproducing the local endpoint failure. A green workflow status means the diagnostic ran; it does not mean headline coverage was recovered.

Inspect manifests and coverage limits before using any generated data. The collector limits request rates, records source responses, and stops on access-denial responses. A successful HTTP response is not by itself successful data collection.

## Interpretation and causal analysis

Fatal and nonfatal shootings, individual and group weapon-taking claims, state police and BSF incidents, street parades and jail allegations, and underwear and full nudity are coded separately. Unknown mechanisms and event dates are retained as unknowns.

A party comparison requires government status on the incident date and identical retrieval, body review, and event deduplication across states. A before/after difference in selected news records is not automatically a causal effect. The work will report descriptive evidence and identification limits rather than turn missing records into zero outcomes.

## Exploratory four-state results

The main outcome includes attempted or completed taking of an officer's firearm immediately followed by police shooting of that individual. All four identified cases were fatal; no additional qualifying nonfatal case was identified. Group attempts and BSF incidents are separate. Events are deduplicated across articles and assigned incident dates, not sitemap dates.

| State | Jan 2024–Apr 2026 (851 days) | Jun 1–Oct 27, 2026 (149 days) |
|---|---:|---:|
| West Bengal | 0 | 3 |
| Kerala | 0 | 0 |
| Tamil Nadu | 0 | 0 |
| Telangana | 1 | 0 |

**Every zero means no qualifying positive identified by this pipeline. It does not mean no real incident occurred.** All 245 expanded lexical-signal articles received AI source-context review; further synonym checks and a separate stratified random audit of 48 low-signal bodies found no visible missed narrow target case. One sampled source was truncated. These checks are not human validation or a recall estimate. Publication selection, URL-language retrieval and body availability can vary by place and period. The older headline study cannot establish historical absence because mechanism details may appear only in bodies.

The synthetic comparison fits nonnegative donor weights using January 2024–April 2026 only, excludes the May transition month, and displays the complete range of predictions across weights compatible with the chosen pre-fit rule. The central gun-outcome weights are approximately half Kerala and half Tamil Nadu. **The weights are nonunique:** all-zero pretreatment Bengal counts supply little information for learning a counterfactual. All three controls have zero detected post-period cases, so every compatible combination also predicts zero. The descriptive post-period gap is therefore **3 detected cases, or 0.604 per 30 days**. This is largely a case-count contrast, not a validated counterfactual or an estimated causal BJP effect. The compatible-weight range is not a confidence interval and does not include uncertainty about undiscovered cases.

For police public parades in the same post-period, the ledger distinguishes **4 broadly defined episodes**, **3 explicitly linked to reconstruction**, and **1 both explicitly linked to reconstruction and described as shirtless**. Including May 9 onward adds one broad episode (5 total). Clothing unspecified, ordinary clothing, underwear and nudity remain separate. The externally verified Howrah May 2026 precedent is not automatically part of this fixed TOI retrieval cohort.

The political audit identifies nine candidate states that have never had a BJP chief minister, while flagging coalition and historical uncertainties separately. The implemented three-donor comparison is a feasibility subset of that universe. It is not an all-India comparison. The secondary broad fatal-encounter outcome was not completely coded and is not modeled as if it were complete.

See `causal_audit/report/` for the readable comparison note, `causal_audit/event_coding/` for article-to-event decisions, `causal_audit/analysis/` for panels, provenance and actual outputs, and `causal_audit/scm_methods/METHOD.md` for the mathematics and limitations. Run the model from the published derived panel:

```sh
python causal_audit/scm_methods/scm_reported_events.py \
  --input causal_audit/analysis/detected_case_panel.csv \
  --output /tmp/toi-synthetic-comparison \
  --outcome gun_taking_police_shooting --donors KL TN TG --pre-slack 0
```

Rebuilding source-context decisions requires collecting the underlying articles and reviewing them again; full bodies are not republished. `build_detected_case_panel.py` intentionally requires that local acquisition and completed-review evidence. The published derived panel supports reproducing the descriptive calculations directly.
