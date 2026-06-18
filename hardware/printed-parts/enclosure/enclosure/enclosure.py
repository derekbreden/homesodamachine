"""Kitchen Edition enclosure — a PETG box sized to the placed contents, split
into two printable halves (front + back) that telescope and screw together.

Dimensions follow the contents at build time: the bounding box of the parts
placed by `../enclosure-assembly/_contents.py` is computed live, padded by an
interior clearance, then walled out. Features:

  * A flat 45° display-mounting facet (a solid surface) chamfered into the
    top-front-left corner, flush to the −X edge.
  * A front↔back split: the front half's rear wall telescopes into the back
    half, and four interlocking screw bosses (one at each top/bottom corner of
    the ±X side walls) fasten the two. The FRONT boss is a socket with a
    ruthex M3 heat-set insert; the BACK boss is a plug carrying an M3 SHCS that
    slides into the socket along +Y — the faucet base-pod idiom (see
    `faucet/touch-flo-shell` base pods + `faucet/touch-flo-mounting-plate`).
    The back half is sized so the cold core seats behind the bosses, clear.

main() exports the two printable halves (enclosure-front.step,
enclosure-back.step) plus enclosure.step — the two halves as separate solids
in assembled position, seams intact (mirrors `touch_flo_shell.py`).
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "enclosure" / "enclosure-assembly"))
from _cadq_export import export_step, export_assembly
from docgen import substitute_md, substitute_py_comments
import _contents

# Shell parameters.
wall = 3.0                  # PETG wall thickness
interior_clearance = 0.0    # gap between contents bbox and inner wall

# H2C left-nozzle build envelope; each printed HALF must fit inside this.
H2C_X, H2C_Y, H2C_Z = 325.0, 320.0, 320.0

# Display-mounting facet — a flat 45° SOLID surface chamfered into the
# top-front-left corner for the Waveshare ESP32-S3-Touch-LCD-4.3B config
# display (../../../reference/waveshare-43b-display/, bezel 112.5 × 75 mm),
# facing up-and-forward (−Y front / +Z up) toward the standing user. Sized to
# the bezel + a 3 mm buffer all around: [118.5 mm](DISPLAY_FACET_X) (X,
# lateral) × [81 mm](DISPLAY_FACET_SLOPE) (along the 45° slope). Flush to the
# −X (left) edge, so the whole top-front-left corner comes off.
display_bezel_x = 112.5
display_bezel_slope = 75.0
display_facet_buffer = 3.0
display_facet_x = display_bezel_x + 2 * display_facet_buffer          # [118.5 mm](DISPLAY_FACET_X)
display_facet_slope = display_bezel_slope + 2 * display_facet_buffer  # [81 mm](DISPLAY_FACET_SLOPE)
display_facet_angle_deg = 45.0

# Split + interlocking-boss parameters (faucet base-pod fastener chain).
split_slip = 0.40            # diametral plug↔socket / lip slip fit
boss_overlap = 18.0          # plug engagement = socket bore depth (mm along Y)
lip_len = boss_overlap       # front-wall lip telescoped into the back
plug_stem_len = 8.0          # plug→back-wall web length beyond the socket
boss_to_coldcore = 14.0      # gap from the joint plane back to the cold core
plug_dia = 12.15             # back plug OD (mounting-plate boss)
socket_bore_dia = plug_dia + split_slip          # 12.55 — front socket bore
boss_wall = 3.0              # socket wall around the bore
socket_od = socket_bore_dia + 2 * boss_wall      # 18.55 — front socket OD
heatset_dia = 4.0            # ruthex M3 short heat-set pocket
heatset_depth = 5.25
screw_clear_dia = 3.9        # M3 shank clearance through the plug
head_cbore_dia = 6.15        # M3 SHCS head counterbore
head_cbore_depth = 4.0
boss_off = socket_od / 2.0 + 2.0   # boss center inset from the inner wall


# --- primitives -------------------------------------------------------------

def _ybox(x0, x1, y0, y1, z0, z1):
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
        .translate((x0, y0, z0))
        .val()
    )


def _ycyl(r, cx, cz, y0, y1):
    """Cylinder of radius r along +Y from y0 to y1, axis at (cx, cz)."""
    return cq.Solid.makeCylinder(r, y1 - y0, cq.Vector(cx, y0, cz), cq.Vector(0, 1, 0))


# --- box dimensions, driven by the placed contents -------------------------

def _dims():
    placed = _contents.build()
    bbs = [s.BoundingBox() for s, _c in placed.values()]
    cxmin = min(b.xmin for b in bbs); cxmax = max(b.xmax for b in bbs)
    cymin = min(b.ymin for b in bbs); cymax = max(b.ymax for b in bbs)
    czmin = min(b.zmin for b in bbs); czmax = max(b.zmax for b in bbs)
    ix0, ix1 = cxmin - interior_clearance, cxmax + interior_clearance
    iy0, iy1 = cymin - interior_clearance, cymax + interior_clearance
    iz0, iz1 = czmin - interior_clearance, czmax + interior_clearance
    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz0, oz1 = iz0 - wall, iz1 + wall
    # Split plane: the cold core's −Y front face sets the back-half depth; the
    # joint sits boss_overlap + boss_to_coldcore forward of it so the bosses
    # land in the clear gap ahead of the cold core.
    cold_front_y = placed["foam-shell"][0].BoundingBox().ymin
    y_joint = cold_front_y - boss_overlap - boss_to_coldcore
    inner = (ix0, ix1, iy0, iy1, iz0, iz1)
    outer = (ox0, ox1, oy0, oy1, oz0, oz1)
    return inner, outer, y_joint, cold_front_y


# --- display facet (solid surface) -----------------------------------------

def _facet_geom(outer):
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    a = math.radians(display_facet_angle_deg)
    dy = display_facet_slope * math.sin(a)   # back from the front face
    dz = display_facet_slope * math.cos(a)   # down from the top face
    normal = (0.0, -math.sin(a), math.cos(a))
    origin = (0.0, oy0 + dy / 2.0, oz1 - dz / 2.0)
    return a, normal, origin, dy, dz


def _halfspace(origin, normal, extent):
    """Solid filling the +normal side of the plane through origin."""
    plane = cq.Plane(origin=cq.Vector(*origin), xDir=cq.Vector(1, 0, 0), normal=cq.Vector(*normal))
    return cq.Workplane(plane).rect(4 * extent, 4 * extent).extrude(extent).val()


def _facet_x_slab(outer, extent):
    """The facet's lateral window: flush to the −X edge, display_facet_x wide."""
    ox0 = outer[0]
    return _ybox(ox0, ox0 + display_facet_x, -2 * extent, 2 * extent, -2 * extent, 2 * extent)


