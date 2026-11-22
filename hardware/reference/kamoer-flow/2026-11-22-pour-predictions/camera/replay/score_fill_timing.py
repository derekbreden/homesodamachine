"""Test the predeclared high/low change in the visible fraction of each fixed pour completed at meter release."""
import argparse
import json
from pathlib import Path

import numpy as np
from read_pour_timings import SITES

def score(results):
    pours=[r for r in results['trials'] if r.get('journal')=='fill.jsonl'];out={}
    for head in ('A','B'):
        out[head]={}
        for site in SITES:
            threshold=results['blank'][site]['absolute_95_px']*5;cells={};excluded=[]
            for p in pours:
                if p['head']!=head:continue
                r=p['sites'].get(site)
                if not p['recorded_trial'] or not r or r['settled']<=threshold or not p['ideal_count_matches']:
                    excluded.append(p['label']);continue
                key=(p['block'],p['level'])
                if key in cells:raise ValueError(f'Duplicate fill pair member at {key}')
                cells[key]={'label':p['label'],'fraction_at_release':r['release']/r['settled'],
                           'signed_step_px':r['settled'],'terminal_correlation':r['terminal_corr'],'terminal_band_iqr_px':r['terminal_iqr_px'],
                           'release_to_closure_px':r['release_to_closure_px'],'wave':r['temporal_harmonic']}
            pairs=[]
            for b in sorted(set(k[0] for k in cells)):
                hi=cells.get((b,'high'));lo=cells.get((b,'low'))
                if hi and lo:pairs.append({'block':b,'high':hi,'low':lo,'high_minus_low':hi['fraction_at_release']-lo['fraction_at_release']})
            delta=np.array([p['high_minus_low'] for p in pairs]);ci=None
            if len(delta)==6:
                half=2.0150483733330233*delta.std(ddof=1)/np.sqrt(6)
                ci=[float(delta.mean()-half),float(delta.mean()+half)]
            out[head][site]={'pairs':pairs,'unusable_labels':excluded,'min_step_px':threshold,'complete_pairs':len(delta),
                 'mean_fraction_difference':float(np.mean(delta)) if len(delta) else None,'paired_90_percent_ci':ci,
                 'inside_declared_band':(-.15<ci[0] and ci[1]<.15) if ci is not None and not excluded else None}
    return out
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('results',type=Path);ap.add_argument('--out',required=True,type=Path)
    a=ap.parse_args();a.out.write_text(json.dumps(score(json.loads(a.results.read_text())),indent=2,allow_nan=False)+'\n')
