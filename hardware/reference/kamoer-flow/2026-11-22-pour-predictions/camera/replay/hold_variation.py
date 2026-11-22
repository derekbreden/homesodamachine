"""Compare minute-scale movement with the short-window repeatability of each stationary liquid boundary."""
import argparse
import json
from pathlib import Path

import numpy as np
from read_hold import epoch,relative_shift

def variability(d):
    meta=json.loads(str(d['metadata']));t=(d['surface_pts_ns']-meta['begin_ns'])/1e9
    a=d['surface_x4']*.25;ref,_=epoch(a,t,2.35,.35);rows=[]
    for site,m in enumerate(ref):
        anchors=[]
        for lane,p in enumerate(m):
            yy=np.arange(len(p)//2-8,len(p)//2+9);anchors.append(yy[np.argmax(p[yy-2]-p[yy+2])])
        samples=[]
        for mid in np.arange(1.,max(t)-.50,.5):
            observed,n=epoch(a[:,site],t,mid,.245)
            if not n:continue
            estimates=[z for j,c in enumerate(anchors) if (z:=relative_shift(m[j],observed[j],c,12)) is not None and z[1]<.5]
            if len(estimates)>=2:samples.append([float(mid),float(np.median(np.asarray(estimates)[:,0]))])
        val=np.array(samples)
        if len(val)<12:rows.append({'midpoints_s_and_dy_px':samples});continue
        def level(lo,hi):
            chosen=(val[:,0]>=lo)&(val[:,0]<=hi)
            return float(np.median(val[chosen,1])) if chosen.any() else None
        short=[]
        for start in np.arange(2.,max(t)-4.,4.):
            early=level(start,start+.5);late=level(start+3.,start+3.5)
            if early is not None and late is not None:short.append(late-early)
        end=level(max(t)-4.,max(t)-1.);begin=level(2.,5.)
        rows.append({'midpoints_s_and_dy_px':samples,'early_to_late_px':end-begin if begin is not None and end is not None else None,
             'paired_short_windows':len(short),'three_second_absolute_change_95_px':float(np.quantile(np.abs(short),.95)) if short else None})
    return dict(zip(('inner','outer'),rows))
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('files',type=Path,nargs='+');ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();values={}
    for f in a.files:
        with np.load(f) as d:values[f.stem]=variability(d)
    a.out.write_text(json.dumps(values,indent=2)+'\n')