def _shell_with_facet(inner, outer):
    """Hollow box with the 45° facet as a SOLID `wall`-thick surface: chamfer
    the outer box, and hold the cavity one wall back from the facet plane."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    a, normal, origin, dy, dz = _facet_geom(outer)
    extent = max(ox1 - ox0, oy1 - oy0, oz1 - oz0) + 100.0

    outer_box = _ybox(ox0, ox1, oy0, oy1, oz0, oz1)
    inner_box = _ybox(ix0, ix1, iy0, iy1, iz0, iz1)
    x_slab = _facet_x_slab(outer, extent)

    # Wedge that chamfers the outer corner, within the facet window.
    wedge = _halfspace(origin, normal, extent).intersect(x_slab)
    outer_chamfered = outer_box.cut(wedge)

    # Keep the cavity one wall behind the facet plane, within the window, so the
    # facet is a solid wall rather than an opening into the cavity.
    back_origin = (origin[0] - wall * normal[0],
                   origin[1] - wall * normal[1],
                   origin[2] - wall * normal[2])
    keepout = _halfspace(back_origin, normal, extent).intersect(x_slab)
    inner_clipped = inner_box.cut(keepout)

    return cq.Workplane(obj=outer_chamfered.cut(inner_clipped))


# --- interlocking bosses ----------------------------------------------------

def _boss_centers(inner):
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    return [
        (ix0 + boss_off, iz1 - boss_off, ix0 - wall),  # left-top   (wall at ox0)
        (ix0 + boss_off, iz0 + boss_off, ix0 - wall),  # left-bottom
        (ix1 - boss_off, iz1 - boss_off, ix1 + wall),  # right-top  (wall at ox1)
        (ix1 - boss_off, iz0 + boss_off, ix1 + wall),  # right-bottom
    ]


def _web(cx, cz, wall_x, y0, y1, half):
    """Box web tying a boss at (cx, cz) out to its side wall over [y0, y1]."""
    x0, x1 = sorted((cx, wall_x))
    return _ybox(x0, x1, y0, y1, cz - half, cz + half)


def _socket_pod(cx, cz, wall_x, y_joint):
    """FRONT socket: a pod from the front body out to the overlap end, webbed
    to its side wall over the front-body span only (the overlap end is a free
    tube the back plug slides into)."""
    r = socket_od / 2.0
    y0 = y_joint - heatset_depth - 2.0
    y1 = y_joint + boss_overlap
    pod = _ycyl(r, cx, cz, y0, y1)
    web = _web(cx, cz, wall_x, y0, y_joint, r)
    return pod.fuse(web)


def _socket_cut(cx, cz, y_joint):
    """Bore (open +Y, receives the plug) + heat-set pocket at the −Y deep end."""
    bore = _ycyl(socket_bore_dia / 2.0, cx, cz, y_joint, y_joint + boss_overlap + 1.0)
    heat = _ycyl(heatset_dia / 2.0, cx, cz, y_joint - heatset_depth, y_joint)
    return bore.fuse(heat)


def _plug_pod(cx, cz, wall_x, y_joint):
    """BACK plug: a cylinder that slides −Y into the front socket, plus a web
    tying it out to the side wall in the back body (beyond the socket)."""
    plug = _ycyl(plug_dia / 2.0, cx, cz, y_joint, y_joint + boss_overlap)
    y_stem = y_joint + boss_overlap + plug_stem_len
    stem = _ycyl(socket_od / 2.0, cx, cz, y_joint + boss_overlap, y_stem)
    web = _web(cx, cz, wall_x, y_joint + boss_overlap, y_stem, socket_od / 2.0)
    return plug.fuse(stem).fuse(web)


def _plug_cut(cx, cz, y_joint):
    """M3 shank clearance through the plug + a head counterbore at the +Y
    (back) end, reachable from inside the back half."""
    y_back = y_joint + boss_overlap + plug_stem_len
    clear = _ycyl(screw_clear_dia / 2.0, cx, cz, y_joint - 1.0, y_back + 0.1)
    cbore = _ycyl(head_cbore_dia / 2.0, cx, cz, y_back - head_cbore_depth, y_back + 0.1)
    return clear.fuse(cbore)


# --- the two halves ---------------------------------------------------------

def _front_lip(inner, outer, y_joint):
    """The front half's rear lip: the INNER half of the perimeter wall,
    extended +Y over the overlap, telescoping inside the back half."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    lap = wall / 2.0
    shell = _ybox(ox0, ox1, y_joint, y_joint + lip_len, oz0, oz1).cut(
        _ybox(ix0, ix1, y_joint - 1, y_joint + lip_len + 1, iz0, iz1)
    )
    # Keep only the inner (lap − slip) of the wall — the outer lap+slip is the
    # back half's to keep, with the slip as clearance.
    inner_keep = _ybox(ox0 + lap + split_slip, ox1 - lap - split_slip,
                       y_joint - 1, y_joint + lip_len + 1,
                       oz0 + lap + split_slip, oz1 - lap - split_slip)
    return shell.intersect(inner_keep)


