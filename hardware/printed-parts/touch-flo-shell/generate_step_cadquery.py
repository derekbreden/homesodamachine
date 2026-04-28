import cadquery as cq
from pathlib import Path

# ═══════════════════════════════════════════════════════
# FEATURES — Touch-Flo Valve Shell
# ═══════════════════════════════════════════════════════
#
# 3D-printed shell that wraps the Westbrass R2031-NL-12 Touch-Flo
# valve body. Slides down over the body from above and rests on
# the countertop.
#
# Reference solid:
#   hardware/harvested/touch-flo-faucet/valve-body-reference/
#
# Regenerate:
#   tools/cad-venv/bin/python generate_step_cadquery.py
# ═══════════════════════════════════════════════════════


# -------------------------------------------------------
# Coordinate convention  (matches valve-body reference)
# -------------------------------------------------------
#
# Z = 0 : countertop surface = bottom of valve body
# +Z    : up
# +Y    : rear  — port arch, flavor tube side
# -Y    : front — lever / plunger arch side
# Body centered at XY origin.
#
# -------------------------------------------------------


# -------------------------------------------------------
# Valve body reference dimensions
# (must match valve-body-reference/generate_step_cadquery.py)
# -------------------------------------------------------
#
body_r          = 15.75         # mm — valve body base cylinder radius
plateau_z       = 39.0          # mm — plateau level, lever-side top of body
arc_peak_z      = 46.0          # mm — peak of arch rails
plateau_width_y = 14.0          # mm — plateau width between arch inner faces
#
# -------------------------------------------------------


# -------------------------------------------------------
# Shell inner cavity
# -------------------------------------------------------
#
# The inner bore is a cylinder of shell_inner_r, centered on the
# body axis. Provides slide clearance so the shell can be lowered
# over the body from above.
#
body_clearance_r = 0.5                          # mm — radial slide clearance
shell_inner_r    = body_r + body_clearance_r    # mm — 16.25 mm
#
# -------------------------------------------------------


# -------------------------------------------------------
# Flavor tube channels  (+Y / rear wall)
# -------------------------------------------------------
#
# Two 1/8" OD (3.175 mm) stainless steel flavor tubes run alongside
# the valve body on the +Y (rear) side. Both tubes and the body shank
# (10.5 mm, below the countertop) pass through the same countertop
# hole together.
#
# Placement:
#   - Each tube is tangent to the valve body: tube center Y = body_r + tube_r
#   - The two tubes are tangent to each other (side by side in X):
#     tube centers at X = ±tube_r
#
tube_od             = 3.175                         # mm — 1/8" OD
tube_r              = tube_od / 2                   # mm — 1.5875 mm
tube_channel_clear  = 0.25                          # mm — radial clearance in channel
tube_channel_r      = tube_r + tube_channel_clear   # mm — 1.8375 mm
#
tube_center_y   = body_r + tube_r   # mm — 17.3375 mm (tangent to body)
tube_center_x   = tube_r            # mm — 1.5875 mm  (symmetric ±X, tangent to each other)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Shell outer wall
# -------------------------------------------------------
#
# Outer radius is set by the tube geometry plus 1 mm minimum wall:
#   shell_outer_r = tube_center_y + tube_channel_r + shell_wall_min
#                 = 17.3375 + 1.8375 + 1.0 = 20.175 mm  →  OD ≈ 40.35 mm
#
# The wall is thinner on the +Y side (1 mm at the tube OD) and
# naturally thicker on all other sides (~3.9 mm), providing good
# structural support on the lever side.
#
shell_wall_min  = 1.0                                               # mm
shell_outer_r   = tube_center_y + tube_channel_r + shell_wall_min  # mm — 20.175 mm
shell_od        = shell_outer_r * 2                                 # mm — 40.35 mm
#
# -------------------------------------------------------


# -------------------------------------------------------
# Shell height
# -------------------------------------------------------
#
# shell_top_z: the closed top of the shell on the ±Y sides (covering
#   the arch rails and port tube area). Set 4 mm above the arch peak.
#
# lever_slot_half_y: half the plateau width — the shell is open above
#   plateau_z in the Y = ±lever_slot_half_y band. Both the stock lever
#   and the water supply tube exit through this opening.
#
shell_top_z       = arc_peak_z + 4.0      # mm — 50.0 mm
lever_slot_half_y = plateau_width_y / 2   # mm —  7.0 mm  (arch inner face boundary)
#
# -------------------------------------------------------


