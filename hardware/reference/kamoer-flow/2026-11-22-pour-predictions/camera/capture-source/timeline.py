"""Associate the live camera clock with recorded appliance events without accessing the controller."""
import json
import os
from pathlib import Path
from timing_window import HERE,physical_gates

def prepare():
    original=HERE.parents[3]/'hardware/reference/kamoer-flow/2026-11-22-pour-predictions'
    programs={}
    for design in ('preregistration.json','fresh-programs.json','fill-design.json','repeat-design.json'):
        if (original/design).is_file():programs.update(json.loads((original/design).read_text()).get('scenarios',{}))
    files=sorted((HERE.parent/'work').glob('*.jsonl'))
    motor=physical_gates(files);trials={}
    for f in files:
        for l in f.read_text().splitlines():
            try:r=json.loads(l)
            except json.JSONDecodeError:continue
            if r.get('event')=='trial':
                trials[r['label']]={k:r[k] for k in ('block','index','level','phase','pre','post','start_ml','finish_ml','primary_ml','heldout_ml','pre_cup','post_cup','optical_flags') if k in r}
    for row in motor:
        if row['kind']!='metered_pour':continue
        pred=row['prediction'];scenario=programs.get(pred.get('scenario'),{})
        row['predicted_switches_ms']=scenario.get('ideal_gates_start_ms_width_ms',[])
        row['trial']=trials.get(row['event_label'])
    base=json.loads((HERE/'windows/station-idle/window.json').read_text())
    result={'reference_pts_ns':base['mid']['pts_ns'],'direct': [m for m in motor if m['kind']=='direct_gate'],
            'pours':[m for m in motor if m['kind']=='metered_pour'],
            'program':{name:{k:v for k,v in obj.items() if k in ('phase','ratio','meter','ideal_gates_start_ms_width_ms','ideal_bursts','ideal_on_s','nominal_water_ml')} for name,obj in programs.items()}}
    target=HERE/'evidence/appliance-timeline.json';tmp=target.with_suffix(f'.{os.getpid()}.partial')
    tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(target);return result

if __name__=='__main__':
    res=prepare();print(len(res['pours']),'metered pours,',len(res['direct']),'direct gates')
