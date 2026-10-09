"""Numbers behind scenes/datum-06-eddy-through-wall.

Skin depth of 316L against frequency, and what fraction of the field left after the 1.65 mm wall
would reach a plate seated behind it. The response model is a TOY (thin-conductor formula on a
smoothed step): it says where a bench test is worth doing, not what a sensor would read.
Resistivity: 316L handbook value about 74 micro-ohm.cm (illustrative, not measured on this tube);
relative permeability taken as 1 (annealed austenitic; cold work can raise it slightly, unknown).
"""
import math
import numpy as np

RHO = 74e-8          # ohm.m, illustrative handbook value
MU0 = 4e-7 * math.pi
WALL = 0.065 * 25.4  # mm [repo]/[derived]


def delta_mm(f):
    return 1000 * math.sqrt(RHO / (math.pi * f * MU0))


def step(f, wall=WALL):
    return math.exp(-2 * wall / delta_mm(f))


if __name__ == "__main__":
    print("wall %.3f mm" % WALL)
    print("   f          skin depth   plate 'step' = exp(-2 t/delta)   field at the plate face exp(-t/delta)")
    for f in (100, 300, 1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6, 1e7):
        d = delta_mm(f)
        print("  %9.0f Hz  %7.2f mm   %.4f                          %.3f" % (f, d, step(f), math.exp(-WALL / d)))
    # frequency at which delta equals the wall thickness
    f1 = RHO / (math.pi * MU0 * (WALL / 1000) ** 2)
    print("\nskin depth equals the wall at %.0f kHz" % (f1 / 1e3))
    for tw in (1.5, 1.65, 1.8):
        print("  wall %.2f mm: step at 30 kHz %.3f, at 100 kHz %.3f" % (tw, step(3e4, tw), step(1e5, tw)))

    # toy scan: rim (z=0) -> air above; wall only in the pocket; wall+plate for 6.35 mm below the plate face
    ZG = np.arange(16, -46, -0.1)          # template / profile grid

    def profile(seat, f, tw=WALL, plate=True):
        W = 1 - math.exp(-2 * tw / delta_mm(f))
        S0 = np.where(ZG > 0, 0.0, W)
        if plate:
            S0 = np.where((ZG <= -seat) & (ZG > -seat - 6.35), 1.0, S0)
        return S0

    def smooth(S0, D, g):
        sk = math.hypot(0.35 * D, 0.5 * g)
        n = int(math.ceil(4 * sk / 0.1))
        kern = np.exp(-0.5 * ((np.arange(-n, n + 1) * 0.1) / sk) ** 2); kern /= kern.sum()
        pad = np.pad(S0, n, mode="edge")
        return np.convolve(pad, kern, mode="valid")

    def scan(f, seat, D, g, sigma=0.004, seed=0):
        rng = np.random.default_rng(seed)
        z = np.arange(10, -34, -0.2)
        S = smooth(profile(seat, f), D, g)
        s = np.interp(-z, -ZG, S) + rng.normal(0, sigma, z.size)
        return z, s

    def max_slope(z, s):
        k = 5
        sm = np.convolve(s, np.ones(k) / k, mode="same")
        dz = np.gradient(sm, z)
        win = np.where((z > -3) & (z < 3))[0]
        rim = z[win[np.argmin(dz[win])]]
        win2 = np.where((z < rim - 3) & (z > rim - 12))[0]
        pf = z[win2[np.argmin(dz[win2])]]
        return rim - pf

    def template_fit(z, s, f, D, g, mis):
        seats = np.arange(3, 12.01, 0.25); best = (1e18, 0, 0)
        tpl = {}
        def T(seat):
            key = round(seat, 2)
            if key not in tpl:
                tpl[key] = smooth(profile(seat, f), D * (1 + mis), g)
            return tpl[key]
        def sse(seat, sh):
            m = np.interp(-(z - sh), -ZG, T(seat))
            return float(((s - m) ** 2).sum())
        for seat in seats:
            for sh in np.arange(-3, 3.01, 0.25):
                e = sse(seat, sh)
                if e < best[0]: best = (e, seat, sh)
        e0, s0, h0 = best
        for seat in np.arange(s0 - 0.25, s0 + 0.2501, 0.05):
            for sh in np.arange(h0 - 0.25, h0 + 0.2501, 0.05):
                e = sse(seat, sh)
                if e < best[0]: best = (e, seat, sh)
        return best[1]

    print("\nMonte Carlo, true seat depth 6.85 mm, noise 0.004 of full scale, coil 6 mm, lift-off 1.5 mm (illustrative)")
    print("  30 kHz, two estimators (proper 4-sigma blur kernel):")
    n = 40
    err_ms = np.array([max_slope(*scan(3e4, 6.85, 6, 1.5, seed=i)) - 6.85 for i in range(n)])
    print("     max-slope edge search: RMS %.2f mm, failures (>2 mm) %d%%" % (np.sqrt((err_ms ** 2).mean()), int(100 * (np.abs(err_ms) > 2).mean())))
    for mis in (0.0, 0.15, 0.3, 0.5):
        err = np.array([template_fit(*scan(3e4, 6.85, 6, 1.5, seed=i), 3e4, 6, 1.5, mis) - 6.85 for i in range(n)])
        print("     template fit, blur calibration error %.0f%%: RMS %.2f mm, bias %+.2f, failures %d%%" % (100 * mis, np.sqrt((err ** 2).mean()), err.mean(), int(100 * (np.abs(err) > 2).mean())))
    print("  template fit (15%% calibration error) against frequency and coil diameter:")
    for f in (3e3, 1e4, 3e4, 1e5, 3e5):
        err = np.array([template_fit(*scan(f, 6.85, 6, 1.5, seed=i), f, 6, 1.5, 0.15) - 6.85 for i in range(n)])
        print("     %7.0f Hz (bump %.3f): RMS %.2f mm, failures %d%%" % (f, step(f), np.sqrt((err ** 2).mean()), int(100 * (np.abs(err) > 2).mean())))
    for D in (2, 4, 6, 10, 16):
        err = np.array([template_fit(*scan(3e4, 6.85, D, 1.5, seed=i), 3e4, D, 1.5, 0.15) - 6.85 for i in range(n)])
        print("     coil %2d mm at 30 kHz: RMS %.2f mm, failures %d%%" % (D, np.sqrt((err ** 2).mean()), int(100 * (np.abs(err) > 2).mean())))
