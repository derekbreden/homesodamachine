"""Compare disjoint early and late sensor frames from the same named exposure at both volume sightlines."""
import argparse
import json
from pathlib import Path
import numpy as np
from replay_sights import read_gray,CROP

def part(z,ids):
    x=z['sensor_x'];y=z['sensor_y'];px=z['native_luma'][ids]
    l,t,r,b=CROP;image=np.zeros((b-t,r-l),dtype=np.uint8)
    image[np.ix_(y-t,x-l)]=np.rint(px.mean(axis=0,dtype=np.float32)).astype(np.uint8).T
    return read_gray(image)

def run(folder,receipts=None):
    records={};all_values={}
    for f in sorted(folder.glob('*.npz')):
        with np.load(f) as z:
            n=len(z['seq']);half=n//2
            if not half:continue
            early=part(z,np.arange(half));late=part(z,np.arange(n-half,n));ts=z['pts_ns']
            elapsed=float((np.mean(ts[-half:])-np.mean(ts[:half]))*1e-9)
        report={}
        for site in early:
            a=early[site];b=late[site];delta=float(b['ml']-a['ml']) if a['ml'] is not None and b['ml'] is not None else None
            report[site]={'row_change_px':float(b['row']-a['row']),'nominal_ml_change':delta}
            if delta is not None:all_values.setdefault(site,[]).append(abs(delta))
        records[f.stem]={'early_to_late_centroid_s':elapsed,'disjoint_frames_per_half':half,'sites':report}
    paired={}
    if receipts:
        for journal in receipts.values():
            for item in journal['records']:
                r=item['record']
                if r.get('event')!='trial':continue
                before=records.get(r['start']);after=records.get(r['finish']);sign=1 if r['head']=='B' else -1
                if not (before and after):continue
                trial={}
                for site in ('x990','x1986'):
                    a=before['sites'][site]['nominal_ml_change'];b=after['sites'][site]['nominal_ml_change']
                    trial[site]=sign*(b-a) if a is not None and b is not None else None
                paired[r['label']]={'head':r['head'],'scenario':r['scenario'],'late_minus_early_dose_ml':trial}
    dose_stats={}
    for site in ('x990','x1986'):
        values=[abs(v['late_minus_early_dose_ml'][site]) for v in paired.values() if v['late_minus_early_dose_ml'][site] is not None]
        if values:dose_stats[site]=dict(zip(('median','p90','p95','maximum'),np.percentile(values,[50,90,95,100]).tolist()))
    return {'readout':'Each endpoint average is split into disjoint early and late subaverages with equal counts. Their separation can include residual surface motion. It describes within-exposure repeatability. All scored optical readings continue to use all recorded frames.','absolute_change_ml':{s:dict(zip(('median','p90','p95','maximum'),np.percentile(v,[50,90,95,100]).tolist())) for s,v in all_values.items()},'windows':records,'trials':paired,'absolute_trial_dose_change_ml':dose_stats}
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('recordings',type=Path);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--receipts',type=Path);v=ap.parse_args()
    v.out.write_text(json.dumps(run(v.recordings,json.loads(v.receipts.read_text()) if v.receipts else None),indent=2)+'\n')