# -------------------------------------------------------
# Flange  (rests on countertop, spans the countertop hole)
# -------------------------------------------------------
#
# The shell flange is a wider disc at the base (Z = 0 → flange_t).
# Its OD is large enough to bridge the countertop hole and provide a
# stable landing surface.
#
# Target countertop hole: 1-3/4" = 44.45 mm.
# Flange OD = 52 mm  →  3.8 mm overreach per side.
#
flange_outer_r  = 26.0     # mm — half of 52 mm OD
flange_t        = 3.0      # mm — flange thickness
#
# -------------------------------------------------------


def build_outer_wall():
    """Outer cylindrical wall, Z = 0 → shell_top_z."""
    return (
        cq.Workplane("XY")
        .circle(shell_outer_r)
        .extrude(shell_top_z)
    )


def build_flange():
    """Wider disc at base (Z = 0 → flange_t), OD = flange_outer_r × 2.

    Rests on the countertop and spans the countertop hole.
    """
    return (
        cq.Workplane("XY")
        .circle(flange_outer_r)
        .extrude(flange_t)
    )


def cut_body_bore(shell):
    """Central cavity: shell_inner_r cylinder, full height.

    Provides radial slide clearance (body_clearance_r = 0.5 mm) so the
    shell can be lowered over the 31.50 mm valve body from above.
    """
    bore = (
        cq.Workplane("XY")
        .circle(shell_inner_r)
        .extrude(shell_top_z + 1)
    )
    return shell.cut(bore)


def cut_tube_channel(shell, x_sign):
    """One 1/8" flavor tube channel in the +Y wall, full height.

    The channel bore (tube_channel_r) is centered at
    (x_sign * tube_center_x, tube_center_y). Its inner edge is tangent
    to the body surface (tube inner edge = body_r = 15.75 mm from axis),
    so the installed tube rests against the valve body.

    x_sign: +1 or -1 for the two symmetric tubes.
    """
    channel = (
        cq.Workplane("XY")
        .center(x_sign * tube_center_x, tube_center_y)
        .circle(tube_channel_r)
        .extrude(shell_top_z + 1)
    )
    return shell.cut(channel)


def cut_lever_slot(shell):
    """Front-face cutaway for lever access and water tube exit.

    Removes all shell material above plateau_z on the front (−Y / lever)
    side, from the front face back to Y = +lever_slot_half_y (the inner
    face of the port arch). This gives the shell a stepped profile:
      - Front (−Y): shell height = plateau_z = 39 mm
      - Rear  (+Y): shell height = shell_top_z = 50 mm

    The lever protrudes above the front rim. The arch rails, port area,
    and tube channels are all enclosed by the taller rear section.
    The water supply tube exits upward through this opening.

    Cut box (above plateau_z):
      X : full shell width  (−shell_outer_r − 1  →  +shell_outer_r + 1)
      Y : front face to arch inner face  (−shell_outer_r  →  +lever_slot_half_y)
    """
    cut_y_span   = shell_outer_r + lever_slot_half_y          # mm — 27.175 mm
    cut_y_center = -shell_outer_r + cut_y_span / 2            # mm — −6.5875 mm
    slot = (
        cq.Workplane("XY")
        .workplane(offset=plateau_z)
        .center(0, cut_y_center)
        .rect(2 * (shell_outer_r + 1), cut_y_span)
        .extrude(shell_top_z - plateau_z + 1)
    )
    return shell.cut(slot)


def build_touch_flo_shell():
    wall   = build_outer_wall()
    flange = build_flange()

    shell  = wall.union(flange)
    shell  = cut_body_bore(shell)
    shell  = cut_tube_channel(shell, +1)
    shell  = cut_tube_channel(shell, -1)
    shell  = cut_lever_slot(shell)

    return shell


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def main():
    shell = build_touch_flo_shell()

    bb = shell.val().BoundingBox()
    print(f"Envelope: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  "
          f"Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Shell OD:        {shell_od:.3f} mm  |  Inner bore: Ø{shell_inner_r * 2:.3f} mm")
    print(f"  Tube channels:   Ø{tube_channel_r * 2:.4f} mm  at  Y={tube_center_y:.4f} mm, X=±{tube_center_x:.4f} mm")
    print(f"  Tube wall (min): {shell_outer_r - tube_center_y - tube_channel_r:.3f} mm")
    print(f"  Lever slot:      Y={-shell_outer_r:.3f} → +{lever_slot_half_y:.1f} mm,  Z={plateau_z:.1f} → {shell_top_z:.1f} mm")
    print(f"  Flange:          Ø{flange_outer_r * 2:.1f} mm × {flange_t:.1f} mm thick")

    here = Path(__file__).resolve().parent
    out  = here / "touch-flo-shell.step"
    cq.exporters.export(shell, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
