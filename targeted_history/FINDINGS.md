# Targeted search for earlier similar TOI reports

Completed 27 October 2026, New York date. OpenAI Codex conducted this work at Aritra Basu's direction, with separate AI subagents checking retrieval, source context and calculations. This is provisional AI-assisted research, not independent human validation of police claims.

## Start here

- [Evidence table](evidence_table.csv): 41 source-linked case, context and exclusion entries, with event and publication dates separated. These are different practices and settings; 41 is not a count of one homogeneous outcome.
- [Ordinary-crime gun-taking reports](ordinary_crime_gun_reports.csv): 14 historical event examples; individual/group attribution, attempted/completed taking and timing remain explicit.
- [Searchable headline catalogue](headline_catalogue.csv): 9,733 candidate date-headlines from the local historical files. These are search hits, not incidents. Search or filter headline, category proxy and retrieval route.
- [Retrieved article index](article_index.csv): actual recovered titles, publication metadata, source links, retrieval status and review depth for 915 selected IDs. It includes six unresolved records; article-body text is not republished.

## What the search establishes

### The firearm-taking account has substantial historical precedents outside Bengal

The two national case tables identify 16 reported events from 2001–2023. Fourteen fall within the declared ordinary-crime comparison scope; Alair terror-suspect transport and the NIMHANS armed hospital standoff are separate contexts. Of the 14 ordinary-scope examples, eight report fatalities and six nonfatal shooting injuries. These are deliberately found examples, not a representative sample, an annual rate or an estimate of national rarity.

Examples include:

