"""Draw the sloped underside's courses from the stage's own moves.

    picture.py <out dir with preamble-moves.npz and plate_1.gcode> <print.json> <png prefix>"""
import json, re, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

out, report, prefix = sys.argv[1:4]
rep = json.load(open(report))
cx, cy, cz = rep["base_rim_supports"]["seat_print_world_center_mm"]
T = math.tan(math.radians(15)); C = math.cos(math.radians(15))
d = np.load(f"{out}/preamble-moves.npz", allow_pickle=True)
m, feats = d["moves"], d["features"]
lay = m[:, 0] == 1
# classify by height over the face plane at the move's end
zf = m[:, 6] - (cz - (m[:, 5] - cy) * T)
n = zf * C
groups = [("scaffold, first layer", lay & (feats == "Support") & (np.abs(m[:, 6] - 0.2) < 1e-6)),
          ("scaffold, a middle layer", lay & (feats == "Support") & (np.abs(m[:, 6] - 7.4) < 1e-6)),
          ("roof 1: level lines", lay & (feats == "Support interface") & (n < -0.60)),
          ("roof 2: up the slope", lay & (feats == "Support interface") & (n > -0.60) & (n < -0.36)),
          ("roof 3: diagonal, the deck", lay & (feats == "Support interface") & (n > -0.36) & (n < -0.12)),
          ("bore deck", lay & (feats == "Support interface") & (n > -0.12)),
          ("skin 1: rings and uphill lines", lay & (feats == "Bottom surface") & (n < 0.36) | (lay & (feats == "Internal solid infill") & (n < 0.36))),
          ("skin 2: rings and diagonal", lay & (n > 0.36))]
fig, axes = plt.subplots(2, 4, figsize=(22, 11.5))
for ax, (title, q) in zip(axes.flat, groups):
    seg = np.stack([m[q][:, 1:3], m[q][:, 4:6]], axis=1)
    ax.add_collection(LineCollection(seg, linewidths=0.5, colors="#16212b"))
    ax.set_xlim(cx - 34, cx + 34); ax.set_ylim(cy - 34, cy + 34); ax.set_aspect("equal")
    ax.set_title(f"{title}  ({int(q.sum())} moves)", fontsize=11)
    ax.invert_yaxis()
    ax.set_xlabel("plate X, mm"); ax.set_ylabel("plate Y, mm (front of printer up)")
fig.tight_layout(); fig.savefig(prefix + "-courses.png", dpi=110); plt.close(fig)

# a section along the slope through x = cx + 21 (through the ring, clear of the bore)
fig, ax = plt.subplots(figsize=(22, 8))
x0 = cx + 24.0
colors = {"Support": "#8a97a3", "Support interface": "#c2410c", "Bottom surface": "#0f766e", "Internal solid infill": "#1d4ed8"}
for name, color in colors.items():
    q = lay & (feats == name) & (np.minimum(m[:, 1], m[:, 4]) <= x0 + 0.7) & (np.maximum(m[:, 1], m[:, 4]) >= x0 - 0.7)
    seg = np.stack([m[q][:, [2, 3]], m[q][:, [5, 6]]], axis=1)
    ax.add_collection(LineCollection(seg, linewidths=1.2, colors=color, label=name))
# the plate's kept base courses near that section
WORD = re.compile(r"([XYZE])(-?\d*\.?\d+)")
x = y = z = None; started = False; obj = None; kept = []
for line in open(f"{out}/plate_1.gcode", errors="replace"):
    if line.startswith(";"):
        if line.startswith("; ===== end of the sloped underside"): started = True
        elif line.startswith("; start printing object"): obj = line.rsplit(":", 1)[1].strip()
        elif line.startswith("; stop printing object"): obj = None
        elif line.startswith("; Z_HEIGHT:") and started and float(line.split(":")[1]) > 6.0: break
        continue
    if line[:3] != "G1 ": continue
    w = {k: float(v) for k, v in WORD.findall(line.split(";", 1)[0])}
    nx, ny, nz = w.get("X", x), w.get("Y", y), w.get("Z", z)
    if started and obj == "1901" and w.get("E", 0) > 0 and x is not None and ("X" in w or "Y" in w):
        if min(x, nx) <= x0 + 0.7 and max(x, nx) >= x0 - 0.7:
            kept.append([[y, z], [ny, nz]])
    x, y, z = nx, ny, nz
ax.add_collection(LineCollection(np.array(kept), linewidths=1.2, colors="#111111", label="the base's own level courses, kept"))
ys = np.array([cy - 32, cy + 31])
ax.plot(ys, cz - (ys - cy) * T, color="#dc2626", lw=0.8, ls="--", label="mounting face")
ax.set_xlim(cy + 31, cy - 33); ax.set_ylim(-0.3, 6.5)
ax.set_xlabel("plate Y, mm (the slope climbs toward the front of the printer, right)"); ax.set_ylabel("Z, mm")
ax.set_title("Section along the slope, low end: bed at Z 0, vertical scale stretched")
ax.legend(loc="upper left"); fig.tight_layout(); fig.savefig(prefix + "-section.png", dpi=110); plt.close(fig)
print("wrote", prefix + "-courses.png", prefix + "-section.png")
