# Independent detected-case panel and synthetic-comparison audit

Reviewed 27 October 2026 by a separate OpenAI Codex subagent. This is an arithmetic, provenance and interpretation audit against the saved coding ledger. It is not independent human verification of police accounts or a new source-context classification of every article.

## Reconciliation

All checks passed: the ledger's 44 event IDs are unique; every one of the panel's 816 state-month-outcome cells agrees with the ledger's positive-label fields; all 96 window-summary rows agree with independently recalculated dates, counts and rates. The saved ledger hash and each model's input-panel hash match the files reviewed. The panel contains six outcomes for four states over 34 calendar months, including May. Each main synthetic comparison correctly excludes May and uses 28 pre-months through April 2026 and five post-months from June through 27 October, totaling 149 post-days. Every saved trajectory has 33 monthly observations and no May observation.

| Main comparison, June 1-October 27 | WB detected events | KL / TN / TG detected events | WB and synthetic gap per 30 days |
|---|---:|---|---:|
| Immediate officer-firearm-taking claim followed by police shooting | 3 | 0 / 0 / 0 | 0.604027 |
| Broad police public parade | 4 | 0 / 0 / 0 | 0.805369 |
| Public parade explicitly described as reconstruction | 3 | 0 / 0 / 0 | 0.604027 |
| Reconstruction plus explicitly shirtless police parade | 1 | 0 / 0 / 0 | 0.201342 |

These rates are count divided by 149, multiplied by 30; they are not risk per suspect, transport or reconstruction. The broad category has five WB events when the May 28 Bonny event is included in the separate May 9-October 27 window, but only four in the main June-onward comparison. The clothing categories must remain distinct: the four broad parades are not four shirtless or naked parades. The three WB gun-claim events are all coded fatal; the one identified Telangana case is October 20, 2025 and therefore belongs to the pre-period. Historical cases, central-force sensitivity cases, earlier gun possession, private mob action and threats are not mixed into these outcomes.

## Synthetic weights and numerical precision

All four main models have nonunique pre-fit-compatible weight sets. For the gun outcome, the zero WB pre-path forces Telangana's weight effectively to zero because its one identified pre-event creates a positive October 2025 observation. Kerala and Tamil Nadu can divide nearly all the weight arbitrarily. The displayed approximately 0.5/0.5 split is a tie-break, not an empirically unique comparison. For the three parade outcomes, all four states have zero detected pre-period outcomes and the donor simplex is entirely compatible; equal one-third weights are again a tie-break.

All three donors have zero detected post-period cases for these outcomes. Consequently, every compatible donor combination has a zero synthetic post-path and the displayed compatible-weight band collapses to zero. That collapse does not establish a known counterfactual or causal certainty. Here the synthetic gap largely restates the WB detected post-count because the donor outcomes are all zero. A perfect zero pre-fit supplies no convincing evidence of comparable underlying policing or reporting processes.

One raw gun-model LP bound was -1.033e-8, numerical solver roundoff at the simplex boundary. The reporting code now clips only bounds outside [0,1] by at most 1e-6; larger violations stop the run. Raw extrema remain in separate CSV columns and the actual constraint tolerances remain recorded unchanged. The four models were rerun after this reporting correction. Reported maximum weight ranges are now at most one. The added roundoff test and four existing substantive synthetic-fixture tests pass.

## Leave-one-donor-out sensitivity

Three actual-panel gun-outcome fits were run in `sensitivity_leave_one_out/`. Omitting TG leaves nonunique KL/TN weights. Omitting TN or KL leaves essentially all the weight on the remaining zero-pre-path state and zero on TG, at 1e-6 reporting precision. All three fits have the same zero synthetic post-path and the same 0.604027 detected-case gap per 30 days. The summary is in `sensitivity_leave_one_out/summary.csv`.

This stability is mechanical because all post-period donor counts are zero. It does not validate the counterfactual or demonstrate robustness of a causal effect to donor choice. The compatible sets, raw numerical extrema and pre-fit diagnostics remain available for each fit.

## Conditions for public interpretation

`complete_frame=1` and `unresolved_count=0` refer to completion of the declared acquisition, lexical screening, flagged-context adjudication and stated audit pipeline. They do not mean every background article was read, all mechanisms are known, all reports are independently confirmed, or recall is known. The coding documentation preserves genuinely uncertain dates, attempted versus completed firearm-taking, and cases whose reported mechanism does not meet the strict label. The panel is a record of positives identified by this completed pipeline; a zero is not an incidence zero or a validated absence of the behavior.

The four summaries correctly describe detected-report comparisons and emit no causal p-value. One treated state, three donors, selected news coverage, rare outcomes, zero pre-paths and possible changes in reporting or retrieval sensitivity do not identify the causal effect of BJP control. The result may be published as a transparent exploratory comparison of the stated detection process, with the event ledger and these limitations. It must not be advertised as a census, proof of a new practice, a probability that police accounts were fabricated, or an identified BJP effect.

The positive-label definitions and political eligibility ledger remain substantive assumptions requiring human review before strong conclusions. Other known reports outside this frozen cohort are evidence of frame limitations, not additional observations that can be silently added to only one side of the comparison.
