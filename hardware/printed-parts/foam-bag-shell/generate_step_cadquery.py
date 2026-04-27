import math
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
outer_shell_foam_gap = 16.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Foam cap (top/bottom 16 mm foam pour tray, printed twice)
# -------------------------------------------------------
#
foam_cap_height = 16.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Foam cap lid (sits atop a cap during foam pour, printed twice)
# -------------------------------------------------------
#
foam_cap_lid_pour_radius = 5.0
foam_cap_lid_vent_radius = 3.0
foam_cap_lid_hole_inset = 30.0
#
# -------------------------------------------------------


# -------------------------------------------------------
# Cap-to-outer-shell pin joinery
# -------------------------------------------------------
# Pins on cap top (one face); holes drilled into outer-shell corners (top + bottom faces).
# Same cap printed twice — used as bottom (pins up into outer shell) and top (flipped, pins down into outer shell).
# Lid has corner clearance holes so the cap pin can pass freely through into the outer shell.
#
pin_radius = 2.0
pin_height = 5.0
pin_hole_depth = pin_height + 1.0
pin_boss_size = 8.0
lid_pin_clearance_radius = pin_radius
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

    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(bag_pocket_x_offset, 0, 0))
        .rect(bag_pocket_depth, bag_pocket_width)
        .extrude(bag_pocket_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )

def punch_a_bag_pocket_shell_hole(foam_bag_shell, side=1):

    # Bag pocket offset
    bag_pocket_x_offset = tank_copper_shell_radius + bag_pocket_depth / 2 - wall_and_floor_thickness
    bag_pocket_x_offset *= side

    # Hole offset
    hole_z_offset = bag_pocket_width / 2 - 10
    hole_x_offset = bag_pocket_x_offset
    hole_y_offset = hole_shift_from_edge + wall_and_floor_thickness

    # Hole
    hole_punch = build_a_hole_punch(origin=(hole_x_offset, hole_y_offset, hole_z_offset))

    return foam_bag_shell.cut(hole_punch)

def build_outer_shell():
    bag_pocket_outermost_x = tank_copper_shell_radius + bag_pocket_depth - wall_and_floor_thickness
    outer_shell_x_length = 2 * (bag_pocket_outermost_x + outer_shell_foam_gap + wall_and_floor_thickness)
    outer_shell_z_length = 2 * (tank_copper_shell_radius + outer_shell_foam_gap + wall_and_floor_thickness)
    shell = (
        cq.Workplane(xz_plane_y_up)
        .rect(outer_shell_x_length, outer_shell_z_length)
        .extrude(tank_copper_shell_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )
    for x_sign in (1, -1):
        for z_sign in (1, -1):
            boss_x = x_sign * (outer_shell_x_length / 2 - pin_boss_size / 2)
            boss_z = z_sign * (outer_shell_z_length / 2 - pin_boss_size / 2)
            boss = (
                cq.Workplane(xz_plane_y_up)
                .workplane(origin=(boss_x, 0, boss_z), offset=0)
                .rect(pin_boss_size, pin_boss_size)
                .extrude(tank_copper_shell_height)
            )
            shell = shell.union(boss)
            for hole_y in (0, tank_copper_shell_height - pin_hole_depth):
                hole = (
                    cq.Workplane(xz_plane_y_up)
                    .workplane(origin=(boss_x, hole_y, boss_z), offset=hole_y)
                    .circle(pin_radius)
                    .extrude(pin_hole_depth)
                )
                shell = shell.cut(hole)
    return shell

def build_foam_cap():
    bag_pocket_outermost_x = tank_copper_shell_radius + bag_pocket_depth - wall_and_floor_thickness
    foam_cap_x_length = 2 * (bag_pocket_outermost_x + outer_shell_foam_gap + wall_and_floor_thickness)
    foam_cap_z_length = 2 * (tank_copper_shell_radius + outer_shell_foam_gap + wall_and_floor_thickness)
    cap = (
        cq.Workplane(xz_plane_y_up)
        .rect(foam_cap_x_length, foam_cap_z_length)
        .extrude(foam_cap_height)
        .faces(">Y")
        .shell(-wall_and_floor_thickness)
    )
    for x_sign in (1, -1):
        for z_sign in (1, -1):
            boss_x = x_sign * (foam_cap_x_length / 2 - pin_boss_size / 2)
            boss_z = z_sign * (foam_cap_z_length / 2 - pin_boss_size / 2)
            boss = (
                cq.Workplane(xz_plane_y_up)
                .workplane(origin=(boss_x, 0, boss_z), offset=0)
                .rect(pin_boss_size, pin_boss_size)
                .extrude(foam_cap_height)
            )
            cap = cap.union(boss)
            pin = (
                cq.Workplane(xz_plane_y_up)
                .workplane(origin=(boss_x, foam_cap_height, boss_z), offset=foam_cap_height)
                .circle(pin_radius)
                .extrude(pin_height)
            )
            cap = cap.union(pin)
    return cap

def build_foam_cap_lid():
    bag_pocket_outermost_x = tank_copper_shell_radius + bag_pocket_depth - wall_and_floor_thickness
    foam_cap_x_length = 2 * (bag_pocket_outermost_x + outer_shell_foam_gap + wall_and_floor_thickness)
    foam_cap_z_length = 2 * (tank_copper_shell_radius + outer_shell_foam_gap + wall_and_floor_thickness)

    lid = (
        cq.Workplane(xz_plane_y_up)
        .rect(foam_cap_x_length, foam_cap_z_length)
        .extrude(wall_and_floor_thickness)
    )

    pour_x = foam_cap_x_length / 2 - foam_cap_lid_hole_inset
    vent_x = -(foam_cap_x_length / 2 - foam_cap_lid_hole_inset)
    vent_z = foam_cap_z_length / 2 - foam_cap_lid_hole_inset

    pour_hole = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(pour_x, 0, 0))
        .circle(foam_cap_lid_pour_radius)
        .extrude(wall_and_floor_thickness * 3)
    )
    vent_hole_a = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(vent_x, 0, vent_z))
        .circle(foam_cap_lid_vent_radius)
        .extrude(wall_and_floor_thickness * 3)
    )
    vent_hole_b = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(vent_x, 0, -vent_z))
        .circle(foam_cap_lid_vent_radius)
        .extrude(wall_and_floor_thickness * 3)
    )

    lid = lid.cut(pour_hole).cut(vent_hole_a).cut(vent_hole_b)

    for x_sign in (1, -1):
        for z_sign in (1, -1):
            boss_x = x_sign * (foam_cap_x_length / 2 - pin_boss_size / 2)
            boss_z = z_sign * (foam_cap_z_length / 2 - pin_boss_size / 2)
            clearance = (
                cq.Workplane(xz_plane_y_up)
                .workplane(origin=(boss_x, 0, boss_z), offset=0)
                .circle(lid_pin_clearance_radius)
                .extrude(wall_and_floor_thickness * 3)
            )
            lid = lid.cut(clearance)

    return lid

