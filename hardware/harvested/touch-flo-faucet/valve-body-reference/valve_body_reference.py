"""Reference solid of the Westbrass R2031-NL-12 Touch-Flo metal valve
body. Not a printed part; used as the cavity/envelope reference when
designing the 3D-printed shell that wraps around it.

All measurements come from `valve-body-geometry.md` (sibling file) —
see it for per-photo measurement notes and open questions.

Coordinate convention — delivered (repo world) frame:
  The reference solid is DELIVERED seated in the repo's +Z-up world
  frame, matching every other faucet part:
    +Z = up (height). Z = 0 is the body bottom / countertop deck plane;
         the threaded shank extends in -Z below the deck.
    -Y = front — the user's side; the lever swings toward -Y.
    +Y = back  — the water port sits toward +Y, behind the body axis.
    +X = lateral; the body is symmetric across the X = 0 plane.

  Measurement frame (used by the construction below and the sibling
  valve-body-geometry.md notes): the Westbrass body was measured in its
  own frame — the long (31.50 mm) axis along local X, the port toward
  +localX, the lever side toward -localX, the short (17 mm) axis along
  local Y. build_valve_body() turns the finished solid +90 deg about Z
  to seat it in the world frame above:
    +localX (port / rear)  -> +worldY (back)
    -localX (lever / front)-> -worldY (front)
    local Y (short axis)   -> world X (lateral)
  So the dimensions below read in the measurement frame; the exported
  STEP is in the world frame. Reason in the world frame (-Y = front)
  when placing the body; reach for the measurement frame only when
  cross-checking a per-face caliper number.

Top-face features (measurement frame; z = plateau_z = 39 mm):
  - Brass actuator plunger at body center (x=0, y=0)
  - Water port at local x = +8.75 mm (seats to world +Y, the back)
  - ~1 mm gap between port wall and plunger wall
  - Lever attaches to the plunger and swings in the -localX half
    (seats to world -Y, the front)

Shell design implication: the entire front half of the top face (local
-X / world -Y) plus the plateau strip from the water port forward must
remain open for the lever. The shell can only wrap the cylindrical
base, the two flanking arches, and the back end behind the water port.
"""

import sys
import cadquery as cq
from pathlib import Path

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "printed-parts" / "cadlib"),
)
from _cadq_export import export_step
from docgen import substitute_md, substitute_py_comments
from world_workplane import (
    WorldWorkplane,
    xy_plane_z_up,
    xy_plane_z_down,
    xz_plane_y_up,
    yz_plane_x_up,
)


# Zone 0 — threaded shank. Through-deck portion clamped from below by
# a locknut; thread profile is not modeled (irrelevant for envelope
# work).
# [11 mm](SHANK_OD) shank OD — passes through 1-3/8" countertop hole.
shank_od = 11.0
# [50 mm](SHANK_LEN) shank length below the deck.
shank_length = 50.0
shank_r = shank_od / 2

# Zone 1 — cylindrical base (z = 0 → cylinder_height). Plain cylinder
# whose diameter equals the long dimension of the rectangular column
# above it.
# [31.5 mm](BODY_OD) body OD — also = long dim of the rectangular column above.
body_od = 31.50
body_r = body_od / 2
# [13 mm](CYL_TOP_Z) — cylinder ends / rect column begins here.
cylinder_height = 13.0

# Zone 2 — rectangular column (z = cylinder_height → plateau_z). Long
# X dim carries over from the cylinder; short Y dim is the body's thin
# axis. The cylinder→rectangle transition on the two Y-facing short
# faces has a concave rounded curve, modeled by `build_transition_cove`.
rect_long = body_od
# [17 mm](RECT_SHORT) — short (Y) dim of the rect column.
rect_short = 17.0
rect_short_half = rect_short / 2
rect_long_half = rect_long / 2
# [39 mm](PLATEAU_Z) — top of the rect column / plateau between the arches.
plateau_z = 39.0
# Measured R = 4–6 mm; 5.0 mm fit was off in test print, trying upper
# end [6 mm](TRANSITION_FILLET_R).
transition_fillet_r = 6.0

