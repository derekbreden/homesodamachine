"""Wave 3 new direction: a switch-locked magnetic skate (idea E). Rough numbers, all labelled.

Geometry (proposal): a tongue from the shell near the barrel reaches out over the rim on +X to a shoe
that rests on a horizontal steel plate beside the tube. Shoe: a Magswitch MagJig 95 (Magswitch spec:
43 kg max breakaway, 4 kg 2:1 shear working load, 0.1 kg, 55.8 x 33 x 45.7 mm, pole footprint 30 x 21 mm)
in a printed/metal body with three 10 mm balls as feet. Pose: opening pose, dial convention.
"""
import numpy as np
from pose import pose_point, JOINT, BENCH_Z

G = 9.81
dot = JOINT + np.array([0, 0, BENCH_Z])                      # bench coordinates
shoe = np.array([120.0, -20.0, 285.0])                         # contact plane at 285 mm above the bench
v = dot - shoe
h_lever = np.linalg.norm(v)
print(f"shoe to dot: {np.round(v,0)} mm, distance {h_lever:.0f} mm, horizontal {np.hypot(v[0], v[1]):.0f} mm, vertical {-v[2]:.0f} mm")

# magnet capability from the spec sheet
N_full = 43 * G                     # normal breakaway, full pole contact on thick steel
shear_break = 2 * 4 * G              # 2:1 working load -> breakaway ~2x working (spec's own ratio)
mu = shear_break / N_full
print(f"MagJig 95: normal breakaway ~{N_full:.0f} N, implied shear breakaway ~{shear_break:.0f} N, mu ~{mu:.2f}")
# with ball feet the poles stand off the plate; assume 30-50 % of full force across a 0.2-0.3 mm gap (estimate)
for frac in (0.3, 0.5, 1.0):
    Fm = frac * N_full
    r = 25.0                          # ball circle radius
    tip = Fm * r / (2 * abs(v[2]))    # lateral force at the dot that unloads a ball (lever = vertical drop)
    print(f"  preload {Fm:4.0f} N ({frac:.0%}): slip at ~{mu*Fm:4.0f} N sideways, a ball unloads at ~{tip:4.0f} N sideways at the dot")

# Hertz: 10 mm chrome ball on steel, per-ball load; lock shift when preload rises from residual to locked
E_star = 1 / ((1 - 0.3**2) / 210e3 * 2)   # MPa, steel on steel
R = 5.0
def hertz_delta(F):
    return (9 * F**2 / (16 * E_star**2 * R)) ** (1 / 3)   # mm
for Fm in (0.3 * N_full, 0.5 * N_full):
    d0, d1 = hertz_delta(1.0), hertz_delta(Fm / 3)
    k = 1.5 * (Fm / 3) / d1
    print(f"  per ball {Fm/3:.0f} N: approach {d1*1000:.1f} um (from {d0*1000:.2f} um at 1 N); contact stiffness ~{k/1000:.0f} N/um per ball")

# debris under one ball
s = 25 * np.sqrt(3)            # ball spacing
for d in (0.01, 0.05, 0.1):
    tilt = d / (s * np.sqrt(3) / 2)
    print(f"  a {d:.2f} mm particle under one ball tilts the shoe {np.degrees(tilt)*60:.1f} arcmin -> dot moves up to {tilt*h_lever:.3f} mm")

# yaw of the shoe (plan-angle setting) moves the dot sideways by horizontal lever x angle
lh = np.hypot(v[0], v[1])
print(f"  1 deg of shoe yaw moves the dot {np.radians(1)*lh:.2f} mm (re-slid on the plate); 1 mm along Y = {np.degrees(1/61.85):.2f} deg of plan angle")

# stiffness chain (estimates)
E_st, E_al = 200e3, 69e3
k_post = 3 * E_st * (np.pi * 25**4 / 64) / 200**3
k_tongue = 3 * E_al * (15 * 25**3 / 12) / 70**3
print(f"  steel post 25 mm x 200 mm: ~{k_post:.0f} N/mm; aluminium tongue 15 x 25 x 70 mm: ~{k_tongue:.0f} N/mm (shell-to-gun fit not counted)")
k_series = 1 / (1 / k_post + 1 / k_tongue + 1 / 500)  # 500 N/mm assumed for plate/shoe/shell interface
print(f"  in series with an assumed 500 N/mm shell interface: ~{k_series:.0f} N/mm -> 2 N wire push moves the dot ~{2/k_series*1000:.0f} um")

# float coupling while unlocked
for L in (800, 1200):
    for travel in (20, 40):
        print(f"  balancer line {L} mm, shoe slid {travel} mm: sideways pull {15*travel/L:.2f} N for a 1.5 kg gun+shell (static friction at 3 N residual ~{mu*3:.2f} N)")
