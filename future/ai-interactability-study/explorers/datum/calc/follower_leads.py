"""Numbers behind scenes/datum-04-corner-follower.

A feeler rides in the inside corner at a lead s ahead of the dot, reading the seam's radial
position y(s) against the gun's straight axis. In the gun frame the seam is
    y(x) = e + x tan(psi) + x^2 / (2 r)        (r = 61.85 mm [repo][derived])
e = dot offset from the seam (what we want), psi = gun yaw against the seam tangent (unknown),
x^2/2r = the circle's own curvature (known). Noise is ILLUSTRATIVE.
"""
import numpy as np

R = 61.85
rng = np.random.default_rng(3)


def curvature(s):
    return s * s / (2 * R)


def one_feeler(s, e, psi_deg, sigma, psi_assumed_deg=0.0, n=4000):
    y = e + s * np.tan(np.radians(psi_deg)) + curvature(s) + rng.normal(0, sigma, n)
    est = y - curvature(s) - s * np.tan(np.radians(psi_assumed_deg))
    return est - e   # error of e


def two_leads(s1, s2, e, psi_deg, sigma, n=4000):
    ps = np.tan(np.radians(psi_deg))
    y1 = e + s1 * ps + curvature(s1) + rng.normal(0, sigma, n)
    y2 = e + s2 * ps + curvature(s2) + rng.normal(0, sigma, n)
    a1, a2 = y1 - curvature(s1), y2 - curvature(s2)
    slope = (a2 - a1) / (s2 - s1)
    est_e = a1 - s1 * slope
    return est_e - e, np.degrees(np.arctan(slope)) - psi_deg


def pair(s, e, psi_deg, sigma, sigma_trail, n=4000):
    ps = np.tan(np.radians(psi_deg))
    yp = e + s * ps + curvature(s) + rng.normal(0, sigma, n)
    ym = e - s * ps + curvature(s) + rng.normal(0, sigma_trail, n)
    est_e = (yp + ym) / 2 - curvature(s)
    est_psi = np.degrees(np.arctan((yp - ym) / (2 * s)))
    return est_e - e, est_psi - psi_deg


if __name__ == "__main__":
    print("curvature term s^2/2r of the circle (known, subtracted):")
    for s in (3, 6, 10, 15, 20, 30, 40):
        print("   lead %2d mm (%.1f deg of arc): %.3f mm" % (s, np.degrees(s / R), curvature(s)))
    print("\none feeler, yaw assumed 0 while the gun is really yawed by 1 deg; sigma 0.02 mm")
    for s in (3, 6, 10, 15, 20):
        err = one_feeler(s, 0.2, 1.0, 0.02)
        print("   lead %2d mm: bias %+.3f mm (= s tan psi = %.3f), RMS %.3f mm" % (s, err.mean(), s * np.tan(np.radians(1.0)), np.sqrt((err ** 2).mean())))
    print("\ntwo leading feelers, yaw solved, sigma 0.02 mm, e=0.2, psi=1 deg")
    for s1, s2 in ((5, 10), (6, 15), (8, 20), (8, 30), (10, 40)):
        ee, pe = two_leads(s1, s2, 0.2, 1.0, 0.02)
        print("   s1=%2d s2=%2d: e error RMS %.3f mm (amplification %.2f), yaw error RMS %.2f deg" % (s1, s2, np.sqrt((ee ** 2).mean()), np.sqrt((ee ** 2).mean()) / 0.02, np.sqrt((pe ** 2).mean())))
    print("\nleading + trailing pair (trailing rides the fresh bead: sigma x4), s=8")
    ee, pe = pair(8, 0.2, 1.0, 0.02, 0.08)
    print("   e error RMS %.3f mm, yaw error RMS %.2f deg" % (np.sqrt((ee ** 2).mean()), np.sqrt((pe ** 2).mean())))
    ee, pe = pair(8, 0.2, 1.0, 0.02, 0.02)
    print("   (if the bead were as clean as the seam: e error RMS %.3f mm, yaw %.2f deg)" % (np.sqrt((ee ** 2).mean()), np.sqrt((pe ** 2).mean())))
    print("\nside clearance of a feeler ball under the wire: wire leaves the dot at elevation a; ball radius 1.5 mm, wire radius 0.38 mm [repo: 0.030 in wire]")
    for a in (20, 30, 40, 60):
        print("   elevation %2d deg:" % a + "".join("  lead %2d mm -> %5.2f mm clear" % (s, s * np.tan(np.radians(a)) - 3.0 - 0.38) for s in (3, 6, 10, 15)))
