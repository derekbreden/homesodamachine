"""Kitchen Edition enclosure — a PETG box sized to the placed contents, split
into two printable halves (front + back) that telescope and cross-pin together.

Dimensions follow the contents at build time: the bounding box of the parts
placed by `../enclosure-assembly/_contents.py` is computed live, padded by an
interior clearance, then walled out. Features:

  * A flat 45° display-mounting facet (a solid surface) chamfered into the
    top-front-left corner, flush to the −X edge.
  * A front↔back split: the front half's rear wall telescopes (a full-wall
    lip, nothing shaved) into the back half, and four interlocking screw
    bosses cross the seam — one in each top/bottom corner, on the ±X (left /
    right) side walls. Each boss is on an X axis: the screw drives in from the
    left/right EXTERIOR face, and the boss is tucked into the corner so it is
    part of the top/bottom (±Z) wall. The BACK half carries the PLUG (faucet
    mounting-plate idiom): a cylinder reaching inward from the corner with a
    screw clearance through it — no web tail. The FRONT half's lip carries the
    SOCKET (faucet shell-bottom idiom): a pod bored to receive the plug, open
    on its +Y face so the plug drops in as the halves close, with a ruthex M3
    heat-set at the deep end. An M3 SHCS from the ±X exterior passes through the
    plug into the heat-set, cross-pinning the two halves. The back half is
    sized so the cold core seats behind the bosses, clear.

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

# Split + boss parameters — every dimension sized to its function, nothing
# inherited from the faucet. The seam is a Y plane; the front half's full-wall
# rear lip telescopes into the back; four corner bosses cross-pin the seam with
# M3 screws from the ±X exterior. The boss itself is just the ONE WALL of
# material the shank crosses between the screw-head seat and the heat-set.
lip_len = 20.0               # telescoping engagement depth (the X/Z registration)
boss_to_coldcore = 14.0      # clear gap from the lip's +Y tip back to the cold core
split_slip = 0.40            # diametral slide fit, plug into socket bore
screw_clear_dia = 3.9        # M3 shank clearance
head_cbore_dia = 6.15        # M3 SHCS head counterbore
head_cbore_depth = 4.0       # head recess depth from the ±X exterior (the head seat)
plug_dia = screw_clear_dia + 2.0 * wall          # 9.9 — the shank + one wall each side
socket_bore_dia = plug_dia + split_slip          # 10.3 — slide fit over the plug
socket_r = socket_bore_dia / 2.0 + wall          # pod half-size: one wall around the bore
heatset_dia = 4.0            # ruthex M3 short heat-set
heatset_depth = 5.25
socket_cap = wall            # one wall capping the insert's deep end


# --- primitives -------------------------------------------------------------

def _ybox(x0, x1, y0, y1, z0, z1):
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
        .translate((x0, y0, z0))
        .val()
    )


def _xcyl(r, y, z, x0, x1):
    """Cylinder of radius r along X from x0 to x1, axis at (y, z)."""
    return cq.Solid.makeCylinder(r, abs(x1 - x0), cq.Vector(min(x0, x1), y, z), cq.Vector(1, 0, 0))


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
    # Split plane: placed so the lip's +Y tip clears the cold core by
    # boss_to_coldcore, with the full lip_len of telescoping ahead of it.
    cold_front_y = placed["foam-shell"][0].BoundingBox().ymin
    y_joint = cold_front_y - boss_to_coldcore - lip_len
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

    wedge = _halfspace(origin, normal, extent).intersect(x_slab)
    outer_chamfered = outer_box.cut(wedge)

    back_origin = (origin[0] - wall * normal[0],
                   origin[1] - wall * normal[1],
                   origin[2] - wall * normal[2])
    keepout = _halfspace(back_origin, normal, extent).intersect(x_slab)
    inner_clipped = inner_box.cut(keepout)

    return cq.Workplane(obj=outer_chamfered.cut(inner_clipped))


# --- split joint: telescoping lip + X-axis corner cross-pins ----------------
#
# Four bosses cross the seam, one in each top/bottom corner of the ±X side
# walls, centered in the telescoping overlap and COAXIAL by construction (one
# y_boss, one z_boss feed both halves). An M3 SHCS drives in from the ±X
# exterior; outboard→inboard the joint reads: head counterbore, then the BOSS —
# exactly ONE WALL of material the shank crosses — then the heat-set, then a
# one-wall cap.
#   * BACK half = PLUG: a cylinder from the ±X exterior to the heat-set, fused
#     to the side wall. Sized to the screw SHANK, not the head (the head sits in
#     the wall counterbore); screw-clearance + head counterbore bored in.
#   * FRONT lip = SOCKET: a corner pod, integral with the ±Z wall, bored to
#     receive the plug (slide fit), the heat-set + cap at the deep inboard end,
#     and a +Y channel so the plug slides in as the lip telescopes into the back.
# The head seats in the back wall; the shank crosses one wall of boss into the
# front heat-set, cross-pinning the two halves along X.

def _bosses(inner):
    """Per-boss tuple (x_in, x_ext, sx, z_boss, sz): the inner ±X wall face the
    screw passes through, its matching exterior face, sx = +1 (left) / −1
    (right) inboard, the bore-axis height (bottom one wall above the floor, top
    one wall below the ceiling), and sz = +1 (bottom) / −1 (top) for the ±Z
    wall the boss is integral with."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    zb = iz0 + wall + socket_bore_dia / 2.0   # bottom
    zt = iz1 - wall - socket_bore_dia / 2.0   # top
    return [
        (ix0, ix0 - wall, +1.0, zb, +1.0),  # bottom-left
        (ix1, ix1 + wall, -1.0, zb, +1.0),  # bottom-right
        (ix0, ix0 - wall, +1.0, zt, -1.0),  # top-left
        (ix1, ix1 + wall, -1.0, zt, -1.0),  # top-right
    ]


