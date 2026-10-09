"""Three tension wires whose lines meet at the laser dot: a virtual ball joint at the dot.

Attachment points A_i sit on the gun shell at distance a_i from the dot along unit
direction u_i; each wire runs on along u_i to an anchor P_i at distance a_i + L_i.
Rotating the gun about the dot leaves every wire length unchanged to first order.
This script finds the dot translation forced by the fixed wire lengths when the gun
is turned by a finite angle about each of Derek's three axes, and the translational
stiffness the three wires give the dot.

All directions and lengths are illustrative choices, not a design.
"""
import numpy as np
from scipy.optimize import fsolve
from pose import pose_all, JOINT

np.set_printoptions(precision=4, suppress=True)
D = JOINT.copy()
P0 = pose_all(45, 30, -15)


def unit(az_deg, el_deg):
    az, el = np.radians(az_deg), np.radians(el_deg)
    return np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])


def rodrigues(n, th):
    n = n / np.linalg.norm(n)
    K = np.array([[0, -n[2], n[1]], [n[2], 0, -n[0]], [-n[1], n[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * K @ K


AXES = {
    "grip axis": P0["grip_base"] - D,
    "hole axis": np.array([-1.0, 0, 0]),       # horizontal radial line through dot and port centres
    "vertical axis": np.array([0, 0, 1.0]),
}

LAYOUTS = {
    # (azimuth, elevation) per wire; a = attachment distance from dot; L = free wire length
    "spread 120 deg, el 55, a=70, L=400": ([(90, 55), (-30, 55), (210, 55)], 70, 400),
    "spread 120 deg, el 55, a=120, L=400": ([(90, 55), (-30, 55), (210, 55)], 120, 400),
    "narrow cone el 70, a=70, L=400": ([(90, 70), (-30, 70), (210, 70)], 70, 400),
    "spread, el 55, a=70, L=800": ([(90, 55), (-30, 55), (210, 55)], 70, 800),
}

for lname, (dirs, a, L) in LAYOUTS.items():
    U = np.array([unit(*d) for d in dirs])
    A0 = D + a * U
    Pan = D + (a + L) * U
    print(f"\n== {lname} ==")
    # translational stiffness at the dot from axial wire stiffness k = EA/L
    for label, EA in (("1.0 mm 7x7 stainless (EA~52 kN)", 52e3), ("2 mm polyester (EA~6.6 kN)", 6.6e3)):
        k = EA / L
        K = sum(k * np.outer(u, u) for u in U)
        ev = np.linalg.eigvalsh(K)
        print(f"  {label}: dot stiffness eigenvalues {ev.round(0)} N/mm")
    for axname, n in AXES.items():
        row = []
        for deg in (2, 5, 10, 20):
            Rm = rodrigues(n, np.radians(deg))

            def f(t):
                return [np.linalg.norm(D + Rm @ (A0[i] - D) + t - Pan[i]) - L for i in range(3)]
            t = fsolve(f, np.zeros(3), xtol=1e-12)
            row.append(f"{deg:>2} deg -> dot moves {np.linalg.norm(t):.3f} mm")
        print(f"  turn about {axname:13s}: " + "; ".join(row))

# Compare: a real ball joint 56 mm up the barrel (a hanging loop on the graduated tube)
print("\n== Compare: pivot at a real point 56 mm from the dot ==")
for deg in (2, 5, 10, 20):
    print(f"  {deg:>2} deg about a pivot 56 mm away moves the dot {2*56*np.sin(np.radians(deg)/2):.2f} mm")
