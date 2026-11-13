"""TPU: the soft plastic for seals, sleeves, gaskets and the pump elbows. Seven pages built on the
elbow trials of October 2026, the faucet sleeve and the flat gaskets, with the strings page between."""
import functools
import math
import struct
import subprocess

import bookkit as b
import svgkit as k
from bookkit import Page
from chapters import _mine

E = "future/pump-elbow-exploration/prints"
O = "hardware/printed-parts/faucet/tpu-o-ring"
T = "hardware/printed-parts/fixtures/tube-insertion/prints"
SETTINGS = "Metadata/project_settings.config"

# The trials, by the folder that holds each one's record.
FIRST = f"{E}/2026-10-13-compact-single-tpu85a-engineering-z000-mark1"        # 21:09, walls set to 25, the fan test
OUTER10 = f"{E}/2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1"  # 21:45, outer wall set to 10
T215 = f"{E}/2026-10-13-compact-single-tpu85a-t215-engineering-z000-mark1"    # 23:05, ten degrees cooler
FIXED = f"{E}/2026-10-13-compact-single-tpu85a-overhang10-engineering-z000-mark1"  # the corrected file, never sent
AMS = f"{E}/2026-10-13-compact-single-tpuams-mark1"
FULLBASE = f"{E}/2026-10-13-full-base-single-tpu85a-mark1"
SIRAYA = f"{E}/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1"
TWO = f"{E}/2026-10-14-compact-two-siraya85a-overhang10-engineering-z000-mark1"
WEB = f"{E}/2026-10-16-vertical-center-web-tpu85a-mark1"
LINKS = f"{E}/2026-10-16-deposited-links-siraya85a-mark1"
ACCEPTED = f"{E}/2026-10-22-deposited-links-siraya85a-mark2"
SLEEVE = f"{O}/prints/2026-10-23-black-tpu85a-right06-mark2"
ELBOW_STL = "hardware/printed-parts/diaphragm-pump-sleeve/diaphragm-pump-sleeve.stl"
THIMBLE_STL = f"{O}/tpu-o-ring.stl"


def sources():
    """The files this part reads current values from. Trial records are pinned to the commit that wrote them."""
    b.source("tpu-elbow", f"{LINKS}/2026-10-16-elbows-deposited-links-siraya85a-right06-z000-mark1.3mf", member=SETTINGS)
    b.source("tpu-sleeve", f"{SLEEVE}/2026-10-23-touch-flo-sleeve-tpu85a-right06-z000-mark2.3mf", member=SETTINGS)
    b.source("tpu-gasket", "hardware/printed-parts/gaskets.3mf", member=SETTINGS)
    b.source("tpu-petgf", "hardware/printed-parts/petgf.3mf", member=SETTINGS)
    b.source("tpu-accepted", f"{ACCEPTED}/physical-result.json")
    b.source("tpu-sleeve-cap", f"{SLEEVE}/emitted-path-review.json")
    b.source("tpu-drying", f"{FIXED}/filament-drying.json", revision="85cc475e9")
    b.source("tpu-lip-set10", f"{T215}/emitted-commands.json", revision="a5eb3dff1")
    b.source("tpu-lip-compare", f"{OUTER10}/outer-speed-comparison.json", revision="a5eb3dff1")
    b.source("tpu-lip-fixed", f"{SIRAYA}/emitted-command-review.json", revision="b61ea4bef")
    b.source("tpu-underside", f"{FIRST}/underside-side-comparison.json", revision="3d2e975a9")


sources()


# ----------------------------------------------------------------------------- reading meshes
@functools.lru_cache(maxsize=None)
def _tris(path, rev=None):
    """The triangles of a binary STL in the repository, as nine floats each. rev reads it at a Git revision."""
    raw = (subprocess.run(["git", "show", f"{rev}:{path}"], cwd=b.ROOT, capture_output=True, check=True).stdout
           if rev else (b.ROOT / path).read_bytes())
    count = struct.unpack_from("<I", raw, 80)[0]
    return [struct.unpack_from("<9f", raw, 84 + 50 * i + 12) for i in range(count)]


@functools.lru_cache(maxsize=None)
def _cut(path, axis, at, rev=None):
    """Outlines where a mesh meets the plane coordinate[axis] = at: closed loops of (u, v) points in
    the other two axes, in mm. The kit draws models with hsm-render; this reads a print mesh so a
    drawing can show the real section in the book's own colours."""
    u, v = [a for a in range(3) if a != axis]
    segs = []
    for t in _tris(path, rev):
        d = [t[3 * i + axis] - at for i in range(3)]
        d = [x if abs(x) > 1e-7 else 1e-7 for x in d]
        pts = []
        for i in range(3):
            j = (i + 1) % 3
            if (d[i] > 0) != (d[j] > 0):
                s = d[i] / (d[i] - d[j])
                pts.append((t[3 * i + u] + s * (t[3 * j + u] - t[3 * i + u]), t[3 * i + v] + s * (t[3 * j + v] - t[3 * i + v])))
        if len(pts) == 2 and pts[0] != pts[1]:
            segs.append((pts[0], pts[1]))

    def key(p):
        return (round(p[0] * 1e4), round(p[1] * 1e4))

    ends = {}
    for n, (p, q) in enumerate(segs):
        ends.setdefault(key(p), []).append((n, q))
        ends.setdefault(key(q), []).append((n, p))
    used, loops = set(), []
    for n, (p, q) in enumerate(segs):
        if n in used:
            continue
        used.add(n)
        loop, cur = [p, q], q
        while key(cur) != key(loop[0]):
            step = next(((m, r) for m, r in ends.get(key(cur), []) if m not in used), None)
            if step is None:
                break
            used.add(step[0])
            loop.append(step[1])
            cur = step[1]
        if len(loop) > 3:
            loops.append(tuple(loop))
    return tuple(loops)


def _d(loops, f):
    """An SVG path through outlines, mapped by f from mm to pixels, dropping points closer together
    than the eye can see. Fill it with fill-rule evenodd."""
    out = []
    for loop in loops:
        pts = []
        for x, y in map(f, loop):
            if not pts or abs(x - pts[-1][0]) + abs(y - pts[-1][1]) >= 0.8:
                pts.append((x, y))
        out.append("M" + " L".join(f"{k.n(x)} {k.n(y)}" for x, y in pts) + " Z")
    return " ".join(out)


def _shape(loops, f, fill=k.COLD, extra=""):
    return f'<path d="{_d(loops, f)}" fill="{fill}" fill-rule="evenodd" {extra}/>'


def _at(loops, v):
    """Where outlines cross the line v = constant: sorted u values."""
    out = []
    for loop in loops:
        for (u0, v0), (u1, v1) in zip(loop, loop[1:]):
            if (v0 > v) != (v1 > v):
                out.append(u0 + (v - v0) / (v1 - v0) * (u1 - u0))
    return sorted(out)


def _bead(x, y, w, h, fill=k.COLD):
    """One road in section, x and y its top left."""
    return f'<rect x="{k.n(x + 1.5)}" y="{k.n(y + 1.5)}" width="{k.n(w - 3)}" height="{k.n(h - 3)}" rx="{k.n((h - 3) / 2)}" fill="{fill}"/>'


def _wedge(x, y, r, a0, a1, color=k.INK):
    """An angle mark at (x, y) from a0 to a1 degrees, measured anticlockwise from +x."""
    p0 = (x + r * math.cos(math.radians(a0)), y - r * math.sin(math.radians(a0)))
    p1 = (x + r * math.cos(math.radians(a1)), y - r * math.sin(math.radians(a1)))
    sweep = 0 if a1 > a0 else 1
    return (f'<path d="M{k.n(p0[0])} {k.n(p0[1])} A{k.n(r)} {k.n(r)} 0 0 {sweep} {k.n(p1[0])} {k.n(p1[1])}" '
            f'fill="none" stroke="{color}" stroke-width="4"/>')


def _note(text):
    return f'<p class="small" style="margin:0">{text}</p>'


