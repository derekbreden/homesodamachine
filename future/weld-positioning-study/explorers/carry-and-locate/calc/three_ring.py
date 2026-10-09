"""Derek's two loops plus a third ring: vertical wire shares at the opening pose.
Three vertical wires (tip T, base B, third C) carry the gun weight; statics in plan.
Gun mass 1.0 kg assumed; umbilical/wire weight hung directly on the base loop is extra."""
import numpy as np
from pose import pose_point, LOCAL
POSE = (45, 30, -15)
T = pose_point(np.array([0, 0, 40.0]), *POSE)
gdir = (LOCAL["grip_end"] - LOCAL["grip_start"]); gdir /= np.linalg.norm(gdir)
B = pose_point(LOCAL["grip_base"] + 40 * gdir, *POSE)
thirds = {"housing back top": LOCAL["housing_top_back"], "housing back centre": LOCAL["housing_back"],
          "housing front top": LOCAL["housing_top_front"]}
coms = {"housing centre": np.array([0, 0, 185.5]), "toward grip": np.array([0, -25, 190.0])}
W = 9.81
for cn, c in thirds.items():
    C = pose_point(c, *POSE)
    for mn, m in coms.items():
        G = pose_point(m, *POSE)
        A = np.array([[1, 1, 1], [T[0], B[0], C[0]], [T[1], B[1], C[1]]])
        f = np.linalg.solve(A, np.array([W, W * G[0], W * G[1]]))
        print(f"third ring at {cn:20s} (world {C.round(0)}), CoM {mn:14s}: tip {f[0]:5.2f} N, base {f[1]:5.2f} N, third {f[2]:5.2f} N")
