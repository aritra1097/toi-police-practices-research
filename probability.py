"""Sensitivity calculations, not estimates of the truth of police accounts."""
from pathlib import Path
from math import exp, expm1, log1p
from datetime import date
import json,csv
from scipy.stats import poisson, gamma, chi2
O=Path(__file__).resolve().parent/'data';O.mkdir(exist_ok=True)
rows=[]
for r in [1,3,5,10,20,50]:
 lam=r/365
 p=float(poisson.sf(1,lam))
 rows.append(dict(assumed_events_per_year=r,p_two_or_more_specified_day=p,p_exactly_two_specified_day=float(poisson.pmf(2,lam)),p_any_calendar_day_two_or_more_in_365_days=-expm1(365*(-lam+log1p(lam))),p_next_event_within_24h=-expm1(-lam)))
with (O/'probability_sensitivity.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
windows=[]
for start in [date(2026,1,1),date(2026,5,9),date(2026,7,8)]:
 T=(date(2026,10,27)-start).days+1
 windows.append(dict(start=str(start),end='2026-10-27',calendar_days=T,p_any_same_calendar_day_given_exactly_3=3/T-2/T**2,p_any_pair_within_24h_given_exactly_3_continuous=1-((T-2)/T)**3))
examples=[]
mean=10/365
for k in [1000000,1,0.1]:
 p0=(k/(k+mean))**k
 p1=p0*k*mean/(k+mean)
 examples.append(dict(mean_events_per_year=10,gamma_daily_shape=k,p_two_or_more_specified_day=1-p0-p1))
beta=111;alpha=1.5
p0=(beta/(beta+1))**alpha
toy=dict(label='Illustration only: assumes exactly one exhaustively observed prior event over a prespecified 111-day window',exposure_days=111,events=1,poisson_plugin_p_two_or_more_next_day=float(poisson.sf(1,1/111)),jeffreys_posterior_predictive_two_or_more_next_day=1-p0*(1+alpha/(beta+1)),rate95_equal_tailed_per_year=[float(x*365) for x in gamma.ppf([.025,.975],a=alpha,scale=1/beta)],frequentist_exact_rate95_per_year=[float(.5*chi2.ppf(.025,2)/111*365),float(.5*chi2.ppf(.975,4)/111*365)])
res=dict(poisson_sensitivity=rows,conditional_three_event_windows=windows,clustered_daily_gamma_poisson=examples,hypothetical_prior_window=toy)
(O/'probabilities.json').write_text(json.dumps(res,indent=2))
print(json.dumps(res,indent=2))
