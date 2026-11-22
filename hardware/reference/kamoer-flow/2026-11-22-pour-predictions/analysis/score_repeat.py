"""Compare the recipe-specific and pulse-width models on the very same future servings."""
import argparse
import csv
import json
from pathlib import Path
from statistics import mean,median


def log(path):
    return [json.loads(s) for s in path.read_text().splitlines()]


def summarize(rows, forecast, field):
    values = [r[field] for r in rows if r[field] is not None]
    bias = mean(values)-forecast if values else None
    within = sum(r[field] is not None and r['bursts_ok'] and r['prospective']
                 and abs(r[field]-forecast)<=max(1,.1*forecast) for r in rows)
    return {'readable':len(values), 'median_ml': median(values) if values else None,
            'observed_range_ml':[min(values),max(values)] if values else None,
            'mean_error_ml':bias, 'median_absolute_error_ml':median([abs(v-forecast) for v in values]) if values else None,
            'in_band':within, 'in_five_percent':sum(r[field] is not None and r['bursts_ok'] and r['prospective']
                          and abs(r[field]-forecast)<=.05*forecast for r in rows),
            'pass':len(rows)==6 and within>=5 and bias is not None and abs(bias)<=max(.6,.05*forecast)}


def score(fresh, extra, local, general):
    merged=[]
    for data,phase in ((fresh,'fresh'),(extra,'repeat')):
        pred={r['index']:r for r in data if r['event']=='prediction'}
        for r in data:
            if r['event']!='trial' or (phase=='fresh' and r['block']<=2):
                continue
            h,n=r['head'],r['scenario']
            prediction=pred[r['index']]
            if prediction['mono_ns']<=local['frozen_monotonic_ns']:
                raise ValueError(('need future replacement of pre-freeze trial',r['label']))
            a=local['forecasts'][n][h];b=general['forecasts'][n][h]
            merged.append({'head':h,'scenario':n,'label':r['label'],'source':phase,'block':r['block'],
                           'recipe_forecast_ml':a,'width_model_ml':b,'primary_ml':r['primary_ml'],
                           'heldout_ml':r['heldout_ml'],'start_ml':r['start_ml'],'end_ml':r['finish_ml'],
                           'predicted_end_ml':r['start_ml']+(-a if h=='A' else a),
                           'prospective':prediction['mono_ns']>local['frozen_monotonic_ns'],
                           'bursts_ok':r['burst_count']==r['expected_bursts']})
    outcome=[]
    for n,cells in local['forecasts'].items():
        for h,val in cells.items():
            these=[r for r in merged if (r['head'],r['scenario'])==(h,n)]
            models={}
            for k,forecast in [('recipe',val),('width',general['forecasts'][n][h])]:
                readings={f:summarize(these,forecast,f) for f in ('primary_ml','heldout_ml')}
                models[k]={'prediction_ml':forecast,'sites':readings,'corroborated':all(s['pass'] for s in readings.values())}
            outcome.append({'head':h,'scenario':n,'n':len(these),**models})
    return merged,outcome


def overall(rows):
    summary = {}
    for name, prediction in (('recipe', 'recipe_forecast_ml'), ('width', 'width_model_ml')):
        summary[name] = {}
        for site in ('primary_ml', 'heldout_ml'):
            valid = [r for r in rows if r['prospective'] and r['bursts_ok'] and r[site] is not None]
            errors = [r[site] - r[prediction] for r in valid]
            summary[name][site] = {
                'attempts': len(rows), 'readable_with_matching_receipt': len(valid),
                'in_practical_band': sum(abs(r[site] - r[prediction]) <= max(1, .1*r[prediction]) for r in valid),
                'in_five_percent': sum(abs(r[site] - r[prediction]) <= .05*r[prediction] for r in valid),
                'mean_signed_error_ml': mean(errors) if errors else None,
                'median_absolute_error_ml': median(abs(e) for e in errors) if errors else None,
                'largest_absolute_error_ml': max((abs(e) for e in errors), default=None),
            }
    return summary


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    for name in ('fresh','extra','recipe','general','out'):a.add_argument(name,type=Path)
    v=a.parse_args();read=lambda x:json.loads(x.read_text())
    rows,summary=score(log(v.fresh),log(v.extra),read(v.recipe),read(v.general))
    v.out.mkdir(parents=True,exist_ok=True)
    with (v.out/'attempts.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (v.out/'scores.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    (v.out/'overall.json').write_text(json.dumps(overall(rows), indent=2, allow_nan=False)+'\n')
