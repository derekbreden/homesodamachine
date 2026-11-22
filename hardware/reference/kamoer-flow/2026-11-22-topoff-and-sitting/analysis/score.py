"""Score every measured pour in the journals against its frozen forecast and write the experiment tables."""
import csv
import json
import statistics as st
import sys
from pathlib import Path

RECORD = Path(__file__).resolve().parents[1]
LOGS = Path(sys.argv[1]) if len(sys.argv) > 1 else RECORD / 'logs'
OUT = RECORD / 'results'
SITES = ('x990', 'x1986')


def tol(f):
    return max(1.0, 0.10 * f)


def trials():
    rows = []
    for path in sorted(LOGS.glob('*.jsonl')):
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['event'] != 'trial':
                continue
            f = r['forecast_ml']
            row = dict(label=r['label'], utc=r['utc'], head=r['head'], program=r['program'], kind=r['kind'],
                       block=r.get('block', ''), sit_min=r.get('sit_min', ''), sit_index=r.get('sit_index', ''),
                       forecast_ml=f, tolerance_ml=tol(f), bursts=r['receipt']['bursts'],
                       elapsed_ms=r['receipt']['elapsed_ms'])
            for k in SITES:
                row[f'{k}_start_ml'] = r['pre'][k]['ml']
                row[f'{k}_dose_ml'] = r['dose_ml'][k]
                row[f'{k}_error_ml'] = r['dose_ml'][k] - f
                row[f'{k}_inside'] = abs(r['dose_ml'][k] - f) <= tol(f)
            rows.append(row)
    rows.sort(key=lambda r: r['utc'])
    return rows


def mean_sd(v):
    return dict(n=len(v), mean=st.mean(v), sd=st.stdev(v) if len(v) > 1 else None) if v else dict(n=0)


def exp1(rows):
    out = {}
    for head in 'AB':
        groups = {}
        for r in rows:
            if r['kind'].startswith('exp1') and r['head'] == head:
                groups.setdefault(r['program'], []).append(r)
        out[head] = {}
        for site in SITES:
            e = {p: [r[f'{site}_error_ml'] for r in g] for p, g in groups.items()}
            m = {p: st.mean(v) for p, v in e.items()}
            per = {p: dict(mean_sd(v), errors=v, starts=[r[f'{site}_start_ml'] for r in groups[p]],
                           per_burst_dose=st.mean(r[f'{site}_dose_ml'] for r in groups[p]) / groups[p][0]['bursts'])
                   for p, v in e.items()}
            contrasts = {}
            for name, (hi, lo) in dict(D_N=('topoff_n22', 'topoff_n6'), D_G=('topoff_gap290', 'topoff_gap600'),
                                       D_L=('topoff_low', 'topoff_high')).items():
                if hi in e and lo in e:
                    d = m[hi] - m[lo]
                    se = (st.variance(e[hi]) / len(e[hi]) + st.variance(e[lo]) / len(e[lo])) ** .5 \
                        if len(e[hi]) > 1 and len(e[lo]) > 1 else None
                    contrasts[name] = dict(difference_ml=d, se_ml=se)
            # Least squares E = a + b * bursts over the three counts at the 494 ms gap.
            pts = [(groups[p][0]['bursts'], x) for p in ('topoff_n6', 'topoff_n11', 'topoff_n22') if p in e for x in e[p]]
            fit = None
            if len({n for n, _ in pts}) >= 2:
                nb = st.mean(n for n, _ in pts)
                eb = st.mean(x for _, x in pts)
                b = sum((n - nb) * (x - eb) for n, x in pts) / sum((n - nb) ** 2 for n, _ in pts)
                a = eb - b * nb
                res = [x - a - b * n for n, x in pts]
                s2 = sum(v * v for v in res) / max(1, len(pts) - 2)
                se_b = (s2 / sum((n - nb) ** 2 for n, _ in pts)) ** .5
                se_a = (s2 * (1 / len(pts) + nb ** 2 / sum((n - nb) ** 2 for n, _ in pts))) ** .5
                fit = dict(per_pour_ml=a, per_pour_se_ml=se_a, per_burst_ml=b, per_burst_se_ml=se_b, pours=len(pts))
            out[head][site] = dict(programs=per, contrasts=contrasts, count_fit=fit)
    if 'A' in out and 'x990' in out['A'] and out['A']['x990']['contrasts']:
        a = out['A']['x990']
        c = a['contrasts']
        rul = {}
        if 'D_N' in c:
            rul['per_burst'] = 'ruled out' if c['D_N']['difference_ml'] < 1.15 else 'not ruled out'
            rul['per_pour'] = 'ruled out as the only carrier' if c['D_N']['difference_ml'] > 1.15 else 'not ruled out'
        if 'D_G' in c:
            rul['gap'] = 'ruled out' if c['D_G']['difference_ml'] < .5 else 'not ruled out'
        if 'D_L' in c:
            rul['level'] = 'ruled out' if abs(c['D_L']['difference_ml']) < .5 else 'not ruled out'
        if 'topoff_n11' in a['programs']:
            rul['reproduction'] = 'reproduced' if a['programs']['topoff_n11']['mean'] >= .8 else 'not reproduced'
        out['registered_rulings_A_x990'] = rul
    return out


