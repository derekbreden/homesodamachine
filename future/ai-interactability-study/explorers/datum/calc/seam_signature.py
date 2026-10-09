"""Numbers behind scenes/datum-02-seam-signature.

The seam, seen from a fixed dot at the weld station, moves as the tube turns:
  radial   r(th) = c_r + a1 cos(th - p1) + a2 cos(2 th - p2)
  vertical z(th) = c_z + b1 cos(th - q1) + b2 cos(2 th - q2)
(c = static setup offset, 1x = eccentricity / face wobble, 2x = ovality / waviness.)
A dry rotation samples N angles with sensor noise sigma; a least-squares harmonic fit
gives the replay command. Rig limits: radial <= 0.25 mm TIR, face <= 0.30 mm TIR [repo],
so a1 = 0.125, b1 = 0.15 at the limit. Everything else here is ILLUSTRATIVE.
Rotation: 5-15 mm/s bead travel at r = 61.85 mm -> 0.772-2.316 rpm [repo]; 0.025 deg/step [repo].
"""
import numpy as np

RI = 61.85
rng = np.random.default_rng(7)


def design(theta, harmonics=2):
    cols = [np.ones_like(theta)]
    for h in range(1, harmonics + 1):
        cols += [np.cos(h * theta), np.sin(h * theta)]
    return np.stack(cols, axis=1)


def truth(theta, p):
    return (p["c"] + p["a1"] * np.cos(theta - p["p1"]) + p["a2"] * np.cos(2 * theta - p["p2"]))


def trial(N, sigma, p, harmonics=2, drift=0.0, bias_amp=0.0):
    th = np.arange(N) * 2 * np.pi / N
    fine = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    meas = truth(th, p) + rng.normal(0, sigma, N) + bias_amp * np.cos(th - 1.0)
    # drift: an extra slow ramp (thermal) that appears after the dry run
    A = design(th, harmonics)
    coef, *_ = np.linalg.lstsq(A, meas, rcond=None)
    fit = design(fine, harmonics) @ coef
    err_dry = truth(fine, p) - fit   # what the replay leaves behind (before drift)
    ramp = drift * fine / (2 * np.pi)
    err = err_dry + ramp
    return np.sqrt(np.mean(err_dry ** 2)), np.max(np.abs(err_dry)), np.sqrt(np.mean(err ** 2)), np.max(np.abs(err))


def stats(N, sigma, p, harmonics=2, drift=0.0, bias_amp=0.0, reps=400):
    r = np.array([trial(N, sigma, p, harmonics, drift, bias_amp) for _ in range(reps)])
    return r.mean(axis=0)


if __name__ == "__main__":
    p = dict(c=0.20, a1=0.125, p1=0.7, a2=0.05, p2=2.0)   # radial: 0.20 mm setup error, rig-limit eccentricity, illustrative ovality
    fine = np.linspace(0, 2 * np.pi, 720, endpoint=False)
    t = truth(fine, p)
    print("uncompensated: RMS %.3f mm, peak %.3f mm  (setup offset 0.20, ecc 0.125, ovality 0.05)" % (np.sqrt(np.mean(t ** 2)), np.max(np.abs(t))))
    print("\nreplay residual (mean over 400 trials): RMS / peak of what is left, mm")
    print("   N   sigma  RMS    peak")
    for N in (8, 12, 24, 36, 72):
        for sigma in (0.02, 0.05, 0.10):
            m = stats(N, sigma, p)
            print("  %3d  %.2f   %.3f  %.3f" % (N, sigma, m[0], m[1]))
    print("\nwith a slow drift of 0.10 mm over the lap that the dry run could not see (N=36, sigma=0.05):")
    m = stats(36, 0.05, p, drift=0.10)
    print("   residual RMS %.3f, peak %.3f" % (m[2], m[3]))
    print("with a sensor bias that varies with angle, amplitude 0.05 mm (N=36, sigma=0.02): the fit cannot tell it from the seam")
    m = stats(36, 0.02, p, bias_amp=0.05)
    print("   residual RMS %.3f, peak %.3f  (vs no-bias %.3f)" % (m[0], m[1], stats(36, 0.02, p)[0]))
    print("\nhow many harmonics? truth has a 2x term of 0.05 mm; fit with 1 harmonic only (N=36, sigma=0.02)")
    m = stats(36, 0.02, p, harmonics=1)
    print("   residual RMS %.3f, peak %.3f" % (m[0], m[1]))

    # actuator demand
    print("\nfine-axis demand (radial, replay):")
    stroke = np.max(np.abs(t))
    for v in (5, 8, 15):
        rpm = v / RI * 60 / (2 * np.pi)
        w = 2 * np.pi * rpm / 60
        peak = w * (p["a1"] + 2 * p["a2"])
        print("   bead %2d mm/s = %.3f rpm: rev %.1f s, peak axis speed %.4f mm/s, stroke +-%.2f mm" % (v, rpm, 60 / rpm, peak, stroke))
    print("   one table step = 0.025 deg = %.4f mm of seam travel [repo says 0.027 mm]" % (RI * np.radians(0.025)))
