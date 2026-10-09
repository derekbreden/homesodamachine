"""The seam map when the judge has an angle-locked bias, and when eight touches are the reference (wave 3, answering datum).

Datum's point (exchange/datum--on--trials-w2.md, section 1): map_learning.py scores the replay against the true seam the simulation
knows.  In the rig the only score is the judge, so anything the judge gets wrong that repeats with table angle is learned as seam.
This script keeps map_learning.py's model (seam = e1 cos(th - 40) + e2 cos 2th + 0.3 e2 cos 3th, per-2 degree bins, DC re-found at replay
start, jitter and drift the map cannot hold) and adds:

  * a judge bias b(th) = b1 cos(th - phi1) + 0.67 b1 cos(3 th - phi3)  (harmonics 1 and 3; rms about 0.85 b1; datum's 25 um rms is b1 = 0.03)
  * three ways to build the map:  judge only | K touches (harmonics 1..3 by least squares) | judge with its low harmonics corrected by the touches
  * two scores:  TRUE (vs the simulation's seam, unknowable in the rig) and READ (vs the judge's own reading, what the rig can say)
  * a fourth score, CHECK: rms of (dot - touched seam) at K fresh azimuths, which is what the rig CAN compute after a replay.

Run:  python3 map_bias_touch.py          (prints the tables quoted in exchange/trials--reply-to-datum-w3.md)
Everything here is ILLUSTRATIVE (amplitudes, noise); the structure is the point.
"""
import numpy as np

PER = 180                      # 2 degree bins
TH = np.arange(PER) * 2 * np.pi / PER


HF_PHASE = np.array([0.3, 2.1, 4.0])


def seam_repeat(a, e1=0.6, e2=0.10, ph1=0.7, hf=0.0):
    """Repeating seam.  hf adds harmonics 4, 5, 6 (amplitude hf each): content a K-touch harmonic 1..3 fit cannot see (tack marks, edge dross)."""
    s = e1 * np.cos(a - ph1) + e2 * np.cos(2 * a - 1.1) + 0.3 * e2 * np.cos(3 * a + 0.4)
    for j, k in enumerate((4, 5, 6)):
        s = s + hf * np.cos(k * a + HF_PHASE[j])
    return s


def bias_curve(a, b1, ph):
    return b1 * np.cos(a - ph[0]) + 0.67 * b1 * np.cos(3 * a - ph[1])


def harmonic_design(a, kmax=3):
    cols = [np.ones_like(a)]
    for k in range(1, kmax + 1):
        cols += [np.cos(k * a), np.sin(k * a)]
    return np.stack(cols, axis=1)


def run(N=3, noise=0.03, b1=0.03, K=8, touch_noise=0.02, mode='judge', jit=0.02, drift=0.01, revs_replay=6, draws=200, seed=3, e1=0.6, e2=0.10, hf=0.0):
    rng = np.random.default_rng(seed)
    true_rms, read_rms, check_rms = [], [], []
    for _ in range(draws):
        ph = rng.uniform(0, 2 * np.pi, 2)
        jp = rng.uniform(0, 2 * np.pi, 3)
        total = N + revs_replay
        k = np.arange(total * PER)
        a = TH[k % PER]
        rev = k // PER
        t = k * (48.6 / PER)
        jitter = jit * (0.6 * np.sin(t / 37 + jp[0]) + 0.4 * np.sin(t / 91 + jp[1]) + 0.3 * np.sin(t / 13 + jp[2]))
        seam = seam_repeat(a, e1, e2, hf=hf) + drift * (rev + a / (2 * np.pi)) + jitter
        bias = bias_curve(a, b1, ph)
        read_seam = seam + bias                                   # what the judge reports as the seam
        # ---- build the map (bins) --------------------------------------------------------------
        judge_map = np.zeros(PER)
        for bnum in range(PER):
            idx = [r * PER + bnum for r in range(N)]
            judge_map[bnum] = np.mean(read_seam[idx] + rng.normal(0, noise, N))
        judge_map -= judge_map.mean()
        # touches at K azimuths, taken at rest during the first learning revolution, reading the TRUE repeating seam plus their own noise
        ka = np.arange(K) * 2 * np.pi / K + rng.uniform(0, 0.3)
        truth_at_touch = seam_repeat(ka, e1, e2, hf=hf) + drift * 0.5
        touches = truth_at_touch + rng.normal(0, touch_noise, K)
        Dk = harmonic_design(ka)
        coef_t, *_ = np.linalg.lstsq(Dk, touches, rcond=None)
        touch_map = harmonic_design(TH) @ coef_t
        touch_map -= touch_map.mean()
        if mode == 'judge':
            m = judge_map
        elif mode == 'touch':
            m = touch_map
        else:                                                      # 'both': replace the judge's harmonics 1..3 by the touches', keep the rest
            cj, *_ = np.linalg.lstsq(harmonic_design(TH), judge_map, rcond=None)
            low_j = harmonic_design(TH) @ cj
            m = judge_map - low_j + touch_map + (low_j.mean() - touch_map.mean() * 0)
            m -= m.mean()
        replay = np.tile(m, total)
        err_true = (replay - seam)[-PER:]
        err_read = (replay - read_seam)[-PER:]
        true_rms.append(np.sqrt(np.mean((err_true - err_true.mean()) ** 2)))
        read_rms.append(np.sqrt(np.mean((err_read - err_read.mean()) ** 2)))
        # the check the rig can run: K fresh azimuths, touch noise, after the replay (DC removed as in the other scores)
        kc = np.arange(K) * 2 * np.pi / K + 0.5
        binc = np.round(kc / (2 * np.pi / PER)).astype(int) % PER
        e_at = err_true[binc] + rng.normal(0, touch_noise, K)
        check_rms.append(np.sqrt(np.mean((e_at - e_at.mean()) ** 2)))
    return np.mean(true_rms) * 1000, np.mean(read_rms) * 1000, np.mean(check_rms) * 1000


