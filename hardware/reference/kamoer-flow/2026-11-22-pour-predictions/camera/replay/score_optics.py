"""Compare preregistered optical predictions with matched, held-out appliance pour trials."""
import argparse
import json
from pathlib import Path

import numpy as np

from read_pour_timings import SITES

def describe(values):
    z=np.asarray(values,dtype=float)
    return {'n':len(z),'median':float(np.median(z)),'range':[float(np.min(z)),float(np.max(z))]} if len(z) else {'n':0}

def score(results,frozen):
    valid=[r for r in results['trials'] if r['phase']=='validation' and r['recorded_trial']]
    by={(r['head'],r['scenario'],r['block']):r for r in valid}
    out={'validation_trials':len(valid),'stationary':results['blank'],'heads':{}}
    for h in ('A','B'):
        out['heads'][h]={}
        for s in SITES:
            diffs=[];ratios=[];matches=[];groups={}
            for b in sorted(set(r['block'] for r in valid)):
                def read(n,when):
                    r=by.get((h,n,b))
                    return r['sites'][s][when] if r and s in r['sites'] else None
                filled,partial=read('full_glass','settled'),read('partial_glass','settled')
                if filled is not None and partial is not None and abs(partial)>1e-6:ratios.append([b,filled/partial])
                continuous,interrupted=read('same_open_time','early'),read('release_reopen','early')
                if continuous is not None and interrupted is not None:diffs.append([b,continuous-interrupted])
            for name in sorted({r['scenario'] for r in valid}):
                group=[r['sites'][s] for r in valid if r['head']==h and r['scenario']==name and s in r['sites']]
                if not group:continue
                z=[v['temporal_harmonic'] for v in group if v['temporal_harmonic']]
                threshold=results['blank'][s]['stationary_harmonic_amplitude_95_px']
                accepted=[w for w in z if w['amplitude_px']>threshold and w['fraction_of_detrended_variance']>=.5 and 2.05<=w['frequency_hz']<=3.95]
                groups[name]={k:describe([v[k] for v in group]) for k in ('early','settled','terminal_corr','terminal_iqr_px','release_to_closure_px','closure_to_settled_px','short_to_settled_px')}
                groups[name]['ringdown']={'all_amplitudes_px':describe([w['amplitude_px'] for w in z]),
                    'qualifying_frequency_hz':describe([w['frequency_hz'] for w in accepted]),'stationary_amplitude_threshold':threshold}
            expected=frozen['predictions'][h][s]['full_partial_ratio']
            out['heads'][h][s]={'early_continuous_minus_reopen_px_by_block':diffs,'early_positive_pairs':sum(v>0 for _,v in diffs),
               'early_passes_five_of_six':(sum(v>0 for _,v in diffs)>=5) if len(diffs)==6 else None,
               'equal_water_predicted_ratio':expected,'full_over_partial_by_block':ratios,'full_over_partial_observed':describe([n for _,n in ratios]),
               'ratio_direction_matches':sum((r-1)*(expected-1)>0 for _,r in ratios),'scenario':groups}
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('results',type=Path);ap.add_argument('frozen',type=Path);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();r=score(json.loads(a.results.read_text()),json.loads(a.frozen.read_text()))
    tmp=a.out.with_suffix('.partial');tmp.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n');tmp.replace(a.out)
