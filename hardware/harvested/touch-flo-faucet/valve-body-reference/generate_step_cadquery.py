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
# +Y = rear       — the long face near the water port arch
# -Y = front      — the user/lever side (plunger arch)
#
# Body is centered at XY origin.
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
# curve on the two short (Y-facing) faces. Measured R = 4–6 mm;
# 5.0 mm used as midpoint estimate. This first-pass model treats
# it as a sharp step. The fillet is a TODO for the next iteration.
#
rect_long             = body_od     # mm — 31.50 mm (X, same as cylinder OD)
rect_short            = 17.0        # mm — 17.00 mm (Y, Photo 6)
rect_short_half       = rect_short / 2  # mm — 8.50 mm (half-width to long face)
plateau_z             = 39.0        # mm — top of rectangular body, plateau level (Photo 3)
transition_fillet_r   = 5.0         # mm — TODO: concave R = 4–6 mm (Photo 4 context)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Zone 3 — Arch features  (Z = plateau_z → arc_peak_z)
# -------------------------------------------------------
#
# Two narrow arch/rail features sit at the outer ±Y edges of the
# rectangular top face. Each is 1.5 mm wide in Y and spans the full
# X length (31.50 mm).
#
#   Port arch    — rear (+Y side), at Y = +7.75 mm center
#   Plunger arch — front (-Y side), at Y = −7.75 mm center
#
# Between them is the plateau/lever zone, 14 mm wide in Y
# (= 17 mm − 2 × 1.5 mm).  The shell must be fully open across
# the entire plateau zone so the stock lever fits and actuates.
#
# Heights (Photos 1–3):
#   plateau_z  = 39 mm  — flat surface between arches
#   arc_base_z = 41 mm  — where arches begin rising (2 mm above plateau)
#   arc_peak_z = 46 mm  — arch peak (5 mm above arc base)
#
# Arch profile: the top long edges are filleted with radius = half the
# arch width (0.75 mm), producing a semi-cylindrical crest along X.
#
arc_base_z            = 41.0                            # mm (Photo 2)
arc_peak_z            = 46.0                            # mm (Photo 1)
arc_rise              = arc_peak_z - arc_base_z         # mm — 5 mm
#
arch_block_width_y    = 1.5                             # mm — confirmed arch width
arch_fillet_r         = arch_block_width_y / 2          # mm — 0.75 mm (semi-cylindrical crest)
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
# Single water port at the top face of the body.
# The port is centered in BOTH axes within the plateau:
#   X = 0  (centered in the 31.50 mm long axis)
#   Y = 0  (centered in the 14.00 mm plateau width)
#
# This places the port wall 2.125 mm from each arch inner face
# (= (14.00 − 9.75) / 2), consistent with the ~2 mm gap
# measured in Photo 7.
#
# The tube exits straight upward through the rear portion of
# the top opening (behind the lever, toward the +Y arch).
#
# The solid brass actuator plunger is the other top-face feature
# (front, toward the −Y arch); no fluid passes through it.
#
port_diameter   = 9.75          # mm (Photo 8)
port_radius     = port_diameter / 2  # mm — 4.875 mm
port_center_x   = 0.0           # mm — centered in long axis
port_center_y   = 0.0           # mm — centered in plateau (Y = 0)
port_bore_depth = 20.0          # mm — approximate; exact depth not measured
#
# Port wall to arch inner face: (plateau_width_y − port_diameter) / 2
#   = (14.00 − 9.75) / 2 = 2.125 mm  ≈ 2 mm (Photo 7)
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
    """One arch rail, Z = plateau_z → arc_peak_z.

    The arch is 1.5 mm wide in Y, spans the full rect_long in X.
    Cross-section in YZ: a wedge — 1.5 mm wide at plateau_z,
    tapering to a point (0.01 mm) at arc_peak_z. This is a
    reasonable first-pass arch profile; refine if a specific
    cross-section (semicircle, etc.) is needed later.

    The foot from plateau_z → arc_base_z remains full-width (1.5 mm)
    because both loft profiles at those heights are essentially
    the same width. The taper only becomes visible in the
    arc_base_z → arc_peak_z zone.

    center_y: global Y center of this arch (±arch_port_center_y).
    """
    return (
        cq.Workplane("XY")
        .workplane(offset=plateau_z)
        .center(0, center_y)
        .rect(rect_long, arch_block_width_y)
        .workplane(offset=arc_peak_z - plateau_z)
        .rect(rect_long, 0.01)
        .loft()
    )


def cut_water_port_bore(body):
    """Bore the water port downward from arc_peak_z into the body.

    Center: (port_center_x, port_center_y) = (0, 0) — plateau center.
    Diameter: 9.75 mm.
    """
    bore = (
        cq.Workplane("XY")
        .workplane(offset=arc_peak_z)
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
    print(f"Envelope: X [{bb.xmin:.1f}, {bb.xmax:.1f}]  "
          f"Y [{bb.ymin:.1f}, {bb.ymax:.1f}]  "
          f"Z [{bb.zmin:.1f}, {bb.zmax:.1f}]")
    print(f"  Arch width:    {arch_block_width_y} mm each  |  Plateau: {plateau_width_y} mm wide")
    print(f"  Port center:   X={port_center_x}, Y={port_center_y}  |  Ø{port_diameter} mm")
    print(f"  Port-to-arch gap: {(plateau_width_y - port_diameter) / 2:.3f} mm each side")

    here = Path(__file__).resolve().parent
    out  = here / "touch-flo-valve-body-reference.step"
    cq.exporters.export(body, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
