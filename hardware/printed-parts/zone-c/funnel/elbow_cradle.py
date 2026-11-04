"""PET-GF cradle holding the funnel's uncut ATEU44W stem elbow under its frame.

Coordinates are local to the frame's drain hole: the origin is on the hole's axis in the frame's
flat underside, +Z up and +Y aft. The installed cradle hangs `CATCH_GAP` below
that datum. The elbow's stem points up to the silicone bowl opening and its socket aft.

The pocket adds `fits.slip` radially to the scanned profile. Its forward horizontal
following seat is retained; the aft mouth continues the largest section to a broad exit.
The opening above the axis uses a convex mouth. The body prints bottom-down. Its top
supports the lower half of the socket and bend. The stem and socket collet stand free above it.

Each X side of the block carries on up as a wing, the body's full length, through a straight slot
in the frame's bottom web. A flat hook at the wing's top reaches outward over the web to within
`TIP_GAP` of the counterbore's X wall, which sets the block's width and so how far the slots stand
off the drain hole. Going up, each wing bends inward into its slot's inboard lane until the hook
clears the slot's outer edge, then springs back over the web. The silicone plug's flat underside
rests on the two hook tops in that released pose.

The counterbore and the silicone plug are rectangles centred on the hole, the plug's width across
X. The counterbore's ±Y walls stand on the slots' farther ends, so the web carries no strip between
a slot and a wall.
"""

import functools
import hashlib
import json
import math
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
for _p in (_hw / "scripts", _hw / "printed-parts" / "cadlib",
           _hw / "reference" / "neofit-stem-elbow", _hw / "manifold-layout", _tools):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import fits                                                   # noqa: E402
import above_core as _layout                                  # noqa: E402

_stem_parameters = json.loads(
    (_hw / "reference/neofit-stem-elbow/reference-parameters.json").read_text())


WEB = 3.0              # the frame's bottom web under the socket
SLIP = fits.slip       # radial growth of the scanned pocket profile
WALL = 3.0             # block wall and floor beyond the elbow's widest section
LOWER_SIDE_RELIEF = 0.65   # air to the neighbouring Y elbows, below the wing roots
ROOT_STOCK = 3.0       # retain the full-width body under each wing
STEM_BODY_AIR = 1.0    # aft lower face off the attached NeoFit collar
HOLE_D = 11.25         # frame's stem passage
WING_ROOT_Z = -8.84    # snap flexure root, 12.89 mm below its hook bearing
SLOT_FORE_Y = -11.24   # frame's fixed wing-slot fore station
SLOT_AFT_Y = 20.56239  # frame's fixed wing-slot aft station
SOCKET_HALF = 18.3     # the counterbore's half-width, `funnel_frame.socket_width / 2`
TIP_GAP = fits.slip    # hook tip off the counterbore's X wall

LEAF_T = 1.3           # wing thickness
SIDE = 0.5             # slot's outer edge off the wing's outer face
OVERLAP = 2.6          # hook over the web past that edge
HOOK_T = 2.75          # full flat-hook thickness under the silicone bearing plane
HOOK_RISE = 0.25       # further lift the printed hooks need to clear the web
CATCH_GAP = fits.slip + fits.supported_surface + HOOK_RISE   # release travel from insertion datum
HOOK_WEB_AIR = fits.slip + fits.supported_surface   # static supported underside above the web
INSERTION_SLIP = fits.running   # hook tip inside the slot's outer edge while it passes
END_SLIP = 0.25        # slot beyond each wing end
PLUG_CORNER = 0.0      # square cast plug corners
SOCKET_CORNER = 0.25   # PET-GF receiver corners; keep static room at the flat hook tips

CORE_R = _stem_parameters['bend_radius_mm']


def _profiles(leg):
    p = _stem_parameters['profiles']
    if leg == 'y':
        return p['fixed_body_y'], p['release_collet_y']
    return sorted((-x, r) for x, r in p['stem_x']), []


def elbow_z():
    """Bend axis in the cradle's insertion frame, from the full stem and silicone bore."""
    import funnel
    return (WEB + CATCH_GAP + funnel.plug_lift + funnel.stem_engagement
            + _stem_parameters['stem_tip_x_mm'])


def block():
    """`(half_width, y0, y1, z0, z1)` of the block the pocket is cut from. Its X sides are the
    wings' outer faces, set back from the counterbore's wall by the hook and its clearances."""
    ry = max(r for _t, r in _profiles("y")[0]) + SLIP + WALL
    half = SOCKET_HALF - TIP_GAP - OVERLAP - SIDE
    stem_y = _layout.snapshot_pose('drain-outlet-stem')['translation_mm'][1]
    drain_y = _layout.specification()['fore_routes']['drain_union_corner_mm'][1]
    collar_radius = max(r for _t, r in _stem_parameters['profiles']['fixed_body_y'])
    aft = min(SLOT_AFT_Y, stem_y - drain_y - collar_radius - STEM_BODY_AIR)
    return (half, SLOT_FORE_Y, aft, elbow_z() - ry, WING_ROOT_Z)


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
    face = WEB + CATCH_GAP + HOOK_WEB_AIR
    s = {"half": half, "y0": y0, "y1": y1, "z0": z0, "top": z1, "w_in": w_in, "w_out": w_out,
         "slot_out": slot_out, "hook_tip": slot_out + OVERLAP, "face": face,
         "hook_top": face + HOOK_T}
    s["bend"] = passage(w_in, w_out, s["hook_tip"], slot_out, z1, face, s["hook_top"])
    s["lane"] = math.ceil((s["bend"]["inner_face_travel"] + fits.running) * 100) / 100
    s["slot_in"] = w_in - s["lane"]
    return s