def build_front_half():
    inner, outer, y_joint, _ = _dims()
    shell = _shell_with_facet(inner, outer).val()
    front = shell.intersect(_ybox(outer[0], outer[1], outer[2], y_joint, outer[4], outer[5]))
    front = front.fuse(_front_lip(inner, outer, y_joint))
    for cx, cz, wall_x in _boss_centers(inner):
        front = front.fuse(_socket_pod(cx, cz, wall_x, y_joint))
    for cx, cz, _wall_x in _boss_centers(inner):
        front = front.cut(_socket_cut(cx, cz, y_joint))
    return cq.Workplane(obj=front)


def build_back_half():
    inner, outer, y_joint, _ = _dims()
    shell = _shell_with_facet(inner, outer).val()
    back = shell.intersect(_ybox(outer[0], outer[1], y_joint, outer[3], outer[4], outer[5]))
    # Open the back's inner-half wall over the overlap to receive the front lip.
    lap = wall / 2.0
    back = back.cut(_ybox(outer[0] + lap, outer[1] - lap, y_joint - 0.1, y_joint + lip_len + 0.1,
                          outer[4] + lap, outer[5] - lap))
    for cx, cz, wall_x in _boss_centers(inner):
        back = back.fuse(_plug_pod(cx, cz, wall_x, y_joint))
    for cx, cz, _wall_x in _boss_centers(inner):
        back = back.cut(_plug_cut(cx, cz, y_joint))
    return cq.Workplane(obj=back)


