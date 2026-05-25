"""Touch-Flo TPU O-ring — printed-TPU thimble that seals 3/8" OD LLDPE
into the harvested Westbrass valve body's top water port. See
README.md for the sealing-interface architecture, print orientation,
and assembly."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments


# Thimble design choices.
inner_diameter = 9.45      # cylinder ID — grips [9.525 mm](LLDPE_OD) LLDPE ([0.0375 mm](LLDPE_INTERFERENCE)/side interference)
outer_diameter = 10.20     # cylinder OD — compresses into [10 mm](BODY_PORT_D) body port ([0.1 mm](BODY_SQUEEZE)/side squeeze)
cap_hole_diameter = 6.50   # hole through the cap — > LLDPE ID ([6.35 mm](LLDPE_ID)), < LLDPE OD ([9.525 mm](LLDPE_OD))
cap_thickness = 1.5        # axial thickness of the closed bottom — solid first layer when printed cap-down
cylinder_length = 13.5     # axial length of the sleeve portion above the cap

# Derived from the design choices.
total_height = cap_thickness + cylinder_length              # [15 mm](TOTAL_H) — vs [20 mm](PORT_DEPTH_MIN) port depth, comfortable headroom
wall_thickness = (outer_diameter - inner_diameter) / 2.0    # [0.375 mm](WALL_T) — sub-nozzle, Arachne thin-wall from layer 2

# External references — uncompressed/measured dimensions of upstream
# parts. Single source of truth for cross-references in the README.
lldpe_od = 9.525                # 3/8" LLDPE tubing OD
lldpe_id = 6.35                 # 1/4" LLDPE tubing ID
body_port_diameter = 10.0       # Westbrass top water port ID, 2026-05-22 re-measurement
factory_o_ring_od = 10.15       # factory toroidal rubber o-ring OD (uncompressed)
factory_tube_od = 9.55          # factory metal dispense tube OD
port_depth_min = 20.0           # minimum measured port depth

# Derived squeezes/interferences (radial, per side).
body_squeeze = (outer_diameter - body_port_diameter) / 2.0
lldpe_interference = (lldpe_od - inner_diameter) / 2.0
factory_o_ring_squeeze = (factory_o_ring_od - body_port_diameter) / 2.0


def build_o_ring() -> cq.Workplane:
    """Build the TPU thimble — closed bottom with a centered hole,
    open top, cylindrical wall.

    Z=0 is the bottom (cap-down on the bed). Cap spans Z = 0 to
    cap_thickness; sleeve spans Z = cap_thickness to total_height.
    """
    # Solid outer cylinder spanning the full part height.
    body = (
        cq.Workplane("XY")
        .circle(outer_diameter / 2.0)
        .extrude(total_height)
    )

    # Cut the cap's centered hole through the full height. (Through
    # the cap and also through the sleeve, but the sleeve's larger
    # bore — cut next — supersedes it above Z = cap_thickness.)
    cap_hole = (
        cq.Workplane("XY")
        .circle(cap_hole_diameter / 2.0)
        .extrude(total_height)
    )
    body = body.cut(cap_hole)

    # Cut the sleeve's larger inner bore from Z = cap_thickness to
    # the top of the part. Leaves the cap (Z = 0 to cap_thickness)
    # with only the smaller cap hole.
    sleeve_bore = (
        cq.Workplane("XY")
        .workplane(offset=cap_thickness)
        .circle(inner_diameter / 2.0)
        .extrude(cylinder_length)
    )
    body = body.cut(sleeve_bore)

    return body


def main():
    o_ring = build_o_ring()
    export_step(o_ring, str(_here / "touch-flo-tpu-o-ring.step"))
    print("-> touch-flo-tpu-o-ring.step")

    variables = {
        # Thimble design choices.
        "INNER_D": f"{inner_diameter:g} mm",
        "OUTER_D": f"{outer_diameter:g} mm",
        "CAP_HOLE_D": f"{cap_hole_diameter:g} mm",
        "CAP_T": f"{cap_thickness:g} mm",
        "CYL_L": f"{cylinder_length:g} mm",
        "TOTAL_H": f"{total_height:g} mm",
        "WALL_T": f"{wall_thickness:g} mm",
        # External references.
        "LLDPE_OD": f"{lldpe_od:g} mm",
        "LLDPE_ID": f"{lldpe_id:g} mm",
        "BODY_PORT_D": f"{body_port_diameter:g} mm",
        "FACTORY_O_RING_OD": f"{factory_o_ring_od:g} mm",
        "FACTORY_TUBE_OD": f"{factory_tube_od:g} mm",
        "PORT_DEPTH_MIN": f"{port_depth_min:g} mm",
        # Derived squeezes/interferences (per side).
        "BODY_SQUEEZE": f"{body_squeeze:g} mm",
        "LLDPE_INTERFERENCE": f"{lldpe_interference:g} mm",
        "FACTORY_O_RING_SQUEEZE": f"{factory_o_ring_squeeze:g} mm",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "INNER_D": 3,
            "OUTER_D": 4,
            "CAP_HOLE_D": 4,
            "CAP_T": 2,
            "CYL_L": 3,
            "TOTAL_H": 2,
            "WALL_T": 3,
            "LLDPE_OD": 5,
            "LLDPE_ID": 2,
            "BODY_PORT_D": 5,
            "FACTORY_O_RING_OD": 1,
            "FACTORY_TUBE_OD": 1,
            "PORT_DEPTH_MIN": 2,
            "BODY_SQUEEZE": 3,
            "LLDPE_INTERFERENCE": 2,
            "FACTORY_O_RING_SQUEEZE": 1,
        },
    )
    print("-> README.md")

    substitute_py_comments(
        __file__,
        variables=variables,
        expected_counts={
            "LLDPE_OD": 2,
            "LLDPE_ID": 1,
            "BODY_PORT_D": 1,
            "LLDPE_INTERFERENCE": 1,
            "BODY_SQUEEZE": 1,
            "TOTAL_H": 1,
            "PORT_DEPTH_MIN": 1,
            "WALL_T": 1,
        },
    )
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
