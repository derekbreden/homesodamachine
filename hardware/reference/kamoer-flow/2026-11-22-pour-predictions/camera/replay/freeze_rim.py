"""Freeze training-only optical predictions for equal-water full and partial metered pours."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

import numpy as np
from read_pour_timings import SITES

def predictions(results,timeline):
    training=[r for r in results['trials'] if r['phase']=='training' and r['recorded_trial']]
    if len(training)<24:raise ValueError('Training endpoints incomplete')
    out={}
    for head in ('A','B'):
        out[head]={}
        for site in SITES:
            forecasts={};training_sets={}
            for target,baseline in [('full_glass','t_full'),('partial_glass','t_partial')]:
                homologous=[r for r in training if r['head']==head and r['scenario']==baseline and site in r['sites']]
                if len(homologous)<3:raise ValueError('Training group incomplete')
                values=[r['sites'][site]['settled']/r['board_bursts'] for r in homologous]
                forecasts[target]=float(np.median(values)*timeline['program'][target]['ideal_bursts'])
                training_sets[baseline]=[{'label':r['label'],'settled_px_per_reported_burst':v} for r,v in zip(homologous,values)]
            out[head][site]=dict(predicted_signed_px=forecasts,full_partial_ratio=forecasts['full_glass']/forecasts['partial_glass'],training=training_sets)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('results',type=Path);ap.add_argument('timeline',type=Path);ap.add_argument('output',type=Path)
    a=ap.parse_args();res=predictions(json.loads(a.results.read_text()),json.loads(a.timeline.read_text()))
    if a.output.exists():
        if json.loads(a.output.read_text())['predictions']!=res:raise RuntimeError('Previously frozen predictions differ')
    else:
        a.output.write_text(json.dumps({'frozen_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'predictions':res},indent=2)+'\n')
    print(a.output,hashlib.sha256(a.output.read_bytes()).hexdigest())
