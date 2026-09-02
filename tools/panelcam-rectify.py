#!/usr/bin/env python3
"""panelcam-rectify.py — where the panel is in a frame, and the frame laid onto the panel's own grid.

    tools/cad-venv/bin/python tools/panelcam-rectify.py find <test-screen-frame.png>
        corners  <TLx,TLy TRx,TRy BRx,BRy BLx,BLy>     the panel's corners in the frame
        score    <w:h:x:y>                             their bounding box, for the shot's focus score
    tools/cad-venv/bin/python tools/panelcam-rectify.py warp <frame.png> <out.png> \\
        --corners "<TLx,TLy TRx,TRy BRx,BRy BLx,BLy>" --panel 800x480 --scale 3
    tools/cad-venv/bin/python tools/panelcam-rectify.py reduce <out.png> <panel.png> --scale 3
        one pixel per panel pixel: the mean of each scale-by-scale block
    tools/cad-venv/bin/python tools/panelcam-rectify.py check <warped-test-screen.png> --scale 3
        the test screen read back off the warped picture

THE PICTURE IS THE PANEL'S OWN GRID. `warp` maps the quadrilateral the panel occupies in the frame
onto a WxH-scale rectangle in one projective resampling, so a rotated or keystoned panel comes out
square, and output pixel (scale*i + k, scale*j + l) is a piece of panel pixel (i, j). One pass from
the frame the camera delivered: nothing is rotated and then cropped and then scaled.

NOTHING THE PANEL SHOWS IS LOST. The frame holds the panel at 3.3 camera px per panel px across
and 3.1 down, and a panel pixel's finest pattern, alternating pixels, has a period of two panel
px: six camera px, and six output px at scale 3, where the output can hold a period of two. The
camera's own texture between panel pixels — sensor noise and the JPEG's blocks — is what the
resampling smooths, and it is not information about the panel.

THE CORNERS COME FROM THE TEST SCREEN. `src_front` draws it when the main board's console is told
`test`: four 32 px white squares centred at panel (32,32) (768,32) (768,448) (32,448), a 2 px white
frame on the outermost pixels, one-pixel stripes at x 240..303 and 368..431 and a 2 px checkerboard
at 496..559, all at y 268..331, on black. `find` takes the squares as the four blobs of a square's
size inside the frame's box, each centred by its light above the black around it — a centre is a
quantity a blur does not move — and the homography those four fix carries the panel's corners into
the frame.

WHAT `check` READS BACK. The stripes as alternate columns and rows: their modulation is how much of
a one-pixel feature survives. The squares' edges: where each lands against where it should, in
output px. The lattice: the period of the panel's own pixel grid, 3.000 at scale 3 when the scale
is right.

COORDINATES ARE CONTINUOUS. Pixel k spans k to k+1 and is centred at k+0.5; PIL's perspective
transform samples with the same convention.
"""

import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None

SQUARES = {"TL": (32, 32), "TR": (768, 32), "BR": (768, 448), "BL": (32, 448)}   # centres, panel px
SQUARE = 32                                                                       # side, panel px

def luma(path):
    return np.asarray(Image.open(path).convert("L")).astype(np.float32)

def homography(src, dst):
    """The 8 coefficients that take a dst point to its src point, as PIL's PERSPECTIVE wants them."""
    A, b = [], []
    for (u, v), (x, y) in zip(dst, src):
        A.append([u, v, 1, 0, 0, 0, -u * x, -v * x]); b.append(x)
        A.append([0, 0, 0, u, v, 1, -u * y, -v * y]); b.append(y)
    return tuple(np.linalg.solve(np.array(A, float), np.array(b, float)))

def project(coeffs, x, y):
    a, b, c, d, e, f, g, h = coeffs
    w = g * x + h * y + 1
    return ((a * x + b * y + c) / w, (d * x + e * y + f) / w)

