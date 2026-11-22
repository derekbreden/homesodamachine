"""Recalculate camera timing outcomes from the current traces and the recorded appliance timeline."""
import json
from pathlib import Path

import numpy as np
from read_pour_timings import SITES,analyze,read_trace,replace_inner
from score_fill_timing import score as fill_score
from score_optics import describe,score
from timeline import prepare
from timing_window import HERE

def write(path,value):
    tmp=path.with_suffix('.partial');tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');tmp.replace(path)

def program_summaries(results):
    result={}
    keys={(r['phase'],r['scenario'],r['head'],r.get('level')) for r in results['trials']}
    for phase,scenario,head,level in sorted(keys,key=lambda x:tuple(str(i) for i in x)):
        group=[r for r in results['trials'] if (r['phase'],r['scenario'],r['head'],r.get('level'))==(phase,scenario,head,level)]
        out={}
        for site in SITES:
            usable=[r['sites'][site] for r in group if site in r['sites'] and r['recorded_trial']]
            if not usable:continue
            waves=[r['temporal_harmonic'] for r in usable if r['temporal_harmonic']]
            floor=results['blank'][site]['stationary_harmonic_amplitude_95_px']
            distinguishable=[a for a in waves if a['amplitude_px']>floor and a['fraction_of_detrended_variance']>=.5 and 2.05<=a['frequency_hz']<=3.95]
            out[site]={k:describe([r[k] for r in usable]) for k in ('settled','release_to_closure_px','closure_to_settled_px','short_to_settled_px','terminal_corr')}
            out[site]['all_ringdown_amplitudes_px']=describe([w['amplitude_px'] for w in waves])
            out[site]['distinct_oscillation_hz']=describe([w['frequency_hz'] for w in distinguishable])
        result['/'.join(str(k) for k in (phase,scenario,head,level) if k is not None)]={'attempted':len(group),'sites':out}
    return result

def run():
    out=HERE/'evidence';timeline=prepare();native=read_trace(HERE/'upper-rim.csv');direct=replace_inner(native,read_trace(HERE/'direct-inner-contact.csv'))
    for name,trace,frozen in [('original',native,'frozen-optics'),('direct',direct,'frozen-direct-contact')]:
        res=analyze(trace,timeline);write(out/(name+'-timing-results.json'),res)
        write(out/(name+'-forecast-check.json'),score(res,json.loads((out/(frozen+'.json')).read_text())))
        if name=='direct':
            write(out/'fill-timing-results.json',fill_score(res));write(out/'program-timing-summary.json',program_summaries(res))
    return timeline

if __name__=='__main__':
    res=run();print(len(res['pours']),'appliance pours')
