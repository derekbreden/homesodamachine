"""PET-GF cradle holding the funnel's PP0308E drain elbow under the funnel frame.

Coordinates are local to the frame's drain hole: the origin is on the hole's axis in the frame's
flat underside, +Z up and +Y aft. The scanned elbow stands with its +Z leg up the hole, its fixed
nose face on that underside, and its +Y leg aft toward V-B.

The cradle is the block under the elbow less the elbow's upward shadow grown by `fits.slip`. The
elbow drops straight in, and every pocket face opens upward, so the body prints bottom-down. The
block's top stands 1 mm under the top of the vertical leg's root band: the pocket wraps the band
about 78% of the way round, and the collar, rung and nose stand free above it.

Each X side of the block carries on up as a wing, the body's full length, through a straight slot
in the frame's bottom web. A flat hook at the wing's top reaches outward over the web to within
`TIP_GAP` of the counterbore's X wall, which sets the block's width and so how far the slots stand
off the drain hole. Going up, each wing bends inward into its slot's inboard lane until the hook
clears the slot's outer edge, then springs back over the web. The plug's pockets, open through its
X sides, keep it there.

The counterbore and the silicone plug are rectangles centred on the hole, the plug's width across
X. The counterbore's ±Y walls stand on the slots' farther ends, so the web carries no strip between
a slot and a wall, and the plug's hook pockets open through its +Y end as well as its X sides.
"""

import functools
import json
import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
for _p in (_hw / "scripts", _hw / "printed-parts" / "cadlib",
           _hw / "reference" / "jg-pp0308e-elbow", _tools):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import fits                                                   # noqa: E402
import elbow as _elbow                                        # noqa: E402

WEB = 3.0              # the frame's bottom web under the plug
SLIP = fits.slip       # pocket off the scanned elbow
WALL = 3.0             # block wall and floor beyond the elbow's widest section
HOLE_D = 11.25         # the 10.64 mm collet passes 0.3 mm a side; the 12.12 mm nose bears round it
ELBOW_Z = -_elbow.FIXED_FACE   # the elbow's axis intersection, under the frame's underside
BODY_TOP_STATION = 10.0   # vertical-leg station of the block's top, 1 mm under the root band's top
SOCKET_HALF = 18.3     # the counterbore's half-width, `funnel_frame.socket_width / 2`
TIP_GAP = fits.slip    # hook tip off the counterbore's X wall

LEAF_T = 1.3           # wing thickness
SIDE = 0.5             # slot's outer edge off the wing's outer face
OVERLAP = 2.6          # hook over the web past that edge
HOOK_T = 2.0           # flat hook thickness
HOOK_RISE = 0.25       # further lift the printed hooks need to clear the web
CATCH_GAP = fits.slip + fits.supported_surface + HOOK_RISE   # hook underside over the web, cradle home
INSERTION_SLIP = 0.1   # hook tip inside the slot's outer edge while it passes
END_SLIP = 0.25        # slot beyond each wing end
POCKET_AIR = 0.5       # plug pocket round each hook and wing top
PLUG_CORNER = 0.0      # square plug corners; the socket's corner radius is its gap

# The scanned elbow's bend: a round core with short stubs up both legs, and a thin web at its
# outer corner, as `elbow.build` draws them.
CORE_R = 4.05
CORE_STUB = 3.5
CORNER_WEB = (5.16, 7.57, 7.57)
CORNER_WEB_OFFSET = -0.285


def _profiles(leg):
    data = json.loads((Path(_elbow.HERE) / "scan-measurements.json").read_text())
    p = data["profiles"][leg]
    return p["fixed_body"], p["collet"]


def block():
    """`(half_width, y0, y1, z0, z1)` of the block the pocket is cut from. Its X sides are the
    wings' outer faces, set back from the counterbore's wall by the hook and its clearances."""
    rz = max(r for _t, r in _profiles("z")[0]) + SLIP + WALL
    ry = max(r for _t, r in _profiles("y")[0]) + SLIP + WALL
    half = SOCKET_HALF - TIP_GAP - OVERLAP - SIDE
    assert half >= max(rz, ry), (half, rz, ry)
    return (half, -rz, _elbow.COLLET_FACE, ELBOW_Z - ry, ELBOW_Z + BODY_TOP_STATION)


def elbow_parts():
    """The scanned elbow's named parts, standing in the hole."""
    return {n: p.val().translate(cq.Vector(0, 0, ELBOW_Z)) for n, p in _elbow.build()}


