"""Score every top-off against the registered raised cut, raw and settling-corrected, and apply the two-of-two rule."""
import csv
import json
import sys
from pathlib import Path

RECORD = Path(__file__).resolve().parents[1]
LOGS = Path(sys.argv[1]) if len(sys.argv) > 1 else RECORD / 'logs'
OUT = RECORD / 'results'
SITES = ('x990', 'x1986')
PLAN = json.loads((RECORD / 'design.json').read_text())['amendment']
CUT = PLAN['raised_cut']


def load():
    rows = []
    for path in sorted(LOGS.glob('*.jsonl')):
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['event'] != 'trial':
                continue
            row = dict(label=r['label'], utc=r['utc'], head=r['head'], program=r['program'], kind=r['kind'],
                       episode=r.get('episode', ''), gates=r.get('gates', ''), forecast_ml=r['forecast_ml'],
                       bursts=r['receipt']['bursts'], end_clock=r['receipt']['end_clock'],
                       elapsed_ms=r['receipt']['elapsed_ms'])
            for k in SITES:
                row[f'{k}_start_ml'] = r['pre'][k]['ml']
                row[f'{k}_raw_dose_ml'] = r['dose_ml'][k]
                s = (r.get('settle_ml') or {}).get(k)
                row[f'{k}_settle_ml'] = s
                row[f'{k}_corrected_dose_ml'] = None if s is None else r['dose_ml'][k] - s
            if r['program'] == 'topoff_n11':
                row['raised'] = row['x990_corrected_dose_ml'] >= CUT[r['head']]
            rows.append(row)
    rows.sort(key=lambda r: r['end_clock'])
    last_glass = None
    for row in rows:
        if row['program'] == 'steady_glass':
            last_glass = row['end_clock']
        elif row['kind'] != 'rested' and last_glass is not None:
            row['last_glass_end_to_topoff_start_s'] = round(row['end_clock'] - row['elapsed_ms'] / 1000 - last_glass, 1)
    return rows


def main():
    rows = load()
    OUT.mkdir(exist_ok=True)
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    with (OUT / 'pours.csv').open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)
    rulings = {}
    for head in 'AB':
        first = [r for r in rows if r['head'] == head and r['kind'] in ('three-glasses-gates-topoff1', 'three-glasses-nogates-topoff1')]
        n = sum(r['raised'] for r in first)
        rulings[head] = dict(first_topoffs_after_three_glasses=len(first), raised=n,
                             ruling=None if len(first) < 2 else 'supported' if n == 2 else 'ruled out' if n == 0 else 'unresolved')
    (OUT / 'reproduce.json').write_text(json.dumps(dict(raised_cut=CUT, rulings=rulings), indent=1) + '\n')
    for r in rows:
        if r['program'] == 'topoff_n11':
            print(f"{r['utc'][11:19]} {r['head']} {r['kind']:30s} corr {r['x990_corrected_dose_ml']:5.2f} raw {r['x990_raw_dose_ml']:5.2f} "
                  f"settle {r['x990_settle_ml']:+.2f} x1986 corr {r['x1986_corrected_dose_ml']:5.2f} start {r['x990_start_ml']:.1f} "
                  f"gap {r.get('last_glass_end_to_topoff_start_s', '')} raised {r['raised']}")
        else:
            print(f"{r['utc'][11:19]} {r['head']} {r['kind']:30s} glass {r['x990_raw_dose_ml']:.2f} forecast {r['forecast_ml']:.2f}")
    print(json.dumps(rulings))


if __name__ == '__main__':
    main()
