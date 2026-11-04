"""TPU o-ring — printed-TPU thimble that seals the 3/8" soda faucet tube
into the harvested Westbrass's top water port. See README.md.

The scalar recipe in `tools/hsm/faucet-data` drives `tpu_o_ring.rs`; `build_o_ring` also supplies the
CadQuery body used by the insertion guide and native assembly readers.
"""

from __future__ import annotations

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import cadquery as cq
from _materials import M_TPU_BLACK, linear
from docgen import substitute_md, substitute_py_comments
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


def numbers():
    """The Rust scalar program supplies the stepped sleeve and cap recipe."""
    return _data()["numbers"]


def main():
    import _rust_part

    said = _rust_part.cut("faucet", "tpu-o-ring", numbers(), _here)
    print("-> " + ", ".join(said["files"]))

    variables = _data()["variables"]

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
