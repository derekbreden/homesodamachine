"""Apply the registered readings to A's traced top-offs, raised against normal, on the x990 sightline."""
import json
import statistics as st
from pathlib import Path

RECORD = Path(__file__).resolve().parents[1]
S = json.loads((RECORD / 'results' / 'trace-summary.json').read_text())
CUT = 7.0
A = [r for r in S if r['head'] == 'A']
R = [r for r in A if r['dose_x990'] >= CUT]
M = [r for r in A if r['dose_x990'] < CUT]
pos = lambda g, i: st.mean(r['x990_steps_ml'][i] for r in g)
diff = st.mean(r['dose_x990'] for r in R) - st.mean(r['dose_x990'] for r in M)
overall = st.mean(r['x990_sum_steps_ml'] for r in R) / st.mean(r['x990_sum_steps_ml'] for r in M)
ratios = [pos(R, i) / pos(M, i) for i in range(11)]
within = sum(abs(q / overall - 1) <= .25 for q in ratios)
two = [(sum(v <= .57 for v in r['x990_steps_ml']), sum(v >= .62 for v in r['x990_steps_ml'])) for r in R]
med_r = st.median(v for r in R for v in r['x990_steps_ml'])
med_m = st.median(v for r in M for v in r['x990_steps_ml'])
gap_m = st.mean(r['x990_sum_gap_drift_ml'] for r in M)
gap_r = st.mean(r['x990_sum_gap_drift_ml'] for r in R)
early = sum(pos(R, i) - pos(M, i) for i in (0, 1)) / diff
out = dict(raised=[r['label'] for r in R], normal=[r['label'] for r in M], dose_difference_ml=diff,
           uniform=dict(overall_step_ratio=overall, position_ratios=ratios, positions_within_25pct=within,
                        reading='holds' if within >= 9 else 'false'),
           two_sizes=dict(per_raised_pour_low_high_counts=two,
                          reading='holds' if all(lo >= 2 and hi >= 2 for lo, hi in two) else
                          'false' if any(min(lo, hi) <= 1 for lo, hi in two) else 'neither'),
           give_back=dict(median_step_raised=med_r, median_step_normal=med_m, normal_sum_gap_ml=gap_m,
                          reading='false' if abs(med_r - med_m) > .1 else
                          'holds' if abs(med_r - med_m) < .05 and -gap_m >= diff / 2 else 'neither'),
           early=dict(share_of_difference_in_bursts_1_2=early,
                      reading='holds' if early >= .7 else 'false' if early < .4 else 'neither'),
           gap_flow=dict(raised_sum_gap_ml=gap_r, share=gap_r / diff,
                         reading='holds' if gap_r >= diff / 2 else 'false' if gap_r < diff / 4 else 'neither'),
           pour_frame_sigma_ml=dict(A=[round(r['x990_pour_frame_sigma_ml'], 3) for r in A],
                                    B=[round(r['x990_pour_frame_sigma_ml'], 3) for r in S if r['head'] == 'B']))
(RECORD / 'results' / 'readings.json').write_text(json.dumps(out, indent=1) + '\n')
print(json.dumps(out, indent=1))
