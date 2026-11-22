"""Summarize native and preview upper-rim movement at electrical gate boundaries and after settling."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from read_rewired import read
def rows(path):
    meta,sites=read(path)
    gates=np.asarray(meta.get('gates',[[meta['tx_ns'],meta['start_ack_ns'],meta['done_ack_ns'],meta['board_ms']]]))
    sign=1 if meta['channel']=='A' else -1
    for name,(summary,data) in sites.items():
        t=data[:,1];z=data[:,5]*sign
        relative=lambda ns:float(np.interp(ns,t,z))
        def median_between(start,end):
            mask=(t>=start)&(t<=end)
            return float(np.median(z[mask])) if mask.any() else None
        for i,g in enumerate(gates):
            start,ack,done,width=g
            following=gates[i+1,0] if i+1<len(gates) else None
            next_dx=relative(following)-relative(done) if following is not None else None
            final=median_between(done+3.9e9,done+4.1e9) if i==len(gates)-1 else None
            yield [meta['label'],meta['channel'],meta.get('condition'),meta.get('score_accepted'),i+1,len(gates),name,start,ack,done,width,(following-done)/1e6 if following is not None else None,
                   relative(start),relative(done),relative(done)-relative(start),next_dx,final,summary['pre_frame_sd_px']]
if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('files',type=Path,nargs='+');a.add_argument('--out',type=Path,required=True);q=a.parse_args()
    with q.out.open('w',newline='') as o:
        fw=csv.writer(o);fw.writerow(['sequence','head','condition','accepted_operational_endpoint','pulse_index','pulses_in_sequence','sightline','tx_ns','start_ack_ns','done_ack_ns','board_gate_ms','observed_next_gap_ms','positive_motion_at_tx_px','positive_motion_at_done_px','during_gate_px','during_following_off_px','four_second_total_px','pre_frame_sd_px'])
        for path in q.files:fw.writerows(rows(path))
