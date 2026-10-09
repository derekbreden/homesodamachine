"""Load and lever geometry of the gun at the scene's opening pose (grip 45, hole 30, vertical -15).

Everything about mass is ASSUMED (gun mass is not in the manual):
  gun mass cases 0.6 / 1.0 / 1.5 kg; centre of mass (CoM) cases in the gun's local frame.
The gun geometry is the scene's schematic proxy (see pose.py).
"""
import numpy as np
from pose import pose_point, pose_all, rot_matrix, JOINT, BENCH_Z, LOCAL, R_IN, RIM

np.set_printoptions(precision=1, suppress=True)
G = 9.81
POSE = (45, 30, -15)
P = pose_all(*POSE)
R = rot_matrix(*POSE)
dot = P["dot"]

# CoM cases (local frame): housing centre; housing + grip/collimator pulled toward grip; forward-biased
COM_CASES = {
    "housing centre (0,0,185)": np.array([0, 0, 185.5]),
    "toward grip (0,-25,190)": np.array([0, -25, 190.0]),
    "forward (0,-10,160)": np.array([0, -10, 160.0]),
}


def dist_point_line(p, a, b):
    d = (b - a) / np.linalg.norm(b - a)
    v = p - a
    return np.linalg.norm(v - np.dot(v, d) * d)


print("== Gun CoM candidates at the opening pose ==")
grip_axis = P["grip_base"] - dot
for name, c in COM_CASES.items():
    cw = pose_point(c, *POSE)
    off = cw - dot
    horiz = np.hypot(off[0], off[1])
    print(f"{name:28s} world={cw}  above dot {off[2]:.0f} mm, horizontal from dot {horiz:.0f} mm, "
          f"from grip axis {dist_point_line(cw, dot, P['grip_base']):.0f} mm, bench_z={cw[2]+BENCH_Z:.0f}")
    for m in (0.6, 1.0, 1.5):
        W = m * G
        # gravity moment about the dot (vector) = r x F
        M = np.cross(off / 1000, np.array([0, 0, -W]))
        # component about the grip axis
        ga = grip_axis / np.linalg.norm(grip_axis)
        print(f"   m={m} kg: |M about dot| = {np.linalg.norm(M):.2f} N·m; about grip axis {np.dot(M, ga):+.2f} N·m;"
              f" toppling stiffness about dot ~ -W*h = {-W*off[2]/1000:.2f} N·m/rad")

# --- Derek's two-loop hang --------------------------------------------------
print("\n== Two loops: tip loop on the graduated tube, base loop on the cable/shell collar ==")
tip_local = np.array([0, 0, 40.0])        # on the graduated tube, 56 mm from the dot
# base loop: 40 mm beyond the grip base along the grip direction (around umbilical + wire / shell collar)
gdir = (LOCAL["grip_end"] - LOCAL["grip_start"]) / np.linalg.norm(LOCAL["grip_end"] - LOCAL["grip_start"])
base_local = LOCAL["grip_base"] + 40 * gdir
T = pose_point(tip_local, *POSE)
B = pose_point(base_local, *POSE)
print("tip loop  world", T, "bench_z", round(T[2] + BENCH_Z), " dist from dot", np.linalg.norm(T - dot).round(1))
print("base loop world", B, "bench_z", round(B[2] + BENCH_Z), " dist from dot", np.linalg.norm(B - dot).round(1))
print("distance of the dot from the T-B line:", dist_point_line(dot, T, B).round(1), "mm")
print("distance of the grip base from the T-B line:", dist_point_line(P["grip_base"], T, B).round(1), "mm")
ang = np.degrees(np.arccos(np.dot((B - T) / np.linalg.norm(B - T), grip_axis / np.linalg.norm(grip_axis))))
print(f"angle between T-B line and Derek's grip axis: {ang:.1f} deg")

# Vertical wires at T and B: weight shares, plus the roll moment the arm or a 3rd ring must take.
for name, c in COM_CASES.items():
    cw = pose_point(c, *POSE)
    # plan-view: project CoM onto the T-B line in plan
    t2, b2, c2 = T[:2], B[:2], cw[:2]
    d = (b2 - t2) / np.linalg.norm(b2 - t2)
    s = np.dot(c2 - t2, d) / np.linalg.norm(b2 - t2)   # fraction along T->B
    perp = np.cross(np.append(d, 0), np.append(c2 - t2, 0))[2]
    print(f"{name:28s} share tip {1-s:.2f} / base {s:.2f}; CoM is {perp:+.0f} mm off the T-B line in plan "
          f"-> roll moment {1.0*G*abs(perp)/1000:.2f} N·m per kg of gun")

