"""Touch-Flo mounting gasket — printed-TPU pad between the rigid
mounting plate (above) and the kitchen countertop (below). Seals spills
out of the deck hole, conforms to surface irregularities so the plate
doesn't rock, anti-rotates under handle torque, and holds preload on the
under-counter nut as the cabinet wood moves seasonally.

Material: Bambu TPU 90A (black).

Footprint and hole pattern match the mounting plate exactly (the shell
foot — foot circle + two lateral teardrops + front D-pod), reusing the
shell's own geometry; the rigid plate locates the parts, the gasket seals
around them.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_here.parent.parent))  # for _touch_flo_interface
sys.path.insert(0, str(_here.parent.parent / "touch-flo-shell"))  # for the shared footprint
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
from _cadq_export import export_step
from _touch_flo_interface import (
    flavor_tube_depth,
    pill_length_x,
    pill_width_y,
    shank_hole_diameter,
)
from touch_flo_shell import (
    shell_outer_cyl,
    _base_pod_teardrops,
    _base_pod_front,
)
from docgen import substitute_py_comments
from world_workplane import WorldWorkplane, xy_plane_z_up


# Footprint matches the mounting plate; [2 mm](GASKET_T) thick, compresses
# under clamp load.
gasket_thickness = 2.0
# Center offset [3.175 mm](GASKET_Y) +Y (toward the appliance back); no
# lateral offset.
gasket_center = (0.0, +3.175)

# Top face flush with the mounting plate's bottom face; bottom face on
# the countertop surface plane.
plate_z_bottom = -4.0
gasket_z_range = (plate_z_bottom - gasket_thickness, plate_z_bottom)


# Hole pattern matches the mounting plate.
# [12.6 mm](SHANK_HOLE_D) shank pocket — fits the body's threaded shank.
# Centered on the body axis (world origin).
shank_hole_center = (0.0, 0.0)

# One rounded-rectangle slot covering both 1/4" flavor tubes, centered
# [18.93 mm](FLAVOR_TUBE_Y) +Y. Long axis LATERAL (world X):
# [13.4 mm](PILL_L) long × [7.05 mm](PILL_W) wide.
flavor_tube_center = (0.0, +flavor_tube_depth)


def gasket_workplane(center):
    """Gasket bottom-face XY workplane, pen at world (x, y) `center`, +Z normal."""
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=gasket_z_range[0])
        .moveTo(center)
    )


def build_mounting_gasket():
    """Shell-foot footprint (foot circle + two teardrops + front D-pod) as a
    gasket_thickness pad, with the shank hole and flavor-tube pill slot. Sharp
    edges, no fillets."""
    z0 = gasket_z_range[0]
    foot = shell_outer_cyl(z0, gasket_thickness).val()
    teardrops = _base_pod_teardrops(z0, gasket_thickness).val()
    front = _base_pod_front(z0, gasket_thickness).val()
    gasket = cq.Workplane(obj=foot.fuse(teardrops, front))

    shank_hole = (
        gasket_workplane(shank_hole_center)
        .circle(shank_hole_diameter / 2.0)
        .extrude(gasket_thickness)
        .unwrap()
    )
    # Long axis along world X (lateral).
    pill_slot = (
        gasket_workplane(flavor_tube_center)
        .slot2D(pill_length_x, pill_width_y, angle=0)
        .extrude(gasket_thickness)
        .unwrap()
    )
    return gasket.cut(shank_hole).cut(pill_slot)


def main():
    gasket = build_mounting_gasket()
    out = Path(__file__).resolve().parent / "touch-flo-mounting-gasket.step"
    export_step(gasket, str(out))
    print(f"-> {out.name}")

    variables = {
        "GASKET_T": f"{gasket_thickness:.4g} mm",
        "GASKET_Y": f"{gasket_center[1]:.4g} mm",
        "SHANK_HOLE_D": f"{shank_hole_diameter:.4g} mm",
        "FLAVOR_TUBE_Y": f"{flavor_tube_center[1]:.4g} mm",
        "PILL_L": f"{pill_length_x:.4g} mm",
        "PILL_W": f"{pill_width_y:.4g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "GASKET_T": 1,
            "GASKET_Y": 1,
            "SHANK_HOLE_D": 1,
            "FLAVOR_TUBE_Y": 1,
            "PILL_L": 1,
            "PILL_W": 1,
        },
    )
    print(f"-> {Path(__file__).name} (self)")


if __name__ == "__main__":
    main()
