import cadquery as cq
from pathlib import Path

# ═══════════════════════════════════════════════════════
# FEATURES — Touch-Flo Valve Body Reference Solid
# ═══════════════════════════════════════════════════════
#
# This is a REFERENCE model of the Westbrass R2031-NL-12 Touch-Flo
# metal valve body. It is not a printed part. It is used as the
# cavity/envelope reference when designing the 3D-printed shell
# that wraps around it.
#
# All measurements come from hardware/harvested/touch-flo-faucet/
# valve-body-geometry.md. Read that file for per-photo measurement
# notes and open questions.
#
# Regenerate:
#   tools/cad-venv/bin/python generate_step_cadquery.py
# ═══════════════════════════════════════════════════════


# -------------------------------------------------------
# Coordinate convention
# -------------------------------------------------------
#
# Z = up (height). Z = 0 is the bottom of the black valve body,
# which is also the countertop reference plane.
#
# X = long axis   — 31.50 mm (cylinder diameter = rectangle long dim)
# Y = short axis  — 17.00 mm (rectangle thin dim)
# +Y = rear       — the arch near the water port side
# -Y = front      — the user/lever side (plunger arch)
#
# Body is centered at the XY origin.
#
# -------------------------------------------------------


# -------------------------------------------------------
# Zone 1 — Cylindrical base  (Z = 0 → cylinder_height)
# -------------------------------------------------------
#
# The bottom 13 mm of the body is a plain cylinder.
# Its diameter equals the long dimension of the rectangle above.
#
body_od         = 31.50         # mm — cylinder OD = rectangle long dim (Photo 5)
body_r          = body_od / 2   # mm — radius = 15.75 mm
cylinder_height = 13.0          # mm — height at which round → rectangular (Photo 4)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Zone 2 — Rectangular column  (Z = cylinder_height → plateau_z)
# -------------------------------------------------------
#
# Above 13 mm the cross-section becomes rectangular.
# Long dim (X) = body_od = 31.50 mm.
# Short dim (Y) = 17.0 mm (Photo 6).
#
# The transition at Z = cylinder_height has a concave rounded
# curve on the two Y-facing short faces. Measured R = 4–6 mm;
# 5.0 mm used as midpoint estimate. This first-pass model treats
# it as a sharp step. The fillet is a TODO for the next iteration.
#
rect_long             = body_od     # mm — 31.50 mm (X, same as cylinder OD)
rect_short            = 17.0        # mm — 17.00 mm (Y, Photo 6)
rect_short_half       = rect_short / 2  # mm — 8.50 mm (half-width to long face)
rect_long_half        = rect_long / 2   # mm — 15.75 mm (half-length to short face)
plateau_z             = 39.0        # mm — top of rectangular body, plateau level (Photo 3)
transition_fillet_r   = 5.0         # mm — TODO: concave R = 4–6 mm (Photo 4 context)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Zone 3 — Arch features  (Z = plateau_z → arc_peak_z)
# -------------------------------------------------------
#
# Two arch rails sit at the outer ±Y edges of the rectangular top face.
# Each is 1.5 mm wide in Y and spans the full X length (31.50 mm).
#
# ARCH ORIENTATION — arch profile is in the ZX plane.
# When viewed from the Y axis (looking along Y), you see the arch shape:
#   - At X = ±15.75 mm (short ends):  Z rises to arc_base_z = 41 mm
#   - At X = 0 (center):              Z peaks at arc_peak_z = 46 mm
#   - Below arc_base_z, each arch has a 2 mm rectangular foot
#     (from plateau_z = 39 mm to arc_base_z = 41 mm)
#
#   Port arch    — rear (+Y side), center at Y = +7.75 mm
#   Plunger arch — front (-Y side), center at Y = −7.75 mm
#
# The plateau between them is 14 mm wide in Y (= 17 − 2 × 1.5 mm).
# The shell must be fully open across the plateau so the stock lever
# can fit and actuate as designed.
#
arc_base_z            = 41.0                            # mm (Photo 2)
arc_peak_z            = 46.0                            # mm (Photo 1)
#
arch_block_width_y    = 1.5                             # mm — confirmed arch width in Y
arch_port_center_y    = rect_short_half - arch_block_width_y / 2   # mm — +7.75 mm (rear)
arch_plunger_center_y = -arch_port_center_y                         # mm — −7.75 mm (front)
#
# Plateau geometry (derived):
plateau_width_y       = rect_short - 2 * arch_block_width_y        # mm — 14.00 mm
#
# -------------------------------------------------------


