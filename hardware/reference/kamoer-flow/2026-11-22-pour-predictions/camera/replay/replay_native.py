"""Rebuild both surface tracks from losslessly stored native luma and compare source timestamps."""
import argparse
import json
from pathlib import Path

import numpy as np
from native_profiles import recover
from read_pour_timings import read_trace
from rim_measure import track_block
from upper_contact import measure

def replay(recording,reference,contact):
    with np.load(recording) as z:
        meta=json.loads(str(z['description']));y0=int(z['sensor_rows'][0]);raw=recover(z)
        t=z['native_pts_ns'].copy();seq=z['native_seq'].copy()
    tracks=track_block(raw,reference['profiles'],reference['rows'],list(meta['prior_tracker_offsets_px']),y0,(0,1))
    upper,_=measure(raw[:,0][:,[2,5,7],:].astype(np.float32)*.25,y0,contact['shape'])
    upper[:,0]-=float(contact['baseline_y'])
    return seq,t,tracks,upper

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('recording',type=Path,nargs='+')
    p.add_argument('--rim-reference',type=Path,required=True);p.add_argument('--contact-reference',type=Path,required=True)
    p.add_argument('--trace',type=Path,required=True);p.add_argument('--direct',type=Path,required=True)
    p.add_argument('--out',type=Path)
    v=p.parse_args();ref=np.load(v.rim_reference);contact=np.load(v.contact_reference)
    series=read_trace(v.trace);other=read_trace(v.direct);summary={}
    for f in v.recording:
        s,t,q,u=replay(f,ref,contact);ii=np.searchsorted(series['seq'],s);jj=np.searchsorted(other['seq'],s)
        if not np.array_equal(t,series['pts_ns'][ii]) or not np.array_equal(t,other['pts_ns'][jj]):raise RuntimeError(f'Camera times disagree at {f}')
        diffs=[np.max(abs(q[:,0,0]-series['inner_shift_px'][ii])),np.max(abs(q[:,1,0]-series['outer_shift_px'][ii])),np.max(abs(u[:,0]-other['inner_shift_px'][jj]))]
        summary[f.name]={'frames':len(t),'max_abs_replay_difference_px':dict(zip(['inner_template','outer_template','inner_contrast'],[round(float(x),6) for x in diffs]))}
    out=json.dumps(summary,indent=2)+'\n'
    if v.out:v.out.write_text(out)
    else:print(out,end='')
