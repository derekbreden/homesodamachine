"""
Compressor shroud — sheet-metal cover that drops over the compressor.

A 5-sided open-bottom box: a top panel with four walls bent down from
its edges, open at the bottom so the compressor's feet sit on the
enclosure floor and the refrigerant/process stubs exit below. One flat
SendCutSend blank, bent on four sides, with the four vertical corners
left open (full corner relief in the flat).

WORLD FRAME
===========
- X: width, +X right. Interior spans X in [-65, +65] (130 mm).
- Y: depth, +Y toward the back. Interior spans Y in [-87.5, +87.5] (175 mm).
- Z: height, +Z up, Z=0 at the open bottom. Interior spans Z in [0, 150].
The "back face" is the +Y wall (130 x 150). The "left face" is the -X
wall (175 x 150). Front is -Y, right is +X.

PENETRATIONS
============
- 120 V AC pass-through: one hole in the back face, centered
  horizontally (X=0) and vertically (Z=75).
- Copper inlet + outlet: two holes in the left face, centered
  vertically (Z=75) and placed by `justify-content: space-around`
  across the full depth of the face — each hole centered in its own
  half of the depth (the quarter points).

MATERIAL / BENDS
================
0.059" G90 hot-dipped galvanized steel, SendCutSend laser-cut + bent.
Inside bend radius 0.063", K-factor 0.36 (SendCutSend's published
G90 0.059" gauge spec). The flat pattern is developed with the
matching 90-degree bend deduction so the formed interior lands on
130 x 175 x 150 mm.

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
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
from _cadq_export import export_step, export_dxf  # noqa: E402

# ── Interior envelope (the volume the shroud encloses) ──────────────
interior_width = 130.0    # X
interior_depth = 175.0    # Y
interior_height = 150.0   # Z

# ── Material — SendCutSend G90 hot-dipped galvanized, 0.059" ────────
wall_thickness = 0.059 * 25.4      # 1.4986 mm
inside_bend_radius = 0.063 * 25.4  # 1.6002 mm
k_factor = 0.36
bend_angle = 90.0

# 90-degree bend math, derived from the gauge spec above. The bend
# deduction is what shortens the flat blank so the sum of the formed
# outside dimensions returns the intended interior.
bend_allowance = math.radians(bend_angle) * (inside_bend_radius + k_factor * wall_thickness)
outside_setback = (inside_bend_radius + wall_thickness) * math.tan(math.radians(bend_angle) / 2)
bend_deduction = 2 * outside_setback - bend_allowance
setback_to_bend_line = bend_deduction / 2  # one face loses this from its outer dim to its bend line

# ── Penetrations ───────────────────────────────────────────────────
ac_hole_diameter = 0.5 * 25.4    # 12.7 mm — 1/2" AC cable pass-through
copper_tube_od = 6.35            # 1/4" OD ACR copper
copper_hole_diameter = 8.0       # clearance hole over the 1/4" tube

# Both holes sit at mid-height of the interior.
hole_center_z = interior_height / 2  # 75 mm

# space-around across the depth: each copper hole sits at the center of
# its own half of the face, i.e. at the quarter points of the depth.
copper_hole_depth_offset = interior_depth / 4

# ── Outer envelope (walls add thickness outward, top adds it upward) ─
outer_width = interior_width + 2 * wall_thickness    # X, apex-to-apex
outer_depth = interior_depth + 2 * wall_thickness    # Y, apex-to-apex
outer_height = interior_height + wall_thickness       # Z, bottom open
inner_x = interior_width / 2     # 65
inner_y = interior_depth / 2     # 87.5
outer_x = outer_width / 2        # 65 + T
outer_y = outer_depth / 2        # 87.5 + T

# ── Flat-pattern anchors ───────────────────────────────────────────
# Bend lines bound the top panel; walls develop outward from them.
top_half_u = outer_width / 2 - setback_to_bend_line   # left/right bend lines at u = -/+ this
top_half_v = outer_depth / 2 - setback_to_bend_line   # front/back bend lines at v = -/+ this
wall_develop = outer_height - setback_to_bend_line     # bend line to free edge
arm_u = top_half_u + wall_develop                      # left/right wall free edges
arm_v = top_half_v + wall_develop                      # front/back wall free edges

# Hole centers in the developed flat. A hole on a wall at interior
# height z is `z` from that wall's free edge (the straight wall length
# develops 1:1). The AC hole rides the back arm; the copper holes ride
# the left arm.
ac_flat = (0.0, arm_v - hole_center_z)
copper_flat = [
    (-arm_u + hole_center_z, -copper_hole_depth_offset),
    (-arm_u + hole_center_z, +copper_hole_depth_offset),
]

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
    """The formed shroud: open-bottom shell, radiused top bends, open
    vertical corners, three bored holes."""
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

    # Open the four vertical corners — the corner relief of the bent
    # blank, so each wall joins the box only through the top panel.
    for sx in (-1, 1):
        for sy in (-1, 1):
            post = cq.Solid.makeBox(
                wall_thickness, wall_thickness, interior_height,
                cq.Vector(sx * inner_x if sx > 0 else -outer_x,
                          sy * inner_y if sy > 0 else -outer_y,
                          0),
            )
            shroud = shroud.cut(post)

    # AC hole in the back (+Y) face.
    shroud = _cut_cylinder(shroud, (0, outer_y - wall_thickness / 2, hole_center_z),
                           (0, 1, 0), ac_hole_diameter)
    # Copper inlet + outlet in the left (-X) face.
    for dy in (-copper_hole_depth_offset, copper_hole_depth_offset):
        shroud = _cut_cylinder(shroud, (-outer_x + wall_thickness / 2, dy, hole_center_z),
                               (1, 0, 0), copper_hole_diameter)

    export_step(shroud, str(_step_path))
    return shroud


def make_dxf():
    """The flat blank: a cruciform cut outline with full corner relief,
    four dashed bend lines, three holes."""
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4  # mm
    msp = doc.modelspace()

    if "BEND" not in doc.layers:
        doc.layers.add("BEND", color=1, linetype="DASHED")

    tu, tv, au, av = top_half_u, top_half_v, arm_u, arm_v
    # Cruciform outline, CCW, starting at the right wall's front-bottom
    # corner. Eight outer corners stay sharp; the four inner corners are
    # the open corner relief.
    outline = [
        (au, -tv), (au, tv),       # right wall free edge
        (tu, tv),                  # inner corner (back-right)
        (tu, av), (-tu, av),       # back wall free edge
        (-tu, tv),                 # inner corner (back-left)
        (-au, tv), (-au, -tv),     # left wall free edge
        (-tu, -tv),                # inner corner (front-left)
        (-tu, -av), (tu, -av),     # front wall free edge
        (tu, -tv),                 # inner corner (front-right)
    ]
    msp.add_lwpolyline(outline, close=True)

    # Bend lines (dashed, own layer), each spanning its flange width.
    for line in [
        ((-tu, -tv), (-tu, tv)),   # left
        ((tu, -tv), (tu, tv)),     # right
        ((-tu, tv), (tu, tv)),     # back
        ((-tu, -tv), (tu, -tv)),   # front
    ]:
        msp.add_line(line[0], line[1], dxfattribs={"layer": "BEND"})

    # Holes.
    msp.add_circle(ac_flat, ac_hole_diameter / 2)
    for c in copper_flat:
        msp.add_circle(c, copper_hole_diameter / 2)

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
    print(f"  AC hole:         d {ac_hole_diameter:.2f} mm, back face, flat {tuple(round(v, 2) for v in ac_flat)}")
    print(f"  Copper holes:    d {copper_hole_diameter:.2f} mm x2, left face, flat "
          f"{[tuple(round(v, 2) for v in c) for c in copper_flat]}")
    print(f"-> {_step_path.name}")
    print(f"-> {_dxf_path.name}")


if __name__ == "__main__":
    main()
