"""Read every kept frame of each traced top-off, line it up with the controller's bursts, and write the trace and per-burst tables."""
import csv
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

RECORD = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(RECORD / 'optics' / 'shim'), str(RECORD / 'optics'), str(RECORD / 'camera')]
sys.path.append('/opt/homebrew/lib/python3.13/site-packages')
from cam import canvas  # noqa: E402
from read_levels import measure_gray  # noqa: E402

LOGS = RECORD / 'logs'
TRACES = RECORD / 'traces'
OUT = RECORD / 'results'
PROGRAMS = json.loads((RECORD / 'programs.json').read_text())['programs']
DESIGN = json.loads((RECORD / 'design.json').read_text())
SITES = ('x990', 'x1986')
BEFORE = (-0.25, 0.0)   # s relative to a burst's commanded start
AFTER = (0.20, 0.45)


def journal():
    pours = {}
    for path in sorted(LOGS.glob('*.jsonl')):
        current = None
        for line in path.read_text().splitlines():
            r = json.loads(line)
            if r['event'] == 'prediction':
                current = r['label']
            elif r['event'] == 'board_pour_start' and current:
                pours.setdefault(current, {})['first_receipt_clock'] = r['first_receipt_clock']
            elif r['event'] == 'trial':
                pours.setdefault(r['label'], {}).update(trial=r)
    return pours


def window_mean(t, y, a, b):
    m = (t >= a) & (t < b) & np.isfinite(y)
    return float(np.mean(y[m])) if m.any() else float('nan'), int(m.sum())