# ----------------------------------------------------------------------------- undersides
def _elbow_section():
    """The production elbow cut down its middle, standing as it prints."""
    loops = _cut(ELBOW_STL, 1, 0.0)
    z28 = b.value("tpu-underside", "/layers/2/z_mm")              # the layer where the curl was noticed
    W, H, BED, S, OX = 1160, 850, 770, 30, 600

    def f(p):
        return OX + p[0] * S, BED - p[1] * S

    xs = _at(loops, z28)
    left, right = f((xs[0], z28)), f((xs[-1], z28))
    g = [k.bed(30, W - 30, BED), _shape(loops, f)]
    g.append(k.line(40, left[1], W - 150, left[1], k.INK, 3, dash="4 12"))
    g.append(k.label(W - 34, left[1] - 16, "LAYER 28", 25, anchor="end", fill=k.INK, weight=600))
    g.append(k.label(W - 34, left[1] + 36, f"{z28:.1f} MM UP", 25, anchor="end"))
    # the two outside undersides at that layer
    g.append(_wedge(left[0], left[1], 120, 180, 135, k.HOT) + k.label(left[0] - 132, left[1] - 44, "45°", 54, anchor="end", fill=k.HOT, weight=600, mono=False))
    g.append(_wedge(right[0], right[1], 120, 0, 66, k.INK) + k.label(right[0] + 124, right[1] - 62, "66°", 54, fill=k.INK, weight=600, mono=False))
    g.append(k.label(40, left[1] + 46, "CURLED FIRST", 25, fill=k.HOT, weight=600))
    # names
    g.append(k.label(f((-10.4, 12.2))[0], f((-10.4, 12.2))[1], "BARB", 25, anchor="middle", fill=k.MUTED))
    g.append(k.label(f((-10.4, 12.2))[0], f((-10.4, 12.2))[1] + 34, "SOCKET", 25, anchor="middle", fill=k.MUTED))
    g.append(k.label(f((9.6, 15.4))[0], f((9.6, 15.4))[1], "TUBE", 25, anchor="middle", fill=k.MUTED))
    g.append(k.label(f((9.6, 15.4))[0], f((9.6, 15.4))[1] + 34, "SOCKET", 25, anchor="middle", fill=k.MUTED))
    roof = f((-4.9, 16.6))
    g.append(k.line(roof[0] - 4, roof[1] + 4, 250, 150) + f'<circle cx="{k.n(roof[0] - 4)}" cy="{k.n(roof[1] + 4)}" r="7" fill="{k.INK}"/>')
    g.append(k.label(40, 110, "A BORE&#8217;S ROOF", 25, fill=k.INK) + k.label(40, 144, "ALSO LEANS AT 45°", 25, fill=k.INK))
    foot = f((-0.4, 0))
    g.append(k.label(foot[0], BED + 62, "THE FLAT FOOT IT STANDS ON", 25, anchor="middle", fill=k.INK))
    g.append(k.arrow(W - 60, 520, W - 60, 110) + f'<text transform="translate({W - 34} 470) rotate(-90)" font-family="IBM Plex Mono, monospace" '
             f'font-size="25" letter-spacing="2" fill="{k.MUTED}">BUILD DIRECTION</text>')
    return k.svg(W, H, "".join(g), "The pump elbow cut down its middle, standing as it prints",
                 "A V on a small flat foot with both mouths up. A dotted line marks layer 28, where the curl was first noticed. At that height "
                 "the outside of the large barb socket, on the left, leans at 45 degrees from the bed. The outside of the tube socket, on the "
                 "right, is still in its neck and leans at about 66 degrees. The roofs of both bores lean at 45 degrees.")


def _lips():
    """The two outside edges at layer 28, drawn with beads at their true proportions."""
    wide, tall = float(b.value("tpu-elbow", "/line_width")), float(b.value("tpu-elbow", "/layer_height"))
    S = 24 / tall                                     # one course is 24 px
    bw, bh, base = wide * S, 24, 300
    W, H = 1160, 400
    g = []

    def stack(x0, sign, step, top):
        out = []
        for r in range(9):
            y = base - (r + 1) * bh
            x = x0 + sign * r * step
            fill = top if r == 8 else k.COLD
            for i in range(2):
                out.append(_bead(x + (i if sign < 0 else -(i + 1)) * bw, y, bw, bh, fill))
        return "".join(out)

    g.append(stack(280, -1, bh, k.HOT))                              # 45 degrees: out one layer height per layer
    g.append(stack(880, 1, bh / math.tan(math.radians(66)), k.HOT))  # 66 degrees
    g.append(k.label(20, 40, "LEFT · 45°", 27, fill=k.HOT, weight=600) + k.label(W - 20, 40, "RIGHT · 66°", 27, anchor="end", fill=k.INK, weight=600))
    g.append(k.label(20, base + 40, "STEPS OUT A WHOLE LAYER HEIGHT", 23) + k.label(W - 20, base + 40, "STEPS OUT LESS THAN HALF OF ONE", 23, anchor="end"))
    g.append(k.label(20, base + 80, "82% OF EACH BEAD LANDS ON THE ONE BELOW", 23, fill=k.HOT, weight=600) + k.label(W - 20, base + 80, "92% LANDS", 23, anchor="end", fill=k.INK, weight=600))
    return k.svg(W, H, "".join(g), "Nine courses of the outside wall on each side of the elbow, at true proportions",
                 "Each bead is about five times as wide as it is tall. On the left the wall leans at 45 degrees and each bead steps out by one "
                 "layer height, so about four fifths of it lands on the bead below. On the right, at 66 degrees, each bead steps out by less "
                 "than half as much and more than nine tenths of it lands.")


def _full_base():
    """The rejected elbow of 13 October: stock added round it, with a channel left under each cuff."""
    loops = _cut(f"{FULLBASE}/full-base-single-elbow-print.stl", 1, 0.0, rev="8f3dd0dab")
    W, H, BED, S, OX = 700, 590, 520, 19, 350

    def f(p):
        return OX + p[0] * S, BED - p[1] * S

    def near(p):
        return min((q for loop in loops for q in loop), key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)

    g = [k.bed(10, W - 10, BED), _shape(loops, f)]
    for slot in ([(-16.83, 11.15), (-16.83, 9.45), (-11.3, 3.89), (-10.47, 4.72)], [(16.83, 13.95), (16.83, 12.29), (11.33, 6.75), (10.47, 7.59)]):
        pts = " ".join(f"{k.n(x)},{k.n(y)}" for x, y in (f(near(p)) for p in slot))
        g.append(f'<polygon points="{pts}" fill="white" stroke="{k.BAD}" stroke-width="4" stroke-dasharray="9 7"/>')
    a, c = f((-14.2, 7.2)), f((14.2, 10.4))
    g.append(k.line(a[0], a[1], 70, 60, k.BAD) + k.line(c[0], c[1], W - 70, 60, k.BAD))
    g.append(k.label(20, 44, "A GAP UNDER THE CUFF", 29, fill=k.BAD, weight=600) + k.label(W - 20, 44, "AND ANOTHER", 29, anchor="end", fill=k.BAD, weight=600))
    return k.svg(W, H, "".join(g), "The rejected elbow with stock added round it, cut down its middle",
                 "The same V with blocks of extra plastic under and above its legs. A narrow channel separates each block from the cuff it sits "
                 "under, so the cuff still hangs over air.")


# ----------------------------------------------------------------------------- the curling lip
def _curl_strip():
    """What Derek watched on 13 October, as three moments at the edge of a wall that leans out."""
    W, H, BW, BH = 2170, 440, 104, 20

    def frame(ox, step):
        top = 9 if step == 1 else 10

        def x(r):
            return ox + 380 - r * BH

        def y(r):
            return 400 - (r + 1) * BH

        g = []
        for r in range(top + 1):
            for i in range(3):
                lifted = step == 1 and r >= 7 and i == 0
                torn = step == 3 and r >= 8 and i == 0
                fill = k.HOT if (step == 2 and r == top) else k.COLD
                if not lifted and not torn:
                    g.append(_bead(x(r) + i * BW, y(r), BW, BH, fill))
        if step == 1:
            for n, r in enumerate((7, 8, 9)):
                sx, sy = x(r) + BW, y(r) + BH / 2
                g.append(k.road(f"M{k.n(sx)} {k.n(sy)} Q{k.n(sx - 70)} {k.n(sy)} {k.n(sx - 118 - 10 * n)} {k.n(sy - 46 - 44 * n)}", k.COLD, 17))
            tip = (x(9) + BW - 138, y(9) + BH / 2 - 134)
            g.append(k.dim(tip[0] - 46, tip[1], tip[0] - 46, y(9) + BH, "", 0))
            g.append(k.label(tip[0] - 70, tip[1] + 60, "ABOUT", 25, anchor="end") + k.label(tip[0] - 70, tip[1] + 94, "1 MM", 25, anchor="end", fill=k.INK, weight=600))
        elif step == 2:
            sx, sy = x(top) + BW, y(top) + BH / 2
            g.append(f'<path d="M{k.n(sx)} {k.n(sy)} Q{k.n(sx - 70)} {k.n(sy)} {k.n(sx - 138)} {k.n(sy - 134)}" fill="none" stroke="{k.FAINT}" stroke-width="17" '
                     f'stroke-linecap="round" stroke-dasharray="2 26"/>')
            g.append(k.nozzle(x(top) + 74, y(top)))
            g.append(k.arrow(x(top) - 78, y(top) - 4, x(top) - 96, y(top) - 104, k.INK, 4))
        else:
            g.append(k.missing(x(10) - 6, y(10) - 4, x(8) + BW, y(8) + BH + 2))
            nx = x(top) + 3 * BW + 110
            g.append(f'<circle cx="{k.n(nx - 6)}" cy="{k.n(y(top) - 2)}" r="26" fill="{k.COLD}"/>' + k.nozzle(nx, y(top) - 26))
            g.append(k.arrow(x(top) + 2 * BW, y(top) - 60, nx - 80, y(top) - 60, k.INK, 4))
        return "".join(g)

    body = frame(40, 1) + frame(740, 2) + frame(1440, 3)
    return k.svg(W, H, body, "A leaning lip curls, is pressed down, springs back and is torn",
                 "Three sections through the top of a wall that leans out to the left. First: the outer bead of the newest courses has "
                 "lifted about a millimetre. Second: the nozzle passes and presses it flat, and it springs back up behind. Third: the "
                 "nozzle has caught the raised edge and carried a lump of it away, leaving a gap in the lip.")


