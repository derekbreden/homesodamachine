#!/usr/bin/env python3
"""panelcam-rectify.py — where the panel is in a frame, and the frame laid onto the panel's own grid.

    tools/cad-venv/bin/python tools/panelcam-rectify.py find <frame.png>
        corners  <TLx,TLy TRx,TRy BRx,BRy BLx,BLy>     the lit panel's corners, sub-pixel
        score    <w:h:x:y>                             their bounding box, for the shot's focus score
        tilt     <deg>                                 the panel's rotation in the frame
    tools/cad-venv/bin/python tools/panelcam-rectify.py warp <frame.png> <out.png> \\
        --corners "<TLx,TLy TRx,TRy BRx,BRy BLx,BLy>" --panel 800x480 --scale 3
    tools/cad-venv/bin/python tools/panelcam-rectify.py grid <out.png>
        period   <x> x <y>                             the panel's pixel pitch as it lands in <out.png>

THE PICTURE IS THE PANEL'S OWN GRID. `warp` maps the quadrilateral the panel occupies in the frame
onto a WxH-scale rectangle in one projective resampling, so a rotated or keystoned panel comes out
square, and output pixel (scale*i + k, scale*j + l) is a piece of panel pixel (i, j). One pass from
the frame the camera delivered: nothing is rotated and then cropped and then scaled.

NOTHING THE PANEL SHOWS IS LOST. The frame holds the panel at 3.3 camera px per panel px across
and 3.0 down, and a panel pixel's finest pattern, alternating pixels, has a period of two panel
px: six camera px, and six output px at scale 3, where the output can hold a period of two. The
camera's own texture between panel pixels — sensor noise and the JPEG's blocks — is what the
resampling smooths, and it is not information about the panel.

THE CORNERS ARE THE LIT PANEL'S EDGES. At a 16 ms shutter the panel's darkest navy reads 29 and up
and the bezel 11 to 24, so each edge is the sub-pixel crossing of the level halfway between the
two, one crossing per column or row, fitted to a line with outliers trimmed; the corners are where
adjacent lines meet. `grid` reads the period of the panel's pixel lattice off the warped picture:
3.000 at scale 3 says the corners span exactly 800 by 480 panel px.

COORDINATES ARE CONTINUOUS. Pixel k spans k to k+1 and is centred at k+0.5; a crossing between two
pixel centres lands between them. PIL's perspective transform samples with the same convention.
"""

import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None

def luma(path):
    return np.asarray(Image.open(path).convert("L")).astype(np.float32)

def coarse(L):
    """The lit panel's axis-aligned box and mask, at a quarter scale."""
    d = 4
    small = L[::d, ::d]
    lab, n = ndimage.label(small > 25)
    if n == 0:
        sys.exit("no lit region in the frame")
    sizes = ndimage.sum(np.ones_like(small), lab, range(1, n + 1))
    panel = lab == int(np.argmax(sizes)) + 1
    # A glint on the bezel joins the panel as a blob off one side; the panel's own rows and
    # columns are lit end to end, and a blob's are not.
    rows = panel.sum(1); cols = panel.sum(0)
    ys = np.where(rows > 0.75 * rows.max())[0]; xs = np.where(cols > 0.75 * cols.max())[0]
    box = (xs[0] * d, (xs[-1] + 1) * d, ys[0] * d, (ys[-1] + 1) * d)   # x0, x1, y0, y1
    return panel, d, box

