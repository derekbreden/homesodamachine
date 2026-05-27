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
LLDPE routes through the foam shell's shared +Y slot (alongside the
water inlet) into the appliance interior, where it terminates open.

Geometry
--------

    Z = 46 mm  ┌──────────────────────┐  ← cap outside surface
               │ ░░░░ 2 mm cap ░░░░░░ │  ← centered ⌀6.35 hole
    Z = 44 mm  ├──────────────────────┤  ← cap inside surface
               │                      │
               │   (cavity around     │
               │    PRV body, hex,    │  ← 19 mm ID
               │    upper smooth cyl, │     23 mm OD (2 mm wall)
               │    bonnet windows,   │
               │    pull-ring)        │
               │                      │
    Z = 0      └ open ────────────────┘  ← seats on elbow ⌀18.8 mm cyl

The 44 mm cavity length matches the in-hand stack measurement from
the bottom of the elbow's smooth cylinder to the very tip of the
PRV pull-ring with the valve hand-tight in the elbow's lateral
F outlet.

Coordinate convention: cylinder axis along Z, open end at Z=0, cap
top at Z=46. Installed orientation is horizontal — the shroud's Z
axis aligns with the lateral run of the TAISHER elbow off Port 4.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments


# Physical dimensions

# [19 mm](INNER_D) — 0.1 mm radial slip-fit over the ⌀18.8 elbow seat cylinder.
inner_diameter = 19.0
# [2 mm](WALL_T) — radial wall around the PRV body.
wall_thickness = 2.0
# [2 mm](CAP_T) — closed (far) end carrying the vent hole.
cap_thickness = 2.0
# [44 mm](CAVITY_L) — elbow seat bottom to PRV pull-ring tip.
cavity_length = 44.0
# [6.35 mm](VENT_D) — 1/4" LLDPE tubing OD.
vent_hole_diameter = 6.35

# [23 mm](OUTER_D) — inner_diameter + 2 × wall_thickness.
outer_diameter = inner_diameter + 2 * wall_thickness
# [46 mm](TOTAL_L) — cavity_length + cap_thickness.
total_length = cavity_length + cap_thickness

# Slop for cut-through operations.
overcut = 0.1


def build_prv_shroud():
    """One-piece cylindrical cup with a centered vent hole in the cap."""
    outer = (
        cq.Workplane("XY")
        .circle(outer_diameter / 2)
        .extrude(total_length)
    )
    cavity = (
        cq.Workplane("XY")
        .circle(inner_diameter / 2)
        .extrude(cavity_length + overcut)
    )
    vent_hole = (
        cq.Workplane("XY")
        .workplane(offset=cavity_length - overcut)
        .circle(vent_hole_diameter / 2)
        .extrude(cap_thickness + 2 * overcut)
    )
    return outer.cut(cavity).cut(vent_hole)


def main():
    out_dir = _here.parent
    shroud = build_prv_shroud()
    export_step(shroud, str(out_dir / "prv-shroud.step"))

    solids = shroud.solids().vals()
    assert len(solids) == 1, f"expected 1 solid, got {len(solids)}"
    solid = solids[0]
    bb = solid.BoundingBox()
    vol = solid.Volume()
    print(
        f"-> prv-shroud.step  "
        f"bbox X[{bb.xmin:6.2f}..{bb.xmax:6.2f}] "
        f"Y[{bb.ymin:6.2f}..{bb.ymax:6.2f}] "
        f"Z[{bb.zmin:6.2f}..{bb.zmax:6.2f}]  "
        f"vol {vol:.3f} mm^3"
    )

    # Short names scoped to this part. Units live inside the value so
    # the script controls them — change a unit in source and every
    # sibling doc + dynamic-comment marker follows.
    variables = {
        "INNER_D": f"{inner_diameter:.4g} mm",
        "WALL_T": f"{wall_thickness:.4g} mm",
        "CAP_T": f"{cap_thickness:.4g} mm",
        "CAVITY_L": f"{cavity_length:.4g} mm",
        "VENT_D": f"{vent_hole_diameter:.4g} mm",
        "OUTER_D": f"{outer_diameter:.4g} mm",
        "TOTAL_L": f"{total_length:.4g} mm",
        # Regression baseline (computed from the actual STEP geometry).
        "VOLUME": f"{vol:.3f} mm³",
        "BBOX_X": f"{bb.xmin:.3f} to {bb.xmax:.3f} mm",
        "BBOX_Y": f"{bb.ymin:.3f} to {bb.ymax:.3f} mm",
        "BBOX_Z": f"{bb.zmin:.3f} to {bb.zmax:.3f} mm",
    }
    substitute_md(
        out_dir / "README.md",
        variables=variables,
        expected_counts={
            "INNER_D": 2,
            "WALL_T": 1,
            "CAP_T": 2,
            "CAVITY_L": 1,
            "VENT_D": 1,
            "OUTER_D": 1,
            "TOTAL_L": 1,
            "VOLUME": 1,
            "BBOX_X": 1,
            "BBOX_Y": 1,
            "BBOX_Z": 1,
        },
    )
    print("-> README.md")
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "INNER_D": 1,
            "WALL_T": 1,
            "CAP_T": 1,
            "CAVITY_L": 1,
            "VENT_D": 1,
            "OUTER_D": 1,
            "TOTAL_L": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