# ----------------------------------------------------------------------------- set speed and emitted speed
def _lip_speeds():
    """(layer, mm/s) at the left lip in the files whose outer wall was set to 10, in the file before
    them, and in the corrected file. Read from the trial records."""
    set10, before, fixed = [], [], []
    for i in range(17):
        try:
            v = b.value("tpu-lip-set10", f"/curl_region_outer_speeds_mm_s/{i}/speeds/1")
        except IndexError:
            v = b.value("tpu-lip-set10", f"/curl_region_outer_speeds_mm_s/{i}/speeds/0")
        set10.append((b.value("tpu-lip-set10", f"/curl_region_outer_speeds_mm_s/{i}/layer"), v))
        fixed.append((b.value("tpu-lip-fixed", f"/onset_region/{i}/layer"), b.value("tpu-lip-fixed", f"/onset_region/{i}/arriving_mm_s")))
    for i in range(8):
        before.append((b.value("tpu-lip-compare", f"/baseline/{i}/layer"), b.value("tpu-lip-compare", f"/baseline/{i}/left_lip_speeds_mm_s/0")))
    return set10, before, fixed


def _speed_chart():
    set10, before, fixed = _lip_speeds()
    W, H, X0, X1, Y0, Y1 = 1300, 760, 150, 1240, 630, 90

    def px(layer):
        return X0 + (layer - 17) / 16 * (X1 - X0)

    def py(v):
        return Y0 - v / 25 * (Y0 - Y1)

    g = []
    for v in range(0, 26, 5):
        g.append(k.line(X0, py(v), X1, py(v), k.FAINT if v else k.INK, 1.5 if v else 4))
        g.append(k.label(X0 - 22, py(v) + 9, str(v), 27, anchor="end"))
    g.append(k.label(X0 - 22, py(25) - 34, "MM/S", 25, anchor="end", fill=k.INK, weight=600))
    for layer in range(17, 34, 4):
        g.append(k.line(px(layer), Y0, px(layer), Y0 + 14) + k.label(px(layer), Y0 + 50, str(layer), 27, anchor="middle"))
    g.append(k.label((X0 + X1) / 2, Y0 + 100, "LAYER, FROM 2.1 MM TO 4.0 MM ABOVE THE BED", 25, anchor="middle", fill=k.INK))

    def line(points, color, width, dash=""):
        d = "M" + " L".join(f"{k.n(px(a))} {k.n(py(v))}" for a, v in points)
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{ds}/>'

    g.append(line(before, k.COLD, 7, "2 16"))
    g.append(line(fixed, k.COLD, 12))
    g.append(k.line(X0, py(10), X1, py(10), k.INK, 4, dash="16 12"))
    g.append(line(set10, k.HOT, 12))
    for a, v in set10:
        g.append(f'<circle cx="{k.n(px(a))}" cy="{k.n(py(v))}" r="9" fill="white" stroke="{k.HOT}" stroke-width="5"/>')
    g.append(k.label(px(17) + 10, py(10) + 52, "THE SETTING, AND THE CORRECTED FILE: 10", 25, fill=k.INK, weight=600))
    g.append(k.label(px(17) + 10, py(22.6), "WHAT THE LIP RAN AT", 25, fill=k.HOT, weight=600))
    g.append(k.label(px(17) + 10, py(22.6) + 34, "WITH THE OUTER WALL SET TO 10", 25, fill=k.HOT))
    g.append(k.label(px(33), py(13.5), "THE PRINT BEFORE,", 25, anchor="end", fill=k.COLD, weight=600))
    g.append(k.label(px(33), py(13.5) + 34, "WALLS SET TO 25", 25, anchor="end", fill=k.COLD))
    l21, l27 = dict(set10)[21], dict(set10)[27]
    g.append(k.callout(1, px(21), py(l21) - 14, px(21), py(l21) - 84))
    g.append(k.callout(2, px(27), py(l27) - 14, px(27), py(l27) - 84))
    return k.svg(W, H, "".join(g), "The speed commanded at the curling lip, layer by layer, against the speed that was set",
                 "A chart from layer 17 to layer 33. A dashed line at 10 millimetres a second is the outer wall setting. The orange line is "
                 "what the file commanded at the lip: 13.4 at layer 17, climbing to 21.8 at layer 32. A dotted line shows the print before, "
                 "with walls set to 25: between 14.6 and 17.6 on layers 26 to 33. The corrected file runs along the 10 line on every layer.")


# ----------------------------------------------------------------------------- islands
PAIR_Z = 10.0      # mm above the bed: each elbow is still one piece here
FORK_Z = 18.0      # above the fork: each elbow is two legs
PITCH = 23.0       # mm between the two elbows on the plate, as printed on 14, 16 and 22 October


def _pair(z):
    """The two plain elbows of the pair at one height, as outlines in plate millimetres."""
    one = _cut(f"{FIRST}/compact-single-elbow-print.stl", 2, z, rev="a86ede62e")
    return one + tuple(tuple((x, y + PITCH) for x, y in loop) for loop in one)


def _fins(z):
    return _cut(f"{WEB}/cutaway-web.stl", 2, z, rev="ff629ceda")


def _span(loops, x):
    """The y values where outlines cross the line x = constant."""
    return _at(tuple(tuple((y, x_) for x_, y in loop) for loop in loops), x)


def _islands(joined):
    W, H, S, OX, OY = 1000, 760, 19, 372, 380

    def f(p):
        return OX + p[0] * S, OY - (p[1] - PITCH / 2) * S

    one = _cut(f"{FIRST}/compact-single-elbow-print.stl", 2, PAIR_Z, rev="a86ede62e")
    g = [f'<rect x="14" y="14" width="{W - 28}" height="{H - 28}" rx="24" fill="{k.WASH}"/>']
    if joined:
        g.append(_shape(_fins(PAIR_Z), f, k.SCAFFOLD))
    g.append(_shape(_pair(PAIR_Z), f))
    for cx, cy in ((-7.0, 0), (4.6, 0), (-7.0, PITCH), (4.6, PITCH)):
        g.append(k.label(f((cx, cy))[0], f((cx, cy))[1] + 9, "BORE", 22, anchor="middle", fill=k.FAINT))
    LX = 716
    if joined:
        web = _fins(PAIR_Z)
        ys = [y for loop in web for _, y in loop]
        xs = [x for loop in web for x, _ in loop]
        mid = (min(xs) + max(xs)) / 2
        a, c = f((mid, min(ys) - 1.2)), f((mid, max(ys) + 1.2))
        my = a[1] + (c[1] - a[1]) * 0.42
        g.append(k.line(a[0], a[1], a[0], my, k.HOT, 13) + k.nozzle_top(a[0], my, 30))
        g.append(k.label(LX, 274, "THE WEB,", 25, fill=k.SCAFFOLD, weight=600) + k.label(LX, 308, "TWO BEADS THICK,", 25, fill=k.SCAFFOLD) + k.label(LX, 342, "CUT OFF LATER", 25, fill=k.SCAFFOLD))
        g.append(k.line(LX - 12, 300, a[0] + 20, c[1] + 44, k.SCAFFOLD))
        g.append(k.label(LX, 476, "THE NOZZLE", 25, fill=k.HOT, weight=600) + k.label(LX, 510, "PRINTS ITS WAY", 25, fill=k.HOT, weight=600)
                 + k.label(LX, 544, "ACROSS", 25, fill=k.HOT, weight=600))
        g.append(k.line(LX - 12, 484, a[0] + 36, my + 8, k.HOT))
        title = "Seen from above: the same two elbows joined by a web, printed as one island"
        desc = ("The two outlines are now joined across the gap by a thin strip, hatched blue because it is cut away afterwards. "
                "The nozzle crosses from one elbow to the other along that strip while it is printing.")
    else:
        stop = (6.4, _span(tuple(tuple((x, y + PITCH) for x, y in loop) for loop in one), 6.4)[0] + 1.0)
        start = (-7.4, _span(one, -7.4)[-1] - 1.0)
        a, c = f(stop), f(start)
        g.append(k.line(a[0], a[1], c[0], c[1], k.HOT, 7))
        g.append(k.road(f"M{k.n(c[0])} {k.n(c[1])} c -40 -44, -104 -34, -98 14 s 62 44, 88 4", k.HOT, 10))
        g.append(f'<circle cx="{k.n(a[0])}" cy="{k.n(a[1])}" r="15" fill="white" stroke="{k.INK}" stroke-width="6"/>' + k.nozzle_top(c[0], c[1], 30))
        LX = 742
        g.append(k.label(LX, 262, "STOPS PRINTING", 25, fill=k.INK) + k.label(LX, 296, "ON ONE ELBOW", 25, fill=k.INK) + k.line(LX - 12, 266, a[0] + 20, a[1] - 4))
        g.append(k.label(LX, 388, "HOPS THE GAP,", 25, fill=k.HOT, weight=600) + k.label(LX, 422, "STILL OOZING", 25, fill=k.HOT, weight=600))
        g.append(k.line(LX - 12, 396, (a[0] + c[0]) / 2 + 16, (a[1] + c[1]) / 2, k.HOT))
        g.append(k.label(LX, 556, "STARTS A WALL", 25, fill=k.INK) + k.label(LX, 590, "ON THE OTHER,", 25, fill=k.INK) + k.label(LX, 624, "WITH A LOOP", 25, fill=k.HOT, weight=600))
        g.append(k.line(LX - 12, 560, c[0] + 36, c[1] + 10))
        title = "Seen from above: two elbows on the bed as two islands, with a hop between them"
        desc = ("Two figure-of-eight outlines, each with two bores, side by side with a gap between them. The nozzle stops printing on "
                "one, crosses the gap leaving a thread, and starts a wall on the other, where a loop of extra plastic sticks out.")
    return k.svg(W, H, "".join(g), title, desc)


