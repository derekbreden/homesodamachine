"""Touch-Flo TPU O-ring — printed-TPU thimble that seals 3/8" OD LLDPE
into the harvested Westbrass valve body's top water port. See README.md."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))

from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments
from world_workplane import xy_plane_z_up


inner_diameter = 9.2
outer_diameter = 10.44
cap_hole_diameter = 6.50
cap_thickness = 2.1
cylinder_length = 13.5

# [15.6 mm](TOTAL_H)
total_height = cap_thickness + cylinder_length
# [0.62 mm](WALL_T)
wall_thickness = (outer_diameter - inner_diameter) / 2.0

lldpe_od = 9.525                # 3/8" LLDPE tubing OD
lldpe_id = 6.35                 # 1/4" LLDPE tubing ID
body_port_diameter = 10.0       # Westbrass top water port ID
port_depth_min = 20.0           # minimum measured port depth

body_squeeze = (outer_diameter - body_port_diameter) / 2.0
lldpe_interference = (lldpe_od - inner_diameter) / 2.0


def build_o_ring() -> cq.Workplane:
    """Build the TPU thimble: closed bottom with a centered hole, open
    top, cylindrical wall. Authored natively in the repo's +Z-up frame:
    Z=0 is the bottom (the face that mates against the valve body's
    port floor); cap spans Z=0 to cap_thickness; sleeve spans
    Z=cap_thickness to total_height. The thimble's axis is +Z."""
    body = (
        cq.Workplane(xy_plane_z_up)
        .circle(outer_diameter / 2.0)
        .extrude(total_height)
    )
    cap_hole = (
        cq.Workplane(xy_plane_z_up)
        .circle(cap_hole_diameter / 2.0)
        .extrude(total_height)
    )
    body = body.cut(cap_hole)
    sleeve_bore = (
        cq.Workplane(xy_plane_z_up)
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
        "INNER_D": f"{inner_diameter:.4g} mm",
        "OUTER_D": f"{outer_diameter:.4g} mm",
        "CAP_HOLE_D": f"{cap_hole_diameter:.4g} mm",
        "CAP_T": f"{cap_thickness:.4g} mm",
        "CYL_L": f"{cylinder_length:.4g} mm",
        "TOTAL_H": f"{total_height:.4g} mm",
        "WALL_T": f"{wall_thickness:.4g} mm",
        "LLDPE_OD": f"{lldpe_od:.4g} mm",
        "LLDPE_ID": f"{lldpe_id:.4g} mm",
        "BODY_PORT_D": f"{body_port_diameter:.4g} mm",
        "PORT_DEPTH_MIN": f"{port_depth_min:.4g} mm",
        "BODY_SQUEEZE": f"{body_squeeze:.4g} mm",
        "LLDPE_INTERFERENCE": f"{lldpe_interference:.4g} mm",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "INNER_D": 2,
            "OUTER_D": 3,
            "CAP_HOLE_D": 3,
            "CAP_T": 1,
            "CYL_L": 1,
            "TOTAL_H": 2,
            "WALL_T": 2,
            "LLDPE_OD": 2,
            "LLDPE_ID": 1,
            "BODY_PORT_D": 2,
            "PORT_DEPTH_MIN": 1,
            "BODY_SQUEEZE": 2,
            "LLDPE_INTERFERENCE": 1,
        },
    )
    print("-> README.md")

    substitute_py_comments(
        __file__,
        variables=variables,
        expected_counts={
            "TOTAL_H": 1,
            "WALL_T": 1,
        },
    )
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
