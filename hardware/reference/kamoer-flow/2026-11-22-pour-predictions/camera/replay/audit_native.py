"""Check every indexed recording against the measured native clocks and all three continuous liquid-surface traces."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from read_pour_timings import read_trace
from replay_native import replay


def check_recordings(index,recordings,rim_reference,contact_reference,trace,direct,checkpoint,out):
    files=[recordings / r['file'] for r in json.loads(index.read_text())['groups']]
    state=json.loads(checkpoint.read_text()) if checkpoint.exists() else {}
    summary={}
    with np.load(rim_reference) as src:
        rim={k:src[k] for k in src.files}
    with np.load(contact_reference) as src:
        contact={k:src[k] for k in src.files}
    series=read_trace(trace)
    other=read_trace(direct)
    for number,path in enumerate(files,1):
        checksum=hashlib.sha256(path.read_bytes()).hexdigest()
        if path.name in state and state[path.name]['sha256']==checksum:
            summary[path.name]=state[path.name]
            continue
        s,t,q,u=replay(path,rim,contact)
        ii=np.searchsorted(series['seq'],s)
        jj=np.searchsorted(other['seq'],s)
        if not (np.array_equal(series['seq'][ii],s) and np.array_equal(other['seq'][jj],s)
                and np.array_equal(series['pts_ns'][ii],t) and np.array_equal(other['pts_ns'][jj],t)):
            raise RuntimeError(f'Native frame sequence or timestamp disagrees for {path.name}.')
        if np.any(np.diff(t)<=0) or np.any(np.diff(s)!=1):
            raise RuntimeError(f'Nonconsecutive native sample inside {path.name}.')
        with np.load(path) as src:
            gates=json.loads(str(src['description']))['gates']
        enclosed=all(t[0]<=g['tx_ns']<=g['done_ack_ns']<=t[-1] for g in gates)
        if not enclosed:raise RuntimeError(f'Recording does not bracket all receipts for {path.name}.')
        diff=np.array([np.max(abs(q[:,0,0]-series['inner_shift_px'][ii])),
                       np.max(abs(q[:,1,0]-series['outer_shift_px'][ii])),
                       np.max(abs(u[:,0]-other['inner_shift_px'][jj]))])
        rec={'sha256':checksum,'frames':len(t),'first_pts_ns':int(t[0]),'last_pts_ns':int(t[-1]),'covered_receipts':len(gates),
             'max_abs_replay_difference_px':dict(zip(('inner_template','outer_template','inner_contrast'),np.round(diff,6)))}
        state[path.name]=summary[path.name]=rec
        temp=checkpoint.with_suffix('.partial')
        temp.write_text(json.dumps(state)+'\n')
        temp.replace(checkpoint)
        if number%20==0:print(number,'of',len(files),flush=True)
    result={'groups':summary,'group_count':len(summary),'sample_rows_across_groups':sum(x['frames'] for x in summary.values()),
            'covered_receipts':sum(x['covered_receipts'] for x in summary.values())}
    temp=out.with_suffix('.partial')
    temp.write_text(json.dumps(result,indent=2)+'\n')
    temp.replace(out)
    print({k:v for k,v in result.items() if k!='groups'},flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('index',type=Path);p.add_argument('--recordings',type=Path,required=True)
    p.add_argument('--rim-reference',type=Path,required=True);p.add_argument('--contact-reference',type=Path,required=True)
    p.add_argument('--trace',type=Path,required=True);p.add_argument('--direct',type=Path,required=True)
    p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    v=p.parse_args()
    check_recordings(v.index,v.recordings,v.rim_reference,v.contact_reference,v.trace,v.direct,v.checkpoint,v.out)
