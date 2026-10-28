# Codebook: targeted historical police-practice reports

Applies to `parade_and_wb_context_events.csv` and the source-linked leads in `independent_web_leads.json` / `.md`. Version: 27 October 2026. Prepared with AI source-context review; independent human verification is outstanding.

## Unit, scope and interpretation

The table contains 12 deduplicated case/episode leads selected through a bounded web search, not a random sample or an event census. It covers eight parade-related examples across India and four Bengal gun-taking/shooting context cases. Eight rows precede 2024. Every row has a source-backed judgement; there are no unreviewed candidates silently coded as negatives. Source text is paraphrased rather than reproduced.

**A confirmed report is not confirmed actual truth.** `source_report_status` describes what the inspected reporting supports. It does not independently establish that the alleged conduct occurred, that an officer's justification was true, or that a court found an act lawful or unlawful. `actual_truth_or_legality_established=no` means this review has not established those matters; it does not mean the source claim is false.

This targeted historical table is separate from the fixed 1,132-article comparative pipeline. Adding selected examples to one period or state changes the measurement frame. Do not combine the resulting counts with the old panel and call the total a comparable incidence series.

## Exact versus similar cases

An **exact reported underclothed public police reconstruction parade** requires all of:

1. Police as the actor conducting the movement of accused persons.
2. Movement through a public street or market.
3. Explicit reporting of underwear, partial undress or nakedness.
4. An explicit case-specific police explanation invoking crime reconstruction, recreation, or scene/spot verification.

The 2019 Behror event meets all four conditions. Its thirteen accused constitute one episode, not thirteen independent observations. The table includes three source articles about that single episode.

Similar or broader rows fail or leave unknown one or more conditions. Important distinctions:

- Nagpur 2020: underwear police parade, but the reported explanation was investigation plus a flat tyre; reconstruction remains unknown.
- Dum Dum 2010: alleged naked prison parade by jail personnel; not a public-street reconstruction.
- Kardhani 2022, Pragpura 2024 and Chittorgarh 2026: case-specific spot verification is explicit; clothing remains unknown.
- Gudhagorji January 2025: underwear parade appears in a later report, but exact date, identities and case-specific reconstruction remain unresolved. A generic paragraph listing several police rationales cannot be transferred to that particular episode.
- Merta 2025: salwar suits are clothing, not evidence of nakedness or underwear. The source's general remarks about physical verification do not establish reconstruction for this event.

The broader Bengal gun cases are likewise separate from an individual accused in state-police custody taking an officer gun and then being shot during reconstruction. Crowd claims, central-force cases, a suspect shooting an officer, and ambiguous death/episode linkage must remain separate categories.

## Column definitions

