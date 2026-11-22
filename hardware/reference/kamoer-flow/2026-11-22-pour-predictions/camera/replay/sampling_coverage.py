"""Audit camera cadence inside the recorded appliance and direct positioning intervals."""
import argparse
import csv
import gzip
import json
from pathlib import Path

import numpy as np

def report(path,timeline):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt') as f:
        points=[(int(r['seq']),int(r['pts_ns']),int(r['host_ns'])) for r in csv.DictReader(f) if r.get('pts_ns') and r.get('host_ns')]
    c=np.asarray(points,dtype=np.int64);seq,pts,host=c.T;intervals=np.diff(pts)/1e6
    counts={};wide=[]
    for g in [*timeline['direct'],*timeline['pours']]:
        kind=g['kind'];first=g.get('start_ack_ns',g['tx_ns']);last=g['done_ack_ns']
        i=np.searchsorted(pts,first,'right')-1;j=np.searchsorted(pts,last)
        if i<0 or j>=len(pts):continue
        sample=intervals[i:j];m=float(np.max(sample)) if len(sample) else None
        raw=counts.setdefault(kind,{'captured':0,'max_active_spacing_ms':0.,'active_windows_with_55ms_gap':0,'active_windows_with_100ms_gap':0})
        raw['captured']+=1
        if m is not None:
            raw['max_active_spacing_ms']=max(raw['max_active_spacing_ms'],m)
            if m>55:
                raw['active_windows_with_55ms_gap']+=1
                wide.append({'label':g.get('event_label',g.get('label_at_tx')),'journal':g['journal'],'kind':kind,'max_active_spacing_ms':m})
            if m>100:raw['active_windows_with_100ms_gap']+=1
        if kind=='metered_pour':
            for name,when,lo,hi in [('pre',first,-.58,-.08),('early',first,1.55,1.90),('near_closure',last,-.17,.17),('settled',last,2.35,3.1)]:
                n=int(np.searchsorted(pts,when+hi*1e9)-np.searchsorted(pts,when+lo*1e9))
                counts_per=raw.setdefault('source_frame_count_range',{}).setdefault(name,[n,n])
                counts_per[0]=min(counts_per[0],n);counts_per[1]=max(counts_per[1],n)
    return {'native_records':len(pts),'native_fps':float((len(pts)-1)*1e9/(pts[-1]-pts[0])),
            'pts_ms_percentiles':dict(zip(['median','p95','p99','max'],np.percentile(intervals,[50,95,99,100]).tolist())),
            'callback_ms_percentiles':dict(zip(['median','p95','p99'],np.percentile((host-pts)/1e6,[50,95,99]).tolist())),
            'intervals':counts,'active_wide_frame_spacings':wide}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('frames',type=Path);p.add_argument('timeline',type=Path);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.write_text(json.dumps(report(a.frames,json.loads(a.timeline.read_text())),indent=2)+'\n')