if __name__ == '__main__':
    print('micrometres rms on the last replay revolution, DC re-found, jitter 0.02 mm, drift 0.01 mm/rev, 200 draws; e1 = 0.6, e2 = 0.1 (map_learning.py model)\n')
    print('A. Judge-only map, N learning revolutions, judge noise 0.03 mm.  TRUE = against the simulation seam; READ = against the judge itself')
    print('   bias b1 (mm)     N=1 true/read   N=3 true/read   N=5 true/read   N=8 true/read')
    for b1 in (0.0, 0.03, 0.06, 0.10):
        row = ''
        for N in (1, 3, 5, 8):
            tr, rd, _ = run(N=N, b1=b1)
            row += f'   {tr:6.1f} / {rd:5.1f}'
        print(f'   {b1:5.2f}         ' + row)
    print('\nB. Where the number can be computed: TRUE, READ and CHECK (K = 8 touches at fresh azimuths, touch noise 0.02) for the judge-only map, b1 = 0.06, N = 3')
    tr, rd, ck = run(N=3, b1=0.06)
    print(f'   true {tr:.1f}   read {rd:.1f}   check {ck:.1f}')
    print('   (the READ score says the map is at the judge noise floor; the CHECK score sees what the READ score cannot)')
    print('\nC. Three ways to build the map, N = 3, judge noise 0.03, touch noise 0.02, K = 8 or 16.  TRUE rms / CHECK rms.  hf = amplitude of harmonics 4, 5, 6 the touches cannot see')
    print('   hf     b1     judge only        K=8 touches       judge + touch-corrected low harmonics   K=16 touches')
    for hf in (0.0, 0.02, 0.05):
        for b1 in (0.03, 0.06):
            j = run(N=3, b1=b1, mode='judge', hf=hf)
            t8 = run(N=3, b1=b1, mode='touch', K=8, hf=hf)
            c8 = run(N=3, b1=b1, mode='both', K=8, hf=hf)
            t16 = run(N=3, b1=b1, mode='touch', K=16, hf=hf)
            print(f'   {hf:4.2f}   {b1:4.2f}   {j[0]:5.1f} / {j[2]:5.1f}     {t8[0]:5.1f} / {t8[2]:5.1f}     {c8[0]:5.1f} / {c8[2]:5.1f}                          {t16[0]:5.1f} / {t16[2]:5.1f}')
    print('\nD. Touch noise against the bias it is meant to bound (touch map, K = 8, b1 = 0.03, hf = 0.02): TRUE rms')
    for tn in (0.005, 0.02, 0.04, 0.08):
        r = run(N=3, b1=0.03, mode='touch', K=8, touch_noise=tn, hf=0.02)
        print(f'   touch noise {tn:5.3f}  -> true rms {r[0]:5.1f} um   (judge-only at the same bias and hf: {run(N=3, b1=0.03, hf=0.02)[0]:.1f})')
