"""Track the upper liquid surface independently at two full-rate native image strips."""
import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
SITES=('inner','outer')
INDICES=(3,4)
OFFSETS=np.arange(-190,191)
TEMPLATE=np.arange(-10,13)

def calibration():
    import sys
    sys.path.append('/opt/homebrew/lib/python3.13/site-packages')
    from PIL import Image
    w=HERE/'windows/station-idle'
    image=np.asarray(Image.open(w/'average.png'),dtype=np.float32)
    ref=[];centers=[];bands=[]
    for (x0,x1),(y0,y1) in zip([(1400,1504),(1860,1980)],[(896,889),(872,858)]):
        unit=(x1-x0)//8
        xs=x0+unit*(np.arange(8)+.5)
        expected=np.interp(xs,[x0,x1],[y0,y1])
        r=[];c=[]
        for i,y in enumerate(expected):
            col=image[:,x0+i*unit:x0+(i+1)*unit].mean(1)
            grid=np.arange(round(y)-5,round(y)+6)
            slope=col[grid-2]-col[grid+2]
            at=grid[np.argmax(slope)]
            r.append(col[at+TEMPLATE]);c.append(int(at))
        ref.append(r);centers.append(c);bands.append(xs)
    data=json.loads((w/'window.json').read_text())
    np.savez_compressed(HERE/'rim-reference.npz',profiles=np.array(ref),rows=centers,x=bands,template_offsets=TEMPLATE,reference_pts_ns=data['mid']['pts_ns'])

def track_block(raw,reference,rows,before,y0=450,indices=INDICES):
    obs=raw.astype(np.float32)*.25
    trace=[]
    for station,ix in enumerate(indices):
        last=before[station];ref=reference[station].astype(np.float32)
        ref-=ref.mean(axis=1,keepdims=True)
        ref/=np.sqrt((ref*ref).sum(axis=1,keepdims=True)).clip(.001)
        idx=rows[station,:,None]+TEMPLATE[None,:]-y0
        # Adjacent camera frames have continuous motion. Reacquire globally when a local match is weak.
        vals=[]
        for fr in obs[:,ix]:
            def matches(shifts):
                sampled=fr[np.arange(8)[None,:,None],idx[None,:,:]+shifts[:,None,None]]
                sampled-=sampled.mean(axis=2,keepdims=True)
                denom=np.sqrt(np.sum(sampled*sampled,axis=2)).clip(.001)
                by=np.sum(sampled*ref[None,:,:],axis=2)/denom
                return by,np.median(by,axis=1)
            loc=OFFSETS[abs(OFFSETS-last)<=13]
            corr,fused=matches(loc)
            pick=np.argmax(fused)
            if fused[pick]<.48:
                corr,fused=matches(OFFSETS)
                nearby=fused-.001*np.minimum(abs(OFFSETS-last),50)
                pick=np.argmax(nearby);loc=OFFSETS
            shift=loc[pick]
            if 0<pick<len(loc)-1:
                left,middle,right=fused[pick-1:pick+2]
                den=2*(2*middle-left-right)
                if den>1e-6:shift+=float(np.clip((right-left)/den,-.5,.5))
            local=abs(loc-shift)<=8
            best=loc[local][np.argmax(corr[local],axis=0)]
            vals.append([float(shift),float(fused[pick]),float(np.percentile(best,75)-np.percentile(best,25))])
            last=shift
        before[station]=last;trace.append(vals)
    return np.asarray(trace).transpose(1,0,2)

def record():
    with np.load(HERE/'rim-reference.npz') as z:
        ref=z['profiles'];rows=z['rows'];start=int(z['reference_pts_ns'])
    path=HERE/'upper-rim.csv';before=[0.,0.];last_seq=0
    if path.exists():
        with path.open() as f:
            for row in csv.DictReader(f):
                last_seq=int(row['seq']);before=[float(row['inner_shift_px']),float(row['outer_shift_px'])]
    header=['seq','pts_ns']+[site+'_'+field for site in SITES for field in ('shift_px','correlation','band_iqr_px')]
    with path.open('a',buffering=1) as output:
        writer=csv.writer(output)
        if not last_seq:writer.writerow(header)
        while (HERE/'port.json').exists():
            files=sorted(q for q in (HERE/'profiles').glob('*.npz') if q.stem.isdigit() and int(q.stem)+124>last_seq)
            for f in files:
                with np.load(f) as z:
                    t=z['pts_ns'];seq=z['seq'];keep=(t>=start)&(seq>last_seq)
                    if not keep.any():continue
                    data=track_block(z['profiles'][keep],ref,rows,before)
                    for i,(s,pts) in enumerate(zip(seq[keep],t[keep])):
                        writer.writerow([int(s),int(pts),*[round(float(v),4) for v in data[i].flat]])
                    last_seq=int(seq[keep][-1])
            time.sleep(.25)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['calibrate','record'])
    args=parser.parse_args()
    if args.action=='calibrate':calibration()
    else:record()
