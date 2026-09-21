"""Fake countertop: the bench stand that stands in for a counter. An inverted U the size of
the bed, one faucet through its 1-3/8" hole, the umbilical hanging and bending under it.

The print stands on the show face: the slab lies on the bed and the legs rise from it, so
the show face takes the plate's texture and nothing needs support. The slab's edges on the
bed are sharp. Every other edge is rounded: the four outer corners, the legs' inner edges
and the feet, and the legs meet the slab on a rounded root. The print mesh is the faucet's
absolute-tolerance triangulation, so the rounds print as rounds.

Frame: X across the legs, Y along the front edge, +Z up from the bed; the show face is Z = 0.
In use the piece stands the other way up.

Run with tools/cad-venv/bin/python. No argument exports the print; `selftest` checks
geometry without writing files.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cadquery as cq


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
for _path in (_hw / "scripts", _hw / "printed-parts" / "cadlib", _repo / "tools"):
    sys.path.insert(0, str(_path))

from _cadq_export import export_assembly, note_write  # noqa: E402
from _material_base import M_PETGF_BLACK, one_body  # noqa: E402
from docgen import substitute_md  # noqa: E402
from print_mesh import write_print_stl  # noqa: E402


INCH = 25.4

# The H2C's plate, per its Bambu Studio machine profile: 330 x 320 x 325, of which the left
# nozzle, the one this job prints with, reaches X 0..325. The project stands inside that
# reach with the 15 mm border every print here keeps (`faucet/refresh_print_project.py`):
# an outline laid 5 mm from the plate's edge lifted within a dozen lines, three times.
BED_Z = 325.0
LEFT_REACH_X = 325.0
LEFT_REACH_Y = 320.0
PLATE_BORDER = 15.0

# The counter hole the shank is sized for (`hardware/faucet-layout/faucet_assembly.py`).
COUNTER_HOLE_D = 1.375 * INCH

# Below the counter's top face: the shank ends at -50 and the umbilical stub at -80 in the
# faucet frame, whose counter top is at -6; the gather bends on a 30 mm radius under that.
UMBILICAL_BELOW_COUNTER = 80.0 - 6.0
UMBILICAL_BEND_R = 30.0
HAND_ROOM = 60.0

T = 12.0
HEIGHT = 220.0
SLAB_X = LEFT_REACH_X - 2 * PLATE_BORDER
SLAB_Y = LEFT_REACH_Y - 2 * PLATE_BORDER
CORNER_R = 6.0
ROOT_R = 6.0
FOOT_R = 3.0

clear_height = HEIGHT - T
leg_inner_x = SLAB_X / 2 - T



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


def _hole():
    return cq.Workplane(obj=cq.Solid.makeCylinder(
        COUNTER_HOLE_D / 2, T + 2.0, cq.Vector(0, 0, -1.0), cq.Vector(0, 0, 1)
    ))


def build():
    return _rounded().cut(_hole())


def _volume(shape):
    return sum(s.Volume() for s in shape.solids().vals())


def _single_valid(name, shape):
    solids = shape.solids().vals()
    if len(solids) != 1 or not solids[0].isValid() or solids[0].Volume() <= 0:
        raise ValueError(f"{name}: expected one valid, positive-volume solid")
    return solids[0]


def _section_extent(shape, z):
    # The part's X and Y extent at height z, from a thin slice through it.
    slab = _box(-LEFT_REACH_X, LEFT_REACH_X, -LEFT_REACH_Y, LEFT_REACH_Y, z - 0.01, z + 0.01)
    bb = shape.intersect(slab).val().BoundingBox()
    return bb.xlen, bb.ylen


def selftest():
    part = build()
    _single_valid("fake countertop", part)
    bb = part.val().BoundingBox()
    if abs(bb.zmin) > 1e-6:
        raise ValueError("print does not sit on Z=0")
    if bb.xlen > LEFT_REACH_X - 2 * PLATE_BORDER + 1e-6 or bb.ylen > LEFT_REACH_Y - 2 * PLATE_BORDER + 1e-6:
        raise ValueError("footprint leaves the plate border inside the left nozzle's reach")
    if bb.zlen > BED_Z:
        raise ValueError("taller than the printer")

    needed = UMBILICAL_BELOW_COUNTER + UMBILICAL_BEND_R + HAND_ROOM
    if clear_height < needed:
        raise ValueError(f"only {clear_height} mm under the slab; the umbilical wants {needed}")

    probe = cq.Workplane(obj=cq.Solid.makeCylinder(
        COUNTER_HOLE_D / 2 - 0.05, T + 2.0, cq.Vector(0, 0, -1.0), cq.Vector(0, 0, 1)))
    if _volume(part.intersect(probe)) > 1e-6:
        raise ValueError("the counter hole is smaller than the shank's standard")

    # The slab's edges on the bed are sharp: the first layer is the whole footprint, and
    # nothing above it stands out past it.
    first = _section_extent(part, 0.2)
    if abs(first[0] - bb.xlen) > 1e-3 or abs(first[1] - bb.ylen) > 1e-3:
        raise ValueError(f"the first layer is not the whole footprint: {first} in {(bb.xlen, bb.ylen)}")

    print(json.dumps({
        "status": "CAD checks passed; the print is untested",
        "envelope_mm": [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)],
        "clear_under_slab_mm": clear_height,
        "volume_cm3": round(_volume(part) / 1000, 1),
    }, indent=2))
    return part


def _export_print(part):
    stem = "fake-countertop"
    stl = _here.parent / f"{stem}.stl"
    step = _here.parent / f"{stem}.step"
    # A sibling print mesh keeps this bench fixture out of viewer payloads.
    written = write_print_stl(part, stl)
    note_write(stl)
    export_assembly(one_body(part, stem, M_PETGF_BLACK), str(step))
    print(f"-> {step.name}, {stl.name}: {_volume(part) / 1000:.1f} cm³, {len(written.faces)} facets")


def main():
    part = selftest()
    _export_print(part)
    substitute_md(_here.parent / "README.md", variables={
        "FCT_SLAB": f"{SLAB_X:g} × {SLAB_Y:g} mm",
        "FCT_T": f"{T:g} mm",
        "FCT_HEIGHT": f"{HEIGHT:g} mm",
        "FCT_CLEAR": f"{clear_height:g} mm",
        "FCT_HOLE": f"{COUNTER_HOLE_D:.2f} mm",
        "FCT_CORNER_R": f"{CORNER_R:g} mm",
        "FCT_ROOT_R": f"{ROOT_R:g} mm",
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
