"""Compare cup motion within commanded gates and their following off intervals on native camera timestamps."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from read_band_response import read
def analyze(path):
    d,ns,seq,gs,t,off,pre,fw,bw=read(path)
    if len(gs)<2:return None
    sgn=1 if d['head']=='A' else -1
    ons=(gs[:,0]-gs[0,0])/1e9;offs=(gs[:,2]-gs[0,0])/1e9
    vals=[sgn*fw[:,:,0],sgn*bw[:,:,0]]
    def phase(y,a,b):
        return np.asarray([np.interp(b,t,y[:,k])-np.interp(a,t,y[:,k]) for k in range(2)])
    def both(z0,z1):
        delta=np.asarray([phase(y,z0,z1) for y in vals])
        return np.median(delta,axis=0),np.abs(delta[0]-delta[1])
    def band(v):return [round(float(x),4) for x in v]
    gates=[]
    for j,(on,done) in enumerate(zip(ons,offs)):
        before=ons[j+1] if j+1<len(ons) else None
        a,b=both(on,done);g={'index':j+1,'from_tx_s':round(on,5),'on_s':round(done-on,5),'during_gate_px':band(a),'during_gate_track_difference_px':band(b)}
        for dt in (.10,.16,.20,.25,.35,.50,.70,.95):
            if before is None or on+dt<before-.01:
                y,dd=both(on,on+dt);g[f'from_tx_{round(dt*1000)}ms_px']=band(y);g[f'from_tx_{round(dt*1000)}ms_track_difference_px']=band(dd)
        if before is not None:
            a,b=both(done,before);g['during_off_px']=band(a);g['during_off_track_difference_px']=band(b)
            g['actual_off_s']=round(before-done,5)
        gates.append(g)
    def median(k,skip_first=True):return np.nanmedian([g[k] for g in (gates[1:] if skip_first else gates) if k in g],axis=0).tolist()
    summ={'label':d['label'],'head':d['head'],'gap_ms':d['pause_ms'],'gate_ms':d['on_ms'],'count':len(gs),'signed_axis':'positive is in pumping direction',
        'sightlines':['right','mid'],'during_gate_median_px':median('during_gate_px'),'during_off_median_px':median('during_off_px'),
        'during_gate_directions_disagree_px':median('during_gate_track_difference_px'),'during_off_directions_disagree_px':median('during_off_track_difference_px'),
        'n_frames':len(t),'actual_pause_median_s':float(np.median(ons[1:]-offs[:-1])),'per_gate':gates}
    for dt in (.10,.16,.20,.25,.35,.50,.70,.95):
        k=f'from_tx_{round(dt*1000)}ms_px'
        if sum(k in g for g in gates[1:-1])>3:summ[k]=median(k)
    return summ
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('files',nargs='+',type=Path);p.add_argument('--out',type=Path,required=True);args=p.parse_args();args.out.mkdir(exist_ok=True)
    for f in args.files:
        out=args.out/(f.stem+'.json')
        if out.exists():continue
        r=analyze(f)
        if r is not None:out.write_text(json.dumps(r,indent=2)+'\n')
