"""Freeze a second, image-coordinate prediction from the clear glass after training."""
import argparse
import json
from pathlib import Path
from statistics import median

from freeze import interp


def camera_model(training,design):
    rows=[json.loads(s) for s in training.read_text().splitlines()]
    anchor={h:{} for h in ['A','B']}
    for n,s in design['scenarios'].items():
        if s['phase']!='training':continue
        w=s['ideal_gates_start_ms_width_ms'][0][1]
        for h in anchor:
            a=[r['operating_change_ml']/.42/r['burst_count'] for r in rows if r['event']=='trial' and r['head']==h and r['scenario']==n and r['burst_count']==r['expected_bursts']]
            if len(a)<2:raise ValueError((h,n,a))
            anchor[h][w]=median(a)
    forecast={}
    for n,s in design['scenarios'].items():
        if s['phase']=='validation':
            forecast[n]={h:sum(interp(w,sorted(vals.items())) for _,w in s['ideal_gates_start_ms_width_ms']) for h,vals in anchor.items()}
    return dict(anchors=anchor,forecasts=forecast,unit='native clear-glass pixel displacement')


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('training',type=Path);a.add_argument('design',type=Path);a.add_argument('output',type=Path)
    v=a.parse_args()
    with v.output.open('x') as f:json.dump(camera_model(v.training,json.loads(v.design.read_text())),f,indent=2);f.write('\n')
