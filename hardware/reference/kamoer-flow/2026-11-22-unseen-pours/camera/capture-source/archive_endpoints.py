"""Retain each named exposure's original sensor pixels and verify both calibrated sightlines against its full photograph."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from replay_sights import HERE,check

SITES=(972,990,1018,1036,1986)
COLUMNS=np.concatenate([np.arange(x-4,x+5) for x in SITES])

def digest(buf):return hashlib.sha256(buf).hexdigest()

def capture(camera):
    out=camera/'evidence';endpoints=out/'endpoints';endpoints.mkdir(parents=True,exist_ok=True)
    index=out/'windows.json'
    readings=json.loads(index.read_text()) if index.exists() else {}
    for w in sorted((camera/'windows').iterdir()):
        if w.name in readings or not (w/'window.json').is_file():continue
        metadata=json.loads((w/'window.json').read_text());color=json.loads((w/'color.json').read_text())
        with np.load(w/'sightlines.npz') as z:
            cols=z['sensor_x'];ii=np.searchsorted(cols,COLUMNS)
            if not np.array_equal(cols[ii],COLUMNS):raise ValueError('A calibrated source column is missing.')
            pixels=z['native_luma'][:,ii,:].copy();rows=z['sensor_y'];seq=z['seq'];pts=z['pts_ns']
        if seq.tolist()!=[m['seq'] for m in metadata['frames']] or pts.tolist()!=[m['pts_ns'] for m in metadata['frames']]:
            raise ValueError(f'Image-source clocks disagree at {w.name}.')
        target=endpoints/(w.name+'.npz');pending=target.with_suffix('.partial')
        with pending.open('wb') as f:
            np.savez_compressed(f,native_luma=pixels,sensor_x=COLUMNS,sensor_y=rows,seq=seq,pts_ns=pts)
        verification=check(pending,w/'average.png')
        if not verification['exact_full_photo_agreement']:raise RuntimeError(f'Different photographic read at {w.name}.')
        pending.replace(target)
        avg=np.rint(pixels.mean(axis=0,dtype=np.float32)).astype(np.uint8)
        readings[w.name]={'source':target.name,'sensor_dimensions_order':'frame,column,row',
             'source_pixel_sha256':digest(pixels.tobytes()),'averaged_pixel_sha256':digest(avg.tobytes()),
             'requested_pts_ns':[metadata['target_start_ns'],metadata['target_end_ns']],
             'mid_seq':metadata['mid']['seq'],'mid_pts_ns':metadata['mid']['pts_ns'],'mid_utc':metadata['mid']['utc'],
             'color_seq':color['seq'],'color_pts_ns':color['pts_ns'],'count':len(seq),
             'absolute_ml':verification['geometry'],'exact_full_photo_agreement':True}
    pending=index.with_suffix('.partial');pending.write_text(json.dumps(readings,indent=2)+'\n');pending.replace(index)
    return readings

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('camera',type=Path,nargs='?',default=HERE)
    a=ap.parse_args();print(len(capture(a.camera)),'native endpoint windows')
