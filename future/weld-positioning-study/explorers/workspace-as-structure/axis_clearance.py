"""Wave 2: is the column over the tube axis clear of the gun, and where does the
gun sit relative to the plate centre, at the scene's true opening pose?

The scene's hole dial is offset: main.js passes (dial - 35) to posePoint
(HOLE_AXIS_OFFSET = 35, default dial 30 -> parameter -5). geom.py applies it.
A script that passes 30 straight to pose_point is showing dial 65.

Gun proxy volumes (scene main.js): nozzle r 8.5 (0-54 mm from tip), graduated
tube r 5.5 (54-100), lens section r 12 (100-118), housing box 34x34x135
(118-253), grip box 30x28 from (0,-25,172) to (0,-111,232). Proxy = [Agent].

Output: for each pose, the minimum horizontal distance from the tube axis to
any gun surface, by height band above the plate face, and the grip-base
position (lever arm for trigger/cable moments about the plate centre).
Run: python3 axis_clearance.py
"""
import math
import numpy as np
import geom

PLATE_Z = geom.CAP_TOP  # plate outer face (dot height) in geom's frame


def cyl_samples(z0, z1, r, n_ax=12, n_c=24):
    out = []
    for z in np.linspace(z0, z1, n_ax):
        for k in range(n_c):
            a = 2 * math.pi * k / n_c
            out.append((r * math.cos(a), r * math.sin(a), z))
    return out


def box_samples(center, size, n=7):
    cx, cy, cz = center
    sx, sy, sz = size
    out = []
    for u in np.linspace(-0.5, 0.5, n):
        for v in np.linspace(-0.5, 0.5, n):
            for w in np.linspace(-0.5, 0.5, n):
                if max(abs(u), abs(v), abs(w)) > 0.49:  # surface only
                    out.append((cx + u * sx, cy + v * sy, cz + w * sz))
    return out


def grip_samples(n=9):
    a = np.array([0, -25, 172.0]); b = np.array([0, -111, 232.0])
    d = (b - a) / np.linalg.norm(b - a)
    nrm = np.cross(d, [1, 0, 0]); nrm /= np.linalg.norm(nrm)
    L = np.linalg.norm(b - a) + 16
    mid = (a + b) / 2
    out = []
    for s in np.linspace(-0.5, 0.5, n):
        for w in np.linspace(-0.5, 0.5, n):
            for q in np.linspace(-0.5, 0.5, n):
                if max(abs(w), abs(q), abs(s)) > 0.49:
                    out.append(tuple(mid + s * L * d + w * 30 * np.array([1, 0, 0]) + q * 28 * nrm))
    return out


LOCAL = (cyl_samples(0, 54, 8.5) + cyl_samples(54, 100, 5.5) + cyl_samples(100, 118, 12)
         + box_samples((0, 0, 185.5), (34, 34, 135)) + grip_samples())


def world(roll, dial, vert):
    hp = dial - geom.HOLE_OFFSET
    return np.array([geom.pose_point(p, roll, hp, vert) for p in LOCAL])


def report(roll, dial, vert, bands=((0, 45), (45, 100), (100, 180), (180, 300))):
    w = world(roll, dial, vert)
    r = np.hypot(w[:, 0], w[:, 1])
    z = w[:, 2] - PLATE_Z
    gb = geom.pose_point(geom.GRIP_BASE, roll, dial - geom.HOLE_OFFSET, vert)
    s = f"grip {roll:3d} dial {dial:3d} vert {vert:4d} | "
    for z0, z1 in bands:
        m = (z >= z0) & (z < z1)
        s += f"z{z0}-{z1}: {r[m].min():5.1f}  " if m.any() else f"z{z0}-{z1}:   -    "
    s += f"| grip base r {math.hypot(gb[0], gb[1]):5.1f} z {gb[2]-PLATE_Z:5.1f} az {math.degrees(math.atan2(gb[1], gb[0])):6.1f}"
    print(s)


if __name__ == "__main__":
    print("min horizontal distance (mm) from tube axis to any gun surface, by height above plate face")
    print("-- scene opening pose, and what a script without the dial offset shows --")
    report(45, 30, -15)
    report(45, 65, -15)
    print("-- neighbourhood of the opening pose --")
    for roll in (30, 45, 60):
        for dial in (10, 20, 30, 40, 50):
            for vert in (-30, -15, 0, 15):
                report(roll, dial, vert)
