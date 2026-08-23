"""TPU o-ring — printed-TPU thimble that seals the 3/8" soda faucet tube
into the harvested Westbrass's top water port. See README.md."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))

from _cadq_export import export_assembly
from _materials import M_TPU_BLACK, one_body
from docgen import substitute_md, substitute_py_comments
from world_workplane import xy_plane_z_up


inner_diameter = 9.2
outer_diameter = 10.44
cap_hole_diameter = 6.50
cap_thickness = 2.1
cylinder_length = 13.5

total_height = cap_thickness + cylinder_length  # [15.6 mm](TOTAL_H)
wall_thickness = (outer_diameter - inner_diameter) / 2.0  # [0.62 mm](ORING_WALL_T)

lldpe_od = 9.525                # 3/8" LLDPE tubing OD
lldpe_id = 6.35                 # 1/4" LLDPE tubing ID
westbrass_port_diameter = 10.0       # Westbrass top water port ID
port_depth_min = 20.0           # Westbrass top water port depth

westbrass_squeeze = (outer_diameter - westbrass_port_diameter) / 2.0
lldpe_interference = (lldpe_od - inner_diameter) / 2.0


def build_o_ring() -> cq.Workplane:
    """Thimble on axis +Z: a cap (Z=0 to cap_thickness, centered hole)
    whose Z=0 face mates the Westbrass's port floor, and an open-top
    cylindrical sleeve (Z=cap_thickness to total_height)."""
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
    export_assembly(one_body(o_ring, "tpu-o-ring", M_TPU_BLACK), str(_here / "tpu-o-ring.step"))
    print("-> tpu-o-ring.step")

    variables = {
        "ORING_INNER_D": f"{inner_diameter:.4g} mm",
        "ORING_OUTER_D": f"{outer_diameter:.4g} mm",
        "CAP_HOLE_D": f"{cap_hole_diameter:.4g} mm",
        "ORING_CAP_T": f"{cap_thickness:.4g} mm",
        "CYL_L": f"{cylinder_length:.4g} mm",
        "TOTAL_H": f"{total_height:.4g} mm",
        "ORING_WALL_T": f"{wall_thickness:.4g} mm",
        "LLDPE_OD": f"{lldpe_od:.4g} mm",
        "LLDPE_ID": f"{lldpe_id:.4g} mm",
        "WESTBRASS_PORT_D": f"{westbrass_port_diameter:.4g} mm",
        "PORT_DEPTH_MIN": f"{port_depth_min:.4g} mm",
        "WESTBRASS_SQUEEZE": f"{westbrass_squeeze:.4g} mm",
        "LLDPE_INTERFERENCE": f"{lldpe_interference:.4g} mm",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
    )
    print("-> README.md")

    substitute_py_comments(
        __file__,
        variables=variables,
    )
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