def socket_half_length():
    """The frame's fixed counterbore boundary, beyond its existing wing slots."""
    return max(SLOT_AFT_Y + END_SLIP, -(SLOT_FORE_Y - END_SLIP))


def plug_half_length(half_width):
    """Half the plug's Y length: the counterbore's, less the plug's gap to its walls."""
    return socket_half_length() - (SOCKET_HALF - half_width)


def hook_corner_clearance(half_width):
    """How far each hook's outer +Y corner stands inside the counterbore's corner round."""
    s = stations()
    r = SOCKET_CORNER
    cx, cy = SOCKET_HALF - r, socket_half_length() - r
    return r - math.hypot(max(s["hook_tip"] - cx, 0.0), max(s["y1"] - cy, 0.0))


def _turn_profile(points):
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
    return pts


def numbers():
    """Scanned pocket, block and snap stations for the authored kernel cradle."""
    from _materials import M_PETGF_BLACK, linear
    b = block()
    s = stations()
    top = b[4] + 2.0
    h = top - elbow_z()
    zb, zc = _profiles('z')
    yb, yc = _profiles('y')
    run, reach = [], 0.0
    for station, radius in zb + zc[1:]:
        reach = max(reach, radius)
        run.append((station, reach + SLIP))
    run.append((max(h + 1.0, run[-1][0]), run[-1][1]))
    mouth_radius = max(yb[-1][1], *(r for _s, r in yc))
    horizontal = yb + [(yc[-1][0] + SLIP, mouth_radius)]
    lower, reach = [], 0.0
    for station, radius in horizontal:
        reach = max(reach, radius)
        lower.append((station - SLIP, reach + SLIP))
    plan, reach = [], 0.0
    for station, radius in horizontal:
        reach = max(reach, radius + SLIP)
        plan.append((reach, station))
    radius = CORE_R + SLIP
    tangents = []
    for index, (x, y) in enumerate(plan):
        d2 = x*x + y*y
        if d2 > radius*radius:
            a, c = radius*radius/d2, radius*math.sqrt(d2-radius*radius)/d2
            tangent = (a*x+c*y, a*y-c*x)
            tangents.append((math.atan2(tangent[1], tangent[0]), index, tangent))
    _angle, start, tangent = min(tangents)
    edge = [tangent]
    for point in plan[start:]:
        while len(edge) > 1:
            a, c = edge[-2:]
            if ((c[0]-a[0])*(point[1]-c[1]) - (c[1]-a[1])*(point[0]-c[0])) > 1e-12:
                break
            edge.pop()
        edge.append(point)
    payload = _hw/'reference/neofit-stem-elbow/neofit-stem-elbow.fine.step.mesh'
    return {
        'block': b, 'elbow_z': elbow_z(),
        'vertical_profile': _turn_profile([(0.0, run[0][1])] + run),
        'horizontal_profile': _turn_profile(lower),
        'mouth_tangent': tangent, 'mouth_chain': edge,
        'mouth_lift': max(0.0, WING_ROOT_Z-elbow_z()), 'shadow_height': h+1.0,
        'shadow_core_radius': max(CORE_R, run[0][1]-SLIP, horizontal[0][1])+SLIP,
        'lower_side_relief': LOWER_SIDE_RELIEF, 'root_stock': ROOT_STOCK,
        'wing_x': (s['w_in'], s['w_out']), 'hook_tip': s['hook_tip'],
        'hook_face': s['face'], 'hook_top': s['hook_top'], 'catch_gap': CATCH_GAP,
        'color': linear(M_PETGF_BLACK),
        'elbow_payload': 'hardware/reference/neofit-stem-elbow/neofit-stem-elbow.fine.step.mesh',
        'elbow_payload_sha256': hashlib.sha256(payload.read_bytes()).hexdigest(),
    }


def _document(s):
    b = s['bend']
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
        "CRADLE_HOOK_T": f"{HOOK_T:g} mm",
        "CRADLE_WEB_AIR": f"{HOOK_WEB_AIR:.2f} mm",
        "CRADLE_SOCKET_CORNER": f"{SOCKET_CORNER:g} mm",
        "CRADLE_WEB": f"{s['slot_in'] - HOLE_D / 2:.2f} mm",
    })


def main():
    import _rust_part
    said = _rust_part.cut('funnel', 'elbow-cradle', numbers(), _here.parent)
    _document(stations())
    print(f"-> elbow-cradle STEP, model, payload and STL; {said['bodies'][0]['volume']:.1f} mm3")


if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    if sys.argv[1:] == ["selftest"]:
        _rust_part.check('funnel', 'elbow-cradle', numbers())
        s = stations()
        print(f"  the elbow drops straight in and both wings stand on the body; the hook bends "
              f"{s['bend']['hook_deflection']:.2f} mm into a {s['lane']:.2f} mm lane")
        print("elbow_cradle selftest OK")
    else:
        main()