| Event | What the inspected reporting says |
|---|---|
| [Bengaluru, 14 December 2001](https://timesofindia.indiatimes.com/city/bengaluru/deepikas-killers-try-to-flee-shot-dead/articleshow/1164422883.cms) | Two arrested suspects were killed during an escorted stolen-jewellery recovery; police alleged one took an escort's rifle. The source does not identify which suspect personally took it. |
| [Hyderabad, 6 December 2019](https://timesofindia.indiatimes.com/city/hyderabad/police-resorted-to-retaliatory-firing-sajjanar-on-hyderabad-encounter/articleshow/72400183.cms) | Police alleged two firearms were taken during investigation/recovery at the crime scene before four rape-murder accused were killed. This is one episode with group-level attribution, not four independent firearm seizures. |
| [Kanpur, 9 July 2020](https://timesofindia.indiatimes.com/city/kanpur/gangster-vikas-dubeys-two-more-close-aides-shot-dead-in-separate-encounters/articleshow/76867811.cms) | Police alleged Prabhat Mishra took a pistol and attempted escape during transport after a vehicle puncture; he was shot dead. |
| [Kanpur, 10 July 2020](https://timesofindia.indiatimes.com/india/vikas-dubey-caught-alive-brought-dead/articleshow/76901667.cms) | Police alleged Vikas Dubey took a pistol and tried to flee after the transporting vehicle overturned; he was shot dead. |
| [Rohini, 13 July 2021](https://timesofindia.indiatimes.com/city/delhi/snatcher-grabs-cops-pistol-opens-fire-in-bid-to-flee/articleshow/84424392.cms) | Police alleged Sumit Bagga grabbed an officer's pistol during a custody escape attempt; the report says police shot him in the leg. |

The additional cached-body search found four ordinary-crime nonfatal examples beyond the web-discovered twelve: Ehtisham in Kanpur (2019), Sumit Bagga in Rohini (2021), Kamal/Kallu in Ghaziabad (2022), and an unnamed Noida rape accused (2023). The Ghaziabad report has a roughly half-hour chase, and the Noida source has an internal date inconsistency. The table preserves both limitations. A source-backed account of a gun-taking allegation does not establish that it occurred or that the shooting was lawful or unlawful.

### Bengal needs narrower context distinctions

The WB source-context audit covers 84 selected articles: all 62 linked WB-proxy encounter headlines, 18 additional strong-context matches, and four priority reports whose URLs were recovered through search. Eighty-three available bodies received full source-context reading; one remained unavailable. No strict historical state-police individual gun-taking-to-shooting example was established in this selected review. This is not evidence of no historical cases: unresolved URLs, unavailable bodies, mechanisms missing from headlines and unsearched news remain.

The review did establish older related contexts, kept in [a separate table](wb_historical_special_contexts.csv):

- Nabagram/Palsanda, 2010: a student died after roadblock firing; police described a mob rifle-taking claim and disputed the source of the fatal bullet.
- Bagula, 2011: a fatal political crowd confrontation, with official accounts referring to threatened or attempted taking and possible accidental discharge.
- Malda, 2019: a BSF fatal shooting linked to a group weapon-taking allegation; the deceased is not individually identified as the gun-taker.
- [Jalangi, 14 August 2020](https://timesofindia.indiatimes.com/articleshow/77580989.cms): a BSF official specifically alleged/inferred that Kasem was attempting to take a weapon when shot. This is an individual-attributed border-force allegation, not a state-police custodial reconstruction.

The independent web search also recovered a 2001 article describing a March 2000 Howrah crowd clash and disputed fatal police firing. Its government firearm-taking account refers to a mob, while the victim's involvement is disputed. Publication and event dates must not be collapsed.

Maoist/other insurgency encounters are explicitly separated from ordinary-crime cases. Group claims do not automatically imply insurgency: the sources above describe public-order crowds or border operations, and the Bengaluru and Hyderabad ordinary-crime cases also involve groups. The 2014 Haridevpur case is another close exclusion: the suspect allegedly took a gun and killed a homeguard, but the inspected report does not say police shot the suspect.

### Police underclothing reports also have earlier precedents

The strongest exact precedent remains [Behror, 22 September 2019](https://timesofindia.indiatimes.com/city/jaipur/rajasthan-cops-parade-13-in-underwear-in-public/articleshow/71251170.cms): police took 13 accused through a market in innerwear, and the SP explicitly described crime-scene recreation. Three follow-up articles are one episode, not three parades.

The new local body review established four broader earlier reports: Sehore 2013 (alleged stripping/torture in custody), Bhopal 2014 (a handcuffed accused taken toward court in underwear), Amritsar 2015 (an alleged private assault involving a constable on leave), and Inderpuri/Delhi 2018 (a disputed naked escort through a market). None was established as the same case-specific underclothed reconstruction practice. Nagpur 2020 and Dum Dum jail 2010 were independently reconfirmed as different contexts. A fifth additional context row concerns a 2010 Salboni media display in a reported insurgency investigation: clothing described at capture is not assumed to be clothing at the later display. It is excluded from the ordinary-crime comparison.

Among the 267 supplemental parade/clothing-route IDs, 105 available bodies received full reading, including every one of four joint underclothing/actor/reconstruction keyword candidates and the other 79 promising actor/parade signal articles. The remaining 160 have no joint lexical signal and are not validated negatives; two lack usable bodies. Thus this bounded search cannot establish Behror as the only earlier exact episode. See the [staged decisions](supplemental_parade_body_review.csv) and [codebook](event_table_codebook.md).

## Acquisition and validation

The supplemental local scan read 6,662,354 raw rows across five hash-verified canonical files. Duplicated file aliases were excluded. It added 2,377 date-headline candidates to the previous 7,356, producing 9,733 in the combined catalogue. The 6.66 million raw rows include overlap between source exports and are not 6.66 million unique stories.

The declared targeted fetch queue contained 915 unique IDs. Final validation found **909 records with usable extracted text and six unresolved records**. All successful records have matching article IDs, actual titles and timezone-aware publication dates. Independent checks reconciled all 921 recorded response hashes and byte counts. One error response appended recommendations after an ERR-RTF marker; it was reclassified as unresolved, superseding an earlier provisional 910-success total.

The three cached-body review streams contain 219 distinct fully read available articles, with overlap between streams; web-source reviews are documented separately. The remainder of the retrieved articles have explicit screening/unreviewed states. Metadata recovery and lexical screening must not be described as manual review of every body. Source content can itself be truncated or inconsistent.

The case catalogue is a discovery product. It does not identify a causal BJP effect, estimate the probability that police accounts are true, or supply an event/population denominator. The fixed recent four-state comparison remains a separately versioned exploratory analysis; purposive historical examples have not been silently added to it.

## Reproduction

Original source files remain unchanged. `scan_headlines.py` applies the versioned lexical routes to separately obtained local inputs; `build_extended_queue.py` declares the purposive fetch selection; `collect_targeted.py` stores local source responses and extraction status; `compile_catalogue.py` builds the public tables. Raw responses and full article bodies stay outside the public repository. The dated audits and source hashes describe exactly what was examined.

With the public derived inputs, `python targeted_history/compile_catalogue.py --use-existing-article-index` rebuilds the case/headline tables while retaining the published article index. Rebuilding that index from source responses requires the local acquisition cache; the flag does not pretend to revalidate unavailable raw bodies.
