"""Reconstruct scene disturbances and native camera cadence during the physical reset."""
import argparse,datetime,json
from pathlib import Path
import numpy as np
def iso(ns):
    return datetime.datetime.fromtimestamp(ns/1e9,datetime.timezone.utc).isoformat(timespec='milliseconds')
def analyze(path):
    with np.load(path,allow_pickle=False) as source:
        t=source['sample_pts_ns'];delta=int(source['wall_offset_ns']);p=source['native_pts_ns'];data=source['luma_sum'].astype(np.float32)/20
        anchors=json.loads(str(source['anchors']));s=source['native_seq']
    k=np.clip(np.searchsorted(t,t-10**9),0,len(t)-1);change=np.mean(np.abs(data-data[k]),axis=(1,2,3))
    hot=np.flatnonzero(change>10);runs=np.split(hot,np.flatnonzero(np.diff(hot)>8)+1)
    return dict(first_utc=iso(p[0]+delta),last_utc=iso(p[-1]+delta),native_frames=len(p),max_gap_ms=float(np.max(np.diff(p))/1e6),seq_skips=int(np.sum(np.diff(s)>1)),
           large_dry_scene_changes=[{'first':iso(t[q[0]]+delta),'last':iso(t[q[-1]]+delta),'peak_mean_absolute_luma_difference':round(float(np.max(change[q])),3)} for q in runs if len(q)],
           anchored_windows={n:[iso(lo+delta),iso(hi+delta)] for n,(lo,hi) in anchors.items()})
if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('recording',type=Path);a.add_argument('--out',type=Path);args=a.parse_args();txt=json.dumps(analyze(args.recording),indent=2)+'\n'
    if args.out:args.out.write_text(txt)
    else:print(txt,end='')
