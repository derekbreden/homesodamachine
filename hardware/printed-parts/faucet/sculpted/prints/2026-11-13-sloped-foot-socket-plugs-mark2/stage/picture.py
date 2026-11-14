"""Draw the sloped foot's courses from the stage's own moves.

    picture.py <out dir with preamble-moves.npz and plate_1.gcode> <print.json> <png prefix>"""
import json, re, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

out, report, prefix = sys.argv[1:4]
rep = json.load(open(report))
rec = json.load(open(f"{out}/sloped-underside.json"))
cx, cy, cz = rep["base_rim_supports"]["seat_print_world_center_mm"]
T = math.tan(math.radians(15)); C = math.cos(math.radians(15)); S = math.sin(math.radians(15))
d = np.load(f"{out}/preamble-moves.npz", allow_pickle=True)
m, feats = d["moves"], d["features"]
lay = m[:, 0] == 1
n = (m[:, 6] - (cz - (m[:, 5] - cy) * T)) * C          # the move's end over the face, along the normal
course = np.round(n / 0.24).astype(int)
shoulder = rec["stack_normal_mm"]["shoulder_course"]
top = int(round(rec["stack_normal_mm"]["slab_top"] / 0.24))
colors = {"Support": "#9aa5b1", "Support interface": "#c2410c", "Bottom surface": "#0f766e", "Outer wall": "#111111",
          "Internal solid infill": "#1d4ed8", "Bridge": "#dc2626"}
panels = [("course 1, the face: rings, then lines up the slope", 1), ("course 2: level lines across the slope", 2),
          ("course 3: lines up the slope", 3), (f"course {shoulder - 1}, under the shoulders: plugs at their tops", shoulder - 1),
          (f"course {shoulder}: the socket shoulders bridged over the plugs", shoulder), (f"course {top}, the last sloped course", top)]
fig, axes = plt.subplots(2, 3, figsize=(21, 14.5))
for ax, (title, k) in zip(axes.flat, panels):
    q = lay & (course == k) & (feats != "Support interface")
    for name, color in colors.items():
        qq = q & (feats == name)
        if qq.any():
            seg = np.stack([m[qq][:, 1:3], m[qq][:, 4:6]], axis=1)
            ax.add_collection(LineCollection(seg, linewidths=0.55, colors=color, label=f"{name} ({int(qq.sum())})"))
    ax.set_xlim(cx - 34, cx + 34); ax.set_ylim(cy - 34, cy + 34); ax.set_aspect("equal"); ax.invert_yaxis()
    ax.set_title(title, fontsize=12); ax.legend(fontsize=8, loc="lower right")
    ax.set_xlabel("plate X, mm"); ax.set_ylabel("plate Y, mm (front of printer up)")
fig.tight_layout(); fig.savefig(prefix + "-courses.png", dpi=100); plt.close(fig)

# a section along the slope through the fore socket (x = cx), true scale
fig, ax = plt.subplots(figsize=(21, 9))
x0 = cx
def crossing(q, half=0.32):
    return q & (np.minimum(m[:, 1], m[:, 4]) <= x0 + half) & (np.maximum(m[:, 1], m[:, 4]) >= x0 - half)
for name, color in colors.items():
    qq = crossing(lay & (feats == name))
    if not qq.any():
        continue
    # keep only the part of each move near the section, so lines that cross it show as points
    rows = m[qq]
    segs = []
    for r in rows:
        (xa, ya, za), (xb, yb, zb) = r[1:4], r[4:7]
        if abs(xb - xa) < 1e-9:
            segs.append([[ya, za], [yb, zb]])
        else:
            ts = sorted(min(1.0, max(0.0, (x0 + s * 0.32 - xa) / (xb - xa))) for s in (-1, 1))
            segs.append([[ya + (yb - ya) * ts[0], za + (zb - za) * ts[0]], [ya + (yb - ya) * ts[1], za + (zb - za) * ts[1]]])
    ax.add_collection(LineCollection(np.array(segs), linewidths=2.2 if name != "Support" else 1.6, colors=color, label=name))
WORD = re.compile(r"([XYZE])(-?\d*\.?\d+)")
x = y = z = None; started = False; obj = None; kept = []
for line in open(f"{out}/plate_1.gcode", errors="replace"):
    if line.startswith(";"):
        if line.startswith("; ===== end of the sloped underside"): started = True
        elif line.startswith("; start printing object"): obj = line.rsplit(":", 1)[1].strip()
        elif line.startswith("; stop printing object"): obj = None
        elif line.startswith("; Z_HEIGHT:") and started and float(line.split(":")[1]) > 21.0: break
        continue
    if line[:3] != "G1 ": continue
    w = {k: float(v) for k, v in WORD.findall(line.split(";", 1)[0])}
    nx, ny, nz = w.get("X", x), w.get("Y", y), w.get("Z", z)
    if started and obj == "1901" and w.get("E", 0) > 0 and x is not None and ("X" in w or "Y" in w):
        if min(x, nx) <= x0 + 0.32 and max(x, nx) >= x0 - 0.32 and ny < cy - 14:
            if abs(nx - x) < 1e-9:
                kept.append([[y, z], [ny, nz]])
            else:
                ts = sorted(min(1.0, max(0.0, (x0 + s * 0.32 - x) / (nx - x))) for s in (-1, 1))
                kept.append([[y + (ny - y) * ts[0], z + (nz - z) * ts[0]], [y + (ny - y) * ts[1], z + (nz - z) * ts[1]]])
    x, y, z = nx, ny, nz
ax.add_collection(LineCollection(np.array(kept), linewidths=2.2, colors="#7c3aed", label="the base's level courses"))
ys = np.array([cy - 33, cy - 13])
ax.plot(ys, cz - (ys - cy) * T, color="#16a34a", lw=1.0, ls="--", label="mounting face")
ax.set_xlim(cy - 13.5, cy - 32.5); ax.set_ylim(9.0, 20.5); ax.set_aspect("equal")
ax.set_xlabel("plate Y, mm (the slope climbs toward the front of the printer, right)"); ax.set_ylabel("Z, mm")
ax.set_title("Section along the slope through the fore insert socket, true scale: scaffold, roof, plug, sloped courses, level courses")
ax.legend(loc="upper left", fontsize=10); fig.tight_layout(); fig.savefig(prefix + "-section.png", dpi=100); plt.close(fig)
print("wrote", prefix + "-courses.png", prefix + "-section.png")