def _boss_x(x_ext, sx):
    """Inboard X stations from the ±X exterior, each sized to its job: the
    screw-head seat (recess), the heat-set start ONE WALL past the seat (that
    wall is the boss), the heat-set end, and the pod cap one wall past it."""
    x_seat = x_ext + sx * head_cbore_depth
    x_tip = x_seat + sx * wall
    x_heat = x_tip + sx * heatset_depth
    x_cap = x_heat + sx * socket_cap
    return x_seat, x_tip, x_heat, x_cap


def _back_plug(x_ext, sx, z_boss, y_boss):
    """BACK plug: an X cylinder from the ±X exterior to the heat-set, fused to
    the side wall — sized to the screw shank, no head, no +Y tail."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    return _xcyl(plug_dia / 2.0, y_boss, z_boss, x_ext, x_tip)


def _front_pod(x_in, x_ext, sx, z_boss, sz, y_boss, inner):
    """FRONT socket pod (solid): a corner block from the ±X wall inboard to the
    cap and from the bore out to the floor/ceiling, so it is one piece with the
    side wall and the ±Z wall. Bore / heat-set / channel are cut afterwards."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    _xs, _xt, _xh, x_cap = _boss_x(x_ext, sx)
    xa, xb = sorted((x_in, x_cap))
    za, zb = (iz0, z_boss + socket_r) if sz > 0 else (z_boss - socket_r, iz1)
    return _ybox(xa, xb, y_boss - socket_r, y_boss + socket_r, za, zb)


def _front_cuts(x_in, x_ext, sx, z_boss, y_boss, y_joint):
    """Front-socket inner cuts: the bore that receives the plug (slide fit), the
    heat-set pocket at the deep end, and a +Y channel so the plug slides into the
    bore as the lip telescopes into the back."""
    _xs, x_tip, x_heat, _xc = _boss_x(x_ext, sx)
    bore = _xcyl(socket_bore_dia / 2.0, y_boss, z_boss, x_in, x_tip)
    heat = _xcyl(heatset_dia / 2.0, y_boss, z_boss, x_tip, x_heat)
    bx0, bx1 = sorted((x_in, x_tip))
    cz0, cz1 = z_boss - socket_bore_dia / 2.0, z_boss + socket_bore_dia / 2.0
    chan = _ybox(bx0, bx1, y_boss, y_joint + lip_len + 1.0, cz0, cz1)
    return bore.fuse(heat).fuse(chan)


