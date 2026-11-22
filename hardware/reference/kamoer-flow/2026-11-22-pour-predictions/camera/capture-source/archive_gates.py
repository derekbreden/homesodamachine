"""Retain compact native image evidence across contiguous groups of acknowledged pump commands."""
import argparse
import bisect
import csv
import json
import re
from pathlib import Path

import numpy as np

from timing_window import HERE, Source, physical_gates
from native_profiles import compress,write

def intervals(gates,front=.75,tail=5.0):
    groups=[]
    for g in gates:
        start=g['tx_ns']-round(front*1e9);end=g['done_ack_ns']+round(tail*1e9)
        if groups and groups[-1][1]>=start and end-groups[-1][0]<35e9:
            groups[-1][1]=max(groups[-1][1],end);groups[-1][2].append(g)
        else:groups.append([start,end,[g]])
    return groups

def write_group(source,output,start,end,gates,latest):
    lower=source.clock[max(0,bisect.bisect_left(source.pts,start)-1)][1]
    upper=source.clock[min(len(source.clock)-1,bisect.bisect_right(source.pts,end))][1]
    lo=max(0,bisect.bisect_right(source.first_seq,lower)-1)
    hi=bisect.bisect_right(source.first_seq,upper)
    ts=[];seq=[];traces=[]
    for f in source.files[lo:hi]:
        with np.load(f) as z:
            ticks=z['pts_ns'];selected=(ticks>=start)&(ticks<=end)
            if not selected.any():continue
            # Every lane and row searched by the two native surface readers is preserved.
            traces.append(z['profiles'][selected,3:5,:,646-450:1111-450])
            ts.append(ticks[selected]);seq.append(z['seq'][selected]);bounds=z['slices'][3:5]
    if not ts:return False
    ts=np.concatenate(ts);seq=np.concatenate(seq)
    if ts[0]>start+100e6 or ts[-1]<end-100e6:return False
    unit=(bounds[:,1]-bounds[:,0])//8
    starts=bounds[:,:1]+unit[:,None]*np.arange(8)[None,:]
    loc=np.stack([starts,starts+unit[:,None]],axis=2)
    if int(seq[0])-1 not in latest:return False
    meta={'start_ns':int(start),'end_ns':int(end),'gates':gates,'encoding':'native_delta_v1','prior_tracker_offsets_px':latest[int(seq[0])-1],
          'sampling':'Decode integer frames using native_profiles.recover. Each uint16 is the rounded native mean luma times four over its indicated horizontal sensor interval. Every camera frame in the interval is retained.'}
    tmp=output.with_suffix('.partial')
    with tmp.open('wb') as out:
        write(out,**compress(np.concatenate(traces)),native_pts_ns=ts,native_seq=seq,
                            sensor_x_intervals=loc,sensor_rows=np.arange(646,1111),
                            description=np.asarray(json.dumps(meta)))
    tmp.replace(output)
    return True

def archive(folder,final):
    out=folder/'evidence'/'gate-profiles';out.mkdir(parents=True,exist_ok=True)
    source=Source(folder)
    latest={}
    with (folder/'upper-rim.csv').open() as f:
        for r in csv.DictReader(f):
            if r.get('outer_shift_px'):latest[int(r['seq'])]=[float(r['inner_shift_px']),float(r['outer_shift_px'])]
    gates=physical_gates((folder.parent/'work').glob('*.jsonl'))
    groups=intervals(gates)
    covered=[];index=[]
    for begin,end,records in groups:
        if source.pts[-1]<end+(4.5 if final else 12.)*1e9:continue
        label=records[0].get('event_label') or records[0].get('label_at_tx') or records[0]['journal']
        label=re.sub(r'[^a-zA-Z0-9-]+','-',label)
        target=out/(str(records[0]['tx_ns'])+'-'+label+'.npz')
        valid=False
        if target.exists():
            with np.load(target) as existing:
                stored=json.loads(str(existing['description']))
                signature=lambda g:(g['kind'],g['tx_ns'],g.get('start_ack_ns'),g['done_ack_ns'],g.get('board_ms'),g.get('reported_bursts'))
                valid=stored.get('encoding')=='native_delta_v1' and stored['start_ns']==begin and stored['end_ns']==end and list(map(signature,stored['gates']))==list(map(signature,records))
        if not valid and not write_group(source,target,begin,end,records,latest):continue
        covered.extend(g['tx_ns'] for g in records)
        index.append({'file':target.name,'first_tx_ns':records[0]['tx_ns'],'last_done_ns':records[-1]['done_ack_ns'],'gates':len(records)})
    record={'acknowledged_commands_seen':len(gates),'archived_commands':len(covered),
            'direct_gate_count':sum(g['kind']=='direct_gate' for g in gates),
            'metered_pour_count':sum(g['kind']=='metered_pour' for g in gates),'groups':index,
            'unarchived_command_times_ns':sorted(set(x['tx_ns'] for x in gates)-set(covered))}
    dest=out.parent/'gate-index.json';tmp=dest.with_suffix('.tmp')
    tmp.write_text(json.dumps(record,indent=2)+'\n');tmp.replace(dest)
    return record

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--camera',default=HERE,type=Path);ap.add_argument('--final',action='store_true')
    a=ap.parse_args();res=archive(a.camera,a.final);print(res['archived_commands'],'of',res['acknowledged_commands_seen'])
