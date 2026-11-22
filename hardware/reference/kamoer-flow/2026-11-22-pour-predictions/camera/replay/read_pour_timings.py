"""Compare settled, release and ring-down surface motion from native camera timestamps and appliance receipts."""
import argparse
import csv
import gzip
import json
from pathlib import Path

import numpy as np

SITES=('inner','outer')
def read_trace(path):
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt') as f:
        rows=list(csv.reader(f))
    names=rows[0]
    a=np.asarray(rows[1:])
    return {k:(a[:,n].astype('i8') if k in ('seq','pts_ns') else a[:,n].astype(float)) for n,k in enumerate(names)}

def replace_inner(original,direct):
    seq,io,ia=np.intersect1d(original['seq'],direct['seq'],assume_unique=True,return_indices=True)
    if not np.array_equal(original['pts_ns'][io],direct['pts_ns'][ia]):raise ValueError('Camera source times disagree')
    out={k:v[io] for k,v in original.items()}
    out['inner_shift_px']=direct['inner_shift_px'][ia];out['inner_correlation']=direct['correlation'][ia]
    out['inner_band_iqr_px']=direct['band_iqr_px'][ia];return out

def bounds(t,when,lo,hi):
    return slice(np.searchsorted(t,when+round(lo*1e9)),np.searchsorted(t,when+round(hi*1e9)))

def median(series,k,when,lo,hi):
    field=series[k][bounds(series['pts_ns'],when,lo,hi)]
    return float(np.median(field)) if len(field)>=3 else None

def wave(series,site,when):
    sl=bounds(series['pts_ns'],when,.10,1.30)
    t=(series['pts_ns'][sl]-when)*1e-9;y=series[site+'_shift_px'][sl]
    if len(t)<25:return None
    line=np.c_[np.ones(len(t)),t];err=y-line@np.linalg.lstsq(line,y,rcond=None)[0]
    peak=None
    for frequency in np.arange(2.,4.001,.025):
        phase=2*np.pi*frequency*t;x=np.c_[line,np.cos(phase),np.sin(phase)]
        coef=np.linalg.lstsq(x,y,rcond=None)[0];left=y-x@coef
        r2=1-float(left@left)/max(1e-12,float(err@err))
        if peak is None or r2>peak[0]:peak=(r2,float(frequency),float(np.hypot(*coef[2:])))
    return {'frequency_hz':peak[1],'amplitude_px':peak[2],'fraction_of_detrended_variance':peak[0],'samples':len(t)}

def blank(trace,reference,stop):
    results={}
    for site in SITES:
        k=site+'_shift_px';deltas=[];amps=[]
        for when in range(int(reference),int(stop-4e9),4_000_000_000):
            a=median(trace,k,when,0,1);b=median(trace,k,when,3,4);w=wave(trace,site,when+1_000_000_000)
            if a is not None and b is not None:deltas.append(b-a)
            if w:amps.append(w['amplitude_px'])
        results[site]=dict(pairs=len(deltas),signed_median_px=float(np.median(deltas)),
             absolute_95_px=float(np.quantile(np.abs(deltas),.95)),max_abs_px=float(np.max(np.abs(deltas))),
             stationary_harmonic_amplitude_95_px=float(np.quantile(amps,.95)))
    return results

def measure(trace,pour):
    start=pour['start_ack_ns'];done=pour['done_ack_ns']
    if trace['pts_ns'][-1]<done+3_100_000_000:return None
    final_zero=[v['transmitted_ns'] for v in pour['meter_stages'] if not v['pulses']]
    if not final_zero:return None
    crit={'early':(start,1.55,1.9),'release':(final_zero[-1],-.20,.04),'closure':(done,-.17,.17),
          'closure_plus_short':(done,.50,.85),'settled':(done,2.35,3.10)}
    template=pour['predicted_switches_ms']
    expected_last=start+sum(template[-1])*1_000_000 if len(template)==pour['reported_bursts'] and template else None
    out={}
    for site in SITES:
        k=site+'_shift_px';pre=median(trace,k,start,-.58,-.08);sign=1 if pour['head']=='A' else -1
        if pre is None:continue
        vals={m:median(trace,k,*window) for m,window in crit.items()}
        if any(v is None for v in vals.values()):continue
        rec={key:sign*(v-pre) for key,v in vals.items()};rec['raw_pre_relative_to_reference_px']=pre
        rec['release_to_closure_px']=rec['closure']-rec['release']
        rec['closure_to_settled_px']=rec['settled']-rec['closure']
        rec['short_to_settled_px']=rec['settled']-rec['closure_plus_short']
        rec['terminal_corr']=median(trace,site+'_correlation',done,2.35,3.10)
        rec['terminal_iqr_px']=median(trace,site+'_band_iqr_px',done,2.35,3.10)
        rec['temporal_harmonic']=wave(trace,site,expected_last) if expected_last else None
        out[site]=rec
    return {'label':pour['event_label'],'head':pour['head'],'phase':pour['prediction'].get('phase'),'journal':pour['journal'],
            'scenario':pour['prediction'].get('scenario'),'block':pour['prediction'].get('block'),'index':pour['prediction'].get('index'),
            'level':pour['prediction'].get('level') or (pour.get('trial') or {}).get('level'),
            'board_bursts':pour['reported_bursts'],'ideal_count_matches':len(template)==pour['reported_bursts'],
            'recorded_trial':bool(pour.get('trial')),'sites':out}

def analyze(trace,timeline):
    stop=min(g['tx_ns'] for g in timeline['direct'])
    obs=[row for pour in timeline['pours'] if (row:=measure(trace,pour))]
    return {'blank':blank(trace,timeline['reference_pts_ns'],stop),'trials':obs}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('trace',type=Path);ap.add_argument('timeline',type=Path);ap.add_argument('--out',required=True,type=Path)
    ap.add_argument('--inner-contact',type=Path);ap.add_argument('--training-only',action='store_true')
    q=ap.parse_args();trace=read_trace(q.trace)
    if q.inner_contact:trace=replace_inner(trace,read_trace(q.inner_contact))
    timeline=json.loads(q.timeline.read_text())
    if q.training_only:timeline['pours']=[p for p in timeline['pours'] if p['prediction'].get('phase')=='training']
    result=analyze(trace,timeline)
    tmp=q.out.with_suffix('.partial');tmp.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');tmp.replace(q.out)