def _screw_cut(x_ext, sx, z_boss, y_boss):
    """M3 shank clearance from the ±X exterior through the plug to the heat-set,
    plus the SHCS head counterbore at the exterior — the seat one wall outboard
    of the heat-set."""
    _xs, x_tip, _xh, _xc = _boss_x(x_ext, sx)
    shank = _xcyl(screw_clear_dia / 2.0, y_boss, z_boss, x_ext - sx * 1.0, x_tip)
    cbore = _xcyl(head_cbore_dia / 2.0, y_boss, z_boss, x_ext - sx * 1.0, x_ext + sx * head_cbore_depth)
    return shank.fuse(cbore)


def _front_lip(inner, y_joint):
    """The front half's rear lip: a full-`wall` perimeter band whose outer face
    is flush with the body's inner wall, so it is one solid with the body —
    nothing shaved — telescoping +Y into the back half. It runs one `wall` back
    into the body cavity (a fusion shoulder / telescoping stop) and forward over
    the overlap."""
    ix0, ix1, iy0, iy1, iz0, iz1 = inner
    y0, y1 = y_joint - wall, y_joint + lip_len
    return _ybox(ix0, ix1, y0, y1, iz0, iz1).cut(
        _ybox(ix0 + wall, ix1 - wall, y0 - 1.0, y1 + 1.0, iz0 + wall, iz1 - wall)
    )


# Boss Y position — one value feeds the plug AND the socket, so they are
# coaxial by construction. Centered in the telescoping overlap.
def _y_boss(y_joint):
    return y_joint + lip_len / 2.0


def build_front_half():
    inner, outer, y_joint, _ = _dims()
    shell = _shell_with_facet(inner, outer).val()
    front = shell.intersect(_ybox(outer[0], outer[1], outer[2], y_joint, outer[4], outer[5]))
    front = front.fuse(_front_lip(inner, y_joint))
    yb = _y_boss(y_joint)
    for x_in, x_ext, sx, z_boss, sz in _bosses(inner):
        front = front.fuse(_front_pod(x_in, x_ext, sx, z_boss, sz, yb, inner))
    for x_in, x_ext, sx, z_boss, _sz in _bosses(inner):
        front = front.cut(_front_cuts(x_in, x_ext, sx, z_boss, yb, y_joint))
    return cq.Workplane(obj=front)


def build_back_half():
    inner, outer, y_joint, _ = _dims()
    shell = _shell_with_facet(inner, outer).val()
    back = shell.intersect(_ybox(outer[0], outer[1], y_joint, outer[3], outer[4], outer[5]))
    yb = _y_boss(y_joint)
    for x_in, x_ext, sx, z_boss, _sz in _bosses(inner):
        back = back.fuse(_back_plug(x_ext, sx, z_boss, yb))
    for x_in, x_ext, sx, z_boss, _sz in _bosses(inner):
        back = back.cut(_screw_cut(x_ext, sx, z_boss, yb))
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
    overlap = front.val().intersect(back.val()).Volume()
    print(f"  front ∩ back:     {overlap:.1f} mm³  ({'CLEAR slip-fit' if overlap < 5 else 'INTERFERENCE'})")
    inner, _o, y_joint, _c = _dims()
    yb = _y_boss(y_joint)
    cold = _contents.build()["foam-shell"][0]
    clash = sum(
        cold.intersect(
            _back_plug(x_ext, sx, z_boss, yb).fuse(
                _front_pod(x_in, x_ext, sx, z_boss, sz, yb, inner))
        ).Volume()
        for x_in, x_ext, sx, z_boss, sz in _bosses(inner)
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