# -------------------------------------------------------
# Water port
# -------------------------------------------------------
#
# Single water port at the top face (plateau level, Z = plateau_z).
# The tube exits straight upward from the port.
#
# Position in Y: centered in the plateau (Y = 0).
# Position in X: 2 mm from one short face (X = +15.75 mm).
#   Port wall at X = 15.75 − 2 = 13.75 mm from center.
#   Port center at X = 15.75 − 2 − (9.75/2) = 8.875 mm from center.
#
# Note: the specific X end (+ or −) needs verification from the
# physical part. Set to +X here; flip port_center_x sign if needed.
#
# Port-to-arch gap in Y: (plateau_width_y − port_diameter) / 2
#   = (14.00 − 9.75) / 2 = 2.125 mm ≈ 2 mm (Photo 7)
#
port_diameter   = 9.75                                  # mm (Photo 8)
port_radius     = port_diameter / 2                     # mm — 4.875 mm
port_edge_gap_x = 2.0                                   # mm — from short face (X=±15.75) to port wall
port_center_x   = rect_long_half - port_edge_gap_x - port_radius   # mm — +8.875 mm
port_center_y   = 0.0                                   # mm — centered in plateau
port_bore_depth = 20.0                                  # mm — approximate; exact depth not measured
#
# -------------------------------------------------------


def build_cylinder_base():
    """Zone 1: solid cylinder, Z = 0 → cylinder_height (13 mm)."""
    return (
        cq.Workplane("XY")
        .circle(body_r)
        .extrude(cylinder_height)
    )


def build_rectangular_column():
    """Zone 2: solid rectangle column, Z = cylinder_height → plateau_z.

    Long dim (X) = rect_long = 31.50 mm.
    Short dim (Y) = rect_short = 17.00 mm.
    Transition fillet at base is a TODO (see transition_fillet_r).
    """
    return (
        cq.Workplane("XY")
        .workplane(offset=cylinder_height)
        .rect(rect_long, rect_short)
        .extrude(plateau_z - cylinder_height)
    )


def build_arch(center_y):
    """One arch rail.

    The arch is 1.5 mm wide in Y, positioned at center_y.
    Its profile in the ZX plane (visible when looking along Y) is:
      - A 2 mm rectangular foot from Z = plateau_z to Z = arc_base_z,
        spanning the full X width (rect_long).
      - An arch from Z = arc_base_z at X = ±rect_long_half rising to
        Z = arc_peak_z at X = 0, then back down symmetrically.

    Constructed by drawing the closed ZX profile on an XZ workplane
    positioned at the arch's near Y face, then extruding arch_block_width_y
    in the +Y direction.

    center_y: global Y center of this arch (±arch_port_center_y).
    """
    y_start = center_y - arch_block_width_y / 2

    return (
        cq.Workplane("XZ")
        .workplane(offset=y_start)
        .moveTo(-rect_long_half, plateau_z)
        .lineTo( rect_long_half, plateau_z)
        .lineTo( rect_long_half, arc_base_z)
        .threePointArc((0, arc_peak_z), (-rect_long_half, arc_base_z))
        .close()
        .extrude(arch_block_width_y)
    )


def cut_water_port_bore(body):
    """Bore the water port downward from the plateau surface.

    The port is in the plateau zone (no arch above it at Y = 0),
    so the bore starts at plateau_z and cuts downward.

    Center: (port_center_x, port_center_y) = (+8.875, 0).
    Diameter: 9.75 mm.
    """
    bore = (
        cq.Workplane("XY")
        .workplane(offset=plateau_z)
        .center(port_center_x, port_center_y)
        .circle(port_radius)
        .extrude(-port_bore_depth)
    )
    return body.cut(bore)


def build_valve_body():
    cylinder     = build_cylinder_base()
    column       = build_rectangular_column()
    arch_port    = build_arch(arch_port_center_y)
    arch_plunger = build_arch(arch_plunger_center_y)

    body = (
        cylinder
        .union(column)
        .union(arch_port)
        .union(arch_plunger)
    )
    body = cut_water_port_bore(body)
    return body


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

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

    here = Path(__file__).resolve().parent
    out  = here / "touch-flo-valve-body-reference.step"
    cq.exporters.export(body, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