def _revolve(points, leg):
    """Solid of revolution of `(station, radius)` points about a leg through the elbow origin."""
    raw = [(0.0, points[0][0])] + [(r, t) for t, r in points] + [(0.0, points[-1][0])]
    pts = []
    for p in raw:
        if not pts or abs(p[0] - pts[-1][0]) > 1e-6 or abs(p[1] - pts[-1][1]) > 1e-6:
            pts.append(p)
    k = 1
    while k < len(pts) - 1:
        (x0, y0), (x1, y1), (x2, y2) = pts[k - 1], pts[k], pts[k + 1]
        if abs((x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)) < 1e-9:
            pts.pop(k)
        else:
            k += 1
    solid = cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0, 0), (0, 1, 0)).val()
    return solid.rotate(cq.Vector(), cq.Vector(1, 0, 0), -90) if leg == "y" else solid


def shadow(top):
    """Everything directly above the elbow, grown by `SLIP`, up to local Z `top`."""
    c = SLIP
    zb, zc = _profiles("z")
    yb, yc = _profiles("y")
    h = top - ELBOW_Z
    # vertical leg: the running maximum radius from the bottom up, carried to the top
    run, m = [], 0.0
    for t, r in zb + zc[1:]:
        m = max(m, r)
        run.append((t, m + c))
    run.append((h + 1.0, run[-1][1]))
    out = _revolve([(0.0, run[0][1])] + run, "z")
    # horizontal leg: the leg itself, and its plan footprint from the axis up
    out = out.fuse(_revolve([(s, r + c) for s, r in yb + yc[1:]], "y"))
    edge = []
    for s, r in yb + yc[1:]:
        q = (r + c, s)
        if not edge or abs(q[0] - edge[-1][0]) > 1e-6 or abs(q[1] - edge[-1][1]) > 1e-6:
            edge.append(q)
    plan = [(-x, y) for x, y in edge] + [(x, y) for x, y in reversed(edge)]
    out = out.fuse(cq.Workplane("XY").polyline(plan).close().extrude(h + 1.0).val())
    # the bend core and its outer-corner web, each with the column above it
    rc = CORE_R + c
    core = cq.Solid.makeSphere(rc, angleDegrees1=-90, angleDegrees2=90)
    core = core.fuse(cq.Solid.makeCylinder(rc, h + 1.0, cq.Vector(), cq.Vector(0, 0, 1)))
    core = core.fuse(cq.Solid.makeCylinder(rc, CORE_STUB, cq.Vector(), cq.Vector(0, 1, 0)))
    core = core.fuse(cq.Solid.makeBox(2 * rc, CORE_STUB, h + 1.0, cq.Vector(-rc, 0, 0)))
    wx, wy, wz = (d / 2 + c for d in CORNER_WEB)
    web = cq.Solid.makeBox(2 * wx, 2 * wy, h + 1.0 + wz,
                           cq.Vector(-wx, CORNER_WEB_OFFSET - wy, CORNER_WEB_OFFSET - wz))
    return out.fuse(core).fuse(web).clean().translate(cq.Vector(0, 0, ELBOW_Z))


def _bent(points, length, tip):
    """Wing and hook points `(x, h, x_neutral)` under a tip-loaded cantilever from the body top,
    the hook rigid above the load line, with `tip` the deflection at `length`."""
    th = 1.5 * tip / length
    out = []
    for x, h, xn in points:
        if h <= length:
            s = h / length
            d = tip * s * s * (3 - s) / 2
            t = tip * 3 / (2 * length) * (2 * s - s * s)
            out.append((xn - d + (x - xn) * math.cos(t), h + (x - xn) * math.sin(t)))
        else:
            dx, dh = x - xn, h - length
            out.append((xn - tip + dx * math.cos(th) - dh * math.sin(th),
                        length + dx * math.sin(th) + dh * math.cos(th)))
    return out


