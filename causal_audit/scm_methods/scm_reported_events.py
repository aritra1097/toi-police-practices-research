#!/usr/bin/env python3
"""Descriptive simplex synthetic control with explicit pre-fit-compatible sets.

This estimates a comparison of retrieved news-reported events, not incidence or
a causal party effect. No missing observation is replaced by zero.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile

import numpy as np
from scipy.optimize import linprog, minimize

ALIASES = {
    'wb': 'WB', 'westbengal': 'WB', 'kl': 'KL', 'kerala': 'KL',
    'tn': 'TN', 'tamilnadu': 'TN', 'tg': 'TG', 'ts': 'TG', 'telangana': 'TG',
}
WEIGHT_BOUND_REPORTING_TOLERANCE = 1e-6


def reported_weight_bound(value: float) -> float:
    """Clip only solver roundoff for reporting; retain raw extrema separately."""
    value = float(value)
    if value < -WEIGHT_BOUND_REPORTING_TOLERANCE or value > 1 + WEIGHT_BOUND_REPORTING_TOLERANCE:
        raise ValueError(f'LP weight bound materially outside simplex: {value}')
    return min(1., max(0., value))


def state_code(value: str) -> str:
    key = ''.join(c for c in value.lower() if c.isalnum())
    return ALIASES.get(key, value.strip())


def is_true(value: str) -> bool:
    return str(value).strip().lower() in {'1', 'true', 'yes'}


def month_start(value: str) -> dt.date:
    value = value.strip()
    if len(value) == 7:
        value += '-01'
    date = dt.date.fromisoformat(value)
    if date.day != 1:
        raise ValueError(f'Month must identify its first day: {value}')
    return date


def months_between(start: dt.date, end: dt.date) -> list[dt.date]:
    result = []
    while start <= end:
        result.append(start)
        start = dt.date(start.year + (start.month == 12), start.month % 12 + 1, 1)
    return result


def read_panel(path: Path, outcome: str, states: list[str], start: dt.date,
               end: dt.date, scale: str) -> tuple[list[dt.date], np.ndarray, np.ndarray]:
    """Strict complete-frame gate. 'observed' includes resolved outcome coding."""
    wanted = months_between(start, end.replace(day=1))
    wanted = [m for m in wanted if m != dt.date(2026, 5, 1)]
    records = {}
    required = {'state', 'month', 'outcome', 'count', 'observed',
                'complete_frame', 'eligible_days'}
    with path.open(newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'Missing columns: {sorted(missing)}')
        for number, row in enumerate(reader, 2):
            if row['outcome'].strip() != outcome:
                continue
            state = state_code(row['state'])
            month = month_start(row['month'])
            if state not in states or month not in wanted:
                continue
            key = state, month
            if key in records:
                raise ValueError(f'Duplicate state-month-outcome at input row {number}: {key}')
            if not is_true(row['observed']) or not is_true(row['complete_frame']):
                raise ValueError(f'Unknown/incomplete cell at row {number}: {state} {month}; '
                                 'not zero-imputed. Complete review or analyze bounds separately.')
            if row.get('unresolved_count', '').strip():
                unresolved = float(row['unresolved_count'])
                if not math.isfinite(unresolved) or unresolved != 0:
                    raise ValueError(f'Unresolved mechanism/date cases at row {number}; '
                                     'point-panel SCM is not permitted.')
            try:
                count, days = float(row['count']), float(row['eligible_days'])
            except ValueError as exc:
                raise ValueError(f'Blank/non-numeric count or exposure at row {number}') from exc
            if not math.isfinite(count) or count < 0 or count != int(count):
                raise ValueError(f'Count must be a nonnegative integer at row {number}')
            calendar_days = calendar.monthrange(month.year, month.month)[1]
            expected_days = min(calendar_days, end.day) if month == end.replace(day=1) else calendar_days
            if not math.isfinite(days) or days != expected_days:
                raise ValueError(f'Exposure mismatch at row {number}: {days}; expected '
                                 f'{expected_days} eligible calendar days for the common frame.')
            records[key] = count, days
    absent = [(s, m.isoformat()[:7]) for m in wanted for s in states if (s, m) not in records]
    if absent:
        raise ValueError(f'Missing state-month cells, never zero-imputed: {absent[:12]} '
                         f'({len(absent)} total)')
    counts = np.array([[records[s, m][0] for s in states] for m in wanted], dtype=float)
    exposure = np.array([records[states[0], m][1] for m in wanted], dtype=float)
    values = counts if scale == 'count' else counts / exposure[:, None] * 30
    return wanted, values, exposure


def fit_compatible_set(y: np.ndarray, x: np.ndarray, slack: float = 0.,
                       ridge: float = 1e-6) -> dict:
    """Define the set using only pre-data and a fixed extra max-residual slack.

    First minimize maximum absolute pre-residual by LP. Then retain all simplex
    weights within optimum + slack. The central curve minimizes pre-MSE with a
    ridge tie-break toward equal weights *inside this set*.
    """
    y, x = np.asarray(y, float), np.asarray(x, float)
    if x.ndim != 2 or y.shape != (x.shape[0],) or x.shape[0] < 2 or x.shape[1] < 2:
        raise ValueError('Need at least two pre-months and two donors')
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('Pre-period has missing/nonfinite observations')
    if not math.isfinite(slack) or slack < 0 or not math.isfinite(ridge) or ridge < 0:
        raise ValueError('Pre-fit slack and ridge must be finite and nonnegative')
    j = x.shape[1]
    objective = np.r_[np.zeros(j), 1.]
    constraints = np.r_[np.c_[x, -np.ones(len(y))], np.c_[-x, -np.ones(len(y))]]
    rhs = np.r_[y, -y]
    result = linprog(objective, A_ub=constraints, b_ub=rhs,
                     A_eq=[np.r_[np.ones(j), 0.]], b_eq=[1.],
                     bounds=[(0., 1.)] * j + [(0., None)], method='highs')
    if not result.success:
        raise ValueError(f'Pre-fit LP failed: {result.message}')
    minimum_error = max(0., float(result.x[-1]))
    tolerance = minimum_error + slack
    # Numerical tolerance is reported separately from the substantive slack.
    numerical = 1e-8 * max(1., abs(y).max(), abs(x).max())
    a_ub = np.r_[x, -x]
    b_ub = np.r_[y + tolerance + numerical, -y + tolerance + numerical]
    feasible = dict(A_ub=a_ub, b_ub=b_ub, A_eq=np.ones((1, j)), b_eq=np.array([1.]),
                    bounds=[(0., 1.)] * j, method='highs')
    equal = np.ones(j) / j
    loss = lambda w: np.mean((x @ w - y) ** 2) + ridge * np.sum((w - equal) ** 2)
    derivative = lambda w: 2 * x.T @ (x @ w - y) / len(y) + 2 * ridge * (w - equal)
    initial = equal if np.max(a_ub @ equal - b_ub) <= numerical else result.x[:-1]
    central = minimize(loss, initial, jac=derivative, method='SLSQP',
                       bounds=[(0., 1.)] * j,
                       constraints=[{'type': 'eq', 'fun': lambda w: w.sum() - 1,
                                     'jac': lambda w: np.ones(j)},
                                    {'type': 'ineq', 'fun': lambda w: b_ub - a_ub @ w,
                                     'jac': lambda w: -a_ub}],
                       options={'maxiter': 2000, 'ftol': 1e-12})
    valid = (central.success and abs(central.x.sum() - 1) < 1e-6
             and np.min(central.x) >= -1e-7
             and np.max(a_ub @ central.x - b_ub) <= 1e-6)
    weights = central.x if valid else result.x[:-1]
    return dict(weights=weights, minimum_max_pre_residual=minimum_error,
                substantive_pre_slack=slack, numerical_tolerance=numerical,
                allowed_max_pre_residual=tolerance, ridge=ridge,
                central_optimizer=str(central.message), central_success=bool(valid),
                central_method='pre-MSE plus ridge toward equal weights' if valid else 'feasible pre-LP fallback',
                feasible=feasible)


def extreme(fit: dict, objective: np.ndarray, maximize: bool = False) -> tuple[float, np.ndarray]:
    vector = np.asarray(objective, float)
    result = linprog(-vector if maximize else vector, **fit['feasible'])
    if not result.success:
        raise ValueError(f'Compatible-set LP failed: {result.message}')
    return float(vector @ result.x), result.x


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(args: argparse.Namespace) -> dict:
    treated = state_code(args.treated)
    donors = [state_code(s) for s in args.donors]
    if len(donors) < 2 or len(set([treated] + donors)) != len(donors) + 1:
        raise ValueError('Need distinct treated state and at least two distinct donors')
    start, end = month_start(args.start), dt.date.fromisoformat(args.end)
    if start > dt.date(2026, 4, 1) or end < dt.date(2026, 6, 1) or end > dt.date(2026, 10, 27):
        raise ValueError('Need pre-period through April and post-period June to no later than October 27, 2026')
    months, values, exposure = read_panel(Path(args.input), args.outcome, [treated] + donors,
                                        start, end, args.scale)
    pre = np.array([m <= dt.date(2026, 4, 1) for m in months])
    post = np.array([m >= dt.date(2026, 6, 1) for m in months])
    fit = fit_compatible_set(values[pre, 0], values[pre, 1:], args.pre_slack, args.ridge)
    bounds, examples = [], []
    def record_extrema(label, objective):
        lo, lw = extreme(fit, objective)
        hi, hw = extreme(fit, objective, True)
        for kind, weight in [('min', lw), ('max', hw)]:
            examples.append(dict(objective=label, extremum=kind,
                                 **{state: float(w) for state, w in zip(donors, weight)}))
        return lo, hi
    for index, donor in enumerate(donors):
        objective = np.eye(len(donors))[index]
        lo, hi = record_extrema(f'weight_{donor}', objective)
        bounds.append(dict(state=donor, central_weight=float(fit['weights'][index]),
                           compatible_min_weight=reported_weight_bound(lo),
                           compatible_max_weight=reported_weight_bound(hi),
                           raw_lp_min_weight=lo, raw_lp_max_weight=hi))
    trajectories = []
    for index, month in enumerate(months):
        lo, hi = record_extrema(month.isoformat()[:7], values[index, 1:])
        actual = float(values[index, 0])
        synthetic = float(values[index, 1:] @ fit['weights'])
        trajectories.append(dict(month=month.isoformat()[:7], period='pre' if pre[index] else 'post',
                                 eligible_days=float(exposure[index]), actual=actual, synthetic=synthetic,
                                 compatible_min_synthetic=lo, compatible_max_synthetic=hi,
                                 actual_minus_synthetic=actual - synthetic,
                                 compatible_min_gap=actual - hi, compatible_max_gap=actual - lo))
    # Exposure weighting gives a pooled post-period rate when the scale is per30days.
    aggregation = exposure[post] / exposure[post].sum() if args.scale == 'per30days' else np.ones(post.sum())
    pooled_objective = aggregation @ values[post, 1:]
    pooled_lo, pooled_hi = record_extrema('pooled_post_rate' if args.scale == 'per30days' else 'post_total_count',
                                         pooled_objective)
    actual_pool = float(aggregation @ values[post, 0])
    central_pool = float(pooled_objective @ fit['weights'])
    widths = [row['compatible_max_weight'] - row['compatible_min_weight'] for row in bounds]
    summary = {k: v for k, v in fit.items() if k not in {'weights', 'feasible'}}
    summary.update(dict(outcome=args.outcome, treated=treated, donors=donors,
        scale=args.scale, input_sha256=hashlib.sha256(Path(args.input).read_bytes()).hexdigest(),
        analysis_start=start.isoformat(), end_inclusive=end.isoformat(), excluded_month='2026-05',
        treatment_date='2026-05-09', pre_months=int(pre.sum()), post_months=int(post.sum()),
        post_eligible_days=float(exposure[post].sum()),
        central_weights={s: float(w) for s, w in zip(donors, fit['weights'])},
        weight_set_nonunique=bool(max(widths) > 1e-6), max_weight_range=float(max(widths)),
        weight_bound_reporting_tolerance=WEIGHT_BOUND_REPORTING_TOLERANCE,
        weight_bound_reporting_rule='Only bounds outside [0,1] by at most reporting tolerance are clipped; '
                                    'raw LP extrema are retained in weight_bounds.csv. Compatible constraints '
                                    'and their numerical tolerance are unchanged.',
        reported_weight_bounds_clipped=sum(row['compatible_min_weight'] != row['raw_lp_min_weight'] or
                                          row['compatible_max_weight'] != row['raw_lp_max_weight'] for row in bounds),
        treated_pre_all_zero=bool(np.all(values[pre, 0] == 0)),
        all_donor_pre_all_zero=bool(np.all(values[pre, 1:] == 0)),
        pre_rmspe=float(np.sqrt(np.mean((values[pre, 1:] @ fit['weights'] - values[pre, 0]) ** 2))),
        pooled_post_actual=actual_pool, pooled_post_central_synthetic=central_pool,
        pooled_post_compatible_min_synthetic=pooled_lo, pooled_post_compatible_max_synthetic=pooled_hi,
        pooled_post_central_gap=actual_pool - central_pool,
        pooled_post_compatible_min_gap=actual_pool - pooled_hi,
        pooled_post_compatible_max_gap=actual_pool - pooled_lo,
        interpretation='Descriptive comparison of retrieved body-validated news-reported events. '
                       'Compatible-weight ranges are not sampling confidence intervals or causal effect bounds. '
                       'No p-value or claim of real-event incidence is produced.'))
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'summary.json').write_text(json.dumps(summary, indent=2))
    feasible = fit['feasible']
    (output / 'compatible_set.json').write_text(json.dumps(dict(
        donors=donors, pre_months=[m.isoformat()[:7] for m, keep in zip(months, pre) if keep],
        A_ub=feasible['A_ub'].tolist(), b_ub=feasible['b_ub'].tolist(),
        A_eq=feasible['A_eq'].tolist(), b_eq=feasible['b_eq'].tolist(),
        bounds=feasible['bounds'], definition='All weights satisfying these linear constraints; '
        'pointwise extrema can use different weight vectors. The central curve does not identify a unique counterfactual.'), indent=2))
    write_csv(output / 'weight_bounds.csv', bounds)
    write_csv(output / 'compatible_weight_examples.csv', examples)
    write_csv(output / 'trajectory.csv', trajectories)
    if not args.no_plot:
        plot(trajectories, summary, output / 'actual_vs_synthetic.png')
    return summary


def plot(rows: list[dict], summary: dict, target: Path) -> None:
    os.environ.setdefault('MPLCONFIGDIR', tempfile.mkdtemp(prefix='scm-matplotlib-'))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    indexed = {row['month']: row for row in rows}
    dates = months_between(month_start(rows[0]['month']), month_start(rows[-1]['month']))
    def series(name):
        return [indexed.get(d.isoformat()[:7], {}).get(name, float('nan')) for d in dates]
    figure, axis = plt.subplots(figsize=(10.5, 5.4))
    axis.plot(dates, series('actual'), color='#153b50', marker='o', label=f"Observed {summary['treated']}")
    axis.plot(dates, series('synthetic'), color='#bd6b26', linestyle='--', label='Synthetic central curve (tie-break)')
    post_rows = [r for r in rows if r['period'] == 'post']
    axis.fill_between([month_start(r['month']) for r in post_rows],
                      [r['compatible_min_synthetic'] for r in post_rows],
                      [r['compatible_max_synthetic'] for r in post_rows],
                      color='#e8c79b', alpha=.6, label='Range across pre-fit-compatible weights')
    axis.axvspan(dt.date(2026, 5, 1), dt.date(2026, 6, 1), color='#d4d8db', alpha=.6,
                 label='May excluded; transition May 9')
    axis.set_title(f"{summary['outcome']}: retrieved reported events\nDescriptive synthetic comparison; range is not a confidence interval")
    axis.set_ylabel('Events per 30 eligible days' if summary['scale'] == 'per30days' else 'Reported events in eligible month')
    axis.grid(axis='y', alpha=.2)
    axis.legend(loc='upper left', fontsize=8)
    figure.autofmt_xdate()
    figure.tight_layout()
    figure.savefig(target, dpi=180)
    plt.close(figure)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument('--input', required=True)
    result.add_argument('--output', required=True)
    result.add_argument('--outcome', required=True)
    result.add_argument('--treated', default='WB')
    result.add_argument('--donors', nargs='+', default=['KL', 'TN', 'TG'])
    result.add_argument('--start', default='2024-01')
    result.add_argument('--end', default='2026-10-27')
    result.add_argument('--scale', choices=['count', 'per30days'], default='per30days')
    result.add_argument('--pre-slack', type=float, default=0.,
                        help='Extra maximum pre-residual allowed beyond the pre-only optimum; set before examining post data')
    result.add_argument('--ridge', type=float, default=1e-6,
                        help='Tie-break toward equal weights; not an identification assumption')
    result.add_argument('--no-plot', action='store_true')
    return result


if __name__ == '__main__':
    options = parser().parse_args()
    try:
        print(json.dumps(run(options), indent=2))
    except (ValueError, OSError) as error:
        raise SystemExit(f'ANALYSIS NOT RUN: {error}')