# Zone 3 — arch features (z = plateau_z → arc_peak_z). Two identical
# side arches at the ±Y edges of the rectangular top face. Each is
# `arch_block_width_y` wide in Y and spans the full X length; the arch
# profile in the ZX plane rises from `arc_base_z` at the short ends to
# `arc_peak_z` at x = 0, atop a rectangular foot from `plateau_z` to
# `arc_base_z`. The plateau between them is `plateau_width_y` wide;
# the plunger and water port both live in this plateau.
# [41 mm](ARC_BASE_Z) — arches start curving upward.
arc_base_z = 41.0
# [46 mm](ARC_PEAK_Z) — arch peak at X=0.
arc_peak_z = 46.0
# [1.5 mm](ARCH_WIDTH) — Y thickness of each arch ridge.
arch_block_width_y = 1.5
arch_y_offset = rect_short_half - arch_block_width_y / 2
# [14 mm](PLATEAU_WIDTH) plateau Y width = rect_short − 2 × arch_block_width_y.
plateau_width_y = rect_short - 2 * arch_block_width_y

# Water port. Single port through the top face at plateau level. The
# tube exits straight upward; depth here is approximate, not measured.
# `port_edge_gap_x` is the [2 mm](PORT_EDGE_GAP) gap from the +X short face (x =
# +rect_long_half) to the port wall, derived per geometry.md.
# [10 mm](PORT_D) — re-measured 2026-05-22 (was 9.75 on 2026-04-27 — caliper
# tips were on the chamfer, not the port wall).
port_diameter = 10.0
port_radius = port_diameter / 2
port_edge_gap_x = 2.0
# [8.75 mm](PORT_X) port center X = rect_long_half − port_edge_gap_x − port_radius.
port_center_x = rect_long_half - port_edge_gap_x - port_radius
port_center_y = 0.0
port_bore_depth = 20.0

# External reference — countertop spec, drives the under-deck clearance
# budget against the [11 mm](SHANK_OD) shank.
# [34.93 mm](COUNTERTOP_HOLE) = 1-3/8" standard countertop hole.
countertop_hole_diameter = 34.93

# Plunger geometry — derived from the ~[1 mm](PLUNGER_GAP) gap between the
# port wall and the plunger wall (port wall at x ≈ port_center_x −
# port_radius = +3.75 mm; plunger wall therefore at x ≈ +2.75 mm and
# plunger OD ≈ [5.5 mm](PLUNGER_OD_EST), not yet caliper-confirmed).
plunger_gap_to_port = 1.0
port_wall_x = port_center_x - port_radius
plunger_od_estimate = 2 * (port_wall_x - plunger_gap_to_port)

# Derived geometry — for cross-referencing in the markdown so the
# arithmetic stays internally consistent if a measurement is updated.
arc_rise = arc_peak_z - arc_base_z                          # [5 mm](ARC_RISE)
plateau_inset = arc_base_z - plateau_z                      # [2 mm](PLATEAU_INSET)
rect_upper_height = plateau_z - cylinder_height             # [26 mm](RECT_UPPER_H)
port_arch_gap_y = (plateau_width_y - port_diameter) / 2.0   # [2 mm](PORT_ARCH_GAP)
rect_long_half_v = rect_long / 2.0                          # [15.75 mm](RECT_LONG_HALF) — half body OD = short-face x


def build_shank():
    """Zone 0: 11 mm cylinder centered on the body axis, extending
    `shank_length` below the deck (down in -Z from the deck plane
    at z = 0). Drawn on the bottom-face plane so `extrude(shank_length)`
    reads as "extend the shank shank_length into the -Z direction"
    without a sign on the extrude argument."""
    return (
        WorldWorkplane(xy_plane_z_down)
        .circle(shank_r)
        .extrude(shank_length)
        .unwrap()
    )


def build_cylinder_base():
    """Zone 1: solid cylinder, z = 0 → cylinder_height."""
    return (
        cq.Workplane(xy_plane_z_up)
        .circle(body_r)
        .extrude(cylinder_height)
    )


def build_rectangular_column():
    """Zone 2: solid rect column, z = cylinder_height → plateau_z."""
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=cylinder_height)
        .rect(rect_long, rect_short)
        .extrude(plateau_z - cylinder_height)
    )


def build_arch(center_y):
    """One arch rail of `arch_block_width_y` thickness in Y, centered
    at world y = `center_y`. The XZ profile (visible looking along
    +Y at the back of the rail) is a rectangular foot from
    `plateau_z` to `arc_base_z` spanning the full X width, then an
    arc from `arc_base_z` at x = ±rect_long_half rising to
    `arc_peak_z` at x = 0 and back down symmetrically."""
    return (
        WorldWorkplane(xz_plane_y_up)
        .workplane(offset=center_y - arch_block_width_y / 2)
        .moveTo((-rect_long_half, plateau_z))
        .lineTo(( rect_long_half, plateau_z))
        .lineTo(( rect_long_half, arc_base_z))
        .threePointArc((0, arc_peak_z), (-rect_long_half, arc_base_z))
        .close()
        .extrude(arch_block_width_y)
        .unwrap()
    )


