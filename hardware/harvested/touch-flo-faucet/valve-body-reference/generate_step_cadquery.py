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
# +Y = rear       — the long face the water port is near
# -Y = front      — the user/lever side
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
# curve on the two short (17 mm) Y-faces. Measured R = 4–6 mm;
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
# Two arch/dome features sit above the plateau.
#   Port arch    — rear (+Y side), over the water port
#   Plunger arch — front (-Y side), over the solid brass actuator plunger
#
# Heights measured from Photos 1–3:
#   arc_base_z  = 41 mm  (2 mm above plateau)
#   arc_peak_z  = 46 mm  (5 mm rise from arc base)
#
# Between the two arches is the plateau/lever zone (Z = 39 mm).
# The shell MUST be fully open across the entire plateau zone so
# the stock lever can fit and actuate as designed.
#
# Y extents of the arch blocks are ESTIMATED, not measured.
# Each arch block occupies the outer ~6 mm of the 8.5 mm half,
# leaving a central ~5 mm gap as the plateau/lever zone.
# Refine these when direct arch-width measurements are available.
#
arc_base_z             = 41.0   # mm — arch base, 2 mm above plateau (Photo 2)
arc_peak_z             = 46.0   # mm — arch peak height (Photo 1)
arc_rise               = arc_peak_z - arc_base_z  # mm — 5 mm
#
arch_plateau_half_gap  = 2.5    # mm — estimated; lever zone is ±2.5 mm around Y = 0
arch_block_width_y     = rect_short_half - arch_plateau_half_gap  # mm — 6.0 mm
arch_port_center_y     = rect_short_half - arch_block_width_y / 2  # mm — +5.5 mm (rear)
arch_plunger_center_y  = -arch_port_center_y                        # mm — −5.5 mm (front)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Water port
# -------------------------------------------------------
#
# Single water port at the top face of the body, on the rear (+Y) side.
# The tube exits straight up through the rear of the top face.
# The solid brass actuator plunger is the other top-face brass feature
# (front, -Y side); no fluid passes through it.
#
# Port wall to rear long face: 2 mm (Photo 7)
# Port diameter:               9.75 mm (Photo 8)
# Port centered in long axis:  X = 0
#
port_diameter   = 9.75                                              # mm (Photo 8)
port_radius     = port_diameter / 2                                 # mm — 4.875 mm
port_edge_gap   = 2.0                                               # mm (Photo 7)
port_center_y   = rect_short_half - port_edge_gap - port_radius     # mm — +1.625 mm
port_center_x   = 0.0                                               # mm — centered in X
port_bore_depth = 20.0                                              # mm — approximate
#                   (bore extends from arc_peak_z down into body;
#                    exact depth not measured — update when known)
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
    """One arch block, Z = plateau_z → arc_peak_z.

    First-pass approximation: rectangular block spanning the full
    long axis (rect_long) and arch_block_width_y in the short axis.
    The rounded dome profile (arcing from arc_base_z to arc_peak_z)
    is a TODO for the next iteration — add fillet on top long edges
    once arch width measurements are confirmed.

    center_y: Y center of this arch block (±arch_port_center_y).
    """
    return (
        cq.Workplane("XY")
        .workplane(offset=plateau_z)
        .center(0, center_y)
        .rect(rect_long, arch_block_width_y)
        .extrude(arc_peak_z - plateau_z)
    )


def cut_water_port_bore(body):
    """Bore the water port downward from arc_peak_z into the body."""
    bore = (
        cq.Workplane("XY")
        .workplane(offset=arc_peak_z)
        .center(port_center_x, port_center_y)
        .circle(port_radius)
        .extrude(-port_bore_depth)
    )
    return body.cut(bore)


def build_valve_body():
    cylinder = build_cylinder_base()
    column   = build_rectangular_column()
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

    here = Path(__file__).resolve().parent
    out  = here / "touch-flo-valve-body-reference.step"
    cq.exporters.export(body, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
