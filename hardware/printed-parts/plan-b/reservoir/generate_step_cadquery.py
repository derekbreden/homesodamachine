import math
import sys
from pathlib import Path
import cadquery as cq

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import export_step

# ═══════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════


# -------------------------------------------------------
# General
# -------------------------------------------------------
#
# Same coordinate convention as ../foam-bag-shell/: +Y vertical, +X is
# the bag-pocket axis (two cavities sit on opposite sides), +Z is
# perpendicular to it.
xz_plane_y_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
#
# -------------------------------------------------------


# -------------------------------------------------------
# Cavity envelope (mirrors as-built foam-bag-shell inner-face values)
# -------------------------------------------------------
#
# These constants describe the bag-pocket cavity into which this
# reservoir fits. They mirror — but do not import from — the analogous
# constants in ../../foam-bag-shell/generate_step_cadquery.py. The
# reservoir is a separate part with its own life cycle; treating the
# foam-bag-shell envelope as a stable interface keeps the two parts
# from leaking implementation details across each other.
#
# Bag-pocket inner faces (the surfaces the reservoir must clear):
#   - Far (away from tank): x = ±104.5 mm (sign flips with reservoir side)
#   - +Z / −Z side: z = ±70.5 mm
#   - Floor top: y = 1.0 mm
#   - Top of bag-pocket walls: y = 212.4 mm
#   - Centerward (toward tank): cylindrical surface, radius 71.5 mm,
#     vertical axis on +Y through origin — this is the tank_copper_shell
#     outer surface, which the reservoir's centerward face follows.
#
bag_pocket_far_inner_x = 104.5
bag_pocket_z_inner_max = 70.5
bag_pocket_floor_top_y = 1.0
bag_pocket_walls_top_y = 212.4
tank_copper_shell_outer_radius = 71.5
#
# -------------------------------------------------------


# -------------------------------------------------------
# Reservoir geometry
# -------------------------------------------------------
#
# Initial design pass: a fully enclosed `[`-shaped shell with uniform
# wall thickness on all six surfaces (far, +Z, −Z, centerward,
# floor, ceiling). Inlet / outlet / vent bosses, sump slope, internal
# fillets, and the cleaning path all come in later iterations — this
# part exists first to check whether 4 mm walls fit in the cavity
# with room left over for ~1 L of syrup.
#
reservoir_wall_thickness = 4.0
#
# Clearance between reservoir outer surfaces and bag-pocket inner
# faces on every face. Slack for sliding the printed reservoir into
# the cavity from above + FDM tolerance on both prints.
reservoir_clearance = 0.5
#
# -------------------------------------------------------


# ═══════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════


def build_reservoir(side=1):
    """
    Fully enclosed PETG reservoir shell sized to fit one side of the
    bag-pocket cavity with `reservoir_clearance` mm of slack on every
    outer face and `reservoir_wall_thickness` mm of PETG on every
    wall, floor, and ceiling.

    Top-down cross-section: rectangle on three sides
    (far, +Z, −Z), with a concave cylindrical face on the centerward
    side following the tank_copper_shell's outer cylinder (vertical
    axis on +Y through origin). Closer to a `[` than a `D` — three
    straight sides, one concave curve.

    side=+1 builds the +X-side reservoir; side=−1 builds the −X side
    (mirrored across x = 0).

    This first design pass returns a fully closed shell with no
    inlet, outlet, or vent. Those come in later iterations.
    """
    # Outer surfaces of the reservoir = bag-pocket inner faces minus
    # clearance on every face. The centerward face sits *outside* the
    # tank_copper_shell at radius 71.5 + clearance.
    outer_far_x_abs = bag_pocket_far_inner_x - reservoir_clearance
    outer_z_max = bag_pocket_z_inner_max - reservoir_clearance
    outer_floor_bottom_y = bag_pocket_floor_top_y + reservoir_clearance
    outer_top_y = bag_pocket_walls_top_y - reservoir_clearance
    outer_centerward_radius = tank_copper_shell_outer_radius + reservoir_clearance
    outer_height = outer_top_y - outer_floor_bottom_y

    # Inner cavity = outer envelope offset inward by wall_thickness on
    # every face. For the centerward face, "inward" is radially *outward*
    # (away from the tank_copper_shell), so the inner-face radius is
    # outer + wall_thickness.
    W = reservoir_wall_thickness
    inner_far_x_abs = outer_far_x_abs - W
    inner_z_max = outer_z_max - W
    inner_floor_top_y = outer_floor_bottom_y + W
    inner_top_y = outer_top_y - W
    inner_centerward_radius = outer_centerward_radius + W
    inner_height = inner_top_y - inner_floor_top_y

    # Outer envelope:
    #   half-rectangle (the side=±1 half-space) extruded the full
    #   height, minus a vertical cylinder of `outer_centerward_radius`
    #   centered on the +Y axis through origin. The cylinder cut
    #   carves the concave centerward face; the rect bounds the
    #   other three sides + floor + ceiling.
    outer_rect = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(side * outer_far_x_abs / 2, outer_floor_bottom_y, 0))
        .rect(outer_far_x_abs, 2 * outer_z_max)
        .extrude(outer_height)
    )
    outer_cylinder = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(0, outer_floor_bottom_y, 0))
        .circle(outer_centerward_radius)
        .extrude(outer_height)
    )
    outer_envelope = outer_rect.cut(outer_cylinder)

    # Inner cavity: same recipe with inner dimensions.
    inner_rect = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(side * inner_far_x_abs / 2, inner_floor_top_y, 0))
        .rect(inner_far_x_abs, 2 * inner_z_max)
        .extrude(inner_height)
    )
    inner_cylinder = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(0, inner_floor_top_y, 0))
        .circle(inner_centerward_radius)
        .extrude(inner_height)
    )
    inner_cavity = inner_rect.cut(inner_cylinder)

    # Reservoir = outer envelope minus inner cavity.
    return outer_envelope.cut(inner_cavity)


# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════


def main():
    reservoir = build_reservoir(side=1)

    here = Path(__file__).resolve().parent
    export_step(reservoir, str(here / "reservoir.step"))
    print(f"-> reservoir.step")


if __name__ == "__main__":
    main()
