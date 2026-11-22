"""Bracket each actual metered program with the last pre-pour and first settled post-pour sensor samples."""
import argparse
import json
from pathlib import Path
import re

import numpy as np


def assess(folder):
    receipts=json.loads((folder/'receipts.json').read_text());windows=json.loads((folder/'windows.json').read_text())
    completed=[];unreported=[];positioning=0;totals={}
    for journal,archive in receipts.items():
        raw=[item['record'] for item in archive['records']]
        rows=[r.get('line','') for r in raw if r['event']=='rx']
        totals[journal]={'direct_writes':sum(r['event']=='tx' and bool(re.fullmatch(r'pump [ab] \d+',r.get('command',''),re.I)) for r in raw),
            'direct_received_completions':sum(bool(re.search(r'pump [AB] done after',line)) for line in rows),
            'meter_received_openings':sum(bool(re.search(r'\[machine\] pour [AB] at 1:',line)) for line in rows),
            'meter_received_closures':sum(bool(re.search(r'\[machine\] pour [AB]: flow stopped after',line)) for line in rows),
            'parsed_openings':sum(r['event']=='board_pour_start' for r in raw),'parsed_closures':sum(r['event']=='board_pour_end' for r in raw)}
        active=None
        for event in archive['records']:
            r=event['record'];kind=r['event'];command=r.get('command','')
            if kind=='tx' and re.fullmatch(r'pump [ab] \d+',command,re.I):positioning+=1
            if kind=='prediction':
                if active is not None:unreported.append(active)
                active={'journal':journal,'label':r['label'],'scenario':r['scenario'],'head':r['head'],
                        'start_window':r['start'],'index':r['index'],'meter_writes':[]}
            if active is None:continue
            if kind=='tx' and (match:=re.fullmatch(r'flow (\d+) (\d+)',command)):
                active['meter_writes'].append({'transmit_host_ns':r['mono_ns'],'pulses':int(match[1]),'duration_s':int(match[2])})
            if kind=='board_pour_start':active['open_ack_host_ns']=r['mono_ns']
            if kind=='board_pour_end':active['closure_ack_host_ns']=r['mono_ns']
            if kind=='trial':
                if active['label']!=r['label']:raise RuntimeError('Trial and predicted labels disagree.')
                active['finish_window']=r['finish'];active['expected_dose_ml']=r['forecast_ml'];active['measured_dose_ml']=r['dose_ml']
                active['reported_bursts']=r['receipt']['bursts']
                for key,edge in ((r['start'],'pre'),(r['finish'],'post')):
                    with np.load(folder/'endpoints'/windows[key]['source']) as z:
                        t=z['pts_ns'];active[edge+'_sensor_span_ns']=[int(t[0]),int(t[-1])]
                nonzero=[m['transmit_host_ns'] for m in active['meter_writes'] if m['pulses']]
                if not nonzero or 'open_ack_host_ns' not in active or 'closure_ack_host_ns' not in active:
                    raise ValueError(f'Incomplete powered program receipt for {r["label"]}.')
                active['camera_to_first_meter_write_s']=(nonzero[0]-active['pre_sensor_span_ns'][1])*1e-9
                active['closure_to_first_post_camera_s']=(active['post_sensor_span_ns'][0]-active['closure_ack_host_ns'])*1e-9
                if min(active['camera_to_first_meter_write_s'],active['closure_to_first_post_camera_s'])<=0:
                    raise ValueError(f'Camera endpoints do not bracket the measured pour for {r["label"]}.')
                completed.append(active);active=None
        if active is not None:unreported.append(active)
    return {'completed':completed,'initiated_without_trial_outcome':unreported,'transmitted_direct_positioning_count':positioning,'raw_receipts_by_journal':totals}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('evidence',type=Path);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();a.out.write_text(json.dumps(assess(a.evidence),indent=2)+'\n')
