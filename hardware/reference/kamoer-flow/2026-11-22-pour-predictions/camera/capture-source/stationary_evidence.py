"""Preserve measured liquid and dry printed rows throughout a stationary optical hold."""
import argparse
import bisect
import json
from pathlib import Path

import numpy as np

from timing_window import HERE,Source

def pack(source,label,start,end,centers):
    lo=max(0,bisect.bisect_left(source.pts,start)-1);hi=min(len(source.pts)-1,bisect.bisect_right(source.pts,end))
    begin=max(0,bisect.bisect_right(source.first_seq,source.clock[lo][1])-1)
    finish=bisect.bisect_right(source.first_seq,source.clock[hi][1])
    t=[];seq=[];raw=[];ink=[];ink_times=[];ink_seq=[];wide=[];wide_times=[];wide_seq=[]
    for f in source.files[begin:finish]:
        with np.load(f) as z:
            ticks=z['pts_ns'];n=z['seq'];use=(ticks>=start)&(ticks<=end)
            if not use.any():continue
            a=z['profiles'];slices=z['slices'];s=n[use];q=ticks[use];images=a[use]
            lanes=np.stack([images[:,3+i][:,[0,2,5,7],round(c)-75-450:round(c)+76-450] for i,c in enumerate(centers)],axis=1)
            t.append(q);seq.append(s);raw.append(lanes)
            keep=s%10==0
            if keep.any():
                ink.append(images[keep,:2,:,500-450:784-450]);ink_times.append(q[keep]);ink_seq.append(s[keep])
            every_second=s%30==0
            if every_second.any():
                wide.append(images[every_second,3:5,:,646-450:1111-450]);wide_times.append(q[every_second]);wide_seq.append(s[every_second])
    if not raw:raise ValueError('Empty native hold window')
    t=np.concatenate(t);seq=np.concatenate(seq)
    if t[0]>start+100e6 or t[-1]<end-100e6:raise ValueError('Native hold is incomplete')
    out=source.folder/'evidence/holds';out.mkdir(parents=True,exist_ok=True)
    dst=out/(label+'.npz');tmp=dst.with_suffix('.partial')
    with tmp.open('wb') as f:
        np.savez_compressed(f,surface_x4=np.concatenate(raw),surface_pts_ns=t,surface_seq=seq,
            surface_sites=slices[[3,4]],surface_band_indices=[0,2,5,7],
            surface_y=np.array([np.arange(round(c)-75,round(c)+76) for c in centers]),
            wide_surface_x4=np.concatenate(wide),wide_pts_ns=np.concatenate(wide_times),wide_seq=np.concatenate(wide_seq),wide_y=np.arange(646,1111),
            dry_ink_x4=np.concatenate(ink),dry_pts_ns=np.concatenate(ink_times),dry_seq=np.concatenate(ink_seq),
            dry_sites=slices[:2],dry_y=np.arange(500,784),metadata=np.asarray(json.dumps({'label':label,
            'begin_ns':start,'end_ns':end,'coordinates':'upright native sensor; bands are eight adjacent equal-width column means; luma times four'})))
    tmp.replace(dst);return dst

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('label');ap.add_argument('begin_ns',type=int);ap.add_argument('end_ns',type=int)
    ap.add_argument('inner_center_row',type=float);ap.add_argument('outer_center_row',type=float);ap.add_argument('--camera',default=HERE,type=Path)
    a=ap.parse_args();print(pack(Source(a.camera),a.label,a.begin_ns,a.end_ns,[a.inner_center_row,a.outer_center_row]))
