"""Pack native camera profiles, absolute frame times and motor receipts for an independently replayable interval."""
import argparse
import bisect
import csv
import json
import re
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
def physical_gates(journals):
    gates={}
    for journal in sorted(journals):
        active=None;label=None;pour=None;prediction={}
        for ix,line in enumerate(journal.read_text().splitlines()):
            try:r=json.loads(line)
            except json.JSONDecodeError:continue
            if r.get('label'):label=r['label']
            if r.get('event')=='prediction':
                prediction={k:r[k] for k in ('label','phase','index','block','level','scenario','head','pre','ideal_bursts','forecast_ml','target_start_ml') if k in r}
            command=re.fullmatch(r'pump ([ab]) (\d+)',r.get('command','')) if r.get('event')=='tx' else None
            if command:
                active={'kind':'direct_gate','tx_ns':r['mono_ns'],'head':command[1].upper(),'requested_ms':int(command[2]),'journal':journal.name,'label_at_tx':label}
                gates[active['tx_ns']]=active
            if active and r.get('event')=='rx':
                if re.search(r'pump [AB] at full for',r['line']):active['start_ack_ns']=r['mono_ns']
                done=re.search(r'pump [AB] done after (\d+) ms',r['line'])
                if done:
                    active['done_ack_ns']=r['mono_ns'];active['board_ms']=int(done[1]);active=None
            if 'tx_ns' in r and r['tx_ns'] in gates and 'done_ack_ns' in r:
                g=gates[r['tx_ns']];g['event_label']=r.get('label');g['event']=r.get('event')
                for key in ('start_ack_ns','done_ack_ns','board_ms'):g[key]=r.get(key,g.get(key))
            meter=re.fullmatch(r'flow (\d+) (\d+)',r.get('command','')) if r.get('event')=='tx' else None
            if meter:
                flow={'transmitted_ns':r['mono_ns'],'pulses':int(meter[1]),'command_seconds':int(meter[2])}
                if flow['pulses'] and pour is None:
                    pour={'kind':'metered_pour','tx_ns':r['mono_ns'],'journal':journal.name,'event_label':label,
                          'prediction':dict(prediction),'meter_stages':[]}
                if pour is not None:pour['meter_stages'].append(flow)
            if pour is not None and r.get('event')=='board_pour_start':
                pour.update(start_ack_ns=r['mono_ns'],head=r['head'],ratio=r['ratio'],first_on_ms=r['first_on'],first_off_ms=r['first_off'])
            if pour is not None and r.get('event')=='board_pour_end':
                pour.update(done_ack_ns=r['mono_ns'],elapsed_ms=r['elapsed_ms'],reported_bursts=r['bursts'])
                gates[pour['tx_ns']]=pour;pour=None
    return sorted((g for g in gates.values() if 'done_ack_ns' in g),key=lambda r:r['tx_ns'])

class Source:
    def __init__(self,folder):
        self.folder=folder
        self.files=sorted(f for f in (folder/'profiles').glob('*.npz') if f.stem.isdigit())
        self.first_seq=[int(f.stem) for f in self.files]
        with (folder/'frames.csv').open() as csv_file:
            self.clock=[(int(r['pts_ns']),int(r['seq'])) for r in csv.DictReader(csv_file) if r.get('seq') and r.get('pts_ns')]
        self.pts=[r[0] for r in self.clock]

    def copy(self,output,start,end,top,bottom,receipts):
        i0=max(0,bisect.bisect_left(self.pts,start)-1)
        i1=min(len(self.pts)-1,bisect.bisect_right(self.pts,end))
        j0=max(0,bisect.bisect_right(self.first_seq,self.clock[i0][1])-1)
        j1=bisect.bisect_right(self.first_seq,self.clock[i1][1])
        raw=[];pts=[];seq=[]
        for f in self.files[j0:j1]:
            with np.load(f) as z:
                ticks=z['pts_ns'];sel=(ticks>=start)&(ticks<=end)
                if sel.any():
                    y0=int(z['y0']);y1=int(z['y1'])
                    if not y0<=top<bottom<=y1:raise ValueError('Rows outside the native acquisition')
                    raw.append(z['profiles'][sel,:,:,top-y0:bottom-y0])
                    pts.append(ticks[sel]);seq.append(z['seq'][sel]);slices=z['slices']
        if not raw:raise ValueError('No native camera samples in the requested interval')
        pts=np.concatenate(pts);seq=np.concatenate(seq)
        if start<pts[0]-300_000_000 or end>pts[-1]+300_000_000:
            raise ValueError('The requested native interval is not fully written')
        output.parent.mkdir(exist_ok=True,parents=True)
        with output.with_suffix('.partial').open('wb') as f:
            np.savez_compressed(f,profiles=np.concatenate(raw),pts_ns=pts,seq=seq,slices=slices,y0=top,y1=bottom,
                timing=np.asarray(json.dumps({'start_requested_ns':start,'end_requested_ns':end,'gates':receipts})),
                sample=np.asarray('Native luma times four, horizontal mean within each of eight adjacent bands per sightline; rows increase downward.'))
        output.with_suffix('.partial').replace(output)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('label');ap.add_argument('start_ns',type=int);ap.add_argument('end_ns',type=int)
    ap.add_argument('--top',type=int,default=720);ap.add_argument('--bottom',type=int,default=1130)
    ap.add_argument('--camera',type=Path,default=HERE)
    a=ap.parse_args()
    if not re.fullmatch(r'[\w.-]+',a.label) or a.end_ns<=a.start_ns:raise ValueError('Invalid range or label')
    src=Source(a.camera)
    gates=physical_gates((a.camera.parent/'work').glob('*.jsonl'))
    selected=[g for g in gates if g['tx_ns']<=a.end_ns and a.start_ns<=g['done_ack_ns']]
    out=a.camera/'timing'/(a.label+'.npz')
    src.copy(out,a.start_ns,a.end_ns,a.top,a.bottom,selected)
    print(out)

if __name__=='__main__':main()
