"""Fake countertop: the bench stand that stands in for a counter. An inverted U the size of
the bed, one faucet through its 1-3/8" hole, the umbilical hanging and bending under it.

The print stands on the show face: the slab lies on the bed and the legs rise from it, so
the show face takes the plate's texture and nothing needs support. The slab's show edges
are rounded down to where the round reaches 45 degrees and run out to the bed at 45 degrees
below that. The four outer corners, the legs' inner edges and the feet are rounded plain,
and the legs meet the slab on a rounded root.

Frame: X across the legs, Y along the front edge, +Z up from the bed; the show face is Z = 0.
In use the piece stands the other way up.

Run with tools/cad-venv/bin/python. No argument exports the print; `selftest` checks
geometry without writing files.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import cadquery as cq


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
for _path in (_hw / "scripts", _repo / "tools"):
    sys.path.insert(0, str(_path))

from _cadq_export import export_assembly, note_write  # noqa: E402
from _material_base import M_PETGF_BLACK, one_body  # noqa: E402
from docgen import substitute_md  # noqa: E402


INCH = 25.4

# The H2C's printable area and height, per its Bambu Studio machine profile.
BED_X = 330.0
BED_Y = 320.0
BED_Z = 325.0
BED_MARGIN = 5.0

# The counter hole the shank is sized for (`hardware/faucet-layout/faucet_assembly.py`).
COUNTER_HOLE_D = 1.375 * INCH

# Below the counter's top face: the shank ends at -50 and the umbilical stub at -80 in the
# faucet frame, whose counter top is at -6; the gather bends on a 30 mm radius under that.
UMBILICAL_BELOW_COUNTER = 80.0 - 6.0
UMBILICAL_BEND_R = 30.0
HAND_ROOM = 60.0

T = 12.0
HEIGHT = 220.0
SLAB_X = BED_X - 2 * BED_MARGIN
SLAB_Y = BED_Y - 2 * BED_MARGIN
SHOW_EDGE_R = 6.0
CORNER_R = 6.0
ROOT_R = 6.0
FOOT_R = 3.0

show_edge_tangent_z = SHOW_EDGE_R * (1 - math.sin(math.radians(45)))
show_edge_runout = 2 * show_edge_tangent_z
clear_height = HEIGHT - T
leg_inner_x = SLAB_X / 2 - T

MESH_TOLERANCE = 0.05
MESH_ANGLE = 0.2


def _box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane(obj=cq.Solid.makeBox(
        x1 - x0, y1 - y0, z1 - z0, cq.Vector(x0, y0, z0)
    ))


def _edges(shape, keep):
    return shape.newObject([e for e in shape.edges().vals() if keep(e.Center())])


def _vertical_edges(shape, keep):
    return shape.newObject([
        e for e in shape.edges("|Z").vals() if keep(e.Center())
    ])


def _u():
    slab = _box(-SLAB_X / 2, SLAB_X / 2, -SLAB_Y / 2, SLAB_Y / 2, 0.0, T)
    left = _box(-SLAB_X / 2, -leg_inner_x, -SLAB_Y / 2, SLAB_Y / 2, T - 1.0, HEIGHT)
    right = _box(leg_inner_x, SLAB_X / 2, -SLAB_Y / 2, SLAB_Y / 2, T - 1.0, HEIGHT)
    return slab.union(left).union(right)


def _rounded():
    u = _u()
    outer = lambda c: abs(c.x) > leg_inner_x + 1.0 and abs(c.y) > SLAB_Y / 2 - 1.0
    u = _vertical_edges(u, outer).fillet(CORNER_R)
    root = lambda c: abs(abs(c.x) - leg_inner_x) < 1e-6 and abs(c.z - T) < 1e-6
    u = _edges(u, root).fillet(ROOT_R)
    inner = lambda c: abs(abs(c.x) - leg_inner_x) < 1e-6 and abs(c.y) > SLAB_Y / 2 - 1.0
    u = _vertical_edges(u, inner).fillet(FOOT_R)
    u = u.edges(">Z").fillet(FOOT_R)
    return u


def _show_edges(u):
    rounded = u.edges("<Z").fillet(SHOW_EDGE_R)
    runout = u.edges("<Z").chamfer(show_edge_runout).intersect(
        _box(-SLAB_X, SLAB_X, -SLAB_Y, SLAB_Y, 0.0, show_edge_tangent_z))
    return rounded.union(runout)


def _hole():
    return cq.Workplane(obj=cq.Solid.makeCylinder(
        COUNTER_HOLE_D / 2, T + 2.0, cq.Vector(0, 0, -1.0), cq.Vector(0, 0, 1)
    ))


def build():
    return _show_edges(_rounded()).cut(_hole())


def _volume(shape):
    return sum(s.Volume() for s in shape.solids().vals())


def _single_valid(name, shape):
    solids = shape.solids().vals()
    if len(solids) != 1 or not solids[0].isValid() or solids[0].Volume() <= 0:
        raise ValueError(f"{name}: expected one valid, positive-volume solid")
    return solids[0]


def _section_width(shape, z):
    # The part's X extent at height z, from a thin slice through it.
    slab = _box(-BED_X, BED_X, -BED_Y, BED_Y, z - 0.01, z + 0.01)
    bb = shape.intersect(slab).val().BoundingBox()
    return bb.xlen, bb.ylen


def selftest():
    part = build()
    _single_valid("fake countertop", part)
    bb = part.val().BoundingBox()
    if abs(bb.zmin) > 1e-6:
        raise ValueError("print does not sit on Z=0")
    if bb.xlen > BED_X - 2 * BED_MARGIN + 1e-6 or bb.ylen > BED_Y - 2 * BED_MARGIN + 1e-6:
        raise ValueError("footprint leaves the bed's margin")
    if bb.zlen > BED_Z:
        raise ValueError("taller than the printer")

    needed = UMBILICAL_BELOW_COUNTER + UMBILICAL_BEND_R + HAND_ROOM
    if clear_height < needed:
        raise ValueError(f"only {clear_height} mm under the slab; the umbilical wants {needed}")

    probe = cq.Workplane(obj=cq.Solid.makeCylinder(
        COUNTER_HOLE_D / 2 - 0.05, T + 2.0, cq.Vector(0, 0, -1.0), cq.Vector(0, 0, 1)))
    if _volume(part.intersect(probe)) > 1e-6:
        raise ValueError("the counter hole is smaller than the shank's standard")

    # The show edges: between the bed and the round's 45-degree point the outline may grow
    # no faster than 45 degrees, layer over layer, which is what prints in air.
    overhang = []
    heights = [0.2, 0.6, 1.0, 1.4, show_edge_tangent_z, 3.0, 5.0, SHOW_EDGE_R]
    widths = [_section_width(part, z) for z in heights]
    for (z0, (x0, y0)), (z1, (x1, y1)) in zip(zip(heights, widths), zip(heights[1:], widths[1:])):
        grow = max(x1 - x0, y1 - y0) / 2.0
        overhang.append({"from_z": z0, "to_z": z1, "grow_per_side_mm": round(grow, 3)})
        if grow > (z1 - z0) + 0.05:
            raise ValueError(f"show edge overhangs past 45 degrees between z {z0} and {z1}: {grow}")

    print(json.dumps({
        "status": "CAD checks passed; the print is untested",
        "envelope_mm": [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)],
        "clear_under_slab_mm": clear_height,
        "volume_cm3": round(_volume(part) / 1000, 1),
        "show_edge": overhang,
    }, indent=2))
    return part


def _export_print(part):
    stem = "fake-countertop"
    stl = _here.parent / f"{stem}.stl"
    step = _here.parent / f"{stem}.step"
    # A sibling slicer mesh keeps this bench fixture out of viewer payloads.
    cq.exporters.export(part, str(stl), tolerance=MESH_TOLERANCE, angularTolerance=MESH_ANGLE)
    note_write(stl)
    export_assembly(one_body(part, stem, M_PETGF_BLACK), str(step))
    print(f"-> {step.name}, {stl.name}: {_volume(part) / 1000:.1f} cm³")


def main():
    part = selftest()
    _export_print(part)
    substitute_md(_here.parent / "README.md", variables={
        "FCT_SLAB": f"{SLAB_X:g} × {SLAB_Y:g} mm",
        "FCT_T": f"{T:g} mm",
        "FCT_HEIGHT": f"{HEIGHT:g} mm",
        "FCT_CLEAR": f"{clear_height:g} mm",
        "FCT_HOLE": f"{COUNTER_HOLE_D:.2f} mm",
        "FCT_SHOW_EDGE_R": f"{SHOW_EDGE_R:g} mm",
        "FCT_RUNOUT": f"{show_edge_runout:.1f} mm",
        "FCT_CORNER_R": f"{CORNER_R:g} mm",
        "FCT_FOOT_R": f"{FOOT_R:g} mm",
        "FCT_UMBILICAL": f"{UMBILICAL_BELOW_COUNTER + UMBILICAL_BEND_R:g} mm",
        "FCT_VOLUME": f"{_volume(part) / 1000:.0f} cm³",
    })


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        selftest()
    elif sys.argv[1:]:
        sys.exit("usage: fake_countertop.py [selftest]")
    else:
        main()