def build_a_hole_punch(
    origin=(0, 0, 0),
    hole_punch_radius=3.25,
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
        .rect(6.5, slit_above)
        .extrude(tank_copper_shell_radius)
    )
    copper_hole = build_a_hole_punch(**hole_args)

    intersection_pieces = foam_bag_shell.intersect(slit_punch)
    solids_by_z = sorted(intersection_pieces.solids().vals(), key=lambda s: s.BoundingBox().zmin)
    cup_slice = solids_by_z[0]
    outer_slice = solids_by_z[-1]

    # The cup slice has exactly two cylindrical faces: the cup's inner curved surface (radius 69.5 from the world Y axis)
    # and the outer curved surface (radius 70.5). Pick the inner one — that's where the plug terminates on the cup side.
    cup_cylinders = [f for f in cup_slice.Faces() if f.geomType() == "CYLINDER"]
    cup_inner_face = min(cup_cylinders, key=lambda f: math.hypot(f.Center().x, f.Center().z))

    # The outer-shell slice has six planar faces (the wall is a flat slab); pick the one whose center has the largest |Z|.
    # That's the outer-shell outermost face — where the plug terminates on the outer side.
    outer_outer_face = max(outer_slice.Faces(), key=lambda f: abs(f.Center().z))

    plug_solid = cq.Solid.makeLoft([cup_inner_face.outerWire(), outer_outer_face.outerWire()])
    plug = cq.Workplane().add(plug_solid).cut(copper_hole)

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
    foam_bag_shell = punch_a_bag_pocket_shell_hole(foam_bag_shell)
    foam_bag_shell = punch_a_bag_pocket_shell_hole(foam_bag_shell, side=-1)
    foam_bag_shell = cut_hole_for_co2_inlet(foam_bag_shell)
    foam_bag_shell = cut_hole_for_water_inlet(foam_bag_shell)
    foam_bag_shell = cut_hole_for_water_outlet(foam_bag_shell)

    # Cut slits + extract their plugs
    foam_bag_shell, copper_inlet_plug = cut_slit_and_build_plug_for_copper_inlet(foam_bag_shell)
    foam_bag_shell, copper_outlet_plug = cut_slit_and_build_plug_for_copper_inlet(foam_bag_shell, which=1)

    # Build the foam cap (separate part, printed twice for top and bottom)
    foam_cap = build_foam_cap()
    # Foam cup must be unioned to turn from a "shell" into a "solid"
    foam_cap = foam_cap.union(foam_cap)

    # Build the foam cap lid (separate part, printed twice, sits atop a cap during pour)
    foam_cap_lid = build_foam_cap_lid()

    here = Path(__file__).resolve().parent
    cq.exporters.export(foam_bag_shell, str(here / "foam-bag-shell.step"))
    cq.exporters.export(copper_inlet_plug, str(here / "copper-inlet-plug.step"))
    cq.exporters.export(copper_outlet_plug, str(here / "copper-outlet-plug.step"))
    cq.exporters.export(foam_cap, str(here / "foam-cap.step"))
    cq.exporters.export(foam_cap_lid, str(here / "foam-cap-lid.step"))
    print(f"-> foam-bag-shell.step")
    print(f"-> copper-inlet-plug.step")
    print(f"-> copper-outlet-plug.step")
    print(f"-> foam-cap.step")
    print(f"-> foam-cap-lid.step")


if __name__ == "__main__":
    main()