def main():
    pours = journal()
    OUT.mkdir(exist_ok=True)
    (OUT / 'traces').mkdir(exist_ok=True)
    burst_rows, summary = [], []
    for npz in sorted(TRACES.glob('*.npz')):
        lab = npz.stem
        p = pours[lab]
        tr = p['trial']
        prog = PROGRAMS[tr['program']]
        sign = 1 if tr['head'] == 'B' else -1
        z = np.load(npz)
        wall = z['wall_s']
        t0 = p['first_receipt_clock'] + float(z['wall_minus_monotonic_s'])
        t = wall - t0
        lv = {k: [] for k in SITES}
        for frame in z['native_luma']:
            r = measure_gray(canvas(frame[None]))
            for k in SITES:
                lv[k].append(np.nan if r[k]['ml'] is None else r[k]['ml'])
        lv = {k: np.array(v) for k, v in lv.items()}
        gates = prog['gates_start_ms_width_ms']
        with (OUT / 'traces' / f'{lab}.csv').open('w', newline='') as fh:
            w = csv.writer(fh)
            w.writerow(['t_s_from_first_burst', 'x990_ml', 'x1986_ml', 'burst_on'])
            for i in range(len(t)):
                on = any(g[0] / 1000 <= t[i] < (g[0] + g[1]) / 1000 for g in gates)
                w.writerow([round(float(t[i]), 4), round(float(lv['x990'][i]), 4), round(float(lv['x1986'][i]), 4), int(on)])
        rec = dict(label=lab, head=tr['head'], kind=tr['kind'], cycle=tr.get('cycle', ''),
                   dose_x990=tr['corrected_dose_ml']['x990'] if tr.get('corrected_dose_ml') else tr['dose_ml']['x990'],
                   frames=len(t), fps=round((len(t) - 1) / (wall[-1] - wall[0]), 2))
        for k in SITES:
            y = lv[k]
            quiet = (t < -0.6) & np.isfinite(y)
            if quiet.sum() > 10:
                yq, tq = y[quiet], t[quiet]
                res = yq - np.polyval(np.polyfit(tq, yq, 1), tq)
                sigma = float(np.std(res, ddof=2))
            else:
                sigma = float('nan')
            steps, gaps = [], []
            for i, (gs, gw) in enumerate(gates):
                s = gs / 1000
                b, nb = window_mean(t, y, s + BEFORE[0], s + BEFORE[1])
                a, na = window_mean(t, y, s + AFTER[0], s + AFTER[1])
                step = (a - b) * sign
                nxt = gates[i + 1][0] / 1000 if i + 1 < len(gates) else None
                if nxt is not None:
                    nb2, _ = window_mean(t, y, nxt + BEFORE[0], nxt + BEFORE[1])
                    gap = (nb2 - a) * sign
                else:
                    gap = float('nan')
                steps.append(step)
                gaps.append(gap)
                if k == 'x990' or True:
                    burst_rows.append(dict(label=lab, head=tr['head'], kind=tr['kind'], site=k, burst=i + 1,
                                           start_s=gs / 1000, end_s=(gs + gw) / 1000, before_ml=b, after_ml=a,
                                           frames_before=nb, frames_after=na, step_ml=step, gap_drift_ml=gap))
            # Frame-to-frame scatter while the bursts run (not registered; reported beside the registered sigma).
            during = (t > 0.1) & (t < gates[-1][0] / 1000 + 0.5) & np.isfinite(y)
            d = np.diff(y[during])
            pour_sigma = float(np.std(d) / np.sqrt(2)) if d.size > 3 else float('nan')
            # Per-period delivery: level just before each burst to just before the next (after the last, its after-window).
            befores = [window_mean(t, y, g[0] / 1000 + BEFORE[0], g[0] / 1000 + BEFORE[1])[0] for g in gates]
            last_after = window_mean(t, y, gates[-1][0] / 1000 + AFTER[0], gates[-1][0] / 1000 + AFTER[1])[0]
            period = [(nb_ - b_) * sign for b_, nb_ in zip(befores, befores[1:] + [last_after])]
            rec.update({f'{k}_pour_frame_sigma_ml': pour_sigma, f'{k}_period_delivery_ml': [round(v, 3) for v in period],
                        f'{k}_bursts_resolved_vs_pour_sigma': sum(1 for v in steps if np.isfinite(v) and v > 5 * pour_sigma)})
            last = gates[-1][0] / 1000
            a_last, _ = window_mean(t, y, last + AFTER[0], last + AFTER[1])
            end = t[-1]
            post, _ = window_mean(t, y, end - 0.6, end + 0.01)
            resolved = sum(1 for v in steps if np.isfinite(v) and v > DESIGN['resolved_cut_sigma'] * sigma)
            rec.update({f'{k}_frame_sigma_ml': sigma, f'{k}_bursts_resolved': resolved,
                        f'{k}_sum_steps_ml': float(np.nansum(steps)), f'{k}_sum_gap_drift_ml': float(np.nansum(gaps)),
                        f'{k}_settle_after_last_ml': (post - a_last) * sign,
                        f'{k}_steps_ml': [round(v, 3) for v in steps], f'{k}_gaps_ml': [round(v, 3) for v in gaps]})
        summary.append(rec)
        print(lab, tr['kind'], 'dose', round(rec['dose_x990'], 2), 'fps', rec['fps'], 'sigma', round(rec['x990_frame_sigma_ml'], 4),
              'resolved', rec['x990_bursts_resolved'], 'pour sigma', round(rec['x990_pour_frame_sigma_ml'], 3),
              'resolved vs pour sigma', rec['x990_bursts_resolved_vs_pour_sigma'], '\n  periods', rec['x990_period_delivery_ml'], '\n  steps', rec['x990_steps_ml'], '\n  gaps ', rec['x990_gaps_ml'],
              '\n  sum steps', round(rec['x990_sum_steps_ml'], 2), 'sum gaps', round(rec['x990_sum_gap_drift_ml'], 2),
              'settle', round(rec['x990_settle_after_last_ml'], 3))
    with (OUT / 'bursts.csv').open('w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(burst_rows[0]))
        w.writeheader()
        w.writerows(burst_rows)
    (OUT / 'trace-summary.json').write_text(json.dumps(summary, indent=1) + '\n')


if __name__ == '__main__':
    main()
