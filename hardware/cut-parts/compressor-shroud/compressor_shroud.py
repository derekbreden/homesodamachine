"""
Compressor shroud — sheet-metal cover that drops over the compressor.

A 5-sided open-bottom box: a top panel with four walls bent down from
its edges, open at the bottom so the compressor's feet sit on the
enclosure floor and the refrigerant/process stubs exit below. One flat
SendCutSend blank, bent on four sides, with a square bend-relief notch
at each corner so the two adjacent bends form without tearing.

WORLD FRAME
===========
- X: width, +X right. Interior spans X from -[65](INNER_X) to +[65](INNER_X) ([130](INT_W) mm).
- Y: depth, +Y toward the back. Interior spans Y from -[87.5](INNER_Y) to +[87.5](INNER_Y) ([175](INT_D) mm).
- Z: height, +Z up, Z=0 at the open bottom. Interior spans Z from 0 to [150](INT_H).
The "back face" is the +Y wall ([130](INT_W) x [150](INT_H)). The "left face" is the -X
wall ([175](INT_D) x [150](INT_H)). Front is -Y, right is +X.

PENETRATIONS
============
Each is centered vertically at Z=[75](HOLE_CENTER_Z), and each crosses the wall the body
it feeds stands against.
- Refrigerant discharge: one hole in the left (-X) face, at the far quarter point of
  the depth — the wall the condenser stands on.
- Refrigerant suction: one hole in the front (-Y) face — the wall the cold core stands
  on — [49.5](SUCTION_HOLE_X) mm right of the plan centre, on the core's west port lane.
- 120 V AC pass-through and earth bond: two holes in the right (+X) face, at the two
  quarter points of the depth, landing the mains feed and the ground bond (wiring AC-6).
- Mounting: one hole near the base of the left face and one near the
  base of the right face, fastening the shroud to the enclosure floor.

MATERIAL / BENDS
================
[0.059"](WALL_IN) G90 hot-dipped galvanized steel, SendCutSend laser-cut + bent.
Inside bend radius [0.063"](BEND_R_IN), K-factor [0.36](K_FACTOR) (SendCutSend's published
G90 [0.059"](WALL_IN) gauge spec). The flat pattern is developed with the
matching [90°](BEND_ANGLE) bend deduction so the formed interior lands on
[130](INT_W) x [175](INT_D) x [150](INT_H) mm.

FILES
=====
- compressor-shroud.step          3D formed shroud (viewer + reference)
- compressor-shroud.step.json     sidecar (wall thickness, material)
- compressor-shroud-flat.dxf      flat pattern: cut outline + holes on
                                  layer 0, bend lines dashed on a
                                  separate layer (SendCutSend upload)
- compressor-shroud-flat.dxf.json sidecar (thickness, material, process)

Units: mm. DXF $INSUNITS = 4 (millimeters).

Run: tools/cad-venv/bin/python compressor_shroud.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq
import ezdxf

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
from _cadq_export import export_step, export_dxf  # noqa: E402

sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
from docgen import substitute_py_comments  # noqa: E402

# Geometry scalars are owned by the dimensions driver (single source,
# also read by the assembly doc-sync drivers). This file builds from them.
sys.path.insert(0, str(_here.parent))
from _compressor_shroud_dimensions import (  # noqa: E402
    interior_width_mm as interior_width,
    interior_depth_mm as interior_depth,
    interior_height_mm as interior_height,
    wall_thickness_mm as wall_thickness,
    wall_thickness_in,
    inside_bend_radius_mm as inside_bend_radius,
    inside_bend_radius_in,
    k_factor,
    bend_angle_deg as bend_angle,
    ac_hole_diameter_mm as ac_hole_diameter,
    copper_hole_diameter_mm as copper_hole_diameter,
    chassis_ground_hole_mm as bond_hole_diameter,
    mounting_hole_diameter_mm as mounting_hole_diameter,
)

# [90°](BEND_ANGLE) bend math, derived from the gauge spec. The bend deduction
# is what shortens the flat blank so the sum of the formed outside
# dimensions returns the intended interior.
bend_allowance = math.radians(bend_angle) * (inside_bend_radius + k_factor * wall_thickness)
outside_setback = (inside_bend_radius + wall_thickness) * math.tan(math.radians(bend_angle) / 2)
bend_deduction = 2 * outside_setback - bend_allowance
setback_to_bend_line = bend_deduction / 2  # one face loses this from its outer dim to its bend line

# ── Bend relief (sendcutsend.com/faq/what-are-your-bend-relief-requirements) ──
# Where two bends meet at a corner each needs a notch past the bend line:
# depth >= bend radius + thickness + 0.020", width >= 50% of thickness. A
# square notch centered on the corner's bend-line intersection gives each
# of the two bends that depth (its half-size) and far exceeds the width min.
bend_relief_min_depth = inside_bend_radius + wall_thickness + 0.020 * 25.4  # [3.607 mm](BEND_RELIEF_MIN_DEPTH)
corner_relief = bend_relief_min_depth + 1.0  # half-size; margin over the SCS minimum

# Both holes sit at mid-height of the interior.
hole_center_z = interior_height / 2  # [75](HOLE_CENTER_Z) mm

# space-around across the depth: each copper hole sits at the center of
# its own half of the face, i.e. at the quarter points of the depth.
copper_hole_depth_offset = interior_depth / 4

# ── Outer envelope (walls add thickness outward, top adds it upward) ─
outer_width = interior_width + 2 * wall_thickness    # X, apex-to-apex
outer_depth = interior_depth + 2 * wall_thickness    # Y, apex-to-apex
outer_height = interior_height + wall_thickness       # Z, bottom open
inner_x = interior_width / 2     # [65](INNER_X)
inner_y = interior_depth / 2     # [87.5](INNER_Y)
outer_x = outer_width / 2        # 65 + T
outer_y = outer_depth / 2        # 87.5 + T

# ── Flat-pattern anchors ───────────────────────────────────────────
# Bend lines bound the top panel; walls develop outward from them.
top_half_u = outer_width / 2 - setback_to_bend_line   # left/right bend lines at u = -/+ this
top_half_v = outer_depth / 2 - setback_to_bend_line   # front/back bend lines at v = -/+ this
wall_develop = outer_height - setback_to_bend_line     # bend line to free edge
arm_u = top_half_u + wall_develop                      # left/right wall free edges
arm_v = top_half_v + wall_develop                      # front/back wall free edges

# Hole centers in the developed flat. A hole on a wall at interior height z is `z` from that
# wall's free edge (the straight wall length develops 1:1) — `flat()` is that reading, taken
# off the station itself. The mounting holes ride the left and right arms.
mounting_hole_z = 15.0   # near the base of the side walls
# Where the suction stub crosses the front wall, off the shroud's own plan centre. The machine
# lands this station on the cold core's WEST port lane, and the evaporator's outlet stands on
# the same point from the other side of the plane between them
# (`_contents.refrigerant_joints`, which measures the pair at every build).
suction_hole_x = 49.5
mounting_flat = [
    (-arm_u + mounting_hole_z, 0.0),   # left wall
    (arm_u - mounting_hole_z, 0.0),    # right wall
]

# ── Stations, in the shroud's own frame ─────────────────────────────
# The four penetrations a line arrives at, each on the OUTER surface of the wall it crosses
# and looking out of it. The two copper stubs take DIFFERENT walls, because the machine mates
# a different body against each: the DISCHARGE crosses the left (−X) wall the condenser stands
# against, and the SUCTION the front (−Y) wall the cold core does
# (`/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py`). Each stands on the
# station its neighbour's own pick stands on, so the joint is made up across the plane between
# the two bodies and no copper is drawn outside either. The AC gland and the earth stud share
# the right (+X) wall, the one this machine leaves open down the west flank.
STATIONS = {
    "refrig-discharge": ((-outer_x, +copper_hole_depth_offset, hole_center_z), (-1.0, 0.0, 0.0)),
    "refrig-suction":   ((suction_hole_x, -outer_y, hole_center_z), (0.0, -1.0, 0.0)),
    "ac-mains":         ((outer_x, -copper_hole_depth_offset, hole_center_z), (1.0, 0.0, 0.0)),
    "earth-bond":       ((outer_x, +copper_hole_depth_offset, hole_center_z), (1.0, 0.0, 0.0)),
}


def port(name):
    """One penetration: `(position, outward axis)` in the shroud's own frame."""
    if name not in STATIONS:
        raise KeyError(f"no station {name!r} (have: {', '.join(STATIONS)})")
    return STATIONS[name]


