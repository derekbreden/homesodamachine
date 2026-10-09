"""Rough numbers behind the work-as-datum arrangements (wave 1).

Every input is labelled. [Repo] = repo fabrication sources, [Manual] = X1 Pro
manual, [Obs] = observed on a vendor page 2026-09-28, [Est] = this explorer's
estimate. Nothing here is a requirement.

Run:  python3 datum_budget.py
"""
import math

IN = 25.4
R_IN = 5 * IN / 2 - 0.065 * IN   # 61.85 corner radius [Repo]
R_OUT = 5 * IN / 2               # 63.50 [Repo]
T = 0.065 * IN                   # 1.651 wall [Repo]
E = 193e3                        # MPa, 316L [Est, handbook]

print("=== 1. What a corner-height error does to the dot, gun fixed in space ===")
# Beam direction nozzle->dot at the scene's opening pose (grip 45, hole dial 30,
# vertical -15) from pose_geometry.py (dial offset corrected in wave 2). [Agent proxy]
from pose_geometry import beam_dir, pose_point, GRIP_BASE
_b = beam_dir(45, 30, -15)
bx, bz = _b[0], _b[2]
print(f"  beam direction {tuple(round(v, 3) for v in _b)}")
for dz in (-3.2, -1.0, -0.5, -0.15, +0.15, +0.5, +1.0, +3.2):
    if dz < 0:
        # corner lower than expected: beam meets the bore wall |dz| above the new corner
        where = f"lands on the WALL {abs(dz):.2f} mm above the corner"
    else:
        # corner higher: beam meets the plate face before reaching the wall
        s = dz / abs(bz)
        where = f"lands on the PLATE {abs(bx) * s:.2f} mm inboard of the wall"
    focus = abs(dz) / abs(bz)
    print(f"corner {dz:+5.2f} mm -> dot {where}; focus off by {focus:.2f} mm")
print("  sources: OnlineMetals cut tolerance +/-0.125 in = +/-3.2 mm [Obs];"
      " face runout acceptance 0.30 TIR = +/-0.15 [Repo]")

print("\n=== 2. Pushing on the unbacked lip (direct roller follower) ===")
# Order-of-magnitude: thin ring under diametral point load,
# delta = 0.149 P R^3 / (E I), with an effective band height of
# 1.56*sqrt(R t) (the shell bending length) [Est].
Rm = R_IN + T / 2
h_eff = 1.56 * math.sqrt(Rm * T)
I = h_eff * T ** 3 / 12
comp = 0.149 * Rm ** 3 / (E * I)
print(f"effective band {h_eff:.1f} mm, compliance ~{comp*1000:.0f} um/N")
for P in (1, 2, 5, 10):
    print(f"  {P:>2} N roller load -> ~{P*comp:.2f} mm lip displacement (x0.3..x1 plausible)")

print("\n=== 3. Heat reaching a hub on the plate centre ===")
P_laser = 0.60 * 700      # 60 % of 700 W peak [Repo recipe, Manual peak]
t_bead = 388.61 * (380 / 360) / 8.0   # one lap + 20 deg at 8 mm/s [Repo]
for absorb in (0.3, 0.5, 0.7):        # absorbed fraction [Est]
    Q = P_laser * t_bead * absorb
    for m, name in ((1.40, "first"), (2.01, "second")):
        dT = Q / (m * 500)
        print(f"  absorbed {absorb:.0%}: {Q/1000:4.1f} kJ, {name} closure mean rise ~{dT:4.1f} K")
print("  the plate centre lags the mean; the lip beside the bead runs far hotter [Est]")

print("\n=== 4. Hub seat: residual weight and tipping ===")
# Three stainless ball transfers at r_b on the plate face (plane), a live
# centre on the port-pair midpoint (x, y only, axially sprung), a fork for
# azimuth. Residual load W sits at an offset e from the hub axis.
r_b = 35.0
inradius = r_b / 2
for W in (5, 10, 20):
    print(f"  residual {W:>2} N: CoM offset allowed < {inradius:.1f} mm; "
          f"max disturbing moment before a ball unloads ~{W*inradius/1000:.2f} N*m")
# A hand pressing the trigger near the grip; grip base sits ~233 mm from the
# hub axis at the opening pose (pose_geometry.py, corrected) [Agent proxy].
_g = pose_point(GRIP_BASE, 45, 30, -15)
lever = math.hypot(_g[0], _g[1]) / 1000
for F in (5, 10, 15):  # trigger force [Unknown]
    print(f"  {F:>2} N trigger push at ~{lever*1000:.0f} mm -> {F*lever:.2f} N*m (compare row above)")

print("\n=== 5. Tube in the nest under a moment ===")
# Tube stands loose in the nest [Repo]. Restoring moment before the rim lifts
# on one side ~ (vessel weight + hub preload) * OD radius.
for m, name in ((1.40, "first"), (2.01, "second")):
    for pre in (0, 10, 20):
        Mr = (m * 9.81 + pre) * R_OUT / 1000
        print(f"  {name} closure, preload {pre:>2} N: restoring ~{Mr:.2f} N*m")

print("\n=== 6. Radial error budget of the plate-centre datum [Est] ===")
items = {
    "port-pair midpoint vs plate edge (same laser program)": 0.10,
    "plate offset in bore (0.005 in radial slip) seen at the bore": 0.13,
    "nipple/seat centring in tapped ports": 0.07,
    "live-centre runout (0.0002 in listed) [Obs]": 0.005,
    "frame compliance under loop/wire forces": 0.05,
}
rss = math.sqrt(sum(v * v for v in items.values()))
for k, v in items.items():
    print(f"  +/-{v:.3f}  {k}")
print(f"  RSS ~ +/-{rss:.2f} mm radial; height/tilt follow the plate face directly")
print("  compare: axis-fixed gun on an indicated tube, +/-0.125 radial and +/-0.15 face"
      " at acceptance [Repo], plus the whole tube-length error in height")
