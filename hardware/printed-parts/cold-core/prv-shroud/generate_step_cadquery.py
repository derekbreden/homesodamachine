"""PRV shroud — printed PETG cup that surrounds the Control Devices
SV-125 pressure-relief valve during the cold-core body foam pour.

The SV-125 is an open-port pop-off valve: gas exits through a single
radial discharge port on the smooth cylinder between the NPT threads
and the hex, and the spring chamber above the hex is open to
atmosphere through bonnet windows above. Both features need to see
air, not cured polyurethane foam, for the valve to function as a
relief device.

The shroud slips over the entire valve from the pull-ring end and
seats on the smooth ⌀18.8 mm cylindrical section of the TAISHER 316L
SS 90° street elbow (B0CZ38MYL1) that threads into Port 4. The
open shroud end-to-elbow joint is sealed pre-pour with hot glue (or
equivalent fast-cure adhesive) for the duration of the foam rise —
foam-tight, not airtight. After foam cure, the cured foam itself
takes over as the structural seal.

A ⌀6.35 mm hole in the closed (far) end of the shroud accepts a
length of 1/4" OD LLDPE tubing — the unpressurized vent line. The
LLDPE routes through the foam shell's shared +Z slot (alongside the
water inlet) into the appliance interior, where it terminates open.

Geometry
--------

    Y = 46 mm  ┌──────────────────────┐  ← cap outside surface
               │ ░░░░ 2 mm cap ░░░░░░ │  ← centered ⌀6.35 hole
    Y = 44 mm  ├──────────────────────┤  ← cap inside surface
               │                      │
               │   (cavity around     │
               │    PRV body, hex,    │  ← 19 mm ID
               │    upper smooth cyl, │     23 mm OD (2 mm wall)
               │    bonnet windows,   │
               │    pull-ring)        │
               │                      │
    Y = 0      └ open ────────────────┘  ← seats on elbow ⌀18.8 mm cyl

The 44 mm cavity length matches the in-hand stack measurement from
the bottom of the elbow's smooth cylinder to the very tip of the
PRV pull-ring with the valve hand-tight in the elbow's lateral
F outlet.

Coordinate convention: cylinder axis along Y, open end at Y=0, cap
top at Y=46. Installed orientation is horizontal — the shroud's Y
axis aligns with the lateral run of the TAISHER elbow off Port 4.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
)

from _cadq_export import export_step


# Physical dimensions
inner_diameter = 19.0       # 0.1 mm radial slip-fit over ⌀18.8 elbow cylinder
wall_thickness = 2.0
cap_thickness = 2.0
cavity_length = 44.0        # elbow seat bottom to PRV pull-ring tip
vent_hole_diameter = 6.35   # 1/4" LLDPE tubing OD

outer_diameter = inner_diameter + 2 * wall_thickness   # 23 mm
total_length = cavity_length + cap_thickness           # 46 mm

# Slop for cut-through operations.
overcut = 0.1


def build_prv_shroud():
    """One-piece cylindrical cup with a centered vent hole in the cap."""
    outer = (
        cq.Workplane("XZ")
        .circle(outer_diameter / 2)
        .extrude(total_length)
    )
    cavity = (
        cq.Workplane("XZ")
        .circle(inner_diameter / 2)
        .extrude(cavity_length + overcut)
    )
    vent_hole = (
        cq.Workplane("XZ")
        .workplane(offset=cavity_length - overcut)
        .circle(vent_hole_diameter / 2)
        .extrude(cap_thickness + 2 * overcut)
    )
    return outer.cut(cavity).cut(vent_hole)


def main():
    shroud = build_prv_shroud()
    export_step(shroud, str(_here / "prv-shroud.step"))

    solids = shroud.solids().vals()
    assert len(solids) == 1, f"expected 1 solid, got {len(solids)}"
    bb = solids[0].BoundingBox()
    vol = solids[0].Volume()
    print(
        f"-> prv-shroud.step  "
        f"bbox X[{bb.xmin:6.2f}..{bb.xmax:6.2f}] "
        f"Y[{bb.ymin:6.2f}..{bb.ymax:6.2f}] "
        f"Z[{bb.zmin:6.2f}..{bb.zmax:6.2f}]  "
        f"vol {vol:.3f} mm^3"
    )


if __name__ == "__main__":
    main()