def build_transition_cove(center_y_sign):
    """Concave cove at the cylinder→rectangle transition for one Y
    face. At z = cylinder_height, the rectangular column (y =
    ±rect_short_half) is narrower than the cylinder base. A concave
    arc of radius `transition_fillet_r` smooths the corner between
    the horizontal cylinder-top ledge and the flat Y-facing face of
    the rectangular column.

    Built as: a filler block fills the r×r corner between the ledge
    and the flat face (oversize in X — the final cylinder clip trims
    the outer edge); a cylinder with axis along X scoops the concave
    arc from it. The result is unioned into the body before the
    cylinder clip, so the cove's outer edge is automatically bounded
    by body_r.

    center_y_sign: +1 for the +Y face, -1 for the -Y face.
    """
    r = transition_fillet_r
    flat_y = center_y_sign * rect_short_half
    filler_center = (0, flat_y + center_y_sign * (r / 2))
    cove_arc_center = (flat_y + center_y_sign * r, cylinder_height + r)
    # Generous half-length for X extrusions; final cylinder clip trims
    # anything past body_r.
    x_overshoot_half = body_r + 2

    filler = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=cylinder_height)
        .center(*filler_center)
        .rect(2 * x_overshoot_half, r)
        .extrude(r)
    )
    cove_cutter = (
        cq.Workplane(yz_plane_x_up)
        .workplane(offset=-x_overshoot_half)
        .center(*cove_arc_center)
        .circle(r)
        .extrude(2 * x_overshoot_half)
    )
    return filler.cut(cove_cutter)


def cut_water_port_bore(body):
    """Bore the water port downward from the plateau. The port sits
    in the plateau zone (no arch above it at y = 0), so the bore
    starts at z = plateau_z and cuts port_bore_depth into the body
    (along -Z). Sketched on the top-face plane at the plateau, then
    extruded back DOWN — negative extrude says "into the body,
    against the +Z normal", which is the natural read for a cut
    tool sketched on a face you're cutting into."""
    bore = (
        cq.Workplane(xy_plane_z_up)
        .workplane(offset=plateau_z)
        .center(port_center_x, port_center_y)
        .circle(port_radius)
        .extrude(-port_bore_depth)
    )
    return body.cut(bore)


def build_valve_body():
    body = (
        build_cylinder_base()
        .union(build_rectangular_column())
        .union(build_arch(+arch_y_offset))
        .union(build_arch(-arch_y_offset))
        .union(build_transition_cove(+1))
        .union(build_transition_cove(-1))
    )

    # Clip the above-deck body to the cylinder profile, removing the
    # overhanging corners from the rectangular column, the arch rail
    # ends, and any cove filler material beyond body_r. Clip range
    # stays at z >= 0 so it doesn't interfere with the shank.
    clip_cyl = (
        cq.Workplane("XY")
        .circle(body_r)
        .extrude(arc_peak_z)
    )
    body = body.intersect(clip_cyl)

    # Shank is a pure cylinder below the deck — union it in after the
    # clip so the clip doesn't erase it.
    body = body.union(build_shank())
    body = cut_water_port_bore(body)

    # Seat the harvested body into the repo world frame. Constructed in
    # the body's measurement frame (long axis along local X, port toward
    # +localX, lever side toward -localX); a +90 deg turn about Z sends
    # +localX -> +worldY (back / port) and -localX -> -worldY (front /
    # lever), matching every other faucet part. See module docstring.
    body = body.rotate((0, 0, 0), (0, 0, 1), 90)
    return body