def flat(name):
    """One station's centre in the developed blank. A wall develops 1:1 off its own bend line,
    so a hole at interior height `z` lands `z` in from that wall's free edge and keeps the
    other plan coordinate it had."""
    (px, py, _pz), axis = port(name)
    reach = arm_u if axis[0] else arm_v
    edge = reach - hole_center_z
    if axis[0]:
        return (edge * (1.0 if axis[0] > 0 else -1.0), py)
    return (px, edge * (1.0 if axis[1] > 0 else -1.0))


# What each station's bore is, so the formed shroud and the flat blank take one list.
HOLE_DIA = {
    "refrig-discharge": copper_hole_diameter,
    "refrig-suction":   copper_hole_diameter,
    "ac-mains":         ac_hole_diameter,
    "earth-bond":       bond_hole_diameter,
}

_out_dir = _here.parent
_step_path = _out_dir / "compressor-shroud.step"
_dxf_path = _out_dir / "compressor-shroud-flat.dxf"


def _cut_cylinder(solid, center, axis, diameter):
    """Bore a through-hole: a cylinder of `diameter` centered on
    `center`, axis along `axis`, long enough to clear the wall."""
    r = diameter / 2
    length = wall_thickness + 4
    base = cq.Vector(*center) - cq.Vector(*axis).normalized().multiply(length / 2)
    cyl = cq.Solid.makeCylinder(r, length, base, cq.Vector(*axis))
    return solid.cut(cyl)


