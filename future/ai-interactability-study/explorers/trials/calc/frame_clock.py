"""Time is a calibration too (wave 3, scene trials-23-frame-clock).

Everything the trial loop compares has a clock: the frame (exposure, readout, USB, a host timestamp), the rotator's angle (a step counter reported over
serial), the positioner's command.  A time error only matters when something MOVES between the two clocks.  Numbers here are ILLUSTRATIVE except where
tagged; the point is the structure.

1. Four sweeps give the seam, the chain's latency and the backlash.  A sweep at speed v (mm/s) in direction d (+1 up, -1 down) records the knee where the
   software's command x_cmd(stamp) crosses it.  The frame shows the dot as it was tau seconds before the stamp (tau = command-to-motion lag + exposure-to-stamp
   lag, all of it), and the achieved position lags the command by half the lash L in the direction of travel, so
        knee_rec(d, v) = x_seam + d * (v * tau + L / 2) + noise.
   The mean over the two directions is the seam at any speed; the half difference is v tau + L/2: linear in v, slope tau, intercept L/2.
   Two speeds, two directions = four sweeps = seam, tau and L (one degree of freedom left for a check).
2. A step test finds tau to a fraction of a frame: command a step at a random phase against the frame clock; the delay to the first frame that shows it
   is tau + T/2 on average (T = frame period), so mean(delay) - T/2 estimates tau with sd T / sqrt(12 N).
3. A moving comparison: pose read at the frame's stamp vs where the dot was: error = speed x tau.  The comparison at rest has none.
4. A seam map learned at one speed and replayed at another: the lag is baked into the map, so only the difference of angular rates times tau shows, on
   a smooth map (amplitude a, harmonic k): a k (2 pi / 360) d_omega tau.
5. Duplicate frames: a stalled camera returns the last frame; sensor read noise makes every real frame unique, so a zero difference is a duplicate.
Run: python3 frame_clock.py
"""
import numpy as np

rng = np.random.default_rng(5)


def four_sweeps(seam=0.0, tau=0.15, lash=0.10, sig_knee=0.02, jitter=0.015, speeds=(0.25, 1.0), n_pairs=1, draws=2000):
    """Monte Carlo of the four-sweep estimator.  jitter = sd of the frame timestamp (s): adds v * jitter to each knee."""
    est = []
    for _ in range(draws):
        rows = []
        for v in speeds:
            for d in (+1, -1):
                for _k in range(n_pairs):
                    knee = seam + d * (v * tau + lash / 2) + rng.normal(0, sig_knee) + d * v * rng.normal(0, jitter)
                    rows.append((v, d, knee))
        rows = np.array(rows)
        # least squares: knee = seam + d * (v * tau + lash / 2)
        A = np.stack([np.ones(len(rows)), rows[:, 1] * rows[:, 0], rows[:, 1] * 0.5], axis=1)
        x, *_ = np.linalg.lstsq(A, rows[:, 2], rcond=None)
        est.append(x)
    est = np.array(est)
    return est.mean(axis=0), est.std(axis=0)


def step_test(tau=0.15, T=1 / 30, N=100, draws=2000, offset_known=True):
    out = []
    for _ in range(draws):
        tc = rng.uniform(0, T, N)                    # command times relative to the frame clock
        first = np.ceil((tc + tau) / T) * T          # first frame exposed after the change has reached the scene
        out.append(np.mean(first - tc) - T / 2)
    out = np.array(out)
    return out.mean(), out.std()


print('1. Four sweeps (0.25 and 1.0 mm/s, both directions), knee noise 0.02 mm per sweep, tau 0.15 s, lash 0.10 mm.  Mean and sd of the estimates over 2000 draws')
print('   timestamp jitter   pairs per speed    seam (mm)          tau (s)            lash (mm)')
for jit in (0.0, 0.015, 0.05):
    for npair in (1, 5):
        m, sd = four_sweeps(jitter=jit, n_pairs=npair)
        print(f'   {jit*1000:5.0f} ms           {npair:3d}                {m[0]:+.3f} +/- {sd[0]:.3f}    {m[1]:.3f} +/- {sd[1]:.3f}     {m[2]:.3f} +/- {sd[2]:.3f}')
print('   (one sweep up alone reads the seam wrong by v tau + L/2 =', round(1.0 * 0.15 + 0.05, 3), 'mm at 1 mm/s, and', round(0.25 * 0.15 + 0.05, 3), 'mm at 0.25 mm/s)')
print()
print('2. Step test, tau = 0.15 s: estimate of tau and its sd for N random-phase steps (a frame every 33.3 ms)')
for T, name in ((1 / 30, '30 fps'), (1 / 100, '100 fps')):
    for N in (20, 100, 400):
        m, sd = step_test(T=T, N=N)
        print(f'   {name:8s} N={N:4d}   mean {m*1000:6.1f} ms   sd {sd*1000:5.2f} ms   (T/sqrt(12 N) = {T/np.sqrt(12*N)*1000:5.2f} ms)')
print()
print('3. A moving comparison: dot speed x tau.  The AI cannot compare the arm pose with the frame while the hand moves')
print('   tau (s)     hand at 20 mm/s    hand at 5 mm/s    dot at 0.5 mm/s (a sweep)    at rest')
for tau in (0.03, 0.10, 0.25):
    print(f'   {tau:5.2f}       {20*tau:6.2f} mm         {5*tau:5.2f} mm         {0.5*tau*1000:5.0f} um                    0')
print('   a stillness gate (dot image speed below 0.3 mm/s for 2 tau) keeps the mismatch to', round(0.3 * 0.10 * 1000), 'um at tau = 0.10 s')
print()
print('4. Seam map learned and replayed at different speeds (the lag is baked into the map at the learn speed).  Error in micrometres')
print('   bead speed learn -> replay     d_omega (deg/s)    tau 0.05 s   0.15 s   0.5 s     for a1 = 0.125 mm (rig limit), k = 1 | for a3 = 0.05, k = 3')
R = 61.85
for vl, vr in ((8, 8), (8, 12), (5, 15)):
    dw = (vr - vl) / R * 180 / np.pi
    row = []
    for tau in (0.05, 0.15, 0.5):
        e1 = 0.125 * 1 * (2 * np.pi / 360) * dw * tau * 1000
        e3 = 0.05 * 3 * (2 * np.pi / 360) * dw * tau * 1000
        row.append(f'{e1:4.1f}|{e3:4.1f}')
    print(f'   {vl:2d} -> {vr:2d} mm/s              {dw:5.2f}               ' + '   '.join(row))
print('   the map is smooth in angle, so a time error costs micrometres; a sweep or a hand costs tenths of a millimetre')
print()
print('5. Rolling shutter: readout 16 ms.  The tube edge moves along the seam at 8 mm/s: skew', round(8 * 0.016, 3), 'mm along the seam (does not matter, 0.008 mm/mm across); a dot swept at 0.5 mm/s:', round(0.5 * 0.016 * 1000), 'um across the frame')
print()
print('6. Angle stamp: a rotator status line every 50 ms with a 30 ms jitter puts the frame at the wrong angle by', round(7.4 * 0.03, 2), 'deg =', round(8 * 0.03, 2), 'mm along the seam at 8 mm/s (tack and bump positions, not the radial map)')
print()
print('7. Duplicate frames: sensor read noise of even 1 grey level makes two real frames differ; a stalled camera repeats one exactly.  P(two real 1280x960 frames identical) is zero for practical purposes.')
