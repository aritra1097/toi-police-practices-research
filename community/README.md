# Contribute to the public case CSV

[View the CSV](cases.csv) · [Download raw CSV](https://raw.githubusercontent.com/aritra1097/toi-police-practices-research/main/community/cases.csv) · [Suggest a case](https://github.com/aritra1097/toi-police-practices-research/issues/new?template=new_case.yml) · [Correct an entry](https://github.com/aritra1097/toi-police-practices-research/issues/new?template=correction.yml)

Anyone with a GitHub account can propose additions or corrections using these forms, or edit the CSV in a fork and open a pull request. A maintainer reviews submissions before merging them. Public access does not grant anonymous write access to the main file.

The starting CSV contains **41 historical case/context entries**, including near matches and exclusions. They cover several distinct practices, and must not be counted as 41 comparable police shootings. This is a living community edition; the original [government-annotated research snapshot](../targeted_history/governments/evidence_with_governments.csv) remains separate. The snapshot generator does not overwrite this file.

## Where did these entries come from?

Older locally scraped TOI headline files supplied historical search candidates. Researchers then retrieved article bodies and checked the reported circumstances. Targeted web searches and follow-up source checks supplied additional entries. **This CSV is not simply 41 matches from the old scraped headline files.**

Each seed row retains its `input_table` review ledger. `discovery_basis` distinguishes the ledger used to assemble it: `web_source_review_ledger` or `cached_article_body_review_ledger`. These labels describe the recorded review stream, not a complete account of every discovery route; overlap is possible. A retrieved body is not itself an old local scrape. All seed rows have `headline_file_linkage=not_row_level_verified`: an exact original headline-file row has not been established in this community export. Do not interpret this as proof the headline was absent. Government sources were added separately.

The original research was performed by **OpenAI Codex at Aritra Basu's direction**, with additional Codex agent checks. All 41 seed records are labelled `ai_reviewed`, not independently human-validated. Subsequent contributors should record their own review status accurately.

## Additions and corrections

Read [CONTRIBUTING](../CONTRIBUTING.md). No programming is needed to submit the forms. Please supply a source URL, an incident date or explicit uncertainty, the location, the reported practice, and a short explanation. Government affiliation requires its own dated source. TOI is the primary research source; other reliable reporting, court records or official documents can be submitted with their provenance identified.

For CSV edits, preserve the header order in [schema.json](schema.json), assign a stable unique `case_id`, and set new submissions to `pending_review`. Unknown information stays blank with an explanation in `uncertainties`; it must not become a zero or a negative finding. Reviewers may retain a near match or exclusion when its relevance is explicit. Repeat coverage of the same incident should normally update the existing row.

Run `python3 community/validate_csv.py` before submitting a CSV change. The same structural check runs on pull requests. It checks formatting, identifiers, source URLs and review metadata; it cannot establish that an allegation is true or that a source has been interpreted correctly.

`record_status` describes the review process: `pending_review`, `ai_reviewed`, `human_reviewed`, or `needs_recheck`. A human review is an assessment of the sources and coding, not proof of the underlying police account. Record the reviewer and the issue/PR link. Git history preserves changes; the seed manifest records the original import. Do not add unnecessary personal identifiers, private contact details or full copyrighted article bodies.

The community CSV is a discovery and validation resource, not a population census, an event-rate denominator or evidence of a causal party effect. Keep ordinary crime, insurgency, crowds, border operations and parade allegations distinct. Keep state incumbency separate from force authority and political instructions.
