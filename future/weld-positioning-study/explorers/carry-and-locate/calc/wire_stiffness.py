"""Idea B: dot displacement under disturbances for the all-taut layout, from wire axial stiffness only.
Twist (translation of the dot, rotation about the dot) -> wire elongation e_i = u_i . (t + w x r_i).
K = J^T diag(k) J. 1/16 in (1.6 mm) and 1.0 mm 7x7 stainless; frame assumed rigid (it is not)."""
import numpy as np
from pose import pose_point, LOCAL, JOINT
POSE = (45, 30, -15); D = JOINT.copy()
def unit(az, el):
    az, el = np.radians(az), np.radians(el); return np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
gp = lambda l: pose_point(np.asarray(l, float), *POSE)
gb, ht = gp(LOCAL["grip_base"]), gp(LOCAL["housing_top_back"])
wires = [(D + 70*unit(a, 55), unit(a, 55), 400) for a in (90, -30, 210)] + \
        [(gb, unit(32, 43), 330), (gb, unit(184, 72), 330), (ht, unit(-158, 12), 330)]
R = np.column_stack([gp(e) - gp([0,0,0]) for e in np.eye(3)])
tp = gp([0, -40, 175])
for label, EA in (("1.6 mm rope, EA~130 kN", 130e3), ("1.0 mm rope, EA~52 kN", 52e3)):
    J = np.array([np.concatenate([u, np.cross(p - D, u)]) for p, u, L in wires])
    k = np.array([EA / L for p, u, L in wires])
    K = J.T @ np.diag(k) @ J
    C = np.linalg.inv(K)
    print(f"== {label} ==")
    for name, (pt, f) in {"5 N +X at dot": (D, [5,0,0]), "5 N +Y at dot": (D, [0,5,0]), "5 N +Z at dot": (D, [0,0,5]),
                          "5 N trigger push": (tp, R @ np.array([0, 5.0, 0])),
                          "3 N tangential drag at wire tip (stuck wire)": (D, [0, 3, 0])}.items():
        f = np.asarray(f, float); w = np.concatenate([f, np.cross(pt - D, f)])
        x = C @ w
        print(f"  {name:45s}: dot moves {np.linalg.norm(x[:3])*1000:.1f} um, gun turns {np.degrees(np.linalg.norm(x[3:]))*60:.2f} arcmin")
