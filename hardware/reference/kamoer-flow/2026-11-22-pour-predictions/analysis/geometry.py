"""Convert clear-glass rows at two sightlines to nominal volume and forecast complete lever traces."""
import argparse
import json
from pathlib import Path
from statistics import median
import sys

import numpy as np
from PIL import Image

from freeze import interp


def read_window(window,calibration):
    from mark_crossings import clear_lane
    from cup_volume import crop
    gray=np.asarray(crop(window/'average.png').convert('L'))
    readings={}
    for site in ('x990','x1986'):
        row,contrast=clear_lane(gray,int(site[1:]))
        points=sorted(calibration['anchors'][site])
        supported=points[0][0]<=row<=points[-1][0] and contrast>=6
        readings[site]={'row':row,'contrast':contrast,'ml':interp(row,points) if supported else None}
    return readings


def train(training,programs,base,calibration,windows):
    rows=[json.loads(s) for s in training.read_text().splitlines()]
    anchor={h:{} for h in ('A','B')};paired=[]
    for trial in (r for r in rows if r['event']=='trial'):
        h,n=trial['head'],trial['scenario'];s=base['scenarios'][n];sign=1 if h=='B' else -1
        before=read_window(windows/trial['pre'],calibration)
        after=read_window(windows/trial['post'],calibration)
        doses={k:(sign*(after[k]['ml']-b['ml']) if after[k]['ml'] is not None and b['ml'] is not None else None) for k,b in before.items()}
        paired.append(dict(index=trial['index'],head=h,scenario=n,before=before,after=after,dose_ml=doses))
        if doses['x990'] is None or trial['burst_count']!=trial['expected_bursts']:continue
        width=s['ideal_gates_start_ms_width_ms'][0][1]
        anchor[h].setdefault(width,[]).append(doses['x990']/trial['burst_count'])
    out={}
    for h,cells in anchor.items():
        if len(cells)!=4 or min(map(len,cells.values()))<2:raise ValueError(('incomplete geometry calibration',h,cells))
        out[h]={w:median(values) for w,values in cells.items()}
    forecast={}
    for n,s in programs['scenarios'].items():
        if s['phase']!='validation':continue
        forecast[n]={h:sum(interp(w,sorted(cells.items())) for _,w in s['ideal_gates_start_ms_width_ms']) for h,cells in out.items()}
    return {'anchors_ml_per_burst':out,'head_calibration_observations':paired,'forecasts':forecast}


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    for n in ['training','programs','original_design','map','windows','optics_source','output']:a.add_argument(n,type=Path)
    v=a.parse_args(); sys.path.insert(0,str(v.optics_source))
    parsed=lambda x:json.loads(x.read_text())
    result=train(v.training,parsed(v.programs),parsed(v.original_design),parsed(v.map),v.windows)
    import hashlib
    result['source_sha256']={k:hashlib.sha256(getattr(v,k).read_bytes()).hexdigest() for k in ['training','programs','original_design','map']}
    with v.output.open('x') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps(result['forecasts'],indent=1))
