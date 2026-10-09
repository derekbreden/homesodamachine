"""Wave 2, on machine-that-learns' B (RCM gun carriage): what gravity does to the chain across its
workspace, and what a float at the gun's centre of mass leaves.

B's own assumptions: gun + shell + yoke ~3 kg, CoM ~180 mm from the hole axis; plan angle is a Y
translation, so the gun's orientation is always the vertical-dial-0 orientation. Hole tilt on an arc
about the radial line through the dot, roll on bearings on the grip axis. X/Y/Z stages above.
Y-carriage location is my reading of their sketch (assumed): 330 mm toward -Y and 420 mm above the dot.
CoM: gun 'toward grip' case in the gun's local frame (assumed).
Float: constant-force balancer, line anchored overhead above the CoM's nominal position.
"""
import numpy as np
from pose import pose_point, JOINT

G = 9.81
M = 3.0
W = M * G
D = JOINT.copy()
COM_LOCAL = np.array([0, -25.0, 190.0])
YCAR = D + np.array([40.0, -330.0, 420.0])
HOLE_AXIS = np.array([1.0, 0, 0])


def pose_vals(roll, hole, dx=0.0, dz=0.0):
    com = pose_point(COM_LOCAL, roll, hole, 0) + np.array([dx, 0, dz])
    gb = pose_point(np.array([0, -118.0, 237.0]), roll, hole, 0)
    ga = (gb - D) / np.linalg.norm(gb - D)
    return com, ga


def moments(com, ga, F):
    r = (com - D) / 1000
    Md = np.cross(r, F)                       # about the dot
    m_hole = np.dot(Md, HOLE_AXIS)            # arc drive
    m_roll = np.dot(Md, ga)                   # roll worm
    Mc = np.cross((com - YCAR) / 1000, F)     # at the Y carriage
    return m_hole, m_roll, Mc


com0, _ = pose_vals(45, 30)
rows = []
for Lb in (None, 800.0, 1500.0):
    anchor = None if Lb is None else com0 + np.array([0, 0, Lb])
    res = []
    for roll in (20, 45, 70):
        for hole in (5, 30, 55):
            for dx, dz in ((0, 0), (50, 0), (-50, 0), (0, 50), (0, -50)):
                com, ga = pose_vals(roll, hole, dx, dz)
                F = np.array([0, 0, -W])
                if anchor is not None:
                    u = (anchor - com) / np.linalg.norm(anchor - com)
                    F = F + W * u             # constant-force float along its line
                mh, mr, Mc = moments(com, ga, F)
                res.append((roll, hole, dx, dz, mh, mr, np.linalg.norm(Mc), np.linalg.norm(F)))
    res = np.array(res)
    name = "no float" if Lb is None else f"float, line {Lb:.0f} mm"
    print(f"== {name} ==")
    print(f"   arc (hole-axis) drive moment: {res[:,4].min():+.2f} .. {res[:,4].max():+.2f} N·m")
    print(f"   roll (grip-axis) drive moment: {res[:,5].min():+.2f} .. {res[:,5].max():+.2f} N·m")
    print(f"   moment at the Y carriage: {res[:,6].min():.2f} .. {res[:,6].max():.2f} N·m;"
          f" net force on the chain {res[:,7].min():.2f} .. {res[:,7].max():.2f} N")
print(f"\nCoM travel over the workspace: roll 20-70, hole 5-55, X/Z +/-50 mm. Gun+shell+yoke {M} kg.")
# how far the CoM moves between extreme poses
pts = np.array([pose_vals(r, h)[0] for r in (20, 45, 70) for h in (5, 30, 55)])
print("CoM spread from rotations alone (mm):", np.round(pts.max(0) - pts.min(0), 0))


# ---- keep every drive loaded one way: float fraction f < 1 and attachment offset e from the CoM ----
from pose import rot_matrix
print("\n== Float at a fraction f of the weight, attached at CoM + e (e fixed in the gun frame) ==")
rng = np.random.default_rng(2)
Lb = 1200.0
poses = [(r, h, dx, dz) for r in (20, 45, 70) for h in (5, 30, 55) for dx, dz in ((0, 0), (50, 0), (-50, 0), (0, 50), (0, -50))]
def residuals(f, e_local):
    out = []
    anchor = None
    for (r, h, dx, dz) in poses:
        com, ga = pose_vals(r, h, dx, dz)
        R = rot_matrix(r, h, 0)
        att = com + R @ e_local
        if anchor is None:
            c0, _ = pose_vals(45, 30); anchor = c0 + R @ e_local * 0 + np.array([0, 0, Lb])
        u = (anchor - att) / np.linalg.norm(anchor - att)
        Ff = f * W * u
        Md = np.cross((com - D) / 1000, np.array([0, 0, -W])) + np.cross((att - D) / 1000, Ff)
        Fz = -W + Ff[2]
        out.append((np.dot(Md, HOLE_AXIS), np.dot(Md, ga), Fz))
    return np.array(out)
for f in (1.0, 0.9, 0.8):
    best = None
    for _ in range(4000):
        e = rng.uniform(-40, 40, 3)
        res = residuals(f, e)
        # sign-consistency score: smallest |moment| margin, requiring one sign per drive
        score = min(max(res[:, 0].min(), -res[:, 0].max()), max(res[:, 1].min(), -res[:, 1].max()))
        if best is None or score > best[0]:
            best = (score, e, res)
    s, e, res = best
    print(f"  f = {f:.1f}: best e (gun frame, mm) = {np.round(e, 0)}; arc drive {res[:,0].min():+.2f}..{res[:,0].max():+.2f} N·m,"
          f" roll drive {res[:,1].min():+.2f}..{res[:,1].max():+.2f} N·m, vertical load on Z {res[:,2].min():+.1f}..{res[:,2].max():+.1f} N")

# Y-carriage moment for the 90 % float attached at e = (36, -13, -38) mm (gun frame)
e = np.array([36.0, -13.0, -38.0]); f = 0.9
c0, _ = pose_vals(45, 30); anchor = c0 + np.array([0, 0, Lb])
Ms = []
for (r, h, dx, dz) in poses:
    com, ga = pose_vals(r, h, dx, dz)
    att = com + rot_matrix(r, h, 0) @ e
    Ff = f * W * (anchor - att) / np.linalg.norm(anchor - att)
    Mc = np.cross((com - YCAR) / 1000, np.array([0, 0, -W])) + np.cross((att - YCAR) / 1000, Ff)
    Ms.append(Mc)
Ms = np.array(Ms)
spread = np.linalg.norm(Ms.max(0) - Ms.min(0))
print(f"\n90 % float at e: Y-carriage moment {np.linalg.norm(Ms, axis=1).min():.2f}..{np.linalg.norm(Ms, axis=1).max():.2f} N·m; "
      f"componentwise spread {spread:.2f} N·m")
lever = np.linalg.norm(YCAR - D) / 1000
for label, dM in (("no float", 4.4), ("90 % float, offset", spread)):
    print(f"  {label}: with an assumed 0.1 mrad per N·m carriage tilt, dot moves up to {lever*1e-4*dM*1000:.3f} mm across the workspace (lever {lever*1000:.0f} mm)")
