"""How many learning revolutions are worth it?  Residual radial error after replay vs N, judge noise, jitter, drift.

Model = the one in scenes/trials-04-seam-map-replay (ILLUSTRATIVE): seam wobble = e1 cos(theta-40deg) + e2 cos(2 theta) + 0.3 e2 cos 3theta,
per-2deg bins, noise added to every learning reading, DC removed, replay with no lag (lead compensation assumed perfect),
non-repeating jitter (slow sinusoids) and drift (mm per revolution) accumulate. 6 replay revolutions; residual RMS on the last one.
Source of the wobble scale: accepted runout <= 0.25 mm TIR radial [repo]; here e1 = 0.6 mm (a rough seating) and e2 = 0.1 mm.
"""
import numpy as np
rng = np.random.default_rng(1)
def run(N, noise, jit=0.02, drift=0.01, e1=0.6, e2=0.10, revs_replay=6, trials=30):
    per = 180; out = []
    th = np.arange(per) * 2 * np.pi / per
    for _ in range(trials):
        ph = rng.uniform(0, 2 * np.pi, 3)
        def wobble(a): return e1 * np.cos(a - 0.7) + e2 * np.cos(2 * a - 1.1) + 0.3 * e2 * np.cos(3 * a + 0.4)
        total = N + revs_replay; k = np.arange(total * per); a = th[k % per]; rev = k // per
        t = k * (48.6 / per)
        jitter = jit * (0.6 * np.sin(t / 37 + ph[0]) + 0.4 * np.sin(t / 91 + ph[1]) + 0.3 * np.sin(t / 13 + ph[2]))
        seam = wobble(a) + drift * (rev + a / (2 * np.pi)) + jitter
        # learn
        m = np.zeros(per)
        for b in range(per):
            idx = [r * per + b for r in range(N)]
            m[b] = np.mean(seam[idx] + rng.normal(0, noise, N))
        m -= m.mean()
        err = seam - np.tile(m, total)                    # follower tracks the map perfectly
        last = err[-per:]; out.append(np.sqrt(np.mean((last - last.mean()) ** 2)))   # DC re-found by the dot probe at replay start
    return float(np.mean(out))
print("residual rms (mm) on the last replay revolution, DC re-found; jitter 0.02, drift 0.01 mm/rev")
print("noise   " + "".join(f"N={n:<6d}" for n in range(1, 9)))
for noise in (0.01, 0.03, 0.06, 0.10):
    print(f"{noise:5.2f}   " + "".join(f"{run(n, noise):<8.3f}" for n in range(1, 9)))
print("\nsame with jitter 0.05 and drift 0.03 mm/rev (a creepier support)")
for noise in (0.03, 0.10):
    print(f"{noise:5.2f}   " + "".join(f"{run(n, noise, jit=0.05, drift=0.03):<8.3f}" for n in range(1, 9)))
print("\nUnmapped rms for reference (e1=0.6, e2=0.1): about", round(np.sqrt((0.6**2 + 0.1**2 + (0.03)**2) / 2), 3), "mm")