| Column | Definition and allowed interpretation |
|---|---|
| `event_id` | Stable working episode identifier; a search aid, not proof of exact date or unique real event. |
| `event_date_display` | Reported/inferred Indian local date, month, or interval. Never substitute publication date automatically. |
| `event_date_start_ist`, `event_date_end_ist` | Bounds on the reported/inferred date. For a month-only date these are calendar bounds, not observed start/end times. |
| `date_precision` | `day`, `month`, `two_day_interval`, or another explicitly bounded multi-day interval (e.g. `three_day_interval` in the supplement). A precise-looking ISO date can still be inferred; read `date_basis`. |
| `date_basis` | Explicit date, weekday-to-calendar inference, retrospective month, or other qualification. |
| `state_actual`, `locality` | Event geography from the report, not the article's dateline, URL section, suspect's origin or gang's operating area. |
| `subjects` | Publicly reported identities/descriptions and available group size. Does not imply guilt. |
| `event_type`, `comparison_class` | Separates the practice/episode and why it is exact, similar, broad, negative-mechanism comparison or unresolved. These are not interchangeable outcome categories. |
| `context_category`, `context_evidence_paraphrase` | Source-based event setting: ordinary criminal investigation, prison discipline, domestic-violence response, Holi crowd clash, international border or election polling. Group size alone never determines insurgency. |
| `insurgency_context_reported` | `not_identified_in_reviewed_reporting` for these 12 rows. This is a source-description label, not proof of the absence of any undisclosed connection. Maoist or other insurgency operations require a separately reported category and must be excluded from the main ordinary-criminal-custody comparison. |
| `reported_actor`, `actor_force_class` | Distinguishes state police, state prison personnel, central BSF, central CISF and other actors. An event in Bengal does not automatically fall under Bengal state-police control. |
| `public_street_parade_reported` | `yes` for an explicit police street/market procession; `no` means the described row is another episode type, not proof no procession ever occurred. |
| `case_specific_reconstruction_reported` | `yes`: explicit case-specific reconstruction/scene/spot-verification claim. `no`: the inspected episode is described as another type of action, e.g. prison punishment or crowd-control firing. `unknown`: not stated specifically, generic investigation only, or only a general explanation about multiple parades. |
| `underclothed_or_naked_reported` | `yes`: explicit underwear, semi-naked or naked report. `no`: the reported clothing is a different described form, currently the Merta salwar-suit case. `unknown`: clothing is not described or not relevantly specified. Unknown is never a claim that clothes were ordinary. |
| `clothing_description` | Preserves whether the source says innerwear, naked, other attire, bare feet, shaved head or no clothing detail. Bare feet or tonsuring alone do not establish nakedness. |
| `gun_taking_claim_scope` | `individual`: one identified accused allegedly took an officer firearm. `group`: a crowd/group allegedly attempted it; do not attribute it personally to each person killed. `none`: no immediate officer-firearm-taking claim is used for this row's episode; not independently verified absence. |
| `gun_taking_claim_stage` | Attempted/completed reported claim, or not applicable. It preserves allegation status. |
| `gun_taking_personally_attributed_to_fatal_victim` | `unknown` for the group cases; no inference that every fatal victim attempted to take a gun. Other rows are not applicable. |
| `reported_shooting_outcome` | Distinguishes police killing a person, suspect killing an officer, central-force deaths, and unresolved linkage. Four Sitalkuchi CISF deaths are distinct from five total poll-violence deaths. |
| `reported_event_count` | `1` for the focal reported episode. `unresolved` for the 2011 combined multi-attack BSF report: its two reported deaths cannot yet be joined confidently to one gun-taking episode. Do not sum all rows as one homogeneous outcome. |
| `evidence_paraphrase` | Original short summary of the relevant report, not article text or a legal conclusion. |
| `uncertainties_and_exclusions` | Limits, actor/group attribution, date issues, reported counter-accounts and reasons not to use the row for an exact comparison. |
| `source_article_ids`, `source_publication_dates`, `source_urls` | Semicolon-separated parallel lists in the same order; one event can have several sources and one source can describe several events. |
| `source_report_status`, `review_method` | Textual source-review status and AI assistance disclosure. |
| `source_access_date`, `sampling_frame` | Retrieval date and the targeted-discovery scope. A search date does not date an event. |
| `actual_truth_or_legality_established` | Always `no` for this research table; see the interpretation above. |

## Deduplication and unresolved episodes

Behror articles 71251170, 71266900 and 71284810 refer to one September 22, 2019 parade. Sitalkuchi articles 82005813 and 82010497 refer to the same focal April 10, 2021 fatal-firing episode. Article 123081647 describes both an August 2025 Merta parade and a January 2025 Gudhagorji parade; those are distinct working episodes, not duplicate records simply because they share a URL.

The 2011 BSF article describes several attacks and then reports two deaths without unambiguous case-to-death linkage. Its row remains an unresolved combined-episode context record; it is not a confirmed two-death gun-taking event. The 2000 Howrah report attributes a firearm-taking allegation to a mob while disputing whether the man killed belonged to it. The 2014 Haridevpur report says an accused took a gun, killed a homeguard and was restrained/arrested; it does not report police shooting the accused.

Retain uncertainty until a source resolves it. An empty search result, absent keyword, inaccessible body or missing detail must not become a real-world negative. A later clarification should be appended with its source and date rather than erasing the earlier report's uncertainty.

## Shareability

The CSV contains bibliographic links, public report identities and original research paraphrases. It contains no source article bodies, private acquisition data, credentials or copied article quotations. It can be shared with the codebook; readers should retain the uncertainty and AI-review disclosures. The table itself does not convey reuse rights to the linked publishers' articles or images.

