# Add a case or correct the research

The public, editable-through-review dataset is [community/cases.csv](community/cases.csv). Anyone with a GitHub account can contribute.

## Without editing a CSV

Use [Suggest a case](https://github.com/aritra1097/toi-police-practices-research/issues/new?template=new_case.yml) or [Correct an entry](https://github.com/aritra1097/toi-police-practices-research/issues/new?template=correction.yml). A maintainer can turn the submission into a CSV change after reviewing the sources. Submission does not automatically add an accepted case. GitHub issues are public.

## By pull request

1. Open [the CSV](https://github.com/aritra1097/toi-police-practices-research/blob/main/community/cases.csv), use GitHub's edit button, and create a fork when prompted. Alternatively, download and edit it with a CSV-aware editor, keeping UTF-8 encoding and the existing headers.
2. Add one episode per row, with a stable unique ID. First search existing rows for repeated coverage, name variants and related locations. Add source URLs separated by semicolons; do not paste entire articles.
3. For a new episode, fill at least `case_id`, `state`, `case_name`, `practice`, `source_urls`, `evidence_notes`, `record_status` and `record_updated_date`. Set `record_status=pending_review`. Supply an incident date when established; otherwise explain the uncertainty. Unknown political affiliation must not be coded as non-BJP.
4. Use [the column dictionary](community/schema.json). Preserve direct allegations, disputed claims, group versus individual attribution, attempted versus completed taking, fatal versus nonfatal outcomes, and reconstruction versus other contexts. Add a dated source for any government assignment. Delhi Police and central forces require separate authority context.
5. Run `python3 community/validate_csv.py` if working locally. Open a pull request explaining the addition or correction and its evidence. Put the issue/PR URL in `contribution_url` when available. For human-reviewed rows, name the reviewer in `reviewed_by`; human review does not verify the underlying allegation.

For corrections, retain the case ID and explain the changed interpretation in the PR. Do not silently replace conflicting dates or collapse distinct events. Use `needs_recheck` when an existing interpretation has become doubtful.

## Maintainer review

Check the actual body or primary document, incident identity/date, outcome and attribution, scope classification, government sources and force authority. If a source is unavailable, keep the limitation explicit. Passing the CSV check is not a substantive evidence review. Record the review status and reviewer truthfully; AI review alone must not become `human_reviewed`.

Set `headline_file_linkage=verified` only after checking the original file reference/hash and row or exact date-headline match documented in `evidence_notes`. This is a substantive maintainer check: the validator cannot establish old-file linkage from generic notes or a status label.

Merge accepted changes into `community/cases.csv`. Do not run a seed import over that file. Original research tables under `targeted_history/` are reproducible snapshots and remain separate; corrections to those outputs require a documented source-input change and regeneration. A community addition does not automatically revise past numerical findings or PDFs.