def _fork():
    """Higher up, each elbow is two legs: three fins make the four pieces one island."""
    W, H, S, OX, OY = 480, 700, 14, 240, 350

    def f(p):
        return OX + p[0] * S, OY - (p[1] - PITCH / 2) * S

    g = [f'<rect x="10" y="10" width="{W - 20}" height="{H - 20}" rx="20" fill="{k.WASH}"/>']
    g.append(_shape(_fins(FORK_Z), f, k.SCAFFOLD) + _shape(_pair(FORK_Z), f))
    g.append(k.label(OX, 60, "ONE ELBOW: TWO LEGS", 29, anchor="middle", fill=k.INK))
    g.append(k.label(OX, H - 36, "THE OTHER ELBOW", 29, anchor="middle", fill=k.INK))
    g.append(k.label(f((0, 0))[0] + 26, f((0, PITCH / 2))[1] + 9, "WEB", 29, fill=k.SCAFFOLD, weight=600))
    g.append(k.label(f((0, PITCH))[0], f((0, PITCH))[1] - 36, "FIN", 29, anchor="middle", fill=k.SCAFFOLD, weight=600))
    g.append(k.label(f((0, 0))[0], f((0, 0))[1] + 54, "FIN", 29, anchor="middle", fill=k.SCAFFOLD, weight=600))
    return k.svg(W, H, "".join(g), "Seen from above, higher up: four separate legs joined by two fins and the web",
                 "Above the point where each elbow forks, a layer is four crescent-shaped legs. A fin joins the two legs of each elbow and "
                 "the web runs straight between the two fins, so the layer is still one island.")


# ----------------------------------------------------------------------------- first layers
def _no_first_layer():
    """22 May 2026: the open sleeve's wall is thinner than one first-layer line."""
    W, H, S, BED, CX = 760, 470, 400, 400, 200
    wall, line_w = 0.375, 0.5
    g = [k.bed(20, W - 20, BED)]
    g.append(f'<rect x="{k.n(CX - wall * S / 2)}" y="70" width="{k.n(wall * S)}" height="{BED - 70}" fill="{k.WASH}" stroke="{k.COLD}" stroke-width="4"/>')
    g.append(f'<rect x="{k.n(CX - line_w * S / 2)}" y="{BED - 74}" width="{k.n(line_w * S)}" height="70" rx="35" fill="none" stroke="{k.BAD}" stroke-width="5" stroke-dasharray="11 9"/>')
    g.append(k.dim(CX - wall * S / 2, 50, CX + wall * S / 2, 50, "", 0, k.COLD) + k.label(CX + wall * S / 2 + 30, 59, "THE WALL · 0.375 MM", 24, fill=k.COLD, weight=600))
    g.append(k.label(CX + line_w * S / 2 + 26, BED - 46, "ONE FIRST-LAYER", 24, fill=k.BAD, weight=600) + k.label(CX + line_w * S / 2 + 26, BED - 14, "LINE · ABOUT 0.5 MM", 24, fill=k.BAD, weight=600))
    return k.svg(W, H, "".join(g), "A wall thinner than one first-layer line",
                 "A section through one wall of the first sleeve where it meets the bed. The wall is 0.375 millimetres thick. The line a "
                 "first layer is drawn with is about half a millimetre wide, so it does not fit inside the wall and the slicer lays nothing.")


def _sleeve_section():
    """The faucet sleeve cut down its middle, cap down, as the saved spiral recipe prints it."""
    loops = _cut(THIMBLE_STL, 1, 0.0)
    zs = sorted({round(z, 3) for loop in loops for _, z in loop})
    cap_cad, top = zs[1], zs[-1]
    r_out = max(x for loop in loops for x, _ in loop)
    r_hole = _at(loops, cap_cad / 2)[2]
    r_bore = _at(loops, (cap_cad + top) / 2)[2]
    first, layer, wide = (float(b.value("tpu-sleeve", ptr)) for ptr in ("/initial_layer_print_height", "/layer_height", "/line_width"))
    cap = b.value("tpu-sleeve-cap", "/native_solid_cap_height_mm")
    W, H, S, BED, CX = 900, 890, 46, 810, 300

    def X(x):
        return CX + x * S

    def Y(z):
        return BED - z * S

    g = [k.bed(30, 610, BED)]
    z, heights = 0.0, []
    while z < top - 1e-6:
        h = first if not heights else layer
        heights.append((z, h))
        z += h
    for z0, h in heights:
        solid = z0 + h <= cap + 1e-6
        for side in (-1, 1):
            if solid:
                n = max(1, round((r_out - r_hole) / wide))
                bw = (r_out - r_hole) * S / n
                x0 = X(r_hole) if side > 0 else X(-r_out)
                g.append("".join(_bead(x0 + i * bw, Y(z0 + h), bw, h * S) for i in range(n)))
            else:
                x0 = X(r_out - wide) if side > 0 else X(-r_out)
                g.append(_bead(x0, Y(z0 + h), wide * S, h * S, k.HOT if z0 + h > top - 1e-6 else k.COLD))
    for side in (-1, 1):
        x0, x1 = (X(r_hole), X(r_bore)) if side > 0 else (X(-r_bore), X(-r_hole))
        g.append(k.missing(x0 + 2, Y(cap_cad), x1 - 2, Y(cap) - 3))
    LX = 640
    g.append(k.label(LX, Y(top * 0.62), "ONE BEAD THICK,", 25, fill=k.INK, weight=600) + k.label(LX, Y(top * 0.62) + 34, "ONE UNBROKEN", 25, fill=k.INK, weight=600)
             + k.label(LX, Y(top * 0.62) + 68, "SPIRAL", 25, fill=k.INK, weight=600) + k.line(LX - 12, Y(top * 0.62) + 26, X(r_out) + 10, Y(top * 0.62) + 26))
    g.append(k.label(LX, Y(cap_cad) - 86, "IN THE MODEL,", 25, fill=k.BAD, weight=600) + k.label(LX, Y(cap_cad) - 52, "NOT PRINTED", 25, fill=k.BAD, weight=600)
             + k.line(LX - 12, Y(cap_cad) - 60, X(r_bore) - 14, Y((cap + cap_cad) / 2)))
    g.append(k.label(LX, Y(cap / 2) + 2, "THE CAP: THREE", 25, fill=k.INK, weight=600) + k.label(LX, Y(cap / 2) + 36, "SOLID LAYERS", 25, fill=k.INK, weight=600)
             + k.line(LX - 12, Y(cap / 2) - 6, X(r_out) + 10, Y(cap / 2) - 6))
    g.append(k.label(CX, BED + 62, "CAP DOWN ON THE BED", 25, anchor="middle"))
    g.append(k.label(CX, Y(top) - 26, "THE TUBE GOES IN HERE", 25, anchor="middle"))
    return k.svg(W, H, "".join(g), "The faucet sleeve cut down its middle, as it prints",
                 "A cup standing on the bed. Its floor is three solid layers with a hole in the middle. Its wall is a single bead, layer on "
                 "layer, to the top. A dashed red outline above the floor marks the rest of the cap as it is drawn in the model, which "
                 "this recipe does not print.")


def _gasket_section():
    """A flat gasket in section at true proportions: every layer solid from edge to edge."""
    first, layer, wide = (float(b.value("tpu-gasket", ptr)) for ptr in ("/initial_layer_print_height", "/layer_height", "/line_width"))
    walls = int(b.value("tpu-gasket", "/wall_loops"))
    W, H, S, BED, X0, n = 940, 360, 100, 300, 40, 10
    g = [k.bed(20, W - 20, BED)]
    y = BED
    for row in range(10):
        h = (first if row == 0 else layer) * S
        y -= h
        for i in range(n):
            g.append(_bead(X0 + i * wide * S, y, wide * S, h))
    g.append(k.line(X0, y - 26, X0 + walls * wide * S, y - 26, k.INK, 4) + k.label(X0, y - 44, "TWO WALLS", 24, fill=k.INK, weight=600))
    g.append(k.label(X0 + n * wide * S / 2, y - 44, "SOLID BETWEEN", 24, anchor="middle"))
    g.append(k.line(X0 + (n - walls) * wide * S, y - 26, X0 + n * wide * S, y - 26, k.INK, 4))
    g.append(k.dim(X0 + n * wide * S + 34, y, X0 + n * wide * S + 34, BED, "TEN LAYERS", -124))
    return k.svg(W, H, "".join(g), "A flat gasket in section",
                 "Ten layers of beads on the bed. The two beads at each edge are walls. Everything between them is filled, on every layer.")


# ============================================================================= pages
def _rec(*links):
    return '<div style="margin-top:30px">' + b.record(*links) + "</div>"


def _marks(w, h, marks):
    """Numbered discs over a photograph, each with a white leader to what it points at."""
    g = []
    for num, (x, y), (tx, ty), kind in marks:
        fill = {"hot": k.HOT}.get(kind, k.INK)
        g.append(f'<path d="M{tx} {ty} L{x} {y}" stroke="white" stroke-width="5" fill="none"/><circle cx="{x}" cy="{y}" r="9" fill="white"/>'
                 f'<circle cx="{tx}" cy="{ty}" r="36" fill="white"/><circle cx="{tx}" cy="{ty}" r="31" fill="{fill}"/>'
                 f'<text x="{tx}" y="{ty + 11}" text-anchor="middle" class="d-num">{num}</text>')
    return f'<svg viewBox="0 0 {w} {h}" aria-hidden="true" style="position:absolute; left:0; top:0; width:{w}px; height:{h}px">{"".join(g)}</svg>'