# --- stiffness of the elements --------------------------------------------------
print("\n== Element stiffness (estimates) ==")
for Tn in (3, 5, 8):
    for L in (300, 500, 800):
        pass
print("pendulum wire, horizontal k = T/L:")
for Tn in (3.0, 5.0, 8.0):
    print("   T=%.0f N:" % Tn, ", ".join(f"L={L} mm -> {Tn/L:.3f} N/mm" for L in (300, 500, 800)))
print("ring hanging around a barrel, lateral k = T/(R_loop - r_barrel):",
      ", ".join(f"gap {g} mm -> {5/g:.2f} N/mm (T=5 N)" for g in (2, 5, 10)))
# bungee: 3/16" / 5 mm shock cord, ~15 N at 100 % stretch (assumed), free length 250 mm
k_bungee = 15 / 250
print(f"one bungee, 15 N at 100 % stretch on 250 mm free length: ~{k_bungee:.3f} N/mm; an opposed pair ~{2*k_bungee:.2f} N/mm")
# wires in tension, axial: EA/L
for label, d_mm, E_gpa, fill in (("1.6 mm 7x7 stainless wire rope", 1.6, 110, 0.6),
                                 ("1.0 mm 7x7 stainless wire rope", 1.0, 110, 0.6),
                                 ("2 mm braided polyester (grow-light hanger)", 2.0, 3, 0.7),
                                 ("1.5 mm Dyneema/UHMWPE braid", 1.5, 60, 0.6)):
    A = np.pi * d_mm**2 / 4 * fill
    EA = E_gpa * 1e3 * A  # N
    print(f"   {label}: EA ~ {EA/1000:.1f} kN -> k over 500 mm ~ {EA/500:.0f} N/mm")

# --- disturbances -> dot displacement ---------------------------------------------
print("\n== Dot displacement = force / stiffness at the dot ==")
forces = {"trigger by finger (assumed 3-8 N)": 5.0, "wire push / conduit spring (assumed 1-3 N)": 2.0,
          "umbilical creep change (assumed 0.5 N)": 0.5, "stuck-wire stickout bending (est. 2.6 N)": 2.6}
for kname, k in (("soft float alone (0.05 N/mm)", 0.05), ("printed arm/stage (20 N/mm)", 20.0),
                 ("stiff locator (200 N/mm)", 200.0), ("wire-tension locator (1000 N/mm)", 1000.0)):
    print(f"  {kname}: " + "; ".join(f"{fn.split(' (')[0]} {F/k:.3f} mm" for fn, F in forces.items()))

# stuck 0.030 in ER316L wire: bending moment capacity of the stickout
d = 0.030 * 25.4e-3
for sy in (400e6, 700e6):
    Mp = sy * d**3 / 6   # plastic section modulus of round = d^3/6
    print(f"stuck wire, yield {sy/1e6:.0f} MPa: plastic moment {Mp*1000:.1f} N·mm -> force at 10 mm stickout {Mp/0.010:.1f} N")
# rotator pull on a stuck wire
hold = 1.9 * 4.5  # N·m at the table (motor 1.9 N·m holding, 4.5:1)
print(f"rotator can pull up to ~{hold/0.0618:.0f} N tangentially at the bead radius (holding-torque bound)")

# --- the tangent is nearly a don't-care direction --------------------------------
print("\n== Tangential (Y) error of the gun relative to the circle ==")
for s in (0.5, 1, 2, 5):
    print(f"  shift {s} mm along the tangent: radial error {s**2/(2*R_IN):.3f} mm, "
          f"plan angle vs local tangent {np.degrees(s/R_IN):.2f} deg")

# --- wobble reaction ---------------------------------------------------------------
print("\n== 80 Hz wobble reaction on a free-floating gun (x = F/(m w^2)) ==")
w = 2 * np.pi * 80
for F in (0.1, 0.5, 2.0):
    print(f"  reaction amplitude {F} N on 1 kg -> {F/(1.0*w**2)*1000:.4f} mm")