## Group claims do not imply insurgency

The three group firearm-taking claims in this table have different reported settings: Howrah 2000 is a Holi clash with police arrests and crowd resistance; Cooch Behar 2011 is a BSF international-border confrontation; Sitalkuchi 2021 is election polling-site crowd control by CISF. None is described as a Maoist/insurgency operation in the inspected reporting. Re-reading the canonical 2001 Howrah article confirms a clash between two groups during Holi, not a jute-mill worker protest. Preserve those categories and keep all three separate from an individual accused in ordinary criminal custody.

## Supplemental body-review stages: final completed source-reading pass

The historical supplement selected 267 article IDs on the clothing/police or literal nonceremonial actor/parade routes. Acquisition is complete for all 267. The staged per-article file `supplemental_parade_body_review.csv` now records:

- 105 complete available bodies read, including all 79 formerly unreviewed underclothing/actor/parade signals and all joint reconstruction candidates.
- 160 records with only deterministic no-joint-signal triage; these are not manually validated negatives.
- Two unavailable/error bodies that remain unknown: 6553224 (Kashmir video followup) and 4039842 (Republic Day parade theft headline).
- Zero unread actor/parade signal articles within the declared 267-route queue. This does not claim full human review of every source or known keyword recall.

The final 79 promising-body reads were partitioned without overlap: 27 IDs in partition 1, 26 in partition 2 and 26 in partition 3. Each completed JSON exactly matches its assigned ID list and marks a full available-body read. Decisions were merged with the original 26 full-body reviews and one unavailable-body source-followup flag, giving 105 full-body reviews and 106 manual decisions in total. `parade_final_partition_merge_manifest.json` records assignment counts and hashes of the three decision files. These are parallel AI source-reading passes, not independent human verification.

The actor vocabulary includes police, cops, constables, inspectors, jail and wardens. Underclothing variants include underwear, innerwear, underpants, undergarments, naked, nude, shirtless, semi/half-clad, bare-bodied/chested, stripping, without clothes and chaddi/kachch. Reconstruction variants include reconstruction, recreation, reenactment, spot/scene/physical verification and moka/mauka. Signals prioritise reading; they do not establish actors, event identity or recall. Full readings checked source-context rationales even when literal reconstruction terms were absent.

The four joint keyword candidates consisted of two articles about the same known Behror 2019 event, an artistic reenactment using moral police terminology, and a Jadavpur ragging account with a separate police dummy reconstruction. A planned reconstruction/test-identification story did not establish an implemented underwear street parade. The completed additional 79 reads found no further exact underclothed public police reconstruction case.

`supplemental_parade_events.csv` has exactly the same 35 columns as the original public table. It contains four newly recorded ordinary/private broader episodes: Sehore 2013 alleged police naked custodial abuse, Bhopal 2014 underwear court transport, Chinkot/Amritsar 2015 alleged private attack involving a constable on leave, and Inderpuri/Delhi 2018 disputed naked arrest escort. None has an explicit public underclothed crime-reconstruction rationale. The Delhi report retains opposing family/police accounts. Sehore is dated to a July 23-25 detention interval, not a precise parade time.

A fifth new context row concerns Salboni 2010: joint forces captured a youth alleged by police to be Maoist, while relatives disputed involvement and supplied disability records. The report describes bare torso/shorts at capture and later police presentation before TV; it does not establish that clothing during the media display. It is not a street reconstruction case and is explicitly excluded from the main ordinary-criminal-custody comparison. Reported insurgency context is not a finding that the individual actually belonged to an insurgent group.

Known Behror, Dum Dum and Nagpur source joins remain separately in `supplemental_parade_case_events.csv` and must not be counted as new episodes. This file contains eight mixed context rows:five new plus three known, reconfirmed episodes. Multiple reports are collapsed by event ID. The broader web catalogue can contain additional corroborating sources.

No new exact case beyond known Behror 2019 was established by the reviewed bodies. This is neither historical absence nor a measured-recall claim. The 160 low-signal records and two unavailable bodies retain their explicit limitations; selected web examples are not interchangeable with a complete population incidence panel.
