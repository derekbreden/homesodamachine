"""Above-counter gasket — printed-TPU pad between the rigid
above-counter plate (above) and the kitchen countertop (below). Seals spills
out of the deck hole, conforms to surface irregularities so the plate
doesn't rock, anti-rotates under faucet-lever torque, and holds preload on the
under-counter nut as the cabinet wood moves seasonally.

Material: Bambu TPU 85A (black), using the saved gaskets.3mf profile.

Footprint and hole pattern match the oval above-counter plate, including
the signal-ribbon branch beside the flavor passage. The rigid plate
locates the parts; the gasket seals around them.

The kernel cuts the gasket (`above_counter_gasket.rs`, beside this module)
from the numbers `numbers()` writes for it (`hardware/scripts/_rust_part.py`).
`build_above_counter_gasket` draws it in CadQuery for the faucet assembly's
CadQuery assembly, which reads it.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_here.parent.parent))  # for _faucet_interface
sys.path.insert(0, str(_here.parent.parent / "faucet-shell"))  # for the shared footprint
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import cadquery as cq  # noqa: E402
from _materials import M_TPU_BLACK, linear
from _faucet_interface import (
    above_counter_gasket_thickness,
    above_counter_plate_thickness,
    flavor_tube_depth,
    pill_length_x,
    pill_width_y,
    shank_hole_diameter,
    bundle_slot_length_x,
    bundle_slot_center_x,
)
from faucet_shell import (
    build_foot_outline,
    foot_width,
    foot_depth,
    foot_center_y,
    build_lower_signal_lane,
    lower_bundle_numbers,
)
from docgen import substitute_py_comments
from world_workplane import WorldWorkplane, xy_plane_z_up


from _rust_data import request


def _data():
    return request("faucet-data", "faucet-data", {
        "op": "above-counter-gasket", "color": list(linear(M_TPU_BLACK)),
        "shell": {
            'foot_width': foot_width,
            'foot_depth': foot_depth,
            'foot_center_y': foot_center_y,
        },
        "lower_bundle": lower_bundle_numbers(),
    })


globals().update(_data()["datums"])
gasket_z_range = tuple(gasket_z_range)
gasket_center = tuple(gasket_center)
shank_hole_center = tuple(shank_hole_center)
flavor_tube_center = tuple(flavor_tube_center)


def gasket_workplane(center):
    """Gasket bottom-face XY workplane, pen at world (x, y) `center`, +Z normal."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=gasket_z_range[0])
        .moveTo(center)
    )


def build_above_counter_gasket():
    """Continuous oval sealing pad with the shank hole and flavor pill."""
    z0 = gasket_z_range[0]
    gasket = build_foot_outline(z0, gasket_thickness)

    shank_hole = (
        gasket_workplane(shank_hole_center)
        .circle(shank_hole_diameter / 2.0)
        .extrude(gasket_thickness)
        .unwrap()
    )
    # Long axis along world X (lateral).
    pill_slot = (
        gasket_workplane(flavor_tube_center)
        .slot2D(bundle_slot_length_x, pill_width_y, angle=0)
        .extrude(gasket_thickness)
        .unwrap()
    )
    return gasket.cut(shank_hole).cut(pill_slot).cut(build_lower_signal_lane())


def numbers() -> dict:
    """The Rust scalar program supplies the countertop stack recipe."""
    return _data()["numbers"]


def main():
    # A run cuts the gasket; an import of this module is a reader of its builder and numbers.
    import _rust_part

    said = _rust_part.cut("faucet", "above-counter-gasket", numbers(),
                          Path(__file__).resolve().parent)
    print("-> " + ", ".join(said["files"]))

    variables = _data()["variables"]

    substitute_py_comments(
        Path(__file__),
        variables=variables,
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
