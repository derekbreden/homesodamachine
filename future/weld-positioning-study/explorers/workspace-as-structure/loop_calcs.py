"""Rough numbers behind the workspace arrangements. Every input is labelled.

Run: python3 loop_calcs.py
"""
import math
import numpy as np
import geom

print("== 1. Where a height error moves the dot (scene opening pose) ==")
hp = 30 - geom.HOLE_OFFSET
tip = geom.pose_point([0, 0, 0], 45, hp, -15)
dot = geom.pose_point([0, 0, -geom.CLEAR], 45, hp, -15)
beam = (dot - tip) / np.linalg.norm(dot - tip)
print(f"  beam direction (x radial+, y tangent, z up): {beam.round(3)}")
print(f"  beam is {math.degrees(math.asin(-beam[2])):.1f} deg below horizontal, "
      f"{math.degrees(math.atan2(beam[1], beam[0])):.1f} deg from the radial in plan")
h = -beam[:2] / (-beam[2])
print(f"  raising the cap face 1 mm moves the dot {-h[0]:.2f} mm radially and {-h[1]:.2f} mm along the seam")

print("\n== 2. Bench-top loop: a lean on the wood top [Agent estimate] ==")
# Strip of the 30 mm rubberwood top between frame members, point load at mid-span.
E_wood = 10_000.0      # MPa, laminated hardwood along grain [assumed]
t, b, L = 30.0, 300.0, 600.0   # thickness [VEVOR listing], strip width, span [assumed]
P = 200.0              # N, a firm lean / forearm [assumed]
I = b * t**3 / 12
slope = P * L**2 / (16 * E_wood * I)
defl = P * L**3 / (48 * E_wood * I)
for lever in (300, 400, 500):
    print(f"  mid-span deflection {defl:.2f} mm, end slope {slope*1e3:.2f} mrad; "
          f"gun-vs-tube shift for {lever} mm between gun support height and rotator base: {slope*lever:.2f} mm")
print("  (the opening itself weakens the strip; treat as 0.1-0.5 mm order)")

print("\n== 3. Four hanging posts: guidance vs lead screws [Agent] ==")
def fixed_guided_k(E, I, L):
    return 12 * E * I / L**3
L = 300.0
I_al_tube = (25.4**4 - (25.4 - 2 * 3.175)**4) / 12   # 1x1x1/8 in aluminium square tube
I_rod8 = math.pi * 8**4 / 64                          # Tr8 screw root ~ treat as 8 mm rod (generous)
for name, E, I in (("1x1x1/8 in 6063 tube", 69_000, I_al_tube), ("Tr8 lead screw as post", 200_000, I_rod8)):
    k4 = 4 * fixed_guided_k(E, I, L)
    print(f"  {name:24s}: 4 posts, {L:.0f} mm, fixed-guided: {k4:7.0f} N/mm -> 10 N side push moves shelf {10/k4*1000:.1f} um")

print("\n== 4. Countertop sled: contact sensitivities (plan layout in sketches) [Agent] ==")
# Feet F1 (40,-95), F2 (40,-260), F3 (-80,-250) world mm; dot (61.85, 0)
F = np.array([[40, -95], [40, -260], [-80, -250]], float)
D = np.array([geom.R_IN, 0.0])
# Height at the dot from foot heights: barycentric extrapolation in plan
A = np.column_stack([F, np.ones(3)])
w = np.linalg.solve(A.T, np.array([D[0], D[1], 1.0]))
print(f"  dot height = {w[0]:+.2f}*F1 {w[1]:+.2f}*F2 {w[2]:+.2f}*F3  (per mm of each foot)")
# Fence buttons at y = -120 and -280 (x = 84); stop along Y
yb1, yb2 = -120.0, -280.0
lever = (0 - yb2) / (yb1 - yb2)
print(f"  front fence button +1 mm (rear fixed): dot moves {lever:.2f} mm across the seam, heading {math.degrees(1/(yb1-yb2)):.2f} deg")
print(f"  both fence buttons +1 mm: dot 1.00 mm across the seam, no heading change")
print(f"  Y stop +1 mm: heading vs local tangent {math.degrees(math.atan(1/geom.R_IN)):.2f} deg, radial {(math.hypot(geom.R_IN,1)-geom.R_IN)*1000:.0f} um")
m_gun, m_shell = 1.2, 0.5   # kg [Unknown gun mass; assumed]
N = (m_gun + m_shell) * 9.81
for mu in (0.1, 0.2):
    print(f"  friction hold with no preload, mu {mu}: {mu*N:.1f} N (sled weight {N:.0f} N)")

print("\n== 5. Tube thermal growth at the joint [Agent estimate, not a workspace fix] ==")
alpha = 16e-6   # 316L /K
for dT in (50, 100, 200):
    print(f"  bore radius grows {geom.R_IN*alpha*dT*1000:.0f} um for a {dT} K rise of the ring near the joint")
