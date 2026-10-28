# Targeted historical headline retrieval extension

`scan_headlines.py` reads the original saved headline files without modifying them or fetching articles. It verifies each canonical input against the SHA-256 hash in `../data/manifest.json`, scans the main dataset and every manifest-canonical export containing dated records, and skips byte-identical filename aliases and undated exports. The manifest's date content, rather than an export filename's apparent year range, determines eligibility.

The search applies the same national rules to every eligible record. It supplements the earlier West Bengal and nationwide encounter/firearm retrieval with broader gun-taking language (including theft, looting and taking) and police/suspect parades, stripping and underclothing language. Ceremonial and identification parades remain in the review frame with a hint flag. The resulting false positives are expected; this is retrieval, not an event classifier. Mob violence, foreign events, metaphorical language and unrelated weapon thefts require subsequent review.

Outputs:

- `supplemental_candidates.csv`: newly retrieved date-headlines absent from the earlier 7,356-candidate inventory.
- `expanded_pattern_matches.csv`: every match to the expanded patterns, including overlap with the earlier inventory.
- `combined_candidate_inventory.csv`: the union of the earlier inventory and new supplement. Its baseline-only rows retain the earlier source references, with empty new-pattern flags because those headlines did not match these routes.
- `retrieval_patterns_v1.json`: exact versioned expressions and Boolean routes.
- `audit_counts.json`: per-file rows, hashes, exclusions, route counts, final totals and limitations.
- `scan_progress.jsonl`: progress log, ending with a formatted summary.

`dataset_publish_date` means the main dataset's supplied publication-date field; it has not been independently checked against each article. `archive_listing_date` means the saved daily archive's heading date, which is neither a verified publication date nor an incident date. A match across the two sources retains both date types. Actual article publication time and incident date must be collected and coded separately.

Deduplication reproduces the earlier date-plus-normalized-headline ID. Thus multiple reports on different dates remain separate, and these row counts must not be presented as incident counts. `all_urls_json`, `all_article_ids_json` and `provenance_json` preserve available links and source record references. A provenance record number includes the CSV header; it is not necessarily a physical text-file line number when quoted cells contain newlines. The first headline/category/URL is a display value; all available provenance should be consulted before assigning geography.

This extension does not measure full-text recall or fill missing historical days. Final inference requires source-body review, actor and event-state verification, follow-up/incident deduplication, treatment-date definitions and explicit handling of unavailable or ambiguous reports. Automated retrieval flags and AI review are not a human-coded gold standard.