def _numbered(items, hot=()):
    return "".join(f'<div style="display:flex; gap:22px; align-items:flex-start; margin-bottom:20px"><span class="num{" hot" if i + 1 in hot else ""}">{i + 1}</span>'
                   f'<p class="small" style="margin:0">{t}</p></div>' for i, t in enumerate(items))


# ----------------------------------------------------------------------------- 1 the plastic
def plastic():
    el, sl, ga, pg = "tpu-elbow", "tpu-sleeve", "tpu-gasket", "tpu-petgf"
    S = b.setting
    photo = b.asset("tpu-elbow-on-the-pump.jpg", "hardware/reference/g-ganen-pump/under-head-tube/IMG_8159.jpeg", max_px=2400)

    def rung(grade, tag, cls, who, text):
        return (f'<div style="display:flex; gap:28px; align-items:flex-start; padding:13px 0 11px; border-top:2px solid var(--line)">'
                f'<p style="flex:0 0 176px; margin:0; font:700 72px/1 \'IBM Plex Sans\', sans-serif; letter-spacing:-.02em; color:var(--ink)">{grade}</p>'
                f'<div style="flex:1; min-width:0"><p class="tiny" style="margin:0 0 5px"><span class="tag {cls}" style="margin-right:14px">{tag}</span>{who}</p>'
                f'<p class="small" style="margin:0; font-size:35px">{text}</p></div></div>')

    ladder = (
        '<p class="mono" style="margin:0 0 12px; font-size:25px; letter-spacing:.08em; color:var(--muted)">STIFFER, AND QUICKER TO PRINT ↑ &nbsp;·&nbsp; SOFTER ↓</p>'
        + rung("68D", "Too stiff", "bad", "Bambu TPU for AMS · the pump elbow · 13 October 2026",
               "&ldquo;That was too stiff.&rdquo; Its maker lets 12 mm³ a second through the nozzle, and the slicer gave the elbow 43.5 minutes. In 85A the same elbow was given 62.")
        + rung("95A", "Locked up", "bad", "Bambu TPU 95A · the faucet sleeve · 24 May 2026",
               "It went over the tube alone and into the faucet&rsquo;s port alone, &ldquo;barely any force required&rdquo;. &ldquo;But attempting both at the same time? Nah, not happening.&rdquo;")
        + rung("90A", "Never stretched", "open", "Bambu TPU 90A · flat gaskets · October 2026",
               "Printed only as flat gaskets, which are squeezed and never stretched. How those fitted was not written down.")
        + rung("85A", "Fits", "good", "Bambu and Siraya TPU 85A · sleeve, elbow · May, October 2026",
               "The sleeve seated in the port with the tube in it &ldquo;for the first time&rdquo;. The elbow went onto the pump by hand: &ldquo;nice firm friction stretchy fit&rdquo;.")
        + '<div style="border-top:2px solid var(--line); padding-top:20px">'
        + b.quote("85A is the only one that flexes enough here.", "DEREK · 19 OCTOBER 2026", size=45) + "</div>")

    rows = [
        ("Nozzle, first layer / rest", f'{S(el, "/nozzle_temperature_initial_layer/0")} / {S(el, "/nozzle_temperature/0")} °C',
         f'{S(sl, "/nozzle_temperature_initial_layer/0")} / {S(sl, "/nozzle_temperature/0")} °C'),
        ("Layers, first / rest", f'{S(el, "/initial_layer_print_height")} / {S(el, "/layer_height")} mm', f'{S(sl, "/initial_layer_print_height")} / {S(sl, "/layer_height")} mm'),
        ("Bead width", f'{S(el, "/line_width")} mm', f'{S(sl, "/line_width")} mm'),
        ("Walls", f'{S(el, "/wall_loops")}, and filled solid', f'{S(sl, "/wall_loops")}, as a spiral'),
        ("Flow ratio", S(el, "/filament_flow_ratio/0"), S(sl, "/filament_flow_ratio/0")),
        ("Flow limit", f'{S(el, "/filament_max_volumetric_speed/0")} mm³/s', f'{S(sl, "/filament_max_volumetric_speed/0")} mm³/s'),
        ("Part fan, after layer one", f'{S(el, "/fan_min_speed/0")}%', f'{S(sl, "/fan_min_speed/0")}%'),
        ("Auxiliary fan", f'{S(el, "/additional_cooling_fan_speed/0")}%', f'{S(sl, "/additional_cooling_fan_speed/0")}%'),
    ]
    recipe = ('<table class="grid" style="font-size:32px"><thead><tr><th style="width:42%"></th><th>Pump elbow<br>Siraya 85A</th><th>Faucet sleeve<br>Bambu 85A</th></tr></thead><tbody>'
              + "".join(f'<tr><td style="padding:10px 22px 10px 0; color:var(--muted)">{a}</td><th style="padding:10px 22px 10px 0">{x}</th><th style="padding:10px 0">{y}</th></tr>' for a, x, y in rows)
              + "</tbody></table>"
              + f'<p class="tiny" style="margin:14px 0 0">Flat gaskets take the sleeve&rsquo;s plastic settings with {S(ga, "/wall_loops")} walls and {S(ga, "/sparse_infill_density")} fill. No supports in any of them.</p>')
    body = (
        b.head("The plastic", "Choose hardness by the fit.",
               "TPU is the rubbery one: the pump&rsquo;s elbows, the faucet&rsquo;s sealing sleeve, the gaskets. The first two must stretch over "
               "something rigid, and only the softest grade we own would.",
               size=160, lede_size=50, top=56)
        + b.scope("Bambu TPU 85A, 90A, 95A and TPU for AMS · Siraya TPU 85A · Mark 1 and Mark2 · right 0.6 mm nozzle")
        + b.row(
            ("0 0 880px", b.fig(photo, "A clear printed elbow pushed onto a port of a black water pump", "23 October 2026 · Siraya TPU 85A",
                                "A printed elbow on a port of the water pump. The port is a barbed stub wider than the elbow&rsquo;s bore, so the elbow has to stretch to go on and then grips it.",
                                h=820, pos="55% 92%", zoom=200)),
            ladder, gap=70, style="margin-top:34px")
        + b.rulebar(30, 28)
        + b.row(
            ("0 0 1010px", "<h2>The recipe</h2>" + recipe
             + b.still_open("The 85A sleeve that seated also had a thicker wall than the 95A one that locked, so that pair changed two things. 90A has never been tried "
                            "on a stretch fit. Nothing compares the two plates: gaskets printed on textured PEI on 8 October &ldquo;turned out fine&rdquo;.")),
            "<h2>The flow limit is the speed</h2>"
            + f'<p class="small">Each maker caps how much plastic may pass through the nozzle in a second: {S(el, "/filament_max_volumetric_speed/0")} mm³ for 85A. On a solid '
              f'part that cap decides the speed. The gasket profile asks for {S(ga, "/outer_wall_speed/0")} mm/s walls. The gasket printed on 23 October 2026 ran them at 21.</p>'
            + "<h2>How it is fed</h2>"
            + f'<p class="small">Through the right hotend, from a spool outside the printer. No AMS feeds TPU. The spool turns on an axle in a sealed box. '
              f'To dry it, the Bambu 85A spool went into the AMS HT on 13 October 2026 at {S("tpu-drying", "/displayed_state/set_temperature_c")} °C for '
              f'{S("tpu-drying", "/displayed_state/set_duration_hours")} hours, the cycle published for 90A.</p>'
            + "<h2>Its bed is not PET-GF&rsquo;s</h2>"
            + f'<p class="small" style="margin:0">A glued Engineering Plate at {S(el, "/eng_plate_temp/0")} °C, with a Z trim of {S("tpu-accepted", "/local_user_z_trim_mm")}. PET-GF prints on a '
              f'{S(pg, "/curr_bed_type")} at {S(pg, "/textured_plate_temp/0")} °C, with a trim of its own on each printer. On 12 October a TPU liner printed at that trim fell over. '
              "The next evening Derek changed the plate: &ldquo;So not our usual 0.18 offset, but with zero offset.&rdquo;</p>",
            gap=70)
        + _rec(b.link("The sleeve&rsquo;s print log", f"{O}/print-log.md"), b.link("Too stiff", f"{AMS}/physical-result.json"),
               b.link("The elbow&rsquo;s fit", f"{OUTER10}/physical-result.json"), b.link("The elbow recipe", f"{LINKS}/README.md"),
               b.link("The 23 October gasket", "hardware/printed-parts/faucet/industrial/prints/2026-10-23-mounting-gasket-tpu85a-right06-mark2/README.md"),
               b.link("What dries where", "hardware/ledger/tools.md", anchor="what-dries-where"),
               b.link("The fallen liner", f"{T}/2026-10-12-tpu-liners-mark1/failure.json"),
               b.link("The wrong plate", f"{SLEEVE}/cancelled-plate-mismatch/cancellation.json"))
    )
    return Page("choose-the-hardness-by-the-fit", "TPU: choose the hardness by the fit", "tpu", body, right="The plastic")


