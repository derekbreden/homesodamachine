"""Score preset end-level predictions and paired dose differences at low and high liquid levels."""
import argparse
import csv
import json
from statistics import mean, median, stdev
from pathlib import Path

from scipy.stats import t as student


def flatten(trial, site):
    start = trial['pre_cup'][site]['ml']
    end = trial['post_cup'][site]['ml']
    sign = 1 if trial['head'] == 'B' else -1
    forecast = trial['forecast_ml']
    complete = start is not None and end is not None
    dose = sign * (end-start) if complete else None
    error = dose-forecast if complete else None
    native = -sign * (trial['post_cup'][site]['row'] - trial['pre_cup'][site]['row'])
    return {'head':trial['head'], 'level':trial['level'], 'block':trial['block'], 'index':trial['index'],
            'site':site, 'forecast_ml':forecast, 'dose_ml':dose, 'error_ml':error, 'start_ml':start,
            'finish_ml':end, 'native_displacement_px':native,
            'local_ml_per_px':dose/native if complete and native else None, 'forecast_finish_ml':start+sign*forecast if start is not None else None,
            'midpoint_ml':(start+end)/2 if complete else None,
            'bursts_correct':trial['expected_bursts']==trial['burst_count'],
            'in_band':complete and abs(error)<=max(1, .10*forecast) and trial['expected_bursts']==trial['burst_count']}


def score(trials):
    rows = [flatten(trial, site) for trial in trials for site in ('x990','x1986')]
    per_head = {}
    for head in ('A','B'):
        per_head[head] = {}
        for site in ('x990','x1986'):
            outcomes = {}
            matches = {}
            for level in ('low','high'):
                obs = [r for r in rows if (r['head'],r['site'],r['level'])==(head,site,level)]
                dose = [r['dose_ml'] for r in obs if r['dose_ml'] is not None]
                errors = [r['error_ml'] for r in obs if r['error_ml'] is not None]
                forecast = obs[0]['forecast_ml'] if obs else None
                passes = sum(r['in_band'] for r in obs)
                bias = mean(errors) if errors else None
                outcomes[level] = {'forecast_ml':forecast, 'attempts':len(obs), 'readable':len(dose), 'in_band':passes,
                                   'dose_range_ml':[min(dose),max(dose)] if dose else None,
                                   'median_ml':median(dose) if dose else None, 'mean_bias_ml':bias,
                                   'passed':len(obs)==6 and passes>=5 and bias is not None and abs(bias)<=max(.6,.05*forecast)}
                matches[level] = {r['block']:r for r in obs if r['dose_ml'] is not None and r['bursts_correct']}
            diffs, distances, pixel_diffs = [], [], []
            for block in sorted(matches['high'].keys() & matches['low'].keys()):
                high,low = matches['high'][block],matches['low'][block]
                diffs.append(high['dose_ml']-low['dose_ml'])
                pixel_diffs.append(high['native_displacement_px']-low['native_displacement_px'])
                distances.append(high['midpoint_ml']-low['midpoint_ml'])
            interval = None
            if len(diffs)>1:
                half = float(student.ppf(.95,len(diffs)-1)) * stdev(diffs) / len(diffs)**.5
                interval=[mean(diffs)-half, mean(diffs)+half]
            outcomes['paired']={'high_minus_low_dose_ml':diffs, 'midpoint_separations_ml':distances,
                                'mean_difference_ml':mean(diffs) if diffs else None, 'interval_90_ml':interval,
                                'high_minus_low_displacement_px':pixel_diffs,
                                'mean_displacement_difference_px':mean(pixel_diffs) if pixel_diffs else None,
                                'equivalent':len(diffs)==6 and mean(distances)>=30 and -1<interval[0] and interval[1]<1}
            per_head[head][site] = outcomes
    return rows,per_head


if __name__ == '__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('journal',type=Path)
    a.add_argument('out',type=Path)
    v=a.parse_args()
    trials=[r for r in map(json.loads,v.journal.read_text().splitlines()) if r['event']=='trial']
    rows, scores=score(trials)
    v.out.mkdir(parents=True,exist_ok=True)
    (v.out/'scores.json').write_text(json.dumps(scores,indent=2,allow_nan=False)+'\n')
    with (v.out/'attempts.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
