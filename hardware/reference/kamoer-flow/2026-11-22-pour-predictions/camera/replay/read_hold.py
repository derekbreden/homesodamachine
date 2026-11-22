"""Measure late upper-surface drift against a local exposure and compare dry printed registration."""
import argparse
import json
from pathlib import Path

import numpy as np

def relative_shift(ref,obs,x,half=10,limit=9):
    offsets=np.arange(-limit,limit+.001,.05);rows=round(x)+np.arange(-half,half+1)
    if rows[0]-limit<0 or rows[-1]+limit>=len(ref):return None
    base=ref[rows];base=base-base.mean()
    if base.std()<1.4:return None
    base/=base.std()
    sampled=np.interp(rows[None,:]+offsets[:,None],np.arange(len(obs)),obs)
    sampled-=sampled.mean(axis=1,keepdims=True);sampled/=sampled.std(axis=1,keepdims=True).clip(.01)
    err=np.mean((sampled-base)**2,axis=1);i=err.argmin()
    if i in (0,len(err)-1):return None
    return float(offsets[i]),float(np.sqrt(err[i]))

def epoch(arr,t,mid,half):
    mask=(t>=mid-half)&(t<=mid+half)
    return (np.median(arr[mask],axis=0),int(mask.sum())) if mask.any() else (None,0)

def result(d):
    meta=json.loads(str(d['metadata']));start=meta['begin_ns'];stop=(meta['end_ns']-start)/1e9
    t=(d['surface_pts_ns']-start)/1e9;ti=(d['dry_pts_ns']-start)/1e9
    surface=d['surface_x4']*.25;dry=d['dry_ink_x4']*.25;surface_y=d['surface_y'];dry_y=d['dry_y']
    ref,_=epoch(surface,t,2.35,.35);ink_ref,_=epoch(dry,ti,2.35,.65)
    schedule=[(.50,.30),(2.35,.35),(5.,.5),(10.,.5),(20.,.65),(30.,.65),(45.,.65),(59.,.8)]
    if stop>60:schedule.append((stop-.7,.6))
    res=[]
    for mid,half in schedule:
        observed,n=epoch(surface,t,mid,half);ink,ni=epoch(dry,ti,mid,max(half,.65))
        if not n or not ni:continue
        measurements=[]
        for ix in range(2):
            lane=[]
            for j,rf in enumerate(ref[ix]):
                at=len(rf)//2;yy=np.arange(at-8,at+9);slope=rf[yy-2]-rf[yy+2]
                center=yy[np.argmax(slope)];q=relative_shift(rf,observed[ix,j],center,12)
                if q:lane.append(q)
            q=np.array(lane)
            measurements.append(None if q.size==0 else {'dy_native_px':float(np.median(q[:,0])),
                'between_lane_range_px':[float(q[:,0].min()),float(q[:,0].max())],
                'normalized_shape_residual':float(np.median(q[:,1])),'good_lanes':int((q[:,1]<.5).sum())})
        print_strokes={}
        for ix,(name,candidates) in enumerate([('right',[551,765]),('left',[553,690])]):
            info=[]
            for anchor in candidates:
                per=[]
                for j,rf in enumerate(ink_ref[ix]):
                    ii=round(anchor-dry_y[0]);area=np.arange(ii-8,ii+9)
                    center=area[np.argmax(abs(rf[area-1]-rf[area+1]))];z=relative_shift(rf,ink[ix,j],center,8,4)
                    if z is not None and z[1]<.5:per.append(z)
                if len(per)>=3:info.append({'row':anchor,'dy_px':float(np.median(np.array(per)[:,0])),'lanes':len(per)})
            print_strokes[name]=info
        res.append({'seconds':mid,'surface_frames':n,'print_frames':ni,'surfaces':dict(zip(('inner','outer'),measurements)),'dry_luma_anchors':print_strokes})
    return {'label':meta['label'],'relative_to_hold_s':2.35,'epochs':res}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('files',type=Path,nargs='+');ap.add_argument('--out',type=Path)
    a=ap.parse_args();out={}
    for f in a.files:
        with np.load(f) as d:out[f.stem]=result(d)
    txt=json.dumps(out,indent=2)+'\n'
    if a.out:a.out.write_text(txt)
    else:print(txt,end='')
