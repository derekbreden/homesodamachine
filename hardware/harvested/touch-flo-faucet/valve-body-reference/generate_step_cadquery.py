"""Reference solid of the Westbrass R2031-NL-12 Touch-Flo metal valve
body. Not a printed part; used as the cavity/envelope reference when
designing the 3D-printed shell that wraps around it.

All measurements come from `valve-body-geometry.md` (sibling file) —
see it for per-photo measurement notes and open questions.

Coordinate convention:
  Z = up (height). Z = 0 is the bottom of the body and the countertop
  reference plane (deck top). The threaded shank extends in -Z below
  the body through the 1-3/8" deck hole.

  X = long axis  — 31.50 mm (cylinder diameter = rectangle long dim)
  Y = short axis — 17.00 mm (rectangle thin dim)
  +X = rear      — water port side (away from the user)
  -X = front     — lever side (toward the user)

  Body is centered at the XY origin.

Top-face features (all at z = plateau_z = 39 mm):
  - Brass actuator plunger at body center (x=0, y=0)
  - Water port at x = +8.875 mm, offset toward +X (rear)
  - ~1 mm gap between port wall and plunger wall
  - Lever attaches to the plunger and swings in the -X half

Shell design implication: the entire -X half of the top face plus the
plateau strip from the water port forward to -X must remain open. The
shell can only wrap the cylindrical base, the two Y-flanking arches,
and the +X end behind the water port.
"""

import sys
import cadquery as cq
from pathlib import Path

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import export_step


# Zone 0 — threaded shank. Through-deck portion clamped from below by
# a locknut; thread profile is not modeled (irrelevant for envelope
# work).
shank_od = 11.0
shank_length = 50.0
shank_r = shank_od / 2

# Zone 1 — cylindrical base (z = 0 → cylinder_height). Plain cylinder
# whose diameter equals the long dimension of the rectangular column
# above it.
body_od = 31.50
body_r = body_od / 2
cylinder_height = 13.0

# Zone 2 — rectangular column (z = cylinder_height → plateau_z). Long
# X dim carries over from the cylinder; short Y dim is the body's thin
# axis. The cylinder→rectangle transition on the two Y-facing short
# faces has a concave rounded curve, modeled by `build_transition_cove`.
rect_long = body_od
rect_short = 17.0
rect_short_half = rect_short / 2
rect_long_half = rect_long / 2
plateau_z = 39.0
# Measured R = 4–6 mm; 5.0 mm fit was off in test print, trying upper
# end 6.0.
transition_fillet_r = 6.0

# Zone 3 — arch features (z = plateau_z → arc_peak_z). Two identical
# side arches at the ±Y edges of the rectangular top face. Each is
# `arch_block_width_y` wide in Y and spans the full X length; the arch
# profile in the ZX plane rises from `arc_base_z` at the short ends to
# `arc_peak_z` at x = 0, atop a rectangular foot from `plateau_z` to
# `arc_base_z`. The plateau between them is `plateau_width_y` wide;
# the plunger and water port both live in this plateau.
arc_base_z = 41.0
arc_peak_z = 46.0
arch_block_width_y = 1.5
arch_y_offset = rect_short_half - arch_block_width_y / 2
plateau_width_y = rect_short - 2 * arch_block_width_y

# Water port. Single port through the top face at plateau level. The
# tube exits straight upward; depth here is approximate, not measured.
# `port_edge_gap_x` is the 2 mm gap from the +X short face (x =
# +rect_long_half) to the port wall, derived per geometry.md.
port_diameter = 9.75
port_radius = port_diameter / 2
port_edge_gap_x = 2.0
port_center_x = rect_long_half - port_edge_gap_x - port_radius
port_center_y = 0.0
port_bore_depth = 20.0


def build_shank():
    """Zone 0: 11 mm cylinder centered on the body axis, extending
    -shank_length below the deck."""
    return (
        cq.Workplane("XY")
        .circle(shank_r)
        .extrude(-shank_length)
    )


def build_cylinder_base():
    """Zone 1: solid cylinder, z = 0 → cylinder_height."""
    return (
        cq.Workplane("XY")
        .circle(body_r)
        .extrude(cylinder_height)
    )


def build_rectangular_column():
    """Zone 2: solid rect column, z = cylinder_height → plateau_z."""
    return (
        cq.Workplane("XY")
        .workplane(offset=cylinder_height)
        .rect(rect_long, rect_short)
        .extrude(plateau_z - cylinder_height)
    )


def build_arch(center_y):
    """One arch rail of `arch_block_width_y` thickness in Y, centered
    at `center_y`. The ZX profile (visible looking along Y) is a
    rectangular foot from `plateau_z` to `arc_base_z` spanning the
    full X width, then an arc from `arc_base_z` at x = ±rect_long_half
    rising to `arc_peak_z` at x = 0 and back down symmetrically."""
    return (
        cq.Workplane("XZ")
        .workplane(offset=center_y - arch_block_width_y / 2)
        .moveTo(-rect_long_half, plateau_z)
        .lineTo(rect_long_half, plateau_z)
        .lineTo(rect_long_half, arc_base_z)
        .threePointArc((0, arc_peak_z), (-rect_long_half, arc_base_z))
        .close()
        .extrude(arch_block_width_y)
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
        cq.Workplane("XY")
        .workplane(offset=cylinder_height)
        .center(*filler_center)
        .rect(2 * x_overshoot_half, r)
        .extrude(r)
    )
    cove_cutter = (
        cq.Workplane("YZ")
        .workplane(offset=-x_overshoot_half)
        .center(*cove_arc_center)
        .circle(r)
        .extrude(2 * x_overshoot_half)
    )
    return filler.cut(cove_cutter)


def cut_water_port_bore(body):
    """Bore the water port downward from the plateau. The port sits
    in the plateau zone (no arch above it at y = 0), so the bore
    starts at plateau_z and cuts in -Z."""
    bore = (
        cq.Workplane("XY")
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


if __name__ == "__main__":
    main()
