"""Kitchen Edition enclosure shell — a six-walled PETG box sized to the
placed contents, sized to fit the H2C left-nozzle build envelope.

Dimensions follow the contents at build time: the bounding box of the parts
placed by `../enclosure-assembly/_contents.py` is computed live, padded by an
interior clearance, then walled out. Six closed walls, plus a 45° display
facet chamfered into the top-front-left corner; no other penetrations modelled.
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
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments
import _contents

# Shell parameters.
wall = 3.0                  # PETG wall thickness
interior_clearance = 0.0    # gap between contents bbox and inner wall

# H2C left-nozzle build envelope; the shell's outer must fit inside this.
H2C_X, H2C_Y, H2C_Z = 325.0, 320.0, 320.0

# Display-mounting facet — a flat 45° surface chamfered into the top-front-left
# corner for the Waveshare ESP32-S3-Touch-LCD-4.3B config display
# (../../../reference/waveshare-43b-display/, bezel 112.5 × 75 mm), facing
# up-and-forward (−Y front / +Z up) toward the standing user. Sized to the
# bezel + a 3 mm buffer all around: [118.5 mm](DISPLAY_FACET_X) (X, lateral) ×
# [81 mm](DISPLAY_FACET_SLOPE) (along the 45° slope). Front is −Y, top is +Z, left
# is −X.
display_bezel_x = 112.5
display_bezel_slope = 75.0
display_facet_buffer = 3.0
display_facet_x = display_bezel_x + 2 * display_facet_buffer          # [118.5 mm](DISPLAY_FACET_X)
display_facet_slope = display_bezel_slope + 2 * display_facet_buffer  # [81 mm](DISPLAY_FACET_SLOPE)
display_facet_angle_deg = 45.0
display_facet_x_margin = 10.0   # facet's left edge inboard of the −X (left) outer edge


def build_display_facet_cutter(outer):
    """Wedge that chamfers the top-front-left corner into a flat 45° facet
    (display_facet_x × display_facet_slope) facing −Y/+Z — the display mount.
    The facet runs from the top face (+Z) down to the front face (−Y) over a
    display_facet_x-wide window inboard of the −X (left) outer edge."""
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    a = math.radians(display_facet_angle_deg)
    # The 45° face's slope length projects to dy back from the front face and
    # dz down from the top face.
    dy = display_facet_slope * math.sin(a)
    dz = display_facet_slope * math.cos(a)

    # Facet plane: through the front-bottom edge (y=oy0, z=oz1−dz) and the
    # top-back edge (y=oy0+dy, z=oz1); outward normal points up-and-forward.
    normal = (0.0, -math.sin(a), math.cos(a))
    origin = (0.0, oy0 + dy / 2.0, oz1 - dz / 2.0)
    plane = cq.Plane(origin=cq.Vector(*origin), xDir=cq.Vector(1, 0, 0), normal=cq.Vector(*normal))
    extent = max(ox1 - ox0, oy1 - oy0, oz1 - oz0) + 100.0
    # Half-space on the +normal side (the top-front corner wedge to remove).
    halfspace = cq.Workplane(plane).rect(4 * extent, 4 * extent).extrude(extent)

    # Constrain the chamfer to the facet's lateral window at the −X edge.
    facet_x0 = ox0 + display_facet_x_margin
    x_slab = (
        cq.Workplane("XY")
        .box(display_facet_x, 4 * extent, 4 * extent, centered=(False, True, True))
        .translate((facet_x0, 0.0, 0.0))
    )
    return halfspace.intersect(x_slab)


def _contents_bbox():
    """Combined bounding box of the placed contents, built in-process from
    ../enclosure-assembly/_contents.py — no serialized contents STEP."""
    placed = _contents.build()
    bbs = [shape.BoundingBox() for shape, _color in placed.values()]
    return (
        min(b.xmin for b in bbs), max(b.xmax for b in bbs),
        min(b.ymin for b in bbs), max(b.ymax for b in bbs),
        min(b.zmin for b in bbs), max(b.zmax for b in bbs),
    )


def build_enclosure():
    cxmin, cxmax, cymin, cymax, czmin, czmax = _contents_bbox()

    ix0, ix1 = cxmin - interior_clearance, cxmax + interior_clearance
    iy0, iy1 = cymin - interior_clearance, cymax + interior_clearance
    iz0, iz1 = czmin - interior_clearance, czmax + interior_clearance

    ox0, ox1 = ix0 - wall, ix1 + wall
    oy0, oy1 = iy0 - wall, iy1 + wall
    oz0, oz1 = iz0 - wall, iz1 + wall

    outer = (
        cq.Workplane("XY")
        .box(ox1 - ox0, oy1 - oy0, oz1 - oz0, centered=False)
        .translate((ox0, oy0, oz0))
    )
    inner = (
        cq.Workplane("XY")
        .box(ix1 - ix0, iy1 - iy0, iz1 - iz0, centered=False)
        .translate((ix0, iy0, iz0))
    )
    shell = outer.cut(inner)
    shell = shell.cut(build_display_facet_cutter((ox0, ox1, oy0, oy1, oz0, oz1)))
    return shell, (ox0, ox1, oy0, oy1, oz0, oz1)


def _report_display_facet(shell):
    """Measure the 45° display facet: collect every planar face whose outward
    normal points up-and-forward (−Y/+Z) and report the combined window's
    lateral width (X) and slope length, against the 118.5 × 81 target."""
    a = math.radians(display_facet_angle_deg)
    target = cq.Vector(0.0, -math.sin(a), math.cos(a))
    boxes = []
    for f in shell.val().Faces():
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
    print(f"  display facet:    {xspan:.1f} mm wide (X) × {slope:.1f} mm slope, "
          f"normal up-forward (−Y/+Z)  (target {display_facet_x:g} × {display_facet_slope:g})")


def main():
    shell, outer = build_enclosure()
    out = _here.parent / "enclosure.step"
    export_step(shell, str(out))
    print(f"-> {out.name}")
    ox0, ox1, oy0, oy1, oz0, oz1 = outer
    dx, dy, dz = ox1 - ox0, oy1 - oy0, oz1 - oz0
    print(f"  outer envelope    {dx:.1f} (X) x {dy:.1f} (Y) x {dz:.1f} (Z) mm")
    print(f"  H2C left nozzle   {H2C_X:.1f} (X) x {H2C_Y:.1f} (Y) x {H2C_Z:.1f} (Z) mm")
    fits = dx <= H2C_X + 1e-3 and dy <= H2C_Y + 1e-3 and dz <= H2C_Z + 1e-3
    print(f"  fits H2C bed:     {fits}")
    _report_display_facet(shell)

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