# ----------------------------------------------------------------------------- 2 the fan
def fan():
    photo = b.asset("tpu-curled-lip.jpg", f"{FIRST}/curl-left-edge.jpg")
    PW, PH = 1250, 820
    marks = _marks(PW, PH, [(1, (474, 413), (300, 270), "hot"), (2, (577, 405), (800, 220), ""), (3, (748, 503), (960, 610), "")])
    figure = (f'<figure style="position:relative; width:{PW}px"><img class="photo" src="art/{photo}" '
              f'alt="A printer nozzle over a small black cup-shaped print whose left rim has lifted" style="height:{PH}px; object-position:50% 45%">{marks}'
              '<figcaption class="cap"><span class="lab">13 October 2026 · Mark 1 · Bambu TPU 85A</span>'
              "The first elbow on the Engineering Plate, about three millimetres tall: the heel of the V, widening as it rises. The nozzle is over its left lip.</figcaption></figure>")
    seen = _numbered([
        "<b>The lip.</b> About layer 28, a millimetre of the outside edge curled upward on the left.",
        "<b>The nozzle.</b> The next layers pressed the edge down. It sprang back.",
        "<b>Loose plastic.</b> Around layer 31 a glob was pulled off the lip and carried elsewhere. A lump lies on the bed here.",
    ], hot=(1,))
    caps = '<div class="grid3" style="gap:20px; margin-top:8px">' + "".join(f'<p class="tiny" style="margin:0">{t}</p>' for t in (
        "The outer edge of the newest courses lifts.", "The next pass presses it flat. It springs back behind the nozzle.",
        "The nozzle catches the raised edge and carries a piece away.")) + "</div>"
    body = (
        b.head("Cooling", "Less fan made it curl more.",
               "Where a wall leans out, the newest ring of plastic has air under its outer edge. In soft TPU that edge curled upward while the "
               "fan was blowing at full. Derek halved the fan to see what would happen. Both lips curled at once.", size=168, lede_size=54, top=56)
        + b.scope("Bambu TPU 85A, black · Mark 1 · glued Engineering Plate · right 0.6 mm nozzle", not_tried="Siraya 85A")
        + b.row(("0 0 1250px", figure),
                "<h2>What Derek watched</h2>" + seen
                + '<div style="margin-top:34px">' + b.quote("Haha, just to test, I dropped part fan from 100 to 50 just now and like instantly we got more curl on that left edge and then the right edge curled too.",
                                                            "DEREK · DURING THAT PRINT", size=44) + "</div>"
                + '<p class="small" style="margin:30px 0 0">The left lip had curled with the fan at full. Halving it made that worse and brought the right lip up too.</p>',
                gap=70, style="margin-top:36px")
        + f'<div style="margin-top:30px">{_curl_strip()}</div>' + caps
        + b.rulebar(34, 30)
        + b.row(
            ("0 0 600px", b.stat(b.setting("tpu-elbow", "/fan_min_speed/0") + "<span>%</span>", "part fan in the TPU 85A recipes, on every layer after the first", hot=True)
             + '<div style="margin-top:26px">' + b.stat(b.setting("tpu-petgf", "/fan_max_speed/0") + "<span>%</span>",
                                                        f'part fan on PET-GF&rsquo;s ordinary walls. It comes on, at {b.setting("tpu-petgf", "/overhang_fan_speed/0")}%, only for a road laid over air.') + "</div>"),
            b.block("Ten degrees cooler changed nothing", "Two prints later the layers ran at 215 °C instead of 225 °C. Derek saw faint curl at layer 21, and at layer 27: "
                    "&ldquo;it is about the same as 2 prints ago. I was wrong about it being sudden at 28, I just happened to notice it there.&rdquo;")
            + b.block("What we do", "The part fan stays at full on soft TPU that leans. That did not stop the curl. What ended it is on the last page of this part, and the fan was at full there too."),
            ("0 0 560px", b.still_open("Why less fan curled it more is not known. It was one change to one running print, and the layer was not noted. "
                                       "It has not been tried on the Siraya spool.")
             + _rec(b.link("What was seen, and the photograph", f"{FIRST}/physical-result.json"), b.link("Ten degrees cooler", f"{T215}/physical-result.json"),
                    b.link("PET-GF&rsquo;s cooling", "hardware/printed-parts/cooling/README.md"))),
            gap=60)
    )
    return Page("less-fan-made-it-curl-more", "TPU: less fan made it curl more", "tpu", body, right="Cooling")


# ----------------------------------------------------------------------------- 3 speed
def speed():
    el, sl = "tpu-elbow", "tpu-sleeve"
    S = b.setting
    table = ('<table class="grid" style="font-size:32px"><thead><tr><th>13 October 2026</th><th>Outer wall set to</th><th>The lip ran at</th></tr></thead><tbody>'
             '<tr><th>21:09 · first elbow</th><td>25 mm/s</td><td><b>14.6 to 17.6</b></td></tr>'
             '<tr><th>21:45 · &ldquo;slower&rdquo;</th><td>10 mm/s</td><td><b style="color:var(--hot)">15.8 to 21.8</b></td></tr>'
             '<tr><th>23:05 · slower and cooler</th><td>10 mm/s</td><td><b style="color:var(--hot)">15.8 to 21.8</b></td></tr>'
             '<tr><th>The corrected file</th><td>10 mm/s</td><td><b>10.0</b></td></tr></tbody></table>'
             '<p class="tiny" style="margin:12px 0 0">Millimetres a second at the lip on layers 26 to 33, read from each file.</p>')
    overhang = ('<table class="grid" style="font-size:32px"><thead><tr><th>Overhang table</th><th>Stock</th><th>Elbow recipe</th></tr></thead><tbody>'
                f'<tr><th>Second band</th><td>{S(sl, "/overhang_2_4_speed/0")} mm/s</td><td><b>{S(el, "/overhang_2_4_speed/0")} mm/s</b></td></tr>'
                f'<tr><th>Third band</th><td>{S(sl, "/overhang_3_4_speed/0")} mm/s</td><td><b>{S(el, "/overhang_3_4_speed/0")} mm/s</b></td></tr>'
                f'<tr><th>Outer wall</th><td>{S(sl, "/outer_wall_speed/0")} mm/s</td><td><b>{S(el, "/outer_wall_speed/0")} mm/s</b></td></tr></tbody></table>')
    body = (
        b.head("Speed", "The setting said 10.<br>The lip ran at 16.",
               "A slicer keeps more than one speed for the same wall. Where the wall leans out, Bambu Studio takes its speed from a separate "
               "overhang table. Two trials that were meant to print a curling lip slowly printed it faster than the trial before them.",
               size=150, lede_size=54, top=56)
        + b.scope("Bambu TPU 85A · Mark 1 · right 0.6 mm nozzle · sliced in Bambu Studio", not_tried="other plastics, whose files have the same table")
        + b.row(
            ("0 0 1250px", f'<div style="margin-top:6px">{_speed_chart()}</div>'
                           '<p class="cap"><span class="lab">The lip of the elbow, layer by layer</span>'
                           '<span class="num" style="width:44px; height:44px; font-size:25px; vertical-align:-8px">1</span> Layer 21, 14.4 mm/s: faint curl already. '
                           '<span class="num" style="width:44px; height:44px; font-size:25px; vertical-align:-8px; margin-left:10px">2</span> Layer 27, 16.4 mm/s: '
                           '&ldquo;about the same as 2 prints ago&rdquo;.</p>'),
            b.quote("Maybe we can try slowing down that outer edge more?", "DEREK · 13 OCTOBER 2026, AFTER THE FIRST CURL", size=45)
            + '<p class="small" style="margin-top:30px">So the outer wall went from 25 mm/s to 10 and the elbow was printed again. The edges looked different for a moment, then the same.</p>'
            + b.quote("Oh, maybe it is curling. I guess I&rsquo;m not interested in a midpoint when the difference in those numbers is 10 13 17 so small and the "
                      "difference I&rsquo;m observing is maybe non existent upon reflection.", "DEREK · LOOKING AT THE SECOND PRINT", size=41)
            + '<p class="small" style="margin:30px 0 0">He was right. The file had not slowed the lip at all.</p>',
            gap=70, style="margin-top:36px")
        + b.rulebar(36, 32)
        + b.row(
            ("0 0 900px", table + '<div style="margin-top:34px">' + overhang + "</div>"),
            "<h2>Why</h2>"
            '<p class="small">The outer wall speed covers beads that sit squarely on the layer below. A bead that hangs partly over air takes its speed from the overhang '
            "table, and two bands of that table still held stock values. The slicer blended them with the wall speed, then stretched each layer to its minimum time of "
            f'{S(el, "/slow_down_layer_time/0")} seconds. With the plain walls slower, that slowdown was shared out differently, and the lip came out faster.</p>'
            "<h2>The fix</h2>"
            '<p class="small">Set those bands to the wall speed, then read the file. In the corrected file all 13,728 outer-wall moves from layer 2 to the top run at 10.0 mm/s.</p>'
            + b.block("Before you print", "Do not trust the speed box. Pick the feature that matters and read the speed the sliced file commands there, layer by layer. "
                      'In this repository that is <span class="mono" style="font-size:30px">hsm-gcode speeds FILE --layers 17-33 --at leftmost</span>.'),
            gap=70)
        + b.row(
            b.still_open("Whether a true 10 mm/s cures the curl in Bambu 85A is not known. The corrected Bambu file was never sent as a single elbow. "
                         "The first lips printed at a real 10 were a different brand, an hour later."),
            ("0 0 800px", _rec(b.link("Set against emitted, 21:09 and 21:45", f"{OUTER10}/outer-speed-comparison.json"), b.link("The 23:05 file", f"{T215}/emitted-commands.json"),
                               b.link("The corrected file", f"{FIXED}/README.md"), b.link("The reader", "tools/gcode/README.md"))),
            gap=70)
    )
    return Page("the-setting-said-10", "TPU: the setting said 10, the lip ran at 16", "tpu", body, right="Speed")


