# Descriptive synthetic comparison of reported events

This module compares West Bengal with an explicitly chosen donor pool after the 9 May 2026 government transition. It measures distinct events retrieved from a common news-search frame, whose article bodies and dates have been reviewed. It does not measure the population incidence of gun-taking, unlawful killings, or police misconduct. Donor political eligibility must be established in a separate dated ledger before running this module. The script does not certify political eligibility.

Use WB with Kerala, Tamil Nadu and Telangana as the primary proposed pool only if the political audit supports the user's definition. A wider pool defined by a different coalition-history criterion is a separate sensitivity analysis, not an interchangeable estimate. Freeze donor membership, outcomes, date windows, scale and pre-fit slack before looking at comparative post-treatment outcomes. This is an exploratory analysis because the WB cluster was already observed, not a preregistered study.

## Input and completeness gate

The CSV has one row per state, calendar month and outcome, with these columns:

| Column | Meaning |
|---|---|
| `state` | `WB`, `KL`, `TN`, `TG`, full names, or explicit other donor labels |
| `month` | `YYYY-MM` or first day `YYYY-MM-01` |
| `outcome` | Explicit, consistent outcome identifier |
| `count` | Nonnegative integer count of distinct reviewed reported events |
| `observed` | `true` only when the cell count and event dating are resolved |
| `complete_frame` | `true` only when the common, explicitly documented retrieval and body-review frame is complete for the cell |
| `eligible_days` | Days in the common observation window, including 27 for October 2026 |
| `unresolved_count` | Optional; must be zero if supplied |

The gate is strict: missing rows, incomplete cells, positive unresolved counts, blank counts and mismatched eligible days stop the analysis. No missing cell becomes zero. An empty URL archive response is not evidence for zero events. Sitemap `lastmod` is not an event or publication date. For the current detected-case panel, `complete_frame=true` means that the fixed acquisition, lexical screening, flagged-context adjudication and stated low-signal audit were completed. It does not mean that every background article was manually read: 245 expanded-signal articles, 21 additional low-signal reports and a separate 48-article stratified audit received the described review. The pipeline still misses news outside its retrieval terms and can miss mechanisms in screened background articles. Document that frame in the input's provenance and interpret zeros as no positive identified by this pipeline, not an AI-validated negative or true incidence zero. A convenience list of examples is insufficient for a population comparison.

Use distinct outcomes for immediate officer-firearm-taking claims followed by police shooting, police parades explicitly described as reconstruction, and broader fatal police events. Fatality and clothing distinctions should remain available in the event ledger. Multiple articles about one incident are not multiple observations. Uncertain cases need a separate measurement-bounds analysis; this point-panel implementation intentionally fails instead of silently excluding them.

## Dates and scale

Weights use only months through April 2026. May is excluded, rather than treated as wholly exposed. The post-period starts June 2026 and ends no later than 27 October 2026. With the default endpoint, it has 149 eligible days over five monthly cells. All states use the same endpoint. The default scale is reported events per 30 eligible days. A raw eligible-month count scale is also available. Neither scale supplies a denominator for true event incidence or prisoner-transport risk.

## Why a single weight vector is insufficient

Let y_t be WB's pre-period outcome, X_t the donor outcomes and w the donor weights. Require w_j >= 0 and sum(w_j) = 1. First solve the pre-period linear program

    e* = min_w max_t |X_t w - y_t|.

Then define the complete compatible set

    W(e) = {w >= 0, sum(w) = 1, |X_t w - y_t| <= e* + delta for every pre-month}.

`delta` is the user-specified `--pre-slack`, in the selected outcome's units; default zero. It must be chosen without post-period fitting. The script reports a separate tiny numerical feasibility tolerance. This is a minimax pre-fit definition so the compatible set has linear constraints. It is not a claim that these are all weights within a particular least-squares confidence region.

The central curve minimizes pre-period mean squared error plus a small ridge penalty toward equal weights inside W(e). That is a descriptive tie-break, not an identified or validated counterfactual. No post-period data enter the central weight fit or the compatible-set definition. If the numerical optimizer cannot find a valid solution, the script transparently uses a feasible pre-LP vector instead.

For every donor, LPs compute the smallest and largest compatible weight. For every post-month, LPs compute

    min_{w in W(e)} X_post w, max_{w in W(e)} X_post w.

