"""The left-active toolhead's underside as a height map about the active tip.

    headmap.py <head dir> <out.npz>

H[iy, ix] is the lowest modelled point of the head over the cell at (X0 + ix*STEP, Y0 + iy*STEP)
from the active nozzle's tip, +X operator's right, +Y toward the back; inf where nothing hangs.
The active nozzle is kept apart, in N."""
import json, sys, numpy as np

STEP = 0.5
X0, X1, Y0, Y1 = -40.0, 76.0, -30.0, 110.0
ZMAX = 30.0

def raster(V, T, H):
    tri = V[T]
    lo = tri.min(axis=1)
    keep = lo[:, 2] < ZMAX
    for a, b, c in tri[keep]:
        e = max(np.linalg.norm(b - a), np.linalg.norm(c - a), np.linalg.norm(c - b))
        n = max(2, int(np.ceil(e / (STEP * 0.5))))
        u, v = np.meshgrid(np.arange(n + 1) / n, np.arange(n + 1) / n)
        m = (u + v) <= 1.0 + 1e-9
        u, v = u[m], v[m]
        p = a[None] + u[:, None] * (b - a)[None] + v[:, None] * (c - a)[None]
        ix = np.round((p[:, 0] - X0) / STEP).astype(int)
        iy = np.round((p[:, 1] - Y0) / STEP).astype(int)
        ok = (ix >= 0) & (ix < H.shape[1]) & (iy >= 0) & (iy < H.shape[0])
        np.minimum.at(H, (iy[ok], ix[ok]), p[ok, 2])

def main():
    d, out = sys.argv[1], sys.argv[2]
    z = np.load(f"{d}/h2c-left-active.step.npz", allow_pickle=True)
    names = json.loads(bytes(z["names"]).decode())
    shape = (int(round((Y1 - Y0) / STEP)) + 1, int(round((X1 - X0) / STEP)) + 1)
    H = np.full(shape, np.inf)
    N = np.full(shape, np.inf)
    per = {}
    for i, name in enumerate(names):
        V, T = z[f"V{i}"], z[f"T{i}"]
        target = N if name.startswith("Left nozzle") else H
        own = np.full(shape, np.inf)
        raster(V, T, own)
        np.minimum(target, own, out=target)
        per[name] = own
    np.savez_compressed(out, H=H, N=N, step=STEP, x0=X0, y0=Y0)
    ys = Y0 + np.arange(shape[0]) * STEP
    xs = X0 + np.arange(shape[1]) * STEP
    tan = np.tan(np.radians(15.0))
    print("lowest bodies against a plane through the tip that rises toward the front (-Y) at 15 degrees:")
    rows = []
    for name, own in per.items():
        if name.startswith("Left nozzle"):
            continue
        clear = own - tan * (-ys)[:, None]
        if np.isfinite(clear).any():
            k = np.unravel_index(np.argmin(clear), clear.shape)
            rows.append((clear[k], name, xs[k[1]], ys[k[0]], own[k]))
    for c, name, x, y, h in sorted(rows)[:12]:
        print(f"  {c:6.2f} mm  {name:42s} at dx {x:6.1f} dy {y:6.1f}  height {h:5.2f}")
    for label, slope in (("back (+Y)", (0, 1)), ("left (-X)", (-1, 0)), ("right (+X)", (1, 0))):
        clear = H - tan * (slope[0] * xs[None, :] + slope[1] * ys[:, None])
        print(f"  rising toward the {label}: least clearance {np.nanmin(np.where(np.isfinite(clear), clear, np.nan)):.2f} mm")
    n = N.copy()
    r = np.hypot(xs[None, :], ys[:, None])
    for rr in (0.5, 1.0, 1.5, 2.0):
        ring = np.isfinite(n) & (np.abs(r - rr) < 0.3)
        print(f"  active nozzle at radius {rr}: lowest {n[ring].min() if ring.any() else float('nan'):.2f} mm")

main()