# --- reporting --------------------------------------------------------------

def _report_facet(half):
    a = math.radians(display_facet_angle_deg)
    target = cq.Vector(0.0, -math.sin(a), math.cos(a))
    boxes = []
    for f in half.val().Faces():
        try:
            n = f.normalAt()
        except Exception:
            continue
        if (n - target).Length < 1e-3:
            boxes.append(f.BoundingBox())
    if not boxes:
        print("  display facet:    NOT FOUND")
        return
    xspan = max(b.xmax for b in boxes) - min(b.xmin for b in boxes)
    slope = (max(b.ymax for b in boxes) - min(b.ymin for b in boxes)) / math.sin(a)
    print(f"  display facet:    {xspan:.1f} mm wide (X) × {slope:.1f} mm slope, solid surface "
          f"(target {display_facet_x:g} × {display_facet_slope:g})")


def _report_split(front, back):
    fb = front.val().BoundingBox()
    bb = back.val().BoundingBox()
    print(f"  front half:       Y[{fb.ymin:.0f}, {fb.ymax:.0f}] = {fb.ylen:.0f} mm  "
          f"({fb.xlen:.0f}×{fb.zlen:.0f} face)")
    print(f"  back half:        Y[{bb.ymin:.0f}, {bb.ymax:.0f}] = {bb.ylen:.0f} mm  "
          f"({bb.xlen:.0f}×{bb.zlen:.0f} face)")
    for tag, h in (("front", front), ("back", back)):
        b = h.val().BoundingBox()
        fits = b.xlen <= H2C_X + 1 and b.ylen <= H2C_Y + 1 and b.zlen <= H2C_Z + 1
        print(f"  {tag} fits H2C bed: {fits}")
    # Cold core must miss every back-half plug boss.
    placed = _contents.build()
    cold = placed["foam-shell"][0]
    inner, outer, y_joint, cold_front = _dims()
    clash = sum(
        cold.intersect(_plug_pod(cx, cz, wx, y_joint).fuse(_socket_pod(cx, cz, wx, y_joint))).Volume()
        for cx, cz, wx in _boss_centers(inner)
    )
    print(f"  cold core vs bosses: {clash:.1f} mm³ overlap  ({'CLEAR' if clash < 1 else 'CLASH'})")


def main():
    front = build_front_half()
    back = build_back_half()

    assy = cq.Assembly(name="enclosure")
    assy.add(front, name="enclosure_front", color=cq.Color(0.80, 0.84, 0.90))
    assy.add(back, name="enclosure_back", color=cq.Color(0.70, 0.74, 0.82))

    export_step(front, str(_here.parent / "enclosure-front.step"))
    export_step(back, str(_here.parent / "enclosure-back.step"))
    export_assembly(assy, str(_here.parent / "enclosure.step"))
    print("-> enclosure-front.step")
    print("-> enclosure-back.step")
    print("-> enclosure.step (assembled halves)")
    _report_facet(front)
    _report_split(front, back)

    variables = {
        "DISPLAY_FACET_X": f"{display_facet_x:.4g} mm",
        "DISPLAY_FACET_SLOPE": f"{display_facet_slope:.4g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={"DISPLAY_FACET_X": 2, "DISPLAY_FACET_SLOPE": 2},
    )
    substitute_md(
        _here.parent / "README.md",
        variables=variables,
        expected_counts={"DISPLAY_FACET_X": 1, "DISPLAY_FACET_SLOPE": 1},
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
