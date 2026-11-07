"""TPU o-ring — printed-TPU thimble that seals the 3/8" soda faucet tube
into the harvested Westbrass's top water port. See README.md.

`tpu_o_ring.rs` cuts the part from its numbers (`numbers.rs`). This module is for readers that
still take the thimble from Python: `build_o_ring` draws the CadQuery body the insertion guide and
the native assembly readers use, and its datums are the numbers crate's.
"""

from __future__ import annotations

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))

import cadquery as cq
from _materials import M_TPU_BLACK, linear
from world_workplane import xy_plane_z_up


from _rust_data import request


def _data():
    return request("faucet-data", "faucet-data", {"op": "o-ring", "color": list(linear(M_TPU_BLACK))})


globals().update(_data()["datums"])


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
