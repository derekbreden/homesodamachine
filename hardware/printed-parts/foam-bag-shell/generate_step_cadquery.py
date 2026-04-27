from pathlib import Path
import cadquery as cq

# ═══════════════════════════════════════════════════════
# FEATURES
# ═══════════════════════════════════════════════════════


# -------------------------------------------------------
# General
# -------------------------------------------------------
#
xz_plane_y_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 1, 0))
xy_plane_z_up = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, 1))
wall_and_floor_thickness = 1.0
hole_shift_from_edge = 15.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Tank copper shell
# -------------------------------------------------------
#
# Tank copper shell radius
tank_outer_radius = 63.5
copper_coil_buffer_radius = 7.0
tank_copper_shell_radius = tank_outer_radius + copper_coil_buffer_radius
#
# Tank copper shell height
tank_height = 152.4
below_tank_elbows_height = 30.0
above_tank_elbows_height = 30.0
tank_copper_shell_height = tank_height + below_tank_elbows_height + above_tank_elbows_height
#
# -------------------------------------------------------


# -------------------------------------------------------
# Tank support wedge
# -------------------------------------------------------
#
tank_support_wedge_height = 30.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Bag pocket
# -------------------------------------------------------
#
bag_pocket_width = 125
bag_pocket_depth = 35
#
# -------------------------------------------------------


# -------------------------------------------------------
# Outer shell
# -------------------------------------------------------
#
outer_shell_foam_gap = 8.0
#
# -------------------------------------------------------


def build_tank_copper_shell():
    
    return (
        cq.Workplane(xz_plane_y_up)
        .circle(tank_copper_shell_radius)
        .extrude(tank_copper_shell_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )

def build_bag_pocket_support_shell():
    bag_pocket_support_side_length = 2 * tank_copper_shell_radius
    return (
        cq.Workplane(xz_plane_y_up)
        .rect(bag_pocket_support_side_length, bag_pocket_support_side_length)
        .extrude(tank_copper_shell_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )

def build_tank_support_wedge():
    support_wedge_outer_radius = tank_copper_shell_radius - wall_and_floor_thickness
    support_wedge_ring_width = 15
    support_wedge_inner_radius = support_wedge_outer_radius - support_wedge_ring_width
    support_wedge_bottom_y = wall_and_floor_thickness
    filled_cylinder = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=support_wedge_bottom_y)
        .circle(support_wedge_outer_radius)
        .extrude(tank_support_wedge_height)
    )
    cut_cone = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=support_wedge_bottom_y)
        .circle(support_wedge_outer_radius)
        .extrude(tank_support_wedge_height, taper=45)
    )
    cut_cylinder = (
        cq.Workplane(xz_plane_y_up)
        .workplane(offset=support_wedge_bottom_y + support_wedge_ring_width)
        .circle(support_wedge_inner_radius)
        .extrude(tank_support_wedge_height)
    )
    cut_object = cut_cone.union(cut_cylinder)
    return filled_cylinder.cut(cut_object)

def build_a_bag_pocket_shell(side=1):
    bag_pocket_height = tank_copper_shell_height

    # Bag pocket offset
    bag_pocket_x_offset = tank_copper_shell_radius + bag_pocket_depth / 2 - wall_and_floor_thickness
    bag_pocket_x_offset *= side

    # Hole offset
    hole_z_offset = bag_pocket_width / 2 - 10
    hole_x_offset = bag_pocket_x_offset
    hole_y_offset = hole_shift_from_edge + wall_and_floor_thickness

    # Hole
    hole_punch = build_a_hole_punch(origin=(hole_x_offset, hole_y_offset, hole_z_offset))

    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(bag_pocket_x_offset, 0, 0))
        .rect(bag_pocket_depth, bag_pocket_width)
        .extrude(bag_pocket_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
        .cut(hole_punch)
    )