def find(path):
    L = luma(path)
    lab, n = ndimage.label(L > 128)
    if n == 0:
        sys.exit("nothing white in the frame: is the test screen up?")
    objs = ndimage.find_objects(lab)
    areas = ndimage.sum(np.ones_like(L), lab, range(1, n + 1))
    # The frame on the outermost pixels: the one component whose box is the panel.
    ring = max(range(n), key=lambda i: (objs[i][0].stop - objs[i][0].start) * (objs[i][1].stop - objs[i][1].start))
    ry0, ry1, rx0, rx1 = objs[ring][0].start, objs[ring][0].stop, objs[ring][1].start, objs[ring][1].stop
    expect = (SQUARE * (rx1 - rx0) / 800.0) ** 2
    found = {}
    for i, sl in enumerate(objs):
        if i == ring or not 0.5 * expect < areas[i] < 1.5 * expect:
            continue
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if not 0.8 < w / h < 1.25 or sl[0].start < ry0 or sl[0].stop > ry1 or sl[1].start < rx0 or sl[1].stop > rx1:
            continue
        # centred by its light above the black around it, over the box grown by 24 px
        y0, y1 = max(0, sl[0].start - 24), min(L.shape[0], sl[0].stop + 24)
        x0, x1 = max(0, sl[1].start - 24), min(L.shape[1], sl[1].stop + 24)
        R = L[y0:y1, x0:x1]
        weight = np.clip(R - np.median(np.concatenate([R[0], R[-1], R[:, 0], R[:, -1]])), 0, None)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        cx, cy = float((weight * (xx + 0.5)).sum() / weight.sum()), float((weight * (yy + 0.5)).sum() / weight.sum())
        name = ("T" if cy < (ry0 + ry1) / 2 else "B") + ("L" if cx < (rx0 + rx1) / 2 else "R")
        if name in found:
            sys.exit(f"two squares in the {name} quarter of the frame")
        found[name] = (cx, cy)
    if len(found) != 4:
        sys.exit(f"{len(found)} of the four squares found: {sorted(found)}")
    names = ["TL", "TR", "BR", "BL"]
    coeffs = homography([found[k] for k in names], [SQUARES[k] for k in names])   # panel -> frame
    corners = [project(coeffs, *p) for p in [(0, 0), (800, 0), (800, 480), (0, 480)]]
    xs, ys = [p[0] for p in corners], [p[1] for p in corners]
    x0, y0 = int(np.floor(min(xs))), int(np.floor(min(ys)))
    print("corners " + " ".join(f"{x:.1f},{y:.1f}" for x, y in corners))
    print(f"score {int(np.ceil(max(xs))) - x0}:{int(np.ceil(max(ys))) - y0}:{x0}:{y0}")
    print("squares " + "  ".join(f"{k} {found[k][0]:.1f},{found[k][1]:.1f}" for k in names))

def warp(path, out, corners, panel, scale):
    W, H = panel[0] * scale, panel[1] * scale
    coeffs = homography(corners, [(0, 0), (W, 0), (W, H), (0, H)])
    im = Image.open(path).convert("RGB")
    im.transform((W, H), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BICUBIC).save(out)

def blocks(arr, scale):
    """The mean of each scale-by-scale block."""
    h, w = arr.shape[0] // scale, arr.shape[1] // scale
    a = arr[: h * scale, : w * scale]
    shape = (h, scale, w, scale) + a.shape[2:]
    return a.reshape(shape).mean(axis=(1, 3))

def reduce(path, out, scale):
    im = np.asarray(Image.open(path).convert("RGB")).astype(np.float64)
    Image.fromarray(blocks(im, scale).round().astype(np.uint8)).save(out)

def period(rows):
    """The panel's pixel lattice as a period along the rows' axis, from the mean spectrum."""
    rows = rows - rows.mean(axis=1, keepdims=True)
    spec = np.abs(np.fft.rfft(rows * np.hanning(rows.shape[1]), axis=1)).mean(axis=0)
    f = np.fft.rfftfreq(rows.shape[1])
    band = (f > 1 / 4.5) & (f < 1 / 2.2)
    k = np.where(band)[0][np.argmax(spec[band])]
    y0, y1, y2 = spec[k - 1], spec[k], spec[k + 1]
    return 1 / ((k + 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)) * (f[1] - f[0]))