def main():
    body = build_valve_body()

    bb = body.val().BoundingBox()
    print(f"Envelope: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Arch width:       {arch_block_width_y} mm each  |  Plateau: {plateau_width_y} mm wide in Y")
    print(f"  Port center:      X={port_center_x:.3f} mm, Y={port_center_y:.1f} mm  |  Ø{port_diameter} mm")
    print(f"  Port to X face:   {rect_long_half - port_center_x - port_radius:.3f} mm (should be {port_edge_gap_x} mm)")
    print(f"  Port to arch (Y): {(plateau_width_y - port_diameter) / 2:.3f} mm each side")
    print(f"  Shank:            Ø{shank_od} mm × {shank_length} mm long, Z = -{shank_length} → 0")

    here = Path(__file__).resolve().parent
    out = here / "touch-flo-valve-body-reference.step"
    export_step(body, str(out))
    print(f"-> {out.name}")

    # Short names scoped to this part. Units live inside the value so
    # the script controls them — change a unit in source and every
    # sibling doc + dynamic-comment marker follows.
    variables = {
        # Measured / stated dimensions.
        "SHANK_OD": f"{shank_od:.4g} mm",
        "SHANK_LEN": f"{shank_length:.4g} mm",
        "BODY_OD": f"{body_od:.4g} mm",
        "CYL_TOP_Z": f"{cylinder_height:.4g} mm",
        "RECT_SHORT": f"{rect_short:.4g} mm",
        "PLATEAU_Z": f"{plateau_z:.4g} mm",
        "ARC_BASE_Z": f"{arc_base_z:.4g} mm",
        "ARC_PEAK_Z": f"{arc_peak_z:.4g} mm",
        "ARCH_WIDTH": f"{arch_block_width_y:.4g} mm",
        "PLATEAU_WIDTH": f"{plateau_width_y:.4g} mm",
        "PORT_D": f"{port_diameter:.4g} mm",
        "PORT_X": f"{port_center_x:.4g} mm",
        "PORT_EDGE_GAP": f"{port_edge_gap_x:.4g} mm",
        # Design choices.
        "TRANSITION_FILLET_R": f"{transition_fillet_r:.4g} mm",
        # External references.
        "COUNTERTOP_HOLE": f"{countertop_hole_diameter:.4g} mm",
        "PLUNGER_GAP": f"{plunger_gap_to_port:.4g} mm",
        # Derived geometry.
        "ARC_RISE": f"{arc_rise:.4g} mm",
        "PLATEAU_INSET": f"{plateau_inset:.4g} mm",
        "RECT_UPPER_H": f"{rect_upper_height:.4g} mm",
        "PORT_ARCH_GAP": f"{port_arch_gap_y:.4g} mm",
        "RECT_LONG_HALF": f"{rect_long_half_v:.4g} mm",
        "PLUNGER_OD_EST": f"{plunger_od_estimate:.4g} mm",
    }
    substitute_md(
        here / "valve-body-geometry.md",
        variables=variables,
        expected_counts={
            "SHANK_OD": 6,
            "SHANK_LEN": 4,
            "BODY_OD": 15,
            "CYL_TOP_Z": 10,
            "RECT_SHORT": 7,
            "PLATEAU_Z": 8,
            "ARC_BASE_Z": 6,
            "ARC_PEAK_Z": 7,
            "ARCH_WIDTH": 3,
            "PLATEAU_WIDTH": 5,
            "PORT_D": 7,
            "PORT_X": 5,
            "PORT_EDGE_GAP": 6,
            "COUNTERTOP_HOLE": 3,
            "PLUNGER_GAP": 3,
            "PLUNGER_OD_EST": 2,
            "ARC_RISE": 2,
            "PLATEAU_INSET": 2,
            "RECT_UPPER_H": 1,
            "PORT_ARCH_GAP": 2,
            "RECT_LONG_HALF": 2,
        },
    )
    print(f"-> valve-body-geometry.md")
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "SHANK_OD": 2,
            "SHANK_LEN": 1,
            "BODY_OD": 1,
            "CYL_TOP_Z": 1,
            "RECT_SHORT": 1,
            "PLATEAU_Z": 1,
            "ARC_BASE_Z": 1,
            "ARC_PEAK_Z": 1,
            "ARCH_WIDTH": 1,
            "PLATEAU_WIDTH": 1,
            "PORT_D": 1,
            "PORT_X": 1,
            "PORT_EDGE_GAP": 1,
            "TRANSITION_FILLET_R": 1,
            "COUNTERTOP_HOLE": 1,
            "PLUNGER_GAP": 1,
            "PLUNGER_OD_EST": 1,
            "ARC_RISE": 1,
            "PLATEAU_INSET": 1,
            "RECT_UPPER_H": 1,
            "PORT_ARCH_GAP": 1,
            "RECT_LONG_HALF": 1,
        },
    )
    print(f"-> valve_body_reference.py (self)")


if __name__ == "__main__":
    main()