def build_outer_shell():
    bag_pocket_outermost_x = tank_copper_shell_radius + bag_pocket_depth - wall_and_floor_thickness
    outer_shell_x_length = 2 * (bag_pocket_outermost_x + outer_shell_foam_gap + wall_and_floor_thickness)
    outer_shell_z_length = 2 * (tank_copper_shell_radius + outer_shell_foam_gap + wall_and_floor_thickness)
    return (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(tank_copper_shell_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )

def build_a_hole_punch(
    origin=(0, 0, 0),
    hole_punch_radius=4,
    hole_punch_height=40,
):
    return (
        cq.Workplane(xy_plane_z_up)
        .workplane(origin=origin, offset=origin[2])
        .circle(hole_punch_radius)
        .extrude(hole_punch_height)
    )

def cut_hole_for_co2_inlet(foam_bag_shell):
    hole_z_offset = (tank_copper_shell_radius + 20) * -1
    hole_x_offset = 0
    hole_y_offset = hole_shift_from_edge + wall_and_floor_thickness
    hole_punch = build_a_hole_punch(origin=(hole_x_offset, hole_y_offset, hole_z_offset))
    return foam_bag_shell.cut(hole_punch)

def cut_hole_for_water_inlet(foam_bag_shell):
    hole_z_offset = tank_copper_shell_radius - 20
    hole_x_offset = 0
    hole_y_offset = tank_copper_shell_height - hole_shift_from_edge
    hole_punch = build_a_hole_punch(origin=(hole_x_offset, hole_y_offset, hole_z_offset))
    return foam_bag_shell.cut(hole_punch)

def cut_hole_for_water_outlet(foam_bag_shell):
    hole_z_offset = tank_copper_shell_radius - 20
    hole_x_offset = 0
    hole_y_offset = hole_shift_from_edge + wall_and_floor_thickness
    hole_punch = build_a_hole_punch(origin=(hole_x_offset, hole_y_offset, hole_z_offset))
    return foam_bag_shell.cut(hole_punch)

def cut_slit_and_build_plug_for_copper_inlet(foam_bag_shell, which = 0):
    hole_z_offset = 20
    hole_x_offset = -30
    hole_y_offset = hole_shift_from_edge + wall_and_floor_thickness + below_tank_elbows_height
    slit_above = tank_copper_shell_height

    if (which == 1):
        hole_x_offset = 30
        hole_y_offset = tank_copper_shell_height - hole_shift_from_edge - wall_and_floor_thickness - above_tank_elbows_height

    hole_args = dict(
        origin=(hole_x_offset, hole_y_offset, hole_z_offset),
        hole_punch_height=tank_copper_shell_radius,
    )

    slit_punch = (
        build_a_hole_punch(**hole_args)
        .moveTo(0, slit_above / 2)
        .rect(8, slit_above)
        .extrude(tank_copper_shell_radius)
    )
    copper_hole = build_a_hole_punch(**hole_args)

    intersection_pieces = foam_bag_shell.intersect(slit_punch)
    combined = cq.Compound.makeCompound(intersection_pieces.solids().vals())
    bb = combined.BoundingBox()
    clip_box = (
        cq.Workplane()
        .box(bb.xmax - bb.xmin, bb.ymax - bb.ymin, bb.zmax - bb.zmin)
        .translate((
            (bb.xmin + bb.xmax) / 2,
            (bb.ymin + bb.ymax) / 2,
            (bb.zmin + bb.zmax) / 2,
        ))
    )
    plug = slit_punch.intersect(clip_box).cut(copper_hole)

    return foam_bag_shell.cut(slit_punch), plug

# ═══════════════════════════════════════════════════════
# BUILD AND EXPORT
# ═══════════════════════════════════════════════════════

def main():

    # Build shell
    tank_copper_shell = build_tank_copper_shell()
    tank_support_wedge = build_tank_support_wedge()
    bag_pocket_support_shell = build_bag_pocket_support_shell()
    bag_pocket_shell = build_a_bag_pocket_shell()
    bag_pocket_shell_2 = build_a_bag_pocket_shell(side=-1)
    outer_shell = build_outer_shell()
    foam_bag_shell = (
        tank_copper_shell
        .union(tank_support_wedge)
        .union(bag_pocket_support_shell)
        .union(bag_pocket_shell)
        .union(bag_pocket_shell_2)
        .union(outer_shell)
    )

    # Cut holes
    foam_bag_shell = cut_hole_for_co2_inlet(foam_bag_shell)
    foam_bag_shell = cut_hole_for_water_inlet(foam_bag_shell)
    foam_bag_shell = cut_hole_for_water_outlet(foam_bag_shell)

    # Cut slits + extract their plugs
    foam_bag_shell, copper_inlet_plug = cut_slit_and_build_plug_for_copper_inlet(foam_bag_shell)
    foam_bag_shell, copper_outlet_plug = cut_slit_and_build_plug_for_copper_inlet(foam_bag_shell, which=1)

    here = Path(__file__).resolve().parent
    cq.exporters.export(foam_bag_shell, str(here / "foam-bag-shell.step"))
    cq.exporters.export(copper_inlet_plug, str(here / "copper-inlet-plug.step"))
    cq.exporters.export(copper_outlet_plug, str(here / "copper-outlet-plug.step"))
    print(f"-> foam-bag-shell.step")
    print(f"-> copper-inlet-plug.step")


if __name__ == "__main__":
    main()
