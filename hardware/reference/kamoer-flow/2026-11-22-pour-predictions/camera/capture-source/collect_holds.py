"""Gather the native optical samples and contemporaneous printed-cup registration for every completed ladder dwell."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from read_pour_timings import read_trace
from stationary_evidence import pack
from timing_window import HERE,Source

def collect():
    j=HERE.parent/'work/graduations.jsonl'
    if not j.is_file():return {}
    windows=HERE/'windows';out=HERE/'evidence';holds={};photos=[]
    for l in j.read_text().splitlines():
        try:r=json.loads(l)
        except json.JSONDecodeError:continue
        if r.get('event')=='hold':holds.setdefault(r['label'],[]).append(r)
        if r.get('event')=='ladder_image':
            w=windows/r['label']/'window.json'
            if w.is_file():photos.append((json.loads(w.read_text())['mid']['pts_ns'],r['label']))
    finished={k:rows for k,rows in holds.items() if max(r['elapsed_s'] for r in rows)>64.}
    if not finished:return {}
    existing=out/'ladder-hold-clock.json'
    if existing.is_file():
        before=json.loads(existing.read_text())
        if set(before)==set(finished):return before
    source=Source(HERE);surface=read_trace(HERE/'direct-inner-contact.csv');outer=read_trace(HERE/'upper-rim.csv')
    with np.load(HERE/'upper-contact-reference.npz') as z:inner_y=float(z['baseline_y'])
    with np.load(HERE/'rim-reference.npz') as z:outer_y=float(np.median(z['rows'][1]))
    result={}
    for label,rows in finished.items():
        begin=round(float(np.median([r['mono_ns']-r['elapsed_s']*1e9 for r in rows])))
        end=begin+65_000_000_000
        if source.pts[-1]<=end+5_000_000_000:continue
        q=(surface['pts_ns']>begin+1e9)&(surface['pts_ns']<begin+3e9)
        t=(outer['pts_ns']>begin+1e9)&(outer['pts_ns']<begin+3e9)
        if not q.any() or not t.any():continue
        centers=[inner_y+float(np.median(surface['inner_shift_px'][q])),outer_y+float(np.median(outer['outer_shift_px'][t]))]
        start_photo=max((pts,w) for pts,w in photos if pts<=begin)[1];last_photo=max(rows,key=lambda r:r['elapsed_s'])['window']
        dest=out/'holds'/(label+'.npz')
        if not dest.is_file():pack(source,label,begin,end,centers)
        ink=out/'hold-ink'/label/'measurements.json'
        if not ink.is_file():
            cmd=[sys.executable,str(HERE/'pack_hold_ink.py'),label,start_photo,last_photo,'--rows',*map(str,centers)]
            subprocess.run(cmd,check=True)
        result[label]={'begin_ns':begin,'end_ns':end,'estimated_roi_centers_native_y':centers,'starting_photograph':start_photo,
                    'hold_photographs':[{'window':r['window'],'elapsed_host_s':r['elapsed_s'],'pts_ns':json.loads((windows/r['window']/'window.json').read_text())['mid']['pts_ns']} for r in rows]}
    dest=out/'ladder-hold-clock.json';tmp=dest.with_suffix('.partial');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(dest)
    return result
if __name__=='__main__':
    print('Archived holds',*collect())