def edge_points(L, panel, d, box, side, span=30, step=4, window=80):
    """Sub-pixel crossings along one side, as (along, across) pairs in continuous coordinates."""
    x0, x1, y0, y1 = box
    horizontal = side in ("top", "bottom")
    lo, hi = (x0, x1) if horizontal else (y0, y1)
    edge = {"top": y0, "bottom": y1, "left": x0, "right": x1}[side]
    inward = 1 if side in ("top", "left") else -1
    margin = int(0.08 * (hi - lo))
    positions = np.arange(lo + margin, hi - margin, step)

    # The edge from the mask, looked for only near the box's side; a glint on the bezel joined to
    # the panel would otherwise be taken for the edge on the rows it touches.
    def mask_edge(p):
        line = panel[:, p // d] if horizontal else panel[p // d, :]
        a, b = max(0, (edge - window) // d), (edge + window) // d + 1
        idx = np.where(line[a:b])[0]
        if len(idx) == 0:
            return None
        return (a + idx[0]) * d if inward == 1 else (a + idx[-1] + 1) * d

    coarse_pts = np.array([(p, c) for p in positions for c in [mask_edge(p)] if c is not None])
    m0, c0, _, _, _ = fit_line(coarse_pts, tol=8)
    predicted = lambda p: m0 * p + c0

    def profile(p, c):
        a, b = max(0, c - span), c + span
        if horizontal:
            return np.arange(a, b), L[a:b, p]
        return np.arange(a, b), L[p, a:b]

    pts, navies, bezels = [], [], []
    for p in positions:
        c = int(round(predicted(p)))
        coords, vals = profile(p, c)
        # the two levels this row's edge runs between, from bands just inside and just outside it
        inside = vals[(coords * inward >= (c + 8 * inward) * inward) & (coords * inward < (c + 24 * inward) * inward)]
        outside = vals[(coords * inward <= (c - 8 * inward) * inward) & (coords * inward > (c - 24 * inward) * inward)]
        if len(inside) == 0 or len(outside) == 0:
            continue
        navy, bezel = np.median(inside), np.median(outside)
        if navy - bezel < 6:       # a glint outside, or content inside: no edge to read on this row
            continue
        mid = (navy + bezel) / 2
        vals = np.convolve(vals, np.ones(3) / 3, mode="same")
        above = vals >= mid
        if inward == 1:
            # scanning inward with increasing coordinate: below at i, above at i+1
            k = np.where(~above[:-1] & above[1:])[0]
            if len(k) == 0:
                continue
            i = k[np.argmin(np.abs(coords[k] + 1 - predicted(p)))]
            t = (mid - vals[i]) / max(1e-3, vals[i + 1] - vals[i])
            pts.append((p + 0.5, coords[i] + 0.5 + t))
        else:
            # scanning inward with decreasing coordinate: above at i, below at i+1
            k = np.where(above[:-1] & ~above[1:])[0]
            if len(k) == 0:
                continue
            i = k[np.argmin(np.abs(coords[k] + 1 - predicted(p)))]
            t = (mid - vals[i + 1]) / max(1e-3, vals[i] - vals[i + 1])
            pts.append((p + 0.5, coords[i + 1] + 0.5 - t))
        navies.append(navy); bezels.append(bezel)
    return np.array(pts), float(np.median(navies)), float(np.median(bezels))

def fit_line(pts, tol=2.0):
    """across = m * along + c: the line most points lie within tol of, then least squares on
    those, with residuals over three spreads trimmed. A glint that bends a third of a side's
    points cannot outvote the rest."""
    a, b = pts[:, 0], pts[:, 1]
    rng = np.random.default_rng(0)
    best, best_n = None, -1
    for _ in range(400):
        i, j = rng.choice(len(a), 2, replace=False)
        if a[i] == a[j]:
            continue
        m = (b[j] - b[i]) / (a[j] - a[i]); c = b[i] - m * a[i]
        n = int((np.abs(b - (m * a + c)) < tol).sum())
        if n > best_n:
            best, best_n = (m, c), n
    m, c = best
    keep = np.abs(b - (m * a + c)) < tol
    for _ in range(8):
        m, c = np.polyfit(a[keep], b[keep], 1)
        r = b - (m * a + c)
        spread = max(0.3, 1.4826 * np.median(np.abs(r[keep])))
        keep = np.abs(r) < 3 * spread
    return m, c, int(keep.sum()), len(a), spread

def meet(top, side):
    """y = mt x + ct  meets  x = ms y + cs."""
    mt, ct = top; ms, cs = side
    y = (mt * cs + ct) / (1 - mt * ms)
    return ms * y + cs, y

def find(path):
    L = luma(path)
    panel, d, box = coarse(L)
    lines, report = {}, []
    for side in ("top", "bottom", "left", "right"):
        pts, navy, bezel = edge_points(L, panel, d, box, side)
        m, c, kept, n, spread = fit_line(pts)
        lines[side] = (m, c)
        report.append(f"{side:6s} {kept}/{n} points within {spread:.2f} px; navy {navy:.0f} bezel {bezel:.0f}")
    TL = meet(lines["top"], lines["left"]); TR = meet(lines["top"], lines["right"])
    BR = meet(lines["bottom"], lines["right"]); BL = meet(lines["bottom"], lines["left"])
    corners = [TL, TR, BR, BL]
    xs = [p[0] for p in corners]; ys = [p[1] for p in corners]
    x0, y0 = int(np.floor(min(xs))), int(np.floor(min(ys)))
    w, h = int(np.ceil(max(xs))) - x0, int(np.ceil(max(ys))) - y0
    tilt_top, tilt_bottom = (np.degrees(np.arctan(lines[k][0])) for k in ("top", "bottom"))
    tilt = (tilt_top + tilt_bottom) / 2
    length = lambda a, b: float(np.hypot(a[0] - b[0], a[1] - b[1]))
    print("corners " + " ".join(f"{x:.1f},{y:.1f}" for x, y in corners))
    print(f"score {w}:{h}:{x0}:{y0}")
    print(f"tilt {tilt:+.2f}")
    print(f"edges top {tilt_top:+.2f} bottom {tilt_bottom:+.2f} left {np.degrees(np.arctan(lines['left'][0])):+.2f} right {np.degrees(np.arctan(lines['right'][0])):+.2f}")
    print(f"sides top {length(TL, TR):.0f} bottom {length(BL, BR):.0f} left {length(TL, BL):.0f} right {length(TR, BR):.0f}")
    for line in report:
        print("  " + line)

def homography(src, dst):
    """The 8 coefficients that take a dst point to its src point, as PIL's PERSPECTIVE wants them."""
    A, b = [], []
    for (u, v), (x, y) in zip(dst, src):
        A.append([u, v, 1, 0, 0, 0, -u * x, -v * x]); b.append(x)
        A.append([0, 0, 0, u, v, 1, -u * y, -v * y]); b.append(y)
    return tuple(np.linalg.solve(np.array(A, float), np.array(b, float)))

def warp(path, out, corners, panel, scale):
    W, H = panel[0] * scale, panel[1] * scale
    coeffs = homography(corners, [(0, 0), (W, 0), (W, H), (0, H)])
    im = Image.open(path).convert("RGB")
    im.transform((W, H), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC).save(out)

def grid(path):
    """The panel's pixel lattice, as a period along each axis of the picture, from the spectrum."""
    L = luma(path)
    L = L[L.shape[0] // 8 : -L.shape[0] // 8, L.shape[1] // 8 : -L.shape[1] // 8]

    def period(rows):
        rows = rows - rows.mean(axis=1, keepdims=True)
        spec = np.abs(np.fft.rfft(rows * np.hanning(rows.shape[1]), axis=1)).mean(axis=0)
        f = np.fft.rfftfreq(rows.shape[1])
        band = (f > 1 / 4.5) & (f < 1 / 2.2)                  # a pitch between 2.2 and 4.5 px
        k = np.where(band)[0][np.argmax(spec[band])]
        # the peak refined between bins
        y0, y1, y2 = spec[k - 1], spec[k], spec[k + 1]
        dk = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
        return 1 / ((k + dk) * (f[1] - f[0]))

    print(f"period {period(L):.3f} x {period(L.T.copy()):.3f}")

def main(argv):
    if len(argv) >= 2 and argv[0] == "find":
        return find(argv[1])
    if len(argv) >= 2 and argv[0] == "grid":
        return grid(argv[1])
    if len(argv) >= 3 and argv[0] == "warp":
        opts = dict(zip(argv[3::2], argv[4::2]))
        corners = [tuple(map(float, p.split(","))) for p in opts["--corners"].split()]
        panel = tuple(int(v) for v in opts.get("--panel", "800x480").split("x"))
        scale = int(opts.get("--scale", "3"))
        if len(corners) != 4:
            sys.exit("--corners wants four x,y pairs: TL TR BR BL")
        return warp(argv[1], argv[2], corners, panel, scale)
    sys.exit(__doc__)

if __name__ == "__main__":
    main(sys.argv[1:])
