"""Lite hopper funnel — a square inlet tapering to a round spout.

The hopper you pour batch liquid into; it drains through its spout to V-B on
the source-select tray (fluid topology segment 4, "Hopper funnel bottom ->
V-B-I"). This is a pour-through guide with a small buffer, not a batch
reservoir — what gets poured in is pumped straight on to a bag.

It rides on the front (-X) of the device, filling the +Y half of the front top,
generously sized: a square inlet tapering to a round spout whose bore matches
the 1/4 in tube line used elsewhere (the reservoir's 6.5 mm port holes).

Local frame: centered on the Z axis (x = y = 0), the spout outlet face on Z = 0,
the square inlet opening at Z = total_height, opening up (+Z). Walls are 2 mm.
Print in PETG.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
from _cadq_export import export_step
from docgen import substitute_py_comments

inlet_side = 130.0    # outer square inlet, side length
wall = 2.0            # wall thickness
taper_height = 78.0   # square-inlet -> round-spout taper body
spout_od = 10.0       # round spout outer diameter
spout_id = 6.5        # spout bore: 1/4 in tube line (matches reservoir ports)
spout_length = 12.0   # straight spout below the taper
total_height = spout_length + taper_height  # [90 mm](TOTAL_HEIGHT)


def build_funnel():
    """Hollow 2 mm-walled funnel: round spout, square-to-round taper, square
    inlet — open through top and bottom."""
    ro, ri = spout_od / 2.0, spout_id / 2.0

    # Outer skin: spout cylinder, then a loft from the spout circle up to the
    # square inlet.
    outer = (
        cq.Workplane("XY").workplane(offset=spout_length).circle(ro)
        .workplane(offset=taper_height).rect(inlet_side, inlet_side)
        .loft(ruled=True)
    )
    outer = outer.union(
        cq.Workplane(obj=cq.Solid.makeCylinder(
            ro, spout_length, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1)))
    )

    # Inner void, one wall thinner; over-runs top and bottom so both ends open.
    inner = (
        cq.Workplane("XY").workplane(offset=spout_length).circle(ri)
        .workplane(offset=taper_height + 1.0).rect(inlet_side - 2 * wall, inlet_side - 2 * wall)
        .loft(ruled=True)
    )
    inner = inner.union(
        cq.Workplane(obj=cq.Solid.makeCylinder(
            ri, spout_length + 1.0, cq.Vector(0, 0, -0.5), cq.Vector(0, 0, 1)))
    )

    return outer.cut(inner)


def main():
    funnel = build_funnel()
    export_step(funnel, str(_here.parent / "funnel.step"))
    print("-> funnel.step")
    bb = funnel.val().BoundingBox()
    print("funnel envelope %.1f x %.1f x %.1f mm  Z[%.1f,%.1f]"
          % (bb.xlen, bb.ylen, bb.zlen, bb.zmin, bb.zmax))
    substitute_py_comments(
        _here,
        variables={"TOTAL_HEIGHT": f"{total_height:.4g} mm"},
        expected_counts={"TOTAL_HEIGHT": 1},
    )
    print(f"-> {_here.name} (self)")


if __name__ == "__main__":
    main()
