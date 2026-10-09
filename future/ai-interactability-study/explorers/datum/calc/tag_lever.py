"""Numbers behind scenes/datum-05-fiducial-collar.

A printed collar or flange on the work carries square tags. A camera on the gun shell reads them.
The tube's pose in the camera frame comes from tag corner positions; the seam is a known offset from
the tags. Error at the seam = lateral error + (distance from tag to seam) x (tilt error) + a systematic
(calibration) term + collar fit error. Pinhole camera; tag corner noise, systematic angle and fit error
are ILLUSTRATIVE. Nobody has measured any of this on the bench [unknown].
"""
import math

W_PX = 1280


def focal_px(fov_deg):
    return (W_PX / 2) / math.tan(math.radians(fov_deg) / 2)


def tag(size_mm, dist_mm, alpha_deg, fov_deg=60, sigma_c=0.3):
    f = focal_px(fov_deg)
    p = size_mm * f * math.cos(math.radians(alpha_deg)) / dist_mm      # projected tag width, px
    sig_lat = sigma_c * dist_mm / f                                    # mm
    sig_tilt = sigma_c / p * (1.0 / max(0.25, math.sin(math.radians(alpha_deg))))  # rad, frontal tags tilt poorly
    return p, sig_lat, sig_tilt


def at_seam(L, sig_lat, sig_tilt, sys_deg=0.3, fit=0.10):
    return math.sqrt(sig_lat ** 2 + (L * sig_tilt) ** 2 + (L * math.radians(sys_deg)) ** 2 + fit ** 2)


if __name__ == "__main__":
    print("focal length %.0f px at 60 deg over %d px" % (focal_px(60), W_PX))
    print("\nOD collar (tags on the vertical wall, seen from above) versus rim flange (tags on the top face)")
    cases = [
        ("OD collar 25 mm below rim, camera 100 mm above, 30 mm out", 8, 96, 72, 25 - 6.35 + 4),
        ("OD collar 60 mm below rim",                               8, 140, 78, 60 - 6.35 + 4),
        ("rim flange top face, camera 70 mm above",                 8, 70, 30, 12.35),
        ("rim flange top face, camera 70 mm above, 4 mm tags",      4, 70, 30, 12.35),
    ]
    for name, s, d, a, L in cases:
        p, sl, st = tag(s, d, a)
        Leff = math.hypot(L, 4.0)
        print("  %-62s tag %2d mm at %3d mm, %2d deg off-normal: %4.0f px wide; lateral %.3f mm, tilt %.2f deg; lever %.1f mm -> seam error %.3f mm (one tag)" % (name, s, d, a, p, sl, math.degrees(st), Leff, at_seam(Leff, sl, st)))
    print("\nlever-arm rule at a fixed good tag (8 mm, 100 mm, 30 deg off-normal): error at the seam versus distance from tag to seam")
    p, sl, st = tag(8, 100, 30)
    for L in (5, 10, 20, 40, 80):
        print("   L = %2d mm: %.3f mm   (systematic 0.3 deg alone gives %.3f mm)" % (L, at_seam(L, sl, st), L * math.radians(0.3)))