def passage(w_in, w_out, tip, slot_out, base, face, top):
    """The hook deflection needed to clear the slot's outer edge at every height on the way up,
    and how far the wing's inner face then travels inward inside the web."""
    length, height = face - base, top - base
    xn = (w_in + w_out) / 2
    n = 60
    pts = [(x, height * k / n, xn) for k in range(n + 1) for x in (w_in, w_out)]
    pts += [(w_out + (tip - w_out) * k / n, h, xn) for k in range(n + 1) for h in (length, height)]
    pts += [(tip, length + (height - length) * k / n, xn) for k in range(n + 1)]
    need = travel = 0.0
    t = -top
    while t <= WEB - face + 1e-9:
        a, b = -base - t, WEB - base - t
        lo, hi = 0.0, 6.0
        for _ in range(40):
            mid = (lo + hi) / 2
            ok = all(not (a < h < b) or x <= slot_out - INSERTION_SLIP
                     for x, h in _bent(pts, length, mid))
            lo, hi = (lo, mid) if ok else (mid, hi)
        need = max(need, hi)
        moved = [w_in - x for (x, h), p in zip(_bent(pts, length, hi), pts)
                 if p[0] == w_in and a < h < b]
        travel = max([travel] + moved)
        t += 0.05
    return {"free_length": length, "hook_deflection": need, "inner_face_travel": travel,
            "root_strain": 1.5 * (w_out - w_in) * need / length ** 2}


@functools.cache
def stations():
    """The snap's stations, local mm, distances from the hole's axis in X."""
    half, y0, y1, z0, z1 = block()
    w_in, w_out = half - LEAF_T, half
    slot_out = w_out + SIDE
    face = WEB + CATCH_GAP
    s = {"half": half, "y0": y0, "y1": y1, "z0": z0, "top": z1, "w_in": w_in, "w_out": w_out,
         "slot_out": slot_out, "hook_tip": slot_out + OVERLAP, "face": face,
         "hook_top": face + HOOK_T}
    s["bend"] = passage(w_in, w_out, s["hook_tip"], slot_out, z1, face, s["hook_top"])
    s["lane"] = round(s["bend"]["inner_face_travel"] + fits.running, 2)
    s["slot_in"] = w_in - s["lane"]
    return s


def socket_half_length():
    """Half the counterbore's Y length: to the slots' ends at the wing end farther from the hole."""
    s = stations()
    return max(s["y1"] + END_SLIP, -(s["y0"] - END_SLIP))


def plug_half_length(half_width):
    """Half the plug's Y length: the counterbore's, less the plug's gap to its walls."""
    return socket_half_length() - (SOCKET_HALF - half_width)


def hook_corner_clearance(half_width):
    """How far each hook's outer +Y corner stands inside the counterbore's corner round."""
    s = stations()
    r = PLUG_CORNER + SOCKET_HALF - half_width
    cx, cy = SOCKET_HALF - r, socket_half_length() - r
    return r - math.hypot(max(s["hook_tip"] - cx, 0.0), max(s["y1"] - cy, 0.0))


def plug_outline(half_width, grow, z0, height, taper=0.0):
    """The plug's plan, centred on the hole and grown by `grow`, extruded from `z0`."""
    length = 2 * (plug_half_length(half_width) + grow)
    sketch = cq.Sketch().rect(2 * (half_width + grow), length)
    if PLUG_CORNER + grow > 0:
        sketch = sketch.vertices().fillet(PLUG_CORNER + grow)
    return (cq.Workplane("XY", origin=(0, 0, z0)).placeSketch(sketch)
            .extrude(height, taper=taper).val())


def socket(half_width, gap, depth, flare_h, flare):
    """The frame's plug socket from the web up, with its lead-in flare at the mouth."""
    body = plug_outline(half_width, gap, WEB, depth)
    lead = plug_outline(half_width, gap, WEB + depth - flare_h, flare_h,
                        taper=-math.degrees(math.atan(flare / flare_h)))
    return body.fuse(lead).clean()


def web_cuts():
    """The drain hole and the two wing slots through the frame's bottom web."""
    s = stations()
    cuts = [cq.Solid.makeCylinder(HOLE_D / 2, WEB + 2.0, cq.Vector(0, 0, -1.0))]
    for side in (-1, 1):
        x0, x1 = sorted((side * s["slot_in"], side * s["slot_out"]))
        cuts.append(cq.Solid.makeBox(x1 - x0, s["y1"] - s["y0"] + 2 * END_SLIP, WEB + 2.0,
                                     cq.Vector(x0, s["y0"] - END_SLIP, -1.0)))
    return cuts


def pockets():
    """The plug's hook pockets, from below the web top to past the hooks."""
    s = stations()
    out = []
    for side in (-1, 1):
        x0, x1 = sorted((side * (s["w_in"] - POCKET_AIR), side * (s["hook_tip"] + POCKET_AIR)))
        out.append(cq.Solid.makeBox(x1 - x0, s["y1"] - s["y0"] + 2 * POCKET_AIR,
                                    s["hook_top"] + POCKET_AIR - WEB + 1.0,
                                    cq.Vector(x0, s["y0"] - POCKET_AIR, WEB - 1.0)))
    return out


