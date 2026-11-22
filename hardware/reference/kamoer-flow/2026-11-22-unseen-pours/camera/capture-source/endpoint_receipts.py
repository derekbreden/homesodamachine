"""Link photographed endpoints and valve/pump receipts to the nearest frames on the same native camera clock."""
import argparse
import bisect
import csv
import hashlib
import json
import re
from pathlib import Path

def clock_index(path):
    with path.open() as f:
        rows=[(int(r['seq']),int(r['pts_ns'])) for r in csv.DictReader(f) if r.get('pts_ns')]
    return [r[0] for r in rows],[r[1] for r in rows]

def summarize(camera,journals):
    seq,pts=clock_index(camera/'frames.csv')
    windows=json.loads((camera/'evidence/windows.json').read_text())
    def around(tick):
        k=bisect.bisect_left(pts,tick);indices=[i for i in (k-1,k) if 0<=i<len(pts)]
        return [[seq[i],pts[i]] for i in indices]
    result={}
    for path in sorted(journals.glob('*.jsonl')):
        raw=path.read_bytes()
        events=[]
        for line in raw.splitlines():
            if not line.strip():continue
            try:row=json.loads(line)
            except json.JSONDecodeError:continue
            name=row.get('event');command=row.get('command','');rx=row.get('line','')
            if name=='tx' and not re.fullmatch(r'(pump [ABab] \d+|flow \d+ \d+)',command):continue
            if name=='rx' and not re.search(r'(\[machine\] pour [AB]|pump [AB] (at full|done after))',rx):continue
            if name in ('opened','closed','setting','settings'):continue
            if not name:continue
            labels={k:v for k,v in row.items() if isinstance(v,str) and v in windows}
            contacts={key:{'label':label,'mid_pts_ns':windows[label]['mid_pts_ns'],'geometry':windows[label]['absolute_ml']} for key,label in labels.items()}
            entry={'record':row}
            if contacts:entry['photographs']=contacts
            if isinstance(row.get('mono_ns'),int):entry['adjacent_native_seq_and_pts_ns']=around(row['mono_ns'])
            events.append(entry)
        result[path.name]={'journal_sha256':hashlib.sha256(raw).hexdigest(),'records':events}
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('camera',type=Path);ap.add_argument('journal_dir',type=Path);ap.add_argument('--out',type=Path,required=True)
    v=ap.parse_args();out=summarize(v.camera,v.journal_dir);v.out.write_text(json.dumps(out,indent=2)+'\n')
