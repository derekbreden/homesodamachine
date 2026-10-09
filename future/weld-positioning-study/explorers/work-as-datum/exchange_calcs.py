"""Wave-2 numbers for work-as-datum's repairs of workspace-as-structure's ideas.

W1  collar-hung centre in the table-opening gantry (plate centre forced onto a
    plunger hung from the collar; the plunger's reading sets the shelf height).
L1  work-borne lid parked by the collar (the lid rides the plate; the gun's nose
    ring is on the lid, its tail on the workspace).

[Repo] repo value, [Obs] observed, [Agent] scene proxy / other explorer, [Est] mine.
Run:  python3 exchange_calcs.py
"""
import math
from pose_geometry import pose_point, beam_dir, GRIP_BASE, R_IN, RECESS

POSE = (45, 30, -15)   # scene dials: grip 45, hole 30, vertical -15 [Agent]

print("=== W1. Collar-hung centre ===")
# Plunger arm: from the +Y edge of a Ø160 opening to the tube axis, loaded by
# the plunger spring. 20 x 20 mm 6061 bar [Est].
E_al, b, L = 69e3, 20.0, 100.0
I = b ** 4 / 12
for P in (30, 50):
    d = P * L ** 3 / (3 * E_al * I)
    print(f"  arm 20x20 Al, {L:.0f} mm, {P} N preload: tip deflection {d*1000:.0f} um (static, constant)")
# Ball-in-cone centring: lateral force available before the ball rides up the
# cone, for a 90 deg included countersink.
for P in (30, 50):
    print(f"  90 deg cone under {P} N: lateral centring capacity ~{P * math.tan(math.radians(45)):.0f} N")
# Friction the tube top must overcome to shift in the nest: vessel weight +
# preload at mu 0.3 on the rim [Est].
for m in (1.40, 2.01):
    for P in (30, 50):
        print(f"  vessel {m} kg + {P} N: rim friction ~{0.3*(m*9.81+P):.0f} N (tube pivots in the nest)")
# Tube tilt and bottom-rim rocking if the plunger is off the rotator axis by e.
for e in (0.1, 0.2, 0.5):
    tilt = e / 152.4
    print(f"  plunger {e} mm off the rotator axis: tube tilt {math.degrees(tilt)*60:.1f} arcmin, "
          f"bottom rim rocks ~{e*63.5/152.4:.2f} mm per rev")
# Side-loading clearance with the port seat on the plate: nipples stand 25 mm
# above the plate face, i.e. 18.7 mm above the rim. Shelf drop 70 mm, top 30 mm
# [workspace-as-structure build].
above_rim = 25.0 - RECESS
gap = 70 - 30
print(f"  seat/nipples {above_rim:.1f} mm above the rim vs {gap} mm under the top with the shelf dropped: "
      f"{gap-above_rim:.1f} mm to spare")

print("\n=== W1b. Sprung shelf against a rigid centre ===")
m_rot = 8.0   # rotator + adapter [Est]
for m_ves in (1.40, 2.01):
    W = (m_rot + m_ves) * 9.81
    for span in (6.4,):  # +/-3.2 mm tube length
        k = 30.0 / span  # keep preload variation within 30 N across the length range
        pre = 45.0
        comp = (W + pre) / k
        print(f"  vessel {m_ves} kg: springs carry {W:.0f} N + {pre:.0f} N preload; total rate {k:.1f} N/mm "
              f"keeps preload within 30 N over +/-3.2 mm; precompression {comp:.0f} mm")

print("\n=== L1. Work-borne lid, gun nose on the lid, tail on the workspace ===")
tip = pose_point((0, 0, 0), *POSE)
dot = pose_point((0, 0, -16), *POSE)
gb = pose_point(GRIP_BASE, *POSE)
print(f"  nozzle tip {tuple(round(v,1) for v in tip)}; grip base {tuple(round(v,1) for v in gb)}")
# Nose ring around the nozzle 10 mm above its tip (local z = 10): distance from the dot
ring = pose_point((0, 0, 10), *POSE)
a = math.dist(ring, dot)
# Tail support near the grip (local (0,-80,215)) [Est]
tail = pose_point((0, -80, 215), *POSE)
bdist = math.dist(ring, tail)
print(f"  ring {tuple(round(v,1) for v in ring)} is {a:.0f} mm from the dot; tail support {bdist:.0f} mm from the ring")
for dz in (0.15, 1.0, 3.2):
    err = dz * a / bdist
    ang = math.degrees(dz / bdist)
    print(f"  work moves {dz:>4} mm -> dot misses the moved corner by {err:.2f} mm; gun tilts {ang:.2f} deg")
print("  (a fully workspace-held gun misses by the whole motion; a fully work-held gun by ~0)")
# Where the barrel and wire cross lid levels: the notch the lid needs.
for zl in (9.4, 12.4, 20, 30):
    # barrel: find local z whose world z = zl
    lo, hi = 0.0, 150.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if pose_point((0, 0, mid), *POSE)[2] < zl:
            lo = mid
        else:
            hi = mid
    p = pose_point((0, 0, lo), *POSE)
    print(f"  barrel axis crosses z={zl:>4}: r {math.hypot(p[0],p[1]):5.1f}, azimuth {math.degrees(math.atan2(p[1],p[0])):6.1f} deg")
wb = pose_point((0, -20, 110), *POSE)
for zl in (9.4, 12.4, 20):
    t = (wb[2] - zl) / (wb[2] - dot[2])
    q = [wb[i] + t * (dot[i] - wb[i]) for i in range(3)]
    print(f"  wire crosses z={zl:>4}: r {math.hypot(q[0],q[1]):5.1f}, azimuth {math.degrees(math.atan2(q[1],q[0])):6.1f} deg")
# Lid gap above the rim when it rides the plate: rim height above the plate face
# is the recess (6.35) +/- spacer seating and rim waviness [Est 0.1-0.3].
print(f"  lid underside at plate+{RECESS+3:.2f}: 3 mm above a nominal rim; rim variation relative to the"
      f" plate ~0.1-0.3 mm [Est], independent of tube length and runout")
print("  pick-up window: lugs 5 mm above the collar when riding a nominal tube; a tube 3.2 mm short"
      " still leaves 1.8 mm; lid parks when the plate drops > 5 mm")