# ----------------------------------------------------------------------------- 4 islands
def island():
    photo = b.asset("tpu-liner-loops.jpg", f"{T}/2026-10-12-liners-d775-mark1/wall-start-physical-1.jpg")
    body = (
        b.head("Stops and starts", "One island at a time.",
               "Each time the nozzle stops laying TPU and starts again elsewhere, a little leaks on the way and a little too much arrives. "
               "Two objects on a bed mean that on every layer.",
               lede_size=50, top=56)
        + b.scope("Bambu and Siraya TPU 85A · Mark 1 and Mark2 · right 0.6 mm nozzle", not_tried="90A, 95A")
        + '<div class="grid2" style="margin-top:34px; gap:60px">'
        + f'<figure>{_islands(False)}<figcaption class="cap"><span class="lab">14 October 2026 · two elbows, two islands</span>'
          "The bed from above, ten millimetres up. The file made 367 hops between the two elbows in 184 layers.</figcaption></figure>"
        + f'<figure>{_islands(True)}<figcaption class="cap"><span class="lab">16 October on · the same two, one island</span>'
          "A web drawn between them makes every layer one piece, so the nozzle can cross on plastic it is laying.</figcaption></figure></div>"
        + b.rulebar(26, 24)
        + b.row(
            ("0 0 700px", b.fig(photo, "A black printed liner with a row of small loops standing along one edge of its channel", "12 October 2026 · Bambu TPU 85A",
                                "Two liners printed two millimetres apart. Derek watched a loop form where a wall started, just after the nozzle arrived from the other liner.",
                                h=400, pos="96% 66%", zoom=185)),
            b.quote("With both ASA Aero and TPU I am finding that the distance between objects increases risk of problems on these &quot;unclean start/stop&quot; filaments.",
                    "DEREK · 12 OCTOBER 2026", size=41)
            + '<p class="small" style="margin-top:26px">That day two liners printed 32 mm apart, and one fell over. The next evening two elbows on one plate failed: '
              "&ldquo;you&rsquo;re gonna make life much easier on both of us if you only try to print one at a time.&rdquo;</p>"
            + '<p class="small" style="margin:0"><b>A timelapse is a hop too.</b> With it on, the head left for the camera after every layer, 184 times in the pair&rsquo;s file. It is off for TPU.</p>',
            ("0 0 390px", f'<figure>{_fork()}<figcaption class="cap"><span class="lab">Eighteen millimetres up</span>Each elbow has forked. Two fins and the web keep it one island.</figcaption></figure>'),
            gap=56)
        + b.rulebar(24, 22)
        + b.row(
            b.block("What we do", "One TPU object on a plate, or neighbours two millimetres apart. A pair is drawn as one piece, joined by fins. "
                    "The fins are cut off with a blade: soft TPU stretches instead of snapping."),
            b.quote("Why didn&rsquo;t you make the fin between the two objects a vertical fin at the center point of them?", "DEREK · 16 OCTOBER 2026", size=40)
            + '<p class="small" style="margin:24px 0 0">The first web had followed one leg. Joining alone was not enough: that pair still came out full of threads. The strings page says why.</p>',
            ("0 0 620px", b.still_open("How much the distance matters has not been measured: the liner retry also took off the Z trim. "
                                       "The two-island elbow print of 14 October has no result on record.")
             + _rec(b.link("The fallen liner", f"{T}/2026-10-12-tpu-liners-mark1/failure.json"), b.link("The loops", f"{T}/2026-10-12-liners-d775-mark1/wall-start-observation.json"),
                    b.link("Two islands, 367 hops", f"{TWO}/README.md"), b.link("The joined pair", f"{WEB}/README.md"),
                    b.link("Hops counted", "future/pump-elbow-exploration/stringing-candidates.md"))),
            gap=60)
    )
    return Page("one-island-at-a-time", "TPU: one island at a time", "tpu", body, right="Stops and starts")


# ----------------------------------------------------------------------------- 5 undersides
def underside():
    photo = b.asset("tpu-elbow-ragged-edges.jpg", f"{OUTER10}/underside-sag-photo-1.jpg")
    body = (
        b.head("Orientation", "Every underside at 45 degrees or steeper.",
               "The elbow prints standing on its corner like a V, both mouths up. Stood that way, no face looks down at the bed more shallowly than "
               "45 degrees and no bore needs support. Its two sides are still not alike.",
               size=150, lede_size=54, top=56)
        + b.scope("Bambu TPU 85A, black · Mark 1 · glued Engineering Plate · right 0.6 mm nozzle", not_tried="other TPUs")
        + b.row(
            ("0 0 1040px", b.fig(photo, "A black V-shaped print on the bed under the nozzle, its sloping outer edges ragged", "13 October 2026 · the elbow on the bed",
                                "The large socket is on the left. Its outer face leans at 45° from the bed up, and is ragged from the bed up. The right side is smooth "
                                "low down, where it is steeper, and ragged above.", h=570, pos="50% 62%")),
            f'<figure>{_elbow_section()}<figcaption class="cap"><span class="lab">The same elbow cut down its middle</span>Both legs lean at 45°. '
            "The outsides do not: the tube socket begins with a steeper neck.</figcaption></figure>",
            gap=60, style="margin-top:34px")
        + b.rulebar(34, 30)
        + b.row(
            ("0 0 1160px", f'<figure>{_lips()}<figcaption class="cap"><span class="lab">The two outside edges at layer 28, at true proportions</span>'
                           "Read from the slice of the first elbow, 13 October 2026.</figcaption></figure>"),
            b.quote("Oh, the left edge is the one that gets the bigger tube. Sure you got the same gradual angle on the underside on left and right?", "DEREK · 13 OCTOBER 2026", size=43)
            + '<p class="small" style="margin:28px 0 0">The curl was first noticed at layer 28, on the left. Both legs lean the same. Their outsides, at that height, do not. '
              "It was Derek who thought to compare them.</p>"
              '<p class="small" style="margin:22px 0 0">Three days earlier, asking for another TPU sleeve: &ldquo;For printability, I&rsquo;d like steeper than 45 degrees please.&rdquo;</p>',
            gap=70)
        + b.rulebar(34, 30)
        + b.row(
            ("0 0 560px", f'<figure>{_full_base()}<figcaption class="cap"><span class="lab">13 October 2026 · stopped</span></figcaption></figure>'),
            "<h2>Added stock has to be solid to the bed</h2>"
            + b.quote("You added material both above and below, and you left a gap that makes the below useless", "DEREK · ON THAT ELBOW", size=41)
            + '<p class="small" style="margin:26px 0 0">Plastic had been added under the legs to hold them up, with a channel left under each cuff. A block that does not touch '
              "the thing above it holds nothing up. The elbow that prints today has no added stock. It stands on a flat cut across its heel.</p>",
            ("0 0 640px", b.still_open("The shallower side curled first, which fits and proves little: the two sides also differ in size and wall. "
                                       "No TPU part has been printed with every underside steeper than 45° to see if its edges come out clean.")
             + _rec(b.link("Left against right", f"{FIRST}/underside-side-comparison.json"), b.link("The ragged elbow", f"{OUTER10}/physical-result.json"),
                    b.link("The stopped one", f"{FULLBASE}/physical-result.json"), b.link("The elbow today", "hardware/printed-parts/diaphragm-pump-sleeve/README.md"),
                    f'<a href="{b.GITHUB}/commit/c1e661bd0">Steeper than 45</a>')),
            gap=56)
    )
    return Page("every-underside-45-degrees-or-steeper", "TPU: every underside at 45 degrees or steeper", "tpu", body, right="Orientation")