def crossings(prof, coords, rising):
    lo, hi = np.percentile(prof, 5), np.percentile(prof, 95)
    mid = (lo + hi) / 2
    k = np.where((prof[:-1] < mid) & (prof[1:] >= mid))[0] if rising else np.where((prof[:-1] >= mid) & (prof[1:] < mid))[0]
    return [coords[i] + 0.5 + (mid - prof[i]) / (prof[i + 1] - prof[i]) for i in k]

def check(path, scale):
    T = luma(path).astype(np.float64)
    s = scale
    inner = T[T.shape[0] // 8 : -T.shape[0] // 8, T.shape[1] // 8 : -T.shape[1] // 8]
    print(f"lattice {period(inner):.3f} x {period(inner.T.copy()):.3f} px per panel px")
    P = blocks(T, s)
    v = P[276:324, 240:304].mean(0); h = P[268:332, 376:424].mean(1)
    ve, vo, he, ho = v[0::2].mean(), v[1::2].mean(), h[0::2].mean(), h[1::2].mean()
    print(f"stripes: one-pixel columns {ve:.0f} / {vo:.0f}, rows {he:.0f} / {ho:.0f}"
          f"  (modulation {abs(ve - vo) / (ve + vo):.2f}, {abs(he - ho) / (he + ho):.2f})")
    off, widths = [], []
    for name, (cx, cy) in SQUARES.items():
        x0, x1, y0, y1 = (cx - SQUARE / 2) * s, (cx + SQUARE / 2) * s, (cy - SQUARE / 2) * s, (cy + SQUARE / 2) * s
        L, R, Tt, B = [], [], [], []
        for y in range(int(y0) + 20, int(y1) - 20, 4):
            c = np.arange(int(x0) - 30, int(x1) + 30); p = T[y, c]
            L += crossings(p, c, True)[:1]; R += crossings(p, c, False)[-1:]
        for x in range(int(x0) + 20, int(x1) - 20, 4):
            c = np.arange(int(y0) - 30, int(y1) + 30); p = T[c, x]
            Tt += crossings(p, c, True)[:1]; B += crossings(p, c, False)[-1:]
        L, R, Tt, B = (np.median(a) for a in (L, R, Tt, B))
        off.append(f"{name} {(L + R) / 2 - (x0 + x1) / 2:+.2f},{(Tt + B) / 2 - (y0 + y1) / 2:+.2f}")
        widths += [R - L, B - Tt]
    print(f"squares: {'  '.join(off)} px off centre; {min(widths):.1f}..{max(widths):.1f} px wide for {SQUARE * s}")

def main(argv):
    args, opts, i = [], {}, 0
    while i < len(argv):
        if argv[i].startswith("--") and i + 1 < len(argv):
            opts[argv[i]] = argv[i + 1]; i += 2
        else:
            args.append(argv[i]); i += 1
    scale = int(opts.get("--scale", "3"))
    if len(args) == 2 and args[0] == "find":
        return find(args[1])
    if len(args) == 2 and args[0] == "check":
        return check(args[1], scale)
    if len(args) == 3 and args[0] == "reduce":
        return reduce(args[1], args[2], scale)
    if len(args) == 3 and args[0] == "warp":
        corners = [tuple(map(float, p.split(","))) for p in opts.get("--corners", "").split()]
        panel = tuple(int(v) for v in opts.get("--panel", "800x480").split("x"))
        if len(corners) != 4:
            sys.exit("--corners wants four x,y pairs: TL TR BR BL")
        return warp(args[1], args[2], corners, panel, scale)
    sys.exit(__doc__)

if __name__ == "__main__":
    main(sys.argv[1:])
