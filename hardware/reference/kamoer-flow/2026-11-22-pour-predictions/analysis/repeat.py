"""Learn the dose of a specific serving from its first pair and predict six further repeats."""
import json
from pathlib import Path
from statistics import mean
import time

work=Path(__file__).resolve().parent
record=work.parents[3]/'hardware/reference/kamoer-flow/2026-11-22-pour-predictions'
programs=json.loads((record/'fresh-programs.json').read_text())
outfile=record/'repeat-model.json'
while True:
    j=[json.loads(s) for s in (work/'fresh.jsonl').read_text().splitlines() if s.endswith('}')]
    base=[r for r in j if r['event']=='trial' and r['block'] in (1,2)]
    if len(base)==16:break
    time.sleep(.15)
cells={n:{} for n in programs['scenarios']}
for n in cells:
    for head in ('A','B'):
        rows=[r for r in base if r['scenario']==n and r['head']==head]
        if len(rows)!=2 or any(r['primary_ml'] is None or r['burst_count']!=r['expected_bursts'] for r in rows):
            raise SystemExit('First two programs must have acknowledged dose observations.')
        cells[n][head]=mean(r['primary_ml'] for r in rows)
with outfile.open('x') as f:
    json.dump({'training_indices':[r['index'] for r in base], 'forecasts':cells,
               'utc_ns':time.time_ns(),'frozen_monotonic_ns':time.monotonic_ns()},f,indent=2);f.write('\n')
print(cells,flush=True)
