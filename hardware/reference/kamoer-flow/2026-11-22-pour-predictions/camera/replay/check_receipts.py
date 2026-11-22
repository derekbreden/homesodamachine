"""Reconcile captured camera intervals with raw appliance transmissions and received motor messages from each journal."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def audit(journals,timeline):
    out={}
    for path in sorted(journals.glob('*.jsonl')):
        rows=[json.loads(l) for l in path.read_text().splitlines() if l.strip()]
        tx=[r['mono_ns'] for r in rows if r['event']=='tx' and re.fullmatch(r'pump [ab] \d+',r.get('command',''))]
        replies=[r['line'] for r in rows if r['event']=='rx']
        direct_done=[s for s in replies if re.search(r'pump [AB] done after \d+ ms',s)]
        openings=[s for s in replies if re.search(r'\[machine\] pour [AB] at 1:\d+: valves',s)]
        closures=[s for s in replies if re.search(r'\[machine\] pour [AB]: flow stopped after',s)]
        board_start=[r['mono_ns'] for r in rows if r['event']=='board_pour_start']
        board_end=[r['mono_ns'] for r in rows if r['event']=='board_pour_end']
        direct_capture=[r['tx_ns'] for r in timeline['direct'] if r['journal']==path.name]
        metered=[r for r in timeline['pours'] if r['journal']==path.name]
        if tx!=direct_capture or len(direct_done)!=len(tx):
            raise ValueError(f'Direct commands differ from received motor completions or captured intervals in {path.name}.')
        if not(len(metered)==len(openings)==len(closures)) or board_start!=[r['start_ack_ns'] for r in metered] or board_end!=[r['done_ack_ns'] for r in metered]:
            raise ValueError(f'Appliance opening or closure receipts differ from the captured intervals in {path.name}.')
        out[path.name]={'journal_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'transmitted_direct_gates':len(tx),'received_direct_completions':len(direct_done),
                        'received_metered_openings':len(openings),'received_metered_closures':len(closures),'recorded_trial_outcomes':sum(r['event']=='trial' for r in rows)}
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('journals',type=Path);p.add_argument('timeline',type=Path);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.write_text(json.dumps(audit(a.journals,json.loads(a.timeline.read_text())),indent=2)+'\n')
