"""Archive wet intervals and bound bulk camera storage while retaining named endpoints and native trajectories."""
import csv
import json
import shutil
import time
from pathlib import Path

import numpy as np

from archive_gates import archive
from timing_window import HERE, physical_gates
from collect_holds import collect

SOFT=7_000_000_000
LIMIT=11_000_000_000
def current_size():
    total=0
    for f in HERE.rglob('*'):
        try:
            if f.is_file():total+=f.stat().st_size
        except FileNotFoundError:pass
    return total

def retire_old_chunks(now,total,free,status):
    latest_trace=0
    with (HERE/'upper-rim.csv').open() as stream:
        for row in csv.DictReader(stream):latest_trace=int(row['pts_ns'])
    gates=physical_gates((HERE.parent/'work').glob('*.jsonl'))
    uncovered=set(status['unarchived_command_times_ns'])
    obstacles=[(g['tx_ns']-800_000_000,g['done_ack_ns']+5_100_000_000) for g in gates if g['tx_ns'] in uncovered]
    dest=HERE/'sparse-idle';dest.mkdir(exist_ok=True)
    for f in sorted((HERE/'profiles').glob('*.npz')):
        if (total<SOFT*.82 and free>3_200_000_000) or f.stat().st_mtime>now-600:break
        if not f.stem.isdigit():continue
        with np.load(f) as raw:
            ticks=raw['pts_ns'];seq=raw['seq']
            if ticks[-1]>latest_trace or any(a<=ticks[-1] and b>=ticks[0] for a,b in obstacles):continue
            use=seq%15==0
            sparse={k:raw[k][use] if k in ('profiles','seq','pts_ns') else raw[k] for k in raw.files}
        out=dest/f.name;tmp=out.with_suffix('.partial')
        with tmp.open('wb') as archive_file:np.savez_compressed(archive_file,**sparse)
        tmp.replace(out)
        with np.load(out) as check:
            if not np.array_equal(check['profiles'],sparse['profiles']):raise RuntimeError('Sparse camera verification failed')
        size=f.stat().st_size;f.unlink();total-=size-out.stat().st_size;free+=size-out.stat().st_size
    return total,free

def once():
    collect()
    total=current_size();free=shutil.disk_usage(HERE).free;status=archive(HERE,False)
    if any((HERE.parent/'work'/f).is_file() for f in ('fresh.jsonl','fill.jsonl')):
        from timeline import prepare
        from dry_waves import pack
        prepare();pack(HERE)
    if total>=SOFT or free<3_000_000_000:
        total,free=retire_old_chunks(time.time(),total,free,status)
    report={'utc_seconds':time.time(),'scratch_bytes':total,'free_bytes':free,'soft_bytes':SOFT,'budget_bytes':LIMIT,
            'acknowledged_gates_seen':status['acknowledged_commands_seen'],'archived_gates':status['archived_commands']}
    if total>=LIMIT or free<2_000_000_000:report['capacity_notice']='Named endpoints and completed native gate archives are retained. Space is low.'
    temp=HERE/'storage.json.tmp';temp.write_text(json.dumps(report)+'\n');temp.replace(HERE/'storage.json')

if __name__=='__main__':
    while (HERE/'port.json').exists():
        try:once()
        except Exception as error:
            with (HERE/'steward.log').open('a') as log:log.write(str(error)+'\n')
        time.sleep(24)
