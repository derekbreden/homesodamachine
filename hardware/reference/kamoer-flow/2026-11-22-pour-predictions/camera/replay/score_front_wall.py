"""Evaluate photographed front-wall motion against the frozen endpoint reconstruction criterion."""
import argparse
import json
from pathlib import Path

import numpy as np


def statistics(values):
    a=np.asarray(values,float)
    if len(a)==0:return None
    return {'n':len(a),'median':float(np.median(a)),'q90':float(np.quantile(a,.90)),
            'q95':float(np.quantile(a,.95)),'maximum':float(a.max())}


def evaluate(source,plan):
    summary={}
    rows=source['trials']
    for source_file,n in plan['planned_counts'].items():
        tests=[m for m in rows if m['journal']==source_file and
               (source_file!='fresh.jsonl' or int(m['label'].split('-')[1])>=20)]
        sites={}
        for site in ('x990','x1986'):
            readings=[(r['label'],r['sites'][site]) for r in tests if site in r['sites']]
            errors=[abs(a['settled_minus_photo_px']) for _,a in readings]
            misses=[{'label':label,'signed_error_px':r['settled_minus_photo_px']} for label,r in readings if abs(r['settled_minus_photo_px'])>6]
            inside=sum(x<=6 for x in errors)
            sites[site]={'planned':n,'attempted_with_reading':len(readings),'within_six_px':inside,'fraction_of_planned':inside/n,
                         'passed':inside/n>=.90,'absolute_endpoint_error_px':statistics(errors),'misses':misses}
        summary[source_file]={'sites':sites}
    phases={}
    for journal in plan['planned_counts']:
        obs=[m for m in rows if m['journal']==journal]
        for head,scenario,level in sorted({(m['head'],m['scenario'],m['level'] or '') for m in obs}):
            group=[m for m in obs if m['head']==head and m['scenario']==scenario and (m['level'] or '')==level]
            key='/'.join(k for k in (journal,head,scenario,level) if k)
            phases[key]={}
            for site in ('x990','x1986'):
                usable=[m['sites'][site] for m in group if site in m['sites']]
                phases[key][site]={k:statistics([d['signed_front_wall_px'][k] for d in usable]) for k in ('release','closure','settled')}
                phases[key][site]['release_to_closure_px']=statistics([d['release_to_closure_px'] for d in usable])
                phases[key][site]['closure_to_settled_px']=statistics([d['signed_front_wall_px']['settled']-d['signed_front_wall_px']['closure'] for d in usable])
    comparisons={}
    for head in ('A','B'):
        for site in ('x990','x1986'):
            pairs={}
            for trial in rows:
                if trial['journal']!='fill.jsonl' or trial['head']!=head or site not in trial['sites']:continue
                data=trial['sites'][site]['signed_front_wall_px']
                if data['settled']<=0:continue
                pairs.setdefault(trial['block'],{})[trial['level']]=data['release']/data['settled']
            paired=[v['high']-v['low'] for _,v in sorted(pairs.items()) if 'high' in v and 'low' in v]
            ci=None
            if len(paired)==6:
                mean=float(np.mean(paired));half=2.0150483733330233*np.std(paired,ddof=1)/np.sqrt(6)
                ci=[float(mean-half),float(mean+half)]
            comparisons[head+'/'+site]={'fractions_by_block_and_level':pairs,'high_minus_low':paired,
                                         'paired_mean_fraction_difference':float(np.mean(paired)) if paired else None,
                                         'paired_90_percent_ci':ci}
    return {'heldout_endpoint_agreement':summary,'front_wall_timing_by_waveform':phases,
            'descriptive_fill_fraction_at_release':comparisons}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('plan',type=Path);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    result=evaluate(json.loads(args.source.read_text()),json.loads(args.plan.read_text()))
    args.out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