def make_step():
    """The formed shroud: open-bottom shell, radiused top bends, corner
    relief (seam up each vertical corner + a notch where two bends meet),
    three bored holes."""
    shroud = (
        cq.Workplane("XY")
        .box(outer_width, outer_depth, outer_height, centered=(True, True, False))
        .faces("<Z")
        .shell(-wall_thickness)
    )

    # Round the four top bends: inside radius R, outside radius R+T,
    # concentric so the wall keeps constant thickness through the bend.
    def _top_edges(z):
        return [
            e for e in shroud.edges().vals()
            if e.BoundingBox().zlen < 1e-3 and abs(e.Center().z - z) < 1e-2
        ]

    shroud = shroud.newObject(_top_edges(interior_height)).fillet(inside_bend_radius)
    shroud = shroud.newObject(_top_edges(outer_height)).fillet(inside_bend_radius + wall_thickness)

    # Corner relief of the bent blank: a thin open seam up each vertical
    # corner (the two perpendicular walls never join) and a wider notch at
    # the top where the two bends meet — the formed counterpart of the
    # flat's corner relief squares.
    cr = corner_relief
    for sx in (-1, 1):
        for sy in (-1, 1):
            seam = cq.Solid.makeBox(
                wall_thickness, wall_thickness, interior_height,
                cq.Vector(sx * inner_x if sx > 0 else -outer_x,
                          sy * inner_y if sy > 0 else -outer_y,
                          0),
            )
            notch = cq.Solid.makeBox(
                wall_thickness + cr + 1, wall_thickness + cr + 1, wall_thickness + cr + 1,
                cq.Vector(inner_x - cr if sx > 0 else -outer_x - 1,
                          inner_y - cr if sy > 0 else -outer_y - 1,
                          interior_height - cr),
            )
            shroud = shroud.cut(seam).cut(notch)

    # The three line penetrations, each bored on its own station's centre, half a wall
    # thickness in from the outer face the station stands on.
    for name, dia in HOLE_DIA.items():
        (px, py, pz), axis = port(name)
        inward = tuple(-a * wall_thickness / 2 for a in axis)
        shroud = _cut_cylinder(shroud, (px + inward[0], py + inward[1], pz + inward[2]),
                               tuple(abs(a) for a in axis), dia)
    # Mounting holes near the base of the left (-X) and right (+X) faces.
    shroud = _cut_cylinder(shroud, (-outer_x + wall_thickness / 2, 0, mounting_hole_z),
                           (1, 0, 0), mounting_hole_diameter)
    shroud = _cut_cylinder(shroud, (outer_x - wall_thickness / 2, 0, mounting_hole_z),
                           (1, 0, 0), mounting_hole_diameter)

    export_step(shroud, str(_step_path))
    return shroud