# ----------------------------------------------------------------------------- 6 the cap
def cap():
    sl, ga, cp = "tpu-sleeve", "tpu-gasket", "tpu-sleeve-cap"
    S = b.setting
    body = (
        b.head("First layer", "A thin soft wall starts on a cap.",
               "The sleeve that seals the faucet&rsquo;s tube is a cylinder of soft plastic one bead thick. A wall that thin has almost nothing "
               "to stand on, and the first version could not be sliced at all. It now begins with a flat cap, laid first, and the wall rises from that.",
               size=160, lede_size=54, top=56)
        + b.scope("Bambu TPU 95A in May 2026, 85A since · the sleeve of 23 October 2026: Mark2, glued Engineering Plate, right 0.6 mm nozzle", not_tried="Siraya 85A")
        + b.row(
            ("0 0 900px", f'<figure>{_sleeve_section()}<figcaption class="cap"><span class="lab">23 October 2026 · Mark2 · Bambu TPU 85A, black</span>'
                          "The sleeve as that file printed it, at its true proportions. Derek: &ldquo;Okay, that came out pretty well.&rdquo;</figcaption></figure>"),
            '<div style="display:flex; gap:34px; align-items:flex-start">'
            f'<div style="flex:0 0 620px">{_no_first_layer()}</div>'
            '<div><h2>22 May 2026: refused</h2><p class="small" style="margin:0">The first sleeve was an open ring with a wall 0.375 mm thick. The slicer would not start it: '
            "&ldquo;empty initial layer&rdquo;. One first-layer line was wider than the wall.</p></div></div>"
            + '<h2 style="margin-top:34px">24 May: cap down</h2>'
            '<p class="small">A floor with a hole in it was added to one end and the part was turned to print on it. The first layer is now a flat ring several beads across. '
            "It sliced without a raft and printed without trouble, in 95A.</p>"
            "<h2>30 May: one bead, one spiral</h2>"
            f'<p class="small">The wall was thickened to one bead of the {S(sl, "/line_width")} mm profile and the softer 85A went in. After the cap the nozzle climbs in a single '
            "unbroken spiral. A spiral never stops, so the wall cannot string. The cap can: its flat layers had five places where a thread could cross the hole, until the "
            "23 October file laid each of them as one tour.</p>"
            "<h2>Drawn thick, printed thin</h2>"
            f'<p class="small" style="margin:0">In spiral mode only the bottom layers are solid. This recipe has {S(cp, "/native_bottom_layers")}, which makes a cap '
            f'{S(cp, "/native_solid_cap_height_mm")} mm thick. The model draws it {S(cp, "/modeled_cap_height_mm")} mm thick. Read the cap from the slice, not from the drawing.</p>',
            gap=70, style="margin-top:34px")
        + b.rulebar(34, 30)
        + b.row(
            ("0 0 940px", f'<figure>{_gasket_section()}<figcaption class="cap"><span class="lab">A flat gasket in section</span>'
                          f'First layer {S(ga, "/initial_layer_print_height")} mm, then {S(ga, "/layer_height")} mm layers. Ten of them make 1.92 mm of a gasket drawn 2 mm thick.</figcaption></figure>'),
            "<h2>Flat gaskets print solid</h2>"
            f'<p class="small">A gasket is squeezed between two faces, so it is laid flat and filled: {S(ga, "/wall_loops")} walls round every edge and {S(ga, "/sparse_infill_density")} '
            "fill between, in Bambu 85A on the stock profile. In June 2026: &ldquo;gaskets are going well.&rdquo; The plate of eight printed on Mark2 on 8 October &ldquo;turned out fine&rdquo;.</p>"
            + b.quote("&hellip;consider carefully if there&rsquo;s any lessons we&rsquo;ve learned from our avoiding threads other places that might apply here&hellip;",
                      "DEREK · 23 OCTOBER 2026, ASKING FOR THE SLEEVE", size=40),
            gap=70)
        + b.still_open("&ldquo;Pretty well&rdquo; is all that is recorded of the 23 October sleeve. Whether it strings less, how it seats, and whether a cap a third as thick "
                       "as drawn seals as intended are not written down. Nor is the result of the gasket printed the same evening with every layer as one tour.")
        + _rec(b.link("The sleeve&rsquo;s print log, May to October", f"{O}/print-log.md"), b.link("The 23 October sleeve", f"{SLEEVE}/README.md"),
               b.link("Its cap, read from the file", f"{SLEEVE}/emitted-path-review.json"), b.link("Gaskets print log", "hardware/printed-parts/gaskets-print-log.md"),
               b.link("The plate of eight", "hardware/printed-parts/prototype-gaskets-2026-10-08/README.md"),
               b.link("The gasket of 23 October", "hardware/printed-parts/faucet/industrial/prints/2026-10-23-mounting-gasket-tpu85a-right06-mark2/README.md"))
    )
    return Page("a-thin-soft-wall-starts-on-a-cap", "TPU: a thin soft wall starts on a cap", "tpu", body, right="First layer")


# ----------------------------------------------------------------------------- 7 two brands
def brands():
    black = b.asset("tpu-elbow-ragged-edges.jpg", f"{OUTER10}/underside-sag-photo-1.jpg")
    clear = b.asset("tpu-elbow-siraya-clean.jpg", f"{SIRAYA}/finished-elbow-1.jpg")
    rows = [
        ("Spool", "Bambu TPU 85A, black", "Bambu TPU 85A, black", "Bambu TPU 85A, black", "<b>Siraya Tech Flex TPU 85A, clear</b>"),
        ("Opened", "earlier", "earlier", "earlier", "<b>that night</b>"),
        ("Nozzle after the first layer", "225 °C", "225 °C", "<b>215 °C</b>", "215 °C"),
        ("Lip speed that ran, mm/s", "14.6 to 17.6", "15.8 to 21.8", "15.8 to 21.8", "<b>10.0</b>"),
        ("Flow ratio", "1.00", "1.00", "1.00", "<b>0.96</b>"),
        ("Auxiliary fan", "100%", "100%", "100%", "<b>off</b>"),
        ("Retraction", "1.0 mm", "1.0 mm", "1.0 mm", "<b>0.8 mm</b>"),
        ("The lips", "curled", "rough", "curled the same", '<b style="color:var(--good)">clean</b>'),
    ]
    table = ('<table class="grid" style="font-size:31px"><thead><tr><th></th><th>13 October<br>21:09</th><th><br>21:45</th><th><br>23:05</th><th>14 October<br>00:11</th></tr></thead><tbody>'
             + "".join(f'<tr><th style="font-weight:400; color:var(--muted)">{r[0]}</th>' + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>" for r in rows)
             + "</tbody></table>"
             '<p class="tiny" style="margin:12px 0 0">Bold marks a change from the print before. The same model, printer, nozzle, plate, layers, six walls and full part fan throughout.</p>')
    body = (
        b.head("Two brands", "Two brands, one hardness.",
               "Two spools both say 85A. One curled its lips on three elbows in an evening. The other printed them clean at its first try, an hour "
               "after the last. Six things changed between those two prints, and nobody has gone back to find out which one mattered.", lede_size=54, top=56)
        + b.scope("Bambu TPU 85A and Siraya TPU 85A · Mark 1 · glued Engineering Plate, no Z trim · right 0.6 mm nozzle")
        + '<div class="grid2" style="margin-top:34px; gap:60px">'
        + b.fig(black, "A black V-shaped elbow on the bed with ragged sloping edges", "13 October 2026, 21:45 · Bambu TPU 85A",
                "Rough at every 45° edge. It still fitted: &ldquo;nice firm friction stretchy fit&rdquo;.", h=500, pos="50% 72%")
        + b.fig(clear, "A clear V-shaped elbow standing on a wooden board, its surfaces smooth", "14 October 2026, 00:11 · Siraya TPU 85A",
                "&ldquo;Turned out perfect.&rdquo; Then, of the inside: &ldquo;I do see some stringing inside as well.&rdquo;", h=500, pos="36% 6%", zoom=150)
        + "</div>"
        + b.rulebar(34, 30)
        + b.row(
            ("0 0 1340px", table),
            b.quote("You sure you don&rsquo;t want to try 215? That is within their range and we&rsquo;re already lowering the speed from their profile.",
                    "DEREK · LOADING THE NEW SPOOL", size=41)
            + '<h2 style="margin-top:34px">What is known</h2>'
            '<p class="small">Heat alone is not it: the third black elbow ran at the same 215 °C and curled. The clear recipe has since printed the pair that went on the pump, '
            "on Mark2 on 22 October. Black Bambu 85A printed the faucet sleeve on 23 October, which has no leaning lip, and it &ldquo;came out pretty well&rdquo;.</p>"
            "<h2>What we do</h2>"
            '<p class="small" style="margin:0">Elbows print in the clear Siraya on its whole recipe. Sleeves and gaskets print in black Bambu. Neither choice is a verdict on a brand.</p>',
            gap=60)
        + '<div class="grid3" style="gap:50px; margin-top:6px">'
        + b.still_open("<b>Which change ended the curl.</b> The print that would say is one black Bambu elbow, alone, with its lip checked at 10 mm/s. That file was prepared on "
                       "13 October and never sent. Black pairs printed at a checked 10 on 15 and 16 October, for the string trials. Nobody judged their lips.")
        + b.still_open("<b>Water in the spool.</b> The black spool went into the dryer after its three curled prints, and whether the cycle finished is not recorded. "
                       "The clear one came out of a sealed bag.")
        + b.still_open("<b>The seal.</b> &ldquo;Seal seems as good as before&rdquo; names no pressure and no time. The elbows have not been held at pressure and watched.")
        + "</div>"
        + _rec(b.link("The clear elbow, and what changed", f"{SIRAYA}/physical-result.json"), b.link("Its recipe and where it came from", f"{SIRAYA}/material-profile.json"),
               b.link("The rough black elbow", f"{OUTER10}/physical-result.json"), b.link("The black spool in the dryer", f"{FIXED}/filament-drying.json"),
               b.link("The pair on Mark2", f"{ACCEPTED}/physical-result.json"), b.link("The pressure test still to run", "hardware/printed-parts/diaphragm-pump-sleeve/README.md", anchor="acceptance"))
    )
    return Page("two-brands-one-hardness", "TPU: two brands, one hardness", "tpu", body, right="Two brands")


def pages():
    return [plastic(), _mine.strings(), fan(), speed(), island(), underside(), cap(), brands()]
