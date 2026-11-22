"""Estimate delivery per burst from calibration pours and freeze each unseen scenario's prediction."""
import argparse
import hashlib
import json
import statistics
from datetime import datetime,timezone
from pathlib import Path


def interp(x,pairs):
    for (x0,y0),(x1,y1) in zip(pairs,pairs[1:]):
        if x0<=x<=x1:return y0+(x-x0)*(y1-y0)/(x1-x0)
    raise ValueError(f'Unsupported pulse width {x}')


def fit(training,design):
    rows=[json.loads(s) for s in training.read_text().splitlines()]
    cells={h:{} for h in ('A','B')}
    for s,e in design['scenarios'].items():
        if e['phase']!='training':continue
        width=e['ideal_gates_start_ms_width_ms'][0][1]
        for h in cells:
            obs=[z for z in rows if z['event']=='trial' and z['scenario']==s and z['head']==h]
            usable=[z for z in obs if z['burst_count']==z['expected_bursts'] and z['primary_ml'] is not None]
            if len(usable)<2:raise ValueError((h,s,'insufficient retained calibration',len(usable)))
            per=[z['primary_ml']/z['burst_count'] for z in usable]
            cells[h][width]=dict(scenario=s,nominal_ml_per_burst=statistics.median(per),individual_ml_per_burst=per,
                                 trial_indices=[z['index'] for z in usable],attempts=len(obs))
    forecasts={}
    for s,e in design['scenarios'].items():
        if e['phase']!='validation':continue
        forecasts[s]={}
        for h,levels in cells.items():
            pairs=sorted((w,b['nominal_ml_per_burst']) for w,b in levels.items())
            forecasts[s][h]=sum(interp(ms,pairs) for _,ms in e['ideal_gates_start_ms_width_ms'])
    return {'anchors':cells,'forecasts':forecasts}


if __name__=='__main__':
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument('training',type=Path);arg.add_argument('preregistration',type=Path);arg.add_argument('output',type=Path)
    a=arg.parse_args();base=json.loads(a.preregistration.read_text());v=fit(a.training,base)
    v.update(utc=datetime.now(timezone.utc).isoformat(),training_sha256=hashlib.sha256(a.training.read_bytes()).hexdigest(),
             preregistration_sha256=hashlib.sha256(a.preregistration.read_bytes()).hexdigest(),unit='Nominal mL concentrate measured on the right front scale; held-out left scale excluded from calibration.')
    with a.output.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
    print(json.dumps(v['forecasts'],indent=1))