def exp2(rows):
    out = []
    pairs = {}
    for r in rows:
        if r['kind'].startswith('exp2'):
            pairs.setdefault((r['sit_index'], r['head']), {})[r['kind']] = r
    for (idx, head), p in sorted(pairs.items()):
        row = dict(sit_index=idx, head=head, sit_min=next(iter(p.values()))['sit_min'])
        for site in SITES:
            sat = p.get('exp2-sat')
            con = p.get('exp2-conditioned')
            row[f'{site}_sat_error_ml'] = sat[f'{site}_error_ml'] if sat else None
            row[f'{site}_conditioned_error_ml'] = con[f'{site}_error_ml'] if con else None
            row[f'{site}_sat_minus_conditioned_ml'] = (sat[f'{site}_dose_ml'] - con[f'{site}_dose_ml']) if sat and con else None
            row[f'{site}_sat_inside'] = sat[f'{site}_inside'] if sat else None
        out.append(row)
    summary = {}
    for head in 'AB':
        for minutes in sorted({r['sit_min'] for r in out}):
            sel = [r for r in out if r['head'] == head and r['sit_min'] == minutes]
            summary[f'{head} {minutes:g} min'] = {
                site: dict(sat_error=mean_sd([r[f'{site}_sat_error_ml'] for r in sel if r[f'{site}_sat_error_ml'] is not None]),
                           sat_minus_conditioned=mean_sd([r[f'{site}_sat_minus_conditioned_ml'] for r in sel
                                                          if r[f'{site}_sat_minus_conditioned_ml'] is not None]))
                for site in SITES}
    verdict = {}
    for head in 'AB':
        s30 = summary.get(f'{head} 30 min', {}).get('x990', {}).get('sat_error', {})
        s3 = summary.get(f'{head} 3 min', {}).get('x990', {}).get('sat_error', {})
        if s30.get('n') and s3.get('n'):
            refuted = abs(s30['mean']) > 1.0 and abs(s30['mean']) - abs(s3['mean']) > .5 and s30['mean'] * s3['mean'] >= 0
            verdict[head] = 'refuted' if refuted else 'not refuted'
    return out, summary, verdict


def main():
    OUT.mkdir(exist_ok=True)
    rows = trials()
    with (OUT / 'pours.csv').open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    e1 = exp1(rows)
    (OUT / 'topoff.json').write_text(json.dumps(e1, indent=1) + '\n')
    e2rows, e2sum, verdict = exp2(rows)
    if e2rows:
        with (OUT / 'sitting.csv').open('w', newline='') as fh:
            w = csv.DictWriter(fh, fieldnames=list(e2rows[0]))
            w.writeheader()
            w.writerows(e2rows)
        (OUT / 'sitting.json').write_text(json.dumps(dict(summary=e2sum, registered_verdict_x990=verdict), indent=1) + '\n')
    glass = [dict(label=r['label'], head=r['head'], kind=r['kind'], forecast_ml=r['forecast_ml'],
                  **{f'{k}_dose_ml': r[f'{k}_dose_ml'] for k in SITES}, **{f'{k}_inside': r[f'{k}_inside'] for k in SITES})
             for r in rows if r['program'] == 'steady_glass']
    (OUT / 'glasses.json').write_text(json.dumps(glass, indent=1) + '\n')
    print(json.dumps(e1.get('registered_rulings_A_x990'), indent=1))
    for head in 'AB':
        if head in e1:
            for p, v in e1[head]['x990']['programs'].items():
                print(head, p, 'n', v['n'], 'E', round(v['mean'], 2), 'sd', v['sd'] and round(v['sd'], 2),
                      'per-burst dose', round(v['per_burst_dose'], 3))
            print(head, e1[head]['x990']['contrasts'], e1[head]['x990']['count_fit'])
    if e2rows:
        print(json.dumps(verdict))
        for k, v in e2sum.items():
            print(k, {s: (v[s]['sat_error'].get('mean'), v[s]['sat_minus_conditioned'].get('mean')) for s in SITES})
    for g in glass:
        print(g)


if __name__ == '__main__':
    main()
