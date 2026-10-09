"""Wave-4 calculations for one-knob-one-parameter--on--who-moves-what-w4.md
(their tilt cradle + escape rail, branch T-b).

1. What the escape-rail stop moves at tau* = 32.5 deg: the beam and the rail are
   not parallel, so a stop change moves the dot along the seam (a vertical-axis
   angle change, s/R) as well as the standoff.
2. Directions on the carriage that change exactly one quantity: along the beam
   (standoff only), and the direction that moves the dot across the corner only.
3. Tube tipping in its nest: the first-closure tube's own centre of mass is high
   (plate at the top), so it tips about its rim edge near tau*.
4. Shielding: Richardson number of the argon jet vs gravity (estimate).

Frame: scene frame, dot at (61.85, 0, 146.05); tilt tau about the station
tangent (Y through the dot), + tips the tube top toward +X (their convention).
Run: python3 tilt_exchange_calcs.py
"""
import math
import numpy as np
from geometry import pose_point, JOINT, R_IN, R_OUT

TAU = 32.5
RECIPE = (45, 30, -15)


def Ry(t):
    c, s = math.cos(math.radians(t)), math.sin(math.radians(t))
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def unit(v):
    return v / np.linalg.norm(v)


R = Ry(TAU)
tip = pose_point([0, 0, 0], *RECIPE)
beam_up = R @ unit(tip - JOINT)                      # dot -> nozzle, room frame after tilt
rail = R @ unit(np.array([-0.537, 0, 0.844]))         # their escape direction, tube frame -> room
seam = np.array([0.0, 1.0, 0.0])                     # root line at the dot (tilt axis)
print(f"== 1. At tau {TAU}: beam (dot->nozzle) {np.round(beam_up,3)}, rail {np.round(rail,3)}, angle between {math.degrees(math.acos(np.dot(beam_up, rail))):.1f} deg")
# move the gun by delta along the rail: new beam line through (dot + delta*rail) along beam_up.
# where does it meet the plane of the corner cross-section / the root line?  Solve closest approach to the root line.
for delta in (1.0,):
    p0 = delta * rail                                 # relative to the dot
    # beam line: p0 + t*beam_up ; root line: s*seam.  Least squares for t, s.
    A = np.column_stack([beam_up, -seam])
    t, s = np.linalg.lstsq(A, -p0, rcond=None)[0]
    miss = np.linalg.norm(p0 + t * beam_up - s * seam)
    print(f"   1 mm up the rail: standoff +{-t:.2f} mm, dot slides {s:+.2f} mm along the seam "
          f"(= {math.degrees(abs(s)/R_IN):.2f} deg of vertical-axis angle), beam misses the root line by {miss:.3f} mm")
# 2. clean directions
across = unit(np.cross(beam_up, seam))
print(f"== 2. standoff-only direction = beam {np.round(beam_up,3)}; across-the-corner direction (perp to beam and seam) {np.round(across,3)}")
coef = np.linalg.solve(np.column_stack([beam_up, across, seam]), rail)
print(f"   rail = {coef[0]:.2f} x beam + {coef[1]:.2f} x across + {coef[2]:.2f} x seam  (a rail move = standoff + a slide along the seam)")

# 3. tube tipping in the nest (tube + plates as thin shells; masses from 316L density 8.0 g/cm3)
rho = 8.0e-6
tube_m = math.pi * (R_OUT + R_IN) * (R_OUT - R_IN) * 152.4 * rho
plate_m = math.pi / 4 * 123.44**2 * 6.35 * rho
for label, parts in (("first closure (plate at the top only)", [(tube_m, 76.2), (plate_m, 149.2)]),
                     ("second closure (plates at both ends + rod/float ~0.2 kg)", [(tube_m, 76.2), (plate_m, 149.2), (plate_m, 3.2), (0.2, 76.0)])):
    m = sum(p[0] for p in parts)
    h = sum(p[0] * p[1] for p in parts) / m
    tip_ang = math.degrees(math.atan(R_OUT / h))
    print(f"== 3. {label}: mass {m:.2f} kg, CoM {h:.0f} mm above the rim it stands on -> tips about the rim edge at tau {tip_ang:.1f} deg (unclamped, friction ignored)")
    print(f"      sliding in the nest starts at tan(tau) > mu: mu 0.3 -> {math.degrees(math.atan(0.3)):.0f} deg")

# 4. shielding jet vs buoyancy
g = 9.81
rho_ar, rho_air = 1.784, 1.204
gp = g * (rho_ar - rho_air) / rho_ar
for q_lpm in (6, 15, 20):
    for d_mm in (6, 10):
        U = q_lpm / 60000 / (math.pi * (d_mm / 2000) ** 2)
        for L in (0.01, 0.03):
            Uloc = U if L == 0.01 else U * 0.2
            Ri = gp * L / Uloc**2
            print(f"== 4. {q_lpm} L/min through {d_mm} mm: jet {U:.1f} m/s; Ri at {L*1000:.0f} mm "
                  f"({'jet speed' if L == 0.01 else 'decayed to 20 %'}) = {Ri:.3f}")
