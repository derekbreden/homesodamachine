"""Copy the session's journals and the sightline pixels of every photograph into the record, and drop the scratch copies."""
import json
import shutil
import sys
from pathlib import Path

RECORD = Path(__file__).resolve().parents[1]
work = Path(sys.argv[1])
(RECORD / 'logs').mkdir(exist_ok=True)
(RECORD / 'camera' / 'endpoints').mkdir(parents=True, exist_ok=True)
labels = set()
for log in sorted((work / 'logs').glob('*.jsonl')):
    shutil.copy2(log, RECORD / 'logs' / log.name)
    labels |= {json.loads(s)['label'] for s in log.read_text().splitlines() if '"event":"image"' in s}
copied = 0
for lab in sorted(labels):
    src = work / 'endpoints' / f'{lab}.npz'
    if src.exists():
        shutil.copy2(src, RECORD / 'camera' / 'endpoints' / src.name)
        copied += 1
print('journals', len(list((work / 'logs').glob('*.jsonl'))), 'photographs', len(labels), 'pixel files', copied)
