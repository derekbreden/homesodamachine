"""Locate the upper clear-to-dark transition directly across the inner native strip of the cup."""
import json
import time
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
SENSOR_X=np.array([1432.5,1471.5,1497.5])
SENSOR_GRID=np.arange(735,1056)
TEMPLATE=np.arange(-10,13)
def measure(samples,y0,reference=None):
    p=np.asarray(samples,dtype=np.float32)
    integral=np.pad(np.cumsum(p,axis=2),((0,0),(0,0),(1,0)))
    grid=SENSOR_GRID[None,:]+np.rint((SENSOR_X-1450)*-.062).astype(int)[:,None]-y0
    bands=np.arange(len(SENSOR_X))[:,None]
    def avg(lo,hi):
        return (integral[:,bands,grid+hi]-integral[:,bands,grid+lo])/(hi-lo)
    above=avg(-22,-8);below=avg(4,18);air=avg(-8,-1);edge=avg(1,6)
    score=np.minimum(above-below,1.45*(air-edge))
    fused=np.median(score,axis=1)
    picks=fused.argmax(axis=1);ids=np.arange(len(samples))
    peaks=fused[ids,picks]
    peak_grid=np.clip(picks,1,len(SENSOR_GRID)-2)
    a=fused[ids,peak_grid-1];b=fused[ids,peak_grid];c=fused[ids,peak_grid+1]
    sub=np.clip((c-a)/np.maximum(1e-5,2*(2*b-a-c)),-.5,.5)
    ys=SENSOR_GRID[picks]+sub
    peer=np.where(np.abs(SENSOR_GRID[None,:]-ys[:,None])>18,fused,-1e4).max(axis=1)
    # Local agreement measures whether separate columns identify the same contrast transition.
    selected=np.abs(SENSOR_GRID[None,None,:]-ys[:,None,None])<7
    local_picks=np.argmax(np.where(selected,score,-1e4),axis=2)
    iqr=np.quantile(local_picks,.75,axis=1)-np.quantile(local_picks,.25,axis=1)
    rows=grid[bands,picks[None,:]].T
    frame_samples=p[ids[:,None,None],np.arange(len(SENSOR_X))[None,:,None],rows[:,:,None]+TEMPLATE]
    zz=frame_samples-frame_samples.mean(axis=2,keepdims=True)
    zz/=np.sqrt(np.sum(zz*zz,axis=2,keepdims=True)).clip(.001)
    corr=np.ones(len(p)) if reference is None else np.median(np.sum(zz*reference[None,:,:],axis=2),axis=1)
    return np.column_stack([ys,peaks,peaks-peer,iqr,corr]),zz

def make_reference():
    import sys
    sys.path.append('/opt/homebrew/lib/python3.13/site-packages')
    from PIL import Image
    image=np.asarray(Image.open(HERE/'windows/station-idle/average.png'),dtype=np.float32)
    samples=np.stack([image[:,int(x-6.5):int(x+6.5)].mean(axis=1) for x in SENSOR_X])
    res,templates=measure(samples[None,:,:],0)
    np.savez_compressed(HERE/'upper-contact-reference.npz',sensor_x=SENSOR_X,baseline_y=res[0,0],shape=templates[0])

def record():
    import csv
    with np.load(HERE/'upper-contact-reference.npz') as ref:
        baseline=float(ref['baseline_y']);shape=ref['shape']
    begin=json.loads((HERE/'windows/station-idle/window.json').read_text())['mid']['pts_ns']
    path=HERE/'direct-inner-contact.csv';last=0
    if path.exists():
        with path.open() as f:
            for row in csv.DictReader(f):last=int(row['seq'])
    with path.open('a',buffering=1) as output:
        writer=csv.writer(output)
        if not last:writer.writerow(['seq','pts_ns','inner_shift_px','step_contrast','competing_step_margin','band_iqr_px','correlation'])
        while (HERE/'port.json').exists():
            files=sorted(f for f in (HERE/'profiles').glob('*.npz') if f.stem.isdigit() and int(f.stem)+124>last)
            for f in files:
                with np.load(f) as z:
                    t=z['pts_ns'];s=z['seq'];m=(t>=begin)&(s>last)
                    if not m.any():continue
                    cap=z['profiles'][m,3][:,[2,5,7],:]
                    result,_=measure(cap.astype(np.float32)*.25,int(z['y0']),shape);result[:,0]-=baseline
                    for j,row in enumerate(result):writer.writerow([int(s[m][j]),int(t[m][j]),*np.round(row,4).tolist()])
                    last=int(s[m][-1])
            time.sleep(.3)

if __name__=='__main__':
    if not (HERE/'upper-contact-reference.npz').is_file():make_reference()
    record()
