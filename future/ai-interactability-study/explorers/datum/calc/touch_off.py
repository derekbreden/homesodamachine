"""Numbers behind scenes/datum-07-touch-off.

A stylus, the wire tip or the nozzle is driven by a small 2-axis stage into the wall and then the plate;
a 1-bit contact signal says when. Position at the trigger, minus the tip radius, is the surface. Errors:
detection latency times speed, contact repeatability, tip-to-dot swap error, backlash, debris. Everything
is ILLUSTRATIVE except geometry taken from the repo: wire 0.030 in = 0.76 mm; the kit's nozzle-to-dot 16 mm.
"""
import numpy as np

rng = np.random.default_rng(11)
TIPS = {
    # name: (tip radius mm, contact repeatability sigma, tip-to-dot swap sigma, note)
    "stylus": (1.0, 0.010, 0.030, "dedicated ball stylus threaded in place of the nozzle; kinematic-probe class"),
    "wire":   (0.38, 0.050, 0.150, "the 0.76 mm wire fed out of its guide: soft, tip position uncertain"),
    "nozzle": (3.0, 0.030, 0.30, "the copper nozzle itself, 16 mm from the dot: 1 deg of beam uncertainty is 0.28 mm"),
}


def trial(tip, v_slow, tau, backlash, debris, n=20000):
    r, rep, swap, _ = TIPS[tip]
    # each axis (wall x, plate z): trigger position error = v tau (late detection) + repeatability + backlash + debris
    def axis():
        late = v_slow * tau
        return late + rng.normal(0, rep, n) + rng.uniform(-backlash, backlash, n) + np.where(rng.random(n) < 0.1, rng.uniform(0, debris, n), 0)
    ex = axis() + rng.normal(0, swap, n)
    ez = axis() + rng.normal(0, swap, n)
    return ex, ez


def time_total(travel=4.0, v_fast=2.0, v_slow=0.1, back=0.5):
    # per axis: fast approach, retract, slow touch, retract; two axes, plus a reposition
    per = travel / v_fast + back / v_fast + (back + 0.1) / v_slow + back / v_fast
    return 2 * per + 4.0 / v_fast


if __name__ == "__main__":
    print("time for a full touch-off (fast 2 mm/s, slow 0.1 mm/s, 4 mm search): %.0f s" % time_total())
    print("\ntip          latency  v_slow   error x (bias, RMS)          error z (bias, RMS)")
    for tip in ("stylus", "wire", "nozzle"):
        for tau in (0.005, 0.1):
            for v in (0.1, 1.0):
                ex, ez = trial(tip, v, tau, 0.02, 0.05)
                print("%-8s    %5.0f ms  %.1f mm/s  %+.3f, %.3f mm            %+.3f, %.3f mm" % (tip, tau * 1000, v, ex.mean(), np.sqrt((ex ** 2).mean()), ez.mean(), np.sqrt((ez ** 2).mean())))
    print("\ndot 16 mm beyond the nozzle tip; 1 deg of beam-direction uncertainty moves it %.2f mm" % (16 * np.tan(np.radians(1))))
    print("one repeat touch (average of 4) reduces the random part by 2x; the late-detection bias v_slow*tau does not average")