def build():
    """The cradle, local."""
    half, y0, y1, z0, z1 = block()
    s = stations()
    body = cq.Solid.makeBox(2 * half, y1 - y0, z1 - z0, cq.Vector(-half, y0, z0))
    body = body.cut(shadow(z1 + 2.0)).clean()
    cradle = body
    for side in (-1, 1):
        for a, b, lo in ((s["w_in"], s["w_out"], z1 - 0.01),
                         (s["w_out"] - 0.01, s["hook_tip"], s["face"])):
            x0, x1 = sorted((side * a, side * b))
            cradle = cradle.fuse(cq.Solid.makeBox(x1 - x0, y1 - y0, s["hook_top"] - lo,
                                                  cq.Vector(x0, y0, lo)))
    cradle = cradle.clean()
    assert cradle.isValid() and len(cradle.Solids()) == 1
    return cradle


def selftest(cradle=None):
    """The elbow drops straight in and stands clear of the cradle; both wings stand on the body."""
    cradle = cradle or build()
    elbow = cq.Compound.makeCompound(list(elbow_parts().values()))
    assert elbow.intersect(cradle).Volume() < 1e-3
    for k in range(1, 61):
        assert elbow.translate(cq.Vector(0, 0, 0.5 * k)).intersect(cradle).Volume() < 1e-3, k
    s = stations()
    half, y0, y1, z0, z1 = block()
    for side in (-1, 1):
        x0, x1 = sorted((side * s["w_in"], side * s["w_out"]))
        foot = cq.Solid.makeBox(x1 - x0, y1 - y0, 0.5, cq.Vector(x0, y0, z1 - 0.5))
        assert abs(cradle.intersect(foot).Volume() - foot.Volume()) < 1e-3
    return s


def main():
    from _cadq_export import export_assembly
    from _materials import M_PETGF_BLACK, one_body
    from flute_payload import cut
    cradle = build()
    s = selftest(cradle)
    print_shape = cradle.translate(cq.Vector(0, 0, -s["z0"]))
    step, stl = _here.parent / "elbow-cradle.step", _here.parent / "elbow-cradle.stl"
    export_assembly(one_body(cq.Workplane(obj=print_shape), "elbow-cradle", M_PETGF_BLACK),
                    str(step))
    cq.exporters.export(print_shape, str(stl), tolerance=0.05, angularTolerance=0.15)
    cut(step, stl)
    b = s["bend"]
    from docgen import substitute_md
    substitute_md(_here.parent / "README.md", variables={
        "CRADLE_SLIP": f"{SLIP:g} mm",
        "CRADLE_LENGTH": f"{s['y1'] - s['y0']:.1f} mm",
        "CRADLE_WING_T": f"{LEAF_T:g} mm",
        "CRADLE_WING_H": f"{s['hook_top'] - s['top']:.2f} mm",
        "CRADLE_HOOK": f"{s['hook_tip'] - s['w_out']:.1f} mm",
        "CRADLE_OVERLAP": f"{OVERLAP:g} mm",
        "CRADLE_CATCH": f"{CATCH_GAP:g} mm",
        "CRADLE_BEND": f"{b['hook_deflection']:.2f} mm",
        "CRADLE_LANE": f"{s['lane']:.2f} mm",
        "CRADLE_STRAIN": f"{100 * b['root_strain']:.1f}%",
        "CRADLE_TIP_GAP": f"{TIP_GAP:g} mm",
        "CRADLE_WIDTH": f"{2 * s['half']:.1f} mm",
        "CRADLE_WEB": f"{s['slot_in'] - HOLE_D / 2:.2f} mm",
    })
    print(f"-> {step.name}, {stl.name}; {cradle.Volume():.1f} mm3; wings "
          f"{s['hook_top'] - s['top']:.2f} mm, hook bends {b['hook_deflection']:.2f} mm over "
          f"{b['free_length']:.2f} mm ({100 * b['root_strain']:.1f}% nominal root strain); "
          f"lane {s['lane']:.2f} mm")


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        s = selftest()
        print(f"  the elbow drops straight in and both wings stand on the body; the hook bends "
              f"{s['bend']['hook_deflection']:.2f} mm into a {s['lane']:.2f} mm lane")
        print("elbow_cradle selftest OK")
    else:
        main()