def make_dxf():
    """The flat blank: a cruciform cut outline with a square bend-relief
    notch at each corner, four dashed bend lines, three holes."""
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4  # mm
    msp = doc.modelspace()

    if "BEND" not in doc.layers:
        doc.layers.add("BEND", color=1, linetype="DASHED")

    tu, tv, au, av, h = top_half_u, top_half_v, arm_u, arm_v, corner_relief
    # Cruciform outline, CCW from the right wall's bottom-front corner.
    # Each inner corner is a square relief notch (half-size h) centered on
    # the bend-line intersection, biting `h` past both bends into the base.
    outline = [
        (au, -tv), (au, tv),                                          # right wall free edge
        (tu + h, tv), (tu + h, tv - h), (tu - h, tv - h),             # back-right relief
        (tu - h, tv + h), (tu, tv + h),
        (tu, av), (-tu, av),                                          # back wall free edge
        (-tu, tv + h), (-tu + h, tv + h), (-tu + h, tv - h),          # back-left relief
        (-tu - h, tv - h), (-tu - h, tv),
        (-au, tv), (-au, -tv),                                        # left wall free edge
        (-tu - h, -tv), (-tu - h, -tv + h), (-tu + h, -tv + h),       # front-left relief
        (-tu + h, -tv - h), (-tu, -tv - h),
        (-tu, -av), (tu, -av),                                        # front wall free edge
        (tu, -tv - h), (tu - h, -tv - h), (tu - h, -tv + h),          # front-right relief
        (tu + h, -tv + h), (tu + h, -tv),
    ]
    msp.add_lwpolyline(outline, close=True)

    # Bend lines (dashed, own layer), each spanning its flange between the
    # two corner reliefs.
    span_u, span_v = tu - h, tv - h
    for line in [
        ((-tu, -span_v), (-tu, span_v)),   # left
        ((tu, -span_v), (tu, span_v)),     # right
        ((-span_u, tv), (span_u, tv)),     # back
        ((-span_u, -tv), (span_u, -tv)),   # front
    ]:
        msp.add_line(line[0], line[1], dxfattribs={"layer": "BEND"})

    # Holes.
    for name, dia in HOLE_DIA.items():
        msp.add_circle(flat(name), dia / 2)
    for c in mounting_flat:
        msp.add_circle(c, mounting_hole_diameter / 2)

    export_dxf(doc, str(_dxf_path))
    return doc


def write_sidecars():
    import json

    material = 'G90 galvanized steel'
    notes = '0.059" (16 ga) G90 hot-dipped galvanized, SendCutSend laser-cut + bent'
    (_out_dir / "compressor-shroud.step.json").write_text(json.dumps({
        "thickness_mm": round(wall_thickness, 3),
        "material": material,
        "process": "laser-cut + bent",
        "notes": notes,
    }, indent=2) + "\n")
    (_out_dir / "compressor-shroud-flat.dxf.json").write_text(json.dumps({
        "thickness_mm": round(wall_thickness, 3),
        "material": material,
        "process": "laser-cut + bent",
        "notes": notes,
    }, indent=2) + "\n")


def main():
    make_step()
    make_dxf()
    write_sidecars()

    print("Compressor shroud — 5-sided open-bottom box")
    print(f"  Interior:        {interior_width:g} (W) x {interior_depth:g} (D) x {interior_height:g} (H) mm")
    print(f"  Outer:           {outer_width:.2f} x {outer_depth:.2f} x {outer_height:.2f} mm")
    print(f"  Material:        0.059\" G90 galvanized ({wall_thickness:.3f} mm), R={inside_bend_radius:.3f} mm, K={k_factor}")
    print(f"  Bend deduction:  {bend_deduction:.3f} mm @ 90 deg (allowance {bend_allowance:.3f} mm)")
    print(f"  Flat blank:      {2 * arm_u:.2f} x {2 * arm_v:.2f} mm  ({2 * arm_u / 25.4:.2f}\" x {2 * arm_v / 25.4:.2f}\")")
    for name, dia in HOLE_DIA.items():
        print(f"  {name:16} d {dia:.2f} mm, flat {tuple(round(v, 2) for v in flat(name))}")
    print(f"  Mounting holes:  d {mounting_hole_diameter:.2f} mm x2, side walls, flat "
          f"{[tuple(round(v, 2) for v in c) for c in mounting_flat]}")
    print(f"-> {_step_path.name}")
    print(f"-> {_dxf_path.name}")

    variables = {
        "INT_W": f"{interior_width:g}",
        "INT_D": f"{interior_depth:g}",
        "INT_H": f"{interior_height:g}",
        "INNER_X": f"{inner_x:g}",
        "INNER_Y": f"{inner_y:g}",
        "HOLE_CENTER_Z": f"{hole_center_z:g}",
        "WALL_IN": f'{wall_thickness_in:.4g}"',
        "BEND_R_IN": f'{inside_bend_radius_in:.4g}"',
        "K_FACTOR": f"{k_factor:.4g}",
        "BEND_ANGLE": f"{bend_angle:.4g}°",
        "BEND_RELIEF_MIN_DEPTH": f"{bend_relief_min_depth:.4g} mm",
        "SUCTION_HOLE_X": f"{suction_hole_x:g}",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "INT_W": 3,
            "INT_D": 3,
            "INT_H": 4,
            "INNER_X": 3,
            "INNER_Y": 3,
            "HOLE_CENTER_Z": 2,
            "SUCTION_HOLE_X": 1,
            "WALL_IN": 2,
            "BEND_R_IN": 1,
            "K_FACTOR": 1,
            "BEND_ANGLE": 2,
            "BEND_RELIEF_MIN_DEPTH": 1,
        },
    )


if __name__ == "__main__":
    main()