Additional LPs calculate the range for the pooled post-period rate, or total when using counts. This pooled range is calculated directly: summing pointwise extrema would generally combine incompatible weight vectors. When WB and all donors have zero pre-period outcomes, the entire simplex is compatible; the post range is the donors' range, not a falsely identified equal-weight counterfactual. The output explicitly flags weight nonuniqueness.

The band measures ambiguity across weights conditional on the chosen pre-fit rule and retrieval frame. It is not a confidence interval, a bound on the causal effect, or uncertainty about undiscovered events. Post-month extrema can correspond to different weights; a path assembled from all lower or upper monthly endpoints need not be feasible as one synthetic trajectory. The `compatible_set.json` constraints describe the actual joint set, and `compatible_weight_examples.csv` provides reproducible extrema witnesses.

LP solvers can return bounds a few billionths outside the theoretical [0,1] weight interval. Reported weight-bound columns clip such violations only when they are at most 1e-6; larger violations stop the run. Raw LP extrema remain in separate columns. This reporting rule does not change the compatible constraints, their numerical tolerance, or the optimization model. Raw witness vectors may retain solver roundoff and should be interpreted at the documented numerical precision.

## Running and outputs

Use a Python environment with NumPy, SciPy and optional Matplotlib:

```sh
python3 scm_reported_events.py --input /absolute/path/validated_panel.csv \
  --output /absolute/path/scm_gun_claims \
  --outcome gun_taking_police_shooting \
  --donors KL TN TG --pre-slack 0
```

The script writes a source hash, fitting metadata, central and bounded weights, compatible-set constraints, trajectory data, and an actual-versus-synthetic plot. `--no-plot` disables only plotting. The main graph labels the band as a compatible-weight range, not inferential uncertainty. `--scale count` is an optional separate sensitivity analysis. Analyze different outcomes in different output directories.

```sh
python3 -m unittest discover -s . -p 'test_*.py' -v
```

Tests use synthetic fixtures only: completely flat pre-periods retain all weight ambiguity, a known unique convex match is recovered, unknown cells stop the run, and changing all post-period observations cannot change fitted weights or the compatible-set tolerance. Fixture outputs are temporary and never represent substantive cases.

A further fixture verifies that monthly extrema cannot be summed into a false pooled bound: when two donors have opposing post-month trajectories, each month can separately have zero as its lower endpoint even though the pooled rate is fixed at a positive value for every single admissible weight vector. Positive minimum pre-fit error and substantive slack are also checked.

## Inference and interpretation

One treated state and three donors do not support reliable conventional cluster-robust significance claims. A four-state treatment-label placebo has minimum one-sided rank fraction 1/4 and is a randomization p-value only under an additional exchangeability assumption. Different policing exposures, conflict, news reporting, government changes and ascertainment may defeat that assumption and parallel-trend interpretations. No p-value is emitted here. A flat pre-period with rare events does not validate parallel trends.

The resulting gap describes a WB-versus-synthetic difference in the retrieved reported-event measure after the government transition. It cannot isolate BJP causation, establish police accounts as true or fabricated, or compare the propensity to seize guns per reconstruction without opportunity denominators. Broader donor pools, alternative frozen pre-fit tolerances, leave-one-donor-out analyses and an additive descriptive DiD can be reported as distinct sensitivity analyses, with no post-period tuning.

This module and note were written with OpenAI Codex AI assistance and checked with automated synthetic fixtures. AI/subagent checks are not independent human validation. The public repository should separately state whether the real event coding and political eligibility ledger received human review.

## Methodological references

- Abadie, Alberto (2021), [Using Synthetic Controls: Feasibility, Data Requirements, and Methodological Aspects](https://www.aeaweb.org/articles?id=10.1257%2Fjel.20191450), Journal of Economic Literature 59(2), 391-425. General guidance on contextual requirements, donor comparisons and inference; the linear compatible-set sensitivity rule above is this module's explicitly specified descriptive construction.
- Conley, Timothy, and Christopher Taber (2005 working-paper version), [Inference with Difference in Differences with a Small Number of Policy Changes](https://www.nber.org/papers/t0312). The few-treated-group problem motivates care with conventional asymptotic inference. Their proposed alternative uses many untreated groups, which this three-donor design does not provide.
