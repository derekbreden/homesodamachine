"""How fast and how far must something follow the seam so the dot stays on it?

Sources: bead travel 5-15 mm/s at the weld radius 61.85 mm -> 26-78 s per revolution [repo] weld-rotation-rig.md.
Accepted runout at the working end: <= 0.25 mm TIR radial, <= 0.30 mm TIR face [repo]. TIR of a pure eccentricity
is twice its amplitude, so amplitude = TIR/2 (a bound only if the TIR is one harmonic) [derived].
Table pulse = 0.025 deg (0.027 mm at the bead) [repo].  Everything about harmonics 2/3 is ILLUSTRATIVE.
Only two directions matter for the dot-vs-seam error: radial (r) and vertical (z) in the section plane;
the tangential direction slides along the seam [derived; first order, see s^2/2r below].
"""
import math
R = 61.85
def rev_time(v): return 2*math.pi*R/v
print("bead speed -> rev time -> angular rate (deg/s)")
for v in (5, 8, 12, 15):
    print(f"  {v:>2} mm/s  {rev_time(v):5.1f} s/rev  {360/rev_time(v):5.2f} deg/s")

print("\nFollower demand for a sinusoidal seam error of amplitude A at harmonic k (per revolution):")
print("  peak velocity = A*k*w, peak accel = A*(k*w)^2, w = 2*pi/T")
print("  A(mm) k  T(s)   peak v (mm/s)  peak a (mm/s^2)")
for A in (0.125, 0.15, 0.5, 1.0, 2.0):
    for k in (1, 2, 3):
        for v in (5, 15):
            T = rev_time(v); w = 2*math.pi/T
            print(f"  {A:5.3f} {k}  {T:5.1f}  {A*k*w:9.4f}      {A*(k*w)**2:9.5f}   (speed {v} mm/s)")
print("\nTangent slide: moving the dot s mm along the tangent leaves the circle by s^2/(2R):")
for s in (1, 2, 5, 10):
    print(f"  s={s:>2} mm -> radial miss {s*s/(2*R):.3f} mm, approach angle change {math.degrees(s/R):.2f} deg")
print("\nSeam direction change from an eccentricity e (tangent rotates by about e/R):")
for e in (0.125, 0.5, 1.0, 2.0):
    print(f"  e={e:5.3f} mm -> {math.degrees(e/R):.3f} deg")
print("\nOne table step = 0.025 deg -> follower keyed to the rotator angle sees an index every", round(0.025/360*2*math.pi*R,4), "mm of bead travel")
print("A 5-deg angle bin (72 bins/rev) at 8 mm/s is", round(rev_time(8)/72,2), "s of dwell per bin.")
