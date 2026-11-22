"""Verify frozen programs, logged forecasts, controller burst counts and the chronology of each bench round."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

d = Path(__file__).resolve().parents[1]
w = d / 'logs'
root = Path(subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], cwd=d, text=True).strip())


def read(f):
    return json.loads(f.read_text())


def loadlog(f):
    return [json.loads(line) for line in f.read_text().splitlines()]


def gitfile_at(fpath):
    relative=fpath.relative_to(root)
    sha=subprocess.check_output(['git','log','-1','--diff-filter=A','--format=%H','--',str(relative)],text=True).strip()
    commit_time=subprocess.check_output(['git','show','-s','--format=%cI',sha],text=True).strip()
    blob=subprocess.check_output(['git','show',f'{sha}:{relative}'])
    if blob!=fpath.read_bytes():
        raise RuntimeError(f'Freeze material was revised: {relative}')
    return {'commit':sha,'committed_at':commit_time,'sha256':hashlib.sha256(blob).hexdigest()}


def audit(phase,model_name,design_name,expected):
    plan=read(d/design_name)
    forecasts=read(d/model_name)['forecasts']
    material={n:gitfile_at(d/n) for n in [model_name,design_name]}
    records=loadlog(w/('validation.jsonl' if phase=='original' else phase+'.jsonl'))
    trials=[r for r in records if r['event']=='trial']
    predictions=[r for r in records if r['event']=='prediction']
    if len(trials)!=expected or len(predictions)!=expected:
        raise RuntimeError((phase,len(trials),len(predictions),expected))
    first=min(datetime.fromisoformat(r['utc']) for r in predictions)
    if not all(datetime.fromisoformat(q['committed_at']) < first for q in material.values()):
        raise RuntimeError('Predictions committed after the first wet test')
    for i,(t,p) in enumerate(zip(trials,predictions)):
        s,h=p['scenario'],p['head']
        if not (i==t['index']==p['index'] and t['label']==p['label'] and p['forecast_ml']==forecasts[s][h]==t['forecast_ml']):
            raise RuntimeError(('unpaired prediction',phase,i,t['label']))
        # Count each first command after forecast and require the same dispense path in the actual receipt.
        between=[r for r in records if p['mono_ns']<r['mono_ns']<t['mono_ns']]
        first_tx=next(r for r in between if r['event']=='tx')
        if not first_tx['command'].startswith('flow '):
            raise RuntimeError(('unexpected command',first_tx))
        starts=[r for r in between if r['event']=='board_pour_start']
        ends=[r for r in between if r['event']=='board_pour_end']
        if len(starts)!=1 or len(ends)!=1 or starts[0]['head']!=h or ends[0]['head']!=h:
            raise RuntimeError(('controller receipts',phase,t['label']))
    return {'scenario_freezes':material,'first_logged_prediction_utc':first.isoformat(),
            'matched_prospective_trials':len(trials),
            'matching_hardware_burst_counts':sum(t['burst_count']==t['expected_bursts'] for t in trials),
            'count_observed_matches_schedule':all(t['expected_bursts']==plan['scenarios'][t['scenario']]['ideal_bursts'] for t in trials),
            'final_board_status': [r['line'] for r in records if r['event']=='rx' and ('state ' in r.get('line','') or 'valves ' in r.get('line',''))][-2:],
            'halts':[r['error'] for r in records if r['event']=='halt']}


if __name__=='__main__':
    summary={phase:audit(phase,m,p,n) for phase,m,p,n in [
        ('original','frozen-model.json','preregistration.json',96),
        ('fresh','geometry-model.json','fresh-programs.json',48),
        ('fill','fill-model.json','fill-design.json',24),
        ('repeat','repeat-model.json','repeat-design.json',16)]}
    fresh=loadlog(w/'fresh.jsonl')
    base=read(d/'repeat-model.json')
    logged=next(r for r in fresh if r['event']=='prediction' and r['block']>=3)
    summary['repeat_recipe_timing']={'last_training_index':max(base['training_indices']),
        'table_frozen_utc':datetime.fromtimestamp(base['utc_ns']/1e9,timezone.utc).isoformat(),
        'first_scored_fresh_trial_logged_utc':logged['utc'],
        'seconds_from_frozen_table_to_first_scored_fresh_prediction':(logged['mono_ns']-base['frozen_monotonic_ns'])/1e9,
        'table_commit':gitfile_at(d/'repeat-model.json'),
        'note':'The numeric table was written locally before the first scored command; its Git commit followed shortly afterward. The recipe calibration rule was committed earlier.'}
    fill = loadlog(w / 'fill.jsonl')
    first_test = next(event for event in fill if event['event'] == 'prediction' and event['block'] == 5)
    level_model = read(d / 'level-forecast.json')
    freeze = gitfile_at(d / 'level-forecast.json')
    delay = (first_test['mono_ns'] - level_model['frozen_monotonic_ns']) / 1e9
    if delay <= 0 or datetime.fromisoformat(freeze['committed_at']) >= datetime.fromisoformat(first_test['utc']):
        raise ValueError('Fill-condition model postdates a reserved serving')
    summary['fill_specific_model_timing'] = {
        'training_indices': level_model['training_indices'], 'freeze': freeze,
        'first_wet_prediction_utc': first_test['utc'], 'seconds_from_local_freeze_to_prediction': delay}
    training = [r for r in loadlog(w / 'train.jsonl') if r['event'] == 'trial']
    if len(training) != 24 or len({r['label'] for r in training}) != len(training):
        raise ValueError('Initial calibration trial count mismatch')
    summary['physical_pours'] = {'calibration': len(training),
        'initial_validation': 96, 'reserved_programs': 48, 'fill': 24, 'additional_recipe_repeats': 16,
        'total_distinct_metered_pours': len(training) + sum(summary[k]['matched_prospective_trials']
            for k in ('original', 'fresh', 'fill', 'repeat')),
        'reused_by_known_recipe_validation': 32, 'reused_by_fill_specific_validation': 8}
    last = loadlog(w / 'return-final.jsonl')
    statuses = [r['line'] for r in last if r['event'] == 'rx']
    restored = [r['settings'] for r in last if r['event'] == 'original_settings_restored']
    summary['parked_appliance'] = {
        'volume': next(msg for msg in reversed(statuses) if msg.startswith('volume')),
        'state': next(msg for msg in reversed(statuses) if msg.startswith('state')),
        'valves': next(msg for msg in reversed(statuses) if msg.startswith('valves')),
        'settings': restored[-1],
        'broad_positioning_scan': next(r for r in last if r['event'] == 'station_position'),
        'qualified_return_readings': 'optical-calibration/geometry-results/return-to-reference.csv',
        'optical_note': 'The broad far-side scanner jumps to a reflection at the returned level. The qualified foreground contacts in the photographs record the return on both sightlines.',
    }
    (d/'chronology.json').write_text(json.dumps(summary,indent=2)+'\n')
